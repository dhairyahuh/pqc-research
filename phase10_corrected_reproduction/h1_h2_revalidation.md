# Revalidation of Hypotheses H1 and H2

**Auditor:** Skeptical Cryptographic Software Verification Researcher  
**Date:** October 2026  
**Scope:** Strict Decoupling and Statistical Revalidation of Internal vs Boundary Failures  

---

## 1. Operational Separation of H1 and H2

The audit enforces strict operational definitions to prevent conflating internal component properties with protocol-level vulnerabilities:

- **Internal False Recovery ($H_1$):**  
  An internal property of the recovery verifier where it reports successful recovery (`recovered_count++` or `MLK_STATUS_SUCCESS`) while the recovered arithmetic state differs from a fault-free reference:
  $$H_1 \iff (\text{Verifier Declares Success}) \land (\mathbf{r}_{\text{recovered}} \ne \mathbf{r}_{\text{reference}})$$

- **Silent Data Corruption ($H_2$):**  
  An end-to-end cryptographic failure where `mlkem768_dec_monitored` accepts or outputs an incorrect shared secret rather than the expected genuine key or the canonical implicit rejection key:
  $$H_2 \iff (\text{Status} = \text{0x5A5A5A5A} \land K_{\text{out}} \ne K_{\text{expected}}) \lor (K_{\text{out}} \ne K_{\text{expected}} \land K_{\text{out}} \ne K_{\text{rej}})$$

---

## 2. Target-by-Target Revalidation Table

*Sample size $N=100$ per target. Confidence intervals are two-sided 95% Wilson score intervals.*

| Target | Model / Path | Armed | Triggered | Reached Location | Internal Verifier Result | Independent Oracle Result | Final API Outcome | $H_1$ False Recovery Count | $H_2$ Accepted Incorrect Key |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **F1** | Harness Model | 100 | 100 | 100 | 98% Pass (Blind) | 98% Mismatch | 98% Downstream FO Reject | **98 / 100** [93.0, 99.4] | **0 / 100** [0.0, 3.6] |
| **F2** | Harness Model | 100 | 100 | 100 | 100% Pass (Blind) | 70% Mismatch | 30% Genuine, 70% FO Reject | **70 / 100** [60.4, 78.1] | **0 / 100** [0.0, 3.6] |
| **F3** | Harness Model | 100 | 100 | 100 | 100% Pass (Blind) | 100% Mismatch | 100% Downstream FO Reject | **100 / 100** [96.3, 100.0] | **0 / 100** [0.0, 3.6] |
| **F4** | **Production Object** | 100 | 100 | 100 | 100% Pass (Genuine) | 100% Match | 100% Genuine Recovery | **0 / 100** [0.0, 3.6] | **0 / 100** [0.0, 3.6] |
| **F5A**| **Production Object** | 100 | 100 | 100 | 100% Fail (Fail-Stop) | 100% Mismatch | 100% Safe Fail-Stop | **0 / 100** [0.0, 3.6] | **0 / 100** [0.0, 3.6] |
| **F5B**| **Production Object** | 100 | 100 | 100 | 100% Fail (Fail-Stop) | 100% Mismatch | 100% Safe Fail-Stop | **0 / 100** [0.0, 3.6] | **0 / 100** [0.0, 3.6] |
| **F6** | Harness Model | 100 | 100 | 100 | 100% Pass (Forced) | 100% Mismatch | 100% Downstream FO Reject | **100 / 100** [96.3, 100.0] | **0 / 100** [0.0, 3.6] |
| **F7** | Harness Model | 100 | 100 | 100 | 100% Fail (Detected) | 100% Mismatch | 100% Safe Fail-Stop | **0 / 100** [0.0, 3.6] | **0 / 100** [0.0, 3.6] |
| **F8** | Harness Model | 100 | 100 | 100 | 100% Fail (Detected) | 100% Mismatch | 100% Safe Fail-Stop | **0 / 100** [0.0, 3.6] | **0 / 100** [0.0, 3.6] |
| **F9** | Harness Model | 100 | 100 | 100 | 93% Pass (Bypass) | 93% Mismatch | 93% Downstream FO Reject | **93 / 100** [86.3, 96.6] | **0 / 100** [0.0, 3.6] |
| **F10**| Harness Model | 100 | 100 | 100 | 100% Pass (Skip) | 100% Mismatch | 100% Downstream FO Reject | **100 / 100** [96.3, 100.0] | **0 / 100** [0.0, 3.6] |
| **F11**| Harness Model | 100 | 100 | 100 | 100% Fail (Detected) | 100% Mismatch | 100% Safe Fail-Stop | **0 / 100** [0.0, 3.6] | **0 / 100** [0.0, 3.6] |
| **F12**| **Production Object** | 0 | 0 | 0 | N/A (Clean Run) | 100% Match | 100% Clean Success | **0 / 100** [0.0, 3.6] | **0 / 100** [0.0, 3.6] |

---

## 3. Statistical Interpretation

### 3.1 Descriptive Pooled Summary (With Explicit Assumptions)
- **$H_1$ Internal False Recovery (Software Model Targets F1, F2, F3, F6, F9, F10):**  
  Total $H_1$ events: $561 / 600$ ($93.5\%$, 95% Wilson CI: $[91.2\%, 95.2\%]$).  
  *Assumption:* Represents the pooled vulnerability of the in-place snapshot verifier arithmetic across various simulated corruption modes.
- **$H_2$ Silent Data Corruption Across All Evaluated Targets ($N=1,300$ total trials):**  
  Total $H_2$ events: $0 / 1,300$ ($0.0\%$, 95% Wilson CI: $[0.0\%, 0.28\%]$).  
  *Assumption:* Represents the empirical performance of the ML-KEM-768 decapsulation interface under the collective set of simulated and production fault models.

### 3.2 Epistemological Caveat
The observation of $0$ accepted incorrect outputs ($H_2 = 0.0\%$) proves that Silent Data Corruption was absent under the tested single-shot and recurring fault injections within the forward NTT butterfly pipeline. It does **not** constitute mathematical proof that the ML-KEM decapsulation protocol is unconditionally immune to arbitrary physical fault attacks targeting the FO comparison registers directly or exploiting microarchitectural side channels.
