# Phase 6B: Novelty and Research Contribution Reassessment

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Phase:** 6B — Independent Adversarial Validation and Scientific Audit  
**Date:** October 1, 2026  
**Status:** COMPLETED  

---

## 1. Literature Context and Prior Art Review

Phase 6 categorized Candidate B (FIPS 203 Incomplete NTT Algebraic Projection Invariant) as a *"New Mathematical Analysis & Application"*. We conduct a rigorous peer-review audit of this classification against established literature.

### 1.1 Algorithm-Based Fault Tolerance (ABFT) Foundation
- **Huang & Abraham (1984):** *"Algorithm-Based Fault Tolerance for Matrix Operations"* (IEEE Trans. Computers). Introduced linear checksum vectors for matrix operations ($\mathbf{c}^T A$).
- **Jou & Abraham (1986):** *"Fault-Tolerant FFT Networks"*. Extended checksum linear invariants to Fast Fourier Transform networks, establishing that input sum vectors project linearly through butterfly stages.
- **Antelo et al. (1998):** *"Use of linear checksums in fault-tolerant FFTs"*. Proved that linear combinations of FFT outputs correspond to evaluations of the polynomial at roots of unity.

### 1.2 NTT Checksums in Lattice-Based Cryptography
- **Sarker et al. (2020), Roy et al. (2019):** Applied ABFT linear checksums to Number Theoretic Transforms in lattice cryptography (Kyber, Dilithium, NewHope).
- **Standard Complete NTT Checksum:** In a complete 8-layer NTT where $X^N+1$ factors completely into linear roots $(X - \zeta_i)$, evaluating at $X=1$ yields the total sum:
  $$\sum_{i=0}^{N-1} \hat{a}_i \equiv a(1) \pmod q$$
  This identity is well-established in the literature.

---

## 2. Precise Scientific Demarcation: What is Known vs. What is Distinct

| Concept / Technique | Prior Art Status | This Project's Contribution |
|:---|:---|:---|
| **Linear Projection Invariants for Transforms** | **ESTABLISHED (Jou & Abraham 1986)** | Standard ABFT methodology applied to modular arithmetic. |
| **Sum Invariants for Complete NTTs ($\sum \hat{a} \equiv a(1)$)** | **ESTABLISHED (Sarker 2020)** | Recognized that this naive formula fails on FIPS 203. |
| **Quadratic Factoring Projection for FIPS 203 Incomplete NTT** | **PROJECT DERIVATION & APPLICATION** | Derived the specific even/odd index projection identities ($\sum \hat{p}_{2i} \equiv 128 p_0$) arising from quadratic irreducible factors $(X^2 - \zeta)$. |
| **Universal Parity Cancellation (The Blind Spot)** | **NEW AUDIT DISCOVERY (Phase 6B)** | Proved mathematically and empirically that intermediate butterfly multiplier faults ($t$) cancel completely in incomplete Cooley-Tukey NTTs because length is always even. |

---

## 3. Revised Novelty Assessment

- **Correction of Phase 6 Overstatement:**
  - Calling Candidate B a wholly "new mathematical analysis" overstated novelty. The underlying mathematical mechanism is a classical Fourier projection onto the 0th and 1st Fourier basis components, which is a known instantiation of ABFT.
- **Defensible Scientific Contribution:**
  1. **Concrete Derivation for FIPS 203:** Adapting linear ABFT to the specific 7-layer incomplete quadratic factorization of NIST FIPS 203 ($q=3329$).
  2. **Rigorous Characterization of the Parity Cancellation Blind Spot:** Demonstrating that while projection invariants achieve +7.4% overhead, they have an inherent 0.0% detection rate for intermediate butterfly multipliers (`INTERMEDIATE_T`), disproving the assumption that ABFT projections protect against internal ALU glitches.
  3. **Classification:** **ENGINEERING APPLICATION & EXTENDED SCIENTIFIC CHARACTERIZATION** (rather than foundational novelty).
