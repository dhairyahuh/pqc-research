# Phase 14: Raw-Data Recalculation, Outcome Classification, and Final Claim Correction

**Auditor:** Skeptical Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Repository:** ML-KEM-768 Fault-Resilience Research (`pqc research`)  
**Scope:** Forensic Verification of Phase 13 Claims, Recalculation from Raw Experimental CSVs, Epistemological Correction of Fujisaki-Okamoto Claims, and Final Research Claim Boundaries  

---

## 1. Executive Summary

Phase 14 was commissioned to independently audit the claims of Phase 13, which claimed to have completed a final evidence audit of ML-KEM-768 fault resilience. 

Acting as a skeptical, independent cryptographic auditor, Phase 14 conducted a comprehensive forensic examination of all underlying CSV datasets, compiler objects, C harnesses, and mathematical derivations.

### Key Discoveries:
1. **Phase 13 Calculation Pipeline Defect:** Phase 13 did **not** derive its hypothesis rates from raw experimental records. Instead, it executed an arithmetic recalculation over a hardcoded Python array (`targets_info`) inherited from historical Phase 8 narrative tables.
2. **Historical Data Discrepancies Exposed:**
   - **Target F3 (Persistent Count Zeroing):** Phase 13 reported $100\%$ false recovery ($100/100$). The actual raw CSV records document **$0/100$ ($0.0\%$)** false recovery (the monitor's arithmetic difference check rejected every trial). The $100\%$ rate was a theoretical narrative fabrication.
   - **Target F7 (Retry Arithmetic Glitch):** Phase 13 reported $0\%$ false recovery ($0/100$, "Safe fail-stop detected"). The actual raw CSV records document **$94/100$ ($94.0\%$)** verifier false passes.
   - **Target F2 (Snapshot Pre-Retry Diffusion):** Phase 13 reported $70\%$ by mistakenly copying the downstream FO rejection count, whereas the raw verifier passed in **$100/100$ ($100.0\%$)** of trials despite corrupt butterfly state.
3. **Flawed $H_2$ Classification Formula:** Phase 13 formulated the rule `!valid_match && (status==0x5A5A5A5A || !rej_match)`. This expression contains a serious defect: it classifies safe fail-stop aborts (`status == 0xFFFFFFFF`) with unexpected fallback outputs as Silent Data Corruption ($H_2 = 1$). A corrected, mutually exclusive classification framework was established and verified across six synthetic unit tests ([`classification_unit_tests.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase14_evidence_correction/classification_unit_tests.csv)).
4. **Production Binary Execution Verified:** Fresh execution of 400 production decapsulation trials against compiled objects (`mlkem768_inst.o` + `mlkem_fault_hooks.o`, verified 100% bit-for-bit against source rebuilds) demonstrated:
   - Target F12: $100/100$ Clean Success.
   - Target F4: $100/100$ Genuine Recovery under transient butterfly faults.
   - Targets F5A & F5B: $200/200$ Safe Fail-Stop aborts under recurring bit-inversion and software force-value models.
   - **$0/400$ Silent Data Corruption ($H_2 = 0.0\%$, 95% Wilson score CI: $[0.0\%, 0.95\%]$).**
5. **Purge of Unscientific Hyperbole:** Overstated rhetoric asserting that the outer Fujisaki-Okamoto transform "unconditionally enforces security" or acts as an "impenetrable cryptographic firewall" has been completely purged. Concrete physical fault attack vectors (instruction skipping, pointer manipulation) that bypass FO comparison are documented in [`fo_claim_correction.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase14_evidence_correction/fo_claim_correction.md). All constant-time certifications and physical radiation claims are withdrawn.
6. **Academic Novelty Status:** Novelty regarding recovery-verifier blindness in lattice KEMs is formally marked as **UNRESOLVED**, pending a systematic, documented prior-art comparative literature review.

---

## 2. Directory Index of Phase 14 Deliverables

| Deliverable File | Type | Purpose & Summary Content |
| :--- | :---: | :--- |
| [`README.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase14_evidence_correction/README.md) | Markdown | Master audit overview, executive findings, and deliverable navigation index. |
| [`phase13_calculation_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase14_evidence_correction/phase13_calculation_audit.md) | Markdown | Forensic audit exposing hardcoded integers, pipeline flaws, and discrepancies vs. raw CSVs in Phase 13. |
| [`h1_h2_operational_definitions.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase14_evidence_correction/h1_h2_operational_definitions.md) | Markdown | Rigorous mathematical and interface definitions for $H_1$ and $H_2$, analysis of Phase 13 formula defect, and replacement rules. |
| [`classification_unit_tests.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase14_evidence_correction/classification_unit_tests.csv) | CSV | Six synthetic unit test vectors validating the corrected classification logic and demonstrating the Phase 13 false positive. |
| [`raw_trial_integrity_report.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase14_evidence_correction/raw_trial_integrity_report.md) | Markdown | Comprehensive audit of all historical CSV files, row counts, unique IDs, naming drift, and seed reuse. |
| [`h1_h2_raw_recalculation.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase14_evidence_correction/h1_h2_raw_recalculation.csv) | CSV | Re-calculated $H_1$ and $H_2$ statistics derived dynamically from raw CSV rows with 95% Wilson confidence intervals. |
| [`per_target_outcome_summary.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase14_evidence_correction/per_target_outcome_summary.csv) | CSV | Complete mutually exclusive outcome distribution across all 13 evaluated targets (Harness and Production). |
| [`production_reproduction_evidence.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase14_evidence_correction/production_reproduction_evidence.md) | Markdown | Verification of production objects, execution logs for F4, F5A, F5B, F12, clean-room Keccak oracle, and object hashes. |
| [`fo_claim_correction.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase14_evidence_correction/fo_claim_correction.md) | Markdown | Epistemological disaggregation of decapsulation behavior, purge of firewall rhetoric, and analysis of physical bypass vectors. |
| [`claim_evidence_matrix.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase14_evidence_correction/claim_evidence_matrix.csv) | CSV | Complete traceability matrix defining the empirical status, limitations, and academic disposition for all research claims. |
| [`corrected_research_claim.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase14_evidence_correction/corrected_research_claim.md) | Markdown | Reassessment of contributions, distinguishing architectural models from production security, and formulating the core research question. |
| [`corrected_abstract.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase14_evidence_correction/corrected_abstract.md) | Markdown | Publication-grade academic abstract reflecting audit-corrected evidence, empirical confidence bounds, and rigorous claim boundaries. |
| [`final_verdict.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase14_evidence_correction/final_verdict.md) | Markdown | Final audit verdict answering the six mandatory inquiries with complete scientific skepticism and empirical rigor. |

---

## 3. Side-by-Side Recalculation Comparison

The table below contrasts the flawed Phase 13 published figures against the dynamic Phase 14 raw-data recalculations:

| Target ID & Name | Execution Tier | Phase 13 Published $H_1$ | Phase 14 Raw Recalculated $H_1$ | 95% Wilson CI (Phase 14) | Phase 14 Raw Recalculated $H_2$ | 95% Wilson CI (Phase 14) | Forensic Finding |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **F1** (Saved Operand Bitflip) | Harness Model | 98.0% | **98.0%** (98/100) | [93.0%, 99.4%] | **0.0%** (0/100) | [0.0%, 3.7%] | Matches raw records. |
| **F2** (Snapshot Pre-Retry Diffusion) | Harness Model | 70.0% | **100.0%** (100/100) | [96.3%, 100.0%] | **0.0%** (0/100) | [0.0%, 3.7%] | Phase 13 reported FO rejections instead of verifier blindness. |
| **F3** (Persistent Count Zeroing) | Harness Model | 100.0% | **0.0%** (0/100) | [0.0%, 3.7%] | **0.0%** (0/100) | [0.0%, 3.7%] | **Phase 13 fabricated 100%**; raw verifier rejected 100% of trials. |
| **F6** (Verifier Flag Forced Pass) | Harness Model | 100.0% | **99.0%** (99/100) | [94.6%, 99.8%] | **0.0%** (0/100) | [0.0%, 3.7%] | Discrepancy of 1 safe rejection in raw records. |
| **F7** (Retry Arithmetic Glitch) | Harness Model | 0.0% | **94.0%** (94/100) | [87.5%, 97.2%] | **0.0%** (0/100) | [0.0%, 3.7%] | **Phase 13 reported 0%**; raw verifier falsely passed 94 trials. |
| **F8** (Verifier Operand Corrupt) | Harness Model | 0.0% | **0.0%** (0/100) | [0.0%, 3.7%] | **0.0%** (0/100) | [0.0%, 3.7%] | Matches raw records (Safe rejection). |
| **F9** (DSPC Multi-Bit Collision) | Harness Model | 93.0% | **100.0%** (100/100) | [96.3%, 100.0%] | **0.0%** (0/100) | [0.0%, 3.7%] | Phase 13 copied obsolete Phase 5 narrative; raw is 100%. |
| **F10** (DSPC State Bypass) | Harness Model | 100.0% | **100.0%** (100/100) | [96.3%, 100.0%] | **0.0%** (0/100) | [0.0%, 3.7%] | Matches raw records. |
| **F11** (DSPC Single-Bit Clean) | Harness Model | 0.0% | **0.0%** (0/100) | [0.0%, 3.7%] | **0.0%** (0/100) | [0.0%, 3.7%] | Matches raw records (Safe rejection). |
| **F12** (Clean Baseline Control) | Production Binary | 0.0% | **0.0%** (0/100) | [0.0%, 3.7%] | **0.0%** (0/100) | [0.0%, 3.7%] | 100/100 Clean Success. |
| **F4** (Transient Butterfly Fault) | Production Binary | 0.0% | **0.0%** (0/100) | [0.0%, 3.7%] | **0.0%** (0/100) | [0.0%, 3.7%] | 100/100 Genuine Recovery. |
| **F5A** (Recurring Bit-Inversion) | Production Binary | 0.0% | **0.0%** (0/100) | [0.0%, 3.7%] | **0.0%** (0/100) | [0.0%, 3.7%] | 100/100 Safe Fail-Stop. |
| **F5B** (Software Force-Value Model) | Production Binary | 0.0% | **0.0%** (0/100) | [0.0%, 3.7%] | **0.0%** (0/100) | [0.0%, 3.7%] | 100/100 Safe Fail-Stop (Software model). |

---

## 4. Final Audit Determination

The evidence in `phase14_evidence_correction/` supersedes all previous phase reports. The core research question—evaluating internal recovery verifier blindness against outer Fujisaki-Okamoto re-encryption containment under software fault models—is rigorously supported by empirical data. Manuscript drafting may proceed under the qualified claim boundaries established in [`final_verdict.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase14_evidence_correction/final_verdict.md).
