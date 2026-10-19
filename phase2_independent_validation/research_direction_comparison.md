# Systematic Comparative Assessment of Candidate Research Directions

**Auditor:** Independent Cryptographic Auditor & Systems Engineering Researcher  
**Target:** Final-Year Computer Science Research Project Formulation  
**Date:** 2026-10-02  

---

## 1. Candidate Direction A: Independent Verification and Safe Recovery for Software ML-KEM

### 1.1 Precise Research Question
> *"Can software-based Algorithm-Based Fault Tolerance (ABFT) in ML-KEM-768 decapsulation achieve verified transient fault recovery without introducing common-mode constant vulnerabilities or macro-architectural timing leakage?"*

### 1.2 What Existing Work Already Covers
- **Forward Cooley-Tukey Invariants:** Formulated by Paul et al. (*IEEE TCAD 2024*) and Sarker et al. (*IEEE TVLSI 2023*) for hardware FPGA pipelines.
- **Twiddle Factor Fault Vulnerability:** Formally proven by Ravi et al. (*IACR TCHES 2023*), establishing that twiddle corruptions bypass butterfly output checks and enable full key recovery.
- **Microarchitectural Fault Injection on Kyber:** Hermelink et al. (*INDOCRYPT 2021*) and Pessl & Primas (*CHES 2021*).

### 1.3 Plausible Remaining Research Gap
Demonstrating that an in-tree software invariant monitor can detect faults in both forward and inverse NTT while maintaining verified snapshot parity and bounding intra-session timing leakage on embedded bare-metal microcontrollers (ARM Cortex-M4 / RISC-V).

### 1.4 Minimum Implementation Scope
1. Implement independent twiddle table hashing (pre-decapsulation CRC32 or SHA-256).
2. Wire up the unreferenced `g_trusted_zetas[128]` into `monitor_fqmul`.
3. Implement non-tautological diverse recovery verification (e.g. 2-bit interleaved snapshot parity).
4. Implement dummy re-encryption padding to equalize fail-stop and retry execution timelines.

### 1.5 Minimum Experiment Set
- Exhaustive fault injection across all 9,856 decapsulation butterflies (Forward CT + Inverse GS).
- Evaluation of multi-bit upsets in `.rodata` and `.data` sections.
- Constant-time TVLA / dudect leakage analysis ($N \ge 100,000$ decapsulations) to prove absence of timing oracles.

### 1.6 Required Baselines
- Unprotected `mlkem-native` baseline.
- Software-sequential Dual Modular Redundancy (DMR).
- Hardware-assisted ECC/EDAC memory emulation.

### 1.7 Main Technical Risks
- **Compiler Invalidation:** Optimizing compilers can merge tables (ICF) or reorder instructions, breaking verification independence.
- **Timing Leakage:** In-place retry introduces variable execution paths that are inherently difficult to make strictly constant-time in software.

### 1.8 Falsification Criteria
The hypothesis is falsified if:
1. In-place retry execution leaks secret-dependent timing information under TVLA ($t > 4.5$).
2. The runtime overhead exceeds that of optimized compiler-level or hardware-assisted redundancy ($> 50\%$).

### 1.9 Final-Year Project Feasibility
- **Feasibility:** **Moderate.** Requires extensive bare-metal embedded assembly auditing and side-channel evaluation setup. High risk of encountering subtle compiler optimization pitfalls.

---

## 2. Candidate Direction B: Cross-Layer Fault Resilience for Secure Space Communications

### 2.1 Precise Research Question
> *"Does coordinating computational fail-stop ML-KEM-768 endpoints with transport-level Automatic Repeat reQuest (ARQ) achieve higher session availability and zero key leakage under combined space radiation SEUs and channel packet loss compared to isolated microarchitectural rollback?"*

### 2.2 What Existing Work Already Covers
- **Cryptographic Fault Literature (Isolated Endpoints):** Focuses exclusively on algorithm-level attacks and countermeasures (Ravi 2023, Paul 2024, Hermelink 2021), treating the communication link as a static black box.
- **Space Communications Protocols:** CCSDS Space Packet Protocol and TC/TM standards define packet-level framing and ARQ, but assume classical cryptography or omit physical fault interactions.
- **Decoupled Architecture:** Standard network protocol layering (OSI / CCSDS).

