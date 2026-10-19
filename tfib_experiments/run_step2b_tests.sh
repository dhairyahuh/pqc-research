#!/usr/bin/env bash
# ==============================================================================
# Phase 2 — Step 2B: Independent Key Generation & Deterministic PRF Integration
# Build and Test Runner (Remediated)
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

echo "================================================================================"
echo "Running Phase 2 Step 2B Build & Test Verification (Remediated)"
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
  -Itfib_experiments \
  -Itfib_experiments/phase11_oracle \
  -I/opt/homebrew/opt/liboqs/include \
  tfib_experiments/tfib_experiment_runner.c \
  bin/obj/mlkem768_inst.o \
  tfib_implementation/libtfib.a \
  tfib_experiments/phase11_oracle/libindependent_oracle.a \
  -L/opt/homebrew/opt/liboqs/lib -loqs \
  -o tfib_experiments/tfib_experiment_runner

echo "[*] Step 3: Symbol Verification — No srand/rand calls..."
if nm tfib_experiments/tfib_experiment_runner 2>/dev/null | grep -q ' U _srand'; then
    echo "FAIL: srand still referenced!" >&2; exit 1
fi
if nm tfib_experiments/tfib_experiment_runner 2>/dev/null | grep -qE ' U _rand$'; then
    echo "FAIL: rand still referenced!" >&2; exit 1
fi
echo "  ✓ No srand/rand undefined symbols"

echo "[*] Step 4: Verify mlkem768_keypair is not called..."
KEYPAIR_CALLS=$(otool -tV tfib_experiments/tfib_experiment_runner 2>/dev/null | grep -c 'mlkem768_keypair$' || true)
if [ "${KEYPAIR_CALLS}" -gt 0 ]; then
    echo "FAIL: mlkem768_keypair is still called!" >&2; exit 1
fi
echo "  ✓ mlkem768_keypair has zero call-site references"

echo "[*] Step 5: Compiling Step 2B Validation Test Suite..."
clang -O3 \
  -Ialgorithms/source_ref/mlkem/include \
  -Itfib_implementation \
  -Itfib_experiments \
  -Itfib_experiments/phase11_oracle \
  -I/opt/homebrew/opt/liboqs/include \
  tfib_experiments/test_step2b_validation.c \
  bin/obj/mlkem768_inst.o \
  tfib_implementation/libtfib.a \
  tfib_experiments/phase11_oracle/libindependent_oracle.a \
  -L/opt/homebrew/opt/liboqs/lib -loqs \
  -o tfib_experiments/test_step2b_validation

echo "[*] Step 6: Executing Step 2B Validation Test Suite..."
./tfib_experiments/test_step2b_validation

echo "================================================================================"
echo "PHASE 2 STEP 2B TESTS COMPLETED SUCCESSFULLY (EXIT 0)"
echo "================================================================================"
