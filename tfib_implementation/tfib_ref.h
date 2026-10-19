#ifndef TFIB_REF_H
#define TFIB_REF_H

#include "tfib_common.h"

#ifdef __cplusplus
extern "C" {
#endif

extern const int16_t tfib_zetas_ref[TFIB_ZETA_COUNT];
extern tfib_stats_t g_tfib_ref_stats;

void tfib_ref_init(void);
void tfib_ref_reset_stats(void);

/* Strategy 1: Dual-Reference Invariant Monitor for Forward Cooley-Tukey Butterfly */
void tfib_ref_monitor_ntt_butterfly(
    unsigned layer, unsigned b_idx, int16_t zeta_op,
    int16_t u_saved, int16_t v_saved, int16_t t_used,
    int16_t *r_j, int16_t *r_j_len
);

/* Strategy 1: Dual-Reference Invariant Monitor for Inverse Gentleman-Sande Butterfly */
void tfib_ref_monitor_invntt_butterfly(
    unsigned layer, unsigned b_idx, int16_t zeta_op,
    int16_t u_saved, int16_t v_saved,
    int16_t *r_j, int16_t *r_j_len
);

#ifdef __cplusplus
}
#endif

#endif /* TFIB_REF_H */
