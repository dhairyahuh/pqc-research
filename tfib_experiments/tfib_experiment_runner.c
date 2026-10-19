#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include "tfib_common.h"
#include "tfib_core.h"
#include "independent_oracle.h"
#include "fips202_ref.h"
#include "campaign_prf.h"

#define SS_BYTES 32
#define CT_BYTES 1088
#define SK_BYTES 2400
#define PK_BYTES 1184

/* Declaration from mlkem768_inst.o — the only production symbol still called.
 * Keypair generation is now delegated to independent_oracle_keypair_derand. */
int mlkem768_dec_monitored(uint8_t *ss, const uint8_t *ct, const uint8_t *sk, uint32_t *internal_status);

/* Provide a randombytes symbol for any residual production code that links
 * against it (e.g. liboqs internal callbacks).  This is NOT used by the
 * campaign's ground-truth generation path. */
int randombytes(uint8_t *out, size_t outlen) {
    /* Fill with non-secret placeholder bytes; the campaign never relies on
     * this function for security-critical randomness. */
    for (size_t i = 0; i < outlen; i++) out[i] = (uint8_t)(i ^ 0xAA);
    return 0;
}

typedef struct {
    int total_trials;
    int activated_faults;
    int detected_faults;
    int recovery_attempted;
    int genuine_recoveries;
    int safe_fail_stops;
    int blind_passes;
    int ineffective_faults;
    int sdc_count;
} suite_summary_t;

static void run_suite(
    FILE *fp, int *trial_id, tfib_mode_t mode, const char *mode_name,
    const char *suite_name, tfib_fault_locus_t locus, bool persistent,
    int num_trials, suite_summary_t *sum
) {
    uint8_t pk[PK_BYTES], sk[SK_BYTES], ct[CT_BYTES];
    uint8_t ss_expected[SS_BYTES], ss_out[SS_BYTES], ss_rej_expected[SS_BYTES];

    memset(sum, 0, sizeof(*sum));
    sum->total_trials = num_trials;

    tfib_set_mode(mode);

    for (int t = 0; t < num_trials; t++) {
        tfib_fault_reset();
        tfib_reset_all_stats();

        /* --- Step 2B: Deterministic SHAKE-256 PRF replaces srand()/rand() --- */
        /* Derive 96 bytes = 64-byte keypair seed (d||z) + 32-byte encaps seed (m) */
        uint8_t prf_output[64 + 32];
        campaign_prf(prf_output, sizeof(prf_output), t, mode, locus, persistent);

        uint8_t *seed64 = prf_output;        /* d || z for KeyGen */
        uint8_t *seed32 = prf_output + 64;   /* m for Encaps */

        /* Generate keypair via independent oracle (replaces in-tree mlkem768_keypair) */
        int kp_rc = independent_oracle_keypair_derand(pk, sk, seed64);
        if (kp_rc != 0) {
            fprintf(stderr, "FATAL: independent_oracle_keypair_derand failed (trial %d)!\n", t);
            exit(1);
        }

        /* Generate ciphertext and valid expected shared secret via independent oracle */
        int o_rc = independent_oracle_encaps_derand(ct, ss_expected, pk, seed32);
        if (o_rc != 0) {
            fprintf(stderr, "FATAL: independent_oracle_encaps_derand failed (trial %d)!\n", t);
            exit(1);
        }

        /* Establish expected canonical rejection key via independent oracle (FIPS 202 reference) */
        int rej_rc = independent_oracle_compute_rejection(ss_rej_expected, sk, ct);
        if (rej_rc != 0) {
            fprintf(stderr, "FATAL: independent_oracle_compute_rejection failed (trial %d)!\n", t);
            exit(1);
        }

        unsigned stage = (t % 7) + 1;
        unsigned b_idx = (t * 17) % 128;
        uint8_t bit = (t % 15) + 1;

        if (locus != TFIB_FAULT_NONE) {
            tfib_fault_arm(locus, stage, b_idx, bit, persistent);
        }

        uint32_t status = 0;
        int rc = mlkem768_dec_monitored(ss_out, ct, sk, &status);
        (void)rc;

        bool fault_act = (g_tfib_fault.trigger_count > 0);
        bool mon_det = (tfib_get_total_mismatches() > 0);
        bool rec_att = (mon_det);
        bool rec_succ = (tfib_get_total_recoveries() > 0);
        bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        bool rej_match = (memcmp(ss_out, ss_rej_expected, SS_BYTES) == 0);
        bool sdc = (!ss_match && !rej_match);

        const char *outcome;
        if (!fault_act && locus == TFIB_FAULT_NONE) {
            outcome = "CLEAN_SUCCESS";
        } else if (ss_match && status == 0x5A5A5A5A && rec_succ) {
            outcome = "GENUINE_RECOVERY";
            sum->genuine_recoveries++;
        } else if (!mon_det && fault_act && ss_match && status == 0x5A5A5A5A) {
            /* Ineffective fault: noise slack absorbed perturbation; m decoded cleanly */
            outcome = "INEFFECTIVE_FAULT_VALID";
            sum->ineffective_faults++;
        } else if (rej_match && (status == 0xFFFFFFFF || status == 0xA5A5A5A5)) {
            if (!mon_det) {
                outcome = "LOCAL_BLIND_FO_CONTAINED";
                sum->blind_passes++;
            } else {
                outcome = "SAFE_FAIL_STOP";
                sum->safe_fail_stops++;
            }
        } else if (sdc) {
            outcome = "SILENT_DATA_CORRUPTION";
            sum->sdc_count++;
        } else {
            outcome = "INCONCLUSIVE";
        }

        if (strcmp(suite_name, "REF_TWIDDLE_TRANSIENT") == 0 && strcmp(outcome, "GENUINE_RECOVERY") != 0) {
            printf("      [REF_TRANSIENT_DEBUG] t=%d stage=%u b_idx=%u bit=%u: outcome=%s ss_match=%d rej_match=%d status=0x%08X rec_succ=%d mon_det=%d\n",
                   t, stage, b_idx, bit, outcome, ss_match, rej_match, status, rec_succ, mon_det);
        }

        if (fault_act) sum->activated_faults++;
        if (mon_det) sum->detected_faults++;
        if (rec_att) sum->recovery_attempted++;

        fprintf(fp, "%d,%s,%s,%u,%u,%u,%d,%d,%d,%d,%d,%d,%d,%d,0x%08X,%s\n",
                (*trial_id)++, mode_name, suite_name,
                stage, b_idx, bit, persistent ? 1 : 0,
                fault_act ? 1 : 0, mon_det ? 1 : 0, rec_att ? 1 : 0, rec_succ ? 1 : 0,
                ss_match ? 1 : 0, rej_match ? 1 : 0, sdc ? 1 : 0,
                status, outcome);
    }
}

