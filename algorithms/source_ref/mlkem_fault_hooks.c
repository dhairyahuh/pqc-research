/**
 * ML-KEM Source-Level Research Fault Injection Hooks Implementation
 * Implements mathematically verified mid-operation and post-operation hooks:
 * - Multi-locus NTT butterfly injection (inputs, twiddle, intermediate t, outputs)
 * - Layer diffusion tracking across all 7 forward NTT layers
 * - PolyMul accumulator vector coordinates and CBD sampling
 * - Fault types: bit-flip, additive delta, random replacement, zeroing, force value
 */

#include "mlkem_fault_hooks.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

mlkem_fault_config_t g_mlkem_fault = {
    .enabled = false,
    .target = HOOK_TARGET_NONE,
    .fault_type = FAULT_TYPE_BIT_FLIP,
    .target_stage = 0,
    .target_butterfly = 0,
    .target_coeff_pair = 0,
    .ntt_locus = NTT_LOCUS_DEFAULT,
    .target_poly_idx = 0,
    .target_acc_idx = 0,
    .target_coord = 0,
    .target_coeff_idx = 0,
    .target_word_idx = 0,
    .bit_to_flip = 0,
    .additive_glitch = 0,
    .forced_value = 0,
    .fo_direction = 0,
    .trigger_count = 0,
    .track_layer_diff = false,
    .has_baseline_poly = false,
    .trace_recorded = false,
    .fault_taxonomy = "NONE",
    .target_function = "",
    .stage_recorded = -1,
    .butterfly_recorded = -1,
    .coeff_recorded = 0,
    .orig_value = 0,
    .faulted_value = 0,
    .operand_a = 0,
    .operand_b = 0,
    .twiddle_zeta = 0,
    .intermediate_product = 0,
    .final_propagated_val = 0,
    .operation_name = "",
    .fault_description = ""
};

void mlkem_fault_reset(void) {
    memset(&g_mlkem_fault, 0, sizeof(g_mlkem_fault));
    g_mlkem_fault.stage_recorded = -1;
    g_mlkem_fault.butterfly_recorded = -1;
    strcpy(g_mlkem_fault.fault_taxonomy, "NONE");
}

static int32_t apply_fault(int32_t orig, mlkem_fault_type_t type, uint8_t bit, int32_t delta, int32_t forced, int32_t min_v, int32_t max_v) {
    switch (type) {
        case FAULT_TYPE_BIT_FLIP:
            return orig ^ (1u << (bit % 32));
        case FAULT_TYPE_ADDITIVE_GLITCH:
            return orig + delta;
        case FAULT_TYPE_RANDOM_REPLACEMENT: {
            uint32_t span = (uint32_t)(max_v - min_v + 1);
            if (span == 0) span = 3329;
            uint32_t r = ((uint32_t)orig * 1103515245u + 12345u) & 0x7fffffffu;
            return (int32_t)(min_v + (r % span));
        }
        case FAULT_TYPE_ZEROING:
            return 0;
        case FAULT_TYPE_FORCE_VALUE:
            return forced;
        default:
            return orig;
    }
}

void mlkem_fault_arm_mid_ntt(
    unsigned stage, unsigned butterfly, unsigned coeff_pair,
    mlkem_fault_type_t fault_type, uint8_t bit, int16_t delta
) {
    mlkem_fault_reset();
    g_mlkem_fault.enabled = true;
    g_mlkem_fault.target = HOOK_TARGET_MID_NTT_BUTTERFLY;
    g_mlkem_fault.fault_type = fault_type;
    g_mlkem_fault.target_stage = stage;
    g_mlkem_fault.target_butterfly = butterfly % 128;
    g_mlkem_fault.target_coeff_pair = (coeff_pair != 0) ? 1 : 0;
    g_mlkem_fault.ntt_locus = NTT_LOCUS_DEFAULT;
    g_mlkem_fault.bit_to_flip = bit % 16;
    g_mlkem_fault.additive_glitch = delta;
    strcpy(g_mlkem_fault.fault_taxonomy, "MID-OPERATION (SELECTED-STAGE/BUTTERFLY)");
    strcpy(g_mlkem_fault.target_function, "mlk_ntt_butterfly_block");
}

