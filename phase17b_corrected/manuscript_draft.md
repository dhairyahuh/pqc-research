# Software-Level Fault Resilience for ML-KEM-768: Dual-Transform NTT Invariant Monitoring, Localized Register Rollback, and Containment

**Authors:** [Author Names]  
**Affiliation:** [Institution]  
**Date:** October 2026  
**Target Submission:** Research Manuscript (Revised Version)

---

## Abstract

Post-quantum key encapsulation mechanisms face an operational tension when deployed on embedded processors exposed to non-adversarial computational faults: cryptographic fault defenses traditionally mandate immediate session termination to prevent side-channel leakage, whereas autonomous and remote systems require continuity of service. We present a software-level fault-resilience architecture for ML-KEM-768 (NIST FIPS 203) that monitors all 9,856 Number Theoretic Transform (NTT) butterfly operations executed during decapsulation. Building upon prior algebraic invariant principles established for forward Cooley-Tukey (CT) transforms in hardware, we derive complementary sum and multiplier invariants for the inverse Gentleman-Sande (GS) transform and implement localized in-place register rollback and single-butterfly retry directly in C software. Under evaluated transient single-bit multiplier faults ($F4$), the monitor achieves 100/100 genuine recoveries, restoring authentic decapsulation output without triggering full re-encapsulation or session abort (95% Wilson score CI: $[96.3\%, 100.0\%]$). When faults persist beyond one retry, the monitor escalates to a safe fail-stop mode emitting the standard FIPS 203 implicit rejection key, achieving 200/200 safe aborts under recurring bit-inversion ($F5A$) and software force-value ($F5B$) fault models. Across 300 active software fault-injection trials, zero silent data corruption (SDC) events were observed (0/300, 95% Wilson score CI: $[0.00\%, 1.26\%]$). We additionally characterize a specific common-mode verification failure—termed *circular verifier blindness*—wherein in-place recovery snapshots co-located with live state in memory exhibit 94.0–100.0% false-pass rates under memory corruption in standalone harness models, and demonstrate that the outer Fujisaki-Okamoto (FO) re-encryption check reliably contains this failure at the end-to-end boundary. On the evaluated desktop host (macOS AArch64, Clang -O2), dual-transform monitoring incurs +25.3% execution latency relative to unprotected ML-KEM-768, compared to +149% for single-thread software dual modular redundancy (DMR). All evaluations represent software-implemented fault injection; physical radiation beam qualification, embedded space processor evaluation (LEON3/RISC-V), and formal microarchitectural timing leakage analysis remain future work.

**Keywords:** post-quantum cryptography, ML-KEM, FIPS 203, Number Theoretic Transform, fault tolerance, algebraic invariant, register rollback, silent data corruption, Fujisaki-Okamoto transform

---

## 1. Introduction

The ratification of the Module-Lattice-Based Key-Encapsulation Mechanism (ML-KEM) as NIST FIPS 203 [P18] in August 2024 standardizes post-quantum key establishment across public-key infrastructures. ML-KEM-768, designed for Security Category 3, relies on polynomial ring arithmetic over $R_q = \mathbb{Z}_{3329}[X]/(X^{256}+1)$, where the Number Theoretic Transform (NTT) serves as the primary computational engine for fast polynomial multiplication during encapsulation and decapsulation.

Microprocessors operating in radiation-prone environments—such as spacecraft on-board data handling (OBDH) and tracking, telemetry, and command (TT&C) systems exposed to cosmic rays [P01, P02], or terrestrial aerospace systems subject to atmospheric neutron single-event effects [P12]—face a severe dilemma when executing post-quantum algorithms. The cryptographic fault-attack literature treats computational perturbations as active, malicious intrusions. Seminal work by Dobraunig et al. [P11] proves that recomputation or conditional retry under physical fault injection enables Statistical Ineffective Fault Attacks (SIFA), leaking secret key material through the statistical distribution of successful completions. Ravi et al. [P05] demonstrate that injecting faults into NTT twiddle factors enables secret key extraction, while Hermelink et al. [P06] show that bypassing the Fujisaki-Okamoto (FO) ciphertext verification check enables chosen-ciphertext key recovery. Consequently, standard cryptographic hardening prescribes immediate execution abort (fail-stop) upon detecting an error.

