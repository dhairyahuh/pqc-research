#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include "algorithms/source_ref/mlkem_fault_hooks.h"

#define SS_BYTES 32
#define CT_BYTES 1088
#define SK_BYTES 2400
#define PK_BYTES 1184

int mlkem768_keypair(uint8_t *pk, uint8_t *sk);
int mlkem768_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int mlkem768_dec_monitored(uint8_t *ss, const uint8_t *ct, const uint8_t *sk, uint32_t *internal_status);
void mlkem768_shake256(uint8_t *out, size_t outlen, const uint8_t *in, size_t inlen);

int randombytes(uint8_t *out, size_t outlen) {
    for (size_t i = 0; i < outlen; i++) out[i] = (uint8_t)(rand() & 0xFF);
    return 0;
}

static void compute_expected_rejection_key(uint8_t ss_rej[SS_BYTES], const uint8_t sk[SK_BYTES], const uint8_t ct[CT_BYTES]) {
    uint8_t z_ct[SS_BYTES + CT_BYTES];
    memcpy(z_ct, sk + SK_BYTES - SS_BYTES, SS_BYTES);
    memcpy(z_ct + SS_BYTES, ct, CT_BYTES);
    mlkem768_shake256(ss_rej, SS_BYTES, z_ct, SS_BYTES + CT_BYTES);
}

