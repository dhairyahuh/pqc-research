/**
 * ML-KEM Source-Level Research Fault Injection Hooks Implementation
 */

#include "mlkem_fault_hooks.h"
#include <stdio.h>
#include <string.h>

mlkem_fault_config_t g_mlkem_fault = {
    .enabled = false,
    .target = HOOK_TARGET_NONE,
    .target_coeff_idx = 0,
    .bit_to_flip = 0,
    .additive_glitch = 0,
    .trigger_count = 0,
    .trace_recorded = false,
    .orig_value = 0,
    .faulted_value = 0,
    .fault_description = ""
};

void mlkem_fault_reset(void) {
    g_mlkem_fault.enabled = false;
    g_mlkem_fault.target = HOOK_TARGET_NONE;
    g_mlkem_fault.trigger_count = 0;
    g_mlkem_fault.trace_recorded = false;
    g_mlkem_fault.fault_description[0] = '\0';
}

void mlkem_fault_arm(mlkem_hook_target_t target, size_t coeff_idx, uint8_t bit, int16_t delta) {
    g_mlkem_fault.enabled = true;
    g_mlkem_fault.target = target;
    g_mlkem_fault.target_coeff_idx = coeff_idx % 256;
    g_mlkem_fault.bit_to_flip = bit % 16;
    g_mlkem_fault.additive_glitch = delta;
    g_mlkem_fault.trigger_count = 0;
    g_mlkem_fault.trace_recorded = false;
}

static void apply_hook_on_coeffs(int16_t *coeffs, size_t count, mlkem_hook_target_t expected_target, const char *name) {
    if (!g_mlkem_fault.enabled || g_mlkem_fault.target != expected_target) {
        return;
    }
    
    // Trigger on first occurrence
    if (g_mlkem_fault.trigger_count == 0 && coeffs && g_mlkem_fault.target_coeff_idx < count) {
        size_t idx = g_mlkem_fault.target_coeff_idx;
        g_mlkem_fault.orig_value = coeffs[idx];
        
        if (g_mlkem_fault.additive_glitch != 0) {
            coeffs[idx] = (int16_t)(coeffs[idx] + g_mlkem_fault.additive_glitch);
        } else {
            coeffs[idx] ^= (int16_t)(1u << g_mlkem_fault.bit_to_flip);
        }
        
        g_mlkem_fault.faulted_value = coeffs[idx];
        g_mlkem_fault.trace_recorded = true;
        snprintf(g_mlkem_fault.fault_description, sizeof(g_mlkem_fault.fault_description),
                 "Hook [%s]: coeff[%zu] altered %d -> %d",
                 name, idx, (int)g_mlkem_fault.orig_value, (int)g_mlkem_fault.faulted_value);
    }
    g_mlkem_fault.trigger_count++;
}

void hook_ntt_coefficient(int16_t *coeffs, size_t count) {
    apply_hook_on_coeffs(coeffs, count, HOOK_TARGET_NTT_COEFF, "NTT_COEFF");
}

void hook_sampling_coefficient(int16_t *coeffs, size_t count) {
    apply_hook_on_coeffs(coeffs, count, HOOK_TARGET_CBD_SAMPLE, "CBD_SAMPLE");
}

void hook_polymul_accumulator(int16_t *coeffs, size_t count) {
    apply_hook_on_coeffs(coeffs, count, HOOK_TARGET_POLY_MUL, "POLY_MUL");
}

void hook_decompress_coefficient(int16_t *coeffs, size_t count) {
    apply_hook_on_coeffs(coeffs, count, HOOK_TARGET_DECOMPRESS, "DECOMPRESS");
}

void hook_decaps_verify_flag(int *fail_flag) {
    if (!g_mlkem_fault.enabled || g_mlkem_fault.target != HOOK_TARGET_DECAPS_VERIFY_FLAG || !fail_flag) {
        return;
    }
    g_mlkem_fault.orig_value = (int16_t)(*fail_flag);
    *fail_flag = (*fail_flag == 0) ? 1 : 0; // Invert equality predicate!
    g_mlkem_fault.faulted_value = (int16_t)(*fail_flag);
    g_mlkem_fault.trace_recorded = true;
    g_mlkem_fault.trigger_count++;
    snprintf(g_mlkem_fault.fault_description, sizeof(g_mlkem_fault.fault_description),
             "Hook [DECAPS_VERIFY_FLAG]: fail flag inverted %d -> %d",
             (int)g_mlkem_fault.orig_value, (int)g_mlkem_fault.faulted_value);
}