void mlkem_fault_arm_mid_ntt_locus(
    unsigned stage, unsigned butterfly, mlkem_ntt_locus_t locus,
    mlkem_fault_type_t fault_type, uint8_t bit, int16_t delta, int32_t force_val
) {
    mlkem_fault_reset();
    g_mlkem_fault.enabled = true;
    g_mlkem_fault.target = HOOK_TARGET_MID_NTT_BUTTERFLY;
    g_mlkem_fault.fault_type = fault_type;
    g_mlkem_fault.target_stage = stage;
    g_mlkem_fault.target_butterfly = butterfly % 128;
    g_mlkem_fault.ntt_locus = locus;
    g_mlkem_fault.target_coeff_pair = (locus == NTT_LOCUS_OUTPUT_SUB || locus == NTT_LOCUS_INPUT_B_PRE_MUL) ? 1 : 0;
    g_mlkem_fault.bit_to_flip = bit % 16;
    g_mlkem_fault.additive_glitch = delta;
    g_mlkem_fault.forced_value = force_val;
    strcpy(g_mlkem_fault.fault_taxonomy, "MID-OPERATION (SELECTED-STAGE/LOCUS)");
    strcpy(g_mlkem_fault.target_function, "mlk_ntt_butterfly_block");
}

void mlkem_fault_enable_diffusion_tracking(const int16_t *baseline_poly) {
    g_mlkem_fault.track_layer_diff = true;
    if (baseline_poly) {
        memcpy(g_mlkem_fault.baseline_poly, baseline_poly, sizeof(int16_t) * 256);
        g_mlkem_fault.has_baseline_poly = true;
    } else {
        g_mlkem_fault.has_baseline_poly = false;
    }
    for (int i = 0; i < 8; i++) {
        g_mlkem_fault.layer_diff_counts[i] = 0;
    }
}

int mlkem_fault_get_diffusion_count(unsigned layer) {
    if (layer >= 1 && layer <= 7) {
        return g_mlkem_fault.layer_diff_counts[layer];
    }
    return 0;
}

void mlkem_fault_arm_mid_polymul(
    unsigned poly_idx, unsigned acc_idx, unsigned coord,
    mlkem_fault_type_t fault_type, uint8_t bit, int32_t delta
) {
    mlkem_fault_reset();
    g_mlkem_fault.enabled = true;
    g_mlkem_fault.target = HOOK_TARGET_MID_POLYMUL_ACC;
    g_mlkem_fault.fault_type = fault_type;
    g_mlkem_fault.target_poly_idx = poly_idx % 128;
    g_mlkem_fault.target_acc_idx = acc_idx;
    g_mlkem_fault.target_coord = (coord != 0) ? 1 : 0;
    g_mlkem_fault.bit_to_flip = bit % 32;
    g_mlkem_fault.additive_glitch = delta;
    strcpy(g_mlkem_fault.fault_taxonomy, "MID-OPERATION (SELECTED-ACCUMULATOR)");
    strcpy(g_mlkem_fault.target_function, "mlk_polyvec_basemul_acc_montgomery_cached_c");
}

void mlkem_fault_arm_mid_cbd_sample(
    size_t coeff_idx, mlkem_fault_type_t fault_type, uint8_t bit, int16_t delta
) {
    mlkem_fault_reset();
    g_mlkem_fault.enabled = true;
    g_mlkem_fault.target = HOOK_TARGET_MID_CBD_SAMPLE;
    g_mlkem_fault.fault_type = fault_type;
    g_mlkem_fault.target_coeff_idx = coeff_idx % 256;
    g_mlkem_fault.bit_to_flip = bit % 16;
    g_mlkem_fault.additive_glitch = delta;
    strcpy(g_mlkem_fault.fault_taxonomy, "MID-OPERATION (SAMPLED-COEFFICIENT)");
    strcpy(g_mlkem_fault.target_function, "mlk_poly_cbd2");
}

void mlkem_fault_arm_mid_cbd_popcount(
    size_t word_idx, uint8_t bit
) {
    mlkem_fault_reset();
    g_mlkem_fault.enabled = true;
    g_mlkem_fault.target = HOOK_TARGET_MID_CBD_POPCOUNT;
    g_mlkem_fault.fault_type = FAULT_TYPE_BIT_FLIP;
    g_mlkem_fault.target_word_idx = word_idx % 32;
    g_mlkem_fault.bit_to_flip = bit % 32;
    strcpy(g_mlkem_fault.fault_taxonomy, "MID-OPERATION (POPCOUNT-INTERMEDIATE)");
    strcpy(g_mlkem_fault.target_function, "mlk_poly_cbd2");
}

void mlkem_fault_arm_fo_flag(int direction) {
    mlkem_fault_reset();
    g_mlkem_fault.enabled = true;
    g_mlkem_fault.target = HOOK_TARGET_FO_VERIFY_FLAG;
    g_mlkem_fault.fo_direction = direction;
    strcpy(g_mlkem_fault.fault_taxonomy, "CONTROL/PREDICATE FAULT");
    strcpy(g_mlkem_fault.target_function, "mlk_kem_dec (FO transform)");
}

