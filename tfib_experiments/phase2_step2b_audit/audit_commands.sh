#!/usr/bin/env bash
# ==============================================================================
# Phase 2 — Step 2B Independent Audit Reproduction Script
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${REPO_ROOT}"

echo "================================================================================"
echo "Phase 2 Step 2B Audit Script"
echo "Working Directory: ${REPO_ROOT}"
echo "================================================================================"

LIBOQS_PREFIX="${LIBOQS_PREFIX:-/opt/homebrew/opt/liboqs}"
if [ ! -d "${LIBOQS_PREFIX}" ]; then
    echo "ERROR: liboqs not found at ${LIBOQS_PREFIX}." >&2
    exit 1
fi

echo "[1] Clean Rebuild of Independent Oracle..."
make -C tfib_experiments/phase11_oracle clean
make -C tfib_experiments/phase11_oracle all

echo "[2] Running Oracle Unit & KAT Verification..."
./tfib_experiments/phase11_oracle/test_independent_oracle

echo "[3] Building tfib_experiment_runner..."
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

echo "[4] Inspecting Dynamic Imported Symbols (Undefined Symbols)..."
nm -u tfib_experiments/tfib_experiment_runner

echo "[5] Verifying absence of rand/srand symbols..."
if nm tfib_experiments/tfib_experiment_runner 2>/dev/null | grep -q ' U _srand'; then
    echo "ERROR: _srand found!" >&2; exit 1
fi
if nm tfib_experiments/tfib_experiment_runner 2>/dev/null | grep -qE ' U _rand$'; then
    echo "ERROR: _rand found!" >&2; exit 1
fi
echo "  ✓ No _rand or _srand undefined symbols"

echo "[6] Disassembly check for mlkem768_keypair call sites..."
KEYPAIR_CALLS=$(otool -tV tfib_experiments/tfib_experiment_runner 2>/dev/null | grep -c 'mlkem768_keypair$' || true)
echo "Call sites to mlkem768_keypair: ${KEYPAIR_CALLS}"
if [ "${KEYPAIR_CALLS}" -ne 0 ]; then
    echo "ERROR: mlkem768_keypair is still called!" >&2; exit 1
fi

echo "[7] Running randombytes call count verification..."
clang -O3 \
  -Ialgorithms/source_ref/mlkem/include \
  -Itfib_implementation \
  -Itfib_experiments/phase11_oracle \
  -I/opt/homebrew/opt/liboqs/include \
  tfib_experiments/phase2_step2b_audit/test_randombytes_call_count.c \
  bin/obj/mlkem768_inst.o \
  tfib_implementation/libtfib.a \
  tfib_experiments/phase11_oracle/libindependent_oracle.a \
  -L/opt/homebrew/opt/liboqs/lib -loqs \
  -o tfib_experiments/phase2_step2b_audit/test_randombytes_call_count
./tfib_experiments/phase2_step2b_audit/test_randombytes_call_count

echo "[8] Running Step 2B Validation Suite..."
clang -O3 \
  -Ialgorithms/source_ref/mlkem/include \
  -Itfib_implementation \
  -Itfib_experiments/phase11_oracle \
  -I/opt/homebrew/opt/liboqs/include \
  tfib_experiments/test_step2b_validation.c \
  bin/obj/mlkem768_inst.o \
  tfib_implementation/libtfib.a \
  tfib_experiments/phase11_oracle/libindependent_oracle.a \
  -L/opt/homebrew/opt/liboqs/lib -loqs \
  -o tfib_experiments/test_step2b_validation
./tfib_experiments/test_step2b_validation

echo "[9] Running Mutation Tests..."
clang -O3 \
  -Ialgorithms/source_ref/mlkem/include \
  -Itfib_implementation \
  -Itfib_experiments/phase11_oracle \
  -I/opt/homebrew/opt/liboqs/include \
  tfib_experiments/phase2_step2b_audit/test_mutation_audit.c \
  bin/obj/mlkem768_inst.o \
  tfib_implementation/libtfib.a \
  tfib_experiments/phase11_oracle/libindependent_oracle.a \
  -L/opt/homebrew/opt/liboqs/lib -loqs \
  -o tfib_experiments/phase2_step2b_audit/test_mutation_audit
./tfib_experiments/phase2_step2b_audit/test_mutation_audit 2 || echo "Mutation 2 caught (exit code $?)"
./tfib_experiments/phase2_step2b_audit/test_mutation_audit 3 || echo "Mutation 3 caught (exit code $?)"
./tfib_experiments/phase2_step2b_audit/test_mutation_audit 4 || echo "Mutation 4 caught (exit code $?)"

echo "[10] Running 900-Trial Campaign Twice for Determinism Verification..."
./tfib_experiments/tfib_experiment_runner tfib_experiments/phase2_step2b_audit/run1.csv > /dev/null
./tfib_experiments/tfib_experiment_runner tfib_experiments/phase2_step2b_audit/run2.csv > /dev/null
diff -u tfib_experiments/phase2_step2b_audit/run1.csv tfib_experiments/phase2_step2b_audit/run2.csv
diff -u tfib_experiments/phase2_step2b_runner_output.csv tfib_experiments/phase2_step2b_audit/run1.csv
echo "  ✓ Byte-for-byte campaign reproduction confirmed"

echo "================================================================================"
echo "AUDIT COMMANDS COMPLETED SUCCESSFULLY"
echo "================================================================================"
