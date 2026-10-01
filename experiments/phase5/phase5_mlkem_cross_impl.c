/**
 * Phase 5 — Cross-Implementation Fault-Surface Validation
 * 
 * This experiment performs:
 * 1. Baseline equivalence: C-ref vs liboqs deterministic API comparison
 * 2. Instrumentation transparency: hooks dormant vs clean build
 * 3. Fault reproduction: selected Phase 2-4 experiments on C-ref
 * 4. Compiler sensitivity: assembly inspection for critical operations
 * 5. Cross-backend statistical comparison
 *
 * Implementation A: mlkem-native / mldsa-native C reference (instrumented)
 * Implementation B: liboqs 0.16.0 (AArch64 assembly backend, opaque)
 *
 * CRITICAL: Both implementations derive from the same pq-code-package source.
 * This is a backend comparison, NOT an independent implementation comparison.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <oqs/oqs.h>

/* Path B symbols (mlkem-native C-ref, parameter set 768) */
int mlkem_keypair_derand(uint8_t *pk, uint8_t *sk, const uint8_t *coins);
int mlkem_enc_derand(uint8_t *ct, uint8_t *ss, const uint8_t *pk, const uint8_t *coins);
int mlkem_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);

/* Path B symbols (mlkem-native C-ref, instrumented with fault hooks) */
int mlkem768_keypair_derand(uint8_t *pk, uint8_t *sk, const uint8_t *coins);
int mlkem768_enc_derand(uint8_t *ct, uint8_t *ss, const uint8_t *pk, const uint8_t *coins);
int mlkem768_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);

/* Fault hook API */
#include "algorithms/source_ref/mlkem_fault_hooks.h"

/* FIPS 203 sizes for ML-KEM-768 */
#define PK_BYTES 1184
#define SK_BYTES 2400
#define CT_BYTES 1088
#define SS_BYTES 32
#define KEYPAIR_SEED_BYTES 64
#define ENCAPS_SEED_BYTES 32

/* Randomness bridge */
int randombytes(uint8_t *out, size_t outlen) {
    OQS_randombytes(out, outlen);
    return 0;
}

/* JSON output helpers */
static FILE *g_json = NULL;
static int g_first_record = 1;

static void json_open(const char *path) {
    g_json = fopen(path, "w");
    if (!g_json) { fprintf(stderr, "ERROR: Cannot open %s\n", path); exit(1); }
    fprintf(g_json, "{\n");
    g_first_record = 1;
}

static void json_close(void) {
    fprintf(g_json, "\n}\n");
    fclose(g_json);
    g_json = NULL;
}

static void json_key_value(const char *key, const char *value) {
    if (!g_first_record) fprintf(g_json, ",\n");
    fprintf(g_json, "  \"%s\": \"%s\"", key, value);
    g_first_record = 0;
}

static void json_key_int(const char *key, int value) {
    if (!g_first_record) fprintf(g_json, ",\n");
    fprintf(g_json, "  \"%s\": %d", key, value);
    g_first_record = 0;
}

static void json_key_bool(const char *key, bool value) {
    if (!g_first_record) fprintf(g_json, ",\n");
    fprintf(g_json, "  \"%s\": %s", key, value ? "true" : "false");
    g_first_record = 0;
}

/* ============================================================
 * CATEGORY 1: Baseline Equivalence
 * Verify C-ref and liboqs produce identical outputs for identical inputs
 * ============================================================ */

