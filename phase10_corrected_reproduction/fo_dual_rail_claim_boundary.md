# Fujisaki-Okamoto and Dual-Rail Claim Boundary Audit

**Auditor:** Skeptical Cryptographic Software Verification Researcher  
**Date:** October 2026  
**Scope:** Rigorous Claim Boundary Audit of FO Re-encryption, Dual-Rail Comparison, and Constant-Time Properties  

---

## 1. Executive Summary

Prior audit reports made broad statements regarding the Fujisaki-Okamoto (FO) transform, claiming "unconditional protection against Silent Data Corruption" and "constant-time decapsulation."

This audit enforces precise scientific boundaries by separating:
1. **Source-level algorithmic intent.**
2. **Compiled-object disassembly observations.**
3. **Software fault simulation results.**
4. **Physical side-channel and hardware fault realities.**

Terms such as "unconditional protection" and "impossible" are formally rejected and replaced with bounded, verifiable statements.

---

## 2. Four-Layer Evidence Separation

### Layer 1: Source-Level Algorithmic Intent
- **Code:** [`kem.c:466-519`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c#L466-L519).
- **Intent:** Decapsulation re-encrypts candidate plaintext $m'$, compares $ct$ with $tmp$ using `mlk_ct_memcmp`, computes reverse dual-rail check `fail_chk`, and conditionally selects between $K_{\text{cand}}$ and $K_{\text{rej}}$ using `mlk_ct_cmov_zero`.
- **Finding:** The source-level design intends for any divergence between $ct$ and $tmp$ to result in $K_{\text{rej}}$.

### Layer 2: Compiled-Object Observations (`bin/obj/mlkem768_inst.o`)
- **Disassembly:** ARM64 instructions at addresses `fea4` to `fed4` ([`fo_and_dual_rail_claim_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase9_reproducibility_audit/fo_and_dual_rail_claim_audit.md)):
  ```asm
  fea4: neg    w9, w24
  feac: ldrb   w11, [x20, x8]
  feb0: ldrb   w12, [x10, x8]
  febc: bic    w12, w12, w13
  fec0: and    w11, w11, w13
  fec4: orr    w11, w11, w12
  fec8: strb   w11, [x20, x8]
  fecc: add    x8, x8, #0x1
  fed0: cmp    x8, #0x20
  fed4: b.ne   0xfeac
  ```
- **Finding:** Under Apple clang 21.0.0 `-O3`, the compiler generates a branchless loop using bitwise multiplexing (`bic`, `and`, `orr`). There are no secret-dependent conditional branches in the selection loop.
- **Limitation:** While the compiled instructions are branchless, physical microarchitectural side channels (e.g., cache-bank conflicts, data-dependent ALU power consumption, memory bus contention) cannot be proven absent through static disassembly inspection alone.

### Layer 3: Software Fault-Model Results
- **Evidence:** 1,300 trials across Phases 7, 8, 9, and 10 tested single-shot and recurring faults in the decapsulation forward NTT engine.
- **Finding:** Zero instances of incorrect shared-secret acceptance ($0/1,300$). When internal false recovery altered ciphertext coordinates, the FO comparison detected the mismatch and selected $K_{\text{rej}}$.
- **Limitation:** The fault injection hooks are located inside `poly.c` and `mlkem_fault_hooks.c`. The FO verification logic itself was not subjected to simulated instruction skipping or register corruption in these runs.

### Layer 4: Physical Hardware and Side-Channel Realities
- **Evidence:** **None currently collected in this repository.**
- **Physical Attack Vectors:**
  1. **Laser / Clock Glitch Instruction Skip:** If a physical fault skips the branch `b.ne` or skips `strb w11, [x20, x8]`, output bytes can be truncated.
  2. **Post-Comparison Register Glitching:** Register `w24` holds the `fail` flag. If perturbed between instruction `fe9c` and `fea4`, an invalid ciphertext could be accepted as genuine.
  3. **Microarchitectural Timing Channels:** If the execution of rollback retry inside the NTT engine introduces observable latency differences, an attacker observing timing could distinguish candidate key characteristics.
- **Finding:** Claims of "unconditional hardware protection" or "physically verified constant-time execution" are **unsupported by current evidence**.

---

## 3. Revised Scientific Claim Boundaries

| Prior Report Wording | Corrected Defensible Claim |
| :--- | :--- |
| *"The Fujisaki-Okamoto transform provides unconditional protection against Silent Data Corruption."* | *"In ML-KEM-768 decapsulation, the Fujisaki-Okamoto re-encryption check prevented Silent Data Corruption across all 1,300 tested internal forward-NTT fault trials by enforcing implicit rejection on invalid ciphertexts."* |
| *"Constant-time decapsulation is mathematically preserved under monitoring."* | *"Compiled assembly on ARM64 confirms branchless bitwise conditional selection between candidate and rejection keys. However, physical side-channel resistance remains unmeasured on hardware."* |
| *"The reverse dual-rail check makes predicate corruption impossible."* | *"The reverse dual-rail check provides algorithmic redundancy against single predicate register flips occurring between forward comparison and flag evaluation, but does not prevent instruction skips or post-verification register corruption."* |
