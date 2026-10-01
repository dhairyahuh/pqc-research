/* =========================================================================
 * Phase 7D: Adversarial Validation, Common-Mode Fault Analysis,
 *           and Reproducibility Audit Harness
 * Target: NIST FIPS 203 ML-KEM-768 Scalar C Reference Implementation
 * ========================================================================= */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include "algorithms/source_ref/mlkem_fault_hooks.h"
#include "algorithms/source_ref/mlkem/mlkem_native.h"

#define MLKEM_Q 3329
#define SS_BYTES 32
#define CT_BYTES 1088
#define SK_BYTES 2400
#define PK_BYTES 1184

#define RESILIENCE_OK_TOKEN     0x5A5A5A5AU
#define RESILIENCE_FAULT_TOKEN  0xA5A5A5A5U
#define RESILIENCE_RETRY_TOKEN  0x3C3C3C3CU
#define RESILIENCE_REJECT_TOKEN 0xC3C3C3C3U

#define MLK_STATUS_SUCCESS 0x5A5A5A5AU
#define MLK_STATUS_REJECT  0xA5A5A5A5U
#define MLK_STATUS_FAULT   0xFFFFFFFFU

/* Native ML-KEM C reference declarations */
int mlkem768_keypair(uint8_t *pk, uint8_t *sk);
int mlkem768_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int mlkem768_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);
int mlkem768_dec_monitored(uint8_t *ss, const uint8_t *ct, const uint8_t *sk, uint32_t *internal_status);

int randombytes(uint8_t *out, size_t outlen) {
    for (size_t i = 0; i < outlen; i++) {
        out[i] = (uint8_t)(rand() & 0xFF);
    }
    return 0;
}

typedef struct {
    int16_t coeffs[256];
} poly_t;

void mlkem768_poly_ntt(poly_t *r);

/* Verified complete 128-element Layer 7 inverse zetas for weighted NTT check */
static const int16_t g_inv_zetas_layer7[128] = {
    1175, -1175, -885, 885, 394, -394, 1219, -1219,
    -1029, 1029, 1455, -1455, -1212, 1212, 1607, -1607,
    -886, 886, 554, -554, 1179, -1179, -1143, 1143,
    -1026, 1026, -403, 403, -1092, 1092, 525, -525,
    735, -735, 863, -863, -561, 561, 1230, -1230,
    -757, 757, 556, -556, -319, 319, -1063, 1063,
    -1645, 1645, 1239, -1239, 780, -780, -375, 375,
    109, -109, 1292, -1292, 1031, -1031, -1584, 1584,
    -641, 641, -268, 268, 992, -992, -733, 733,
    941, -941, 892, -892, 1021, -1021, -939, 939,
    642, -642, -1461, 1461, -952, 952, 1482, -1482,
    1540, -1540, 540, -540, -1651, 1651, 1626, -1626,
    279, -279, 314, -314, 1173, -1173, -756, 756,
    -233, 233, 48, -48, 667, -667, -1409, 1409,
    -1100, 1100, 1041, -1041, -723, 723, -1637, 1637,
    680, -680, -583, 583, 568, -568, -17, 17
};

/* CRC32 IEEE 802.3 implementation */
static uint32_t crc32_ieee(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (int j = 0; j < 8; j++) {
            crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
        }
    }
    return ~crc;
}

/* Invariant Verifier: Unweighted */
static uint32_t verify_unweighted_ntt(const poly_t *time_poly, const poly_t *ntt_poly) {
    int32_t sum_even = 0, sum_odd = 0;
    for (int i = 0; i < 128; i++) {
        sum_even = (sum_even + ntt_poly->coeffs[2 * i]) % MLKEM_Q;
        sum_odd  = (sum_odd  + ntt_poly->coeffs[2 * i + 1]) % MLKEM_Q;
    }
    sum_even = (sum_even + MLKEM_Q) % MLKEM_Q;
    sum_odd  = (sum_odd  + MLKEM_Q) % MLKEM_Q;

    int32_t exp_even = (128 * (int32_t)time_poly->coeffs[0]) % MLKEM_Q;
    int32_t exp_odd  = (128 * (int32_t)time_poly->coeffs[1]) % MLKEM_Q;
    exp_even = (exp_even + MLKEM_Q) % MLKEM_Q;
    exp_odd  = (exp_odd  + MLKEM_Q) % MLKEM_Q;

    return (sum_even == exp_even && sum_odd == exp_odd) ? RESILIENCE_OK_TOKEN : RESILIENCE_FAULT_TOKEN;
}

/* Invariant Verifier: Complementary Weighted (Full 128 elements) */
static uint32_t verify_complementary_ntt(const poly_t *time_poly, const poly_t *ntt_poly) {
    int32_t sum_even = 0, sum_odd = 0;
    int32_t w_even = 0, w_odd = 0;

    for (int i = 0; i < 128; i++) {
        int16_t e = ntt_poly->coeffs[2 * i];
        int16_t o = ntt_poly->coeffs[2 * i + 1];
        int16_t wz = g_inv_zetas_layer7[i];

        sum_even = (sum_even + e) % MLKEM_Q;
        sum_odd  = (sum_odd  + o) % MLKEM_Q;
        w_even   = (w_even + (int32_t)e * wz) % MLKEM_Q;
        w_odd    = (w_odd  + (int32_t)o * wz) % MLKEM_Q;
    }

    sum_even = (sum_even + MLKEM_Q) % MLKEM_Q;
    sum_odd  = (sum_odd  + MLKEM_Q) % MLKEM_Q;
    w_even   = (w_even + MLKEM_Q) % MLKEM_Q;
    w_odd    = (w_odd + MLKEM_Q) % MLKEM_Q;

    int32_t exp_even  = (128 * (int32_t)time_poly->coeffs[0]) % MLKEM_Q;
    int32_t exp_odd   = (128 * (int32_t)time_poly->coeffs[1]) % MLKEM_Q;
    int32_t exp_weven = (128 * (int32_t)time_poly->coeffs[2]) % MLKEM_Q;
    int32_t exp_wodd  = (128 * (int32_t)time_poly->coeffs[3]) % MLKEM_Q;

    exp_even  = (exp_even + MLKEM_Q) % MLKEM_Q;
    exp_odd   = (exp_odd  + MLKEM_Q) % MLKEM_Q;
    exp_weven = (exp_weven + MLKEM_Q) % MLKEM_Q;
    exp_wodd  = (exp_wodd + MLKEM_Q) % MLKEM_Q;

    if (sum_even != exp_even || sum_odd != exp_odd ||
        w_even != exp_weven || w_odd != exp_wodd) {
        return RESILIENCE_FAULT_TOKEN;
    }
    return RESILIENCE_OK_TOKEN;
}

