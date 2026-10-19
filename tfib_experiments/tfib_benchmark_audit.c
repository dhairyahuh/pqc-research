#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <mach/mach_time.h>
#include "tfib_common.h"
#include "tfib_core.h"

#define WARMUP_ROUNDS 2000
#define BENCH_ROUNDS  10000

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

static inline uint64_t get_ns(void) {
    static mach_timebase_info_data_t tb;
    if (tb.denom == 0) mach_timebase_info(&tb);
    uint64_t t = mach_absolute_time();
    return (t * tb.numer) / tb.denom;
}

static int compare_doubles(const void *a, const void *b) {
    double da = *(const double *)a;
    double db = *(const double *)b;
    if (da < db) return -1;
    if (da > db) return 1;
    return 0;
}

typedef struct {
    const char *name;
    const char *condition;
    int num_samples;
    double mean_us;
    double trimmed_mean_us; /* 99.8% trimmed */
    double median_us;
    double stddev_us;
    double iqr_us;
    double min_us;
    double max_us;
    double p95_us;
    double p99_us;
    int outliers_above_1ms;
} bench_stats_t;

static void compute_stats(
    const char *name, const char *cond,
    double *times, int n, bench_stats_t *st
) {
    st->name = name;
    st->condition = cond;
    st->num_samples = n;

    double sum = 0.0;
    st->outliers_above_1ms = 0;
    for (int i = 0; i < n; i++) {
        sum += times[i];
        if (times[i] > 1000.0) st->outliers_above_1ms++;
    }
    st->mean_us = sum / n;

    qsort(times, n, sizeof(double), compare_doubles);
    st->min_us = times[0];
    st->max_us = times[n - 1];
    st->median_us = times[n / 2];
    st->p95_us = times[(size_t)(n * 0.95)];
    st->p99_us = times[(size_t)(n * 0.99)];

    double q1 = times[(size_t)(n * 0.25)];
    double q3 = times[(size_t)(n * 0.75)];
    st->iqr_us = q3 - q1;

    double var = 0.0;
    for (int i = 0; i < n; i++) {
        double d = times[i] - st->mean_us;
        var += d * d;
    }
    st->stddev_us = sqrt(var / n);

    /* 0.1% trimmed mean (exclude bottom 0.1% and top 0.1%) */
    int trim_k = n / 1000;
    if (trim_k < 1) trim_k = 1;
    double trim_sum = 0.0;
    for (int i = trim_k; i < n - trim_k; i++) {
        trim_sum += times[i];
    }
    st->trimmed_mean_us = trim_sum / (n - 2 * trim_k);
}

