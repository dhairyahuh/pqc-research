#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "kat_runners.h"

#define MLK_CONFIG_PARAMETER_SET 1024
#include "references/test_vectors/mlkem_expected_kat.h"

int mlkem1024_keypair_derand(uint8_t *pk, uint8_t *sk, const uint8_t *coins);
int mlkem1024_enc_derand(uint8_t *ct, uint8_t *ss, const uint8_t *pk, const uint8_t *coins);
int mlkem1024_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);

int run_mlkem1024_kat(void) {
    uint8_t coins[64];
    memcpy(coins, test_vector_d, 32);
    memcpy(coins + 32, test_vector_z, 32);

    uint8_t pk[1568];
    uint8_t sk[3168];
    uint8_t ct[1568];
    uint8_t ss[32];
    uint8_t ss_dec[32];

    int all_passed = 1;

    // 1. KeyGen KAT
    if (mlkem1024_keypair_derand(pk, sk, coins) != 0) {
        printf("ML-KEM | ML-KEM-1024 | NIST-FIPS203-KAT-1024-KEYGEN | Internal Error | FAIL\n");
        return 1;
    }
    int pk_match = (memcmp(pk, test_vector_pk, sizeof(pk)) == 0);
    int sk_match = (memcmp(sk, test_vector_sk, sizeof(sk)) == 0);
    printf("Algorithm:       ML-KEM\n");
    printf("Parameter Set:   ML-KEM-1024\n");
    printf("Vector ID:       NIST-FIPS203-KAT-1024-KEYGEN\n");
    print_kat_hex_short("Expected PK", test_vector_pk, sizeof(pk));
    print_kat_hex_short("Computed PK", pk, sizeof(pk));
    printf("Result:          %s\n\n", (pk_match && sk_match) ? "PASS" : "FAIL");
    if (!pk_match || !sk_match) all_passed = 0;

    // 2. Encaps KAT
    if (mlkem1024_enc_derand(ct, ss, pk, test_vector_m) != 0) {
        printf("ML-KEM | ML-KEM-1024 | NIST-FIPS203-KAT-1024-ENCAPS | Internal Error | FAIL\n");
        return 1;
    }
    int ct_match = (memcmp(ct, test_vector_ct, sizeof(ct)) == 0);
    int ss_match = (memcmp(ss, test_vector_ss, sizeof(ss)) == 0);
    printf("Algorithm:       ML-KEM\n");
    printf("Parameter Set:   ML-KEM-1024\n");
    printf("Vector ID:       NIST-FIPS203-KAT-1024-ENCAPS\n");
    print_kat_hex_short("Expected CT", test_vector_ct, sizeof(ct));
    print_kat_hex_short("Computed CT", ct, sizeof(ct));
    print_kat_hex_short("Expected SS", test_vector_ss, sizeof(ss));
    print_kat_hex_short("Computed SS", ss, sizeof(ss));
    printf("Result:          %s\n\n", (ct_match && ss_match) ? "PASS" : "FAIL");
    if (!ct_match || !ss_match) all_passed = 0;

    // 3. Decaps KAT
    if (mlkem1024_dec(ss_dec, ct, sk) != 0) {
        printf("ML-KEM | ML-KEM-1024 | NIST-FIPS203-KAT-1024-DECAPS | Internal Error | FAIL\n");
        return 1;
    }
    int dec_match = (memcmp(ss_dec, test_vector_ss, sizeof(ss_dec)) == 0);
    printf("Algorithm:       ML-KEM\n");
    printf("Parameter Set:   ML-KEM-1024\n");
    printf("Vector ID:       NIST-FIPS203-KAT-1024-DECAPS\n");
    print_kat_hex_short("Expected SS", test_vector_ss, sizeof(ss));
    print_kat_hex_short("Decaps   SS", ss_dec, sizeof(ss_dec));
    printf("Result:          %s\n\n", dec_match ? "PASS" : "FAIL");
    if (!dec_match) all_passed = 0;

    return all_passed ? 0 : 1;
}