int main(void) {
    FILE *fp = fopen("phase10_corrected_reproduction/raw_production_trials.csv", "w");
    if (!fp) {
        perror("Failed to open raw_production_trials.csv");
        return 1;
    }

    fprintf(fp, "trial_id,target,stage,butterfly,bit,fault_semantics,armed,trigger_count,"
                "mismatch_count,retry_attempt_count,recovered_count,persistent_count,"
                "decaps_rc,internal_status,matches_valid_key,matches_rejection_key,outcome\n");

    ntt_native_monitor_configure(NTT_NATIVE_MONITOR_RECOMPUTED_T, true, 0x7F);

    uint8_t pk[PK_BYTES], sk[SK_BYTES], ct[CT_BYTES], ss_expected[SS_BYTES], ss_out[SS_BYTES], ss_rej_expected[SS_BYTES];
    uint32_t status = 0;
    int trial_id = 0;

    /* =========================================================================
     * 1. Target F12: Clean Baseline Control (100 trials)
     * ========================================================================= */
    for (int t = 0; t < 100; t++) {
        srand(0x1337C0DE + t);
        mlkem768_keypair(pk, sk);
        mlkem768_enc(ct, ss_expected, pk);
        compute_expected_rejection_key(ss_rej_expected, sk, ct);

        mlkem_fault_reset();
        ntt_native_monitor_reset();

        status = 0;
        int rc = mlkem768_dec_monitored(ss_out, ct, sk, &status);

        bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        bool rej_match = (memcmp(ss_out, ss_rej_expected, SS_BYTES) == 0);

        const char *outcome;
        if (ss_match && status == 0x5A5A5A5A && g_ntt_native_monitor.mismatch_count == 0) {
            outcome = "CLEAN_SUCCESS";
        } else {
            outcome = "INCONCLUSIVE";
        }

        fprintf(fp, "%d,F12_CLEAN_BASELINE,0,0,0,NONE,0,%llu,%u,%u,%u,%u,%d,0x%08X,%d,%d,%s\n",
                trial_id++,
                (unsigned long long)g_mlkem_fault.trigger_count,
                g_ntt_native_monitor.mismatch_count,
                g_ntt_native_monitor.retry_attempt_count,
                g_ntt_native_monitor.recovered_count,
                g_ntt_native_monitor.persistent_count,
                rc, status, ss_match, rej_match, outcome);
    }

    /* =========================================================================
     * 2. Target F4: Transient Butterfly Fault (100 trials)
     * ========================================================================= */
    for (int t = 0; t < 100; t++) {
        srand(0x1337C0DE + t);
        mlkem768_keypair(pk, sk);
        mlkem768_enc(ct, ss_expected, pk);
        compute_expected_rejection_key(ss_rej_expected, sk, ct);

        unsigned stage = (t % 7) + 1;
        unsigned b_idx = (t * 13) % 128;
        uint8_t bit = t % 16;

        mlkem_fault_reset();
        mlkem_fault_arm_mid_ntt_locus(stage, b_idx, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
        g_mlkem_fault.persistent = false;
        ntt_native_monitor_reset();

        status = 0;
        int rc = mlkem768_dec_monitored(ss_out, ct, sk, &status);

        bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        bool rej_match = (memcmp(ss_out, ss_rej_expected, SS_BYTES) == 0);

        const char *outcome;
        if (g_mlkem_fault.trigger_count == 0) {
            outcome = "FAULT_NOT_TRIGGERED";
        } else if (ss_match && status == 0x5A5A5A5A && g_ntt_native_monitor.recovered_count > 0 && g_ntt_native_monitor.persistent_count == 0) {
            outcome = "GENUINE_RECOVERY";
        } else if (!ss_match && status == 0x5A5A5A5A) {
            outcome = "SDC_ACCEPTED_INCORRECT";
        } else if (rej_match && (status == 0xFFFFFFFF || status == 0xA5A5A5A5)) {
            outcome = "SAFE_FAIL_STOP";
        } else {
            outcome = "INCONCLUSIVE";
        }

        fprintf(fp, "%d,F4_TRANSIENT_RECOVERY,%u,%u,%u,TRANSIENT_BIT_FLIP,1,%llu,%u,%u,%u,%u,%d,0x%08X,%d,%d,%s\n",
                trial_id++, stage, b_idx, bit,
                (unsigned long long)g_mlkem_fault.trigger_count,
                g_ntt_native_monitor.mismatch_count,
                g_ntt_native_monitor.retry_attempt_count,
                g_ntt_native_monitor.recovered_count,
                g_ntt_native_monitor.persistent_count,
                rc, status, ss_match, rej_match, outcome);
    }

    /* =========================================================================
     * 3. Target F5A: Recurring Bit-Inversion Fault (100 trials)
     * ========================================================================= */
    for (int t = 0; t < 100; t++) {
        srand(0x1337C0DE + t);
        mlkem768_keypair(pk, sk);
        mlkem768_enc(ct, ss_expected, pk);
        compute_expected_rejection_key(ss_rej_expected, sk, ct);

        unsigned stage = (t % 7) + 1;
        unsigned b_idx = (t * 13) % 128;
        uint8_t bit = t % 16;

        mlkem_fault_reset();
        mlkem_fault_arm_mid_ntt_locus(stage, b_idx, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
        g_mlkem_fault.persistent = true;
        ntt_native_monitor_reset();

        status = 0;
        int rc = mlkem768_dec_monitored(ss_out, ct, sk, &status);

        bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        bool rej_match = (memcmp(ss_out, ss_rej_expected, SS_BYTES) == 0);

        const char *outcome;
        if (g_mlkem_fault.trigger_count == 0) {
            outcome = "FAULT_NOT_TRIGGERED";
        } else if (rej_match && status == 0xFFFFFFFF && g_ntt_native_monitor.persistent_count > 0 && !ss_match) {
            outcome = "SAFE_FAIL_STOP";
        } else if (!ss_match && status == 0x5A5A5A5A) {
            outcome = "SDC_ACCEPTED_INCORRECT";
        } else if (ss_match) {
            outcome = "GENUINE_RECOVERY";
        } else if (rej_match && status == 0xA5A5A5A5) {
            outcome = "DOWNSTREAM_FO_REJECTION";
        } else {
            outcome = "INCONCLUSIVE";
        }

        fprintf(fp, "%d,F5A_RECURRING_BITFLIP,%u,%u,%u,RECURRING_BIT_INVERSION,1,%llu,%u,%u,%u,%u,%d,0x%08X,%d,%d,%s\n",
                trial_id++, stage, b_idx, bit,
                (unsigned long long)g_mlkem_fault.trigger_count,
                g_ntt_native_monitor.mismatch_count,
                g_ntt_native_monitor.retry_attempt_count,
                g_ntt_native_monitor.recovered_count,
                g_ntt_native_monitor.persistent_count,
                rc, status, ss_match, rej_match, outcome);
    }

    /* =========================================================================
     * 4. Target F5B: True Hardware Stuck-At-0 Fault (100 trials)
     * ========================================================================= */
    for (int t = 0; t < 100; t++) {
        srand(0x1337C0DE + t);
        mlkem768_keypair(pk, sk);
        mlkem768_enc(ct, ss_expected, pk);
        compute_expected_rejection_key(ss_rej_expected, sk, ct);

        unsigned stage = (t % 7) + 1;
        unsigned b_idx = (t * 13) % 128;

        mlkem_fault_reset();
        mlkem_fault_arm_mid_ntt_locus(stage, b_idx, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_FORCE_VALUE, 0, 0, 0);
        g_mlkem_fault.persistent = true;
        ntt_native_monitor_reset();

        status = 0;
        int rc = mlkem768_dec_monitored(ss_out, ct, sk, &status);

        bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        bool rej_match = (memcmp(ss_out, ss_rej_expected, SS_BYTES) == 0);

        const char *outcome;
        if (g_mlkem_fault.trigger_count == 0) {
            outcome = "FAULT_NOT_TRIGGERED";
        } else if (rej_match && status == 0xFFFFFFFF && g_ntt_native_monitor.persistent_count > 0 && !ss_match) {
            outcome = "SAFE_FAIL_STOP";
        } else if (!ss_match && status == 0x5A5A5A5A) {
            outcome = "SDC_ACCEPTED_INCORRECT";
        } else if (ss_match) {
            outcome = "GENUINE_RECOVERY";
        } else if (rej_match && status == 0xA5A5A5A5) {
            outcome = "DOWNSTREAM_FO_REJECTION";
        } else {
            outcome = "INCONCLUSIVE";
        }

        fprintf(fp, "%d,F5B_STUCK_AT_ZERO,%u,%u,0,HARDWARE_STUCK_AT_ZERO,1,%llu,%u,%u,%u,%u,%d,0x%08X,%d,%d,%s\n",
                trial_id++, stage, b_idx,
                (unsigned long long)g_mlkem_fault.trigger_count,
                g_ntt_native_monitor.mismatch_count,
                g_ntt_native_monitor.retry_attempt_count,
                g_ntt_native_monitor.recovered_count,
                g_ntt_native_monitor.persistent_count,
                rc, status, ss_match, rej_match, outcome);
    }

    fclose(fp);
    printf("Successfully executed 400 production-object trials and wrote raw_production_trials.csv\n");
    return 0;
}
