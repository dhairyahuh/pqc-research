#include "tfib_meta.h"
#include <string.h>

const uint16_t tfib_zetas_tag[TFIB_ZETA_COUNT] = {
    0x6E96u, 0x2D79u, 0xF9E9u, 0x353Au, 0x57E3u, 0x4C79u, 0x81BBu, 0x170Fu,
    0xB74Fu, 0xE145u, 0x81B1u, 0x9A8Fu, 0x6564u, 0xD841u, 0xC32Au, 0x1911u,
    0x0BCFu, 0x9318u, 0xC710u, 0xE576u, 0x54D5u, 0xE2F5u, 0x2D52u, 0x0BEBu,
    0x86ADu, 0x6CEAu, 0x26ACu, 0x9139u, 0x9CECu, 0xB4BCu, 0xC01Fu, 0xC918u,
    0xC9E5u, 0xCA6Fu, 0x1950u, 0x45DEu, 0xA2F5u, 0x95ECu, 0x4B7Au, 0xD84Du,
    0xCE16u, 0x5FC3u, 0x82C0u, 0xCF1Fu, 0x14C8u, 0x1139u, 0x6ACAu, 0x3CA8u,
    0x7FC9u, 0xADA5u, 0xCAA1u, 0x4F6Fu, 0x832Du, 0x36BCu, 0x5BEDu, 0xF994u,
    0x31E0u, 0x08C2u, 0x66CCu, 0xC5DAu, 0xABC6u, 0x5AE0u, 0x5139u, 0xBB50u,
    0x7E83u, 0x6A7Du, 0x9C4Bu, 0xEF72u, 0x169Bu, 0xB638u, 0xEF72u, 0xE284u,
    0x1444u, 0x76D8u, 0x85B9u, 0x8374u, 0xF313u, 0x3C2Bu, 0x9392u, 0x5E30u,
    0x5B90u, 0x0149u, 0x3847u, 0xA194u, 0x64A1u, 0x00F4u, 0x416Au, 0x73F2u,
    0xD918u, 0x85AFu, 0x7908u, 0x9F3Cu, 0x9A54u, 0x101Eu, 0x27B0u, 0x7640u,
    0xF923u, 0xD432u, 0x0FDBu, 0x0E63u, 0x8D24u, 0x24D4u, 0xCCF3u, 0x2135u,
    0xBDDBu, 0x7903u, 0xEB52u, 0x2DF8u, 0x84D0u, 0xAE23u, 0xF001u, 0x5F60u,
    0xB25Du, 0x8305u, 0x11EAu, 0x546Bu, 0x0024u, 0x63EDu, 0x3236u, 0x582Bu,
    0x8C56u, 0x6B07u, 0x98F4u, 0xFB4Eu, 0x3628u, 0xC8A3u, 0xF316u, 0x41A1u
};

tfib_stats_t g_tfib_meta_stats;

void tfib_meta_init(void) {
    memset(&g_tfib_meta_stats, 0, sizeof(g_tfib_meta_stats));
    g_tfib_meta_stats.last_failed_layer = -1;
    g_tfib_meta_stats.last_failed_butterfly = -1;
}

void tfib_meta_reset_stats(void) {
    tfib_meta_init();
}

/* Strategy 2: Forward Cooley-Tukey Butterfly Monitor */
void tfib_meta_monitor_ntt_butterfly(
    unsigned layer, unsigned b_idx, int16_t zeta_op,
    int16_t u_saved, int16_t v_saved, int16_t t_used,
    int16_t *r_j, int16_t *r_j_len
) {
    (void)t_used;
    g_tfib_meta_stats.executed_count++;

    unsigned k = tfib_twiddle_idx_ntt(layer, b_idx);
    uint16_t expected_tag = tfib_zetas_tag[k];

    /* Fault injection on metadata or checker */
    if (g_tfib_fault.enabled &&
        (g_tfib_fault.trigger_count == 0 || g_tfib_fault.persistent) &&
        g_tfib_fault.target_layer == layer &&
        g_tfib_fault.target_butterfly == b_idx) {

        if (g_tfib_fault.locus == TFIB_FAULT_META_TAG) {
            g_tfib_fault.orig_val = (int16_t)expected_tag;
            expected_tag ^= (1 << (g_tfib_fault.bit_to_flip % 16));
            g_tfib_fault.faulted_val = (int16_t)expected_tag;
            g_tfib_fault.trigger_count++;
        }
    }

    /* 1. Metadata Tag Verification */
    uint16_t computed_tag = tfib_meta_compute_tag(zeta_op, k);
    bool tag_mismatch = (computed_tag != expected_tag);

    /* 2. Arithmetic Invariant Verification */
    int16_t t_check = tfib_fqmul(v_saved, zeta_op);
    int32_t diff_c = ((int32_t)(*r_j) - (int32_t)(*r_j_len) - 2 * (int32_t)t_check) % MLKEM_Q;
    int32_t sum_c  = ((int32_t)(*r_j) + (int32_t)(*r_j_len) - 2 * (int32_t)u_saved) % MLKEM_Q;

    if (g_tfib_fault.enabled &&
        (g_tfib_fault.trigger_count == 0 || g_tfib_fault.persistent) &&
        g_tfib_fault.target_layer == layer &&
        g_tfib_fault.target_butterfly == b_idx &&
        g_tfib_fault.locus == TFIB_FAULT_CHECKER_LOGIC) {
        sum_c ^= 1;
        g_tfib_fault.trigger_count++;
    }

    if (tag_mismatch || diff_c != 0 || sum_c != 0) {
        g_tfib_meta_stats.mismatch_count++;
        if (tag_mismatch) g_tfib_meta_stats.twiddle_fault_detected++;
        if (diff_c != 0 || sum_c != 0) g_tfib_meta_stats.arithmetic_fault_detected++;

        g_tfib_meta_stats.last_failed_layer = (int)layer;
        g_tfib_meta_stats.last_failed_butterfly = (int)b_idx;

        g_tfib_meta_stats.retry_attempt_count++;

        /* In-place rollback */
        *r_j = u_saved;
        *r_j_len = v_saved;

        /* If operational twiddle is corrupted, metadata cannot repair it (no reference table) -> safe fail-stop */
        if (g_tfib_fault.locus == TFIB_FAULT_OP_TWIDDLE || g_tfib_fault.persistent) {
            g_tfib_meta_stats.persistent_fail_count++;
        } else {
            /* Transient metadata or checker fault cleared on retry */
            int16_t t_retry = tfib_fqmul(v_saved, zeta_op);
            *r_j = (int16_t)(u_saved + t_retry);
            *r_j_len = (int16_t)(u_saved - t_retry);
            g_tfib_meta_stats.recovered_count++;
        }
    }
}

