#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <signal.h>
#include <unistd.h>
#include <mach/mach.h>
#include <mach/vm_region.h>
#include <mach/vm_map.h>

#define MLK_CONFIG_PARAMETER_SET 768
#include "references/test_vectors/mlkem_expected_kat.h"

#define MLKEM768_SK_BYTES 2400
#define MLKEM768_CT_BYTES 1088
#define MLKEM768_SS_BYTES 32
#define MLKEM768_Z_BYTES  32

/* Declarations from research build */
int mlkem768_keypair_derand(uint8_t *pk, uint8_t *sk, const uint8_t *coins);
int mlkem768_enc_derand(uint8_t *ct, uint8_t *ss, const uint8_t *pk, const uint8_t *coins);
int mlkem768_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);
int16_t *mlkem_research_get_zetas_mutable_ptr(void);
const int16_t *mlkem_research_get_zetas_table(void);

int randombytes(uint8_t *out, size_t outlen) {
    (void)out; (void)outlen;
    return 0;
}

/* Pre-computed golden table */
static const int16_t golden_zetas[128] = {
    -1044, -758,  -359,  -1517, 1493,  1422,  287,   202,  -171,  622,   1577,
    182,   962,   -1202, -1474, 1468,  573,   -1325, 264,  383,   -829,  1458,
    -1602, -130,  -681,  1017,  732,   608,   -1542, 411,  -205,  -1571, 1223,
    652,   -552,  1015,  -1293, 1491,  -282,  -1544, 516,  -8,    -320,  -666,
    -1618, -1162, 126,   1469,  -853,  -90,   -271,  830,  107,   -1421, -247,
    -951,  -398,  961,   -1508, -725,  448,   -1065, 677,  -1275, -1103, 430,
    555,   843,   -1251, 871,   1550,  105,   422,   587,  177,   -235,  -291,
    -460,  1574,  1653,  -246,  778,   1159,  -147,  -777, 1483,  -602,  1119,
    -1590, 644,   -872,  349,   418,   329,   -156,  -75,  817,   1097,  603,
    610,   1322,  -1285, -1465, 384,   -1215, -136,  1218, -1335, -874,  220,
    -1187, -1659, -1185, -1530, -1278, 794,   -1510, -854, -870,  478,   -108,
    -308,  996,   991,   958,   -1460, 1522,  1628
};

/* ======================================================================= */
/* INDEPENDENT FIPS 202 SHAKE256 IMPLEMENTATION (CLEAN ORACLE PROVENANCE)   */
/* Zero shared code with SUT / mlkem-native; strictly standard C11.        */
/* ======================================================================= */

#define ROL64(x, y) (((x) << (y)) | ((x) >> (64 - (y))))

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

static const int keccakf_rotc[24] = {
    1,  3,  6,  10, 15, 21, 28, 36, 45, 55, 2,  14,
    27, 41, 56, 8,  25, 43, 62, 18, 39, 61, 20, 44
};

static const int keccakf_piln[24] = {
    10, 7,  11, 17, 18, 3,  5,  16, 8,  21, 24, 4,
    15, 23, 19, 13, 12, 2,  20, 14, 22, 9,  6,  1
};

static void independent_keccak_f1600(uint64_t state[25]) {
    for (int round = 0; round < 24; round++) {
        uint64_t bc[5];
        /* Theta */
        for (int i = 0; i < 5; i++) {
            bc[i] = state[i] ^ state[i + 5] ^ state[i + 10] ^ state[i + 15] ^ state[i + 20];
        }
        for (int i = 0; i < 5; i++) {
            uint64_t d = bc[(i + 4) % 5] ^ ROL64(bc[(i + 1) % 5], 1);
            for (int j = 0; j < 25; j += 5) {
                state[j + i] ^= d;
            }
        }
        /* Rho & Pi */
        uint64_t t = state[1];
        for (int i = 0; i < 24; i++) {
            int j = keccakf_piln[i];
            bc[0] = state[j];
            state[j] = ROL64(t, keccakf_rotc[i]);
            t = bc[0];
        }
        /* Chi */
        for (int j = 0; j < 25; j += 5) {
            for (int i = 0; i < 5; i++) {
                bc[i] = state[j + i];
            }
            for (int i = 0; i < 5; i++) {
                state[j + i] ^= (~bc[(i + 1) % 5]) & bc[(i + 2) % 5];
            }
        }
        /* Iota */
        state[0] ^= keccakf_rndc[round];
    }
}