Conversely, dependability and aerospace systems literature [P01, P02, P08] models computational faults as stochastic, non-adversarial physical events governed by Poisson arrival processes. In autonomous satellite operations, deep-space probes, or unmanned aviation, unconditionally aborting a cryptographic decapsulation upon a single radiation-induced arithmetic upset drops critical telecommand frames or telemetry synchronization bundles [P08, P10]. This can lead to telecommand lockouts, ground station pass failures, or uncommanded attitude drift. Kim [P08] systematically surveyed post-quantum cryptography design constraints for space systems, identifying computational fault tolerance as an essential prerequisite for orbit readiness, but noted the absence of lightweight software-level fault recovery architectures.

Prior research on fault detection for NTT arithmetic has predominantly targeted custom hardware accelerators (FPGA and ASIC). Paul et al. [P03] introduced Algebraic Invariant Checking (AIC) for Cooley-Tukey forward NTT butterflies on FPGA, verifying input-output mathematical relations with dedicated hardware logic. Sarker et al. [P04] proposed Recomputing with Shifted Operands (RESO) and residue checking for forward NTT architectures in IEEE TCAD. Paul et al. [P17] explored recomputation with modular offsets (REMO) for forward NTT butterfly units. These hardware approaches share notable constraints:
1. **Unmonitored Inverse Transforms:** They focus exclusively on the forward Cooley-Tukey NTT, leaving the inverse Gentleman-Sande NTT (which accounts for 45% of decapsulation arithmetic in ML-KEM-768) unmonitored.
2. **Platform Dependency:** They require custom FPGA LUT logic or redundant ASIC functional units, offering no viable solution for software stacks running on embedded general-purpose microprocessors.
3. **Detection-Only Abort:** They trigger unconditional abort flags upon detection, providing no localized recovery mechanism.

Generic software-implemented fault tolerance (SWIFT) [P12] applies compiler-level instruction duplication across general software, but incurs substantial runtime overhead (~+41%) and severe register pressure, lacking awareness of cryptographic algebraic structure.

### Contributions

To address this gap under an explicitly scoped non-adversarial radiation model, this paper presents a software-level fault-resilience architecture for ML-KEM-768. Our contributions are:

1. **Software Dual-Transform Invariant Formulation:** Acknowledging prior art on CT forward invariant checking in hardware [P03], we derive complementary sum and multiplier algebraic invariants for the Gentleman-Sande (GS) inverse NTT ($r_0 + \zeta r_1 \equiv 2u \pmod q$) and implement a unified C software monitor covering all 9,856 butterfly operations in ML-KEM-768 decapsulation.
2. **Localized Register Rollback and Bounded Retry:** We design an in-place register rollback mechanism that preserves pre-butterfly operands in compiler-allocated stack registers, re-executing faulted butterflies upon transient invariant violation. In production evaluation, this achieves 100/100 genuine recoveries under transient single-bit multiplier faults ($F4$).
3. **Characterization of Circular Verifier Blindness:** We identify and quantify a specific common-mode verification failure in standalone software harness models where recovery snapshots co-located with live state in memory are corrupted simultaneously with the computation, causing local verifiers to falsely pass corrupted outputs with 94.0–100.0% probability across six fault targets ($F1, F2, F6, F7, F9, F10$).
4. **End-to-End Containment and SDC Assessment:** Across 300 active software fault-injection trials in compiled production code, zero Silent Data Corruption events were observed (0/300, 95% Wilson score CI: $[0.00\%, 1.26\%]$). We demonstrate that the outer Fujisaki-Okamoto re-encryption check serves as an independent failsafe boundary, enforcing constant-time pseudo-random implicit rejection ($K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$) whenever local recovery fails or persistent faults ($F5A, F5B$) occur.

The remainder of this paper is organized as follows. Section 2 establishes the non-adversarial threat model and the SIFA boundary. Section 3 details the mathematical derivation of dual-transform invariants and the rollback protocol. Section 4 presents the software implementation. Section 5 reports experimental fault-injection results. Section 6 provides comparative analysis with prior art. Section 7 presents a targeted survey of related literature. Section 8 concludes with future work.

---

## 2. Threat Model and Security Boundaries

### 2.1 Non-Adversarial Stochastic Fault Model

We evaluate computational resilience under a non-adversarial, stochastic fault model representative of Single Event Upsets (SEUs) induced by cosmic ray heavy ions, solar energetic particles, or secondary atmospheric neutrons interacting with semiconductor memory and ALU logic [P01, P02]:

