# Mathematical Operation to Implementation Traceability Mapping

**Standard Reference:** NIST FIPS 203 (ML-KEM, August 2024)  
**Target Codebase:** `mlkem-native` (PQCA, Commit `fc269bc2d106`)  
**Document Version:** 1.0.0-PHASE1  
**Classification:** Engineering Specification  

---

## 1. Traceability Mapping Matrix

The following table provides an exhaustive 1-to-1 mapping connecting every mathematical operation in NIST FIPS 203 to its concrete C90 representation in `mlkem-native`, the corresponding research fault hook, and its current experimental validation status.

| Mathematical Operation | FIPS 203 Reference | Specification Equation | Concrete C Function | Source File | Core Data Structure | Research Fault Hook | Experimental Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **Polynomial Ring Addition** | §2.1, Eq. (2.1) | $c(X) = a(X) + b(X) \in R_q$ | `mlk_poly_add` | `algorithms/source_ref/mlkem/src/poly.c` | `mlk_poly` (`int16_t[256]`) | Post-op buffer mutation | Validated in Level 1 campaign |
| **Polynomial Subtraction** | §2.1, Alg. 14 | $c(X) = a(X) - b(X) \in R_q$ | `mlk_poly_sub` | `algorithms/source_ref/mlkem/src/poly.c` | `mlk_poly` (`int16_t[256]`) | Post-op buffer mutation | Validated in Level 1 campaign |
| **Forward NTT (Layer 1–7)** | §2.3, Alg. 8 | $\hat{f} = \text{NTT}(f)$ | `mlk_poly_ntt_c`, `mlk_ntt_layer`, `mlk_ntt_butterfly_block` | `algorithms/source_ref/mlkem/src/poly.c` | `mlk_poly` (`int16_t[256]`), twiddle table `mlk_zetas` | `hook_mid_ntt_butterfly` (inside Cooley-Tukey loop) | **Validated in Phase 4B** ($N=100$, Layers 1, 4, 7) |
| **Inverse NTT (iNTT)** | §2.3, Alg. 9 | $f = \text{NTT}^{-1}(\hat{f})$ | `mlk_poly_invntt_c`, `mlk_invntt_layer`, `mlk_invntt_butterfly_block` | `algorithms/source_ref/mlkem/src/poly.c` | `mlk_poly` (`int16_t[256]`), twiddle table `mlk_zetas` | Planned `hook_mid_invntt_butterfly` | Verified in KAT; mid-op hook planned for Phase 2 |
| **Vector Dot Product in NTT Domain** | §2.3, Alg. 10 | $\hat{\mathbf{u}} = \hat{\mathbf{A}}^T \hat{\mathbf{r}}$ | `mlk_polyvec_basemul_acc_montgomery_cached_c` | `algorithms/source_ref/mlkem/src/poly_k.c` | `mlk_polyvec` (`mlk_poly[K]`), accumulators `int32_t t[2]` | `hook_mid_polymul_accumulator` (inside $k$-loop) | **Validated in Phase 4B** ($N=100$, coords $k=0,1,2$) |
| **Base Multiplication (Degree-1 Poly)** | §2.3, Alg. 10 | $(a_0 + a_1 X)(b_0 + b_1 X) \pmod{X^2 - \zeta}$ | `mlk_poly_basemul_montgomery_cached` | `algorithms/source_ref/mlkem/src/poly.c` | Pairs of coefficients (`int16_t`), cache table `mlk_poly_mulcache` | Intermediate accumulator hook | **Validated in Phase 4B** |
| **Centered Binomial Noise Sampling** | §4.2.2, Alg. 6, 7 | $y = \sum_{i=0}^{\eta-1} (a_i - b_i)$ | `mlk_poly_cbd2`, `mlk_poly_cbd3` | `algorithms/source_ref/mlkem/src/sampling.c` | PRF byte buffer, 32-bit SWAR mask $d$, `int16_t[256]` | `hook_mid_cbd_popcount`, `hook_mid_cbd_sample` | **Validated in Phase 4B** ($N=100$, popcount & sample) |
| **Uniform Rejection Sampling for Matrix $\mathbf{A}$** | §4.2.1, Alg. 11 | $a_i \leftarrow \text{SampleNTT}(\text{XOF}(\rho, i, j))$ | `mlk_poly_rej_uniform` | `algorithms/source_ref/mlkem/src/sampling.c` | 168-byte SHAKE-128 squeeze buffer, `int16_t[256]` | Planned XOF squeeze buffer bit-flip | Verified in baseline KATs |
| **Scalar Compression $d=10$ ($d_u$)** | §4.2.3, Eq. (4.7) | $\lceil (2^{10}/q) \cdot x \rfloor \pmod{2^{10}}$ | `mlk_scalar_compress_d10` | `algorithms/source_ref/mlkem/src/compress.h` | 16-bit unsigned integer (`uint16_t`), scalar return | Arithmetic perturbation injection | Symbolically validated in Phase 1 |
| **Scalar Compression $d=4$ ($d_v$)** | §4.2.3, Eq. (4.7) | $\lceil (2^4/q) \cdot x \rfloor \pmod{2^4}$ | `mlk_scalar_compress_d4` | `algorithms/source_ref/mlkem/src/compress.h` | 8-bit unsigned integer (`uint8_t`), scalar return | Arithmetic perturbation injection | Symbolically validated in Phase 1 |
| **Vector Compression & Serialization** | §4.2.3, Alg. 4 | $c_1 = \text{ByteEncode}_{d_u}(\text{Compress}_{d_u}(\mathbf{u}))$ | `mlk_polyvec_compress_du` | `algorithms/source_ref/mlkem/src/compress.c` | Packed byte array `uint8_t[320 * K]` | Level 1 memory buffer bit-flip | Validated in Level 1 campaign |
| **Polynomial Compression & Serialization** | §4.2.3, Alg. 4 | $c_2 = \text{ByteEncode}_{d_v}(\text{Compress}_{d_v}(v))$ | `mlk_poly_compress_dv` | `algorithms/source_ref/mlkem/src/compress.c` | Packed byte array `uint8_t[128]` | Level 1 memory buffer bit-flip | Validated in Level 1 campaign |
| **Vector Decompression & Deserialization** | §4.2.3, Alg. 5 | $\mathbf{u}' = \text{Decompress}_{d_u}(\text{ByteDecode}_{d_u}(c_1))$ | `mlk_polyvec_decompress_du` | `algorithms/source_ref/mlkem/src/compress.c` | `uint8_t[320 * K]` $\to$ `mlk_polyvec` (`int16_t`) | Ciphertext bit-flip hook | Validated in Phase 4B |
| **Polynomial Decompression & Deserialization** | §4.2.3, Alg. 5 | $v' = \text{Decompress}_{d_v}(\text{ByteDecode}_{d_v}(c_2))$ | `mlk_poly_decompress_dv` | `algorithms/source_ref/mlkem/src/compress.c` | `uint8_t[128]` $\to$ `mlk_poly` (`int16_t`) | Ciphertext bit-flip hook | Validated in Phase 4B |
| **Message Polynomial Encoding** | §4.2.4, Alg. 2 | $\mu = \text{Decompress}_1(\text{ByteDecode}_1(m))$ | `mlk_poly_frommsg` | `algorithms/source_ref/mlkem/src/indcpa.c` | `uint8_t[32]` message $\to$ `mlk_poly` | Input buffer mutation | Validated in Level 1 campaign |
| **Message Polynomial Decoding** | §4.2.4, Alg. 3 | $m = \text{ByteEncode}_1(\text{Compress}_1(w))$ | `mlk_poly_tomsg` | `algorithms/source_ref/mlkem/src/indcpa.c` | `mlk_poly` $\to$ `uint8_t[32]` message | Decoding threshold injection | Validated in FO Direction B1 |
| **Fujisaki-Okamoto Re-Encryption Check** | §7.3, Alg. 17 | $c' \stackrel{?}{=} c$ | `mlk_ct_memcmp` | `algorithms/source_ref/mlkem/src/verify.c` | Byte arrays `uint8_t[MLKEM_INDCCA_CIPHERTEXTBYTES]` | Predicate inversion hook (`fail` $0 \to 1$ and $1 \to 0$) | **Validated in Phase 4B** ($N=1,000$ bidirectional) |
| **Implicit Rejection Key Selection** | §7.3, Alg. 17 | $K = \text{cmov}(K_{\text{cand}}, K_{\text{rej}}, \text{fail})$ | `mlk_ct_cmov_zero` | `algorithms/source_ref/mlkem/src/kem.c` | `uint8_t[32]` shared secret arrays | Predicate flag control | **Validated in Phase 4B** ($N=1,000$ sweeps) |

