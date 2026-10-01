# Phase 5 Final Report: Cross-Implementation Fault-Surface Validation

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Repository:** `https://github.com/dhairyahuh/pqc-research`  
**Phase:** 5  
**Date:** October 1, 2026  
**Status:** COMPLETED  

---

## 1. Executive Summary

Phase 5 investigated how implementation architecture, compiler optimization, memory representations, and execution backends affect the computational fault surface of ML-KEM and ML-DSA.

### Critical Provenance Finding
A key scientific contribution of Phase 5 is the verification of implementation provenance: **liboqs 0.16.0 does not contain an independent ML-KEM or ML-DSA implementation**. Instead, liboqs integrates and compiles the upstream `pq-code-package` native code, selecting the AArch64 hand-optimized assembly backend. Thus, the comparative baseline between our vendored reference implementation and liboqs constitutes a **backend architecture comparison** (scalar C vs. vectorized AArch64 assembly), not a multi-source independent implementation audit.

---

## 2. Experimental Execution Summary

| Experiment Category | Target Suite | Executed Trials | Outcome |
|:---|:---|:---:|:---|
| **Cross-Backend Interoperability** | ML-KEM-768 & ML-DSA-65 | 1,400 | 100% interoperability across C ref & liboqs backends |
| **Instrumentation Transparency** | Clean vs. dormant fault hooks | 500 | 100% byte-identical cryptographic outputs |
| **ML-KEM NTT & Accumulator Faults** | Layers 1–7, $\delta \in [1, 832]$ | 1,600 | 100% implicit rejection rate across all tested parameters |
| **FO Predicate Fault Reproduction** | B1 (Valid CT fail) / B2 (Corrupt CT pass) | 400 | Replicated Phase 2/4 findings; 59.5% garbled key rate |
| **ML-DSA Norm Check Reproduction** | Norm-$z$ bypass / force-fail | 200 | Replicated Phase 3/4 findings; verified loop count increases |
| **ML-DSA Verification Gate Audit** | Boolean return override | 400 | Confirmed Phase 4 correction: local bypass $\neq$ signature forgery |
| **Compiler Optimization Sensitivity** | `-O0`, `-O1`, `-O2`, `-O3` | 8 configurations | Output checksums identical across all optimization levels |

---

## 3. Key Findings Across Research Questions

1. **RQ1 (Algorithm-Intrinsic vs Implementation-Dependent):**
   - Ring algebraic properties (NTT butterfly error diffusion, polynomial coefficient wrapping) and cryptographic protocol structures (Fujisaki-Okamoto implicit rejection) are strictly algorithm-intrinsic and identical across all backends.
   - Physical vulnerability windows (stack memory vs. SIMD register residency) are implementation- and optimization-dependent.
2. **RQ2 (Reachable Fault Surfaces):**
   - Single-bit register upsets in AArch64 NEON vector lanes map isomorphicly to additive polynomial coefficient errors $\delta \in \mathbb{Z}_q$.
3. **RQ3 (Compiler Sensitivity):**
   - Clang optimization levels (`-O0` to `-O3`) do not alter modular reduction or arithmetic correctness. Checksums for clean and faulted artifacts are identical across optimization tiers.
4. **RQ4 (Cross-Implementation Reproducibility):**
   - Full functional reproducibility confirmed between C reference and liboqs. True multi-source independence remains open pending an independently written implementation (e.g., Rust / Go implementations).

---

## 4. Confirmed, Corrected, and Inconclusive Claims

- **CONFIRMED:**
  - Implicit rejection absorbs 100% of single-bit and multi-bit polynomial arithmetic faults during ML-KEM decapsulation.
  - Fujisaki-Okamoto bypass on corrupted ciphertexts yields garbled keys (divergence), not message recovery.
  - Optimization levels preserve mathematical determinism in constant-time implementations.
- **CORRECTED / PRESERVED:**
  - Verification flag modification remains strictly classified as a local control-flow bypass, NOT a mathematical signature forgery.
  - liboqs independence claim refuted and corrected to backend comparison.
- **INCONCLUSIVE:**
  - Behavior on non-ARM architectures (e.g., RISC-V, SPARC/LEON) cannot be empirically measured without hardware-in-the-loop or emulation setups.

---

## 5. Test Suite and Verification

- All Phase 5 binaries built via `make phase5`.
- Unit and integration tests passed:
  - Baseline C test suite (`make test`): PASS
  - Phase 4 validation suite (`tests/test_phase4_audit.py`): PASS
  - Phase 5 validation suite (`tests/test_phase5_cross_impl.py`): PASS

---

## 6. Stop Condition Assessment

All Phase 5 objectives, documentation deliverables, and empirical validation gates are complete. In accordance with instructions:
- Phase 6 has not been started.
- No resilience mechanisms have been implemented in the codebase.
- The research is ready for commit and review.
