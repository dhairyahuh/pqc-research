# Phase 6: Baseline Implementation Definition

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Phase:** 6 — Targeted Software Resilience Prototyping and Evaluation  
**Date:** October 1, 2026  
**Status:** COMPLETED  

---

## 1. Selected Primary Baseline Implementation

For all primary resilience experiments in Phase 6, we select:
- **Implementation:** `mlkem-native` C Reference Scalar Backend (vendored snapshot from `pq-code-package/mlkem-native` @ commit `fc269bc2d106`).
- **Primary Parameter Set:** **ML-KEM-768** (NIST Security Category 3, standard space telecommand configuration).
- **Secondary Reference Set:** **ML-DSA-65** (NIST Security Category 3, standard space telecommand authentication).

### Justification for Selection
1. **Source Accessibility and Contract Proofs:** Written in clean, CBMC-verified C90 with strict modular boundaries.
2. **Controlled Micro-Architectural Injection:** Provides validated, low-overhead hook points at every butterfly stage, multiplier accumulator, and FO branch without perturbing compiler register allocation.
3. **Reproducibility:** Tested across Phases 1–5 with byte-identical Known Answer Tests (KATs) against NIST FIPS 203/204 specifications.

---

## 2. Toolchain and Build Configuration

| Property | Primary Baseline Specification |
|:---|:---|
| **Host / Target System** | Apple Silicon (`arm64-apple-darwin27.0.0`) |
| **Compiler Toolchain** | Apple clang version 21.0.0 (`clang-2100.1.1.101`) |
| **Standard Baseline Flags** | `-O3 -Wall -Wextra -std=c11` |
| **Preprocessor Directives** | `-DMLK_CONFIG_PARAMETER_SET=768 -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem768` |
| **Instrumentation Switch** | Controlled via `-DMLKEM_RESEARCH_FAULT_HOOKS` (dormant transparency verified in Phase 5) |
| **Random Number Generator** | Deterministic derivation bridge using `randombytes()` |

---

## 3. Baseline Cryptographic Metrics & Checksums

Under clean (unfaulted) deterministic evaluation with standard test seed vector $\mathbf{s}_{\text{seed}} = (0x11, 0x11, \dots)$:

- **Public Key Checksum (`pk`):** `0x85a689b8b8fd0ec4`
- **Secret Key Checksum (`sk`):** `0xe24048933b2c6e2c`
- **Ciphertext Checksum (`ct`):** `0x22149e7f1c6b41b9`
- **Shared Secret Checksum (`ss`):** `0x2c24c6945c7d79af`
- **Baseline KAT Verification:** 100% PASS across ML-KEM-512, 768, 1024 and ML-DSA-44, 65, 87 via `test_fips_kats`.

---

## 4. Known Differences from Production Vector Builds

1. **Arithmetic Engine:** Uses scalar C Montgomery and Barrett reductions rather than hand-written AArch64 SIMD assembly (`mlkem_ntt_aarch64_asm.S`). As demonstrated in Phase 5, the mathematical outcomes and fault divergence characteristics are isomorphic.
2. **Execution Timing:** Scalar reference decapsulation takes ~180–220 $\mu$s on Apple Silicon, compared to ~45–65 $\mu$s for vectorized assembly.
3. **Isolation Rule:** All comparative overhead measurements in Phase 6 compare protected variants directly against this exact uninstrumented baseline compiled under identical flags.
