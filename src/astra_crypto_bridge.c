/**
 * ASTRA-Sec: Cryptographic Engine Native Bridge
 *
 * Links ML-KEM-768 Native Fault-Resilient Engine (with TFIB-Ref and NTT monitoring)
 * and ML-DSA-65 into a unified shared library.
 */

#include "astra_mlkem_monitored.h"
#include "tfib_common.h"
#include "tfib_core.h"
#include "tfib_ref.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <fcntl.h>

#if defined(__APPLE__)
#include <stdlib.h>
#else
#include <sys/random.h>
#endif

/* Global reentrancy / multi-thread mutex for fault state & telemetry isolation */
static pthread_mutex_t g_crypto_mutex = PTHREAD_MUTEX_INITIALIZER;

/* Robust cross-platform CSPRNG */
int randombytes(uint8_t *out, size_t outlen) {
#if defined(__APPLE__)
    arc4random_buf(out, outlen);
    return 0;
#else
    ssize_t ret = getrandom(out, outlen, 0);
    if (ret == (ssize_t)outlen) return 0;
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd < 0) return -1;
    ssize_t read_bytes = read(fd, out, outlen);
    close(fd);
    return (read_bytes == (ssize_t)outlen) ? 0 : -1;
#endif
}

/* External symbols from mlkem768_inst.o */
int mlkem768_keypair(uint8_t *pk, uint8_t *sk);
int mlkem768_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int mlkem768_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);
int mlkem768_dec_monitored(uint8_t *ss, const uint8_t *ct, const uint8_t *sk, uint32_t *internal_status);

/* External symbols from mldsa65.o */
int mldsa_keypair(uint8_t *pk, uint8_t *sk);
int mldsa_signature(uint8_t *sig, const uint8_t *m, size_t mlen, const uint8_t *ctx, size_t ctxlen, const uint8_t *sk);
int mldsa_verify(const uint8_t *sig, const uint8_t *m, size_t mlen, const uint8_t *ctx, size_t ctxlen, const uint8_t *pk);

/* =========================================================================
 * Version and Lifecycle API
 * ========================================================================= */

uint32_t astra_mlkem_get_version(void) {
    return ASTRA_MLKEM_API_VERSION;
}

/* =========================================================================
 * ML-KEM-768 Core API
 * ========================================================================= */

int astra_mlkem_keypair(uint8_t *pk, uint8_t *sk) {
    if (!pk || !sk) return -1;
    return mlkem768_keypair(pk, sk);
}

int astra_mlkem_encaps(uint8_t *ct, uint8_t *ss, const uint8_t *pk) {
    if (!ct || !ss || !pk) return -1;
    return mlkem768_enc(ct, ss, pk);
}

int astra_mlkem_decaps_monitored(
    uint8_t *ss,
    const uint8_t *ct,
    const uint8_t *sk,
    astra_mlkem_telemetry_t *telemetry
) {
    if (!ss || !ct || !sk || !telemetry) {
        if (telemetry) {
            memset(telemetry, 0, sizeof(*telemetry));
            telemetry->status = ASTRA_FAULT_STATUS_INVALID_INPUT;
        }
        return -1;
    }

    pthread_mutex_lock(&g_crypto_mutex);

    /* Enforce TFIB-Ref mode: Strategy 1 Dual-Reference Table */
    tfib_set_mode(TFIB_MODE_REF);
    g_tfib_ref_stats.executed_count = 0;
    g_tfib_ref_stats.retry_attempt_count = 0;

    uint32_t raw_status = 0;
    int rc = mlkem768_dec_monitored(ss, ct, sk, &raw_status);
    (void)rc;

    /* Populate telemetry from execution counters */
    telemetry->raw_internal_code = raw_status;
    telemetry->butterflies_executed = g_tfib_ref_stats.executed_count;
    telemetry->mismatch_count = tfib_get_total_mismatches();
    telemetry->retry_count = g_tfib_ref_stats.retry_attempt_count;
    telemetry->recovered_count = tfib_get_total_recoveries();
    telemetry->persistent_count = tfib_get_total_persistent_fails();
    telemetry->twiddle_faults_detected = tfib_get_twiddle_faults_detected();
    telemetry->last_failed_layer = g_tfib_ref_stats.last_failed_layer;
    telemetry->last_failed_butterfly = g_tfib_ref_stats.last_failed_butterfly;
    telemetry->fail_stop_engaged = false;

    /* Classify structured status according to architectural rules */
    int return_code = 0;
    if (telemetry->persistent_count > 0 || raw_status == 0xFFFFFFFFU) {
        telemetry->status = ASTRA_FAULT_STATUS_PERSISTENT;
        telemetry->fail_stop_engaged = true;
        return_code = -2;
    } else if (telemetry->twiddle_faults_detected > 0 && telemetry->recovered_count == 0) {
        telemetry->status = ASTRA_FAULT_STATUS_UNRECOVERABLE;
        telemetry->fail_stop_engaged = true;
        return_code = -3;
    } else if (telemetry->mismatch_count > 0 && telemetry->recovered_count > 0 && telemetry->persistent_count == 0) {
        telemetry->status = ASTRA_FAULT_STATUS_RECOVERED;
        return_code = 0;
    } else if (telemetry->mismatch_count == 0 && raw_status == 0x5A5A5A5AU) {
        telemetry->status = ASTRA_FAULT_STATUS_SUCCESS;
        return_code = 0;
    } else if (raw_status == 0xA5A5A5A5U) {
        /* Standard FIPS 203 Section 7.3 implicit rejection of invalid/corrupted ciphertext */
        telemetry->status = ASTRA_FAULT_STATUS_PERSISTENT;
        telemetry->fail_stop_engaged = true;
        return_code = 0;
    } else {
        telemetry->status = ASTRA_FAULT_STATUS_CHECKER_FAILURE;
        telemetry->fail_stop_engaged = true;
        return_code = -5;
    }

    pthread_mutex_unlock(&g_crypto_mutex);
    return return_code;
}