void mlkem_fault_arm_post_op(
    mlkem_hook_target_t target, size_t coeff_idx, uint8_t bit, int16_t delta
) {
    mlkem_fault_reset();
    g_mlkem_fault.enabled = true;
    g_mlkem_fault.target = target;
    g_mlkem_fault.target_coeff_idx = coeff_idx % 256;
    g_mlkem_fault.bit_to_flip = bit % 16;
    g_mlkem_fault.additive_glitch = delta;
    strcpy(g_mlkem_fault.fault_taxonomy, "POST-OPERATION STATE FAULT");
}

// 1. Mid-NTT Pre-Butterfly Hook (Inputs and Twiddle)
void hook_mid_ntt_pre_butterfly(
    unsigned layer, unsigned butterfly_idx, int16_t *zeta_ptr,
    int16_t *r_j, int16_t *r_j_len, size_t idx0, size_t idx1
) {
    if (!g_mlkem_fault.enabled || g_mlkem_fault.target != HOOK_TARGET_MID_NTT_BUTTERFLY) {
        return;
    }

    if ((g_mlkem_fault.trigger_count == 0 || g_mlkem_fault.persistent) &&
        g_mlkem_fault.target_stage == layer &&
        g_mlkem_fault.target_butterfly == butterfly_idx) {

        if (g_mlkem_fault.ntt_locus == NTT_LOCUS_INPUT_B_PRE_MUL) {
            g_mlkem_fault.orig_value = *r_j_len;
            *r_j_len = (int16_t)apply_fault(*r_j_len, g_mlkem_fault.fault_type, g_mlkem_fault.bit_to_flip,
                                            g_mlkem_fault.additive_glitch, g_mlkem_fault.forced_value, -3328, 3328);
            g_mlkem_fault.faulted_value = *r_j_len;
            g_mlkem_fault.stage_recorded = (int)layer;
            g_mlkem_fault.butterfly_recorded = (int)butterfly_idx;
            g_mlkem_fault.coeff_recorded = idx1;
            g_mlkem_fault.twiddle_zeta = *zeta_ptr;
            strcpy(g_mlkem_fault.operation_name, "PRE_MUL_INPUT_B (r[j+len] before fqmul)");
            snprintf(g_mlkem_fault.fault_description, sizeof(g_mlkem_fault.fault_description),
                     "Mid-NTT Locus PRE_MUL_B Stage %u Butterfly %u: %d -> %d",
                     layer, butterfly_idx, (int)g_mlkem_fault.orig_value, (int)g_mlkem_fault.faulted_value);
            g_mlkem_fault.trace_recorded = true;
            g_mlkem_fault.trigger_count++;
        } else if (g_mlkem_fault.ntt_locus == NTT_LOCUS_TWIDDLE_ZETA) {
            g_mlkem_fault.orig_value = *zeta_ptr;
            *zeta_ptr = (int16_t)apply_fault(*zeta_ptr, g_mlkem_fault.fault_type, g_mlkem_fault.bit_to_flip,
                                             g_mlkem_fault.additive_glitch, g_mlkem_fault.forced_value, -3328, 3328);
            g_mlkem_fault.faulted_value = *zeta_ptr;
            g_mlkem_fault.stage_recorded = (int)layer;
            g_mlkem_fault.butterfly_recorded = (int)butterfly_idx;
            g_mlkem_fault.coeff_recorded = idx0;
            g_mlkem_fault.twiddle_zeta = *zeta_ptr;
            strcpy(g_mlkem_fault.operation_name, "TWIDDLE_ZETA (zeta before fqmul)");
            snprintf(g_mlkem_fault.fault_description, sizeof(g_mlkem_fault.fault_description),
                     "Mid-NTT Locus TWIDDLE Stage %u Butterfly %u: %d -> %d",
                     layer, butterfly_idx, (int)g_mlkem_fault.orig_value, (int)g_mlkem_fault.faulted_value);
            g_mlkem_fault.trace_recorded = true;
            g_mlkem_fault.trigger_count++;
        }
    }
}

