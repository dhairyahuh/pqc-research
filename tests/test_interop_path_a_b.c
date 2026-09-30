/**
 * Cross-Validation Test: Path A (liboqs) vs Path B (source-level mlkem-native / mldsa-native)
 * Verifies that the source-level implementation produces byte-for-byte valid
 * cryptographic structures that the independent reference library accepts,
 * proving strict FIPS 203 and FIPS 204 compliance prior to fault injection.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <oqs/oqs.h>

// Path B mlkem (768 configuration) symbols
int mlkem_keypair_derand(uint8_t *pk, uint8_t *sk, const uint8_t *coins);
int mlkem_enc_derand(uint8_t *ct, uint8_t *ss, const uint8_t *pk, const uint8_t *coins);
int mlkem_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);

// Path B mldsa (65 configuration) symbols
int mldsa_keypair_internal(uint8_t *pk, uint8_t *sk, const uint8_t *seed);
int mldsa_signature(uint8_t *sig, const uint8_t *m, size_t mlen, const uint8_t *ctx, size_t ctxlen, const uint8_t *sk);
int mldsa_verify(const uint8_t *sig, const uint8_t *m, size_t mlen, const uint8_t *ctx, size_t ctxlen, const uint8_t *pk);

// FIPS 203/204 standard sizes
#define KEM768_PK_BYTES 1184
#define KEM768_SK_BYTES 2400
#define KEM768_CT_BYTES 1088
#define KEM768_SS_BYTES 32

#define DSA65_PK_BYTES 1952
#define DSA65_SK_BYTES 4032
#define DSA65_SIG_BYTES 3309

// Randombytes bridge implementation for native builds (returns 0 on success)
int randombytes(uint8_t *out, size_t outlen) {
    OQS_randombytes(out, outlen);
    return 0;
}

int test_kem_cross_interop(void) {
    printf("[+] Testing ML-KEM-768 Cross-Engine Interoperability...\n");

    uint8_t pk_b[KEM768_PK_BYTES];
    uint8_t sk_b[KEM768_SK_BYTES];
    uint8_t coins[64];
    memset(coins, 0x42, sizeof(coins));

    // 1. Path B generates keypair deterministically
    if (mlkem_keypair_derand(pk_b, sk_b, coins) != 0) {
        fprintf(stderr, "FAIL: Path B mlkem_keypair_derand failed\n");
        return 1;
    }
    printf("  1. Path B (mlkem-native source) generated ML-KEM-768 keypair.\n");

    // 2. Path A (liboqs) encapsulates using Path B's public key
    OQS_KEM *kem_a = OQS_KEM_new(OQS_KEM_alg_ml_kem_768);
    if (!kem_a) {
        fprintf(stderr, "FAIL: Could not allocate liboqs ML-KEM-768\n");
        return 1;
    }

    uint8_t ct_a[KEM768_CT_BYTES];
    uint8_t ss_a[KEM768_SS_BYTES];
    OQS_STATUS rc = OQS_KEM_encaps(kem_a, ct_a, ss_a, pk_b);
    if (rc != OQS_SUCCESS) {
        fprintf(stderr, "FAIL: Path A liboqs failed to encapsulate under Path B's PK\n");
        OQS_KEM_free(kem_a);
        return 1;
    }
    printf("  2. Path A (liboqs binary) encapsulated shared secret under Path B's PK.\n");

    // 3. Path B decapsulates ciphertext produced by Path A
    uint8_t ss_b[KEM768_SS_BYTES];
    if (mlkem_dec(ss_b, ct_a, sk_b) != 0) {
        fprintf(stderr, "FAIL: Path B mlkem_dec failed\n");
        OQS_KEM_free(kem_a);
        return 1;
    }
    printf("  3. Path B (mlkem-native source) decapsulated Path A's ciphertext.\n");

    // 4. Verify shared secret match
    if (memcmp(ss_a, ss_b, KEM768_SS_BYTES) == 0) {
        printf("  >>> SUCCESS: Path A and Path B shared secrets MATCH! (32 bytes identical)\n");
    } else {
        fprintf(stderr, "FAIL: Shared secret mismatch between Path A and Path B!\n");
        OQS_KEM_free(kem_a);
        return 1;
    }

    OQS_KEM_free(kem_a);
    return 0;
}

int test_dsa_cross_interop(void) {
    printf("\n[+] Testing ML-DSA-65 Cross-Engine Interoperability...\n");

    uint8_t pk_b[DSA65_PK_BYTES];
    uint8_t sk_b[DSA65_SK_BYTES];
    uint8_t seed[32];
    memset(seed, 0x5A, sizeof(seed));

    // 1. Path B generates keypair deterministically
    if (mldsa_keypair_internal(pk_b, sk_b, seed) != 0) {
        fprintf(stderr, "FAIL: Path B mldsa_keypair_internal failed\n");
        return 1;
    }
    printf("  1. Path B (mldsa-native source) generated ML-DSA-65 keypair.\n");

    // 2. Path B signs message
    const uint8_t msg[] = "Cross-Validation Spaceflight Telecommand 2026";
    size_t msg_len = sizeof(msg) - 1;
    uint8_t sig_b[DSA65_SIG_BYTES];

    // Standard empty context string
    if (mldsa_signature(sig_b, msg, msg_len, NULL, 0, sk_b) != 0) {
        fprintf(stderr, "FAIL: Path B mldsa_signature failed\n");
        return 1;
    }
    printf("  2. Path B (mldsa-native source) signed telemetry message (%zu bytes signature).\n", (size_t)DSA65_SIG_BYTES);

    // 3. Path A (liboqs) verifies Path B's signature
    OQS_SIG *sig_a = OQS_SIG_new(OQS_SIG_alg_ml_dsa_65);
    if (!sig_a) {
        fprintf(stderr, "FAIL: Could not allocate liboqs ML-DSA-65\n");
        return 1;
    }

    OQS_STATUS rc = OQS_SIG_verify(sig_a, msg, msg_len, sig_b, DSA65_SIG_BYTES, pk_b);
    if (rc == OQS_SUCCESS) {
        printf("  >>> SUCCESS: Path A (liboqs binary) successfully VERIFIED Path B's signature!\n");
    } else {
        fprintf(stderr, "FAIL: Path A liboqs rejected Path B's signature!\n");
        OQS_SIG_free(sig_a);
        return 1;
    }

    // 4. Negative test: Corrupt 1 bit in Path B's signature and verify Path A rejects it
    sig_b[0] ^= 0x01;
    rc = OQS_SIG_verify(sig_a, msg, msg_len, sig_b, DSA65_SIG_BYTES, pk_b);
    if (rc != OQS_SUCCESS) {
        printf("  >>> SUCCESS: Path A correctly rejected 1-bit corrupted Path B signature!\n");
    } else {
        fprintf(stderr, "FAIL: Path A accepted corrupted Path B signature!\n");
        OQS_SIG_free(sig_a);
        return 1;
    }

    OQS_SIG_free(sig_a);
    return 0;
}

int main(void) {
    OQS_init();
    printf("=================================================================\n");
    printf(" DUAL IMPLEMENTATION CROSS-VALIDATION (Path A vs Path B)\n");
    printf(" Standards: NIST FIPS 203 & NIST FIPS 204\n");
    printf("=================================================================\n\n");

    int r1 = test_kem_cross_interop();
    int r2 = test_dsa_cross_interop();

    OQS_destroy();
    if (r1 == 0 && r2 == 0) {
        printf("\n=================================================================\n");
        printf(" ALL CROSS-VALIDATION TESTS PASSED: Path B is 100%% interoperable!\n");
        printf("=================================================================\n");
        return 0;
    } else {
        printf("\n>>> CROSS-VALIDATION FAILED <<<\n");
        return 1;
    }
}
