# Phase 5: Recovery-Path and Monitor-State Fault Analysis Audit Package

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Target:** ML-KEM-768 (FIPS 203) Implementation  
**Status:** Complete, Verified, and Fully Reproducible

---

## 1. Directory Contents and Artifact Sitemap

| File | Description |
|---|---|
| [`recovery_trust_boundary.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase5_recovery_trust_audit/recovery_trust_boundary.md) | Comprehensive source mapping of operand capture, retry rollback, verifier equations, and fail-stop logic in `poly.c`, `kem.c`, and `mlkem_fault_hooks.c`. |
| [`fault_target_matrix.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase5_recovery_trust_audit/fault_target_matrix.csv) | Machine-readable definition of all 10 fault targets, injection loci, fault models, expected paths, and theoretical outcomes. |
| [`source_level_injection_map.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase5_recovery_trust_audit/source_level_injection_map.md) | Technical description of injection mechanisms, hardware physical counterparts, and source-level hooks without test-wrapper simulation. |
| [`genuine_recovery_fault_harness.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase5_recovery_trust_audit/genuine_recovery_fault_harness.c) | Standalone, reproducible C test harness linking directly against real compiled cryptographic object (`bin/obj/mlkem768_inst.o`). |
| [`raw_trial_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase5_recovery_trust_audit/raw_trial_results.csv) | Ground-truth empirical output of 1,300 genuine injection trials across baseline, mitigated, and state-faulted variants. |
| [`per_fault_model_statistics.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase5_recovery_trust_audit/per_fault_model_statistics.md) | Non-pooled statistical breakdown with 95% Wilson score confidence intervals, exact contingency matrix, and mathematical explanations. |
| [`oracle_independence_review.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase5_recovery_trust_audit/oracle_independence_review.md) | Formal proof and architectural analysis of the external output oracle and the 7-tier classification taxonomy. |
| [`demonstrated_failure_cases.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase5_recovery_trust_audit/demonstrated_failure_cases.md) | Detailed analysis of demonstrated failure modes: Tautological Recovery Blindness, Monitor State Zeroing, and Dual-Rail Defense Barrier. |
| [`mitigation_experiment.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase5_recovery_trust_audit/mitigation_experiment.md) | Implementation and adversarial validation of Dual-Snapshot Parity Checksum (DSPC), including testing against faults on its own state. |
| [`README.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase5_recovery_trust_audit/README.md) | This document: build commands, reproduction instructions, and audit summary. |

---

## 2. Build and Reproduction Instructions

### 2.1 Prerequisites
- A POSIX-compliant C toolchain (Clang or GCC) supporting C11.
- Precompiled ML-KEM-768 instrumented object: `bin/obj/mlkem768_inst.o`.

### 2.2 Compilation Command
From the repository root (`/Users/dhairyajain/Desktop/pqc research`):

```bash
clang -O3 -Wall -Wextra -std=c11 \
  -I. -I algorithms/source_ref/mlkem \
  phase5_recovery_trust_audit/genuine_recovery_fault_harness.c \
  bin/obj/mlkem768_inst.o \
  -o bin/phase5_genuine_recovery_fault_harness
```

### 2.3 Execution Command
Execute the compiled binary:

```bash
./bin/phase5_genuine_recovery_fault_harness
```

Execution will run 1,300 trials in under 2 seconds and generate:
`phase5_recovery_trust_audit/raw_trial_results.csv`.

### 2.4 Verify Statistics and Wilson Confidence Intervals
Run the validation script against the newly generated CSV:

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

with open('phase5_recovery_trust_audit/raw_trial_results.csv') as f:
    rows = list(csv.DictReader(f))

targets = {}
for r in rows:
    tn = r['target_name']
    targets.setdefault(tn, {})
    c = r['classification']
    targets[tn][c] = targets[tn].get(c, 0) + 1

for tn, d in targets.items():
    tot = sum(d.values())
    dom_c, dom_n = max(d.items(), key=lambda x: x[1])
    low, high = wilson(dom_n, tot)
    print(f'{tn:<40} : {dom_c:<24} {dom_n}/{tot} ({dom_n/tot*100:5.1f}%) 95%CI=[{low*100:5.1f}%, {high*100:5.1f}%]')
"
```
