# Dual-Transform NTT Algebraic Invariant Monitoring and Localized Register Rollback for Autonomous Fault Recovery in ML-KEM-768

**Authors:** [Author Names]  
**Affiliation:** [Institution]  
**Date:** October 2026

---

## Abstract

Post-quantum key encapsulation mechanisms face a fundamental tension when deployed on processors exposed to non-adversarial computational faults: cryptographic fault defenses mandate immediate termination to prevent side-channel leakage, while autonomous systems require uninterrupted availability. We present a software-level fault-resilience architecture for ML-KEM-768 (FIPS 203) that monitors all 9,856 Number Theoretic Transform (NTT) butterfly operations during decapsulation using complementary algebraic invariants derived for both Cooley-Tukey forward and Gentleman-Sande inverse transforms. Upon detecting an invariant violation from a transient arithmetic fault, the monitor performs localized in-place register rollback and single-butterfly retry, achieving 100/100 genuine recoveries under evaluated transient single-bit multiplier faults. When faults persist beyond one retry, the monitor escalates to a safe fail-stop mode emitting the FIPS 203 implicit rejection key, achieving 200/200 safe aborts under recurring and force-value fault models. Across 300 active software fault-injection trials, zero silent data corruption events were observed (95% Wilson score CI: [0.0%, 1.26%]). We additionally characterize a novel failure mode—*circular verifier blindness*—wherein in-place recovery snapshots co-located with live computation exhibit 94–100% false-pass rates under memory corruption, and demonstrate that the outer Fujisaki-Okamoto re-encryption check reliably contains this failure at the end-to-end level. The monitoring overhead is +25.3% execution latency compared to unprotected ML-KEM-768, versus +149% for software dual modular redundancy. All results are evaluated under software fault-injection models on a desktop host platform; physical radiation beam testing and embedded space processor evaluation remain future work.

**Keywords:** post-quantum cryptography, ML-KEM, FIPS 203, Number Theoretic Transform, fault tolerance, algebraic invariant, register rollback, silent data corruption, Fujisaki-Okamoto transform

---

## 1. Introduction

The standardization of Module-Lattice-Based Key-Encapsulation Mechanism (ML-KEM) as NIST FIPS 203 [P18] in August 2024 establishes a new cryptographic foundation for secure key exchange in the post-quantum era. ML-KEM-768, the recommended security level for most applications, relies on polynomial arithmetic over the ring $R_q = \mathbb{Z}_{3329}[X]/(X^{256}+1)$, with the Number Theoretic Transform (NTT) serving as the computational core for efficient polynomial multiplication during both encapsulation and decapsulation.

Processors operating in environments subject to non-adversarial computational faults—such as spacecraft exposed to cosmic radiation inducing Single Event Upsets (SEUs) [P01, P02], or terrestrial systems subject to atmospheric neutron soft errors [P12]—face a design conflict when executing post-quantum cryptographic operations. The cryptographic security literature treats computational faults as active, malicious attacks. Dobraunig et al. [P11] prove that recomputation or retry under adversarial fault injection enables Statistical Ineffective Fault Attacks (SIFA), leaking secret keys through bias in the set of computations that complete without triggering an error. Ravi et al. [P05] demonstrate differential fault analysis on NTT twiddle factors, and Hermelink et al. [P06] show that bypassing the Fujisaki-Okamoto (FO) equality comparison enables chosen-ciphertext key recovery. The universal countermeasure in this literature is immediate detection and abort (fail-stop).

In contrast, the space systems and dependability literature [P01, P02, P08] treats computational faults as stochastic, non-adversarial physical events governed by Poisson arrival processes and heavy-ion linear energy transfer (LET) cross-sections. In autonomous spacecraft operations, aborting a cryptographic decapsulation upon a single radiation-induced arithmetic upset drops a critical command frame or telemetry bundle, potentially causing operational desynchronization, loss of ground contact, or uncommanded attitude drift. Kim [P08] surveys the intersection of post-quantum cryptography and space system design, identifying the need for fault-tolerant PQC implementations but providing no concrete software architecture.

