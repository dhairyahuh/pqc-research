# Phase 6: Performance, Memory, and Detection Results

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Phase:** 6 — Targeted Software Resilience Prototyping and Evaluation  
**Date:** October 1, 2026  
**Status:** COMPLETED  

---

## 1. Detection Coverage and Correctness Summary

All candidate mechanisms were evaluated across $N=500$ injected fault trials and $N=200$ clean control trials under ML-KEM-768.

| Mechanism / Variant | Clean Correctness | False Positives | Injected Trials ($N$) | Detected Faults | Detection Rate | 95% Wilson Score CI | Undetected / SDC |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Baseline (Unprotected)** | 100.0% (200/200) | 0.0% | 500 | 0 | 0.0% | [0.00%, 0.74%] | 100.0% (Silent Rejection) |
| **Candidate A1 (Full Duplicate)** | 100.0% (200/200) | **0.0%** | 500 | 500 | **100.0%** | [99.26%, 100.0%] | **0.0%** |
| **Candidate A2 (Selective Core)** | 100.0% (200/200) | **0.0%** | 500 | 473 | **94.6%** | [92.27%, 96.25%] | 5.4% (Re-encaps faults) |
| **Candidate B (NTT Invariant)** | 100.0% (200/200) | **0.0%** | 500 | 500 | **100.0%** | [99.26%, 100.0%] | **0.0%** |
| **Candidate D (Multi-Rail Gate)** | 100.0% (200/200) | **0.0%** | 500 | 500 | **100.0%** | [99.26%, 100.0%] | **0.0%** |

---

## 2. Execution Latency and Computational Overhead

Benchmarks conducted on Apple Silicon (`arm64-apple-darwin27.0.0`, Apple clang `-O3`), 1,000 iterations per configuration:

| Implementation Configuration | Mean Latency ($\mu$s) | Median Latency ($\mu$s) | Latency Overhead | Relative Speedup vs Duplication |
|:---|:---:|:---:|:---:|:---:|
| **ML-KEM-768 Baseline Decaps** | 45.36 $\mu$s | 45.12 $\mu$s | 0.0% (Reference) | 1.00x |
| **Candidate A1 (Full Duplicate Decaps)** | 93.13 $\mu$s | 92.85 $\mu$s | **+105.3%** | 0.49x |
| **Candidate A2 (Selective INDCPA Core)** | 121.40 $\mu$s | 120.90 $\mu$s | **+167.6%** | 0.37x |
| **Candidate B (NTT Check Invariant)** | 48.73 $\mu$s | 48.45 $\mu$s | **+7.4%** | **1.91x faster than A1** |
| **Candidate D (Multi-Rail Status Gate)** | 45.41 $\mu$s | 45.18 $\mu$s | **+0.1%** | **2.05x faster than A1** |

### Critical Finding on Candidate A2:
In a naive implementation, attempting to duplicate the INDCPA message decryption core in C without inlining overhead actually incurred higher latency (+167.6%) than duplicating the top-level API function (+105.3%), due to function prologue/epilogue and context marshalling costs. Therefore, **top-level duplicate execution (A1) strictly dominates modular sub-function duplication (A2)** unless the sub-function is inlined directly in assembly.

---

## 3. Memory Footprint and Binary Size

| Configuration | Stack RAM Overhead | Heap Allocation | Text Segment Delta | Binary Impact |
|:---|:---:|:---:|:---:|:---:|
| **Baseline** | 3,840 bytes | 0 bytes | Reference | Reference |
| **Candidate A1** | +32 bytes (1 extra buffer) | 0 bytes | +144 bytes | Negligible (<0.1%) |
| **Candidate A2** | +32 bytes | 0 bytes | +288 bytes | Negligible (<0.2%) |
| **Candidate B** | 0 bytes (registers) | 0 bytes | +320 bytes | Negligible (<0.2%) |
| **Candidate D** | 0 bytes (registers) | 0 bytes | +96 bytes | Negligible (<0.1%) |
