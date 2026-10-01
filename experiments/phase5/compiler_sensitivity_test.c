/**
 * Phase 5 — Compiler and Optimization Sensitivity Analysis
 * 
 * This program is compiled at multiple optimization levels (-O0, -O1, -O2, -O3)
 * to measure whether compiler optimization changes observable fault behavior.
 * 
 * The experiment:
 * 1. Records compilation settings at runtime
 * 2. Runs deterministic keygen/encaps/decaps with known seeds
 * 3. Runs fault injection experiments with identical parameters
 * 4. Compares output checksums to detect optimization-dependent behavior
 * 
 * IMPORTANT: This same source file must be compiled separately at each
 * optimization level. The Makefile handles this.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

/* Instrumented mlkem768 symbols */
int mlkem768_keypair_derand(uint8_t *pk, uint8_t *sk, const uint8_t *coins);
int mlkem768_enc_derand(uint8_t *ct, uint8_t *ss, const uint8_t *pk, const uint8_t *coins);
int mlkem768_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);

#include "algorithms/source_ref/mlkem_fault_hooks.h"

#define PK_BYTES 1184
#define SK_BYTES 2400
#define CT_BYTES 1088
#define SS_BYTES 32

/* Deterministic RNG for reproducibility */
static uint64_t rng_state = 0x42424242DEADBEEFULL;

int randombytes(uint8_t *out, size_t outlen) {
    for (size_t i = 0; i < outlen; i++) {
        rng_state = rng_state * 6364136223846793005ULL + 1442695040888963407ULL;
        out[i] = (uint8_t)(rng_state >> 33);
    }
    return 0;
}

/* Compute simple SHA-like checksum for comparison */
static uint64_t checksum(const uint8_t *data, size_t len) {
    uint64_t h = 0x5555555555555555ULL;
    for (size_t i = 0; i < len; i++) {
        h = h * 31 + data[i];
    }
    return h;
}

int main(int argc, char **argv) {
    const char *opt_level = "unknown";
    if (argc > 1) opt_level = argv[1];
    
    printf("Compiler Sensitivity Test — Optimization: %s\n", opt_level);
    printf("Compiler: %s\n",
#if defined(__clang__)
    "clang " __clang_version__
#elif defined(__GNUC__)
    "gcc " __VERSION__
#else
    "unknown"
#endif
    );
    
    /* Reset deterministic RNG */
    rng_state = 0x42424242DEADBEEFULL;
    
    /* Deterministic seed */
    uint8_t seed[64];
    memset(seed, 0x42, 64);
    
    uint8_t pk[PK_BYTES], sk[SK_BYTES];
    mlkem_fault_reset();
    mlkem768_keypair_derand(pk, sk, seed);
    
    uint64_t pk_cksum = checksum(pk, PK_BYTES);
    uint64_t sk_cksum = checksum(sk, SK_BYTES);
    printf("  KeyGen pk_checksum: 0x%016llx\n", (unsigned long long)pk_cksum);
    printf("  KeyGen sk_checksum: 0x%016llx\n", (unsigned long long)sk_cksum);
    
    /* Deterministic encaps */
    uint8_t enc_seed[32];
    memset(enc_seed, 0xAA, 32);
    uint8_t ct[CT_BYTES], ss_enc[SS_BYTES];
    
    mlkem_fault_reset();
    mlkem768_enc_derand(ct, ss_enc, pk, enc_seed);
    
    uint64_t ct_cksum = checksum(ct, CT_BYTES);
    uint64_t ss_cksum = checksum(ss_enc, SS_BYTES);
    printf("  Encaps ct_checksum: 0x%016llx\n", (unsigned long long)ct_cksum);
    printf("  Encaps ss_checksum: 0x%016llx\n", (unsigned long long)ss_cksum);
    
    /* Decaps (fault-free) */
    uint8_t ss_dec[SS_BYTES];
    mlkem_fault_reset();
    mlkem768_dec(ss_dec, ct, sk);
    
    bool agree = (memcmp(ss_enc, ss_dec, SS_BYTES) == 0);
    uint64_t ss_dec_cksum = checksum(ss_dec, SS_BYTES);
    printf("  Decaps ss_checksum: 0x%016llx  key_agreement: %s\n",
           (unsigned long long)ss_dec_cksum, agree ? "YES" : "NO");
    
    /* Fault injection: NTT Layer 4, delta=+1 */
    mlkem_fault_reset();
    mlkem_fault_arm_mid_ntt_locus(4, 0, NTT_LOCUS_OUTPUT_ADD,
        FAULT_TYPE_ADDITIVE_GLITCH, 0, 1, 0);
    
    uint8_t ss_fault[SS_BYTES];
    mlkem768_dec(ss_fault, ct, sk);
    
    bool fault_agree = (memcmp(ss_enc, ss_fault, SS_BYTES) == 0);
    uint64_t ss_fault_cksum = checksum(ss_fault, SS_BYTES);
    printf("  Faulted decaps ss_checksum: 0x%016llx  key_agreement: %s\n",
           (unsigned long long)ss_fault_cksum, fault_agree ? "YES" : "NO");
    
    /* Summary line for automated parsing */
    printf("SUMMARY|%s|%016llx|%016llx|%016llx|%016llx|%016llx|%d|%016llx|%d\n",
           opt_level,
           (unsigned long long)pk_cksum,
           (unsigned long long)sk_cksum,
           (unsigned long long)ct_cksum,
           (unsigned long long)ss_cksum,
           (unsigned long long)ss_dec_cksum,
           agree,
           (unsigned long long)ss_fault_cksum,
           fault_agree);
    
    return agree ? 0 : 1;
}
