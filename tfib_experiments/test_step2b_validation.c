/**
 * Phase 2 — Step 2B Validation Test Suite (Remediated)
 *
 * Subject: Deterministic SHAKE-256 PRF-based Input Generation & Independent Keypair Generation
 *
 * Verifies:
 *   Test A: SHAKE-256 campaign PRF determinism (same inputs → identical output)
 *   Test B: PRF domain separation across trials, modes, loci (all 6 loci), and persistence flags
 *   Test C: Independent oracle keypair_derand produces valid pk/sk from PRF seed
 *   Test D: Clean valid-path pipeline decapsulation strictly matches oracle expected valid secret
 *           and strictly does NOT match expected rejection secret (resolves DEF-01)
 *   Test E: Symbol and disassembly verification — runner binary has no undefined srand/rand
 *           and zero call-site references to mlkem768_keypair
 *   Test F: PRF output distribution quality (non-zero, ≥16 distinct byte values)
 *   Test G: Explicit Little-Endian Serialization & SHAKE-256 KAT (resolves DEF-05)
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include "independent_oracle.h"
#include "fips202_ref.h"
#include "tfib_common.h"
#include "tfib_core.h"
#include "campaign_prf.h"

#define SS_BYTES 32
#define CT_BYTES 1088
#define SK_BYTES 2400
#define PK_BYTES 1184

/* Production decapsulation under test */
int mlkem768_dec_monitored(uint8_t *ss, const uint8_t *ct, const uint8_t *sk, uint32_t *internal_status);

/* Provide required randombytes symbol for linker resolution of mlkem768_inst.o */
int randombytes(uint8_t *out, size_t outlen) {
    for (size_t i = 0; i < outlen; i++) out[i] = (uint8_t)(i ^ 0xAA);
    return 0;
}

static int tests_passed = 0;
static int tests_failed = 0;

static void report(const char *name, bool pass) {
    printf("  [%s] %s\n", pass ? "PASS" : "FAIL", name);
    if (pass) tests_passed++; else tests_failed++;
}

/* -------------------------------------------------------------------- */
/* Test A: SHAKE-256 PRF determinism                                    */
/* -------------------------------------------------------------------- */
static void test_a_prf_determinism(void) {
    uint8_t out1[96], out2[96];
    campaign_prf(out1, sizeof(out1), 42, TFIB_MODE_REF, TFIB_FAULT_OP_TWIDDLE, false);
    campaign_prf(out2, sizeof(out2), 42, TFIB_MODE_REF, TFIB_FAULT_OP_TWIDDLE, false);
    report("Test A: SHAKE-256 PRF determinism (same inputs → identical output)",
           memcmp(out1, out2, sizeof(out1)) == 0);
}

/* -------------------------------------------------------------------- */
/* Test B: PRF domain separation (trials, modes, loci, persistence)     */
/* -------------------------------------------------------------------- */
static void test_b_prf_domain_separation(void) {
    uint8_t out_base[96];
    campaign_prf(out_base, sizeof(out_base), 0, TFIB_MODE_BASELINE, TFIB_FAULT_NONE, false);

    /* 1. Trial differentiation */
    uint8_t out_trial1[96];
    campaign_prf(out_trial1, sizeof(out_trial1), 1, TFIB_MODE_BASELINE, TFIB_FAULT_NONE, false);
    bool diff_trial = (memcmp(out_base, out_trial1, sizeof(out_base)) != 0);

    /* 2. Mode differentiation (all 3 modes pairwise distinct) */
    uint8_t out_ref[96], out_meta[96];
    campaign_prf(out_ref, sizeof(out_ref), 0, TFIB_MODE_REF, TFIB_FAULT_NONE, false);
    campaign_prf(out_meta, sizeof(out_meta), 0, TFIB_MODE_META, TFIB_FAULT_NONE, false);
    bool diff_mode = (memcmp(out_base, out_ref, sizeof(out_base)) != 0) &&
                     (memcmp(out_base, out_meta, sizeof(out_base)) != 0) &&
                     (memcmp(out_ref, out_meta, sizeof(out_ref)) != 0);

    /* 3. Locus differentiation (exercise all 6 fault loci pairwise) */
    tfib_fault_locus_t loci[6] = {
        TFIB_FAULT_NONE,
        TFIB_FAULT_OP_TWIDDLE,
        TFIB_FAULT_REF_TWIDDLE,
        TFIB_FAULT_SIMULTANEOUS,
        TFIB_FAULT_CHECKER_LOGIC,
        TFIB_FAULT_META_TAG
    };
    uint8_t out_loci[6][96];
    for (int i = 0; i < 6; i++) {
        campaign_prf(out_loci[i], 96, 0, TFIB_MODE_REF, loci[i], false);
    }
    bool diff_locus = true;
    for (int i = 0; i < 6; i++) {
        for (int j = i + 1; j < 6; j++) {
            if (memcmp(out_loci[i], out_loci[j], 96) == 0) {
                diff_locus = false;
            }
        }
    }

    /* 4. Persistence flag differentiation */
    uint8_t out_persist[96];
    campaign_prf(out_persist, sizeof(out_persist), 0, TFIB_MODE_BASELINE, TFIB_FAULT_NONE, true);
    bool diff_persist = (memcmp(out_base, out_persist, sizeof(out_base)) != 0);

    report("Test B: PRF domain separation (trial, mode, all 6 loci, persistence all distinct)",
           diff_trial && diff_mode && diff_locus && diff_persist);
}