// 2. Mid-NTT Post-Mul Hook (Intermediate t before addition/subtraction)
void hook_mid_ntt_post_mul(
    unsigned layer, unsigned butterfly_idx, int16_t *t_ptr, size_t idx0, size_t idx1
) {
    (void)idx0; (void)idx1;
    if (!g_mlkem_fault.enabled || g_mlkem_fault.target != HOOK_TARGET_MID_NTT_BUTTERFLY) {
        return;
    }

    if ((g_mlkem_fault.trigger_count == 0 || g_mlkem_fault.persistent) &&
        g_mlkem_fault.target_stage == layer &&
        g_mlkem_fault.target_butterfly == butterfly_idx &&
        g_mlkem_fault.ntt_locus == NTT_LOCUS_INTERMEDIATE_T) {

        g_mlkem_fault.orig_value = *t_ptr;
        *t_ptr = (int16_t)apply_fault(*t_ptr, g_mlkem_fault.fault_type, g_mlkem_fault.bit_to_flip,
                                      g_mlkem_fault.additive_glitch, g_mlkem_fault.forced_value, -3328, 3328);
        g_mlkem_fault.faulted_value = *t_ptr;
        g_mlkem_fault.stage_recorded = (int)layer;
        g_mlkem_fault.butterfly_recorded = (int)butterfly_idx;
        g_mlkem_fault.coeff_recorded = idx1;
        g_mlkem_fault.intermediate_product = *t_ptr;
        strcpy(g_mlkem_fault.operation_name, "INTERMEDIATE_T (shared t = fqmul(r[j+len], zeta))");
        snprintf(g_mlkem_fault.fault_description, sizeof(g_mlkem_fault.fault_description),
                 "Mid-NTT Locus INTERMEDIATE_T Stage %u Butterfly %u: %d -> %d",
                 layer, butterfly_idx, (int)g_mlkem_fault.orig_value, (int)g_mlkem_fault.faulted_value);
        g_mlkem_fault.trace_recorded = true;
        g_mlkem_fault.trigger_count++;
    }
}

// 3. Mid-NTT Butterfly Output Hook (r[j] or r[j+len] after add/sub)
void hook_mid_ntt_butterfly(
    unsigned layer, unsigned butterfly_idx, int16_t zeta,
    int16_t *r_j, int16_t *r_j_len, int16_t t, size_t idx0, size_t idx1
) {
    if (!g_mlkem_fault.enabled || g_mlkem_fault.target != HOOK_TARGET_MID_NTT_BUTTERFLY) {
        return;
    }

    // Only handle if locus is DEFAULT or OUTPUT_ADD or OUTPUT_SUB
    if (g_mlkem_fault.ntt_locus != NTT_LOCUS_DEFAULT &&
        g_mlkem_fault.ntt_locus != NTT_LOCUS_OUTPUT_ADD &&
        g_mlkem_fault.ntt_locus != NTT_LOCUS_OUTPUT_SUB) {
        return;
    }

    if ((g_mlkem_fault.trigger_count == 0 || g_mlkem_fault.persistent) &&
        g_mlkem_fault.target_stage == layer &&
        g_mlkem_fault.target_butterfly == butterfly_idx) {

        int use_second = (g_mlkem_fault.ntt_locus == NTT_LOCUS_OUTPUT_SUB) ? 1 :
                         (g_mlkem_fault.ntt_locus == NTT_LOCUS_OUTPUT_ADD) ? 0 :
                         g_mlkem_fault.target_coeff_pair;

        int16_t *target_ptr = (use_second == 0) ? r_j : r_j_len;
        size_t target_idx = (use_second == 0) ? idx0 : idx1;
        
        g_mlkem_fault.orig_value = *target_ptr;
        *target_ptr = (int16_t)apply_fault(*target_ptr, g_mlkem_fault.fault_type, g_mlkem_fault.bit_to_flip,
                                           g_mlkem_fault.additive_glitch, g_mlkem_fault.forced_value, -3328, 3328);
        g_mlkem_fault.faulted_value = *target_ptr;

        g_mlkem_fault.stage_recorded = (int)layer;
        g_mlkem_fault.butterfly_recorded = (int)butterfly_idx;
        g_mlkem_fault.coeff_recorded = target_idx;
        g_mlkem_fault.twiddle_zeta = zeta;
        g_mlkem_fault.intermediate_product = (int32_t)t;
        strcpy(g_mlkem_fault.operation_name,
               (use_second == 0) ? "CT_BUTTERFLY_ADD (r[j] = r[j] + t)" : "CT_BUTTERFLY_SUB (r[j+len] = r[j] - t)");

        snprintf(g_mlkem_fault.fault_description, sizeof(g_mlkem_fault.fault_description),
                 "Mid-NTT Stage %u Butterfly %u (coeff %zu): %d -> %d [twiddle zeta=%d]",
                 layer, butterfly_idx, target_idx, (int)g_mlkem_fault.orig_value, (int)g_mlkem_fault.faulted_value, (int)zeta);
        
        g_mlkem_fault.trace_recorded = true;
        g_mlkem_fault.trigger_count++;
    }
}

