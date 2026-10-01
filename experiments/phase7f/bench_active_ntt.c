#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <string.h>

#define MLKEM_Q 3329
#define MLKEM_Q_PRIME -3327

static const int16_t g_mlk_zetas[128] = {
    -1044, -758,  -359,  -1517, 1493,  1422,  287,   202,  -171,  622,   1577,
    182,   962,   -1202, -1474, 1468,  573,   -1325, 264,  383,   -829,  1458,
    -1602, -130,  -681,  1017,  732,   608,   -1542, 411,  -205,  -1571, 1223,
    652,   -552,  1015,  -1293, 1491,  -282,  -1544, 516,  -8,    -320,  -666,
    -1618, -1162, 126,   1469,  -853,  -90,   -271,  830,  107,   -1421, -247,
    -951,  -398,  961,   -1508, -725,  448,   -1065, 677,  -1275, -1103, 430,
    555,   843,   -1251, 871,   1550,  105,   422,   587,  177,   -235,  -291,
    -460,  1574,  1653,  -246,  778,   1159,  -147,  -777, 1483,  -602,  1119,
    -1590, 644,   -872,  349,   418,   329,   -156,  -75,  817,   1097,  603,
    610,   1322,  -1285, -1465, 384,   -1215, -136,  1218, -1335, -874,  220,
    -1187, -1659, -1185, -1530, -1278, 794,   -1510, -854, -870,  478,   -108,
    -308,  996,   991,   958,   -1460, 1522,  1628
};

static inline int16_t fqmul_c(int16_t a, int16_t b) {
    int32_t prod = (int32_t)a * (int32_t)b;
    int16_t u = (int16_t)((int32_t)((int16_t)prod) * MLKEM_Q_PRIME);
    int32_t t = (int32_t)u * MLKEM_Q;
    t = prod - t;
    t >>= 16;
    return (int16_t)t;
}

typedef struct {
    int16_t coeffs[256];
} poly_t;

static void ntt_unmonitored(poly_t *p) {
    int16_t *r = p->coeffs;
    for (unsigned layer = 1; layer <= 7; layer++) {
        unsigned k = 1u << (layer - 1);
        unsigned len = 256u >> layer;
        for (unsigned start = 0; start < 256; start += 2 * len) {
            int16_t zeta = g_mlk_zetas[k++];
            for (unsigned j = start; j < start + len; j++) {
                int16_t u = r[j];
                int16_t v = r[j + len];
                int16_t t = fqmul_c(v, zeta);
                r[j + len] = (int16_t)(u - t);
                r[j] = (int16_t)(u + t);
            }
        }
    }
}

static void ntt_monitored_reused_t(poly_t *p, uint32_t layer_mask, uint32_t *fault_flag) {
    int16_t *r = p->coeffs;
    uint32_t fault_accum = 0;
    for (unsigned layer = 1; layer <= 7; layer++) {
        unsigned k = 1u << (layer - 1);
        unsigned len = 256u >> layer;
        bool monitor = ((layer_mask >> (layer - 1)) & 1u) != 0;
        for (unsigned start = 0; start < 256; start += 2 * len) {
            int16_t zeta = g_mlk_zetas[k++];
            for (unsigned j = start; j < start + len; j++) {
                int16_t u = r[j];
                int16_t v = r[j + len];
                int16_t t = fqmul_c(v, zeta);
                int16_t v_out = (int16_t)(u - t);
                int16_t u_out = (int16_t)(u + t);
                if (monitor) {
                    int32_t diff_c = ((int32_t)u_out - (int32_t)v_out - 2 * (int32_t)t) % MLKEM_Q;
                    int32_t sum_c  = ((int32_t)u_out + (int32_t)v_out - 2 * (int32_t)u) % MLKEM_Q;
                    if (diff_c != 0 || sum_c != 0) fault_accum |= 1;
                }
                r[j + len] = v_out;
                r[j] = u_out;
            }
        }
    }
    if (fault_flag) *fault_flag |= fault_accum;
}

static void ntt_monitored_recomputed_t(poly_t *p, uint32_t layer_mask, uint32_t *fault_flag) {
    int16_t *r = p->coeffs;
    uint32_t fault_accum = 0;
    for (unsigned layer = 1; layer <= 7; layer++) {
        unsigned k = 1u << (layer - 1);
        unsigned len = 256u >> layer;
        bool monitor = ((layer_mask >> (layer - 1)) & 1u) != 0;
        for (unsigned start = 0; start < 256; start += 2 * len) {
            int16_t zeta = g_mlk_zetas[k++];
            for (unsigned j = start; j < start + len; j++) {
                int16_t u = r[j];
                int16_t v = r[j + len];
                int16_t t = fqmul_c(v, zeta);
                int16_t v_out = (int16_t)(u - t);
                int16_t u_out = (int16_t)(u + t);
                if (monitor) {
                    /* Independent recomputation of t to detect multiplier/twiddle faults */
                    int16_t t_check = fqmul_c(v, zeta);
                    int32_t diff_c = ((int32_t)u_out - (int32_t)v_out - 2 * (int32_t)t_check) % MLKEM_Q;
                    int32_t sum_c  = ((int32_t)u_out + (int32_t)v_out - 2 * (int32_t)u) % MLKEM_Q;
                    if (diff_c != 0 || sum_c != 0) fault_accum |= 1;
                }
                r[j + len] = v_out;
                r[j] = u_out;
            }
        }
    }
    if (fault_flag) *fault_flag |= fault_accum;
}

static inline double get_time_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e9 + (double)ts.tv_nsec;
}

int main(void) {
    const int ITERS = 20000;
    poly_t p;
    for (int i = 0; i < 256; i++) p.coeffs[i] = (int16_t)(i * 3 + 1);

    uint32_t flag = 0;
    double t0, t_unmon = 0, t_reused_l7 = 0, t_reused_all = 0, t_recomputed_all = 0;

    for (int i = 0; i < ITERS; i++) {
        poly_t t_p = p;
        t0 = get_time_ns();
        ntt_unmonitored(&t_p);
        t_unmon += get_time_ns() - t0;

        t_p = p;
        t0 = get_time_ns();
        ntt_monitored_reused_t(&t_p, 0x40, &flag);
        t_reused_l7 += get_time_ns() - t0;

        t_p = p;
        t0 = get_time_ns();
        ntt_monitored_reused_t(&t_p, 0x7F, &flag);
        t_reused_all += get_time_ns() - t0;

        t_p = p;
        t0 = get_time_ns();
        ntt_monitored_recomputed_t(&t_p, 0x7F, &flag);
        t_recomputed_all += get_time_ns() - t0;
    }

    printf("Single Poly NTT Benchmarks (N=%d iterations):\n", ITERS);
    printf("  1. Unmonitored NTT:               %6.2f ns (1.00x)\n", t_unmon / ITERS);
    printf("  2. Monitored (Reused t, L7 only): %6.2f ns (+%5.1f%%)\n",
           t_reused_l7 / ITERS, (t_reused_l7 - t_unmon) / t_unmon * 100.0);
    printf("  3. Monitored (Reused t, All L1-7):%6.2f ns (+%5.1f%%)\n",
           t_reused_all / ITERS, (t_reused_all - t_unmon) / t_unmon * 100.0);
    printf("  4. Monitored (Recomputed t, L1-7):%6.2f ns (+%5.1f%%)\n",
           t_recomputed_all / ITERS, (t_recomputed_all - t_unmon) / t_unmon * 100.0);

    return 0;
}
