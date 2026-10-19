# Phase 13: Final Evidence Verification and Research Contribution Audit

**Auditor:** Independent Cryptographic Implementation Auditor, Experimental Methodology Reviewer, and Research Paper Evaluator  
**Date:** October 2026  
**Repository:** `https://github.com/dhairyahuh/pqc-research.git`  
**Active Branch:** `space-resilience-framework`  
**Commit Hash (HEAD):** `ca38dec3b76f54e405a268c3f06a5f04a13e3660`  

---

## 1. Executive Summary

Phase 13 constitutes the comprehensive, skeptical final audit of Phases 1 through 12. It establishes the verifiable baseline of the ML-KEM-768 fault resilience codebase, independently validates the clean-room cryptographic output oracle against NIST FIPS 202 rate boundaries, executes a clean reproduction of production-path fault experiments, reconciles all historical trial datasets, audits the Fujisaki-Okamoto and dual-rail claim boundaries, and evaluates the surviving academic research contribution.

### Key Audit Findings:
1. **Deterministic Production Object Reproducibility:**  
   The compiled production objects `bin/obj/mlkem768_inst.o` (SHA-256: `7adc4280...`) and `bin/obj/mlkem_fault_hooks.o` (SHA-256: `e7a90d06...`) were rebuilt from the repository source code (`algorithms/source_ref/mlkem/mlkem_native.c` and `algorithms/source_ref/mlkem_fault_hooks.c`). The resulting objects match the repository binaries **100% bit-for-bit**.
2. **Independent Oracle Verification:**  
   The clean-room Keccak-f[1600] / SHAKE256 implementation was verified across 9 rate-boundary test vectors (0B to 1,120B) against Python 3.11 `hashlib.shake_256`, achieving **100% agreement** without invoking or reusing any symbols from `mlkem-native`.
3. **Production-Path Fault Reproduction ($N=400$):**  
   Target experiments F12 (Clean Baseline), F4 (Transient Software Bit-Flip), F5A (Recurring Software Bit-Inversion), and F5B (Software Force-Value Model) were reproduced fresh directly against compiled production binaries:
   - F12: 100% `CLEAN_SUCCESS` (100/100)
   - F4: 100% `GENUINE_RECOVERY` (100/100)
   - F5A: 100% `SAFE_FAIL_STOP` (100/100)
   - F5B: 100% `SAFE_FAIL_STOP` (100/100)
4. **Complete Evidence Recalculation:**  
   Audited all raw trial logs across Phases 5–13. Clarified that clean controls ($N=100$) are excluded from the recovery-verifier failure rate denominator ($H_1$) because no recovery is attempted, but included in the API-level Silent Data Corruption denominator ($H_2$):
   - **Pooled $H_1$ across vulnerable software models (F1, F2, F3, F6, F9, F10):** **561 / 600 (93.5%)**, 95% Wilson CI: **[91.2%, 95.2%]**.
   - **Pooled $H_2$ across all evaluated scenarios ($N=1,300$):** **0 / 1,300 (0.0%)**, 95% Wilson CI: **[0.0%, 0.28%]**.
5. **Epistemic Discipline & Claim Revisions:**  
   Unsubstantiated claims asserting "universal fault immunity", "certified constant-time execution", or "physical hardware resilience" are formally **withdrawn**. The central academic claim is strictly narrowed to the empirical software evidence.

---

## 2. Directory Artifact Inventory

The [`phase13_final_evidence_audit/`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/) directory contains the complete final evidence package:

