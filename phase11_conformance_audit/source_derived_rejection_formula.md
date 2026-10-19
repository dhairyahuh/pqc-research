# Audit of ML-KEM Implicit-Rejection Derivation

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Target:** ML-KEM-768 Decapsulation Implementation (`algorithms/source_ref/mlkem/`)  
**Standard:** NIST FIPS 203 (Module-Lattice-Based Key-Encapsulation Mechanism Standard)  

---

## 1. Executive Summary

Phase 10 employed the mathematical expression `SHAKE256(z || ct)` to calculate the expected implicit-rejection shared secret for ML-KEM-768 decapsulation. This audit re-examines that derivation from the raw source code of the implementation, compares it against the NIST FIPS 203 standard and the legacy CRYSTALS-Kyber Round 3 specification, and audits the independence of the output validation mechanism.

### Key Audit Findings:
1. **Mathematical Conformance:** The expression `SHAKE256(z || ct)` is **strictly correct and conformant** with FIPS 203 (Algorithm 21, Line 7 and Section 4.1, Eq. 4.4).
2. **Standard Transition from Kyber Round 3:** In CRYSTALS-Kyber Round 3 (the NIST PQC submission), the implicit-rejection derivation was defined as $K_{\text{rej}} = \text{SHAKE256}(z \parallel H(c), 32)$ where $H(c) = \text{SHA3-256}(c)$ (input length: 64 bytes). In FIPS 203, NIST eliminated the intermediate SHA3-256 hash of the ciphertext and specified $J(z \parallel c) = \text{SHAKE256}(z \parallel c, 32)$ directly over the full raw ciphertext (input length: 1,120 bytes for ML-KEM-768).
3. **Phase 10 Oracle Defect:** While Phase 10 used the correct mathematical formula, it evaluated that formula by calling `mlkem768_shake256(...)`—a function exported directly by the production object under test (`bin/obj/mlkem768_inst.o`). Consequently, Phase 10 did not provide an architecturally independent cryptographic oracle.
4. **Phase 11 Resolution:** Phase 11 deploys a clean-room, self-contained Keccak-f[1600] / SHAKE256 implementation that shares zero code, headers, or object symbols with the production library, validating the production rejection outputs bit-for-bit.

---

## 2. In-Depth Source Code Audit of Implicit Rejection

The decapsulation routine is implemented in `algorithms/source_ref/mlkem/src/kem.c` within the function `mlk_kem_dec_monitored(...)`.

### 2.1 Buffer Setup and Secret Key Decomposition
In `kem.c` (lines 410–416):
```c
  const uint8_t *pk = sk + MLKEM_INDCPA_SECRETKEYBYTES;
  MLK_ALLOC(buf, uint8_t, 2 * MLKEM_SYMBYTES, context);
  MLK_ALLOC(kr, uint8_t, 2 * MLKEM_SYMBYTES, context);
  MLK_ALLOC(tmp, uint8_t, MLKEM_SYMBYTES + MLKEM_INDCCA_CIPHERTEXTBYTES, context);
```
For ML-KEM-768:
- `MLKEM_SYMBYTES` = 32
- `MLKEM_SSBYTES` = 32
- `MLKEM_INDCPA_SECRETKEYBYTES` = 1,152
- `MLKEM_INDCPA_PUBLICKEYBYTES` = 1,184
- `MLKEM_INDCCA_CIPHERTEXTBYTES` = 1,088
- `MLKEM_INDCCA_SECRETKEYBYTES` = 2,400

The secret key layout in memory is:
- `sk[0 .. 1151]`: IND-CPA secret key ($d_K$)
- `sk[1152 .. 2335]`: IND-CPA public key ($e_K = \text{pk}$)
- `sk[2336 .. 2367]`: Public key hash $H(pk) = \text{SHA3-256}(pk)$
- `sk[2368 .. 2399]`: Implicit rejection seed ($z$)

