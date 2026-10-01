# Mathematical Symbol Table & Implementation Representation Guide

**Standard References:** NIST FIPS 203 (ML-KEM)  
**Document Version:** 1.0.0-PHASE1  
**Classification:** Scientific Reference  

---

## 1. Primary Mathematical Symbols

| Symbol | Mathematical Meaning | Formal Domain | Implementation Type / Struct (`mlkem-native`) | FIPS 203 Reference | Spec vs. Implementation Notation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| $n$ | Polynomial ring degree | $n = 256$ | Macro `MLKEM_N` (`256`) | §2.1, Table 1 | Identical |
| $q$ | Prime modulus | $q = 3329$ | Macro `MLKEM_Q` (`3329`) | §2.1, Table 1 | Identical |
| $\mathbb{Z}_q$ | Finite field / integers modulo $q$ | $\{0, 1, \dots, q-1\}$ | `int16_t` in canonical range $[0, 3328]$ or centered $[-\lfloor q/2 \rfloor, \lfloor q/2 \rfloor]$ | §2.1 | Spec uses $[0, q-1]$; C code often uses signed representations |
| $R_q$ | Quotient polynomial ring | $\mathbb{Z}_q[X]/(X^n+1)$ | `mlk_poly` (`struct { int16_t coeffs[256]; }`) | §2.1, Eq. (2.1) | Identical degree and modulus |
| $k$ | Module rank (vector dimension) | $k \in \{2, 3, 4\}$ | Macro `MLKEM_K` (2 for 512, 3 for 768, 4 for 1024) | Table 2 | Identical |
| $R_q^k$ | Module of rank $k$ over $R_q$ | Vector of $k$ polynomials | `mlk_polyvec` (`struct { mlk_poly vec[MLKEM_K]; }`) | §2.1 | Vector of polynomial structs |
| $R_q^{k \times k}$ | Matrix of polynomials over $R_q$ | $k \times k$ matrix | `mlk_polyvec[MLKEM_K]` or generated on-the-fly via XOF | §2.1 | Generated block-by-block |
| $\mathbf{A}, \hat{\mathbf{A}}$ | Public matrix in standard / NTT domain | $\mathbf{A} \in R_q^{k \times k}$ | Generated row-by-row via `mlk_polyvec_gen_matrix` using SHAKE-128 | Alg. 12, 13 | Spec generates $\hat{\mathbf{A}}$ directly in NTT domain |
| $\mathbf{s}, \hat{\mathbf{s}}$ | Secret key vector in standard / NTT domain | $\mathbf{s} \in R_q^k$ | `mlk_polyvec` stored in private key | Alg. 12, 15 | Stored in NTT domain in secret key |
| $\mathbf{e}, \hat{\mathbf{e}}$ | Error / noise vector in standard / NTT domain | $\mathbf{e} \in R_q^k$ | Sampled via `mlk_poly_cbd2` or `mlk_poly_cbd3` | Alg. 12 | Sampled from PRF byte stream |
| $\mathbf{t}, \hat{\mathbf{t}}$ | Public key polynomial vector | $\mathbf{t} = \mathbf{A}\mathbf{s} + \mathbf{e} \in R_q^k$ | `mlk_polyvec` packed in `pk` | Alg. 12 | Encoded via `mlk_polyvec_tobytes` |
| $\zeta$ | Primitive 256th root of unity modulo $q$ | $\zeta = 17 \pmod{3329}$ ($\zeta^{128} \equiv -1$) | Stored in table `mlk_zetas[128]` (bit-reversed powers) | §2.3, Table 3 | Code uses bit-reversed Montgomery representation |
| $R$ | Montgomery reduction constant | $R = 2^{16} = 65536 \equiv 2285 \pmod q$ | Implicit in `mlk_montgomery_reduce` | N/A (Implementation) | Implementation-specific optimization |
| $QINV$ | Modulo inverse $q^{-1} \pmod{2^{16}}$ | $QINV = 62209$ | Macro/constant `QINV = 62209` in `poly.h` | N/A (Implementation) | Implementation-specific optimization |
| $\eta_1$ | Noise parameter for key generation | $\eta_1 \in \{2, 3\}$ | Macro `MLKEM_ETA1` | Table 2 | Identical |
| $\eta_2$ | Noise parameter for encryption | $\eta_2 = 2$ | Macro `MLKEM_ETA2` | Table 2 | Identical |
| $d_u$ | Ciphertext vector compression bits | $d_u \in \{10, 11\}$ | Macro `MLKEM_DU` | Table 2 | Identical |
| $d_v$ | Ciphertext polynomial compression bits | $d_v \in \{4, 5\}$ | Macro `MLKEM_DV` | Table 2 | Identical |
| $\mathbf{u}$ | Ciphertext vector component | $\mathbf{u} = \mathbf{A}^T \mathbf{r} + \mathbf{e}_1 \in R_q^k$ | `mlk_polyvec` compressed to $c_1$ | Alg. 13, 14 | Compressed via `mlk_polyvec_compress_du` |
| $v$ | Ciphertext polynomial component | $v = \mathbf{t}^T \mathbf{r} + e_2 + \mu \in R_q$ | `mlk_poly` compressed to $c_2$ | Alg. 13, 14 | Compressed via `mlk_poly_compress_dv` |
| $m, \mu$ | 32-byte message / decoded polynomial | $m \in \{0, 1\}^{256}, \mu \in R_q$ | `uint8_t[32]` / `mlk_poly` via `mlk_poly_frommsg` | Alg. 13, 14 | Spec maps bits to $\{0, \lfloor q/2 \rfloor\}$ |
| $c = (c_1, c_2)$ | Ciphertext byte array | $\{0, 1\}^{32(d_u k + d_v)}$ | Packed byte array in `ct` | Alg. 13 | Byte-encoded compressed coefficients |
| $K_{valid}$ | Legitimate shared secret | $\{0, 1\}^{256}$ (32 bytes) | `uint8_t[32]` derived from $\text{Hash}_G(m \parallel H(pk))$ | Alg. 16, 17 | Output of successful decapsulation |
| $K_{rej}$ | Implicit rejection shared secret | $\{0, 1\}^{256}$ (32 bytes) | `uint8_t[32]` derived from $\text{Hash}_J(z \parallel c)$ | Alg. 17 | Output of failed re-encryption check |
| $K_{cand}$ | Candidate shared secret under fault | $\{0, 1\}^{256}$ (32 bytes) | `uint8_t[32]` derived from $\text{Hash}_G(m' \parallel H(pk))$ | Alg. 17 under FO bypass | Out-of-sync key produced when FO check is forced to 0 on corrupt $c^*$ |

---

## 2. Fault Analysis Notation

| Symbol | Meaning | Mathematical Domain | Description |
| :--- | :--- | :--- | :--- |
| $\Delta$ | Additive arithmetic fault perturbation | $\mathbb{Z}$ or $\mathbb{Z}_q$ | Added to a coefficient: $x' = x + \Delta$ |
| $b$ | Bit index of a bit-flip fault | $b \in \{0, \dots, 15\}$ | Inverts bit $b$: $x' = x \oplus 2^b$ |
| $L$ | NTT butterfly layer / stage index | $L \in \{1, 2, 3, 4, 5, 6, 7\}$ | Forward NTT layer (Layer 1 is widest, Layer 7 is narrowest) |
| $B$ | Butterfly index within layer $L$ | $B \in \{0, \dots, 127\}$ | Index of the 2-coefficient butterfly operation |
| $N_{\text{diffused}}(L)$ | Number of output coefficients affected by a fault at layer $L$ | $N_{\text{diffused}} = 2^{7-L+1}$ | Diffusion width: $L=1 \implies 128$; $L=7 \implies 2$ |
| $T(x, d, q)$ | Dynamic quantization tolerance boundary | $\mathbb{Z}_{\ge 0}$ | Maximum perturbation $|\Delta|$ such that $\text{Compress}_d(x + \Delta) = \text{Compress}_d(x)$ |
| $W_d$ | Nominal quantization bin width | $W_d \approx q / 2^d$ | For $d=10$: $W_{10} \approx 3.25$; for $d=4$: $W_4 \approx 208.06$ |
| $\delta_j$ | Propagated error in output polynomial coefficient $j$ | $\mathbb{Z}_q$ | $r'[j] = r_{\text{clean}}[j] + \delta_j \pmod q$ |
| $\Omega$ | Categorical fault outcome space | Categorical set | $\{Correct, ImplicitReject, ExplicitError, CandidateMismatch, Crash, Timeout, UndetectedFault, PotentialLeakage\}$ |
