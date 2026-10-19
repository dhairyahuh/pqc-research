# Phase 3 Harness Audit & Independent Verification

This directory contains the independent adversarial audit of Phase 2 experimental harnesses, the genuine outcome-observation test harness, statistical analyses, cross-layer protocol sensitivity simulations, and the research-direction decision brief.

---

## Deliverables Manifest

| File | Description |
| :--- | :--- |
| `phase3_harness_audit.md` | Comprehensive technical audit of Phase 2 harnesses, exposing manual status overrides, variant inequivalence, and claim verdicts. |
| `genuine_fault_test_plan.md` | Formal specification for the genuine outcome-observation harness without forced metrics. |
| `countermeasure_results.csv` | Raw 2,400-trial dataset from the genuine countermeasure test harness across 4 variants and 6 target fault models. |
| `statistical_analysis.md` | Wilson score 95% confidence intervals, per-target detection, recovery, safe rejection, and SDC rate analysis. |
| `cross_layer_protocol_audit.md` | Architectural specification of spacecraft endpoint FSM, telecommand framing, and adversarial sensitivity evaluation. |
| `cross_layer_sensitivity_results.csv` | Empirical results of 15 parameter sweeps across channel loss, BER, computational SEU, persistent faults, and reboots. |
| `research_gap_and_literature_check.md` | Rigorous literature analysis comparing Direction A (NTT invariants/recovery) vs. Direction B (cross-layer space protocol). |
| `supervisor_decision_brief.md` | Strategic brief for the supervisor summarizing reproduced findings, failed reproductions, unknowns, and recommended path. |
| `README.md` | Reproduction guide, compiler configurations, environment specifications, and known limitations. |
| `harness/genuine_countermeasure_test.c` | C source code for the genuine outcome-observation test harness (strictly zero manual status assignments). |
| `harness/cross_layer_sensitivity.py` | Python simulation harness evaluating the cross-layer space communication protocol under adversarial conditions. |

---

## System Requirements & Build Environment

- **Operating System**: macOS (Darwin 24.x / Apple Silicon ARM64) or Linux x86_64
- **C Compiler**: Apple Clang $\ge 15.0.0$ or GCC $\ge 11.0.0$ (`clang -O3 -Wall -Wextra -std=c11`)
- **Python**: Python $\ge 3.9$ (standard library: `struct`, `hmac`, `hashlib`, `random`, `math`, `csv`)
- **Cryptography Libraries**: In-tree ML-KEM-768 object files (`bin/obj/mlkem768_inst.o`, `bin/obj/mlkem_fault_hooks.o`)

---

## Step-by-Step Reproduction Instructions

### 1. Compile the Genuine Outcome-Observation Harness
```bash
clang -O3 -Wall -Wextra -std=c11 \
  -I. -I algorithms/source_ref/mlkem \
  phase3_harness_audit/harness/genuine_countermeasure_test.c \
  bin/obj/mlkem768_inst.o \
  bin/obj/mlkem_fault_hooks.o \
  -o /tmp/genuine_countermeasure_test
```

### 2. Execute Genuine Countermeasure Campaign (2,400 Trials)
```bash
/tmp/genuine_countermeasure_test
```
*Outputs:* Matrix summary printed to terminal; detailed trial log written to `phase3_harness_audit/countermeasure_results.csv`.

### 3. Run Statistical Verification Script
```bash
python3 -c '
import csv, math
from collections import defaultdict

def wilson_ci(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k / n
    d = 1 + (z**2) / n
    c = (p + (z**2) / (2 * n)) / d
    m = (z * math.sqrt((p * (1 - p) / n) + (z**2) / (4 * n**2))) / d
    return (max(0.0, c - m), min(1.0, c + m))

data = defaultdict(lambda: defaultdict(int))
with open("phase3_harness_audit/countermeasure_results.csv") as f:
    for row in csv.DictReader(f):
        data[(row["variant_name"], row["target_name"])][row["genuine_classification"]] += 1
        data[(row["variant_name"], row["target_name"])]["TOTAL"] += 1

for (v, tg), c in sorted(data.items()):
    n = c["TOTAL"]
    det = c["FAULT_DETECTED_AND_SAFELY_REJECTED"] + c["FALSE_POSITIVE_ABORT"] + c["SAFELY_QUENCHED_REJECT"] + c["FAULT_DETECTED_AND_RECOVERED"]
    lo, hi = wilson_ci(det, n)
    print(f"{v:<32} | {tg:<26} | Det: {det/n*100:5.1f}% [{lo*100:4.1f}%, {hi*100:4.1f}%]")
'
```

### 4. Execute Cross-Layer Protocol Sensitivity Sweeps
```bash
python3 phase3_harness_audit/harness/cross_layer_sensitivity.py
```
*Outputs:* 15 parameter sweeps written to `phase3_harness_audit/cross_layer_sensitivity_results.csv`.

---

## Known Limitations and Audit Notes

1. **Software Fault Injection Abstraction**: Single-bit flips in C integer registers simulate transient bit flips (SEUs) at the ISA level. They do not simulate analog physical transient pulses (SETs) in clock distribution or supply rails.
2. **Timing Side Channel Across Execution Modes**: The fail-stop path terminates in $\approx 153.1\,\mu\text{s}$, whereas clean decapsulation completes in $\approx 106.2\,\mu\text{s}$. This $+44.2\%$ latency delta is observable to a network-level adversary and must be padded with constant-time dummy cycles in production deployments.
3. **Common-Mode Linker Folding**: Secondary reference tables stored in `.rodata` will be merged with operational tables by modern optimizing linkers unless separated via explicit linker scripts or placed in physically partitioned memory segments.
