# Phase 7B Independent Mathematical Audit: NTT Invariants and Error Kernels

**Auditor:** Independent Mathematical Reviewer & Implementation Auditor  
**Target:** Polynomial Arithmetic in NIST FIPS 203 ML-KEM-768 (`algorithms/source_ref/mlkem/src/poly.c`)  
**Date:** October 2026  

---

## 1. Mathematical Audit of the Unweighted Parity Invariant

Phase 6 and Phase 7 evaluate the unweighted parity projection checks:
$$\phi_{\text{even}}(\hat{p}) = \sum_{i=0}^{127} \hat{p}_{2i} \equiv 128 \cdot p_0 \pmod{3329}$$
$$\phi_{\text{odd}}(\hat{p}) = \sum_{i=0}^{127} \hat{p}_{2i+1} \equiv 128 \cdot p_1 \pmod{3329}$$

### Independent Verification of Clean Correctness
In the polynomial ring $R_q = \mathbb{Z}_q[X]/(X^{256} + 1)$, $X^{256} + 1 = \prod_{i=0}^{127} (X^2 - \zeta_{2i+1})$.  
Under forward NTT, an input polynomial $p(X) = p_{\text{even}}(X^2) + X \cdot p_{\text{odd}}(X^2)$ is mapped to 128 degree-1 polynomials:
$$\hat{p}_{2i} = p_{\text{even}}(\zeta_{2i+1}) = \sum_{k=0}^{127} p_{2k} \zeta_{2i+1}^k \pmod q$$
$$\hat{p}_{2i+1} = p_{\text{odd}}(\zeta_{2i+1}) = \sum_{k=0}^{127} p_{2k+1} \zeta_{2i+1}^k \pmod q$$

Summing over all $i \in \{0, \dots, 127\}$:
$$\sum_{i=0}^{127} \hat{p}_{2i} = \sum_{k=0}^{127} p_{2k} \left( \sum_{i=0}^{127} \zeta_{2i+1}^k \right) \pmod q$$

Since $\zeta_{2i+1}$ are the 128 distinct roots of $Y^{128} + 1 = 0 \pmod q$, by Newton's symmetric power sums:
$$S_k = \sum_{i=0}^{127} \zeta_{2i+1}^k = \begin{cases} 128 \pmod q & k = 0 \\ 0 \pmod q & 1 \le k \le 127 \end{cases}$$

Hence:
$$\sum_{i=0}^{127} \hat{p}_{2i} = 128 \cdot p_0 \pmod q, \quad \sum_{i=0}^{127} \hat{p}_{2i+1} = 128 \cdot p_1 \pmod q$$
**Status:** Mathematically valid and verified on clean inputs.

---

### Audit of Universal Parity Cancellation
The Phase 7 report claims that intermediate butterfly multiplier faults ($t$) and twiddle factor errors ($\zeta$) cancel to zero in every single layer.

**Auditor Verification:**
In Cooley-Tukey butterfly:
$$r'[j] = r[j] + t, \quad r'[j+\text{len}] = r[j] - t, \quad \text{where } t = r[j+\text{len}] \cdot \zeta \pmod q$$

Because ML-KEM's incomplete NTT stops at Layer 7, the butterfly length $\text{len} = 256 \gg \text{layer}$ takes values:
$$\text{len} \in \{128, 64, 32, 16, 8, 4, 2\}$$

Notice that $\text{len}$ is **strictly even in all 7 layers**:
$$\text{len} \equiv 0 \pmod 2 \implies j \equiv (j + \text{len}) \pmod 2$$

Therefore, an error $\Delta$ affecting intermediate value $t$ adds $+\Delta$ to index $j$ and $-\Delta$ to index $j+\text{len}$. Since both indices have identical parity, both updates fall into the exact same sum:
$$\Delta \phi_{\text{even}} = +\Delta - \Delta = 0 \pmod q$$
$$\Delta \phi_{\text{odd}} = 0 \pmod q$$

**Conclusion:** The theorem is **MATHEMATICALLY SOUND**. Across 128 butterflies in all 7 layers (total 896 intermediate butterfly locations), unweighted parity checks have an intrinsic mathematical blind spot of **100% false-negative rate** for intermediate $t$ glitches.

---

## 2. Mathematical Audit of the Weighted Inverse-Zeta Invariant

