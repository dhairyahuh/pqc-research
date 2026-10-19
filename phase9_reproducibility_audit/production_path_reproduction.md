# Production Path Independent Reproduction Report

**Auditor:** Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Binary Executed:** [`phase9_reproducibility_audit/production_reproducer`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/production_reproducer)  
**Linked Objects:** `bin/obj/mlkem768_inst.o` + `bin/obj/mlkem_fault_hooks.o`  
**Trial Dataset:** [`phase9_reproducibility_audit/raw_trial_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/raw_trial_results.csv) (300 trials)  

---

## 1. Executive Summary

Phase 8 established that while Targets F1, F2, F3, and F6 required a harness-level reimplementation of the monitor to inject operand/state corruption, Targets **F4 (transient recovery)**, **F5 (persistent fail-stop)**, and **F12 (clean baseline)** can be executed directly against the compiled in-tree production objects.

This audit independently executed 300 fresh trials (100 per target) directly linking `bin/obj/mlkem768_inst.o` and `bin/obj/mlkem_fault_hooks.o` without stubs or harness overrides.

---

## 2. Experimental Execution Summary (300 Trials)

| Target | Description | Trials Run | Fault Armed | Fault Injected (Triggered) | Invariant Violation Detected | Monitor Autonomous Recoveries | Monitor Persistent Failures | Decapsulation Status | Shared Secret Match | Cryptographic Outcome |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **F12** | Clean Baseline Control | 100 | 0 | 0 | 0 | 0 | 0 | `0x5A5A5A5A` (100/100) | 100/100 (100.0%) | **Genuine Success** |
| **F4** | Transient Butterfly Fault | 100 | 100 | 100 | 100 | 100 | 0 | `0x5A5A5A5A` (100/100) | 100/100 (100.0%) | **Genuine Recovery** |
| **F5** | Stuck-At Persistent Fault | 100 | 100 | 100 | 100 | 0 | 100 | `0xFFFFFFFF` (100/100) | 0/100 (0.0%) | **Safe Fail-Stop Rejection** |

---

## 3. Detailed Trace by Target

### 3.1 Target F12: Clean Baseline Control (100 Trials)
- **Call Graph:** `mlkem768_dec_monitored` $\to$ `mlk_indcpa_dec` $\to$ `mlk_indcpa_enc` $\to$ `mlk_polyvec_ntt` $\to$ `native_ntt_monitor_butterfly` $\to$ `kem.c` FO checks.
- **Trace Evidence:**
  - `executed_count`: exactly 5,376 butterflies executed per trial ($896 \times 6$ polynomials).
  - `mismatch_count`: 0 across all 100 trials.
  - `internal_status`: `0x5A5A5A5A` (`MLK_DECAPS_STATUS_SUCCESS`) in 100/100 trials.
  - `ss_out`: matches expected encapsulation shared secret in 100/100 trials ($100.0\%$, 95% CI: $[96.3\%, 100.0\%]$).

### 3.2 Target F4: Transient Butterfly Fault with Recovery (100 Trials)
- **Injection:** Armed via `mlkem_fault_arm_mid_ntt_locus(stage, b_idx, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, bit, 0, 0)` with `persistent = false`.
- **Locus:** Single-bit flip injected into intermediate butterfly multiplier product $t = \text{fqmul}(r[j+\text{len}], \zeta)$ in [`poly.c:393`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L393).
- **Execution Lifecycle:**
  1. **Armed:** Configured before decapsulation.
  2. **Injected:** `g_mlkem_fault.trigger_count` transitioned from 0 to 1 when the target butterfly executed during polynomial #0.
  3. **Detected:** `native_ntt_monitor_butterfly` ([`mlkem_fault_hooks.c:623-626`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L623-L626)) evaluated:
     $$diff_c = (*r_j - *r_{j+\text{len}} - 2 \cdot t_{\text{check}}) \pmod{3329} \ne 0$$
     Incremented `mismatch_count` from 0 to 1.
  4. **Recovered:** Because `allow_retry == true`, monitor executed in-place rollback:
     ```c
     *r_j = u_saved; *r_j_len = v_saved;
     int16_t t_retry = monitor_fqmul(v_saved, zeta);
     *r_j = (int16_t)(u_saved + t_retry);
     *r_j_len = (int16_t)(u_saved - t_retry);
     ```
     Because the fault was transient, $t_{\text{retry}}$ evaluated correctly. Verifier confirmed $diff_{\text{retry}} == 0 \land sum_{\text{retry}} == 0$, incrementing `recovered_count` to 1.
  5. **Decapsulation Completion:** FO re-encryption ciphertext `tmp` matched `ct` bit-for-bit. Reverse dual-rail check confirmed `fail == fail_chk == 0`. Returned `0x5A5A5A5A` and genuine shared secret ($100/100$).

### 3.3 Target F5: Persistent Stuck-At Butterfly Fault (100 Trials)
- **Injection:** Same butterfly locus with `persistent = true`.
- **Execution Lifecycle:**
  1. **Armed & Injected:** Trigger fired on target butterfly during polynomial #0.
  2. **Detected & Retry Attempted:** `mismatch_count` incremented. In-place rollback executed.
  3. **Persistent Re-corruption:** During retry, line 646 of `mlkem_fault_hooks.c` re-applied the stuck-at bitflip to `u_new`.
  4. **Verifier Detection:** Verifier detected that $sum_{\text{retry}} \ne 0$, incrementing `persistent_count`.
  5. **Subsequent Polynomial Invocations:** In all 6 polynomials of the decapsulation pass, the persistent stuck-at fault re-corrupted the butterfly, resulting in `persistent_count = 6`.
  6. **Decapsulation Fail-Stop Gate:** Line 486 of `kem.c` inspected `ntt_native_monitor_get_persistent_count() > 0`, forced `fail = 0xFF`, and set `internal_status = 0xFFFFFFFF` (`MLK_DECAPS_STATUS_FAULT`).
  7. **Implicit Rejection:** Constant-time `cmov_zero` retained $K_{\text{rej}} = \text{SHAKE256}(z \parallel ct)$ in 100/100 trials ($100.0\%$, 95% CI: $[96.3\%, 100.0\%]$).

---

## 4. Verification Conclusion

1. **Production Path Authenticity:**  
   Targets F4, F5, and F12 run 100% on the authentic compiled production objects `bin/obj/mlkem768_inst.o` and `bin/obj/mlkem_fault_hooks.o`. No harness mocking or substitution was present.
2. **Defensible Physical Interpretation:**  
   Under independent recomputation of $t$ (`NTT_NATIVE_MONITOR_RECOMPUTED_T`), transient single-event upsets in the butterfly multiplier are **100% autonomously recovered** by the production monitor. Persistent hardware faults are **100% safely detected and fail-stop rejected** via implicit rejection.
