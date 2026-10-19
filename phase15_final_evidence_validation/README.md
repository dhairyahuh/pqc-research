# Phase 15: Final Trial-Level Evidence Validation and Research Claim Freeze

**Auditor:** Skeptical Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Repository:** ML-KEM-768 Fault-Resilience Research (`pqc research`)  
**Scope:** Trial-Level Telemetry Recalculation, Input-Aware Classification, Recovery Verification, Discrepancy Reconciliation, and Final Claim Freeze  

---

## 1. Executive Summary

Phase 15 represents the final, trial-level verification and evidence freeze of the ML-KEM-768 fault-resilience research repository. 

Rather than launching new fault campaigns or proposing ad-hoc countermeasures, Phase 15 focused exclusively on:
1. **Validating every numerical result from raw trial rows** without hardcoded assumptions or narrative overrides.
2. **Implementing input-aware outcome classification** for Hypothesis $H_2$, distinguishing valid ciphertext decapsulation from FIPS 203 implicit rejection.
3. **Auditing individual recovery events** across all 400 production decapsulation trials (F12, F4, F5A, F5B).
4. **Reconciling all historical discrepancies** between Phase 13 and Phase 14 in a row-by-row matrix.
5. **Enacting a Formal Evidence Freeze** that defines the precise boundary of safe academic claims.

---

## 2. Directory Index of Phase 15 Deliverables

| Deliverable File | Type | Purpose & Summary Content |
| :--- | :---: | :--- |
| [`README.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase15_final_evidence_validation/README.md) | Markdown | Master overview, audit scope, method summary, and deliverable navigation index. |
| [`evidence_manifest.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase15_final_evidence_validation/evidence_manifest.csv) | CSV | SHA-256 hashes, execution tiers, provenance, and descriptions for all key repository evidence files. |
| [`h1_trial_level_recalculation.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase15_final_evidence_validation/h1_trial_level_recalculation.csv) | CSV | Trial-level $H_1$ outcomes derived from raw rows, with intermediate locus measurability status. |
| [`h2_input_aware_recalculation.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase15_final_evidence_validation/h2_input_aware_recalculation.csv) | CSV | Input-aware $H_2$ classification evaluated across valid ciphertexts, invalid ciphertexts, and status contracts. |
| [`classification_test_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase15_final_evidence_validation/classification_test_results.csv) | CSV | Ten synthetic test cases validating input-aware classification logic across valid/invalid ciphertexts and missing oracles. |
| [`recovery_trial_validation.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase15_final_evidence_validation/recovery_trial_validation.csv) | CSV | Trial-by-trial inspection of all 400 production executions (F12, F4, F5A, F5B) validating genuine recovery vs fail-stop. |
| [`dataset_integrity_report.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase15_final_evidence_validation/dataset_integrity_report.md) | Markdown | Exhaustive audit of historical CSV files, row counts, unique IDs, naming drift, seed reuse, and pooling hazards. |
| [`phase13_phase14_discrepancy_matrix.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase15_final_evidence_validation/phase13_phase14_discrepancy_matrix.csv) | CSV | Row-by-row reconciliation table for every material numerical claim from Phase 13 vs Phase 14 vs Phase 15. |
| [`statistical_methods_and_results.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase15_final_evidence_validation/statistical_methods_and_results.md) | Markdown | Formal statistical methods, Wilson score confidence intervals, matched-pair seed caveats, and raw rate tables. |
| [`claim_evidence_matrix.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase15_final_evidence_validation/claim_evidence_matrix.csv) | CSV | Final classification of all research claims into the six formal support levels, with limitations and dispositions. |
| [`corrected_abstract.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase15_final_evidence_validation/corrected_abstract.md) | Markdown | Final validated academic abstract using only certified empirical claims and exact confidence bounds. |
| [`final_evidence_verdict.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase15_final_evidence_validation/final_evidence_verdict.md) | Markdown | Concise verdict certifying safe vs unsafe claims and issuing the formal four-part evidence freeze decision. |
| [`reproduction_instructions.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase15_final_evidence_validation/reproduction_instructions.md) | Markdown | Deterministic step-by-step instructions, build commands, and script workflows for reproducing all calculations. |

---

## 3. Key Telemetry Reconciliations

### 3.1 Explicit Revalidation of Discrepancies
The table below highlights the reconciliation of previously contested metrics:

| Target ID & Name | Phase 13 Published | Phase 14 Recalculated | Phase 15 Validated | Root Cause of Discrepancy | Final Disposition |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **F2** (Snapshot Diffusion) | 70.0% | 100.0% | **100.0% (100/100)** | Phase 13 copied downstream FO rejection count (70) instead of verifier blindness ($V_{\text{pass}} = 100$). | Corrected to 100.0% |
| **F3** (Persistent Count Zero) | 100.0% | 0.0% | **0.0% (0/100)** | Phase 13 copied narrative assumption from Phase 8. Raw data shows verifier rejected 100% of trials ($V_{\text{pass}} = 0$). | Corrected to 0.0% (Withdrawn 100%) |
| **F6** (Verifier Flag Pass) | 100.0% | 99.0% | **99.0% (99/100)** | Raw data records 99 false passes and 1 safe monitor rejection. | Corrected to 99.0% |
| **F7** (Retry Glitch) | 0.0% | 94.0% | **94.0% (94/100)** | Phase 13 claimed safe fail-stop (0%). Raw data proves verifier falsely passed in 94/100 trials. | Corrected to 94.0% |
| **F9** (DSPC Multi-Bit) | 93.0% | 100.0% | **100.0% (100/100)** | Phase 13 copied obsolete Phase 5 narrative. Raw Phase 7 dataset records 100/100 false passes. | Corrected to 100.0% |
| **F4** (Transient Recovery) | 0.0% | 0.0% | **0.0% (Genuine Recovery)** | All 100 trials verified genuine recovery ($100/100$). Intermediate coefficients internal to `poly.c`. | Retain (Qualified) |
| **F5A/F5B** (Persistent Abort) | 0.0% | 0.0% | **0.0% (Safe Fail-Stop)** | All 200 trials verified safe fail-stop abort ($200/200$) returning `0xFFFFFFFF` and emitting $K_{\text{rej}}$. | Retain (Qualified) |

---

## 4. Formal Evidence Freeze Summary

1. **What is Established:**
   - In-place snapshot recovery creates circular verifier blindness ($H_1$) under internal memory corruption ($94.0\%$ to $100.0\%$ in vulnerable harness configurations).
   - Authentic compiled production decapsulation achieves $100\%$ genuine recovery under transient butterfly faults and $100\%$ safe fail-stop under recurring/force-value faults.
   - Zero Silent Data Corruption ($H_2 = 0/400$, 95% CI: $[0.0\%, 0.95\%]$) occurred under evaluated software fault models; outer FO re-encryption reliably contained internal butterfly errors.
   - Decapsulation implicit rejection conforms bit-for-bit with FIPS 203 Section 7.3 ($K = \text{J}(z \parallel c)$).
2. **What Remains Unknown:**
   - Behavior under physical hardware glitching (EMFI, laser, clock transients).
   - Resistance to physical comparison skipping or pointer aliasing ($c' \equiv c$).
   - Microarchitectural side-channel leakage during decapsulation and retry loops.
   - Formal novelty pending comparative literature review against published fault detection schemes.
3. **Verdict:** **The evidence package is certified complete and sufficient for academic manuscript drafting.**
