/**
 * ML-DSA (FIPS 204) Baseline C Harness
 * Supports ML-DSA-44, ML-DSA-65, ML-DSA-87
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <oqs/oqs.h>

int run_dsa_workflow(const char *alg_name, int verbose) {
    if (!OQS_SIG_alg_is_enabled(alg_name)) {
        fprintf(stderr, "Algorithm %s is not enabled in liboqs.\n", alg_name);
        return 1;
    }

    OQS_SIG *sig = OQS_SIG_new(alg_name);
    if (!sig) {
        fprintf(stderr, "Failed to instantiate SIG %s.\n", alg_name);
        return 1;
    }

    if (verbose) {
        printf("--- Testing %s ---\n", sig->method_name);
        printf("  Public Key:   %zu bytes\n", sig->length_public_key);
        printf("  Secret Key:   %zu bytes\n", sig->length_secret_key);
        printf("  Max Signature:%zu bytes\n", sig->length_signature);
    }

    uint8_t *public_key = malloc(sig->length_public_key);
    uint8_t *secret_key = malloc(sig->length_secret_key);
    uint8_t *signature = malloc(sig->length_signature);
    size_t signature_len = 0;

    const uint8_t test_msg[] = "Flight-Critical Telecommand: Activate Deep Space Transponder Mode B.";
    size_t test_msg_len = sizeof(test_msg) - 1;

    // 1. KeyGen
    OQS_STATUS rc = OQS_SIG_keypair(sig, public_key, secret_key);
    if (rc != OQS_SUCCESS) {
        fprintf(stderr, "KeyGen failed for %s\n", alg_name);
        goto cleanup_fail;
    }

    // 2. Sign
    rc = OQS_SIG_sign(sig, signature, &signature_len, test_msg, test_msg_len, secret_key);
    if (rc != OQS_SUCCESS) {
        fprintf(stderr, "Sign failed for %s\n", alg_name);
        goto cleanup_fail;
    }

    if (verbose) {
        printf("  Signature Size:%zu bytes\n", signature_len);
    }

    // 3. Verify Genuine Signature
    rc = OQS_SIG_verify(sig, test_msg, test_msg_len, signature, signature_len, public_key);
    if (rc != OQS_SUCCESS) {
        fprintf(stderr, "Valid signature verification failed for %s\n", alg_name);
        goto cleanup_fail;
    }

    if (verbose) {
        printf("  Verification Genuine: SUCCESS\n");
    }

    // 4. Verify Corrupted Signature (Single-bit flip in signature)
    signature[signature_len / 2] ^= 0x01; // flip 1 bit in middle of signature
    rc = OQS_SIG_verify(sig, test_msg, test_msg_len, signature, signature_len, public_key);
    if (rc == OQS_SUCCESS) {
        fprintf(stderr, "CRITICAL ERROR: Corrupted signature was accepted by %s!\n", alg_name);
        goto cleanup_fail;
    }

    if (verbose) {
        printf("  Tamper Detection:     SUCCESS (Bit-flip was rejected)\n");
    }

    OQS_SIG_free(sig);
    free(public_key);
    free(secret_key);
    free(signature);
    return 0;

cleanup_fail:
    OQS_SIG_free(sig);
    free(public_key);
    free(secret_key);
    free(signature);
    return 1;
}

int main(void) {
    OQS_init();
    printf("========================================\n");
    printf(" ML-DSA (FIPS 204) Baseline Verification\n");
    printf(" liboqs version: %s\n", OQS_version());
    printf("========================================\n");

    const char *algs[] = {
        OQS_SIG_alg_ml_dsa_44,
        OQS_SIG_alg_ml_dsa_65,
        OQS_SIG_alg_ml_dsa_87
    };

    int all_passed = 1;
    for (int i = 0; i < 3; i++) {
        if (run_dsa_workflow(algs[i], 1) != 0) {
            all_passed = 0;
        }
    }

    OQS_destroy();
    if (all_passed) {
        printf("\n>>> All ML-DSA baseline tests PASSED successfully. <<<\n");
        return 0;
    } else {
        printf("\n>>> Some ML-DSA tests FAILED! <<<\n");
        return 1;
    }
}
