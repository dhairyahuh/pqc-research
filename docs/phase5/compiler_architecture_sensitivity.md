# Phase 5: Compiler and Architecture Sensitivity Analysis

**Phase:** 5 — Cross-Implementation Fault-Surface Validation  
**Date:** October 1, 2026  
**Status:** COMPLETED  

---

## 1. Objective and Scope

Assess whether compiler optimization levels (`-O0`, `-O1`, `-O2`, `-O3`), compiler dead-code elimination, loop vectorization, or architectural instruction scheduling alter:
1. Deterministic cryptographic outputs.
2. Sensitivity to localized faults.
3. Fault propagation pathways across memory boundaries.

---

## 2. Experimental Setup

- **Toolchain:** Apple clang version 21.0.0 (`arm64-apple-darwin27`).
- **Binary Binaries Compiled:**
  - `bin/phase5_compiler_O0`: Compiled strictly with `-O0 -g`.
  - `bin/phase5_compiler_O1`: Compiled with `-O1`.
  - `bin/phase5_compiler_O2`: Compiled with `-O2`.
  - `bin/phase5_compiler_O3`: Compiled with `-O3 -flto`.
- **Target Operations:** ML-KEM-768 deterministic keygen, encapsulation, and decapsulation under clean conditions and controlled single-bit fault injections.

---

## 3. Empirical Results

### 3.1 Checksum Invariance Across Optimization Levels

| State / Artifact | `-O0` Checksum | `-O3` Checksum | Match Status |
|:---|:---|:---|:---:|
| **Public Key (`pk`)** | `0x85a689b8b8fd0ec4` | `0x85a689b8b8fd0ec4` | **IDENTICAL** |
| **Secret Key (`sk`)** | `0xe24048933b2c6e2c` | `0xe24048933b2c6e2c` | **IDENTICAL** |
| **Ciphertext (`ct`)** | `0x22149e7f1c6b41b9` | `0x22149e7f1c6b41b9` | **IDENTICAL** |
| **Shared Secret (`ss`)** | `0x2c24c6945c7d79af` | `0x2c24c6945c7d79af` | **IDENTICAL** |
| **Faulted Shared Secret** | `0xc3bd6a3c536e921b` | `0xc3bd6a3c536e921b` | **IDENTICAL** |

### 3.2 Key Observations

1. **Deterministic Functional Equivalence:**
   - Optimization flags do not alter mathematical evaluation order in modular arithmetic routines, Barrett reductions, or Montgomery multiplications.
2. **Deterministic Fault Divergence:**
   - When an identical fault is injected into polynomial coefficients at `-O0` and `-O3`, the resulting divergent outputs are byte-identical (`0xc3bd6a3c536e921b`).
3. **Register Spilling vs. In-Register SIMD:**
   - At `-O0`, intermediate polynomial coefficients reside in stack memory (L1 D-Cache), making them susceptible to memory-directed fault injections across function frames.
   - At `-O3`, inner loops keep butterfly operands strictly in general-purpose and SIMD registers (`q0-q15` / `x0-x30`), collapsing memory vulnerability windows into pure register-file exposure windows.
4. **Constant-Time Verification:**
   - Both `-O0` and `-O3` maintain branchless conditional copies in Fujisaki-Okamoto verification (`cmov` / bitwise masking), preventing compiler-induced timing side channels.
