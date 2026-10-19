# Revised H1 and H2 Evidence and Results Matrix

**Auditor:** Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Target:** Rigorous Audit of Hypotheses H1 (Internal False Recovery) and H2 (Accepted Incorrect Output)  

---

## 1. Formal Hypothesis Definitions

To prevent circular reasoning or classification conflation, the audit strictly decouples the internal monitor behavior from the end-to-end cryptographic result:

- **Hypothesis H1 (Internal False Recovery):**  
  The internal recovery monitor reports successful recovery (`diff_retry == 0 && sum_retry == 0`, incrementing `recovered_count` or returning `MLK_STATUS_SUCCESS`) while the recovered butterfly computational state differs from an independently computed fault-free reference:
  $$H_1 \iff (\text{Monitor Declares Success}) \land (\mathbf{r}_{\text{recovered}} \ne \mathbf{r}_{\text{reference}})$$

- **Hypothesis H2 (Accepted Incorrect Output / Silent Data Corruption):**  
  The complete cryptographic operation (`mlkem768_dec_monitored`) returns a shared secret $K_{\text{out}}$ that differs from the expected valid shared secret $K_{\text{valid}}$, yet is accepted as successful without triggering implicit or explicit rejection:
  $$H_2 \iff (\text{Status} = \text{SUCCESS}) \land (K_{\text{out}} \ne K_{\text{valid}})$$

---

## 2. Re-evaluated Results Matrix (1,200 Trials)

*All confidence intervals represent 95% Wilson score intervals ($N=100$ per target).*

| Target | Description | Execution Path | Injected & Triggered | Monitor Blind / Declares Success | Independent Oracle False Recovery ($H_1$) | Safe Fail-Stop Rejection | Genuine Recovery | Downstream FO Rejection | Accepted Incorrect Output ($H_2$) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **F1** | Saved Operand Bitflip | Harness Model | 100/100 | **98.0%** [93.0, 99.4] | **98.0%** [93.0, 99.4] | 2.0% [0.6, 7.0] | 0.0% [0.0, 3.6] | 98.0% [93.0, 99.4] | **0.0%** [0.0, 3.6] |
| **F2** | Snapshot Additive Bias (+100) | Harness Model | 100/100 | **100.0%** [96.3, 100.0] | **70.0%** [60.4, 78.1] | 0.0% [0.0, 3.6] | **30.0%** [21.9, 39.6] | 70.0% [60.4, 78.1] | **0.0%** [0.0, 3.6] |
| **F3** | Stride / Persistent Count Zero | Harness Model | 100/100 | **100.0%** [96.3, 100.0] | **100.0%** [96.3, 100.0] | 0.0% [0.0, 3.6] | 0.0% [0.0, 3.6] | 100.0% [96.3, 100.0] | **0.0%** [0.0, 3.6] |
| **F4** | Transient Fault with Retry | **Production Object** | 100/100 | 0.0% [0.0, 3.6] | **0.0%** [0.0, 3.6] | 0.0% [0.0, 3.6] | **100.0%** [96.3, 100.0] | 0.0% [0.0, 3.6] | **0.0%** [0.0, 3.6] |
| **F5** | Stuck-At Persistent Fault | **Production Object** | 100/100 | 0.0% [0.0, 3.6] | **0.0%** [0.0, 3.6] | **100.0%** [96.3, 100.0] | 0.0% [0.0, 3.6] | 0.0% [0.0, 3.6] | **0.0%** [0.0, 3.6] |
| **F6** | Verifier Flag Forced Pass | Harness Model | 100/100 | **100.0%** [96.3, 100.0] | **100.0%** [96.3, 100.0] | 0.0% [0.0, 3.6] | 0.0% [0.0, 3.6] | 100.0% [96.3, 100.0] | **0.0%** [0.0, 3.6] |
| **F7** | Retry Arithmetic Glitch | Harness Model | 100/100 | 0.0% [0.0, 3.6] | **0.0%** [0.0, 3.6] | **100.0%** [96.3, 100.0] | 0.0% [0.0, 3.6] | 0.0% [0.0, 3.6] | **0.0%** [0.0, 3.6] |
| **F8** | Verifier Operand Corrupt | Harness Model | 100/100 | 0.0% [0.0, 3.6] | **0.0%** [0.0, 3.6] | **100.0%** [96.3, 100.0] | 0.0% [0.0, 3.6] | 0.0% [0.0, 3.6] | **0.0%** [0.0, 3.6] |
| **F9** | DSPC Correlated Linear | Harness Model | 100/100 | **93.0%** [86.3, 96.6] | **93.0%** [86.3, 96.6] | 7.0% [3.4, 13.7] | 0.0% [0.0, 3.6] | 93.0% [86.3, 96.6] | **0.0%** [0.0, 3.6] |
| **F10**| DSPC Control Bypass | Harness Model | 100/100 | **100.0%** [96.3, 100.0] | **100.0%** [96.3, 100.0] | 0.0% [0.0, 3.6] | 0.0% [0.0, 3.6] | 100.0% [96.3, 100.0] | **0.0%** [0.0, 3.6] |
| **F11**| DSPC Single-Bit Flip | Harness Model | 100/100 | 0.0% [0.0, 3.6] | **0.0%** [0.0, 3.6] | **100.0%** [96.3, 100.0] | 0.0% [0.0, 3.6] | 0.0% [0.0, 3.6] | **0.0%** [0.0, 3.6] |
| **F12**| Clean Baseline Control | **Production Object** | 0/100 | 0.0% [0.0, 3.6] | **0.0%** [0.0, 3.6] | 0.0% [0.0, 3.6] | 0.0% [0.0, 3.6] | 0.0% [0.0, 3.6] | **0.0%** [0.0, 3.6] |

---

## 3. Key Observations & Findings

### 1. Hypothesis H1 Status
- **Occurs in 461 of 1,200 trials (38.4% overall; 70% to 100% in vulnerable targets F1, F2, F3, F6, F9, F10).**
- When internal snapshots or monitor state variables are corrupted, the recovery verifier algorithmically clears the operation because it verifies the corrupted computation against its own corrupted snapshot.
- **Clarification:** Target F4 does **not** exhibit H1. Target F4 is a genuine, verified recovery ($100/100$).

### 2. Hypothesis H2 Status
- **0.0% across all 1,200 trials (0/1,200, 95% CI: [0.0%, 0.31%]).**
- Even when the internal monitor is completely blinded (as in F1, F2, F3, F6, F9, F10), the outer Fujisaki-Okamoto transform in `kem.c` prevents the acceptance of an incorrect shared secret.
- In every case where the final ciphertext differed from the genuine ciphertext, the FO re-encryption comparison (`mlk_ct_memcmp`) evaluated to non-zero, triggering safe implicit rejection ($K = \text{SHAKE256}(z \parallel ct)$).

### 3. Separation of Production Code from Harness Models
- **F4, F5, F12** were executed against the **authentic compiled production objects** (`bin/obj/mlkem_fault_hooks.o` + `bin/obj/mlkem768_inst.o`).
- **F1, F2, F3, F6, F7, F8, F9, F10, F11** were executed through a **harness-level simulation** of operand and register corruption, because the in-tree production source contains no hooks into stack-passed snapshot variables.