### 2.2 Re-encryption and Comparison
In `kem.c` (lines 448–482):
```c
  /* Multitarget countermeasure for coins + contributory KEM */
  mlk_memcpy(buf + MLKEM_SYMBYTES,
             sk + MLKEM_INDCCA_SECRETKEYBYTES - 2 * MLKEM_SYMBYTES,
             MLKEM_SYMBYTES);
  mlk_hash_g(kr, buf, 2 * MLKEM_SYMBYTES);

  /* Recompute and compare ciphertext */
  ret = mlk_indcpa_enc(tmp, buf, pk, kr + MLKEM_SYMBYTES, context);
  fail = mlk_ct_memcmp(ct, tmp, MLKEM_INDCCA_CIPHERTEXTBYTES);
```
- `buf` contains $m' \parallel H(pk)$.
- `mlk_hash_g` computes $(K', r) = \text{SHA3-512}(m' \parallel H(pk))$.
- `mlk_indcpa_enc` re-encrypts $m'$ using coins $r$ to produce re-encrypted ciphertext $c'$ in `tmp`.
- Constant-time comparison `mlk_ct_memcmp(ct, tmp, 1088)` sets `fail = 0` if $c == c'$, or `fail != 0` if $c \neq c'$.

### 2.3 Dual-Rail Verification and Fail-Stop Override
In `kem.c` (lines 476–510):
```c
  /* Dual-rail verification: independent reverse comparison to detect predicate flips */
  uint8_t fail_chk = 0;
  for (size_t i = 0; i < MLKEM_INDCCA_CIPHERTEXTBYTES; i++) {
    fail_chk |= (ct[MLKEM_INDCCA_CIPHERTEXTBYTES - 1 - i] ^ tmp[MLKEM_INDCCA_CIPHERTEXTBYTES - 1 - i]);
  }
  fail_chk = mlk_ct_cmask_nonzero_u8(fail_chk);

#if defined(MLKEM_RESEARCH_FAULT_HOOKS)
  if (ntt_native_monitor_get_persistent_count() > 0 ||
      invntt_native_monitor_get_persistent_count() > 0)
  {
    fail = 0xFF; /* Force implicit rejection regardless of internal_status pointer */
    if (internal_status != NULL) {
      *internal_status = MLK_DECAPS_STATUS_FAULT;
    }
  }
  else
#endif
  if (fail != fail_chk) {
    fail = 0xFF;
    if (internal_status != NULL) {
      *internal_status = MLK_DECAPS_STATUS_FAULT;
    }
  } else if (internal_status != NULL) {
    uint32_t is_fail = ((uint32_t)fail | (0 - (uint32_t)fail)) >> 31;
    *internal_status = (1 - is_fail) * MLK_DECAPS_STATUS_SUCCESS +
                       is_fail * MLK_DECAPS_STATUS_REJECT;
  }
```

### 2.4 Derivation and Selection of the Implicit-Rejection Key
In `kem.c` (lines 512–520):
```c
  /* Compute rejection key */
  mlk_memcpy(tmp, sk + MLKEM_INDCCA_SECRETKEYBYTES - MLKEM_SYMBYTES,
             MLKEM_SYMBYTES);
  mlk_memcpy(tmp + MLKEM_SYMBYTES, ct, MLKEM_INDCCA_CIPHERTEXTBYTES);
  mlk_hash_j(ss, tmp, MLKEM_SYMBYTES + MLKEM_INDCCA_CIPHERTEXTBYTES);

  /* Copy true key to return buffer if fail is 0 */
  mlk_ct_cmov_zero(ss, kr, MLKEM_SYMBYTES, fail);
```
In `algorithms/source_ref/mlkem/src/symmetric.h` (lines 34–36):
```c
/* Hash function J, @[FIPS203, Section 4.1, Eq (4.4)] */
#define mlk_hash_j(OUT, IN, INBYTES) \
  mlk_shake256(OUT, MLKEM_SYMBYTES, IN, INBYTES)
```

