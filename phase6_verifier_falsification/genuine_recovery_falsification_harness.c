/**
 * Phase 6 Genuine Recovery-Verifier Falsification Harness
 * 
 * Strict Audit Rules Enforced:
 * 1. Dual-Layer Independent Recovery Oracle:
 *    - Layer 1: Component-level butterfly output verification against pre-captured reference.
 *    - Layer 2: Protocol-level decapsulation key verification against pristine expected key.
 * 2. Explicit independent evaluation of Hypothesis H1 and Hypothesis H2.
 * 3. Deep challenge of DSPC mitigation: single-bit, correlated 2-bit collision, and control bypass.
 * 4. Zero wrapper metric simulation: status and counters derived purely from C execution.
 */

#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define SS_BYTES 32
#define CT_BYTES 1088
#define SK_BYTES 2400
#define PK_BYTES 1184

#define MLK_STATUS_SUCCESS 0x5A5A5A5AU
#define MLK_STATUS_REJECT  0xA5A5A5A5U
#define MLK_STATUS_FAULT   0xFFFFFFFFU

/* Monitor State Struct */
typedef struct {
    int mode;
    bool allow_retry;
    uint32_t layer_mask;
    uint32_t executed_count;
    uint32_t mismatch_count;
    uint32_t retry_attempt_count;
    uint32_t recovered_count;
    uint32_t persistent_count;
    int last_failed_layer;
    int last_failed_butterfly;
} monitor_state_t;

static monitor_state_t g_ntt_mon = {0};
static monitor_state_t g_invntt_mon = {0};

/* Fault Target Definitions */
typedef enum {
    F1_SAVED_OPERAND_BITFLIP = 0,
    F2_SNAPSHOT_PRE_RETRY_DIFFUSION = 1,
    F3_MONITOR_PERSISTENT_COUNT_ZERO = 2,
    F4_MONITOR_ALLOW_RETRY_FORCE = 3,
    F5_VERIFIER_DIFF_CALC_CORRUPT = 4,
    F6_VERIFIER_RESULT_FORCE_PASS = 5,
    F7_RETRY_ARITHMETIC_GLITCH = 6,
    F8_VERIFIER_INPUT_OPERAND_CORRUPT = 7,
    F9_DSPC_COLLISION_MULTI_BIT = 8,
    F10_DSPC_STATE_BYPASS = 9,
    F11_DSPC_CLEAN_CORRECTION = 10,
    F12_CLEAN_BASELINE_CONTROL = 11
} phase6_target_t;

/* Active Injection Control */
typedef struct {
    phase6_target_t target;
    unsigned stage;
    unsigned butterfly;
    uint8_t bit;
    uint32_t trigger_count;
    bool initial_mismatch_injected;
} active_fault_t;

static active_fault_t g_fault = {0};

/* Intermediate Arithmetic Oracle Trace */
typedef struct {
    int16_t pre_retry_u;
    int16_t pre_retry_v;
    int16_t retry_u;
    int16_t retry_v;
    int32_t diff_retry;
    int32_t sum_retry;
    bool verifier_passed;
    bool trace_captured;
} trial_trace_t;

static trial_trace_t g_trace = {0};

/* Reference Butterfly Lookup: [layer 1..7][butterfly 0..127] */
typedef struct {
    int16_t u;
    int16_t v;
} butterfly_ref_t;

static butterfly_ref_t g_ref_butterflies[8][128];
static bool g_capture_ref_mode = false;

/* External Symbols from mlkem768_inst.o */
int mlkem768_keypair(uint8_t *pk, uint8_t *sk);
int mlkem768_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int mlkem768_dec_monitored(uint8_t *ss, const uint8_t *ct, const uint8_t *sk, uint32_t *internal_status);

int randombytes(uint8_t *out, size_t outlen) {
    for (size_t i = 0; i < outlen; i++) out[i] = (uint8_t)(rand() & 0xFF);
    return 0;
}

static inline int16_t monitor_fqmul(int16_t a, int16_t b) {
    int32_t prod = (int32_t)a * (int32_t)b;
    int16_t u = (int16_t)((int32_t)((int16_t)prod) * (-3327));
    int32_t t = (int32_t)u * 3329;
    t = prod - t;
    t >>= 16;
    return (int16_t)t;
}

/* Source Hook Implementations for mlkem768_inst.o */
uint32_t ntt_native_monitor_get_persistent_count(void) {
    return g_ntt_mon.persistent_count;
}

