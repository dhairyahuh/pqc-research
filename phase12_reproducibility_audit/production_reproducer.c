#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include "algorithms/source_ref/mlkem_fault_hooks.h"

#define SS_BYTES 32
#define CT_BYTES 1088
#define SK_BYTES 2400
#define PK_BYTES 1184
#define Z_BYTES  32

/* =========================================================================
 * Clean-room Independent Keccak-f[1600] / SHAKE256 Implementation
 * ========================================================================= */
#define KECCAK_ROUNDS 24
#define SHAKE256_RATE 136

static const uint64_t keccakf_rndc[24] = {
    0x0000000000000001ULL, 0x0000000000008082ULL, 0x800000000000808aULL,
    0x8000000080008000ULL, 0x000000000000808bULL, 0x0000000080000001ULL,
    0x8000000080008081ULL, 0x8000000000008009ULL, 0x000000000000008aULL,
    0x0000000000000088ULL, 0x0000000080008009ULL, 0x000000008000000aULL,
    0x000000008000808bULL, 0x800000000000008bULL, 0x8000000000008089ULL,
    0x8000000000008003ULL, 0x8000000000008002ULL, 0x8000000000000080ULL,
    0x000000000000800aULL, 0x800000008000000aULL, 0x8000000080008081ULL,
    0x8000000000008080ULL, 0x0000000080000001ULL, 0x8000000080008008ULL
};

static const unsigned int keccakf_rotc[24] = {
    1,  3,  6,  10, 15, 21, 28, 36, 45, 55, 2,  14,
    27, 41, 56, 8,  25, 43, 62, 18, 39, 61, 20, 44
};

static const unsigned int keccakf_piln[24] = {
    10, 7,  11, 17, 18, 3, 5,  16, 8,  21, 24, 4,
    15, 23, 19, 13, 12, 2, 20, 14, 22, 9,  6,  1
};

static inline uint64_t rotl64(uint64_t x, unsigned int n) {
    return (x << n) | (x >> (64 - n));
}

static void cleanroom_keccak_f1600(uint64_t state[25]) {
    for (int round = 0; round < KECCAK_ROUNDS; round++) {
        uint64_t C[5], D[5];
        for (int i = 0; i < 5; i++)
            C[i] = state[i] ^ state[i + 5] ^ state[i + 10] ^ state[i + 15] ^ state[i + 20];
        for (int i = 0; i < 5; i++)
            D[i] = C[(i + 4) % 5] ^ rotl64(C[(i + 1) % 5], 1);
        for (int i = 0; i < 25; i++)
            state[i] ^= D[i % 5];

        uint64_t last = state[1];
        for (int i = 0; i < 24; i++) {
            int next_idx = keccakf_piln[i];
            uint64_t temp = state[next_idx];
            state[next_idx] = rotl64(last, keccakf_rotc[i]);
            last = temp;
        }

        for (int j = 0; j < 25; j += 5) {
            uint64_t t[5];
            for (int i = 0; i < 5; i++) t[i] = state[j + i];
            for (int i = 0; i < 5; i++)
                state[j + i] = t[i] ^ ((~t[(i + 1) % 5]) & t[(i + 2) % 5]);
        }

        state[0] ^= keccakf_rndc[round];
    }
}