static int16_t g_baseline_layers[8][256];
static bool g_has_baseline_layers = false;
static bool g_capturing_baseline_layers = false;

void mlkem_fault_start_baseline_layer_capture(void) {
    g_capturing_baseline_layers = true;
    g_has_baseline_layers = false;
    memset(g_baseline_layers, 0, sizeof(g_baseline_layers));
}

void mlkem_fault_finish_baseline_layer_capture(void) {
    g_capturing_baseline_layers = false;
    g_has_baseline_layers = true;
}

// 4. NTT Layer End Hook (Tracks intermediate layer diffusion)
void hook_mid_ntt_layer_end(unsigned layer, int16_t *coeffs) {
    if (layer < 1 || layer > 7) {
        return;
    }
    if (g_capturing_baseline_layers) {
        memcpy(g_baseline_layers[layer], coeffs, sizeof(int16_t) * 256);
        return;
    }
    if (g_mlkem_fault.enabled && g_mlkem_fault.track_layer_diff && g_has_baseline_layers) {
        int diff = 0;
        for (int c = 0; c < 256; c++) {
            if (coeffs[c] != g_baseline_layers[layer][c]) {
                diff++;
            }
        }
        g_mlkem_fault.layer_diff_counts[layer] = diff;
    }
}

// 5. Mid-PolyMul Accumulator Hook
void hook_mid_polymul_accumulator(
    unsigned poly_idx, unsigned acc_idx, int32_t t[2],
    int16_t op_a, int16_t op_b, int32_t prod
) {
    if (!g_mlkem_fault.enabled || g_mlkem_fault.target != HOOK_TARGET_MID_POLYMUL_ACC) {
        return;
    }

    if (g_mlkem_fault.trigger_count == 0 &&
        g_mlkem_fault.target_poly_idx == poly_idx &&
        g_mlkem_fault.target_acc_idx == acc_idx) {

        unsigned coord = g_mlkem_fault.target_coord;
        g_mlkem_fault.orig_value = t[coord];
        t[coord] = apply_fault(t[coord], g_mlkem_fault.fault_type, g_mlkem_fault.bit_to_flip,
                               g_mlkem_fault.additive_glitch, g_mlkem_fault.forced_value, -10000000, 10000000);
        g_mlkem_fault.faulted_value = t[coord];

        g_mlkem_fault.coeff_recorded = 2 * poly_idx + coord;
        g_mlkem_fault.operand_a = op_a;
        g_mlkem_fault.operand_b = op_b;
        g_mlkem_fault.intermediate_product = prod;
        snprintf(g_mlkem_fault.operation_name, sizeof(g_mlkem_fault.operation_name),
                 "ACCUMULATE_DOT_PRODUCT (k=%u, t[%u])", acc_idx, coord);

        snprintf(g_mlkem_fault.fault_description, sizeof(g_mlkem_fault.fault_description),
                 "Mid-PolyMul Poly %u VectorCoord k=%u Accumulator t[%u]: %d -> %d [op_a=%d op_b=%d]",
                 poly_idx, acc_idx, coord, (int)g_mlkem_fault.orig_value, (int)g_mlkem_fault.faulted_value, (int)op_a, (int)op_b);
        
        g_mlkem_fault.trace_recorded = true;
        g_mlkem_fault.trigger_count++;
    }
}

void hook_mid_polymul_post_reduce(unsigned poly_idx, int16_t r0, int16_t r1) {
    (void)poly_idx; (void)r0; (void)r1;
}

// 6. Mid-CBD SWAR Popcount Hook
void hook_mid_cbd_popcount(unsigned word_idx, uint32_t *d_ptr) {
    if (!g_mlkem_fault.enabled || g_mlkem_fault.target != HOOK_TARGET_MID_CBD_POPCOUNT) {
        return;
    }

    if (g_mlkem_fault.trigger_count == 0 && g_mlkem_fault.target_word_idx == word_idx) {
        g_mlkem_fault.orig_value = (int32_t)(*d_ptr);
        *d_ptr = (uint32_t)apply_fault((int32_t)*d_ptr, g_mlkem_fault.fault_type, g_mlkem_fault.bit_to_flip,
                                       g_mlkem_fault.additive_glitch, g_mlkem_fault.forced_value, 0, 0xFFFFFFFF);
        g_mlkem_fault.faulted_value = (int32_t)(*d_ptr);

        g_mlkem_fault.coeff_recorded = word_idx * 8;
        strcpy(g_mlkem_fault.operation_name, "CBD_SWAR_POPCOUNT_MASK");
        snprintf(g_mlkem_fault.fault_description, sizeof(g_mlkem_fault.fault_description),
                 "Mid-CBD Popcount Word %u: 0x%08x -> 0x%08x",
                 word_idx, (unsigned)g_mlkem_fault.orig_value, (unsigned)g_mlkem_fault.faulted_value);
        g_mlkem_fault.trace_recorded = true;
        g_mlkem_fault.trigger_count++;
    }
}