uint32_t invntt_native_monitor_get_persistent_count(void) {
    return g_invntt_mon.persistent_count;
}

void hook_mid_ntt_pre_butterfly(unsigned layer, unsigned butterfly_idx, int16_t *zeta_ptr, int16_t *r_j, int16_t *r_j_len, size_t idx0, size_t idx1) {
    (void)layer; (void)butterfly_idx; (void)zeta_ptr; (void)r_j; (void)r_j_len; (void)idx0; (void)idx1;
}

void hook_mid_ntt_post_mul(unsigned layer, unsigned butterfly_idx, int16_t *t_ptr, size_t idx0, size_t idx1) {
    (void)idx0; (void)idx1;
    if (g_capture_ref_mode) return;

    /* For targets requiring initial mismatch, inject single-shot error into t */
    if (g_fault.target == F2_SNAPSHOT_PRE_RETRY_DIFFUSION ||
        g_fault.target == F3_MONITOR_PERSISTENT_COUNT_ZERO ||
        g_fault.target == F4_MONITOR_ALLOW_RETRY_FORCE ||
        g_fault.target == F5_VERIFIER_DIFF_CALC_CORRUPT ||
        g_fault.target == F6_VERIFIER_RESULT_FORCE_PASS ||
        g_fault.target == F7_RETRY_ARITHMETIC_GLITCH ||
        g_fault.target == F8_VERIFIER_INPUT_OPERAND_CORRUPT ||
        g_fault.target == F9_DSPC_COLLISION_MULTI_BIT ||
        g_fault.target == F10_DSPC_STATE_BYPASS ||
        g_fault.target == F11_DSPC_CLEAN_CORRECTION) {
        if (!g_fault.initial_mismatch_injected &&
            g_fault.stage == layer && g_fault.butterfly == butterfly_idx) {
            *t_ptr ^= (1 << (g_fault.bit % 16));
            g_fault.trigger_count++;
            g_fault.initial_mismatch_injected = true;
        }
    }
}

void hook_mid_ntt_butterfly(unsigned layer, unsigned butterfly_idx, int16_t zeta, int16_t *r_j, int16_t *r_j_len, int16_t t, size_t idx0, size_t idx1) {
    (void)layer; (void)butterfly_idx; (void)zeta; (void)r_j; (void)r_j_len; (void)t; (void)idx0; (void)idx1;
}

void hook_mid_ntt_layer_end(unsigned layer, int16_t *coeffs) { (void)layer; (void)coeffs; }
void hook_mid_invntt_pre_butterfly(unsigned layer, unsigned butterfly_idx, int16_t *zeta_ptr, int16_t *r_j, int16_t *r_j_len, size_t idx0, size_t idx1) { (void)layer; (void)butterfly_idx; (void)zeta_ptr; (void)r_j; (void)r_j_len; (void)idx0; (void)idx1; }
void hook_mid_invntt_post_diff(unsigned layer, unsigned butterfly_idx, int16_t *diff_ptr, size_t idx0, size_t idx1) { (void)layer; (void)butterfly_idx; (void)diff_ptr; (void)idx0; (void)idx1; }
void hook_mid_invntt_butterfly(unsigned layer, unsigned butterfly_idx, int16_t zeta, int16_t *r_j, int16_t *r_j_len, size_t idx0, size_t idx1) { (void)layer; (void)butterfly_idx; (void)zeta; (void)r_j; (void)r_j_len; (void)idx0; (void)idx1; }
void hook_mid_polymul_accumulator(unsigned poly_idx, unsigned acc_idx, int32_t t[2], int16_t op_a, int16_t op_b, int32_t prod) { (void)poly_idx; (void)acc_idx; (void)t; (void)op_a; (void)op_b; (void)prod; }
void hook_mid_polymul_post_reduce(unsigned poly_idx, int16_t r0, int16_t r1) { (void)poly_idx; (void)r0; (void)r1; }
void hook_mid_cbd_popcount(unsigned word_idx, uint32_t *d_ptr) { (void)word_idx; (void)d_ptr; }
void hook_mid_cbd_sample(size_t coeff_idx, int16_t a, int16_t b, int16_t *sampled_ptr) { (void)coeff_idx; (void)a; (void)b; (void)sampled_ptr; }
void hook_post_ntt_coefficient(int16_t *coeffs, size_t count) { (void)coeffs; (void)count; }
void hook_post_polymul_coefficient(int16_t *coeffs, size_t count) { (void)coeffs; (void)count; }
void hook_post_sampling_coefficient(int16_t *coeffs, size_t count) { (void)coeffs; (void)count; }
void hook_decaps_verify_flag(int *fail_flag) { (void)fail_flag; }

