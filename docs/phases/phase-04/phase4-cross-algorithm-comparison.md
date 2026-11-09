# Phase 4 — Cross-Algorithm Comparison & Comparability Analysis

**Project Title:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Standards:** NIST FIPS 203 (ML-KEM) & NIST FIPS 204 (ML-DSA)  
**Document Version:** 1.0.0-CROSS-ALGO  
**Date:** October 1, 2026  
**Status:** COMPLETE & INDEPENDENTLY AUDITED  

---

## 1. Executive Summary

Phase 4 establishes the first rigorous, evidence-based comparative framework contrasting implementation-level fault propagation across **ML-KEM** (Key Encapsulation Mechanism) and **ML-DSA** (Digital Signature Algorithm).

A foundational mandate of this audit is to avoid the methodological trap of pooling experimental outcome percentages across incompatible interfaces. Instead, cross-algorithm evaluation is strictly structured using a **4-tier Comparability Classification**:
1. **Directly Comparable:** Experiments sharing identical algebraic operators and execution metrics.
2. **Comparable with Normalization:** Experiments sharing architectural intent but requiring mathematical normalization.
3. **Qualitatively Comparable:** Experiments sharing high-level security concepts that differ in concrete implementation.
4. **Not Comparable:** Distinct algorithmic mechanisms that cannot be mapped without introducing false equivalence.

---

## 2. Cross-Algorithm Comparability Matrix

| Dimension / Mechanism | Comparability Category | ML-KEM (FIPS 203) Behavior | ML-DSA (FIPS 204) Behavior | Methodological Reconciliation & Audit Findings |
|:---|:---:|:---|:---|:---|
| **Baseline Integrity & Zero-Glitch Controls** | `DIRECTLY_COMPARABLE` | 100.0% `CORRECT` across 512, 768, 1024 ($N=1000$ each). Zero overhead when injector inactive. | 100.0% `CORRECT` across 44, 65, 87 ($N=1000$ each). Zero overhead when injector inactive. | **Directly Comparable.** Both baselines confirm that compiler optimization (`-O3`), memory alignment, and inactive harness structures introduce zero functional artifact. |
| **Forward NTT Butterfly Diffusion Tree** | `DIRECTLY_COMPARABLE` | 7-layer incomplete NTT ($X^{256}+1 \to 128$ quadratic factors). Layer $L$ diffuses across $2^{8-L}$ (shared) and $2^{7-L}$ (single) coefficients. | 8-layer complete NTT ($X^{256}+1 \to 256$ linear factors). Layer $L$ diffuses across $2^{9-L}$ (shared) and $2^{8-L}$ (single) coefficients. | **Directly Comparable.** Both follow identical binary tree propagation laws down to irreducible ring factors. ML-DSA extends one layer deeper because $q \equiv 1 \pmod{512}$ enables degree-1 factoring. |
| **Secret-Key Memory Region Decomposition** | `COMPARABLE_WITH_NORMALIZATION` | Private vector $\mathbf{s} \to$ `IMPLICIT_REJECTION`; Public key $pk/H(pk) \to$ `EXPLICIT_ERROR`; Rejection seed $z \to$ `CORRECT`. | Private vectors $\mathbf{s}_1, \mathbf{s}_2 \to$ `ATTEMPT_EXHAUSTION`; Public parameters $\rho, tr, \mathbf{t}_0 \to$ `INVALID_SIGNATURE`; PRF seed $K \to$ `CORRECT` (det). | **Comparable with Normalization.** Corruptions in secret polynomial vectors consistently induce fail-closed execution in both schemes (implicit rejection fallback vs. signing loop attempt budget exhaustion). |
| **Fault Magnitude & Arithmetic Sensitivity** | `COMPARABLE_WITH_NORMALIZATION` | Algebraic decoding slack budget ($\lfloor q/4 \rfloor = 832$). Faults with $|\Delta| \le 12$ are completely masked; $|\Delta| \ge 13$ trigger implicit rejection. | Zero arithmetic slack during verification. Any arithmetic perturbation $\Delta \ge 1$ changes commitment $\mathbf{w}_1$, resulting in 100% verification rejection. | **Comparable with Normalization.** ML-KEM has a bounded continuous error absorption budget in decapsulation; ML-DSA verification is strictly binary and brittle to arithmetic noise. |
| **Containment Failure & Fail-Closed Modes** | `QUALITATIVELY_COMPARABLE` | Fails closed via Fujisaki-Okamoto implicit rejection, outputting pseudorandom session key $K_{\text{rej}} = H(z, c)$. | Fails closed via rejection sampling attempt budget exhaustion (`MLD_ERR_SIGN_ATTEMPTS_EXHAUSTED`). | **Qualitatively Comparable.** Both schemes prevent direct plaintext secret emission under arithmetic faults, but through fundamentally distinct operational modes (silent desync vs. explicit loop termination). |
| **Decision Variable Override Vulnerability** | `QUALITATIVELY_COMPARABLE` | Inverting FO verification flag (`fail: 1 -> 0`) selects $K_{\text{cand}}$ instead of $K_{\text{rej}}$, producing candidate key mismatch. | Inverting verification comparison flag (`cmp: 1 -> 0`) causes invalid signature to return success (`VERIFICATION_ACCEPT`). | **Qualitatively Comparable.** Both represent software execution / control-flow overrides on a binary variable. Neither constitutes a mathematical cryptographic break or signature forgery. |
| **Rejection Sampling vs. Fujisaki-Okamoto Transform** | `NOT_COMPARABLE` | Deterministic decapsulation pass with re-encryption hash equality comparison. | Iterative stochastic loop checking infinity-norm bounds ($\|z\|_\infty < \gamma_1 - \beta$, $\|w_0\|_\infty < \gamma_2 - \beta$). | **Not Comparable.** Raw outcome counts cannot be statistically pooled. One is an algebraic consistency check; the other is a statistical zero-knowledge distribution firewall. |
| **Ciphertext Compression vs. Signature Hints** | `NOT_COMPARABLE` | Non-linear lossy quantization $\text{Compress}_d(x)$ with dynamic boundary margins. | Exact high-bits extraction $\text{HighBits}(r)$ with explicit auxiliary hint vectors $\mathbf{h}$. | **Not Comparable.** Quantization error absorption does not exist in ML-DSA ($q=8380417$ is uncompressed); hint bit corruption has no analog in ML-KEM. |

