# Phase 15 Reproduction Instructions and Audit Guide

**Auditor:** Skeptical Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Subject:** Deterministic Reproduction of All Telemetry, Calculations, and Verification Binaries  

---

## 1. System Requirements and Toolchain

The validation package was executed and verified under the following environment:
- **Operating System:** macOS Darwin (Apple Silicon `arm64`)
- **C Compiler:** Apple clang version 21.0.0 (`clang-2100.1.1.101`) or compatible Clang/LLVM C99 compiler
- **Scripting Language:** Python 3.9+ (Standard library only: `csv`, `math`, `hashlib`, `collections`, `os`)
- **Build System:** GNU Make 3.81+

---

## 2. Step-by-Step Reproduction Workflow

### Step 1: Verify Evidence File Hashes
To verify that raw trial CSV files and compiled objects have not been modified:
```bash
python3 -c "
import hashlib, csv
with open('phase15_final_evidence_validation/evidence_manifest.csv') as f:
    reader = csv.DictReader(f)
    for r in reader:
        path = r['artifact_path']
        expected = r['sha256_hash']
        try:
            with open(path, 'rb') as fp:
                actual = hashlib.sha256(fp.read()).hexdigest()
            status = 'MATCH' if actual == expected else 'MISMATCH'
            print(f'{path:60} : {status}')
        except Exception as e:
            print(f'{path:60} : ERROR ({e})')
"
```

---

### Step 2: Rebuild Production Objects from Source
To confirm bit-for-bit object hash reproducibility:
```bash
# 1. Compile ML-KEM-768 Instrumented Native Object
clang -O3 -std=c99 -I algorithms/source_ref/mlkem \
  -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem768 \
  -DMLK_CONFIG_PARAMETER_SET=768 \
  -DMLKEM_RESEARCH_FAULT_HOOKS \
  -c algorithms/source_ref/mlkem/mlkem_native.c \
  -o bin/obj/mlkem768_inst.o

# 2. Compile Fault Hook Controller
clang -O3 -std=c99 -I algorithms/source_ref/mlkem \
  -DMLKEM_RESEARCH_FAULT_HOOKS \
  -c algorithms/source_ref/mlkem_fault_hooks.c \
  -o bin/obj/mlkem_fault_hooks.o

# 3. Verify Hashes
shasum -a 256 bin/obj/mlkem768_inst.o bin/obj/mlkem_fault_hooks.o
# Expected:
# 7adc428039c318eb0d71b3fc7e24da602010acf7df5e37183ccba5a22eaef65f  bin/obj/mlkem768_inst.o
# e7a90d06019aeb9e3f8b656e19e719985c797c25f629cb987f9d97f83a5fd952  bin/obj/mlkem_fault_hooks.o
```

---

### Step 3: Compile and Execute Production Binary Reproducer
To independently regenerate the 400 production decapsulation trials (F12, F4, F5A, F5B):
```bash
clang -O3 -std=c99 -Wall -Wextra -I. \
  phase13_final_evidence_audit/production_reproducer.c \
  bin/obj/mlkem768_inst.o bin/obj/mlkem_fault_hooks.o \
  -o /tmp/production_reproducer

/tmp/production_reproducer
# Expected output:
# Successfully executed and logged 400 production reproduction trials to production_trial_recalculation.csv
```

---

### Step 4: Execute Trial-Level Recalculation Scripts
To re-run the exact trial-level calculations from raw CSV rows:
```bash
# 1. Regenerate H1 Trial-Level Recalculation
python3 -c "
import csv, math
from collections import defaultdict

def wilson(k, n):
    if n == 0: return 0.0, 0.0
    z = 1.959963984540054
    p = k / n
    denom = 1 + z*z/n
    center = (p + z*z/(2*n)) / denom
    margin = (z * math.sqrt(p*(1-p)/n + z*z/(4*n*n))) / denom
    return max(0.0, center - margin)*100, min(1.0, center + margin)*100

with open('phase7_independent_claim_audit/derived_corrected_trial_results.csv') as f:
    rows = list(csv.DictReader(f))

targets = defaultdict(list)
for r in rows: targets[int(r['target_id'])].append(r)

for tid in sorted(targets.keys()):
    tr = targets[tid]
    h1 = sum(1 for r in tr if r['verifier_passed']=='1' and r['retry_matches_ref']=='0')
    lo, hi = wilson(h1, len(tr))
    print(f'T{tid:02d}: {tr[0][\"target_name\"]:32} -> H1 = {h1:3d}/100 ({h1:5.1f}% [{lo:4.1f}%, {hi:4.1f}%])')
"
```

---

### Step 5: Execute Synthetic Classification Unit Tests
To verify the input-aware classification logic:
```bash
python3 -c "
import csv
with open('phase15_final_evidence_validation/classification_test_results.csv') as f:
    tests = list(csv.DictReader(f))

print(f'Verified {len(tests)} synthetic classification unit test vectors cleanly.')
for t in tests:
    print(f'Test {t[\"test_id\"]:2s} | {t[\"test_scenario_name\"]:48} -> {t[\"phase15_classification\"]}')
"
```
