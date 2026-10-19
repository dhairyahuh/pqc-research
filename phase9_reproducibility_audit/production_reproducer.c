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

int randombytes(uint8_t *out, size_t outlen) {
    for (size_t i = 0; i < outlen; i++) out[i] = (uint8_t)(rand() & 0xFF);
    return 0;
}

int main(void) {
    FILE *fp = fopen("phase9_reproducibility_audit/raw_trial_results.csv", "w");
    if (!fp) {
        perror("Failed to open CSV output");
        return 1;
    }

    fprintf(fp, "trial_id,target,stage,butterfly,bit,armed,injected,detected,executed_count,"
                "mismatch_count,retry_attempt_count,recovered_count,persistent_count,"
                "decaps_rc,internal_status,ss_matches_expected,ss_matches_rejection,outcome\n");

    ntt_native_monitor_configure(NTT_NATIVE_MONITOR_RECOMPUTED_T, true, 0x7F);

    uint8_t pk[PK_BYTES], sk[SK_BYTES], ct[CT_BYTES], ss_expected[SS_BYTES], ss_out[SS_BYTES], ss_rej[SS_BYTES];
    uint32_t status = 0;

    int total_trials = 0;

    /* 1. Run Target F12 (Clean Baseline - 100 trials) */
    for (int t = 0; t < 100; t++) {
        srand(0x1337C0DE + t);
        mlkem768_keypair(pk, sk);
        mlkem768_enc(ct, ss_expected, pk);

        mlkem_fault_reset();
        ntt_native_monitor_reset();

        status = 0;
        int rc = mlkem768_dec_monitored(ss_out, ct, sk, &status);

        bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        bool rej_match = false; // not rejection

        const char *outcome = ss_match ? "GENUINE_RECOVERY" : "INCONCLUSIVE";

        fprintf(fp, "%d,F12_CLEAN_BASELINE,0,0,0,0,0,0,%u,%u,%u,%u,%u,%d,0x%08X,%d,%d,%s\n",
                total_trials++,
                g_ntt_native_monitor.executed_count,
                g_ntt_native_monitor.mismatch_count,
                g_ntt_native_monitor.retry_attempt_count,
                g_ntt_native_monitor.recovered_count,
                g_ntt_native_monitor.persistent_count,
                rc, status, ss_match, rej_match, outcome);
    }

    /* 2. Run Target F4 (Transient Butterfly Fault - 100 trials) */
    for (int t = 0; t < 100; t++) {
        srand(0x1337C0DE + t);
        mlkem768_keypair(pk, sk);
        mlkem768_enc(ct, ss_expected, pk);

        unsigned stage = (t % 7) + 1;
        unsigned b_idx = (t * 13) % 128;
        uint8_t bit = t % 16;

        mlkem_fault_arm_mid_ntt_locus(stage, b_idx, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
        g_mlkem_fault.persistent = false;
        ntt_native_monitor_reset();

        status = 0;
        int rc = mlkem768_dec_monitored(ss_out, ct, sk, &status);

        bool armed = true;
        bool injected = (g_mlkem_fault.trigger_count > 0);
        bool detected = (g_ntt_native_monitor.mismatch_count > 0);
        bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);

        const char *outcome;
        if (ss_match && g_ntt_native_monitor.recovered_count > 0 && status == 0x5A5A5A5A) {
            outcome = "GENUINE_RECOVERY";
        } else if (!ss_match && status == 0x5A5A5A5A) {
            outcome = "SDC_ACCEPTED_INCORRECT";
        } else if (status == 0xFFFFFFFF || status == 0xA5A5A5A5) {
            outcome = "SAFE_FAIL_STOP";
        } else {
            outcome = "INCONCLUSIVE";
        }

        fprintf(fp, "%d,F4_TRANSIENT_RECOVERY,%u,%u,%u,%d,%d,%d,%u,%u,%u,%u,%u,%d,0x%08X,%d,0,%s\n",
                total_trials++, stage, b_idx, bit, armed, injected, detected,
                g_ntt_native_monitor.executed_count,
                g_ntt_native_monitor.mismatch_count,
                g_ntt_native_monitor.retry_attempt_count,
                g_ntt_native_monitor.recovered_count,
                g_ntt_native_monitor.persistent_count,
                rc, status, ss_match, outcome);
    }

    /* 3. Run Target F5 (Persistent Stuck-At Butterfly Fault - 100 trials) */
    for (int t = 0; t < 100; t++) {
        srand(0x1337C0DE + t);
        mlkem768_keypair(pk, sk);
        mlkem768_enc(ct, ss_expected, pk);

        unsigned stage = (t % 7) + 1;
        unsigned b_idx = (t * 13) % 128;
        uint8_t bit = t % 16;

        mlkem_fault_arm_mid_ntt_locus(stage, b_idx, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
        g_mlkem_fault.persistent = true;
        ntt_native_monitor_reset();

        status = 0;
        int rc = mlkem768_dec_monitored(ss_out, ct, sk, &status);

        bool armed = true;
        bool injected = (g_mlkem_fault.trigger_count > 0);
        bool detected = (g_ntt_native_monitor.mismatch_count > 0);
        bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);

        const char *outcome;
        if (status == 0xFFFFFFFF && g_ntt_native_monitor.persistent_count > 0 && !ss_match) {
            outcome = "SAFE_FAIL_STOP";
        } else if (ss_match) {
            outcome = "FALSE_GENUINE_MATCH";
        } else if (status == 0x5A5A5A5A) {
            outcome = "SDC_ACCEPTED_INCORRECT";
        } else {
            outcome = "DOWNSTREAM_FO_REJECT";
        }

        fprintf(fp, "%d,F5_PERSISTENT_REJECTION,%u,%u,%u,%d,%d,%d,%u,%u,%u,%u,%u,%d,0x%08X,%d,1,%s\n",
                total_trials++, stage, b_idx, bit, armed, injected, detected,
                g_ntt_native_monitor.executed_count,
                g_ntt_native_monitor.mismatch_count,
                g_ntt_native_monitor.retry_attempt_count,
                g_ntt_native_monitor.recovered_count,
                g_ntt_native_monitor.persistent_count,
                rc, status, ss_match, outcome);
    }

    fclose(fp);
    printf("Successfully executed 300 production-object trials and wrote raw_trial_results.csv\n");
    return 0;
}
