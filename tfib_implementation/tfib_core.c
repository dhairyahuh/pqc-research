#include "tfib_core.h"
#include <stdio.h>
#include <string.h>

tfib_mode_t g_tfib_mode = TFIB_MODE_BASELINE;

/* Baseline monitor fallback state */
static uint32_t g_baseline_executed = 0;
static uint32_t g_baseline_mismatches = 0;
static uint32_t g_baseline_retries = 0;
static uint32_t g_baseline_recovered = 0;
static uint32_t g_baseline_persistent = 0;

void tfib_set_mode(tfib_mode_t mode) {
    g_tfib_mode = mode;
}

tfib_mode_t tfib_get_mode(void) {
    return g_tfib_mode;
}

void tfib_reset_all_stats(void) {
    g_baseline_executed = 0;
    g_baseline_mismatches = 0;
    g_baseline_retries = 0;
    g_baseline_recovered = 0;
    g_baseline_persistent = 0;
    tfib_ref_reset_stats();
    tfib_meta_reset_stats();
}

uint32_t tfib_get_total_mismatches(void) {
    if (g_tfib_mode == TFIB_MODE_REF) return g_tfib_ref_stats.mismatch_count;
    if (g_tfib_mode == TFIB_MODE_META) return g_tfib_meta_stats.mismatch_count;
    return g_baseline_mismatches;
}

uint32_t tfib_get_total_recoveries(void) {
    if (g_tfib_mode == TFIB_MODE_REF) return g_tfib_ref_stats.recovered_count;
    if (g_tfib_mode == TFIB_MODE_META) return g_tfib_meta_stats.recovered_count;
    return g_baseline_recovered;
}

uint32_t tfib_get_total_persistent_fails(void) {
    if (g_tfib_mode == TFIB_MODE_REF) return g_tfib_ref_stats.persistent_fail_count;
    if (g_tfib_mode == TFIB_MODE_META) return g_tfib_meta_stats.persistent_fail_count;
    return g_baseline_persistent;
}

uint32_t tfib_get_twiddle_faults_detected(void) {
    if (g_tfib_mode == TFIB_MODE_REF) return g_tfib_ref_stats.twiddle_fault_detected;
    if (g_tfib_mode == TFIB_MODE_META) return g_tfib_meta_stats.twiddle_fault_detected;
    return 0;
}

/* =========================================================================
 * Production Monitor Hooks Linked into mlkem768_inst.o
 * ========================================================================= */

uint32_t ntt_native_monitor_get_persistent_count(void) {
    return tfib_get_total_persistent_fails();
}

uint32_t invntt_native_monitor_get_persistent_count(void) {
    return tfib_get_total_persistent_fails();
}

void native_ntt_monitor_butterfly(
    unsigned layer, unsigned butterfly_idx, int16_t zeta,
    int16_t u_saved, int16_t v_saved, int16_t t_used,
    int16_t *r_j, int16_t *r_j_len
) {
    if (g_tfib_mode == TFIB_MODE_REF) {
        tfib_ref_monitor_ntt_butterfly(layer, butterfly_idx, zeta, u_saved, v_saved, t_used, r_j, r_j_len);
        return;
    }
    if (g_tfib_mode == TFIB_MODE_META) {
        tfib_meta_monitor_ntt_butterfly(layer, butterfly_idx, zeta, u_saved, v_saved, t_used, r_j, r_j_len);
        return;
    }

    /* Baseline behavior: consumes caller-supplied zeta */
    g_baseline_executed++;
    int16_t t_check = tfib_fqmul(v_saved, zeta);
    int32_t diff_c = ((int32_t)(*r_j) - (int32_t)(*r_j_len) - 2 * (int32_t)t_check) % MLKEM_Q;
    int32_t sum_c  = ((int32_t)(*r_j) + (int32_t)(*r_j_len) - 2 * (int32_t)u_saved) % MLKEM_Q;

    if (diff_c != 0 || sum_c != 0) {
        g_baseline_mismatches++;
        g_baseline_retries++;
        *r_j = u_saved;
        *r_j_len = v_saved;
        int16_t t_retry = tfib_fqmul(v_saved, zeta);
        *r_j = (int16_t)(u_saved + t_retry);
        *r_j_len = (int16_t)(u_saved - t_retry);
        if (g_tfib_fault.persistent) {
            g_baseline_persistent++;
        } else {
            g_baseline_recovered++;
        }
    }
}

