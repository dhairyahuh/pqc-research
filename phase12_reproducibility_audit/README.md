# Phase 12: Independent Reproducibility, Evidence Integrity, and Claim-Boundary Audit

**Auditor:** Skeptical Cryptographic Implementation Auditor & Research Methodology Reviewer  
**Date:** October 2026  
**Repository:** `https://github.com/dhairyahuh/pqc-research.git`  
**Active Branch:** `space-resilience-framework`  
**Commit Hash (HEAD):** `ca38dec3b76f54e405a268c3f06a5f04a13e3660`  

---

## 1. Executive Audit Overview

Phase 12 conducts a comprehensive reproducibility, evidence integrity, and claim-boundary audit across all historical phases (Phases 5–11) and the compiled production objects of the ML-KEM-768 fault resilience research repository.

### Key Audit Findings:
1. **Independent Oracle Verification:**  
   The clean-room Keccak-f[1600] / SHAKE256 oracle was tested across 9 critical rate-boundary vectors (empty, 1B, 43B, 135B, 136B, 137B, 272B, 500B, and 1,120B). All outputs matched Python 3.11 `hashlib.shake_256` bit-for-bit, confirming that the oracle independently and accurately models NIST FIPS 202/203 without circular dependencies.
2. **Production-Path Fault Reproduction ($N=400$):**  
   Targets F12 (Clean Baseline), F4 (Transient Software Bit-Flip), F5A (Recurring Software Bit-Inversion), and F5B (Software Force-Value Model) were reproduced fresh directly against compiled production binaries (`bin/obj/mlkem768_inst.o` and `bin/obj/mlkem_fault_hooks.o`). Every output was verified byte-for-byte against the independent clean-room oracle:
   - F12: 100% `CLEAN_SUCCESS` (100/100)
   - F4: 100% `GENUINE_RECOVERY` (100/100)
   - F5A: 100% `SAFE_FAIL_STOP` (100/100)
   - F5B: 100% `SAFE_FAIL_STOP` (100/100)
3. **Forensic Data Integrity & Denominator Reconciliation:**  
   Reconstructed all historical trial datasets (Phases 5–11). Resolved historical clerical errors (Phase 8 text typo of 461 vs 561; Phase 9 F12 classification bug). Fully reconciled the reported pooled metrics:
   - **Pooled $H_1$ across vulnerable software models (F1, F2, F3, F6, F9, F10):** **561 / 600 (93.5%)**, 95% Wilson CI: **[91.2%, 95.2%]**.
   - **Pooled $H_2$ across all evaluated scenarios ($N=1,300$):** **0 / 1,300 (0.0%)**, 95% Wilson CI: **[0.0%, 0.28%]**.
4. **Claim Boundary & Disposition:**  
   Overstated claims asserting "universal fault immunity", "certified constant-time execution", or "physical hardware resilience" were audited and formally **withdrawn**. The central academic claim has been narrowed strictly to the defensible empirical evidence.

---

## 2. Directory Artifact Inventory

The [`phase12_reproducibility_audit/`](file:///Users/dhairyajain/Desktop/pqc%20research/phase12_reproducibility_audit/) directory contains the complete suite of verification tools, raw CSV datasets, and audit reports:

| Artifact File | Description | Primary Role |
| :--- | :--- | :--- |
| [`README.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase12_reproducibility_audit/README.md) | Executive audit overview and directory index | Audit Index |
| [`environment_and_build_manifest.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase12_reproducibility_audit/environment_and_build_manifest.md) | Repository commit, compiler flags, and SHA-256 hashes | Baseline Manifest |
| [`oracle_independent_verification.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase12_reproducibility_audit/oracle_independent_verification.md) | Technical audit of clean-room Keccak engine | Oracle Verification |
| [`oracle_test_vectors.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase12_reproducibility_audit/oracle_test_vectors.csv) | Execution log of 9 rate-boundary test vectors | Raw Test Vector Log |
| [`verify_oracle.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase12_reproducibility_audit/verify_oracle.c) | Standalone C source for boundary verification | Executable Code |
| [`production_reproduction_protocol.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase12_reproducibility_audit/production_reproduction_protocol.md) | In-tree hook call path, rules, and reproduction protocol | Reproduction Protocol |
| [`production_reproduction_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase12_reproducibility_audit/production_reproduction_trials.csv) | Raw trial log of 400 reproduced production trials | Raw Production Log |
| [`production_reproducer.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase12_reproducibility_audit/production_reproducer.c) | Standalone C reproduction harness | Executable Code |
| [`raw_data_integrity_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase12_reproducibility_audit/raw_data_integrity_audit.md) | Forensic analysis of historical CSV files and anomalies | Evidence Integrity |
| [`recalculated_h1_h2.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase12_reproducibility_audit/recalculated_h1_h2.csv) | Per-target recalculated $H_1$/$H_2$ with Wilson intervals | Reconciled Statistics |
| [`statistical_interpretation.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase12_reproducibility_audit/statistical_interpretation.md) | Denominator accounting and statistical methodology | Statistical Audit |
| [`fo_dualrail_claim_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase12_reproducibility_audit/fo_dualrail_claim_audit.md) | Critical audit of FO re-encryption and dual-rail logic | Security Architecture |
| [`claim_evidence_matrix.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase12_reproducibility_audit/claim_evidence_matrix.md) | Full matrix mapping proposed claims to dispositions | Claim Traceability |
| [`revised_research_claim.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase12_reproducibility_audit/revised_research_claim.md) | Narrow defensible claim, abstract, and disallowed claims | Academic Framing |
| [`limitations_and_open_questions.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase12_reproducibility_audit/limitations_and_open_questions.md) | Methodological boundaries and future roadmap | Pre-Submission Review |
| [`final_audit_verdict.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase12_reproducibility_audit/final_audit_verdict.md) | Four-tier epistemic classification verdict | Final Verdict |

---

## 3. Exact Commands to Reproduce Phase 12

```bash
# 1. Build and verify clean-room Keccak oracle across boundary vectors
clang -O2 -Wall -Wextra \
  phase12_reproducibility_audit/verify_oracle.c \
  -o phase12_reproducibility_audit/verify_oracle

./phase12_reproducibility_audit/verify_oracle

# 2. Build and execute 400 production reproduction trials
clang -O2 -Wall -Wextra -I. \
  phase12_reproducibility_audit/production_reproducer.c \
  bin/obj/mlkem768_inst.o \
  bin/obj/mlkem_fault_hooks.o \
  -o phase12_reproducibility_audit/production_reproducer

./phase12_reproducibility_audit/production_reproducer
```