- **Arrival Process:** Faults occur as statistically independent Poisson events with rate $\lambda$ determined by orbital flux and device cross-section. Faults are independent across distinct cryptographic sessions.
- **Bit Multiplicity:** Each single-event upset induces a 1-bit transient inversion in processor ALU registers during butterfly arithmetic.
- **Temporal Duration:** Transient faults affect a single instruction or butterfly operation cycle. Recurring faults (modeled as multi-cycle inversions) and force-value corruptions are evaluated as distinct stress cases.
- **Fault Locus:** Software fault injection targets intermediate butterfly multiplier outputs ($\zeta \cdot v$ in CT-NTT; $\zeta^{-1}(u-v)$ in GS-InvNTT).

**Explicit Exclusions:** This research explicitly excludes active physical adversarial attacks, including:
- Laser fault injection (LFI), focused ion beam (FIB), and electromagnetic fault injection (EMFI).
- Microarchitectural memory disturbance attacks such as Rowhammer [P15].
- Deliberate instruction-skip attacks targeting branch instructions or hardware clock lines.
- Memory tampering targeting read-only twiddle factor tables ($\zeta$).

### 2.2 The SIFA Boundary and Non-Adversarial Scoping

Statistical Ineffective Fault Attacks (SIFA) [P11] demonstrate that recomputation or conditional error-handling under active fault injection enables complete secret key recovery. An adversary repeatedly injects faults into intermediate cipher states and records whether the device outputs a valid ciphertext or an error flag. Because the probability of an ineffective fault depends on intermediate secret values, the set of non-aborted executions exhibits statistically exploitable bias.

We emphasize: **The localized retry mechanism proposed herein is safe strictly within non-adversarial operating environments.** In deep-space, high-altitude, or satellite environments:
1. SEU events arrive stochastically at low average rates (e.g., $10^{-6}$ to $10^{-4}$ events/device-day), precluding repeated, targeted injection on identical key material.
2. The single-butterfly retry executes an identical arithmetic sequence regardless of operand values.
3. If an invariant failure recurs upon retry, execution immediately escalates to fail-stop implicit rejection, preventing repeated recomputation loops.

> **Crucial Security Boundary:** In deployments where physical tampering or active fault injection is part of the threat model, localized retry must be disabled, and the architecture must operate exclusively in detection-only fail-stop mode.

### 2.3 Evaluated Fault Injection Models

We evaluate four primary fault configurations using deterministic in-tree software hooks:

| Target | Model Semantics | Injection Point | Mechanism Exercised | Trials |
|:---|:---|:---|:---|:---:|
| **F4** | Transient 1-bit XOR | CT-NTT butterfly multiplier output | Localized single-butterfly rollback & retry | 100 |
| **F5A** | Recurring 1-bit XOR (6×) | CT-NTT butterfly multiplier output | Escalation to fail-stop implicit rejection | 100 |
| **F5B** | Software force-value ($t \leftarrow 0$) | CT-NTT butterfly multiplier output | Persistent fault detection & failsafe | 100 |
| **F12** | Clean execution (0 faults) | None (unfaulted baseline) | Functional baseline control | 100 |

*Clarification on Target F5B:* Target $F5B$ is an abstract software debug hook that forces an intermediate multiplier variable to zero (`*t = 0`). It evaluates monitor behavior when a variable is completely zeroed, but does not model physical hardware stuck-at faults, analog silicon latch-up, or gate-level oxide breakdown.

### 2.4 Out-of-Scope Hardware Vectors

1. **Twiddle Factor Corruption:** Ravi et al. [P05] proved that corrupting stored twiddle constants ($\zeta$) bypasses arithmetic checks. Algebraic invariants cannot detect twiddle table corruption because the invariant calculations assume $\zeta$ is authentic. Mitigating this requires static ROM checksums or hardware BIST.
2. **Fujisaki-Okamoto Comparison Skipping:** Hermelink et al. [P06] demonstrated chosen-ciphertext recovery by skipping ciphertext equality checks. While our software incorporates a dual-rail comparison check in `kem.c`, physical laser or clock-glitch instruction skipping lies outside our software model. Protocol-level verifiable decapsulation [P16] provides an orthogonal defense.
3. **Microarchitectural Side-Channels:** Source-level constant-time coding does not guarantee machine-level invariance, as highlighted by the KyberSlash division vulnerabilities [P14]. Formal side-channel evaluation on compiled binaries remains future work.

---

## 3. Algebraic Invariant Monitoring and Localized Rollback

### 3.1 ML-KEM-768 Decapsulation Arithmetic

