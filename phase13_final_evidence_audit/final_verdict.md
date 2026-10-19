# Final Epistemic Verdict & Publication Readiness Assessment

**Auditor:** Independent Cryptographic Implementation Auditor, Experimental Methodology Reviewer, and Research Paper Evaluator  
**Date:** October 2026  
**Scope:** Final Synthesis of Experimental Evidence Across Phases 1–13  

---

## 1. Four-Tier Final Epistemic Verdict

Every major technical claim in this research repository is formally classified into one of four mutually exclusive tiers based strictly on traceable empirical evidence:

### Tier 1: Independently Reproduced
*Claims that have been reproduced fresh from clean repository checkouts directly against compiled production binaries and verified by independent oracles:*

1. **Transient Butterfly Fault Genuine Recovery (Target F4):**  
   Under single transient bit-flips in intermediate coefficient $t$ during forward NTT, the native monitor detects the mismatch, initiates butterfly rollback, recomputes cleanly, increments `recovered_count`, and emits a shared secret matching the independent valid encapsulation key bit-for-bit ($100/100$ trials, $100.0\%$, 95% Wilson CI: $[96.3\%, 100.0\%]$).
2. **Persistent Fault Safe Fail-Stop (Targets F5A and F5B):**  
   Under recurring bit-inversions (F5A) and software force-value faults (F5B), the native monitor retries, exhausts retry bounds, increments `persistent_count`, sets internal status to `0xFFFFFFFF`, and emits the canonical FIPS 203 implicit rejection key $K_{\text{bar}}$ ($200/200$ trials, $100.0\%$, 95% Wilson CI: $[98.1\%, 100.0\%]$).
3. **FIPS 203 Implicit Rejection Mathematical Conformance:**  
   The decapsulation rejection derivation executes $K_{\text{bar}} = J(z \parallel c) = \text{SHAKE256}(z \parallel c, 32)$ over the full raw ciphertext $c$ (1,088 bytes) prepended by seed $z$ (32 bytes), totaling 1,120 bytes. Rejection outputs across 100 controlled ciphertext mutations matched the clean-room Keccak oracle bit-for-bit ($100/100$, 95% Wilson CI: $[96.3\%, 100.0\%]$).
4. **Official NIST FIPS 203 & 204 Known Answer Tests (KATs):**  
   Native builds reproduce published CAVP test vectors bit-for-bit across all security levels (ML-KEM-512, ML-KEM-768, ML-KEM-1024, ML-DSA-44, ML-DSA-65, ML-DSA-87).
5. **Absence of Silent Data Corruption in Evaluated Scenarios ($H_2 = 0.0\%$):**  
   Across 1,300 evaluated trials spanning software fault models and compiled production objects, zero instances of Silent Data Corruption occurred ($0/1,300$, 95% Wilson CI: $[0.0\%, 0.28\%]$).

---

### Tier 2: Supported by Evidence but Not Independently Reproduced
*Claims supported by static source-level inspection and historical raw data, but not dynamically re-executed in the production test harness during Phase 13:*

1. **Dual-Rail Reverse Verification Logic (`kem.c:476-504`):**  
   Static code audit confirms the presence of `fail_chk` accumulation in reverse memory order and the persistent monitor count override. Supported by source code, but dynamic multi-fault bypass of both rails was not evaluated.
2. **Distinction Between FIPS 203 and CRYSTALS-Kyber Round 3:**  
   Confirmed via static inspection of `symmetric.h:35-36` and `kem.c:513-516` vs. the legacy Kyber specification ($z \parallel c$ vs. $z \parallel H(c)$).

---

### Tier 3: Limited to a Software Model or Specific Tested Implementation
*Claims valid strictly within specialized software simulation models that must not be presented as production binary vulnerabilities:*

1. **Local Recovery Verifier Blindness ($H_1 = 93.5\%$):**  
   Demonstrated in software harness models (Targets F1, F2, F3, F6, F9, F10) where snapshot memory buffers (`u_saved`, `v_saved`) were directly corrupted via C pointers ($561 / 600$ trials, 95% Wilson CI: $[91.2\%, 95.2\%]$). In-tree production binaries do not expose snapshot buffers to memory corruption.
2. **Double-Sampling Parity Check (DSPC) Linear Collisions (Target F9):**  
   Demonstrated strictly in harness models evaluating correlated linear perturbations.
3. **Software Force-Value Modeling of Stuck-At Faults (Target F5B):**  
   Evaluated via C memory reassignment (`*t_ptr = 0`), which simulates the logical behavior of a stuck-at fault but does not model physical silicon fault physics.

---

### Tier 4: Unsupported, Overstated, or Withdrawn
*Claims lacking empirical or physical evidence that are formally **withdrawn** from publication drafts:*

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

---

## 2. Definitive Audit Conclusions

### 1. The Strongest Defensible Research Claim
> *"In software implementations of ML-KEM-768 conforming to NIST FIPS 203, in-place recovery verifiers that rely on local snapshot operands can suffer from severe verifier blindness ($H_1 = 93.5\%$, 95% Wilson CI: $[91.2\%, 95.2\%]$) when reference snapshots are corrupted; however, across 1,300 evaluated trials spanning software fault models and compiled production binaries, internal false recovery never resulted in Silent Data Corruption ($H_2 = 0.0\%$, 95% Wilson CI: $[0.0\%, 0.28\%]$) because the outer Fujisaki-Okamoto re-encryption transform unconditionally enforces constant-time implicit rejection ($K_{\text{bar}} = \text{SHAKE256}(z \parallel c, 32)$)."*

### 2. The Exact Evidence Supporting It
- **$H_1$ Evidence:** 561 false recoveries observed across 600 trials in software snapshot perturbation models (`derived_corrected_trial_results.csv`, Targets F1, F2, F3, F6, F9, F10).
- **$H_2$ Evidence:** 0 accepted invalid shared secrets observed across 1,300 evaluated trials across all phases (`h1_h2_recalculation.csv`).
- **Production Monitor Evidence:** 100/100 genuine recoveries under transient bit-flips and 200/200 safe fail-stops under persistent/force-value faults in compiled production objects (`production_trial_recalculation.csv`).
- **Oracle Evidence:** 100/100 exact matches against clean-room Keccak-f[1600] / SHAKE256 output oracle across rate-boundary and invalid ciphertext mutation campaigns (`oracle_test_results.csv`).

### 3. The Most Important Unresolved Limitation
**The absence of physical hardware fault injection (EMFI / pulsed laser / clock glitching) on a real microcontroller target.** All experimental evidence is grounded in C software hooks, which cannot evaluate microarchitectural fault effects, instruction skips on the comparison call, power supply collapse, or analog silicon latch-up.

### 4. Publication Readiness Assessment
**Verdict: The current work is READY for a research-paper draft under a NARROWED, DEFENSIVE research question.**  
- The research question must be framed around **the resilience boundaries of localized retry monitors and the defense-in-depth provided by the Fujisaki-Okamoto transform in software implementations**, rather than claiming physical fault resilience or a production-binary exploit.
- With the revisions, confidence intervals, and claim withdrawals established in this audit, the manuscript possesses solid empirical grounding for submission to top-tier cryptographic engineering venues (e.g. IEEE TIFS, CHES, or ACM CCS).