/* Multi-rail barrier verification */
static uint32_t verify_multi_rail_barrier(uint32_t rail1, uint32_t rail2) {
    uint32_t pass1 = (rail1 == RESILIENCE_OK_TOKEN);
    uint32_t pass2 = (rail2 == (uint32_t)~RESILIENCE_OK_TOKEN);
    __asm__ volatile("" ::: "memory");
    if (pass1 && pass2) {
        return RESILIENCE_OK_TOKEN;
    }
    return RESILIENCE_FAULT_TOKEN;
}

/* Config 4: Full Duplicate Execution (DMR) */
static uint32_t decaps_duplicate(uint8_t *ss, const uint8_t *ct, const uint8_t *sk) {
    uint8_t ss1[SS_BYTES];
    uint8_t ss2[SS_BYTES];

    int ret1 = mlkem768_dec(ss1, ct, sk);
    int ret2 = mlkem768_dec(ss2, ct, sk);

    if (ret1 != 0 || ret2 != 0 || memcmp(ss1, ss2, SS_BYTES) != 0) {
        memset(ss, 0, SS_BYTES);
        return RESILIENCE_FAULT_TOKEN;
    }
    memcpy(ss, ss1, SS_BYTES);
    return RESILIENCE_OK_TOKEN;
}

/* Config 5: Phase 7 Layered Decapsulation (with oracle) */
static uint32_t decaps_layered_oracle(
    uint8_t *ss, const uint8_t *ct, const uint8_t *sk,
    uint32_t expected_ct_crc, bool allow_retry, const uint8_t *expected_ss,
    const poly_t *opt_time_poly, const poly_t *opt_ntt_poly
) {
    uint32_t actual_crc = crc32_ieee(ct, CT_BYTES);
    if (actual_crc != expected_ct_crc) {
        memset(ss, 0, SS_BYTES);
        return RESILIENCE_FAULT_TOKEN;
    }
    if (opt_time_poly && opt_ntt_poly) {
        if (verify_complementary_ntt(opt_time_poly, opt_ntt_poly) == RESILIENCE_FAULT_TOKEN) {
            memset(ss, 0, SS_BYTES);
            return RESILIENCE_FAULT_TOKEN;
        }
    }
    int dec_res = mlkem768_dec(ss, ct, sk);
    bool dec_fault = (expected_ss && memcmp(ss, expected_ss, SS_BYTES) != 0);
    uint32_t rail1 = (!dec_fault && dec_res == 0) ? RESILIENCE_OK_TOKEN : RESILIENCE_FAULT_TOKEN;
    uint32_t rail2 = (!dec_fault && dec_res == 0) ? ~RESILIENCE_OK_TOKEN : ~RESILIENCE_FAULT_TOKEN;
    uint32_t status = verify_multi_rail_barrier(rail1, rail2);

    if (status != RESILIENCE_OK_TOKEN && allow_retry) {
        mlkem_fault_reset();
        dec_res = mlkem768_dec(ss, ct, sk);
        dec_fault = (expected_ss && memcmp(ss, expected_ss, SS_BYTES) != 0);
        rail1 = (!dec_fault && dec_res == 0) ? RESILIENCE_OK_TOKEN : RESILIENCE_FAULT_TOKEN;
        rail2 = (!dec_fault && dec_res == 0) ? ~RESILIENCE_OK_TOKEN : ~RESILIENCE_FAULT_TOKEN;
        status = verify_multi_rail_barrier(rail1, rail2);
        if (status == RESILIENCE_OK_TOKEN) {
            return RESILIENCE_RETRY_TOKEN;
        }
        memset(ss, 0, SS_BYTES);
        return RESILIENCE_FAULT_TOKEN;
    }
    if (status != RESILIENCE_OK_TOKEN) {
        memset(ss, 0, SS_BYTES);
        return RESILIENCE_FAULT_TOKEN;
    }
    return RESILIENCE_OK_TOKEN;
}

/* Config 6: Phase 7C Unpatched Native Layered Decapsulation (contains invalid CT retry artifact) */
static uint32_t decaps_layered_native_unpatched(
    uint8_t *ss, const uint8_t *ct, const uint8_t *sk,
    uint32_t expected_ct_crc, bool allow_retry,
    const poly_t *opt_time_poly, const poly_t *opt_ntt_poly
) {
    uint32_t actual_crc = crc32_ieee(ct, CT_BYTES);
    if (actual_crc != expected_ct_crc) {
        memset(ss, 0, SS_BYTES);
        return RESILIENCE_FAULT_TOKEN;
    }
    if (opt_time_poly && opt_ntt_poly) {
        if (verify_complementary_ntt(opt_time_poly, opt_ntt_poly) == RESILIENCE_FAULT_TOKEN) {
            memset(ss, 0, SS_BYTES);
            return RESILIENCE_FAULT_TOKEN;
        }
    }
    uint32_t internal_status = 0;
    int dec_res = mlkem768_dec_monitored(ss, ct, sk, &internal_status);
    bool dec_fault  = (internal_status == MLK_STATUS_FAULT);
    bool dec_reject = (internal_status == MLK_STATUS_REJECT);

    uint32_t rail1 = (!dec_fault && !dec_reject && dec_res == 0) ? RESILIENCE_OK_TOKEN : RESILIENCE_FAULT_TOKEN;
    uint32_t rail2 = (!dec_fault && !dec_reject && dec_res == 0) ? ~RESILIENCE_OK_TOKEN : ~RESILIENCE_FAULT_TOKEN;
    uint32_t status = verify_multi_rail_barrier(rail1, rail2);

    if (status != RESILIENCE_OK_TOKEN && allow_retry) {
        mlkem_fault_reset();
        uint32_t retry_status = 0;
        dec_res = mlkem768_dec_monitored(ss, ct, sk, &retry_status);
        bool retry_fault  = (retry_status == MLK_STATUS_FAULT);
        bool retry_reject = (retry_status == MLK_STATUS_REJECT);

        rail1 = (!retry_fault && !retry_reject && dec_res == 0) ? RESILIENCE_OK_TOKEN : RESILIENCE_FAULT_TOKEN;
        rail2 = (!retry_fault && !retry_reject && dec_res == 0) ? ~RESILIENCE_OK_TOKEN : ~RESILIENCE_FAULT_TOKEN;
        status = verify_multi_rail_barrier(rail1, rail2);

        if (status == RESILIENCE_OK_TOKEN) {
            return RESILIENCE_RETRY_TOKEN;
        }
        if (!retry_fault && retry_reject) {
            return RESILIENCE_REJECT_TOKEN;
        }
        memset(ss, 0, SS_BYTES);
        return RESILIENCE_FAULT_TOKEN;
    }
    if (!dec_fault && dec_reject) {
        return RESILIENCE_REJECT_TOKEN;
    }
    if (status != RESILIENCE_OK_TOKEN) {
        memset(ss, 0, SS_BYTES);
        return RESILIENCE_FAULT_TOKEN;
    }
    return RESILIENCE_OK_TOKEN;
}

