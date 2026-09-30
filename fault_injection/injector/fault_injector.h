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

// Cryptographic Layer Outcome Classifications
typedef enum {
    CRYPTO_OUTCOME_CORRECT_VALID = 0,       // Legitimate output matches ground truth
    CRYPTO_OUTCOME_IMPLICIT_REJECTION = 1,  // Cryptographically expected FO transform rejection
    CRYPTO_OUTCOME_SIGNATURE_REJECTION = 2, // Cryptographically expected signature rejection
    CRYPTO_OUTCOME_EXPLICIT_ERROR = 3,      // Checked library error (e.g. check_sk/check_pk)
    CRYPTO_OUTCOME_UNEXPECTED_OUTPUT = 4,   // Undetected invalid output violating guarantees
    CRYPTO_OUTCOME_CRASH = 5,               // Segmentation fault, bus error, abort
    CRYPTO_OUTCOME_TIMEOUT = 6              // Infinite loop or watchdog expiration
} crypto_outcome_class_t;

// Protocol Layer Outcome Classifications
typedef enum {
    PROTOCOL_OUTCOME_KEY_MATCH = 0,
    PROTOCOL_OUTCOME_KEY_MISMATCH_DETECTED = 1,
    PROTOCOL_OUTCOME_KEY_MISMATCH_UNDETECTED = 2,
    PROTOCOL_OUTCOME_SESSION_ABORTED = 3,
    PROTOCOL_OUTCOME_SESSION_RECOVERED = 4,
    PROTOCOL_OUTCOME_TIMEOUT = 5
} protocol_outcome_class_t;

// Fault Specification
typedef struct {
    uint64_t experiment_id;
    const char *algorithm;
    const char *parameter_set;
    fault_class_t fault_class;
    const char *fault_type_str;
    const char *target_name;
    size_t target_index;      // Byte or coefficient index
    uint8_t bit_index;        // Bit position within byte/element
    const char *injection_stage;
    uint64_t seed;
    uint32_t duration;
    uint32_t magnitude;
} fault_descriptor_t;

// Execution Result Record
typedef struct {
    crypto_outcome_class_t outcome_class;
    bool fault_detected;
    double runtime_us;
    size_t memory_bytes;
    int32_t error_code;
} crypto_fault_result_t;

// Core C Buffer Inversion Routines
int inject_bit_flip(uint8_t *buffer, size_t buf_len, size_t byte_offset, uint8_t bit_pos);
int inject_byte_corruption(uint8_t *buffer, size_t buf_len, size_t byte_offset, uint8_t xor_mask);
int inject_burst_corruption(uint8_t *buffer, size_t buf_len, size_t start_offset, size_t length, uint64_t seed);
int inject_polynomial_coefficient_glitch(int16_t *coeffs, size_t num_coeffs, size_t coeff_idx, int16_t delta);

const char *crypto_outcome_to_string(crypto_outcome_class_t outcome);
const char *protocol_outcome_to_string(protocol_outcome_class_t outcome);
const char *fault_class_to_string(fault_class_t fclass);

#ifdef __cplusplus
}
#endif

#endif // FAULT_INJECTOR_H