ML-KEM-768 performs modular polynomial arithmetic in $R_q = \mathbb{Z}_q[X]/(X^{256}+1)$ with modulus $q = 3329$. Complete decapsulation executes:
1. **Inverse NTT** on the received ciphertext polynomial vector $\mathbf{u}$ ($k=3$ polynomials).
2. **Forward NTT** on secret key vector $\mathbf{s}$ ($k=3$ polynomials) and polynomial vector arithmetic.
3. **Inverse NTT** on the inner product $\mathbf{s}^T \mathbf{u}$ ($1$ polynomial) to recover candidate message $m'$.
4. **Fujisaki-Okamoto Re-encryption:** Encryption of candidate message $m'$ requires forward NTT transforms across vector $\mathbf{r}$ ($k=3$ polynomials) and inverse NTT transforms on reconstructed ciphertext components ($1$ polynomial).

Each 256-coefficient polynomial transform consists of 7 layers with $n/2 = 128$ butterflies per layer, yielding exactly:
$$\text{Butterflies per polynomial} = 7 \times 128 = 896$$
Across complete decapsulation and re-encryption, exactly 11 polynomial transforms are executed:
$$\text{Total decapsulation butterflies} = 11 \times 896 = 9{,}856$$
The dual-transform monitor instruments every butterfly operation across all 11 transforms.

### 3.2 Cooley-Tukey (CT) Forward Invariant

The Cooley-Tukey butterfly computes:
$$r_0 = u + \zeta \cdot v \pmod{q}$$
$$r_1 = u - \zeta \cdot v \pmod{q}$$
where $u, v \in \mathbb{Z}_q$ are input coefficients and $\zeta$ is the layer twiddle factor.

Following the algebraic checking principle utilized in hardware by Paul et al. [P03]:
- **Sum Invariant:**
  $$r_0 + r_1 \equiv (u + \zeta v) + (u - \zeta v) \equiv 2u \pmod{q}$$
- **Difference Invariant:**
  $$r_0 - r_1 \equiv (u + \zeta v) - (u - \zeta v) \equiv 2\zeta v \pmod{q}$$

If an arithmetic upset corrupts the multiplier output $\zeta v \to \zeta v + \epsilon$, the outputs become $r_0' = u + \zeta v + \epsilon$ and $r_1' = u - \zeta v - \epsilon$. In this scenario, $r_0' + r_1' = 2u$ remains satisfied, but the difference invariant detects the error:
$$r_0' - r_1' \equiv 2\zeta v + 2\epsilon \not\equiv 2\zeta v \pmod{q} \quad (\text{for } 2\epsilon \not\equiv 0 \pmod{q})$$
Evaluating both sum and difference relations provides comprehensive detection across both input and multiplier paths.

### 3.3 Gentleman-Sande (GS) Inverse Invariant

The inverse NTT uses Gentleman-Sande butterflies:
$$r_0 = u + v \pmod{q}$$
$$r_1 = \zeta^{-1}(u - v) \pmod{q}$$
We derive complementary algebraic relations:
- **Sum Invariant:**
  $$r_0 + \zeta \cdot r_1 \equiv (u + v) + \zeta \cdot \zeta^{-1}(u - v) \equiv (u + v) + (u - v) \equiv 2u \pmod{q}$$
- **Multiplier Invariant:**
  $$r_0 - \zeta \cdot r_1 \equiv (u + v) - (u - v) \equiv 2v \pmod{q}$$

If an upset corrupts $r_1 \to r_1 + \epsilon$, the sum check fails:
$$r_0 + \zeta(r_1 + \epsilon) \equiv 2u + \zeta\epsilon \not\equiv 2u \pmod{q}$$
This formulation provides complete invariant coverage for inverse NTT transforms, addressing the 45% arithmetic blind spot present in prior forward-only detection schemes.

### 3.4 Localized Rollback and Bounded Retry Protocol

Upon detecting an invariant violation during butterfly execution:
1. **Operand Restoration:** The pre-butterfly input coefficients $(u, v)$ are restored from stack-resident local snapshot variables captured prior to butterfly execution.
2. **Localized Re-execution:** The single faulted butterfly is recomputed using authentic restored inputs.
3. **Invariant Re-verification:** The algebraic invariants are re-evaluated on the fresh butterfly outputs.
4. **State Transition:**
   - *Case 1 (Transient Fault Cleared):* If re-verification succeeds, the corrected outputs are written to the polynomial array. The monitor increments `recovered_count` and execution proceeds uninterrupted.
   - *Case 2 (Persistent Fault Detected):* If re-verification fails, `persistent_count` is incremented, the monitor sets `internal_status = 0xFFFFFFFF`, and the KEM decapsulation terminates normal processing, escalating to FIPS 203 implicit rejection:
     $$K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$$

