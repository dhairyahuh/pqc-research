# Mathematical-to-Implementation Mapping and Fault Target Traceability

## 1. Research Purpose

To ensure scientific defensibility, every fault-injection hook must trace directly through the full research chain:
$$\text{Mathematical Operation} \longrightarrow \text{FIPS Standard Equation} \longrightarrow \text{Source Function} \longrightarrow \text{Data Structure} \longrightarrow \text{Fault Target} \longrightarrow \text{Expected Consequence}$$

---

## 2. ML-KEM (FIPS 203) Mathematical Mapping

### Map KEM-1: Forward Number Theoretic Transform (NTT)
- **Mathematical Operation:** Isomorphism $R_q \to \prod_{i=0}^{127} \mathbb{Z}_q[X]/(X^2 - \zeta^{2\text{BitRev}(i)+1})$.
- **FIPS 203 Section:** Algorithm 9 ($\text{NTT}$), Equation (4.13).
- **Source Function:** `poly_ntt(poly *r)` in [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c).
- **Data Structure:** `poly` containing `int16_t coeffs[256]` in Montgomery domain.
- **Fault Target:** Intermediate coefficient register/memory during butterfly step $j \in \{0 \dots 127\}$.
- **Expected Consequence:** Butterfly diffusion corrupts all 256 coefficients of the polynomial. During decapsulation, re-encryption check fails, triggering FO implicit rejection (pseudorandom shared secret / SDC).

### Map KEM-2: Inverse NTT ($\text{NTT}^{-1}$)
- **Mathematical Operation:** Inverse isomorphism transforming NTT representation back to standard basis polynomial in $R_q$.
- **FIPS 203 Section:** Algorithm 10 ($\text{NTT}^{-1}$), Equation (4.14).
- **Source Function:** `poly_invntt_tomont(poly *r)` in [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c).
- **Data Structure:** `poly` array `int16_t coeffs[256]`.
- **Fault Target:** Twiddle factor multiplication accumulator or butterfly output.
- **Expected Consequence:** Decoded message polynomial $m'$ contains erroneous bits exceeding error-correcting decoding threshold, causing decapsulation failure.

### Map KEM-3: Centered Binomial Noise Sampling ($\text{CBD}_\eta$)
- **Mathematical Operation:** $\sum_{i=0}^{\eta-1} (a_i - b_i)$, $a_i, b_i \leftarrow \{0, 1\}$.
- **FIPS 203 Section:** Algorithm 7 ($\text{SamplePolyCBD}_\eta$), Equation (4.7).
- **Source Function:** `poly_cbd_eta1(...)` / `poly_cbd_eta2(...)` in [`algorithms/source_ref/mlkem/src/sampling.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/sampling.c).
- **Data Structure:** Input byte buffer `const uint8_t buf[]`, output `poly *r`.
- **Fault Target:** PRF output bytes or subtraction accumulator $(a_i - b_i)$.
- **Expected Consequence:** Sampled noise vector exceeds nominal bound $[-\eta, +\eta]$. If total error term $\|e\|_\infty > q/4$, deterministic decryption fails.

### Map KEM-4: Matrix-Vector Polynomial Multiplication ($\mathbf{A} \circ \mathbf{s}$)
- **Mathematical Operation:** Inner product $\sum_{j=0}^{k-1} \hat{\mathbf{A}}_{i,j} \circ \hat{\mathbf{s}}_j$.
- **FIPS 203 Section:** Algorithm 13 ($\text{K-PKE.Encaps}$), Step 6.
- **Source Function:** `poly_vec_basemul_acc_montgomery(...)` in [`algorithms/source_ref/mlkem/src/poly_k.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly_k.c).
- **Data Structure:** `polyvec` struct containing $k$ polynomials: `poly vec[k]`.
- **Fault Target:** Montgomery accumulation variable `acc`.
- **Expected Consequence:** Ciphertext vector $\mathbf{u}$ is perturbed away from lattice point, rendering legitimate decapsulation impossible.

