/*
 * ML-DSA Internal Fault Injection Hooks Implementation
 * Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems
 * Standards: NIST FIPS 204 (ML-DSA-44, ML-DSA-65, ML-DSA-87)
 */

#include "mldsa_fault_hooks.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    bool active;
    unsigned target_layer;
    unsigned target_butterfly;
    mldsa_ntt_locus_t locus;
    mldsa_fault_type_t fault_type;
    unsigned bit;
    int32_t delta;
    int32_t force_val;
} mldsa_ntt_config_t;

typedef struct {
    bool active;
    int override_mode; /* 0: force pass, 1: force fail */
} mldsa_norm_config_t;

typedef struct {
    bool active;
    unsigned byte_idx;
    uint8_t xor_mask;
} mldsa_challenge_config_t;

typedef struct {
    bool active;
    int override_mode; /* 0: force 0 (ACCEPT), 1: force non-zero (REJECT) */
} mldsa_verify_config_t;

static mldsa_ntt_config_t g_ntt_cfg = {0};
static mldsa_norm_config_t g_norm_z_cfg = {0};
static mldsa_norm_config_t g_norm_w0_cfg = {0};
static mldsa_norm_config_t g_norm_ct0_cfg = {0};
static mldsa_challenge_config_t g_chal_cfg = {0};
static mldsa_verify_config_t g_ver_norm_cfg = {0};
static mldsa_verify_config_t g_ver_cmp_cfg = {0};

static uint32_t g_trigger_count = 0;

/* Diffusion Measurement State (8 layers in ML-DSA) */
static int32_t g_clean_baseline_layers[9][256];
static int32_t g_faulted_observed_layers[9][256];
static bool g_baseline_captured = false;

void mldsa_fault_reset(void) {
    memset(&g_ntt_cfg, 0, sizeof(g_ntt_cfg));
    memset(&g_norm_z_cfg, 0, sizeof(g_norm_z_cfg));
    memset(&g_norm_w0_cfg, 0, sizeof(g_norm_w0_cfg));
    memset(&g_norm_ct0_cfg, 0, sizeof(g_norm_ct0_cfg));
    memset(&g_chal_cfg, 0, sizeof(g_chal_cfg));
    memset(&g_ver_norm_cfg, 0, sizeof(g_ver_norm_cfg));
    memset(&g_ver_cmp_cfg, 0, sizeof(g_ver_cmp_cfg));
    g_trigger_count = 0;
}

uint32_t mldsa_fault_get_trigger_count(void) {
    return g_trigger_count;
}

void mldsa_fault_arm_mid_ntt(
    unsigned target_layer,
    unsigned target_butterfly,
    mldsa_ntt_locus_t locus,
    mldsa_fault_type_t type,
    unsigned bit,
    int32_t delta,
    int32_t force_val
) {
    g_ntt_cfg.active = true;
    g_ntt_cfg.target_layer = target_layer;
    g_ntt_cfg.target_butterfly = target_butterfly;
    g_ntt_cfg.locus = locus;
    g_ntt_cfg.fault_type = type;
    g_ntt_cfg.bit = bit;
    g_ntt_cfg.delta = delta;
    g_ntt_cfg.force_val = force_val;
}

void mldsa_fault_arm_norm_z(int override_mode) {
    g_norm_z_cfg.active = true;
    g_norm_z_cfg.override_mode = override_mode;
}

void mldsa_fault_arm_norm_w0(int override_mode) {
    g_norm_w0_cfg.active = true;
    g_norm_w0_cfg.override_mode = override_mode;
}

void mldsa_fault_arm_norm_ct0(int override_mode) {
    g_norm_ct0_cfg.active = true;
    g_norm_ct0_cfg.override_mode = override_mode;
}

void mldsa_fault_arm_challenge(unsigned byte_idx, uint8_t xor_mask) {
    g_chal_cfg.active = true;
    g_chal_cfg.byte_idx = byte_idx;
    g_chal_cfg.xor_mask = xor_mask;
}

