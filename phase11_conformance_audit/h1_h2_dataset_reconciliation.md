# Complete H1/H2 Dataset Reconciliation and Statistical Audit

**Auditor:** Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Scope:** Raw Evidence Reconciliation across Phases 5, 6, 7, 8, 9, 10, and 11  

---

## 1. Traceability of Primary Trial Datasets

To resolve all discrepancies between narrative claims and raw CSV files, every included dataset was indexed and traced to its origin:

| Phase | Filename | Row Count | Target Coverage | Execution Nature |
| :--- | :--- | :---: | :--- | :--- |
| **Phase 5** | `phase5_recovery_trust_audit/raw_trial_results.csv` | 1,300 | FT1 to FT10 | Model simulations of verifier corruption |
| **Phase 6** | `phase6_verifier_falsification/raw_trial_results.csv` | 1,200 | F1 to F12 | Independent test harness simulating snapshot corruption |
| **Phase 7** | `phase7_independent_claim_audit/derived_corrected_trial_results.csv` | 1,200 | F1 to F12 | Derived audit matrix auditing Phase 6 raw records |
| **Phase 8** | `phase8_production_path_audit/revised_h1_h2_results.md` | 1,200 | F1 to F12 | Formal separation of production objects vs harness models |
| **Phase 9** | `phase9_reproducibility_audit/raw_trial_results.csv` | 300 | F12, F4, F5 | Production object execution (identified F12 labeling bug) |
| **Phase 10**| `phase10_corrected_reproduction/raw_production_trials.csv` | 400 | F12, F4, F5A, F5B | Corrected production object execution |
| **Phase 11**| `phase11_conformance_audit/fault_output_revalidation.csv` | 400 | F12, F4, F5A, F5B | Production execution validated against clean-room oracle |

---

## 2. Reconstructed Target-by-Target Reconciliation

*All confidence intervals are 95% two-sided Wilson score intervals ($N=100$ per target).*

| Target | Target Description | Execution Environment | Total Trials | Armed | Triggered | $H_1$ Numerator / Denominator | $H_1$ Point Est. [95% CI] | $H_2$ Numerator / Denominator | $H_2$ Point Est. [95% CI] | Pooled $H_1$ Status |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **F1** | Saved Operand Bitflip | Harness Model | 100 | 100 | 100 | 98 / 100 | 98.0% [93.0, 99.4] | 0 / 100 | 0.0% [0.0, 3.6] | **Included** |
| **F2** | Snapshot Additive Bias (+100) | Harness Model | 100 | 100 | 100 | 70 / 100 | 70.0% [60.4, 78.1] | 0 / 100 | 0.0% [0.0, 3.6] | **Included** |
| **F3** | Persistent Count Zeroing | Harness Model | 100 | 100 | 100 | 100 / 100 | 100.0% [96.3, 100.0]| 0 / 100 | 0.0% [0.0, 3.6] | **Included** |
| **F4** | Transient Butterfly Fault | **Production Object** | 100 | 100 | 100 | 0 / 100 | 0.0% [0.0, 3.6] | 0 / 100 | 0.0% [0.0, 3.6] | **Excluded (Genuine)** |
| **F5A**| Recurring Bit-Inversion | **Production Object** | 100 | 100 | 100 | 0 / 100 | 0.0% [0.0, 3.6] | 0 / 100 | 0.0% [0.0, 3.6] | **Excluded (Fail-Stop)**|
| **F5B**| Hardware Stuck-At-Zero | **Production Object** | 100 | 100 | 100 | 0 / 100 | 0.0% [0.0, 3.6] | 0 / 100 | 0.0% [0.0, 3.6] | **Excluded (Fail-Stop)**|
| **F6** | Verifier Flag Forced Pass | Harness Model | 100 | 100 | 100 | 100 / 100 | 100.0% [96.3, 100.0]| 0 / 100 | 0.0% [0.0, 3.6] | **Included** |
| **F7** | Retry Arithmetic Glitch | Harness Model | 100 | 100 | 100 | 0 / 100 | 0.0% [0.0, 3.6] | 0 / 100 | 0.0% [0.0, 3.6] | **Excluded (Detected)**|
| **F8** | Verifier Operand Corrupt | Harness Model | 100 | 100 | 100 | 0 / 100 | 0.0% [0.0, 3.6] | 0 / 100 | 0.0% [0.0, 3.6] | **Excluded (Detected)**|
| **F9** | DSPC Correlated Linear | Harness Model | 100 | 100 | 100 | 93 / 100 | 93.0% [86.3, 96.6] | 0 / 100 | 0.0% [0.0, 3.6] | **Included** |
| **F10**| DSPC Control Bypass | Harness Model | 100 | 100 | 100 | 100 / 100 | 100.0% [96.3, 100.0]| 0 / 100 | 0.0% [0.0, 3.6] | **Included** |
| **F11**| DSPC Single-Bit Flip | Harness Model | 100 | 100 | 100 | 0 / 100 | 0.0% [0.0, 3.6] | 0 / 100 | 0.0% [0.0, 3.6] | **Excluded (Detected)**|
| **F12**| Clean Baseline Control | **Production Object** | 100 | 0 | 0 | 0 / 100 | 0.0% [0.0, 3.6] | 0 / 100 | 0.0% [0.0, 3.6] | **Excluded (Clean)** |

