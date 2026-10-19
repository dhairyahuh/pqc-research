#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
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

#include <mach/mach_time.h>

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
    const char *description;
    size_t table_bytes;
    size_t state_bytes;
    double mean_us;
    double median_us;
    double stddev_us;
    double min_us;
    double max_us;
    double p95_us;
    double p99_us;
} bench_result_t;

static void run_benchmark(
    tfib_mode_t mode, const char *name, const char *desc,
    size_t table_bytes, size_t state_bytes,
    const uint8_t *ct, const uint8_t *sk,
    bench_result_t *res
) {
    uint8_t ss[SS_BYTES];
    uint32_t status = 0;
    tfib_set_mode(mode);
    tfib_fault_reset();
    tfib_reset_all_stats();

    /* Warmup */
    for (int i = 0; i < WARMUP_ROUNDS; i++) {
        mlkem768_dec_monitored(ss, ct, sk, &status);
    }

    double *times = (double *)malloc(BENCH_ROUNDS * sizeof(double));
    double sum = 0.0;

    for (int i = 0; i < BENCH_ROUNDS; i++) {
        uint64_t t0 = get_ns();
        mlkem768_dec_monitored(ss, ct, sk, &status);
        uint64_t t1 = get_ns();

        double elapsed_us = (double)(t1 - t0) / 1000.0;
        times[i] = elapsed_us;
        sum += elapsed_us;
    }

    double mean = sum / BENCH_ROUNDS;
    qsort(times, BENCH_ROUNDS, sizeof(double), compare_doubles);

    double var = 0.0;
    for (int i = 0; i < BENCH_ROUNDS; i++) {
        double d = times[i] - mean;
        var += d * d;
    }
    double stddev = sqrt(var / BENCH_ROUNDS);

    res->name = name;
    res->description = desc;
    res->table_bytes = table_bytes;
    res->state_bytes = state_bytes;
    res->mean_us = mean;
    res->median_us = times[BENCH_ROUNDS / 2];
    res->stddev_us = stddev;
    res->min_us = times[0];
    res->max_us = times[BENCH_ROUNDS - 1];
    res->p95_us = times[(size_t)(BENCH_ROUNDS * 0.95)];
    res->p99_us = times[(size_t)(BENCH_ROUNDS * 0.99)];

    free(times);
}

