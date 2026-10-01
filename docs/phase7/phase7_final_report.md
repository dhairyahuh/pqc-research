# Phase 7 Final Report: Targeted Layered Fault-Resilience Engineering for ML-KEM

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Repository:** `https://github.com/dhairyajain/pqc-research`  
**Phase:** 7 — Targeted Layered Fault-Resilience Engineering for ML-KEM  
**Date:** October 2026  
**Status:** Completed and Validated  

---

## 1. Executive Summary

Phase 7 addressed the central research question:
> **Can a layered, low-overhead software protection architecture improve the detection and containment of implementation-level faults in ML-KEM-768, particularly faults that evade simple algebraic projection checks, without imposing the full cost of duplicate execution?**

**Answer: YES.**

Through rigorous mathematical analysis, machine code inspection, and a 1,200-trial systematic fault campaign, Phase 7 delivered the following key conclusions:
1. **Mathematical Diagnosis of Parity Projection Failure:** Proved the **Universal Parity Cancellation Theorem**, demonstrating that because ML-KEM's incomplete NTT terminates at Layer 7 with $\text{len} \ge 2$ (always even), unweighted parity checks have an intrinsic mathematical blind spot (0.0% detection) against butterfly multiplier and twiddle faults across all layers.
2. **Breakthrough Weighted Invariant:** Derived the **Weighted Inverse-Zeta Invariant** $\sum \zeta_{2i+1}^{-1} \hat{p}_{2i} \equiv 128 p_2 \pmod{3329}$, achieving 100% detection against Layer 7 multiplier glitches where unweighted checks failed completely.
3. **Common-Mode Failure of DMR:** Proved and experimentally validated that Full Duplicate Decapsulation (DMR) has **0.0% detection** against pre-invocation ciphertext buffer corruption and persistent hardware latch-ups, while imposing a punitive **+103.0% latency penalty** (86.81 µs vs 42.77 µs).
4. **Compiled Multi-Rail Preservation:** Overcame compiler dead-code elimination and branch folding at `-O3` via inline assembly barriers (`__asm__ volatile`), forcing independent physical register evaluation on AArch64.
5. **Validated Layered Architecture:** Implemented and benchmarked a 4-layer defense architecture (Input CRC32 + Complementary NTT + Multi-Rail Barrier + Transient Retry). The architecture achieves **$\ge 96.7\%$ detection across all 8 threat classes** for only **+22.6% overhead** (52.42 µs), outperforming duplicate execution in both coverage and efficiency.

---

## 2. Quantitative Summary Table

| Metric | Config 1 (Baseline) | Config 2 (Unweighted Invariant) | Config 3 (Complementary NTT) | Config 4 (Duplicate DMR) | Config 5 (Layered Architecture) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Decapsulation Latency** | 42.77 µs | 43.21 µs | 43.84 µs | 86.81 µs | **52.42 µs** |
| **Relative Overhead** | 1.00x | +1.0% | +2.5% | +103.0% | **+22.6%** |
| **Static Table Size** | 0 bytes | 0 bytes | 256 bytes | 0 bytes | **256 bytes** |
| **Peak Stack Allocation** | ~3.8 KB | ~3.8 KB | ~4.0 KB | ~7.6 KB | **~4.1 KB** |
| **Class 1 (Intermediate T)** | 0.0% | 0.0% | 14.0% | 96.7% | **96.7%** |
| **Class 2 (Twiddle Zeta)** | 0.0% | 0.0% | 14.0% | 100.0% | **100.0%** |
| **Class 3 (Output Register)** | 0.0% | 100.0% | 100.0% | 98.7% | **100.0%** |
| **Class 4 (Correlated Mult)** | 0.0% | 0.0% | 0.0% | 100.0% | **100.0%** |
| **Class 5 (Pre-Invoc Input)** | 0.0% | 0.0% | 0.0% | **0.0%** | **100.0%** |
| **Class 6 (Checker Perturb)** | 0.0% | 0.0% | 0.0% | **0.0%** | **100.0%** |
| **Class 7 (Control FO Gate)** | 0.0% | 0.0% | 0.0% | **0.0%** | **100.0%** |
| **Class 8 (Persistent Stuck)** | 0.0% | 0.0% | 0.0% | **0.0%** | **100.0%** |

---

## 3. Validation Gate & Result Classification

| Major Finding / Mechanism | Scientific Status | Evidence & Verification |
| :--- | :--- | :--- |
| **Universal Parity Cancellation** | **Mathematically Established** | Proved via even stride parity in incomplete NTT; verified 128/128 cancel |
| **Weighted Inverse-Zeta Invariant** | **Mathematically Established** | Proved via Newton power sums on $Y^{128}+1=0$; verified 100% on L7 |
| **Multi-Rail Compiler Barrier** | **Independently Reproduced** | Verified in AArch64 disassembly (`cset w8; cset w9; and w0, w8, w9`) |
| **DMR Common-Mode Blind Spot** | **Empirically Supported** | Confirmed 0/150 detection on pre-invocation corruption & stuck faults |
| **Layered Fault Resilience** | **Empirically Supported** | 1,200 trials demonstrate $\ge 96.7\%$ detection at +22.6% overhead |

---

## 4. Remaining Weaknesses & Limitations

1. **Intermediate Layers 1–6 Projection Blind Spots:** While the weighted inverse-zeta invariant catches 100% of Layer 7 faults, Layers 1 to 6 require stage-local checking to ensure complete intermediate coverage without relying on the downstream FO check.
2. **Side-Channel Independence:** The software countermeasures focus on fault detection and control-flow integrity; physical power/EM side-channel analysis was out of scope.
3. **Instruction Cache Injections:** Compiler barriers protect register evaluation but cannot prevent instruction corruption that replaces machine instructions with NOPs.

---

## 5. Recommendation for Next Research Step

Do not pursue full duplicate execution in flight software; its computational cost is excessive (+103%) and its input common-mode vulnerability is fatal. The recommended next step is to evaluate **automated compiler-pass integration (e.g. LLVM plugin)** to automatically insert optimization barriers and stage invariants into PQC builds without manual inline assembly annotations.
