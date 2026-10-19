/* fuzz_fault_contract.c — robustness harness for the contract (CRITERION 8).
 *
 * The shared body `fc_fuzz_one()` runs the full validate/classify/ledger path on
 * arbitrary bytes under ASAN/UBSAN; it must never crash or read OOB.
 *
 * Two front-ends:
 *   -DFC_LIBFUZZER  -> libFuzzer entry point (coverage-guided), if the runtime
 *                      is installed (full Xcode). Build with -fsanitize=fuzzer,...
 *   (default)       -> a self-contained deterministic driver (xorshift64 inputs),
 *                      used when the libFuzzer runtime is unavailable (CLT-only).
 */
#include "fault_contract.h"
#include <stdint.h>
#include <string.h>

static void fc_fuzz_one(const uint8_t *data, size_t size) {
    fc_trial_t t;
    memset(&t, 0, sizeof(t));
    size_t n = size < sizeof(t) ? size : sizeof(t);
    memcpy(&t, data, n);
    t.event.model_id[sizeof(t.event.model_id) - 1] = '\0';
    t.exclude_reason[sizeof(t.exclude_reason) - 1] = '\0';

    (void)fc_event_valid(&t.event);
    fc_outcome_t o = fc_classify(&t);
    (void)fc_outcome_name(o);

    fc_ledger_t l;
    fc_ledger_init(&l);
    fc_ledger_begin(&l);
    fc_ledger_record(&l, o);
    (void)fc_ledger_check(&l);
}

#if defined(FC_LIBFUZZER)
int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    fc_fuzz_one(data, size);
    return 0;
}
#else
#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    unsigned long iters = (argc > 1) ? strtoul(argv[1], NULL, 10) : 500000UL;
    uint64_t st = 0x9E3779B97F4A7C15ULL; /* deterministic seed */
    uint8_t buf[sizeof(fc_trial_t) + 16];
    for (unsigned long i = 0; i < iters; i++) {
        st ^= st << 13; st ^= st >> 7; st ^= st << 17;
        size_t n = (size_t)(st % (sizeof(buf) + 1));
        for (size_t j = 0; j < n; j++) {
            st ^= st << 13; st ^= st >> 7; st ^= st << 17;
            buf[j] = (uint8_t)st;
        }
        fc_fuzz_one(buf, n);
    }
    printf("standalone fuzz: %lu iterations, no ASAN/UBSAN violation\n", iters);
    return 0;
}
#endif
