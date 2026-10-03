#!/usr/bin/env bash
# ==============================================================================
# Phase 2 — Step 2C-A: Countermeasure Independence & Common-Mode Fault Analysis
# Build, Validation, and Trial Execution Script
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

echo "================================================================================"
echo "Running Phase 2 Step 2C-A Build, Verification & Experiment Suite"
echo "Working Directory: ${REPO_ROOT}"
echo "================================================================================"

# Verify liboqs dependency
LIBOQS_PREFIX="${LIBOQS_PREFIX:-/opt/homebrew/opt/liboqs}"
if [ ! -d "${LIBOQS_PREFIX}" ]; then
    echo "ERROR: liboqs not found at ${LIBOQS_PREFIX}." >&2
    exit 1
fi

echo "[*] Step 1: Compiling Independent Oracle Static Library..."
make -C tfib_experiments/phase11_oracle all

echo "[*] Step 2: Compiling Step 2C-A Validation Test Suite..."
clang -O3 \
  -Ialgorithms/source_ref/mlkem/include \
  -Itfib_implementation \
  -Itfib_experiments \
  -Itfib_experiments/phase11_oracle \
  -I/opt/homebrew/opt/liboqs/include \
  tfib_experiments/test_step2c_countermeasure_independence.c \
  bin/obj/mlkem768_inst.o \
  tfib_implementation/libtfib.a \
  tfib_experiments/phase11_oracle/libindependent_oracle.a \
  -L/opt/homebrew/opt/liboqs/lib -loqs \
  -o tfib_experiments/test_step2c_countermeasure_independence

echo "[*] Step 3: Executing Step 2C-A Validation Test Suite..."
./tfib_experiments/test_step2c_countermeasure_independence

echo "[*] Step 4: Compiling Integrated Experiment Runner..."
clang -O3 \
  -Ialgorithms/source_ref/mlkem/include \
  -Itfib_implementation \
  -Itfib_experiments \
  -Itfib_experiments/phase11_oracle \
  -I/opt/homebrew/opt/liboqs/include \
  tfib_experiments/tfib_experiment_runner.c \
  bin/obj/mlkem768_inst.o \
  tfib_implementation/libtfib.a \
  tfib_experiments/phase11_oracle/libindependent_oracle.a \
  -L/opt/homebrew/opt/liboqs/lib -loqs \
  -o tfib_experiments/tfib_experiment_runner

echo "[*] Step 5: Executing Dedicated Step 2C-A Campaign (900 Trials)..."
./tfib_experiments/tfib_experiment_runner tfib_experiments/phase2_step2c_trial_results.csv

# Also copy/link trial results to repo root for prompt requirement "Create: Machine-readable trial results"
cp tfib_experiments/phase2_step2c_trial_results.csv phase2_step2c_trial_results.csv

echo "[*] Step 6: Verifying Trial Results Integrity..."
TOTAL_TRIALS=$(wc -l < tfib_experiments/phase2_step2c_trial_results.csv | tr -d ' ')
# Header + 900 rows = 901 lines
if [ "${TOTAL_TRIALS}" -ne 901 ]; then
    echo "ERROR: Expected 901 lines in phase2_step2c_trial_results.csv, found ${TOTAL_TRIALS}" >&2
    exit 1
fi

SDC_COUNT=$(awk -F',' '$14 == "1" {count++} END {print count+0}' tfib_experiments/phase2_step2c_trial_results.csv)
if [ "${SDC_COUNT}" -ne 0 ]; then
    echo "CRITICAL SECURITY FAULT: SDC detected in trial results! Count: ${SDC_COUNT}" >&2
    exit 1
fi
echo "  ✓ Exactly 900 trials recorded with 0 SDC events across all configurations"

echo "================================================================================"
echo "PHASE 2 STEP 2C-A VALIDATION & CAMPAIGN COMPLETED SUCCESSFULLY (EXIT 0)"
echo "================================================================================"
