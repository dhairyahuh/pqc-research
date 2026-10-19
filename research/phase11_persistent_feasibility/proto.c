/* proto.c — minimal, ISOLATED persistent-storage fault feasibility prototype.
 *
 * MODEL (not the real ML-KEM): a 128x int16 const table placed in __DATA_CONST,
 * mirroring the SIZE/ALIGN/const nature of the operational `mlk_zetas` table — but
 * relocated to a writable-after-vm_protect section. It does NOT touch mlkem_native.
 * The REAL `mlk_zetas` is in __TEXT,__const (code-signed) and is NOT writable here
 * (SIGBUS) without an approved research-only relocation of the SUT source.
 *
 * Per trial i: snapshot -> vm_protect(RW) -> laundered poke of table[i] -> read-back
 * (must change) -> consume via separate-TU checksum (must differ from clean baseline)
 * -> restore -> read-back (must equal orig) -> re-checksum (== baseline) -> re-protect RO.
 * Writes RESULTS.csv. Fails closed on any vm_protect/read-back/restore mismatch.
 */
#include <mach/mach.h>
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <string.h>

#define N 128
__attribute__((aligned(64)))
__attribute__((section("__DATA_CONST,__fc_tbl")))
const int16_t table[N] = {0};   /* zero-init; filled conceptually like a twiddle table */

extern uint32_t fc_checksum(const int16_t *, int);
extern void     fc_poke(void *, int16_t);
extern int16_t  fc_peek(const void *);

int main(int argc, char **argv) {
    const char *out = (argc > 1) ? argv[1] : "RESULTS.csv";
    FILE *fp = fopen(out, "w");
    if (!fp) { perror("fopen"); return 1; }
    fprintf(fp, "trial,coeff_index,orig,faulted,readback_changed,consumed_changed,restored_ok,baseline_reproduced\n");

    size_t ps = (size_t)getpagesize();
    uintptr_t pstart = ((uintptr_t)table) & ~(uintptr_t)(ps - 1);
    size_t span = ((((uintptr_t)table + sizeof(table) - 1) & ~(uintptr_t)(ps - 1)) - pstart) + ps;

    uint32_t base = fc_checksum(table, N);           /* clean baseline (reader TU) */
    uint32_t init_full = base;
    int ok_all = 1, consumed = 0;

    for (int i = 0; i < N; i++) {
        int16_t orig = fc_peek(&table[i]);
        if (vm_protect(mach_task_self(), (vm_address_t)pstart, span, FALSE,
                       VM_PROT_READ | VM_PROT_WRITE) != KERN_SUCCESS) {
            fprintf(stderr, "FAILCLOSED: vm_protect RW failed at trial %d\n", i); ok_all = 0; break;
        }
        int16_t faulted = (int16_t)(orig ^ (int16_t)0x0055);
        fc_poke((void *)(uintptr_t)&table[i], faulted);
        int rb_changed = (fc_peek(&table[i]) == faulted) && (faulted != orig);
        uint32_t cs = fc_checksum(table, N);
        int consumed_changed = (cs != base);
        fc_poke((void *)(uintptr_t)&table[i], orig);
        int restored_ok = (fc_peek(&table[i]) == orig);
        uint32_t cs2 = fc_checksum(table, N);
        int base_repro = (cs2 == base);
        vm_protect(mach_task_self(), (vm_address_t)pstart, span, FALSE, VM_PROT_READ);
        if (consumed_changed) consumed++;
        if (!(rb_changed && restored_ok && base_repro)) ok_all = 0;
        fprintf(fp, "%d,%d,%d,%d,%d,%d,%d,%d\n", i, i, orig, faulted,
                rb_changed, consumed_changed, restored_ok, base_repro);
    }
    uint32_t final_full = fc_checksum(table, N);
    int no_contam = (final_full == init_full);
    fclose(fp);
    printf("trials=%d consumed_changed=%d/%d all_rb+restore+baseline_ok=%d no_cross_trial_contam=%d\n",
           N, consumed, N, ok_all, no_contam);
    printf("wrote %s\n", out);
    return (ok_all && no_contam) ? 0 : 3;
}
