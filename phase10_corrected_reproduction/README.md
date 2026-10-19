# Phase 10: Corrected Reproduction and Claim Revalidation

**Auditor:** Skeptical Cryptographic Software Verification Researcher  
**Date:** October 2026  
**Audit Directory:** [`phase10_corrected_reproduction/`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction)  
**Binary Executed:** [`phase10_corrected_reproduction/corrected_production_reproducer`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/corrected_production_reproducer)  
**Raw Dataset:** [`phase10_corrected_reproduction/raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/raw_production_trials.csv) (400 trials)  

---

## 1. Executive Summary and Experimental Corrections

Phase 10 audited Phase 9, resolving several experimental defects and enforcing rigorous scientific boundaries:

1. **Outcome Definition Correction:**  
   Clean baseline executions (Target F12) were previously misclassified as `GENUINE_RECOVERY`. Phase 10 formalizes mutually exclusive categories; F12 is now correctly classified as **`CLEAN_SUCCESS`** ([`corrected_outcome_definitions.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/corrected_outcome_definitions.md)).
2. **Disambiguation of Fault Semantics (F5A vs F5B):**  
   Prior reports labeled recurring bit-inversions as "stuck-at faults." Phase 10 distinguishes recurring bit-inversion (`F5A_RECURRING_BITFLIP`) from true hardware stuck-at-zero clamping (`F5B_STUCK_AT_ZERO`), verifying both models on production objects ([`fault_hook_semantics.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/fault_hook_semantics.md)).
3. **Cryptographic Output Verification of Implicit Rejection:**  
   Safe fail-stop rejection was validated not merely by checking status codes, but by independently computing $K_{\text{rej}} = \text{SHAKE256}(z \parallel ct)$ and confirming bit-for-bit key equality in 100/100 trials ([`per_target_statistics.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/per_target_statistics.md)).
4. **Target F2 Reclassification:**  
   Because `f2_tracer.c` reimplemented `native_ntt_monitor_butterfly` in the harness, all production-path wording regarding F2 is formally withdrawn and reclassified as a **software model experiment** ([`f2_trace_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/f2_trace_audit.md)).
5. **Rigorous Revalidation of H1 and H2:**  
   Internal verifier blindness (H1) is strictly decoupled from Silent Data Corruption (H2) ([`h1_h2_revalidation.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/h1_h2_revalidation.md)).

---

## 2. Directory Sitemap and Deliverables

| Deliverable | Type | Description |
| :--- | :---: | :--- |
| [`README.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/README.md) | Guide | Executive summary, experimental corrections, and reproduction guide (this file). |
| [`repository_and_build_identity.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/repository_and_build_identity.md) | Audit | Git commit, toolchain, build flags, and bit-for-bit SHA-256 rebuild verification. |
| [`fault_hook_semantics.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/fault_hook_semantics.md) | Audit | Lifecycle analysis of `mlkem_fault_reset` and distinction between bitflips and stuck-at faults. |
| [`corrected_production_reproducer.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/corrected_production_reproducer.c) | Code | Standalone C test harness linking directly against compiled production objects. |
| [`raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/raw_production_trials.csv) | Dataset | Raw CSV records for 400 production-object trials across F12, F4, F5A, and F5B. |
| [`corrected_outcome_definitions.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/corrected_outcome_definitions.md) | Analysis | Exact mathematical predicates for mutually exclusive outcome categories. |
| [`per_target_statistics.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/per_target_statistics.md) | Statistics | Per-target counts, exact denominators, and 95% Wilson confidence intervals. |
| [`f2_trace_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/f2_trace_audit.md) | Report | Audit of `f2_tracer.c`, withdrawal of production-path wording, and model reclassification. |
| [`h1_h2_revalidation.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/h1_h2_revalidation.md) | Analysis | Decoupled revalidation of internal verifier blindness vs API-boundary key corruption. |
| [`fo_dual_rail_claim_boundary.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/fo_dual_rail_claim_boundary.md) | Audit | Four-layer claim boundary audit separating source intent, assembly, and physical reality. |
| [`claim_evidence_matrix.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/claim_evidence_matrix.md) | Taxonomy | Master claim classification matrix categorizing all research findings across six tiers. |
| [`limitations_and_next_experiments.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/limitations_and_next_experiments.md) | Scope | Smallest defensible research claim and roadmap of pre-submission experiments. |

---

## 3. Reproduction Instructions

### 3.1 Compile and Run the Corrected Production Reproducer
```bash
clang -O3 -Wall -Wextra -std=c11 \
  -I. -I algorithms/source_ref/mlkem \
  phase10_corrected_reproduction/corrected_production_reproducer.c \
  bin/obj/mlkem768_inst.o bin/obj/mlkem_fault_hooks.o \
  -o bin/phase10_reproducer

./bin/phase10_reproducer
```

### 3.2 Verify Trial Statistics via Python
```bash
python3 -c "
import pandas as pd
df = pd.read_csv('phase10_corrected_reproduction/raw_production_trials.csv')
print(df.groupby(['target', 'outcome']).size())
print('\nRejection Key Verification:')
print(df.groupby(['target', 'matches_rejection_key', 'internal_status']).size())
"
```