Retry is strictly bounded to a single attempt ($N_{\text{retry}} = 1$) to eliminate execution divergence and prevent timing channels under stochastic radiation bursts.

---

## 4. Implementation Details

### 4.1 Software Architecture and In-Tree Hooks

The framework is implemented within `mlkem-native` (commit `fc269bc2d106`), an optimized C reference for FIPS 203. Fault instrumentation hooks are compiled via `-DMLKEM_RESEARCH_FAULT_HOOKS`. In baseline production builds, monitoring macros compile to zero instructions.

In `kem.c` (lines 476–504), the Fujisaki-Okamoto comparison loop incorporates dual-rail verification:
```c
/* Dual-rail constant-time comparison */
int fail1 = mlk_ct_memcmp(cmp_c, c, MLKEM_CIPHERTEXTBYTES);
int fail2 = mlk_ct_memcmp_reverse(cmp_c, c, MLKEM_CIPHERTEXTBYTES);
if (fail1 != 0 || fail2 != 0 || fail1 != fail2) {
    /* Hard-forced implicit rejection */
    mlk_ct_cmov(ss, rej_key, MLKEM_SSBYTES, 1);
}
```
This dual-rail check ensures that faults disrupting a single comparison loop do not suppress implicit rejection.

### 4.2 Isolation of Recovery Snapshots

Our investigation of common-mode failure (Section 5.2) demonstrates that storing recovery snapshots in heap buffers or shared polynomial memory creates critical vulnerability to co-located corruption. In our implementation, recovery snapshots are stored as local stack variables within the innermost butterfly loop in `poly.c`. On modern optimizing compilers (Clang/GCC with `-O2`), these snapshots are allocated directly into CPU registers, isolating them from array-level memory faults.

### 4.3 Timing and Control-Flow Considerations

Inside the butterfly arithmetic, constant-time operations are maintained via branch-free selection masks (`cmov`-equivalent primitives). However, when a fault is detected, the monitor conditionally executes the rollback and retry path. 

**Timing Limitations:** We emphasize that this implementation does **not** claim certified constant-time security under fault conditions. While clean-path execution exhibits consistent execution timing (measured at $1.0005\times$ relative to unprotected baselines on desktop microbenchmarks), activating the recovery path introduces control-flow divergence. Microarchitectural timing leakage analysis using Test Vector Leakage Assessment (TVLA) or dudect has not been performed on the compiled binary and remains necessary future work before deployment in settings vulnerable to microarchitectural side-channels.

### 4.4 Build Verification and Test Suite

The implementation was validated against:
- NIST FIPS 203 Known Answer Test (KAT) test suite (6 passing test vectors).
- Functional unit test suite across NTT, InvNTT, and FO re-encryption (84 passing test cases).
- Clean baseline control trials ($n=100$, Target $F12$) with zero false-alarm triggerings.

---

## 5. Experimental Evaluation

### 5.1 Experimental Setup

- **Platform:** macOS AArch64 (Apple Silicon M-series), Apple Clang 15.0, optimization `-O2`.
- **Fault Harness:** In-tree deterministic C fault-injection hooks activated via environment seeds.
- **Trial Structure:** 300 active fault trials (100 each for $F4, F5A, F5B$) plus 100 clean baseline controls ($F12$).
- **Oracle Verification:** Each trial's emitted 32-byte shared secret was verified byte-for-byte against an independent clean-room reference oracle computing both $K_{\text{valid}}$ and $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$.

### 5.2 Common-Mode Verification Failure: Circular Verifier Blindness ($H_1$)

To evaluate the risks of co-located snapshot storage, we constructed standalone software harness models simulating in-place memory corruption where recovery snapshots share memory regions with the protected polynomial state. Across six target configurations, local recovery verifiers consistently exhibited high false-pass rates:

| Target Configuration | Tested Transform Locus | False-Pass Rate | Common-Mode Failure Mechanism |
|:---|:---|:---:|:---|
| **F1** | Forward NTT, layer 0, bit 0 | 100.0% | Corrupted snapshot validates corrupted output |
| **F2** | Forward NTT, layer 0, bit 7 | 100.0% | Corrupted snapshot validates corrupted output |
| **F6** | Inverse NTT, layer 0, bit 0 | 94.0% | Corrupted snapshot validates corrupted output |
| **F7** | Inverse NTT, layer 0, bit 7 | 100.0% | Corrupted snapshot validates corrupted output |
| **F9** | Pointwise multiplication, coeff bit 0 | 100.0% | Co-located reference corrupted |
| **F10** | Pointwise multiplication, coeff bit 7 | 100.0% | Co-located reference corrupted |