/* =========================================================================
 * Fault Injection Testing API
 * ========================================================================= */

int astra_mlkem_inject_op_twiddle_fault(unsigned layer, unsigned butterfly, uint8_t bit, bool persistent) {
    pthread_mutex_lock(&g_crypto_mutex);
    tfib_fault_reset();
    tfib_reset_all_stats();
    tfib_fault_arm(TFIB_FAULT_OP_TWIDDLE, layer, butterfly, bit, persistent);
    pthread_mutex_unlock(&g_crypto_mutex);
    return 0;
}

int astra_mlkem_inject_ref_twiddle_fault(unsigned layer, unsigned butterfly, uint8_t bit, bool persistent) {
    pthread_mutex_lock(&g_crypto_mutex);
    tfib_fault_reset();
    tfib_reset_all_stats();
    tfib_fault_arm(TFIB_FAULT_REF_TWIDDLE, layer, butterfly, bit, persistent);
    pthread_mutex_unlock(&g_crypto_mutex);
    return 0;
}

int astra_mlkem_inject_checker_logic_fault(unsigned layer, unsigned butterfly, bool persistent) {
    pthread_mutex_lock(&g_crypto_mutex);
    tfib_fault_reset();
    tfib_reset_all_stats();
    tfib_fault_arm(TFIB_FAULT_CHECKER_LOGIC, layer, butterfly, 0, persistent);
    pthread_mutex_unlock(&g_crypto_mutex);
    return 0;
}

int astra_mlkem_reset_faults(void) {
    pthread_mutex_lock(&g_crypto_mutex);
    tfib_fault_reset();
    tfib_reset_all_stats();
    pthread_mutex_unlock(&g_crypto_mutex);
    return 0;
}

/* =========================================================================
 * ML-DSA-65 Digital Signatures API
 * ========================================================================= */

int astra_dsa65_keypair(uint8_t *pk, uint8_t *sk) {
    if (!pk || !sk) return -1;
    return mldsa_keypair(pk, sk);
}

int astra_dsa65_sign(uint8_t *sig, size_t *sig_len, const uint8_t *msg, size_t msg_len, const uint8_t *sk) {
    if (!sig || !sig_len || !msg || !sk) return -1;
    if (mldsa_signature(sig, msg, msg_len, NULL, 0, sk) == 0) {
        *sig_len = ASTRA_DSA65_SIG_BYTES;
        return 0;
    }
    return -1;
}

int astra_dsa65_verify(const uint8_t *sig, size_t sig_len, const uint8_t *msg, size_t msg_len, const uint8_t *pk) {
    if (!sig || !msg || !pk) return -1;
    if (sig_len != ASTRA_DSA65_SIG_BYTES) return -1;
    return mldsa_verify(sig, msg, msg_len, NULL, 0, pk);
}

/* =========================================================================
 * Backward Compatibility Aliases for Phase 04 / Scaffolding
 * ========================================================================= */

int astra_kem768_keypair(uint8_t *pk, uint8_t *sk) {
    return astra_mlkem_keypair(pk, sk);
}

int astra_kem768_encaps(uint8_t *ct, uint8_t *ss, const uint8_t *pk) {
    return astra_mlkem_encaps(ct, ss, pk);
}

int astra_kem768_decaps_monitored(uint8_t *ss, const uint8_t *ct, const uint8_t *sk, uint32_t *status) {
    astra_mlkem_telemetry_t telem;
    int rc = astra_mlkem_decaps_monitored(ss, ct, sk, &telem);
    if (status) {
        *status = telem.raw_internal_code;
    }
    if (telem.raw_internal_code == 0x5A5A5A5AU || telem.raw_internal_code == 0xA5A5A5A5U) {
        return 0;
    }
    return rc;
}
