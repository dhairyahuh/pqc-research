# Fujisaki-Okamoto Re-encryption and Dual-Rail Verification Audit

**Auditor:** Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Target:** Implementation, Disassembly, Constant-Time Properties, and Threat Boundaries of the FO Gate  

---

## 1. Executive Summary

In ML-KEM-768 decapsulation, the Fujisaki-Okamoto (FO) transform guarantees IND-CCA2 security by re-encrypting the decrypted plaintext $m'$ and verifying that the candidate ciphertext $\mathbf{ct}'$ matches the received ciphertext $\mathbf{ct}$. If they differ, the implementation must return a pseudorandom rejection key $K_{\text{rej}} = \text{SHAKE256}(z \parallel ct)$ without leaking information.

This audit:
1. Traces the source and compiled assembly of the FO verification gate in [`kem.c:466-520`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c#L466-L520).
2. Evaluates the constant-time implementation in the compiled binary `bin/obj/mlkem768_inst.o`.
3. Assesses the protection provided by the reverse dual-rail check against physical predicate corruption.
4. Separates verified algorithmic protection from hypothesized physical fault immunity.

---

## 2. Source-Level Path Trace

```c
  /* 1. Forward constant-time comparison */
  fail = mlk_ct_memcmp(ct, tmp, MLKEM_INDCCA_CIPHERTEXTBYTES);
#if defined(MLKEM_RESEARCH_FAULT_HOOKS)
  {
    int fail_int = (int)fail;
    extern void hook_decaps_verify_flag(int *fail_flag);
    hook_decaps_verify_flag(&fail_int);
    fail = (uint8_t)fail_int;
  }
#endif

  /* 2. Independent reverse-order comparison (Dual-Rail Guard) */
  uint8_t fail_chk = 0;
  for (size_t i = 0; i < MLKEM_INDCCA_CIPHERTEXTBYTES; i++) {
    fail_chk |= (ct[MLKEM_INDCCA_CIPHERTEXTBYTES - 1 - i] ^ tmp[MLKEM_INDCCA_CIPHERTEXTBYTES - 1 - i]);
  }
  fail_chk = mlk_ct_cmask_nonzero_u8(fail_chk);

  /* 3. Fail-stop & predicate cross-check */
  if (ntt_native_monitor_get_persistent_count() > 0 ||
      invntt_native_monitor_get_persistent_count() > 0)
  {
    fail = 0xFF; /* Force implicit rejection */
    if (internal_status != NULL) *internal_status = MLK_DECAPS_STATUS_FAULT;
  }
  else if (fail != fail_chk)
  {
    fail = 0xFF; /* Reverse dual-rail predicate mismatch forces rejection */
    if (internal_status != NULL) *internal_status = MLK_DECAPS_STATUS_FAULT;
  }
  else if (internal_status != NULL)
  {
    uint32_t is_fail = ((uint32_t)fail | (0 - (uint32_t)fail)) >> 31;
    *internal_status = (1 - is_fail) * MLK_DECAPS_STATUS_SUCCESS +
                       is_fail * MLK_DECAPS_STATUS_REJECT;
  }

  /* 4. Rejection key computation */
  mlk_memcpy(tmp, sk + MLKEM_INDCCA_SECRETKEYBYTES - MLKEM_SYMBYTES, MLKEM_SYMBYTES);
  mlk_memcpy(tmp + MLKEM_SYMBYTES, ct, MLKEM_INDCCA_CIPHERTEXTBYTES);
  mlk_hash_j(ss, tmp, MLKEM_SYMBYTES + MLKEM_INDCCA_CIPHERTEXTBYTES);

  /* 5. Constant-time conditional key selection */
  mlk_ct_cmov_zero(ss, kr, MLKEM_SYMBYTES, fail);
```

---

## 3. Compiled Assembly Disassembly Audit (`AArch64`)

Disassembly of `bin/obj/mlkem768_inst.o` at the conditional key selection gate ([`binary_and_build_identity.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase8_production_path_audit/binary_and_build_identity.md)):

```text
    fea4: neg    w9, w24             ; w24 holds fail flag (0x00 or 0xFF)
    fea8: add    x10, sp, #0x460     ; x10 points to candidate key kr
    feac: ldrb   w11, [x20, x8]      ; w11 = ss[i] (currently rejection key K_rej)
    feb0: ldrb   w12, [x10, x8]      ; w12 = kr[i] (candidate key K_cand)
    feb4: mov    x13, x9             ; x13 = mask from fail
    feb8: lsr    w13, w13, #16       ; broadcast mask
    febc: bic    w12, w12, w13       ; bitwise clear candidate key bits if fail != 0
    fec0: and    w11, w11, w13       ; bitwise retain rejection key bits if fail != 0
    fec4: orr    w11, w11, w12       ; combine selected bits
    fec8: strb   w11, [x20, x8]      ; store into output buffer ss[i]
    fecc: add    x8, x8, #0x1        ; increment loop index i
    fed0: cmp    x8, #0x20           ; loop 32 bytes (256 bits)
    fed4: b.ne   0xfeac              ; deterministic counter loop
```

### Constant-Time Assessment:
- **No Secret-Dependent Branches:** The loop counter `x8` iterates deterministically from 0 to 31.
- **Bitwise Multiplexing:** Selection between $K_{\text{cand}}$ and $K_{\text{rej}}$ is performed strictly using constant-time instructions (`bic`, `and`, `orr`).
- **Timing Invariance:** Latency is mathematically independent of whether `fail == 0x00` or `fail == 0xFF`.

---

## 4. Dual-Rail Redundancy Analysis

The reverse dual-rail check computes `fail_chk` by iterating backwards over the 1,088-byte ciphertext:
$$fail\_chk = \bigvee_{i=0}^{1087} (ct[1087 - i] \oplus tmp[1087 - i])$$

### Fault Coverage:
1. **Single-Event Transient Flip on `fail`:**  
   If an electromagnetic pulse or laser strike forces the register holding `fail` from `0xFF` to `0x00` at line 472 (`hook_decaps_verify_flag`), the subsequent check `fail != fail_chk` detects that `0x00 != 0xFF`, overrides `fail = 0xFF`, and sets status to `0xFFFFFFFF`.
2. **Re-encryption Bypass Resistance:**  
   To successfully bypass the dual-rail gate, an adversary would need to simultaneously corrupt both `fail` and `fail_chk`, or force a branch skip across the entire verification block.

### Threat Model Boundaries (What Is NOT Protected):
- **Post-Verification Register Corruption:** If a physical fault corrupts register `w24` *after* the `fail != fail_chk` check (e.g., between `fe9c` and `fea4`), the constant-time selection could still be misled.
- **Clock Glitch Instruction Skip:** A clock glitch skipping the instruction `strb w11, [x20, x8]` or forcing the loop exit could truncate or corrupt output bytes.
- **Conclusion:** The dual-rail mechanism provides **software-level algorithmic redundancy** against single predicate flips, but does not provide unconditional protection against arbitrary hardware-level physical attacks.