// 7. Mid-CBD Sampled Coefficient Hook
void hook_mid_cbd_sample(size_t coeff_idx, int16_t a, int16_t b, int16_t *sampled_ptr) {
    if (!g_mlkem_fault.enabled || g_mlkem_fault.target != HOOK_TARGET_MID_CBD_SAMPLE) {
        return;
    }

    if (g_mlkem_fault.trigger_count == 0 && g_mlkem_fault.target_coeff_idx == coeff_idx) {
        g_mlkem_fault.orig_value = *sampled_ptr;
        *sampled_ptr = (int16_t)apply_fault(*sampled_ptr, g_mlkem_fault.fault_type, g_mlkem_fault.bit_to_flip,
                                            g_mlkem_fault.additive_glitch, g_mlkem_fault.forced_value, -10, 10);
        g_mlkem_fault.faulted_value = *sampled_ptr;

        g_mlkem_fault.coeff_recorded = coeff_idx;
        g_mlkem_fault.operand_a = a;
        g_mlkem_fault.operand_b = b;
        strcpy(g_mlkem_fault.operation_name, "CBD_SUBTRACT_SAMPLED (sampled = a - b)");
        snprintf(g_mlkem_fault.fault_description, sizeof(g_mlkem_fault.fault_description),
                 "Mid-CBD Sample Coeff %zu: %d -> %d [bits a=%d b=%d, valid support [-2, 2]]",
                 coeff_idx, (int)g_mlkem_fault.orig_value, (int)g_mlkem_fault.faulted_value, (int)a, (int)b);
        g_mlkem_fault.trace_recorded = true;
        g_mlkem_fault.trigger_count++;
    }
}

// 8. FO Predicate Verification Flag Hook
void hook_decaps_verify_flag(int *fail_flag) {
    if (!g_mlkem_fault.enabled || g_mlkem_fault.target != HOOK_TARGET_FO_VERIFY_FLAG) {
        return;
    }

    int orig = *fail_flag;
    g_mlkem_fault.orig_value = orig;

    if (g_mlkem_fault.fo_direction == 0) {
        // Valid ciphertext path: force failure (0 -> 1)
        *fail_flag = 1;
    } else if (g_mlkem_fault.fo_direction == 1) {
        // Corrupted ciphertext path: force success (1 -> 0)
        *fail_flag = 0;
    } else {
        // Toggle flag
        *fail_flag = (orig == 0) ? 1 : 0;
    }

    g_mlkem_fault.faulted_value = *fail_flag;
    strcpy(g_mlkem_fault.operation_name, "CT_MEMCMP_EQUALITY_PREDICATE");
    snprintf(g_mlkem_fault.fault_description, sizeof(g_mlkem_fault.fault_description),
             "FO Predicate Decapsulation Fail Flag: %d -> %d (direction=%d)",
             orig, *fail_flag, g_mlkem_fault.fo_direction);
    g_mlkem_fault.trace_recorded = true;
    g_mlkem_fault.trigger_count++;
}

// 9. Legacy Post-Operation Hooks
void hook_post_ntt_coefficient(int16_t *coeffs, size_t count) {
    if (!g_mlkem_fault.enabled || g_mlkem_fault.target != HOOK_TARGET_POST_NTT) {
        return;
    }
    if (g_mlkem_fault.trigger_count == 0 && g_mlkem_fault.target_coeff_idx < count) {
        size_t idx = g_mlkem_fault.target_coeff_idx;
        g_mlkem_fault.orig_value = coeffs[idx];
        coeffs[idx] = (int16_t)apply_fault(coeffs[idx], g_mlkem_fault.fault_type, g_mlkem_fault.bit_to_flip,
                                           g_mlkem_fault.additive_glitch, g_mlkem_fault.forced_value, -3328, 3328);
        g_mlkem_fault.faulted_value = coeffs[idx];
        g_mlkem_fault.coeff_recorded = idx;
        strcpy(g_mlkem_fault.operation_name, "POST_OPERATION_BUFFER_MUTATION");
        snprintf(g_mlkem_fault.fault_description, sizeof(g_mlkem_fault.fault_description),
                 "Post-NTT Output Buffer Mutation (Coeff %zu): %d -> %d",
                 idx, (int)g_mlkem_fault.orig_value, (int)g_mlkem_fault.faulted_value);
        g_mlkem_fault.trace_recorded = true;
        g_mlkem_fault.trigger_count++;
    }
}

