# Phase 7K: Clean-Room Reproducibility Protocol

## 1. Audit Scope & Protocol Design

This document specifies the exact protocol used to independently reproduce, build, and verify the fault resilience research claims for NIST FIPS 203 ML-KEM-768 decapsulation from a clean repository state.

### Core Principles:
- **Zero-Prior Assumption**: Prior reports and summaries are treated as hypotheses requiring experimental proof.
- **Traceable Execution**: Every metric, table, and conclusion must map to executable code, deterministic PRNG seeds, and raw data files.
- **Strict Distinction**: Autonomous in-place recovery ($K == K_{\text{valid}}$) is strictly separated from implicit safe rejection ($K == K_{\text{rej}}$) and benign equivalent behavior.

---

## 2. Clean-Room Execution Steps

### Step 1: System Baseline Verification
Record the exact commit, branch, and remote:
```bash
git rev-parse HEAD
git status
```
Baseline Commit: `02f0212a30359c9e5c88ed2b363890d445733800`

### Step 2: Build the Production Libraries and Test Harnesses
Compile the instrumented library and test harnesses from scratch:
```bash
make clean
make phase7j
```
*Compiler Command Executed*:
```bash
clang -O3 -Wall -Wextra -std=c11 -I/opt/homebrew/include -I. -Ialgorithms/source_ref/mlkem \
  experiments/phase7j/phase7j_independent_validator.c \
  bin/obj/mlkem768_inst.o bin/obj/mlkem_fault_hooks.o \
  -o bin/phase7j_independent_validator -L/opt/homebrew/lib -loqs
```

### Step 3: Run the Complete Audit and Regression Suite
```bash
make test-phase7j
```
This automated target executes:
1. `experiments/phase7j/audit_phase7i_analysis.py` (re-auditing Phase 7I raw data).
2. `bin/phase7j_independent_validator` (running all 16 extended threat classes, multi-run benchmarks, and randomized timing).
3. `tests/phase7j/test_phase7j_independent_validation.py` (running automated unit and regression checks).

### Step 4: Run Historical Regressions and Known Answer Tests
```bash
make test-phase7i
python3 -m unittest discover -s tests/phase7h -v
python3 -m unittest discover -s tests/phase7g -v
python3 -m unittest discover -s tests/phase7f -v
./bin/test_fips_kats
```

---

## 3. Reproducibility Checklist & Verification Status

| Step / Verification Target | Expected Result | Observed Result | Status |
| :--- | :--- | :--- | :---: |
| **Compilation** | Clean build with 0 errors | 0 errors, binary created in `bin/` | **PASS** |
| **Transform Butterfly Counts** | 5,376 Forward + 4,480 Inverse = 9,856 | Exactly 5,376 Fwd + 4,480 Inv = 9,856 | **PASS** |
| **Phase 7I Raw Data Audit** | 1,400 trials, 0 duplicates, 0 undetected | 1,400 trials, 0 duplicates, 0 undetected | **PASS** |
| **Phase 7J Extended Campaign** | 1,600 trials, 16 classes, 0 undetected | 1,600 trials, 16 classes, 0 undetected | **PASS** |
| **Public API Fail-Stop Contract** | `mlkem768_dec(NULL)` emits $K_{\text{rej}}$ | 100/100 trials emitted $K_{\text{rej}}$ | **PASS** |
| **Multi-Run Benchmarks** | Combined overhead bounded below 35% | Mean overhead +12.6% to +29.7% | **PASS** |
| **Randomized-Order Timing** | Median ratio 1.0000x, Cohen's $d < 0.20$ | Median 1.0000x, $d = 0.0399$ | **PASS** |
| **NIST FIPS 203 & 204 KATs** | 6/6 parameter sets match golden vectors | 100% PASS for ML-KEM and ML-DSA | **PASS** |
