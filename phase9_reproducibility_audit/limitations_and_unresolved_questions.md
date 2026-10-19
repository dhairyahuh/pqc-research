# Limitations and Unresolved Research Questions

**Auditor:** Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Target:** Scientific Gaps, Methodological Boundaries, and Required Pre-Submission Experiments  

---

## 1. Executive Summary

This audit establishes the rigorous, defensible boundaries of the ML-KEM fault resilience research. While the mathematical logic of recovery verifier blindness and the outer protection of the Fujisaki-Okamoto transform are established, several critical empirical gaps remain before these findings can be submitted for peer-reviewed publication.

---

## 2. Critical Methodological Limitations

### 2.1 Software-Simulated vs Physical Fault Injection
- **Current State:** All fault models in Phases 1 through 9 were executed in software via C source-level mutation hooks (`hook_mid_ntt_post_mul`) or local harness parameter overrides.
- **Scientific Limitation:** Software simulations cannot verify whether physical electromagnetic fault injection (EMFI), body-bias injection (BBI), or pulsed laser fault injection (LFI) can cleanly perturb a single register holding an operand snapshot (`u_saved`) without inducing a processor reset, bus error, or instruction cache corruption.
- **Required Action:** Validation on physical microcontrollers (e.g., STM32F4 / ARM Cortex-M4 or ChipWhisperer target board) using localized EMFI/LFI.

### 2.2 Primitive Boundary: Scope of FO Re-encryption Protection
- **Current State:** The absence of Silent Data Corruption ($H_2 = 0.0\%$) was demonstrated exclusively for **ML-KEM-768 Decapsulation**, where candidate ciphertexts are verified by re-encryption.
- **Scientific Limitation:** This protection does **NOT** exist in cryptographic algorithms or modes that lack an FO re-encryption loop:
  1. **ML-KEM Key Generation:** Faults in forward NTT during public key generation $\mathbf{t} = \mathbf{A} \mathbf{s} + \mathbf{e}$ produce an invalid or weakened public key without detection.
  2. **ML-KEM Encapsulation:** Faults in forward NTT alter ciphertext coordinates, allowing chosen-ciphertext side-channel or fault attacks.
  3. **ML-DSA (FIPS 204 / Dilithium) Signature Generation:** Signatures do not use an FO re-encryption loop. An undetected NTT butterfly fault in polynomial multiplication will produce an invalid signature that leaks private key bits via nonce-fault analysis.
- **Required Action:** Extend recovery-verifier blindness analysis to ML-KEM Keygen, Encapsulation, and ML-DSA-65 signing.

### 2.3 Absence of DSPC in In-Tree Production Source
- **Current State:** The Dual-Snapshot Parity Checksum (DSPC) exists solely as an experimental prototype inside test harnesses. It was never integrated into `algorithms/source_ref/mlkem_fault_hooks.c` or `poly.c`.
- **Scientific Limitation:** Claims regarding DSPC performance, code size overhead, register pressure, and compiler optimization interactions have not been measured in a unified production build.
- **Required Action:** Formally integrate DSPC into `algorithms/source_ref/` and measure runtime overhead under NIST FIPS 203 KAT test suites.

### 2.4 Empirical Timing and Power Side-Channel Analysis
- **Current State:** Constant-time behavior was evaluated by inspecting compiled ARM64 disassembly (`fea4-fed4` branchless conditional move loop).
- **Scientific Limitation:** A static disassembly inspection does not rule out microarchitectural latency differences, cache line eviction effects, or data-dependent power consumption when rollback retry is triggered.
- **Required Action:** Conduct Welch's t-test (DUDCT) and power side-channel leakage assessment using oscilloscope acquisitions during clean vs retried decapsulations.

---

## 3. Pre-Submission Checklist

Before submitting this work to an academic cryptographic venue (e.g., CHES, IEEE S&P, USENIX Security), the research team must complete:

1. [ ] **Hardware EMFI/LFI Experimentation:** Measure physical fault injection success rates on a physical ARM Cortex-M4 target.
2. [ ] **Cross-Algorithm Expansion:** Formally evaluate recovery-verifier blindness on ML-DSA-65 and ML-KEM Encapsulation.
3. [ ] **In-Tree Native Integration:** Merge verified snapshot protection into `algorithms/source_ref/` and run the full 2,400-trial suite against unified production objects.
4. [ ] **Physical Timing Leakage Assessment:** Execute `dudct` (1,000,000 decapsulations) to prove that autonomous retry does not leak secret-key information through microarchitectural timing channels.