void mldsa_fault_arm_verify_norm(int override_mode) {
    g_ver_norm_cfg.active = true;
    g_ver_norm_cfg.override_mode = override_mode;
}

void mldsa_fault_arm_verify_cmp(int override_mode) {
    g_ver_cmp_cfg.active = true;
    g_ver_cmp_cfg.override_mode = override_mode;
}

/* Helper to apply fault to a 32-bit signed ring coefficient */
static void apply_fault_to_int32(int32_t *val_ptr, mldsa_ntt_config_t *cfg) {
    if (!cfg || !val_ptr || !cfg->active) return;
    int32_t orig = *val_ptr;
    switch (cfg->fault_type) {
        case MLDSA_FAULT_BIT_FLIP:
            *val_ptr ^= (1 << (cfg->bit % 32));
            break;
        case MLDSA_FAULT_ADDITIVE_GLITCH:
            *val_ptr += cfg->delta;
            break;
        case MLDSA_FAULT_ZEROING:
            *val_ptr = 0;
            break;
        case MLDSA_FAULT_RANDOM_REPLACEMENT:
            *val_ptr = (int32_t)((rand() % (2 * MLDSA_RING_Q)) - MLDSA_RING_Q);
            break;
        case MLDSA_FAULT_FORCE_VALUE:
            *val_ptr = cfg->force_val;
            break;
        default:
            break;
    }
    g_trigger_count++;
    cfg->active = false; /* Single-shot transient fault: model single SEU particle strike */
}

/* Callbacks from C source */
void hook_mid_mldsa_ntt_pre_butterfly(
    unsigned layer, unsigned butterfly_idx,
    int32_t *r_j, int32_t *r_jlen, int32_t *zeta_ptr
) {
    (void)r_j;
    if (!g_ntt_cfg.active) return;
    if (g_ntt_cfg.target_layer != layer) return;
    if (g_ntt_cfg.target_butterfly != butterfly_idx) return;

    if (g_ntt_cfg.locus == MLDSA_NTT_LOCUS_INPUT_B_PRE_MUL) {
        apply_fault_to_int32(r_jlen, &g_ntt_cfg);
    } else if (g_ntt_cfg.locus == MLDSA_NTT_LOCUS_TWIDDLE_ZETA) {
        apply_fault_to_int32(zeta_ptr, &g_ntt_cfg);
    }
}

void hook_mid_mldsa_ntt_post_mul(
    unsigned layer, unsigned butterfly_idx,
    int32_t *t_ptr, int32_t zeta
) {
    (void)zeta;
    if (!g_ntt_cfg.active) return;
    if (g_ntt_cfg.target_layer != layer) return;
    if (g_ntt_cfg.target_butterfly != butterfly_idx) return;

    if (g_ntt_cfg.locus == MLDSA_NTT_LOCUS_INTERMEDIATE_T) {
        apply_fault_to_int32(t_ptr, &g_ntt_cfg);
    }
}

void hook_mid_mldsa_ntt_output(
    unsigned layer, unsigned butterfly_idx,
    int32_t *r_j, int32_t *r_jlen
) {
    if (!g_ntt_cfg.active) return;
    if (g_ntt_cfg.target_layer != layer) return;
    if (g_ntt_cfg.target_butterfly != butterfly_idx) return;

    if (g_ntt_cfg.locus == MLDSA_NTT_LOCUS_OUTPUT_ADD) {
        apply_fault_to_int32(r_j, &g_ntt_cfg);
    } else if (g_ntt_cfg.locus == MLDSA_NTT_LOCUS_OUTPUT_SUB) {
        apply_fault_to_int32(r_jlen, &g_ntt_cfg);
    }
}

void hook_mid_mldsa_ntt_layer_end(unsigned layer, int32_t r[256]) {
    if (layer >= 1 && layer <= 8) {
        if (!g_baseline_captured) {
            memcpy(g_clean_baseline_layers[layer], r, sizeof(int32_t) * 256);
        } else {
            memcpy(g_faulted_observed_layers[layer], r, sizeof(int32_t) * 256);
        }
    }
}