void native_invntt_monitor_butterfly(
    unsigned layer, unsigned butterfly_idx, int16_t zeta,
    int16_t u_saved, int16_t v_saved,
    int16_t *r_j, int16_t *r_j_len
) {
    if (g_tfib_mode == TFIB_MODE_REF) {
        tfib_ref_monitor_invntt_butterfly(layer, butterfly_idx, zeta, u_saved, v_saved, r_j, r_j_len);
        return;
    }
    if (g_tfib_mode == TFIB_MODE_META) {
        tfib_meta_monitor_invntt_butterfly(layer, butterfly_idx, zeta, u_saved, v_saved, r_j, r_j_len);
        return;
    }

    /* Baseline behavior */
    g_baseline_executed++;
    int32_t sum_c = ((int32_t)(*r_j) - (int32_t)(u_saved + v_saved)) % MLKEM_Q;
    int16_t d_check = (int16_t)(v_saved - u_saved);
    int16_t v_expected = tfib_fqmul(d_check, zeta);
    int32_t diff_c = ((int32_t)(*r_j_len) - (int32_t)v_expected) % MLKEM_Q;

    if (sum_c != 0 || diff_c != 0) {
        g_baseline_mismatches++;
        g_baseline_retries++;
        *r_j = u_saved;
        *r_j_len = v_saved;
        int16_t u_new = tfib_barrett_reduce((int16_t)(u_saved + v_saved));
        int16_t d_retry = (int16_t)(v_saved - u_saved);
        int16_t v_new = tfib_fqmul(d_retry, zeta);
        *r_j = u_new;
        *r_j_len = v_new;
        if (g_tfib_fault.persistent) {
            g_baseline_persistent++;
        } else {
            g_baseline_recovered++;
        }
    }
}

/* =========================================================================
 * Fault Injection Hooks
 * ========================================================================= */

void hook_mid_ntt_pre_butterfly(
    unsigned layer, unsigned butterfly_idx, int16_t *zeta_ptr,
    int16_t *r_j, int16_t *r_j_len, size_t idx0, size_t idx1
) {
    (void)r_j; (void)r_j_len; (void)idx0; (void)idx1;
    if (!g_tfib_fault.enabled) return;

    if ((g_tfib_fault.trigger_count == 0 || g_tfib_fault.persistent) &&
        g_tfib_fault.target_layer == layer &&
        g_tfib_fault.target_butterfly == butterfly_idx) {

        if (g_tfib_fault.locus == TFIB_FAULT_OP_TWIDDLE || g_tfib_fault.locus == TFIB_FAULT_SIMULTANEOUS) {
            g_tfib_fault.orig_val = *zeta_ptr;
            *zeta_ptr ^= (1 << (g_tfib_fault.bit_to_flip % 16));
            g_tfib_fault.faulted_val = *zeta_ptr;
            g_tfib_fault.trigger_count++;
            g_tfib_fault.op_fault_fired = true;
        }
    }
}

void hook_mid_invntt_pre_butterfly(
    unsigned layer, unsigned butterfly_idx, int16_t *zeta_ptr,
    int16_t *r_j, int16_t *r_j_len, size_t idx0, size_t idx1
) {
    (void)r_j; (void)r_j_len; (void)idx0; (void)idx1;
    if (!g_tfib_fault.enabled) return;

    if ((g_tfib_fault.trigger_count == 0 || g_tfib_fault.persistent) &&
        g_tfib_fault.target_layer == layer &&
        g_tfib_fault.target_butterfly == butterfly_idx) {

        if (g_tfib_fault.locus == TFIB_FAULT_OP_TWIDDLE || g_tfib_fault.locus == TFIB_FAULT_SIMULTANEOUS) {
            g_tfib_fault.orig_val = *zeta_ptr;
            *zeta_ptr ^= (1 << (g_tfib_fault.bit_to_flip % 16));
            g_tfib_fault.faulted_val = *zeta_ptr;
            g_tfib_fault.trigger_count++;
            g_tfib_fault.op_fault_fired = true;
        }
    }
}

/* Stubs for remaining unused research hooks */
void hook_decaps_verify_flag(int *fail) { (void)fail; }
void hook_mid_cbd_popcount(int16_t *a, int16_t *b) { (void)a; (void)b; }
void hook_mid_cbd_sample(int16_t *coeff, uint32_t a, uint32_t b) { (void)coeff; (void)a; (void)b; }
void hook_mid_invntt_butterfly(unsigned l, unsigned b, int16_t z, int16_t *rj, int16_t *rjl, size_t i0, size_t i1) {
    (void)l; (void)b; (void)z; (void)rj; (void)rjl; (void)i0; (void)i1;
}
void hook_mid_invntt_post_diff(unsigned l, unsigned b, int16_t *diff, size_t i0, size_t i1) {
    (void)l; (void)b; (void)diff; (void)i0; (void)i1;
}
void hook_mid_ntt_butterfly(unsigned l, unsigned b, int16_t z, int16_t *rj, int16_t *rjl, int16_t t, size_t i0, size_t i1) {
    (void)l; (void)b; (void)z; (void)rj; (void)rjl; (void)t; (void)i0; (void)i1;
}
void hook_mid_ntt_layer_end(unsigned layer, int16_t *coeffs) { (void)layer; (void)coeffs; }
void hook_mid_ntt_post_mul(unsigned l, unsigned b, int16_t *t, size_t i0, size_t i1) {
    (void)l; (void)b; (void)t; (void)i0; (void)i1;
}
void hook_mid_polymul_accumulator(int32_t *acc, int16_t a, int16_t b) { (void)acc; (void)a; (void)b; }
void hook_mid_polymul_post_reduce(int16_t *c, int32_t acc) { (void)c; (void)acc; }
void hook_post_ntt_coefficient(int16_t *coeffs, size_t count) { (void)coeffs; (void)count; }
void hook_post_polymul_coefficient(int16_t *coeffs, size_t count) { (void)coeffs; (void)count; }
void hook_post_sampling_coefficient(int16_t *coeffs, size_t count) { (void)coeffs; (void)count; }
