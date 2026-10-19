# Statistical Interpretation & Rigorous Denominator Accounting

**Auditor:** Skeptical Cryptographic Implementation Auditor  
**Date:** October 2026  
**Scope:** Reconciled Statistical Recalculation of Hypotheses $H_1$ and $H_2$ Across Evaluated Trials  

---

## 1. Statistical Methodology

### 1.1 Wilson Score Confidence Intervals
For every binomial proportion $\hat{p} = k/n$, two-sided 95% confidence intervals are calculated using the Wilson score method without continuity correction:
$$w = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$
where $z = 1.95996398454$. The Wilson score interval provides superior coverage probability over the Wald interval for extreme proportions near 0% and 100%.

### 1.2 Epistemological Caveat on Pooling
Pooling heterogeneous fault scenarios (e.g. combining a transient butterfly bit flip with an artificial register wipe of `persistent_count`) into a single unweighted aggregate violates the assumption of identically distributed trials. Therefore, **per-target statistics are primary**, while pooled figures represent descriptive summaries across defined subsets.

---

## 2. Reconciled Target-by-Target Statistical Table

*Sample size $N=100$ per target. All intervals are two-sided 95% Wilson score intervals.*

| Target | Description | Execution Path | Armed | Trig. | $H_1$ Count / $N$ | $H_1$ Rate | $H_1$ 95% Wilson CI | $H_2$ Count / $N$ | $H_2$ Rate | $H_2$ 95% Wilson CI |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **F1** | Saved Operand Bitflip | Harness Model | 100 | 100 | 98 / 100 | **98.0%** | [93.0%, 99.4%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F2** | Snapshot Additive Bias (+100) | Harness Model | 100 | 100 | 70 / 100 | **70.0%** | [60.4%, 78.1%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F3** | Persistent Count Zeroing | Harness Model | 100 | 100 | 100 / 100 | **100.0%** | [96.3%, 100.0%]| 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F4** | Transient Butterfly Fault | **Production Object** | 100 | 100 | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F5A**| Recurring Bit-Inversion | **Production Object** | 100 | 100 | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F5B**| Hardware Stuck-At-Zero | **Production Object** | 100 | 100 | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F6** | Verifier Flag Forced Pass | Harness Model | 100 | 100 | 100 / 100 | **100.0%** | [96.3%, 100.0%]| 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F7** | Retry Arithmetic Glitch | Harness Model | 100 | 100 | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F8** | Verifier Operand Corrupt | Harness Model | 100 | 100 | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F9** | DSPC Correlated Linear | Harness Model | 100 | 100 | 93 / 100 | **93.0%** | [86.3%, 96.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F10**| DSPC Control Bypass | Harness Model | 100 | 100 | 100 / 100 | **100.0%** | [96.3%, 100.0%]| 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F11**| DSPC Single-Bit Flip | Harness Model | 100 | 100 | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F12**| Clean Baseline Control | **Production Object** | 0 | 0 | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |

---

## 3. Detailed Denominator Accounting

### 3.1 Denominator Justification for $H_1$ (Internal False Recovery)
- **Mathematical Definition:**
  $$H_1 \iff (\text{Verifier Declares Success}) \land (\mathbf{r}_{\text{recovered}} \ne \mathbf{r}_{\text{reference}})$$
- **Why Clean Controls (F12) are Excluded from the $H_1$ Denominator:**  
  In F12, no fault was injected (`armed = 0`, `triggered = 0`), and the native monitor never executed a recovery routine (`recovered_count = 0`). Evaluating "recovery verifier failure" on trials where no recovery was attempted is methodologically invalid and would artificially depress the observed failure rate.
- **Why Genuine Recovery (F4) is Excluded from the $H_1$ Numerator:**  
  Under transient bit-flips, the native recovery monitor successfully recovers the computation. The recovered arithmetic state matches the fault-free reference bit-for-bit ($100/100$). Because recovery is mathematically valid, $H_1 = 0$.
- **Why Safe Fail-Stop Runs (F5A, F5B, F7, F8, F11) are Excluded from the $H_1$ Numerator:**  
  In persistent and detected scenarios, the verifier correctly flags unrecoverable errors and aborts execution (`persistent_count > 0` or status `0xFFFFFFFF`). Because the verifier does **not** declare recovery, it does not commit false recovery ($H_1 = 0$).
- **Reconciliation of the $561 / 600$ Aggregate:**  
  The 6 targets modeling in-place snapshot verifier vulnerability (F1, F2, F3, F6, F9, F10) yield:
  $$\sum k_{H1} = 98 + 70 + 100 + 100 + 93 + 100 = 561$$
  $$\text{Pooled } H_1 \text{ Rate} = \frac{561}{600} = \mathbf{93.5\%} \quad (95\% \text{ Wilson CI: } [91.2\%, 95.2\%])$$

### 3.2 Denominator Justification for $H_2$ (Accepted Invalid Shared Secret)
- **Mathematical Definition:**
  $$H_2 \iff (\text{Status} = \text{SUCCESS} \land K_{\text{out}} \ne K_{\text{valid}}) \lor (K_{\text{out}} \ne K_{\text{valid}} \land K_{\text{out}} \ne K_{\text{rej}})$$
- **Why All Trials are Included in the $H_2$ Denominator:**  
  Unlike $H_1$ (an internal subcomponent metric), $H_2$ evaluates an end-to-end API invariant. Every caller invoking `mlkem768_dec_monitored` relies on the guarantee that an incorrect shared secret will never be returned as valid under any circumstances.
- **Reconciliation of the $0 / 1,300$ Aggregate:**  
  Across all 13 evaluated targets (100 trials each = 1,300 trials total):
  $$\sum k_{H2} = 0$$
  $$\text{Pooled } H_2 \text{ Rate} = \frac{0}{1,300} = \mathbf{0.0\%} \quad (95\% \text{ Wilson CI: } [0.0\%, 0.28\%])$$

---

## 4. Key Takeaways & Rigorous Conclusions

1. **$H_1$ and $H_2$ are Statistically Decoupled:**  
   Internal false recovery is frequent ($93.5\%$) in software models where snapshots are compromised, but protocol-level silent data corruption is completely absent ($0.0\%$).
2. **Empirical Bound on SDC:**  
   An observed rate of $0 / 1,300$ does not constitute mathematical proof that SDC is impossible. It proves that the probability of SDC is bounded by the upper Wilson confidence limit ($p \le 0.28\%$) under the tested single-shot and recurring fault models in the NTT engine.
