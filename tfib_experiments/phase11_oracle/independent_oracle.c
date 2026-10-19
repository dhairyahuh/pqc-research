#include "independent_oracle.h"
#include "fips202_ref.h"
#include <oqs/oqs.h>
#include <string.h>
#include <stdio.h>

static bool g_oracle_initialized = false;

int independent_oracle_init(void) {
    if (!g_oracle_initialized) {
        OQS_init();
        g_oracle_initialized = true;
    }
    return 0;
}

const char *independent_oracle_get_version(void) {
    return "Independent Reference Oracle: Open Quantum Safe (liboqs) v" OQS_VERSION_TEXT
           " + FIPS 202 Specification Reference (TweetFIPS-202)";
}

int independent_oracle_keypair_derand(
    uint8_t *pk,
    uint8_t *sk,
    const uint8_t *seed64
) {
    if (!g_oracle_initialized) independent_oracle_init();
    if (!pk || !sk || !seed64) return -1;

    OQS_STATUS rc = OQS_KEM_ml_kem_768_keypair_derand(pk, sk, seed64);
    return (rc == OQS_SUCCESS) ? 0 : -1;
}

int independent_oracle_encaps_derand(
    uint8_t *ct,
    uint8_t *ss,
    const uint8_t *pk,
    const uint8_t *seed32
) {
    if (!g_oracle_initialized) independent_oracle_init();
    if (!ct || !ss || !pk || !seed32) return -1;

    OQS_STATUS rc = OQS_KEM_ml_kem_768_encaps_derand(ct, ss, pk, seed32);
    return (rc == OQS_SUCCESS) ? 0 : -1;
}

int independent_oracle_decaps(
    uint8_t *ss,
    const uint8_t *ct,
    const uint8_t *sk
) {
    if (!g_oracle_initialized) independent_oracle_init();
    if (!ss || !ct || !sk) return -1;

    OQS_STATUS rc = OQS_KEM_ml_kem_768_decaps(ss, ct, sk);
    return (rc == OQS_SUCCESS) ? 0 : -1;
}

int independent_oracle_compute_rejection(
    uint8_t *ss_rej,
    const uint8_t *sk,
    const uint8_t *ct
) {
    if (!ss_rej || !sk || !ct) return -1;

    /* Per FIPS 203 Section 3.3 and Algorithm 17:
     * sk is 2400 bytes, z is the last 32 bytes (sk[2368..2399]).
     * K_rej = J(z || c) = SHAKE-256(z || c, 32).
     */
    const uint8_t *z = sk + (ORACLE_MLKEM768_SK_BYTES - ORACLE_MLKEM768_SS_BYTES);

    uint8_t z_c[ORACLE_MLKEM768_SS_BYTES + ORACLE_MLKEM768_CT_BYTES];
    memcpy(z_c, z, ORACLE_MLKEM768_SS_BYTES);
    memcpy(z_c + ORACLE_MLKEM768_SS_BYTES, ct, ORACLE_MLKEM768_CT_BYTES);

    /* Use standalone specification-based reference SHAKE-256 */
    fips202_ref_shake256(ss_rej, ORACLE_MLKEM768_SS_BYTES, z_c, sizeof(z_c));
    return 0;
}
