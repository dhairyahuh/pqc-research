# Mathematical Foundation and Implementation Mapping: ML-DSA (FIPS 204)

## 1. Algebraic Structures and Parameters

ML-DSA operates over the polynomial quotient ring:
$$R_q = \mathbb{Z}_q[X] / (X^{256} + 1)$$
where the prime modulus is:
$$q = 8380417 = 2^{23} - 2^{13} + 1$$
Degree $n = 256$.

### Parameter Sets (FIPS 204)

| Parameter | ML-DSA-44 | ML-DSA-65 | ML-DSA-87 | Description |
| :--- | :--- | :--- | :--- | :--- |
| **$(k, \ell)$** | $(4, 4)$ | $(6, 5)$ | $(8, 7)$ | Matrix dimensions $\mathbf{A} \in R_q^{k \times \ell}$ |
| **$q$** | 8380417 | 8380417 | 8380417 | Modulus |
| **$\eta$** | 2 | 4 | 2 | Secret key coefficient bound $[-\eta, +\eta]$ |
| **$\gamma_1$** | $2^{17}$ | $2^{19}$ | $2^{19}$ | Masking polynomial coefficient bound |
| **$\gamma_2$** | $(q-1)/88 = 95232$ | $(q-1)/32 = 261888$ | $(q-1)/32 = 261888$ | Low-order rounding bound |
| **$\tau$** | 39 | 49 | 60 | Number of non-zero coefficients in challenge $c$ |
| **$\beta$** | $\tau \cdot \eta = 78$ | $\tau \cdot \eta = 196$ | $\tau \cdot \eta = 120$ | Bound on $\|c \cdot \mathbf{s}\|_\infty$ |
| **NIST Security Level** | 2 | 3 | 5 | Post-quantum security equivalent |

---

## 2. Mathematical Components, Equations, and Fault Analysis

### Component 1: Signing Equation and Fiat-Shamir with Aborts

#### Equation
$$\mathbf{z} = \mathbf{y} + c \cdot \mathbf{s}_1$$
Rejection condition:
$$\text{If } \|\mathbf{z}\|_\infty \ge \gamma_1 - \beta \quad \text{or} \quad \|\text{LowBits}(\mathbf{w} - c \cdot \mathbf{s}_2)\|_\infty \ge \gamma_2 - \beta, \quad \text{restart loop}$$

1. **What it means:** The signer generates an ephemeral masking vector $\mathbf{y} \leftarrow [-\gamma_1 + 1, \gamma_1]^\ell$, computes commitment $\mathbf{w}_1 = \text{HighBits}(\mathbf{A}\mathbf{y})$, derives challenge $c = H(\mu, \mathbf{w}_1)$, and computes candidate response $\mathbf{z}$. If $\mathbf{z}$ leaks information about the secret key $\mathbf{s}_1$ (manifested as an infinity norm exceeding the threshold), the candidate is rejected and the loop restarts.
2. **Why it exists:** Crucial to prevent private key leakage via signature statistical distributions (Fiat-Shamir with Aborts).
3. **Data structure in code:** Vector of $\ell$ polynomials, each having 256 signed 32-bit integers (`int32_t[l][256]`).
4. **What can go wrong under faults:**
   - If an SEU alters the norm comparison (`norm >= bound`), a leaking signature may be released, compromising the mission's master private key.
   - If an SEU perturbs $\mathbf{z}$ after the norm check, an invalid signature is emitted (detected at verification).
   - If the loop counter or rejection condition is stuck, execution hangs (denial of service on spacecraft telecommand receiver).
5. **How implementation handles it:** OpenSSL and liboqs execute while loops with bounded max iterations. Rejection logic relies on standard C branching without hardware-fault checks.

---

### Component 2: HighBits and LowBits Decomposition

#### Equation
$$r = r_1 \cdot 2\gamma_2 + r_0, \quad \text{where } -\gamma_2 < r_0 \le \gamma_2$$

1. **What it means:** Decomposes arbitrary field elements into a high-order part $r_1$ and small remainder $r_0$.
2. **Why it exists:** Allows verification using only the high-order bits of the commitment vector, drastically compressing the public key and signature sizes.
3. **Data structure in code:** `int32_t` arithmetic using division/modulo approximations optimized for $q = 8380417$.
4. **What can go wrong under faults:** An off-by-one arithmetic glitch flips $r_1 \pm 1$, causing hint generation failure in verification.
5. **How implementation handles it:** Pure arithmetic routines using constant-time bit operations.

---

### Component 3: Hint Bit Generation and Verification

#### Equation
$$h = \text{MakeHint}(-\mathbf{c}\mathbf{t}_0, \mathbf{w} - \mathbf{c}\mathbf{s}_2 + \mathbf{c}\mathbf{t}_0, 2\gamma_2)$$
Verification checks:
$$\mathbf{w}'_1 = \text{UseHint}(h, \mathbf{A}\mathbf{z} - c\mathbf{t}_1 \cdot 2^d, 2\gamma_2), \quad c \stackrel{?}{=} H(\mu, \mathbf{w}'_1)$$

1. **What it means:** The hint vector $h$ identifies exactly which coefficients shifted across high-bit rounding boundaries due to the secret key addition.
2. **Why it exists:** Ensures the verifier can reconstruct the exact high bits $\mathbf{w}_1$ without knowing the secret keys $\mathbf{s}_1, \mathbf{s}_2$.
3. **Data structure in code:** Sparse bit-array packing indices where $h_{i,j} = 1$.
4. **What can go wrong under faults:** A single bit-flip in the hint array causes $\text{UseHint}$ to compute the wrong $\mathbf{w}'_1$, leading to signature verification rejection.
5. **How implementation handles it:** Hint count is bound-checked against parameter $\omega$; exceeding $\omega$ returns verification failure.
