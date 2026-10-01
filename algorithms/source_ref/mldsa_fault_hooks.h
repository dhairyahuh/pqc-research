/*
 * ML-DSA Internal Fault Injection Hooks Header
 * Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems
 * Standards: NIST FIPS 204 (ML-DSA-44, ML-DSA-65, ML-DSA-87)
 */

#ifndef MLDSA_FAULT_HOOKS_H
#define MLDSA_FAULT_HOOKS_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define MLDSA_RING_Q 8380417
#define MLDSA_RING_N 256

/* NTT Operand Locus */
typedef enum {
    MLDSA_NTT_LOCUS_DEFAULT = 0,
    MLDSA_NTT_LOCUS_INPUT_B_PRE_MUL,
    MLDSA_NTT_LOCUS_TWIDDLE_ZETA,
    MLDSA_NTT_LOCUS_INTERMEDIATE_T,
    MLDSA_NTT_LOCUS_OUTPUT_ADD,
    MLDSA_NTT_LOCUS_OUTPUT_SUB
} mldsa_ntt_locus_t;

/* Fault Type */
typedef enum {
    MLDSA_FAULT_NONE = 0,
    MLDSA_FAULT_BIT_FLIP,
    MLDSA_FAULT_ADDITIVE_GLITCH,
    MLDSA_FAULT_RANDOM_REPLACEMENT,
    MLDSA_FAULT_ZEROING,
    MLDSA_FAULT_FORCE_VALUE
} mldsa_fault_type_t;

/* Outcome Classification Taxonomy (Phase 3) */
typedef enum {
    MLDSA_OUTCOME_CORRECT = 0,
    MLDSA_OUTCOME_SIGNING_REJECT_RETRY,
    MLDSA_OUTCOME_INVALID_SIGNATURE,
    MLDSA_OUTCOME_VERIFICATION_REJECT,
    MLDSA_OUTCOME_VERIFICATION_ACCEPT,
    MLDSA_OUTCOME_EXPLICIT_ERROR,
    MLDSA_OUTCOME_CRASH,
    MLDSA_OUTCOME_TIMEOUT,
    MLDSA_OUTCOME_UNDETECTED_FAULT,
    MLDSA_OUTCOME_POTENTIAL_LEAKAGE_SIGNAL
} mldsa_outcome_class_t;

/* Control & Configuration APIs */
void mldsa_fault_reset(void);
uint32_t mldsa_fault_get_trigger_count(void);

/* Arm NTT Butterfly Glitch */
void mldsa_fault_arm_mid_ntt(
    unsigned target_layer,
    unsigned target_butterfly,
    mldsa_ntt_locus_t locus,
    mldsa_fault_type_t type,
    unsigned bit,
    int32_t delta,
    int32_t force_val
);

/* Arm Norm Checks */
void mldsa_fault_arm_norm_z(int override_mode);   /* 0: force pass, 1: force fail */
void mldsa_fault_arm_norm_w0(int override_mode);  /* 0: force pass, 1: force fail */
void mldsa_fault_arm_norm_ct0(int override_mode); /* 0: force pass, 1: force fail */

/* Arm Challenge Corruptions */
void mldsa_fault_arm_challenge(unsigned byte_idx, uint8_t xor_mask);

/* Arm Verification Control Flags */
void mldsa_fault_arm_verify_norm(int override_mode); /* 0: force pass, 1: force fail */
void mldsa_fault_arm_verify_cmp(int override_mode);  /* 0: force 0/ACCEPT, 1: force non-zero/REJECT */

/* Diffusion Tracking */
void mldsa_ntt_capture_baseline(const int32_t r_clean[256]);
int mldsa_ntt_get_layer_diffs(unsigned layer);

/* Internal Callbacks invoked from mldsa-native source */
void hook_mid_mldsa_ntt_pre_butterfly(unsigned layer, unsigned butterfly_idx, int32_t *r_j, int32_t *r_jlen, int32_t *zeta_ptr);
void hook_mid_mldsa_ntt_post_mul(unsigned layer, unsigned butterfly_idx, int32_t *t_ptr, int32_t zeta);
void hook_mid_mldsa_ntt_output(unsigned layer, unsigned butterfly_idx, int32_t *r_j, int32_t *r_jlen);
void hook_mid_mldsa_ntt_layer_end(unsigned layer, int32_t r[256]);

void hook_mid_mldsa_challenge(uint8_t *challenge_bytes, size_t len);
void hook_mid_mldsa_norm_check_z(int *ret_ptr);
void hook_mid_mldsa_norm_check_w0(uint32_t *w0_invalid_ptr, unsigned k);
void hook_mid_mldsa_norm_check_ct0(uint32_t *h_invalid_ptr, unsigned k);

void hook_mid_mldsa_verify_norm_z(int *norm_failed_ptr);
void hook_mid_mldsa_verify_cmp(int *cmp_ptr, const uint8_t *c, const uint8_t *c2);

#ifdef __cplusplus
}
#endif

#endif /* MLDSA_FAULT_HOOKS_H */