---

## 3. Deep-Dive Comparative Dimensions

### 3.1 Ring Arithmetic and NTT Architectures
Both algorithms leverage cyclotomic rings, but their structural choices dictate divergent fault diffusion:
- **ML-KEM:** The modulus $q = 3329$ satisfies $q \equiv 1 \pmod{256}$, but does **not** split completely over linear factors in $\mathbb{Z}_q$. Consequently, its forward NTT terminates after 7 layers, leaving 128 quadratic polynomial factors of degree 1. A single output register fault in Layer 7 affects exactly 1 coefficient, but Montgomery base multiplication operates on blocks of 2 coefficients.
- **ML-DSA:** The modulus $q = 8,380,417$ satisfies $q \equiv 1 \pmod{512}$, permitting complete factorization into 256 degree-1 linear factors across 8 layers. A fault in Layer 8 affects a single coefficient, and subsequent base multiplication is strictly pointwise scalar multiplication.

**Comparative Takeaway:** Error propagation in ML-DSA forward NTT reaches all 256 ring coefficients at Layer 1 ($2^{9-1} = 256$), whereas ML-KEM's incomplete NTT reaches a maximum of 128 coefficients ($2^{8-1} = 128$) before the quadratic base-multiplication stage.

### 3.2 Error Containment: Continuous Slack vs. Discrete Norm Bounds
The most pronounced operational divergence between the two standards lies in how they handle computational errors:
- **ML-KEM (Continuous Decoding Slack):**
  ML-KEM decapsulation is inherently an approximate computation. It computes $w = v - \mathbf{s}^T \mathbf{u} \pmod q$, where $w$ contains both the message signal and accumulated LWE noise. 
  Because message decoding rounds coefficients to the nearest multiple of $q/2$, any computational perturbation that leaves $\|e_{\text{time}}\|_\infty < 832.25$ is **completely absorbed**. As formally audited in Phase 4, this grants ML-KEM decapsulation an intrinsic tolerance margin ($|\Delta| \le 12$ in Layer 1 single register).
- **ML-DSA (Discrete Norm Boundary & Hash Firewall):**
  ML-DSA contains two distinct containment mechanisms:
  1. *Signing (Rejection Sampling):* The signer iteratively samples candidates $\mathbf{y}$ and checks whether the response $\mathbf{z} = \mathbf{y} + c \mathbf{s}_1$ falls strictly within the $L_\infty$ hypercube of radius $\gamma_1 - \beta$. Arithmetic perturbations that inflate $\|\mathbf{z}\|_\infty$ beyond this hypercube trigger immediate rejection retries. If the fault persists, all attempts exhaust, terminating execution cleanly.
  2. *Verification (Zero Arithmetic Slack):* Verification reconstructs the commitment $\mathbf{w}_1 = \text{UseHint}(\mathbf{A}\mathbf{z} - c\mathbf{t}_1 \cdot 2^d, \mathbf{h})$ and evaluates the cryptographic hash $c_2 = H(\mu, \mathbf{w}_1)$. Because cryptographic hash functions have zero error tolerance, any arithmetic perturbation in $\mathbf{z}$, $\mathbf{A}$, or $\mathbf{t}_1$ produces an unpredictable 256-bit challenge $c_2$, resulting in immediate rejection with probability $1 - 2^{-256}$.

### 3.3 Security Implications of Failure Modes
The operational consequences of containment failure diverge significantly:
- When ML-KEM decapsulation fails closed, it outputs a deterministic pseudorandom fallback key $K_{\text{rej}} = H(z, c)$. The software does **not** raise an exception or return an error code. To downstream systems, the decapsulation appears successful, but the session is silently desynchronized.
- When ML-DSA signing fails closed, it returns an explicit error code (`MLD_ERR_SIGN_ATTEMPTS_EXHAUSTED`), signaling an operational failure to the spacecraft system.
- When ML-DSA verification fails, it explicitly returns `MLD_ERR_INVALID_SIGNATURE`, enabling the system to immediately reject the unauthenticated packet.

---

## 4. Synthesis and Guidelines for Cross-Algorithm Engineering

1. **Never Pool Outcome Frequencies:** A research claim that "ML-KEM has 95% resilience while ML-DSA has 10% resilience" is mathematically meaningless because the failure modes (implicit key mismatch vs. attempt exhaustion) represent different operational states.
2. **Selective Redundancy Must Be Algorithm-Specific:**
   - In **ML-KEM**, protective checksums are unnecessary in Layer 1 single registers for small glitches ($|\Delta| \le 12$), but are critical in Layers 2–7 and on shared intermediates $t$.
   - In **ML-DSA**, arithmetic checksums are critical throughout verification because verification has zero error slack. In signing, redundancy should focus on preventing infinite rejection loops or attempt budget exhaustion.
3. **Control-Flow Integrity Is Universally Critical:**
   - Both algorithms share a common vulnerability to Boolean decision-variable overrides (`fail = 0` in ML-KEM; `cmp = 0` in ML-DSA). Software-level fault countermeasures (such as double-evaluation or complementary condition variables) provide high value across both algorithms.