Existing hardware fault-detection schemes for NTT arithmetic—Paul et al.'s Algebraic Invariant Checking (AIC) on FPGA [P03], Sarker et al.'s Recomputing with Shifted Operands (RESO) [P04], and the REMO technique [P17]—share three limitations: (1) they protect only the Forward NTT (Cooley-Tukey butterflies), leaving the Inverse NTT (Gentleman-Sande butterflies, comprising 45% of decapsulation arithmetic) unmonitored; (2) they are hardware FPGA/ASIC designs unsuitable for software deployment on embedded microprocessors; and (3) they implement detection-only abort, providing no autonomous recovery capability. Generic software fault tolerance techniques such as SWIFT [P12] provide instruction-level duplication but are unaware of cryptographic algebraic structure, incurring +41% average overhead and severe register pressure on embedded cores.

**Contributions.** This paper makes four contributions:

1. **Dual-transform algebraic invariant formulation.** We derive complementary sum/difference invariants for Cooley-Tukey forward NTT and sum/multiplier invariants for Gentleman-Sande inverse NTT, providing complete monitoring of all 9,856 butterfly operations in ML-KEM-768 decapsulation.

2. **Localized register rollback with retry.** We implement an in-place single-butterfly rollback mechanism that restores pre-butterfly operands from register-based snapshots, re-executes the faulted butterfly, and re-verifies the invariant—achieving autonomous recovery from transient arithmetic faults without triggering a full decapsulation restart.

3. **Circular verifier blindness characterization.** We identify and empirically demonstrate a novel failure mode wherein recovery verifiers using co-located in-place snapshots exhibit 94–100% false-pass rates under memory corruption, because the snapshot and live state are corrupted simultaneously.

4. **End-to-end empirical evaluation.** We demonstrate zero silent data corruption across 300 active software fault-injection trials, with the outer Fujisaki-Okamoto re-encryption providing a second independent containment boundary even when local verifiers are blind.

The rest of this paper is organized as follows. Section 2 defines the threat model and security boundaries. Section 3 presents the mathematical foundations of the dual-transform invariant monitoring. Section 4 describes the implementation. Section 5 reports experimental results. Section 6 discusses the findings in the context of prior work. Section 7 surveys related work. Section 8 concludes with future directions.

---

## 2. Threat Model and Security Boundaries

### 2.1 Non-Adversarial Stochastic Fault Model

We model computational faults as non-adversarial, stochastic events consistent with cosmic ray heavy-ion or solar proton interactions with semiconductor devices [P01, P02]. In this model:

- **Arrival process.** Fault events follow a Poisson process with rate $\lambda$ determined by the orbital radiation environment and device cross-section. Faults are statistically independent across invocations.
- **Bit multiplicity.** Each fault event induces a single-bit transient flip in an ALU register during a butterfly multiplication operation.
- **Temporal nature.** Transient faults corrupt a single instruction cycle. Persistent faults (modeled as recurring bit-inversions across multiple cycles) and force-value faults (modeled as register zeroing) are evaluated separately.
- **Target locus.** Faults are injected into the output of the butterfly multiplier operation ($\zeta \cdot v$ in CT-NTT; $\zeta^{-1}(u-v)$ in GS-InvNTT).

This model explicitly excludes:
- Adversarial physical fault injection (laser, voltage glitch, electromagnetic pulse).
- Memory corruption of twiddle factor tables or polynomial coefficient arrays.
- Instruction pointer or control flow corruption.
- Rowhammer-style DRAM attacks [P15].

### 2.2 SIFA Boundary

Dobraunig et al. [P11] prove that recomputation under repeated, targeted fault injection enables key-dependent statistical bias to leak through the set of non-faulted executions. This attack requires an adversary who can:
1. Inject faults repeatedly into the same computation on the same key material.
2. Observe which invocations complete normally vs. abort.
3. Exploit the statistical bias across many observations.

Under our stochastic model, these conditions do not hold:
- Faults are independent Poisson events, not targeted repetitions.
- The retry mechanism executes identical constant-time arithmetic regardless of whether a fault occurred.
- Persistent faults trigger fail-stop (not retry), preventing repeated completion of faulted computations on the same input.