/* Native Forward NTT Butterfly Monitor Implementation */
void native_ntt_monitor_butterfly(
    unsigned layer, unsigned butterfly_idx, int16_t zeta,
    int16_t u_saved, int16_t v_saved, int16_t t_used,
    int16_t *r_j, int16_t *r_j_len
) {
    (void)t_used;
    if (layer < 1 || layer > 7) return;

    /* Reference Capture Mode: record fault-free output */
    if (g_capture_ref_mode) {
        if (layer <= 7 && butterfly_idx < 128) {
            g_ref_butterflies[layer][butterfly_idx].u = *r_j;
            g_ref_butterflies[layer][butterfly_idx].v = *r_j_len;
        }
        return;
    }

    if (g_ntt_mon.mode == 0) return;
    g_ntt_mon.executed_count++;

    /* Fault Target 1: Saved operand post-capture bit flip (Single-Shot Isolated) */
    if (g_fault.target == F1_SAVED_OPERAND_BITFLIP &&
        g_fault.trigger_count == 0 &&
        g_fault.stage == layer && g_fault.butterfly == butterfly_idx) {
        u_saved ^= (1 << (g_fault.bit % 16));
        g_fault.trigger_count++;
    }

    int32_t diff_c, sum_c;
    int16_t t_check = monitor_fqmul(v_saved, zeta);

    diff_c = ((int32_t)(*r_j) - (int32_t)(*r_j_len) - 2 * (int32_t)t_check) % 3329;
    sum_c  = ((int32_t)(*r_j) + (int32_t)(*r_j_len) - 2 * (int32_t)u_saved) % 3329;

    if (diff_c != 0 || sum_c != 0) {
        g_ntt_mon.mismatch_count++;
        g_ntt_mon.last_failed_layer = (int)layer;
        g_ntt_mon.last_failed_butterfly = (int)butterfly_idx;

        /* Record faulted state pre-retry */
        g_trace.pre_retry_u = *r_j;
        g_trace.pre_retry_v = *r_j_len;

        /* Fault Target 4: Force allow_retry = true */
        if (g_fault.target == F4_MONITOR_ALLOW_RETRY_FORCE &&
            g_fault.stage == layer && g_fault.butterfly == butterfly_idx) {
            g_ntt_mon.allow_retry = true;
            g_fault.trigger_count++;
        }

        if (g_ntt_mon.allow_retry) {
            g_ntt_mon.retry_attempt_count++;

            /* Fault Target 2: Snapshot corruption pre-retry */
            if (g_fault.target == F2_SNAPSHOT_PRE_RETRY_DIFFUSION &&
                g_fault.stage == layer && g_fault.butterfly == butterfly_idx) {
                u_saved = (int16_t)(u_saved + 100);
                g_fault.trigger_count++;
            }

            /* DSPC Mitigation Logic */
            bool dspc_active = (g_fault.target == F9_DSPC_COLLISION_MULTI_BIT ||
                                g_fault.target == F10_DSPC_STATE_BYPASS ||
                                g_fault.target == F11_DSPC_CLEAN_CORRECTION);

            if (dspc_active) {
                /* Generate DSPC checksum token */
                uint32_t snap_token = ((uint32_t)(uint16_t)u_saved) ^
                                      (((uint32_t)(uint16_t)v_saved) << 16) ^
                                      0xA55A5AA5U;

                /* Corrupt snapshot for F9, F10, F11 */
                u_saved ^= (1 << (g_fault.bit % 16));

                /* Fault Target 9: Correlated 2-bit collision against DSPC */
                if (g_fault.target == F9_DSPC_COLLISION_MULTI_BIT) {
                    /* Flip identical bit in snap_token: test_token will COLLIDE! */
                    snap_token ^= (1 << (g_fault.bit % 16));
                    g_fault.trigger_count++;
                }

                uint32_t test_token = ((uint32_t)(uint16_t)u_saved) ^
                                      (((uint32_t)(uint16_t)v_saved) << 16) ^
                                      0xA55A5AA5U;

                bool token_mismatch = (test_token != snap_token);

                /* Fault Target 10: State bypass (instruction skip / branch glitch) */
                if (g_fault.target == F10_DSPC_STATE_BYPASS) {
                    token_mismatch = false; /* Bypassed */
                    g_fault.trigger_count++;
                }

                if (token_mismatch) {
                    /* DSPC caught corruption */
                    g_ntt_mon.persistent_count++;
                    g_trace.verifier_passed = false;
                    g_trace.trace_captured = true;
                    return;
                }
            }

            /* In-place rollback */
            *r_j = u_saved;
            *r_j_len = v_saved;

            int16_t t_retry = monitor_fqmul(v_saved, zeta);

            /* Fault Target 7: Retry arithmetic glitch in multiplier */
            if (g_fault.target == F7_RETRY_ARITHMETIC_GLITCH &&
                g_fault.stage == layer && g_fault.butterfly == butterfly_idx) {
                t_retry ^= (1 << (g_fault.bit % 16));
                g_fault.trigger_count++;
            }

            int16_t u_new = (int16_t)(u_saved + t_retry);
            int16_t v_new = (int16_t)(u_saved - t_retry);

            /* For F3 & F6: Persistent fault re-strikes u_new */
            if ((g_fault.target == F3_MONITOR_PERSISTENT_COUNT_ZERO ||
                 g_fault.target == F6_VERIFIER_RESULT_FORCE_PASS) &&
                g_fault.stage == layer && g_fault.butterfly == butterfly_idx) {
                u_new ^= (1 << (g_fault.bit % 16));
            }

            *r_j = u_new;
            *r_j_len = v_new;

            /* Record retry output */
            g_trace.retry_u = u_new;
            g_trace.retry_v = v_new;

            /* Verifier Input: Fault Target 8 corrupts verifier operand u_saved */
            int16_t u_ver_operand = u_saved;
            if (g_fault.target == F8_VERIFIER_INPUT_OPERAND_CORRUPT &&
                g_fault.stage == layer && g_fault.butterfly == butterfly_idx) {
                u_ver_operand ^= (1 << (g_fault.bit % 16));
                g_fault.trigger_count++;
            }

            int32_t diff_retry = ((int32_t)u_new - (int32_t)v_new - 2 * (int32_t)t_retry) % 3329;
            int32_t sum_retry  = ((int32_t)u_new + (int32_t)v_new - 2 * (int32_t)u_ver_operand) % 3329;

            /* Fault Target 5: Verifier difference calculation glitch */
            if (g_fault.target == F5_VERIFIER_DIFF_CALC_CORRUPT &&
                g_fault.stage == layer && g_fault.butterfly == butterfly_idx) {
                diff_retry = (diff_retry + 1) % 3329;
                g_fault.trigger_count++;
            }

            /* Fault Target 6: Force verifier result to pass */
            if (g_fault.target == F6_VERIFIER_RESULT_FORCE_PASS &&
                g_fault.stage == layer && g_fault.butterfly == butterfly_idx) {
                diff_retry = 0;
                sum_retry = 0;
                g_fault.trigger_count++;
            }

            g_trace.diff_retry = diff_retry;
            g_trace.sum_retry = sum_retry;

            if (diff_retry == 0 && sum_retry == 0) {
                g_ntt_mon.recovered_count++;
                g_trace.verifier_passed = true;
            } else {
                g_ntt_mon.persistent_count++;
                g_trace.verifier_passed = false;

                /* Fault Target 3: Persistent count zeroing */
                if (g_fault.target == F3_MONITOR_PERSISTENT_COUNT_ZERO &&
                    g_fault.stage == layer && g_fault.butterfly == butterfly_idx) {
                    g_ntt_mon.persistent_count = 0;
                    g_fault.trigger_count++;
                }
            }
            g_trace.trace_captured = true;
        } else {
            g_ntt_mon.persistent_count++;
        }
    }
}

