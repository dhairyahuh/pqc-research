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
    printf("PHASE 2 — STEP 2A: INDEPENDENT CIPHERTEXT GENERATION VALIDATION SUITE\n");
    printf("================================================================================\n\n");

    if (independent_oracle_init() != 0) {
        fprintf(stderr, "FATAL: Failed to initialize independent oracle backend!\n");
        return 1;
    }
    printf("Independent Oracle Initialized: %s\n\n", independent_oracle_get_version());

    int failed_tests = 0;

    /* -------------------------------------------------------------------------
     * Test A: Deterministic Reproducibility
     * ------------------------------------------------------------------------- */
    printf("[Test A] Deterministic Encapsulation Reproducibility\n");
    {
        uint8_t pk[PK_BYTES], sk[SK_BYTES];
        srand(1337);
        mlkem768_keypair(pk, sk);

        uint8_t seed32[32];
        for (int i = 0; i < 32; i++) seed32[i] = (uint8_t)(i * 7 + 13);

        uint8_t ct1[CT_BYTES], ss1[SS_BYTES];
        uint8_t ct2[CT_BYTES], ss2[SS_BYTES];

        int rc1 = independent_oracle_encaps_derand(ct1, ss1, pk, seed32);
        int rc2 = independent_oracle_encaps_derand(ct2, ss2, pk, seed32);

        bool rc_ok = (rc1 == 0 && rc2 == 0);
        bool ct_identical = (memcmp(ct1, ct2, CT_BYTES) == 0);
        bool ss_identical = (memcmp(ss1, ss2, SS_BYTES) == 0);

        bool test_a_pass = rc_ok && ct_identical && ss_identical;
        printf("  - Encapsulation Call 1 RC: %d, Call 2 RC: %d\n", rc1, rc2);
        printf("  - Repeated Ciphertext Byte-Exact Match: %s\n", ct_identical ? "YES" : "NO");
        printf("  - Repeated Shared Secret Byte-Exact Match: %s\n", ss_identical ? "YES" : "NO");
        printf("  -> Result: %s\n\n", test_a_pass ? "PASS" : "FAIL");
        if (!test_a_pass) failed_tests++;
    }

    /* -------------------------------------------------------------------------
     * Test B: Independent Ciphertext Generation (Source & Symbol Check)
     * ------------------------------------------------------------------------- */
    printf("[Test B] Independent Ciphertext Generation (Call-Path & Symbol Inspection)\n");
    {
        /* 1. Object symbol check: runner translation unit does NOT reference _mlkem768_enc */
        int compile_rc = system("clang -O3 -Ialgorithms/source_ref/mlkem/include -Itfib_implementation "
                                "-Itfib_experiments/phase11_oracle -I/opt/homebrew/opt/liboqs/include "
                                "-c tfib_experiments/tfib_experiment_runner.c -o /tmp/tfib_runner_symcheck.o");
        int obj_sym_rc = system("nm -u /tmp/tfib_runner_symcheck.o | grep -w \"_mlkem768_enc\" > /dev/null 2>&1");
        bool obj_not_referencing = (compile_rc == 0) && (obj_sym_rc != 0);

        /* 2. Disassembly call-path check: no branch instruction calls _mlkem768_enc */
        int call_rc = system("otool -tv tfib_experiments/tfib_experiment_runner | grep -E \"bl.*_mlkem768_enc$\" > /dev/null 2>&1");
        bool no_call_instruction = (call_rc != 0);

        /* 3. Source check: zero references in runner source file */
        int src_grep_rc = system("grep -n \"mlkem768_enc\" tfib_experiments/tfib_experiment_runner.c > /dev/null 2>&1");
        bool src_call_absent = (src_grep_rc != 0);

        bool test_b_pass = obj_not_referencing && no_call_instruction && src_call_absent;
        printf("  - Runner Object Reference Check (_mlkem768_enc unreferenced): %s\n", obj_not_referencing ? "YES" : "NO");
        printf("  - Disassembly Branch Target Check (0 calls to _mlkem768_enc): %s\n", no_call_instruction ? "YES" : "NO");
        printf("  - Runner Source Check (mlkem768_enc absent): %s\n", src_call_absent ? "YES" : "NO");
        printf("  -> Result: %s\n\n", test_b_pass ? "PASS" : "FAIL");
        if (!test_b_pass) failed_tests++;
    }

    /* -------------------------------------------------------------------------
     * Test C: Valid Decapsulation Agreement
     * ------------------------------------------------------------------------- */
    printf("[Test C] Valid Decapsulation Agreement with Oracle Ciphertext\n");
    {
        uint8_t pk[PK_BYTES], sk[SK_BYTES];
        srand(2024);
        mlkem768_keypair(pk, sk);

        uint8_t seed32[32];
        randombytes(seed32, sizeof(seed32));

        uint8_t ct[CT_BYTES], ss_expected[SS_BYTES], ss_prod[SS_BYTES];
        int enc_rc = independent_oracle_encaps_derand(ct, ss_expected, pk, seed32);

        uint32_t status = 0;
        int dec_rc = mlkem768_dec_monitored(ss_prod, ct, sk, &status);
        (void)dec_rc;

        bool enc_ok = (enc_rc == 0);
        bool status_clean = (status == 0x5A5A5A5A);
        bool ss_match = (memcmp(ss_prod, ss_expected, SS_BYTES) == 0);

        bool test_c_pass = enc_ok && status_clean && ss_match;
        printf("  - Oracle Encapsulation Return Code: %d\n", enc_rc);
        printf("  - Production Decapsulation Status: 0x%08X (expected 0x5A5A5A5A)\n", status);
        printf("  - Production Output Matches Oracle Valid Shared Secret: %s\n", ss_match ? "YES" : "NO");
        printf("  -> Result: %s\n\n", test_c_pass ? "PASS" : "FAIL");
        if (!test_c_pass) failed_tests++;
    }

    /* -------------------------------------------------------------------------
     * Test D: Rejection Expectation Consistency
     * ------------------------------------------------------------------------- */
    printf("[Test D] Rejection Expectation Consistency on Mutated Ciphertext\n");
    {
        uint8_t pk[PK_BYTES], sk[SK_BYTES];
        srand(9999);
        mlkem768_keypair(pk, sk);

        uint8_t seed32[32];
        randombytes(seed32, sizeof(seed32));

        uint8_t ct[CT_BYTES], ss_expected[SS_BYTES], ct_mut[CT_BYTES];
        independent_oracle_encaps_derand(ct, ss_expected, pk, seed32);

        /* Mutate ciphertext at offset 250 */
        memcpy(ct_mut, ct, CT_BYTES);
        ct_mut[250] ^= 0x80;

        uint8_t ss_rej_expected[SS_BYTES], ss_prod[SS_BYTES];
        int rej_rc = independent_oracle_compute_rejection(ss_rej_expected, sk, ct_mut);

        uint32_t status = 0;
        mlkem768_dec_monitored(ss_prod, ct_mut, sk, &status);

        bool rej_ok = (rej_rc == 0);
        bool status_rej = (status == 0xA5A5A5A5 || status == 0xFFFFFFFF);
        bool rej_match = (memcmp(ss_prod, ss_rej_expected, SS_BYTES) == 0);
        bool differs_from_valid = (memcmp(ss_prod, ss_expected, SS_BYTES) != 0);

        bool test_d_pass = rej_ok && status_rej && rej_match && differs_from_valid;
        printf("  - Oracle Rejection Calculation Return Code: %d\n", rej_rc);
        printf("  - Production Decapsulation Status: 0x%08X\n", status);
        printf("  - Production Output Matches Expected Rejection Secret: %s\n", rej_match ? "YES" : "NO");
        printf("  - Output Strictly Differs from Valid Shared Secret: %s\n", differs_from_valid ? "YES" : "NO");
        printf("  -> Result: %s\n\n", test_d_pass ? "PASS" : "FAIL");
        if (!test_d_pass) failed_tests++;
    }

    /* -------------------------------------------------------------------------
     * Test E: Campaign Configuration & Historical Data Protection
     * ------------------------------------------------------------------------- */
    printf("[Test E] Campaign Configuration Preservation & Historical Data Protection\n");
    {
        off_t raw_size_pre = get_file_size("tfib_raw_results.csv");
        time_t raw_mtime_pre = get_file_mtime("tfib_raw_results.csv");

        off_t trial_size_pre = get_file_size("tfib_trial_level_results.csv");
        time_t trial_mtime_pre = get_file_mtime("tfib_trial_level_results.csv");

        /* Execute mini-campaign (5 trials per mode across all 3 modes) using independent encapsulation */
        const char *step2a_csv = "tfib_experiments/test_step2a_output.csv";
        FILE *fp = fopen(step2a_csv, "w");
        assert(fp != NULL);
        fprintf(fp, "trial_id,config,stage,b_idx,bit,persistent,status,outcome\n");

        int trial_id = 0;
        tfib_mode_t modes[3] = {TFIB_MODE_BASELINE, TFIB_MODE_REF, TFIB_MODE_META};
        const char *mode_names[3] = {"BASELINE", "TFIB_REF", "TFIB_META"};

        for (int m = 0; m < 3; m++) {
            tfib_set_mode(modes[m]);
            for (int t = 0; t < 5; t++) {
                tfib_fault_reset();
                tfib_reset_all_stats();

                unsigned stage = (t % 7) + 1;
                unsigned b_idx = (t * 17) % 128;
                uint8_t bit = (t % 15) + 1;

                srand(0x1337C0DE + t * 31 + (int)modes[m] * 1000 + 100);

                uint8_t pk[PK_BYTES], sk[SK_BYTES];
                mlkem768_keypair(pk, sk);

                uint8_t seed32[32];
                randombytes(seed32, sizeof(seed32));

                uint8_t ct[CT_BYTES], ss_exp[SS_BYTES], ss_rej_exp[SS_BYTES], ss_out[SS_BYTES];
                int enc_rc = independent_oracle_encaps_derand(ct, ss_exp, pk, seed32);
                int rej_rc = independent_oracle_compute_rejection(ss_rej_exp, sk, ct);
                assert(enc_rc == 0 && rej_rc == 0);

                tfib_fault_arm(TFIB_FAULT_OP_TWIDDLE, stage, b_idx, bit, false);
                uint32_t status = 0;
                mlkem768_dec_monitored(ss_out, ct, sk, &status);

                bool ss_match = (memcmp(ss_out, ss_exp, SS_BYTES) == 0);
                bool rej_match = (memcmp(ss_out, ss_rej_exp, SS_BYTES) == 0);

                const char *out_str = ss_match ? "VALID_MATCH" : (rej_match ? "REJECTION_MATCH" : "SDC");
                fprintf(fp, "%d,%s,%u,%u,%u,0,0x%08X,%s\n",
                        trial_id++, mode_names[m], stage, b_idx, bit, status, out_str);
            }
        }
        fclose(fp);

        off_t raw_size_post = get_file_size("tfib_raw_results.csv");
        time_t raw_mtime_post = get_file_mtime("tfib_raw_results.csv");

        off_t trial_size_post = get_file_size("tfib_trial_level_results.csv");
        time_t trial_mtime_post = get_file_mtime("tfib_trial_level_results.csv");

        bool historical_raw_untouched = (raw_size_pre == raw_size_post) && (raw_mtime_pre == raw_mtime_post);
        bool historical_trial_untouched = (trial_size_pre == trial_size_post) && (trial_mtime_pre == trial_mtime_post);
        bool new_csv_written = (get_file_size(step2a_csv) > 0);

        bool test_e_pass = historical_raw_untouched && historical_trial_untouched && new_csv_written;
        printf("  - Historical tfib_raw_results.csv Untouched: %s\n", historical_raw_untouched ? "YES" : "NO");
        printf("  - Historical tfib_trial_level_results.csv Untouched: %s\n", historical_trial_untouched ? "YES" : "NO");
        printf("  - Step 2A Test Output CSV Written: %s (%lld bytes)\n", new_csv_written ? "YES" : "NO", (long long)get_file_size(step2a_csv));
        printf("  -> Result: %s\n\n", test_e_pass ? "PASS" : "FAIL");
        if (!test_e_pass) failed_tests++;
    }

    printf("================================================================================\n");
    printf("STEP 2A VALIDATION VERDICT: %s (%d failures)\n",
           (failed_tests == 0) ? "ALL TESTS PASSED (PASS)" : "TESTS FAILED (FAIL)", failed_tests);
    printf("================================================================================\n");

    return (failed_tests == 0) ? 0 : 1;
}