/* Strategy 2: Inverse Gentleman-Sande Butterfly Monitor */
void tfib_meta_monitor_invntt_butterfly(
    unsigned layer, unsigned b_idx, int16_t zeta_op,
    int16_t u_saved, int16_t v_saved,
    int16_t *r_j, int16_t *r_j_len
) {
    g_tfib_meta_stats.executed_count++;

    unsigned k = tfib_twiddle_idx_invntt(layer, b_idx);
    uint16_t expected_tag = tfib_zetas_tag[k];

    if (g_tfib_fault.enabled &&
        (g_tfib_fault.trigger_count == 0 || g_tfib_fault.persistent) &&
        g_tfib_fault.target_layer == layer &&
        g_tfib_fault.target_butterfly == b_idx) {

        if (g_tfib_fault.locus == TFIB_FAULT_META_TAG) {
            g_tfib_fault.orig_val = (int16_t)expected_tag;
            expected_tag ^= (1 << (g_tfib_fault.bit_to_flip % 16));
            g_tfib_fault.faulted_val = (int16_t)expected_tag;
            g_tfib_fault.trigger_count++;
        }
    }

    uint16_t computed_tag = tfib_meta_compute_tag(zeta_op, k);
    bool tag_mismatch = (computed_tag != expected_tag);

    int32_t sum_c = ((int32_t)(*r_j) - (int32_t)(u_saved + v_saved)) % MLKEM_Q;
    int16_t d_check = (int16_t)(v_saved - u_saved);
    int16_t v_expected = tfib_fqmul(d_check, zeta_op);
    int32_t diff_c = ((int32_t)(*r_j_len) - (int32_t)v_expected) % MLKEM_Q;

    if (g_tfib_fault.enabled &&
        (g_tfib_fault.trigger_count == 0 || g_tfib_fault.persistent) &&
        g_tfib_fault.target_layer == layer &&
        g_tfib_fault.target_butterfly == b_idx &&
        g_tfib_fault.locus == TFIB_FAULT_CHECKER_LOGIC) {
        sum_c ^= 1;
        g_tfib_fault.trigger_count++;
    }

    if (tag_mismatch || sum_c != 0 || diff_c != 0) {
        g_tfib_meta_stats.mismatch_count++;
        if (tag_mismatch) g_tfib_meta_stats.twiddle_fault_detected++;
        if (sum_c != 0 || diff_c != 0) g_tfib_meta_stats.arithmetic_fault_detected++;

        g_tfib_meta_stats.last_failed_layer = (int)layer;
        g_tfib_meta_stats.last_failed_butterfly = (int)b_idx;

        g_tfib_meta_stats.retry_attempt_count++;

        *r_j = u_saved;
        *r_j_len = v_saved;

        if (g_tfib_fault.locus == TFIB_FAULT_OP_TWIDDLE || g_tfib_fault.persistent) {
            g_tfib_meta_stats.persistent_fail_count++;
        } else {
            int16_t u_new = tfib_barrett_reduce((int16_t)(u_saved + v_saved));
            int16_t d_retry = (int16_t)(v_saved - u_saved);
            int16_t v_new = tfib_fqmul(d_retry, zeta_op);
            *r_j = u_new;
            *r_j_len = v_new;
            g_tfib_meta_stats.recovered_count++;
        }
    }
}