void hook_post_polymul_coefficient(int16_t *coeffs, size_t count) {
    if (!g_mlkem_fault.enabled || g_mlkem_fault.target != HOOK_TARGET_POST_POLYMUL) {
        return;
    }
    if (g_mlkem_fault.trigger_count == 0 && g_mlkem_fault.target_coeff_idx < count) {
        size_t idx = g_mlkem_fault.target_coeff_idx;
        g_mlkem_fault.orig_value = coeffs[idx];
        coeffs[idx] = (int16_t)apply_fault(coeffs[idx], g_mlkem_fault.fault_type, g_mlkem_fault.bit_to_flip,
                                           g_mlkem_fault.additive_glitch, g_mlkem_fault.forced_value, -3328, 3328);
        g_mlkem_fault.faulted_value = coeffs[idx];
        g_mlkem_fault.coeff_recorded = idx;
        strcpy(g_mlkem_fault.operation_name, "POST_OPERATION_BUFFER_MUTATION");
        snprintf(g_mlkem_fault.fault_description, sizeof(g_mlkem_fault.fault_description),
                 "Post-PolyMul Output Buffer Mutation (Coeff %zu): %d -> %d",
                 idx, (int)g_mlkem_fault.orig_value, (int)g_mlkem_fault.faulted_value);
        g_mlkem_fault.trace_recorded = true;
        g_mlkem_fault.trigger_count++;
    }
}

void hook_post_sampling_coefficient(int16_t *coeffs, size_t count) {
    if (!g_mlkem_fault.enabled || g_mlkem_fault.target != HOOK_TARGET_POST_CBD) {
        return;
    }
    if (g_mlkem_fault.trigger_count == 0 && g_mlkem_fault.target_coeff_idx < count) {
        size_t idx = g_mlkem_fault.target_coeff_idx;
        g_mlkem_fault.orig_value = coeffs[idx];
        coeffs[idx] = (int16_t)apply_fault(coeffs[idx], g_mlkem_fault.fault_type, g_mlkem_fault.bit_to_flip,
                                           g_mlkem_fault.additive_glitch, g_mlkem_fault.forced_value, -10, 10);
        g_mlkem_fault.faulted_value = coeffs[idx];
        g_mlkem_fault.coeff_recorded = idx;
        strcpy(g_mlkem_fault.operation_name, "POST_OPERATION_BUFFER_MUTATION");
        snprintf(g_mlkem_fault.fault_description, sizeof(g_mlkem_fault.fault_description),
                 "Post-Sampling Output Buffer Mutation (Coeff %zu): %d -> %d",
                 idx, (int)g_mlkem_fault.orig_value, (int)g_mlkem_fault.faulted_value);
        g_mlkem_fault.trace_recorded = true;
        g_mlkem_fault.trigger_count++;
    }
}

/* =========================================================================
 * Phase 7G: Native NTT Monitor and In-Place Recovery Implementation
 * ========================================================================= */
ntt_native_monitor_state_t g_ntt_native_monitor = {
    .mode = NTT_NATIVE_MONITOR_DISABLED,
    .allow_retry = false,
    .layer_mask = 0x7F,
    .executed_count = 0,
    .mismatch_count = 0,
    .retry_attempt_count = 0,
    .recovered_count = 0,
    .persistent_count = 0,
    .last_failed_layer = -1,
    .last_failed_butterfly = -1
};

static const int16_t g_trusted_zetas[128] = {
    -1044, -758,  -359,  -1517, 1493,  1422,  287,   202,  -171,  622,   1577,
    182,   962,   -1202, -1474, 1468,  573,   -1325, 264,  383,   -829,  1458,
    -1602, -130,  -681,  1017,  732,   608,   -1542, 411,  -205,  -1571, 1223,
    652,   -552,  1015,  -1293, 1491,  -282,  -1544, 516,  -8,    -320,  -666,
    -1618, -1162, 126,   1469,  -853,  -90,   -271,  830,  107,   -1421, -247,
    -951,  -398,  961,   -1508, -725,  448,   -1065, 677,  -1275, -1103, 430,
    555,   843,   -1251, 871,   1550,  105,   422,   587,  177,   -235,  -291,
    -460,  1574,  1653,  -246,  778,   1159,  -147,  -777, 1483,  -602,  1119,
    -1590, 644,   -872,  349,   418,   329,   -156,  -75,  817,   1097,  603,
    610,   1322,  -1285, -1465, 384,   -1215, -136,  1218, -1335, -874,  220,
    -1187, -1659, -1185, -1530, -1278, 794,   -1510, -854, -870,  478,   -108,
    -308,  996,   991,   958,   -1460, 1522,  1628
};