static void independent_shake256(const uint8_t *input, size_t inlen, uint8_t *output, size_t outlen) {
    const size_t rate = 136;
    uint8_t st_bytes[200];
    memset(st_bytes, 0, sizeof(st_bytes));

    size_t pos = 0;
    for (size_t i = 0; i < inlen; i++) {
        st_bytes[pos] ^= input[i];
        pos++;
        if (pos == rate) {
            uint64_t st_words[25];
            for (int w = 0; w < 25; w++) {
                st_words[w] = 0;
                for (int b = 0; b < 8; b++) {
                    st_words[w] |= ((uint64_t)st_bytes[w * 8 + b]) << (b * 8);
                }
            }
            independent_keccak_f1600(st_words);
            for (int w = 0; w < 25; w++) {
                for (int b = 0; b < 8; b++) {
                    st_bytes[w * 8 + b] = (uint8_t)(st_words[w] >> (b * 8));
                }
            }
            pos = 0;
        }
    }

    /* Padding pad10*1 with domain separator 0x1F for SHAKE256 */
    st_bytes[pos] ^= 0x1F;
    st_bytes[rate - 1] ^= 0x80;

    uint64_t st_words[25];
    for (int w = 0; w < 25; w++) {
        st_words[w] = 0;
        for (int b = 0; b < 8; b++) {
            st_words[w] |= ((uint64_t)st_bytes[w * 8 + b]) << (b * 8);
        }
    }
    independent_keccak_f1600(st_words);
    for (int w = 0; w < 25; w++) {
        for (int b = 0; b < 8; b++) {
            st_bytes[w * 8 + b] = (uint8_t)(st_words[w] >> (b * 8));
        }
    }

    /* Squeeze */
    size_t out_pos = 0;
    pos = 0;
    while (out_pos < outlen) {
        if (pos == rate) {
            for (int w = 0; w < 25; w++) {
                st_words[w] = 0;
                for (int b = 0; b < 8; b++) {
                    st_words[w] |= ((uint64_t)st_bytes[w * 8 + b]) << (b * 8);
                }
            }
            independent_keccak_f1600(st_words);
            for (int w = 0; w < 25; w++) {
                for (int b = 0; b < 8; b++) {
                    st_bytes[w * 8 + b] = (uint8_t)(st_words[w] >> (b * 8));
                }
            }
            pos = 0;
        }
        size_t take = outlen - out_pos;
        if (take > rate - pos) {
            take = rate - pos;
        }
        memcpy(output + out_pos, st_bytes + pos, take);
        out_pos += take;
        pos += take;
    }
}

/* NIST FIPS 202 Known-Answer Test: SHAKE256("", 32) */
static const uint8_t nist_shake256_empty_kat[32] = {
    0x46, 0xb9, 0xdd, 0x2b, 0x0b, 0xa8, 0x8d, 0x13, 0x23, 0x3b, 0x3f, 0xeb, 0x74, 0x3e, 0xeb, 0x24,
    0x3f, 0xcd, 0x52, 0xea, 0x62, 0xb8, 0x1b, 0x82, 0xb5, 0x0c, 0x27, 0x64, 0x6e, 0xd5, 0x76, 0x2f
};

/* Pre-computed golden rejection key for ML-KEM-768 KAT vector */
static const uint8_t expected_krej_kat[32] = {
    0xf0, 0xf0, 0xe1, 0x58, 0xed, 0x09, 0xb1, 0xc2, 0x73, 0x50, 0xa0, 0xac, 0x9e, 0xf3, 0xb4, 0xe1,
    0x42, 0xe7, 0xf5, 0x99, 0x68, 0x8c, 0x82, 0x89, 0x35, 0xf5, 0x04, 0x7e, 0x50, 0xf3, 0xdb, 0x03
};

/* Signal handling for hardware traps during pilot */
static volatile sig_atomic_t g_signal_received = 0;
static void handle_trap_signal(int sig) {
    g_signal_received = sig;
    const char msg[] = "\n!!! CRITICAL TRAP SIGNAL INTERCEPTED IN RUNNER !!!\n";
    write(STDERR_FILENO, msg, sizeof(msg) - 1);
    _exit(128 + sig);
}

typedef struct {
    int trial_id;
    int target_idx;
    uint16_t bit_mask;
    const char *desc;
    const char *mutation_status;
    const char *consumption_status;
    const char *crypto_endpoint;
    const char *restoration_status;
    uint8_t output_ss[32];
} trial_record_t;

/* Trial specifications (16 trials) */
typedef struct {
    int target_idx;
    uint16_t bit_mask;
    const char *desc;
    const char *expected_behavior;
} trial_spec_t;