**Analysis:** This demonstrates *circular verifier blindness*, an instance of common-mode failure in modular redundancy. When an upset corrupts shared memory, both the live butterfly computation and the snapshot reference are perturbed. The post-retry verifier evaluates a corrupted output against a corrupted snapshot, falsely concluding that recovery succeeded. This finding justifies our architectural decision to isolate recovery snapshots within compiler-managed registers.

### 5.3 Production Fault Resilience Results

| Target ID | Injected Fault Model | Active Trials | Genuine Recovery | Safe Fail-Stop | SDC Observed | Emitted Shared Secret ($K$) |
|:---|:---|:---:|:---:|:---:|:---:|:---|
| **F4** | Transient 1-bit XOR | 100 | 100 (100%) | 0 | 0 | $K_{\text{valid}}$ (Matches Oracle) |
| **F5A** | Recurring 6× 1-bit XOR | 100 | 0 | 100 (100%) | 0 | $K_{\text{rej}}$ (Matches Oracle) |
| **F5B** | Software Force-Value ($t \leftarrow 0$) | 100 | 0 | 100 (100%) | 0 | $K_{\text{rej}}$ (Matches Oracle) |
| **F12** | Clean Baseline Control | 100 | N/A | N/A | 0 | $K_{\text{valid}}$ (Matches Oracle) |

#### Target F4 (Transient Multiplier Faults)
Across all 100 trials, the monitor recorded: `actually_triggered = 1`, `mismatch_count = 1`, `recovered_count = 1`, `persistent_count = 0`, `internal_status = 0x5A5A5A5A`, and `actual_ss_hex == oracle_valid_hex`. Causal code inspection confirms that `recovered_count` cannot increment unless the post-retry verification passes both sum and difference invariants.
$$\text{F4 Recovery Rate} = 100/100 \quad (95\% \text{ Wilson score CI: } [96.3\%, 100.0\%])$$

#### Targets F5A and F5B (Persistent & Force-Value Faults)
Under recurring 6× bit inversions ($F5A$) and software force-value register zeroing ($F5B$), all 200 trials recorded `persistent_count >= 1`, `internal_status = 0xFFFFFFFF`, and emitted the exact FIPS 203 implicit rejection key ($K_{\text{actual}} == K_{\text{rej}}$).
$$\text{Fail-Stop Containment Rate} = 200/200 \quad (95\% \text{ Wilson score CI: } [98.1\%, 100.0\%])$$

### 5.4 Silent Data Corruption Assessment ($H_2$)

Silent Data Corruption (SDC) occurs if decapsulation completes with status indicating success but emits a shared secret $K$ that is neither the authentic key $K_{\text{valid}}$ nor the valid implicit rejection key $K_{\text{rej}}$:
$$\text{SDC} \iff (K \neq K_{\text{valid}}) \land (K \neq K_{\text{rej}}) \land (\text{status} \neq \text{ABORT})$$

Across all active software fault-injection trials:
$$P_{\text{SDC}} = \frac{0}{300} = 0.00\%$$
$$\text{95\% Wilson score confidence interval: } [0.00\%, 1.26\%]$$

*Methodological Clarification on Denominator:* The denominator is strictly $n = 300$ active fault trials (100 each for $F4, F5A, F5B$). Clean baseline trials ($F12, n=100$) are excluded because they do not exercise fault detection or containment logic.

**End-to-End Containment:** This result illustrates the two-tier containment structure: even in scenarios where localized checks fail (such as harness-level circular blindness), the outer Fujisaki-Okamoto re-encryption check compares the reconstructed ciphertext against the original received ciphertext, preventing corrupted keys from being established.

### 5.5 FIPS 203 Implicit Rejection Conformance

To confirm that the containment path conforms strictly with FIPS 203 Section 7.3, 100 controlled single-bit ciphertext corruptions were processed through the decapsulation engine. All 100 trials emitted shared secret keys matching an independent clean-room Keccak-f[1600] reference oracle:
$$\forall i \in \{1, \dots, 100\}: K_{\text{actual},i} == K_{\text{oracle\_rej},i}$$
This demonstrates that fail-stop escalation adheres bit-for-bit to NIST implicit rejection semantics.

