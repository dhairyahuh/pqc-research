#!/usr/bin/env bash
# ==============================================================================
# Phase 11: Independent Oracle Validation Runner
# ==============================================================================
# Builds and executes the isolated reference oracle test suite using liboqs 0.16.0
# and the standalone FIPS 202 SHAKE-256 specification implementation.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

echo "================================================================================"
echo "Running Phase 11 Independent Oracle Build & Test Campaign"
echo "Working Directory: ${SCRIPT_DIR}"
echo "================================================================================"

# Verify liboqs dependency
LIBOQS_PREFIX="${LIBOQS_PREFIX:-/opt/homebrew/opt/liboqs}"
if [ ! -d "${LIBOQS_PREFIX}" ]; then
    echo "ERROR: liboqs not found at ${LIBOQS_PREFIX}." >&2
    echo "Please install liboqs (e.g., brew install liboqs) or set LIBOQS_PREFIX." >&2
    exit 1
fi

echo "[*] Cleaning previous build artifacts..."
make clean

echo "[*] Building independent oracle library and test runner..."
make all

echo "[*] Executing independent oracle test suite..."
./test_independent_oracle

# Validate that results JSON was produced and reports PASS
if [ ! -f "kat_validation_results.json" ]; then
    echo "ERROR: kat_validation_results.json was not generated!" >&2
    exit 1
fi

if grep -q '"overall_status": "PASS"' kat_validation_results.json; then
    echo "================================================================================"
    echo "PHASE 1 ORACLE VALIDATION: SUCCESS (All KATs & Rejection Invariants Verified)"
    echo "================================================================================"
    exit 0
else
    echo "ERROR: Oracle validation failed. Check kat_validation_results.json." >&2
    exit 1
fi