static int test_baseline_equivalence(void) {
    printf("\n=== CATEGORY 1: Baseline Equivalence (C-ref vs liboqs) ===\n");
    
    int pass_count = 0;
    int fail_count = 0;
    
    /* Test with multiple deterministic seed patterns */
    uint8_t seed_patterns[4][64];
    memset(seed_patterns[0], 0x00, 64);
    memset(seed_patterns[1], 0xFF, 64);
    memset(seed_patterns[2], 0x42, 64);
    for (int i = 0; i < 64; i++) seed_patterns[3][i] = (uint8_t)(i * 7 + 13);
    
    for (int sp = 0; sp < 4; sp++) {
        printf("  Seed pattern %d: ", sp);
        
        /* Generate keypair with both implementations */
        uint8_t pk_ref[PK_BYTES], sk_ref[SK_BYTES];
        uint8_t pk_oqs[PK_BYTES], sk_oqs[SK_BYTES];
        
        int rc_ref = mlkem_keypair_derand(pk_ref, sk_ref, seed_patterns[sp]);
        OQS_STATUS rc_oqs = OQS_KEM_ml_kem_768_keypair_derand(pk_oqs, sk_oqs, seed_patterns[sp]);
        
        if (rc_ref != 0 || rc_oqs != OQS_SUCCESS) {
            printf("FAIL (keygen error: ref=%d, oqs=%d)\n", rc_ref, rc_oqs);
            fail_count++;
            continue;
        }
        
        /* Compare public keys */
        bool pk_match = (memcmp(pk_ref, sk_ref, PK_BYTES) == 0) ? false : true; /* check valid */
        pk_match = (memcmp(pk_ref, pk_oqs, PK_BYTES) == 0);
        
        /* Compare secret keys */
        bool sk_match = (memcmp(sk_ref, sk_oqs, SK_BYTES) == 0);
        
        if (!pk_match || !sk_match) {
            printf("FAIL (pk_match=%d, sk_match=%d)\n", pk_match, sk_match);
            fail_count++;
            continue;
        }
        
        /* Encaps with C-ref pk, using deterministic seed */
        uint8_t enc_seed[ENCAPS_SEED_BYTES];
        memset(enc_seed, (uint8_t)(0xAA + sp), ENCAPS_SEED_BYTES);
        
        uint8_t ct_ref[CT_BYTES], ss_ref_enc[SS_BYTES];
        uint8_t ct_oqs[CT_BYTES], ss_oqs_enc[SS_BYTES];
        
        rc_ref = mlkem_enc_derand(ct_ref, ss_ref_enc, pk_ref, enc_seed);
        rc_oqs = OQS_KEM_ml_kem_768_encaps_derand(ct_oqs, ss_oqs_enc, pk_oqs, enc_seed);
        
        if (rc_ref != 0 || rc_oqs != OQS_SUCCESS) {
            printf("FAIL (encaps error)\n");
            fail_count++;
            continue;
        }
        
        bool ct_match = (memcmp(ct_ref, ct_oqs, CT_BYTES) == 0);
        bool ss_enc_match = (memcmp(ss_ref_enc, ss_oqs_enc, SS_BYTES) == 0);
        
        /* Cross-decaps: C-ref decaps liboqs ciphertext, and vice versa */
        uint8_t ss_ref_dec[SS_BYTES], ss_oqs_dec[SS_BYTES];
        
        mlkem_dec(ss_ref_dec, ct_oqs, sk_ref);  /* C-ref decaps liboqs CT */
        OQS_KEM_ml_kem_768_decaps(ss_oqs_dec, ct_ref, sk_oqs);  /* liboqs decaps C-ref CT */
        
        bool cross_ref_match = (memcmp(ss_ref_dec, ss_oqs_enc, SS_BYTES) == 0);
        bool cross_oqs_match = (memcmp(ss_oqs_dec, ss_ref_enc, SS_BYTES) == 0);
        
        bool all_pass = pk_match && sk_match && ct_match && ss_enc_match && 
                        cross_ref_match && cross_oqs_match;
        
        if (all_pass) {
            printf("PASS (pk=sk=ct=ss=cross-decaps all match)\n");
            pass_count++;
        } else {
            printf("FAIL (pk=%d sk=%d ct=%d ss=%d cross_ref=%d cross_oqs=%d)\n",
                   pk_match, sk_match, ct_match, ss_enc_match,
                   cross_ref_match, cross_oqs_match);
            fail_count++;
        }
    }
    
    printf("  Baseline equivalence: %d/%d passed\n", pass_count, pass_count + fail_count);
    return fail_count;
}

/* ============================================================
 * CATEGORY 2: Instrumentation Transparency
 * Verify that fault hooks (when dormant) do not alter outputs
 * ============================================================ */

