# Workstream 6: Mathematical and Security Review

**Auditor:** Independent Cryptographic Theory and Hardware Security Auditor  
**Date:** October 2026  
**Subject:** Formal Derivation of Butterfly Invariants, Evading Fault Patterns, and Security Taxonomies  
**Target Specifications:** NIST FIPS PUB 203 (ML-KEM) & Module Ring $R_q = \mathbb{Z}_{3329}[X]/(X^{256} + 1)$

---

## 1. Formal Mathematical Derivation of Invariants

All polynomial arithmetic in ML-KEM-768 is defined over the finite field $\mathbb{Z}_q$ with prime modulus $q = 3329$. Because $q \equiv 1 \pmod{256}$, $\mathbb{Z}_q$ contains primitive 256th roots of unity, enabling fast radix-2 Number Theoretic Transforms.

### 1.1. Forward Cooley-Tukey (CT) Invariants

#### Butterfly Definition:
For input coefficients $u, v \in \mathbb{Z}_q$ and twiddle factor $\zeta \in \mathbb{Z}_q$:
$$t = v \cdot \zeta \pmod{q}$$
$$r_0 = u + t \pmod{q}$$
$$r_1 = u - t \pmod{q}$$

#### Derivation 1: Sum Invariant
$$r_0 + r_1 \equiv (u + t) + (u - t) \equiv 2u \pmod{q}$$
- **Assumptions:** Input $u$ is known and preserved in an authentic snapshot $u_{\text{saved}}$.
- **Detection Scope:** Detects independent corruptions of $r_0$ or $r_1$, or asymmetric errors where $\Delta r_0 + \Delta r_1 \not\equiv 0 \pmod{q}$.
- **Blind Spot:** If an error occurs in intermediate multiplication $t \to t + \epsilon$, both outputs are corrupted symmetrically:
  $$r_0' = u + t + \epsilon, \quad r_1' = u - t - \epsilon$$
  $$r_0' + r_1' \equiv (u + t + \epsilon) + (u - t - \epsilon) \equiv 2u \pmod{q}$$
  **The sum invariant is completely blind to multiplier errors.**

#### Derivation 2: Difference Invariant
$$r_0 - r_1 \equiv (u + t) - (u - t) \equiv 2t \equiv 2(v \cdot \zeta) \pmod{q}$$
- **Assumptions:** Input $v$ and twiddle factor $\zeta$ are authentic.
- **Detection Scope:** If multiplication is corrupted $t \to t + \epsilon$:
  $$r_0' - r_1' \equiv (u + t + \epsilon) - (u - t - \epsilon) \equiv 2t + 2\epsilon \pmod{q}$$
  $$\text{Invariant Difference} = (r_0' - r_1') - 2t \equiv 2\epsilon \pmod{q}$$
  Because $\gcd(2, 3329) = 1$, $2\epsilon \equiv 0 \pmod{3329} \iff \epsilon \equiv 0 \pmod{3329}$.
  **Any non-zero additive multiplier error $\epsilon$ is detected by the difference invariant.**

---

### 1.2. Inverse Gentleman-Sande (GS) Invariants

#### Butterfly Definition:
For input coefficients $u, v \in \mathbb{Z}_q$ and inverse twiddle factor $\zeta \in \mathbb{Z}_q$:
$$r_0 = u + v \pmod{q}$$
$$r_1 = \zeta^{-1}(u - v) \equiv \zeta(v - u) \pmod{q}$$
*(Note: In the `mlkem-native` implementation, the layer twiddle table pre-inverts twiddles and stores $\zeta$ such that multiplication by $\zeta$ implements the inverse transform step).*

#### Mathematical Sum Invariant (Manuscript §3.3 Formulation):
$$r_0 + \zeta \cdot r_1 \equiv (u + v) + \zeta \cdot \zeta^{-1}(u - v) \equiv (u + v) + (u - v) \equiv 2u \pmod{q}$$
$$r_0 - \zeta \cdot r_1 \equiv (u + v) - (u - v) \equiv 2v \pmod{q}$$

#### Implementation Decoupling (Source Code Formulation in `mlkem_fault_hooks.c:818-827`):
In compiled software, computing $\zeta \cdot r_1$ requires an extra modular multiplication. The in-tree implementation decouples the verification:
1. **Adder Check:**
   $$\text{sum\_c} = \left( r_0 - (u_{\text{saved}} + v_{\text{saved}}) \right) \bmod 3329$$
