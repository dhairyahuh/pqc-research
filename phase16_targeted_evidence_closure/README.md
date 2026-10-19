# Phase 16: Targeted Evidence Closure and Final Claim Qualification

**Auditor:** Skeptical Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Repository:** ML-KEM-768 Fault-Resilience Research (`pqc research`)  
**Scope:** Final Targeted Validation, Denominator Correction, Counter Control-Flow Verification, and Definitive Evidence Closure  

---

## 1. Executive Summary

Phase 16 was commissioned to resolve the final remaining methodological gaps identified in Phase 15. In accordance with strict auditing guidelines, **no new fault campaigns were launched and no new countermeasures were introduced.** 

Instead, Phase 16 focused exclusively on validating existing trial-level records, auditing source-level counter semantics, correcting production denominators, and establishing an untainted claim baseline for academic publication.

### Key Methodological Resolutions:
1. **H1 Fault Activation Audit:** Evaluated whether fault activation is independently distinguishable from fault arming in Phase 7 harness data. Discovered that while arming parameters (`stage, butterfly, bit`) and downstream detection (`mismatch_count > 0`) are logged, the CSV lacks a dedicated `trigger_count` column. Formally documented this distinction in [`h1_activation_audit.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/h1_activation_audit.csv).
2. **Corrected Production H2 Denominator ($n = 300$):** Disaggregated the 100 clean baseline control trials (Target F12) from active fault trials. Established the authentic fault-triggered production denominator as **$n = 300$** (100 each for F4, F5A, F5B). Under $n = 300, k = 0$, the 95% Wilson score upper confidence bound is **$1.26\%$** (correcting previous inflated $n = 400$ metrics).
3. **Recovery Counter Semantics Proven:** Line-by-line control-flow tracing of `poly.c`, `mlkem_fault_hooks.c`, and `kem.c` verified that `recovered_count` in Target F4 cannot increment unless an initial mismatch is detected followed by successful post-retry invariant verification ([`recovery_counter_source_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/recovery_counter_source_audit.md)).
4. **Input-Aware Classifier Validation:** Verified 10 synthetic test cases spanning valid/invalid ciphertexts, fail-stop status, corrupted fallback buffers, and missing oracles ([`classifier_validation.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/classifier_validation.csv)).
5. **Final Claim Reconciliation:** Audited all 8 material research claims, establishing authoritative wording that separates directly observed telemetry from inferred control-flow transitions and unverified assumptions ([`claim_reconciliation.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/claim_reconciliation.csv), [`corrected_claims.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/corrected_claims.md)).
6. **Definitive Verdict:** **EVIDENCE CLOSURE ACHIEVED.**

---

## 2. Directory Index of Phase 16 Deliverables

| Deliverable File | Type | Purpose & Summary Content |
| :--- | :---: | :--- |
| [`README.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/README.md) | Markdown | Master overview, audit scope, method summary, and deliverable navigation index. |
| [`evidence_manifest.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/evidence_manifest.csv) | CSV | SHA-256 hashes, execution tiers, provenance, and descriptions for all key repository evidence files. |
| [`h1_activation_audit.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/h1_activation_audit.csv) | CSV | Trial-level evaluation of the 6 fault activation conditions across all 1,200 Phase 7 trials. |
| [`h2_corrected_trial_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/h2_corrected_trial_results.csv) | CSV | Trial-level production decapsulation classifications segregating baseline controls from active fault trials. |
| [`classifier_validation.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/classifier_validation.csv) | CSV | Ten synthetic test cases evaluating input-aware classification logic across valid/invalid ciphertexts. |
| [`recovery_counter_source_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/recovery_counter_source_audit.md) | Markdown | Source-level control-flow audit tracing trigger, mismatch, recovery, and persistent failure counters. |
| [`dataset_integrity_findings.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/dataset_integrity_findings.md) | Markdown | Audit report on dataset integrity, row counts, corrected $n=300$ denominator, and PRNG dependencies. |
| [`claim_reconciliation.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/claim_reconciliation.csv) | CSV | Claim-by-claim reconciliation matrix detailing observed fields, inferred fields, and final dispositions. |
| [`corrected_claims.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/corrected_claims.md) | Markdown | Authoritative prose wording for all research claims with explicit epistemological boundaries. |
| [`final_closure_verdict.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/final_closure_verdict.md) | Markdown | Definitive closure verdict and methodological certification confirming evidence closure achieved. |
| [`reproduction_instructions.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/reproduction_instructions.md) | Markdown | Deterministic step-by-step instructions, build commands, and script workflows for reproducing results. |

---

## 3. Side-by-Side Summary of Critical Metrics

| Experimental Target | Experimental Tier | Claimed Condition | Verified Sample Size ($n$) | Primary Observed Outcome | 95% Wilson Score CI | Methodological Caveat |
| :--- | :---: | :--- | :---: | :--- | :---: | :--- |
| **F1** (Saved Bitflip) | Harness Model | Simulated In-Place Snapshot | 100 | 98/100 Verifier False Passes ($H_1$) | [93.0%, 99.4%] | Activation inferred from mismatch counter. |
| **F2** (Snapshot Bias) | Harness Model | Simulated In-Place Snapshot | 100 | 100/100 Verifier False Passes ($H_1$) | [96.3%, 100.0%] | Corrected from Phase 13's erroneous 70%. |
| **F3** (Count Zeroing) | Harness Model | Simulated Monitor Control | 100 | 0/100 False Passes (Safe Rejection) | [0.0%, 3.7%] | Historical 100% claim permanently withdrawn. |
| **F6** (Result Force) | Harness Model | Simulated Verifier Bypass | 100 | 99/100 Verifier False Passes ($H_1$) | [94.6%, 99.8%] | 1 safe monitor rejection observed. |
| **F7** (Arithmetic Glitch)| Harness Model | Simulated Retry Multiplier | 100 | 94/100 Verifier False Passes ($H_1$) | [87.5%, 97.2%] | Corrected from Phase 13's inverted 0%. |
| **F9** (Multi-Bit) | Harness Model | Simulated State Collision | 100 | 100/100 Verifier False Passes ($H_1$) | [96.3%, 100.0%] | Corrected from Phase 13's obsolete 93%. |
| **F12** (Clean Baseline)| Production Binary | Unfaulted Sanity Control | 100 | 100/100 Clean Success Baseline | [96.3%, 100.0%] | Excluded from fault resilience denominator. |
| **F4** (Transient Bitflip)| Production Binary | Active Fault Injection | 100 | 100/100 Genuine Recovery | [96.3%, 100.0%] | Intermediate coefficients not serialized. |
| **F5A** (Recurring Bitflip)| Production Binary| Active Fault Injection | 100 | 100/100 Safe Fail-Stop Aborts | [96.3%, 100.0%] | Emitted conformant $K_{\text{rej}} = \text{J}(z \parallel c)$. |
| **F5B** (Force-Value) | Production Binary | Active Fault Injection | 100 | 100/100 Safe Fail-Stop Aborts | [96.3%, 100.0%] | Strictly labeled software force-value model. |
| **Active Fault Production**| Production Binary | Pooled Active Fault Treatments | **300** | **0/300 Silent Data Corruption ($H_2$)** | **[0.0%, 1.26%]** | **Corrected authentic denominator ($n=300$).** |

---

## 4. Final Methodological Determination

The Phase 16 audit concludes that **all evidence closure criteria are fulfilled**. The repository is certified ready for peer-reviewed academic manuscript drafting under the qualified claim boundaries defined in [`final_closure_verdict.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/final_closure_verdict.md).
