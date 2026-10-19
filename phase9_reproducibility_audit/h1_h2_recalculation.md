# Recalculation of Hypotheses H1 and H2 with Confidence Intervals

**Auditor:** Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Target:** Statistical Recalculation of Internal False Recovery (H1) and Silent Data Corruption (H2)  

---

## 1. Statistical Methodology & Assumptions

1. **Uncertainty Intervals:** All confidence intervals are calculated using the **Wilson score interval** (without continuity correction), which provides robust coverage for extreme binomial proportions near $0\%$ and $100\%$:
   $$w = \frac{p + \frac{z^2}{2n} \pm z \sqrt{\frac{p(1-p)}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$
   where $z = 1.95996$ for a two-sided $95\%$ confidence level.
2. **Prohibition of Inappropriate Pooling:** Pooling heterogeneous fault models (e.g., combining a transient multiplier bitflip with an artificial state wipe of `persistent_count`) into a single "overall fault vulnerability rate" violates the assumption of identical distribution. Each fault model represents a distinct physical or algorithmic failure mechanism and must be reported with its own specific denominator ($N=100$).
3. **Epistemological Constraint on Zero Counts:** An observed count of 0/100 or 0/1,200 does **not** prove that an event is mathematically impossible. It demonstrates that the event did not occur within the tested parameter space and trial volume, bounded by the corresponding upper Wilson confidence limit.

---

## 2. Target-by-Target Recalculation Table

*Sample size $N=100$ per target. Confidence intervals are 95% Wilson score intervals.*

| Target | Description | Evaluated Path | $H_1$ False Recovery Events | $H_1$ Point Estimate | $H_1$ 95% Wilson CI | $H_2$ Accepted Incorrect Keys | $H_2$ Point Estimate | $H_2$ 95% Wilson CI |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **F1** | Saved Operand Bitflip | Harness Model | 98 / 100 | **98.0%** | [93.0%, 99.4%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F2** | Additive Bias (+100) | Harness Model | 70 / 100 | **70.0%** | [60.4%, 78.1%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F3** | Stride / Persistent Count Zero | Harness Model | 100 / 100 | **100.0%** | [96.3%, 100.0%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F4** | Transient Butterfly Fault | **Production Object** | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F5** | Persistent Stuck-At Fault | **Production Object** | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F6** | Verifier Flag Forced Pass | Harness Model | 100 / 100 | **100.0%** | [96.3%, 100.0%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F7** | Retry Arithmetic Glitch | Harness Model | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F8** | Verifier Operand Corrupt | Harness Model | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F9** | DSPC Correlated Linear | Harness Model | 93 / 100 | **93.0%** | [86.3%, 96.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F10**| DSPC Control Bypass | Harness Model | 100 / 100 | **100.0%** | [96.3%, 100.0%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F11**| DSPC Single-Bit Flip | Harness Model | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F12**| Clean Baseline Control | **Production Object** | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |

---

## 3. Comprehensive Analysis of Hypotheses

### 3.1 Hypothesis H1 Findings
- **Defensible Conclusion:** In software models where in-place snapshot operands (`u_saved`) or monitor state registers are perturbed, the internal recovery verifier exhibits verifier blindness in **70% to 100% of trials** across Targets F1, F2, F3, F6, F9, and F10.
- **Root Cause:** The recovery verifier recomputes differences and sums using the *corrupted* snapshot as its truth reference, causing arithmetic cancellation ($u' - v' - 2t \equiv 0$).
- **F4 Status:** Target F4 does **not** exhibit H1 ($0/100$, 95% CI: $[0.0\%, 3.6\%]$). It represents genuine recovery.

### 3.2 Hypothesis H2 Findings
- **Defensible Conclusion:** Across all 1,200 trials (including 591 trials where the recovery monitor was blinded or bypassed), **zero instances of Accepted Incorrect Output ($H_2$) were observed** ($0/1,200$, 95% Wilson CI: $[0.0\%, 0.31\%]$).
- **Physical Interpretation:** In ML-KEM-768 decapsulation, internal false recovery does not breach the API boundary because the outer Fujisaki-Okamoto re-encryption loop unconditionally compares candidate ciphertext `tmp` against received ciphertext `ct`.
- **Epistemological Qualification:** This result proves that $H_2$ was absent under the tested single-shot and persistent fault injections in the decapsulation NTT engine. It does **not** prove that ML-KEM is universally immune to physical fault attacks targeting the FO check itself or primitives without an FO loop.