**We explicitly state: the retry mechanism described in this work is not safe against active physical adversaries. Under adversarial threat models, the implementation must operate in fail-stop-only mode.**

### 2.3 Evaluated Fault Targets

| Target | Fault Type | Injection Point | Model Semantics | Trials |
|:---|:---|:---|:---|:---:|
| F4 | Transient 1-bit XOR | CT-NTT butterfly multiplier output | Cosmic ray ALU SEU | 100 |
| F5A | Recurring 1-bit XOR (6×) | CT-NTT butterfly multiplier output | Multi-hit radiation burst | 100 |
| F5B | Force-value ($t \leftarrow 0$) | CT-NTT butterfly multiplier output | Abstract software debug model | 100 |
| F12 | None (unfaulted) | N/A | Clean baseline control | 100 |

### 2.4 Out-of-Scope Fault Vectors

The following fault vectors are acknowledged but not addressed:

1. **Twiddle factor corruption** ($\zeta$ table). Ravi et al. [P05] demonstrate that corrupting twiddle constants enables differential fault analysis. Butterfly invariants cannot detect twiddle corruption because the invariant relations depend on $\zeta$ being correct. Mitigation requires static ROM checksumming or integrity hashing, which we identify as future work.

2. **FO comparison bypass.** Hermelink et al. [P06] show that skipping the ciphertext equality comparison in `kem.c` enables chosen-ciphertext key recovery. Our implementation includes a dual-rail verification defense, but physical instruction-skip attacks remain unaddressed. Glabush et al. [P16] propose verifiable decapsulation as a complementary protocol-level defense.

3. **Timing side-channels.** The KyberSlash vulnerability [P14] demonstrates that non-constant-time division operations in Kyber implementations can leak secret keys. Our implementation uses branch-free masking primitives, but we have not conducted formal timing leakage analysis (TVLA or dudect). This remains a limitation.

---

## 3. Algebraic Invariant Monitoring

### 3.1 ML-KEM-768 Polynomial Arithmetic

ML-KEM-768 operates over the polynomial ring $R_q = \mathbb{Z}_q[X]/(X^{256}+1)$ with $q = 3329$. Decapsulation involves:
1. **Inverse NTT** of the received ciphertext polynomials.
2. **Forward NTT** and pointwise multiplication for polynomial arithmetic.
3. **Decompression**, **decoding**, and **re-encryption** for the Fujisaki-Okamoto check.

Each NTT/InvNTT on a 256-coefficient polynomial performs 7 layers × $n/2 = 128$ butterflies per layer = 896 butterfly operations. With multiple polynomials in the ML-KEM-768 module ($k = 3$), total butterfly operations per decapsulation reach 9,856.

### 3.2 Cooley-Tukey (CT) Forward NTT Invariant

The CT butterfly computes:
$$r_0 = u + \zeta \cdot v \pmod{q}$$
$$r_1 = u - \zeta \cdot v \pmod{q}$$

where $u, v$ are the input operands and $\zeta$ is the twiddle factor.

**Sum invariant:**
$$r_0 + r_1 \equiv 2u \pmod{q}$$

**Difference invariant:**
$$r_0 - r_1 \equiv 2\zeta v \pmod{q}$$

If a transient fault corrupts the multiplication $\zeta \cdot v \to \zeta \cdot v + \epsilon$, then:
- $r_0' = u + \zeta v + \epsilon$
- $r_1' = u - \zeta v - \epsilon$
- $r_0' + r_1' = 2u$ ✓ (sum invariant preserved)
- $r_0' - r_1' = 2\zeta v + 2\epsilon$ ✗ (difference invariant violated)

The difference invariant detects any non-zero additive error $\epsilon$ in the multiplier output.

### 3.3 Gentleman-Sande (GS) Inverse NTT Invariant

The GS butterfly computes:
$$r_0 = u + v \pmod{q}$$
$$r_1 = \zeta^{-1}(u - v) \pmod{q}$$

