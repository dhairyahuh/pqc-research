# Phase 6: Empirical and Mathematical Evidence Validation

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Phase:** 6 — Targeted Software Resilience Prototyping and Evaluation  
**Date:** October 1, 2026  
**Status:** COMPLETED  

---

## 1. Objective and Audit Scope

Before prototyping candidate software resilience countermeasures, this audit examines the empirical and mathematical evidence established across Phases 1 through 5. It reconciles apparent tensions in reported datasets, clarifies physical fault-to-cryptographic mapping boundaries, refines compiler sensitivity interpretations, and evaluates the experimental justification for each proposed countermeasure.

---

## 2. ML-KEM Implicit Rejection and Fujisaki-Okamoto Behavior

### 2.1 Reconciling Empirical Findings
Prior phases reported two seemingly divergent sets of observations:
1. **100% Implicit Rejection Rate:** In Phase 2, Phase 4, and Phase 5, injecting arithmetic faults into NTT layers, twiddle factors, or polynomial multiplication accumulators during decapsulation consistently produced 100.0% implicit rejection (0 correct decapsulations, 0 explicit crashes).
2. **~60% Garbled Key Divergence:** Under the Phase 2/4/5 Fujisaki-Okamoto (FO) predicate bypass test, an injected 1-byte ciphertext corruption coupled with a forced validation pass produced a garbled key in ~60% of trials, while ~40% yielded the expected shared secret.

