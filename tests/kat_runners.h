#ifndef KAT_RUNNERS_H
#define KAT_RUNNERS_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

void print_kat_hex_short(const char *label, const uint8_t *data, size_t len);

int run_mlkem512_kat(void);
int run_mlkem768_kat(void);
int run_mlkem1024_kat(void);

int run_mldsa44_kat(void);
int run_mldsa65_kat(void);
int run_mldsa87_kat(void);

#endif // KAT_RUNNERS_H
