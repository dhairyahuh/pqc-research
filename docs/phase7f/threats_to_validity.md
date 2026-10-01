# Phase 7F — Threats to Validity and Scientific Limitations

## 1. Overview

This document outlines the methodological boundaries, theoretical assumptions, and practical threats to validity associated with the fault resilience mechanisms developed throughout this research project. Transparent disclosure of these limitations is essential for rigorous paper synthesis.

---

## 2. Threats to Internal Validity

### 2.1 Harness Simulation vs Native Inline Instrumentation
- **Limitation:** In the Phase 7E fault injection harness, multi-layer stage monitoring was evaluated by passing a simulated status flag (`flg_e = MLK_STATUS_FAULT`) into `decaps_layered_stage_monitored()` rather than calling `mlkem768_poly_ntt_stage_monitored()` directly on intermediate decapsulation polynomials.
- **Impact:** While this accurately captures the macro-level recovery behavior of an ideal detector (showing that resetting transient hardware hooks enables successful retry), it did not subject the C-level butterfly invariant routine to concurrent fault injection during decapsulation.
- **Mitigation for Synthesis:** The paper must present the 1,050-trial recovery campaign as an *architectural recovery evaluation under simulated stage detection*, supported by separate mathematical proofs and standalone microbenchmarks.

### 2.2 Intermediate Product ($t$) Reuse and Multiplier Blind Spots
- **Limitation:** To achieve the claimed "zero additional modular multiplications," the intra-butterfly difference check reuses the intermediate product $t = \text{fqmul}(v, \zeta)$.
- **Impact:** Any transient or permanent fault in the multiplier ALU, twiddle factor register $\zeta$, or input operand $v$ prior to multiplication scales both butterfly outputs symmetrically, satisfying $(u' - v') - 2t \equiv 0 \pmod q$.
- **Mitigation for Synthesis:** The publication must explicitly distinguish between:
  1. *Output-register integrity checking* (achievable with zero extra multiplications).
  2. *Full butterfly arithmetic verification* (requiring independent recomputation of $t$, doubling Montgomery multiplications).

### 2.3 Single-Event Injection vs Complex Radiation Faults
- **Limitation:** The experimental campaigns injected single-event transients (bit flips, additive perturbations, stuck-at values) at localized loci.
- **Impact:** Heavy-ion strikes and high-energy cosmic rays in space environments can cause Multi-Bit Upsets (MBUs), clock glitches, or power-rail collapses affecting multiple butterfly operations or pipeline stages simultaneously.
- **Mitigation for Synthesis:** The scope of autonomous recovery claims must be explicitly restricted to Single Event Transients (SETs) and Single Event Upsets (SEUs).

---

## 3. Threats to External Validity

### 3.1 Scalar C Reference vs Vectorized SIMD Implementations
- **Limitation:** All experiments were conducted on the portable scalar C implementation (`mlkem-native` scalar backend).
- **Impact:** Production flight systems or high-throughput ground stations frequently utilize SIMD vectorization (ARM Neon on Cortex-A53, AVX2 on x86, or RISC-V Vector extensions). In SIMD implementations:
  - Cooley-Tukey butterflies are computed in parallel across 128-bit or 256-bit vector registers.
  - Faults in a vector lane or vector permute instruction propagate differently than scalar register corruptions.
  - Invariant checks must be vectorized to avoid severe performance penalties.

### 3.2 Target Platform Architecture
- **Limitation:** Performance benchmarks were measured on Apple Silicon (ARM64, M-series high-performance P-core with out-of-order execution, deep pipelines, and gigahertz frequencies).
- **Impact:** Spaceborne computers typically utilize radiation-hardened processors operating at 50–250 MHz (e.g., BAE RAD750, Cobham Gaisler GR740 LEON4, or Vorago VA416x0 ARM Cortex-M4).
- **Mitigation for Synthesis:** Report overhead both in absolute microseconds on the host testbed and in relative instruction/cycle estimates normalized for space-grade embedded processors.

---

## 4. Threats to Construct Validity

### 4.1 Conflation of Recovery ($R_R$) and Safe Rejection ($R_S$)
- **Limitation:** Early project reports occasionally conflated safe rejection with recovery under a single "100% resilience" umbrella.
- **Impact:** Safe rejection aborts the communication session, requiring re-keying or command retry over high-latency deep-space links. Autonomous recovery preserves session continuity without retransmission.
- **Mitigation for Synthesis:** The paper must maintain strict tripartite reporting:
  $$R_{\text{Total}} = R_R \text{ (Recovery)} + R_S \text{ (Safe Rejection)} + R_U \text{ (Undetected Corrupt Key)}$$
  emphasizing that $R_U = 0.0\%$ is the non-negotiable security requirement, while $R_R$ governs operational availability.

### 4.2 Constant-Time Assessment Under Error Conditions
- **Limitation:** Constant-time verification was demonstrated by comparing valid vs invalid ciphertexts in the absence of hardware faults (ratio 1.000x).
- **Impact:** When a physical fault is detected and triggers an autonomous retry, the re-execution path consumes additional cycles. If an adversary can selectively inject faults remotely (e.g., via electromagnetic fault injection or optical pulsing), the timing of the retry response could theoretically leak secret state.
- **Mitigation for Synthesis:** Clarify that internal monitoring is designed for environmental cosmic radiation, not hostile side-channel physical attackers with laboratory physical access to the spacecraft bus.

---

## 5. Space System Applicability Assessment

- **Mission Impact:** For deep-space missions (e.g., Mars orbital or interplanetary probes) where Round-Trip Light Time (RTLT) ranges from minutes to hours, an aborted KEM decapsulation invalidates an entire command uplink frame.
- **Flight Readiness:** The algorithmic invariants developed in this project provide a viable conceptual framework for low-overhead fault detection. However, full flight readiness requires:
  1. Formal verification of C code using tools such as CBMC or Frama-C.
  2. Integration with SpaceWire / CCSDS frame reassembly layers.
  3. Physical beam testing using heavy-ion accelerators (e.g., Texas A&M Cyclotron or CERN CHARM) on target space microprocessors.