**Scientific Reconciliation:**
These results are **not contradictory**; they describe fundamentally different experimental boundaries and fault injection loci:
- In the **arithmetic fault campaign**, the ciphertext $c$ presented to the decapsulation engine is completely valid. The fault occurs inside the internal polynomial arithmetic ($u, v, s$). This corrupts the recovered plaintext $m'$. When re-encryption computes $c' = \operatorname{Encaps}(pk, m')$, the resulting ciphertext $c'$ diverges substantially from $c$. The FO comparison $c \stackrel{?}{=} c'$ fails honestly, routing the output to the implicit rejection pseudo-random PRF: $K = \operatorname{J}(z \| c)$.
- In the **FO bypass campaign (B2)**, the ciphertext $c$ was corrupted externally (1 byte altered), but the internal FO check result was artificially forced to `PASS` ($c' \stackrel{?}{=} c \to \text{true}$). Because of Kyber/ML-KEM's error-correcting decoding slack ($q/4 = 832.25$), a single-byte change in the low-order compression bits of $c$ was absorbed during message decoding in ~40% of random seeds, so the decapsulator still recovered the original message $m$. When the FO predicate was forced to accept, the session key derived from $m$ matched the encapsulation key. In the remaining ~60% of seeds, the corruption flipped message bits, yielding an erroneous message $m'$ and producing an out-of-sync garbled session key.

> **CRITICAL SCIENTIFIC RULE:** We explicitly reject the inaccurate claim that *"implicit rejection protects against all faults."* Implicit rejection only guarantees that internal arithmetic faults or invalid ciphertexts fail closed into a deterministic pseudo-random key rather than leaking private key coefficients directly. It does **not** protect against silent session key desynchronization in communications protocols, nor does it protect against control-flow faults that force the FO decision predicate.

### 2.2 Precise Cryptographic Outcome Taxonomy

To prevent methodological ambiguity, all Phase 6 experiments adhere to this 7-class outcome taxonomy:

| Taxonomy Class | Operational Definition | Observable State | Cryptographic Consequence |
|:---|:---|:---|:---|
| **Class 1: Correct Agreement** | Decapsulation outputs true shared secret $K_{\text{true}} = \operatorname{KDF}(K_{\text{bar}} \| H(c))$. | $K_{\text{dec}} = K_{\text{enc}}$ | Session established normally. |
| **Class 2: Implicit Rejection** | Decapsulation detects $c' \neq c$ and computes fallback key $K_{\text{rand}} = \operatorname{J}(z \| c)$. | $K_{\text{dec}} \neq K_{\text{enc}}$, deterministic on $(z, c)$ | Silent session desynchronization; CCA security preserved. |
| **Class 3: Candidate-Key Agreement** | Faulted plaintext $m'$ decodes within slack budget, yielding true key despite internal perturbation. | $K_{\text{dec}} = K_{\text{enc}}$ | Fault absorbed by algorithm slack budget. |
| **Class 4: Candidate-Key Mismatch** | FO predicate forced to `VALID` despite corrupted $m'$, outputting pseudo-valid key $K = \operatorname{KDF}(m' \| H(c))$. | $K_{\text{dec}} \neq K_{\text{enc}}$, neither true nor $K_{\text{rand}}$ | Garbled key divergence; link authentication failure. |
| **Class 5: Explicit Error** | Input validation detects malformed input or length mismatch before cryptographic execution. | Error code returned ($r \neq 0$) | Execution halts safely before processing. |
| **Class 6: Invalid Ciphertext Acceptance** | An adversarially crafted, invalid ciphertext is accepted as valid without triggering rejection. | Cryptographic violation | Catastrophic CCA security failure (IND-CCA2 broken). |
| **Class 7: Direct Predicate Override** | A hardware or software fault flips a single boolean branch condition or return register in memory. | Local variable corrupted | Control-flow bypass; does not produce a valid ciphertext or signature. |

---

## 3. Physical Fault to Algorithmic Mapping Audit

We audit the abstraction layers between physical radiation events and mathematical models:

$$\text{Physical Particle Strike} \longrightarrow \text{Circuit Transistor Upset} \longrightarrow \text{CPU Register / Memory Bit Flip} \longrightarrow \text{Instruction Operand Perturbation} \longrightarrow \text{Polynomial Coefficient Error} \longrightarrow \text{Cryptographic Output}$$

### Mapping Characterization Matrix

| Transition Layer | Mapping Status | Physical Reality vs. Model Assumption |
|:---|:---|:---|
| **SEU $\to$ Machine Register** | **Exact** | Single Event Upsets flip individual bits ($0 \to 1$ or $1 \to 0$) in SRAM cells or register latches. |
| **Register $\to$ Vector Lane** | **Exact on AArch64** | Flipping bit $k$ in a 128-bit NEON vector register (`v0`–`v31`) corrupts exactly one 16-bit lane out of eight. |
| **Vector Lane $\to$ Additive $\delta \in \mathbb{Z}_q$** | **Conditional** | Flipping bit $k$ in an integer register changes value by $\pm 2^k$. Modulo $q=3329$, this maps to $\delta \equiv \pm 2^k \pmod q$. However, an arithmetic glitch in an intermediate multiplier accumulator can produce arbitrary offsets $\delta \not\in \{\pm 2^k\}$. |
| **Vector Fault $\to$ Arbitrary Coeff Error** | **APPROXIMATE (Do Not Conflate)** | Register bit flips have non-uniform distribution modulo $q$ ($2^k \pmod{3329}$). Treating all $\delta \in \mathbb{Z}_q$ as equiprobable is an algorithmic approximation, not an exact physical model. |
| **Coeff Error $\to$ Polynomial Perturbation** | **Exact** | Follows ring arithmetic $\mathbb{Z}_q[X]/(X^{256}+1)$. Linear propagation in NTT and multiplication. |

---

## 4. Reassessment of Compiler and Architecture Claims

Phase 5 demonstrated that output checksums of clean and faulted runs were identical between Apple clang `-O0` and `-O3`. We refine the precise scientific claims:

1. **What the Data ESTABLISHES:**
   - Optimization flags do not alter constant-time modular arithmetic evaluation order or mathematical correctness.
   - For a fixed programmatic injection point (e.g. at the C source hook), the resulting mathematical divergence propagates identically under `-O0` and `-O3`.
2. **What the Data DOES NOT ESTABLISH (Distinctions):**
   - **Physical Fault Exposure Window:** Under `-O0`, intermediate polynomial coefficients reside in stack memory (L1 D-Cache) across function calls, leaving a wide temporal window for memory-bus or cache upsets. Under `-O3`, inner loops keep butterfly operands strictly in CPU registers (`q0`–`q31` / `x0`–`x30`), eliminating memory residency and confining physical vulnerability to register-file exposure.
   - **Control-Flow and Instruction Scheduling:** `-O3` extensively unrolls loops and vectorizes SIMD instructions. A single SEU hitting an instruction decoder or pipeline branch predictor affects different instruction sequences under `-O0` vs `-O3`.

---

## 5. Resilience Priority Evidence Review

We evaluate each proposed candidate countermeasure against our accumulated empirical data:

### 5.1 Candidate A: Selective Duplicate Execution (ML-KEM Decapsulation)
- **Supporting Evidence:** Phases 2–5 proved that 100% of arithmetic faults during decapsulation trigger implicit rejection, leading to silent link desynchronization in space communications.
- **Protected Fault Classes:** Single-event transient arithmetic faults during NTT, BaseMul, or polynomial decoding.
- **Unprotected Fault Classes:** Common-mode faults in shared inputs ($sk, c$), persistent hardware stuck-at faults, faults affecting the comparison logic.
- **Possible False Positives:** None (decapsulation is deterministic given $sk$ and $c$).
- **New Failure Modes:** Fault during second execution could cause false mismatch; decision logic corruption.
- **Complexity & Overhead:** Moderate; +90–100% CPU latency for full duplicate, +30–40% for selective recomputation.

### 5.2 Candidate B: Arithmetic Invariant Checks (NTT & Polynomial Operations)
- **Supporting Evidence:** Phase 1 and Phase 4 proved that NTT butterflies follow strict algebraic linear invariants.
- **Protected Fault Classes:** Single-coefficient and localized multi-coefficient corruptions during polynomial transformations.
- **Unprotected Fault Classes:** Faults that preserve the invariant (e.g., self-canceling perturbations where $\Delta \sum \equiv 0 \pmod q$).
- **Possible False Positives:** Zero, provided modular reductions and representation conversions are mathematically sound.
- **New Failure Modes:** Arithmetic overflow in invariant accumulator; assertion logic fault.
- **Complexity & Overhead:** Low; +5–15% CPU time, negligible memory.

### 5.3 Candidate C: ML-DSA Rejection & Verification Gate Protection
- **Supporting Evidence:** Phase 3 and Phase 5 identified two critical surfaces: (1) rejection loop exhaustion under persistent faults, and (2) single-bit memory corruption of the boolean comparison flag in `verify()`.
- **Protected Fault Classes:** Transient single-bit corruptions of verification comparison result variables; out-of-bounds candidate signatures.
- **Unprotected Fault Classes:** Mathematical forging of lattice parameters; faults during key generation.
- **Complexity & Overhead:** Very low; <2% CPU overhead for multi-rail verification status.

### 5.4 Candidate D: Control-Flow and Multi-Rail Status Integrity
- **Supporting Evidence:** Phase 4 claim audit demonstrated that treating boolean `0` / `1` as decision variables is vulnerable to single-bit memory flips.
- **Protected Fault Classes:** Memory flips in return status codes and decision predicates.
- **Unprotected Fault Classes:** Computational corruption occurring prior to status assignment.
- **Complexity & Overhead:** Negligible; replaces scalar integers with multi-rail Hamming-distance-separated constants (`0x5A5A` / `0xA5A5`).
