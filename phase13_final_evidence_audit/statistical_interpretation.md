# Statistical Interpretation & Evidence Reconciliation

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Scope:** Per-Target Confidence Intervals, Denominator Accounting, and Pooling Justification  

---

## 1. Operational Definitions

To prevent circular reasoning, the audit enforces strict operational definitions:

- **Operational Hypothesis $H_1$ (Internal False Recovery):**  
  An internal property of the recovery verifier where it reports successful recovery (`recovered_count > 0` or status `0x5A5A5A5A`), but the recovered arithmetic polynomial state differs from an independently computed fault-free reference:
  $$H_1 \iff (\text{Verifier Declares Success}) \land (\mathbf{r}_{\text{recovered}} \ne \mathbf{r}_{\text{reference}})$$
- **Operational Hypothesis $H_2$ (Accepted Invalid Output / Silent Data Corruption):**  
  An API-level cryptographic failure where `mlkem768_dec_monitored` emits an invalid shared secret ($K_{\text{out}} \ne K_{\text{valid}}$), yet accepts it as valid without triggering implicit rejection:
  $$H_2 \iff (\text{Status} = \text{0x5A5A5A5A} \land K_{\text{out}} \ne K_{\text{valid}}) \lor (K_{\text{out}} \ne K_{\text{valid}} \land K_{\text{out}} \ne K_{\text{rej}})$$

---

## 2. Target-by-Target Recalculation Table

*Sample size $N=100$ per target. All confidence intervals are two-sided 95% Wilson score intervals.*

| Target ID | Description | Execution Path | Armed | Trig. | $H_1$ Count / $N$ | $H_1$ Rate | $H_1$ 95% Wilson CI | $H_2$ Count / $N$ | $H_2$ Rate | $H_2$ 95% Wilson CI |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **F1** | Saved Operand Bitflip | Harness Model | 100 | 100 | 98 / 100 | **98.0%** | [93.0%, 99.4%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F2** | Snapshot Additive Bias (+100) | Harness Model | 100 | 100 | 70 / 100 | **70.0%** | [60.4%, 78.1%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F3** | Persistent Count Zeroing | Harness Model | 100 | 100 | 100 / 100 | **100.0%** | [96.3%, 100.0%]| 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F4** | Transient Butterfly Fault | **Production Binary** | 100 | 100 | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F5A**| Recurring Bit-Inversion | **Production Binary** | 100 | 100 | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F5B**| Software Force-Value Model | **Production Binary** | 100 | 100 | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F6** | Verifier Flag Forced Pass | Harness Model | 100 | 100 | 100 / 100 | **100.0%** | [96.3%, 100.0%]| 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F7** | Retry Arithmetic Glitch | Harness Model | 100 | 100 | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F8** | Verifier Operand Corrupt | Harness Model | 100 | 100 | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F9** | DSPC Correlated Linear | Harness Model | 100 | 100 | 93 / 100 | **93.0%** | [86.3%, 96.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F10**| DSPC Control Bypass | Harness Model | 100 | 100 | 100 / 100 | **100.0%** | [96.3%, 100.0%]| 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F11**| DSPC Single-Bit Flip | Harness Model | 100 | 100 | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |
| **F12**| Clean Baseline Control | **Production Binary** | 0 | 0 | 0 / 100 | **0.0%** | [0.0%, 3.6%] | 0 / 100 | **0.0%** | [0.0%, 3.6%] |

---

## 3. Denominator Accounting & Pooling Justification

### 3.1 The $H_1$ Denominator (Why Clean Controls and Inapplicable Scenarios are Excluded)
- **Exclusion of Clean Baseline (F12):**  
  In F12, `armed = 0` and `triggered = 0`. No fault was injected, and the recovery monitor was never invoked (`recovered_count = 0`). Evaluating recovery-verifier failure on trials where recovery was never exercised is mathematically invalid and would artificially depress the observed failure rate.
- **Exclusion of Genuine Recovery (F4):**  
  Under transient bit-flips, the native monitor recomputes the butterfly with a clean twiddle factor. The recomputed state matches the reference bit-for-bit ($100/100$). Because recovery is mathematically valid, $H_1 = 0$.
- **Exclusion of Safe Fail-Stop Runs (F5A, F5B, F7, F8, F11):**  
  In persistent and detected scenarios, the verifier correctly flags errors and aborts execution (`persistent_count > 0` or status `0xFFFFFFFF`). Because the verifier does **not** declare recovery, it does not commit false recovery ($H_1 = 0$).
- **The Vulnerable Model Cohort (F1, F2, F3, F6, F9, F10):**  
  These 6 targets specifically test whether an in-place snapshot verifier can be blinded by corrupting its reference inputs or control predicates:
  $$\sum k_{H1} = 98 + 70 + 100 + 100 + 93 + 100 = 561$$
  $$\text{Pooled } H_1 \text{ Rate} = \frac{561}{600} = \mathbf{93.5\%} \quad (95\% \text{ Wilson CI: } [91.2\%, 95.2\%])$$

### 3.2 The $H_2$ Denominator (Why All Trials are Included)
- Unlike $H_1$ (an internal verifier property), $H_2$ evaluates an end-to-end API invariant. Every caller invoking `mlkem768_dec_monitored` relies on the guarantee that an incorrect shared secret will never be returned as valid under any circumstances.
- Across all 13 evaluated targets (100 trials each = 1,300 trials total):
  $$\sum k_{H2} = 0$$
  $$\text{Pooled } H_2 \text{ Rate} = \frac{0}{1,300} = \mathbf{0.0\%} \quad (95\% \text{ Wilson CI: } [0.0\%, 0.28\%])$$

---

## 4. Epistemological Caveat on Zero-Event Observations

> **Auditor Caveat on $H_2 = 0.0\%$:**  
> An observed count of $0 / 1,300$ does **not** prove that Silent Data Corruption is mathematically impossible. It demonstrates that under the evaluated parameter space and fault models, the probability of SDC is bounded by the upper Wilson confidence limit ($p \le 0.28\%$). It does not rule out physical fault attacks targeting the comparison instruction directly.
