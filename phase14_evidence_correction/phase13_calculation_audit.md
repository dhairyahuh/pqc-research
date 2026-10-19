# Forensic Audit of the Phase 13 Calculation Pipeline

**Auditor:** Skeptical Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Subject:** Verification of Phase 13 Claims, Metrics, and Data Derivation Pipelines  
**Baseline Artifacts Audited:**
- `phase13_final_evidence_audit/h1_h2_recalculation.csv`
- `phase13_final_evidence_audit/production_trial_recalculation.csv`
- `phase13_final_evidence_audit/artifact_traceability_matrix.csv`
- `phase13_final_evidence_audit/claim_evidence_matrix.csv`
- Underlying historical datasets (Phases 5, 6, 7, 8, 9, 10, 11, 12)

---

## 1. Executive Summary

Phase 13 purported to perform an "independent experimental recalculation" of all fault-resilience hypotheses ($H_1$ and $H_2$) across ML-KEM-768. 

This independent forensic audit reveals a critical methodological defect: **Phase 13 did NOT calculate its primary hypothesis rates from raw trial outcomes.** 

Instead, Phase 13:
1. **Hardcoded a Python array of legacy counts** inherited directly from narrative tables written in Phase 8 (`phase8_production_path_audit/revised_h1_h2_results.md`).
2. Performed closed-form Wilson score interval arithmetic over these pre-set integers.
3. Labeled the resulting CSV ([`h1_h2_recalculation.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/h1_h2_recalculation.csv)) as an "independent recalculation from raw evidence."
4. Directly contradicted the actual raw records stored in [`derived_corrected_trial_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/derived_corrected_trial_results.csv) across multiple targets (e.g., misreporting Target F3 as 100% false recovery when raw records document 0%, and Target F7 as 0% when raw records document 94%).
5. Formulated an invalid $H_2$ Boolean expression in [`artifact_traceability_matrix.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/artifact_traceability_matrix.csv) that falsely classifies safe fail-stop aborts as Silent Data Corruption.

An arithmetic re-computation of hardcoded integers must never be presented as an empirical recalculation of experimental data.

---

## 2. Metric-by-Metric Forensic Audit Matrix

The table below examines every metric reported across Phase 13's summary artifacts, tracing each value back to its origin and determining whether it was derived from raw data rows or entered from historical narratives.

| Target ID & Name | Phase 13 Metric Reported | Alleged Source Dataset | Phase 13 Numerator / Denominator | Outcome Classification Rule Used by Phase 13 | Truly Derived from Raw Rows? | Raw CSV Row Reality (`derived_corrected_trial_results.csv` or `production_trial_recalculation.csv`) | Discrepancy & Forensic Finding |
| :--- | :--- | :--- | :---: | :--- | :---: | :---: | :--- |
| **F1** (Saved Operand Bitflip) | $H_1 = 98.0\%$ [93.0, 99.4] | Historical Phase 7 | 98 / 100 | Hardcoded value in script | **NO** (Hardcoded) | `v_pass=98`, `ret_match=0`, `h1_col=98` | Numerical value happens to match raw rows, but was not parsed dynamically. |
| **F2** (Snapshot Additive Bias) | $H_1 = 70.0\%$ [60.4, 78.1] | Historical Phase 7 | 70 / 100 | Downstream FO rejection count copied as $H_1$ | **NO** (Hardcoded) | `v_pass=100`, `ret_match=0`, `h1_col=100`, `rej_FO=70`, `rec_gen=30` | **Severe Error**: Phase 13 reported the downstream FO rejection count (70) instead of verifier blindness ($V_{\text{pass}} = 100$). The local verifier was blind in 100/100 trials. |
| **F3** (Persistent Count Zeroing) | $H_1 = 100.0\%$ [96.3, 100.0] | Historical Phase 7 | 100 / 100 | Manual narrative assumption from Phase 8 | **NO** (Fabricated) | `v_pass=0`, `ret_match=0`, `h1_col=0`, `safe_rej=98`, `inconcl=2` | **Catastrophic Error**: Phase 13 reported 100% false recovery. The raw CSV contains **0/100** verifier passes. The arithmetic difference check caught the glitch; the verifier never passed. |
| **F4** (Transient Butterfly Fault) | $H_1 = 0.0\%$ [0.0, 3.7] | Fresh Production Binary | 0 / 100 | `trig>0 && valid_match && status==0x5A5A5A5A && rec>0 && pers==0` | **YES** | 100 trials `GENUINE_RECOVERY` (`rec=1, pers=0`) | Legitimately executed and derived from `production_reproducer.c`. |
| **F5A** (Recurring Bit-Inversion) | $H_1 = 0.0\%$ [0.0, 3.7] | Fresh Production Binary | 0 / 100 | `trig>0 && rej_match && status==0xFFFFFFFF && pers>0 && !valid_match` | **YES** | 100 trials `SAFE_FAIL_STOP` (`pers=1, status=0xFFFFFFFF`) | Legitimately executed and derived from `production_reproducer.c`. |
| **F5B** (Software Force-Value Model) | $H_1 = 0.0\%$ [0.0, 3.7] | Fresh Production Binary | 0 / 100 | `trig>0 && rej_match && status==0xFFFFFFFF && pers>0 && !valid_match` | **YES** | 100 trials `SAFE_FAIL_STOP` (`pers=1, status=0xFFFFFFFF`) | Legitimately executed. Note: Labeled in Phase 13 as software model, correctly avoiding physical stuck-at claims. |
| **F6** (Verifier Flag Forced Pass) | $H_1 = 100.0\%$ [96.3, 100.0] | Historical Phase 7 | 100 / 100 | Manual entry in Phase 8 narrative table | **NO** (Hardcoded) | `v_pass=99`, `ret_match=0`, `h1_col=99`, `safe_rej=1` | Discrepancy of 1 trial: raw CSV has 99/100 false passes, with 1 safe rejection. |
| **F7** (Retry Arithmetic Glitch) | $H_1 = 0.0\%$ [0.0, 3.7] | Historical Phase 7 | 0 / 100 | Phase 13 text: "Safe fail-stop detected" | **NO** (Inverted) | `v_pass=94`, `ret_match=0`, `h1_col=94`, `safe_rej=6` | **Severe Error**: Phase 13 reported F7 as 0% $H_1$ (safe fail-stop). The actual raw CSV has **94/100** verifier false passes! |
| **F8** (Verifier Operand Corrupt) | $H_1 = 0.0\%$ [0.0, 3.7] | Historical Phase 7 | 0 / 100 | Hardcoded value in script | **NO** (Hardcoded) | `v_pass=0`, `ret_match=100`, `h1_col=0`, `safe_rej=100` | Numerical count matches raw data (0/100). |
| **F9** (DSPC Correlated Linear) | $H_1 = 93.0\%$ [86.3, 96.6] | Historical Phase 7 | 93 / 100 | Copied from Phase 5 FT3/FT6/FT9 narrative | **NO** (Hardcoded) | `v_pass=100`, `ret_match=0`, `h1_col=100` | **Discrepancy**: Phase 13 inherited the obsolete 93% figure from Phase 5; the actual Phase 7 dataset exhibits 100/100. |
| **F10** (DSPC Control Bypass) | $H_1 = 100.0\%$ [96.3, 100.0] | Historical Phase 7 | 100 / 100 | Hardcoded value in script | **NO** (Hardcoded) | `v_pass=100`, `ret_match=0`, `h1_col=100` | Numerical count matches raw data (100/100). |
| **F11** (DSPC Single-Bit Flip) | $H_1 = 0.0\%$ [0.0, 3.7] | Historical Phase 7 | 0 / 100 | Hardcoded value in script | **NO** (Hardcoded) | `v_pass=0`, `ret_match=0`, `h1_col=0`, `safe_rej=100` | Numerical count matches raw data (0/100). |
| **F12** (Clean Baseline Control) | $H_1 = 0.0\%$ [0.0, 3.7] | Fresh Production Binary | 0 / 100 | `valid_match && status==0x5A5A5A5A && mismatch==0` | **YES** | 100 trials `CLEAN_SUCCESS` | Legitimately executed and derived from `production_reproducer.c`. |
| **Global Pooled $H_1$** | $H_1 = 93.5\%$ (561/600) | Selected Harness Models | 561 / 600 | Pooled sum of targets F1, F2, F3, F6, F9, F10 | **NO** (Synthetic Sum) | Sum of raw counts for these 6 targets: $98 + 100 + 0 + 99 + 100 + 100 = 497 / 600$ (82.8%) | Pooling disparate attack semantics is scientifically invalid. Furthermore, Phase 13's pooled sum of 561 relied on fabricated 100 for F3 and miscalculated 70 for F2. |
| **Global Pooled $H_2$** | $H_2 = 0.0\%$ (0/1,300) | All Phases 5–13 | 0 / 1300 | `!valid_match && (status==0x5A5A5A5A || !rej_match)` | **NO** (Conflated Datasets) | Across Phase 7 (1,200) + Prod (400): $H_2 = 0$ | The 0/1,300 numerator is empirically true under the corrected rule, but Phase 13's formula was defective and the denominator pooled non-comparable harnesses. |

---

## 3. Detailed Audit of Phase 13 Artifacts

### 3.1 `phase13_final_evidence_audit/h1_h2_recalculation.csv`
- **Origin:** Created by a script using a hardcoded array `targets_info` containing pairs `(target_id, target_name, execution_path, h1_count, ...)`.
- **Finding:** The script did not read any historical CSV file. It treated historical Phase 8 narrative tables as authoritative data.
- **Consequence:** Historical errors in Phase 8 (such as F3 being assumed 100% blind despite failing the verifier in actual execution, and F7 being assumed 0% blind despite passing the verifier in 94 trials) were canonized as verified experimental evidence.

### 3.2 `phase13_final_evidence_audit/production_trial_recalculation.csv`
- **Origin:** Generated dynamically by compiling and running `production_reproducer.c` against `bin/obj/mlkem768_inst.o` and `bin/obj/mlkem_fault_hooks.o`.
- **Finding:** This component is **sound and auditable**. The C harness executed 400 real decapsulation trials (100 each of F12, F4, F5A, F5B), re-seeded per trial, correctly recorded internal telemetry, computed independent clean-room Keccak SHA-3 oracle keys, and logged byte-exact hex representations.
- **Traceability:** The 400 rows are fully traceable and 100% reproducible bit-for-bit from source.

### 3.3 `phase13_final_evidence_audit/artifact_traceability_matrix.csv`
- **Origin:** Hand-authored markdown/CSV matrix summarizing evidence grounding.
- **Finding:** Row 9 specifies the classification rule:
  ```c
  !valid_match && (status == 0x5A5A5A5A || !rej_match)
  ```
  As proven in [`h1_h2_operational_definitions.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase14_evidence_correction/h1_h2_operational_definitions.md), this rule is logically invalid because it classifies safe fail-stop aborts (`status == 0xFFFFFFFF`) where `rej_match == 0` as Silent Data Corruption ($H_2 = 1$).

### 3.4 `phase13_final_evidence_audit/claim_evidence_matrix.csv`
- **Origin:** Hand-authored claim disposition table.
- **Finding:** Claim 5 asserts absence of SDC across 1,300 trials. While $H_2 = 0$ is supported across both the harness and production trials under the corrected formula, pooling harness simulation models with production objects to claim a single confidence bound ($[0.0\%, 0.28\%]$) obscures the fact that only 400 trials evaluated the compiled production implementation.

---

## 4. Conclusion and Remediation Mandate

1. The Phase 13 $H_1$ rate calculations for historical harness targets must be **completely retracted and replaced** with dynamic recalculations directly parsed from [`derived_corrected_trial_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/derived_corrected_trial_results.csv).
2. The defective $H_2$ Boolean rule must be **purged and replaced** with the corrected operational rule:
   $$H_2 \iff (\text{status} == 0\text{x}5\text{A}5\text{A}5\text{A}5\text{A}) \land (!\text{valid\_match})$$
3. Harness model trials and compiled production binary trials must be **strictly separated** in all summaries.
4. Arbitrary pooling across disparate targets must be eliminated.
