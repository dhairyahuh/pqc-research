# Phase 7B Research Contribution and Novelty Reassessment

**Auditor:** Independent Research Methodology Critic  
**Date:** October 2026  
**Focus:** Critical Scrutiny of Claims, Novelty Demarcation, and Research Boundaries  

---

## 1. Categorization of Project Contributions

To maintain strict scientific integrity, we independently classify each Phase 7 contribution:

### A. Genuinely Validated Mathematical Contributions
1. **The Incomplete NTT Universal Parity Cancellation Theorem:**
   - *Status:* **Novel & Mathematically Proved.**
   - Explains why classical ABFT unweighted parity projections fail completely (0% detection) specifically on FIPS 203 ML-KEM. The root cause is the incomplete NTT structure where $\text{len} \ge 2$ is strictly even in all 7 layers, forcing butterfly output pairs to share identical parity indices.
2. **Weighted Inverse-Zeta Projection Derivation:**
   - *Status:* **Mathematically Proved & Validated.**
   - Derives the exact linear projection weights $w_i = \zeta_{2i+1}^{-1}$ from Newton power sums on the roots of $Y^{128} + 1 = 0 \pmod{3329}$, breaking the parity cancellation symmetry at Layer 7.

### B. Engineering Integrations of Known Techniques
1. **Pre-Invocation CRC32 for Common-Mode SEU Mitigation:**
   - *Status:* **Engineering Integration (Known Principle Applied to KEMs).**
   - Applying CRC32 to memory buffers is standard aerospace practice. The scientific contribution is demonstrating that duplicate decapsulation (DMR) has an unrecognized 0% common-mode blind spot against pre-invocation SRAM flips, which CRC32 mitigates at negligible cost (<2.8%).
2. **Inline Assembly Multi-Rail Optimization Barrier:**
   - *Status:* **Practical Implementation Contribution.**
   - Solved compiler dead-code elimination and condition flag folding at `-O3` on AArch64 using explicit `__asm__ volatile` constraints.

### C. General vs Algorithm-Specific Findings

| Finding | Scope | Generalizable Beyond ML-KEM? |
| :--- | :--- | :--- |
| **Even-Stride Parity Cancellation** | Incomplete Cooley-Tukey NTTs | Yes (Applies to any incomplete NTT where final length is even) |
| **Weighted Projection via Inverse Roots** | Modulus $X^{2N} + 1$ Rings | Yes (Applies to cyclotomic ring NTTs with known roots) |
| **DMR Common-Mode Input Blind Spot** | Redundant Execution Generally | Yes (Applies to all deterministic KEM and signature algorithms) |
| **Specific Weight Table `g_inv_zetas`** | ML-KEM-768 Scalar Reference | Specific to FIPS 203 $q=3329$ and implementation coefficient ordering |

---

## 2. Plausible Research Paper Contributions

A defensible academic paper can be built around the following core thesis:
> *"Why Simple Algebraic Checksums Fail on Incomplete NTTs: Diagnosis, Weighted Remedies, and Layered Fault Resilience for Post-Quantum KEMs in Space Applications."*

### Key Defensible Claims:
1. First formal proof and experimental demonstration of Universal Parity Cancellation in FIPS 203 incomplete NTTs.
2. Formulation of the Weighted Inverse-Zeta Invariant as an exact algebraic countermeasure.
3. Quantitative demonstration of the cost-resilience trade-off: Layered defense achieves $\ge 96.7\%$ multi-class detection at +21% overhead, whereas DMR incurs +100% overhead while failing completely against common-mode buffer corruption.

---

## 3. Recommended Next Smallest Research Step

Rather than prematurely attempting an LLVM compiler plugin or drafting the final research paper, the next smallest experiment should be:
> **Inline Library Integration of the FO Flag:**  
> Modify `algorithms/source_ref/mlkem/src/kem.c` to directly return a dual-rail status token from `mlk_kem_dec_c`, eliminating the artificial `expected_ss` oracle dependency in the harness and establishing an in-tree resilient decapsulation function.