Phase 7 proposes weighting outputs by inverse roots:
$$\psi_{\text{even}}(\hat{p}) = \sum_{i=0}^{127} \zeta_{2i+1}^{-1} \cdot \hat{p}_{2i} \equiv 128 \cdot p_2 \pmod{3329}$$
$$\psi_{\text{odd}}(\hat{p}) = \sum_{i=0}^{127} \zeta_{2i+1}^{-1} \cdot \hat{p}_{2i+1} \equiv 128 \cdot p_3 \pmod{3329}$$

### Auditor Derivation & Root Ordering Verification
Multiplying each coefficient evaluation by $\zeta_{2i+1}^{-1}$:
$$\sum_{i=0}^{127} \zeta_{2i+1}^{-1} \hat{p}_{2i} = \sum_{k=0}^{127} p_{2k} \left( \sum_{i=0}^{127} \zeta_{2i+1}^{k-1} \right) \pmod q$$

For $k = 1$, the exponent is $k - 1 = 0$, so $\sum \zeta_{2i+1}^0 = 128$.  
For $k \ne 1$ (where $0 \le k \le 127$), $-1 \le k - 1 \le 126$. The sum vanishes modulo 3329:
$$\sum_{i=0}^{127} \zeta_{2i+1}^{-1} \hat{p}_{2i} = 128 \cdot p_2 \pmod q$$

### Critical Verification of the Implementation Table
In `experiments/phase7/phase7_layered_resilience.c`, the table `g_inv_zetas_layer7` is defined.
We verified in `find_weights.c` that the table elements:
$$w = [1175, -1175, -885, 885, 394, -394, \dots]$$
exactly match the inverse evaluations of basis vector $e_2$ ($p(X) = X^2$) under `mlkem768_poly_ntt`.

### Error Kernel Analysis
At Layer 7 ($\text{len} = 2$), butterfly pairs are $(2i, 2i+2)$. In the weighted check, coefficient $\hat{p}_{2i}$ is weighted by $w_i$, while coefficient $\hat{p}_{2i+2}$ is weighted by $w_{i+1}$.  
As verified, $w_i = -w_{i+1} \pmod q$, so:
$$\Delta \psi_{\text{even}} = (w_i - w_{i+1}) \cdot \Delta = 2 w_i \Delta \not\equiv 0 \pmod q$$
This ensures **100% detection (128/128) for Layer 7 intermediate faults**.

However, for Layers 1 to 6, butterfly pairs span coordinates where the sum of weights over the butterfly support can vanish for certain twiddle combinations. The weighted check alone achieves only **14.0% detection** across general all-layer sweeps (detecting Layer 7 completely, but missing most faults in Layers 1–6).

---

## 3. Audit of the Butterfly Difference Check

Phase 7 presents the butterfly invariant:
$$r'[j] - r'[j+\text{len}] \equiv 2 \cdot r[j+\text{len}] \cdot \zeta \pmod q$$

### Auditor Findings
1. **Mathematical Soundness:**
   $$r'[j] - r'[j+\text{len}] = (r[j] + t) - (r[j] - t) = 2 t = 2 \cdot r[j+\text{len}] \cdot \zeta \pmod q$$
   The formula is algebraically exact.
2. **Implementation Status in Phase 7:**
   Inspection of `experiments/phase7/phase7_layered_resilience.c` reveals that `verify_complementary_ntt` is called with:
   `verify_complementary_ntt(&p_time, &p_ntt, NULL, NULL, 0);`
   The arguments `mid_in` and `mid_out` are passed as `NULL` across all 1,200 trials and in all benchmarks!
   **Finding:** The butterfly difference check **was not active during Phase 7 experimental trials**. Its detection coverage and overhead were unmeasured in the primary benchmark.

---

## 4. Cross-Check Summary Table

| Mechanism | Math Derivation Status | Implementation Status | Confirmed Coverage | Overhead |
| :--- | :--- | :--- | :--- | :--- |
| **Unweighted Parity Invariant** | Validated | Fully Executed | 100% Asymmetric Output Faults; **0.0% Intermediate $t, \zeta$ Faults** | +0.2% |
| **Weighted Inverse-Zeta Invariant** | Validated | Fully Executed | **100% Layer 7 Intermediate Faults**; 14.0% across all layers | +1.0% |
| **Butterfly Difference Check** | Validated | **Uncalled in Benchmark** (Passed `NULL`) | Theoretical 100% at checked stages; **Empirically Inactive** | Unmeasured |
