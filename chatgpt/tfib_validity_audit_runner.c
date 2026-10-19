#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include "tfib_common.h"
#include "tfib_core.h"

#define SS_BYTES 32
#define CT_BYTES 1088
#define SK_BYTES 2400
#define PK_BYTES 1184

int randombytes(uint8_t *out, size_t outlen) {
    for (size_t i = 0; i < outlen; i++) out[i] = (uint8_t)rand();
    return 0;
}

int mlkem768_keypair(uint8_t *pk, uint8_t *sk);
int mlkem768_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int mlkem768_dec_monitored(uint8_t *ss, const uint8_t *ct, const uint8_t *sk, uint32_t *internal_status);
void mlkem768_shake256(uint8_t *out, size_t outlen, const uint8_t *in, size_t inlen);

static void compute_expected_rejection_key(uint8_t ss_rej[SS_BYTES], const uint8_t sk[SK_BYTES], const uint8_t ct[CT_BYTES]) {
    uint8_t z_ct[SS_BYTES + CT_BYTES];
    memcpy(z_ct, sk + SK_BYTES - SS_BYTES, SS_BYTES);
    memcpy(z_ct + SS_BYTES, ct, CT_BYTES);
    mlkem768_shake256(ss_rej, SS_BYTES, z_ct, SS_BYTES + CT_BYTES);
}

typedef struct {
    int total_trials;
    int activated_faults;
    uint64_t total_triggers;
    int detected_faults;
    int recovery_attempted;
    int genuine_recoveries;
    int safe_fail_stops;
    int blind_fo_catches;
    int ineffective_faults;
    int sdc_count;
    int incorrect_reject_keys;
} audit_summary_t;

static void run_audit_suite(
    FILE *fp_trials, int *trial_id, tfib_mode_t mode, const char *mode_name,
    const char *suite_name, tfib_fault_locus_t locus, bool persistent,
    int num_trials, audit_summary_t *sum
) {
    uint8_t pk[PK_BYTES], sk[SK_BYTES], ct[CT_BYTES];
    uint8_t ss_expected[SS_BYTES], ss_out[SS_BYTES], ss_rej_expected[SS_BYTES];

    memset(sum, 0, sizeof(*sum));
    sum->total_trials = num_trials;

    tfib_set_mode(mode);

    for (int t = 0; t < num_trials; t++) {
        tfib_fault_reset();
        tfib_reset_all_stats();

        srand(0x1337C0DE + t * 31 + (int)mode * 1000 + (int)locus * 100 + (persistent ? 777 : 0));
        mlkem768_keypair(pk, sk);
        mlkem768_enc(ct, ss_expected, pk);
        compute_expected_rejection_key(ss_rej_expected, sk, ct);

        unsigned stage = (t % 7) + 1;
        unsigned b_idx = (t * 17) % 128;
        uint8_t bit = (t % 15) + 1;

        if (locus != TFIB_FAULT_NONE) {
            tfib_fault_arm(locus, stage, b_idx, bit, persistent);
        }

        uint32_t status = 0;
        int rc = mlkem768_dec_monitored(ss_out, ct, sk, &status);
        (void)rc;

        uint64_t triggers = g_tfib_fault.trigger_count;
        bool fault_act = (triggers > 0);
        uint32_t mismatches = tfib_get_total_mismatches();
        bool mon_det = (mismatches > 0);
        bool rec_att = (mon_det);
        uint32_t recoveries = tfib_get_total_recoveries();
        bool rec_succ = (recoveries > 0);

        bool ss_match_valid = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        bool ss_match_rejection = (memcmp(ss_out, ss_rej_expected, SS_BYTES) == 0);
        bool sdc = (!ss_match_valid && !ss_match_rejection);

        const char *outcome;
        if (!fault_act && locus == TFIB_FAULT_NONE) {
            outcome = "CLEAN_SUCCESS";
        } else if (ss_match_valid && status == 0x5A5A5A5A && rec_succ) {
            outcome = "GENUINE_RECOVERY";
            sum->genuine_recoveries++;
        } else if (ss_match_valid && !mon_det && fault_act) {
            /* Oracle confirmed: valid key matches despite unmonitored fault -> LWE noise absorption */
            outcome = "INEFFECTIVE_FAULT_VALID";
            sum->ineffective_faults++;
        } else if (ss_match_rejection) {
            if (!mon_det) {
                outcome = "LOCAL_BLIND_FO_CONTAINED";
                sum->blind_fo_catches++;
            } else {
                outcome = "SAFE_FAIL_STOP";
                sum->safe_fail_stops++;
            }
        } else if (sdc) {
            outcome = "SILENT_DATA_CORRUPTION";
            sum->sdc_count++;
        } else {
            outcome = "INCORRECT_REJECT_KEY";
            sum->incorrect_reject_keys++;
        }

        if (fault_act) sum->activated_faults++;
        sum->total_triggers += triggers;
        if (mon_det) sum->detected_faults++;
        if (rec_att) sum->recovery_attempted++;

        /* Write trial-level record */
        fprintf(fp_trials, "%d,%s,%s,%u,%u,%u,%d,%llu,%d,%u,%d,%u,%d,%d,%d,0x%08X,%s\n",
                (*trial_id)++, mode_name, suite_name,
                stage, b_idx, bit, persistent ? 1 : 0,
                triggers, fault_act ? 1 : 0,
                mismatches, mon_det ? 1 : 0,
                recoveries, rec_succ ? 1 : 0,
                ss_match_valid ? 1 : 0, ss_match_rejection ? 1 : 0,
                status, outcome);
    }
}