static inline int16_t monitor_fqmul(int16_t a, int16_t b) {
    int32_t prod = (int32_t)a * (int32_t)b;
    int16_t u = (int16_t)((int32_t)((int16_t)prod) * (-3327));
    int32_t t = (int32_t)u * 3329;
    t = prod - t;
    t >>= 16;
    return (int16_t)t;
}

void ntt_native_monitor_reset(void) {
    g_ntt_native_monitor.executed_count = 0;
    g_ntt_native_monitor.mismatch_count = 0;
    g_ntt_native_monitor.retry_attempt_count = 0;
    g_ntt_native_monitor.recovered_count = 0;
    g_ntt_native_monitor.persistent_count = 0;
    g_ntt_native_monitor.last_failed_layer = -1;
    g_ntt_native_monitor.last_failed_butterfly = -1;
}

void ntt_native_monitor_configure(ntt_native_monitor_mode_t mode, bool allow_retry, uint32_t layer_mask) {
    ntt_native_monitor_reset();
    g_ntt_native_monitor.mode = mode;
    g_ntt_native_monitor.allow_retry = allow_retry;
    g_ntt_native_monitor.layer_mask = layer_mask;
}

uint32_t ntt_native_monitor_get_persistent_count(void) {
    return g_ntt_native_monitor.persistent_count;
}

void native_ntt_monitor_butterfly(
    unsigned layer, unsigned butterfly_idx, int16_t zeta,
    int16_t u_saved, int16_t v_saved, int16_t t_used,
    int16_t *r_j, int16_t *r_j_len
) {
    if (g_ntt_native_monitor.mode == NTT_NATIVE_MONITOR_DISABLED) {
        return;
    }
    if (layer < 1 || layer > 7 || !((g_ntt_native_monitor.layer_mask >> (layer - 1)) & 1u)) {
        return;
    }

    g_ntt_native_monitor.executed_count++;

    int32_t diff_c, sum_c;
    int16_t t_check;

    if (g_ntt_native_monitor.mode == NTT_NATIVE_MONITOR_RECOMPUTED_T) {
        t_check = monitor_fqmul(v_saved, zeta);
    } else {
        t_check = t_used;
    }

    diff_c = ((int32_t)(*r_j) - (int32_t)(*r_j_len) - 2 * (int32_t)t_check) % 3329;
    sum_c  = ((int32_t)(*r_j) + (int32_t)(*r_j_len) - 2 * (int32_t)u_saved) % 3329;

    if (diff_c != 0 || sum_c != 0) {
        g_ntt_native_monitor.mismatch_count++;
        g_ntt_native_monitor.last_failed_layer = (int)layer;
        g_ntt_native_monitor.last_failed_butterfly = (int)butterfly_idx;

        if (g_ntt_native_monitor.allow_retry) {
            g_ntt_native_monitor.retry_attempt_count++;

            /* In-place rollback using saved pre-butterfly operands */
            *r_j = u_saved;
            *r_j_len = v_saved;

            int16_t t_retry = monitor_fqmul(v_saved, zeta);
            int16_t u_new = (int16_t)(u_saved + t_retry);
            int16_t v_new = (int16_t)(u_saved - t_retry);

            if (g_mlkem_fault.persistent && g_mlkem_fault.enabled &&
                g_mlkem_fault.target == HOOK_TARGET_MID_NTT_BUTTERFLY &&
                g_mlkem_fault.target_stage == layer &&
                g_mlkem_fault.target_butterfly == butterfly_idx) {
                u_new ^= (1u << (g_mlkem_fault.bit_to_flip % 16));
            }

            *r_j = u_new;
            *r_j_len = v_new;

            int32_t diff_retry = ((int32_t)u_new - (int32_t)v_new - 2 * (int32_t)t_retry) % 3329;
            int32_t sum_retry  = ((int32_t)u_new + (int32_t)v_new - 2 * (int32_t)u_saved) % 3329;

            if (diff_retry == 0 && sum_retry == 0) {
                g_ntt_native_monitor.recovered_count++;
            } else {
                g_ntt_native_monitor.persistent_count++;
            }
        } else {
            g_ntt_native_monitor.persistent_count++;
        }
    }
}
