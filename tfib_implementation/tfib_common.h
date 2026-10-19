#ifndef TFIB_COMMON_H
#define TFIB_COMMON_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define MLKEM_Q 3329
#define MLKEM_N 256
#define TFIB_ZETA_COUNT 128

/* Twiddle table indexing helpers */
static inline unsigned tfib_twiddle_idx_ntt(unsigned layer, unsigned b_idx) {
    return (1u << (layer - 1)) + (b_idx >> (8 - layer));
}

static inline unsigned tfib_twiddle_idx_invntt(unsigned layer, unsigned b_idx) {
    return ((1u << layer) - 1) - (b_idx >> (8 - layer));
}

/* Barrett modular reduction & Montgomery multiplication helpers for monitor */
static inline int16_t tfib_barrett_reduce(int16_t a) {
    int32_t t;
    const int32_t v = (int32_t)(((1U << 26) + (MLKEM_Q / 2)) / MLKEM_Q);
    t = (v * (int32_t)a + (1 << 25)) >> 26;
    t *= MLKEM_Q;
    return (int16_t)(a - (int16_t)t);
}

static inline int16_t tfib_fqmul(int16_t a, int16_t b) {
    int32_t t = (int32_t)a * (int32_t)b;
    int16_t u = (int16_t)(t * -3327);
    int32_t res = (t - (int32_t)u * MLKEM_Q) >> 16;
    return (int16_t)res;
}

/* Fault injection configuration */
typedef enum {
    TFIB_FAULT_NONE = 0,
    TFIB_FAULT_OP_TWIDDLE,        /* Corrupt operational zeta */
    TFIB_FAULT_REF_TWIDDLE,       /* Corrupt reference zeta */
    TFIB_FAULT_META_TAG,          /* Corrupt metadata tag */
    TFIB_FAULT_SIMULTANEOUS,      /* Corrupt operational and verification data identically */
    TFIB_FAULT_CHECKER_LOGIC      /* Corrupt checker evaluation / comparison */
} tfib_fault_locus_t;

typedef struct {
    bool enabled;
    bool persistent;
    tfib_fault_locus_t locus;
    unsigned target_layer;
    unsigned target_butterfly;
    uint8_t bit_to_flip;
    uint64_t trigger_count;
    bool op_fault_fired;
    int16_t orig_val;
    int16_t faulted_val;
} tfib_fault_context_t;

extern tfib_fault_context_t g_tfib_fault;

void tfib_fault_reset(void);
void tfib_fault_arm(tfib_fault_locus_t locus, unsigned layer, unsigned b_idx, uint8_t bit, bool persistent);

/* Execution statistics */
typedef struct {
    uint32_t executed_count;
    uint32_t mismatch_count;
    uint32_t twiddle_fault_detected;
    uint32_t arithmetic_fault_detected;
    uint32_t retry_attempt_count;
    uint32_t recovered_count;
    uint32_t persistent_fail_count;
    int last_failed_layer;
    int last_failed_butterfly;
} tfib_stats_t;

#ifdef __cplusplus
}
#endif

#endif /* TFIB_COMMON_H */
