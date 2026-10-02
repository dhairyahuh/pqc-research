# Research Manuscript Blueprint

**Working Title:**  
*Dual-Transform NTT Algebraic Invariant Monitoring and Localized Register Rollback for Autonomous Fault Recovery in ML-KEM-768: Characterizing Circular Verifier Blindness and Fujisaki-Okamoto Containment Under Software Fault Injection*

**Target Venue:** IEEE Transactions on Computers / ACM TECS / Applied Cryptography Conference  
**Date:** October 2026  
**Evidence Baseline:** Phase 16 Evidence Closure (Commit `ca38dec`)

---

## Section 1: Introduction (≈1.5 pages)

### Content:
1. **The Post-Quantum Imperative for Space Systems.**
   - NIST FIPS 203 (ML-KEM) is the mandated global standard for key encapsulation (August 2024).
   - Spacecraft onboard computers face cosmic radiation causing Single Event Upsets (SEUs) in ALU registers during cryptographic computation [P01, P02, P08].
   - The harvest-now-decrypt-later threat makes PQC adoption urgent for long-duration space missions [P08].

2. **The Fundamental Tension: Security vs. Availability.**
   - Cryptographic fault literature mandates immediate abort (fail-stop) upon fault detection to prevent SIFA/DFA key leakage [P05, P06, P07, P11].
   - Space systems cannot tolerate unconditional abort: dropped decapsulation causes loss of critical commands, telemetry desynchronization, or attitude control failure [P08, P10].
   - **Research gap:** No published work reconciles these opposing requirements for any lattice-based KEM.

3. **Scope Limitation and Thesis Statement.**
   > "In lattice-based key encapsulation mechanisms (ML-KEM-768), local checkpoint-and-verify arithmetic recovery introduces circular verifier blindness under internal memory corruption in software models, but outer Fujisaki-Okamoto re-encryption reliably suppresses resulting end-to-end silent data corruption across evaluated software fault injections."

### Key References: P01, P02, P08, P11, P18

---

## Section 2: Threat Model and Security Boundaries (≈1.5 pages)

### Content:
1. **Non-Adversarial Stochastic Fault Model.**
   - Cosmic ray heavy ions and solar protons cause independent, Poisson-distributed SEUs in processor registers and SRAM [P01, P02].
   - Faults are modeled as single-bit transient flips in ALU multiplier output during NTT butterfly execution.
   - This is explicitly **not** an adversarial physical attack model.

2. **SIFA Boundary Declaration (Critical).**
   - Dobraunig et al. (2018) proves that recomputation under active adversarial fault injection leaks keys [P11].
   - Our retry mechanism is safe under the stochastic non-adversarial model because:
     - Faults are independent Poisson events (not repeated targeted injections).
     - Retry executes constant-time arithmetic without secret-dependent branching.
     - Persistent faults trigger fail-stop (not retry), emitting FIPS 203 implicit rejection.
   - The manuscript explicitly states: **retry is not safe against active physical attackers.**

3. **Evaluated Fault Targets.**

   | Target | Fault Type | Injection Point | Model Semantics |
   |:---|:---|:---|:---|
   | F4 | Transient single-bit XOR | Forward NTT butterfly multiplier | Cosmic ray ALU SEU |
   | F5A | Recurring single-bit XOR (6 injections) | Forward NTT butterfly multiplier | Multi-hit radiation burst |
   | F5B | Force-value (*t = 0) | Forward NTT butterfly multiplier | Software debug hook (abstract) |
   | F12 | None (unfaulted baseline) | N/A | Clean control |

4. **Out-of-Scope Fault Vectors.**
   - Twiddle factor memory corruption (evades butterfly invariants) [P05].
   - FO comparison instruction skip (requires dual-rail or verifiable decapsulation) [P06, P16].
   - Physical clock/voltage/laser glitching [P05, P06, P07].
   - DRAM Rowhammer attacks [P15].

### Key References: P01, P02, P05, P06, P11, P14, P15, P16