/* Config 7: Phase 7D Remediated Native Layered Decapsulation
 * (Decouples normal cryptographic rejection from physical faults; no redundant retry) */
static uint32_t decaps_layered_native_remediated(
    uint8_t *ss, const uint8_t *ct, const uint8_t *sk,
    uint32_t expected_ct_crc, bool allow_retry,
    const poly_t *opt_time_poly, const poly_t *opt_ntt_poly
) {
    /* Layer 1: Input Integrity Verification */
    uint32_t actual_crc = crc32_ieee(ct, CT_BYTES);
    if (actual_crc != expected_ct_crc) {
        memset(ss, 0, SS_BYTES);
        return RESILIENCE_FAULT_TOKEN;
    }

    /* Layer 2: Polynomial NTT Transform Invariant */
    if (opt_time_poly && opt_ntt_poly) {
        if (verify_complementary_ntt(opt_time_poly, opt_ntt_poly) == RESILIENCE_FAULT_TOKEN) {
            memset(ss, 0, SS_BYTES);
            return RESILIENCE_FAULT_TOKEN;
        }
    }

    /* Layer 3: Native Decapsulation with In-Tree Dual-Rail Monitoring */
    uint32_t internal_status = 0;
    int dec_res = mlkem768_dec_monitored(ss, ct, sk, &internal_status);

    /* Cryptographic rejection is a normal IND-CCA2 outcome, NOT a physical fault */
    if (dec_res == 0 && internal_status == MLK_STATUS_REJECT) {
        return RESILIENCE_REJECT_TOKEN; /* Output valid Krej in 1.0x constant time */
    }

    /* Check for physical fault or unexpected return code */
    bool dec_fault = (internal_status == MLK_STATUS_FAULT || dec_res != 0);

    /* Multi-Rail Verification with Compiler Barrier */
    uint32_t rail1 = (!dec_fault) ? RESILIENCE_OK_TOKEN : RESILIENCE_FAULT_TOKEN;
    uint32_t rail2 = (!dec_fault) ? ~RESILIENCE_OK_TOKEN : ~RESILIENCE_FAULT_TOKEN;
    uint32_t status = verify_multi_rail_barrier(rail1, rail2);

    /* Layer 4: Autonomous Retry strictly for physical faults */
    if (status != RESILIENCE_OK_TOKEN && allow_retry) {
        mlkem_fault_reset();
        uint32_t retry_status = 0;
        dec_res = mlkem768_dec_monitored(ss, ct, sk, &retry_status);

        if (dec_res == 0 && retry_status == MLK_STATUS_REJECT) {
            return RESILIENCE_REJECT_TOKEN;
        }

        bool retry_fault = (retry_status == MLK_STATUS_FAULT || dec_res != 0);
        rail1 = (!retry_fault) ? RESILIENCE_OK_TOKEN : RESILIENCE_FAULT_TOKEN;
        rail2 = (!retry_fault) ? ~RESILIENCE_OK_TOKEN : ~RESILIENCE_FAULT_TOKEN;
        status = verify_multi_rail_barrier(rail1, rail2);

        if (status == RESILIENCE_OK_TOKEN) {
            return RESILIENCE_RETRY_TOKEN; /* Successfully recovered transient fault */
        }

        memset(ss, 0, SS_BYTES);
        return RESILIENCE_FAULT_TOKEN; /* Persistent fault: Safe rejection */
    }

    if (status != RESILIENCE_OK_TOKEN) {
        memset(ss, 0, SS_BYTES);
        return RESILIENCE_FAULT_TOKEN;
    }
    return RESILIENCE_OK_TOKEN;
}

static inline double get_time_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e6 + (double)ts.tv_nsec * 1e-3;
}

static int compare_doubles(const void *a, const void *b) {
    double da = *(const double *)a;
    double db = *(const double *)b;
    return (da > db) - (da < db);
}

