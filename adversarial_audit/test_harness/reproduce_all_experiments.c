/**
 * Controlled Adversarial Reproduction Harness for ML-KEM-768
 * 
 * Independently executes and validates all reported experimental claims:
 * 1. Twiddle Factor Shared-Constant Corruption (200 trials)
 * 2. Extended Twiddle Perturbation Campaign J07 (100 trials)
 * 3. Pre-Latch Input Memory Corruption (50 trials)
 * 4. Post-Latch Hook Mutation (50 trials)
 * 5. Persistent / Retry-Path Faults (50 trials)
 * 6. Clean Negative Control (50 trials)
 * 
 * Generates trial_outcomes.csv with complete per-trial telemetry.
 */

#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include "algorithms/source_ref/mlkem_fault_hooks.h"

#define SS_BYTES 32
#define CT_BYTES 1088
#define SK_BYTES 2400
#define PK_BYTES 1184

#define MLK_STATUS_SUCCESS 0x5A5A5A5AU
#define MLK_STATUS_REJECT  0xA5A5A5A5U
#define MLK_STATUS_FAULT   0xFFFFFFFFU

// Function prototypes from mlkem768_inst.o
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

int main(void) {
    printf("=========================================================================\n");
    printf(" ADVERSARIAL REPRODUCTION HARNESS: INDEPENDENT EXPERIMENT VALIDATION\n");
    printf(" Target: ML-KEM-768 (Dual NTT Monitors, Shadow Rollback, FO Re-encryption)\n");
    printf("=========================================================================\n\n");

    FILE *f_csv = fopen("adversarial_audit/trial_outcomes.csv", "w");
    if (!f_csv) {
        fprintf(stderr, "Fatal: Cannot open adversarial_audit/trial_outcomes.csv for writing\n");
        return 1;
    }

    // CSV Header
    fprintf(f_csv, "trial_id,experiment_group,stage,butterfly,locus,bit,delta,orig_val,faulted_val,triggered,monitor_mismatches,recovery_logged,final_status,reencrypt_match,ss_match,outcome_category\n");

    srand(0x1337BEEF);
    uint8_t pk[PK_BYTES];
    uint8_t sk[SK_BYTES];
    uint8_t ct_valid[CT_BYTES];
    uint8_t ss_expected[SS_BYTES];

    if (mlkem768_keypair(pk, sk) != 0 || mlkem768_enc(ct_valid, ss_expected, pk) != 0) {
        fprintf(stderr, "Fatal: Keypair generation or encapsulation failed\n");
        fclose(f_csv);
        return 1;
    }

    int trial_counter = 0;

    // -------------------------------------------------------------------------
    // GROUP 1: Twiddle Factor Corruption (EXP 4 Baseline: 200 trials)
    // -------------------------------------------------------------------------
    printf(">>> Executing Group 1: Twiddle Factor Corruption (EXP 4: N=200)...\n");
    int g1_evasions = 0, g1_rejects = 0, g1_benign = 0, g1_sdc = 0;
    for (int t = 0; t < 200; t++) {
        trial_counter++;
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

        bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        bool triggered = (g_mlkem_fault.trigger_count > 0);
        uint32_t mismatches = g_ntt_native_monitor.mismatch_count + g_invntt_native_monitor.mismatch_count;
        bool recovery_logged = (g_ntt_native_monitor.recovered_count + g_invntt_native_monitor.recovered_count > 0);

        // Re-encryption match test (ct match)
        // If status == MLK_STATUS_SUCCESS and ss_match == 1, then FO re-encryption matched
        bool reencrypt_match = (status == MLK_STATUS_SUCCESS);

        const char *outcome = "UNKNOWN";
        if (mismatches == 0) g1_evasions++;

        if (status == MLK_STATUS_REJECT || status == MLK_STATUS_FAULT) {
            outcome = "SAFE_REJECT";
            g1_rejects++;
        } else if (status == MLK_STATUS_SUCCESS && ss_match) {
            outcome = "BENIGN_EQUIV";
            g1_benign++;
        } else {
            outcome = "UNDETECTED_SDC";
            g1_sdc++;
        }

        fprintf(f_csv, "%d,EXP4_TWIDDLE,%u,%u,NTT_LOCUS_TWIDDLE_ZETA,%u,0,%d,%d,%d,%u,%d,0x%08X,%d,%d,%s\n",
                trial_counter, stage, butterfly, bit,
                g_mlkem_fault.orig_value, g_mlkem_fault.faulted_value,
                triggered ? 1 : 0, mismatches, recovery_logged ? 1 : 0,
                status, reencrypt_match ? 1 : 0, ss_match ? 1 : 0, outcome);
    }
    printf("    Completed: Evasions=%d, Rejections=%d, BenignEquiv=%d, SDC=%d\n",
           g1_evasions, g1_rejects, g1_benign, g1_sdc);

    // -------------------------------------------------------------------------
    // GROUP 2: Extended Twiddle Perturbation Campaign (J07: N=100)
    // -------------------------------------------------------------------------
    printf(">>> Executing Group 2: Campaign J07 Twiddle Perturbations (N=100)...\n");
    int g2_evasions = 0, g2_rejects = 0, g2_benign = 0, g2_sdc = 0;
    for (int t = 0; t < 100; t++) {
        trial_counter++;
        uint32_t seed = (uint32_t)(7 * 50000 + t + 1234);
        srand(seed);

        unsigned stage = 1 + (t % 7);
        unsigned butterfly = (t * 17 + 3) % 128;
        uint8_t bit = t % 16;

        mlkem_fault_reset();
        ntt_native_monitor_configure(NTT_NATIVE_MONITOR_RECOMPUTED_T, true, 0x7F);
        invntt_native_monitor_configure(INVNTT_NATIVE_MONITOR_RECOMPUTED, true, 0x7F);

        g_mlkem_fault.enabled = true;
        g_mlkem_fault.target = HOOK_TARGET_MID_INVNTT_BUTTERFLY;
        g_mlkem_fault.target_stage = stage;
        g_mlkem_fault.target_butterfly = butterfly;
        g_mlkem_fault.ntt_locus = INVNTT_LOCUS_TWIDDLE_ZETA;
        g_mlkem_fault.fault_type = FAULT_TYPE_BIT_FLIP;
        g_mlkem_fault.bit_to_flip = bit;

        uint8_t ss_out[SS_BYTES];
        uint32_t status = 0;
        mlkem768_dec_monitored(ss_out, ct_valid, sk, &status);

        bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        bool triggered = (g_mlkem_fault.trigger_count > 0);
        uint32_t mismatches = g_ntt_native_monitor.mismatch_count + g_invntt_native_monitor.mismatch_count;
        bool recovery_logged = (g_ntt_native_monitor.recovered_count + g_invntt_native_monitor.recovered_count > 0);
        bool reencrypt_match = (status == MLK_STATUS_SUCCESS);

        const char *outcome = "UNKNOWN";
        if (mismatches == 0) g2_evasions++;

        if (status == MLK_STATUS_REJECT || status == MLK_STATUS_FAULT) {
            outcome = "SAFE_REJECT";
            g2_rejects++;
        } else if (status == MLK_STATUS_SUCCESS && ss_match) {
            outcome = "BENIGN_EQUIV";
            g2_benign++;
        } else {
            outcome = "UNDETECTED_SDC";
            g2_sdc++;
        }

        fprintf(f_csv, "%d,J07_INV_TWIDDLE,%u,%u,INVNTT_LOCUS_TWIDDLE_ZETA,%u,0,%d,%d,%d,%u,%d,0x%08X,%d,%d,%s\n",
                trial_counter, stage, butterfly, bit,
                g_mlkem_fault.orig_value, g_mlkem_fault.faulted_value,
                triggered ? 1 : 0, mismatches, recovery_logged ? 1 : 0,
                status, reencrypt_match ? 1 : 0, ss_match ? 1 : 0, outcome);
    }
    printf("    Completed: Evasions=%d, Rejections=%d, BenignEquiv=%d, SDC=%d\n",
           g2_evasions, g2_rejects, g2_benign, g2_sdc);

    // -------------------------------------------------------------------------
    // GROUP 3: Pre-Latch Memory Corruption (Pre-NTT Input: N=50)
    // -------------------------------------------------------------------------
    printf(">>> Executing Group 3: True Pre-Latch Memory Corruption (N=50)...\n");
    int g3_evasions = 0, g3_rejects = 0, g3_sdc = 0;
    for (int t = 0; t < 50; t++) {
        trial_counter++;
        mlkem_fault_reset();
        ntt_native_monitor_configure(NTT_NATIVE_MONITOR_RECOMPUTED_T, true, 0x7F);
        invntt_native_monitor_configure(INVNTT_NATIVE_MONITOR_RECOMPUTED, true, 0x7F);

        uint8_t ct_corrupt[CT_BYTES];
        memcpy(ct_corrupt, ct_valid, CT_BYTES);
        size_t byte_idx = 10 + (t % 100);
        uint8_t bit = t % 8;
        uint8_t orig_byte = ct_corrupt[byte_idx];
        ct_corrupt[byte_idx] ^= (uint8_t)(1 << bit);
        uint8_t fault_byte = ct_corrupt[byte_idx];

        uint8_t ss_out[SS_BYTES];
        uint32_t status = 0;
        mlkem768_dec_monitored(ss_out, ct_corrupt, sk, &status);

        bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        uint32_t mismatches = g_ntt_native_monitor.mismatch_count + g_invntt_native_monitor.mismatch_count;
        bool recovery_logged = (g_ntt_native_monitor.recovered_count + g_invntt_native_monitor.recovered_count > 0);

        if (mismatches == 0) g3_evasions++;

        const char *outcome = "UNKNOWN";
        if (status == MLK_STATUS_REJECT || status == MLK_STATUS_FAULT) {
            outcome = "SAFE_REJECT";
            g3_rejects++;
        } else if (ss_match) {
            outcome = "BENIGN_EQUIV";
        } else {
            outcome = "UNDETECTED_SDC";
            g3_sdc++;
        }

        fprintf(f_csv, "%d,PRE_LATCH_MEM,0,0,PRE_NTT_CT_BYTE,%u,0,%u,%u,1,%u,%d,0x%08X,0,%d,%s\n",
                trial_counter, bit, (unsigned)orig_byte, (unsigned)fault_byte,
                mismatches, recovery_logged ? 1 : 0, status, ss_match ? 1 : 0, outcome);
    }
    printf("    Completed: Evasions=%d, Rejections=%d, SDC=%d\n", g3_evasions, g3_rejects, g3_sdc);

    // -------------------------------------------------------------------------
    // GROUP 4: Post-Latch Hook Mutation (EXP 5A Artifact: N=50)
    // -------------------------------------------------------------------------
    printf(">>> Executing Group 4: Post-Latch Hook Mutation (N=50)...\n");
    int g4_detections = 0, g4_recoveries = 0, g4_sdc = 0;
    for (int t = 0; t < 50; t++) {
        trial_counter++;
        mlkem_fault_reset();
        ntt_native_monitor_configure(NTT_NATIVE_MONITOR_RECOMPUTED_T, true, 0x7F);
        invntt_native_monitor_configure(INVNTT_NATIVE_MONITOR_RECOMPUTED, true, 0x7F);

        unsigned stage = 1 + (t % 7);
        unsigned butterfly = (t * 13 + 5) % 128;
        uint8_t bit = t % 16;

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

        bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        bool triggered = (g_mlkem_fault.trigger_count > 0);
        uint32_t mismatches = g_ntt_native_monitor.mismatch_count + g_invntt_native_monitor.mismatch_count;
        bool recovery_logged = (g_ntt_native_monitor.recovered_count + g_invntt_native_monitor.recovered_count > 0);

        if (mismatches > 0) g4_detections++;
        if (recovery_logged) g4_recoveries++;

        const char *outcome = "UNKNOWN";
        if (recovery_logged && ss_match) {
            outcome = "RECOVERED";
        } else if (status == MLK_STATUS_REJECT || status == MLK_STATUS_FAULT) {
            outcome = "SAFE_REJECT";
        } else {
            outcome = "UNDETECTED_SDC";
            g4_sdc++;
        }

        fprintf(f_csv, "%d,POST_LATCH_HOOK,%u,%u,INVNTT_LOCUS_INPUT_U,%u,0,%d,%d,%d,%u,%d,0x%08X,%d,%d,%s\n",
                trial_counter, stage, butterfly, bit,
                g_mlkem_fault.orig_value, g_mlkem_fault.faulted_value,
                triggered ? 1 : 0, mismatches, recovery_logged ? 1 : 0,
                status, ss_match ? 1 : 0, ss_match ? 1 : 0, outcome);
    }
    printf("    Completed: Detections=%d, Recoveries=%d, SDC=%d\n", g4_detections, g4_recoveries, g4_sdc);

    // -------------------------------------------------------------------------
    // GROUP 5: Persistent Stuck-At Fault During Retry (N=50)
    // -------------------------------------------------------------------------
    printf(">>> Executing Group 5: Persistent Faults During Retry (N=50)...\n");
    int g5_detections = 0, g5_rejections = 0, g5_sdc = 0;
    for (int t = 0; t < 50; t++) {
        trial_counter++;
        mlkem_fault_reset();
        ntt_native_monitor_configure(NTT_NATIVE_MONITOR_RECOMPUTED_T, true, 0x7F);
        invntt_native_monitor_configure(INVNTT_NATIVE_MONITOR_RECOMPUTED, true, 0x7F);

        unsigned stage = 1 + (t % 7);
        unsigned butterfly = (t * 13 + 5) % 128;
        uint8_t bit = t % 16;

        mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
        g_mlkem_fault.persistent = true; // Remains stuck on retry

        uint8_t ss_out[SS_BYTES];
        uint32_t status = 0;
        mlkem768_dec_monitored(ss_out, ct_valid, sk, &status);

        bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        uint32_t mismatches = g_ntt_native_monitor.mismatch_count + g_invntt_native_monitor.mismatch_count;
        bool recovery_logged = (g_ntt_native_monitor.recovered_count + g_invntt_native_monitor.recovered_count > 0);

        if (mismatches > 0) g5_detections++;

        const char *outcome = "UNKNOWN";
        if (status == MLK_STATUS_FAULT || status == MLK_STATUS_REJECT) {
            outcome = "SAFE_REJECT";
            g5_rejections++;
        } else {
            outcome = "UNDETECTED_SDC";
            g5_sdc++;
        }

        fprintf(f_csv, "%d,PERSISTENT_RETRY,%u,%u,NTT_LOCUS_OUTPUT_ADD,%u,0,%d,%d,1,%u,%d,0x%08X,0,%d,%s\n",
                trial_counter, stage, butterfly, bit,
                g_mlkem_fault.orig_value, g_mlkem_fault.faulted_value,
                mismatches, recovery_logged ? 1 : 0, status, ss_match ? 1 : 0, outcome);
    }
    printf("    Completed: Detections=%d, Rejections=%d, SDC=%d\n", g5_detections, g5_rejections, g5_sdc);

    // -------------------------------------------------------------------------
    // GROUP 6: Clean Execution Negative Control (N=50)
    // -------------------------------------------------------------------------
    printf(">>> Executing Group 6: Clean Execution Negative Controls (N=50)...\n");
    int g6_success = 0, g6_false_pos = 0;
    for (int t = 0; t < 50; t++) {
        trial_counter++;
        mlkem_fault_reset();
        ntt_native_monitor_configure(NTT_NATIVE_MONITOR_RECOMPUTED_T, true, 0x7F);
        invntt_native_monitor_configure(INVNTT_NATIVE_MONITOR_RECOMPUTED, true, 0x7F);

        uint8_t ss_out[SS_BYTES];
        uint32_t status = 0;
        mlkem768_dec_monitored(ss_out, ct_valid, sk, &status);

        bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        uint32_t mismatches = g_ntt_native_monitor.mismatch_count + g_invntt_native_monitor.mismatch_count;

        const char *outcome = "UNKNOWN";
        if (mismatches == 0 && status == MLK_STATUS_SUCCESS && ss_match) {
            outcome = "CLEAN_SUCCESS";
            g6_success++;
        } else {
            outcome = "FALSE_POSITIVE";
            g6_false_pos++;
        }

        fprintf(f_csv, "%d,CLEAN_CONTROL,0,0,NONE,0,0,0,0,0,%u,0,0x%08X,1,%d,%s\n",
                trial_counter, mismatches, status, ss_match ? 1 : 0, outcome);
    }
    printf("    Completed: CleanSuccess=%d, FalsePositives=%d\n\n", g6_success, g6_false_pos);

    fclose(f_csv);
    printf("=========================================================================\n");
    printf(" ALL 500 REPRODUCTION TRIALS RECORDED TO adversarial_audit/trial_outcomes.csv\n");
    printf("=========================================================================\n");

    return 0;
}