/* -------------------------------------------------------------------- */
/* Test C: Oracle keypair_derand produces valid key material             */
/* -------------------------------------------------------------------- */
static void test_c_oracle_keypair(void) {
    uint8_t prf_out[96];
    campaign_prf(prf_out, sizeof(prf_out), 0, TFIB_MODE_BASELINE, TFIB_FAULT_NONE, false);

    uint8_t pk[PK_BYTES], sk[SK_BYTES];
    int rc = independent_oracle_keypair_derand(pk, sk, prf_out);
    bool keygen_ok = (rc == 0);

    /* Verify pk/sk are not all zero */
    uint8_t zero_pk[PK_BYTES] = {0};
    uint8_t zero_sk[SK_BYTES] = {0};
    bool pk_nontrivial = (memcmp(pk, zero_pk, PK_BYTES) != 0);
    bool sk_nontrivial = (memcmp(sk, zero_sk, SK_BYTES) != 0);

    report("Test C: Oracle keypair_derand produces valid non-trivial keys",
           keygen_ok && pk_nontrivial && sk_nontrivial);
}

/* -------------------------------------------------------------------- */
/* Test D: Strengthened Clean Valid-Path Decapsulation Pipeline (DEF-01) */
/* -------------------------------------------------------------------- */
static void test_d_clean_path_pipeline(void) {
    int clean_failures = 0;
    int trials = 20;

    for (int t = 0; t < trials; t++) {
        uint8_t prf_out[96];
        campaign_prf(prf_out, sizeof(prf_out), t, TFIB_MODE_BASELINE, TFIB_FAULT_NONE, false);

        uint8_t pk[PK_BYTES], sk[SK_BYTES], ct[CT_BYTES];
        uint8_t ss_expected[SS_BYTES], ss_out[SS_BYTES], ss_rej[SS_BYTES];

        /* Independent oracle keypair generation */
        int kp_rc = independent_oracle_keypair_derand(pk, sk, prf_out);
        assert(kp_rc == 0);

        /* Independent oracle encapsulation */
        int enc_rc = independent_oracle_encaps_derand(ct, ss_expected, pk, prf_out + 64);
        assert(enc_rc == 0);

        /* Independent oracle canonical implicit rejection calculation */
        int rej_rc = independent_oracle_compute_rejection(ss_rej, sk, ct);
        assert(rej_rc == 0);

        /* Production decapsulation under test (clean control, no fault) */
        tfib_set_mode(TFIB_MODE_BASELINE);
        tfib_fault_reset();
        tfib_reset_all_stats();

        uint32_t status = 0;
        mlkem768_dec_monitored(ss_out, ct, sk, &status);

        /* Strict Clean-Path Invariants (DEF-01 Remediation):
         * 1. Output MUST match the independent oracle's valid expected shared secret.
         * 2. Output MUST NOT match the implicit rejection key.
         * 3. Valid shared secret and rejection key MUST be distinct.
         */
        bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        bool rej_match = (memcmp(ss_out, ss_rej, SS_BYTES) == 0);
        bool keys_distinct = (memcmp(ss_expected, ss_rej, SS_BYTES) != 0);

        if (!ss_match || rej_match || !keys_distinct) {
            clean_failures++;
        }
    }

    report("Test D: Clean valid-path decapsulation matches oracle valid secret and differs from rejection key",
           clean_failures == 0);
}

/* -------------------------------------------------------------------- */
/* Test E: Symbol verification & Call-Site Audit                        */
/* -------------------------------------------------------------------- */
static void test_e_symbol_verification(void) {
    /* Verify srand and rand are not undefined symbols in runner binary */
    int rc = system("nm tfib_experiments/tfib_experiment_runner 2>/dev/null | grep -q ' U _srand'");
    bool no_srand = (rc != 0);

    int rc2 = system("nm tfib_experiments/tfib_experiment_runner 2>/dev/null | grep -q ' U _rand$'");
    bool no_rand = (rc2 != 0);

    /* Verify mlkem768_keypair has 0 call sites in runner binary */
    int keypair_calls = system("otool -tV tfib_experiments/tfib_experiment_runner 2>/dev/null | grep -q 'mlkem768_keypair$'");
    bool no_keypair_calls = (keypair_calls != 0); /* grep non-zero = 0 matches = pass */

    report("Test E: Runner binary has no undefined srand/rand and 0 mlkem768_keypair call sites",
           no_srand && no_rand && no_keypair_calls);
}

