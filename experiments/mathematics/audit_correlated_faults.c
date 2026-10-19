/**
 * Focused Experimental Audit: Correlated Fault Invariant Evasion in ML-KEM-768
 * 
 * Tests the hypothesis:
 * "Correlated faults affecting NTT arithmetic operands, verification inputs,
 *  or shared constants may evade the existing algebraic invariant checks
 *  more often than independent random faults."
 */

#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <math.h>

#include "algorithms/source_ref/mlkem_fault_hooks.h"

#define SS_BYTES 32
#define CT_BYTES 1088
#define SK_BYTES 2400
#define PK_BYTES 1184

#define MLK_STATUS_SUCCESS 0x5A5A5A5AU
#define MLK_STATUS_REJECT  0xA5A5A5A5U
#define MLK_STATUS_FAULT   0xFFFFFFFFU

int mlkem768_keypair(uint8_t *pk, uint8_t *sk);
int mlkem768_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int mlkem768_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);
int mlkem768_dec_monitored(uint8_t *ss, const uint8_t *ct, const uint8_t *sk, uint32_t *internal_status);

int randombytes(uint8_t *out, size_t outlen) {
    for (size_t i = 0; i < outlen; i++) {
        out[i] = (uint8_t)(rand() & 0xFF);
    }
    return 0;
}

typedef struct {
    const char *test_name;
    int total_trials;
    int invariant_evasions;   /* Mismatches == 0 despite active arithmetic fault */
    int invariant_detections; /* Mismatches > 0 */
    int recoveries_claimed;   /* Monitor logged recovery */
    int safe_rejections;      /* FO implicit rejection triggered */
    int silent_corruptions;   /* Returned invalid key with STATUS_SUCCESS or wrong key accepted */
    int crashes;
} experiment_result_t;