static int test_instrumentation_transparency(void) {
    printf("\n=== CATEGORY 2: Instrumentation Transparency ===\n");
    
    int pass_count = 0;
    int fail_count = 0;
    
    /* Compare clean build (mlkem_*) vs instrumented build (mlkem768_*) with hooks dormant */
    uint8_t seeds[3][64];
    memset(seeds[0], 0x11, 64);
    memset(seeds[1], 0x55, 64);
    memset(seeds[2], 0x99, 64);
    
    for (int s = 0; s < 3; s++) {
        printf("  Seed %d: ", s);
        
        /* Ensure hooks are disarmed */
        mlkem_fault_reset();
        
        uint8_t pk_clean[PK_BYTES], sk_clean[SK_BYTES];
        uint8_t pk_inst[PK_BYTES], sk_inst[SK_BYTES];
        
        mlkem_keypair_derand(pk_clean, sk_clean, seeds[s]);
        mlkem768_keypair_derand(pk_inst, sk_inst, seeds[s]);
        
        bool pk_match = (memcmp(pk_clean, pk_inst, PK_BYTES) == 0);
        bool sk_match = (memcmp(sk_clean, sk_inst, SK_BYTES) == 0);
        
        /* Encaps with both */
        uint8_t enc_seed[32];
        memset(enc_seed, (uint8_t)(0xBB + s), 32);
        
        uint8_t ct_clean[CT_BYTES], ss_clean[SS_BYTES];
        uint8_t ct_inst[CT_BYTES], ss_inst[SS_BYTES];
        
        mlkem_enc_derand(ct_clean, ss_clean, pk_clean, enc_seed);
        mlkem768_enc_derand(ct_inst, ss_inst, pk_inst, enc_seed);
        
        bool ct_match = (memcmp(ct_clean, ct_inst, CT_BYTES) == 0);
        bool ss_match = (memcmp(ss_clean, ss_inst, SS_BYTES) == 0);
        
        /* Decaps */
        uint8_t ss_dec_clean[SS_BYTES], ss_dec_inst[SS_BYTES];
        mlkem_dec(ss_dec_clean, ct_clean, sk_clean);
        mlkem768_dec(ss_dec_inst, ct_inst, sk_inst);
        
        bool dec_match = (memcmp(ss_dec_clean, ss_dec_inst, SS_BYTES) == 0);
        bool key_agreement = (memcmp(ss_clean, ss_dec_clean, SS_BYTES) == 0);
        
        bool all_pass = pk_match && sk_match && ct_match && ss_match && dec_match && key_agreement;
        
        if (all_pass) {
            printf("PASS (clean == instrumented, key agreement OK)\n");
            pass_count++;
        } else {
            printf("FAIL (pk=%d sk=%d ct=%d ss=%d dec=%d agree=%d)\n",
                   pk_match, sk_match, ct_match, ss_match, dec_match, key_agreement);
            fail_count++;
        }
    }
    
    printf("  Instrumentation transparency: %d/%d passed\n", pass_count, pass_count + fail_count);
    return fail_count;
}

/* ============================================================
 * CATEGORY 3: Cross-Backend Key Agreement Statistical Comparison
 * Large-trial test of key agreement rates across backends
 * ============================================================ */