| Artifact File | Description | Primary Role |
| :--- | :--- | :--- |
| [`README.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/README.md) | Master executive overview and directory index | Directory Index |
| [`repository_baseline.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/repository_baseline.md) | Repository commit, compiler flags, and deterministic object rebuild proof | Baseline Verification |
| [`artifact_traceability_matrix.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/artifact_traceability_matrix.csv) | Full traceability matrix mapping claims to code, tests, and raw records | Traceability Matrix |
| [`oracle_reproduction.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/oracle_reproduction.md) | Technical audit of clean-room Keccak oracle and FIPS 203 derivation | Oracle Verification |
| [`oracle_test_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/oracle_test_results.csv) | Execution log of 9 rate-boundary test vectors | Raw Test Vector Log |
| [`verify_oracle.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/verify_oracle.c) | Standalone C source for boundary verification | Executable Code |
| [`production_path_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/production_path_audit.md) | Detailed audit of production hooks, reset behavior, and classification rules | Protocol Audit |
| [`production_trial_recalculation.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/production_trial_recalculation.csv) | Raw trial log of 400 reproduced production trials | Raw Production Log |
| [`production_reproducer.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/production_reproducer.c) | Standalone C reproduction harness | Executable Code |
| [`raw_data_integrity_results.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/raw_data_integrity_results.md) | Forensic analysis of historical CSV files, row counts, and seed schedules | Data Integrity |
| [`h1_h2_recalculation.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/h1_h2_recalculation.csv) | Recalculated $H_1$/$H_2$ statistics with 95% Wilson confidence intervals | Reconciled Statistics |
| [`statistical_interpretation.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/statistical_interpretation.md) | Denominator accounting, pooling justification, and Wilson interval methodology | Statistical Audit |
| [`fo_dualrail_claim_review.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/fo_dualrail_claim_review.md) | Review of FO transform, dual-rail checks, and plausible physical bypasses | Security Architecture |
| [`claim_evidence_matrix.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/claim_evidence_matrix.csv) | Complete matrix mapping research claims to dispositions | Claim Matrix |
| [`research_contribution_assessment.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/research_contribution_assessment.md) | Assessment of scientific novelty, value-add, and model vs production realities | Contribution Audit |
| [`revised_abstract.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/revised_abstract.md) | Refined, publication-ready academic abstract | Publication Framing |
| [`limitations_and_threats_to_validity.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/limitations_and_threats_to_validity.md) | Comprehensive review of internal, construct, and external threats to validity | Pre-Submission Review |
| [`final_verdict.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/final_verdict.md) | Four-tier epistemic verdict and publication readiness assessment | Final Verdict |

---

## 3. Exact Commands to Reproduce Phase 13

```bash
# 1. Verify clean-room Keccak oracle across boundary vectors
clang -O2 -Wall -Wextra \
  phase13_final_evidence_audit/verify_oracle.c \
  -o phase13_final_evidence_audit/verify_oracle

./phase13_final_evidence_audit/verify_oracle

# 2. Execute 400 production reproduction trials directly against compiled objects
clang -O2 -Wall -Wextra -I. \
  phase13_final_evidence_audit/production_reproducer.c \
  bin/obj/mlkem768_inst.o \
  bin/obj/mlkem_fault_hooks.o \
  -o phase13_final_evidence_audit/production_reproducer

./phase13_final_evidence_audit/production_reproducer

# 3. Deterministically rebuild production objects from source to verify bit-for-bit hashes
clang -O3 -std=c99 -I algorithms/source_ref/mlkem \
  -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem768 \
  -DMLK_CONFIG_PARAMETER_SET=768 \
  -DMLKEM_RESEARCH_FAULT_HOOKS \
  -c algorithms/source_ref/mlkem/mlkem_native.c \
  -o /tmp/rebuilt_mlkem768_inst.o

clang -O3 -std=c99 -I algorithms/source_ref/mlkem \
  -DMLKEM_RESEARCH_FAULT_HOOKS \
  -c algorithms/source_ref/mlkem_fault_hooks.c \
  -o /tmp/rebuilt_mlkem_fault_hooks.o

shasum -a 256 bin/obj/mlkem768_inst.o /tmp/rebuilt_mlkem768_inst.o
shasum -a 256 bin/obj/mlkem_fault_hooks.o /tmp/rebuilt_mlkem_fault_hooks.o
```
