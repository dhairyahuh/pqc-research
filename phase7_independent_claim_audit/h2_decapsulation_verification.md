# Phase 7: Independent Verification of End-to-End Hypothesis H2

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Artifact:** `phase7_independent_claim_audit/h2_decapsulation_verification.md`  
**Dataset Reference:** `phase7_independent_claim_audit/derived_corrected_trial_results.csv` (1,200 trials)

---

## 1. Scope of the End-to-End Investigation

Hypothesis H2 asserts that an internal false recovery report in the butterfly monitor can cause an incorrect ML-KEM shared secret to be accepted by the complete decapsulation procedure:
$$\text{H2 True} \iff (\text{status} == \text{MLK\_DECAPS\_STATUS\_SUCCESS}) \land (ss_{\text{out}} \neq ss_{\text{expected}})$$

We audited all trials across the 12 fault targets where the recovery verifier was blinded or declared false recovery (a total of **591 trials** across `F1`, `F2`, `F6`, `F7`, `F9`, and `F10`).

---

## 2. Empirical Verification Across Blinded Trials

| Fault Target | Blinded Trials ($n_{\text{blind}}$) | Output Matches Expected True Key ($ss_{\text{exp}}$) | Output Matches Canonical Rejection Key ($ss_{\text{rej}}$) | Output Accepted as SUCCESS | Silent Data Corruption (H2) |
|---|---|---|---|---|---|
| `F1_SAVED_OPERAND_BITFLIP` | 98 | 13 (Lattice Slack) | 85 (FO Rejection) | 13 (True Keys) | **0 (0.0%)** [0.0%, 3.7%] |
| `F2_SNAPSHOT_PRE_RETRY_DIFFUSION`| 100 | 30 (Lattice Slack) | 70 (FO Rejection) | 30 (True Keys) | **0 (0.0%)** [0.0%, 3.7%] |
| `F6_VERIFIER_RESULT_FORCE_PASS` | 99 | 2 (Lattice Slack) | 97 (FO Rejection) | 2 (True Keys) | **0 (0.0%)** [0.0%, 3.7%] |
| `F7_RETRY_ARITHMETIC_GLITCH` | 94 | 3 (Lattice Slack) | 91 (FO Rejection) | 3 (True Keys) | **0 (0.0%)** [0.0%, 3.7%] |
| `F9_DSPC_COLLISION_MULTI_BIT` | 100 | 13 (Lattice Slack) | 87 (FO Rejection) | 13 (True Keys) | **0 (0.0%)** [0.0%, 3.7%] |
| `F10_DSPC_STATE_BYPASS` | 100 | 13 (Lattice Slack) | 87 (FO Rejection) | 13 (True Keys) | **0 (0.0%)** [0.0%, 3.7%] |
| **Total Across Blinded Trials** | **591** | **74 (12.5%)** | **517 (87.5%)** | **74 (12.5%)** | **0 (0.0%)** [0.0%, 0.6%] |

---

## 3. Four Cryptographic Output States

Our independent analysis establishes that every trial resolves into one of four distinct cryptographic states:

```
                                [ Decapsulation Output ]
                                            │
                     ┌──────────────────────┴──────────────────────┐
                     ▼                                             ▼
          [ status == SUCCESS ]                          [ status != SUCCESS ]
                     │                                             │
          ┌──────────┴──────────┐                       ┌──────────┴──────────┐
          ▼                     ▼                       ▼                     ▼
    ss == ss_expected     ss != ss_expected       ss == ss_rejection    ss != ss_rejection
    [ STATE 1: TRUE KEY ] [ STATE 2: SDC ]        [ STATE 3: SAFE REJ ] [ STATE 4: INVALID ]
    (Clean or Slack)      (Catastrophic H2)       (Implicit Rejection)  (Broken Protocol)
```

1. **State 1: Accepted Correct Shared Secret (`ss == ss_expected` and `status == SUCCESS`):**
   Occurs in clean execution and in trials where the arithmetic perturbation remained below the lattice decoding threshold ($q/4 \approx 832$). The authentic key is released.
2. **State 2: Silent Data Corruption (`ss != ss_expected` and `status == SUCCESS`):**
   An incorrect shared secret is released to the caller and labeled valid. **Zero trials produced this state.**
3. **State 3: Canonical Implicit Rejection (`ss == ss_rejection` and `status == REJECT/FAULT`):**
   The implementation derives the pseudorandom rejection key $K_{\text{rej}} = \text{Hash}_J(z \parallel ct)$ in strict compliance with FIPS 203 Section 3.3. **517 of 591 blinded trials produced this state.**
4. **State 4: Broken/Inconclusive State:**
   Outputs garbage matching neither true nor rejection key. **Zero trials produced this state.**

---

## 4. Why Does the FO Check Prevent H2 in Decapsulation?

In `algorithms/source_ref/mlkem/src/kem.c:466-520`:
```c
fail = mlk_ct_memcmp(ct, tmp, MLKEM_INDCCA_CIPHERTEXTBYTES);
...
/* Dual-rail verification */
uint8_t fail_chk = 0;
for (size_t i = 0; i < MLKEM_INDCCA_CIPHERTEXTBYTES; i++) {
    fail_chk |= (ct[MLKEM_INDCCA_CIPHERTEXTBYTES - 1 - i] ^ tmp[MLKEM_INDCCA_CIPHERTEXTBYTES - 1 - i]);
}
fail_chk = mlk_ct_cmask_nonzero_u8(fail_chk);
...
if (fail != fail_chk) fail = 0xFF;
...
mlk_hash_j(ss, tmp, MLKEM_SYMBYTES + MLKEM_INDCCA_CIPHERTEXTBYTES);
mlk_ct_cmov_zero(ss, kr, MLKEM_SYMBYTES, fail);
```

The Fujisaki-Okamoto transform acts as an **end-to-end semantic checksum**:
- The monitor failure pollutes the polynomial coefficients in memory.
- But those coefficients determine the decrypted message $m'$.
- The re-encrypted ciphertext $tmp = \text{Enc}(pk, m')$ diverges from the received ciphertext $ct$ whenever $m' \neq m$.
- The byte-by-byte comparison `mlk_ct_memcmp` evaluates to non-zero, forcing `fail = 0xFF`.
- The constant-time move `mlk_ct_cmov_zero(ss, kr, MLKEM_SYMBYTES, fail)` leaves `ss` containing $K_{\text{rej}}$.
- Therefore, the protocol safely rejects the corrupted state despite the internal monitor's blindness.

---

## 5. Strict Boundaries of the FO Defense (No Overstated Claims)

The auditor emphasizes three critical caveats:

1. **Primitive-Specific Boundary:** This defense is strictly specific to **IND-CCA2 KEM decapsulation**. It does NOT exist in **ML-KEM Key Encapsulation (`mlkem_enc`)** or **ML-DSA Signature Generation (`mldsa_sign`)**. In those algorithms, there is no re-encryption loop. An H1 false recovery in encapsulation or signature generation leads directly to Silent Data Corruption or signature forgery!
2. **Multi-Fault Coordinated Attacks:** If an attacker combines a snapshot fault (blinding the monitor) with a multi-rail comparator fault (forcing `fail = 0` and `fail_chk = 0`), H2 will succeed.
3. **Denial-of-Service Side Effects:** While implicit rejection prevents key leakage, it causes communication teardown, turning an integrity attack into an availability denial-of-service attack.
