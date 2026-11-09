#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>

#if defined(__APPLE__)
#include <stdlib.h>
#else
#include <sys/random.h>
#endif

// Robust cross-platform CSPRNG randombytes
int randombytes(uint8_t *out, size_t outlen) {
#if defined(__APPLE__)
    arc4random_buf(out, outlen);
    return 0;
#else
    ssize_t ret = getrandom(out, outlen, 0);
    if (ret == (ssize_t)outlen) return 0;
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd < 0) return -1;
    ssize_t read_bytes = read(fd, out, outlen);
    close(fd);
    return (read_bytes == (ssize_t)outlen) ? 0 : -1;
#endif
}

// Declarations from mlkem768_instrumented.o
int mlkem_keypair(uint8_t *pk, uint8_t *sk);
int mlkem_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int mlkem_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);
int mlkem_dec_monitored(uint8_t *ss, const uint8_t *ct, const uint8_t *sk, uint32_t *internal_status, void *ctx);

// Declarations from mldsa65.o
int mldsa_keypair(uint8_t *pk, uint8_t *sk);
int mldsa_signature(uint8_t *sig, const uint8_t *m, size_t mlen, const uint8_t *ctx, size_t ctxlen, const uint8_t *sk);
int mldsa_verify(const uint8_t *sig, const uint8_t *m, size_t mlen, const uint8_t *ctx, size_t ctxlen, const uint8_t *pk);

// FIPS 203 / 204 Parameter Constants
#define KEM768_PK_BYTES 1184
#define KEM768_SK_BYTES 2400
#define KEM768_CT_BYTES 1088
#define KEM768_SS_BYTES 32

#define DSA65_PK_BYTES 1952
#define DSA65_SK_BYTES 4032
#define DSA65_SIG_BYTES 3309

// Internal Monitoring Status Codes
#define ASTRA_DECAPS_STATUS_SUCCESS 0x5A5A5A5AU
#define ASTRA_DECAPS_STATUS_REJECT  0xA5A5A5A5U
#define ASTRA_DECAPS_STATUS_FAULT   0xDEADBEEFU

// Exported C Bridge API
int astra_kem768_keypair(uint8_t *pk, uint8_t *sk) {
    if (!pk || !sk) return -1;
    return mlkem_keypair(pk, sk);
}

int astra_kem768_encaps(uint8_t *ct, uint8_t *ss, const uint8_t *pk) {
    if (!ct || !ss || !pk) return -1;
    return mlkem_enc(ct, ss, pk);
}

int astra_kem768_decaps_monitored(uint8_t *ss, const uint8_t *ct, const uint8_t *sk, uint32_t *status) {
    if (!ss || !ct || !sk) return -1;
    return mlkem_dec_monitored(ss, ct, sk, status, NULL);
}

int astra_dsa65_keypair(uint8_t *pk, uint8_t *sk) {
    if (!pk || !sk) return -1;
    return mldsa_keypair(pk, sk);
}

int astra_dsa65_sign(uint8_t *sig, size_t *sig_len, const uint8_t *msg, size_t msg_len, const uint8_t *sk) {
    if (!sig || !sig_len || !msg || !sk) return -1;
    if (mldsa_signature(sig, msg, msg_len, NULL, 0, sk) == 0) {
        *sig_len = DSA65_SIG_BYTES;
        return 0;
    }
    return -1;
}

int astra_dsa65_verify(const uint8_t *sig, size_t sig_len, const uint8_t *msg, size_t msg_len, const uint8_t *pk) {
    if (!sig || !msg || !pk) return -1;
    if (sig_len != DSA65_SIG_BYTES) return -1;
    return mldsa_verify(sig, msg, msg_len, NULL, 0, pk);
}

int astra_crypto_get_sizes(size_t *kem_pk, size_t *kem_sk, size_t *kem_ct, size_t *kem_ss,
                           size_t *dsa_pk, size_t *dsa_sk, size_t *dsa_sig) {
    if (kem_pk) *kem_pk = KEM768_PK_BYTES;
    if (kem_sk) *kem_sk = KEM768_SK_BYTES;
    if (kem_ct) *kem_ct = KEM768_CT_BYTES;
    if (kem_ss) *kem_ss = KEM768_SS_BYTES;
    if (dsa_pk) *dsa_pk = DSA65_PK_BYTES;
    if (dsa_sk) *dsa_sk = DSA65_SK_BYTES;
    if (dsa_sig) *dsa_sig = DSA65_SIG_BYTES;
    return 0;
}
