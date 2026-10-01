# Mathematical Derivation: Stage-Specific NTT Butterfly Invariants

## 1. Mathematical Structure of the FIPS 203 ML-KEM NTT

In NIST FIPS 203, polynomial operations in ML-KEM-768 are performed in the quotient ring:
$$\mathcal{R}_q = \mathbb{Z}_q[X]/(X^{256} + 1), \quad q = 3329$$
Because $X^{256} + 1$ does not fully split into linear factors in $\mathbb{Z}_q[X]$ (since $q \not\equiv 1 \pmod{512}$), it factors into 128 quadratic polynomials:
$$X^{256} + 1 = \prod_{i=0}^{127} (X^2 - \zeta^{2 \cdot \text{bitrev}_7(i) + 1}) \pmod q$$
where $\zeta = 17$ is a primitive 256-th root of unity in $\mathbb{Z}_q$.

The forward Number Theoretic Transform (NTT) maps a polynomial $p(X) = \sum_{i=0}^{255} p_i X^i \in \mathcal{R}_q$ to 128 degree-1 elements:
$$\text{NTT}(p) = (\hat{p}_0, \dots, \hat{p}_{255}) \in \mathbb{Z}_q^{256}$$
via 7 successive decimation-in-time (DIT) Cooley-Tukey butterfly layers.

---

## 2. Stage-by-Stage Butterfly Indexing and Twiddle Architecture

The forward transform executes across 7 layers ($l \in \{1, 2, 3, 4, 5, 6, 7\}$). In each layer $l$:
- **Stride length:** $\text{len} = 256 \gg l = 2^{8-l}$
- **Block step:** $2 \times \text{len} = 2^{9-l}$
- **Number of blocks:** $2^{l-1}$
- **Twiddle index range:** $k \in [2^{l-1}, 2^l - 1]$
- **Butterflies per layer:** $2^{l-1} \times \text{len} = 128$

