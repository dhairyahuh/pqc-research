#ifndef TFIB_META_H
#define TFIB_META_H

#include "tfib_common.h"

#ifdef __cplusplus
extern "C" {
#endif

extern const uint16_t tfib_zetas_tag[TFIB_ZETA_COUNT];
extern tfib_stats_t g_tfib_meta_stats;

static inline uint16_t tfib_meta_compute_tag(int16_t zeta, unsigned k) {
    uint32_t val = (uint32_t)(uint16_t)zeta;
    uint32_t idx = (uint32_t)k;
    return (uint16_t)(((val * 31337u) ^ (idx * 1337u) ^ 0xA55Au) & 0xFFFFu);
}

void tfib_meta_init(void);
void tfib_meta_reset_stats(void);

/* Strategy 2: Metadata-Guarded Invariant Monitor for Forward Cooley-Tukey Butterfly */
void tfib_meta_monitor_ntt_butterfly(
    unsigned layer, unsigned b_idx, int16_t zeta_op,
    int16_t u_saved, int16_t v_saved, int16_t t_used,
    int16_t *r_j, int16_t *r_j_len
);

/* Strategy 2: Metadata-Guarded Invariant Monitor for Inverse Gentleman-Sande Butterfly */
void tfib_meta_monitor_invntt_butterfly(
    unsigned layer, unsigned b_idx, int16_t zeta_op,
    int16_t u_saved, int16_t v_saved,
    int16_t *r_j, int16_t *r_j_len
);

#ifdef __cplusplus
}
#endif

#endif /* TFIB_META_H */
