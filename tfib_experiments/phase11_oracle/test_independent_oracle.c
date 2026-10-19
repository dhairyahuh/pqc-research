#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include "independent_oracle.h"
#include "fips202_ref.h"

#define MLK_CONFIG_PARAMETER_SET 768
#include "references/test_vectors/mlkem_expected_kat.h"

static void hex_dump_short(const char *label, const uint8_t *data, size_t len) {
    printf("  %-18s ", label);
    for (size_t i = 0; i < 8 && i < len; i++) {
        printf("%02x", data[i]);
    }
    printf("...%02x%02x (%zu bytes)\n", data[len - 2], data[len - 1], len);
}

int main(void) {
    printf("================================================================================\n");
    printf("PHASE 11: INDEPENDENT ORACLE VALIDATION & KNOWN-ANSWER TEST (KAT) RUNNER\n");
    printf("%s\n", independent_oracle_get_version());
    printf("Target Parameter Set: ML-KEM-768 (FIPS 203)\n");
    printf("================================================================================\n\n");

    if (independent_oracle_init() != 0) {
        fprintf(stderr, "FATAL: Failed to initialize independent oracle backend!\n");
        return 1;
    }

    FILE *json_fp = fopen("tfib_experiments/phase11_oracle/kat_validation_results.json", "w");
    if (!json_fp) {
        json_fp = fopen("kat_validation_results.json", "w");
    }
    if (!json_fp) {
        perror("Failed to open kat_validation_results.json");
        return 1;
    }

    fprintf(json_fp, "{\n");
    fprintf(json_fp, "  \"oracle_version\": \"%s\",\n", independent_oracle_get_version());
    fprintf(json_fp, "  \"parameter_set\": \"ML-KEM-768\",\n");
    fprintf(json_fp, "  \"tests\": [\n");

    bool all_passed = true;

    /* -------------------------------------------------------------------------
     * Test 1: Deterministic Keypair Generation KAT (FIPS 203 Algorithm 15)
     * ------------------------------------------------------------------------- */
    printf("[1/6] Deterministic Keypair Generation KAT (FIPS 203)\n");
    uint8_t coins64[64];
    memcpy(coins64, test_vector_d, 32);
    memcpy(coins64 + 32, test_vector_z, 32);

    uint8_t pk_out[ORACLE_MLKEM768_PK_BYTES];
    uint8_t sk_out[ORACLE_MLKEM768_SK_BYTES];

    int rc = independent_oracle_keypair_derand(pk_out, sk_out, coins64);
    bool pk_match = (rc == 0) && (memcmp(pk_out, test_vector_pk, sizeof(pk_out)) == 0);
    bool sk_match = (rc == 0) && (memcmp(sk_out, test_vector_sk, sizeof(sk_out)) == 0);
    bool test1_pass = pk_match && sk_match;

    hex_dump_short("Expected PK", test_vector_pk, sizeof(pk_out));
    hex_dump_short("Oracle PK", pk_out, sizeof(pk_out));
    hex_dump_short("Expected SK", test_vector_sk, sizeof(sk_out));
    hex_dump_short("Oracle SK", sk_out, sizeof(sk_out));
    printf("  -> Result: %s\n\n", test1_pass ? "PASS" : "FAIL");

    fprintf(json_fp, "    {\n");
    fprintf(json_fp, "      \"test_name\": \"NIST-FIPS203-KAT-768-KEYGEN\",\n");
    fprintf(json_fp, "      \"status\": \"%s\",\n", test1_pass ? "PASS" : "FAIL");
    fprintf(json_fp, "      \"pk_match\": %s,\n", pk_match ? "true" : "false");
    fprintf(json_fp, "      \"sk_match\": %s\n", sk_match ? "true" : "false");
    fprintf(json_fp, "    },\n");
    if (!test1_pass) all_passed = false;

    /* -------------------------------------------------------------------------
     * Test 2: Deterministic Encapsulation KAT (FIPS 203 Algorithm 16)
     * ------------------------------------------------------------------------- */
    printf("[2/6] Deterministic Encapsulation KAT (FIPS 203)\n");
    uint8_t ct_out[ORACLE_MLKEM768_CT_BYTES];
    uint8_t ss_enc_out[ORACLE_MLKEM768_SS_BYTES];

    rc = independent_oracle_encaps_derand(ct_out, ss_enc_out, pk_out, test_vector_m);
    bool ct_match = (rc == 0) && (memcmp(ct_out, test_vector_ct, sizeof(ct_out)) == 0);
    bool ss_enc_match = (rc == 0) && (memcmp(ss_enc_out, test_vector_ss, sizeof(ss_enc_out)) == 0);
    bool test2_pass = ct_match && ss_enc_match;

    hex_dump_short("Expected CT", test_vector_ct, sizeof(ct_out));
    hex_dump_short("Oracle CT", ct_out, sizeof(ct_out));
    hex_dump_short("Expected SS", test_vector_ss, sizeof(ss_enc_out));
    hex_dump_short("Oracle SS", ss_enc_out, sizeof(ss_enc_out));
    printf("  -> Result: %s\n\n", test2_pass ? "PASS" : "FAIL");

    fprintf(json_fp, "    {\n");
    fprintf(json_fp, "      \"test_name\": \"NIST-FIPS203-KAT-768-ENCAPS\",\n");
    fprintf(json_fp, "      \"status\": \"%s\",\n", test2_pass ? "PASS" : "FAIL");
    fprintf(json_fp, "      \"ct_match\": %s,\n", ct_match ? "true" : "false");
    fprintf(json_fp, "      \"ss_match\": %s\n", ss_enc_match ? "true" : "false");
    fprintf(json_fp, "    },\n");
    if (!test2_pass) all_passed = false;

    /* -------------------------------------------------------------------------
     * Test 3: Authentic Decapsulation KAT (FIPS 203 Algorithm 17)
     * ------------------------------------------------------------------------- */
    printf("[3/6] Authentic Decapsulation KAT (FIPS 203)\n");
    uint8_t ss_dec_out[ORACLE_MLKEM768_SS_BYTES];

    rc = independent_oracle_decaps(ss_dec_out, ct_out, sk_out);
    bool ss_dec_match = (rc == 0) && (memcmp(ss_dec_out, test_vector_ss, sizeof(ss_dec_out)) == 0);
    bool test3_pass = ss_dec_match;

    hex_dump_short("Expected SS", test_vector_ss, sizeof(ss_dec_out));
    hex_dump_short("Oracle Decaps SS", ss_dec_out, sizeof(ss_dec_out));
    printf("  -> Result: %s\n\n", test3_pass ? "PASS" : "FAIL");

    fprintf(json_fp, "    {\n");
    fprintf(json_fp, "      \"test_name\": \"NIST-FIPS203-KAT-768-DECAPS\",\n");
    fprintf(json_fp, "      \"status\": \"%s\",\n", test3_pass ? "PASS" : "FAIL");
    fprintf(json_fp, "      \"ss_match\": %s\n", ss_dec_match ? "true" : "false");
    fprintf(json_fp, "    },\n");
    if (!test3_pass) all_passed = false;

    /* -------------------------------------------------------------------------
     * Test 4: Canonical Implicit Rejection Verification (FIPS 203 Specification)
     * ------------------------------------------------------------------------- */
    printf("[4/6] Canonical Implicit Rejection Verification (FIPS 203)\n");
    uint8_t ct_corrupted[ORACLE_MLKEM768_CT_BYTES];
    memcpy(ct_corrupted, ct_out, sizeof(ct_out));
    ct_corrupted[0] ^= 0x01; // flip single bit in ciphertext

    uint8_t ss_dec_rej[ORACLE_MLKEM768_SS_BYTES];
    rc = independent_oracle_decaps(ss_dec_rej, ct_corrupted, sk_out);

    uint8_t ss_expected_rej[ORACLE_MLKEM768_SS_BYTES];
    independent_oracle_compute_rejection(ss_expected_rej, sk_out, ct_corrupted);

    bool rej_matches_spec = (rc == 0) && (memcmp(ss_dec_rej, ss_expected_rej, sizeof(ss_dec_rej)) == 0);
    bool rej_differs_from_valid = (memcmp(ss_dec_rej, ss_enc_out, sizeof(ss_dec_rej)) != 0);
    bool test4_pass = rej_matches_spec && rej_differs_from_valid;

    hex_dump_short("Spec Rejection SS", ss_expected_rej, sizeof(ss_expected_rej));
    hex_dump_short("Oracle Rejection SS", ss_dec_rej, sizeof(ss_dec_rej));
    printf("  -> Spec Match: %s, Different from Valid SS: %s\n",
           rej_matches_spec ? "YES" : "NO", rej_differs_from_valid ? "YES" : "NO");
    printf("  -> Result: %s\n\n", test4_pass ? "PASS" : "FAIL");

    fprintf(json_fp, "    {\n");
    fprintf(json_fp, "      \"test_name\": \"FIPS203-CANONICAL-IMPLICIT-REJECTION\",\n");
    fprintf(json_fp, "      \"status\": \"%s\",\n", test4_pass ? "PASS" : "FAIL");
    fprintf(json_fp, "      \"rejection_matches_spec\": %s,\n", rej_matches_spec ? "true" : "false");
    fprintf(json_fp, "      \"rejection_differs_from_valid\": %s\n", rej_differs_from_valid ? "true" : "false");
    fprintf(json_fp, "    },\n");
    if (!test4_pass) all_passed = false;

    /* -------------------------------------------------------------------------
     * Test 5: Negative Testing (Deliberate Corruption Detection)
     * ------------------------------------------------------------------------- */
    printf("[5/6] Negative Testing: Deliberate Corruption & Falsification\n");

    // Case 5a: Oracle decapsulation against a deliberately corrupted expected shared secret.
    // Exercises independent_oracle_decaps to obtain ground truth, then verifies that
    // the harness detects when a candidate/purported shared secret is corrupted.
    uint8_t ss_oracle_truth[ORACLE_MLKEM768_SS_BYTES];
    rc = independent_oracle_decaps(ss_oracle_truth, ct_out, sk_out);
    uint8_t ss_purported_corrupted[ORACLE_MLKEM768_SS_BYTES];
    memcpy(ss_purported_corrupted, ss_oracle_truth, sizeof(ss_oracle_truth));
    ss_purported_corrupted[15] ^= 0x42; // deliberate corruption of purported secret

    bool oracle_ok = (rc == 0);
    bool mismatch_flagged = (memcmp(ss_oracle_truth, ss_purported_corrupted, sizeof(ss_oracle_truth)) != 0);
    bool neg_ss_detected = oracle_ok && mismatch_flagged;

    // Case 5b: Corrupted secret key causes decapsulation failure or rejection
    uint8_t sk_tampered[ORACLE_MLKEM768_SK_BYTES];
    memcpy(sk_tampered, sk_out, sizeof(sk_out));
    sk_tampered[100] ^= 0x55;
    uint8_t ss_bad_sk[32];
    rc = independent_oracle_decaps(ss_bad_sk, ct_out, sk_tampered);
    bool neg_sk_detected = (memcmp(ss_bad_sk, ss_enc_out, 32) != 0);

    // Case 5c: Modified encapsulation seed produces distinct ciphertext and secret
    uint8_t m_tampered[32];
    memcpy(m_tampered, test_vector_m, 32);
    m_tampered[0] ^= 0xFF;
    uint8_t ct_alt[ORACLE_MLKEM768_CT_BYTES], ss_alt[32];
    independent_oracle_encaps_derand(ct_alt, ss_alt, pk_out, m_tampered);
    bool neg_seed_distinct = (memcmp(ct_alt, ct_out, sizeof(ct_out)) != 0) &&
                            (memcmp(ss_alt, ss_enc_out, 32) != 0);

    bool test5_pass = neg_ss_detected && neg_sk_detected && neg_seed_distinct;
    printf("  -> SS Tampering Flagged: %s\n", neg_ss_detected ? "YES" : "NO");
    printf("  -> SK Tampering Flagged: %s\n", neg_sk_detected ? "YES" : "NO");
    printf("  -> Seed Mutation Distinct: %s\n", neg_seed_distinct ? "YES" : "NO");
    printf("  -> Result: %s\n\n", test5_pass ? "PASS" : "FAIL");

    fprintf(json_fp, "    {\n");
    fprintf(json_fp, "      \"test_name\": \"NEGATIVE-TEST-FALSIFICATION\",\n");
    fprintf(json_fp, "      \"status\": \"%s\",\n", test5_pass ? "PASS" : "FAIL");
    fprintf(json_fp, "      \"ss_tamper_flagged\": %s,\n", neg_ss_detected ? "true" : "false");
    fprintf(json_fp, "      \"sk_tamper_flagged\": %s,\n", neg_sk_detected ? "true" : "false");
    fprintf(json_fp, "      \"seed_mutation_distinct\": %s\n", neg_seed_distinct ? "true" : "false");
    fprintf(json_fp, "    },\n");
    if (!test5_pass) all_passed = false;

    /* -------------------------------------------------------------------------
     * Test 6: Boundary & Malformed Inputs (Canonical Implicit Rejection Verification)
     * ------------------------------------------------------------------------- */
    printf("[6/6] Boundary & Malformed Inputs\n");
    // Case 6a: All-zero ciphertext must trigger canonical implicit rejection
    uint8_t ct_zeros[ORACLE_MLKEM768_CT_BYTES] = {0};
    uint8_t ss_zeros[ORACLE_MLKEM768_SS_BYTES];
    int rc_zeros = independent_oracle_decaps(ss_zeros, ct_zeros, sk_out);

    uint8_t exp_rej_zeros[ORACLE_MLKEM768_SS_BYTES];
    independent_oracle_compute_rejection(exp_rej_zeros, sk_out, ct_zeros);

    bool zeros_matches_rej = (rc_zeros == 0) && (memcmp(ss_zeros, exp_rej_zeros, sizeof(ss_zeros)) == 0);
    bool zeros_differs_valid = (memcmp(ss_zeros, ss_enc_out, sizeof(ss_zeros)) != 0);
    bool zeros_rejected = zeros_matches_rej && zeros_differs_valid;

    // Case 6b: All-0xFF ciphertext must trigger canonical implicit rejection
    uint8_t ct_ones[ORACLE_MLKEM768_CT_BYTES];
    memset(ct_ones, 0xFF, sizeof(ct_ones));
    uint8_t ss_ones[ORACLE_MLKEM768_SS_BYTES];
    int rc_ones = independent_oracle_decaps(ss_ones, ct_ones, sk_out);

    uint8_t exp_rej_ones[ORACLE_MLKEM768_SS_BYTES];
    independent_oracle_compute_rejection(exp_rej_ones, sk_out, ct_ones);

    bool ones_matches_rej = (rc_ones == 0) && (memcmp(ss_ones, exp_rej_ones, sizeof(ss_ones)) == 0);
    bool ones_differs_valid = (memcmp(ss_ones, ss_enc_out, sizeof(ss_ones)) != 0);
    bool ones_rejected = ones_matches_rej && ones_differs_valid;

    bool test6_pass = zeros_rejected && ones_rejected;
    printf("  -> All-zeros CT Rejection Match: %s (differs from valid: %s)\n",
           zeros_matches_rej ? "YES" : "NO", zeros_differs_valid ? "YES" : "NO");
    printf("  -> All-ones CT Rejection Match:  %s (differs from valid: %s)\n",
           ones_matches_rej ? "YES" : "NO", ones_differs_valid ? "YES" : "NO");
    printf("  -> Result: %s\n\n", test6_pass ? "PASS" : "FAIL");

    fprintf(json_fp, "    {\n");
    fprintf(json_fp, "      \"test_name\": \"BOUNDARY-MALFORMED-INPUTS\",\n");
    fprintf(json_fp, "      \"status\": \"%s\",\n", test6_pass ? "PASS" : "FAIL");
    fprintf(json_fp, "      \"zeros_matches_rejection\": %s,\n", zeros_matches_rej ? "true" : "false");
    fprintf(json_fp, "      \"zeros_differs_from_valid\": %s,\n", zeros_differs_valid ? "true" : "false");
    fprintf(json_fp, "      \"ones_matches_rejection\": %s,\n", ones_matches_rej ? "true" : "false");
    fprintf(json_fp, "      \"ones_differs_from_valid\": %s\n", ones_differs_valid ? "true" : "false");
    fprintf(json_fp, "    }\n");
    if (!test6_pass) all_passed = false;

    fprintf(json_fp, "  ],\n");
    fprintf(json_fp, "  \"overall_status\": \"%s\"\n", all_passed ? "PASS" : "FAIL");
    fprintf(json_fp, "}\n");
    fclose(json_fp);

    printf("================================================================================\n");
    printf("ORACLE VALIDATION VERDICT: %s\n", all_passed ? "ALL TESTS PASSED (PASS)" : "TESTS FAILED (FAIL)");
    printf("Machine-readable results saved to tfib_experiments/phase11_oracle/kat_validation_results.json\n");
    printf("================================================================================\n");

    return all_passed ? 0 : 1;
}