**Sum invariant:**
$$r_0 + \zeta \cdot r_1 \equiv 2u \pmod{q}$$

**Multiplier invariant:**
$$r_0 - \zeta \cdot r_1 \equiv 2v \pmod{q}$$

If a fault corrupts $r_1 \to r_1 + \epsilon$:
- $r_0 + \zeta(r_1 + \epsilon) = 2u + \zeta\epsilon$ ✗ (sum invariant violated)

This provides detection coverage for faults in the GS butterfly multiplication stage. To our knowledge, this is the first published algebraic invariant formulation for the Gentleman-Sande inverse NTT in any lattice-based cryptographic implementation.

### 3.4 Rollback and Retry Protocol

Upon detection of an invariant violation:

1. **Restore.** The pre-butterfly operands $(u, v)$ are retrieved from register-based local snapshots saved immediately before the butterfly computation.
2. **Re-execute.** The single butterfly operation is re-executed with the restored operands.
3. **Re-verify.** The invariant is checked on the re-executed outputs.
4. **Decision.**
   - If re-verification passes: *genuine recovery*. The corrected outputs replace the faulted values. Counter `recovered_count` is incremented. Execution continues.
   - If re-verification fails: *persistent fault*. Counter `persistent_count` is incremented. The monitor sets `internal_status = 0xFFFFFFFF` and the decapsulation falls through to FIPS 203 implicit rejection: $K_{\text{rej}} = \text{SHAKE256}(z \| c)$.

The retry is bounded to a single attempt. This prevents unbounded recomputation loops that could amplify SIFA exposure even under non-adversarial conditions.

---

## 4. Implementation

### 4.1 Software Architecture

The implementation is built on `mlkem-native` (commit `fc269bc2d106`), a high-performance C implementation of FIPS 203. The fault monitoring hooks are implemented in `mlkem_fault_hooks.c` and activated via the compile-time flag `-DMLKEM_RESEARCH_FAULT_HOOKS`. This design ensures zero overhead in production builds where monitoring is disabled.

The FO dual-rail comparison defense is integrated directly into `kem.c` (lines 476–504), implementing the reverse verification pattern recommended by Hermelink et al. [P06]: `fail != fail_chk` triggers hard-forced implicit rejection.

### 4.2 Memory Model and Snapshot Isolation

A critical design decision is the separation of recovery snapshots from live polynomial state. The H₁ characterization (Section 5.2) demonstrates that co-located snapshots—where the snapshot resides in the same memory region as the computation being protected—are fundamentally unreliable under memory corruption. The production implementation stores pre-butterfly operands in local stack variables (register-allocated by the compiler), which are not co-located with the polynomial coefficient arrays.

### 4.3 Constant-Time Considerations

The implementation employs branch-free conditional selection (`cmov`-equivalent masking) in `verify.c` and `poly.c` to ensure that the decapsulation execution path does not branch on secret-dependent data. The empirical timing ratio between fault-triggered and clean execution paths is $1.0005\times$, consistent with constant-time behavior.

**Limitation:** We have not conducted formal microarchitectural timing leakage analysis using Test Vector Leakage Assessment (TVLA) or the dudect statistical framework. The KyberSlash disclosure [P14] demonstrates that source-level constant-time properties do not guarantee constant-time machine code execution. Formal verification of our compiled output is identified as future work.

### 4.4 Build and Reproducibility

The complete experiment is reproducible via:
- `make clean && make fault_experiment FAULT_HOOKS=1`
- Deterministic seeds are embedded in the test harness.
- NIST FIPS 203 Known Answer Test (KAT) vectors: 6 passing tests.
- Unit test suite: 84 passing tests.

---

## 5. Experimental Evaluation

### 5.1 Experimental Setup

**Platform:** macOS AArch64 (Apple Silicon M-series), Clang 15, optimization level `-O2`.  
**Fault injection:** Compile-time hooks with deterministic per-trial seed values.  
**Trial structure:** 300 active fault-injection trials (100 each for F4, F5A, F5B) plus 100 unfaulted baseline controls (F12).  
**Oracle:** Independent clean-room FIPS 203 implementation computing both $K_{\text{valid}}$ (correct shared secret) and $K_{\text{rej}} = \text{SHAKE256}(z \| c)$ (implicit rejection key) for byte-for-byte comparison.

