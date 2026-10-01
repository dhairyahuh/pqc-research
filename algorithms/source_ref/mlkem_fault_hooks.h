/**
 * ML-KEM Source-Level Research Fault Injection Hooks
 * Provides mathematically explicit, mid-operation and post-operation
 * instrumentation hooks for:
 * 1. Mid-NTT Cooley-Tukey butterfly stages (stage, butterfly, operand locus, bit, delta, random, zero, force)
 * 2. Mid-PolyMul accumulation loops (vector coordinate k, accumulator t[0]/t[1])
 * 3. Mid-CBD noise sampling (SWAR popcount calculation, sampled coefficient)
 * 4. FO decapsulation re-encryption verification predicate (bidirectional 0->1, 1->0)
 * 5. Legacy post-operation comparison hooks (for taxonomy validation)
 * 6. Stage-by-stage NTT diffusion tracking (layer 1..7 diffusion count measurement)
 */

#ifndef MLKEM_FAULT_HOOKS_H
#define MLKEM_FAULT_HOOKS_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    HOOK_TARGET_NONE = 0,
    // Mid-operation internal hooks (True algorithmic instrumentation)
    HOOK_TARGET_MID_NTT_BUTTERFLY = 1,
    HOOK_TARGET_MID_POLYMUL_ACC = 2,
    HOOK_TARGET_MID_CBD_SAMPLE = 3,
    HOOK_TARGET_MID_CBD_POPCOUNT = 4,
    // Control / Predicate verification hooks
    HOOK_TARGET_FO_VERIFY_FLAG = 5,
    // Post-operation baseline hooks (for taxonomy comparison)
    HOOK_TARGET_POST_NTT = 6,
    HOOK_TARGET_POST_POLYMUL = 7,
    HOOK_TARGET_POST_CBD = 8
} mlkem_hook_target_t;

typedef enum {
    FAULT_TYPE_BIT_FLIP = 0,
    FAULT_TYPE_ADDITIVE_GLITCH = 1,
    FAULT_TYPE_RANDOM_REPLACEMENT = 2,
    FAULT_TYPE_ZEROING = 3,
    FAULT_TYPE_FORCE_VALUE = 4
} mlkem_fault_type_t;

typedef enum {
    NTT_LOCUS_DEFAULT = 0,             // After add/sub on chosen output (legacy default)
    NTT_LOCUS_INPUT_B_PRE_MUL = 1,     // r[j+len] before fqmul
    NTT_LOCUS_TWIDDLE_ZETA = 2,        // zeta before fqmul
    NTT_LOCUS_INTERMEDIATE_T = 3,      // t after fqmul, before add/sub
    NTT_LOCUS_OUTPUT_ADD = 4,          // r[j] after addition
    NTT_LOCUS_OUTPUT_SUB = 5           // r[j+len] after subtraction
} mlkem_ntt_locus_t;

typedef struct {
    bool enabled;
    mlkem_hook_target_t target;
    mlkem_fault_type_t fault_type;
    
    // Mid-NTT targets:
    unsigned target_stage;      // 1..7
    unsigned target_butterfly;  // 0..127
    unsigned target_coeff_pair; // 0 for r[j], 1 for r[j+len]
    mlkem_ntt_locus_t ntt_locus;// Specific operand locus within butterfly
    
    // Mid-PolyMul targets:
    unsigned target_poly_idx;   // 0..127 (i)
    unsigned target_acc_idx;    // 0..K-1 (k, e.g. 0..2 for 768)
    unsigned target_coord;      // 0 for t[0], 1 for t[1]
    
    // CBD Popcount / Sample targets:
    size_t target_coeff_idx;    // 0..255
    size_t target_word_idx;     // 0..31
    
    // Bit / Glitch configuration:
    uint8_t bit_to_flip;        // 0..31
    int32_t additive_glitch;    // delta value
    int32_t forced_value;       // for FORCE_VALUE
    
    // FO Transform configuration:
    int fo_direction;           // 0: valid CT (0->1), 1: corrupted CT (1->0), 2: always toggle
    
    uint64_t trigger_count;
    
    // Multi-layer diffusion tracking
    bool track_layer_diff;
    bool has_baseline_poly;
    int16_t baseline_poly[256];
    int layer_diff_counts[8];   // [1..7] number of differing coefficients after each layer
    
    // Detailed execution trace recording buffer
    bool trace_recorded;
    char fault_taxonomy[48];    // "MID-OPERATION", "POST-OPERATION", "CONTROL/PREDICATE"
    char target_function[64];
    int stage_recorded;
    int butterfly_recorded;
    size_t coeff_recorded;
    int32_t orig_value;
    int32_t faulted_value;
    int16_t operand_a;
    int16_t operand_b;
    int16_t twiddle_zeta;
    int32_t intermediate_product;
    int32_t final_propagated_val;
    char operation_name[64];
    char fault_description[256];
} mlkem_fault_config_t;

