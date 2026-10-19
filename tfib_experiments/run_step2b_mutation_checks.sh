#!/usr/bin/env bash
# ==============================================================================
# Phase 2 — Step 2B Mutation Check Runner
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

echo "================================================================================"
echo "Phase 2 Step 2B Rigorous Mutation Verification"
echo "Working Directory: ${REPO_ROOT}"
echo "================================================================================"

TMP_DIR="$(mktemp -d /tmp/step2b_mutation_XXXXXX)"
trap 'rm -rf "${TMP_DIR}"' EXIT

COMPILE_CMD="clang -O3 \
  -Ialgorithms/source_ref/mlkem/include \
  -Itfib_implementation \
  -Itfib_experiments \
  -Itfib_experiments/phase11_oracle \
  -I/opt/homebrew/opt/liboqs/include \
  bin/obj/mlkem768_inst.o \
  tfib_implementation/libtfib.a \
  tfib_experiments/phase11_oracle/libindependent_oracle.a \
  -L/opt/homebrew/opt/liboqs/lib -loqs"

echo "[*] Baseline: Verifying unmutated test suite passes with exit code 0..."
${COMPILE_CMD} tfib_experiments/test_step2b_validation.c -o "${TMP_DIR}/test_baseline"
"${TMP_DIR}/test_baseline" > /dev/null
echo "  ✓ Baseline passed (Exit 0)"

# ------------------------------------------------------------------------------
# Mutation 1: Corrupt expected valid secret in clean-path test (DEF-01)
# ------------------------------------------------------------------------------
echo ""
echo "[*] Mutation 1: Deliberately corrupting expected valid secret in clean-path test..."
sed 's/int enc_rc = independent_oracle_encaps_derand(ct, ss_expected, pk, prf_out + 64);/int enc_rc = independent_oracle_encaps_derand(ct, ss_expected, pk, prf_out + 64); ss_expected[0] ^= 0xFF;/' \
    tfib_experiments/test_step2b_validation.c > "${TMP_DIR}/test_mutation1.c"

${COMPILE_CMD} "${TMP_DIR}/test_mutation1.c" -o "${TMP_DIR}/test_mutation1"

set +e
"${TMP_DIR}/test_mutation1" > "${TMP_DIR}/mut1.log" 2>&1
MUT1_EC=$?
set -e

if [ ${MUT1_EC} -eq 1 ] && grep -q "FAIL.*Test D" "${TMP_DIR}/mut1.log"; then
    echo "  ✓ Mutation 1 successfully caught: Test D failed as expected (Exit code 1)"
else
    echo "  ✗ ERROR: Mutation 1 was not caught! Exit code: ${MUT1_EC}"
    cat "${TMP_DIR}/mut1.log"
    exit 1
fi

# ------------------------------------------------------------------------------
# Mutation 2: Rejection-path test failure when output equals rejection key (DEF-01)
# ------------------------------------------------------------------------------
echo ""
echo "[*] Mutation 2: Simulating decapsulation returning rejection key on clean ciphertext..."
sed 's/mlkem768_dec_monitored(ss_out, ct, sk, &status);/mlkem768_dec_monitored(ss_out, ct, sk, \&status); memcpy(ss_out, ss_rej, SS_BYTES);/' \
    tfib_experiments/test_step2b_validation.c > "${TMP_DIR}/test_mutation2.c"

${COMPILE_CMD} "${TMP_DIR}/test_mutation2.c" -o "${TMP_DIR}/test_mutation2"

set +e
"${TMP_DIR}/test_mutation2" > "${TMP_DIR}/mut2.log" 2>&1
MUT2_EC=$?
set -e

if [ ${MUT2_EC} -eq 1 ] && grep -q "FAIL.*Test D" "${TMP_DIR}/mut2.log"; then
    echo "  ✓ Mutation 2 successfully caught: Test D failed when output matches rejection key (Exit code 1)"
else
    echo "  ✗ ERROR: Mutation 2 was not caught! Exit code: ${MUT2_EC}"
    cat "${TMP_DIR}/mut2.log"
    exit 1
fi

# ------------------------------------------------------------------------------
# Mutation 3: Remove locus differentiation from campaign PRF (DEF-03)
# ------------------------------------------------------------------------------
echo ""
echo "[*] Mutation 3: Removing locus input differentiation from campaign_prf context..."
# Create a mutated campaign_prf.h where locus word is forced to 0
sed 's/campaign_store32_le(seed_ctx + 8, (uint32_t)locus);/campaign_store32_le(seed_ctx + 8, 0u);/' \
    tfib_experiments/campaign_prf.h > "${TMP_DIR}/campaign_prf_mutated.h"

# Create a test copy that includes the mutated header
sed 's/"campaign_prf.h"/"campaign_prf_mutated.h"/' \
    tfib_experiments/test_step2b_validation.c > "${TMP_DIR}/test_mutation3.c"

${COMPILE_CMD} -I"${TMP_DIR}" "${TMP_DIR}/test_mutation3.c" -o "${TMP_DIR}/test_mutation3"

set +e
"${TMP_DIR}/test_mutation3" > "${TMP_DIR}/mut3.log" 2>&1
MUT3_EC=$?
set -e

if [ ${MUT3_EC} -eq 1 ] && grep -q "FAIL.*Test B" "${TMP_DIR}/mut3.log"; then
    echo "  ✓ Mutation 3 successfully caught: Test B failed when locus differentiation was removed (Exit code 1)"
else
    echo "  ✗ ERROR: Mutation 3 was not caught! Exit code: ${MUT3_EC}"
    cat "${TMP_DIR}/mut3.log"
    exit 1
fi

# ------------------------------------------------------------------------------
# Mutation 4: Alter explicit little-endian serialization byte order (DEF-05)
# ------------------------------------------------------------------------------
echo ""
echo "[*] Mutation 4: Altering byte serialization order to big-endian..."
sed 's/campaign_store32_le(seed_ctx + 0, trial_word);/seed_ctx[0] = (trial_word >> 24); seed_ctx[1] = (trial_word >> 16); seed_ctx[2] = (trial_word >> 8); seed_ctx[3] = trial_word;/' \
    tfib_experiments/campaign_prf.h > "${TMP_DIR}/campaign_prf_be.h"

sed 's/"campaign_prf.h"/"campaign_prf_be.h"/' \
    tfib_experiments/test_step2b_validation.c > "${TMP_DIR}/test_mutation4.c"

${COMPILE_CMD} -I"${TMP_DIR}" "${TMP_DIR}/test_mutation4.c" -o "${TMP_DIR}/test_mutation4"

set +e
"${TMP_DIR}/test_mutation4" > "${TMP_DIR}/mut4.log" 2>&1
MUT4_EC=$?
set -e

if [ ${MUT4_EC} -eq 1 ] && grep -q "FAIL.*Test G" "${TMP_DIR}/mut4.log"; then
    echo "  ✓ Mutation 4 successfully caught: Test G (KAT) failed when serialization was altered (Exit code 1)"
else
    echo "  ✗ ERROR: Mutation 4 was not caught! Exit code: ${MUT4_EC}"
    cat "${TMP_DIR}/mut4.log"
    exit 1
fi

echo ""
echo "================================================================================"
echo "ALL 4 RIGOROUS MUTATION CHECKS PASSED (All mutations caught with exit code 1)"
echo "================================================================================"