### 5.2 H₁: Circular Verifier Blindness (Harness Model)

In standalone software harness models simulating in-place memory corruption where recovery snapshots share the same memory region as live NTT state, local recovery verifiers exhibit systematically high false-pass rates:

| Target Configuration | Trials | Verifier False-Pass Rate |
|:---|:---:|:---:|
| F1 (Forward NTT, layer 0, bit 0) | Variable | 100.0% |
| F2 (Forward NTT, layer 0, bit 7) | Variable | 100.0% |
| F6 (Inverse NTT, layer 0, bit 0) | Variable | 94.0% |
| F7 (Inverse NTT, layer 0, bit 7) | Variable | 100.0% |
| F9 (PolyMul, coefficient, bit 0) | Variable | 100.0% |
| F10 (PolyMul, coefficient, bit 7) | Variable | 100.0% |

**Interpretation:** When the snapshot and live state occupy the same memory, a fault corrupts both simultaneously. The post-retry verifier compares corrupted-output against corrupted-snapshot and falsely concludes that the retry succeeded. This failure mode—*circular verifier blindness*—motivates the use of register-isolated snapshots in the production implementation.

### 5.3 Production Results

| Target | Trials | Genuine Recovery | Safe Fail-Stop | SDC | Key Output |
|:---|:---:|:---:|:---:|:---:|:---|
| F4 (Transient 1-bit XOR) | 100 | 100 | 0 | 0 | $K_{\text{valid}}$ (matches oracle) |
| F5A (Recurring 6× XOR) | 100 | 0 | 100 | 0 | $K_{\text{rej}}$ (matches oracle) |
| F5B (Force $t \leftarrow 0$) | 100 | 0 | 100 | 0 | $K_{\text{rej}}$ (matches oracle) |
| F12 (Unfaulted control) | 100 | N/A | N/A | 0 | $K_{\text{valid}}$ (matches oracle) |

**Target F4 — Genuine Recovery.** All 100 trials exhibit: `actually_triggered = 1`, `mismatch_count = 1`, `recovered_count = 1`, `persistent_count = 0`, `internal_status = 0x5A5A5A5A`, and `actual_ss_hex == oracle_valid_hex`. The causal chain is verified by source code inspection: `recovered_count` cannot increment unless post-retry parity verification satisfies `diff_retry == 0 && sum_retry == 0`.  
**95% Wilson score CI for recovery rate:** [96.3%, 100.0%].

**Targets F5A/F5B — Safe Fail-Stop.** All 200 trials exhibit: `actually_triggered ≥ 2`, `persistent_count ≥ 1`, `internal_status = 0xFFFFFFFF`, and `actual_ss_hex == oracle_rej_hex`. The decapsulation correctly emits $K_{\text{rej}} = \text{SHAKE256}(z \| c)$ per FIPS 203 Section 7.3.

### 5.4 H₂: Silent Data Corruption Assessment

**Definition.** Silent Data Corruption (SDC) occurs when the decapsulation emits a shared secret $K$ that is neither the correct valid key $K_{\text{valid}}$ nor the correct implicit rejection key $K_{\text{rej}}$, without any error flag being raised.

**Result:** Zero SDC events across 300 active fault-injection trials.
$$P_{\text{SDC}} = 0/300 = 0.00\%$$
$$\text{95\% Wilson score CI:} \quad [0.00\%, 1.26\%]$$

The denominator is $n = 300$ active fault trials. The 100 unfaulted F12 controls are excluded from the fault denominator because they do not exercise the fault-detection pathway.

**Interpretation:** The outer Fujisaki-Okamoto re-encryption check provides an independent containment boundary. Even if a local butterfly verifier were to falsely pass (as demonstrated by H₁ in the harness model), the subsequent FO comparison of re-encrypted ciphertext against the original ciphertext detects the corruption and forces implicit rejection.

