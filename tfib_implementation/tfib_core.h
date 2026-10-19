#ifndef TFIB_CORE_H
#define TFIB_CORE_H

#include "tfib_common.h"
#include "tfib_ref.h"
#include "tfib_meta.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    TFIB_MODE_BASELINE = 0,  /* Original unenhanced monitor (Theorem 1 blind spot present) */
    TFIB_MODE_REF = 1,       /* Strategy 1: Dual-Reference Table */
    TFIB_MODE_META = 2       /* Strategy 2: Precomputed Integrity Metadata */
} tfib_mode_t;

extern tfib_mode_t g_tfib_mode;

void tfib_set_mode(tfib_mode_t mode);
tfib_mode_t tfib_get_mode(void);
void tfib_reset_all_stats(void);

/* Query aggregate metrics */
uint32_t tfib_get_total_mismatches(void);
uint32_t tfib_get_total_recoveries(void);
uint32_t tfib_get_total_persistent_fails(void);
uint32_t tfib_get_twiddle_faults_detected(void);

#ifdef __cplusplus
}
#endif

#endif /* TFIB_CORE_H */
