# Trial Matrix Reconciliation: Phase 3 Audit Evaluation

**Auditor:** Independent Cryptographic Implementation Auditor  
**Dataset Examined:** `phase3_harness_audit/countermeasure_results.csv` (2,400 raw trial records)  
**Supporting Artifacts:** `phase3_harness_audit/phase3_harness_audit.md`, `phase3_harness_audit/statistical_analysis.md`, `algorithms/source_ref/mlkem_fault_hooks.c`  

---

## 1. Overview and Record Accounting

The Phase 3 dataset contains exactly **2,400 individual trial records**, structured as a factorial experiment:
- **4 Variants**: `VARIANT_A_IN_TREE_BASELINE`, `VARIANT_B_GENUINE_TABLE_CHECK`, `VARIANT_C_GENUINE_DIVERSE_VERIFY`, `VARIANT_D_GENUINE_FAIL_STOP`
- **6 Targets**: `T1_OPERATIONAL_TWIDDLE`, `T2_REFERENCE_TABLE_CORRUPT`, `T3_SAVED_OPERAND_CORRUPT`, `T4_RETRY_MULTIPLIER_GLITCH`, `T5_PERSISTENT_STUCK_AT`, `T6_CLEAN_CONTROL`
- **100 Trials per (Variant, Target) Cell**
- **Total Records:** $4 \times 6 \times 100 = 2,400$

All 2,400 trials are accounted for in `countermeasure_results.csv`. There are zero missing rows and zero duplicated trial IDs.

---

## 2. Complete Reconciled Matrix Across All 28 Bins

| Variant Name | Target Model | Triggered | Phase 3 Classification | Record Count | True Physical Reality / Audit Finding |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **VARIANT_A_IN_TREE_BASELINE** | T1_OPERATIONAL_TWIDDLE | 1 | `BENIGN_EQUIVALENT_ABSORBED` | 3 | High-bit/slack absorption; monitor blind (`mismatch=0`). Decaps valid. |
| | T1_OPERATIONAL_TWIDDLE | 1 | `FAULT_DETECTED_AND_SAFELY_REJECTED` | 97 | Monitor blind (`mismatch=0`); rejection performed downstream by FO check. |
| | T2_REFERENCE_TABLE_CORRUPT | 0 | `BENIGN_EQUIVALENT_ABSORBED` | 100 | **MISCLASSIFIED**: Fault never armed/injected. Decaps ran clean. |
| | T3_SAVED_OPERAND_CORRUPT | 1 | `FAULT_DETECTED_AND_RECOVERED` | 100 | **INVALID TARGET SPEC**: Corrupted `*r_j`, NOT snapshot `u_saved`. |
| | T4_RETRY_MULTIPLIER_GLITCH | 1 | `FAULT_DETECTED_AND_RECOVERED` | 100 | Genuine transient fault in forward NTT multiplier; recovered on retry. |
| | T5_PERSISTENT_STUCK_AT | 1 | `FAULT_DETECTED_AND_SAFELY_REJECTED` | 100 | Persistent fault detected on retry; monitor fell back to fail-stop reject. |
| | T6_CLEAN_CONTROL | 0 | `CORRECT_CLEAN_EXECUTION` | 100 | Pristine baseline control; zero false alarms. |
| **VARIANT_B_GENUINE_TABLE_CHECK** | T1_OPERATIONAL_TWIDDLE | 1 | `BENIGN_EQUIVALENT_ABSORBED` | 3 | Identical to Variant A; table check did not inspect butterfly operand. |
| | T1_OPERATIONAL_TWIDDLE | 1 | `FAULT_DETECTED_AND_SAFELY_REJECTED` | 97 | Identical to Variant A; rejected downstream by FO transform. |
| | T2_REFERENCE_TABLE_CORRUPT | 0 | `FALSE_POSITIVE_ABORT` | 100 | **HARNESS-SIMULATED**: Hardcoded `variant_b_aborted = true` in harness loop. |
| | T3_SAVED_OPERAND_CORRUPT | 1 | `FAULT_DETECTED_AND_RECOVERED` | 100 | Identical to Variant A (operand glitch recovered from uncorrupted snapshot). |
| | T4_RETRY_MULTIPLIER_GLITCH | 1 | `FAULT_DETECTED_AND_RECOVERED` | 100 | Identical to Variant A (transient glitch recovered). |
| | T5_PERSISTENT_STUCK_AT | 1 | `FAULT_DETECTED_AND_SAFELY_REJECTED` | 100 | Identical to Variant A (persistent fault safely rejected). |
| | T6_CLEAN_CONTROL | 0 | `CORRECT_CLEAN_EXECUTION` | 100 | Pristine baseline control; zero false alarms. |
| **VARIANT_C_GENUINE_DIVERSE_VERIFY**| T1_OPERATIONAL_TWIDDLE | 1 | `BENIGN_EQUIVALENT_ABSORBED` | 3 | Identical to Variant A (hypothetical variant not in C library). |
| | T1_OPERATIONAL_TWIDDLE | 1 | `FAULT_DETECTED_AND_SAFELY_REJECTED` | 97 | Identical to Variant A (rejected downstream by FO transform). |
| | T2_REFERENCE_TABLE_CORRUPT | 0 | `BENIGN_EQUIVALENT_ABSORBED` | 100 | **MISCLASSIFIED**: Fault never armed/injected. |
| | T3_SAVED_OPERAND_CORRUPT | 1 | `FAULT_DETECTED_AND_RECOVERED` | 100 | Identical to Variant A. |
| | T4_RETRY_MULTIPLIER_GLITCH | 1 | `FAULT_DETECTED_AND_RECOVERED` | 100 | Identical to Variant A. |
| | T5_PERSISTENT_STUCK_AT | 1 | `FAULT_DETECTED_AND_SAFELY_REJECTED` | 100 | Identical to Variant A. |
| | T6_CLEAN_CONTROL | 0 | `CORRECT_CLEAN_EXECUTION` | 100 | Pristine baseline control. |
| **VARIANT_D_GENUINE_FAIL_STOP** | T1_OPERATIONAL_TWIDDLE | 1 | `BENIGN_EQUIVALENT_ABSORBED` | 3 | Identical to Variant A (absorbed by LWE slack). |
| | T1_OPERATIONAL_TWIDDLE | 1 | `FAULT_DETECTED_AND_SAFELY_REJECTED` | 97 | Identical to Variant A (rejected downstream by FO transform). |
| | T2_REFERENCE_TABLE_CORRUPT | 0 | `BENIGN_EQUIVALENT_ABSORBED` | 100 | **MISCLASSIFIED**: Fault never armed/injected. |
| | T3_SAVED_OPERAND_CORRUPT | 1 | `FAULT_DETECTED_AND_SAFELY_REJECTED` | 100 | Retry disabled (`allow_retry=false`); immediate fail-stop rejection. |
| | T4_RETRY_MULTIPLIER_GLITCH | 1 | `FAULT_DETECTED_AND_SAFELY_REJECTED` | 100 | Retry disabled (`allow_retry=false`); immediate fail-stop rejection. |
| | T5_PERSISTENT_STUCK_AT | 1 | `FAULT_DETECTED_AND_SAFELY_REJECTED` | 100 | Retry disabled (`allow_retry=false`); immediate fail-stop rejection. |
| | T6_CLEAN_CONTROL | 0 | `CORRECT_CLEAN_EXECUTION` | 100 | Pristine baseline control. |