int main(void) {
    uint8_t pk[PK_BYTES], sk[SK_BYTES], ct[CT_BYTES], ss_enc[SS_BYTES];
    srand(0xDEADBEEF);
    mlkem768_keypair(pk, sk);
    mlkem768_enc(ct, ss_enc, pk);

    printf("=========================================================================================\n");
    printf("TFIB RESEARCH EXTENSION: PERFORMANCE AND OVERHEAD BENCHMARK\n");
    printf("Host: Apple M3 Pro | OS: Darwin 25.1.0 | Compiler: Apple Clang 17.0.0 (-O3)\n");
    printf("Iterations: %d timed runs per config (%d warmup rounds)\n", BENCH_ROUNDS, WARMUP_ROUNDS);
    printf("=========================================================================================\n\n");

    bench_result_t baseline_res, ref_res, meta_res;

    /* Baseline Monitor */
    run_benchmark(
        TFIB_MODE_BASELINE, "BASELINE",
        "Original Dual-Transform Invariant Monitor (No Twiddle Binding)",
        0, sizeof(uint32_t) * 5,
        ct, sk, &baseline_res
    );

    /* Strategy 1: TFIB-Ref */
    run_benchmark(
        TFIB_MODE_REF, "TFIB-REF",
        "Dual Reference Table Cross-Validation + In-Place Rollback/Repair",
        sizeof(int16_t) * 128, sizeof(tfib_stats_t) + sizeof(int16_t) * 128,
        ct, sk, &ref_res
    );

    /* Strategy 2: TFIB-Meta */
    run_benchmark(
        TFIB_MODE_META, "TFIB-META",
        "Precomputed 16-bit Tag Integrity Check + Immediate Fail-Stop",
        sizeof(uint16_t) * 128, sizeof(tfib_stats_t) + sizeof(uint16_t) * 128,
        ct, sk, &meta_res
    );

    printf("%-12s | %-10s | %-10s | %-10s | %-10s | %-10s | %-12s | %-10s\n",
           "Config", "Mean (us)", "Median", "StdDev", "p95 (us)", "p99 (us)", "Overhead vs BL", "Mem Overhead");
    printf("---------------------------------------------------------------------------------------------------------\n");

    printf("%-12s | %10.2f | %10.2f | %10.2f | %10.2f | %10.2f | %12s | %8zu B\n",
           baseline_res.name, baseline_res.mean_us, baseline_res.median_us, baseline_res.stddev_us,
           baseline_res.p95_us, baseline_res.p99_us, "0.0% (ref)",
           baseline_res.table_bytes + baseline_res.state_bytes);

    double ref_overhead = ((ref_res.mean_us - baseline_res.mean_us) / baseline_res.mean_us) * 100.0;
    printf("%-12s | %10.2f | %10.2f | %10.2f | %10.2f | %10.2f | %+11.2f%% | %8zu B\n",
           ref_res.name, ref_res.mean_us, ref_res.median_us, ref_res.stddev_us,
           ref_res.p95_us, ref_res.p99_us, ref_overhead,
           ref_res.table_bytes + ref_res.state_bytes);

    double meta_overhead = ((meta_res.mean_us - baseline_res.mean_us) / baseline_res.mean_us) * 100.0;
    printf("%-12s | %10.2f | %10.2f | %10.2f | %10.2f | %10.2f | %+11.2f%% | %8zu B\n",
           meta_res.name, meta_res.mean_us, meta_res.median_us, meta_res.stddev_us,
           meta_res.p95_us, meta_res.p99_us, meta_overhead,
           meta_res.table_bytes + meta_res.state_bytes);

    printf("\nDetailed Latency & Memory Breakdown:\n");
    printf("1. Baseline:\n");
    printf("   - Memory: 0 bytes static tables (uses operational zetas directly), 20 bytes monitor telemetry\n");
    printf("   - Latency: Mean = %.3f us, Median = %.3f us, Min = %.3f us, Max = %.3f us\n",
           baseline_res.mean_us, baseline_res.median_us, baseline_res.min_us, baseline_res.max_us);
    printf("2. TFIB-Ref:\n");
    printf("   - Memory: 256 bytes static reference table (128 x int16_t), 32 bytes runtime telemetry\n");
    printf("   - Latency: Mean = %.3f us, Median = %.3f us, Min = %.3f us, Max = %.3f us\n",
           ref_res.mean_us, ref_res.median_us, ref_res.min_us, ref_res.max_us);
    printf("   - Net Delta: %+.3f us (%.2f%% overhead over baseline monitor)\n",
           ref_res.mean_us - baseline_res.mean_us, ref_overhead);
    printf("3. TFIB-Meta:\n");
    printf("   - Memory: 256 bytes static tag table (128 x uint16_t), 24 bytes runtime telemetry\n");
    printf("   - Latency: Mean = %.3f us, Median = %.3f us, Min = %.3f us, Max = %.3f us\n",
           meta_res.mean_us, meta_res.median_us, meta_res.min_us, meta_res.max_us);
    printf("   - Net Delta: %+.3f us (%.2f%% overhead over baseline monitor)\n",
           meta_res.mean_us - baseline_res.mean_us, meta_overhead);

    /* Write benchmark CSV summary */
    FILE *fp = fopen("tfib_experiments/tfib_benchmark_results.csv", "w");
    if (fp) {
        fprintf(fp, "config,mean_us,median_us,stddev_us,min_us,max_us,p95_us,p99_us,overhead_pct,memory_overhead_bytes\n");
        fprintf(fp, "%s,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.2f,%zu\n",
                baseline_res.name, baseline_res.mean_us, baseline_res.median_us, baseline_res.stddev_us,
                baseline_res.min_us, baseline_res.max_us, baseline_res.p95_us, baseline_res.p99_us,
                0.0, baseline_res.table_bytes + baseline_res.state_bytes);
        fprintf(fp, "%s,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.2f,%zu\n",
                ref_res.name, ref_res.mean_us, ref_res.median_us, ref_res.stddev_us,
                ref_res.min_us, ref_res.max_us, ref_res.p95_us, ref_res.p99_us,
                ref_overhead, ref_res.table_bytes + ref_res.state_bytes);
        fprintf(fp, "%s,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.2f,%zu\n",
                meta_res.name, meta_res.mean_us, meta_res.median_us, meta_res.stddev_us,
                meta_res.min_us, meta_res.max_us, meta_res.p95_us, meta_res.p99_us,
                meta_overhead, meta_res.table_bytes + meta_res.state_bytes);
        fclose(fp);
        printf("\nSaved benchmark metrics to tfib_experiments/tfib_benchmark_results.csv\n");
    }

    return 0;
}
