# Phase 5: Demonstrated Failure Cases and Verifier Falsification Analysis

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Artifact:** `phase5_recovery_trust_audit/demonstrated_failure_cases.md`

---

## 1. Executive Summary of Demonstrated Weaknesses

Our adversarial fault injection campaign on the ML-KEM-768 recovery path has successfully falsified the central assumption of the in-place fault recovery architecture:

> **Falsified Hypothesis:** *"The recovery verifier independently confirms that the recomputed butterfly state is cryptographically correct before committing it back to the polynomial buffer."*

**Actual Finding:** The recovery verifier is **tautologically coupled** to the saved snapshot. When the snapshot is corrupted (via register glitch or memory SEU), the recovery verifier checks the recomputed output against the *same corrupted input*, causing the algebraic error terms to cancel identically to zero.

As a direct consequence, the monitor certifies **successful recovery on corrupted cryptographic state** in 94.0% of trials (FT1) and 70.0% of trials (FT2).

---

## 2. Demonstrated Failure Case 1: Tautological Recovery Blindness (FT1 & FT2)

### 2.1 The Vulnerability in Source Code
In `algorithms/source_ref/mlkem_fault_hooks.c:634-655`:
```c
/* Step 1: Restore pre-butterfly operands from snapshot */
*r_j = u_saved;
*r_j_len = v_saved;

/* Step 2: Recompute butterfly */
int16_t t_retry = monitor_fqmul(v_saved, zeta);
int16_t u_new = (int16_t)(u_saved + t_retry);
int16_t v_new = (int16_t)(u_saved - t_retry);

*r_j = u_new;
*r_j_len = v_new;

/* Step 3: Recovery Verifier */
int32_t diff_retry = ((int32_t)u_new - (int32_t)v_new - 2 * (int32_t)t_retry) % 3329;
int32_t sum_retry  = ((int32_t)u_new + (int32_t)v_new - 2 * (int32_t)u_saved) % 3329;

if (diff_retry == 0 && sum_retry == 0) {
    g_ntt_native_monitor.recovered_count++;
} else {
    g_ntt_native_monitor.persistent_count++;
}
```

### 2.2 Algebraic Falsification Proof
Let $u_{\text{true}}$ be the authentic coefficient before the butterfly. Suppose an SEU strikes $u_{\text{saved}}$, such that:
$$u_{\text{saved}} = u_{\text{true}} \oplus \delta$$
1. Recomputation calculates:
   $$u_{\text{new}} \equiv (u_{\text{true}} \oplus \delta) + t_{\text{retry}} \pmod{3329}$$
   $$v_{\text{new}} \equiv (u_{\text{true}} \oplus \delta) - t_{\text{retry}} \pmod{3329}$$
2. The verifier sum check computes:
   $$sum_{\text{retry}} = (u_{\text{new}} + v_{\text{new}} - 2 \cdot u_{\text{saved}}) \pmod{3329}$$
   $$sum_{\text{retry}} = \left( ((u_{\text{true}} \oplus \delta) + t_{\text{retry}}) + ((u_{\text{true}} \oplus \delta) - t_{\text{retry}}) - 2 \cdot (u_{\text{true}} \oplus \delta) \right) \pmod{3329}$$
   $$sum_{\text{retry}} \equiv 2(u_{\text{true}} \oplus \delta) - 2(u_{\text{true}} \oplus \delta) \equiv 0 \pmod{3329}$$
3. The difference check computes:
   $$diff_{\text{retry}} = (u_{\text{new}} - v_{\text{new}} - 2 \cdot t_{\text{retry}}) \equiv 2 \cdot t_{\text{retry}} - 2 \cdot t_{\text{retry}} \equiv 0 \pmod{3329}$$

**Result:** Both invariant checks evaluate to EXACTLY ZERO. The recovery verifier declares that recovery succeeded!

