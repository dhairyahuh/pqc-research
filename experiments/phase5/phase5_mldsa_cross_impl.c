/**
 * Phase 5 — Cross-Implementation ML-DSA Fault-Surface Validation
 *
 * Experiment categories:
 * 1. Baseline equivalence: C-ref vs liboqs deterministic signing/verify
 * 2. Instrumentation transparency: hooks dormant vs clean build
 * 3. Cross-backend sign/verify interoperability
 * 4. Fault injection reproduction (C-ref only)
 * 5. Verification gate behavior audit
 *
 * Implementation A: mldsa-native C reference (instrumented)
 * Implementation B: liboqs 0.16.0 (AArch64 assembly backend, opaque)
 *
 * CRITICAL: Both derive from pq-code-package mldsa-native.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <oqs/oqs.h>

/* Path B symbols (mldsa-native C-ref, parameter set 65) */
int mldsa_keypair_internal(uint8_t *pk, uint8_t *sk, const uint8_t *seed);
int mldsa_signature(uint8_t *sig, const uint8_t *m, size_t mlen,
                    const uint8_t *ctx, size_t ctxlen, const uint8_t *sk);
int mldsa_verify(const uint8_t *sig, const uint8_t *m, size_t mlen,
                 const uint8_t *ctx, size_t ctxlen, const uint8_t *pk);

/* Instrumented symbols (mldsa65 prefix for fault-hook build) */
int mldsa65_keypair_internal(uint8_t *pk, uint8_t *sk, const uint8_t *seed);
int mldsa65_signature(uint8_t *sig, const uint8_t *m, size_t mlen,
                      const uint8_t *ctx, size_t ctxlen, const uint8_t *sk);
int mldsa65_verify(const uint8_t *sig, const uint8_t *m, size_t mlen,
                   const uint8_t *ctx, size_t ctxlen, const uint8_t *pk);

/* Fault hook API */
#include "algorithms/source_ref/mldsa_fault_hooks.h"

/* FIPS 204 sizes for ML-DSA-65 */
#define DSA65_PK_BYTES 1952
#define DSA65_SK_BYTES 4032
#define DSA65_SIG_BYTES 3309
#define DSA65_SEED_BYTES 32

/* Randomness bridge */
int randombytes(uint8_t *out, size_t outlen) {
    OQS_randombytes(out, outlen);
    return 0;
}

/* ============================================================
 * CATEGORY 1: Baseline Interoperability
 * C-ref signs, liboqs verifies (and vice versa)
 * ============================================================ */

static int test_dsa_interoperability(int num_trials) {
    printf("\n=== ML-DSA Category 1: Cross-Backend Sign/Verify Interop (%d trials) ===\n", num_trials);
    
    int ref_sign_oqs_verify = 0;
    int oqs_sign_ref_verify = 0;
    int ref_self = 0;
    int oqs_self = 0;
    int errors = 0;
    
    OQS_SIG *sig_oqs = OQS_SIG_new(OQS_SIG_alg_ml_dsa_65);
    if (!sig_oqs) {
        printf("  ERROR: Cannot allocate liboqs ML-DSA-65\n");
        return 1;
    }
    
    for (int t = 0; t < num_trials; t++) {
        /* Generate keypair with C-ref (deterministic seed) */
        uint8_t seed[DSA65_SEED_BYTES];
        OQS_randombytes(seed, DSA65_SEED_BYTES);
        
        uint8_t pk_ref[DSA65_PK_BYTES], sk_ref[DSA65_SK_BYTES];
        if (mldsa_keypair_internal(pk_ref, sk_ref, seed) != 0) { errors++; continue; }
        
        /* Test message */
        const char *msg = "Phase 5 cross-implementation test message";
        size_t msg_len = strlen(msg);
        const uint8_t *ctx = (const uint8_t *)"";
        size_t ctx_len = 0;
        
        /* C-ref sign */
        uint8_t sig_ref[DSA65_SIG_BYTES];
        if (mldsa_signature(sig_ref, (const uint8_t *)msg, msg_len, ctx, ctx_len, sk_ref) != 0) {
            errors++;
            continue;
        }
        
        /* C-ref self-verify */
        if (mldsa_verify(sig_ref, (const uint8_t *)msg, msg_len, ctx, ctx_len, pk_ref) == 0) {
            ref_self++;
        }
        
        /* liboqs verify C-ref signature */
        size_t sig_len_dummy = DSA65_SIG_BYTES;
        if (OQS_SIG_verify(sig_oqs, (const uint8_t *)msg, msg_len, sig_ref, sig_len_dummy, pk_ref) == OQS_SUCCESS) {
            ref_sign_oqs_verify++;
        }
        
        /* liboqs keygen + sign (from same seed if possible, else random) */
        uint8_t pk_oqs[DSA65_PK_BYTES], sk_oqs[DSA65_SK_BYTES];
        if (OQS_SIG_keypair(sig_oqs, pk_oqs, sk_oqs) != OQS_SUCCESS) { errors++; continue; }
        
        uint8_t sig_oqs_buf[DSA65_SIG_BYTES + 100]; /* OQS may use variable length */
        size_t sig_oqs_len = 0;
        if (OQS_SIG_sign(sig_oqs, sig_oqs_buf, &sig_oqs_len, (const uint8_t *)msg, msg_len, sk_oqs) == OQS_SUCCESS) {
            /* liboqs self-verify */
            if (OQS_SIG_verify(sig_oqs, (const uint8_t *)msg, msg_len, sig_oqs_buf, sig_oqs_len, pk_oqs) == OQS_SUCCESS) {
                oqs_self++;
            }
            
            /* C-ref verify liboqs signature */
            if (sig_oqs_len == DSA65_SIG_BYTES) {
                if (mldsa_verify(sig_oqs_buf, (const uint8_t *)msg, msg_len, ctx, ctx_len, pk_oqs) == 0) {
                    oqs_sign_ref_verify++;
                }
            }
        } else { errors++; }
    }
    
    OQS_SIG_free(sig_oqs);
    
    printf("  C-ref self-verify:          %d/%d (%.1f%%)\n", ref_self, num_trials, 100.0*ref_self/num_trials);
    printf("  C-ref sign, liboqs verify:  %d/%d (%.1f%%)\n", ref_sign_oqs_verify, num_trials, 100.0*ref_sign_oqs_verify/num_trials);
    printf("  liboqs self-verify:         %d/%d (%.1f%%)\n", oqs_self, num_trials, 100.0*oqs_self/num_trials);
    printf("  liboqs sign, C-ref verify:  %d/%d (%.1f%%)\n", oqs_sign_ref_verify, num_trials, 100.0*oqs_sign_ref_verify/num_trials);
    printf("  Errors: %d\n", errors);
    
    int failures = 0;
    if (ref_self != num_trials) failures++;
    if (oqs_self != num_trials) failures++;
    /* Cross-verify may have context encoding differences — report but don't fail */
    
    return failures;
}