| Layer $l$ | Stride $\text{len}$ | Blocks ($2^{l-1}$) | Butterflies/Block | Twiddle Index $k$ | Twiddle Range | Diffusion Span ($2^{7-l}$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Layer 1** | 128 | 1 | 128 | $1$ | $\text{zetas}[1]$ | 64 pairs (128 coeffs) |
| **Layer 2** | 64 | 2 | 64 | $2 \dots 3$ | $\text{zetas}[2 \dots 3]$ | 32 pairs (64 coeffs) |
| **Layer 3** | 32 | 4 | 32 | $4 \dots 7$ | $\text{zetas}[4 \dots 7]$ | 16 pairs (32 coeffs) |
| **Layer 4** | 16 | 8 | 16 | $8 \dots 15$ | $\text{zetas}[8 \dots 15]$ | 8 pairs (16 coeffs) |
| **Layer 5** | 8 | 16 | 8 | $16 \dots 31$ | $\text{zetas}[16 \dots 31]$ | 4 pairs (8 coeffs) |
| **Layer 6** | 4 | 32 | 4 | $32 \dots 63$ | $\text{zetas}[32 \dots 63]$ | 2 pairs (4 coeffs) |
| **Layer 7** | 2 | 64 | 2 | $64 \dots 127$ | $\text{zetas}[64 \dots 127]$ | 1 pair (2 coeffs) |

Total butterflies executed across full NTT: $7 \times 128 = 896$ butterflies.

---

## 3. Symbolic Derivation of the Butterfly Invariants

For any butterfly at indices $(j, j+\text{len})$ with twiddle factor $\zeta \in \mathbb{Z}_q$:
Let the pre-butterfly input values be $u = r[j]$ and $v = r[j+\text{len}]$.

### 3.1 Arithmetic Operations in `mlk_ntt_butterfly_block`
1. **Twiddle Multiplication:**
   $$t = \text{fqmul}(v, \zeta) \equiv v \cdot \zeta \cdot R^{-1} \pmod q$$
   In `mlkem-native`, the table $\text{mlk\_zetas}[k]$ pre-multiplies each root by Montgomery constant $R = 2^{16} \equiv -1044 \pmod q$:
   $$\text{mlk\_zetas}[k] = \zeta_k \cdot R \pmod q$$
   Therefore:
   $$t = \text{fqmul}(v, \text{mlk\_zetas}[k]) \equiv v \cdot (\zeta_k \cdot R) \cdot R^{-1} \equiv v \cdot \zeta_k \pmod q$$
2. **Butterfly Add/Subtract:**
   $$r'[j+\text{len}] = u - t \pmod q$$
   $$r'[j] = u + t \pmod q$$

### 3.2 Derivation of the Difference Invariant
Subtracting the second output from the first output:
$$r'[j] - r'[j+\text{len}] = (u + t) - (u - t) = 2t \pmod q$$
Substituting $t \equiv \text{fqmul}(r[j+\text{len}]_{\text{in}}, \zeta) \pmod q$:
$$\boxed{r'[j] - r'[j+\text{len}] \equiv 2 \cdot \text{fqmul}(r[j+\text{len}]_{\text{in}}, \zeta) \pmod q}$$

### 3.3 Derivation of the Sum Invariant
Adding the two outputs together:
$$r'[j] + r'[j+\text{len}] = (u + t) + (u - t) = 2u \pmod q$$
Substituting $u \equiv r[j]_{\text{in}}$:
$$\boxed{r'[j] + r'[j+\text{len}] \equiv 2 \cdot r[j]_{\text{in}} \pmod q}$$

---

## 4. In-Place Overwrite Dynamics and Verification Boundaries

Because the reference implementation operates strictly **in-place**:
```c
t = mlk_fqmul(r[j + len], zeta);
r[j + len] = (int16_t)(r[j] - t);
r[j] = (int16_t)(r[j] + t);
```
$r[j+\text{len}]$ is overwritten first, then $r[j]$ is overwritten second.

### Consequence for Runtime Monitoring:
1. **Intra-Butterfly Verification (Inside the Butterfly Loop):**
   The verification must occur *before* the input values are lost, or using a saved copy of $u$ and $t$:
   ```c
   int16_t u = r[j];
   int16_t v = r[j + len];
   int16_t t = mlk_fqmul(v, zeta);
   int16_t u_out = (int16_t)(u + t);
   int16_t v_out = (int16_t)(u - t);
   // Invariant checks:
   if (((u_out - v_out) - 2 * t) % q != 0 || ((u_out + v_out) - 2 * u) % q != 0) {
       fault_detected = true;
   }
   r[j] = u_out;
   r[j + len] = v_out;
   ```
2. **Inter-Stage Layer Checkpointing:**
   If checking at the layer boundary, the input polynomial to layer $l$ ($r^{(l-1)}$) can be preserved in an auxiliary stack buffer ($256 \times 2 = 512$ bytes) or validated via linear projection.

---

## 5. Duality and Completeness Theorem

### Theorem: Zero Error Kernel of the Combined Invariant
Let an arbitrary fault perturb the butterfly outputs:
$$r'[j]_{\text{fault}} = u' + \Delta_0, \quad r'[j+\text{len}]_{\text{fault}} = v' + \Delta_1 \quad (\Delta_0, \Delta_1 \in \mathbb{Z}_q)$$

1. **Difference Invariant Condition:**
   $$(u' + \Delta_0) - (v' + \Delta_1) \equiv 2t \pmod q \iff \Delta_0 - \Delta_1 \equiv 0 \pmod q \iff \Delta_0 \equiv \Delta_1 \pmod q$$
2. **Sum Invariant Condition:**
   $$(u' + \Delta_0) + (v' + \Delta_1) \equiv 2u \pmod q \iff \Delta_0 + \Delta_1 \equiv 0 \pmod q \iff \Delta_0 \equiv -\Delta_1 \pmod q$$

Combining both conditions over $\mathbb{Z}_q$:
$$\begin{cases} \Delta_0 - \Delta_1 \equiv 0 \pmod q \\ \Delta_0 + \Delta_1 \equiv 0 \pmod q \end{cases} \implies 2 \Delta_0 \equiv 0 \pmod q$$
Since $q = 3329$ is prime and $\gcd(2, 3329) = 1$:
$$2 \Delta_0 \equiv 0 \implies \Delta_0 = 0 \implies \Delta_1 = 0$$

$$\boxed{\ker(\text{Diff}) \cap \ker(\text{Sum}) = \{(0, 0)\}}$$

### Corollary:
The combined dual butterfly invariant has **zero non-trivial error kernel**. No non-zero error vector $(\Delta_0, \Delta_1) \neq (0, 0)$ can evade detection by both invariants simultaneously.
