# Production Recovery Counter Control-Flow and Semantic Audit

**Auditor:** Skeptical Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Subject:** Source-Level Control-Flow Verification of Recovery and Persistent Telemetry Counters  
**Target Code Audited:**
- `algorithms/source_ref/mlkem/src/poly.c` (Lines 380–415)
- `algorithms/source_ref/mlkem_fault_hooks.c` (Lines 250–278, 620–664)
- `algorithms/source_ref/mlkem/src/kem.c` (Lines 483–520)
- `algorithms/source_ref/mlkem_fault_hooks.h` (State definitions)

---

## 1. Executive Summary

This audit traces the exact source-level control flow governing fault injection, invariant checking, rollback, retry, and fail-stop handling in the compiled ML-KEM-768 production implementation. 

The investigation confirms that the five-stage causal sequence reported for Target F4 (Transient Fault Recovery) is structurally guaranteed by the C source code and cannot be produced by an unfaulted clean execution, an ineffective injection, or an unhandled exception.

However, we explicitly document the physical telemetry boundary: **intermediate polynomial coefficients ($u_{\text{retry}}, v_{\text{retry}}$) are local register/stack variables in `poly.c` and are not serialized into the production trial CSV.** Recovery integrity is established via the causal counter chain (`trigger_count == 1`, `mismatch_count == 1`, `recovered_count == 1`, `persistent_count == 0`), outer re-encryption equivalence ($c' \equiv c$), and bit-for-bit match against the independent clean-room Keccak oracle ($K_{\text{out}} = K_{\text{valid}}$).

---

## 2. Line-by-Line Control Flow Tracing

```
  poly.c:382-383: Snapshot pre-butterfly operands (u_saved, v_saved)
       |
  poly.c:389: Compute intermediate product: t = mlk_fqmul(r[j+len], zeta)
       |
  poly.c:393: Invoke hook_mid_ntt_post_mul()
       |
       v
  mlkem_fault_hooks.c:250-277: Apply bitflip to *t_ptr; increment trigger_count++
       |
       v
  poly.c:394-395: Forward butterfly computes corrupt: r[j] = u + t; r[j+len] = u - t
       |
       v
  poly.c:408: Invoke native_ntt_monitor_butterfly()
       |
       v
  mlkem_fault_hooks.c:623-626: Parity Check: diff_c != 0 || sum_c != 0
       |--> [TRUE] --> mlkem_fault_hooks.c:627: mismatch_count++
                            |
                       mlkem_fault_hooks.c:632: retry_attempt_count++
                            |
                       mlkem_fault_hooks.c:635-636: Rollback: *r_j = u_saved; *r_j_len = v_saved
                            |
                       mlkem_fault_hooks.c:638-640: Recompute: t_retry = fqmul(v_saved, zeta);
                            |                       u_new = u_saved + t_retry; v_new = u_saved - t_retry
                            |
                       mlkem_fault_hooks.c:642: Persistent check (g_mlkem_fault.persistent)
                            |
                            +---> [TRANSIENT (F4)]: No reinjection
                            |          |
                            |     mlkem_fault_hooks.c:652-655: Post-retry verification
                            |     diff_retry == 0 && sum_retry == 0
                            |          |
                            |     mlkem_fault_hooks.c:656: recovered_count++
                            |          |
                            |          v
                            |     poly.c completes NTT with restored state --> kem.c:486 persistent_count==0
                            |     --> FO check passes --> MLK_STATUS_SUCCESS (0x5A5A5A5A) --> K_out = K_valid
                            |
                            +---> [PERSISTENT (F5A/F5B)]: Inverts bit or forces *t = 0 again
                                       |
                                  mlkem_fault_hooks.c:652-655: Post-retry verification fails!
                                       |
                                  mlkem_fault_hooks.c:658: persistent_count++
                                       |
                                       v
                                  kem.c:486: persistent_count > 0 detected!
                                  kem.c:489: fail = 0xFF; *internal_status = 0xFFFFFFFF
                                  kem.c:516: ss = SHAKE256(z || ct)
                                  kem.c:519: cmov retains K_rej --> SAFE FAIL-STOP
```

---

## 3. Evaluation of the Five Mandatory F4 Recovery Conditions

| Condition | Theoretical Requirement | Exact Source Code Enforcement | Observability in Telemetry | Audit Verdict |
| :--- | :--- | :--- | :--- | :---: |
| **1. Fault Activated** | The fault was executed at the target locus, mutating computation. | `mlkem_fault_hooks.c:264-276`: `*t_ptr ^= (1 << bit); g_mlkem_fault.trigger_count++;` | `actually_triggered = 1` recorded in all 100 trials. | **PROVEN** |
| **2. Mismatch Detected** | The monitor verifier detected arithmetic corruption. | `mlkem_fault_hooks.c:626-627`: `if (diff_c != 0 \|\| sum_c != 0) g_ntt_native_monitor.mismatch_count++;` | `mismatch_count = 1` recorded in all 100 trials. | **PROVEN** |
| **3. Recovery Path Invoked** | The implementation initiated in-place rollback and recomputation. | `mlkem_fault_hooks.c:631-640`: `*r_j = u_saved; *r_j_len = v_saved; t_retry = monitor_fqmul(...);` | `g_ntt_native_monitor.retry_attempt_count` incremented. | **PROVEN** |
| **4. Recovery Completed & Verified** | The post-retry verifier checked arithmetic parity and cleared state. | `mlkem_fault_hooks.c:655-656`: `if (diff_retry == 0 && sum_retry == 0) g_ntt_native_monitor.recovered_count++;` | `recovered_count = 1, persistent_count = 0` in all 100 trials. | **PROVEN** |
| **5. Valid Key Released** | End-to-end decapsulation returned authentic valid shared secret. | `kem.c:486, 519`: `fail == 0`, `mlk_ct_cmov_zero(ss, kr, 32, 0)` releases authentic valid key. | `actual_ss_hex == oracle_valid_hex` in all 100 trials. | **PROVEN** |

---

## 4. Distinction Between Genuine Recovery and Non-Recovery Execution

To satisfy the skeptical audit mandate that **an output match alone must never be described as proof of recovery**, we establish the negative control boundaries:

1. **Clean Baseline Execution (F12):**
   - Emits valid key ($K_{\text{out}} = K_{\text{valid}}$).
   - Telemetry: `trigger_count == 0, mismatch_count == 0, recovered_count == 0`.
   - Distinct from F4 because no fault was triggered and no recovery logic was invoked.
2. **Ineffective Injection / Masked Fault:**
   - If an injection fails to alter arithmetic (e.g. flipping an unused sign bit in a normalized zero), `diff_c == 0 && sum_c == 0`.
   - Telemetry: `trigger_count == 1, mismatch_count == 0, recovered_count == 0`.
   - Never occurred in F4: all 100 trials produced `mismatch_count = 1`.
3. **Downstream FO Rejection:**
   - If recovery fails, the corrupt state propagates to re-encryption ($c' \ne c$), triggering implicit rejection ($K_{\text{out}} = K_{\text{rej}}$).
   - Distinct from F4: F4 produced $K_{\text{out}} = K_{\text{valid}}$ with `status = 0x5A5A5A5A`.

---

## 5. Explicit Telemetry Limitations

1. **Intermediate Butterfly Coefficients Unserialized:**
   The intermediate values `u_new` and `v_new` generated by `mlkem_fault_hooks.c:639-640` are local stack variables. They are verified internally by `diff_retry` and `sum_retry`, but their 16-bit integer values are not dumped into `production_trial_recalculation.csv`.
2. **Scope of Fault Injection:**
   The native monitor was evaluated against transient single-bit flips on intermediate butterfly multiplier products ($t$). Multi-butterfly spatial burst faults or multi-layer temporal cascade faults were not evaluated in the production binary test suite.

---

## 6. Audit Conclusion

The production recovery sequence in Target F4 is certified as **authentic genuine recovery**. The increment of `recovered_count` cannot occur without an initial detected mismatch followed by successful post-retry invariant verification.
