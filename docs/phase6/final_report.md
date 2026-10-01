# Phase 6 Final Report: Targeted Software Resilience Prototyping and Evaluation

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Repository:** `https://github.com/dhairyahuh/pqc-research`  
**Phase:** 6 — Targeted Software Resilience Prototyping and Evaluation  
**Date:** October 1, 2026  
**Status:** COMPLETED  

---

## 1. Executive Summary

Phase 6 designed, implemented, and empirically evaluated targeted software-level fault resilience mechanisms for post-quantum key encapsulation (NIST FIPS 203 ML-KEM) and digital signatures (NIST FIPS 204 ML-DSA). Guided by empirical findings from Phases 1–5, the phase investigated whether selective protections at verified sensitive loci can prevent harmful failure modes (such as silent telecommand session key desynchronization and boolean status overrides) while maintaining acceptable computational, memory, and complexity budgets.

---

## 2. Implemented vs. Deferred Mechanisms

### Implemented Candidate Mechanisms:
1. **Candidate A1 (Full Duplicate Decapsulation):** End-to-end redundant decapsulation with constant-time equality validation. Successfully traps 100% of internal arithmetic and re-encryption transient SEUs. Latency overhead: +105.3%.
2. **Candidate B (FIPS 203 NTT Projection Invariant):** Mathematically derived projection invariants based on root-of-unity orthogonality over incomplete quadratic factoring ($\sum \hat{p}_{2i} \equiv 128 p_0 \pmod q$ and $\sum \hat{p}_{2i+1} \equiv 128 p_1 \pmod q$). Achieved **100.0% fault detection** on tested single-event NTT butterfly perturbations at **only +7.4% latency overhead** and 0 bytes RAM.
3. **Candidate D (Multi-Rail Encoded Status Gate):** Replaced scalar boolean return values with 32-bit Hamming-separated complementary tokens (`0x5A5AA5A5` vs `0xA5A55A5A`). Completely eliminated single-bit return register vulnerabilities at <0.1% overhead.

### Deferred / Rejected Candidates:
- **Candidate A2 (Selective INDCPA Message Core Duplication):** Rejected as suboptimal for C implementations. Duplicating internal helper subroutines without whole-program compiler inlining incurred higher latency (+167.6%) than duplicating the top-level API function (+105.3%), while providing lower fault coverage (94.6% vs 100.0%).

---

## 3. Quantitative Evaluation Summary

| Metric | Baseline Control | Candidate A1 (Duplicate) | Candidate B (NTT Invariant) | Candidate D (Multi-Rail Gate) |
|:---|:---:|:---:|:---:|:---:|
| **Mean Execution Time** | 45.36 $\mu$s | 93.13 $\mu$s | 48.73 $\mu$s | 45.41 $\mu$s |
| **Execution Overhead** | 0.0% (Ref) | **+105.3%** | **+7.4%** | **+0.1%** |
| **Stack Memory Delta** | 0 B | +32 B | **0 B** | **0 B** |
| **Detection Rate (SEUs)** | 0.0% (Silent Fail) | **100.0% (500/500)** | **100.0% (500/500)** | **100.0% (500/500)** |
| **95% Wilson Score CI** | [0.00%, 0.74%] | **[99.26%, 100.0%]** | **[99.26%, 100.0%]** | **[99.26%, 100.0%]** |
| **False Positive Rate** | 0.0% | **0.0% (0/200)** | **0.0% (0/200)** | **0.0% (0/200)** |

---

## 4. Space-System Protocol Findings

Under abstract CCSDS telecommand link simulation modeling random orbital single-event upsets ($P_{\text{SEU}} = 0.05$ per pass):
- Unprotected baseline suffered **5.0% session lockout rate**, forcing 30-minute watchdog communication timeouts.
- Protected decapsulation coupled with autonomous single-retry absorbed 100% of transient single faults, elevating link session availability from **95.0% to 99.9%** without ground intervention.

---

## 5. Scientific Limitations and Open Questions

1. **Common-Mode Input Vulnerabilities:** Duplicate execution cannot detect corruptions in the input ciphertext $c$ or private key $sk$ buffers if the corruption occurred prior to function invocation.
2. **Invariant Blind Spots:** Candidate B cannot detect paired faults that cancel out modulo 3329 ($\delta_1 + \delta_2 \equiv 0 \pmod q$). For random faults, this blind spot is bounded by $1/q \approx 0.03\%$.
3. **Hardware Emulation Requirement:** Benchmarks were collected on Apple Silicon (`arm64`). Flight deployment requires execution on space-qualified microarchitectures (SPARC/LEON4, Cortex-R52, RISC-V).

---

## 6. Stop Condition Assessment

All Phase 6 objectives, experimental harnesses, empirical benchmarks, and 11 documentation deliverables are complete and verified. In accordance with project instructions:
- Phase 7 has not been started.
- No final research paper has been drafted.
- The repository is prepared for clean commit, push, and review.
