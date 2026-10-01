# Novelty and Scientific Contribution Review

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Evaluation Phase:** Phase 7

---

## 1. Classification of Project Contributions

In accordance with scientific rigor, we classify each major finding and deliverable of Phase 7 into standard academic contribution categories:

### A. Distinct Mathematical Results
1. **Universal Parity Cancellation Theorem in Incomplete NTT:**
   - *Status:* **Mathematically Established & Empirically Confirmed.**
   - Proves that because ML-KEM-768 operates on an incomplete NTT terminating at layer 7 with $\text{len} \ge 2$ (strictly even), both outputs of every butterfly pair possess identical parity index.
   - Consequently, all symmetric arithmetic faults ($t$) and twiddle perturbations ($\zeta$) cancel algebraically to zero ($\Delta - \Delta = 0$) in unweighted parity projection checks across 100% of all layers.
2. **Weighted Inverse-Zeta Projection Derivation:**
   - *Status:* **Mathematically Established & Empirically Confirmed.**
   - Derives $\sum_{i=0}^{127} \zeta_{2i+1}^{-1} \hat{p}_{2i} \equiv 128 \cdot p_2 \pmod{3329}$ via Newton power sums on the roots of $Y^{128} + 1 = 0$, proving that weighting by $\zeta^{-1}$ breaks the parity cancellation barrier at Layer 7.

### B. Meaningful Implementation & Integration Contributions
1. **Compiled Multi-Rail Optimization Barrier:**
   - *Status:* **Independently Reproduced & Verified via Disassembly.**
   - Solved compiler optimization collapse at `-O3` by establishing inline assembly memory barriers (`__asm__ volatile("" : "+r"(x), "+r"(y) : : "memory")`), forcing AArch64 code generation into two distinct physical registers (`w8`, `w9`) rather than a single condition flag register (`ccmp`).
2. **Layered 4-Stage Software Architecture:**
   - *Status:* **Empirically Supported Under Stated Threat Model.**
   - Integrates pre-invocation input integrity (CRC32), dual-projection NTT checks, multi-rail decision barriers, and transient retry into a cohesive C implementation.

### C. Experimentally Supported Resilience Trade-Offs
1. **Layered Defense vs Duplicate Decapsulation (DMR):**
   - *Status:* **Empirically Demonstrated.**
   - Demonstrates that the Layered Architecture achieves $\ge 96.7\%$ detection across all 8 threat classes for **+22.6% overhead**, whereas full duplicate decapsulation incurs **+103.0% overhead** and has **0.0% detection** against pre-invocation SRAM buffer corruption and persistent stuck-at hardware faults.

---

## 2. Review Against Prior Art

- **Algorithm-Based Fault Tolerance (ABFT):** Huang & Abraham (1984) pioneered checksums for matrix operations. Our work adapts linear projections to the specific algebraic structure of the FIPS 203 incomplete cyclotomic polynomial ring $\mathbb{Z}_q[X]/(X^{256}+1)$.
- **Lattice Fault Detection:** Prior work (e.g. Ravi et al., 2020; Espitau et al., 2022) focused either on full recomputation or hardware parity bits. Phase 7 is the first systematic evaluation demonstrating why unweighted software projections fail completely against incomplete Cooley-Tukey NTTs and providing an exact weighted remedy.
- **Novelty Boundary:** We do **not** claim novelty for CRC32 or dual-rail logic in isolation; the contribution lies in the rigorous mathematical diagnosis of the incomplete NTT parity failure, the derivation of the weighted invariant, and the experimental demonstration of the layered cost-resilience trade-off in post-quantum KEMs.