static const trial_spec_t pilot_specs[16] = {
    { -1,  0x0000, "Trial 0: Baseline uncorrupted check",                          "Baseline golden key match" },
    {  0,  0x0001, "Trial 1: Index 0, LSB flip (Root/Unused twiddle)",             "Mathematically unused twiddle factor (Root)" },
    {  0,  0x0000, "Trial 2: Sham Control (Index 0, unprotect/write-0/reprotect)", "Sham control on index 0 (mask 0)" },
    {  1,  0x0001, "Trial 3: Index 1, LSB flip (Forward NTT Layer 1)",             "Active Layer 1 twiddle factor -> FO rejection key" },
    {  1,  0x0080, "Trial 4: Index 1, Mid-byte flip (Forward NTT Layer 1)",         "Active Layer 1 twiddle factor -> FO rejection key" },
    {  1,  0x8000, "Trial 5: Index 1, Sign-bit flip (Forward NTT Layer 1)",        "Active Layer 1 twiddle factor -> FO rejection key" },
    { 32,  0x0002, "Trial 6: Index 32, Bit 1 flip (Mid NTT Layer 6)",              "Active Layer 6 twiddle factor -> FO rejection key" },
    { 63,  0x0004, "Trial 7: Index 63, Bit 2 flip (Forward NTT Layer 7)",          "Active Layer 7 twiddle factor -> FO rejection key" },
    { 64,  0x0001, "Trial 8: Index 64, LSB flip (Mulcache Layer factor)",          "Active Mulcache factor -> FO rejection key" },
    { 64,  0x0400, "Trial 9: Index 64, Bit 10 flip (Mulcache Layer factor)",       "Active Mulcache factor -> FO rejection key" },
    { 95,  0x0001, "Trial 10: Index 95, LSB flip (Mulcache Mid factor)",           "Active Mulcache factor -> FO rejection key" },
    { 127, 0x0001, "Trial 11: Index 127, LSB flip (Basemul & InvNTT factor)",      "Active InvNTT/Basemul factor -> FO rejection key" },
    { 127, 0xFFFF, "Trial 12: Index 127, Word inversion (Basemul & InvNTT factor)", "Active InvNTT/Basemul factor -> FO rejection key" },
    { 64,  0x0000, "Trial 13: Sham Control on active index 64",                     "Sham control on active index 64 (mask 0)" },
    {  2,  0x0008, "Trial 14: Index 2, Bit 3 flip (Forward NTT Layer 2)",          "Active Layer 2 twiddle factor -> FO rejection key" },
    { -1,  0x0000, "Trial 15: Post-pilot baseline uncorrupted check",               "Post-pilot baseline golden key match" }
};

static void print_hex32(const uint8_t *data) {
    for (int i = 0; i < 32; i++) {
        printf("%02x", data[i]);
    }
}

/* Independent Oracle Endpoint Classifier */
static const char *oracle_classify_endpoint(
    int dec_rc,
    const uint8_t *ss_out,
    const uint8_t *golden_ss,
    const uint8_t *krej,
    int oracle_available)
{
    if (!oracle_available) {
        return "UNKNOWN";
    }
    if (dec_rc != 0) {
        return "NO_OUTPUT";
    }
    if (memcmp(ss_out, golden_ss, 32) == 0) {
        return "EXPECTED_OUTPUT";
    }
    if (memcmp(ss_out, krej, 32) == 0) {
        return "REJECTION";
    }
    /* Output differs from both golden and valid FIPS 203 rejection key */
    return "DIFFERENT_OUTPUT";
}

