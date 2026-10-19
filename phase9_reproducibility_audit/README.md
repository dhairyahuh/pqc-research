# Phase 9: Reproducibility, Evidence Integrity, and Claim-Boundary Audit

**Auditor:** Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Audit Directory:** [`phase9_reproducibility_audit/`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit)  

---

## 1. Executive Summary

Phase 9 establishes the definitive reproducibility, evidence integrity, and claim boundaries of the ML-KEM-768 fault resilience research. All prior artifacts from Phases 1 through 8 have been preserved unchanged.

### Core Audit Findings:
1. **Bit-for-Bit Object Reproducibility:**  
   The precompiled production objects `bin/obj/mlkem768_inst.o` and `bin/obj/mlkem_fault_hooks.o` were rebuilt from source using Apple clang 21.0.0; their SHA-256 hashes matched the repository objects **bit-for-bit** ([`repository_and_build_identity.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/repository_and_build_identity.md)).
2. **Authentic Production-Object Execution:**  
   Targets **F4 (transient recovery)**, **F5 (persistent fail-stop)**, and **F12 (clean baseline)** were independently reproduced across 300 fresh trials linking strictly against `bin/obj/mlkem768_inst.o` and `bin/obj/mlkem_fault_hooks.o` with **zero harness stubs or metric overrides** ([`production_path_reproduction.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/production_path_reproduction.md)).
3. **Symbol Resolution Verified:**  
   Binary inspection (`nm`) confirmed that `production_reproducer` binds all monitor functions and fault hooks directly to `mlkem_fault_hooks.o` ([`symbol_resolution_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/symbol_resolution_audit.md)).
4. **F2 Empirical Trace Verified:**  
   100 fresh trials in `f2_tracer` verified that the 30% genuine recovery / 70% downstream rejection split is an exact consequence of butterfly diffusion depth relative to the 10-bit ciphertext compression rounding margin ([`f2_causal_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/f2_causal_audit.md)).
5. **Rigorous Outcome Separation:**  
   H1 (Internal False Recovery) and H2 (Accepted Incorrect Shared Secret) were recalculated with exact denominators and 95% Wilson score confidence intervals ([`h1_h2_recalculation.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/h1_h2_recalculation.md)).

---

## 2. Directory Sitemap and Deliverables

| File | Type | Description |
| :--- | :---: | :--- |
| [`README.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/README.md) | Guide | Executive summary, directory manifest, and reproduction instructions (this file). |
| [`repository_and_build_identity.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/repository_and_build_identity.md) | Audit | Git commit, toolchain, build flags, and bit-for-bit SHA-256 rebuild verification. |
| [`production_path_reproduction.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/production_path_reproduction.md) | Report | Independent reproduction of 300 production-object trials (F4, F5, F12). |
| [`symbol_resolution_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/symbol_resolution_audit.md) | Audit | Disassembly and symbol binding audit proving genuine production object execution. |
| [`raw_trial_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/raw_trial_results.csv) | Dataset | Raw CSV records for 300 production-object trials. |
| [`outcome_definitions_and_counts.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/outcome_definitions_and_counts.md) | Analysis | Formal operational formulas, denominators, and mutually exclusive outcome categories. |
| [`h1_h2_recalculation.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/h1_h2_recalculation.md) | Statistics | Statistical recalculation of H1 and H2 with 95% Wilson score confidence intervals. |
| [`fo_and_dual_rail_claim_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/fo_and_dual_rail_claim_audit.md) | Audit | Analysis of constant-time properties, assembly disassembly, and dual-rail boundaries. |
| [`f2_trace_evidence.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/f2_trace_evidence.csv) | Dataset | Raw trial-level records across 100 trials linking stages, diffs, and FO fail flags. |
| [`f2_causal_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/f2_causal_audit.md) | Report | Empirical validation and mathematical origin of F2 stage-dependent outcome split. |
| [`claim_evidence_matrix.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/claim_evidence_matrix.md) | Taxonomy | Master claim classification matrix categorizing all research claims (Phases 1–9). |
| [`limitations_and_unresolved_questions.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/limitations_and_unresolved_questions.md) | Scope | Pre-submission scientific checklist and physical experimental gaps. |

---

## 3. Reproduction Instructions

### 3.1 Rebuild Production Objects from Source
```bash
clang -O3 -std=c99 -I algorithms/source_ref/mlkem \
  -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem768 -DMLK_CONFIG_PARAMETER_SET=768 \
  -DMLKEM_RESEARCH_FAULT_HOOKS \
  -c algorithms/source_ref/mlkem/mlkem_native.c -o /tmp/mlkem768_inst.o

clang -O3 -std=c99 -I algorithms/source_ref/mlkem \
  -DMLKEM_RESEARCH_FAULT_HOOKS \
  -c algorithms/source_ref/mlkem_fault_hooks.c -o /tmp/mlkem_fault_hooks.o

# Verify SHA-256 match
shasum -a 256 /tmp/mlkem768_inst.o bin/obj/mlkem768_inst.o
shasum -a 256 /tmp/mlkem_fault_hooks.o bin/obj/mlkem_fault_hooks.o
```

### 3.2 Execute 300 Production-Object Trials (F4, F5, F12)
```bash
clang -O3 -Wall -Wextra -std=c11 -I. -I algorithms/source_ref/mlkem \
  phase9_reproducibility_audit/production_reproducer.c \
  bin/obj/mlkem768_inst.o bin/obj/mlkem_fault_hooks.o \
  -o bin/phase9_reproducer

./bin/phase9_reproducer
```

### 3.3 Execute 100 F2 Stage-Trace Trials
```bash
clang -O3 -Wall -Wextra -std=c11 -I. -I algorithms/source_ref/mlkem \
  phase9_reproducibility_audit/f2_tracer.c \
  bin/obj/mlkem768_inst.o \
  -o bin/phase9_f2_tracer

./bin/phase9_f2_tracer
```

### 3.4 Verify Trial Statistics via Python
```bash
python3 -c "
import pandas as pd
df = pd.read_csv('phase9_reproducibility_audit/raw_trial_results.csv')
print(df.groupby(['target', 'outcome']).size())
f2 = pd.read_csv('phase9_reproducibility_audit/f2_trace_evidence.csv')
print(f2.groupby(['stage', 'outcome']).size())
"
```
