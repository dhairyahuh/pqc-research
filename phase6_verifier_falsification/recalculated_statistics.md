# Phase 6: Recalculated Fault-Model Statistics and Empirical Evidence

**Auditor:** Skeptical Cryptographic Implementation Researcher  
**Date:** October 2026  
**Artifact:** `phase6_verifier_falsification/recalculated_statistics.md`  
**Dataset Reference:** `phase6_verifier_falsification/raw_trial_results.csv` (1,200 trials total)

---

## 1. Statistical Framework and Methodological Constraints

In accordance with strict independent audit guidelines:
1. **Separation of Component (H1) and Protocol (H2) Metrics:** Internal false recovery rate (H1) is reported completely separately from Silent Data Corruption rate (H2).
2. **Explicit Denominator Grounding:** Denominators represent strictly triggered, valid trials for each specific fault model ($n=100$). Untriggered faults and clean controls are not pooled into fault denominators.
3. **95% Wilson Score Confidence Intervals:** Confidence intervals for all rates are computed using the Wilson score interval formulation without continuity correction.

---

## 2. Master Statistical Contingency Matrix

| Target Name | Valid $n$ | Internal False Rec (H1) [95% CI] | Correct Recovery | Safe Mon Rej | Downstream FO Rej | SDC (H2) [95% CI] | Inconclusive |
|---|---|---|---|---|---|---|---|
| `F1_SAVED_OPERAND_BITFLIP` | 100 | **98 (98.0%)** [93.0%, 99.4%] | 13 | 2 | 85 | **0 (0.0%)** [0.0%, 3.7%] | 0 |
| `F2_SNAPSHOT_PRE_RETRY_DIFFUSION` | 100 | **100 (100.0%)** [96.3%, 100.0%] | 30 | 0 | 70 | **0 (0.0%)** [0.0%, 3.7%] | 0 |
| `F3_MONITOR_PERSISTENT_COUNT_ZERO` | 100 | **0 (0.0%)** [0.0%, 3.7%] | 0 | 1 | 97 | **0 (0.0%)** [0.0%, 3.7%] | 2 |
| `F4_MONITOR_ALLOW_RETRY_FORCE` | 100 | **100 (100.0%)** [96.3%, 100.0%] | 100 | 0 | 0 | **0 (0.0%)** [0.0%, 3.7%] | 0 |
| `F5_VERIFIER_DIFF_CALC_CORRUPT` | 100 | **0 (0.0%)** [0.0%, 3.7%] | 0 | 100 | 0 | **0 (0.0%)** [0.0%, 3.7%] | 0 |
| `F6_VERIFIER_RESULT_FORCE_PASS` | 100 | **99 (99.0%)** [94.6%, 99.8%] | 2 | 1 | 97 | **0 (0.0%)** [0.0%, 3.7%] | 0 |
| `F7_RETRY_ARITHMETIC_GLITCH` | 100 | **94 (94.0%)** [87.5%, 97.2%] | 3 | 6 | 91 | **0 (0.0%)** [0.0%, 3.7%] | 0 |
| `F8_VERIFIER_INPUT_OPERAND_CORRUPT` | 100 | **0 (0.0%)** [0.0%, 3.7%] | 0 | 100 | 0 | **0 (0.0%)** [0.0%, 3.7%] | 0 |
| `F9_DSPC_COLLISION_MULTI_BIT` | 100 | **100 (100.0%)** [96.3%, 100.0%] | 13 | 0 | 87 | **0 (0.0%)** [0.0%, 3.7%] | 0 |
| `F10_DSPC_STATE_BYPASS` | 100 | **100 (100.0%)** [96.3%, 100.0%] | 13 | 0 | 87 | **0 (0.0%)** [0.0%, 3.7%] | 0 |
| `F11_DSPC_CLEAN_CORRECTION` | 100 | **0 (0.0%)** [0.0%, 3.7%] | 0 | 100 | 0 | **0 (0.0%)** [0.0%, 3.7%] | 0 |
| `F12_CLEAN_BASELINE_CONTROL` | 100 | **0 (0.0%)** [0.0%, 3.7%] | 0 | 0 | 0 | **0 (0.0%)** [0.0%, 3.7%] | 0 |

*(Note: In `F12_CLEAN_BASELINE_CONTROL`, all 100 trials resulted in `CORRECT_CLEAN_EXECUTION` [96.3%, 100.0%]).*

---

## 3. Key Empirical Findings by Hypothesis

### 3.1 Hypothesis H1 (Internal False Recovery)
- **Status:** **REPRODUCED AND CONCLUSIVELY PROVEN.**
- In `F1` (isolated stack bit flip), 98/100 trials (98.0%) exhibited internal false recovery: the monitor verifier passed and reported recovery, while the butterfly arithmetic diverged from the fault-free reference.
- In `F2` (additive snapshot glitch), 100/100 trials (100.0%) exhibited internal false recovery.
- In `F7` (retry multiplier glitch), 94/100 trials (94.0%) exhibited internal false recovery due to algebraic cancellation in the difference check.

### 3.2 Hypothesis H2 (Silent Data Corruption)
- **Status:** **CONTRADICTED FOR ISOLATED MONITOR/SNAPSHOT FAULTS IN DECAPSULATION.**
- In 1,200 trials across all 12 target configurations, **0 trials of Silent Data Corruption occurred** ($0.0\%$ [0.0%, 3.7%]).
- When the internal monitor was completely blinded (as in `F1`, `F2`, `F6`, `F7`, `F9`, `F10`), the outer Fujisaki-Okamoto re-encryption check ($c' = \text{Enc}(pk, m') \stackrel{?}{=} c$) detected ciphertext mismatch in 85% to 97% of trials, safely enforcing implicit rejection.
- In the remaining trials, the error did not cross the lattice decoding noise margin ($q/4 \approx 832$), resulting in valid key extraction without arithmetic error.

---

## 4. Evaluation of the DSPC Mitigation

| Test Configuration | Threat Model | Triggered | DSPC Detection Rate [95% CI] | Downstream Safe Rejection |
|---|---|---|---|---|
| `F11_DSPC_CLEAN_CORRECTION` | Single-bit snapshot flip | 100 | **100.0%** (100/100) [96.3%, 100.0%] | 100.0% (Monitor Fail-Stop) |
| `F9_DSPC_COLLISION_MULTI_BIT` | Correlated 2-bit collision | 100 | **0.0%** (0/100) [0.0%, 3.7%] | 87.0% (Downstream FO) |
| `F10_DSPC_STATE_BYPASS` | Instruction skip of branch | 100 | **0.0%** (0/100) [0.0%, 3.7%] | 87.0% (Downstream FO) |

### Conclusion on DSPC:
DSPC provides robust, $O(1)$-cost protection against single-point transient SEUs in snapshot memory. However, against multi-bit correlated disturbances or control-flow glitches, DSPC offers zero barrier, and the implementation relies entirely on outer protocol defenses.