int main(void) {
    uint8_t pk[PK_BYTES], sk[SK_BYTES], ct[CT_BYTES], ss_enc[SS_BYTES];
    uint8_t ss[SS_BYTES];
    uint32_t status = 0;

    srand(0xDEADBEEF);
    mlkem768_keypair(pk, sk);
    mlkem768_enc(ct, ss_enc, pk);

    FILE *fp_raw = fopen("tfib_benchmark_raw.csv", "w");
    if (!fp_raw) {
        perror("Failed to open tfib_benchmark_raw.csv");
        return 1;
    }
    fprintf(fp_raw, "config,condition,iteration,latency_us\n");

    printf("=========================================================================================\n");
    printf("TFIB BENCHMARK AUDIT: SAMPLE-LEVEL REASSESSMENT & TAIL-LATENCY DECOMPOSITION\n");
    printf("Iterations: %d timed runs per config (%d warmup rounds)\n", BENCH_ROUNDS, WARMUP_ROUNDS);
    printf("=========================================================================================\n\n");

    double *times_base = (double *)malloc(BENCH_ROUNDS * sizeof(double));
    double *times_ref  = (double *)malloc(BENCH_ROUNDS * sizeof(double));
    double *times_meta = (double *)malloc(BENCH_ROUNDS * sizeof(double));
    double *times_ref_fault = (double *)malloc(BENCH_ROUNDS * sizeof(double));

    /* 1. BASELINE (Fault-Free) */
    tfib_set_mode(TFIB_MODE_BASELINE);
    tfib_fault_reset();
    tfib_reset_all_stats();
    for (int i = 0; i < WARMUP_ROUNDS; i++) mlkem768_dec_monitored(ss, ct, sk, &status);
    for (int i = 0; i < BENCH_ROUNDS; i++) {
        uint64_t t0 = get_ns();
        mlkem768_dec_monitored(ss, ct, sk, &status);
        uint64_t t1 = get_ns();
        times_base[i] = (double)(t1 - t0) / 1000.0;
        fprintf(fp_raw, "BASELINE,FAULT_FREE,%d,%.3f\n", i, times_base[i]);
    }

    /* 2. TFIB-REF (Fault-Free) */
    tfib_set_mode(TFIB_MODE_REF);
    tfib_fault_reset();
    tfib_reset_all_stats();
    for (int i = 0; i < WARMUP_ROUNDS; i++) mlkem768_dec_monitored(ss, ct, sk, &status);
    for (int i = 0; i < BENCH_ROUNDS; i++) {
        uint64_t t0 = get_ns();
        mlkem768_dec_monitored(ss, ct, sk, &status);
        uint64_t t1 = get_ns();
        times_ref[i] = (double)(t1 - t0) / 1000.0;
        fprintf(fp_raw, "TFIB_REF,FAULT_FREE,%d,%.3f\n", i, times_ref[i]);
    }

    /* 3. TFIB-META (Fault-Free) */
    tfib_set_mode(TFIB_MODE_META);
    tfib_fault_reset();
    tfib_reset_all_stats();
    for (int i = 0; i < WARMUP_ROUNDS; i++) mlkem768_dec_monitored(ss, ct, sk, &status);
    for (int i = 0; i < BENCH_ROUNDS; i++) {
        uint64_t t0 = get_ns();
        mlkem768_dec_monitored(ss, ct, sk, &status);
        uint64_t t1 = get_ns();
        times_meta[i] = (double)(t1 - t0) / 1000.0;
        fprintf(fp_raw, "TFIB_META,FAULT_FREE,%d,%.3f\n", i, times_meta[i]);
    }

    /* 4. TFIB-REF (Under Active Fault & Recovery) */
    tfib_set_mode(TFIB_MODE_REF);
    for (int i = 0; i < BENCH_ROUNDS; i++) {
        tfib_fault_reset();
        tfib_reset_all_stats();
        tfib_fault_arm(TFIB_FAULT_OP_TWIDDLE, 1, 0, 1, false); /* transient fault layer 1 b_idx 0 */
        uint64_t t0 = get_ns();
        mlkem768_dec_monitored(ss, ct, sk, &status);
        uint64_t t1 = get_ns();
        times_ref_fault[i] = (double)(t1 - t0) / 1000.0;
        fprintf(fp_raw, "TFIB_REF,ACTIVE_RECOVERY,%d,%.3f\n", i, times_ref_fault[i]);
    }

    fclose(fp_raw);

    bench_stats_t st_base, st_ref, st_meta, st_ref_fault;
    compute_stats("BASELINE", "FAULT_FREE", times_base, BENCH_ROUNDS, &st_base);
    compute_stats("TFIB-REF", "FAULT_FREE", times_ref, BENCH_ROUNDS, &st_ref);
    compute_stats("TFIB-META", "FAULT_FREE", times_meta, BENCH_ROUNDS, &st_meta);
    compute_stats("TFIB-REF", "ACTIVE_RECOVERY", times_ref_fault, BENCH_ROUNDS, &st_ref_fault);

    printf("%-10s | %-15s | Mean(us) | TrimMean | Median   | StdDev   | IQR(us)  | p95(us)  | p99(us)  | >1ms Outliers\n",
           "Config", "Condition");
    printf("------------------------------------------------------------------------------------------------------------------------\n");

    bench_stats_t *all_st[] = {&st_base, &st_ref, &st_meta, &st_ref_fault};
    for (int i = 0; i < 4; i++) {
        bench_stats_t *s = all_st[i];
        printf("%-10s | %-15s | %8.2f | %8.2f | %8.2f | %8.2f | %8.2f | %8.2f | %8.2f | %13d\n",
               s->name, s->condition, s->mean_us, s->trimmed_mean_us, s->median_us,
               s->stddev_us, s->iqr_us, s->p95_us, s->p99_us, s->outliers_above_1ms);
    }

    printf("\nBenchmark Analysis & Discrepancy Investigation:\n");
    printf("1. Baseline Fault-Free Mean: %.2f us, Median: %.2f us, IQR: %.2f us\n",
           st_base.mean_us, st_base.median_us, st_base.iqr_us);
    printf("2. TFIB-Ref Fault-Free Mean: %.2f us, Median: %.2f us, Net Overhead: +%.2f%% (median: +%.2f%%)\n",
           st_ref.mean_us, st_ref.median_us,
           ((st_ref.mean_us - st_base.mean_us) / st_base.mean_us) * 100.0,
           ((st_ref.median_us - st_base.median_us) / st_base.median_us) * 100.0);
    printf("3. TFIB-Meta Fault-Free Mean: %.2f us, Median: %.2f us, Net Overhead: +%.2f%% (median: +%.2f%%)\n",
           st_meta.mean_us, st_meta.median_us,
           ((st_meta.mean_us - st_base.mean_us) / st_base.mean_us) * 100.0,
           ((st_meta.median_us - st_base.median_us) / st_base.median_us) * 100.0);
    printf("4. TFIB-Ref Under Active Recovery: Mean: %.2f us, Median: %.2f us, Cost of Rollback & Repair: +%.2f us (+%.2f%% over fault-free TFIB-Ref)\n",
           st_ref_fault.mean_us, st_ref_fault.median_us,
           st_ref_fault.median_us - st_ref.median_us,
           ((st_ref_fault.median_us - st_ref.median_us) / st_ref.median_us) * 100.0);

    free(times_base);
    free(times_ref);
    free(times_meta);
    free(times_ref_fault);

    return 0;
}
