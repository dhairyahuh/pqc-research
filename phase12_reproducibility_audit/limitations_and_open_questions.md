# Methodological Limitations and Open Research Questions

**Auditor:** Skeptical Cryptographic Implementation Auditor  
**Date:** October 2026  
**Scope:** Experimental Boundary Constraints and Future Research Trajectory  

---

## 1. Experimental and Methodological Limitations

### 1.1 Model-Only Scope of Verifier Blindness ($H_1$)
- **Structural Boundary:**  
  The phenomenon of local verifier blindness ($H_1 = 93.5\%$) was demonstrated exclusively inside specialized harness simulation harnesses (Phases 5–7). In those models, snapshot buffers (`u_saved`, `v_saved`) and verifier control registers were artificially manipulated via C memory pointers.
- **Production Reality:**  
  In the compiled production object (`mlkem768_inst.o`), butterfly variables and twiddle factors are maintained within CPU registers and ephemeral stack frames. The in-tree source code contains no software hooks allowing direct perturbation of snapshot operands during production runtime without modifying function calling conventions.

### 1.2 Software Fault Models vs. Physical Silicon Faults
- **Simulation Constraints:**  
  The production experiments (F4, F5A, F5B) evaluate clean, deterministic software-level mutations (single-bit XOR, forced assignment `t = 0`) at a single defined locus in C (`hook_mid_ntt_post_mul`).
- **Hardware Complexities:**  
  Physical electromagnetic fault injection (EMFI), body-bias injection, or pulsed laser fault injection (PLFI) on real microcontrollers (e.g. ARM Cortex-M4, RISC-V RV32) induces chaotic physical effects:
  - Multi-bit bus perturbations.
  - Glitching of ALU carry flags and condition code registers.
  - Instruction skipping and jump target redirection.
  - Complete processor hard-faults and watch-dog resets.
  Software hook resilience does not imply physical hardware immunity.

### 1.3 Absence of Secret-Dependent Side-Channel Certification
- While the software code utilizes constant-time techniques (`mlk_ct_memcmp`, `mlk_ct_cmov_zero`), compiler back-ends (`clang -O3`) are free to vectorize or optimize bitwise sequences, potentially introducing secret-dependent timing variations.
- No leakage tests (e.g. `dudect`, Welch's t-test) or side-channel power/EM measurements were performed on the decapsulation engine.

---

## 2. Open Research Questions for Academic Follow-Up

1. **Physical Hardware-in-the-Loop Validation:**  
   - *Question:* Can an attacker armed with sub-nanosecond EMFI probes bypass the FO comparison call or glitch the conditional move instruction `mlk_ct_cmov_zero` to emit faulted decapsulation keys on a physical target (e.g. STM32F405)?
2. **Formal Verification of Dual-Rail Predicates:**  
   - *Question:* Can C Bounded Model Checking (CBMC) formally verify that the dual-rail condition `fail != fail_chk` is unconditionally triggered for all single-instruction fault corruptions of the comparison loop?
3. **Multi-Locus Concurrent Fault Models:**  
   - *Question:* If an attacker injects a fault into the NTT butterfly and simultaneously glitches the FO comparison flag, what is the probability of recovering secret key coefficients from the accepted faulty shared secret?
4. **Side-Channel Masking of FO Re-encryption:**  
   - *Question:* How can IND-CPA re-encryption (`mlk_indcpa_enc`) be combined with first-order or higher-order masking to protect against side-channel assisted fault attacks?
