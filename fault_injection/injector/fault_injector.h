/**
 * Fault Injector Core Engine (C Header)
 * Defines structured fault descriptors, targets, outcome classifications,
 * and deterministic buffer manipulation routines.
 */

#ifndef FAULT_INJECTOR_H
#define FAULT_INJECTOR_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Fault Classes
typedef enum {
    FAULT_CLASS_SEU = 0,         // Single Event Upset (Single bit flip)
    FAULT_CLASS_MULTI_BIT = 1,   // Multiple independent bit flips
    FAULT_CLASS_BURST = 2,       // Contiguous burst bit corruption
    FAULT_CLASS_TRANSIENT = 3,   // Transient value perturbation (reset after use)
    FAULT_CLASS_PERSISTENT = 4   // Stuck-at / persistent memory degradation
} fault_class_t;

// Outcome Classifications
typedef enum {
    OUTCOME_CORRECT = 0,                 // Fault had no impact; output is legitimate
    OUTCOME_EXPECTED_REJECTION = 1,      // Standard cryptographic rejection (e.g. invalid signature rejected)
    OUTCOME_DETECTED_FAILURE = 2,        // An explicit integrity/resilience check detected corruption
    OUTCOME_RECOVERED = 3,               // Detected and corrected (e.g. retry / checkpoint)
    OUTCOME_INCORRECT_OUTPUT = 4,        // Output differs from baseline without detection
    OUTCOME_SILENT_DATA_CORRUPTION = 5,  // Cryptographic state changed silently (e.g. implicit rejection desync)
    OUTCOME_CRASH = 6,                   // Segmentation fault, bus error, abort
    OUTCOME_TIMEOUT = 7                  // Infinite loop or watchdog expiration
} outcome_class_t;

// Fault Specification
typedef struct {
    uint64_t experiment_id;
    const char *algorithm;
    const char *parameter_set;
    fault_class_t fault_class;
    const char *fault_type_str;
    const char *target_name;
    size_t target_index;      // Byte or coefficient index
    uint8_t bit_index;        // Bit position within byte/element (0..7 or 0..15/31)
    const char *injection_stage;
    uint64_t seed;
    uint32_t duration;
    uint32_t magnitude;
} fault_descriptor_t;

// Execution Result Record
typedef struct {
    outcome_class_t outcome_class;
    bool fault_detected;
    bool recovered;
    double runtime_us;
    size_t memory_bytes;
    int32_t error_code;
} fault_result_t;

// Core C Buffer Inversion Routines
int inject_bit_flip(uint8_t *buffer, size_t buf_len, size_t byte_offset, uint8_t bit_pos);
int inject_byte_corruption(uint8_t *buffer, size_t buf_len, size_t byte_offset, uint8_t xor_mask);
int inject_burst_corruption(uint8_t *buffer, size_t buf_len, size_t start_offset, size_t length, uint64_t seed);
int inject_polynomial_coefficient_glitch(int16_t *coeffs, size_t num_coeffs, size_t coeff_idx, int16_t delta);

const char *outcome_class_to_string(outcome_class_t outcome);
const char *fault_class_to_string(fault_class_t fclass);

#ifdef __cplusplus
}
#endif

#endif // FAULT_INJECTOR_H