int main(void) {
    FILE *fp_trials = fopen("tfib_trial_level_results.csv", "w");
    if (!fp_trials) {
        perror("Failed to open tfib_trial_level_results.csv");
        return 1;
    }

    fprintf(fp_trials, "trial_id,config,fault_suite,stage,butterfly,bit,persistent,"
                       "trigger_count,fault_activated,mismatch_count,monitor_detected,"
                       "recovery_count,recovered_success,oracle_valid_match,oracle_rejection_match,"
                       "final_status,oracle_classification\n");

    FILE *fp_summary = fopen("tfib_reproduced_results.csv", "w");
    if (!fp_summary) {
        perror("Failed to open tfib_reproduced_results.csv");
        fclose(fp_trials);
        return 1;
    }

    fprintf(fp_summary, "config,suite,persistent,total_trials,activated_trials,total_triggers,"
                        "detected_trials,detection_rate_pct,genuine_recoveries,safe_fail_stops,"
                        "blind_fo_catches,ineffective_faults,sdc_count,sdc_rate_pct\n");

    int trial_id = 0;
    audit_summary_t sum;

    printf("================================================================================\n");
    printf("TFIB INDEPENDENT EXPERIMENTAL VALIDITY AUDIT: FULL SUITE REPRODUCTION\n");
    printf("================================================================================\n\n");

    /* Define suites across all 3 configs */
    struct {
        tfib_mode_t mode;
        const char *mode_name;
        const char *suite_name;
        tfib_fault_locus_t locus;
        bool persistent;
    } suites[] = {
        /* Baseline */
        {TFIB_MODE_BASELINE, "BASELINE", "CLEAN_CONTROL", TFIB_FAULT_NONE, false},
        {TFIB_MODE_BASELINE, "BASELINE", "OP_TWIDDLE_TRANSIENT", TFIB_FAULT_OP_TWIDDLE, false},
        {TFIB_MODE_BASELINE, "BASELINE", "OP_TWIDDLE_PERSISTENT", TFIB_FAULT_OP_TWIDDLE, true},

        /* TFIB-Ref */
        {TFIB_MODE_REF, "TFIB_REF", "CLEAN_CONTROL", TFIB_FAULT_NONE, false},
        {TFIB_MODE_REF, "TFIB_REF", "OP_TWIDDLE_TRANSIENT", TFIB_FAULT_OP_TWIDDLE, false},
        {TFIB_MODE_REF, "TFIB_REF", "OP_TWIDDLE_PERSISTENT", TFIB_FAULT_OP_TWIDDLE, true},
        {TFIB_MODE_REF, "TFIB_REF", "REF_TWIDDLE_TRANSIENT", TFIB_FAULT_REF_TWIDDLE, false},
        {TFIB_MODE_REF, "TFIB_REF", "REF_TWIDDLE_PERSISTENT", TFIB_FAULT_REF_TWIDDLE, true},
        {TFIB_MODE_REF, "TFIB_REF", "SIMULTANEOUS_COMMON_MODE", TFIB_FAULT_SIMULTANEOUS, false},
        {TFIB_MODE_REF, "TFIB_REF", "CHECKER_LOGIC_TRANSIENT", TFIB_FAULT_CHECKER_LOGIC, false},
        {TFIB_MODE_REF, "TFIB_REF", "CHECKER_LOGIC_PERSISTENT", TFIB_FAULT_CHECKER_LOGIC, true},

        /* TFIB-Meta */
        {TFIB_MODE_META, "TFIB_META", "CLEAN_CONTROL", TFIB_FAULT_NONE, false},
        {TFIB_MODE_META, "TFIB_META", "OP_TWIDDLE_TRANSIENT", TFIB_FAULT_OP_TWIDDLE, false},
        {TFIB_MODE_META, "TFIB_META", "OP_TWIDDLE_PERSISTENT", TFIB_FAULT_OP_TWIDDLE, true},
        {TFIB_MODE_META, "TFIB_META", "META_TAG_TRANSIENT", TFIB_FAULT_META_TAG, false},
        {TFIB_MODE_META, "TFIB_META", "META_TAG_PERSISTENT", TFIB_FAULT_META_TAG, true},
        {TFIB_MODE_META, "TFIB_META", "CHECKER_LOGIC_TRANSIENT", TFIB_FAULT_CHECKER_LOGIC, false},
        {TFIB_MODE_META, "TFIB_META", "CHECKER_LOGIC_PERSISTENT", TFIB_FAULT_CHECKER_LOGIC, true}
    };

    size_t num_suites = sizeof(suites) / sizeof(suites[0]);

    for (size_t s = 0; s < num_suites; s++) {
        run_audit_suite(
            fp_trials, &trial_id, suites[s].mode, suites[s].mode_name,
            suites[s].suite_name, suites[s].locus, suites[s].persistent,
            50, &sum
        );

        double det_rate = (sum.total_trials > 0) ? (sum.detected_faults * 100.0) / sum.total_trials : 0.0;
        double sdc_rate = (sum.total_trials > 0) ? (sum.sdc_count * 100.0) / sum.total_trials : 0.0;

        printf("[%2zu/%2zu] %-10s | %-26s | Act=%2d/50 (Trigs=%3llu) | Det=%2d/50 (%5.1f%%) | Rec=%2d | Stop=%2d | FO=%2d | Ineff=%2d | SDC=%d\n",
               s + 1, num_suites, suites[s].mode_name, suites[s].suite_name,
               sum.activated_faults, sum.total_triggers,
               sum.detected_faults, det_rate,
               sum.genuine_recoveries, sum.safe_fail_stops,
               sum.blind_fo_catches, sum.ineffective_faults, sum.sdc_count);

        fprintf(fp_summary, "%s,%s,%d,%d,%d,%llu,%d,%.2f,%d,%d,%d,%d,%d,%.2f\n",
                suites[s].mode_name, suites[s].suite_name, suites[s].persistent ? 1 : 0,
                sum.total_trials, sum.activated_faults, sum.total_triggers,
                sum.detected_faults, det_rate,
                sum.genuine_recoveries, sum.safe_fail_stops,
                sum.blind_fo_catches, sum.ineffective_faults,
                sum.sdc_count, sdc_rate);
    }

    fclose(fp_trials);
    fclose(fp_summary);

    printf("\nAudit reproduction complete. 900 trials recorded in tfib_trial_level_results.csv.\n");
    printf("Aggregated results written to tfib_reproduced_results.csv.\n");

    return 0;
}