---

## 2. Variable and Parameter Cross-Reference

| Mathematical Variable | Description | Dimension in ML-KEM-768 | C Variable in `indcpa.c` / `kem.c` | Memory Size |
| :--- | :--- | :--- | :--- | :--- |
| $\mathbf{A}$ | Public matrix | $3 \times 3$ polynomials | `a[MLKEM_K][MLKEM_K]` | On-the-fly generated |
| $\mathbf{s}$ | Secret key vector | 3 polynomials (768 coeffs) | `skpv` (`mlk_polyvec`) | $3 \times 256 \times 2 = 1536$ bytes |
| $\mathbf{e}$ | Secret error vector | 3 polynomials (768 coeffs) | `e` (`mlk_polyvec`) | $3 \times 256 \times 2 = 1536$ bytes |
| $\mathbf{t}$ | Public key vector | 3 polynomials (768 coeffs) | `pkpv` (`mlk_polyvec`) | $3 \times 256 \times 2 = 1536$ bytes |
| $\mathbf{r}$ | Ephemeral randomness vector | 3 polynomials (768 coeffs) | `sp` (`mlk_polyvec`) | $3 \times 256 \times 2 = 1536$ bytes |
| $\mathbf{e}_1$ | Ephemeral error vector | 3 polynomials (768 coeffs) | `ep` (`mlk_polyvec`) | $3 \times 256 \times 2 = 1536$ bytes |
| $e_2$ | Ephemeral error scalar poly | 1 polynomial (256 coeffs) | `epp` (`mlk_poly`) | $256 \times 2 = 512$ bytes |
| $\mathbf{u}$ | Ciphertext vector part | 3 polynomials (768 coeffs) | `bp` (`mlk_polyvec`) | Compressed to 960 bytes |
| $v$ | Ciphertext scalar poly part | 1 polynomial (256 coeffs) | `v` (`mlk_poly`) | Compressed to 128 bytes |
| $m$ | Plaintext message | 256 bits | `m` (`uint8_t[32]`) | 32 bytes |
| $c$ | Complete ciphertext | $(c_1, c_2)$ | `ct` (`uint8_t[1088]`) | 1088 bytes |
| $K$ | Shared secret key | 256 bits | `ss` (`uint8_t[32]`) | 32 bytes |
| $z$ | Rejection seed | 256 bits | Packed in secret key buffer | 32 bytes |