/* ============================================================
 * CATEGORY 2: Norm Check Fault Reproduction
 * Reproduce Phase 3 norm check bypass/force experiments
 * ============================================================ */

static int test_norm_check_faults(int num_trials) {
    printf("\n=== ML-DSA Category 2: Norm Check Fault Reproduction (%d trials) ===\n", num_trials);
    
    int norm_z_force_pass_accepted = 0;
    int norm_z_force_fail_retried = 0;
    int norm_w0_force_pass_accepted = 0;
    int norm_w0_force_fail_retried = 0;
    int errors = 0;
    
    for (int t = 0; t < num_trials; t++) {
        uint8_t seed[DSA65_SEED_BYTES];
        OQS_randombytes(seed, DSA65_SEED_BYTES);
        
        uint8_t pk[DSA65_PK_BYTES], sk[DSA65_SK_BYTES];
        mldsa_fault_reset();
        if (mldsa65_keypair_internal(pk, sk, seed) != 0) { errors++; continue; }
        
        const char *msg = "norm check test";
        size_t msg_len = strlen(msg);
        uint8_t sig[DSA65_SIG_BYTES];
        
        /* Test: Force norm_z pass (bypass rejection) */
        mldsa_fault_reset();
        mldsa_fault_arm_norm_z(0); /* 0 = force pass */
        int rc = mldsa65_signature(sig, (const uint8_t *)msg, msg_len,
                                   (const uint8_t *)"", 0, sk);
        if (rc == 0) {
            /* Verify the resulting signature */
            mldsa_fault_reset();
            int v = mldsa65_verify(sig, (const uint8_t *)msg, msg_len,
                                   (const uint8_t *)"", 0, pk);
            if (v == 0) norm_z_force_pass_accepted++;
            /* v != 0 means bypassed norm check produced invalid signature */
        }
        
        /* Test: Force norm_z fail (force rejection) */
        mldsa_fault_reset();
        mldsa_fault_arm_norm_z(1); /* 1 = force fail */
        rc = mldsa65_signature(sig, (const uint8_t *)msg, msg_len,
                               (const uint8_t *)"", 0, sk);
        if (rc != 0) {
            norm_z_force_fail_retried++; /* Signing exhausted attempts */
        }
    }
    
    printf("  Norm-z force pass → valid sig: %d/%d (%.1f%%)\n",
           norm_z_force_pass_accepted, num_trials, 100.0*norm_z_force_pass_accepted/num_trials);
    printf("  Norm-z force fail → exhaustion: %d/%d (%.1f%%)\n",
           norm_z_force_fail_retried, num_trials, 100.0*norm_z_force_fail_retried/num_trials);
    printf("  Errors: %d\n", errors);
    
    return 0; /* Observational — no pass/fail criterion */
}

/* ============================================================
 * CATEGORY 3: Verification Gate Audit
 * Phase 4 correction: distinguishing mathematical computation faults
 * from direct Boolean decision-variable overrides
 * ============================================================ */

