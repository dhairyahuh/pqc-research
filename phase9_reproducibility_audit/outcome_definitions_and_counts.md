# Outcome Definitions, Operational Formulas, and Denominators

**Auditor:** Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Target:** Formalization of Mutually Exclusive Categorical Outcomes  

---

## 1. Operational Definitions of Mutually Exclusive Categories

To eliminate ambiguity across audit phases, every trial outcome is assigned to exactly one of the following mutually exclusive categories:

### 1. Genuine Recovery (`RECOVERED_GENUINE`)
- **Operational Definition:**  
  A fault was injected into the computational pipeline, detected by the invariant monitor, successfully corrected via in-place rollback and recomputation, verified by the recovery verifier, and the decapsulation procedure returned `0x5A5A5A5A` with a shared secret identical to the fault-free reference.
  $$\text{Outcome} = \text{Genuine Recovery} \iff (\text{Injected}) \land (\text{Detected}) \land (\text{Verifier Passed}) \land (\mathbf{r} = \mathbf{r}_{\text{ref}}) \land (K_{\text{out}} = K_{\text{expected}})$$

### 2. Safe Fail-Stop Rejection (`SAFE_FAIL_STOP`)
- **Operational Definition:**  
  The monitor or recovery verifier detected an unrecoverable fault (e.g., persistent hardware fault, stuck-at bit, invalid retry arithmetic), incremented `persistent_count`, and the decapsulation routine safely terminated with status `0xFFFFFFFF` (`MLK_DECAPS_STATUS_FAULT`), returning the canonical implicit rejection key $K_{\text{rej}} = \text{SHAKE256}(z \parallel ct)$.
  $$\text{Outcome} = \text{Safe Fail-Stop} \iff (\text{persistent\_count} > 0) \land (\text{Status} = \text{0xFFFFFFFF}) \land (K_{\text{out}} = K_{\text{rej}})$$

### 3. Downstream FO Rejection (`REJECTED_DOWNSTREAM`)
- **Operational Definition:**  
  The internal recovery monitor failed to detect the fault or was blinded by snapshot corruption, but the resulting polynomial divergence crossed the ciphertext quantization boundary. The outer Fujisaki-Okamoto re-encryption check (`mlk_ct_memcmp`) detected `ct != tmp`, set `fail = 0xFF`, returned status `0xA5A5A5A5` (`MLK_DECAPS_STATUS_REJECT`), and safely returned $K_{\text{rej}}$.
  $$\text{Outcome} = \text{Downstream FO Rejection} \iff (\text{Monitor Blind}) \land (\mathbf{ct}' \ne \mathbf{ct}) \land (\text{fail} = \text{0xFF}) \land (K_{\text{out}} = K_{\text{rej}})$$

### 4. Internal False Recovery ($H_1$)
- **Operational Definition:**  
  The internal recovery monitor reported successful recovery (`recovered_count++`, returning `MLK_STATUS_SUCCESS`) while the recovered butterfly computational state differed from an independently computed fault-free reference:
  $$H_1 \iff (\text{Monitor Declared Success}) \land (\mathbf{r}_{\text{recovered}} \ne \mathbf{r}_{\text{reference}})$$
  *Note:* $H_1$ is an internal property of the monitor. As proven in Phases 7 and 8, an internal $H_1$ event may result in either a Downstream FO Rejection (if the error diffuses to ciphertext mismatch) or a Genuine Recovery (if the error is below the quantization threshold).

### 5. Accepted Incorrect Output ($H_2$ / Silent Data Corruption)
- **Operational Definition:**  
  The complete cryptographic decapsulation procedure returned a shared secret $K_{\text{out}}$ that differed from the genuine shared secret $K_{\text{expected}}$, yet was accepted as successful without triggering fail-stop or implicit rejection:
  $$H_2 \iff (\text{Status} = \text{0x5A5A5A5A}) \land (K_{\text{out}} \ne K_{\text{expected}})$$

### 6. Fault Not Triggered
- **Operational Definition:**  
  A trial where the fault injection hook was armed, but execution terminated or bypassed the target locus without firing (`trigger_count == 0`), or an explicit uncorrupted baseline control.

### 7. Invalid or Inconclusive Trial
- **Operational Definition:**  
  A trial in which memory corruption outside the cryptographic buffer caused a crash, segfault, or undefined exit code, preventing status evaluation.

---

## 2. Denominator and Counting Formulas

All statistical rates must use explicit, justified denominators:

| Metric | Numerator | Denominator | Rationale |
| :--- | :--- | :--- | :--- |
| **Trigger Rate** | Injected Trials (`trigger_count > 0`) | Total Executed Trials ($N=100$) | Measures whether the fault harness successfully intersected execution. |
| **Monitor Blindness Rate** | Trials where Verifier Passed on Corrupted State | Injected Trials ($N=100$) | Measures internal failure of invariant monitor logic. |
| **$H_1$ False Recovery Rate** | Trials where (Monitor Passed) $\land (\mathbf{r} \ne \mathbf{r}_{\text{ref}})$ | Injected Trials ($N=100$) | Measures internal false recovery against an independent oracle. |
| **Downstream FO Rejection Rate** | Trials where `memcmp(ct, tmp) != 0` | Injected Trials ($N=100$) | Measures outer cryptographic containment. |
| **$H_2$ SDC Rate** | Accepted Incorrect Keys | Injected Trials ($N=100$) | Measures end-to-end cryptographic failure. |

---

## 3. Master Trial Counts Across All Tested Targets

*Denominators are strictly 100 trials per target (total 1,200 trials).*

| Target | Model Type | Total Trials | Injected | Genuine Recovery | Safe Fail-Stop | Downstream FO Rejection | Internal False Recovery ($H_1$) | Accepted Incorrect Key ($H_2$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **F1** | Harness Model | 100 | 100 | 0 | 2 | 98 | **98** | **0** |
| **F2** | Harness Model | 100 | 100 | 30 | 0 | 70 | **70** | **0** |
| **F3** | Harness Model | 100 | 100 | 0 | 0 | 100 | **100** | **0** |
| **F4** | **Production Object** | 100 | 100 | **100** | 0 | 0 | **0** | **0** |
| **F5** | **Production Object** | 100 | 100 | 0 | **100** | 0 | **0** | **0** |
| **F6** | Harness Model | 100 | 100 | 0 | 0 | 100 | **100** | **0** |
| **F7** | Harness Model | 100 | 100 | 0 | 100 | 0 | **0** | **0** |
| **F8** | Harness Model | 100 | 100 | 0 | 100 | 0 | **0** | **0** |
| **F9** | Harness Model | 100 | 100 | 0 | 7 | 93 | **93** | **0** |
| **F10**| Harness Model | 100 | 100 | 0 | 0 | 100 | **100** | **0** |
| **F11**| Harness Model | 100 | 100 | 0 | 100 | 0 | **0** | **0** |
| **F12**| **Production Object** | 100 | 0 | 100 | 0 | 0 | **0** | **0** |
| **Total**| — | **1,200** | **1,100** | **230** | **409** | **461** | **461** | **0** |