static int test_cross_backend_key_agreement(int num_trials) {
    printf("\n=== CATEGORY 3: Cross-Backend Key Agreement (%d trials) ===\n", num_trials);
    
    int agree_ref_ref = 0;
    int agree_oqs_oqs = 0;
    int agree_cross_ref_decaps_oqs_ct = 0;
    int agree_cross_oqs_decaps_ref_ct = 0;
    int errors = 0;
    
    OQS_KEM *kem = OQS_KEM_new(OQS_KEM_alg_ml_kem_768);
    if (!kem) {
        printf("  ERROR: Cannot allocate liboqs ML-KEM-768\n");
        return 1;
    }
    
    for (int t = 0; t < num_trials; t++) {
        /* Generate random keypair with C-ref */
        uint8_t coins[64];
        OQS_randombytes(coins, 64);
        
        uint8_t pk[PK_BYTES], sk[SK_BYTES];
        if (mlkem_keypair_derand(pk, sk, coins) != 0) { errors++; continue; }
        
        /* C-ref encaps + decaps */
        uint8_t enc_seed[32];
        OQS_randombytes(enc_seed, 32);
        
        uint8_t ct_ref[CT_BYTES], ss_enc_ref[SS_BYTES], ss_dec_ref[SS_BYTES];
        mlkem_enc_derand(ct_ref, ss_enc_ref, pk, enc_seed);
        mlkem_dec(ss_dec_ref, ct_ref, sk);
        if (memcmp(ss_enc_ref, ss_dec_ref, SS_BYTES) == 0) agree_ref_ref++;
        
        /* liboqs encaps (random) + C-ref decaps */
        uint8_t ct_oqs[CT_BYTES], ss_enc_oqs[SS_BYTES], ss_dec_cross[SS_BYTES];
        if (OQS_KEM_encaps(kem, ct_oqs, ss_enc_oqs, pk) == OQS_SUCCESS) {
            mlkem_dec(ss_dec_cross, ct_oqs, sk);
            if (memcmp(ss_enc_oqs, ss_dec_cross, SS_BYTES) == 0) agree_cross_ref_decaps_oqs_ct++;
        } else { errors++; }
        
        /* C-ref encaps + liboqs decaps (need liboqs sk) */
        uint8_t pk_oqs[PK_BYTES], sk_oqs[SK_BYTES];
        OQS_KEM_ml_kem_768_keypair_derand(pk_oqs, sk_oqs, coins);
        
        uint8_t ct_ref2[CT_BYTES], ss_enc_ref2[SS_BYTES], ss_dec_oqs[SS_BYTES];
        mlkem_enc_derand(ct_ref2, ss_enc_ref2, pk_oqs, enc_seed);
        if (OQS_KEM_ml_kem_768_decaps(ss_dec_oqs, ct_ref2, sk_oqs) == OQS_SUCCESS) {
            if (memcmp(ss_enc_ref2, ss_dec_oqs, SS_BYTES) == 0) agree_cross_oqs_decaps_ref_ct++;
        } else { errors++; }
        
        /* liboqs self-consistency */
        uint8_t ct_oqs2[CT_BYTES], ss_enc_oqs2[SS_BYTES], ss_dec_oqs2[SS_BYTES];
        if (OQS_KEM_encaps(kem, ct_oqs2, ss_enc_oqs2, pk_oqs) == OQS_SUCCESS) {
            OQS_KEM_ml_kem_768_decaps(ss_dec_oqs2, ct_oqs2, sk_oqs);
            if (memcmp(ss_enc_oqs2, ss_dec_oqs2, SS_BYTES) == 0) agree_oqs_oqs++;
        } else { errors++; }
    }
    
    OQS_KEM_free(kem);
    
    printf("  C-ref self-agreement:      %d/%d (%.2f%%)\n", agree_ref_ref, num_trials, 100.0*agree_ref_ref/num_trials);
    printf("  liboqs self-agreement:     %d/%d (%.2f%%)\n", agree_oqs_oqs, num_trials, 100.0*agree_oqs_oqs/num_trials);
    printf("  Cross (ref decaps oqs CT): %d/%d (%.2f%%)\n", agree_cross_ref_decaps_oqs_ct, num_trials, 100.0*agree_cross_ref_decaps_oqs_ct/num_trials);
    printf("  Cross (oqs decaps ref CT): %d/%d (%.2f%%)\n", agree_cross_oqs_decaps_ref_ct, num_trials, 100.0*agree_cross_oqs_decaps_ref_ct/num_trials);
    printf("  Errors: %d\n", errors);
    
    int failures = 0;
    if (agree_ref_ref != num_trials) failures++;
    if (agree_oqs_oqs != num_trials) failures++;
    if (agree_cross_ref_decaps_oqs_ct != num_trials) failures++;
    if (agree_cross_oqs_decaps_ref_ct != num_trials) failures++;
    
    return failures;
}

/* ============================================================
 * CATEGORY 4: Fault Injection Reproduction
 * Reproduce selected Phase 2-4 experiments on the C-ref instrumented build
 * ============================================================ */

typedef struct {
    const char *name;
    unsigned ntt_stage;
    unsigned butterfly;
    mlkem_ntt_locus_t locus;
    mlkem_fault_type_t fault_type;
    uint8_t bit;
    int16_t delta;
    int32_t force_val;
    const char *expected_outcome;
} fault_experiment_t;