/* -------------------------------------------------------------------- */
/* Test F: PRF output quality (not all-zero, byte diversity)            */
/* -------------------------------------------------------------------- */
static void test_f_prf_quality(void) {
    uint8_t out[96];
    campaign_prf(out, sizeof(out), 0, TFIB_MODE_REF, TFIB_FAULT_OP_TWIDDLE, false);

    uint8_t zeros[96] = {0};
    bool not_zero = (memcmp(out, zeros, sizeof(out)) != 0);

    /* Check byte distribution: at least 16 distinct byte values in 96 bytes */
    bool seen[256] = {false};
    int distinct = 0;
    for (int i = 0; i < 96; i++) {
        if (!seen[out[i]]) { seen[out[i]] = true; distinct++; }
    }
    bool good_distribution = (distinct >= 16);

    report("Test F: PRF output is non-zero with reasonable byte diversity (>=16 distinct)",
           not_zero && good_distribution);
}

/* -------------------------------------------------------------------- */
/* Test G: Explicit Little-Endian Serialization & SHAKE-256 KAT (DEF-05)*/
/* -------------------------------------------------------------------- */
static void test_g_explicit_serialization_kat(void) {
    /* KAT Case 1: trial=0, mode=BASELINE, locus=NONE, persistent=false */
    const uint8_t expected_ctx1[16] = {
        0xDE, 0xC0, 0x37, 0x13,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00
    };
    const uint8_t expected_hash1[32] = {
        0x04, 0x11, 0xef, 0x60, 0x15, 0xd2, 0x30, 0x69,
        0x32, 0xf3, 0x36, 0xf8, 0x2f, 0x05, 0xeb, 0xe9,
        0xb7, 0xf0, 0x97, 0x3c, 0xc3, 0xbb, 0xe3, 0x11,
        0x48, 0x08, 0x62, 0x6e, 0x38, 0x72, 0x1e, 0x77
    };

    uint8_t actual_ctx1[16];
    campaign_prf_serialize_context(actual_ctx1, 0, TFIB_MODE_BASELINE, TFIB_FAULT_NONE, false);
    bool ctx1_match = (memcmp(actual_ctx1, expected_ctx1, 16) == 0);

    uint8_t actual_hash1[32];
    fips202_ref_shake256(actual_hash1, sizeof(actual_hash1), actual_ctx1, sizeof(actual_ctx1));
    bool hash1_match = (memcmp(actual_hash1, expected_hash1, 32) == 0);

    /* KAT Case 2: trial=42, mode=REF, locus=OP_TWIDDLE, persistent=true */
    /* trial_word = 0x1337C0DE + 42 * 31 = 0x1337C5F4 */
    const uint8_t expected_ctx2[16] = {
        0xF4, 0xC5, 0x37, 0x13,
        0x01, 0x00, 0x00, 0x00,
        0x01, 0x00, 0x00, 0x00,
        0x01, 0x00, 0x00, 0x00
    };
    const uint8_t expected_hash2[32] = {
        0x53, 0xd6, 0xc8, 0x23, 0x70, 0x67, 0x69, 0x52,
        0x42, 0xc5, 0xf6, 0xa0, 0x45, 0x58, 0xa8, 0xa2,
        0x8e, 0x5b, 0x1e, 0x54, 0x44, 0x99, 0x1b, 0xb4,
        0x37, 0xa7, 0x55, 0x73, 0x81, 0x9f, 0x7b, 0xc2
    };

    uint8_t actual_ctx2[16];
    campaign_prf_serialize_context(actual_ctx2, 42, TFIB_MODE_REF, TFIB_FAULT_OP_TWIDDLE, true);
    bool ctx2_match = (memcmp(actual_ctx2, expected_ctx2, 16) == 0);

    uint8_t actual_hash2[32];
    fips202_ref_shake256(actual_hash2, sizeof(actual_hash2), actual_ctx2, sizeof(actual_ctx2));
    bool hash2_match = (memcmp(actual_hash2, expected_hash2, 32) == 0);

    report("Test G: Explicit Little-Endian Serialization & SHAKE-256 KAT (Cases 1 & 2)",
           ctx1_match && hash1_match && ctx2_match && hash2_match);
}

int main(void) {
    if (independent_oracle_init() != 0) {
        fprintf(stderr, "FATAL: Oracle init failed!\n");
        return 1;
    }

    printf("================================================================================\n");
    printf("Phase 2 — Step 2B Remediation Validation Test Suite\n");
    printf("Subject: Deterministic SHAKE-256 PRF + Independent Keypair Generation\n");
    printf("================================================================================\n");

    test_a_prf_determinism();
    test_b_prf_domain_separation();
    test_c_oracle_keypair();
    test_d_clean_path_pipeline();
    test_e_symbol_verification();
    test_f_prf_quality();
    test_g_explicit_serialization_kat();

    printf("\n================================================================================\n");
    printf("RESULTS: %d passed, %d failed\n", tests_passed, tests_failed);
    printf("================================================================================\n");

    return tests_failed > 0 ? 1 : 0;
}
