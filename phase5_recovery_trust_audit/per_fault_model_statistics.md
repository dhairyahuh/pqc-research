# Phase 5: Per-Fault-Model Statistical Evaluation and Confidence Intervals

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Artifact:** `phase5_recovery_trust_audit/per_fault_model_statistics.md`  
**Dataset Reference:** `phase5_recovery_trust_audit/raw_trial_results.csv` (1,300 total trials)

---

## 1. Statistical Methodology and Non-Pooling Constraint

In strict adherence to cryptographic audit principles:
1. **Zero Model Pooling:** Fault models targeting different physical registers, architectural loci, and recovery stages are NOT pooled into an aggregate detection or recovery metric.
2. **Explicit Denominator Accounting:** Attempted, triggered, and valid trial counts are reported independently for each model.
3. **95% Wilson Score Confidence Intervals:** Confidence intervals are calculated using the asymmetric Wilson score interval formulation:
   $$w = \frac{p + \frac{z^2}{2n} \pm z\sqrt{\frac{p(1-p)}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$
   with $z = 1.95996$ for a two-sided 95% confidence level.

---

## 2. Comprehensive Per-Target Results Matrix

| Target Identifier | Fault Model & Injection Locus | Attempted | Triggered | Valid | Dominant Classification | Count (%) | 95% Wilson CI |
|---|---|---|---|---|---|---|---|
| `FT1_SAVED_OPERAND_POST_CAPTURE` | Bit flip in stack variable `u_saved` after capture | 100 | 100 | 100 | `REJECTED_DOWNSTREAM_FO` | 94 (94.0%) | [87.5%, 97.2%] |
| `FT2_SNAPSHOT_PRE_RETRY` | Additive glitch (+100) on `u_saved` before rollback | 100 | 100 | 100 | `REJECTED_DOWNSTREAM_FO` | 70 (70.0%) | [60.4%, 78.1%] |
| `FT3_MONITOR_PERSISTENT_COUNT_ZERO` | Stuck-at-zero on `g_ntt_native_monitor.persistent_count` | 100 | 100 | 100 | `REJECTED_DOWNSTREAM_FO` | 98 (98.0%) | [93.0%, 99.4%] |
| `FT4_MONITOR_ALLOW_RETRY_FORCE` | Bit flip on `allow_retry` (0 $\to$ 1) in fail-stop mode | 100 | 100 | 100 | `RECOVERED_GENUINE` | 100 (100.0%) | [96.3%, 100.0%] |
| `FT5_VERIFIER_INPUT_CORRUPT` | Bit flip in verifier difference check input `d_verify` | 100 | 100 | 100 | `SAFELY_REJECTED_MONITOR` | 100 (100.0%) | [96.3%, 100.0%] |
| `FT6_VERIFIER_RESULT_FORCE_ZERO` | Branch condition glitch: force `diff_retry = sum_retry = 0` | 100 | 100 | 100 | `REJECTED_DOWNSTREAM_FO` | 98 (98.0%) | [93.0%, 99.4%] |
| `FT7_RETRY_TRANSIENT_CLEAN` | Transient bit flip on multiplier intermediate $t$ | 100 | 100 | 100 | `RECOVERED_GENUINE` | 100 (100.0%) | [96.3%, 100.0%] |
| `FT8_RETRY_PERSISTENT_ALU` | Persistent bit flip on multiplier intermediate $t$ | 100 | 100 | 100 | `SAFELY_REJECTED_MONITOR` | 100 (100.0%) | [96.3%, 100.0%] |
| `FT9_FO_PREDICATE_BYPASS_CORRUPT_KEY` | Monitor zeroing + single-locus predicate bypass (`fail=0`) | 100 | 100 | 100 | `SAFELY_REJECTED_MONITOR` | 98 (98.0%) | [93.0%, 99.4%] |
| `FT10_CLEAN_CONTROL` | Nominal un-faulted baseline execution | 100 | 0 | 100 | `CORRECT_CLEAN_EXECUTION` | 100 (100.0%) | [96.3%, 100.0%] |
| `FT1_SAVED_OPERAND_MITIGATED` | FT1 with Dual-Snapshot Parity Checksum enabled | 100 | 100 | 100 | `SAFELY_REJECTED_MONITOR` | 100 (100.0%) | [96.3%, 100.0%] |
| `FT2_SNAPSHOT_MITIGATED` | FT2 with Dual-Snapshot Parity Checksum enabled | 100 | 100 | 100 | `SAFELY_REJECTED_MONITOR` | 100 (100.0%) | [96.3%, 100.0%] |
| `FT1_MITIGATION_STATE_FAULTED` | FT1 with checksum check bypassed (state fault) | 100 | 100 | 100 | `REJECTED_DOWNSTREAM_FO` | 94 (94.0%) | [87.5%, 97.2%] |

---

## 3. Complete Contingency Matrix by Outcome

| Target Identifier | Total | CLEAN | RECOVERED | REJECT_MONITOR | REJECT_FO | SDC | INCONCLUSIVE |
|---|---|---|---|---|---|---|---|
| `FT1_SAVED_OPERAND_POST_CAPTURE` | 100 | 0 | 0 | 6 | **94** | 0 | 0 |
| `FT2_SNAPSHOT_PRE_RETRY` | 100 | 0 | **30** | 0 | **70** | 0 | 0 |
| `FT3_MONITOR_PERSISTENT_COUNT_ZERO` | 100 | 0 | 0 | 0 | **98** | 0 | 2 |
| `FT4_MONITOR_ALLOW_RETRY_FORCE` | 100 | 0 | **100** | 0 | 0 | 0 | 0 |
| `FT5_VERIFIER_INPUT_CORRUPT` | 100 | 0 | 0 | **100** | 0 | 0 | 0 |
| `FT6_VERIFIER_RESULT_FORCE_ZERO` | 100 | 0 | 2 | 0 | **98** | 0 | 0 |
| `FT7_RETRY_TRANSIENT_CLEAN` | 100 | 0 | **100** | 0 | 0 | 0 | 0 |
| `FT8_RETRY_PERSISTENT_ALU` | 100 | 0 | 0 | **100** | 0 | 0 | 0 |
| `FT9_FO_PREDICATE_BYPASS_CORRUPT_KEY` | 100 | 0 | 0 | **98** | 0 | 0 | 2 |
| `FT10_CLEAN_CONTROL` | 100 | **100** | 0 | 0 | 0 | 0 | 0 |
| `FT1_MITIGATED` | 100 | 0 | 0 | **100** | 0 | 0 | 0 |
| `FT2_MITIGATED` | 100 | 0 | 0 | **100** | 0 | 0 | 0 |
| `FT1_MITIGATION_STATE_FAULTED` | 100 | 0 | 0 | 6 | **94** | 0 | 0 |

---

## 4. Deep Phenomenological Explanations

### 4.1 Explanation of FT1 Outcomes (94 REJECT_FO vs 6 REJECT_MONITOR)
In FT1, a single-bit flip was applied to `u_saved`.
- **94 trials (94.0%):** The bit flip caused an invariant mismatch in the initial check. During retry, $u_{\text{saved}}$ was used to recompute $u_{\text{new}}$ and $v_{\text{new}}$. The recovery verifier evaluated:
  $$sum_{\text{retry}} = (u_{\text{new}} + v_{\text{new}} - 2 \cdot u_{\text{saved}}) \equiv 0 \pmod{3329}$$
  The verifier passed unconditionally. The monitor declared successful recovery (`recovered_count++`, `persistent_count == 0`). The corrupted polynomial propagated to the FO transform, where re-encryption detected $tmp \neq ct$, returning `status = MLK_STATUS_REJECT` and $K_{\text{rej}}$.
- **6 trials (6.0%):** When the bit flip targeted high bits ($b \ge 11$), $u_{\text{saved}}$ overflowed signed 16-bit bounds or modulo arithmetic constraints during initial difference computation, causing modular residue mismatches that prevented recovery pass.

### 4.2 Explanation of FT2 Outcomes (70 REJECT_FO vs 30 RECOVERED_GENUINE)
In FT2, an additive glitch of $+100$ was injected into $u_{\text{saved}}$ pre-rollback.
- In 70 trials, the perturbation propagated into the message decoding step, flipping decoded bits and causing downstream FO rejection.
- In 30 trials, the decapsulation output matched $ss_{\text{expected}}$ exactly (`RECOVERED_GENUINE`).
  **Mathematical Cause:** In ML-KEM-768, message bit extraction in `poly_tomsg` maps coefficients into binary bits by testing whether the coefficient is closer to $0$ or $\lfloor q/2 \rfloor = 1664$. The noise boundary is $q/4 \approx 832$. A perturbation of $\Delta = +100$ on coefficients where native noise is low ($\approx 20$) yields a total noise of $\approx 120 \ll 832$. The lattice decoding step completely absorbed the arithmetic perturbation, reproducing the correct message $m$!

### 4.3 Explanation of Inconclusive Trials in FT3 and FT9 (2 trials each)
In trials 236/299 (FT3) and 836/899 (FT9), the bit flip targeted bit 2 ($2^2 = 4$) and bit 3 ($2^3 = 8$). Similar to the lattice noise margin above, an error of magnitude $4$ or $8$ was insufficient to cross the lattice rounding boundary in `poly_tomsg`. The true session key was decoded, preventing FO mismatch. Because `persistent_count` was zeroed, no fail-stop occurred, resulting in `INCONCLUSIVE` classification (untriggered error propagation).

### 4.4 Dual-Rail Verification in FT9 (98 REJECT_MONITOR)
In FT9, `hook_decaps_verify_flag` forced the comparison flag `fail = 0`. However, the reverse dual-rail check in `kem.c:477-504` re-accumulates ciphertext differences in reverse:
```c
if (fail != fail_chk) {
    fail = 0xFF;
    *internal_status = MLK_DECAPS_STATUS_FAULT;
}
```
Because $ct \neq tmp$, `fail_chk = 0xFF`. The predicate mismatch $0 \neq 0xFF$ triggered the dual-rail defense, aborting execution with `MLK_STATUS_FAULT` in 98% of trials!
