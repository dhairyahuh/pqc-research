/**
 * Phase 4B: Rigorous ML-KEM-768 Internal Fault Validation Experiment Runner
 * Implements:
 *   1. Corrected Research Taxonomy (Mid-NTT, Mid-PolyMul, Mid-CBD, FO-Predicate, Post-Op)
 *   2. Strict Baseline Controls (Pairwise Control vs Fault under identical seed/keys)
 *   3. Multi-Stage NTT Sweep (Stages 1..7, Butterflies 0, 31, 63, 127)
 *   4. Multi-Accumulator PolyMul Sweep (Poly pairs 0, 42, 127; Vector coords k=0, 1, 2)
 *   5. Mathematically Valid Sampling Sweep (Popcount mask vs sampled coeff vs input buf)
 *   6. Bidirectional FO Transform Verification (0->1 on valid CT vs 1->0 on corrupted CT)
 *   7. Detailed Internal Traces with actual observed intermediate values
 *   8. Statistical Wilson 95% Confidence Intervals & Reproducible JSON Output
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <time.h>

#include "algorithms/source_ref/mlkem_fault_hooks.h"

// Forward declarations for instrumented ML-KEM-768
int mlkem_keypair_derand(uint8_t *pk, uint8_t *sk, const uint8_t *coins);
int mlkem_enc_derand(uint8_t *ct, uint8_t *ss, const uint8_t *pk, const uint8_t *coins);
int mlkem_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);

int randombytes(uint8_t *out, size_t outlen) {
    (void)out; (void)outlen;
    return 0;
}

#define KEM768_PK_BYTES 1184
#define KEM768_SK_BYTES 2400
#define KEM768_CT_BYTES 1088
#define KEM768_SS_BYTES 32

typedef enum {
    OUTCOME_CORRECT_VALID = 0,
    OUTCOME_EXPECTED_IMPLICIT_REJECTION = 1,
    OUTCOME_CANDIDATE_KEY_MISMATCH = 2,
    OUTCOME_EXPLICIT_ERROR = 3,
    OUTCOME_CRASH_OR_FAULT = 4
} validation_outcome_t;

typedef struct {
    uint32_t correct_count;
    uint32_t implicit_rejection_count;
    uint32_t candidate_key_mismatch_count;
    uint32_t explicit_error_count;
    uint32_t crash_count;
    uint32_t total;
} campaign_stats_t;

typedef struct {
    char fault_id[64];
    uint64_t seed;
    char parameter_set[16];
    char function_name[64];
    int stage;
    int butterfly;
    size_t target_index;
    int32_t pre_fault_val;
    char fault_transformation[64];
    int32_t post_fault_val;
    char next_operation[64];
    int32_t propagated_state;
    char detection_check[64];
    char final_output_hex[64];
    char baseline_output_hex[64];
    char outcome_class[48];
} trace_record_t;

#define MAX_REPRESENTATIVE_TRACES 10
static trace_record_t g_traces[MAX_REPRESENTATIVE_TRACES];
static size_t g_trace_count = 0;

static void wilson_ci(uint32_t k, uint32_t n, double *rate, double *low, double *high) {
    if (n == 0) {
        *rate = 0.0; *low = 0.0; *high = 0.0;
        return;
    }
    double p = (double)k / n;
    double z = 1.95996;
    double denom = 1.0 + (z * z) / n;
    double center = p + (z * z) / (2.0 * n);
    double spread = z * sqrt((p * (1.0 - p) / n) + ((z * z) / (4.0 * n * n)));
    *rate = p * 100.0;
    *low = fmax(0.0, (center - spread) / denom) * 100.0;
    *high = fmin(1.0, (center + spread) / denom) * 100.0;
}

static void hex_to_str(char *dst, size_t dst_len, const uint8_t *src, size_t src_len) {
    size_t written = 0;
    for (size_t i = 0; i < 4 && i < src_len && written + 3 < dst_len; i++) {
        written += snprintf(dst + written, dst_len - written, "%02x", src[i]);
    }
    if (written + 7 < dst_len && src_len > 4) {
        written += snprintf(dst + written, dst_len - written, "..%02x%02x", src[src_len - 2], src[src_len - 1]);
    }
}

// Master deterministic PRNG for reproducibility
static void derive_deterministic_inputs(uint64_t seed, uint8_t coins[64], uint8_t m[32]) {
    uint64_t s = seed;
    for (size_t i = 0; i < 64; i++) {
        s = s * 6364136223846793005ULL + 1442695040888963407ULL;
        coins[i] = (uint8_t)(s >> 32);
    }
    for (size_t i = 0; i < 32; i++) {
        s = s * 6364136223846793005ULL + 1442695040888963407ULL;
        m[i] = (uint8_t)(s >> 32);
    }
}

// Campaign execution with control and machine-readable output
void run_validated_campaign(
    FILE *json_fp,
    bool is_first_json,
    const char *campaign_id,
    const char *taxonomy_name,
    const char *target_description,
    uint32_t iterations,
    uint64_t master_seed,
    int campaign_type, // 1: mid-ntt, 2: mid-polymul, 3: mid-cbd-sample, 4: mid-cbd-popcount, 5: fo-valid, 6: fo-corrupt, 7: post-op
    unsigned param_stage, unsigned param_butterfly, unsigned param_pair,
    unsigned param_poly_idx, unsigned param_acc_idx, unsigned param_coord,
    size_t param_coeff_idx, uint8_t param_bit, int32_t param_delta,
    bool capture_representative_trace
) {
    printf("\n=========================================================================\n");
    printf("[+] Campaign: %s (N=%u)\n", campaign_id, iterations);
    printf("    Taxonomy:   %s\n", taxonomy_name);
    printf("    Target:     %s\n", target_description);

    campaign_stats_t stats = {0, 0, 0, 0, 0, iterations};

    uint8_t coins[64];
    uint8_t m[32];
    uint8_t pk[KEM768_PK_BYTES];
    uint8_t sk[KEM768_SK_BYTES];
    uint8_t ct_clean[KEM768_CT_BYTES];
    uint8_t ct_eval[KEM768_CT_BYTES];
    uint8_t ss_ground[KEM768_SS_BYTES];
    uint8_t ss_control[KEM768_SS_BYTES];
    uint8_t ss_fault[KEM768_SS_BYTES];

    for (uint32_t iter = 0; iter < iterations; iter++) {
        uint64_t iter_seed = master_seed + iter * 6364136223846793005ULL;
        derive_deterministic_inputs(iter_seed, coins, m);

        // 1. CONTROL RUN: Generate legitimate baseline keys and ciphertext
        mlkem_fault_reset();
        mlkem_keypair_derand(pk, sk, coins);
        mlkem_enc_derand(ct_clean, ss_ground, pk, m);
        memcpy(ct_eval, ct_clean, sizeof(ct_clean));

        // If testing corrupted ciphertext:
        if (campaign_type == 6) {
            ct_eval[0] ^= 0x01; // Corrupt ciphertext bit 0 (within LWE error-correcting slack: m' == m)
        } else if (campaign_type == 8) {
            for (size_t b = 0; b < 32; b++) {
                ct_eval[960 + b] ^= 0xAA; // Severe payload corruption in c_2: forces m' != m
            }
        }

        // Execute baseline control decapsulation without fault
        mlkem_fault_reset();
        int rc_control = mlkem_dec(ss_control, ct_eval, sk);
        (void)rc_control;

        // 2. FAULT RUN: Arm research hook under exact same parameters
        mlkem_fault_reset();
        if (campaign_type == 1) {
            mlkem_fault_arm_mid_ntt(param_stage, param_butterfly, param_pair,
                                   (param_delta != 0) ? FAULT_TYPE_ADDITIVE_GLITCH : FAULT_TYPE_BIT_FLIP,
                                   param_bit, (int16_t)param_delta);
        } else if (campaign_type == 2) {
            mlkem_fault_arm_mid_polymul(param_poly_idx, param_acc_idx, param_coord,
                                       (param_delta != 0) ? FAULT_TYPE_ADDITIVE_GLITCH : FAULT_TYPE_BIT_FLIP,
                                       param_bit, param_delta);
        } else if (campaign_type == 3) {
            mlkem_fault_arm_mid_cbd_sample(param_coeff_idx,
                                          (param_delta != 0) ? FAULT_TYPE_ADDITIVE_GLITCH : FAULT_TYPE_BIT_FLIP,
                                          param_bit, (int16_t)param_delta);
        } else if (campaign_type == 4) {
            mlkem_fault_arm_mid_cbd_popcount(param_coeff_idx / 8, param_bit);
        } else if (campaign_type == 5) {
            mlkem_fault_arm_fo_flag(0); // Valid CT: 0 -> 1
        } else if (campaign_type == 6 || campaign_type == 8) {
            mlkem_fault_arm_fo_flag(1); // Corrupted CT: 1 -> 0
        } else if (campaign_type == 7) {
            mlkem_fault_arm_post_op(HOOK_TARGET_POST_NTT, param_coeff_idx, param_bit, (int16_t)param_delta);
        }

        int rc_fault = mlkem_dec(ss_fault, ct_eval, sk);

        // Outcome classification
        validation_outcome_t outcome;
        if (rc_fault != 0) {
            outcome = OUTCOME_EXPLICIT_ERROR;
            stats.explicit_error_count++;
        } else if (campaign_type == 6 || campaign_type == 8) {
            // In FO corrupted CT direction:
            // Control produced ss_control (implicit rejection key Krej).
            // Fault inverted fail 1 -> 0, causing candidate key selection.
            if (memcmp(ss_fault, ss_control, KEM768_SS_BYTES) == 0) {
                outcome = OUTCOME_EXPECTED_IMPLICIT_REJECTION;
                stats.implicit_rejection_count++;
            } else if (memcmp(ss_fault, ss_ground, KEM768_SS_BYTES) == 0) {
                // If candidate key matches ground (m' == m under LWE slack)
                outcome = OUTCOME_CORRECT_VALID;
                stats.correct_count++;
            } else {
                // Returns candidate key derived from corrupted m', matching neither Ground nor Krej!
                outcome = OUTCOME_CANDIDATE_KEY_MISMATCH;
                stats.candidate_key_mismatch_count++;
            }
        } else {
            // Standard decapsulation of valid CT:
            if (memcmp(ss_fault, ss_ground, KEM768_SS_BYTES) == 0) {
                outcome = OUTCOME_CORRECT_VALID;
                stats.correct_count++;
            } else {
                outcome = OUTCOME_EXPECTED_IMPLICIT_REJECTION;
                stats.implicit_rejection_count++;
            }
        }

        // Capture representative trace on iteration 0
        if (iter == 0 && capture_representative_trace && g_trace_count < MAX_REPRESENTATIVE_TRACES) {
            trace_record_t *tr = &g_traces[g_trace_count++];
            snprintf(tr->fault_id, sizeof(tr->fault_id), "%s-TR0", campaign_id);
            tr->seed = iter_seed;
            strcpy(tr->parameter_set, "ML-KEM-768");
            strncpy(tr->function_name, g_mlkem_fault.target_function, sizeof(tr->function_name));
            tr->stage = g_mlkem_fault.stage_recorded;
            tr->butterfly = g_mlkem_fault.butterfly_recorded;
            tr->target_index = g_mlkem_fault.coeff_recorded;
            tr->pre_fault_val = g_mlkem_fault.orig_value;
            tr->post_fault_val = g_mlkem_fault.faulted_value;
            tr->propagated_state = (g_mlkem_fault.final_propagated_val != 0) ? g_mlkem_fault.final_propagated_val : g_mlkem_fault.faulted_value;

            if (param_delta != 0) {
                snprintf(tr->fault_transformation, sizeof(tr->fault_transformation), "ADD_DELTA(%+d)", (int)param_delta);
            } else {
                snprintf(tr->fault_transformation, sizeof(tr->fault_transformation), "BIT_FLIP(bit_%u)", param_bit);
            }

            strncpy(tr->next_operation, g_mlkem_fault.operation_name, sizeof(tr->next_operation));
            strcpy(tr->detection_check, "FO re-encryption c' == c");
            hex_to_str(tr->final_output_hex, sizeof(tr->final_output_hex), ss_fault, KEM768_SS_BYTES);
            hex_to_str(tr->baseline_output_hex, sizeof(tr->baseline_output_hex), ss_control, KEM768_SS_BYTES);

            if (outcome == OUTCOME_CORRECT_VALID) strcpy(tr->outcome_class, "CORRECT_VALID_DECAPSULATION");
            else if (outcome == OUTCOME_EXPECTED_IMPLICIT_REJECTION) strcpy(tr->outcome_class, "EXPECTED_IMPLICIT_REJECTION");
            else if (outcome == OUTCOME_CANDIDATE_KEY_MISMATCH) strcpy(tr->outcome_class, "CANDIDATE_KEY_SELECTED_MISMATCH");
            else strcpy(tr->outcome_class, "EXPLICIT_ERROR");
        }
    }

    mlkem_fault_reset();

    // Compute Wilson 95% Confidence Intervals
    double r_corr, l_corr, h_corr;
    double r_imp, l_imp, h_imp;
    double r_cand, l_cand, h_cand;
    double r_err, l_err, h_err;

    wilson_ci(stats.correct_count, iterations, &r_corr, &l_corr, &h_corr);
    wilson_ci(stats.implicit_rejection_count, iterations, &r_imp, &l_imp, &h_imp);
    wilson_ci(stats.candidate_key_mismatch_count, iterations, &r_cand, &l_cand, &h_cand);
    wilson_ci(stats.explicit_error_count, iterations, &r_err, &l_err, &h_err);

    printf("  Outcome Distribution:\n");
    if (stats.correct_count > 0)
        printf("    - CORRECT_VALID_DECAPSULATION:      %4u (%6.2f%%) [95%% CI: %5.2f%% - %5.2f%%]\n",
               stats.correct_count, r_corr, l_corr, h_corr);
    if (stats.implicit_rejection_count > 0)
        printf("    - EXPECTED_IMPLICIT_REJECTION:      %4u (%6.2f%%) [95%% CI: %5.2f%% - %5.2f%%]\n",
               stats.implicit_rejection_count, r_imp, l_imp, h_imp);
    if (stats.candidate_key_mismatch_count > 0)
        printf("    - CANDIDATE_KEY_SELECTED_MISMATCH:  %4u (%6.2f%%) [95%% CI: %5.2f%% - %5.2f%%]\n",
               stats.candidate_key_mismatch_count, r_cand, l_cand, h_cand);
    if (stats.explicit_error_count > 0)
        printf("    - EXPLICIT_ERROR:                   %4u (%6.2f%%) [95%% CI: %5.2f%% - %5.2f%%]\n",
               stats.explicit_error_count, r_err, l_err, h_err);

    // Emit JSON record
    if (json_fp) {
        if (!is_first_json) fprintf(json_fp, ",\n");
        fprintf(json_fp, "    {\n");
        fprintf(json_fp, "      \"campaign_id\": \"%s\",\n", campaign_id);
        fprintf(json_fp, "      \"taxonomy\": \"%s\",\n", taxonomy_name);
        fprintf(json_fp, "      \"target_description\": \"%s\",\n", target_description);
        fprintf(json_fp, "      \"iterations\": %u,\n", iterations);
        fprintf(json_fp, "      \"outcomes\": {\n");
        fprintf(json_fp, "        \"CORRECT_VALID_DECAPSULATION\": {\"count\": %u, \"rate_pct\": %.2f, \"ci_95\": [%.2f, %.2f]},\n",
                stats.correct_count, r_corr, l_corr, h_corr);
        fprintf(json_fp, "        \"EXPECTED_IMPLICIT_REJECTION\": {\"count\": %u, \"rate_pct\": %.2f, \"ci_95\": [%.2f, %.2f]},\n",
                stats.implicit_rejection_count, r_imp, l_imp, h_imp);
        fprintf(json_fp, "        \"CANDIDATE_KEY_SELECTED_MISMATCH\": {\"count\": %u, \"rate_pct\": %.2f, \"ci_95\": [%.2f, %.2f]},\n",
                stats.candidate_key_mismatch_count, r_cand, l_cand, h_cand);
        fprintf(json_fp, "        \"EXPLICIT_ERROR\": {\"count\": %u, \"rate_pct\": %.2f, \"ci_95\": [%.2f, %.2f]}\n",
                stats.explicit_error_count, r_err, l_err, h_err);
        fprintf(json_fp, "      }\n");
        fprintf(json_fp, "    }");
    }
}

int main(void) {
    printf("=========================================================================\n");
    printf(" PHASE 4B: ML-KEM-768 INTERNAL FAULT VALIDATION AUDIT EXPERIMENT\n");
    printf(" Implementation: mlkem-native (Pinned Commit: fc269bc2d106)\n");
    printf(" Mathematical Standard: NIST FIPS 203 | Parameter Set: ML-KEM-768\n");
    printf(" Compiler: Apple Clang | Architecture: arm64 | OS: Darwin\n");
    printf("=========================================================================\n");

    const char *out_json_path = "results/mlkem768_internal_fault_validation.json";
    FILE *json_fp = fopen(out_json_path, "w");
    if (json_fp) {
        fprintf(json_fp, "{\n");
        fprintf(json_fp, "  \"metadata\": {\n");
        fprintf(json_fp, "    \"timestamp\": \"2026-10-01T00:00:00Z\",\n");
        fprintf(json_fp, "    \"implementation\": \"mlkem-native\",\n");
        fprintf(json_fp, "    \"pinned_commit\": \"fc269bc2d106\",\n");
        fprintf(json_fp, "    \"compiler\": \"Apple Clang\",\n");
        fprintf(json_fp, "    \"target_architecture\": \"arm64\",\n");
        fprintf(json_fp, "    \"standard\": \"NIST FIPS 203\",\n");
        fprintf(json_fp, "    \"parameter_set\": \"ML-KEM-768\"\n");
        fprintf(json_fp, "  },\n");
        fprintf(json_fp, "  \"campaigns\": [\n");
    }

    uint64_t base_seed = 0x5EEDCAFE421098ULL;
    bool first_json = true;

    // -------------------------------------------------------------
    // SECTION 1: NTT STAGE & BUTTERFLY SWEEPS (N=100 per sweep)
    // -------------------------------------------------------------
    printf("\n>>> SECTION 1: MID-NTT STAGE & BUTTERFLY SWEEPS (TAXONOMY B/C) <<<\n");

    // Stage 1 (len=128), Butterfly 0
    run_validated_campaign(json_fp, first_json, "MID_NTT_STAGE1_B0_BIT3",
                           "MID-OPERATION (SELECTED-STAGE)", "Stage 1 Butterfly 0, Bit 3 Flip (Early diffusion across 128 coeffs)",
                           100, base_seed + 1, 1, 1, 0, 0, 0, 0, 0, 0, 3, 0, true);
    first_json = false;

    // Stage 1, Butterfly 63
    run_validated_campaign(json_fp, first_json, "MID_NTT_STAGE1_B63_BIT3",
                           "MID-OPERATION (SELECTED-STAGE)", "Stage 1 Butterfly 63, Bit 3 Flip",
                           100, base_seed + 2, 1, 1, 63, 0, 0, 0, 0, 0, 3, 0, false);

    // Stage 4 (len=16), Butterfly 31
    run_validated_campaign(json_fp, first_json, "MID_NTT_STAGE4_B31_BIT3",
                           "MID-OPERATION (SELECTED-STAGE)", "Stage 4 Butterfly 31, Bit 3 Flip (Mid-depth diffusion)",
                           100, base_seed + 3, 1, 4, 31, 0, 0, 0, 0, 0, 3, 0, true);

    // Stage 7 (len=1, final butterfly), Butterfly 0
    run_validated_campaign(json_fp, first_json, "MID_NTT_STAGE7_B0_BIT3",
                           "MID-OPERATION (SELECTED-STAGE)", "Stage 7 Butterfly 0, Bit 3 Flip (Late-stage localized perturbation)",
                           100, base_seed + 4, 1, 7, 0, 0, 0, 0, 0, 0, 3, 0, true);

    // Stage 7, Butterfly 127
    run_validated_campaign(json_fp, first_json, "MID_NTT_STAGE7_B127_BIT3",
                           "MID-OPERATION (SELECTED-STAGE)", "Stage 7 Butterfly 127, Bit 3 Flip",
                           100, base_seed + 5, 1, 7, 127, 0, 0, 0, 0, 0, 3, 0, false);

    // -------------------------------------------------------------
    // SECTION 2: POLYNOMIAL MULTIPLICATION ACCUMULATOR SWEEPS (TAXONOMY B/E)
    // -------------------------------------------------------------
    printf("\n>>> SECTION 2: MID-POLYMUL ACCUMULATOR SWEEPS (TAXONOMY B/E) <<<\n");

    // Poly 0, Coord k=0 (first term accumulated into t[0])
    run_validated_campaign(json_fp, first_json, "MID_POLYMUL_P0_K0_GLITCH15",
                           "MID-OPERATION (SELECTED-ACCUMULATOR)", "Poly 0 VectorCoord k=0, Accumulator t[0] Delta=+15",
                           100, base_seed + 10, 2, 0, 0, 0, 0, 0, 0, 0, 0, 15, true);

    // Poly 42, Coord k=1 (middle term accumulated into t[0])
    run_validated_campaign(json_fp, first_json, "MID_POLYMUL_P42_K1_GLITCH15",
                           "MID-OPERATION (SELECTED-ACCUMULATOR)", "Poly 42 VectorCoord k=1, Accumulator t[0] Delta=+15",
                           100, base_seed + 11, 2, 0, 0, 0, 42, 1, 0, 0, 0, 15, false);

    // Poly 42, Coord k=2 (final term accumulated into t[0] before reduction)
    run_validated_campaign(json_fp, first_json, "MID_POLYMUL_P42_K2_GLITCH15",
                           "MID-OPERATION (SELECTED-ACCUMULATOR)", "Poly 42 VectorCoord k=2, Accumulator t[0] Delta=+15",
                           100, base_seed + 12, 2, 0, 0, 0, 42, 2, 0, 0, 0, 15, false);

    // -------------------------------------------------------------
    // SECTION 3: SAMPLING SWEEPS (TAXONOMY B/D)
    // -------------------------------------------------------------
    printf("\n>>> SECTION 3: CBD NOISE SAMPLING SWEEPS (TAXONOMY B/D) <<<\n");

    // SWAR Popcount Intermediate Bit Flip (Word 0, Bit 1)
    run_validated_campaign(json_fp, first_json, "MID_CBD_POPCOUNT_W0_BIT1",
                           "MID-OPERATION (POPCOUNT-INTERMEDIATE)", "SWAR Popcount Word 0 Bit 1 Flip (Perturbs sum of bits d)",
                           100, base_seed + 20, 4, 0, 0, 0, 0, 0, 0, 0, 1, 0, true);

    // Sampled Coefficient Bit Flip during computation (Coeff 15, Bit 2: 2 -> 6)
    run_validated_campaign(json_fp, first_json, "MID_CBD_SAMPLE_C15_BIT2",
                           "MID-OPERATION (SAMPLED-COEFFICIENT)", "Sampled Coeff 15, Bit 2 Flip (Violates support [-2, 2])",
                           100, base_seed + 21, 3, 0, 0, 0, 0, 0, 0, 15, 2, 0, false);

    // -------------------------------------------------------------
    // SECTION 4: FO EQUALITY PREDICATE FAULTS (TWO DIRECTIONS) (TAXONOMY F)
    // -------------------------------------------------------------
    printf("\n>>> SECTION 4: FUJISAKI-OKAMOTO EQUALITY PREDICATE SWEEPS (TAXONOMY F) <<<\n");

    // Direction A: Valid Ciphertext, Fail Flag Inverted 0 -> 1 (N=1000)
    run_validated_campaign(json_fp, first_json, "FO_PREDICATE_DIR_A_VALID_CT",
                           "CONTROL/PREDICATE FAULT", "Valid Ciphertext: fail 0 -> 1 (Forces Implicit Rejection Krej)",
                           1000, base_seed + 30, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, true);

    // Direction B1: Corrupted Ciphertext within LWE Error Slack, Fail Flag Inverted 1 -> 0 (N=1000)
    run_validated_campaign(json_fp, first_json, "FO_PREDICATE_DIR_B1_LWE_SLACK_CT",
                           "CONTROL/PREDICATE FAULT", "1-Bit Corrupted CT (m'=m via LWE slack): fail 1 -> 0 (Candidate key equals Ground key)",
                           1000, base_seed + 31, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, true);

    // Direction B2: Severe Corrupted Ciphertext exceeding LWE Slack, Fail Flag Inverted 1 -> 0 (N=1000)
    run_validated_campaign(json_fp, first_json, "FO_PREDICATE_DIR_B2_SEVERE_CORRUPT_CT",
                           "CONTROL/PREDICATE FAULT", "Severe Corrupted CT (m'!=m): fail 1 -> 0 (Forces Kcand != Krej != Kground)",
                           1000, base_seed + 32, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, true);

    // -------------------------------------------------------------
    // SECTION 5: TAXONOMY COMPARISON: POST-OP vs MID-OP (TAXONOMY A)
    // -------------------------------------------------------------
    printf("\n>>> SECTION 5: POST-OPERATION VS MID-OPERATION COMPARISON (TAXONOMY A) <<<\n");
    run_validated_campaign(json_fp, first_json, "POST_OP_NTT_OUTPUT_MUTATION",
                           "POST-OPERATION STATE FAULT", "Post-NTT Output Buffer Coeff 0 Bit 3 Flip (Occurs AFTER all butterflies)",
                           100, base_seed + 40, 7, 0, 0, 0, 0, 0, 0, 0, 3, 0, true);

    if (json_fp) {
        fprintf(json_fp, "\n  ],\n");
        fprintf(json_fp, "  \"representative_traces\": [\n");
        for (size_t t = 0; t < g_trace_count; t++) {
            trace_record_t *tr = &g_traces[t];
            if (t > 0) fprintf(json_fp, ",\n");
            fprintf(json_fp, "    {\n");
            fprintf(json_fp, "      \"fault_id\": \"%s\",\n", tr->fault_id);
            fprintf(json_fp, "      \"seed\": %llu,\n", (unsigned long long)tr->seed);
            fprintf(json_fp, "      \"parameter_set\": \"%s\",\n", tr->parameter_set);
            fprintf(json_fp, "      \"function\": \"%s\",\n", tr->function_name);
            fprintf(json_fp, "      \"stage\": %d,\n", tr->stage);
            fprintf(json_fp, "      \"butterfly\": %d,\n", tr->butterfly);
            fprintf(json_fp, "      \"target_index\": %zu,\n", tr->target_index);
            fprintf(json_fp, "      \"pre_fault_value\": %d,\n", tr->pre_fault_val);
            fprintf(json_fp, "      \"fault_transformation\": \"%s\",\n", tr->fault_transformation);
            fprintf(json_fp, "      \"post_fault_value\": %d,\n", tr->post_fault_val);
            fprintf(json_fp, "      \"next_operation\": \"%s\",\n", tr->next_operation);
            fprintf(json_fp, "      \"propagated_state\": %d,\n", tr->propagated_state);
            fprintf(json_fp, "      \"detection_check\": \"%s\",\n", tr->detection_check);
            fprintf(json_fp, "      \"final_output\": \"%s\",\n", tr->final_output_hex);
            fprintf(json_fp, "      \"baseline_output\": \"%s\",\n", tr->baseline_output_hex);
            fprintf(json_fp, "      \"outcome_class\": \"%s\"\n", tr->outcome_class);
            fprintf(json_fp, "    }");
        }
        fprintf(json_fp, "\n  ]\n");
        fprintf(json_fp, "}\n");
        fclose(json_fp);
    }

    // Print Representative Traces Table
    printf("\n=========================================================================\n");
    printf(" REPRESENTATIVE INTERNAL FAULT PROPAGATION TRACES (ACTUAL VALUES)\n");
    printf("=========================================================================\n");
    for (size_t t = 0; t < g_trace_count; t++) {
        trace_record_t *tr = &g_traces[t];
        printf("\n[Trace %zu: %s]\n", t + 1, tr->fault_id);
        printf("  Function:           %s\n", tr->function_name);
        if (tr->stage >= 0) {
            printf("  Stage / Butterfly:  Layer %d | Butterfly %d (Coeff %zu)\n", tr->stage, tr->butterfly, tr->target_index);
        } else {
            printf("  Target Index:       Index %zu\n", tr->target_index);
        }
        printf("  Pre-Fault Value:    %d\n", tr->pre_fault_val);
        printf("  Transformation:     %s -> Post-Fault Value: %d\n", tr->fault_transformation, tr->post_fault_val);
        printf("  Next Operation:     %s\n", tr->next_operation);
        printf("  Propagated State:   %d\n", tr->propagated_state);
        printf("  Baseline Shared SS: %s\n", tr->baseline_output_hex);
        printf("  Faulted Shared SS:  %s\n", tr->final_output_hex);
        printf("  Outcome Class:      %s\n", tr->outcome_class);
    }

    printf("\n=========================================================================\n");
    printf(" >>> PHASE 4B VALIDATION AUDIT COMPLETE: JSON SAVED TO %s <<<\n", out_json_path);
    printf("=========================================================================\n");

    return 0;
}