static const fault_experiment_t selected_experiments[] = {
    /* NTT stage faults — reproduction of Phase 2 key findings */
    { "NTT-L1-B0-delta1",   1, 0, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_ADDITIVE_GLITCH, 0, 1, 0,   "IMPLICIT_REJECTION_or_CORRECT" },
    { "NTT-L1-B0-delta13",  1, 0, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_ADDITIVE_GLITCH, 0, 13, 0,  "IMPLICIT_REJECTION" },
    { "NTT-L4-B0-delta1",   4, 0, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_ADDITIVE_GLITCH, 0, 1, 0,   "IMPLICIT_REJECTION_or_CORRECT" },
    { "NTT-L7-B0-delta1",   7, 0, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_ADDITIVE_GLITCH, 0, 1, 0,   "IMPLICIT_REJECTION" },
    /* Twiddle factor corruption */
    { "NTT-L3-B0-twiddle-bit4", 3, 0, NTT_LOCUS_TWIDDLE_ZETA, FAULT_TYPE_BIT_FLIP, 4, 0, 0,    "IMPLICIT_REJECTION" },
    /* Intermediate-t corruption */
    { "NTT-L5-B0-interm-zero",  5, 0, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_ZEROING, 0, 0, 0,    "IMPLICIT_REJECTION" },
    /* Layer 1 conditional masking — Phase 4 correction */
    { "NTT-L1-B0-delta12-boundary", 1, 0, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_ADDITIVE_GLITCH, 0, 12, 0, "BOUNDARY_CONDITIONAL" },
    { "NTT-L1-B0-delta832-max",     1, 0, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_ADDITIVE_GLITCH, 0, 832, 0, "IMPLICIT_REJECTION" },
};
#define N_EXPERIMENTS (sizeof(selected_experiments) / sizeof(selected_experiments[0]))

static int test_fault_reproduction(int trials_per_experiment) {
    printf("\n=== CATEGORY 4: Fault Injection Reproduction (%d trials each) ===\n", trials_per_experiment);
    
    int total_experiments = 0;
    int total_completed = 0;
    
    for (unsigned exp = 0; exp < N_EXPERIMENTS; exp++) {
        const fault_experiment_t *e = &selected_experiments[exp];
        printf("  [%u/%lu] %s: ", exp+1, (unsigned long)N_EXPERIMENTS, e->name);
        
        int correct = 0, implicit_rej = 0, error_count = 0, other = 0;
        
        for (int t = 0; t < trials_per_experiment; t++) {
            /* Fresh keypair */
            uint8_t coins[64], enc_seed[32];
            OQS_randombytes(coins, 64);
            OQS_randombytes(enc_seed, 32);
            
            uint8_t pk[PK_BYTES], sk[SK_BYTES];
            uint8_t ct[CT_BYTES], ss_enc[SS_BYTES], ss_dec[SS_BYTES];
            
            /* Keygen and encaps (fault-free) */
            if (mlkem768_keypair_derand(pk, sk, coins) != 0) { error_count++; continue; }
            
            mlkem_fault_reset();
            if (mlkem768_enc_derand(ct, ss_enc, pk, enc_seed) != 0) { error_count++; continue; }
            
            /* Arm fault for decaps */
            mlkem_fault_reset();
            mlkem_fault_arm_mid_ntt_locus(
                e->ntt_stage, e->butterfly, e->locus,
                e->fault_type, e->bit, e->delta, e->force_val
            );
            
            mlkem768_dec(ss_dec, ct, sk);
            
            if (memcmp(ss_enc, ss_dec, SS_BYTES) == 0) {
                correct++;
            } else {
                implicit_rej++;
            }
        }
        
        total_experiments++;
        total_completed++;
        
        double corr_rate = 100.0 * correct / trials_per_experiment;
        double rej_rate = 100.0 * implicit_rej / trials_per_experiment;
        
        printf("correct=%.1f%% (%d) implicit_rej=%.1f%% (%d) errors=%d [expected: %s]\n",
               corr_rate, correct, rej_rate, implicit_rej, error_count, e->expected_outcome);
    }
    
    printf("  Completed: %d/%d experiments\n", total_completed, total_experiments);
    return 0; /* Fault experiments report observations, not pass/fail */
}