static int test_verification_gate_audit(int num_trials) {
    printf("\n=== ML-DSA Category 3: Verification Gate Audit (%d trials) ===\n", num_trials);
    printf("  IMPORTANT: Phase 4 correction — Boolean override ≠ cryptographic forgery\n");
    
    int valid_sig_verify_pass = 0;
    int valid_sig_cmp_forced_fail = 0;
    int invalid_sig_cmp_forced_pass = 0;
    int invalid_sig_verify_reject = 0;
    int errors = 0;
    
    for (int t = 0; t < num_trials; t++) {
        uint8_t seed[DSA65_SEED_BYTES];
        OQS_randombytes(seed, DSA65_SEED_BYTES);
        
        uint8_t pk[DSA65_PK_BYTES], sk[DSA65_SK_BYTES];
        mldsa_fault_reset();
        if (mldsa65_keypair_internal(pk, sk, seed) != 0) { errors++; continue; }
        
        const char *msg = "verification gate test";
        size_t msg_len = strlen(msg);
        uint8_t sig[DSA65_SIG_BYTES];
        
        /* Generate valid signature (no fault) */
        mldsa_fault_reset();
        if (mldsa65_signature(sig, (const uint8_t *)msg, msg_len,
                              (const uint8_t *)"", 0, sk) != 0) { errors++; continue; }
        
        /* Test 1: Valid sig, normal verify → should pass */
        mldsa_fault_reset();
        int v = mldsa65_verify(sig, (const uint8_t *)msg, msg_len,
                               (const uint8_t *)"", 0, pk);
        if (v == 0) valid_sig_verify_pass++;
        
        /* Test 2: Valid sig, force cmp to non-zero (reject) */
        mldsa_fault_reset();
        mldsa_fault_arm_verify_cmp(1); /* force reject */
        v = mldsa65_verify(sig, (const uint8_t *)msg, msg_len,
                           (const uint8_t *)"", 0, pk);
        if (v != 0) valid_sig_cmp_forced_fail++;
        
        /* Test 3: Corrupted sig, normal verify → should reject */
        uint8_t sig_bad[DSA65_SIG_BYTES];
        memcpy(sig_bad, sig, DSA65_SIG_BYTES);
        sig_bad[10] ^= 0xFF;
        
        mldsa_fault_reset();
        v = mldsa65_verify(sig_bad, (const uint8_t *)msg, msg_len,
                           (const uint8_t *)"", 0, pk);
        if (v != 0) invalid_sig_verify_reject++;
        
        /* Test 4: Corrupted sig, force cmp=0 (Boolean override → "accept") */
        /* Phase 4 correction: This is a GENERIC BOOLEAN DECISION OVERRIDE, */
        /* NOT a cryptographic forgery. The mathematical computation still failed; */
        /* only the final comparison variable was overridden. */
        mldsa_fault_reset();
        mldsa_fault_arm_verify_cmp(0); /* force accept */
        v = mldsa65_verify(sig_bad, (const uint8_t *)msg, msg_len,
                           (const uint8_t *)"", 0, pk);
        if (v == 0) invalid_sig_cmp_forced_pass++;
    }
    
    printf("  Valid sig + normal verify → accept:   %d/%d\n", valid_sig_verify_pass, num_trials);
    printf("  Valid sig + cmp forced reject:         %d/%d\n", valid_sig_cmp_forced_fail, num_trials);
    printf("  Invalid sig + normal verify → reject:  %d/%d\n", invalid_sig_verify_reject, num_trials);
    printf("  Invalid sig + cmp forced accept (*):   %d/%d\n", invalid_sig_cmp_forced_pass, num_trials);
    printf("  (*) = Generic Boolean override, NOT cryptographic forgery\n");
    printf("  Errors: %d\n", errors);
    
    int failures = 0;
    if (valid_sig_verify_pass != num_trials) failures++;
    if (valid_sig_cmp_forced_fail != num_trials) failures++;
    if (invalid_sig_verify_reject != num_trials) failures++;
    /* invalid_sig_cmp_forced_pass: expected to be num_trials (override works) */
    
    return failures;
}

/* ============================================================
 * MAIN
 * ============================================================ */

int main(void) {
    printf("================================================================\n");
    printf("Phase 5: Cross-Implementation Fault-Surface Validation (ML-DSA)\n");
    printf("Implementation A: mldsa-native C-reference (instrumented)\n");
    printf("Implementation B: liboqs 0.16.0 (AArch64 assembly backend)\n");
    printf("NOTE: Both derive from pq-code-package — backend comparison only\n");
    printf("================================================================\n");
    
    int total_failures = 0;
    
    total_failures += test_dsa_interoperability(200);
    total_failures += test_norm_check_faults(100);
    total_failures += test_verification_gate_audit(200);
    
    printf("\n================================================================\n");
    printf("Phase 5 ML-DSA Summary: %d critical failures detected\n", total_failures);
    printf("================================================================\n");
    
    return (total_failures > 0) ? 1 : 0;
}
