#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "algorithms/source_ref/mlkem_fault_hooks.h"

int mlkem768_keypair(uint8_t *pk, uint8_t *sk);
int mlkem768_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int mlkem768_dec_monitored(uint8_t *ss, const uint8_t *ct, const uint8_t *sk, uint32_t *internal_status);

int randombytes(uint8_t *out, size_t outlen) {
    for (size_t i = 0; i < outlen; i++) out[i] = (uint8_t)(i & 0xFF);
    return 0;
}

int main(void) {
    printf("Testing production link with mlkem768_inst.o and mlkem_fault_hooks.o\n");
    ntt_native_monitor_configure(1, true, 0x7F);
    
    uint8_t pk[1184], sk[2400], ct[1088], ss_enc[32], ss_dec[32];
    uint32_t status = 0;
    
    mlkem768_keypair(pk, sk);
    mlkem768_enc(ct, ss_enc, pk);
    
    // Clean run
    ntt_native_monitor_reset();
    int rc = mlkem768_dec_monitored(ss_dec, ct, sk, &status);
    printf("Clean run: rc=%d, status=0x%08X, persistent=%u, recovered=%u, executed=%u\n",
           rc, status, ntt_native_monitor_get_persistent_count(),
           g_ntt_native_monitor.recovered_count, g_ntt_native_monitor.executed_count);
           
    // Test transient fault during NTT using production fault hook
    mlkem_fault_arm_mid_ntt_locus(1, 10, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, 0, 0, 0);
    g_mlkem_fault.persistent = false;
    ntt_native_monitor_reset();
    rc = mlkem768_dec_monitored(ss_dec, ct, sk, &status);
    printf("Transient fault run: rc=%d, status=0x%08X, persistent=%u, recovered=%u, mismatch=%u\n",
           rc, status, ntt_native_monitor_get_persistent_count(),
           g_ntt_native_monitor.recovered_count, g_ntt_native_monitor.mismatch_count);

    // Test persistent fault during NTT using production fault hook
    mlkem_fault_arm_mid_ntt_locus(1, 10, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, 0, 0, 0);
    g_mlkem_fault.persistent = true;
    ntt_native_monitor_reset();
    rc = mlkem768_dec_monitored(ss_dec, ct, sk, &status);
    printf("Persistent fault run: rc=%d, status=0x%08X, persistent=%u, recovered=%u, mismatch=%u\n",
           rc, status, ntt_native_monitor_get_persistent_count(),
           g_ntt_native_monitor.recovered_count, g_ntt_native_monitor.mismatch_count);
           
    return 0;
}