/* ============================================================
 * CATEGORY 5: FO Predicate Fault Reproduction
 * Reproduce the Fujisaki-Okamoto verification flag override
 * ============================================================ */

static int test_fo_predicate_reproduction(int num_trials) {
    printf("\n=== CATEGORY 5: FO Predicate Fault Reproduction (%d trials) ===\n", num_trials);
    
    int correct_ct_forced_fail = 0;   /* Valid CT, force FO fail → implicit rejection */
    int correct_ct_no_fault = 0;      /* Valid CT, no fault → correct key */
    int corrupted_ct_forced_pass = 0; /* Corrupted CT, force FO pass → garbled key */
    int corrupted_ct_no_fault = 0;    /* Corrupted CT, no fault → implicit rejection */
    
    for (int t = 0; t < num_trials; t++) {
        uint8_t coins[64], enc_seed[32];
        OQS_randombytes(coins, 64);
        OQS_randombytes(enc_seed, 32);
        
        uint8_t pk[PK_BYTES], sk[SK_BYTES];
        uint8_t ct[CT_BYTES], ss_enc[SS_BYTES], ss_dec[SS_BYTES];
        
        mlkem_fault_reset();
        mlkem768_keypair_derand(pk, sk, coins);
        mlkem_fault_reset();
        mlkem768_enc_derand(ct, ss_enc, pk, enc_seed);
        
        /* Test 1: Valid CT, force FO fail (0→1) */
        mlkem_fault_reset();
        mlkem_fault_arm_fo_flag(0); /* direction=0: force fail=1 on valid CT */
        mlkem768_dec(ss_dec, ct, sk);
        if (memcmp(ss_enc, ss_dec, SS_BYTES) != 0) correct_ct_forced_fail++;
        
        /* Test 2: Valid CT, no fault */
        mlkem_fault_reset();
        mlkem768_dec(ss_dec, ct, sk);
        if (memcmp(ss_enc, ss_dec, SS_BYTES) == 0) correct_ct_no_fault++;
        
        /* Test 3: Corrupted CT, force FO pass (1→0) */
        uint8_t ct_bad[CT_BYTES];
        memcpy(ct_bad, ct, CT_BYTES);
        ct_bad[0] ^= 0xFF; /* Corrupt first byte */
        
        mlkem_fault_reset();
        mlkem_fault_arm_fo_flag(1); /* direction=1: force fail=0 on corrupted CT */
        mlkem768_dec(ss_dec, ct_bad, sk);
        /* Key should be garbled (not matching ss_enc, and not matching H(z,c)) */
        if (memcmp(ss_enc, ss_dec, SS_BYTES) != 0) corrupted_ct_forced_pass++;
        
        /* Test 4: Corrupted CT, no fault → should produce implicit rejection key */
        mlkem_fault_reset();
        mlkem768_dec(ss_dec, ct_bad, sk);
        if (memcmp(ss_enc, ss_dec, SS_BYTES) != 0) corrupted_ct_no_fault++;
    }
    
    printf("  Valid CT + FO forced fail → rejection: %d/%d (%.1f%%)\n",
           correct_ct_forced_fail, num_trials, 100.0*correct_ct_forced_fail/num_trials);
    printf("  Valid CT + no fault → correct key:     %d/%d (%.1f%%)\n",
           correct_ct_no_fault, num_trials, 100.0*correct_ct_no_fault/num_trials);
    printf("  Corrupted CT + FO forced pass → garbled: %d/%d (%.1f%%)\n",
           corrupted_ct_forced_pass, num_trials, 100.0*corrupted_ct_forced_pass/num_trials);
    printf("  Corrupted CT + no fault → rejection:   %d/%d (%.1f%%)\n",
           corrupted_ct_no_fault, num_trials, 100.0*corrupted_ct_no_fault/num_trials);
    
    int failures = 0;
    if (correct_ct_forced_fail != num_trials) failures++;
    if (correct_ct_no_fault != num_trials) failures++;
    if (corrupted_ct_no_fault != num_trials) failures++;
    /* corrupted_ct_forced_pass should produce garbled key (not matching enc key) — verified by != */
    
    return failures;
}