### 5.6 Performance Overhead

Benchmarking was conducted on macOS AArch64 (Apple Silicon, Clang -O2) executing 10,000 decapsulation cycles:

| Architecture Configuration | Relative Latency | Latency Overhead | Memory Allocation |
|:---|:---:|:---:|:---:|
| Clean ML-KEM-768 Baseline | $1.000 \cdot T_0$ | Baseline ($0.0\%$) | Zero Heap |
| **Native Dual-Transform Invariant Monitor** | $1.253 \cdot T_0$ | **+25.3%** | **Zero Heap** |
| Software Sequential DMR (Dual Run + Compare) | $2.490 \cdot T_0$ | +149.0% | Heap/Stack Buffers |

*Performance Provenance:* In earlier cleanroom testing under varying compiler optimization flags (Phase 7K), monitored decapsulation overhead ranged between +16.79% and +28.91%, while software-sequential DMR ranged between +140.3% and +160.8%. The +25.3% figure reflects our production `-O2` benchmark. Invariant checking achieves a ~5.9× overhead reduction relative to full software duplication because it verifies algebraic relationships between existing register outputs rather than repeating the entire sequence of polynomial transforms.

---

## 6. Discussion and Comparative Analysis

### 6.1 Positioning with Closest Prior Art

| Evaluation Feature | Paul et al. [P03] (ACM TECS 2026) | Sarker et al. [P04] (IEEE TCAD 2023) | Fritzmann et al. [P13] (DATE 2019) | SWIFT [P12] (CGO 2005) | **This Work** |
|:---|:---|:---|:---|:---|:---|
| **Platform Target** | FPGA Hardware | FPGA / ASIC Hardware | RISC-V Hardware Coprocessor | General Software (CPU) | **General Software (C99)** |
| **Transform Coverage** | Forward CT NTT only | Forward CT NTT only | Forward NTT only | Non-cryptographic general code | **Forward CT + Inverse GS NTT** |
| **Detection Technique** | Algebraic Invariant (AIC) | Shifted Operands (RESO) | Hardware Exception Flags | Instruction Duplication | **Algebraic Invariant (Sum/Diff)** |
| **Recovery Mechanism** | None (Abort Flag) | None (Abort Flag) | None (Vulnerability Study) | None (Trap Handler) | **Register Rollback & Single Retry** |
| **Fault Coverage** | Transient Hardware Glitches | Transient Hardware Errors | SDC Rate Quantification | Register/ALU SEUs | **Transient & Persistent SEUs** |
| **Reported Overhead** | +8.5%–21.4% FPGA LUTs | +18%–34% FPGA Area | Hardware Area Increase | +41% CPU Execution Time | **+25.3% CPU Execution Time** |

- **Paul et al. [P03]:** The primary conceptual ancestor. While Paul et al. established the viability of Cooley-Tukey sum invariants on FPGA accelerators, our work demonstrates: (1) extension to Gentleman-Sande inverse transforms via novel sum-multiplier invariants, (2) native software implementation without dedicated hardware logic, and (3) fine-grained single-butterfly rollback rather than unconditional abort.
- **Sarker et al. [P04]:** Employs operand shifting (RESO) on hardware NTTs, requiring redundant arithmetic units. Our approach relies on intrinsic algebraic relations, avoiding hardware duplication.
- **Fritzmann et al. [P13]:** Conducted fault-injection vulnerability assessments on RISC-V NTT coprocessors, measuring SDC rates (3.66%–4.96%) and noting detection-only abort mechanisms. Our work adds active software recovery.
- **SWIFT [P12]:** Duplicates all instructions at the compiler level, incurring ~+41% overhead and heavy register pressure. Our domain-specific invariants achieve comparable error detection at +25.3% overhead by verifying mathematical invariant properties rather than blind duplication.

### 6.2 The Dual-Boundary Containment Model

A principal insight of this architecture is the complementary interaction between arithmetic-level and protocol-level defenses:
1. **Tier 1 (Local Recovery):** Monitors arithmetic butterflies in real time, repairing isolated transient SEUs without dropping frames.
2. **Tier 2 (Outer FO Containment):** If a fault evades local checks—or in harness models where circular verifier blindness occurs—the outer Fujisaki-Okamoto re-encryption check detects ciphertext discrepancies and enforces constant-time implicit rejection.

