# Methodological Limitations & Threats to Validity

**Auditor:** Skeptical Cryptographic Implementation Auditor  
**Date:** October 2026  
**Scope:** Critical Assessment of Methodological Vulnerabilities and Experimental Bounds  

---

## 1. Threats to Internal Validity

### 1.1 Instrumentation and Hook Placement Artifacts
- **In-Tree Hook Constraints:** In the compiled production object (`mlkem768_inst.o`), hooks are placed strictly at butterfly multiplication outputs (`hook_mid_ntt_post_mul`). This location models arithmetic corruption on intermediate coefficient $t$, but does not evaluate fault injection into accumulator registers, address generators, or Keccak absorbing loops.
- **Compiler Inlining Dynamics:** Aggressive optimization (`-O3`) inlines helper functions and reorders registers. While the in-tree hooks successfully mutated intermediate coefficients in compiled binaries, the exact instruction sequences differ from unoptimized or debug builds.

### 1.2 PRNG Determinism and Sample Diversity
- All 400 production trials in Phase 13 were seeded deterministically via `srand(0x1337C0DE + t)`. While this guarantees exact bit-for-bit reproducibility across independent auditor runs, it exercises a bounded subspace of 100 distinct ephemeral keypairs and ciphertexts per target.
- Although sufficient to establish tight 95% Wilson confidence intervals ($N=100$), rare cryptographic edge cases (such as polynomial coefficients near the modulus boundary $q=3329$) may remain unexercised.

---

## 2. Threats to Construct Validity

### 2.1 Software Fault Injection vs. Physical Silicon Dynamics
- **Software Hook Abstraction:** Software hooks modify a single memory word or register value instantaneously via C assignment (`*t_ptr = ...`).
- **Physical Fault Reality:** Physical electromagnetic fault injection (EMFI), pulsed laser injection (PLFI), and clock glitching on actual silicon chips (e.g. ARM Cortex-M4) do not produce clean, isolated software bit-flips. Physical faults introduce:
  - Multi-byte memory bus corruption.
  - Instruction decoding corruption and op-code skipping.
  - Branch predictor and program counter misdirection.
  - Power supply transient collapse and CPU lockup.
  Consequently, demonstrating fault tolerance against C software hooks does **not** prove resilience against physical physical fault attacks on real microcontrollers.

### 2.2 Model-Only Nature of Verifier Blindness ($H_1$)
- The high verifier blindness rate ($93.5\%$) was observed only in software harness models where snapshot buffers were manipulated via explicit memory pointers. In the production library, butterfly coefficients are stored in transient registers and stack frames without exposed external pointers. The finding demonstrates an algorithmic design vulnerability in *concept*, not a dynamic exploit in `mlkem-native`.

---

## 3. Threats to External Validity

### 3.1 Generalization to Other Parameter Sets and Primitives
- The production experiments evaluated ML-KEM-768 exclusively. While ML-KEM-512 and ML-KEM-1024 share the identical Cooley-Tukey NTT structure and FO decapsulation logic, differences in vector dimensions ($k=2, 3, 4$) and compression parameters ($d_u, d_v$) could alter downstream error diffusion rates.
- Findings regarding the FO transform do **not** generalize to signature schemes (e.g. ML-DSA / FIPS 204), which do not execute re-encryption during verification.

### 3.2 Side-Channel and Constant-Time Caveats
- No physical power or electromagnetic side-channel measurements were performed.
- While source code employs constant-time masking idioms (`mlk_ct_memcmp`, `mlk_ct_cmov_zero`), compiler back-ends can introduce timing variations via early-exit vectorizations or branch optimizations. Constant-time execution is uncertified.

---

## 4. Mandatory Pre-Submission Checklist

Before submitting these findings to a peer-reviewed cryptographic venue, authors must:
1. **Clearly State Software-Only Scope:** Explicitly state in the introduction and methodology that all experiments are software simulations and do not constitute physical silicon validation.
2. **Qualify Verifier Blindness as an Architectural Finding:** Avoid terminology implying that `mlkem-native` has a vulnerability; frame it as an algorithmic study of snapshot-based verification.
3. **Report Confidence Intervals:** Present all zero-event outcomes with their two-sided 95% Wilson confidence intervals ($[0.0\%, 0.28\%]$), explicitly rejecting claims of "universal" or "absolute" immunity.
