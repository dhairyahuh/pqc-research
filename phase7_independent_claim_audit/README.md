# Phase 7: Independent Source-Level Audit of Phase 6 Claims Package

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Target:** ML-KEM-768 (FIPS 203) Implementation  
**Status:** Complete, Verified, and Fully Reproducible

---

## 1. Directory Contents and Artifact Sitemap

| File | Description |
|---|---|
| [`phase6_source_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/phase6_source_audit.md) | Forensic inspection of Phase 6 harness, object files, and discovery of the 1D oracle reference collision bug. |
| [`h1_independent_oracle_results.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/h1_independent_oracle_results.md) | Independent re-evaluation of Hypothesis H1 using the corrected multi-polynomial reference oracle. |
| [`f1_arithmetic_reconciliation.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/f1_arithmetic_reconciliation.md) | Forensic reconciliation of the F1 arithmetic discrepancy, proving exact signed 16-bit overflow residue ($\pm 2285$). |
| [`f2_stage_outcome_reconciliation.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/f2_stage_outcome_reconciliation.md) | Detailed resolution of F2 stage-dependent diffusion, explaining the 30% genuine recovery and 70% downstream rejection split. |
| [`f4_classification_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/f4_classification_audit.md) | Forensic trace and correction of Target F4, resolving the contradiction between H1 and `RECOVERED_GENUINE`. |
| [`h2_decapsulation_verification.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/h2_decapsulation_verification.md) | Independent verification of Hypothesis H2 across 591 blinded trials, proving zero SDC in decapsulation. |
| [`dspc_implementation_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/dspc_implementation_audit.md) | Implementation audit of DSPC across 6 failure scenarios, analyzing physical feasibility vs. software construction. |
| [`recalculated_statistics.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/recalculated_statistics.md) | Corrected master statistics contingency matrix with 95% Wilson score confidence intervals. |
| [`claim_evidence_matrix.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/claim_evidence_matrix.md) | Partition table separating reproduced findings, contradicted claims, and untested hypotheses, with direct audit answers. |
| [`derived_corrected_trial_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/derived_corrected_trial_results.csv) | Derived empirical dataset of 1,200 trials with corrected polynomial reference tracking. |
| [`genuine_phase7_audit_harness.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/genuine_phase7_audit_harness.c) | Standalone C harness with multi-polynomial reference oracle. |
| [`README.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/README.md) | This document: build commands and audit guide. |

---

## 2. Build and Reproduction Instructions

### 2.1 Prerequisites
- POSIX-compliant C toolchain (Clang or GCC) supporting C11.
- Precompiled ML-KEM-768 instrumented object: `bin/obj/mlkem768_inst.o`.

### 2.2 Compilation Command
From the repository root (`/Users/dhairyajain/Desktop/pqc research`):

```bash
clang -O3 -Wall -Wextra -std=c11 \
  -I. -I algorithms/source_ref/mlkem \
  phase7_independent_claim_audit/genuine_phase7_audit_harness.c \
  bin/obj/mlkem768_inst.o \
  -o bin/phase7_audit_harness
```

### 2.3 Execution Command
Execute the compiled harness:

```bash
./bin/phase7_audit_harness
```

Execution will run 1,200 trials in under 2 seconds and produce:
`phase7_independent_claim_audit/derived_corrected_trial_results.csv`.

### 2.4 Verify Statistics
Run the verification script:

```bash
python3 -c "
import csv, math

def wilson(s, n):
    if n == 0: return (0, 0)
    z = 1.95996
    p = s / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    w = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / d
    return (max(0, c - w), min(1, c + w))

with open('phase7_independent_claim_audit/derived_corrected_trial_results.csv') as f:
    rows = list(csv.DictReader(f))

targets = {}
for r in rows:
    tn = r['target_name']
    targets.setdefault(tn, {'n': 0, 'h1': 0, 'h2': 0, 'dom': {}})
    targets[tn]['n'] += 1
    if r['h1_false_recovery'] == '1': targets[tn]['h1'] += 1
    if r['h2_silent_corruption'] == '1': targets[tn]['h2'] += 1
    c = r['classification']
    targets[tn]['dom'][c] = targets[tn]['dom'].get(c, 0) + 1

for tn, d in targets.items():
    n = d['n']
    h1 = d['h1']
    h2 = d['h2']
    h1_l, h1_h = wilson(h1, n)
    dom_c, dom_n = max(d['dom'].items(), key=lambda x: x[1])
    print(f'{tn:<35} | H1={h1:3d} ({h1/n*100:5.1f}%) [{h1_l*100:4.1f}%,{h1_h*100:4.1f}%] | H2={h2:2d} | Dom={dom_c} ({dom_n})')
"
```
