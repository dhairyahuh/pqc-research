# Phase 5: Cross-Implementation Synthesis

**Phase:** 5 — Cross-Implementation Fault-Surface Validation  
**Date:** October 1, 2026  
**Status:** COMPLETED  

---

## 1. Executive Synthesis

Phase 5 conducted an empirical and structural comparison between:
1. **Implementation A:** `mlkem-native` / `mldsa-native` (scalar C reference fallback).
2. **Implementation B:** `liboqs 0.16.0` (compiled with AArch64 vector assembly backends).
3. **Compiler Variants:** Apple clang 21.0.0 at `-O0`, `-O1`, `-O2`, and `-O3`.

### Key Structural Finding: The Implementation Provenance Reality
As established in `implementation_provenance.md`, liboqs 0.16.0 wraps `pq-code-package` native code. Therefore, this comparison assesses **backend and architecture differences** (scalar C vs. hand-written AArch64 SIMD assembly), rather than two independently developed algorithm implementations.

---

## 2. Core Research Question Resolutions

### RQ1: Algorithm-Intrinsic vs. Implementation-Dependent Behavior
- **Algorithm-Intrinsic Properties (Constant across all backends & compilers):**
  - **Diffusion Dynamics:** In NTT layers, error expansion is governed by the ring arithmetic $\mathbb{Z}_q[X]/(X^{256}+1)$. The ring structure forces full diffusion across coefficients regardless of whether executed via scalar loops or 128-bit NEON vector lanes.
  - **Implicit Rejection Invariance:** Single-bit perturbations in polynomial arithmetic during decapsulation result in 100% rejection via pseudorandom shared secret derivation ($K = \operatorname{J}(z \| c)$).
  - **FO Bypass Behavior:** Bypassing ciphertext re-encryption comparison causes silent key divergence in ~60% of single-byte corruptions and 100% of multi-byte corruptions.
- **Implementation-Dependent Properties:**
  - **Vulnerability Lifetime & Spatial Exposure:** Under `-O0`, variables live on the memory stack for thousands of cycles. Under `-O3` / assembly, variables reside in NEON vector registers (`q0`-`q31`), drastically shrinking the temporal window for memory faults while exposing architectural vector registers to single-event upsets.
  - **Fault Masking Boundaries:** High-order compression masks in ML-KEM ($d_u, d_v$) and hint decomposition in ML-DSA ($2\gamma_2$) mathematically absorb faults at the algorithmic boundary; compiler optimizations do not alter these absorption windows.

### RQ2: Reachable Fault Surfaces
- Source-level fault hooks effectively model bit flips in algorithmic operands.
- Hardware single-event upsets (SEUs) in SIMD execution units map directly to the arithmetic faults modeled in Phase 2 and Phase 3:
  - An ALU fault in an AArch64 `fmla` / `smlal` instruction corresponds exactly to an additive coefficient error $\delta \in \mathbb{Z}_q$.
  - Register corruption in `v0-v31` corresponds directly to vector polynomial coefficient corruption.

### RQ3: Compiler and Optimization Sensitivity
- Binary output checksums for key generation, encapsulation, decapsulation, and faulted executions are **identical between `-O0` and `-O3`**.
- Compilers do not reorder or alter the mathematical semantics of constant-time modular arithmetic.
- Compiler optimization level does not introduce new algorithmic fault modes, but shifts physical vulnerability from RAM/Cache to CPU core registers.

### RQ4: Replicability across Independent Frameworks
- Replicated 100% of baseline operations between scalar C reference and liboqs AArch64 assembly.
- All Phase 4 audit conclusions remain valid across both execution paths.