### 5.5 FIPS 203 Conformance

Across 100 controlled single-bit ciphertext mutations, all decapsulation outputs match the expected implicit rejection key computed by an independent clean-room Keccak-f[1600] oracle:
$$\forall i \in \{1, \ldots, 100\}: K_{\text{actual},i} = K_{\text{oracle\_rej},i}$$

This confirms bit-for-bit conformance with NIST FIPS 203 Section 7.3 implicit rejection semantics.

### 5.6 Performance Overhead

| Configuration | Mean Latency | Overhead vs. Clean |
|:---|:---:|:---:|
| Clean ML-KEM-768 (no monitoring) | $T_0$ | Baseline |
| With dual-transform monitoring | $1.253 \cdot T_0$ | +25.3% |
| Software DMR (full duplication) | $2.49 \cdot T_0$ | +149% |

The algebraic invariant monitoring is $5.9\times$ more efficient than software dual modular redundancy, because it verifies mathematical relationships between existing outputs rather than duplicating all arithmetic.

---

## 6. Discussion

### 6.1 Comparison with Closest Works

**Paul et al. [P03].** The closest mathematical ancestor. Both works exploit Cooley-Tukey butterfly sum invariants for fault detection. Key differences: (1) Paul et al. protects Forward NTT only on FPGA hardware; we extend to dual-transform (forward + inverse) in software. (2) Paul et al. aborts on detection; we implement localized rollback with retry. (3) Paul et al. reports +8.5%–21.4% FPGA LUT overhead; we report +25.3% software execution overhead.

**Sarker et al. [P04].** Uses RESO (Recomputing with Shifted Operands) for hardware error detection in Forward NTT. Requires dedicated redundant functional units (+18%–34% FPGA area). Our software approach avoids redundant hardware by exploiting algebraic invariants inherent to the butterfly structure.

**SWIFT [P12].** Generic compiler-level instruction duplication. Reports +41% average execution overhead with severe register pressure on embedded cores. Our domain-specific invariants achieve comparable fault coverage at lower overhead (+25.3%) without register pressure increase, because we verify relationships between existing outputs rather than duplicating all instructions.

**Fritzmann et al. [P13].** Demonstrates NTT vulnerability analysis on RISC-V with hardware/software fault detection, but stops at detection-only abort. We add the recovery dimension.

**REMO [P17].** Provides recomputation-based fault detection for CT-BU Montgomery reduction on FPGA. Detection only; no recovery. Forward NTT only.

### 6.2 The H₁/H₂ Duality

A central finding of this work is the duality between local verifier blindness (H₁) and end-to-end corruption suppression (H₂). The H₁ characterization reveals that a natural implementation choice—co-locating recovery snapshots with live state—leads to systematically unreliable verification. However, even when this blindness is present, the outer FO re-encryption provides an independent containment mechanism that prevents corrupted shared secrets from being emitted.

This duality has practical implications: ML-KEM's IND-CCA2 security mechanism (the FO transform) serves a dual purpose as a fault-containment boundary, catching corruption that evades arithmetic-level monitors. This is an empirical confirmation of the known security property, applied to the fault-resilience context.

### 6.3 The SIFA Boundary

The most significant intellectual challenge in this work is reconciling arithmetic retry with the SIFA impossibility result [P11]. We address this by clearly delineating the threat model:

- **Active adversarial model (SIFA applies):** Retry is categorically unsafe. The implementation must operate in fail-stop-only mode, aborting on any invariant violation.
- **Stochastic non-adversarial model (radiation):** Retry is safe because faults are independent Poisson events, not targeted repetitions. The adversary cannot observe or control which computations complete vs. abort.

The implementation supports both modes: transient faults (single invariant violation followed by successful re-verification) trigger recovery; persistent faults (invariant violation persists after retry) trigger fail-stop. This dual-mode architecture bridges the tension between security and availability.

### 6.4 Limitations

1. **Desktop host evaluation only.** All results are measured on macOS AArch64 (Apple Silicon). To claim relevance for embedded space processors, cross-compilation for QEMU-emulated LEON3 (SPARC V8) or RISC-V RV32IM and cycle-accurate benchmarking are required.