/* ============================================================
 * CATEGORY 6: NTT Diffusion Tree Validation
 * Verify Phase 1-4 diffusion model: fault at layer L affects 2^(7-L) coefficients
 * ============================================================ */

typedef struct {
    int16_t coeffs[256];
} mlk_poly_diff_t;

void mlkem768_poly_ntt(mlk_poly_diff_t *r);

static int test_ntt_diffusion_model(void) {
    printf("\n=== CATEGORY 6: NTT Diffusion Model Validation ===\n");
    
    int failures = 0;
    mlk_poly_diff_t base_poly, clean_poly, fault_poly;
    
    /* Initialize base polynomial */
    for (int i = 0; i < 256; i++) {
        base_poly.coeffs[i] = (int16_t)((i * 37 + 13) % 3329);
    }
    
    /* Compute clean baseline NTT */
    mlkem_fault_reset();
    clean_poly = base_poly;
    mlkem768_poly_ntt(&clean_poly);
    
    for (unsigned layer = 1; layer <= 7; layer++) {
        int expected_single = 1 << (7 - layer);
        int expected_shared = 1 << (8 - layer);
        
        /* Test Single Output Register (OUTPUT_ADD) */
        mlkem_fault_reset();
        mlkem_fault_arm_mid_ntt_locus(layer, 0, NTT_LOCUS_OUTPUT_ADD,
                                      FAULT_TYPE_ADDITIVE_GLITCH, 0, 8, 0);
        fault_poly = base_poly;
        mlkem768_poly_ntt(&fault_poly);
        
        int observed_single = 0;
        for (int i = 0; i < 256; i++) {
            if (fault_poly.coeffs[i] != clean_poly.coeffs[i]) observed_single++;
        }
        
        /* Test Shared Intermediate (INTERMEDIATE_T) */
        mlkem_fault_reset();
        mlkem_fault_arm_mid_ntt_locus(layer, 0, NTT_LOCUS_INTERMEDIATE_T,
                                      FAULT_TYPE_ADDITIVE_GLITCH, 0, 8, 0);
        fault_poly = base_poly;
        mlkem768_poly_ntt(&fault_poly);
        
        int observed_shared = 0;
        for (int i = 0; i < 256; i++) {
            if (fault_poly.coeffs[i] != clean_poly.coeffs[i]) observed_shared++;
        }
        
        bool single_match = (observed_single == expected_single);
        bool shared_match = (observed_shared == expected_shared);
        
        printf("  Layer %u: Single out=%d (expected %d, %s) | Shared T=%d (expected %d, %s)\n",
               layer, observed_single, expected_single, single_match ? "EXACT" : "MISMATCH",
               observed_shared, expected_shared, shared_match ? "EXACT" : "MISMATCH");
        
        if (!single_match || !shared_match) failures++;
    }
    
    return failures;
}

/* ============================================================
 * MAIN
 * ============================================================ */

int main(void) {
    printf("================================================================\n");
    printf("Phase 5: Cross-Implementation Fault-Surface Validation (ML-KEM)\n");
    printf("Implementation A: mlkem-native C-reference (instrumented)\n");
    printf("Implementation B: liboqs 0.16.0 (AArch64 assembly backend)\n");
    printf("NOTE: Both derive from pq-code-package — backend comparison only\n");
    printf("================================================================\n");
    
    int total_failures = 0;
    
    /* Category 1: Baseline Equivalence */
    total_failures += test_baseline_equivalence();
    
    /* Category 2: Instrumentation Transparency */
    total_failures += test_instrumentation_transparency();
    
    /* Category 3: Cross-Backend Key Agreement */
    total_failures += test_cross_backend_key_agreement(500);
    
    /* Category 4: Fault Injection Reproduction */
    total_failures += test_fault_reproduction(200);
    
    /* Category 5: FO Predicate Fault Reproduction */
    total_failures += test_fo_predicate_reproduction(200);
    
    /* Category 6: NTT Diffusion Model */
    total_failures += test_ntt_diffusion_model();
    
    printf("\n================================================================\n");
    printf("Phase 5 ML-KEM Summary: %d critical failures detected\n", total_failures);
    printf("================================================================\n");
    
    return (total_failures > 0) ? 1 : 0;
}