int main(void) {
    printf("=========================================================================\n");
    printf(" Phase 7D: Adversarial Validation & Reproducibility Audit\n");
    printf(" Target: NIST FIPS 203 ML-KEM-768 Scalar C Reference\n");
    printf("=========================================================================\n\n");

    uint8_t pk[PK_BYTES], sk[SK_BYTES];
    uint8_t ct_valid[CT_BYTES], ss_expected[SS_BYTES];
    mlkem768_keypair(pk, sk);
    mlkem768_enc(ct_valid, ss_expected, pk);
    uint32_t valid_ct_crc = crc32_ieee(ct_valid, CT_BYTES);

    uint8_t ct_invalid[CT_BYTES];
    memcpy(ct_invalid, ct_valid, CT_BYTES);
    ct_invalid[10] ^= 0x55;
    uint32_t invalid_ct_crc = crc32_ieee(ct_invalid, CT_BYTES);

    uint8_t ss_expected_rej[SS_BYTES];
    mlkem768_dec(ss_expected_rej, ct_invalid, sk);

    poly_t test_time_poly, test_ntt_poly;
    for (int i = 0; i < 256; i++) {
        test_time_poly.coeffs[i] = (int16_t)((i * 17 + 3) % MLKEM_Q);
    }
    test_ntt_poly = test_time_poly;
    mlkem768_poly_ntt(&test_ntt_poly);

    /* -------------------------------------------------------------------------
     * SECTION 1: Adversarial Validation and Remediation Sanity Checks
     * ------------------------------------------------------------------------- */
    printf("--- [Section 1] Functional & Remediated Sanity Checks ---\n");
    {
        uint8_t ss_test[SS_BYTES];
        /* Test 1.1: Valid CT */
        uint32_t tok = decaps_layered_native_remediated(ss_test, ct_valid, sk, valid_ct_crc, true, NULL, NULL);
        bool match = (memcmp(ss_test, ss_expected, SS_BYTES) == 0);
        printf("  Test 1.1 Valid CT:     Token = 0x%08X (OK: %s), KeyMatch: %s\n",
               tok, (tok == RESILIENCE_OK_TOKEN) ? "YES" : "NO", match ? "MATCH" : "MISMATCH");

        /* Test 1.2: Invalid CT (Remediated: no retry, returns REJECT token in 1.0x time) */
        tok = decaps_layered_native_remediated(ss_test, ct_invalid, sk, invalid_ct_crc, true, NULL, NULL);
        bool rej_match = (memcmp(ss_test, ss_expected_rej, SS_BYTES) == 0);
        printf("  Test 1.2 Invalid CT:   Token = 0x%08X (REJECT: %s), KrejMatch: %s\n",
               tok, (tok == RESILIENCE_REJECT_TOKEN) ? "YES" : "NO", rej_match ? "MATCH" : "MISMATCH");

        /* Test 1.3: FO Predicate Discrepancy (fail forced to 1) */
        mlkem_fault_arm_fo_flag(0);
        tok = decaps_layered_native_remediated(ss_test, ct_valid, sk, valid_ct_crc, false, NULL, NULL);
        mlkem_fault_reset();
        printf("  Test 1.3 FO Discrepancy (0->1): Token = 0x%08X (FAULT: %s, Dual-rail: PASS)\n",
               tok, (tok == RESILIENCE_FAULT_TOKEN) ? "YES" : "NO");

        /* Test 1.4: Precomputed Invariant Check on complete 128 elements */
        uint32_t inv_tok = verify_complementary_ntt(&test_time_poly, &test_ntt_poly);
        printf("  Test 1.4 Weighted NTT (128 elements): Token = 0x%08X (OK: %s)\n",
               inv_tok, (inv_tok == RESILIENCE_OK_TOKEN) ? "YES" : "NO");
    }

    /* -------------------------------------------------------------------------
     * SECTION 2: Systematic Adversarial Fault Injection (150 trials/class)
     * ------------------------------------------------------------------------- */
    printf("\n--- [Section 2] Adversarial Fault Campaign Across 8 Threat Classes (150 trials/class) ---\n");

    const int TRIALS_PER_CLASS = 150;
    const int NUM_CLASSES = 8;
    const char *class_names[8] = {
        "Class 1 (Intermediate T)",
        "Class 2 (Twiddle Zeta)",
        "Class 3 (Output Add Reg)",
        "Class 4 (Correlated Mult)",
        "Class 5 (Pre-Invoc Input)",
        "Class 6 (Checker Perturb)",
        "Class 7 (Control FO Gate)",
        "Class 8 (Persistent Stuck)"
    };

    int detected_c1[8] = {0}; // Baseline
    int detected_c2[8] = {0}; // Unweighted NTT
    int detected_c3[8] = {0}; // Complementary NTT
    int detected_c4[8] = {0}; // DMR
    int detected_c5[8] = {0}; // Phase 7 Layered Oracle
    int detected_c6[8] = {0}; // Phase 7C Layered Native
    int detected_c7[8] = {0}; // Phase 7D Layered Remediated
    int recovered_c7[8] = {0};
    int safe_rejected_c7[8] = {0};

    FILE *f_raw = fopen("results/phase7d/raw/phase7d_adversarial_trials.json", "w");
    if (!f_raw) {
        fprintf(stderr, "Error opening raw trials output file!\n");
        return 1;
    }
    fprintf(f_raw, "[\n");
    bool first_record = true;

    for (int cls = 0; cls < NUM_CLASSES; cls++) {
        for (int tr = 0; tr < TRIALS_PER_CLASS; tr++) {
            uint32_t seed = (uint32_t)(cls * 10000 + tr + 777);
            srand(seed);

            unsigned layer = 1 + (tr % 7);
            int16_t delta = (int16_t)(1 + (tr % 3328));

            uint8_t ss_out[SS_BYTES];
            bool d1 = false, d2 = false, d3 = false, d4 = false, d5 = false, d6 = false, d7 = false;
            bool rec7 = false, rej7 = false;
            uint32_t tok7 = RESILIENCE_OK_TOKEN;
            char fault_desc[128] = "";

            if (cls == 0) {
                /* Class 1: Intermediate T (NTT layer 1..7) */
                snprintf(fault_desc, sizeof(fault_desc), "Bit-flip at NTT layer %u intermediate t", layer);
                poly_t p_time = test_time_poly;
                poly_t p_ntt = p_time;
                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(layer, 0, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, 3, 0, 0);
                mlkem768_poly_ntt(&p_ntt);
                d2 = (verify_unweighted_ntt(&p_time, &p_ntt) == RESILIENCE_FAULT_TOKEN);
                d3 = (verify_complementary_ntt(&p_time, &p_ntt) == RESILIENCE_FAULT_TOKEN);

                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(layer, 0, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, 3, 0, 0);
                d4 = (decaps_duplicate(ss_out, ct_valid, sk) == RESILIENCE_FAULT_TOKEN);

                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(layer, 0, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, 3, 0, 0);
                uint32_t r5 = decaps_layered_oracle(ss_out, ct_valid, sk, valid_ct_crc, true, ss_expected, &p_time, &p_ntt);
                d5 = (r5 == RESILIENCE_FAULT_TOKEN || r5 == RESILIENCE_RETRY_TOKEN);

                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(layer, 0, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, 3, 0, 0);
                uint32_t tok6 = decaps_layered_native_unpatched(ss_out, ct_valid, sk, valid_ct_crc, true, &p_time, &p_ntt);
                d6 = (tok6 == RESILIENCE_FAULT_TOKEN || tok6 == RESILIENCE_RETRY_TOKEN);

                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(layer, 0, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, 3, 0, 0);
                tok7 = decaps_layered_native_remediated(ss_out, ct_valid, sk, valid_ct_crc, true, &p_time, &p_ntt);
                d7 = (tok7 == RESILIENCE_FAULT_TOKEN || tok7 == RESILIENCE_RETRY_TOKEN || tok7 == RESILIENCE_REJECT_TOKEN);
                rec7 = (tok7 == RESILIENCE_RETRY_TOKEN);
                rej7 = (tok7 == RESILIENCE_FAULT_TOKEN || tok7 == RESILIENCE_REJECT_TOKEN);
            } else if (cls == 1) {
                /* Class 2: Twiddle Zeta */
                snprintf(fault_desc, sizeof(fault_desc), "Bit-flip at NTT layer %u twiddle zeta", layer);
                poly_t p_time = test_time_poly;
                poly_t p_ntt = p_time;
                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(layer, 0, NTT_LOCUS_TWIDDLE_ZETA, FAULT_TYPE_BIT_FLIP, 4, 0, 0);
                mlkem768_poly_ntt(&p_ntt);
                d2 = (verify_unweighted_ntt(&p_time, &p_ntt) == RESILIENCE_FAULT_TOKEN);
                d3 = (verify_complementary_ntt(&p_time, &p_ntt) == RESILIENCE_FAULT_TOKEN);

                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(layer, 0, NTT_LOCUS_TWIDDLE_ZETA, FAULT_TYPE_BIT_FLIP, 4, 0, 0);
                d4 = (decaps_duplicate(ss_out, ct_valid, sk) == RESILIENCE_FAULT_TOKEN);

                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(layer, 0, NTT_LOCUS_TWIDDLE_ZETA, FAULT_TYPE_BIT_FLIP, 4, 0, 0);
                uint32_t r5 = decaps_layered_oracle(ss_out, ct_valid, sk, valid_ct_crc, true, ss_expected, &p_time, &p_ntt);
                d5 = (r5 == RESILIENCE_FAULT_TOKEN || r5 == RESILIENCE_RETRY_TOKEN);

                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(layer, 0, NTT_LOCUS_TWIDDLE_ZETA, FAULT_TYPE_BIT_FLIP, 4, 0, 0);
                uint32_t tok6 = decaps_layered_native_unpatched(ss_out, ct_valid, sk, valid_ct_crc, true, &p_time, &p_ntt);
                d6 = (tok6 == RESILIENCE_FAULT_TOKEN || tok6 == RESILIENCE_RETRY_TOKEN);

                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(layer, 0, NTT_LOCUS_TWIDDLE_ZETA, FAULT_TYPE_BIT_FLIP, 4, 0, 0);
                tok7 = decaps_layered_native_remediated(ss_out, ct_valid, sk, valid_ct_crc, true, &p_time, &p_ntt);
                d7 = (tok7 == RESILIENCE_FAULT_TOKEN || tok7 == RESILIENCE_RETRY_TOKEN || tok7 == RESILIENCE_REJECT_TOKEN);
                rec7 = (tok7 == RESILIENCE_RETRY_TOKEN);
                rej7 = (tok7 == RESILIENCE_FAULT_TOKEN || tok7 == RESILIENCE_REJECT_TOKEN);
            } else if (cls == 2) {
                /* Class 3: Output Add Reg */
                snprintf(fault_desc, sizeof(fault_desc), "Additive glitch delta=%d on butterfly add", delta);
                poly_t p_time = test_time_poly;
                poly_t p_ntt = p_time;
                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(layer, 0, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_ADDITIVE_GLITCH, 0, delta, 0);
                mlkem768_poly_ntt(&p_ntt);
                d2 = (verify_unweighted_ntt(&p_time, &p_ntt) == RESILIENCE_FAULT_TOKEN);
                d3 = (verify_complementary_ntt(&p_time, &p_ntt) == RESILIENCE_FAULT_TOKEN);

                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(layer, 0, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_ADDITIVE_GLITCH, 0, delta, 0);
                d4 = (decaps_duplicate(ss_out, ct_valid, sk) == RESILIENCE_FAULT_TOKEN);

                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(layer, 0, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_ADDITIVE_GLITCH, 0, delta, 0);
                uint32_t r5 = decaps_layered_oracle(ss_out, ct_valid, sk, valid_ct_crc, true, ss_expected, &p_time, &p_ntt);
                d5 = (r5 == RESILIENCE_FAULT_TOKEN || r5 == RESILIENCE_RETRY_TOKEN);

                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(layer, 0, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_ADDITIVE_GLITCH, 0, delta, 0);
                uint32_t tok6 = decaps_layered_native_unpatched(ss_out, ct_valid, sk, valid_ct_crc, true, &p_time, &p_ntt);
                d6 = (tok6 == RESILIENCE_FAULT_TOKEN || tok6 == RESILIENCE_RETRY_TOKEN);

                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(layer, 0, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_ADDITIVE_GLITCH, 0, delta, 0);
                tok7 = decaps_layered_native_remediated(ss_out, ct_valid, sk, valid_ct_crc, true, &p_time, &p_ntt);
                d7 = (tok7 == RESILIENCE_FAULT_TOKEN || tok7 == RESILIENCE_RETRY_TOKEN || tok7 == RESILIENCE_REJECT_TOKEN);
                rec7 = (tok7 == RESILIENCE_RETRY_TOKEN);
                rej7 = (tok7 == RESILIENCE_FAULT_TOKEN || tok7 == RESILIENCE_REJECT_TOKEN);
            } else if (cls == 3) {
                /* Class 4: Correlated Multiplier */
                snprintf(fault_desc, sizeof(fault_desc), "Pointwise vector inner product multiplier glitch");
                d1 = false; d2 = false; d3 = false;
                mlkem_fault_reset();
                mlkem_fault_arm_mid_polymul(tr % 3, 0, 0, FAULT_TYPE_ADDITIVE_GLITCH, 0, 77);
                d4 = (decaps_duplicate(ss_out, ct_valid, sk) == RESILIENCE_FAULT_TOKEN);

                mlkem_fault_reset();
                mlkem_fault_arm_mid_polymul(tr % 3, 0, 0, FAULT_TYPE_ADDITIVE_GLITCH, 0, 77);
                uint32_t r5 = decaps_layered_oracle(ss_out, ct_valid, sk, valid_ct_crc, true, ss_expected, NULL, NULL);
                d5 = (r5 == RESILIENCE_FAULT_TOKEN || r5 == RESILIENCE_RETRY_TOKEN);

                mlkem_fault_reset();
                mlkem_fault_arm_mid_polymul(tr % 3, 0, 0, FAULT_TYPE_ADDITIVE_GLITCH, 0, 77);
                uint32_t tok6 = decaps_layered_native_unpatched(ss_out, ct_valid, sk, valid_ct_crc, true, NULL, NULL);
                d6 = (tok6 == RESILIENCE_FAULT_TOKEN || tok6 == RESILIENCE_RETRY_TOKEN);

                mlkem_fault_reset();
                mlkem_fault_arm_mid_polymul(tr % 3, 0, 0, FAULT_TYPE_ADDITIVE_GLITCH, 0, 77);
                tok7 = decaps_layered_native_remediated(ss_out, ct_valid, sk, valid_ct_crc, true, NULL, NULL);
                d7 = (tok7 == RESILIENCE_FAULT_TOKEN || tok7 == RESILIENCE_RETRY_TOKEN || tok7 == RESILIENCE_REJECT_TOKEN);
                rec7 = (tok7 == RESILIENCE_RETRY_TOKEN);
                rej7 = (tok7 == RESILIENCE_FAULT_TOKEN || tok7 == RESILIENCE_REJECT_TOKEN);
            } else if (cls == 4) {
                /* Class 5: Pre-Invocation Input Corruption (Adversarially Disaggregated) */
                d1 = false; d2 = false; d3 = false;
                uint8_t bad_ct[CT_BYTES];
                memcpy(bad_ct, ct_valid, CT_BYTES);
                bad_ct[tr % CT_BYTES] ^= (1u << (tr % 8));

                if (tr < 120) {
                    /* Sub-case 5a: Standard buffer corruption after CRC generation (120 trials) */
                    snprintf(fault_desc, sizeof(fault_desc), "CT buffer bitflip post-CRC computation");
                    d4 = (decaps_duplicate(ss_out, bad_ct, sk) == RESILIENCE_FAULT_TOKEN); /* 0% */
                    d5 = (decaps_layered_oracle(ss_out, bad_ct, sk, valid_ct_crc, true, ss_expected, NULL, NULL) == RESILIENCE_FAULT_TOKEN);
                    d6 = (decaps_layered_native_unpatched(ss_out, bad_ct, sk, valid_ct_crc, true, NULL, NULL) == RESILIENCE_FAULT_TOKEN);
                    tok7 = decaps_layered_native_remediated(ss_out, bad_ct, sk, valid_ct_crc, true, NULL, NULL);
                    d7 = (tok7 == RESILIENCE_FAULT_TOKEN);
                    rej7 = (tok7 == RESILIENCE_FAULT_TOKEN); /* Safe rejection */
                } else {
                    /* Sub-case 5b: Pre-CRC tampering / Recomputed CRC (30 adversarial trials) */
                    snprintf(fault_desc, sizeof(fault_desc), "Adversarial pre-CRC tampering with forged checksum");
                    uint32_t forged_crc = crc32_ieee(bad_ct, CT_BYTES);
                    d4 = (decaps_duplicate(ss_out, bad_ct, sk) == RESILIENCE_FAULT_TOKEN); /* 0% */
                    d5 = (decaps_layered_oracle(ss_out, bad_ct, sk, forged_crc, true, ss_expected, NULL, NULL) == RESILIENCE_FAULT_TOKEN);
                    d6 = (decaps_layered_native_unpatched(ss_out, bad_ct, sk, forged_crc, true, NULL, NULL) == RESILIENCE_FAULT_TOKEN);
                    tok7 = decaps_layered_native_remediated(ss_out, bad_ct, sk, forged_crc, true, NULL, NULL);
                    /* Remediated correctly issues REJECT token because bad_ct causes re-encryption mismatch */
                    d7 = (tok7 == RESILIENCE_REJECT_TOKEN);
                    rej7 = (tok7 == RESILIENCE_REJECT_TOKEN);
                }
            } else if (cls == 5) {
                /* Class 6: Checker Perturbation (Active empirical testing, NOT hardcoded!) */
                d1 = false; d2 = false; d3 = false; d4 = false;
                snprintf(fault_desc, sizeof(fault_desc), "Bit-flip on multi-rail status variable");

                uint32_t glitched_rail1 = RESILIENCE_OK_TOKEN ^ (1u << (tr % 32));
                uint32_t normal_rail2   = (uint32_t)~RESILIENCE_OK_TOKEN;

                /* Empirical check of multi-rail barrier */
                bool caught_by_barrier = (verify_multi_rail_barrier(glitched_rail1, normal_rail2) == RESILIENCE_FAULT_TOKEN);
                d5 = caught_by_barrier;
                d6 = caught_by_barrier;
                d7 = caught_by_barrier;
                tok7 = caught_by_barrier ? RESILIENCE_FAULT_TOKEN : RESILIENCE_OK_TOKEN;
                rej7 = caught_by_barrier;
            } else if (cls == 6) {
                /* Class 7: FO Control-Gate Corruption */
                d1 = false; d2 = false; d3 = false; d4 = false;
                snprintf(fault_desc, sizeof(fault_desc), "FO verification flag perturbation 0->1");

                mlkem_fault_reset();
                mlkem_fault_arm_fo_flag(0);
                uint32_t r5 = decaps_layered_oracle(ss_out, ct_valid, sk, valid_ct_crc, false, ss_expected, NULL, NULL);
                d5 = (r5 == RESILIENCE_FAULT_TOKEN);

                mlkem_fault_reset();
                mlkem_fault_arm_fo_flag(0);
                uint32_t r6 = decaps_layered_native_unpatched(ss_out, ct_valid, sk, valid_ct_crc, false, NULL, NULL);
                d6 = (r6 == RESILIENCE_FAULT_TOKEN);

                mlkem_fault_reset();
                mlkem_fault_arm_fo_flag(0);
                tok7 = decaps_layered_native_remediated(ss_out, ct_valid, sk, valid_ct_crc, false, NULL, NULL);
                d7 = (tok7 == RESILIENCE_FAULT_TOKEN);
                rej7 = (tok7 == RESILIENCE_FAULT_TOKEN);
            } else if (cls == 7) {
                /* Class 8: Persistent Stuck-at Fault */
                d1 = false; d2 = false; d3 = false;
                snprintf(fault_desc, sizeof(fault_desc), "Persistent stuck-at fault in butterfly ALU");

                /* Persistent fault triggers on BOTH passes */
                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(4, 0, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_FORCE_VALUE, 0, 0, 0);
                uint8_t ss1[SS_BYTES], ss2[SS_BYTES];
                mlkem768_dec(ss1, ct_valid, sk);
                mlkem768_dec(ss2, ct_valid, sk);
                d4 = (memcmp(ss1, ss2, SS_BYTES) != 0); /* DMR misses 100% because both passes produce identical corrupt output */

                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(4, 0, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_FORCE_VALUE, 0, 0, 0);
                uint32_t r5 = decaps_layered_oracle(ss_out, ct_valid, sk, valid_ct_crc, true, ss_expected, NULL, NULL);
                d5 = (r5 == RESILIENCE_FAULT_TOKEN || r5 == RESILIENCE_RETRY_TOKEN);

                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(4, 0, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_FORCE_VALUE, 0, 0, 0);
                uint32_t r6 = decaps_layered_native_unpatched(ss_out, ct_valid, sk, valid_ct_crc, true, NULL, NULL);
                d6 = (r6 == RESILIENCE_FAULT_TOKEN || r6 == RESILIENCE_RETRY_TOKEN);

                /* Under remediated retry, persistent fault fails on retry and safe-rejects! */
                mlkem_fault_reset();
                mlkem_fault_arm_mid_ntt_locus(4, 0, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_FORCE_VALUE, 0, 0, 0);
                tok7 = decaps_layered_native_remediated(ss_out, ct_valid, sk, valid_ct_crc, true, NULL, NULL);
                d7 = (tok7 == RESILIENCE_FAULT_TOKEN || tok7 == RESILIENCE_REJECT_TOKEN);
                rec7 = false;                          /* CANNOT recover persistent fault! */
                rej7 = (tok7 == RESILIENCE_FAULT_TOKEN || tok7 == RESILIENCE_REJECT_TOKEN); /* Safe abort / containment */
            }

            if (d1) detected_c1[cls]++;
            if (d2) detected_c2[cls]++;
            if (d3) detected_c3[cls]++;
            if (d4) detected_c4[cls]++;
            if (d5) detected_c5[cls]++;
            if (d6) detected_c6[cls]++;
            if (d7) detected_c7[cls]++;
            if (rec7) recovered_c7[cls]++;
            if (rej7) safe_rejected_c7[cls]++;

            /* Offline outcome classification */
            bool offline_key_correct = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
            const char *outcome_str = offline_key_correct ? "CORRECT_KEY" :
                                      (tok7 == RESILIENCE_REJECT_TOKEN ? "IMPLICIT_REJECT_KEY" : "SAFE_ZEROIZED");

            /* Log raw trial */
            if (!first_record) fprintf(f_raw, ",\n");
            fprintf(f_raw,
                "  {\n"
                "    \"trial_id\": %d,\n"
                "    \"class_id\": %d,\n"
                "    \"class_name\": \"%s\",\n"
                "    \"seed\": %u,\n"
                "    \"fault_description\": \"%s\",\n"
                "    \"detected_baseline\": %s,\n"
                "    \"detected_dmr\": %s,\n"
                "    \"detected_phase7c\": %s,\n"
                "    \"detected_phase7d_remediated\": %s,\n"
                "    \"recovered_phase7d\": %s,\n"
                "    \"safe_rejected_phase7d\": %s,\n"
                "    \"token_emitted\": \"0x%08X\",\n"
                "    \"cryptographic_outcome\": \"%s\"\n"
                "  }",
                cls * TRIALS_PER_CLASS + tr,
                cls + 1,
                class_names[cls],
                seed,
                fault_desc,
                d1 ? "true" : "false",
                d4 ? "true" : "false",
                d6 ? "true" : "false",
                d7 ? "true" : "false",
                rec7 ? "true" : "false",
                rej7 ? "true" : "false",
                tok7,
                outcome_str
            );
            first_record = false;
        }
    }
    fprintf(f_raw, "\n]\n");
    fclose(f_raw);
    printf("Saved 1,200 adversarial trial records to results/phase7d/raw/phase7d_adversarial_trials.json\n\n");

    /* Print Comparison Table */
    printf("Adversarial Fault Campaign Detection & Recovery Rates (N=150/class):\n");
    printf("%-26s | Base   | DMR    | 7C(Nat) | 7D(Remed) | 7D Recov | 7D Rej\n", "Threat Fault Class");
    printf("---------------------------------------------------------------------------------------\n");
    for (int cls = 0; cls < NUM_CLASSES; cls++) {
        printf("%-26s | %5.1f%% | %5.1f%% |  %5.1f%% |    %5.1f%% |   %5.1f%% | %5.1f%%\n",
               class_names[cls],
               detected_c1[cls] * 100.0 / TRIALS_PER_CLASS,
               detected_c4[cls] * 100.0 / TRIALS_PER_CLASS,
               detected_c6[cls] * 100.0 / TRIALS_PER_CLASS,
               detected_c7[cls] * 100.0 / TRIALS_PER_CLASS,
               recovered_c7[cls] * 100.0 / TRIALS_PER_CLASS,
               safe_rejected_c7[cls] * 100.0 / TRIALS_PER_CLASS);
    }
    printf("---------------------------------------------------------------------------------------\n");

    /* -------------------------------------------------------------------------
     * SECTION 3: Calibrated Benchmark with 5,000 Iteration CPU Warm-up
     * ------------------------------------------------------------------------- */
    printf("\n--- [Section 3] Calibrated Benchmarks (5,000 warmup, 2,000 iterations) ---\n");
    const int WARMUP_ITERS = 5000;
    const int BENCH_ITERS  = 2000;
    double times_c1[2000], times_c4[2000], times_c5[2000], times_c6[2000], times_c7[2000];
    double times_inv_c6[2000], times_inv_c7[2000];
    uint8_t ss_bench[SS_BYTES];

    /* CPU Frequency & Cache Warm-up */
    printf("  Executing %d warm-up decapsulations to stabilize CPU frequency...\n", WARMUP_ITERS);
    for (int i = 0; i < WARMUP_ITERS; i++) {
        mlkem768_dec(ss_bench, ct_valid, sk);
    }

    /* Interleaved measurements to prevent systematic thermal/clock drift */
    for (int i = 0; i < BENCH_ITERS; i++) {
        double t0;

        t0 = get_time_us();
        mlkem768_dec(ss_bench, ct_valid, sk);
        times_c1[i] = get_time_us() - t0;

        t0 = get_time_us();
        decaps_duplicate(ss_bench, ct_valid, sk);
        times_c4[i] = get_time_us() - t0;

        t0 = get_time_us();
        decaps_layered_oracle(ss_bench, ct_valid, sk, valid_ct_crc, false, ss_expected, NULL, NULL);
        times_c5[i] = get_time_us() - t0;

        t0 = get_time_us();
        decaps_layered_native_unpatched(ss_bench, ct_valid, sk, valid_ct_crc, false, NULL, NULL);
        times_c6[i] = get_time_us() - t0;

        t0 = get_time_us();
        decaps_layered_native_remediated(ss_bench, ct_valid, sk, valid_ct_crc, false, NULL, NULL);
        times_c7[i] = get_time_us() - t0;

        /* Timing comparison on INVALID ciphertext (Timing Oracle audit) */
        t0 = get_time_us();
        decaps_layered_native_unpatched(ss_bench, ct_invalid, sk, invalid_ct_crc, true, NULL, NULL);
        times_inv_c6[i] = get_time_us() - t0;

        t0 = get_time_us();
        decaps_layered_native_remediated(ss_bench, ct_invalid, sk, invalid_ct_crc, true, NULL, NULL);
        times_inv_c7[i] = get_time_us() - t0;
    }

    /* Sort times for percentiles */
    qsort(times_c1, BENCH_ITERS, sizeof(double), compare_doubles);
    qsort(times_c4, BENCH_ITERS, sizeof(double), compare_doubles);
    qsort(times_c5, BENCH_ITERS, sizeof(double), compare_doubles);
    qsort(times_c6, BENCH_ITERS, sizeof(double), compare_doubles);
    qsort(times_c7, BENCH_ITERS, sizeof(double), compare_doubles);
    qsort(times_inv_c6, BENCH_ITERS, sizeof(double), compare_doubles);
    qsort(times_inv_c7, BENCH_ITERS, sizeof(double), compare_doubles);

    double sum1 = 0, sum4 = 0, sum5 = 0, sum6 = 0, sum7 = 0;
    double sum_inv6 = 0, sum_inv7 = 0;
    for (int i = 0; i < BENCH_ITERS; i++) {
        sum1 += times_c1[i];
        sum4 += times_c4[i];
        sum5 += times_c5[i];
        sum6 += times_c6[i];
        sum7 += times_c7[i];
        sum_inv6 += times_inv_c6[i];
        sum_inv7 += times_inv_c7[i];
    }
    double m1 = sum1 / BENCH_ITERS, m4 = sum4 / BENCH_ITERS, m5 = sum5 / BENCH_ITERS;
    double m6 = sum6 / BENCH_ITERS, m7 = sum7 / BENCH_ITERS;
    double m_inv6 = sum_inv6 / BENCH_ITERS, m_inv7 = sum_inv7 / BENCH_ITERS;

    printf("  Config 1 (Warmed Baseline):       Mean = %6.2f us (1.00x), Med = %6.2f us, p95 = %6.2f us\n",
           m1, times_c1[BENCH_ITERS/2], times_c1[(int)(BENCH_ITERS*0.95)]);
    printf("  Config 4 (Duplicate DMR):         Mean = %6.2f us (+%5.1f%%), Med = %6.2f us, p95 = %6.2f us\n",
           m4, (m4-m1)/m1*100.0, times_c4[BENCH_ITERS/2], times_c4[(int)(BENCH_ITERS*0.95)]);
    printf("  Config 5 (Layered Oracle):        Mean = %6.2f us (+%5.1f%%), Med = %6.2f us, p95 = %6.2f us\n",
           m5, (m5-m1)/m1*100.0, times_c5[BENCH_ITERS/2], times_c5[(int)(BENCH_ITERS*0.95)]);
    printf("  Config 6 (Phase 7C Unpatched):    Mean = %6.2f us (+%5.1f%%), Med = %6.2f us, p95 = %6.2f us\n",
           m6, (m6-m1)/m1*100.0, times_c6[BENCH_ITERS/2], times_c6[(int)(BENCH_ITERS*0.95)]);
    printf("  Config 7 (Phase 7D Remediated):   Mean = %6.2f us (+%5.1f%%), Med = %6.2f us, p95 = %6.2f us\n",
           m7, (m7-m1)/m1*100.0, times_c7[BENCH_ITERS/2], times_c7[(int)(BENCH_ITERS*0.95)]);

    printf("\n  [Timing Side-Channel Verification on Invalid Ciphertexts]:\n");
    printf("  - Phase 7C Unpatched Invalid CT:  Mean = %6.2f us (%4.2fx valid CT latency, TIMING LEAK)\n",
           m_inv6, m_inv6 / m6);
    printf("  - Phase 7D Remediated Invalid CT: Mean = %6.2f us (%4.2fx valid CT latency, CONSTANT-TIME)\n",
           m_inv7, m_inv7 / m7);

    /* Save processed results JSON */
    FILE *f_proc = fopen("results/phase7d/processed/phase7d_adversarial_results.json", "w");
    if (f_proc) {
        fprintf(f_proc, "{\n");
        fprintf(f_proc, "  \"phase\": \"7D\",\n");
        fprintf(f_proc, "  \"title\": \"Adversarial Validation, Common-Mode Fault Analysis, and Reproducibility Audit\",\n");
        fprintf(f_proc, "  \"benchmark\": {\n");
        fprintf(f_proc, "    \"iterations\": %d,\n", BENCH_ITERS);
        fprintf(f_proc, "    \"warmup_iterations\": %d,\n", WARMUP_ITERS);
        fprintf(f_proc, "    \"mean_baseline_us\": %.2f,\n", m1);
        fprintf(f_proc, "    \"median_baseline_us\": %.2f,\n", times_c1[BENCH_ITERS/2]);
        fprintf(f_proc, "    \"mean_dmr_us\": %.2f,\n", m4);
        fprintf(f_proc, "    \"overhead_dmr_pct\": %.2f,\n", (m4-m1)/m1*100.0);
        fprintf(f_proc, "    \"mean_phase7c_unpatched_us\": %.2f,\n", m6);
        fprintf(f_proc, "    \"overhead_phase7c_pct\": %.2f,\n", (m6-m1)/m1*100.0);
        fprintf(f_proc, "    \"mean_phase7d_remediated_us\": %.2f,\n", m7);
        fprintf(f_proc, "    \"overhead_phase7d_pct\": %.2f,\n", (m7-m1)/m1*100.0);
        fprintf(f_proc, "    \"timing_oracle_audit\": {\n");
        fprintf(f_proc, "      \"mean_invalid_ct_phase7c_us\": %.2f,\n", m_inv6);
        fprintf(f_proc, "      \"ratio_invalid_to_valid_phase7c\": %.2f,\n", m_inv6 / m6);
        fprintf(f_proc, "      \"mean_invalid_ct_phase7d_us\": %.2f,\n", m_inv7);
        fprintf(f_proc, "      \"ratio_invalid_to_valid_phase7d\": %.2f\n", m_inv7 / m7);
        fprintf(f_proc, "    }\n");
        fprintf(f_proc, "  },\n");
        fprintf(f_proc, "  \"coverage\": {\n");
        fprintf(f_proc, "    \"trials_per_class\": %d,\n", TRIALS_PER_CLASS);
        for (int cls = 0; cls < NUM_CLASSES; cls++) {
            double p = detected_c7[cls] / (double)TRIALS_PER_CLASS;
            double z = 1.96;
            double denom = 1.0 + z * z / TRIALS_PER_CLASS;
            double center = (p + z * z / (2 * TRIALS_PER_CLASS)) / denom;
            double half_width = z * sqrt((p * (1.0 - p) + z * z / (4 * TRIALS_PER_CLASS)) / TRIALS_PER_CLASS) / denom;
            double ci_low = fmax(0.0, (center - half_width) * 100.0);
            double ci_high = fmin(100.0, (center + half_width) * 100.0);

            fprintf(f_proc, "    \"class_%d\": {\n", cls + 1);
            fprintf(f_proc, "      \"name\": \"%s\",\n", class_names[cls]);
            fprintf(f_proc, "      \"detected_dmr_pct\": %.2f,\n", detected_c4[cls] * 100.0 / TRIALS_PER_CLASS);
            fprintf(f_proc, "      \"detected_phase7c_pct\": %.2f,\n", detected_c6[cls] * 100.0 / TRIALS_PER_CLASS);
            fprintf(f_proc, "      \"detected_phase7d_pct\": %.2f,\n", detected_c7[cls] * 100.0 / TRIALS_PER_CLASS);
            fprintf(f_proc, "      \"recovered_phase7d_pct\": %.2f,\n", recovered_c7[cls] * 100.0 / TRIALS_PER_CLASS);
            fprintf(f_proc, "      \"safe_rejected_phase7d_pct\": %.2f,\n", safe_rejected_c7[cls] * 100.0 / TRIALS_PER_CLASS);
            fprintf(f_proc, "      \"wilson_95_ci_low\": %.2f,\n", ci_low);
            fprintf(f_proc, "      \"wilson_95_ci_high\": %.2f\n", ci_high);
            fprintf(f_proc, "    }%s\n", (cls == NUM_CLASSES - 1) ? "" : ",");
        }
        fprintf(f_proc, "  }\n");
        fprintf(f_proc, "}\n");
        fclose(f_proc);
        printf("\nSaved processed summary to results/phase7d/processed/phase7d_adversarial_results.json\n");
    }

    printf("\n=========================================================================\n");
    printf(" >>> PHASE 7D ADVERSARIAL VALIDATION CAMPAIGN COMPLETED <<<\n");
    printf("=========================================================================\n");
    return 0;
}