---

## Section 3: Mathematical Foundation (≈2 pages)

### Content:
1. **ML-KEM-768 Polynomial Arithmetic.**
   - Ring $R_q = \mathbb{Z}_{3329}[X] / (X^{256} + 1)$.
   - Decapsulation requires Forward NTT (Cooley-Tukey) and Inverse NTT (Gentleman-Sande).
   - Total butterfly operations per decapsulation: 9,856.

2. **Forward NTT (CT) Butterfly Invariant Derivation.**
   - Cooley-Tukey butterfly: $r_0 = u + \zeta \cdot v$, $r_1 = u - \zeta \cdot v$.
   - **Sum invariant:** $r_0 + r_1 = 2u \pmod{q}$.
   - **Difference invariant:** $r_0 - r_1 = 2\zeta v \pmod{q}$.
   - Fault detection: if $r_0 + r_1 \neq 2u \pmod{q}$, a fault is detected.

3. **Inverse NTT (GS) Butterfly Invariant Derivation.**
   - Gentleman-Sande butterfly: $r_0 = u + v$, $r_1 = \zeta^{-1}(u - v)$.
   - **Sum invariant:** $r_0 + \zeta \cdot r_1 = 2u \pmod{q}$.
   - **Multiplier invariant:** $r_0 - \zeta \cdot r_1 = 2v \pmod{q}$.
   - This is the novel dual-transform contribution.

4. **Rollback Mechanism.**
   - On invariant violation: restore pre-butterfly operands from register snapshots.
   - Re-execute the single butterfly operation.
   - Re-verify the invariant.
   - If the re-verification passes → genuine recovery.
   - If the re-verification fails → persistent fault → fail-stop with $K_{\text{rej}}$.

### Key References: P03, P04, P18

---

## Section 4: Implementation (≈1.5 pages)

### Content:
1. **Software Architecture.**
   - Base: `mlkem-native` (commit `fc269bc2d106`), FIPS 203 compliant.
   - Monitor hooks: `mlkem_fault_hooks.c` — compile-time activated via `-DMLKEM_RESEARCH_FAULT_HOOKS`.
   - FO dual-rail defense: `kem.c:476-504`.

2. **Memory Model.**
   - Register-based snapshots: pre-butterfly operands saved in local stack variables.
   - NOT co-located with live polynomial array (avoiding H₁ circular blindness).

3. **Constant-Time Considerations.**
   - Branch-free masking in `verify.c` and `poly.c`.
   - Empirical timing ratio: $1.0005\times$ (fault path vs. clean path).
   - **Limitation:** No formal TVLA/dudect verification conducted.

4. **Build and Reproducibility.**
   - Automated Makefile with deterministic seeds.
   - NIST FIPS KAT vectors: 6 passing tests.
   - Unit test suite: 84 passing tests.

### Key References: P14, P18

---

## Section 5: Experimental Evaluation (≈2.5 pages)

### Content:
1. **Experimental Setup.**
   - Platform: macOS AArch64 (Apple Silicon), Clang 15, `-O2`.
   - Fault injection: Compile-time hooks, deterministic seeds per trial.
   - Trial count: 300 active fault trials + 100 unfaulted controls.

2. **H₁ Results: Circular Verifier Blindness (Harness Model).**
   - In-place snapshot harness: 94.0%–100.0% verifier false-pass across 6 vulnerable targets.
   - Demonstrates the failure mode that motivates separate-register snapshotting.

3. **Production Recovery Results.**

   | Target | Trials | Recovery | Fail-Stop | SDC | Status |
   |:---|:---:|:---:|:---:|:---:|:---|
   | F4 (Transient SEU) | 100 | 100/100 | 0 | 0 | Genuine recovery |
   | F5A (Recurring XOR) | 100 | 0 | 100/100 | 0 | Safe fail-stop |
   | F5B (Force-value) | 100 | 0 | 100/100 | 0 | Safe fail-stop |
   | **Total active** | **300** | **100** | **200** | **0** | — |