---

## 3. Detailed Denominator Accounting & Reconciliation

### 3.1 The $H_1$ Denominator (Why Clean Controls and Incompatible Faults are Excluded)
- **Definition of $H_1$:** Internal False Recovery occurs when the monitor declares successful recovery (`recovered_count++` or `MLK_STATUS_SUCCESS`), but the recovered arithmetic computation differs from the fault-free reference:
  $$H_1 \iff (\text{Verifier Declares Success}) \land (\mathbf{r}_{\text{recovered}} \ne \mathbf{r}_{\text{reference}})$$
- **Exclusion of Clean Baseline (F12):** Clean controls have `armed = 0` and `triggered = 0`. No fault is injected, and the native monitor never initiates a recovery procedure (`recovered_count = 0`). Including F12 in the denominator of an internal recovery verifier failure rate would artificially dilute the vulnerability metric by adding trials where recovery was never exercised.
- **Exclusion of Genuine Recovery (F4):** Under transient faults in the production object, the recovery verifier recomputes the butterfly with a clean twiddle factor. The recomputed state matches the fault-free reference bit-for-bit ($100/100$). Because recovery is genuine and mathematically correct, $H_1 = 0$.
- **Exclusion of Safe Fail-Stop (F5A, F5B, F7, F8, F11):** In these targets, the monitor or verifier correctly detects that the fault is persistent or unrecoverable. The verifier declares failure (`persistent_count++` or fail-stop status `0xFFFFFFFF`). Because the verifier does **not** declare recovery, it is not a false recovery event ($H_1 = 0$).
- **The Vulnerable Model Cohort (F1, F2, F3, F6, F9, F10):**  
  These 6 targets specifically test whether an in-place snapshot verifier can be blinded by corrupting its reference inputs or control predicates.
  - Numerator: $98 + 70 + 100 + 100 + 93 + 100 = 561$
  - Denominator: $6 \times 100 = 600$
  - Pooled Rate: **93.5% (561 / 600)**
  - 95% Wilson Score Interval: **[91.2%, 95.2%]**

### 3.2 The $H_2$ Denominator (Why All Trials are Included)
- **Definition of $H_2$:** Silent Data Corruption / Accepted Incorrect Key occurs when the complete decapsulation routine emits an invalid shared secret that is accepted as legitimate:
  $$H_2 \iff (\text{Status} = \text{0x5A5A5A5A} \land K_{\text{out}} \ne K_{\text{valid}}) \lor (K_{\text{out}} \ne K_{\text{valid}} \land K_{\text{out}} \ne K_{\text{rej}})$$
- **Universal Scope:** Unlike $H_1$, $H_2$ is an API-level guarantee. Every single decapsulation execution—whether clean, transiently faulted, persistently faulted, or executed under software-modeled verifier blindness—must never accept an invalid key.
- **Pooled $H_2$ Metric:**
  - Total Trials Evaluated across 13 Targets: $N = 1,300$
  - Total Accepted Incorrect Keys: **0**
  - Point Estimate: **0.0% (0 / 1,300)**
  - 95% Wilson Score Interval: **[0.0%, 0.28%]**

---

## 4. Reconciliation of Historical Discrepancies

1. **Phase 8 Text Typo ($461$ vs $561$):**  
   In Phase 8 `revised_h1_h2_results.md` Section 3.1, the text noted "Occurs in 461 of 1,200 trials", whereas the table rows summed to $98 + 70 + 100 + 100 + 93 + 100 = 561$. Phase 10 audited and corrected this clerical error to $561 / 600$.
2. **Phase 9 Target F12 Labeling Bug:**  
   Phase 9's automated harness logged Target F12 outcomes as `GENUINE_RECOVERY` because it checked `status == 0x5A5A5A5A` without asserting `mismatch_count == 0` and `recovered_count == 0`. Phase 10 rectified the classification logic, establishing `CLEAN_SUCCESS` for clean controls.
3. **Phase 10 Oracle Circularity:**  
   Phase 10 evaluated rejection keys by calling `mlkem768_shake256` from the production object under test. Phase 11 eliminated this circularity by executing the entire suite against an independent clean-room Keccak-f[1600] oracle.