### Map KEM-5: Fujisaki-Okamoto Re-encryption Verification
- **Mathematical Operation:** Verification predicate $c \stackrel{?}{=} \text{K-PKE.Encrypt}(pk, m', r')$.
- **FIPS 203 Section:** Algorithm 17 ($\text{ML-KEM.Decaps}$), Step 8.
- **Source Function:** `crypto_kem_dec(...)` and `verify(...)` in [`algorithms/source_ref/mlkem/src/kem.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c).
- **Data Structure:** Ciphertext buffer byte comparison `uint8_t c[MLKEM_CT_BYTES]`.
- **Fault Target:** Conditional selection variable `fail` in constant-time copy `ct_verify(...)`.
- **Expected Consequence:** If `fail` is flipped from 1 to 0 under corrupted ciphertext, invalid ciphertext is treated as valid, potentially leaking secret key bits through decapsulation oracle behavior.

---

## 3. ML-DSA (FIPS 204) Mathematical Mapping

### Map DSA-1: Fiat-Shamir with Aborts & Infinity Norm Bounds
- **Mathematical Operation:** Rejection test: restart loop if $\|\mathbf{z}\|_\infty \ge \gamma_1 - \beta$ or $\|\mathbf{r}_0\|_\infty \ge \gamma_2 - \beta$.
- **FIPS 204 Section:** Algorithm 7 ($\text{ML-DSA.Sign}$), Steps 14 & 18.
- **Source Function:** `polyvecl_chknorm(...)` in [`algorithms/source_ref/mldsa/src/polyvec.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mldsa/src/polyvec.c) called inside `crypto_sign_signature(...)` in [`algorithms/source_ref/mldsa/src/sign.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mldsa/src/sign.c).
- **Data Structure:** `polyvecl` containing $\ell \times 256$ elements of `int32_t`.
- **Fault Target:** Comparison branch condition or norm accumulator.
- **Expected Consequence:** 
  1. *Norm check bypassed:* Out-of-bounds signature $\mathbf{z}$ emitted $\implies$ **critical private key leakage** via statistical attacks.
  2. *Norm check falsely failed:* Infinite loop or abnormal elongation $\implies$ **denial of service (SEFI)**.

### Map DSA-2: HighBits and LowBits Decomposition
- **Mathematical Operation:** $r = r_1 \cdot 2\gamma_2 + r_0$, with $-\gamma_2 < r_0 \le \gamma_2$.
- **FIPS 204 Section:** Algorithm 29 ($\text{Decompose}$), Algorithm 30 ($\text{HighBits}$).
- **Source Function:** `poly_decompose(...)` in [`algorithms/source_ref/mldsa/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mldsa/src/poly.c).
- **Data Structure:** Output polynomials `poly *a1, poly *a0` with signed 32-bit coefficients.
- **Fault Target:** Decomposition quotient $r_1$ calculation.
- **Expected Consequence:** Hint bit inconsistency; signature fails verification at the receiving ground station.

### Map DSA-3: Hint Vector Generation & Population Count Check
- **Mathematical Operation:** $h = \text{MakeHint}(-\mathbf{c}\mathbf{t}_0, \mathbf{w} - \mathbf{c}\mathbf{s}_2 + \mathbf{c}\mathbf{t}_0, 2\gamma_2)$, with $\|h\|_1 \le \omega$.
- **FIPS 204 Section:** Algorithm 33 ($\text{MakeHint}$), Algorithm 7 Step 24.
- **Source Function:** `poly_make_hint(...)` in [`algorithms/source_ref/mldsa/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mldsa/src/poly.c).
- **Data Structure:** Sparse bit index array `uint8_t hints[]`, counter `int hints_count`.
- **Fault Target:** `hints_count` accumulator.
- **Expected Consequence:** If `hints_count > \omega`, signer aborts loop; if verifier encounters corrupted hints, signature verification evaluates to `EXPECTED_REJECTION`.