### 2.3 Plausible Remaining Research Gap
Bridging the gap between post-quantum cryptographic fault resilience and space communication protocol engineering. Specifically: proving that treating PQC decapsulation as a strictly fail-stop primitive—and delegating recovery to an authenticated retransmission layer—eliminates microarchitectural timing channels, prevents key desynchronization, and maintains mission availability under high radiation flux.

### 2.4 Minimum Implementation Scope
1. A C/Python discrete-event space communications simulator modeling orbital radiation regimes (LEO, GEO, Deep Space).
2. Authenticated transport protocol pipeline (CCSDS-compliant framing, sequence windowing, CRC-16, HMAC-SHA256).
3. Fail-Stop ML-KEM-768 endpoint that deterministically releases $K_{\text{rej}}$ upon any computational fault.
4. Autonomous session resynchronization state machine with bounded ARQ retransmission.

### 2.5 Minimum Experiment Set
- Parametric sweep across orbital radiation SEU flux rates ($10^{-5}$ to $10^{-1}$ upsets/sec) and RF channel loss rates ($0\%$ to $15\%$).
- Evaluation of session establishment rate, authenticated delivery rate, goodput ratio, and end-to-end latency.
- State-machine verification proving that zero stale keys or desynchronized session states are ever reused.

### 2.6 Required Baselines
- Unprotected baseline (standard ML-KEM without monitoring or ARQ).
- Fail-stop endpoint without transport recovery (abort-only).
- Microarchitectural in-place retry endpoint (Direction A).
- Software DMR endpoint.

### 2.7 Main Technical Risks
- **Network Simulator Realism:** The simulator must accurately model realistic orbital link parameters (delay, jitter, Doppler, framing) to be taken seriously by aerospace reviewers.
- **Protocol Overhead:** ARQ retransmissions over high-latency links (e.g. Lunar/Deep Space, RTT $> 2.5\,\text{s}$) can degrade effective goodput if handshake timeouts are poorly tuned.

### 2.8 Falsification Criteria
The hypothesis is falsified if:
1. Transport-level retransmission incurs a bandwidth or latency overhead that exceeds the cost of microarchitectural DMR across all orbital radiation flux regimes.
2. Channel loss combined with decapsulation fail-stop leads to deadlock or unrecoverable session desynchronization.

### 2.9 Final-Year Project Feasibility
- **Feasibility:** **High.** Well-suited for a software-only computer science final-year project. Leverages existing working code in `spacecraft_protocol_sim.py` and `mlkem_native`, does not require expensive physical EMFI/laser benchtop hardware, and produces clear, actionable systems-level engineering tradeoffs.

---

## 3. Objective Comparative Matrix

| Evaluation Dimension | Candidate Direction A: Independent In-Tree Recovery | Candidate Direction B: Cross-Layer Protocol Resilience |
| :--- | :--- | :--- |
| **Primary System Layer** | Layer 0 (Microarchitectural ALU / Register State) | Cross-Layer (Layer 0 Endpoint + Layer 4 Transport) |
| **Threat Model** | Single-point physical fault injection (DFA / SIFA) | Joint Space Radiation SEU Flux + RF Channel Errors |
| **Failure Recovery Mechanism**| In-place register rollback & single retry | Protocol-level fresh handshake ARQ retransmission |
| **Side-Channel Timing Risk** | **High** (Retry path introduces execution timing variance) | **Low** (Decapsulation is strictly fail-stop / constant-time) |
| **Common-Mode Table Risk** | **High** (Susceptible to compiler table folding & SRAM upsets)| **Zero** (Fresh encapsulation on recovery generates fresh seed) |
| **Hardware Dependence** | Requires bare-metal embedded testbench (Cortex-M4/RISC-V)| Fully evaluable via reproducible software simulation |
| **Academic Novelty Positioning**| Incremental patch on existing ABFT literature (Paul 2024)| Interdisciplinary synthesis of PQC security and space systems |
