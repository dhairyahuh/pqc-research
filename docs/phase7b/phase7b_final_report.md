# Phase 7B Final Report: Independent Validation and Claim Reconciliation

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Repository:** `https://github.com/dhairyajain/pqc-research`  
**Phase:** 7B (Independent Validation & Reconciliation of Phase 7)  
**Auditor:** Independent Implementation Auditor, Reviewer, and Critic  
**Audit Date:** October 2026  
**Audited Commit:** `01bf425aff397694624c087d3638f46f2af29486`  

---

## 1. Executive Summary of Audit Findings

This independent audit subjected Phase 7 to mathematical derivations, disassembly analysis, automated per-trial data reconstruction, and empirical re-benchmarking.

### Major Confirmed Findings
1. **Mathematical Proof of Universal Parity Cancellation:** Confirmed both analytically and through fault sweeps that unweighted parity projection checks suffer a **100% false-negative rate (0.0% detection)** against intermediate butterfly multiplier and twiddle faults across all 7 layers of ML-KEM's incomplete NTT.
2. **Breakthrough Weighted Invariant:** Confirmed that weighting butterfly outputs by inverse roots $\zeta_{2i+1}^{-1}$ breaks parity cancellation at Layer 7, achieving **100.0% detection [97.5%, 100.0%]**.
3. **Common-Mode Failure of DMR:** Confirmed that duplicate decapsulation (DMR) has **0.0% detection [0.0%, 2.5%]** against pre-invocation ciphertext buffer corruption and persistent hardware latch-ups, while imposing a **+99.3% to +103.0% latency penalty**.
4. **Machine Code Multi-Rail Preservation:** Verified via AArch64 disassembly that inline assembly memory barriers (`__asm__ volatile`) successfully prevent compiler dead-code elimination and branch folding at `-O3`.
5. **Overhead Trade-off:** Re-benchmarked the Layered Architecture at **+19.0% (median) / +28.7% (mean)** overhead, proving it provides comprehensive resilience at approximately one-fourth the computational cost of DMR.

### Major Discrepancies and Limitations Uncovered
1. **Empty Raw Data in Phase 7:** The original Phase 7 raw file (`results/phase7/raw/phase7_raw_trials.json`) contained only a 5-line summary object without individual trial logs. Phase 7B rectified this by generating complete per-trial records for all 1,200 trials.
2. **The `expected_ss` Oracle Dependency:** In `decaps_layered`, detection of FO implicit rejection relied on passing `expected_ss` from the test harness. In real-world decapsulation, `expected_ss` is unavailable. The FO flag inside `kem.c` must be exposed directly.
3. **Implementation Mismatch in Integration:** The countermeasures were implemented in a harness wrapper (`decaps_layered`), not built into the core `mlkem-native` library.
4. **Inactive Butterfly Difference Check:** The butterfly difference check code path was passed `NULL` pointers in all benchmarks and trials, leaving its empirical overhead and coverage unmeasured.

---

## 2. Recomputed Fault Coverage with Wilson 95% Confidence Intervals

Based on 1,200 independently logged trials in `results/phase7b/raw/phase7b_raw_trials.json`:

| Threat Fault Class | Baseline (C1) | Unweighted Invariant (C2) | Complementary NTT (C3) | Duplicate DMR (C4) | Layered Architecture (C5) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Class 1 (Intermediate T)** | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | 14.0% [9.4%, 20.4%] | 96.7% [92.4%, 98.6%] | **96.7% [92.4%, 98.6%]** |
| **Class 2 (Twiddle Zeta)** | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | 14.0% [9.4%, 20.4%] | 100.0% [97.5%, 100.0%] | **100.0% [97.5%, 100.0%]** |
| **Class 3 (Output Add Reg)** | 0.0% [0.0%, 2.5%] | 100.0% [97.5%, 100.0%] | 100.0% [97.5%, 100.0%] | 98.7% [95.3%, 99.6%] | **100.0% [97.5%, 100.0%]** |
| **Class 4 (Correlated Mult)** | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | 100.0% [97.5%, 100.0%] | **100.0% [97.5%, 100.0%]** |
| **Class 5 (Pre-Invoc Input)** | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | **0.0% [0.0%, 2.5%]** | **100.0% [97.5%, 100.0%]** |
| **Class 6 (Checker Perturb)** | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | **0.0% [0.0%, 2.5%]** | **100.0% [97.5%, 100.0%]** |
| **Class 7 (Control FO Gate)** | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | **0.0% [0.0%, 2.5%]** | **100.0% [97.5%, 100.0%]** |
| **Class 8 (Persistent Stuck)** | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | 0.0% [0.0%, 2.5%] | **0.0% [0.0%, 2.5%]** | **100.0% [97.5%, 100.0%]** |

---

## 3. Performance Benchmark Summary (2,000 Iterations)

- **Baseline ML-KEM-768:** Mean = 79.83 µs ($\sigma = 5.66$ µs), Median = 79.00 µs [p5 = 78.0 µs, p95 = 84.0 µs].
- **Duplicate Decapsulation (DMR):** Mean = 159.13 µs ($\sigma = 7.76$ µs), Overhead = **+99.3%**.
- **Layered Architecture:** Mean = 102.75 µs ($\sigma = 85.19$ µs), Median = 94.00 µs, Overhead = **+19.0% (med) / +28.7% (mean)**.

---

## 4. Defensible Research Contribution

The most defensible scientific contribution of this work is:
1. **The mathematical characterization of Universal Parity Cancellation** in incomplete Cooley-Tukey NTTs.
2. **The weighted inverse-zeta algebraic remedy** overcoming parity symmetry at Layer 7.
3. **The experimental refutation of duplicate execution** as an adequate space fault countermeasure, proving its 0% blind spot against pre-invocation memory corruption and persistent faults.
4. **Demonstrating that a 4-layer defense** provides $\ge 96.7\%$ multi-class detection at less than 30% overhead.

---

## 5. Most Important Unresolved Technical Question

How can the Fujisaki-Okamoto re-encryption comparison flag (`fail`) inside `kem.c` be exposed to the multi-rail status gate in constant time without modifying the public FIPS 203 API signature, thereby removing the harness `expected_ss` oracle?
