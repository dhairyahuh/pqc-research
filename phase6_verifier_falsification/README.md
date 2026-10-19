# Phase 6: Independent Falsification of Recovery-Verifier Blindness Audit Package

**Auditor:** Skeptical Cryptographic Implementation Researcher  
**Date:** October 2026  
**Target:** ML-KEM-768 (FIPS 203) Implementation  
**Status:** Complete, Verified, and Fully Reproducible

---

## 1. Directory Contents and Artifact Sitemap

| File | Description |
|---|---|
| [`claim_and_threat_model.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase6_verifier_falsification/claim_and_threat_model.md) | Formal threat model and explicit separation between Hypothesis H1 (component false recovery) and H2 (protocol SDC). |
| [`phase5_harness_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase6_verifier_falsification/phase5_harness_audit.md) | Forensic line-by-line inspection of Phase 5 harness, explaining the mathematical origin of 94% and 70% false-recovery rates. |
| [`fault_injection_traceability.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase6_verifier_falsification/fault_injection_traceability.csv) | Full mapping of memory locations, injection timing, affected subsystems, and verification hooks for all 12 fault targets. |
| [`independent_oracle_design.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase6_verifier_falsification/independent_oracle_design.md) | Architecture and formal classification taxonomy of the Dual-Layer Independent Recovery Oracle. |
| [`genuine_recovery_falsification_harness.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase6_verifier_falsification/genuine_recovery_falsification_harness.c) | Standalone C test harness linking directly against compiled cryptographic object `bin/obj/mlkem768_inst.o`. |
| [`raw_trial_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase6_verifier_falsification/raw_trial_results.csv) | Empirical dataset containing 1,200 genuine fault injection trials across 12 targets with dual-layer trace data. |
| [`verifier_falsification_results.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase6_verifier_falsification/verifier_falsification_results.md) | Comprehensive experimental results falsifying verifier trust assumptions across 6 distinct attack loci. |
| [`dspc_collision_analysis.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase6_verifier_falsification/dspc_collision_analysis.md) | Mathematical analysis of DSPC affine linearity, proof of 2-bit correlated collisions, and empirical bypass tests. |
| [`recalculated_statistics.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase6_verifier_falsification/recalculated_statistics.md) | Per-fault-model statistical contingency matrix and 95% Wilson score confidence intervals. |
| [`limitations_and_research_contribution.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase6_verifier_falsification/limitations_and_research_contribution.md) | Explicit answers to research questions, residual failure modes, and smallest defensible research contribution. |
| [`README.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase6_verifier_falsification/README.md) | This document: build commands and reproduction guide. |

---

## 2. Build and Reproduction Instructions

### 2.1 Prerequisites
- A POSIX C11 compliant compiler (`clang` or `gcc`).
- Precompiled ML-KEM-768 instrumented object: `bin/obj/mlkem768_inst.o`.

### 2.2 Compilation Command
From the repository root (`/Users/dhairyajain/Desktop/pqc research`):

```bash
clang -O3 -Wall -Wextra -std=c11 \
  -I. -I algorithms/source_ref/mlkem \
  phase6_verifier_falsification/genuine_recovery_falsification_harness.c \
  bin/obj/mlkem768_inst.o \
  -o bin/phase6_falsification_harness
```

### 2.3 Execution Command
Execute the compiled harness:

```bash
./bin/phase6_falsification_harness
```

The harness will execute 1,200 trials (100 trials across 12 targets) in under 2 seconds, populating:
`phase6_verifier_falsification/raw_trial_results.csv`.

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

with open('phase6_verifier_falsification/raw_trial_results.csv') as f:
    rows = list(csv.DictReader(f))

targets = {}
for r in rows:
    tn = r['target_name']
    targets.setdefault(tn, {'tot': 0, 'h1': 0, 'h2': 0, 'dom': {}})
    targets[tn]['tot'] += 1
    if r['h1_false_recovery'] == '1': targets[tn]['h1'] += 1
    if r['h2_silent_corruption'] == '1': targets[tn]['h2'] += 1
    c = r['classification']
    targets[tn]['dom'][c] = targets[tn]['dom'].get(c, 0) + 1

for tn, d in targets.items():
    tot = d['tot']
    h1 = d['h1']
    h2 = d['h2']
    h1_low, h1_high = wilson(h1, tot)
    dom_c, dom_n = max(d['dom'].items(), key=lambda x: x[1])
    print(f'{tn:<35} | H1={h1:3d}/100 ({h1_low*100:4.1f}%-{h1_high*100:4.1f}%) | H2={h2:2d} | Dom={dom_c} ({dom_n})')
"
```
