# Phase 7J: Mathematical Re-Derivation of Inverse NTT Invariants

## 1. Algebraic Domain & Butterfly Structure

In NIST FIPS 203 ML-KEM-768, polynomial arithmetic takes place in the cyclotomic quotient ring:
$$R_q = \mathbb{Z}_q[X]/(X^{256} + 1), \quad q = 3329$$
The prime $q = 3329$ satisfies $q \equiv 1 \pmod{256}$, guaranteeing the existence of primitive 256-th roots of unity in $\mathbb{F}_q = \mathbb{Z}/3329\mathbb{Z}$.

The inverse Number Theoretic Transform converts coefficients from the NTT domain back to the standard polynomial basis using **Gentleman–Sande (GS) decimation-in-frequency butterflies**.

In `algorithms/source_ref/mlkem/src/poly.c` (`mlk_invntt_layer`), each butterfly operates on two coefficient registers:
$$u = r[j], \quad v = r[j + \text{len}], \quad \zeta \in \mathbb{F}_q^\times$$

The implemented operations are:
$$\begin{aligned}
u' &= \text{barrett\_reduce}(u + v) \equiv u + v \pmod q \\
d  &= v - u \pmod q \\
v' &= \text{fqmul}(d, \zeta) \equiv (v - u) \cdot \zeta \cdot R^{-1} \pmod q
\end{aligned}$$
where $R = 2^{16} \equiv 2285 \pmod q$ is the Montgomery constant, and $R^{-1} = 169 \pmod q$.

---

## 2. Rigorous Algebraic Impossibility Theorem

Phase 7I provided an informal derivative argument to explain why $v'$ cannot be checked without modular multiplication by $\zeta$. In an audit of finite field arithmetic, differentiation is purely formal. We provide here a **rigorous algebraic proof using polynomial identities over $\mathbb{F}_q$**.

### Theorem (Impossibility of $\zeta$-Free Linear Invariant for $v'$):
Let $\mathbb{F}_q$ be the finite field of order $q = 3329$. Let $(u, v) \in \mathbb{F}_q \times \mathbb{F}_q$ be arbitrary butterfly inputs, and let $\zeta \in \mathcal{Z} \subset \mathbb{F}_q^\times$ be the set of twiddle factors ($|\mathcal{Z}| = 128$).  
Suppose there exists a non-trivial affine polynomial relation:
$$L(u', v') = \alpha u' + \beta v' - \gamma(u, v) \equiv 0 \pmod q$$
where $\alpha, \beta \in \mathbb{F}_q$ and $\gamma: \mathbb{F}_q \times \mathbb{F}_q \to \mathbb{F}_q$ are independent of $\zeta$.  
Then $\beta \equiv 0 \pmod q$.

### Proof:
Substitute the nominal butterfly expressions for $u'$ and $v'$ into $L$:
$$\alpha (u + v) + \beta (v - u) \zeta R^{-1} - \gamma(u, v) \equiv 0 \pmod q$$
This equation must hold for all twiddle factors $\zeta \in \mathcal{Z}$.  
Because $|\mathcal{Z}| = 128 \ge 2$, choose two distinct twiddle factors $\zeta_1, \zeta_2 \in \mathcal{Z}$ with $\zeta_1 \not\equiv \zeta_2 \pmod q$.  
Evaluating the equation at $\zeta_1$ and $\zeta_2$ and subtracting:
$$\beta (v - u) (\zeta_1 - \zeta_2) R^{-1} \equiv 0 \pmod q$$
Since $q$ is prime, $\mathbb{F}_q$ is a field and has no non-zero zero-divisors:
1. By assumption, $\zeta_1 \not\equiv \zeta_2 \pmod q$, so $(\zeta_1 - \zeta_2) \neq 0$.
2. The Montgomery constant $R = 2^{16}$ is coprime to $q = 3329$, so $R^{-1} \neq 0$.
3. For general inputs where $u \not\equiv v \pmod q$, $(v - u) \neq 0$.

Therefore, the product $\beta \cdot (v - u) \cdot (\zeta_1 - \zeta_2) \cdot R^{-1} = 0$ implies:
$$\beta \equiv 0 \pmod q \quad \blacksquare$$

### Corollary:
Any candidate invariant that does not depend on $\zeta$ reduces to $\alpha (u + v) - \gamma(u, v) \equiv 0$, which evaluates only $u'$ and has zero mathematical sensitivity to faults in $v'$, $d$, or $\zeta$. Consequently, **any check verifying $v'$ must perform modular multiplication by $\zeta$ (or $\zeta^{-1}$)**.

---

## 3. Kernel and Detection Sensitivity of the Dual Invariants

The implemented monitor in `mlkem_fault_hooks.c` applies two decoupled invariants:

### 3.1. Adder Output Sum Check ($S$)
$$S = u' - (u_{\text{saved}} + v_{\text{saved}}) \pmod q$$
- **Fault Detection Kernel**: $\ker(S) = \{ (\Delta u', \Delta v') \in \mathbb{F}_q^2 \mid \Delta u' \equiv 0 \pmod q \}$.
- **Sensitivity**: Detects any perturbation where $\Delta u' \not\equiv 0 \pmod q$.
- **Cost**: 1 addition, 1 subtraction (0 modular multiplications).

### 3.2. Multiplier Recomputed Check ($D$)
$$d_{\text{check}} = v_{\text{saved}} - u_{\text{saved}} \pmod q$$
$$v'_{\text{expected}} = \text{fqmul}(d_{\text{check}}, \zeta)$$
$$D = v' - v'_{\text{expected}} \pmod q$$
- **Fault Detection Kernel**: $\ker(D) = \{ (\Delta u', \Delta v') \in \mathbb{F}_q^2 \mid \Delta v' \equiv 0 \pmod q \}$.
- **Sensitivity**: Detects any perturbation where $\Delta v' \not\equiv 0 \pmod q$.
- **Cost**: 1 subtraction, 1 Montgomery multiplication (`fqmul`), 1 subtraction.

### 3.3. Combined Dual Kernel
$$\ker(S) \cap \ker(D) = \{ (0, 0) \} \subset \mathbb{F}_q^2$$
Every non-zero arithmetic perturbation $(\Delta u', \Delta v') \neq (0, 0)$ is detected by at least one of the two checks, completely closing the single-rail cancellation blind spots.

---

## 4. Shared Operands and Explicit Common-Mode Assumptions

The independent audit confirms that the dual invariant relies on the following explicit structural assumptions:
1. **Shared Input Operands**:
   The checker uses shadow variables $u_{\text{saved}}$ and $v_{\text{saved}}$ captured at butterfly entry. If an electrical glitch corrupts the memory bus before entry, both the butterfly and the checker receive the same corrupted input $(u_{\text{fault}}, v_{\text{fault}})$. The invariant evaluates to 0. (Downstream Fujisaki–Okamoto re-encryption catches this).
2. **Shared Twiddle Factor ($\zeta$)**:
   The checker reads the same twiddle factor $\zeta$ as the butterfly. A bit-flip in the twiddle factor table scales both the forward/inverse arithmetic and the checker identically ($v' = d \cdot \zeta_{\text{corrupt}}$, $v'_{\text{expected}} = d_{\text{check}} \cdot \zeta_{\text{corrupt}}$), evading the local invariant ($D = 0$).
3. **Correlated Arithmetic/Checker Faults**:
   If an adversary injects identical perturbations into the output register and the expected checker value ($\Delta v' = \Delta v'_{\text{expected}}$), the difference $(v' + \Delta) - (v'_{\text{expected}} + \Delta) = 0$ modulo $q$.
