# Final Audit Verdict & Epistemic Taxonomy

**Auditor:** Skeptical Cryptographic Implementation Auditor  
**Date:** October 2026  
**Scope:** Final Epistemic Classification of All Experimental Findings Across Phases 1–12  

---

## 1. Executive Verdict Statement

This independent audit rigorously examined the ML-KEM-768 fault resilience research repository, verified the cryptographic rejection-output oracle against NIST FIPS 202/203 across critical boundary conditions, reproduced production-path fault injections from a clean state, and reconciled historical raw datasets across Phases 5 through 12.

---

## 2. Four-Tier Epistemic Verdict

### 1. Independently Reproduced
The following findings were reproduced from a clean repository state directly against compiled production binaries (`mlkem768_inst.o`, `mlkem_fault_hooks.o`) and verified against an independent, clean-room Keccak oracle:

1. **Transient Butterfly Fault Genuine Recovery (Target F4):**  
   Under single transient bit-flips injected into intermediate $t$ within the forward NTT, the native monitor detects the mismatch, initiates butterfly rollback, recomputes cleanly, increments `recovered_count`, and emits a shared secret matching the independent valid encapsulation key bit-for-bit ($100/100$ trials, $100.0\%$, 95% Wilson CI: $[96.3\%, 100.0\%]$).
2. **Persistent Fault Safe Fail-Stop (Targets F5A and F5B):**  
   Under recurring bit-inversions (F5A) and software force-value faults (F5B), the native monitor retries, exhausts retry bounds, increments `persistent_count`, sets internal status to `0xFFFFFFFF`, and emits the canonical FIPS 203 implicit rejection key $K_{\text{bar}}$ ($200/200$ trials, $100.0\%$, 95% Wilson CI: $[98.1\%, 100.0\%]$).
3. **FIPS 203 Mathematical Conformance of Implicit Rejection:**  
   The decapsulation rejection derivation executes $K_{\text{bar}} = J(z \parallel c) = \text{SHAKE256}(z \parallel c, 32)$ over the full raw ciphertext $c$ (1,088 bytes) prepended by seed $z$ (32 bytes), totaling 1,120 bytes. Rejection outputs across 100 controlled ciphertext mutations matched the clean-room Keccak oracle bit-for-bit ($100/100$, 95% Wilson CI: $[96.3\%, 100.0\%]$).
4. **Official NIST FIPS 203 & 204 Known Answer Tests (KATs):**  
   Native builds reproduce published CAVP test vectors bit-for-bit across all security levels (ML-KEM-512, ML-KEM-768, ML-KEM-1024, ML-DSA-44, ML-DSA-65, ML-DSA-87).
5. **Absence of Silent Data Corruption in Tested Scenarios ($H_2 = 0.0\%$):**  
   Across 1,300 evaluated trials spanning software fault models and compiled production objects, zero instances of Silent Data Corruption occurred ($0/1,300$, 95% Wilson CI: $[0.0\%, 0.28\%]$).

---

### 2. Supported by Existing Evidence but Not Independently Reproduced
The following findings are supported by static source-level inspection and historical raw data, but were not re-executed in the production test harness during Phase 12:

1. **Dual-Rail Reverse Verification Logic (`kem.c:476-504`):**  
   Static code audit confirms the presence of `fail_chk` accumulation in reverse memory order and the persistent monitor count override. It is supported by source analysis, but dynamic multi-fault bypass of both rails was not evaluated.
2. **Distinction Between FIPS 203 and CRYSTALS-Kyber Round 3:**  
   Verified via static inspection of `symmetric.h:35-36` and `kem.c:513-516` vs. the legacy Kyber specification ($z \parallel c$ vs. $z \parallel H(c)$).

---

### 3. Model-Only or Otherwise Limited Findings
The following findings are valid strictly within specialized software simulation models and must not be presented as production binary vulnerabilities:

1. **Local Recovery Verifier Blindness ($H_1 = 93.5\%$):**  
   Demonstrated in software harness models (Targets F1, F2, F3, F6, F9, F10) where snapshot memory buffers (`u_saved`, `v_saved`) were directly corrupted via C pointers ($561 / 600$ trials, 95% Wilson CI: $[91.2\%, 95.2\%]$). In-tree production binaries do not expose snapshot buffers to memory corruption.
2. **Double-Sampling Parity Check (DSPC) Linear Collisions (Target F9):**  
   Demonstrated strictly in harness models evaluating correlated linear perturbations.
3. **Software Force-Value Modeling of Stuck-At Faults (Target F5B):**  
   Evaluated via C memory reassignment (`*t_ptr = 0`), which simulates the logical behavior of a stuck-at fault but does not model analog silicon fault physics.

---

### 4. Unsupported, Overstated, or Withdrawn Claims
The following claims lack empirical or physical evidence and must be completely **withdrawn** from publication drafts:

1. **WITHDRAWN: "ML-KEM-768 decapsulation is unconditionally immune to physical fault injection."**  
   *Reason:* Overstated and false. Physical EMFI or laser injection targeting CPU instruction decoding can skip comparison loops or force conditional moves to accept corrupted keys.
2. **WITHDRAWN: "The native monitor guarantees fault resilience on physical embedded devices."**  
   *Reason:* Unsupported. Evaluated solely via software hooks; physical microcontroller experiments (EMFI, clock glitching) have not been conducted.
3. **WITHDRAWN: "The implementation is certified constant-time."**  
   *Reason:* Unsupported. No cycle-accurate timing or leakage tests (`dudect`) were conducted; source-level bitwise operations can be optimized into branchy code by compiler back-ends.
4. **WITHDRAWN: "Verifier blindness was discovered as an exploit in production binaries."**  
   *Reason:* Misleading. Verifier blindness was observed only when harness code artificially perturbed private local snapshot buffers.
5. **WITHDRAWN: "Zero observed SDC events proves universal protocol immunity."**  
   *Reason:* Epistemologically invalid. $0/1,300$ establishes an empirical upper bound ($p \le 0.28\%$), not a mathematical proof of absolute immunity.
