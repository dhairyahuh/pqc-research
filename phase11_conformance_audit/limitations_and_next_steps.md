# Methodological Limitations and Academic Roadmap

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Scope:** Critical Assessment of Methodological Boundaries and Pre-Submission Requirements  

---

## 1. Methodological Limitations

### 1.1 In-Tree Production Hook Boundaries vs. Software Harness Models
- **Production Objects (`mlkem768_inst.o`):**  
  The authentic in-tree production source code contains hooks (`MLKEM_RESEARCH_FAULT_HOOKS`) strictly at defined arithmetic loci within the NTT butterfly pipeline (e.g. `hook_butterfly_pre_twiddle`, `hook_butterfly_mid_ntt_locus`, and the persistent monitor state).
- **Harness-Only Models (Targets F1–F3, F6–F11):**  
  Fault targets simulating snapshot buffer corruption (`u_saved`), verifier operand poisoning, or artificial manipulation of verifier loop branch conditions cannot be exercised against `mlkem768_inst.o` without modifying production function signatures or stack structures. Consequently, findings regarding $H_1$ (verifier blindness) represent **software models of hypothetical architectural flaws**, rather than vulnerabilities demonstrated directly inside the production binary.

### 1.2 Simulated Fault Models vs. Physical Hardware Attacks
- **Software Bit-Flips:**  
  The experiments evaluate precise single-instruction, single-register bit inversions and stuck-at-zero corruptions.
- **Physical Realities (EMFI / Laser / Clock Glitching):**  
  Physical fault injection on real silicon (e.g. ARM Cortex-M4, RISC-V RV32IM) rarely produces clean single-bit flips in isolated registers. Physical faults frequently induce multi-byte bus corruption, instruction skipping, program counter redirection, or microarchitectural pipeline stalls. Therefore, empirical resilience in software simulation does not guarantee physical fault resistance without hardware-level sensor integration.

### 1.3 Side-Channel Leakage in FO Re-encryption
- While the constant-time memory comparison (`mlk_ct_memcmp`) and conditional move (`mlk_ct_cmov_zero`) prevent timing variations in the key selection step, the entire IND-CPA re-encryption operation (`mlk_indcpa_enc`) and Keccak absorb operations may leak secret message Hamming weights via power or electromagnetic side channels during decapsulation.

---

## 2. Narrowest Defensible Research Claim

Prior to academic submission, the central claim must be bounded strictly to the empirical evidence:

> **Defensible Claim:**  
> *"In the reference and native implementations of ML-KEM-768 conforming to NIST FIPS 203, in-place recovery verifiers that rely on local snapshot operands can suffer from complete verifier blindness ($H_1 = 93.5\%$) when snapshot state is corrupted. However, across 1,300 evaluated trials spanning software fault models and compiled production objects, internal false recovery never resulted in Silent Data Corruption ($H_2 = 0.0\%$, 95% Wilson CI: $[0.0\%, 0.28\%]$), because the outer Fujisaki-Okamoto re-encryption transform unconditionally enforces constant-time implicit rejection conformant with FIPS 203 Algorithm 21 ($K_{\text{bar}} = \text{SHAKE256}(z \parallel c, 32)$)."*

---

## 3. Mandatory Steps Prior to Academic Submission

1. **Hardware In-the-Loop Validation:**  
   Port the validated native build to an embedded testbench (e.g. ChipWhisperer + STM32F405 / ChipWhisperer Nano) to evaluate electromagnetic fault injection (EMFI) and clock glitching during the forward NTT and FO comparison stages.
2. **Formal Verification of the Dual-Rail Predicate:**  
   Apply CBMC (C Bounded Model Checker) to mathematically prove that under all single-point fault injections in the decapsulation control registers, the condition `(fail != fail_chk)` unconditionally triggers `*internal_status = MLK_DECAPS_STATUS_FAULT` and forces rejection key emission.
3. **Artifact Package Packaging:**  
   Package the clean-room Keccak oracle, KAT runner, deterministic seeds, and raw CSV logs into an automated, single-command reproducible container (Docker / Nix).