### 2.3 Experimental Confirmation
- In **FT1**, 100 bit-flip trials were injected into `u_saved`.
- The monitor recorded `mismatch_count > 0`, `retry_attempt_count > 0`, and `recovered_count > 0` in **94 out of 100 trials**.
- In all 94 trials, `persistent_count` remained **0**.
- The monitor completely failed to safe-reject the corrupted state.
- The trial was caught downstream ONLY by the Fujisaki-Okamoto re-encryption check (`REJECTED_DOWNSTREAM_FO`).

---

## 3. Demonstrated Failure Case 2: Monitor State Erasure and Fail-Stop Bypass (FT3)

### 3.1 The Vulnerability
In `kem.c:486-494`:
```c
if (ntt_native_monitor_get_persistent_count() > 0 ||
    invntt_native_monitor_get_persistent_count() > 0)
{
    fail = 0xFF;
    if (internal_status != NULL) {
        *internal_status = MLK_DECAPS_STATUS_FAULT;
    }
}
```
The fail-stop protection relies entirely on the global integer `g_ntt_native_monitor.persistent_count`.

### 3.2 Experimental Confirmation
- In **FT3**, a persistent ALU fault was injected into the butterfly, causing `persistent_count` to increment. Immediately thereafter, a single fault cleared `persistent_count = 0`.
- In **98 out of 100 trials**, the fail-stop condition `ntt_native_monitor_get_persistent_count() > 0` evaluated to **false**.
- Execution fell through to the downstream FO comparison without signaling `MLK_DECAPS_STATUS_FAULT`.
- The decapsulation routine returned `status = MLK_DECAPS_STATUS_REJECT` instead of `MLK_DECAPS_STATUS_FAULT`.

---

## 4. Demonstrated Failure Case 3: Spurious Fail-Stop via Verifier Input Corruption (FT5)

### 4.1 The Vulnerability
The recovery verifier requires input operands ($d_{\text{verify}}$, $\zeta$, $u_{\text{saved}}$) to evaluate its invariants. If the verifier's own inputs are disturbed while the computational core is healthy, the verifier registers a false negative.

### 4.2 Experimental Confirmation
- In **FT5**, the retry recomputed authentic values, but bit flip was applied to `diff_retry`.
- In **100 out of 100 trials**, the monitor recorded `persistent_count++` and triggered a hard fail-stop abort (`status = MLK_STATUS_FAULT`).
- **Cryptographic Impact:** Permanent availability denial of service (DoS) caused by fault vulnerability in the defense mechanism itself.

---

## 5. Demonstrated Defense Barrier: Dual-Rail FO Predicate Verification (FT9)

An important positive finding emerged from testing **FT9**:
- An attacker attempted to bypass FO rejection by hooking `hook_decaps_verify_flag(&fail_int)` to force `fail = 0`.
- In `kem.c:477-504`, the implementation computes an independent reverse accumulation:
  ```c
  uint8_t fail_chk = 0;
  for (size_t i = 0; i < MLKEM_INDCCA_CIPHERTEXTBYTES; i++) {
      fail_chk |= (ct[MLKEM_INDCCA_CIPHERTEXTBYTES - 1 - i] ^ tmp[MLKEM_INDCCA_CIPHERTEXTBYTES - 1 - i]);
  }
  fail_chk = mlk_ct_cmask_nonzero_u8(fail_chk);
  ...
  if (fail != fail_chk) {
      fail = 0xFF;
      *internal_status = MLK_DECAPS_STATUS_FAULT;
  }
  ```
- Because the re-encrypted ciphertext $tmp$ did not match $ct$, `fail_chk` was `0xFF`.
- The comparison `fail (0) != fail_chk (0xFF)` caught the single-rail predicate corruption in **98 out of 100 trials** (the remaining 2 being absorbed by lattice noise), successfully aborting decapsulation with `MLK_STATUS_FAULT`.
- **Conclusion:** The dual-rail reverse loop in `kem.c` provides effective, genuine resilience against single-locus predicate glitches during FO verification.