static void run_audit_suite(void) {
    printf("=========================================================================\n");
    printf(" FOCUSED EXPERIMENTAL AUDIT: CORRELATED FAULT INVARIANT EVASION\n");
    printf(" Target: ML-KEM-768 Decapsulation (Dual NTT Invariants & Local Rollback)\n");
    printf("=========================================================================\n\n");

    srand(0x1337BEEF);

    uint8_t pk[PK_BYTES];
    uint8_t sk[SK_BYTES];
    uint8_t ct_valid[CT_BYTES];
    uint8_t ss_expected[SS_BYTES];

    if (mlkem768_keypair(pk, sk) != 0 || mlkem768_enc(ct_valid, ss_expected, pk) != 0) {
        fprintf(stderr, "Fatal: Keypair or Encapsulation failed\n");
        exit(1);
    }

    const int N_TRIALS = 200;

    /* ---------------------------------------------------------------------
     * EXP 1: Independent Single-Bit ALU Faults (Control Baseline)
     * --------------------------------------------------------------------- */
    experiment_result_t exp1 = {"EXP 1: Independent Single-Bit ALU Faults", N_TRIALS, 0, 0, 0, 0, 0, 0};
    for (int t = 0; t < N_TRIALS; t++) {
        mlkem_fault_reset();
        ntt_native_monitor_configure(NTT_NATIVE_MONITOR_RECOMPUTED_T, true, 0x7F);
        invntt_native_monitor_configure(INVNTT_NATIVE_MONITOR_RECOMPUTED, true, 0x7F);

        unsigned stage = 1 + (t % 7);
        unsigned butterfly = (t * 13 + 5) % 128;
        uint8_t bit = t % 16;

        mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, bit, 0, 0);

        uint8_t ss_out[SS_BYTES];
        uint32_t status = 0;
        int rc = mlkem768_dec_monitored(ss_out, ct_valid, sk, &status);
        (void)rc;

        if (g_ntt_native_monitor.mismatch_count == 0) {
            exp1.invariant_evasions++;
        } else {
            exp1.invariant_detections++;
        }

        if (g_ntt_native_monitor.recovered_count > 0) {
            exp1.recoveries_claimed++;
        }

        if (status == MLK_STATUS_REJECT || status == MLK_STATUS_FAULT) {
            exp1.safe_rejections++;
        }

        if (memcmp(ss_out, ss_expected, SS_BYTES) != 0 && status == MLK_STATUS_SUCCESS) {
            exp1.silent_corruptions++;
        }
    }

    /* ---------------------------------------------------------------------
     * EXP 2: Correlated Symmetric Output Glitch (r_j + delta, r_j_len + delta)
     * --------------------------------------------------------------------- */
    experiment_result_t exp2 = {"EXP 2: Correlated Symmetric Output Glitch (delta, delta)", N_TRIALS, 0, 0, 0, 0, 0, 0};
    for (int t = 0; t < N_TRIALS; t++) {
        mlkem_fault_reset();
        ntt_native_monitor_configure(NTT_NATIVE_MONITOR_RECOMPUTED_T, true, 0x7F);
        invntt_native_monitor_configure(INVNTT_NATIVE_MONITOR_RECOMPUTED, true, 0x7F);

        unsigned stage = 1 + (t % 7);
        unsigned butterfly = (t * 13 + 5) % 128;
        int16_t delta = (int16_t)(1 + (t % 3328));

        /* Arm symmetric output glitch */
        g_mlkem_fault.enabled = true;
        g_mlkem_fault.target = HOOK_TARGET_MID_INVNTT_BUTTERFLY;
        g_mlkem_fault.target_stage = stage;
        g_mlkem_fault.target_butterfly = butterfly;
        g_mlkem_fault.ntt_locus = INVNTT_LOCUS_SYMMETRIC;
        g_mlkem_fault.additive_glitch = delta;

        uint8_t ss_out[SS_BYTES];
        uint32_t status = 0;
        mlkem768_dec_monitored(ss_out, ct_valid, sk, &status);

        if (g_invntt_native_monitor.mismatch_count == 0) {
            exp2.invariant_evasions++;
        } else {
            exp2.invariant_detections++;
        }

        if (g_invntt_native_monitor.recovered_count > 0) {
            exp2.recoveries_claimed++;
        }

        if (status == MLK_STATUS_REJECT || status == MLK_STATUS_FAULT) {
            exp2.safe_rejections++;
        }

        if (memcmp(ss_out, ss_expected, SS_BYTES) != 0 && status == MLK_STATUS_SUCCESS) {
            exp2.silent_corruptions++;
        }
    }

    /* ---------------------------------------------------------------------
     * EXP 3: Correlated Antisymmetric Output Glitch (delta, -delta)
     * --------------------------------------------------------------------- */
    experiment_result_t exp3 = {"EXP 3: Correlated Antisymmetric Glitch (delta, -delta)", N_TRIALS, 0, 0, 0, 0, 0, 0};
    for (int t = 0; t < N_TRIALS; t++) {
        mlkem_fault_reset();
        ntt_native_monitor_configure(NTT_NATIVE_MONITOR_RECOMPUTED_T, true, 0x7F);
        invntt_native_monitor_configure(INVNTT_NATIVE_MONITOR_RECOMPUTED, true, 0x7F);

        unsigned stage = 1 + (t % 7);
        unsigned butterfly = (t * 13 + 5) % 128;
        int16_t delta = (int16_t)(1 + (t % 3328));

        /* Arm antisymmetric output glitch */
        g_mlkem_fault.enabled = true;
        g_mlkem_fault.target = HOOK_TARGET_MID_INVNTT_BUTTERFLY;
        g_mlkem_fault.target_stage = stage;
        g_mlkem_fault.target_butterfly = butterfly;
        g_mlkem_fault.ntt_locus = INVNTT_LOCUS_ANTISYMMETRIC;
        g_mlkem_fault.additive_glitch = delta;

        uint8_t ss_out[SS_BYTES];
        uint32_t status = 0;
        mlkem768_dec_monitored(ss_out, ct_valid, sk, &status);

        if (g_invntt_native_monitor.mismatch_count == 0) {
            exp3.invariant_evasions++;
        } else {
            exp3.invariant_detections++;
        }

        if (g_invntt_native_monitor.recovered_count > 0) {
            exp3.recoveries_claimed++;
        }

        if (status == MLK_STATUS_REJECT || status == MLK_STATUS_FAULT) {
            exp3.safe_rejections++;
        }

        if (memcmp(ss_out, ss_expected, SS_BYTES) != 0 && status == MLK_STATUS_SUCCESS) {
            exp3.silent_corruptions++;
        }
    }

    /* ---------------------------------------------------------------------
     * EXP 4: Twiddle Factor Corruption (Shared Constant zeta)
     * --------------------------------------------------------------------- */
    experiment_result_t exp4 = {"EXP 4: Twiddle Factor Shared Constant Corruption (zeta)", N_TRIALS, 0, 0, 0, 0, 0, 0};
    for (int t = 0; t < N_TRIALS; t++) {
        mlkem_fault_reset();
        ntt_native_monitor_configure(NTT_NATIVE_MONITOR_RECOMPUTED_T, true, 0x7F);
        invntt_native_monitor_configure(INVNTT_NATIVE_MONITOR_RECOMPUTED, true, 0x7F);

        unsigned stage = 1 + (t % 7);
        unsigned butterfly = (t * 13 + 5) % 128;
        uint8_t bit = t % 16;

        mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_TWIDDLE_ZETA, FAULT_TYPE_BIT_FLIP, bit, 0, 0);

        uint8_t ss_out[SS_BYTES];
        uint32_t status = 0;
        mlkem768_dec_monitored(ss_out, ct_valid, sk, &status);

        if (g_ntt_native_monitor.mismatch_count == 0) {
            exp4.invariant_evasions++;
        } else {
            exp4.invariant_detections++;
        }

        if (g_ntt_native_monitor.recovered_count > 0) {
            exp4.recoveries_claimed++;
        }

        if (status == MLK_STATUS_REJECT || status == MLK_STATUS_FAULT) {
            exp4.safe_rejections++;
        }

        if (memcmp(ss_out, ss_expected, SS_BYTES) != 0 && status == MLK_STATUS_SUCCESS) {
            exp4.silent_corruptions++;
        }
    }

    /* ---------------------------------------------------------------------
     * EXP 5: Pre-Butterfly Input Corruption (Corrupting r[j] prior to butterfly)
     * --------------------------------------------------------------------- */
    experiment_result_t exp5 = {"EXP 5: Input Operand Corruption (Prior to Butterfly)", N_TRIALS, 0, 0, 0, 0, 0, 0};
    for (int t = 0; t < N_TRIALS; t++) {
        mlkem_fault_reset();
        ntt_native_monitor_configure(NTT_NATIVE_MONITOR_RECOMPUTED_T, true, 0x7F);
        invntt_native_monitor_configure(INVNTT_NATIVE_MONITOR_RECOMPUTED, true, 0x7F);

        unsigned stage = 1 + (t % 7);
        unsigned butterfly = (t * 13 + 5) % 128;
        uint8_t bit = t % 16;

        /* Inverting bit in r[j+len] before pre-butterfly capture */
        g_mlkem_fault.enabled = true;
        g_mlkem_fault.target = HOOK_TARGET_MID_INVNTT_BUTTERFLY;
        g_mlkem_fault.target_stage = stage;
        g_mlkem_fault.target_butterfly = butterfly;
        g_mlkem_fault.ntt_locus = INVNTT_LOCUS_INPUT_U;
        g_mlkem_fault.fault_type = FAULT_TYPE_BIT_FLIP;
        g_mlkem_fault.bit_to_flip = bit;

        uint8_t ss_out[SS_BYTES];
        uint32_t status = 0;
        mlkem768_dec_monitored(ss_out, ct_valid, sk, &status);

        if (g_invntt_native_monitor.mismatch_count == 0) {
            exp5.invariant_evasions++;
        } else {
            exp5.invariant_detections++;
        }

        if (g_invntt_native_monitor.recovered_count > 0) {
            exp5.recoveries_claimed++;
        }

        if (status == MLK_STATUS_REJECT || status == MLK_STATUS_FAULT) {
            exp5.safe_rejections++;
        }

        if (memcmp(ss_out, ss_expected, SS_BYTES) != 0 && status == MLK_STATUS_SUCCESS) {
            exp5.silent_corruptions++;
        }
    }

    /* ---------------------------------------------------------------------
     * EXP 6: Retry-Path Persistent Fault (Fault Active on Retry Recomputation)
     * --------------------------------------------------------------------- */
    experiment_result_t exp6 = {"EXP 6: Persistent / Retry-Path Fault (Active on Retry)", N_TRIALS, 0, 0, 0, 0, 0, 0};
    for (int t = 0; t < N_TRIALS; t++) {
        mlkem_fault_reset();
        ntt_native_monitor_configure(NTT_NATIVE_MONITOR_RECOMPUTED_T, true, 0x7F);
        invntt_native_monitor_configure(INVNTT_NATIVE_MONITOR_RECOMPUTED, true, 0x7F);

        unsigned stage = 1 + (t % 7);
        unsigned butterfly = (t * 13 + 5) % 128;
        uint8_t bit = t % 16;

        g_mlkem_fault.enabled = true;
        g_mlkem_fault.target = HOOK_TARGET_MID_NTT_BUTTERFLY;
        g_mlkem_fault.target_stage = stage;
        g_mlkem_fault.target_butterfly = butterfly;
        g_mlkem_fault.ntt_locus = NTT_LOCUS_OUTPUT_ADD;
        g_mlkem_fault.fault_type = FAULT_TYPE_BIT_FLIP;
        g_mlkem_fault.bit_to_flip = bit;
        g_mlkem_fault.persistent = true; /* Stays corrupted on retry! */

        uint8_t ss_out[SS_BYTES];
        uint32_t status = 0;
        mlkem768_dec_monitored(ss_out, ct_valid, sk, &status);

        if (g_ntt_native_monitor.mismatch_count == 0) {
            exp6.invariant_evasions++;
        } else {
            exp6.invariant_detections++;
        }

        if (g_ntt_native_monitor.recovered_count > 0) {
            exp6.recoveries_claimed++;
        }

        if (status == MLK_STATUS_REJECT || status == MLK_STATUS_FAULT) {
            exp6.safe_rejections++;
        }

        if (memcmp(ss_out, ss_expected, SS_BYTES) != 0 && status == MLK_STATUS_SUCCESS) {
            exp6.silent_corruptions++;
        }
    }

    /* Print Audit Table */
    printf("%-55s | Invariant Evasions | Invariant Detections | Recoveries | Safe Rejections | SDC (Silent)\n", "Experiment");
    printf("------------------------------------------------------------------------------------------------------------------------------------\n");
    experiment_result_t *results[6] = {&exp1, &exp2, &exp3, &exp4, &exp5, &exp6};
    for (int i = 0; i < 6; i++) {
        experiment_result_t *r = results[i];
        printf("%-55s | %4d (%5.1f%%)     | %4d (%5.1f%%)       | %4d       | %4d (%5.1f%%)   | %4d (%4.1f%%)\n",
               r->test_name,
               r->invariant_evasions, (double)r->invariant_evasions * 100.0 / r->total_trials,
               r->invariant_detections, (double)r->invariant_detections * 100.0 / r->total_trials,
               r->recoveries_claimed,
               r->safe_rejections, (double)r->safe_rejections * 100.0 / r->total_trials,
               r->silent_corruptions, (double)r->silent_corruptions * 100.0 / r->total_trials);
    }
    printf("------------------------------------------------------------------------------------------------------------------------------------\n\n");
}

int main(void) {
    run_audit_suite();
    return 0;
}