4. **H₂: Silent Data Corruption Assessment.**
   - SDC events: 0/300 active fault trials.
   - 95% Wilson score CI: $[0.0\%, 1.26\%]$.
   - Denominator: $n = 300$ (excludes 100 unfaulted F12 controls).

5. **FIPS 203 Conformance.**
   - 100/100 invalid ciphertext mutations emit correct implicit rejection key.
   - Verified against independent clean-room Keccak-f[1600] oracle.

6. **Performance Overhead.**
   - Monitor overhead: $+25.3\%$ latency vs. unprotected.
   - Software DMR baseline: $+149\%$ latency.
   - Overhead ratio: $5.9\times$ more efficient than software DMR.

### Key References: P03, P04, P12, P18

---

## Section 6: Discussion (≈1.5 pages)

### Content:
1. **Comparison with Closest Works.**
   - Paul et al. (P03): FPGA, forward-only, detection-only → we extend to software, dual-transform, with recovery.
   - Sarker et al. (P04): Hardware RESO, forward-only → we provide software equivalent.
   - SWIFT (P12): Generic compiler technique, +41% overhead → our domain-specific invariants achieve +25.3%.
   - Fritzmann et al. (P13): RISC-V NTT detection without recovery → we add localized rollback.

2. **The H₁/H₂ Duality.**
   - Local verifier blindness (H₁) exists in co-located snapshot models.
   - End-to-end SDC suppression (H₂) is maintained by the outer FO re-encryption layer.
   - This duality means: even a blind local verifier does not compromise end-to-end security, because the FO transform provides a second independent check.

3. **SIFA and the Threat Model Boundary.**
   - Under active adversarial attacks, retry must be disabled.
   - Under stochastic radiation, retry provides autonomous availability.
   - The implementation supports both modes: transient → retry; persistent → fail-stop.

4. **Limitations (Mandatory Section).**
   - Desktop host evaluation only (no LEON3/RISC-V).
   - No physical radiation beam testing.
   - No formal constant-time verification (TVLA/dudect).
   - Twiddle factor corruption evades butterfly invariants.
   - FO comparison bypass via instruction skip not addressed.
   - Sample size $n = 300$ provides finite-sample bounds only.

### Key References: P05, P06, P11, P14, P16

---

## Section 7: Related Work (≈1 page)

### Content:
Organized into four categories:
1. **Space Radiation Physics:** P01, P02, P08.
2. **PQC Fault Attacks:** P05, P06, P07, P11, P14, P15.
3. **Hardware NTT Fault Detection:** P03, P04, P13, P17.
4. **Software Fault Tolerance:** P12.
5. **Protocol-Level PQC Defense:** P16, P18.
6. **Space Communication & PQC Deployment:** P09, P10.

---

## Section 8: Conclusion and Future Work (≈0.5 pages)

### Content:
1. **Summary of Contributions:**
   - First dual-transform (CT + GS) NTT algebraic invariant formulation for software.
   - First autonomous localized register rollback for ML-KEM-768.
   - Discovery of circular verifier blindness (H₁) under co-located memory corruption.
   - Empirical zero-SDC confirmation across 300 active fault trials.

2. **Future Work:**
   - QEMU-emulated LEON3/RISC-V cross-compilation and cycle-accurate evaluation.
   - Twiddle factor integrity protection (static ROM checksumming).
   - Formal constant-time verification via dudect or CT-Prover.
   - Orbit-calibrated radiation fault model (LET spectra, MCU clustering).
   - Physical proton/heavy-ion beam testing at certified facilities.

---

## References

18 works as listed in `prior_art_matrix.csv`, formatted per venue style guide.

---

## Appendices

- **Appendix A:** Full butterfly invariant derivations (CT and GS).
- **Appendix B:** Trial-level raw data summary tables.
- **Appendix C:** Reproduction instructions (Makefile targets, compiler flags, seed values).
- **Appendix D:** Evidence manifest with SHA-256 hashes.
