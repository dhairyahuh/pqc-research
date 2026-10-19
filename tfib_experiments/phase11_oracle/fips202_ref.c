#include "fips202_ref.h"
#include <string.h>

#define FOR(i, n) for (size_t i = 0; i < (size_t)(n); ++i)
#define ROTL64(x, y) (((x) << (y)) | ((x) >> (64 - (y))))

static const uint64_t RC[24] = {
    1ULL, 0x8082ULL, 0x800000000000808aULL, 0x8000000080008000ULL,
    0x808bULL, 0x80000001ULL, 0x8000000080008081ULL, 0x8000000000008009ULL,
    0x8aULL, 0x88ULL, 0x80008009ULL, 0x8000000aULL,
    0x8000808bULL, 0x800000000000008bULL, 0x8000000000008089ULL, 0x8000000000008003ULL,
    0x8000000000008002ULL, 0x8000000000000080ULL, 0x800aULL, 0x800000008000000aULL,
    0x8000000080008081ULL, 0x8000000000008080ULL, 0x80000001ULL, 0x8000000080008008ULL
};

static const int r_rot[24] = {
    1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 2, 14,
    27, 41, 56, 8, 25, 43, 62, 18, 39, 61, 20, 44
};

static const int pi_idx[24] = {
    10, 7, 11, 17, 18, 3, 5, 16, 8, 21, 24, 4,
    15, 23, 19, 13, 12, 2, 20, 14, 22, 9, 6, 1
};

static void keccak_f1600(uint64_t state[25]) {
    FOR(round, 24) {
        // Theta step
        uint64_t C[5], D[5];
        FOR(i, 5) C[i] = state[i] ^ state[i + 5] ^ state[i + 10] ^ state[i + 15] ^ state[i + 20];
        FOR(i, 5) D[i] = C[(i + 4) % 5] ^ ROTL64(C[(i + 1) % 5], 1);
        FOR(i, 25) state[i] ^= D[i % 5];

        // Rho and Pi steps
        uint64_t x = state[1];
        FOR(i, 24) {
            int j = pi_idx[i];
            uint64_t y = state[j];
            state[j] = ROTL64(x, r_rot[i]);
            x = y;
        }

        // Chi step
        FOR(j, 5) {
            uint64_t t[5];
            FOR(i, 5) t[i] = state[j * 5 + i];
            FOR(i, 5) state[j * 5 + i] = t[i] ^ ((~t[(i + 1) % 5]) & t[(i + 2) % 5]);
        }

        // Iota step
        state[0] ^= RC[round];
    }
}

void fips202_ref_shake256(uint8_t *out, size_t outlen, const uint8_t *in, size_t inlen) {
    uint64_t st[25] = {0};
    uint8_t *st_bytes = (uint8_t *)st;
    const size_t rate = 136; // 1088 bits for SHAKE-256

    // Absorb full rate-sized blocks
    while (inlen >= rate) {
        FOR(i, rate) st_bytes[i] ^= in[i];
        keccak_f1600(st);
        in += rate;
        inlen -= rate;
    }

    // Absorb remaining partial block and apply domain separator + multi-rate padding
    // For SHAKE-256, domain suffix is 1111 (0x1F with pad bit), final bit is 0x80
    FOR(i, inlen) st_bytes[i] ^= in[i];
    st_bytes[inlen] ^= 0x1F;
    st_bytes[rate - 1] ^= 0x80;
    keccak_f1600(st);

    // Squeeze output blocks
    while (outlen > 0) {
        size_t block = (outlen < rate) ? outlen : rate;
        memcpy(out, st_bytes, block);
        out += block;
        outlen -= block;
        if (outlen > 0) {
            keccak_f1600(st);
        }
    }
}