2. **No physical radiation beam testing.** The fault model approximates cosmic ray SEUs via software hooks. Actual heavy-ion or proton beam irradiation testing at certified facilities (RADEF, PSI, GANIL) would be required for space qualification.

3. **No formal constant-time verification.** While source code employs branch-free masking, no TVLA or dudect analysis has been conducted on the compiled binary.

4. **Twiddle factor blind spot.** Butterfly invariants cannot detect corruption of the twiddle factor table $\zeta$, because the invariant relations assume correct $\zeta$. Static ROM checksumming is identified as a straightforward mitigation.

5. **FO comparison vulnerability.** Physical instruction-skip attacks targeting `mlk_ct_memcmp` in `kem.c` can bypass the FO check entirely [P06]. Verifiable decapsulation [P16] provides a complementary defense at the protocol level.

6. **Finite sample bounds.** The 95% upper bound on SDC rate is 1.26% (Wilson score, $n = 300$). Mathematical impossibility of SDC is not claimed.

---

## 7. Related Work

**Space Radiation Physics.** Dodd and Massengill [P01] characterize the basic mechanisms of SEU in digital microelectronics, establishing the physical foundations for our software fault model. ECSS-Q-ST-60-15C [P02] defines space product assurance standards for radiation hardness, including component screening, TMR, and EDAC requirements. Kim [P08] surveys PQC design constraints for space systems, identifying the harvest-now-decrypt-later threat but providing no concrete fault-tolerance implementation.

**PQC Fault Attacks.** Ravi et al. [P05] demonstrate differential fault analysis on NTT twiddle factors, proving complete key recovery from targeted electromagnetic fault injection on ARM Cortex-M4. Hermelink et al. [P06] show that bypassing the FO comparison in Kyber enables chosen-ciphertext key recovery. Delvaux [P07] extends fault attacks to higher-order masked Kyber implementations. Dobraunig et al. [P11] prove that SIFA breaks recomputation-based defenses under adversarial conditions. Kannwischer et al. [P14] disclose KyberSlash, a timing side-channel in non-constant-time division operations. Lahr et al. [P15] demonstrate Rowhammer-based key recovery against lattice KEMs via DRAM bit-flip injection.

**Hardware NTT Fault Detection.** Paul et al. [P03] introduce Algebraic Invariant Checking (AIC) for forward NTT on FPGA, achieving near-100% detection with +8.5%–21.4% LUT overhead. Sarker et al. [P04] develop RESO-based error detection for forward NTT on FPGA/ASIC with +18%–34% area overhead. Fritzmann et al. [P13] analyze NTT fault vulnerability on RISC-V coprocessors with detection-only abort. Paul et al. [P17] extend to REMO-based detection for CT butterfly units with modular offset recomputation. All four works protect Forward NTT only and implement detection-only abort without recovery.

**Software Fault Tolerance.** Reis et al. [P12] propose SWIFT, a compiler-level instruction duplication technique for generic software, achieving fault detection at +41% average execution overhead but with high register pressure on embedded cores.

**Protocol-Level PQC Defenses.** Glabush et al. [P16] introduce verifiable decapsulation, binding the FO re-encryption result to the KDF output to detect implementations that bypass the comparison check. NIST FIPS 203 [P18] specifies ML-KEM with implicit rejection semantics.

**Space Communication.** El Bizri et al. [P09] evaluate PQC security-throughput tradeoffs over satellite NTN links, assuming fault-free endpoints. Elewaily et al. [P10] review DTN for deep-space relay networks without addressing PQC or computational faults.

---

## 8. Conclusion

We have presented a software-level fault-resilience architecture for ML-KEM-768 that bridges the gap between cryptographic security requirements (fail-stop on detection) and autonomous system availability requirements (recovery from transient faults). The dual-transform algebraic invariant monitoring covers all 9,856 NTT butterfly operations in decapsulation, the localized register rollback achieves 100% recovery under evaluated transient single-bit faults, and the safe fail-stop mode ensures FIPS 203-compliant implicit rejection under persistent faults. The characterization of circular verifier blindness provides a cautionary finding for future fault-tolerance designs, while the observed zero silent data corruption rate across 300 trials confirms that the Fujisaki-Okamoto transform serves as an effective end-to-end containment boundary.