void hook_mid_mldsa_challenge(uint8_t *challenge_bytes, size_t len) {
    if (!g_chal_cfg.active || !challenge_bytes) return;
    if (g_chal_cfg.byte_idx < len) {
        challenge_bytes[g_chal_cfg.byte_idx] ^= g_chal_cfg.xor_mask;
        g_trigger_count++;
        g_chal_cfg.active = false; /* Single-shot transient fault */
    }
}

void hook_mid_mldsa_norm_check_z(int *ret_ptr) {
    if (!g_norm_z_cfg.active || !ret_ptr) return;
    if (g_norm_z_cfg.override_mode == 0) {
        *ret_ptr = 0; /* Force PASS (Bypass norm bound) */
        g_norm_z_cfg.active = false;
    } else if (g_norm_z_cfg.override_mode == 1) {
        *ret_ptr = -1; /* Force FAIL single-shot (Trigger attempt retry) */
        g_norm_z_cfg.active = false;
    } else {
        *ret_ptr = -1; /* Force FAIL persistent (Exhaust attempt budget / DoS) */
    }
    g_trigger_count++;
}

void hook_mid_mldsa_norm_check_w0(uint32_t *w0_invalid_ptr, unsigned k) {
    (void)k;
    if (!g_norm_w0_cfg.active || !w0_invalid_ptr) return;
    if (g_norm_w0_cfg.override_mode == 0) {
        *w0_invalid_ptr = 0; /* Force PASS */
        g_norm_w0_cfg.active = false;
    } else if (g_norm_w0_cfg.override_mode == 1) {
        *w0_invalid_ptr = 1; /* Force FAIL single-shot */
        g_norm_w0_cfg.active = false;
    } else {
        *w0_invalid_ptr = 1; /* Force FAIL persistent */
    }
    g_trigger_count++;
}

void hook_mid_mldsa_norm_check_ct0(uint32_t *h_invalid_ptr, unsigned k) {
    (void)k;
    if (!g_norm_ct0_cfg.active || !h_invalid_ptr) return;
    if (g_norm_ct0_cfg.override_mode == 0) {
        *h_invalid_ptr = 0; /* Force PASS */
        g_norm_ct0_cfg.active = false;
    } else if (g_norm_ct0_cfg.override_mode == 1) {
        *h_invalid_ptr = 1; /* Force FAIL single-shot */
        g_norm_ct0_cfg.active = false;
    } else {
        *h_invalid_ptr = 1; /* Force FAIL persistent */
    }
    g_trigger_count++;
}

void hook_mid_mldsa_verify_norm_z(int *norm_failed_ptr) {
    if (!g_ver_norm_cfg.active || !norm_failed_ptr) return;
    if (g_ver_norm_cfg.override_mode == 0) {
        *norm_failed_ptr = 0; /* Force PASS */
    } else {
        *norm_failed_ptr = 1; /* Force FAIL */
    }
    g_ver_norm_cfg.active = false;
    g_trigger_count++;
}

void hook_mid_mldsa_verify_cmp(int *cmp_ptr, const uint8_t *c, const uint8_t *c2) {
    (void)c; (void)c2;
    if (!g_ver_cmp_cfg.active || !cmp_ptr) return;
    if (g_ver_cmp_cfg.override_mode == 0) {
        *cmp_ptr = 0; /* Force 0 -> ACCEPT signature */
    } else {
        *cmp_ptr = 1; /* Force 1 -> REJECT signature */
    }
    g_ver_cmp_cfg.active = false;
    g_trigger_count++;
}

void mldsa_ntt_capture_baseline(const int32_t r_clean[256]) {
    (void)r_clean;
    g_baseline_captured = true;
}

int mldsa_ntt_get_layer_diffs(unsigned layer) {
    if (layer < 1 || layer > 8) return 0;
    int diffs = 0;
    for (int i = 0; i < 256; i++) {
        if (g_clean_baseline_layers[layer][i] != g_faulted_observed_layers[layer][i]) {
            diffs++;
        }
    }
    return diffs;
}
