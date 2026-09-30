/**
 * ML-KEM (FIPS 203) Baseline C Harness
 * Supports ML-KEM-512, ML-KEM-768, ML-KEM-1024
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <oqs/oqs.h>

typedef struct {
    const char *alg_name;
    size_t length_public_key;
    size_t length_secret_key;
    size_t length_ciphertext;
    size_t length_shared_secret;
} ml_kem_metadata_t;

int run_kem_workflow(const char *alg_name, int verbose) {
    if (!OQS_KEM_alg_is_enabled(alg_name)) {
        fprintf(stderr, "Algorithm %s is not enabled in liboqs.\n", alg_name);
        return 1;
    }

    OQS_KEM *kem = OQS_KEM_new(alg_name);
    if (!kem) {
        fprintf(stderr, "Failed to instantiate KEM %s.\n", alg_name);
        return 1;
    }

    if (verbose) {
        printf("--- Testing %s ---\n", kem->method_name);
        printf("  Public Key:   %zu bytes\n", kem->length_public_key);
        printf("  Secret Key:   %zu bytes\n", kem->length_secret_key);
        printf("  Ciphertext:   %zu bytes\n", kem->length_ciphertext);
        printf("  Shared Secret:%zu bytes\n", kem->length_shared_secret);
    }

    uint8_t *public_key = malloc(kem->length_public_key);
    uint8_t *secret_key = malloc(kem->length_secret_key);
    uint8_t *ciphertext = malloc(kem->length_ciphertext);
    uint8_t *shared_secret_e = malloc(kem->length_shared_secret);
    uint8_t *shared_secret_d = malloc(kem->length_shared_secret);

    // 1. KeyGen
    OQS_STATUS rc = OQS_KEM_keypair(kem, public_key, secret_key);
    if (rc != OQS_SUCCESS) {
        fprintf(stderr, "KeyGen failed for %s\n", alg_name);
        goto cleanup_fail;
    }

    // 2. Encaps
    rc = OQS_KEM_encaps(kem, ciphertext, shared_secret_e, public_key);
    if (rc != OQS_SUCCESS) {
        fprintf(stderr, "Encaps failed for %s\n", alg_name);
        goto cleanup_fail;
    }

    // 3. Decaps
    rc = OQS_KEM_decaps(kem, shared_secret_d, ciphertext, secret_key);
    if (rc != OQS_SUCCESS) {
        fprintf(stderr, "Decaps failed for %s\n", alg_name);
        goto cleanup_fail;
    }

    // 4. Verification
    if (memcmp(shared_secret_e, shared_secret_d, kem->length_shared_secret) != 0) {
        fprintf(stderr, "Shared secret mismatch for %s\n", alg_name);
        goto cleanup_fail;
    }

    if (verbose) {
        printf("  Result: SUCCESS (Shared secrets match perfectly)\n");
    }

    OQS_KEM_free(kem);
    free(public_key);
    free(secret_key);
    free(ciphertext);
    free(shared_secret_e);
    free(shared_secret_d);
    return 0;

cleanup_fail:
    OQS_KEM_free(kem);
    free(public_key);
    free(secret_key);
    free(ciphertext);
    free(shared_secret_e);
    free(shared_secret_d);
    return 1;
}

int main(void) {
    OQS_init();
    printf("========================================\n");
    printf(" ML-KEM (FIPS 203) Baseline Verification\n");
    printf(" liboqs version: %s\n", OQS_version());
    printf("========================================\n");

    const char *algs[] = {
        OQS_KEM_alg_ml_kem_512,
        OQS_KEM_alg_ml_kem_768,
        OQS_KEM_alg_ml_kem_1024
    };

    int all_passed = 1;
    for (int i = 0; i < 3; i++) {
        if (run_kem_workflow(algs[i], 1) != 0) {
            all_passed = 0;
        }
    }

    OQS_destroy();
    if (all_passed) {
        printf("\n>>> All ML-KEM baseline tests PASSED successfully. <<<\n");
        return 0;
    } else {
        printf("\n>>> Some ML-KEM tests FAILED! <<<\n");
        return 1;
    }
}
