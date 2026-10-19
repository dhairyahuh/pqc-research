#!/usr/bin/env bash
# ==============================================================================
# Phase 2 — Step 2A: Independent Ciphertext Generation Test Runner
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

echo "================================================================================"
echo "Running Phase 2 Step 2A Build & Test Verification"
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

echo "[*] Step 2: Compiling Integrated Experiment Runner..."
clang -O3 \
  -Ialgorithms/source_ref/mlkem/include \
  -Itfib_implementation \
  -Itfib_experiments/phase11_oracle \
  -I/opt/homebrew/opt/liboqs/include \
  tfib_experiments/tfib_experiment_runner.c \
  bin/obj/mlkem768_inst.o \
  tfib_implementation/libtfib.a \
  tfib_experiments/phase11_oracle/libindependent_oracle.a \
  -L/opt/homebrew/opt/liboqs/lib -loqs \
  -o tfib_experiments/tfib_experiment_runner

echo "[*] Step 3: Compiling Step 2A Validation Test Suite..."
clang -O3 \
  -Ialgorithms/source_ref/mlkem/include \
  -Itfib_implementation \
  -Itfib_experiments/phase11_oracle \
  -I/opt/homebrew/opt/liboqs/include \
  tfib_experiments/test_step2a_validation.c \
  bin/obj/mlkem768_inst.o \
  tfib_implementation/libtfib.a \
  tfib_experiments/phase11_oracle/libindependent_oracle.a \
  -L/opt/homebrew/opt/liboqs/lib -loqs \
  -o tfib_experiments/test_step2a_validation

echo "[*] Step 4: Executing Step 2A Validation Test Suite..."
./tfib_experiments/test_step2a_validation

echo "================================================================================"
echo "PHASE 2 STEP 2A TESTS COMPLETED SUCCESSFULLY (EXIT 0)"
echo "================================================================================"
