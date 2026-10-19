#include "tfib_common.h"
#include <string.h>

tfib_fault_context_t g_tfib_fault;

void tfib_fault_reset(void) {
    memset(&g_tfib_fault, 0, sizeof(g_tfib_fault));
}

void tfib_fault_arm(tfib_fault_locus_t locus, unsigned layer, unsigned b_idx, uint8_t bit, bool persistent) {
    g_tfib_fault.enabled = true;
    g_tfib_fault.locus = locus;
    g_tfib_fault.target_layer = layer;
    g_tfib_fault.target_butterfly = b_idx;
    g_tfib_fault.bit_to_flip = bit;
    g_tfib_fault.persistent = persistent;
    g_tfib_fault.trigger_count = 0;
    g_tfib_fault.orig_val = 0;
    g_tfib_fault.faulted_val = 0;
}