void cleanroom_shake256(uint8_t *out, size_t outlen, const uint8_t *in, size_t inlen) {
    uint64_t state[25] = {0};
    uint8_t block[SHAKE256_RATE];
    size_t offset = 0;

    while (inlen >= SHAKE256_RATE) {
        for (int i = 0; i < SHAKE256_RATE / 8; i++) {
            uint64_t lane = 0;
            for (int b = 0; b < 8; b++) {
                lane |= ((uint64_t)in[offset + i * 8 + b]) << (8 * b);
            }
            state[i] ^= lane;
        }
        cleanroom_keccak_f1600(state);
        offset += SHAKE256_RATE;
        inlen -= SHAKE256_RATE;
    }

    memset(block, 0, sizeof(block));
    if (inlen > 0) {
        memcpy(block, in + offset, inlen);
    }
    block[inlen] ^= 0x1F;
    block[SHAKE256_RATE - 1] ^= 0x80;

    for (int i = 0; i < SHAKE256_RATE / 8; i++) {
        uint64_t lane = 0;
        for (int b = 0; b < 8; b++) {
            lane |= ((uint64_t)block[i * 8 + b]) << (8 * b);
        }
        state[i] ^= lane;
    }
    cleanroom_keccak_f1600(state);

    size_t out_pos = 0;
    while (outlen > 0) {
        uint8_t squeeze_buf[SHAKE256_RATE];
        for (int i = 0; i < SHAKE256_RATE / 8; i++) {
            for (int b = 0; b < 8; b++) {
                squeeze_buf[i * 8 + b] = (uint8_t)((state[i] >> (8 * b)) & 0xFF);
            }
        }
        size_t take = (outlen < SHAKE256_RATE) ? outlen : SHAKE256_RATE;
        memcpy(out + out_pos, squeeze_buf, take);
        out_pos += take;
        outlen -= take;
        if (outlen > 0) {
            cleanroom_keccak_f1600(state);
        }
    }
}

static void independent_compute_rejection_key(uint8_t ss_rej[SS_BYTES],
                                              const uint8_t sk[SK_BYTES],
                                              const uint8_t ct[CT_BYTES]) {
    uint8_t z_ct[Z_BYTES + CT_BYTES];
    memcpy(z_ct, sk + SK_BYTES - Z_BYTES, Z_BYTES);
    memcpy(z_ct + Z_BYTES, ct, CT_BYTES);
    cleanroom_shake256(ss_rej, SS_BYTES, z_ct, sizeof(z_ct));
}

int mlkem768_keypair(uint8_t *pk, uint8_t *sk);
int mlkem768_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int mlkem768_dec_monitored(uint8_t *ss, const uint8_t *ct, const uint8_t *sk, uint32_t *internal_status);

int randombytes(uint8_t *out, size_t outlen) {
    for (size_t i = 0; i < outlen; i++) out[i] = (uint8_t)(rand() & 0xFF);
    return 0;
}

static void bytes_to_hex(char *hex, const uint8_t *bytes, size_t len) {
    for (size_t i = 0; i < len; i++) {
        sprintf(hex + (i * 2), "%02x", bytes[i]);
    }
    hex[len * 2] = '\0';
}