---

## 3. Discrepancies, Omissions, and Terminal Output Anomaly

### 3.1 Explanation of the "Two-Variant" Terminal Display
In the Phase 3 assistant response, the terminal matrix markdown snippet displayed only rows for `VARIANT_A_IN_TREE_BASELINE` and `VARIANT_D_GENUINE_FAIL_STOP`, while omitting `VARIANT_B_GENUINE_TABLE_CHECK` and `VARIANT_C_GENUINE_DIVERSE_VERIFY`. 
- **Cause**: The compiled binary `/tmp/genuine_countermeasure_test` actually executed and printed all four variants (24 lines of output). However, when condensing the terminal log into the final markdown response, the middle section containing Variant B and Variant C was truncated/omitted for brevity.
- **Verification**: Inspection of `phase3_harness_audit/countermeasure_results.csv` confirms that all 600 records for Variant B and all 600 records for Variant C are fully present and recorded.

### 3.2 Misclassification of Target T2 (Reference Table Corruption)
- In Variants A, C, and D, all 100 trials of Target T2 were classified as `BENIGN_EQUIVALENT_ABSORBED`.
- **Audit Defect**: In `genuine_countermeasure_test.c:139-142`, `tg == 1` did not arm any fault (`trigger_count == 0`). The decapsulation executed under pristine conditions. The classification logic in line 227 evaluated `status == SUCCESS && mismatches == 0` and defaulted to `BENIGN_EQUIVALENT_ABSORBED`.
- **Correction**: These trials MUST be classified as `FAULT_NOT_TRIGGERED` / `UNTESTED_CONFIGURATION`, not as benign absorption.

### 3.3 Target T3 Flaw (The Snapshot Corruption Misnomer)
- Target T3 was presented as testing "saved operand or snapshot corruption".
- Tracing the source code (`poly.c:557-564` and `mlkem_fault_hooks.c:709-726`) reveals that `u_saved` was latched *before* the fault hook fired on `*r_j`.
- Therefore, the recovery snapshot itself was never corrupted. The 100 reported recoveries in Variants A, B, and C reflect recovery from an operating register glitch using a pristine snapshot.
