/**
 * ML-KEM Source-Level Research Fault Injection Hooks
 * Provides clean, non-intrusive mathematical instrumentation hooks for:
 * 1. NTT output & butterfly stage coefficients
 * 2. CBD error sampling coefficients
 * 3. Dyadic polynomial multiplication accumulators
 * 4. Compression/Decompression boundary coefficients
 * 5. Decapsulation re-encryption comparison flag (FO transform)
 */

#ifndef MLKEM_FAULT_HOOKS_H
#define MLKEM_FAULT_HOOKS_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    HOOK_TARGET_NONE = 0,
    HOOK_TARGET_NTT_COEFF = 1,
    HOOK_TARGET_CBD_SAMPLE = 2,
    HOOK_TARGET_POLY_MUL = 3,
    HOOK_TARGET_DECOMPRESS = 4,
    HOOK_TARGET_DECAPS_VERIFY_FLAG = 5
} mlkem_hook_target_t;

typedef struct {
    bool enabled;
    mlkem_hook_target_t target;
    size_t target_coeff_idx;   // 0 .. 255
    uint8_t bit_to_flip;       // 0 .. 15
    int16_t additive_glitch;   // delta
    uint64_t trigger_count;
    
    // Trace recording buffer
    bool trace_recorded;
    int16_t orig_value;
    int16_t faulted_value;
    char fault_description[256];
} mlkem_fault_config_t;

extern mlkem_fault_config_t g_mlkem_fault;

void mlkem_fault_reset(void);
void mlkem_fault_arm(mlkem_hook_target_t target, size_t coeff_idx, uint8_t bit, int16_t delta);

// Instrumentation Hook APIs
void hook_ntt_coefficient(int16_t *coeffs, size_t count);
void hook_sampling_coefficient(int16_t *coeffs, size_t count);
void hook_polymul_accumulator(int16_t *coeffs, size_t count);
void hook_decompress_coefficient(int16_t *coeffs, size_t count);
void hook_decaps_verify_flag(int *fail_flag);

#ifdef __cplusplus
}
#endif

#endif // MLKEM_FAULT_HOOKS_H