int main(void) {
    FILE *fp = fopen("phase12_reproducibility_audit/production_reproduction_trials.csv", "w");
    if (!fp) {
        perror("Failed to open production_reproduction_trials.csv");
        return 1;
    }

    fprintf(fp, "trial_id,target_id,target_label,injection_function,source_location,"
                "fault_type,fault_value,persistence,trigger_condition,armed,actually_triggered,"
                "reset_operations,recovered_count,persistent_count,mismatch_count,internal_status,"
                "decaps_rc,matches_oracle_valid,matches_oracle_rejection,classification,classification_rule,"
                "actual_ss_hex,oracle_valid_hex,oracle_rej_hex\n");

    ntt_native_monitor_configure(NTT_NATIVE_MONITOR_RECOMPUTED_T, true, 0x7F);

    uint8_t pk[PK_BYTES], sk[SK_BYTES], ct[CT_BYTES];
    uint8_t ss_expected[SS_BYTES], ss_out[SS_BYTES], ss_rej_oracle[SS_BYTES];
    uint32_t status = 0;
    int trial_id = 0;

    char hex_actual[SS_BYTES * 2 + 1];
    char hex_oracle_valid[SS_BYTES * 2 + 1];
    char hex_oracle_rej[SS_BYTES * 2 + 1];

    /* =========================================================================
     * 1. Target F12: Clean Baseline Control (100 trials)
     * ========================================================================= */
    for (int t = 0; t < 100; t++) {
        srand(0x1337C0DE + t);
        mlkem768_keypair(pk, sk);
        mlkem768_enc(ct, ss_expected, pk);
        independent_compute_rejection_key(ss_rej_oracle, sk, ct);

        mlkem_fault_reset();
        ntt_native_monitor_reset();

        status = 0;
        int rc = mlkem768_dec_monitored(ss_out, ct, sk, &status);

        bool valid_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        bool rej_match = (memcmp(ss_out, ss_rej_oracle, SS_BYTES) == 0);

        bytes_to_hex(hex_actual, ss_out, SS_BYTES);
        bytes_to_hex(hex_oracle_valid, ss_expected, SS_BYTES);
        bytes_to_hex(hex_oracle_rej, ss_rej_oracle, SS_BYTES);

        const char *classification;
        const char *rule;
        if (valid_match && status == 0x5A5A5A5A && g_ntt_native_monitor.mismatch_count == 0 &&
            g_ntt_native_monitor.recovered_count == 0 && g_mlkem_fault.trigger_count == 0) {
            classification = "CLEAN_SUCCESS";
            rule = "valid_match && status==0x5A5A5A5A && mismatch==0 && rec==0 && trig==0";
        } else {
            classification = "INCONCLUSIVE";
            rule = "state_or_status_unexpected";
        }

        fprintf(fp, "%d,F12,CLEAN_BASELINE_CONTROL,none,none,NONE,0,false,none,0,0,"
                    "mlkem_fault_reset+ntt_native_monitor_reset,%u,%u,%u,0x%08X,%d,%d,%d,%s,%s,%s,%s,%s\n",
                trial_id++,
                g_ntt_native_monitor.recovered_count,
                g_ntt_native_monitor.persistent_count,
                g_ntt_native_monitor.mismatch_count,
                status, rc, valid_match, rej_match, classification, rule,
                hex_actual, hex_oracle_valid, hex_oracle_rej);
    }

    /* =========================================================================
     * 2. Target F4: Transient Software-Modeled Bit Flip (100 trials)
     * ========================================================================= */
    for (int t = 0; t < 100; t++) {
        srand(0x1337C0DE + t);
        mlkem768_keypair(pk, sk);
        mlkem768_enc(ct, ss_expected, pk);
        independent_compute_rejection_key(ss_rej_oracle, sk, ct);

        unsigned stage = (t % 7) + 1;
        unsigned b_idx = (t * 13) % 128;
        uint8_t bit = t % 16;

        mlkem_fault_reset();
        mlkem_fault_arm_mid_ntt_locus(stage, b_idx, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
        g_mlkem_fault.persistent = false;
        ntt_native_monitor_reset();

        status = 0;
        int rc = mlkem768_dec_monitored(ss_out, ct, sk, &status);

        bool valid_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        bool rej_match = (memcmp(ss_out, ss_rej_oracle, SS_BYTES) == 0);

        bytes_to_hex(hex_actual, ss_out, SS_BYTES);
        bytes_to_hex(hex_oracle_valid, ss_expected, SS_BYTES);
        bytes_to_hex(hex_oracle_rej, ss_rej_oracle, SS_BYTES);

        const char *classification;
        const char *rule;
        if (g_mlkem_fault.trigger_count == 0) {
            classification = "FAULT_NOT_TRIGGERED";
            rule = "trigger_count==0";
        } else if (valid_match && status == 0x5A5A5A5A && g_ntt_native_monitor.recovered_count > 0 &&
                   g_ntt_native_monitor.persistent_count == 0) {
            classification = "GENUINE_RECOVERY";
            rule = "trig>0 && valid_match && status==0x5A5A5A5A && rec>0 && pers==0";
        } else if (!valid_match && status == 0x5A5A5A5A) {
            classification = "SDC_ACCEPTED_INCORRECT";
            rule = "!valid_match && status==0x5A5A5A5A";
        } else if (rej_match && (status == 0xFFFFFFFF || status == 0xA5A5A5A5)) {
            classification = "SAFE_FAIL_STOP";
            rule = "rej_match && (status==0xFFFFFFFF || status==0xA5A5A5A5)";
        } else {
            classification = "INCONCLUSIVE";
            rule = "unmapped_state";
        }

        fprintf(fp, "%d,F4,TRANSIENT_SOFTWARE_BITFLIP,hook_mid_ntt_post_mul,mlkem_fault_hooks.c:250-265,"
                    "BIT_FLIP,%u,false,trigger_count==0_and_stage_bidx_match,1,%llu,"
                    "mlkem_fault_reset+ntt_native_monitor_reset,%u,%u,%u,0x%08X,%d,%d,%d,%s,%s,%s,%s,%s\n",
                trial_id++, bit,
                (unsigned long long)g_mlkem_fault.trigger_count,
                g_ntt_native_monitor.recovered_count,
                g_ntt_native_monitor.persistent_count,
                g_ntt_native_monitor.mismatch_count,
                status, rc, valid_match, rej_match, classification, rule,
                hex_actual, hex_oracle_valid, hex_oracle_rej);
    }

    /* =========================================================================
     * 3. Target F5A: Recurring Software-Modeled Bit Inversion (100 trials)
     * ========================================================================= */
    for (int t = 0; t < 100; t++) {
        srand(0x1337C0DE + t);
        mlkem768_keypair(pk, sk);
        mlkem768_enc(ct, ss_expected, pk);
        independent_compute_rejection_key(ss_rej_oracle, sk, ct);

        unsigned stage = (t % 7) + 1;
        unsigned b_idx = (t * 13) % 128;
        uint8_t bit = t % 16;

        mlkem_fault_reset();
        mlkem_fault_arm_mid_ntt_locus(stage, b_idx, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
        g_mlkem_fault.persistent = true;
        ntt_native_monitor_reset();

        status = 0;
        int rc = mlkem768_dec_monitored(ss_out, ct, sk, &status);

        bool valid_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        bool rej_match = (memcmp(ss_out, ss_rej_oracle, SS_BYTES) == 0);

        bytes_to_hex(hex_actual, ss_out, SS_BYTES);
        bytes_to_hex(hex_oracle_valid, ss_expected, SS_BYTES);
        bytes_to_hex(hex_oracle_rej, ss_rej_oracle, SS_BYTES);

        const char *classification;
        const char *rule;
        if (g_mlkem_fault.trigger_count == 0) {
            classification = "FAULT_NOT_TRIGGERED";
            rule = "trigger_count==0";
        } else if (rej_match && status == 0xFFFFFFFF && g_ntt_native_monitor.persistent_count > 0 && !valid_match) {
            classification = "SAFE_FAIL_STOP";
            rule = "trig>0 && rej_match && status==0xFFFFFFFF && pers>0 && !valid_match";
        } else if (!valid_match && status == 0x5A5A5A5A) {
            classification = "SDC_ACCEPTED_INCORRECT";
            rule = "!valid_match && status==0x5A5A5A5A";
        } else if (valid_match) {
            classification = "GENUINE_RECOVERY";
            rule = "valid_match";
        } else if (rej_match && status == 0xA5A5A5A5) {
            classification = "DOWNSTREAM_FO_REJECTION";
            rule = "rej_match && status==0xA5A5A5A5";
        } else {
            classification = "INCONCLUSIVE";
            rule = "unmapped_state";
        }

        fprintf(fp, "%d,F5A,RECURRING_SOFTWARE_BIT_INVERSION,hook_mid_ntt_post_mul,mlkem_fault_hooks.c:250-265,"
                    "BIT_FLIP,%u,true,always_on_stage_bidx_match,1,%llu,"
                    "mlkem_fault_reset+ntt_native_monitor_reset,%u,%u,%u,0x%08X,%d,%d,%d,%s,%s,%s,%s,%s\n",
                trial_id++, bit,
                (unsigned long long)g_mlkem_fault.trigger_count,
                g_ntt_native_monitor.recovered_count,
                g_ntt_native_monitor.persistent_count,
                g_ntt_native_monitor.mismatch_count,
                status, rc, valid_match, rej_match, classification, rule,
                hex_actual, hex_oracle_valid, hex_oracle_rej);
    }

    /* =========================================================================
     * 4. Target F5B: Software Force-Value Fault Model (100 trials)
     * ========================================================================= */
    for (int t = 0; t < 100; t++) {
        srand(0x1337C0DE + t);
        mlkem768_keypair(pk, sk);
        mlkem768_enc(ct, ss_expected, pk);
        independent_compute_rejection_key(ss_rej_oracle, sk, ct);

        unsigned stage = (t % 7) + 1;
        unsigned b_idx = (t * 13) % 128;

        mlkem_fault_reset();
        mlkem_fault_arm_mid_ntt_locus(stage, b_idx, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_FORCE_VALUE, 0, 0, 0);
        g_mlkem_fault.persistent = true;
        ntt_native_monitor_reset();

        status = 0;
        int rc = mlkem768_dec_monitored(ss_out, ct, sk, &status);

        bool valid_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
        bool rej_match = (memcmp(ss_out, ss_rej_oracle, SS_BYTES) == 0);

        bytes_to_hex(hex_actual, ss_out, SS_BYTES);
        bytes_to_hex(hex_oracle_valid, ss_expected, SS_BYTES);
        bytes_to_hex(hex_oracle_rej, ss_rej_oracle, SS_BYTES);

        const char *classification;
        const char *rule;
        if (g_mlkem_fault.trigger_count == 0) {
            classification = "FAULT_NOT_TRIGGERED";
            rule = "trigger_count==0";
        } else if (rej_match && status == 0xFFFFFFFF && g_ntt_native_monitor.persistent_count > 0 && !valid_match) {
            classification = "SAFE_FAIL_STOP";
            rule = "trig>0 && rej_match && status==0xFFFFFFFF && pers>0 && !valid_match";
        } else if (!valid_match && status == 0x5A5A5A5A) {
            classification = "SDC_ACCEPTED_INCORRECT";
            rule = "!valid_match && status==0x5A5A5A5A";
        } else if (valid_match) {
            classification = "GENUINE_RECOVERY";
            rule = "valid_match";
        } else if (rej_match && status == 0xA5A5A5A5) {
            classification = "DOWNSTREAM_FO_REJECTION";
            rule = "rej_match && status==0xA5A5A5A5";
        } else {
            classification = "INCONCLUSIVE";
            rule = "unmapped_state";
        }

        fprintf(fp, "%d,F5B,SOFTWARE_FORCE_VALUE_MODEL,hook_mid_ntt_post_mul,mlkem_fault_hooks.c:250-265,"
                    "FORCE_VALUE,0,true,always_on_stage_bidx_match,1,%llu,"
                    "mlkem_fault_reset+ntt_native_monitor_reset,%u,%u,%u,0x%08X,%d,%d,%d,%s,%s,%s,%s,%s\n",
                trial_id++,
                (unsigned long long)g_mlkem_fault.trigger_count,
                g_ntt_native_monitor.recovered_count,
                g_ntt_native_monitor.persistent_count,
                g_ntt_native_monitor.mismatch_count,
                status, rc, valid_match, rej_match, classification, rule,
                hex_actual, hex_oracle_valid, hex_oracle_rej);
    }

    fclose(fp);
    printf("Successfully executed and logged 400 production reproduction trials to production_reproduction_trials.csv\n");
    return 0;
}
