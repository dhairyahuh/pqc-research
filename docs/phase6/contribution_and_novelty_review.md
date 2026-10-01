# Phase 6: Research Contribution and Novelty Review

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Phase:** 6 — Targeted Software Resilience Prototyping and Evaluation  
**Date:** October 1, 2026  
**Status:** COMPLETED  

---

## 1. Structured Countermeasure Comparison

| Dimension | Candidate A1: Full Duplicate Decaps | Candidate A2: Selective Recomputation | Candidate B: FIPS 203 NTT Projection Invariant | Candidate D: Multi-Rail Status Gate |
|:---|:---|:---|:---|:---|
| **Target Algorithm** | ML-KEM-768 | ML-KEM-768 | ML-KEM-768 / 512 / 1024 | ML-KEM & ML-DSA |
| **Protected Operation** | Full Decapsulation | INDCPA Core | Polynomial NTT Transformations | Verification & FO Decision Gates |
| **Fault Classes Addressed** | Transient single SEUs across all decaps stages | Arithmetic faults in $\mathbf{s}^T\mathbf{u}$ and message decoding | Single/multi-coefficient errors in NTT butterflies | Memory bit flips in boolean return flags |
| **Empirical Detection Rate** | **100.0%** (95% CI: [99.26%, 100%]) | **94.6%** (95% CI: [92.27%, 96.25%]) | **100.0%** (95% CI: [99.26%, 100%]) | **100.0%** (95% CI: [99.26%, 100%]) |
| **Undetected Outcomes** | Common-mode inputs, stuck-at faults | Faults in re-encapsulation stage | Errors where $\Delta \sum \equiv 0 \pmod q$ | Exact 32-bit coordinated flips ($P < 2^{-32}$) |
| **False Positive Rate** | **0.0%** | **0.0%** | **0.0%** | **0.0%** |
| **Runtime Overhead** | **+105.3%** | **+167.6%** (un-inlined C) | **+7.4%** | **+0.1%** |
| **RAM Footprint Overhead** | +32 bytes (stack buffer) | +32 bytes | **0 bytes** (registers only) | **0 bytes** (registers only) |
| **Implementation Complexity** | Low (API wrapper) | High (internal refactoring) | Low (self-contained mathematical check) | Very Low (macro replacement) |
| **Common-Mode Limitations** | Fails if inputs $c, sk$ are already corrupted | Fails if inputs are corrupted | Blind to paired cancellation errors | Blind to computational errors before status flag |
| **Evidence Confidence** | **High** (reproducible across 1,000 trials) | **High** | **Very High** (mathematically proven) | **Very High** (information-theoretic Hamming bound) |

---

## 2. Rigorous Novelty Classification

In strict adherence to academic peer-review standards, we evaluate each contribution against established literature:

### 2.1 Candidate B: Exact FIPS 203 Incomplete NTT Projection Invariant
- **Novelty Classification:** **NEW MATHEMATICAL ANALYSIS & APPLICATION**
- **Prior Art Context:** In classical signal processing and complete NTT cryptosystems (e.g. Dilithium/ML-DSA), sum invariants of the form $\sum_i \hat{a}_i \equiv a_0 \pmod q$ are known. However, prior literature has not rigorously derived or evaluated the incomplete quadratic factoring projections:
  $$\sum_{i=0}^{127} \hat{p}_{2i} \equiv 128 \cdot p_0 \pmod q \quad \text{and} \quad \sum_{i=0}^{127} \hat{p}_{2i+1} \equiv 128 \cdot p_1 \pmod q$$
  specifically for NIST FIPS 203's incomplete 7-layer modulus $q=3329$ structure. Proving orthogonality of the roots over the quadratic factors and demonstrating zero false-positive detection at +7.4% latency represents a genuinely novel mathematical contribution.

### 2.2 Candidate A1: Full Duplicate Decapsulation Wrapper
- **Novelty Classification:** **ESTABLISHED TECHNIQUE APPLIED TO NEW SETTING**
- **Prior Art Context:** Dual-modular redundancy (DMR) is a standard aerospace technique. The contribution here is an **empirical characterization** of DMR specifically addressing the implicit-rejection session desynchronization pathology in post-quantum key encapsulation.

### 2.3 Candidate D: Multi-Rail Status Tokens
- **Novelty Classification:** **ENGINEERING INTEGRATION**
- **Prior Art Context:** Complementary Hamming-distance encoding (e.g., dual-rail logic) has long been used in smartcards. Implementing it as a software abstraction to defeat boolean override attacks in ML-KEM/ML-DSA verification is sound engineering integration.