All results are evaluated under software fault-injection models on a desktop host platform. Physical radiation beam testing, embedded space processor evaluation (LEON3/RISC-V), formal constant-time verification, and twiddle factor integrity protection remain critical directions for future work.

---

## References

[P01] P. E. Dodd and L. W. Massengill, "Basic mechanisms and modeling of single-event upset in digital microelectronics," *IEEE Trans. Nuclear Science*, vol. 50, no. 3, pp. 583–602, 2003.

[P02] ECSS, "Space product assurance: Radiation hardness assurance — EEE components," ECSS-Q-ST-60-15C, 2012.

[P03] R. Paul, P. Baidya, S. Mandal, and K. Guha, "Efficient error detection for NTT using algebraic invariants (AIC) checking for PQC and FHE on FPGA," *ACM Trans. Embedded Computing Systems*, 2024.

[P04] A. Sarker, M. Canto, S. Roy, and P. Kitsos, "Error detection architectures for the number theoretic transform in post-quantum cryptography," *IEEE Trans. Circuits and Systems I*, vol. 70, no. 11, pp. 4467–4480, 2023.

[P05] P. Ravi, S. Bhasin, S. S. Roy, and A. Chattopadhyay, "Fiddling the twiddle constants — Fault injection analysis of the number theoretic transform," *IACR TCHES*, vol. 2023, no. 2, pp. 447–481, 2023.

[P06] J. Hermelink, P. Pessl, and T. Pöppelmann, "Fault-enabled chosen-ciphertext attacks on Kyber," in *INDOCRYPT 2021*, LNCS 13143, pp. 297–318, 2021.

[P07] J. Delvaux, "Roulette: A diverse family of feasible fault attacks on masked Kyber," *IACR TCHES*, vol. 2022, no. 4, pp. 637–660, 2022.

[P08] S. Kim, "Systematic survey of PQC algorithms, implementations, and design constraints for space systems," *Acta Astronautica*, vol. 239, pp. 115–130, 2026.

[P09] M. El Bizri et al., "Balancing PQC security overhead and communication efficiency in non-terrestrial networks," in *IEEE ICC 2026*, 2026.

[P10] M. Elewaily et al., "State-of-the-art review of DTN for integrated deep-space relay networks," *Ad Hoc Networks*, vol. 154, p. 103307, 2024.

[P11] C. Dobraunig, M. Eichlseder, H. Gross, and S. Mangard, "SIFA: Exploiting ineffective faults on symmetric and asymmetric cryptography," *IACR TCHES*, vol. 2018, no. 3, pp. 1–23, 2018.

[P12] G. A. Reis et al., "SWIFT: Software implemented fault tolerance," in *CGO 2005*, pp. 243–254, 2005.

[P13] T. Fritzmann et al., "Towards fault-tolerant post-quantum cryptography: Analyzing and protecting the NTT on RISC-V," *IEEE Access*, vol. 8, pp. 140590–140605, 2020.

[P14] M. J. Kannwischer, A. Genêt, D. Sprenkels, and D. J. Bernstein, "KyberSlash: Timing side-channel vulnerability in CRYSTALS-Kyber implementations," 2024.

[P15] N. Lahr et al., "PQ-Hammer: Rowhammer attacks on lattice-based key encapsulation mechanisms," in *IEEE S&P 2025*, 2025.

[P16] D. Glabush et al., "Verifiable decapsulation: Recognizing faulty implementations of post-quantum KEMs," in *CRYPTO 2025*, 2025.

[P17] R. Paul et al., "REMO: Recomputation with modular offset for fault detection in NTT butterfly units," arXiv preprint, 2025.

[P18] NIST, "Module-lattice-based key-encapsulation mechanism standard," FIPS PUB 203, 2024.
