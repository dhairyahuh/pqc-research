# Phase 7I: Mathematical Derivation of Gentleman–Sande Inverse NTT Invariants

## 1. Algorithmic Context & Butterfly Structure

In NIST FIPS 203 ML-KEM-768, polynomial multiplication requires transforming coefficients between the standard polynomial domain $R_q = \mathbb{Z}_q[X]/(X^{256} + 1)$ and the Number Theoretic Transform (NTT) domain. While forward NTT converts time-domain coefficients to frequency-domain vectors using Cooley-Tukey (CT) decimation-in-time butterflies, the inverse NTT converts frequency-domain vectors back to the polynomial ring using **Gentleman-Sande (GS) decimation-in-frequency butterflies**.

In `algorithms/source_ref/mlkem/src/poly.c` (`mlk_invntt_layer`), each butterfly executes:

```c
int16_t t = r[j];
r[j] = mlk_barrett_reduce((int16_t)(t + r[j + len]));
r[j + len] = (int16_t)(r[j + len] - t);
r[j + len] = mlk_fqmul(r[j + len], zeta);
```

### Algebraic Formulation
Let inputs be $u = r[j]$ and $v = r[j + \text{len}]$, with twiddle factor $\zeta \in \mathbb{Z}_q$.
1. **First Output (Adder)**:
   $$u' = u + v \pmod q$$
2. **Intermediate Difference**:
   $$d = v - u \pmod q$$
3. **Second Output (Multiplier)**:
   $$v' = \text{fqmul}(d, \zeta) = (v - u) \cdot \zeta \cdot R^{-1} \pmod q$$
where $q = 3329$ and Montgomery constant $R = 2^{16} \equiv 2285 \pmod q$.

---

## 2. Fundamental Mathematical Distinction from Cooley-Tukey

In the Cooley-Tukey forward butterfly:
$$t_{\text{CT}} = v \cdot \zeta \cdot R^{-1}, \quad u' = u + t_{\text{CT}}, \quad v' = u - t_{\text{CT}}$$
Because both outputs share $t_{\text{CT}}$, the difference satisfies $(u' - v') = 2t_{\text{CT}}$.

In the Gentleman-Sande inverse butterfly:
- Addition and subtraction occur **before** multiplication.
- Output $u' = u + v$ does **not** depend on $\zeta$.
- Output $v' = (v - u) \cdot \zeta \cdot R^{-1}$ depends on $\zeta$.
- **Theorem (Impossibility of Multiplication-Free Invariant for $v'$)**:
  There exists no linear algebraic combination of $u'$ and $v'$ over $\mathbb{Z}_q$ that cancels $\zeta$ without modular multiplication by $\zeta$ or $\zeta^{-1}$.
  *Proof*: Suppose $c_1 u' + c_2 v' = f(u, v)$ for constants $c_1, c_2$ independent of $\zeta$. Then $c_1(u + v) + c_2(v - u)\zeta R^{-1}$ must be constant with respect to $\zeta$. Since $(v - u) \not\equiv 0$ in general, $\frac{\partial}{\partial \zeta} (c_2 (v - u) \zeta R^{-1}) = c_2 (v - u) R^{-1} = 0 \implies c_2 = 0$. Hence $v'$ cannot be checked without multiplication.

---

## 3. Derivation of the Dual Invariant for Gentleman-Sande

We establish the following dual invariant system for $(u', v')$:

### Invariant 1: Adder Output Invariant ($S$)
$$S = u' - (u_{\text{saved}} + v_{\text{saved}}) \pmod q \equiv 0$$
- **Computational Cost**: 1 addition, 1 subtraction modulo $q$ (0 multiplications).
- **Target Loci**: Catches faults in $u'$, in the adder ALU, and symmetric perturbations.

### Invariant 2: Multiplier Output Recomputed Invariant ($D$)
$$d_{\text{check}} = v_{\text{saved}} - u_{\text{saved}} \pmod q$$
$$v'_{\text{expected}} = \text{fqmul}(d_{\text{check}}, \zeta)$$
$$D = v' - v'_{\text{expected}} \pmod q \equiv 0$$
- **Computational Cost**: 1 Montgomery multiplication (`fqmul`), 1 subtraction modulo $q$.
- **Target Loci**: Catches faults in $v'$, intermediate difference $d$, and multiplier ALU.

---

## 4. Fault Detection Kernel & Blind Spot Analysis

| Fault Mechanism | Algebraic Perturbation | Invariant $S$ Evaluation | Invariant $D$ Evaluation | Detected? |
| :--- | :--- | :--- | :--- | :--- |
| **Output $u'$ Bit Flip** | $u^* = u' \oplus \delta$ | $S = \delta \not\equiv 0$ | $D = 0$ | **Yes** (via $S$) |
| **Intermediate Difference $d$** | $d^* = d \oplus \delta$ | $S = 0$ | $D = \text{fqmul}(\delta, \zeta) \not\equiv 0$ | **Yes** (via $D$) |
| **Output $v'$ Bit Flip** | $v^* = v' \oplus \delta$ | $S = 0$ | $D = \delta \not\equiv 0$ | **Yes** (via $D$) |
| **Symmetric Output ($+\Delta, +\Delta$)** | $u^* = u' + \Delta, v^* = v' + \Delta$ | $S = \Delta \not\equiv 0$ | $D = \Delta \not\equiv 0$ | **Yes** (via $S$ and $D$) |
| **Anti-Symmetric Output ($+\Delta, -\Delta$)** | $u^* = u' + \Delta, v^* = v' - \Delta$ | $S = \Delta \not\equiv 0$ | $D = -\Delta \not\equiv 0$ | **Yes** (via $S$ and $D$) |
| **Twiddle Factor $\zeta$** | $\zeta^* = \zeta \oplus \delta$ | $S = 0$ | $D = 0$ (Shared $\zeta^*$) | **Blind Spot** (Handled by FO) |
| **Pre-Butterfly Input $u$ or $v$** | $u^* = u \oplus \delta$ | $S = 0$ (Valid math on bad input) | $D = 0$ | **Blind Spot** (Handled by FO) |

### Key Theoretical Conclusion
The dual invariant $(S, D)$ provides 100% mathematical coverage against any single transient arithmetic perturbation occurring in the adder, subtractor, intermediate difference register, or multiplier during the inverse butterfly. Shared operand defects ($\zeta, u_{\text{saved}}, v_{\text{saved}}$) escape arithmetic invariants and rely on the Fujisaki-Okamoto re-encryption barrier.