2. **Recomputed Multiplier Check:**
   $$v_{\text{expected}} = \text{monitor\_fqmul}(v_{\text{saved}} - u_{\text{saved}}, \zeta)$$
   $$\text{diff\_c} = \left( r_1 - v_{\text{expected}} \right) \bmod 3329$$

- **Detection Scope:** Adder faults perturb $\text{sum\_c}$; multiplier or difference faults perturb $\text{diff\_c}$.
- **Equivalence:** Decoupled checking provides identical fault coverage to the algebraic invariant without requiring an extra modular inversion or multiplication by $\zeta$.

---

## 2. Invariant Blind Spots and Evading Fault Patterns

| Vulnerability Scenario | Mathematical Manifestation | Local Detection Probability | Downstream Mitigation |
|:---|:---|:---:|:---|
| **Twiddle Factor Corruption ($\zeta \to \zeta + \Delta\zeta$)** | Operational $t^* = v \cdot \zeta^*$; Monitor $t_{\text{check}} = v_{\text{saved}} \cdot \zeta^*$. Difference check: $2t^* - 2t_{\text{check}} \equiv 0 \pmod q$. | **0.0% (Universal Blindness)** | Reconstructed ciphertext $c' \neq c$; caught 100% by outer FO re-encryption check. |
| **Symmetric Output Fault ($\Delta r_0 = \Delta r_1 = \delta$)** | Sum check: $2u + 2\delta \not\equiv 2u$ (DETECTED). Difference check: $(r_0+\delta) - (r_1+\delta) = 2t$ (BLIND). | **100.0% (Detected by Sum Check)** | Local monitor detects and repairs. |
| **Antisymmetric Output Fault ($\Delta r_0 = -\Delta r_1 = \delta$)** | Sum check: $(r_0+\delta) + (r_1-\delta) = 2u$ (BLIND). Difference check: $(r_0+\delta) - (r_1-\delta) - 2t = 2\delta \not\equiv 0$ (DETECTED). | **100.0% (Detected by Difference Check)** | Local monitor detects and repairs. |
| **Simultaneous Multiplier + Parity Collision** | $\Delta r_0 - \Delta r_1 \equiv 2\Delta t \pmod q$ and $\Delta r_0 + \Delta r_1 \equiv 0 \pmod q$. | $\approx \frac{1}{q} \approx 0.03\%$ | Caught by outer FO re-encryption check. |
| **Snapshot Corruption ($H_1$)** | Corrupted snapshot $u_{\text{saved}}^*$ validates corrupted computation $u^*$. | **0.0% (Verifier Blindness)** | Caught by outer FO re-encryption check. |

---

## 3. Strict Security Taxonomy: Six Essential Distinctions

To ensure rigor and avoid overclaiming in academic manuscripts, the capabilities of the architecture must be classified across six distinct technical concepts:

```
+-------------------------------------------------------------------------+
|                        CRYPTOGRAPHIC SECURITY                           |
|                                                                         |
|  1. FAULT DETECTION         2. FAULT CORRECTION     3. ERROR CONTAINMENT|
|     (Parity check in           (In-place register      (Fail-stop FIPS  |
|      butterfly monitors)        rollback & retry)       203 rejection)  |
|                                                                         |
|  4. AVAILABILITY            5. CONFIDENTIALITY      6. SIDE-CHANNEL     |
|     (100/100 transient         (Zero key leakage       RESISTANCE       |
|      recoveries, no drop)       under Poisson SEU)     (No TVLA/dudect) |
+-------------------------------------------------------------------------+
```

1. **Fault Detection:** Identifying that an invariant violation has occurred ($\text{diff\_c} \neq 0 \lor \text{sum\_c} \neq 0$). Verified: 100% detection for evaluated arithmetic faults.
2. **Fault Correction:** Localized rollback restoring authentic register state and recomputing the butterfly ($N_{\text{retry}} = 1$). Verified: 100/100 for transient multiplier faults ($F4$).
3. **Error Containment:** Forcing execution into safe implicit rejection ($K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$) whenever recovery fails or persistent faults ($F5A, F5B$) occur. Verified: 200/200 trials.
4. **Availability:** Preventing unnecessary session termination or dropped telecommands in benign space environments.
5. **Confidentiality:** Preventing secret key exposure through decapsulation outputs. Under non-adversarial Poisson arrivals, confidentiality is preserved (zero SDC). Under active physical adversaries, confidentiality is **not preserved** due to SIFA.
6. **Side-Channel Resistance:** Certified constant-time behavior across all paths. **NOT CLAIMED.** Recovery paths branch conditionally upon error; no TVLA or dudect testing has been performed on the compiled binary.