int main(int argc, char **argv) {
    /* Install emergency signal handlers */
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_trap_signal;
    sigaction(SIGBUS, &sa, NULL);
    sigaction(SIGSEGV, &sa, NULL);

    int check_oracle_only = (argc > 1 && (strcmp(argv[1], "--check-oracle") == 0 ||
                                          strcmp(argv[1], "--oracle-test") == 0 ||
                                          strcmp(argv[1], "--oracle-self-test") == 0));

    printf("=======================================================================\n");
    printf(" PHASE 15D: HARDENED PERSISTENT-TABLE FEASIBILITY RUNNER\n");
    printf(" Target: mlk_zetas_page (ML-KEM-768 relocated twiddle table)\n");
    printf("=======================================================================\n\n");

    /* ------------------------------------------------------------- */
    /* INDEPENDENT FIPS 203 ORACLE SELF-TEST & VALIDATION            */
    /* ------------------------------------------------------------- */
    printf("--- [ORACLE VALIDATION] Independent FIPS 202 SHAKE256 Self-Test ---\n");
    uint8_t empty_digest[32];
    independent_shake256((const uint8_t *)"", 0, empty_digest, 32);
    if (memcmp(empty_digest, nist_shake256_empty_kat, 32) != 0) {
        fprintf(stderr, "ORACLE FAIL: Independent SHAKE256 empty string failed NIST KAT.\n");
        return 1;
    }
    printf("  SHAKE256(\"\", 32) matches NIST FIPS 202 KAT:\n  ");
    print_hex32(empty_digest);
    printf("\n  Result: PASS\n\n");

    printf("--- [ORACLE DERIVATION] Independent FIPS 203 Rejection Key Derivation ---\n");
    /* In FIPS 203 Algorithm 17: K_bar = J(z || c, 32) = SHAKE256(z || c, 32) */
    /* z is the last 32 bytes of test_vector_sk; c is test_vector_ct (1088 bytes) */
    const uint8_t *test_z = test_vector_sk + MLKEM768_SK_BYTES - MLKEM768_Z_BYTES;
    size_t z_len = MLKEM768_Z_BYTES; /* 32 bytes */
    size_t ct_len = MLKEM768_CT_BYTES; /* 1088 bytes */
    size_t z_c_len = z_len + ct_len; /* 1120 bytes */

    uint8_t *z_c_buf = malloc(z_c_len);
    if (!z_c_buf) {
        fprintf(stderr, "ORACLE FAIL: Out of memory allocating oracle input buffer.\n");
        return 1;
    }
    memcpy(z_c_buf, test_z, z_len);
    memcpy(z_c_buf + z_len, test_vector_ct, ct_len);

    uint8_t derived_krej[32];
    independent_shake256(z_c_buf, z_c_len, derived_krej, 32);
    free(z_c_buf);

    printf("  Concatenation length: %zu bytes (32-byte z + 1088-byte ciphertext c)\n", z_c_len);
    printf("  Derived FIPS 203 K_rej: ");
    print_hex32(derived_krej);
    printf("\n  Expected KAT K_rej:    ");
    print_hex32(expected_krej_kat);
    printf("\n");

    if (memcmp(derived_krej, expected_krej_kat, 32) != 0) {
        fprintf(stderr, "ORACLE FAIL: Derived rejection key does not match golden test vector reference.\n");
        return 1;
    }
    printf("  Result: PASS (Independent Oracle Bit-Identical to Expected FIPS 203 KAT)\n\n");

    if (check_oracle_only) {
        printf(">>> Oracle check completed successfully (--check-oracle mode). Exiting without memory mutation. <<<\n");
        return 0;
    }

    /* ------------------------------------------------------------- */
    /* 1. MANDATORY PREFLIGHT CHECKS                                 */
    /* ------------------------------------------------------------- */
    printf("--- [PREFLIGHT 1/5] Symbol Resolution & Section Alignment ---\n");
    int16_t *table_ptr = mlkem_research_get_zetas_mutable_ptr();
    if (!table_ptr) {
        fprintf(stderr, "PREFLIGHT FAIL: mlkem_research_get_zetas_mutable_ptr() returned NULL.\n");
        return 1;
    }
    uintptr_t table_addr = (uintptr_t)table_ptr;
    vm_address_t page_addr = table_addr & ~(0x4000 - 1);
    printf("  Resolved symbol address: 0x%lx\n", (unsigned long)table_addr);
    printf("  Calculated page base:    0x%lx\n", (unsigned long)page_addr);
    if (table_addr != (uintptr_t)page_addr) {
        fprintf(stderr, "PREFLIGHT FAIL: table_addr is not 16KB aligned (offset: 0x%lx)\n",
                (unsigned long)(table_addr - page_addr));
        return 1;
    }
    printf("  Result: PASS (16KB Page-Aligned)\n\n");

    printf("--- [PREFLIGHT 2/5] Live VM Mapping Query via vm_region_64 ---\n");
    vm_address_t query_addr = page_addr;
    vm_size_t region_size = 0;
    vm_region_basic_info_data_64_t info;
    mach_msg_type_number_t count = VM_REGION_BASIC_INFO_COUNT_64;
    mach_port_t object_name = MACH_PORT_NULL;
    kern_return_t kr = vm_region_64(mach_task_self(), &query_addr, &region_size,
                                    VM_REGION_BASIC_INFO_64,
                                    (vm_region_info_t)&info, &count, &object_name);
    if (kr != KERN_SUCCESS) {
        fprintf(stderr, "PREFLIGHT FAIL: vm_region_64 returned code %d\n", kr);
        return 1;
    }
    printf("  Region mapped address:   0x%lx\n", (unsigned long)query_addr);
    printf("  Region mapped size:      0x%lx (%lu bytes)\n", (unsigned long)region_size, (unsigned long)region_size);
    printf("  Current protection:      %s%s%s (0x%x)\n",
           (info.protection & VM_PROT_READ) ? "r" : "-",
           (info.protection & VM_PROT_WRITE) ? "w" : "-",
           (info.protection & VM_PROT_EXECUTE) ? "x" : "-",
           info.protection);
    printf("  Maximum protection:      %s%s%s (0x%x)\n",
           (info.max_protection & VM_PROT_READ) ? "r" : "-",
           (info.max_protection & VM_PROT_WRITE) ? "w" : "-",
           (info.max_protection & VM_PROT_EXECUTE) ? "x" : "-",
           info.max_protection);

    if (query_addr != page_addr) {
        fprintf(stderr, "PREFLIGHT FAIL: Region address 0x%lx does not match expected page 0x%lx\n",
                (unsigned long)query_addr, (unsigned long)page_addr);
        return 1;
    }
    if (!(info.protection & VM_PROT_READ)) {
        fprintf(stderr, "PREFLIGHT FAIL: Page is not readable initially.\n");
        return 1;
    }
    if (!(info.max_protection & VM_PROT_WRITE)) {
        fprintf(stderr, "PREFLIGHT FAIL: maxprot does not allow write (0x%x).\n", info.max_protection);
        return 1;
    }
    printf("  Result: PASS (Darwin VM confirms __DATA_CONST permissions)\n\n");

    printf("--- [PREFLIGHT 3/5] Initial Table Integrity & Padding Canary Check ---\n");
    if (memcmp(table_ptr, golden_zetas, sizeof(golden_zetas)) != 0) {
        fprintf(stderr, "PREFLIGHT FAIL: Initial table does not match golden twiddle constants.\n");
        return 1;
    }
    /* Verify padding (16,128 bytes after the 256-byte table) */
    uint8_t *padding_ptr = (uint8_t *)(table_ptr + 128);
    size_t padding_len = 16384 - sizeof(golden_zetas);
    for (size_t i = 0; i < padding_len; i++) {
        if (padding_ptr[i] != 0) {
            fprintf(stderr, "PREFLIGHT FAIL: Non-zero byte detected in page padding at offset %zu (0x%x)\n",
                    i, padding_ptr[i]);
            return 1;
        }
    }
    printf("  Result: PASS (Table matches golden digest; 16,128 padding bytes clean)\n\n");

    printf("--- [PREFLIGHT 4/5] Dry-Run Protection Transition (Zero Write) ---\n");
    kr = vm_protect(mach_task_self(), page_addr, 0x4000, FALSE, VM_PROT_READ | VM_PROT_WRITE);
    if (kr != KERN_SUCCESS) {
        fprintf(stderr, "PREFLIGHT FAIL: vm_protect(RW) dry-run returned %d\n", kr);
        return 1;
    }
    /* Re-protect read-only immediately */
    kr = vm_protect(mach_task_self(), page_addr, 0x4000, FALSE, VM_PROT_READ);
    if (kr != KERN_SUCCESS) {
        fprintf(stderr, "PREFLIGHT FAIL: vm_protect(RO) dry-run returned %d\n", kr);
        return 1;
    }
    printf("  Result: PASS (vm_protect RW -> RO toggling verified without write)\n\n");

    printf("--- [PREFLIGHT 5/5] Preflight Clean Baseline Decapsulation Check ---\n");
    uint8_t ss_base[32];
    if (mlkem768_dec(ss_base, test_vector_ct, test_vector_sk) != 0) {
        fprintf(stderr, "PREFLIGHT FAIL: Baseline mlkem768_dec returned non-zero error.\n");
        return 1;
    }
    if (memcmp(ss_base, test_vector_ss, 32) != 0) {
        fprintf(stderr, "PREFLIGHT FAIL: Baseline shared secret does not match NIST KAT.\n");
        return 1;
    }
    printf("  Expected KAT SS: ");
    print_hex32(test_vector_ss);
    printf("\n  Computed KAT SS: ");
    print_hex32(ss_base);
    printf("\n  Result: PASS (Cryptographic baseline 100%% matches KAT)\n\n");

    printf(">>> PREFLIGHT VERDICT: GO (All preflights passed; ready for hardened trials) <<<\n\n");

    /* ------------------------------------------------------------- */
    /* 2. PREDECLARED 16-TRIAL HARDENED EXECUTION                    */
    /* ------------------------------------------------------------- */
    trial_record_t records[16];
    memset(records, 0, sizeof(records));
    for (int t = 0; t < 16; t++) {
        records[t].trial_id = t;
        records[t].target_idx = pilot_specs[t].target_idx;
        records[t].bit_mask = pilot_specs[t].bit_mask;
        records[t].desc = pilot_specs[t].desc;
    }

    int trials_recorded = 0;
    int abort_triggered = 0;

    for (int t = 0; t < 16; t++) {
        trials_recorded = t + 1;
        printf("-----------------------------------------------------------------------\n");
        printf("--- [DIAGNOSTIC TRIAL %d/16] %s ---\n", t, pilot_specs[t].desc);

        /* Complete Target Bounds Check before calculating addresses or unprotecting */
        if (pilot_specs[t].target_idx < -1 || pilot_specs[t].target_idx >= 128) {
            fprintf(stderr, "BOUNDS CHECK FAIL: Invalid target_idx %d in trial %d (valid targets: -1 for baseline, 0..127 for twiddles). Failing closed.\n",
                    pilot_specs[t].target_idx, t);
            records[t].mutation_status = "REJECTED";
            records[t].consumption_status = "VERIFIED_NOT_CONSUMED";
            records[t].crypto_endpoint = "NOT_RUN";
            records[t].restoration_status = "NOT_RUN_INVALID_TARGET";
            continue;
        }

        int is_baseline = (pilot_specs[t].target_idx == -1);
        int is_mutation = (pilot_specs[t].target_idx >= 0 && pilot_specs[t].bit_mask != 0);
        int is_sham = (pilot_specs[t].target_idx >= 0 && pilot_specs[t].bit_mask == 0);

        if (is_mutation || is_sham) {
            int idx = pilot_specs[t].target_idx;
            uint16_t mask = pilot_specs[t].bit_mask;
            int16_t orig_val = golden_zetas[idx];
            /* Standard-conformant two's-complement arithmetic conversion */
            int16_t target_val = (int16_t)((uint16_t)orig_val ^ mask);

            int page_is_rw = 0;
            int mutation_applied = 0;

            /* Step 1: Unprotect to RW */
            kr = vm_protect(mach_task_self(), page_addr, 0x4000, FALSE, VM_PROT_READ | VM_PROT_WRITE);
            if (kr != KERN_SUCCESS) {
                records[t].mutation_status = "REJECTED";
                records[t].consumption_status = "UNKNOWN";
                records[t].crypto_endpoint = "NOT_RUN";
                records[t].restoration_status = "UNKNOWN";
                fprintf(stderr, "ABORT in trial %d: vm_protect(RW) failed with %d\n", t, kr);
                abort_triggered = 1;
                break;
            }
            page_is_rw = 1;

            /* Step 2: Write mutated value (or sham write) */
            volatile int16_t *vtable = (volatile int16_t *)table_ptr;
            vtable[idx] = target_val;

            /* Step 3: Immediate read-back */
            int16_t readback_val = vtable[idx];
            if (readback_val == target_val) {
                records[t].mutation_status = "APPLIED";
                mutation_applied = 1;
            } else {
                records[t].mutation_status = "UNKNOWN";
                fprintf(stderr, "CRITICAL: Read-back mismatch in trial %d (expected 0x%04x, got 0x%04x)\n",
                        t, (uint16_t)target_val, (uint16_t)readback_val);
            }

            /* Step 4: Re-protect to RO */
            kr = vm_protect(mach_task_self(), page_addr, 0x4000, FALSE, VM_PROT_READ);
            if (kr == KERN_SUCCESS) {
                page_is_rw = 0;
            } else {
                fprintf(stderr, "CRITICAL: vm_protect(RO) post-mutation failed with %d in trial %d\n", kr, t);
                /* Do NOT break: proceed straight to structured cleanup */
            }

            /* Step 5: Execute decapsulation only if page is safely protected and mutation verified */
            uint8_t ss_out[32];
            memset(ss_out, 0, sizeof(ss_out));
            int dec_rc = -1;

            if (!page_is_rw && mutation_applied) {
                dec_rc = mlkem768_dec(ss_out, test_vector_ct, test_vector_sk);
                memcpy(records[t].output_ss, ss_out, 32);

                /* Independent Oracle Classification */
                records[t].crypto_endpoint = oracle_classify_endpoint(
                    dec_rc, ss_out, test_vector_ss, derived_krej, 1);

                if (strcmp(records[t].crypto_endpoint, "EXPECTED_OUTPUT") == 0) {
                    records[t].consumption_status = "VERIFIED_NOT_CONSUMED";
                } else if (strcmp(records[t].crypto_endpoint, "REJECTION") == 0 ||
                           strcmp(records[t].crypto_endpoint, "DIFFERENT_OUTPUT") == 0 ||
                           strcmp(records[t].crypto_endpoint, "NO_OUTPUT") == 0) {
                    records[t].consumption_status = "VERIFIED_CONSUMED";
                } else {
                    records[t].consumption_status = "UNKNOWN";
                }
            } else {
                records[t].crypto_endpoint = "NOT_RUN";
                records[t].consumption_status = "UNKNOWN";
            }

            printf("  Injected value: 0x%04x (orig: 0x%04x, mask: 0x%04x)\n",
                   (uint16_t)target_val, (uint16_t)orig_val, mask);
            printf("  Output SS:      ");
            print_hex32(ss_out);
            printf(" [%s]\n", records[t].crypto_endpoint);

            /* ============================================================== */
            /* STRUCTURED MANDATORY CLEANUP PATH                              */
            /* ============================================================== */
            int cleanup_passed = 1;

            /* Cleanup Step 1: Unprotect to restore entry (if still RO) */
            if (!page_is_rw) {
                kr = vm_protect(mach_task_self(), page_addr, 0x4000, FALSE, VM_PROT_READ | VM_PROT_WRITE);
                if (kr != KERN_SUCCESS) {
                    cleanup_passed = 0;
                    fprintf(stderr, "CLEANUP FAIL: Failed to unprotect for restore in trial %d (kr=%d)\n", t, kr);
                } else {
                    page_is_rw = 1;
                }
            }

            /* Cleanup Step 2: Restore original entry & verify value */
            if (page_is_rw) {
                vtable[idx] = orig_val;
                int16_t restored_val = vtable[idx];
                if (restored_val != orig_val) {
                    cleanup_passed = 0;
                    fprintf(stderr, "CLEANUP FAIL: Restored read-back mismatch in trial %d (expected 0x%04x, got 0x%04x)\n",
                            t, (uint16_t)orig_val, (uint16_t)restored_val);
                }
            }

            /* Cleanup Step 3: Reprotect page to RO */
            kr = vm_protect(mach_task_self(), page_addr, 0x4000, FALSE, VM_PROT_READ);
            if (kr != KERN_SUCCESS) {
                cleanup_passed = 0;
                fprintf(stderr, "CLEANUP FAIL: vm_protect(RO) failed post-restore in trial %d (kr=%d)\n", t, kr);
            } else {
                page_is_rw = 0;
            }

            /* Cleanup Step 4: Verify live protection state via vm_region_64 */
            vm_address_t v_addr = page_addr;
            vm_size_t v_size = 0;
            vm_region_basic_info_data_64_t v_info;
            mach_msg_type_number_t v_cnt = VM_REGION_BASIC_INFO_COUNT_64;
            mach_port_t v_port = MACH_PORT_NULL;
            kr = vm_region_64(mach_task_self(), &v_addr, &v_size,
                              VM_REGION_BASIC_INFO_64,
                              (vm_region_info_t)&v_info, &v_cnt, &v_port);
            if (kr != KERN_SUCCESS || !(v_info.protection & VM_PROT_READ) || (v_info.protection & VM_PROT_WRITE)) {
                cleanup_passed = 0;
                fprintf(stderr, "CLEANUP FAIL: Live VM query indicates page is not read-only in trial %d (prot=0x%x)\n",
                        t, v_info.protection);
            }

            /* Cleanup Step 5: Verify table & padding canaries */
            int restore_ok = (memcmp(table_ptr, golden_zetas, sizeof(golden_zetas)) == 0);
            int pad_ok = 1;
            for (size_t i = 0; i < padding_len; i++) {
                if (padding_ptr[i] != 0) { pad_ok = 0; break; }
            }
            if (!restore_ok || !pad_ok) {
                cleanup_passed = 0;
                fprintf(stderr, "CLEANUP FAIL: Table or padding integrity check failed in trial %d (table=%d, pad=%d)\n",
                        t, restore_ok, pad_ok);
            }

            /* Cleanup Step 6: Post-trial baseline decapsulation recheck ONLY when safe */
            int ss_recheck_ok = 0;
            if (cleanup_passed) {
                uint8_t ss_recheck[32];
                int recheck_rc = mlkem768_dec(ss_recheck, test_vector_ct, test_vector_sk);
                ss_recheck_ok = (recheck_rc == 0 && memcmp(ss_recheck, test_vector_ss, 32) == 0);
                if (!ss_recheck_ok) {
                    cleanup_passed = 0;
                    fprintf(stderr, "CLEANUP FAIL: Baseline KAT shared secret recheck failed in trial %d\n", t);
                }
            }

            if (cleanup_passed && ss_recheck_ok) {
                records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED";
                printf("  Restoration:    PASS (Table restored, permissions RO, padding clean, baseline reproduced)\n");
            } else {
                records[t].restoration_status = "RESTORATION_FAILED";
                fprintf(stderr, "CRITICAL EMERGENCY: Cleanup failed in trial %d. Terminating runner immediately.\n", t);
                abort_triggered = 1;
                break;
            }

        } else if (is_baseline) {
            /* Baseline run (Trial 0 or Trial 15: strictly target_idx == -1) */
            records[t].mutation_status = "NOT_ATTEMPTED";
            records[t].consumption_status = "VERIFIED_NOT_CONSUMED";

            uint8_t ss_out[32];
            int dec_rc = mlkem768_dec(ss_out, test_vector_ct, test_vector_sk);
            memcpy(records[t].output_ss, ss_out, 32);

            records[t].crypto_endpoint = oracle_classify_endpoint(
                dec_rc, ss_out, test_vector_ss, derived_krej, 1);

            int table_ok = (memcmp(table_ptr, golden_zetas, sizeof(golden_zetas)) == 0);
            if (table_ok && strcmp(records[t].crypto_endpoint, "EXPECTED_OUTPUT") == 0) {
                records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED";
            } else {
                records[t].restoration_status = "RESTORATION_FAILED";
                fprintf(stderr, "CRITICAL EMERGENCY: Baseline integrity failure in trial %d. Terminating runner immediately.\n", t);
                abort_triggered = 1;
                break;
            }

            printf("  Output SS:      ");
            print_hex32(ss_out);
            printf(" [%s]\n", records[t].crypto_endpoint);
            printf("  Restoration:    PASS (Baseline intact)\n");
        } else {
            /* Defensive unreachable branch: fail closed */
            records[t].mutation_status = "REJECTED";
            records[t].consumption_status = "VERIFIED_NOT_CONSUMED";
            records[t].crypto_endpoint = "NOT_RUN";
            records[t].restoration_status = "NOT_RUN_INVALID_TARGET";
            continue;
        }
    }

    /* ------------------------------------------------------------- */
    /* 3. GENERATE AUTHORITATIVE 9-COLUMN TRIAL LEDGER (CSV FORMAT)  */
    /* ------------------------------------------------------------- */
    printf("\n=======================================================================\n");
    if (abort_triggered || trials_recorded < 16) {
        printf(" PARTIAL TRIAL LEDGER (ABORTED RUN - %d/16 TRIALS RECORDED)\n", trials_recorded);
    } else {
        printf(" AUTHORITATIVE TRIAL LEDGER (CSV FORMAT - 9 COLUMNS)\n");
    }
    printf("=======================================================================\n");
    printf("trial_id,target_idx,bit_mask,mutation_status,consumption_status,crypto_endpoint,restoration_status,output_ss,expected_behavior\n");
    for (int t = 0; t < trials_recorded; t++) {
        char ss_hex[65];
        for (int b = 0; b < 32; b++) {
            sprintf(ss_hex + b * 2, "%02x", records[t].output_ss[b]);
        }
        ss_hex[64] = '\0';

        printf("%d,%d,0x%04x,%s,%s,%s,%s,%s,%s\n",
               records[t].trial_id,
               records[t].target_idx,
               records[t].bit_mask,
               records[t].mutation_status ? records[t].mutation_status : "UNKNOWN",
               records[t].consumption_status ? records[t].consumption_status : "UNKNOWN",
               records[t].crypto_endpoint ? records[t].crypto_endpoint : "UNKNOWN",
               records[t].restoration_status ? records[t].restoration_status : "UNKNOWN",
               ss_hex,
               pilot_specs[t].expected_behavior ? pilot_specs[t].expected_behavior : "UNKNOWN");
    }

    if (abort_triggered || trials_recorded < 16) {
        printf("\n>>> PILOT RUN ABORTED: INCOMPLETE RUN (%d/16 TRIALS PROCESSED) (STATUS: FAILED) <<<\n", trials_recorded);
        return 1;
    }

    printf("\n>>> PILOT RUN COMPLETE: 16/16 TRIALS PROCESSED (STATUS: SUCCESS) <<<\n");
    return 0;
}
