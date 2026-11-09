/**
 * ASTRA-Sec: Monitored ML-KEM-768 Fault-Resilient C Integration API
 * 
 * Exposes NIST FIPS 203 ML-KEM-768 with:
 * - Dual-transform Cooley-Tukey NTT Invariant Monitoring
 * - Gentleman-Sande Inverse NTT Invariant Monitoring
 * - In-place Localized Register Rollback (K <= 2)
 * - TFIB-Ref Twiddle Factor Integrity Binding
 * - Deterministic Fail-Stop Implicit Rejection Containment
 */

#ifndef ASTRA_MLKEM_MONITORED_H
#define ASTRA_MLKEM_MONITORED_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define ASTRA_MLKEM_API_VERSION 0x010000 /* v1.0.0 */

#define ASTRA_KEM768_PK_BYTES 1184
#define ASTRA_KEM768_SK_BYTES 2400
#define ASTRA_KEM768_CT_BYTES 1088
#define ASTRA_KEM768_SS_BYTES 32

#define ASTRA_DSA65_PK_BYTES  1952
#define ASTRA_DSA65_SK_BYTES  4032
#define ASTRA_DSA65_SIG_BYTES 3309

/**
 * Structured Fault Resilience Status Codes
 */
typedef enum {
    ASTRA_FAULT_STATUS_SUCCESS = 0,         /* Clean execution, zero invariant violations */
    ASTRA_FAULT_STATUS_RECOVERED = 1,       /* Transient fault caught and recovered via rollback */
    ASTRA_FAULT_STATUS_PERSISTENT = 2,      /* Persistent fault detected, retries exhausted, fail-stop engaged */
    ASTRA_FAULT_STATUS_UNRECOVERABLE = 3,   /* Unrecoverable error / twiddle reference failure */
    ASTRA_FAULT_STATUS_INVALID_INPUT = 4,   /* NULL pointer or invalid buffer length */
    ASTRA_FAULT_STATUS_CHECKER_FAILURE = 5  /* Checker inconsistency detected */
} astra_fault_status_t;

/**
 * Comprehensive Decapsulation Telemetry Structure
 */
typedef struct {
    astra_fault_status_t status;            /* Categorized fault status */
    uint32_t raw_internal_code;             /* Low-level FIPS 203 status (0x5A5A5A5A, 0xFFFFFFFF, etc.) */
    uint32_t butterflies_executed;          /* Total butterflies monitored */
    uint32_t mismatch_count;                /* Invariant violations detected */
    uint32_t retry_count;                   /* Rollback attempts performed */
    uint32_t recovered_count;               /* Successful transient recoveries */
    uint32_t persistent_count;              /* Unrecoverable persistent faults */
    uint32_t twiddle_faults_detected;       /* Twiddle table mismatches caught via TFIB-Ref */
    int last_failed_layer;                  /* Layer index of last fault (-1 if none) */
    int last_failed_butterfly;              /* Butterfly index of last fault (-1 if none) */
    bool fail_stop_engaged;                 /* True if implicit rejection key substitution occurred */
} astra_mlkem_telemetry_t;

/* API Version Query */
uint32_t astra_mlkem_get_version(void);

/* Key Generation and Encapsulation */
int astra_mlkem_keypair(uint8_t *pk, uint8_t *sk);
int astra_mlkem_encaps(uint8_t *ct, uint8_t *ss, const uint8_t *pk);

/* Monitored Decapsulation with Full Telemetry */
int astra_mlkem_decaps_monitored(
    uint8_t *ss,
    const uint8_t *ct,
    const uint8_t *sk,
    astra_mlkem_telemetry_t *telemetry
);

/* Research Fault Injection Hooks (For Testing & Validation) */
int astra_mlkem_inject_op_twiddle_fault(unsigned layer, unsigned butterfly, uint8_t bit, bool persistent);
int astra_mlkem_inject_ref_twiddle_fault(unsigned layer, unsigned butterfly, uint8_t bit, bool persistent);
int astra_mlkem_inject_checker_logic_fault(unsigned layer, unsigned butterfly, bool persistent);
int astra_mlkem_reset_faults(void);

/* Digital Signatures (ML-DSA-65) */
int astra_dsa65_keypair(uint8_t *pk, uint8_t *sk);
int astra_dsa65_sign(uint8_t *sig, size_t *sig_len, const uint8_t *msg, size_t msg_len, const uint8_t *sk);
int astra_dsa65_verify(const uint8_t *sig, size_t sig_len, const uint8_t *msg, size_t msg_len, const uint8_t *pk);

#ifdef __cplusplus
}
#endif

#endif /* ASTRA_MLKEM_MONITORED_H */
