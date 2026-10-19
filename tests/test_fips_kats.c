/**
 * Explicit Reproducible NIST FIPS 203 & 204 Known Answer Test (KAT) Runner.
 * Verifies that Path B native implementations exactly reproduce standardized
 * test vectors across all parameter sets:
 *   - ML-KEM-512, ML-KEM-768, ML-KEM-1024
 *   - ML-DSA-44, ML-DSA-65, ML-DSA-87
 *
 * Prints structured validation output for every vector:
 *   algorithm | parameter set | vector ID | expected value | computed value | PASS/FAIL
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "kat_runners.h"

int randombytes(uint8_t *out, size_t outlen) {
    (void)out; (void)outlen;
    return 0;
}

void print_kat_hex_short(const char *label, const uint8_t *data, size_t len) {
    printf("  %-16s ", label);
    for (size_t i = 0; i < 8 && i < len; i++) {
        printf("%02x", data[i]);
    }
    printf("...%02x%02x\n", data[len - 2], data[len - 1]);
}

int main(void) {
    printf("=========================================================================\n");
    printf(" NIST FIPS 203 & 204 KNOWN ANSWER TEST (KAT) VERIFICATION SUITE\n");
    printf(" Sources: mlkem-native (fc269bc2d106) & mldsa-native (88a5369bb911)\n");
    printf("=========================================================================\n\n");

    int failed_suites = 0;

    printf("--- [1/6] ML-KEM-512 (FIPS 203) ---\n");
    if (run_mlkem512_kat() != 0) failed_suites++;

    printf("--- [2/6] ML-KEM-768 (FIPS 203) ---\n");
    if (run_mlkem768_kat() != 0) failed_suites++;

    printf("--- [3/6] ML-KEM-1024 (FIPS 203) ---\n");
    if (run_mlkem1024_kat() != 0) failed_suites++;

    printf("--- [4/6] ML-DSA-44 (FIPS 204) ---\n");
    if (run_mldsa44_kat() != 0) failed_suites++;

    printf("--- [5/6] ML-DSA-65 (FIPS 204) ---\n");
    if (run_mldsa65_kat() != 0) failed_suites++;

    printf("--- [6/6] ML-DSA-87 (FIPS 204) ---\n");
    if (run_mldsa87_kat() != 0) failed_suites++;

    printf("=========================================================================\n");
    if (failed_suites == 0) {
        printf(" >>> ALL NIST FIPS 203 & 204 TEST VECTORS VERIFIED SUCCESSFULLY (PASS) <<<\n");
        printf("     Checked: ML-KEM-512, ML-KEM-768, ML-KEM-1024\n");
        printf("     Checked: ML-DSA-44,  ML-DSA-65,  ML-DSA-87\n");
        printf("=========================================================================\n");
        return 0;
    } else {
        printf(" >>> FIPS KAT VERIFICATION SUITE FAILED (%d suites failed) <<<\n", failed_suites);
        printf("=========================================================================\n");
        return 1;
    }
}
