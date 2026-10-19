# Phase 4 Evidence Reconciliation & Research Baseline

This directory contains the independent cryptographic audit, trial matrix reconciliation, fault injection traceability analysis, validated statistical metrics, timing reviews, and research baseline for ML-KEM-768 fault resilience.

---

## Deliverables Manifest

| File | Description |
| :--- | :--- |
| `trial_matrix_reconciliation.md` | Full reconciliation of the 2,400-trial matrix across all 28 distinct bins, detailing the terminal display truncation and classification corrections. |
| `fault_injection_traceability.csv` | Field-by-field trace of all 6 target models from harness calls to exact source file lines, variables, storage classes, and persistence. |
| `recovery_outcome_validation.md` | Deep audit of the 100 reported recoveries in Targets T3 and T4, exposing the snapshot timing bug and verifying arithmetic recovery. |
| `validated_countermeasure_results.csv` | Reconciled dataset (2,400 rows) with validated classifications and explicit distinction between in-tree and hypothetical variants. |
| `recalculated_statistics.md` | Recalculated Wilson 95% confidence intervals, per-target detection, recovery, safe rejection, SDC, and false-alarm rates. |
| `timing_claim_review.md` | Technical audit of POSIX monotonic timing measurements, experimental controls, and critical review of SIFA claims. |
| `cross_layer_assumption_review.md` | Distinction between model-level assumptions vs. empirical evidence in the cross-layer space communication framework. |
| `research_baseline.md` | Comprehensive baseline detailing reproduced findings, failed claims, invalid trials, research gaps, and the smallest falsifiable next experiment. |
| `README.md` | Environment configuration, build commands, and reproduction instructions. |

---

## Environment & Build Specifications

- **Host Environment**: macOS (Darwin 24.x, Apple Silicon ARM64) / Linux x86_64
- **C Compiler**: Apple Clang $\ge 15.0$ or GCC $\ge 11.0$ (`clang -O3 -Wall -Wextra -std=c11`)
- **Python Runtime**: Python $\ge 3.9$ (Standard library dependencies: `csv`, `math`, `struct`, `hmac`, `hashlib`, `random`)
- **Source Objects**: `bin/obj/mlkem768_inst.o`, `bin/obj/mlkem_fault_hooks.o`

---

## Exact Reproduction Commands

### 1. Reconcile the Trial Matrix and Verify Records
```bash
python3 -c '
import csv
from collections import Counter

records = list(csv.DictReader(open("phase4_evidence_reconciliation/validated_countermeasure_results.csv")))
print(f"Total Validated Records: {len(records)}")

counts = Counter((r["variant_name"], r["target_name"], r["validated_classification"]) for r in records)
for (v, tg, cl), c in sorted(counts.items()):
    print(f"{v:<32} | {tg:<26} | {cl:<35} | {c}")
'
```

### 2. Verify Recalculated Wilson Statistics
```bash
python3 -c '
import csv, math
from collections import defaultdict

def wilson_ci(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k / n; d = 1 + (z**2) / n
    c = (p + (z**2) / (2 * n)) / d
    m = (z * math.sqrt((p * (1 - p) / n) + (z**2) / (4 * n**2))) / d
    return (max(0.0, c - m), min(1.0, c + m))

records = list(csv.DictReader(open("phase4_evidence_reconciliation/validated_countermeasure_results.csv")))
grouped = defaultdict(list)
for r in records: grouped[(r["variant_name"], r["target_name"])].append(r)

for (v, tg), rows in sorted(grouped.items()):
    n_att = len(rows)
    n_trig = sum(1 for r in rows if int(r["triggered"]) == 1)
    if tg == "T6_CLEAN_CONTROL":
        fp = sum(1 for r in rows if r["validated_classification"] != "CORRECT_CLEAN_EXECUTION")
        print(f"{v:<32} | {tg:<24} | Clean Control (FP: {fp}/{n_att})")
    elif tg == "T2_REFERENCE_TABLE_CORRUPT" and v != "VARIANT_B_GENUINE_TABLE_CHECK":
        print(f"{v:<32} | {tg:<24} | Not Estimable (0 Triggered)")
    else:
        det = sum(1 for r in rows if "REJECTED" in r["validated_classification"] or "RECOVERED" in r["validated_classification"])
        lo, hi = wilson_ci(det, n_trig)
        print(f"{v:<32} | {tg:<24} | Det: {det/n_trig*100:5.1f}% [{lo*100:4.1f}%, {hi*100:4.1f}%]")
'
```

### 3. Re-Execute Protocol Sensitivity Sweeps
```bash
python3 phase3_harness_audit/harness/cross_layer_sensitivity.py
```

---

## Auditor Summary of Validated Truth

1. **NTT Monitor Invariant Scope**: The in-tree butterfly monitor is an effective detector of internal arithmetic errors ($t$), but is algebraically blind to shared twiddle factors ($\zeta$).
2. **True Downstream Security**: ML-KEM-768 security against twiddle factor manipulation is provided by the Fujisaki-Okamoto re-encryption check, which safely rejects corrupted ciphertexts with 97% probability (and 3% benign absorption), maintaining **0 SDCs across 2,400 trials**.
3. **Recovery Mechanism Limitation**: In-place recovery succeeds for transient register glitches, but the current verifier is tautological with respect to saved snapshot memory (`u_saved`), meaning a corrupted snapshot cannot be safely recovered without independent checksums.
4. **Observable Timing Gap**: Fail-stop decapsulation exhibits an observable $+44.2\%$ latency delta relative to clean decapsulation, requiring constant-time busy-wait padding in production environments.
