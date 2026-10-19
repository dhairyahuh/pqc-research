#ifndef INDEPENDENT_ORACLE_H
#define INDEPENDENT_ORACLE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Standard ML-KEM-768 parameter lengths per FIPS 203 */
#define ORACLE_MLKEM768_PK_BYTES        1184
#define ORACLE_MLKEM768_SK_BYTES        2400
#define ORACLE_MLKEM768_CT_BYTES        1088
#define ORACLE_MLKEM768_SS_BYTES        32
#define ORACLE_MLKEM768_KEYPAIR_SEED    64
#define ORACLE_MLKEM768_ENCAPS_SEED     32

/**
 * Initialize the independent oracle backend (liboqs).
 * Returns 0 on success, non-zero on failure.
 */
int independent_oracle_init(void);

/**
 * Returns provenance description and library version of the independent oracle.
 */
const char *independent_oracle_get_version(void);

/**
 * Deterministic Keypair Generation (FIPS 203 Algorithm 15 / ML-KEM.KeyGen_internal)
 *
 * @param[out] pk      1184-byte public key buffer
 * @param[out] sk      2400-byte secret key buffer
 * @param[in]  seed64  64-byte random coins (d || z)
 * @return 0 on success, non-zero on error
 */
int independent_oracle_keypair_derand(
    uint8_t *pk,
    uint8_t *sk,
    const uint8_t *seed64
);

/**
 * Deterministic Encapsulation (FIPS 203 Algorithm 16 / ML-KEM.Encaps_internal)
 *
 * @param[out] ct      1088-byte ciphertext buffer
 * @param[out] ss      32-byte shared secret buffer
 * @param[in]  pk      1184-byte public key buffer
 * @param[in]  seed32  32-byte random message seed (m)
 * @return 0 on success, non-zero on error
 */
int independent_oracle_encaps_derand(
    uint8_t *ct,
    uint8_t *ss,
    const uint8_t *pk,
    const uint8_t *seed32
);

/**
 * Decapsulation (FIPS 203 Algorithm 17 / ML-KEM.Decaps_internal)
 *
 * @param[out] ss      32-byte shared secret buffer (valid key if ct authentic, canonical rejection key otherwise)
 * @param[in]  ct      1088-byte ciphertext buffer
 * @param[in]  sk      2400-byte secret key buffer
 * @return 0 on success, non-zero on error
 */
int independent_oracle_decaps(
    uint8_t *ss,
    const uint8_t *ct,
    const uint8_t *sk
);

/**
 * Compute the Canonical FIPS 203 Implicit Rejection Shared Secret:
 * K_rej = J(z || c) = SHAKE-256(z || c, 32)
 *
 * Where z is the 32-byte rejection seed from sk[2368..2399].
 *
 * @param[out] ss_rej  32-byte expected implicit rejection key
 * @param[in]  sk      2400-byte secret key buffer
 * @param[in]  ct      1088-byte ciphertext buffer
 * @return 0 on success, non-zero on error
 */
int independent_oracle_compute_rejection(
    uint8_t *ss_rej,
    const uint8_t *sk,
    const uint8_t *ct
);

#ifdef __cplusplus
}
#endif

#endif /* INDEPENDENT_ORACLE_H */
