#include "tfib_ref.h"
#include <string.h>

/* Independent reference twiddle table (identical values, distinct symbol/storage) */
const int16_t tfib_zetas_ref[TFIB_ZETA_COUNT] = {
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

tfib_stats_t g_tfib_ref_stats;

void tfib_ref_init(void) {
    memset(&g_tfib_ref_stats, 0, sizeof(g_tfib_ref_stats));
    g_tfib_ref_stats.last_failed_layer = -1;
    g_tfib_ref_stats.last_failed_butterfly = -1;
}

void tfib_ref_reset_stats(void) {
    tfib_ref_init();
}

/* Strategy 1: Forward Cooley-Tukey Butterfly Monitor */
void tfib_ref_monitor_ntt_butterfly(
    unsigned layer, unsigned b_idx, int16_t zeta_op,
    int16_t u_saved, int16_t v_saved, int16_t t_used,
    int16_t *r_j, int16_t *r_j_len
) {
    (void)t_used;
    g_tfib_ref_stats.executed_count++;

    unsigned k = tfib_twiddle_idx_ntt(layer, b_idx);
    int16_t zeta_ref = tfib_zetas_ref[k];

    /* Simulate targeted fault injections on verification path if armed */
    if (g_tfib_fault.enabled &&
        g_tfib_fault.target_layer == layer &&
        g_tfib_fault.target_butterfly == b_idx) {

        if (g_tfib_fault.locus == TFIB_FAULT_REF_TWIDDLE &&
            (g_tfib_fault.trigger_count == 0 || g_tfib_fault.persistent)) {
            g_tfib_fault.orig_val = zeta_ref;
            zeta_ref ^= (1 << (g_tfib_fault.bit_to_flip % 16));
            g_tfib_fault.faulted_val = zeta_ref;
            g_tfib_fault.trigger_count++;
        } else if (g_tfib_fault.locus == TFIB_FAULT_SIMULTANEOUS && g_tfib_fault.op_fault_fired) {
            /* Simultaneous common-mode: operational twiddle was already perturbed before butterfly;
             * perturb reference twiddle with the identical bit flip to simulate common corrupted source */
            int16_t mask = (1 << (g_tfib_fault.bit_to_flip % 16));
            zeta_ref ^= mask;
            g_tfib_fault.op_fault_fired = false;
        }
    }

    /* 1. Direct Twiddle Reference Check */
    bool twiddle_mismatch = (zeta_op != zeta_ref);

    /* 2. Recomputed Arithmetic Checks using Independent Reference */
    int16_t t_check = tfib_fqmul(v_saved, zeta_ref);
    int32_t diff_c = ((int32_t)(*r_j) - (int32_t)(*r_j_len) - 2 * (int32_t)t_check) % MLKEM_Q;
    int32_t sum_c  = ((int32_t)(*r_j) + (int32_t)(*r_j_len) - 2 * (int32_t)u_saved) % MLKEM_Q;

    /* Simulate fault in checker logic itself */
    if (g_tfib_fault.enabled &&
        (g_tfib_fault.trigger_count == 0 || g_tfib_fault.persistent) &&
        g_tfib_fault.target_layer == layer &&
        g_tfib_fault.target_butterfly == b_idx &&
        g_tfib_fault.locus == TFIB_FAULT_CHECKER_LOGIC) {
        sum_c ^= 1; /* perturb checker decision */
        g_tfib_fault.trigger_count++;
    }

    if (twiddle_mismatch || diff_c != 0 || sum_c != 0) {
        g_tfib_ref_stats.mismatch_count++;
        if (twiddle_mismatch) g_tfib_ref_stats.twiddle_fault_detected++;
        if (diff_c != 0 || sum_c != 0) g_tfib_ref_stats.arithmetic_fault_detected++;

        g_tfib_ref_stats.last_failed_layer = (int)layer;
        g_tfib_ref_stats.last_failed_butterfly = (int)b_idx;

        /* In-place Localized Rollback & Repair */
        g_tfib_ref_stats.retry_attempt_count++;

        /* Restore original operand snapshots */
        *r_j = u_saved;
        *r_j_len = v_saved;

        /* If operational twiddle was corrupted but reference is valid, recompute using reference */
        int16_t zeta_repair = tfib_zetas_ref[k];
        int16_t t_retry = tfib_fqmul(v_saved, zeta_repair);
        int16_t u_new = (int16_t)(u_saved + t_retry);
        int16_t v_new = (int16_t)(u_saved - t_retry);

        /* Check if fault is persistent and re-applies on retry */
        if (g_tfib_fault.enabled && g_tfib_fault.persistent &&
            g_tfib_fault.target_layer == layer &&
            g_tfib_fault.target_butterfly == b_idx) {
            /* Persistent fault re-perturbs output */
            u_new ^= (1 << (g_tfib_fault.bit_to_flip % 16));
        }

        *r_j = u_new;
        *r_j_len = v_new;

        /* Verify repaired computation */
        int32_t diff_retry = ((int32_t)u_new - (int32_t)v_new - 2 * (int32_t)t_retry) % MLKEM_Q;
        int32_t sum_retry  = ((int32_t)u_new + (int32_t)v_new - 2 * (int32_t)u_saved) % MLKEM_Q;

        if (diff_retry == 0 && sum_retry == 0 && !g_tfib_fault.persistent) {
            g_tfib_ref_stats.recovered_count++;
        } else {
            g_tfib_ref_stats.persistent_fail_count++;
        }
    }
}

/* Strategy 1: Inverse Gentleman-Sande Butterfly Monitor */
void tfib_ref_monitor_invntt_butterfly(
    unsigned layer, unsigned b_idx, int16_t zeta_op,
    int16_t u_saved, int16_t v_saved,
    int16_t *r_j, int16_t *r_j_len
) {
    g_tfib_ref_stats.executed_count++;

    unsigned k = tfib_twiddle_idx_invntt(layer, b_idx);
    int16_t zeta_ref = tfib_zetas_ref[k];

    if (g_tfib_fault.enabled &&
        g_tfib_fault.target_layer == layer &&
        g_tfib_fault.target_butterfly == b_idx) {

        if (g_tfib_fault.locus == TFIB_FAULT_REF_TWIDDLE &&
            (g_tfib_fault.trigger_count == 0 || g_tfib_fault.persistent)) {
            g_tfib_fault.orig_val = zeta_ref;
            zeta_ref ^= (1 << (g_tfib_fault.bit_to_flip % 16));
            g_tfib_fault.faulted_val = zeta_ref;
            g_tfib_fault.trigger_count++;
        } else if (g_tfib_fault.locus == TFIB_FAULT_SIMULTANEOUS && g_tfib_fault.op_fault_fired) {
            int16_t mask = (1 << (g_tfib_fault.bit_to_flip % 16));
            zeta_ref ^= mask;
            g_tfib_fault.op_fault_fired = false;
        }
    }

    bool twiddle_mismatch = (zeta_op != zeta_ref);

    int32_t sum_c = ((int32_t)(*r_j) - (int32_t)(u_saved + v_saved)) % MLKEM_Q;
    int16_t d_check = (int16_t)(v_saved - u_saved);
    int16_t v_expected = tfib_fqmul(d_check, zeta_ref);
    int32_t diff_c = ((int32_t)(*r_j_len) - (int32_t)v_expected) % MLKEM_Q;

    if (g_tfib_fault.enabled &&
        (g_tfib_fault.trigger_count == 0 || g_tfib_fault.persistent) &&
        g_tfib_fault.target_layer == layer &&
        g_tfib_fault.target_butterfly == b_idx &&
        g_tfib_fault.locus == TFIB_FAULT_CHECKER_LOGIC) {
        sum_c ^= 1;
        g_tfib_fault.trigger_count++;
    }

    if (twiddle_mismatch || sum_c != 0 || diff_c != 0) {
        g_tfib_ref_stats.mismatch_count++;
        if (twiddle_mismatch) g_tfib_ref_stats.twiddle_fault_detected++;
        if (sum_c != 0 || diff_c != 0) g_tfib_ref_stats.arithmetic_fault_detected++;

        g_tfib_ref_stats.last_failed_layer = (int)layer;
        g_tfib_ref_stats.last_failed_butterfly = (int)b_idx;

        g_tfib_ref_stats.retry_attempt_count++;

        *r_j = u_saved;
        *r_j_len = v_saved;

        int16_t zeta_repair = tfib_zetas_ref[k];
        int16_t u_new = tfib_barrett_reduce((int16_t)(u_saved + v_saved));
        int16_t d_retry = (int16_t)(v_saved - u_saved);
        int16_t v_new = tfib_fqmul(d_retry, zeta_repair);

        if (g_tfib_fault.enabled && g_tfib_fault.persistent &&
            g_tfib_fault.target_layer == layer &&
            g_tfib_fault.target_butterfly == b_idx) {
            v_new ^= (1 << (g_tfib_fault.bit_to_flip % 16));
        }

        *r_j = u_new;
        *r_j_len = v_new;

        int32_t sum_retry = ((int32_t)u_new - (int32_t)(u_saved + v_saved)) % MLKEM_Q;
        int16_t v_expected_retry = tfib_fqmul(d_retry, zeta_repair);
        int32_t diff_retry = ((int32_t)v_new - (int32_t)v_expected_retry) % MLKEM_Q;

        if (sum_retry == 0 && diff_retry == 0 && !g_tfib_fault.persistent) {
            g_tfib_ref_stats.recovered_count++;
        } else {
            g_tfib_ref_stats.persistent_fail_count++;
        }
    }
}
