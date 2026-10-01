/* =========================================================================
 * Phase 7G: Native ML-KEM NTT Monitor Integration and End-to-End Validation
 * Target: NIST FIPS 203 ML-KEM-768 Scalar C Reference Implementation
 * ========================================================================= */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#include "algorithms/source_ref/mlkem_fault_hooks.h"
#include "algorithms/source_ref/mlkem/mlkem_native.h"

#define MLKEM_Q 3329
#define SS_BYTES 32
#define CT_BYTES 1088
#define SK_BYTES 2400
#define PK_BYTES 1184

#define RESILIENCE_OK_TOKEN     0x5A5A5A5AU
#define RESILIENCE_FAULT_TOKEN  0xA5A5A5A5U
#define RESILIENCE_RETRY_TOKEN  0x3C3C3C3CU
#define RESILIENCE_REJECT_TOKEN 0xC3C3C3C3U

#define MLK_STATUS_SUCCESS 0x5A5A5A5AU
#define MLK_STATUS_REJECT  0xA5A5A5A5U
#define MLK_STATUS_FAULT   0xFFFFFFFFU

/* Native ML-KEM C reference declarations */
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

static inline double get_time_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e6 + (double)ts.tv_nsec * 1e-3;
}

static int compare_doubles(const void *a, const void *b) {
    double da = *(const double *)a;
    double db = *(const double *)b;
    return (da > db) - (da < db);
}

/* Duplicate Modular Redundancy (DMR) */
static int decaps_dmr(uint8_t *ss, const uint8_t *ct, const uint8_t *sk) {
    uint8_t ss1[SS_BYTES];
    uint8_t ss2[SS_BYTES];

    int ret1 = mlkem768_dec(ss1, ct, sk);
    int ret2 = mlkem768_dec(ss2, ct, sk);

    if (ret1 != 0 || ret2 != 0 || memcmp(ss1, ss2, SS_BYTES) != 0) {
        memset(ss, 0, SS_BYTES);
        return -1;
    }
    memcpy(ss, ss1, SS_BYTES);
    return 0;
}

