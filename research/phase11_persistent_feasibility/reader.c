/* reader.c — SEPARATE translation unit that CONSUMES the table at runtime.
 * Because the table is defined in another TU and only declared extern-const here,
 * the compiler cannot constant-fold its values and must emit real memory loads,
 * so a change to the backing bytes is actually observed by this "computation".
 * Also provides laundered poke/peek so writes are not elided as writes-to-const. */
#include <stdint.h>
#include <stddef.h>

uint32_t fc_checksum(const int16_t *t, int n) {
    uint32_t h = 2166136261u;            /* FNV-ish mix over every element read */
    for (int i = 0; i < n; i++) {
        h ^= (uint16_t)t[i];
        h *= 16777619u;
    }
    return h;
}
void    fc_poke(void *p, int16_t v)        { *(volatile int16_t *)p = v; }
int16_t fc_peek(const void *p)             { return *(volatile const int16_t *)p; }
