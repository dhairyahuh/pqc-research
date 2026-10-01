# Phase 7K: Mathematical Verification of Transform Invariants

## 1. Mathematical Domain & Trusted Foundation

Transform monitoring in ML-KEM-768 operates over the finite prime field:
$$\mathbb{F}_q = \mathbb{Z}/3329\mathbb{Z}, \quad q = 3329$$
Montgomery arithmetic employs the constant $R = 2^{16} \equiv 2285 \pmod q$ with multiplicative inverse $R^{-1} \equiv 169 \pmod q$.

### Explicit Trust Assumptions:
1. **Local Register Capture**: The monitor assumes that local shadow variables $u_{\text{saved}}$ and $v_{\text{saved}}$ accurately preserve the register state present at butterfly invocation.
2. **Twiddle Table Constants**: The twiddle factor $\zeta \in \mathbb{F}_q^\times$ is assumed to be correctly read from the precomputed constant table in read-only memory.

---

## 2. Forward Cooley–Tukey NTT Invariant Derivation

In Cooley–Tukey decimation-in-time butterflies:
$$\begin{aligned}
t  &= \text{fqmul}(v, \zeta) \equiv v \cdot \zeta \cdot R^{-1} \pmod q \\
u' &= u + t \pmod q \\
v' &= u - t \pmod q
\end{aligned}$$

### Invariant 1: Forward Difference Invariant ($D_{\text{CT}}$)
$$D_{\text{CT}} = (u' - v' - 2 \cdot t_{\text{check}}) \pmod q \equiv 0$$
where $t_{\text{check}} = \text{fqmul}(v_{\text{saved}}, \zeta)$.
- **Derivation**: $u' - v' = (u + t) - (u - t) = 2t$.
- **Detection Scope**: Detects faults in intermediate product $t$, output registers $u'$ or $v'$, and anti-symmetric perturbations.
- **Blind Spot**: Symmetric perturbations $(u' + \Delta, v' + \Delta)$ evaluate to $(u'+\Delta) - (v'+\Delta) = u' - v'$, canceling $\Delta$.

### Invariant 2: Forward Sum Invariant ($S_{\text{CT}}$)
$$S_{\text{CT}} = (u' + v' - 2 \cdot u_{\text{saved}}) \pmod q \equiv 0$$
- **Derivation**: $u' + v' = (u + t) + (u - t) = 2u$.
- **Detection Scope**: Directly detects symmetric perturbations $(u'+\Delta, v'+\Delta)$ where $\Delta \neq 0$.
- **Complementarity**: $\ker(D_{\text{CT}}) \cap \ker(S_{\text{CT}}) = \{ (0, 0) \}$.

---

## 3. Inverse Gentleman–Sande NTT Invariant Derivation

In Gentleman–Sande decimation-in-frequency butterflies:
$$\begin{aligned}
u' &= \text{barrett\_reduce}(u + v) \equiv u + v \pmod q \\
d  &= v - u \pmod q \\
v' &= \text{fqmul}(d, \zeta) \equiv (v - u) \cdot \zeta \cdot R^{-1} \pmod q
\end{aligned}$$

### Invariant 1: Adder Output Sum Check ($S_{\text{GS}}$)
$$S_{\text{GS}} = (u' - (u_{\text{saved}} + v_{\text{saved}})) \pmod q \equiv 0$$
- **Derivation**: Follows directly from $u' \equiv u + v \pmod q$.
- **Arithmetic Cost**: 1 addition, 1 subtraction (0 modular multiplications).
- **Detection Scope**: Detects adder ALU faults, non-modular Barrett outputs, and perturbations in $u'$.

### Invariant 2: Multiplier Output Recomputed Check ($D_{\text{GS}}$)
$$D_{\text{GS}} = (v' - \text{fqmul}(v_{\text{saved}} - u_{\text{saved}}, \zeta)) \pmod q \equiv 0$$
- **Derivation**: Follows from $v' \equiv (v - u)\zeta R^{-1} \pmod q$.
- **Arithmetic Cost**: 1 subtraction, 1 Montgomery multiplication (`fqmul`), 1 subtraction.
- **Detection Scope**: Detects multiplier ALU faults, difference register glitches, and perturbations in $v'$.

---

## 4. Scope and Precision of the Twiddle Impossibility Theorem

Phase 7J proved that $v'$ cannot be checked without modular multiplication by $\zeta$. In Phase 7K, we rigorously define the **exact scope and boundary** of this theorem:

### Clarified Scope:
1. **Affine Invariants**: The theorem rigorously proves that for any **affine polynomial relation** of the form $\alpha u' + \beta v' - \gamma(u, v) \equiv 0 \pmod q$, the coefficient $\beta$ must be zero ($\beta \equiv 0$) if the relation is to hold independently of $\zeta$.
2. **Non-Linear Combinations**: Higher-degree polynomial combinations (e.g., $u'^k v'^m$) likewise retain powers of $\zeta$ ($v'^m \propto \zeta^m$). Because the 128 twiddle factors $\zeta$ span 128 distinct non-zero field elements, any polynomial identity in $(u', v', u, v)$ that holds for all $\zeta$ without evaluating $\zeta$ must have all coefficients of $\zeta$-dependent monomials vanish identically.
3. **Small-Domain Verification**: The theorem was verified exhaustively across all $17 \times 17$ input pairs in $\mathbb{F}_{17}$ via `experiments/phase7k/symbolic_math_verification.py`, confirming zero false generalizations.

### Publication Claim Wording:
> *"Within the algebra of affine polynomial relations over $\mathbb{F}_q$, no invariant can evaluate the correctness of the second Gentleman–Sande butterfly output $v'$ without explicitly incorporating the twiddle factor $\zeta$ through modular multiplication."*
