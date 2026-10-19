#ifndef CAMPAIGN_PRF_H
#define CAMPAIGN_PRF_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>
#include "tfib_common.h"
#include "tfib_core.h"
#include "fips202_ref.h"

#define CAMPAIGN_PRF_SEED_BYTES   16
#define CAMPAIGN_SEED_BASE_MAGIC  0x1337C0DEu

/**
 * Explicit Little-Endian 32-bit Serialization.
 *
 * Guarantees cross-platform deterministic serialization of 32-bit words
 * into little-endian byte streams, independent of host CPU endianness.
 */
static inline void campaign_store32_le(uint8_t out[4], uint32_t val) {
    out[0] = (uint8_t)(val & 0xFFu);
    out[1] = (uint8_t)((val >> 8) & 0xFFu);
    out[2] = (uint8_t)((val >> 16) & 0xFFu);
    out[3] = (uint8_t)((val >> 24) & 0xFFu);
}

/**
 * Explicit 16-byte seed context serialization.
 *
 * Layout of seed_ctx (16 bytes, strictly little-endian):
 *   [0..3]   0x1337C0DE + trial * 31  (uint32_le)
 *   [4..7]   mode enum                (uint32_le)
 *   [8..11]  locus enum               (uint32_le)
 *   [12..15] persistent flag (0 or 1) (uint32_le)
 */
static inline void campaign_prf_serialize_context(
    uint8_t seed_ctx[CAMPAIGN_PRF_SEED_BYTES],
    int trial, tfib_mode_t mode, tfib_fault_locus_t locus, bool persistent
) {
    uint32_t trial_word = (uint32_t)(CAMPAIGN_SEED_BASE_MAGIC + (uint32_t)trial * 31u);
    campaign_store32_le(seed_ctx + 0, trial_word);
    campaign_store32_le(seed_ctx + 4, (uint32_t)mode);
    campaign_store32_le(seed_ctx + 8, (uint32_t)locus);
    campaign_store32_le(seed_ctx + 12, persistent ? 1u : 0u);
}

/**
 * Deterministic campaign seed expansion function (PRF) using SHAKE-256.
 *
 * This function provides deterministic pseudorandom input generation for
 * reproducible experimental fault-injection campaigns. It is a deterministic
 * PRF / XOF expansion based on FIPS 202 SHAKE-256, NOT an interactive OS CSPRNG.
 *
 * @param[out] out         Output buffer for pseudorandom bytes
 * @param[in]  outlen      Number of pseudorandom bytes requested (e.g. 96)
 * @param[in]  trial       Trial index within the suite (e.g. 0..49)
 * @param[in]  mode        Target configuration (BASELINE, REF, META)
 * @param[in]  locus       Fault injection locus enum
 * @param[in]  persistent  Fault persistence flag
 */
static inline void campaign_prf(
    uint8_t *out, size_t outlen,
    int trial, tfib_mode_t mode, tfib_fault_locus_t locus, bool persistent
) {
    uint8_t seed_ctx[CAMPAIGN_PRF_SEED_BYTES];
    campaign_prf_serialize_context(seed_ctx, trial, mode, locus, persistent);
    fips202_ref_shake256(out, outlen, seed_ctx, sizeof(seed_ctx));
}

#endif /* CAMPAIGN_PRF_H */
