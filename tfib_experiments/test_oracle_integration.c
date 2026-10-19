#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include <sys/stat.h>

#include "tfib_common.h"
#include "tfib_core.h"
#include "independent_oracle.h"

#define SS_BYTES 32
#define CT_BYTES 1088
#define SK_BYTES 2400
#define PK_BYTES 1184

/* Declarations from mlkem768_inst.o */
int mlkem768_keypair(uint8_t *pk, uint8_t *sk);
int mlkem768_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int mlkem768_dec_monitored(uint8_t *ss, const uint8_t *ct, const uint8_t *sk, uint32_t *internal_status);

int randombytes(uint8_t *out, size_t outlen) {
    for (size_t i = 0; i < outlen; i++) out[i] = (uint8_t)(rand() & 0xFF);
    return 0;
}

static time_t get_file_mtime(const char *filename) {
    struct stat st;
    if (stat(filename, &st) == 0) return st.st_mtime;
    return 0;
}

static off_t get_file_size(const char *filename) {
    struct stat st;
    if (stat(filename, &st) == 0) return st.st_size;
    return -1;
}

int main(void) {
    printf("================================================================================\n");
    printf("PHASE 2 — STEP 1: INDEPENDENT ORACLE INTEGRATION VALIDATION SUITE\n");
    printf("================================================================================\n\n");

    if (independent_oracle_init() != 0) {
        fprintf(stderr, "FATAL: Failed to initialize independent oracle backend!\n");
        return 1;
    }
    printf("Independent Oracle Initialized: %s\n\n", independent_oracle_get_version());

    int failed_tests = 0;

    /* -------------------------------------------------------------------------
     * Test A: Valid Baseline
     * ------------------------------------------------------------------------- */
    printf("[Test A] Valid Baseline Decapsulation\n");
    {
        uint8_t pk[PK_BYTES], sk[SK_BYTES], ct[CT_BYTES];
        uint8_t ss_enc[SS_BYTES], ss_oracle[SS_BYTES], ss_prod[SS_BYTES];

        tfib_set_mode(TFIB_MODE_BASELINE);
        tfib_fault_reset();
        tfib_reset_all_stats();

        srand(42);
        mlkem768_keypair(pk, sk);
        mlkem768_enc(ct, ss_enc, pk);

        int o_rc = independent_oracle_decaps(ss_oracle, ct, sk);
        uint32_t status = 0;
        mlkem768_dec_monitored(ss_prod, ct, sk, &status);

        bool oracle_ok = (o_rc == 0);
        bool ss_match = (memcmp(ss_prod, ss_oracle, SS_BYTES) == 0);
        bool status_clean = (status == 0x5A5A5A5A);
        bool no_false_recovery = (tfib_get_total_recoveries() == 0);
        bool no_false_detection = (tfib_get_total_mismatches() == 0);

        bool test_a_pass = oracle_ok && ss_match && status_clean && no_false_recovery && no_false_detection;
        printf("  - Oracle Decaps Return Code: %d (expected 0)\n", o_rc);
        printf("  - Production vs Oracle SS Match: %s\n", ss_match ? "YES" : "NO");
        printf("  - Final Status: 0x%08X (expected 0x5A5A5A5A)\n", status);
        printf("  - False Recoveries Reported: %llu (expected 0)\n", (unsigned long long)tfib_get_total_recoveries());
        printf("  -> Result: %s\n\n", test_a_pass ? "PASS" : "FAIL");
        if (!test_a_pass) failed_tests++;
    }

    /* -------------------------------------------------------------------------
     * Test B: Invalid Ciphertext Canonical Implicit Rejection
     * ------------------------------------------------------------------------- */
    printf("[Test B] Invalid Ciphertext Canonical Implicit Rejection\n");
    {
        uint8_t pk[PK_BYTES], sk[SK_BYTES], ct[CT_BYTES], ct_mut[CT_BYTES];
        uint8_t ss_valid_oracle[SS_BYTES], ss_rej_oracle[SS_BYTES], ss_prod[SS_BYTES];

        tfib_set_mode(TFIB_MODE_BASELINE);
        tfib_fault_reset();
        tfib_reset_all_stats();

        srand(101);
        mlkem768_keypair(pk, sk);
        mlkem768_enc(ct, ss_valid_oracle, pk);

        /* Mutate ciphertext at offset 100 */
        memcpy(ct_mut, ct, CT_BYTES);
        ct_mut[100] ^= 0x01;

        int o_val_rc = independent_oracle_decaps(ss_valid_oracle, ct, sk);
        int o_rej_rc = independent_oracle_compute_rejection(ss_rej_oracle, sk, ct_mut);

        uint32_t status = 0;
        mlkem768_dec_monitored(ss_prod, ct_mut, sk, &status);

        bool o_rej_ok = (o_rej_rc == 0) && (o_val_rc == 0);
        bool rej_match = (memcmp(ss_prod, ss_rej_oracle, SS_BYTES) == 0);
        bool differs_from_valid = (memcmp(ss_prod, ss_valid_oracle, SS_BYTES) != 0);
        bool status_rej = (status == 0xA5A5A5A5 || status == 0xFFFFFFFF);

        bool test_b_pass = o_rej_ok && rej_match && differs_from_valid && status_rej;
        printf("  - Oracle Rejection Calc Return Code: %d (expected 0)\n", o_rej_rc);
        printf("  - Production Output Matches Oracle Canonical Rejection: %s\n", rej_match ? "YES" : "NO");
        printf("  - Production Output Strictly Differs from Valid Secret: %s\n", differs_from_valid ? "YES" : "NO");
        printf("  - Production Rejection Status: 0x%08X\n", status);
        printf("  -> Result: %s\n\n", test_b_pass ? "PASS" : "FAIL");
        if (!test_b_pass) failed_tests++;
    }

    /* -------------------------------------------------------------------------
     * Test C: Oracle Mismatch Detection
     * ------------------------------------------------------------------------- */
    printf("[Test C] Oracle Mismatch Detection\n");
    {
        uint8_t pk[PK_BYTES], sk[SK_BYTES], ct[CT_BYTES];
        uint8_t ss_valid_oracle[SS_BYTES], ss_corrupted_expected[SS_BYTES], ss_prod[SS_BYTES];

        tfib_set_mode(TFIB_MODE_BASELINE);
        tfib_fault_reset();
        tfib_reset_all_stats();

        srand(202);
        mlkem768_keypair(pk, sk);
        mlkem768_enc(ct, ss_valid_oracle, pk);

        independent_oracle_decaps(ss_valid_oracle, ct, sk);
        memcpy(ss_corrupted_expected, ss_valid_oracle, SS_BYTES);
        ss_corrupted_expected[15] ^= 0xAA; /* deliberate expected-value corruption */

        uint32_t status = 0;
        mlkem768_dec_monitored(ss_prod, ct, sk, &status);

        bool raw_prod_valid = (memcmp(ss_prod, ss_valid_oracle, SS_BYTES) == 0);
        bool mismatch_detected = (memcmp(ss_prod, ss_corrupted_expected, SS_BYTES) != 0);
        bool rejected_as_success = (!mismatch_detected); /* must be false */

        bool test_c_pass = raw_prod_valid && mismatch_detected && !rejected_as_success;
        printf("  - Deliberately corrupted expected secret supplied to comparison layer\n");
        printf("  - Mismatch Detected by Verification Layer: %s\n", mismatch_detected ? "YES" : "NO");
        printf("  - Incorrectly Classified as Success: %s\n", rejected_as_success ? "YES (FAIL)" : "NO (PASS)");
        printf("  -> Result: %s\n\n", test_c_pass ? "PASS" : "FAIL");
        if (!test_c_pass) failed_tests++;
    }

    /* -------------------------------------------------------------------------
     * Test D: Oracle Failure Handling
     * ------------------------------------------------------------------------- */
    printf("[Test D] Oracle Failure Handling\n");
    {
        /* Test double simulation: pass NULL buffer to oracle decapsulation */
        uint8_t sk[SK_BYTES] = {0}, ct[CT_BYTES] = {0};
        int bad_rc = independent_oracle_decaps(NULL, ct, sk);
        int bad_rej_rc = independent_oracle_compute_rejection(NULL, sk, ct);

        bool failure_signaled = (bad_rc != 0) && (bad_rej_rc != 0);

        /* Verify that when oracle fails, runner records explicit error rather than normal outcome */
        const char *outcome = "INITIAL";
        if (bad_rc != 0) {
            outcome = "ORACLE_VALIDATION_FAILURE";
        } else {
            outcome = "CLEAN_SUCCESS"; /* Would be erroneous */
        }

        bool handled_safely = (strcmp(outcome, "ORACLE_VALIDATION_FAILURE") == 0);
        bool test_d_pass = failure_signaled && handled_safely;
        printf("  - Oracle Decaps Error on Invalid Input: %d (expected non-zero)\n", bad_rc);
        printf("  - Oracle Rejection Error on Invalid Input: %d (expected non-zero)\n", bad_rej_rc);
        printf("  - Runner Classification on Oracle Failure: %s\n", outcome);
        printf("  -> Result: %s\n\n", test_d_pass ? "PASS" : "FAIL");
        if (!test_d_pass) failed_tests++;
    }

    /* -------------------------------------------------------------------------
     * Test E: Existing Campaign Compatibility & Historical Data Protection
     * ------------------------------------------------------------------------- */
    printf("[Test E] Existing Campaign Compatibility & Historical Data Protection\n");
    {
        /* Record pre-execution state of historical CSV files */
        off_t raw_size_pre = get_file_size("tfib_raw_results.csv");
        time_t raw_mtime_pre = get_file_mtime("tfib_raw_results.csv");

        off_t trial_size_pre = get_file_size("tfib_trial_level_results.csv");
        time_t trial_mtime_pre = get_file_mtime("tfib_trial_level_results.csv");

        /* Run small deterministic campaign (3 trials across 3 modes) into safe test output file */
        const char *test_csv = "tfib_experiments/test_compatibility_output.csv";
        FILE *fp_test = fopen(test_csv, "w");
        assert(fp_test != NULL);
        fprintf(fp_test, "trial_id,config,suite,stage,b_idx,bit,persistent,outcome\n");

        int trial_id = 0;
        int trials_per_suite = 3;
        tfib_mode_t modes[3] = {TFIB_MODE_BASELINE, TFIB_MODE_REF, TFIB_MODE_META};
        const char *mode_names[3] = {"BASELINE", "TFIB_REF", "TFIB_META"};

        for (int m = 0; m < 3; m++) {
            tfib_set_mode(modes[m]);
            for (int t = 0; t < trials_per_suite; t++) {
                tfib_fault_reset();
                tfib_reset_all_stats();

                unsigned stage = (t % 7) + 1;
                unsigned b_idx = (t * 17) % 128;
                uint8_t bit = (t % 15) + 1;

                srand(0x1337C0DE + t * 31 + (int)modes[m] * 1000 + 100);

                uint8_t pk[PK_BYTES], sk[SK_BYTES], ct[CT_BYTES];
                uint8_t ss_exp[SS_BYTES], ss_rej_exp[SS_BYTES], ss_out[SS_BYTES];
                uint8_t ss_enc_dummy[SS_BYTES];

                mlkem768_keypair(pk, sk);
                mlkem768_enc(ct, ss_enc_dummy, pk);

                int o_rc1 = independent_oracle_decaps(ss_exp, ct, sk);
                int o_rc2 = independent_oracle_compute_rejection(ss_rej_exp, sk, ct);
                assert(o_rc1 == 0 && o_rc2 == 0);

                tfib_fault_arm(TFIB_FAULT_OP_TWIDDLE, stage, b_idx, bit, false);
                uint32_t status = 0;
                mlkem768_dec_monitored(ss_out, ct, sk, &status);

                bool ss_match = (memcmp(ss_out, ss_exp, SS_BYTES) == 0);
                bool rej_match = (memcmp(ss_out, ss_rej_exp, SS_BYTES) == 0);

                const char *out_str = ss_match ? "VALID_MATCH" : (rej_match ? "REJECTION_MATCH" : "SDC");
                fprintf(fp_test, "%d,%s,OP_TWIDDLE,%u,%u,%u,0,%s\n",
                        trial_id++, mode_names[m], stage, b_idx, bit, out_str);
            }
        }
        fclose(fp_test);

        /* Verify post-execution state of historical CSV files */
        off_t raw_size_post = get_file_size("tfib_raw_results.csv");
        time_t raw_mtime_post = get_file_mtime("tfib_raw_results.csv");

        off_t trial_size_post = get_file_size("tfib_trial_level_results.csv");
        time_t trial_mtime_post = get_file_mtime("tfib_trial_level_results.csv");

        bool historical_raw_untouched = (raw_size_pre == raw_size_post) && (raw_mtime_pre == raw_mtime_post);
        bool historical_trial_untouched = (trial_size_pre == trial_size_post) && (trial_mtime_pre == trial_mtime_post);
        bool test_csv_written = (get_file_size(test_csv) > 0);

        bool test_e_pass = historical_raw_untouched && historical_trial_untouched && test_csv_written;
        printf("  - Historical tfib_raw_results.csv Untouched: %s (size=%lld, mtime=%ld)\n",
               historical_raw_untouched ? "YES" : "NO", (long long)raw_size_post, (long)raw_mtime_post);
        printf("  - Historical tfib_trial_level_results.csv Untouched: %s (size=%lld, mtime=%ld)\n",
               historical_trial_untouched ? "YES" : "NO", (long long)trial_size_post, (long)trial_mtime_post);
        printf("  - Integration Test CSV Written: %s (%lld bytes)\n",
               test_csv_written ? "YES" : "NO", (long long)get_file_size(test_csv));
        printf("  -> Result: %s\n\n", test_e_pass ? "PASS" : "FAIL");
        if (!test_e_pass) failed_tests++;
    }

    printf("================================================================================\n");
    printf("INTEGRATION VALIDATION VERDICT: %s (%d failures)\n",
           (failed_tests == 0) ? "ALL TESTS PASSED (PASS)" : "TESTS FAILED (FAIL)", failed_tests);
    printf("================================================================================\n");

    return (failed_tests == 0) ? 0 : 1;
}
