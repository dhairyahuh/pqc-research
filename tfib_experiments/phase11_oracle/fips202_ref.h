#ifndef FIPS202_REF_H
#define FIPS202_REF_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Standalone, specification-based reference implementation of FIPS 202 SHAKE-256.
 * Derived from the public-domain TweetFIPS-202 implementation (Keccak team).
 *
 * Used exclusively for independent canonical implicit-rejection calculation:
 *   K_rej = J(z || c) = SHAKE-256(z || c, 32)
 *
 * @param[out] out     Output buffer
 * @param[in]  outlen  Requested output length in bytes (e.g. 32)
 * @param[in]  in      Input message buffer
 * @param[in]  inlen   Length of input message in bytes
 */
void fips202_ref_shake256(uint8_t *out, size_t outlen, const uint8_t *in, size_t inlen);

#ifdef __cplusplus
}
#endif

#endif /* FIPS202_REF_H */
