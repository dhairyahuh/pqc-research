/**
 * Fault Injector Core Engine (C Implementation)
 * Provides deterministic, bounds-checked memory and arithmetic corruptions.
 */

#include "fault_injector.h"
#include <string.h>

int inject_bit_flip(uint8_t *buffer, size_t buf_len, size_t byte_offset, uint8_t bit_pos) {
    if (!buffer || byte_offset >= buf_len || bit_pos > 7) {
        return -1;
    }
    buffer[byte_offset] ^= (uint8_t)(1u << bit_pos);
    return 0;
}

int inject_byte_corruption(uint8_t *buffer, size_t buf_len, size_t byte_offset, uint8_t xor_mask) {
    if (!buffer || byte_offset >= buf_len) {
        return -1;
    }
    if (xor_mask == 0) {
        xor_mask = 0xFF;
    }
    buffer[byte_offset] ^= xor_mask;
    return 0;
}

int inject_burst_corruption(uint8_t *buffer, size_t buf_len, size_t start_offset, size_t length, uint64_t seed) {
    if (!buffer || start_offset >= buf_len) {
        return -1;
    }
    size_t end = start_offset + length;
    if (end > buf_len) {
        end = buf_len;
    }
    
    uint64_t state = seed ? seed : 0xDEADBEEFCAFEBABEULL;
    for (size_t i = start_offset; i < end; i++) {
        state = state * 6364136223846793005ULL + 1442695040888963407ULL;
        uint8_t mask = (uint8_t)(state >> 33);
        if (mask == 0) mask = 0xAA;
        buffer[i] ^= mask;
    }
    return 0;
}

int inject_polynomial_coefficient_glitch(int16_t *coeffs, size_t num_coeffs, size_t coeff_idx, int16_t delta) {
    if (!coeffs || coeff_idx >= num_coeffs) {
        return -1;
    }
    coeffs[coeff_idx] = (int16_t)(coeffs[coeff_idx] + delta);
    return 0;
}

const char *crypto_outcome_to_string(crypto_outcome_class_t outcome) {
    switch (outcome) {
        case CRYPTO_OUTCOME_CORRECT_VALID: return "CORRECT_VALID_DECAPSULATION";
        case CRYPTO_OUTCOME_IMPLICIT_REJECTION: return "EXPECTED_IMPLICIT_REJECTION";
        case CRYPTO_OUTCOME_SIGNATURE_REJECTION: return "EXPECTED_SIGNATURE_REJECTION";
        case CRYPTO_OUTCOME_EXPLICIT_ERROR: return "EXPLICIT_ERROR";
        case CRYPTO_OUTCOME_UNEXPECTED_OUTPUT: return "UNEXPECTED_INCORRECT_OUTPUT";
        case CRYPTO_OUTCOME_CRASH: return "CRASH";
        case CRYPTO_OUTCOME_TIMEOUT: return "TIMEOUT";
        default: return "UNKNOWN";
    }
}

const char *protocol_outcome_to_string(protocol_outcome_class_t outcome) {
    switch (outcome) {
        case PROTOCOL_OUTCOME_KEY_MATCH: return "KEY_MATCH";
        case PROTOCOL_OUTCOME_KEY_MISMATCH_DETECTED: return "KEY_MISMATCH_DETECTED";
        case PROTOCOL_OUTCOME_KEY_MISMATCH_UNDETECTED: return "KEY_MISMATCH_UNDETECTED";
        case PROTOCOL_OUTCOME_SESSION_ABORTED: return "SESSION_ABORTED";
        case PROTOCOL_OUTCOME_SESSION_RECOVERED: return "SESSION_RECOVERED";
        case PROTOCOL_OUTCOME_TIMEOUT: return "TIMEOUT";
        default: return "UNKNOWN";
    }
}

const char *fault_class_to_string(fault_class_t fclass) {
    switch (fclass) {
        case FAULT_CLASS_SEU: return "SEU";
        case FAULT_CLASS_MULTI_BIT: return "MULTI_BIT";
        case FAULT_CLASS_BURST: return "BURST";
        case FAULT_CLASS_TRANSIENT: return "TRANSIENT";
        case FAULT_CLASS_PERSISTENT: return "PERSISTENT";
        default: return "UNKNOWN";
    }
}
