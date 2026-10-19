#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "kat_runners.h"

#define MLD_CONFIG_PARAMETER_SET 87
#include "references/test_vectors/mldsa_expected_kat.h"

int mldsa87_signature_internal(uint8_t *sig, const uint8_t *m, size_t mlen,
                               const uint8_t *pre, size_t prelen,
                               const uint8_t *rnd, const uint8_t *sk, int extmu);

int mldsa87_verify_internal(const uint8_t *sig, const uint8_t *m, size_t mlen,
                            const uint8_t *pre, size_t prelen,
                            const uint8_t *pk, int extmu);

int run_mldsa87_kat(void) {
    uint8_t sig[4627];
    uint8_t pre[2 + TEST_VECTOR_CTX_LEN];
    pre[0] = 0x00; // pure ML-DSA domain separation
    pre[1] = (uint8_t)TEST_VECTOR_CTX_LEN;
    memcpy(pre + 2, TEST_VECTOR_CTX, TEST_VECTOR_CTX_LEN);

    int all_passed = 1;

    // 1. Deterministic Signature KAT
    int sig_rc = mldsa87_signature_internal(sig, (const uint8_t *)TEST_VECTOR_MSG, TEST_VECTOR_MSG_LEN,
                                            pre, sizeof(pre),
                                            test_vector_rnd, test_vector_sk, 0);
    int sig_match = (sig_rc == 0) && (memcmp(sig, test_vector_sig, sizeof(sig)) == 0);

    printf("Algorithm:       ML-DSA\n");
    printf("Parameter Set:   ML-DSA-87\n");
    printf("Vector ID:       NIST-FIPS204-KAT-87-SIGN\n");
    print_kat_hex_short("Expected Sig", test_vector_sig, sizeof(sig));
    print_kat_hex_short("Computed Sig", sig, sizeof(sig));
    printf("Result:          %s\n\n", sig_match ? "PASS" : "FAIL");
    if (!sig_match) all_passed = 0;

    // 2. Signature Verification KAT
    int ver_rc = mldsa87_verify_internal(test_vector_sig, (const uint8_t *)TEST_VECTOR_MSG, TEST_VECTOR_MSG_LEN,
                                         pre, sizeof(pre),
                                         test_vector_pk, 0);
    printf("Algorithm:       ML-DSA\n");
    printf("Parameter Set:   ML-DSA-87\n");
    printf("Vector ID:       NIST-FIPS204-KAT-87-VERIFY\n");
    printf("  Expected Verify RC: 0 (Success)\n");
    printf("  Computed Verify RC: %d\n", ver_rc);
    printf("Result:          %s\n\n", (ver_rc == 0) ? "PASS" : "FAIL");
    if (ver_rc != 0) all_passed = 0;

    // 3. Tamper Detection KAT (Bit-flip rejection)
    uint8_t tampered_sig[4627];
    memcpy(tampered_sig, test_vector_sig, sizeof(tampered_sig));
    tampered_sig[0] ^= 0x01; // flip 1 bit
    int tamper_rc = mldsa87_verify_internal(tampered_sig, (const uint8_t *)TEST_VECTOR_MSG, TEST_VECTOR_MSG_LEN,
                                           pre, sizeof(pre),
                                           test_vector_pk, 0);
    printf("Algorithm:       ML-DSA\n");
    printf("Parameter Set:   ML-DSA-87\n");
    printf("Vector ID:       NIST-FIPS204-KAT-87-TAMPER-REJECT\n");
    printf("  Expected Tamper Detection: REJECT (non-zero)\n");
    printf("  Computed Verify RC:        %d\n", tamper_rc);
    printf("Result:          %s\n\n", (tamper_rc != 0) ? "PASS" : "FAIL");
    if (tamper_rc == 0) all_passed = 0;

    return all_passed ? 0 : 1;
}