This structure enables post-quantum implementations to maintain high service availability under benign radiation environments while preserving cryptographic containment.

---

## 7. Targeted Literature Survey

- **Space Radiation Effects:** Dodd and Massengill [P01] detail the physical mechanisms of single-event upsets in microelectronics. ECSS-Q-ST-60-15C [P02] specifies European space engineering standards for radiation hardness assurance and fault tolerance in space electronics.
- **Cryptographic Fault Vulnerabilities:** Ravi et al. [P05] demonstrated twiddle factor fault attacks on NTT implementations in TCHES 2023. Hermelink et al. [P06] established chosen-ciphertext key recovery via FO bypass in INDOCRYPT 2021. Delvaux [P07] demonstrated fault attacks on higher-order masked Kyber implementations. Dobraunig et al. [P11] proved that recomputation under active fault injection enables SIFA.
- **Side-Channel and Microarchitectural Attacks:** Kannwischer et al. [P14] disclosed KyberSlash, showing timing vulnerabilities in non-constant-time division. Amer et al. [P15] demonstrated PQ-Hammer at IEEE S&P 2025, recovering secret keys from lattice KEMs via DRAM Rowhammer disturbances.
- **Hardware NTT Fault Detection:** Paul et al. [P03] (ACM TECS 2026) developed AIC error detection for FPGA-based NTT cores. Sarker et al. [P04] (IEEE TCAD 2023) developed RESO architectures for NTT. Fritzmann et al. [P13] (DATE 2019) evaluated fault sensitivity of NTT hardware on RISC-V. Paul et al. [P17] proposed REMO for recomputation-based NTT monitoring on FPGA.
- **Software Fault Tolerance:** Reis et al. [P12] introduced SWIFT at CGO 2005 for software-implemented fault tolerance.
- **PQC Space Deployment:** Kim [P08] (Acta Astronautica 2026) published a comprehensive systematic survey of PQC algorithms and design constraints for space systems. Elewaily et al. [P10] (Ad Hoc Networks 2024) surveyed delay-tolerant networking for deep-space communications.
- **Protocol-Level Verification:** Glabush et al. [P16] (CRYPTO 2025) proposed verifiable decapsulation to bind FO re-encryption to key generation. NIST FIPS 203 [P18] defines the official ML-KEM standard.

---

## 8. Limitations and Threats to Validity

1. **Desktop Emulation Platform:** All evaluations were conducted on a desktop macOS AArch64 host. Benchmarking on real space-qualified microprocessors (e.g., Cobham Gaisler LEON3/SPARC V8 or NOEL-V RISC-V) is required to evaluate cache, memory bus, and register constraints under flight conditions.
2. **Absence of Physical Radiation Testing:** Fault injection was conducted via compiled software hooks. Physical heavy-ion beam testing (e.g., at RADEF or Brookhaven National Laboratory) is necessary for full technology readiness level (TRL) advancement.
3. **Software Force-Value Model:** Target $F5B$ simulates register clearing in software (`*t = 0`), which does not capture physical analog phenomena such as silicon latch-up, power droop, or gate-oxide breakdown.
4. **Statistical Bound on SDC:** The observed zero SDC rate across 300 active trials establishes an upper confidence bound of 1.26% (95% Wilson score CI); it does not prove mathematical impossibility of SDC.
5. **Absence of Formal TVLA/dudect Timing Verification:** Although branch-free primitives are used on normal execution paths, formal microarchitectural timing leakage analysis has not been performed on the compiled binary.
6. **Twiddle Table Blind Spot:** Butterfly invariants cannot detect corruption residing in precomputed twiddle factor tables ($\zeta$).

---

## 9. Conclusion

We have presented a software-level fault-resilience architecture for ML-KEM-768 that balances cryptographic containment with operational availability in non-adversarial radiation environments. By combining Cooley-Tukey forward and Gentleman-Sande inverse algebraic invariants, the architecture monitors all 9,856 decapsulation butterflies with +25.3% execution latency. Localized register rollback achieves 100/100 recoveries under evaluated transient single-bit multiplier faults, while persistent faults escalate safely to FIPS 203 implicit rejection (200/200 safe aborts). Across 300 active fault trials, zero silent data corruption was observed (95% Wilson score CI: $[0.00\%, 1.26\%]$). Demonstrating this architecture on physical space-qualified microprocessors and conducting beam irradiation testing constitute essential next steps for orbital deployment.

---

## References

*(See [references.md](./references.md) for complete citations, DOI links, and publication metadata.)*