The concrete steps performed by the production code are:
1. Load $z = sk[2400 - 32 \dots 2399]$ (32 bytes) into `tmp[0..31]`.
2. Load $ct$ (1,088 bytes) into `tmp[32..1119]`.
3. Call `mlk_hash_j(ss, tmp, 1120)`, which calls `mlk_shake256(ss, 32, tmp, 1120)`.
4. If `fail == 0` (ciphertext matched), conditionally copy $K' = kr[0..31]$ over `ss`.
5. If `fail != 0` (ciphertext mismatched or fail-stop triggered), retain `ss` untouched.

---

## 3. Comparative Formula Analysis

To avoid ambiguity, we record the three expressions explicitly:

| Designation | Exact Mathematical Formula | Input Byte Length | Status & Context |
| :--- | :--- | :---: | :--- |
| **Original Phase 10 Formula** | $\text{SHAKE256}(z \parallel ct)$ | 1,120 bytes | Mathematically correct for FIPS 203; implemented via production library helper `mlkem768_shake256`. |
| **Source-Derived Formula** | $\text{SHAKE256}(sk[2368..2399] \parallel ct, 32)$ | 1,120 bytes | Exact sequence executed by `kem.c:513-516` via macro `mlk_hash_j`. |
| **FIPS 203 Standard Formula** | $K_{\text{bar}} \leftarrow J(z \parallel c) = \text{SHAKE256}(z \parallel c, 32)$ | 1,120 bytes | Mandated by NIST FIPS 203 Algorithm 21 (Line 7) & Section 4.1 Eq. (4.4). |
| **Legacy Kyber Round 3 Formula** | $\text{SHAKE256}(z \parallel \text{SHA3-256}(c), 32)$ | 64 bytes | Specification in Round 3 NIST submission; obsolete in FIPS 203. |

### Evaluation:
The Phase 10 expression `SHAKE256(z || ct)` is **identical** to the FIPS 203 specification. It does **not** contain any mathematical error.

---

## 4. Oracle Independence Audit

### The Flaw in Phase 10:
In `phase10_corrected_reproduction/corrected_production_reproducer.c` (lines 24–29):
```c
static void compute_expected_rejection_key(uint8_t ss_rej[SS_BYTES], const uint8_t sk[SK_BYTES], const uint8_t ct[CT_BYTES]) {
    uint8_t z_ct[SS_BYTES + CT_BYTES];
    memcpy(z_ct, sk + SK_BYTES - SS_BYTES, SS_BYTES);
    memcpy(z_ct + SS_BYTES, ct, CT_BYTES);
    mlkem768_shake256(ss_rej, SS_BYTES, z_ct, SS_BYTES + CT_BYTES);
}
```
Line 28 calls `mlkem768_shake256`, which resolves to `bin/obj/mlkem768_inst.o`. Because the oracle and the library under test executed the exact same compiled machine instructions for Keccak-f[1600], any internal bug in the Keccak implementation (e.g. incorrect sponge padding, domain separation mismatch, or endianness error) would produce identical erroneous outputs in both `ss_out` and `ss_rej`, creating a false positive verification.

### Phase 11 Independent Clean-Room Implementation:
In `phase11_conformance_audit/independent_output_oracle.c`, the audit built a standalone, zero-dependency 24-round Keccak-f[1600] engine:
- Self-contained round constants `keccakf_rndc[24]` and rotation offsets `keccakf_rotc[24]`.
- Direct implementation of $\theta$, $\rho$, $\pi$, $\chi$, $\iota$ permutations.
- Independent state absorbing with FIPS 202 domain separation byte `0x1F` and padding `0x80`.
- Independent rate squeezing at rate $r = 136$ bytes.
- Validated bit-for-bit against Python 3.11 `hashlib.shake_256` reference vectors.