extern mlkem_fault_config_t g_mlkem_fault;

void mlkem_fault_reset(void);

// Arming APIs
void mlkem_fault_arm_mid_ntt(
    unsigned stage, unsigned butterfly, unsigned coeff_pair,
    mlkem_fault_type_t fault_type, uint8_t bit, int16_t delta
);

void mlkem_fault_arm_mid_ntt_locus(
    unsigned stage, unsigned butterfly, mlkem_ntt_locus_t locus,
    mlkem_fault_type_t fault_type, uint8_t bit, int16_t delta, int32_t force_val
);

void mlkem_fault_enable_diffusion_tracking(const int16_t *baseline_poly);
int mlkem_fault_get_diffusion_count(unsigned layer);
void mlkem_fault_start_baseline_layer_capture(void);
void mlkem_fault_finish_baseline_layer_capture(void);

void mlkem_fault_arm_mid_polymul(
    unsigned poly_idx, unsigned acc_idx, unsigned coord,
    mlkem_fault_type_t fault_type, uint8_t bit, int32_t delta
);

void mlkem_fault_arm_mid_cbd_sample(
    size_t coeff_idx, mlkem_fault_type_t fault_type, uint8_t bit, int16_t delta
);

void mlkem_fault_arm_mid_cbd_popcount(
    size_t word_idx, uint8_t bit
);

void mlkem_fault_arm_fo_flag(int direction);

void mlkem_fault_arm_post_op(
    mlkem_hook_target_t target, size_t coeff_idx, uint8_t bit, int16_t delta
);

// Source instrumentation hook callbacks
void hook_mid_ntt_pre_butterfly(
    unsigned layer, unsigned butterfly_idx, int16_t *zeta_ptr,
    int16_t *r_j, int16_t *r_j_len, size_t idx0, size_t idx1
);

void hook_mid_ntt_post_mul(
    unsigned layer, unsigned butterfly_idx, int16_t *t_ptr, size_t idx0, size_t idx1
);

void hook_mid_ntt_butterfly(
    unsigned layer, unsigned butterfly_idx, int16_t zeta,
    int16_t *r_j, int16_t *r_j_len, int16_t t, size_t idx0, size_t idx1
);

void hook_mid_ntt_layer_end(unsigned layer, int16_t *coeffs);

void hook_mid_polymul_accumulator(
    unsigned poly_idx, unsigned acc_idx, int32_t t[2],
    int16_t op_a, int16_t op_b, int32_t prod
);

void hook_mid_polymul_post_reduce(
    unsigned poly_idx, int16_t r0, int16_t r1
);

void hook_mid_cbd_popcount(
    unsigned word_idx, uint32_t *d_ptr
);

void hook_mid_cbd_sample(
    size_t coeff_idx, int16_t a, int16_t b, int16_t *sampled_ptr
);

void hook_decaps_verify_flag(int *fail_flag);

// Legacy post-op hooks
void hook_post_ntt_coefficient(int16_t *coeffs, size_t count);
void hook_post_polymul_coefficient(int16_t *coeffs, size_t count);
void hook_post_sampling_coefficient(int16_t *coeffs, size_t count);

#ifdef __cplusplus
}
#endif

#endif // MLKEM_FAULT_HOOKS_H
