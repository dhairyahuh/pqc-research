# TFIB Reproducibility Guide: Exact Commands, Environment, and Verification Steps

**Document:** Deliverable — Independent Reproducibility Runbook  
**Target:** ML-KEM-768 Twiddle Factor Integrity Binding (`TFIB-Ref` & `TFIB-Meta`)  
**Host Architecture:** Apple Silicon ARM64 (Apple M3 Pro), macOS Darwin 25.1.0, Apple Clang 17.0.0  

---

## 1. Prerequisites and Build Environment

Verify the compiler version and working directory:
```bash
cd "/Users/dhairyajain/Desktop/pqc research"
clang --version
# Expected: Apple clang version 17.0.0 or compatible LLVM/Clang
```

---

## 2. Step-by-Step Clean Build Pipeline

### Step 2.1: Compile Instrumented Production ML-KEM-768 Object
```bash
mkdir -p bin/obj
clang -c -O3 -Wall -Wextra \
  -Ialgorithms/source_ref/mlkem/include \
  -Ialgorithms/source_ref/mlkem/src \
  -DMLK_MULTILEVEL_BUILD_NO_SHARED \
  algorithms/source_ref/mlkem/src/poly.c \
  algorithms/source_ref/mlkem/src/indcpa.c \
  algorithms/source_ref/mlkem/src/kem.c \
  algorithms/source_ref/mlkem/src/verify.c \
  algorithms/source_ref/fips202/fips202.c \
  -o bin/obj/mlkem768_inst.o
```
**Expected Exit Code:** `0`

### Step 2.2: Compile TFIB Static Library (`libtfib.a`)
```bash
clang -O3 -c \
  -Ialgorithms/source_ref/mlkem/include \
  -Itfib_implementation \
  tfib_implementation/tfib_ref.c \
  tfib_implementation/tfib_meta.c \
  tfib_implementation/tfib_hooks.c \
  tfib_implementation/tfib_core.c && \
ar rcs tfib_implementation/libtfib.a tfib_ref.o tfib_meta.o tfib_hooks.o tfib_core.o && \
rm -f tfib_*.o
```
**Expected Exit Code:** `0`  
**Output Artifact:** `tfib_implementation/libtfib.a`

---

## 3. Step-by-Step Experiment Execution

### Step 3.1: Reproduce Full Experimental Suites (900 Trials)
Execute the independent validity audit runner:
```bash
clang -O3 \
  -Ialgorithms/source_ref/mlkem/include \
  -Itfib_implementation \
  tfib_experiments/tfib_validity_audit_runner.c \
  bin/obj/mlkem768_inst.o \
  tfib_implementation/libtfib.a \
  -o tfib_experiments/tfib_validity_audit_runner && \
./tfib_experiments/tfib_validity_audit_runner
```
**Expected Exit Code:** `0`  
**Generated Artifacts:**
- `tfib_trial_level_results.csv` (901 lines: header + 900 individual trials)
- `tfib_reproduced_results.csv` (19 lines: header + 18 aggregated test suites)

### Step 3.2: Reassess Performance & Sample-Level Tail Latency
Execute the high-precision 40,000-sample benchmark runner:
```bash
clang -O3 \
  -Ialgorithms/source_ref/mlkem/include \
  -Itfib_implementation \
  tfib_experiments/tfib_benchmark_audit.c \
  bin/obj/mlkem768_inst.o \
  tfib_implementation/libtfib.a \
  -lm \
  -o tfib_experiments/tfib_benchmark_audit && \
./tfib_experiments/tfib_benchmark_audit
```
**Expected Exit Code:** `0`  
**Generated Artifact:**
- `tfib_benchmark_raw.csv` (40,001 lines: header + 40,000 raw timing records)

---

## 4. Verification and Audit Assertions

To programmatically assert that the generated datasets are valid and match the audit conclusions:

```bash
# 1. Assert exactly 900 trial records exist in trial-level CSV:
[ $(wc -l < tfib_trial_level_results.csv) -eq 901 ] && echo "[PASS] Trial CSV complete" || echo "[FAIL] Trial CSV row count mismatch"

# 2. Assert exactly 40,000 benchmark timing records exist in raw benchmark CSV:
[ $(wc -l < tfib_benchmark_raw.csv) -eq 40001 ] && echo "[PASS] Benchmark CSV complete" || echo "[FAIL] Benchmark CSV row count mismatch"

# 3. Assert zero Silent Data Corruption (SDC) across all 900 trials:
grep -c "SILENT_DATA_CORRUPTION" tfib_trial_level_results.csv | grep -q "^0$" && echo "[PASS] Zero SDC confirmed" || echo "[FAIL] SDC detected!"

# 4. Assert 100% recovery on transient operational twiddle under TFIB-Ref:
grep "TFIB_REF,OP_TWIDDLE_TRANSIENT" tfib_trial_level_results.csv | grep -c "GENUINE_RECOVERY" | grep -q "^50$" && echo "[PASS] 100% TFIB-Ref recovery confirmed" || echo "[FAIL] Recovery rate mismatch"

# 5. Assert 0% local detection on baseline operational twiddle (Theorem 1):
grep "BASELINE,OP_TWIDDLE_TRANSIENT" tfib_trial_level_results.csv | grep -c ",1," | grep -q "^0$" && echo "[PASS] Theorem 1 confirmed (0% local detection)" || echo "[FAIL] Baseline unexpectedly detected twiddle fault"
```