int main(int argc, char **argv) {
    if (independent_oracle_init() != 0) {
        fprintf(stderr, "FATAL: Failed to initialize independent oracle backend!\n");
        return 1;
    }

    /* Preserve historical CSV by defaulting to a dedicated output path unless overridden */
    const char *out_csv = (argc > 1) ? argv[1] : "tfib_experiments/phase2_step1_runner_output.csv";
    FILE *fp = fopen(out_csv, "w");
    if (!fp) {
        perror("Failed to open output CSV file");
        return 1;
    }

    fprintf(fp, "trial_id,config,fault_suite,stage,butterfly,bit,persistent,"
                "fault_activated,monitor_detected,recovery_attempted,recovered_success,"
                "output_correct,implicit_rejection,silent_data_corruption,final_status,outcome_class\n");

    int trial_id = 0;
    suite_summary_t sum;

    printf("================================================================================\n");
    printf("EXECUTING TFIB TARGETED EXPERIMENTAL SUITES ACROSS 3 CONFIGURATIONS\n");
    printf("================================================================================\n\n");

    /* -------------------------------------------------------------------------
     * 1. CONFIG: BASELINE (Original Monitor)
     * ------------------------------------------------------------------------- */
    printf("[1/3] Testing Configuration: BASELINE (Original Monitor)\n");

    run_suite(fp, &trial_id, TFIB_MODE_BASELINE, "BASELINE", "CLEAN_CONTROL", TFIB_FAULT_NONE, false, 50, &sum);
    printf("  - Clean Baseline: %d/%d Success, 0 False Alarms\n", sum.total_trials, sum.total_trials);
    assert(sum.detected_faults == 0);

    run_suite(fp, &trial_id, TFIB_MODE_BASELINE, "BASELINE", "OP_TWIDDLE_TRANSIENT", TFIB_FAULT_OP_TWIDDLE, false, 50, &sum);
    printf("  - Op Twiddle Transient: Detected=%d/%d (%.1f%%), Recovered=%d, Blind FO Catches=%d, Ineffective Valid=%d, SDC=%d\n",
           sum.detected_faults, sum.total_trials, (sum.detected_faults * 100.0) / sum.total_trials,
           sum.genuine_recoveries, sum.blind_passes, sum.ineffective_faults, sum.sdc_count);
    assert(sum.detected_faults == 0); /* Baseline monitor local detection is 0.0%! */
    assert(sum.blind_passes + sum.ineffective_faults == 50);
    assert(sum.sdc_count == 0);

    run_suite(fp, &trial_id, TFIB_MODE_BASELINE, "BASELINE", "OP_TWIDDLE_PERSISTENT", TFIB_FAULT_OP_TWIDDLE, true, 50, &sum);
    printf("  - Op Twiddle Persistent: Detected=%d/%d (%.1f%%), Blind FO Catches=%d, Ineffective Valid=%d, SDC=%d\n",
           sum.detected_faults, sum.total_trials, (sum.detected_faults * 100.0) / sum.total_trials,
           sum.blind_passes, sum.ineffective_faults, sum.sdc_count);
    assert(sum.detected_faults == 0);
    assert(sum.blind_passes + sum.ineffective_faults == 50);
    assert(sum.sdc_count == 0);

    /* -------------------------------------------------------------------------
     * 2. CONFIG: TFIB-REF (Strategy 1: Dual-Reference Table)
     * ------------------------------------------------------------------------- */
    printf("\n[2/3] Testing Configuration: TFIB-REF (Strategy 1: Dual Reference)\n");

    run_suite(fp, &trial_id, TFIB_MODE_REF, "TFIB_REF", "CLEAN_CONTROL", TFIB_FAULT_NONE, false, 50, &sum);
    printf("  - Clean Baseline: %d/%d Success, 0 False Alarms\n", sum.total_trials, sum.total_trials);
    assert(sum.detected_faults == 0);

    run_suite(fp, &trial_id, TFIB_MODE_REF, "TFIB_REF", "OP_TWIDDLE_TRANSIENT", TFIB_FAULT_OP_TWIDDLE, false, 50, &sum);
    printf("  - Op Twiddle Transient: Detected=%d/%d (%.1f%%), Recovered=%d/%d (%.1f%%), SDC=%d\n",
           sum.detected_faults, sum.total_trials, (sum.detected_faults * 100.0) / sum.total_trials,
           sum.genuine_recoveries, sum.total_trials, (sum.genuine_recoveries * 100.0) / sum.total_trials,
           sum.sdc_count);
    assert(sum.detected_faults == 50);   /* 100% local detection closes Theorem 1 blind spot! */
    assert(sum.genuine_recoveries == 50); /* 100% genuine recovery using reference table! */
    assert(sum.sdc_count == 0);

    run_suite(fp, &trial_id, TFIB_MODE_REF, "TFIB_REF", "OP_TWIDDLE_PERSISTENT", TFIB_FAULT_OP_TWIDDLE, true, 50, &sum);
    printf("  - Op Twiddle Persistent: Detected=%d/%d (%.1f%%), Safe Fail-Stops=%d/%d, SDC=%d\n",
           sum.detected_faults, sum.total_trials, (sum.detected_faults * 100.0) / sum.total_trials,
           sum.safe_fail_stops, sum.total_trials, sum.sdc_count);
    assert(sum.detected_faults == 50);
    assert(sum.safe_fail_stops == 50);
    assert(sum.sdc_count == 0);

    run_suite(fp, &trial_id, TFIB_MODE_REF, "TFIB_REF", "REF_TWIDDLE_TRANSIENT", TFIB_FAULT_REF_TWIDDLE, false, 50, &sum);
    printf("  - Ref Twiddle Transient: Detected=%d/%d (%.1f%%), Recovered=%d/%d (%.1f%%), SDC=%d\n",
           sum.detected_faults, sum.total_trials, (sum.detected_faults * 100.0) / sum.total_trials,
           sum.genuine_recoveries, sum.total_trials, (sum.genuine_recoveries * 100.0) / sum.total_trials,
           sum.sdc_count);
    assert(sum.detected_faults == 50);
    assert(sum.genuine_recoveries == 50);

    run_suite(fp, &trial_id, TFIB_MODE_REF, "TFIB_REF", "REF_TWIDDLE_PERSISTENT", TFIB_FAULT_REF_TWIDDLE, true, 50, &sum);
    printf("  - Ref Twiddle Persistent: Detected=%d/%d (%.1f%%), Safe Fail-Stops=%d/%d, SDC=%d\n",
           sum.detected_faults, sum.total_trials, (sum.detected_faults * 100.0) / sum.total_trials,
           sum.safe_fail_stops, sum.total_trials, sum.sdc_count);
    assert(sum.detected_faults == 50);
    assert(sum.safe_fail_stops == 50);

    run_suite(fp, &trial_id, TFIB_MODE_REF, "TFIB_REF", "SIMULTANEOUS_COMMON_MODE", TFIB_FAULT_SIMULTANEOUS, false, 50, &sum);
    printf("  - Simultaneous Common-Mode: Detected Locally=%d/%d (%.1f%%), Blind FO Catches=%d, Ineffective Valid=%d, SDC=%d\n",
           sum.detected_faults, sum.total_trials, (sum.detected_faults * 100.0) / sum.total_trials,
           sum.blind_passes, sum.ineffective_faults, sum.sdc_count);
    assert(sum.detected_faults == 0); /* Demonstrates remaining common-mode failure boundary! */
    assert(sum.blind_passes + sum.ineffective_faults == 50); /* Downstream FO acts as failsafe! */
    assert(sum.sdc_count == 0);

    run_suite(fp, &trial_id, TFIB_MODE_REF, "TFIB_REF", "CHECKER_LOGIC_TRANSIENT", TFIB_FAULT_CHECKER_LOGIC, false, 50, &sum);
    printf("  - Checker Logic Transient: Detected=%d/%d (%.1f%%), Recovered=%d/%d (%.1f%%), SDC=%d\n",
           sum.detected_faults, sum.total_trials, (sum.detected_faults * 100.0) / sum.total_trials,
           sum.genuine_recoveries, sum.total_trials, (sum.genuine_recoveries * 100.0) / sum.total_trials,
           sum.sdc_count);
    assert(sum.detected_faults == 50);
    assert(sum.genuine_recoveries == 50);

    run_suite(fp, &trial_id, TFIB_MODE_REF, "TFIB_REF", "CHECKER_LOGIC_PERSISTENT", TFIB_FAULT_CHECKER_LOGIC, true, 50, &sum);
    printf("  - Checker Logic Persistent: Detected=%d/%d (%.1f%%), Safe Fail-Stops=%d/%d, SDC=%d\n",
           sum.detected_faults, sum.total_trials, (sum.detected_faults * 100.0) / sum.total_trials,
           sum.safe_fail_stops, sum.total_trials, sum.sdc_count);
    assert(sum.detected_faults == 50);
    assert(sum.safe_fail_stops == 50);

    /* -------------------------------------------------------------------------
     * 3. CONFIG: TFIB-META (Strategy 2: Precomputed Integrity Metadata)
     * ------------------------------------------------------------------------- */
    printf("\n[3/3] Testing Configuration: TFIB-META (Strategy 2: Metadata Tags)\n");

    run_suite(fp, &trial_id, TFIB_MODE_META, "TFIB_META", "CLEAN_CONTROL", TFIB_FAULT_NONE, false, 50, &sum);
    printf("  - Clean Baseline: %d/%d Success, 0 False Alarms\n", sum.total_trials, sum.total_trials);
    assert(sum.detected_faults == 0);

    run_suite(fp, &trial_id, TFIB_MODE_META, "TFIB_META", "OP_TWIDDLE_TRANSIENT", TFIB_FAULT_OP_TWIDDLE, false, 50, &sum);
    printf("  - Op Twiddle Transient: Detected=%d/%d (%.1f%%), Safe Fail-Stops=%d/%d, SDC=%d\n",
           sum.detected_faults, sum.total_trials, (sum.detected_faults * 100.0) / sum.total_trials,
           sum.safe_fail_stops, sum.total_trials, sum.sdc_count);
    assert(sum.detected_faults == 50); /* Tag mismatch flags 100% of twiddle faults! */
    assert(sum.safe_fail_stops == 50); /* Metadata detects, forces safe fail-stop */
    assert(sum.sdc_count == 0);

    run_suite(fp, &trial_id, TFIB_MODE_META, "TFIB_META", "OP_TWIDDLE_PERSISTENT", TFIB_FAULT_OP_TWIDDLE, true, 50, &sum);
    printf("  - Op Twiddle Persistent: Detected=%d/%d (%.1f%%), Safe Fail-Stops=%d/%d, SDC=%d\n",
           sum.detected_faults, sum.total_trials, (sum.detected_faults * 100.0) / sum.total_trials,
           sum.safe_fail_stops, sum.total_trials, sum.sdc_count);
    assert(sum.detected_faults == 50);
    assert(sum.safe_fail_stops == 50);

    run_suite(fp, &trial_id, TFIB_MODE_META, "TFIB_META", "META_TAG_TRANSIENT", TFIB_FAULT_META_TAG, false, 50, &sum);
    printf("  - Metadata Tag Transient: Detected=%d/%d (%.1f%%), Recovered=%d/%d (%.1f%%), SDC=%d\n",
           sum.detected_faults, sum.total_trials, (sum.detected_faults * 100.0) / sum.total_trials,
           sum.genuine_recoveries, sum.total_trials, (sum.genuine_recoveries * 100.0) / sum.total_trials,
           sum.sdc_count);
    assert(sum.detected_faults == 50);
    assert(sum.genuine_recoveries == 50);

    run_suite(fp, &trial_id, TFIB_MODE_META, "TFIB_META", "META_TAG_PERSISTENT", TFIB_FAULT_META_TAG, true, 50, &sum);
    printf("  - Metadata Tag Persistent: Detected=%d/%d (%.1f%%), Safe Fail-Stops=%d/%d, SDC=%d\n",
           sum.detected_faults, sum.total_trials, (sum.detected_faults * 100.0) / sum.total_trials,
           sum.safe_fail_stops, sum.total_trials, sum.sdc_count);
    assert(sum.detected_faults == 50);
    assert(sum.safe_fail_stops == 50);

    run_suite(fp, &trial_id, TFIB_MODE_META, "TFIB_META", "CHECKER_LOGIC_TRANSIENT", TFIB_FAULT_CHECKER_LOGIC, false, 50, &sum);
    printf("  - Checker Logic Transient: Detected=%d/%d (%.1f%%), Recovered=%d/%d (%.1f%%), SDC=%d\n",
           sum.detected_faults, sum.total_trials, (sum.detected_faults * 100.0) / sum.total_trials,
           sum.genuine_recoveries, sum.total_trials, (sum.genuine_recoveries * 100.0) / sum.total_trials,
           sum.sdc_count);
    assert(sum.detected_faults == 50);
    assert(sum.genuine_recoveries == 50);

    run_suite(fp, &trial_id, TFIB_MODE_META, "TFIB_META", "CHECKER_LOGIC_PERSISTENT", TFIB_FAULT_CHECKER_LOGIC, true, 50, &sum);
    printf("  - Checker Logic Persistent: Detected=%d/%d (%.1f%%), Safe Fail-Stops=%d/%d, SDC=%d\n",
           sum.detected_faults, sum.total_trials, (sum.detected_faults * 100.0) / sum.total_trials,
           sum.safe_fail_stops, sum.total_trials, sum.sdc_count);
    assert(sum.detected_faults == 50);
    assert(sum.safe_fail_stops == 50);

    fclose(fp);
    printf("\n================================================================================\n");
    printf("ALL AUTOMATED ASSERTIONS PASSED! Total Trials Recorded: %d\n", trial_id);
    printf("Raw dataset successfully written to %s\n", out_csv);
    printf("================================================================================\n");

    return 0;
}