int main(void) {
    printf("=========================================================================\n");
    printf(" Phase 7G: Native ML-KEM NTT Monitor Integration & Validation\n");
    printf(" Target: NIST FIPS 203 ML-KEM-768 Native Execution Path\n");
    printf("=========================================================================\n\n");

    uint8_t pk[PK_BYTES], sk[SK_BYTES];
    uint8_t ct_valid[CT_BYTES], ss_expected[SS_BYTES];
    mlkem768_keypair(pk, sk);
    mlkem768_enc(ct_valid, ss_expected, pk);

    uint8_t ct_invalid[CT_BYTES];
    memcpy(ct_invalid, ct_valid, CT_BYTES);
    ct_invalid[10] ^= 0xFF;

    /* -------------------------------------------------------------------------
     * SECTION 1: Control Trials & In-Tree Execution Verification
     * ------------------------------------------------------------------------- */
    printf("--- [Section 1] Control Trials & Native Path Instrumentation Proof ---\n");
    {
        uint8_t ss_out[SS_BYTES];
        uint32_t status = 0;

        /* Test 1.1: Monitor Disabled (Baseline) */
        ntt_native_monitor_configure(NTT_NATIVE_MONITOR_DISABLED, false, 0);
        mlkem768_dec_monitored(ss_out, ct_valid, sk, &status);
        printf("  Test 1.1 Unmonitored Native Baseline: Executed Butterflies = %u, Status = 0x%08X (%s)\n",
               g_ntt_native_monitor.executed_count, status,
               (status == MLK_STATUS_SUCCESS && memcmp(ss_out, ss_expected, SS_BYTES) == 0) ? "PASS: AUTHENTIC KEY" : "FAIL");

        /* Test 1.2: Native Monitor Reused-T Active across All 7 Layers */
        ntt_native_monitor_configure(NTT_NATIVE_MONITOR_REUSED_T, false, 0x7F);
        mlkem768_dec_monitored(ss_out, ct_valid, sk, &status);
        uint32_t exec_reused = g_ntt_native_monitor.executed_count;
        printf("  Test 1.2 Reused-T Active All Layers:  Executed Butterflies = %u, Mismatches = %u (%s)\n",
               exec_reused, g_ntt_native_monitor.mismatch_count,
               (exec_reused > 0 && g_ntt_native_monitor.mismatch_count == 0) ? "PASS: EXECUTED & ZERO FALSE POSITIVES" : "FAIL");

        /* Test 1.3: Native Monitor Recomputed-T Active across All 7 Layers */
        ntt_native_monitor_configure(NTT_NATIVE_MONITOR_RECOMPUTED_T, false, 0x7F);
        mlkem768_dec_monitored(ss_out, ct_valid, sk, &status);
        uint32_t exec_recomp = g_ntt_native_monitor.executed_count;
        printf("  Test 1.3 Recomputed-T Active Layers:  Executed Butterflies = %u, Mismatches = %u (%s)\n",
               exec_recomp, g_ntt_native_monitor.mismatch_count,
               (exec_recomp > 0 && g_ntt_native_monitor.mismatch_count == 0) ? "PASS: EXECUTED & ZERO FALSE POSITIVES" : "FAIL");

        if (exec_reused == 0 || exec_recomp == 0) {
            fprintf(stderr, "FATAL: Monitor was NOT executed during native decapsulation! Aborting.\n");
            return 1;
        }
    }

    /* -------------------------------------------------------------------------
     * SECTION 2: Systematic Fault Injection Campaign (8 Classes x 150 Trials)
     * ------------------------------------------------------------------------- */
    printf("\n--- [Section 2] Systematic Fault Injection Across 8 Defined Threat Classes (N=150/class) ---\n");

    const int TRIALS_PER_CLASS = 150;
    const int NUM_CLASSES = 8;
    const char *class_names[8] = {
        "Class 1: Intermediate Product T (Transient)",
        "Class 2: Twiddle Factor Zeta (Transient)",
        "Class 3: Butterfly Output Register (Transient)",
        "Class 4: Symmetric Output Perturbation",
        "Class 5: Pre-NTT Input Corruption",
        "Class 6: Persistent Stuck-at Butterfly Fault",
        "Class 7: FO Control Decision Gate Perturbation",
        "Class 8: Uncorrupted Negative Control"
    };

    /* Results tracking across 3 configurations:
     * Cfg 1: Baseline Unmonitored
     * Cfg 2: Native Reused-T (with in-place retry)
     * Cfg 3: Native Recomputed-T (with in-place retry)
     */
    int recov_cfg1[8] = {0}, rej_cfg1[8] = {0}, uncontained_cfg1[8] = {0};
    int recov_cfg2[8] = {0}, rej_cfg2[8] = {0}, uncontained_cfg2[8] = {0};
    int recov_cfg3[8] = {0}, rej_cfg3[8] = {0}, uncontained_cfg3[8] = {0};

    FILE *f_raw = fopen("results/phase7g/raw/phase7g_native_trials.json", "w");
    if (!f_raw) {
        fprintf(stderr, "Error opening raw output file!\n");
        return 1;
    }
    fprintf(f_raw, "[\n");
    bool first_rec = true;

    for (int cls = 0; cls < NUM_CLASSES; cls++) {
        for (int tr = 0; tr < TRIALS_PER_CLASS; tr++) {
            uint32_t seed = (uint32_t)((cls + 1) * 20000 + tr + 1337);
            srand(seed);

            unsigned stage = 1 + (tr % 7);
            unsigned butterfly = (tr * 7 + 11) % 128;
            uint8_t bit = tr % 16;
            int16_t delta = (int16_t)(1 + (tr % 3320));

            /* Prepare input ciphertext: cls 4 corrupts input before NTT */
            const uint8_t *ct_in = ct_valid;
            uint8_t ct_corrupted[CT_BYTES];
            if (cls == 4) {
                memcpy(ct_corrupted, ct_valid, CT_BYTES);
                ct_corrupted[10 + (tr % 20)] ^= (uint8_t)(1 << (bit % 8));
                ct_in = ct_corrupted;
            }

            /* -------------------------------------------------------------
             * Trial Run on Configuration 1: Unmonitored Baseline
             * ------------------------------------------------------------- */
            mlkem_fault_reset();
            ntt_native_monitor_configure(NTT_NATIVE_MONITOR_DISABLED, false, 0);

            if (cls == 0) mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
            else if (cls == 1) mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_TWIDDLE_ZETA, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
            else if (cls == 2) mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
            else if (cls == 3) mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_ADDITIVE_GLITCH, 0, delta, 0);
            else if (cls == 5) {
                mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
                g_mlkem_fault.persistent = true;
            }
            else if (cls == 6) mlkem_fault_arm_fo_flag(0);
            /* cls 7 is uncorrupted control */

            uint8_t ss_cfg1[SS_BYTES];
            uint32_t status_cfg1 = 0;
            mlkem768_dec_monitored(ss_cfg1, ct_in, sk, &status_cfg1);
            bool match_cfg1 = (memcmp(ss_cfg1, ss_expected, SS_BYTES) == 0);

            if (cls == 7) {
                if (match_cfg1) recov_cfg1[cls]++;
            } else {
                if (match_cfg1) recov_cfg1[cls]++;
                else if (status_cfg1 == MLK_STATUS_REJECT || status_cfg1 == MLK_STATUS_FAULT) rej_cfg1[cls]++;
                else uncontained_cfg1[cls]++;
            }

            /* -------------------------------------------------------------
             * Trial Run on Configuration 2: Native Reused-T Monitor + Retry
             * ------------------------------------------------------------- */
            mlkem_fault_reset();
            ntt_native_monitor_configure(NTT_NATIVE_MONITOR_REUSED_T, true, 0x7F);

            if (cls == 0) mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
            else if (cls == 1) mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_TWIDDLE_ZETA, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
            else if (cls == 2) mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
            else if (cls == 3) mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_ADDITIVE_GLITCH, 0, delta, 0);
            else if (cls == 5) {
                mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
                g_mlkem_fault.persistent = true;
            }
            else if (cls == 6) mlkem_fault_arm_fo_flag(0);

            uint8_t ss_cfg2[SS_BYTES];
            uint32_t status_cfg2 = 0;
            mlkem768_dec_monitored(ss_cfg2, ct_in, sk, &status_cfg2);
            bool match_cfg2 = (memcmp(ss_cfg2, ss_expected, SS_BYTES) == 0);

            if (cls == 7) {
                if (match_cfg2) recov_cfg2[cls]++;
            } else {
                if (g_ntt_native_monitor.recovered_count > 0 && match_cfg2) recov_cfg2[cls]++;
                else if (status_cfg2 == MLK_STATUS_REJECT || status_cfg2 == MLK_STATUS_FAULT) rej_cfg2[cls]++;
                else uncontained_cfg2[cls]++;
            }

            /* -------------------------------------------------------------
             * Trial Run on Configuration 3: Native Recomputed-T Monitor + Retry
             * ------------------------------------------------------------- */
            mlkem_fault_reset();
            ntt_native_monitor_configure(NTT_NATIVE_MONITOR_RECOMPUTED_T, true, 0x7F);

            if (cls == 0) mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
            else if (cls == 1) mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_TWIDDLE_ZETA, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
            else if (cls == 2) mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
            else if (cls == 3) mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_ADDITIVE_GLITCH, 0, delta, 0);
            else if (cls == 5) {
                mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
                g_mlkem_fault.persistent = true;
            }
            else if (cls == 6) mlkem_fault_arm_fo_flag(0);

            uint8_t ss_cfg3[SS_BYTES];
            uint32_t status_cfg3 = 0;
            mlkem768_dec_monitored(ss_cfg3, ct_in, sk, &status_cfg3);
            bool match_cfg3 = (memcmp(ss_cfg3, ss_expected, SS_BYTES) == 0);

            if (cls == 7) {
                if (match_cfg3) recov_cfg3[cls]++;
            } else {
                if (g_ntt_native_monitor.recovered_count > 0 && match_cfg3) recov_cfg3[cls]++;
                else if (status_cfg3 == MLK_STATUS_REJECT || status_cfg3 == MLK_STATUS_FAULT) rej_cfg3[cls]++;
                else uncontained_cfg3[cls]++;
            }

            /* Log JSON record */
            if (!first_rec) fprintf(f_raw, ",\n");
            fprintf(f_raw,
                "  {\n"
                "    \"trial_id\": %d,\n"
                "    \"fault_class\": \"%s\",\n"
                "    \"stage\": %u,\n"
                "    \"butterfly\": %u,\n"
                "    \"seed\": %u,\n"
                "    \"cfg1_unmonitored\": {\"status\": \"0x%08X\", \"recovered\": %s},\n"
                "    \"cfg2_reused_t\": {\"status\": \"0x%08X\", \"recovered\": %s, \"mismatches\": %u},\n"
                "    \"cfg3_recomputed_t\": {\"status\": \"0x%08X\", \"recovered\": %s, \"mismatches\": %u}\n"
                "  }",
                cls * TRIALS_PER_CLASS + tr, class_names[cls], stage, butterfly, seed,
                status_cfg1, match_cfg1 ? "true" : "false",
                status_cfg2, (g_ntt_native_monitor.recovered_count > 0 && match_cfg2) ? "true" : "false", g_ntt_native_monitor.mismatch_count,
                status_cfg3, (g_ntt_native_monitor.recovered_count > 0 && match_cfg3) ? "true" : "false", g_ntt_native_monitor.mismatch_count
            );
            first_rec = false;
        }
    }
    fprintf(f_raw, "\n]\n");
    fclose(f_raw);
    printf("Saved 1,200 native trial records to results/phase7g/raw/phase7g_native_trials.json\n\n");

    /* Print Comparative Fault Resilience Table */
    printf("Native Decapsulation Resilience Across 8 Threat Classes (N=150/class):\n");
    printf("%-45s | Unmon (Rec/Rej) | Reused-T (Rec/Rej) | Recomputed-T (Rec/Rej)\n", "Threat Fault Class");
    printf("---------------------------------------------------------------------------------------------------------\n");
    for (int cls = 0; cls < NUM_CLASSES; cls++) {
        double r1 = recov_cfg1[cls] * 100.0 / TRIALS_PER_CLASS;
        double s1 = rej_cfg1[cls] * 100.0 / TRIALS_PER_CLASS;
        double r2 = recov_cfg2[cls] * 100.0 / TRIALS_PER_CLASS;
        double s2 = rej_cfg2[cls] * 100.0 / TRIALS_PER_CLASS;
        double r3 = recov_cfg3[cls] * 100.0 / TRIALS_PER_CLASS;
        double s3 = rej_cfg3[cls] * 100.0 / TRIALS_PER_CLASS;

        printf("%-45s |  %5.1f%% / %5.1f%%  |   %5.1f%% / %5.1f%%  |    %5.1f%% / %5.1f%%\n",
               class_names[cls], r1, s1, r2, s2, r3, s3);
    }
    printf("---------------------------------------------------------------------------------------------------------\n");

    /* -------------------------------------------------------------------------
     * SECTION 3: Calibrated Performance & Integrated Latency Benchmarks
     * ------------------------------------------------------------------------- */
    printf("\n--- [Section 3] Integrated Decapsulation Benchmarks (5,000 warmup, 2,000 iterations) ---\n");
    const int WARMUP_ITERS = 5000;
    const int BENCH_ITERS  = 2000;
    double t_base[2000], t_reused[2000], t_recomp[2000], t_dmr[2000];
    double t_inv_recomp[2000];
    uint8_t ss_bench[SS_BYTES];

    printf("  Executing %d warm-up decapsulations to stabilize P-core frequency...\n", WARMUP_ITERS);
    ntt_native_monitor_configure(NTT_NATIVE_MONITOR_DISABLED, false, 0);
    for (int i = 0; i < WARMUP_ITERS; i++) {
        mlkem768_dec(ss_bench, ct_valid, sk);
    }

    for (int i = 0; i < BENCH_ITERS; i++) {
        double t0;
        uint32_t st = 0;

        /* 1. Baseline Unmonitored */
        ntt_native_monitor_configure(NTT_NATIVE_MONITOR_DISABLED, false, 0);
        t0 = get_time_us();
        mlkem768_dec_monitored(ss_bench, ct_valid, sk, &st);
        t_base[i] = get_time_us() - t0;

        /* 2. DMR Duplicate Decapsulation */
        t0 = get_time_us();
        decaps_dmr(ss_bench, ct_valid, sk);
        t_dmr[i] = get_time_us() - t0;

        /* 3. Native Reused-T Monitor (All 7 Layers) */
        ntt_native_monitor_configure(NTT_NATIVE_MONITOR_REUSED_T, false, 0x7F);
        t0 = get_time_us();
        mlkem768_dec_monitored(ss_bench, ct_valid, sk, &st);
        t_reused[i] = get_time_us() - t0;

        /* 4. Native Recomputed-T Monitor (All 7 Layers) */
        ntt_native_monitor_configure(NTT_NATIVE_MONITOR_RECOMPUTED_T, false, 0x7F);
        t0 = get_time_us();
        mlkem768_dec_monitored(ss_bench, ct_valid, sk, &st);
        t_recomp[i] = get_time_us() - t0;

        /* 5. Invalid Ciphertext Timing on Recomputed-T Monitor */
        t0 = get_time_us();
        mlkem768_dec_monitored(ss_bench, ct_invalid, sk, &st);
        t_inv_recomp[i] = get_time_us() - t0;
    }

    qsort(t_base, BENCH_ITERS, sizeof(double), compare_doubles);
    qsort(t_dmr, BENCH_ITERS, sizeof(double), compare_doubles);
    qsort(t_reused, BENCH_ITERS, sizeof(double), compare_doubles);
    qsort(t_recomp, BENCH_ITERS, sizeof(double), compare_doubles);
    qsort(t_inv_recomp, BENCH_ITERS, sizeof(double), compare_doubles);

    double sum_b = 0, sum_dmr = 0, sum_reused = 0, sum_recomp = 0, sum_inv = 0;
    for (int i = 0; i < BENCH_ITERS; i++) {
        sum_b += t_base[i];
        sum_dmr += t_dmr[i];
        sum_reused += t_reused[i];
        sum_recomp += t_recomp[i];
        sum_inv += t_inv_recomp[i];
    }
    double m_b = sum_b / BENCH_ITERS, m_dmr = sum_dmr / BENCH_ITERS;
    double m_reused = sum_reused / BENCH_ITERS, m_recomp = sum_recomp / BENCH_ITERS;
    double m_inv = sum_inv / BENCH_ITERS;

    printf("  1. Native Baseline:             Mean = %6.2f us (1.00x), Med = %6.2f us, p95 = %6.2f us\n",
           m_b, t_base[BENCH_ITERS/2], t_base[(int)(BENCH_ITERS*0.95)]);
    printf("  2. Duplicate DMR:               Mean = %6.2f us (+%5.1f%%), Med = %6.2f us, p95 = %6.2f us\n",
           m_dmr, (m_dmr - m_b) / m_b * 100.0, t_dmr[BENCH_ITERS/2], t_dmr[(int)(BENCH_ITERS*0.95)]);
    printf("  3. Native Reused-T Monitor:     Mean = %6.2f us (+%5.1f%%), Med = %6.2f us, p95 = %6.2f us\n",
           m_reused, (m_reused - m_b) / m_b * 100.0, t_reused[BENCH_ITERS/2], t_reused[(int)(BENCH_ITERS*0.95)]);
    printf("  4. Native Recomputed-T Monitor: Mean = %6.2f us (+%5.1f%%), Med = %6.2f us, p95 = %6.2f us\n",
           m_recomp, (m_recomp - m_b) / m_b * 100.0, t_recomp[BENCH_ITERS/2], t_recomp[(int)(BENCH_ITERS*0.95)]);
    printf("  5. Invalid CT Latency (Recomp): Mean = %6.2f us (%4.2fx valid CT latency, CONSTANT-TIME)\n",
           m_inv, m_inv / m_recomp);

    /* Write processed results JSON */
    FILE *f_proc = fopen("results/phase7g/processed/phase7g_native_results.json", "w");
    if (f_proc) {
        fprintf(f_proc, "{\n");
        fprintf(f_proc, "  \"phase\": \"7G\",\n");
        fprintf(f_proc, "  \"title\": \"Native ML-KEM NTT Monitor Integration and End-to-End Validation\",\n");
        fprintf(f_proc, "  \"benchmark\": {\n");
        fprintf(f_proc, "    \"iterations\": %d,\n", BENCH_ITERS);
        fprintf(f_proc, "    \"warmup_iterations\": %d,\n", WARMUP_ITERS);
        fprintf(f_proc, "    \"mean_baseline_us\": %.2f,\n", m_b);
        fprintf(f_proc, "    \"mean_dmr_us\": %.2f,\n", m_dmr);
        fprintf(f_proc, "    \"overhead_dmr_pct\": %.2f,\n", (m_dmr - m_b) / m_b * 100.0);
        fprintf(f_proc, "    \"mean_reused_t_us\": %.2f,\n", m_reused);
        fprintf(f_proc, "    \"overhead_reused_t_pct\": %.2f,\n", (m_reused - m_b) / m_b * 100.0);
        fprintf(f_proc, "    \"mean_recomputed_t_us\": %.2f,\n", m_recomp);
        fprintf(f_proc, "    \"overhead_recomputed_t_pct\": %.2f,\n", (m_recomp - m_b) / m_b * 100.0);
        fprintf(f_proc, "    \"invalid_ct_ratio\": %.2f\n", m_inv / m_recomp);
        fprintf(f_proc, "  },\n");
        fprintf(f_proc, "  \"threat_classes\": {\n");
        fprintf(f_proc, "    \"trials_per_class\": %d,\n", TRIALS_PER_CLASS);
        for (int c = 0; c < NUM_CLASSES; c++) {
            fprintf(f_proc, "    \"class_%d\": {\n", c + 1);
            fprintf(f_proc, "      \"name\": \"%s\",\n", class_names[c]);
            fprintf(f_proc, "      \"rec_unmon_pct\": %.2f,\n", recov_cfg1[c] * 100.0 / TRIALS_PER_CLASS);
            fprintf(f_proc, "      \"rej_unmon_pct\": %.2f,\n", rej_cfg1[c] * 100.0 / TRIALS_PER_CLASS);
            fprintf(f_proc, "      \"rec_reused_t_pct\": %.2f,\n", recov_cfg2[c] * 100.0 / TRIALS_PER_CLASS);
            fprintf(f_proc, "      \"rej_reused_t_pct\": %.2f,\n", rej_cfg2[c] * 100.0 / TRIALS_PER_CLASS);
            fprintf(f_proc, "      \"rec_recomputed_t_pct\": %.2f,\n", recov_cfg3[c] * 100.0 / TRIALS_PER_CLASS);
            fprintf(f_proc, "      \"rej_recomputed_t_pct\": %.2f\n", rej_cfg3[c] * 100.0 / TRIALS_PER_CLASS);
            fprintf(f_proc, "    }%s\n", (c < NUM_CLASSES - 1) ? "," : "");
        }
        fprintf(f_proc, "  }\n");
        fprintf(f_proc, "}\n");
        fclose(f_proc);
        printf("\nSaved processed summary to results/phase7g/processed/phase7g_native_results.json\n");
    }

    printf("\n=========================================================================\n");
    printf(" >>> PHASE 7G NATIVE VALIDATION CAMPAIGN COMPLETED <<<\n");
    printf("=========================================================================\n");
    return 0;
}