void native_invntt_monitor_butterfly(unsigned l, unsigned b, int16_t z, int16_t u, int16_t v, int16_t *r_j, int16_t *r_j_len) {
    (void)l; (void)b; (void)z; (void)u; (void)v; (void)r_j; (void)r_j_len;
}

/* =========================================================================
 * Main Benchmark Suite & Independent Oracle Evaluation
 * ========================================================================= */
int main(void) {
    printf("=========================================================================\n");
    printf(" PHASE 6 INDEPENDENT VERIFIER-FALSIFICATION AUDIT HARNESS\n");
    printf(" Rigorous Dual-Layer Recovery Oracle (Testing H1 & H2 Independently)\n");
    printf("=========================================================================\n\n");

    srand(0x1337C0DE);

    /* 1. Pre-compute clean reference keypair and ciphertext */
    uint8_t pk[PK_BYTES], sk[SK_BYTES], ct_valid[CT_BYTES], ss_expected[SS_BYTES];
    mlkem768_keypair(pk, sk);
    mlkem768_enc(ct_valid, ss_expected, pk);

    /* 2. Pre-compute canonical rejection key J(z || ct_valid) */
    uint8_t ss_rejection[SS_BYTES];
    uint32_t status_rej_clean = 0;
    memset(&g_ntt_mon, 0, sizeof(g_ntt_mon));
    g_ntt_mon.persistent_count = 1; /* Forces fail = 0xFF in kem.c */
    mlkem768_dec_monitored(ss_rejection, ct_valid, sk, &status_rej_clean);
    memset(&g_ntt_mon, 0, sizeof(g_ntt_mon));

    /* 3. Capture baseline butterfly reference outputs across all layers/butterflies */
    g_capture_ref_mode = true;
    uint8_t ss_dummy[SS_BYTES];
    uint32_t status_dummy = 0;
    mlkem768_dec_monitored(ss_dummy, ct_valid, sk, &status_dummy);
    g_capture_ref_mode = false;
    printf("[Oracle] Captured %d reference butterfly outputs for Layer 1..7.\n", 7 * 128);

    FILE *f_csv = fopen("phase6_verifier_falsification/raw_trial_results.csv", "w");
    if (!f_csv) {
        fprintf(stderr, "Fatal: Cannot open phase6_verifier_falsification/raw_trial_results.csv\n");
        return 1;
    }

    fprintf(f_csv, "trial_id,target_id,target_name,trial_idx,stage,butterfly,bit,"
                   "ref_u,ref_v,pre_retry_u,pre_retry_v,retry_u,retry_v,retry_matches_ref,"
                   "diff_retry,sum_retry,verifier_passed,mismatch_count,recovered_count,persistent_count,"
                   "status,ss_matches_expected,ss_matches_rejection,h1_false_recovery,h2_silent_corruption,classification\n");

    const char *target_names[12] = {
        "F1_SAVED_OPERAND_BITFLIP",
        "F2_SNAPSHOT_PRE_RETRY_DIFFUSION",
        "F3_MONITOR_PERSISTENT_COUNT_ZERO",
        "F4_MONITOR_ALLOW_RETRY_FORCE",
        "F5_VERIFIER_DIFF_CALC_CORRUPT",
        "F6_VERIFIER_RESULT_FORCE_PASS",
        "F7_RETRY_ARITHMETIC_GLITCH",
        "F8_VERIFIER_INPUT_OPERAND_CORRUPT",
        "F9_DSPC_COLLISION_MULTI_BIT",
        "F10_DSPC_STATE_BYPASS",
        "F11_DSPC_CLEAN_CORRECTION",
        "F12_CLEAN_BASELINE_CONTROL"
    };

    int global_id = 0;
    int h1_counts[12] = {0};
    int h2_counts[12] = {0};
    int class_summary[12][7] = {0};

    for (int tg = 0; tg < 12; tg++) {
        for (int t = 0; t < 100; t++) {
            global_id++;

            /* Setup monitor state */
            memset(&g_ntt_mon, 0, sizeof(g_ntt_mon));
            memset(&g_invntt_mon, 0, sizeof(g_invntt_mon));
            g_ntt_mon.mode = 2; // RECOMPUTED_T
            g_ntt_mon.layer_mask = 0x7F;

            if (tg == F4_MONITOR_ALLOW_RETRY_FORCE) {
                g_ntt_mon.allow_retry = false; // Starts in fail-stop mode
            } else {
                g_ntt_mon.allow_retry = true;
            }

            /* Arm fault target */
            g_fault.target = (phase6_target_t)tg;
            g_fault.stage = 1 + (t % 7);
            g_fault.butterfly = (t * 13 + 5) % 128;
            g_fault.bit = t % 16;
            g_fault.trigger_count = 0;
            g_fault.initial_mismatch_injected = false;

            /* Clear trial trace */
            memset(&g_trace, 0, sizeof(g_trace));

            uint8_t ss_out[SS_BYTES];
            uint32_t status = 0;

            /* Execute Decapsulation */
            mlkem768_dec_monitored(ss_out, ct_valid, sk, &status);

            /* External Oracle Evaluation */
            bool ss_matches_expected = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
            bool ss_matches_rejection = (memcmp(ss_out, ss_rejection, SS_BYTES) == 0);
            bool final_accepted = (status == MLK_STATUS_SUCCESS);

            /* Reference Butterfly Comparison */
            int16_t ref_u = g_ref_butterflies[g_fault.stage][g_fault.butterfly].u;
            int16_t ref_v = g_ref_butterflies[g_fault.stage][g_fault.butterfly].v;
            bool retry_matches_ref = (g_trace.trace_captured) ?
                (g_trace.retry_u == ref_u && g_trace.retry_v == ref_v) : false;

            /* Evaluate Hypotheses */
            bool h1_false_recovery = (g_trace.trace_captured && g_trace.verifier_passed && !retry_matches_ref);
            bool h2_silent_corruption = (final_accepted && !ss_matches_expected);

            if (h1_false_recovery) h1_counts[tg]++;
            if (h2_silent_corruption) h2_counts[tg]++;

            /* Independent Outcome Classification */
            const char *classification = "INCONCLUSIVE";
            int c_idx = 6;

            if (tg == F12_CLEAN_BASELINE_CONTROL) {
                if (status == MLK_STATUS_SUCCESS && ss_matches_expected && g_ntt_mon.mismatch_count == 0) {
                    classification = "CORRECT_CLEAN_EXECUTION";
                    c_idx = 0;
                }
            } else if (g_fault.trigger_count == 0) {
                classification = "FAULT_NOT_TRIGGERED";
                c_idx = 5;
            } else if (h2_silent_corruption) {
                classification = "SILENT_DATA_CORRUPTION";
                c_idx = 4;
            } else if (status == MLK_STATUS_FAULT && ss_matches_rejection) {
                classification = "SAFELY_REJECTED_MONITOR";
                c_idx = 2;
            } else if (status == MLK_STATUS_REJECT && ss_matches_rejection) {
                classification = "REJECTED_DOWNSTREAM_FO";
                c_idx = 3;
            } else if (status == MLK_STATUS_SUCCESS && ss_matches_expected && g_ntt_mon.recovered_count > 0) {
                classification = "RECOVERED_GENUINE";
                c_idx = 1;
            } else {
                classification = "INCONCLUSIVE";
                c_idx = 6;
            }

            class_summary[tg][c_idx]++;

            fprintf(f_csv, "%d,%d,%s,%d,%u,%u,%u,"
                           "%d,%d,%d,%d,%d,%d,%d,"
                           "%d,%d,%d,%u,%u,%u,"
                           "0x%08X,%d,%d,%d,%d,%s\n",
                    global_id, tg, target_names[tg], t, g_fault.stage, g_fault.butterfly, g_fault.bit,
                    ref_u, ref_v, g_trace.pre_retry_u, g_trace.pre_retry_v, g_trace.retry_u, g_trace.retry_v,
                    retry_matches_ref ? 1 : 0,
                    g_trace.diff_retry, g_trace.sum_retry, g_trace.verifier_passed ? 1 : 0,
                    g_ntt_mon.mismatch_count, g_ntt_mon.recovered_count, g_ntt_mon.persistent_count,
                    status, ss_matches_expected ? 1 : 0, ss_matches_rejection ? 1 : 0,
                    h1_false_recovery ? 1 : 0, h2_silent_corruption ? 1 : 0,
                    classification);
        }
    }

    fclose(f_csv);
    printf("[Success] 1,200 trials executed. Results saved to phase6_verifier_falsification/raw_trial_results.csv\n\n");

    printf("=========================================================================\n");
    printf(" PHASE 6 INDEPENDENT AUDIT SUMMARY (100 TRIALS PER TARGET)\n");
    printf("=========================================================================\n");
    printf("%-35s | H1 (False Rec) | H2 (SDC) | Main Outcome\n", "Target Name");
    printf("------------------------------------+----------------+----------+------------------------\n");
    for (int tg = 0; tg < 12; tg++) {
        const char *dom_outcome = "INCONC";
        int max_n = -1;
        const char *c_names[7] = {"CLEAN", "REC_GENUINE", "REJ_MONITOR", "REJ_FO", "SDC", "NOT_TRIG", "INCONC"};
        for (int c = 0; c < 7; c++) {
            if (class_summary[tg][c] > max_n) {
                max_n = class_summary[tg][c];
                dom_outcome = c_names[c];
            }
        }
        printf("%-35s | %3d/100 (%3d%%) | %2d/100   | %s (%d)\n",
               target_names[tg], h1_counts[tg], h1_counts[tg], h2_counts[tg], dom_outcome, max_n);
    }
    printf("=========================================================================\n");

    return 0;
}
