# Mathematical Foundation and Implementation Mapping: ML-KEM (FIPS 203)

## 1. Algebraic Structures and Parameters

ML-KEM operates over the quotient polynomial ring:
$$R_q = \mathbb{Z}_q[X] / (X^{256} + 1)$$
where the prime modulus is fixed across all parameter sets at:
$$q = 3329$$
The degree of polynomials is $n = 256$.

### Parameter Sets (FIPS 203)

| Parameter | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 | Description |
| :--- | :--- | :--- | :--- | :--- |
| **$k$** | 2 | 3 | 4 | Module rank (vector dimension) |
| **$q$** | 3329 | 3329 | 3329 | Prime modulus |
| **$n$** | 256 | 256 | 256 | Polynomial ring degree |
| **$\eta_1$** | 3 | 2 | 2 | Noise parameter for secrets / errors |
| **$\eta_2$** | 2 | 2 | 2 | Noise parameter for ciphertext errors |
| **$d_u$** | 10 | 10 | 11 | Ciphertext vector compression bits |
| **$d_v$** | 4 | 4 | 5 | Ciphertext polynomial compression bits |
| **NIST Security Level** | 1 (AES-128) | 3 (AES-192) | 5 (AES-256) | Post-quantum security equivalent |

---

## 2. Mathematical Components, Equations, and Fault Analysis

### Component 1: Ring Arithmetic and Number Theoretic Transform (NTT)

#### Equation
$$f(X) \cdot g(X) \pmod{X^{256} + 1, q} = \text{iNTT}(\text{NTT}(f) \circ \text{NTT}(g))$$
where $\circ$ denotes coefficient-wise dyadic multiplication in the NTT domain.

1. **What it means:** Standard polynomial multiplication in $R_q$ requires $O(n^2)$ coefficient operations. The NTT transforms degree-255 polynomials into 128 quadratic polynomials over $\mathbb{Z}_q$ using primitive roots of unity $\zeta$, reducing complexity to $O(n \log n)$.
2. **Why it exists:** Crucial for latency and throughput in embedded and space processors where energy and CPU cycle budgets are tightly constrained.
3. **Data structure in code:** Array of 256 signed 16-bit integers (`int16_t[256]`). A module vector of rank $k$ is represented as `int16_t[k][256]`.
4. **What can go wrong under faults:** If a single coefficient is corrupted before or during the NTT butterfly stages, the butterfly network propagates the error to all 256 coefficients in the polynomial.
5. **How implementation handles it:** Baseline implementations assume uncorrupted ALU and cache lines; no runtime bounds check is performed inside the butterfly loops, resulting in immediate Silent Data Corruption (SDC).

---

### Component 2: Noise Sampling via Centered Binomial Distribution ($\text{CBD}_\eta$)

#### Equation
$$y = \sum_{i=0}^{\eta-1} (a_i - b_i), \quad a_i, b_i \leftarrow \{0, 1\}$$

1. **What it means:** Samples small error/noise coefficients with mean 0 and variance $\sigma^2 = \eta / 2$. Coefficients strictly fall within $[-\eta, +\eta]$.
2. **Why it exists:** Forms the core hardness of the Module Learning with Errors ($\text{M-LWE}$) problem. Without carefully calibrated noise, the linear system $\mathbf{A}\mathbf{s} + \mathbf{e}$ would be solvable in polynomial time via Gaussian elimination.
3. **Data structure in code:** Byte stream from SHAKE-256 / PRF parsed in bit-chunks and converted to `int16_t[256]`.
4. **What can go wrong under faults:** If an SEU flips bits in the sampled noise vector, the noise variance increases or falls outside $[-\eta, +\eta]$. If the error exceeds the threshold $q/4$, the decryption error probability spikes to 1.
5. **How implementation handles it:** The sampling logic produces values based purely on the PRF stream. It does not re-verify the empirical variance or boundedness of the sampled vector.

---

### Component 3: Compression and Decompression Functions

#### Equation
$$\text{Compress}_q(x, d) = \left\lceil \frac{2^d}{q} \cdot x \right\rfloor \pmod{2^d}$$
$$\text{Decompress}_q(y, d) = \left\lceil \frac{q}{2^d} \cdot y \right\rfloor$$

1. **What it means:** Discards low-order bits from polynomial coefficients to reduce transmission bandwidth over bandwidth-limited satellite downlinks.
2. **Why it exists:** Transmitting uncompressed 12-bit coefficients would increase ciphertext sizes by ~25-35%, consuming excessive RF link power and storage.
3. **Data structure in code:** Packed bit-arrays (`uint8_t[]`). For $d=10$, 4 coefficients (48 bits) are packed into 5 bytes (40 bits).
4. **What can go wrong under faults:** An SEU in the bit-packing routine corrupts multiple adjacent unpacked coefficients due to bit-shift alignment dependencies.
5. **How implementation handles it:** Constant-time bit-shifting loops. No integrity checksums exist on intermediate packed bytes.

---

### Component 4: Fujisaki-Okamoto (FO) Transform & Implicit Rejection

#### Equation
$$K = \begin{cases} \text{KDF}(K', H(c)) & \text{if } c' = c \\ \text{KDF}(z, H(c)) & \text{if } c' \ne c \end{cases}$$

1. **What it means:** During decapsulation, the decapsulator re-encrypts the recovered message $m'$ to obtain candidate ciphertext $c'$. If $c' \ne c$, the algorithm does not return an error code; instead, it outputs a deterministic pseudorandom key derived from a secret seed $z$.
2. **Why it exists:** Defends against Chosen-Ciphertext Attacks (IND-CCA2) by preventing oracle-based side-channel leakage through error messages.
3. **Data structure in code:** Constant-time `memcmp` / conditional copy (`OQS_MEM_cnd_copy`).
4. **What can go wrong under faults:** If an SEU strikes during decapsulation, $c' \ne c$. The algorithm silently substitutes the pseudorandom key without alerting the caller. The remote receiver will compute a different shared secret, silently breaking cryptographic synchronization across the space link.
5. **How implementation handles it:** Built into FIPS 203 explicitly. For space systems, this architectural behavior makes silent fault detection particularly insidious.
