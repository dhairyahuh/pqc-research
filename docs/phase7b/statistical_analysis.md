# Phase 7B Statistical Analysis and Confidence Interval Reconciliation

**Auditor:** Independent Statistical and Empirical Reviewer  
**Dataset:** `results/phase7b/raw/phase7b_raw_trials.json` (1,200 individual trials)  
**Date:** October 2026  

---

## 1. Statistical Methodology

For empirical detection experiments with binary outcomes (detected vs undetected), sample estimates $\hat{p} = k/n$ must be presented with appropriate binomial confidence intervals. We employ the **Wilson Score Interval** without continuity correction, which provides robust coverage for both extreme probabilities ($p \approx 0$ or $p \approx 1$) and moderate sample sizes:

$$w = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$

where $z = 1.96$ for a two-sided 95% confidence level.

---

## 2. Recomputed Detection Table with Wilson 95% Intervals

| Fault Class | Total Trials ($n$) | DMR Detections ($k$) | DMR Empirical Rate | DMR 95% CI | Layered Detections ($k$) | Layered Empirical Rate | Layered 95% CI |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Class 1 (Intermediate T)** | 150 | 145 | 96.7% | **[92.4%, 98.6%]** | 145 | 96.7% | **[92.4%, 98.6%]** |
| **Class 2 (Twiddle Zeta)** | 150 | 150 | 100.0% | **[97.5%, 100.0%]** | 150 | 100.0% | **[97.5%, 100.0%]** |
| **Class 3 (Output Add Reg)** | 150 | 148 | 98.7% | **[95.3%, 99.6%]** | 150 | 100.0% | **[97.5%, 100.0%]** |
| **Class 4 (Correlated Mult)** | 150 | 150 | 100.0% | **[97.5%, 100.0%]** | 150 | 100.0% | **[97.5%, 100.0%]** |
| **Class 5 (Pre-Invoc Input)** | 150 | 0 | **0.0%** | **[0.0%, 2.5%]** | 150 | 100.0% | **[97.5%, 100.0%]** |
| **Class 6 (Checker Perturb)** | 150 | 0 | **0.0%** | **[0.0%, 2.5%]** | 150 | 100.0% | **[97.5%, 100.0%]** |
| **Class 7 (Control FO Gate)** | 150 | 0 | **0.0%** | **[0.0%, 2.5%]** | 150 | 100.0% | **[97.5%, 100.0%]** |
| **Class 8 (Persistent Stuck)** | 150 | 0 | **0.0%** | **[0.0%, 2.5%]** | 150 | 100.0% | **[97.5%, 100.0%]** |

---

## 3. Critical Statistical Observations

1. **Observed 100% vs True Probability:**
   - Observing 150 successes in 150 trials establishes that the true detection probability is at least **97.5%** with 95% confidence. It does **not** prove that the underlying probability is mathematically 1.000 (100.0%), because untested corner-case perturbations could still exist.
2. **Observed 0% vs True Probability:**
   - Observing 0 detections in 150 trials establishes an upper bound on detection probability of **2.5%** with 95% confidence.
3. **Statistical Sample Size:**
   - $n = 150$ per class is sufficient to establish clear statistical separation ($p < 10^{-15}$) between the Layered Architecture and DMR on Classes 5, 6, 7, and 8.
