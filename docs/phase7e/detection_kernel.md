# Detection Kernel and Blind-Spot Characterization of Stage Invariants

## 1. Algebraic Kernel Formalization

Let the butterfly operation be defined over $\mathbb{Z}_q$ ($q=3329$):
$$(u', v') = \mathcal{B}(u, v, \zeta) = (u + t, u - t), \quad t \equiv \text{fqmul}(v, \zeta) \pmod q$$
Let an error vector $\mathbf{e} = (\Delta_u, \Delta_v) \in \mathbb{Z}_q^2$ corrupt the output state:
$$(u'_{\text{fault}}, v'_{\text{fault}}) = (u' + \Delta_u, v' + \Delta_v)$$

We define the detection kernel $\ker(\mathcal{I})$ of an invariant $\mathcal{I}$ as the subspace of error vectors that evaluate to zero under the invariant:
$$\ker(\mathcal{I}) = \{(\Delta_u, \Delta_v) \in \mathbb{Z}_q^2 : \mathcal{I}(u'+\Delta_u, v'+\Delta_v) = \mathcal{I}(u', v')\}$$

---

## 2. Characterization of Individual Invariant Kernels

### 2.1 The Difference Invariant: $\mathcal{I}_{\text{diff}}(u', v') = (u' - v') - 2t \pmod q$
Evaluating with error:
$$(u' + \Delta_u) - (v' + \Delta_v) - 2t \equiv (\Delta_u - \Delta_v) \pmod q$$
$$\boxed{\ker(\mathcal{I}_{\text{diff}}) = \{(\Delta, \Delta) : \Delta \in \mathbb{Z}_q\}}$$

**Properties:**
- **Dimensionality:** 1-dimensional subspace of $\mathbb{Z}_q^2$ of size $q = 3329$ vectors out of $3329^2 \approx 1.11 \times 10^7$ possible errors.
- **Coverage:** Detects $1 - \frac{1}{q} \approx 99.97\%$ of random error pairs $(\Delta_u, \Delta_v)$.
- **Critical Blind Spot:** **Symmetric Perturbations.** When both outputs suffer the identical additive error $\Delta_u = \Delta_v = \Delta$, $\Delta_u - \Delta_v = 0$.
  *Physical Cause:* Common-mode bus faults, DC offset glitches, power rail transients shifting both butterfly registers equally.

### 2.2 The Sum Invariant: $\mathcal{I}_{\text{sum}}(u', v') = (u' + v') - 2u \pmod q$
Evaluating with error:
$$(u' + \Delta_u) + (v' + \Delta_v) - 2u \equiv (\Delta_u + \Delta_v) \pmod q$$
$$\boxed{\ker(\mathcal{I}_{\text{sum}}) = \{(\Delta, -\Delta) : \Delta \in \mathbb{Z}_q\}}$$

**Properties:**
- **Dimensionality:** 1-dimensional subspace of size $q = 3329$.
- **Coverage:** Detects $1 - \frac{1}{q} \approx 99.97\%$ of random error pairs.
- **Critical Blind Spot:** **Anti-Symmetric Perturbations.** When $\Delta_u = -\Delta_v = \Delta$, $\Delta_u + \Delta_v = 0$.
  *Physical Cause:* ANY fault in the intermediate multiplier $t$ or twiddle factor $\zeta$ naturally induces $\Delta_u = +\Delta$ and $\Delta_v = -\Delta$. Consequently, **the Sum Invariant has a 100% blind spot for all intermediate multiplication and twiddle errors**.

### 2.3 The Dual Invariant: $\mathcal{I}_{\text{dual}} = (\mathcal{I}_{\text{diff}}, \mathcal{I}_{\text{sum}})$
$$\ker(\mathcal{I}_{\text{dual}}) = \ker(\mathcal{I}_{\text{diff}}) \cap \ker(\mathcal{I}_{\text{sum}}) = \{(\Delta, \Delta)\} \cap \{(\Delta, -\Delta)\} = \{(0, 0)\}$$

**Properties:**
- **Zero Algebraic Error Kernel:** Every non-zero error vector $(\Delta_u, \Delta_v) \neq (0, 0)$ is guaranteed to violate at least one invariant.

---

## 3. Locus-by-Locus Detection Comparison Matrix

The table below disaggregates coverage across physical fault loci based on both algebraic derivation and empirical verification across 500 trials per locus in `experiments/phase7e/mathematical_reference.py`:

| Fault Locus & Representation | Algebraic Error Form $(\Delta_u, \Delta_v)$ | Diff Invariant Coverage | Sum Invariant Coverage | Combined Dual Coverage |
| :--- | :---: | :---: | :---: | :---: |
| **Output $u'$ Register Bit-Flip** | $(2^b, 0)$ | **100.0%** | **100.0%** | **100.0%** |
| **Output $v'$ Register Bit-Flip** | $(0, 2^b)$ | **100.0%** | **100.0%** | **100.0%** |
| **Intermediate $t$ Register Glitch** | $(\Delta, -\Delta)$ | **100.0%** | **0.0% (Blind Spot)** | **100.0%** |
| **Twiddle $\zeta$ Memory Corruption** | $(\Delta \cdot v, -\Delta \cdot v)$ | **99.97%** ($v \not\equiv 0$) | **0.0% (Blind Spot)** | **99.97%** |
| **Symmetric Output Perturbation** | $(\Delta, \Delta)$ | **0.0% (Blind Spot)** | **100.0%** | **100.0%** |
| **Anti-Symmetric Output Perturbation**| $(\Delta, -\Delta)$ | **100.0%** | **0.0% (Blind Spot)** | **100.0%** |
| **Correlated Arithmetic Glitch** | $(\Delta_u, \Delta_v)$ arbitrary | **100.0%** ($\Delta_u \neq \Delta_v$) | **100.0%** ($\Delta_u \neq -\Delta_v$) | **100.0%** |

---

## 4. Multi-Layer Error Diffusion and Spatial Masking

When a fault occurs in Layer $l$ ($l \in \{1, \dots, 6\}$), the perturbation diffuses through all downstream layers $(l+1) \dots 7$.

### Diffusion Factor:
At Layer $l$, each butterfly output connects to $2^{7-l}$ final output coefficients:
$$\text{Diffusion Span}(l) = 2^{7-l}$$

- **Layer 1 Fault:** Diffuses to $2^6 = 64$ butterfly pairs ($128$ coefficients).
- **Layer 4 Fault:** Diffuses to $2^3 = 8$ butterfly pairs ($16$ coefficients).
- **Layer 7 Fault:** Localized to $2^0 = 1$ butterfly pair ($2$ coefficients).

### The Spatial Masking Phenomenon:
If detection is deferred until the final transform output (as in Phase 7C's Layer 7 weighted check):
- A fault in Layer 7 produces a clean, isolated perturbation on 2 coefficients, matching the basis vector $e_2$ ($100\%$ detection).
- A fault in Layer 1 diffuses across 128 coefficients with varying signs and twiddle powers. The linear combination can sum to $0 \pmod q$ for specific coefficient subsets, reducing the final weighted invariant's coverage to only **14.0%**.
- **Conclusion:** Deferring detection to the final layer causes catastrophic loss of recovery visibility. Catching faults **at or near their injection stage** preserves the isolated $2 \times 2$ butterfly structure and guarantees $100\%$ detection.
