# Staged Implementation Roadmap & Execution Plan
**Project:** Adaptive, Resilient, Post-Quantum Space Communication Framework  
**Phase:** Phase 7 — Project Scope and Execution Roadmap  
**Date:** October 2026  
**Status:** Defensible Engineering Roadmap  

---

## 1. Project Scoping Strategy: Staged Deliverable Tiers

To ensure that the final-year research project reaches completion with high academic rigor and zero unfinished or broken components, development is partitioned into three strictly sequential tiers:

```
[Implementation Strategy]
  ├── Tier 1: Minimum Viable Framework (MVP) ──► Working software-only pipeline with isolated modules
  ├── Tier 2: Core Research Contribution     ──► Joint cross-layer controller, baselines 1-5, and evaluation
  └── Tier 3: Advanced Optional Extensions  ──► Microcontroller hardware cross-validation & multi-orbit passes
```

> **Golden Rule:** Development will advance to a subsequent tier **only after** all unit tests, integration targets, and verification audits of the preceding tier pass cleanly with 100% reproducible results.

---

## 2. Stage Breakdown & Execution Plan

### Stage 1: Minimum Viable Framework (Weeks 1–3)
* **Objective:** Establish the foundational end-to-end software pipeline linking application traffic, cryptographic security, basic packet framing, and the simulated Markov channel.
* **Core Tasks:**
  1. *Subsystem A (Application):* Implement telemetry generator generating parameterized Telecommand (TC) and Housekeeping (HK-TM) payloads with monotonic 64-bit sequence counters.
  2. *Subsystem B (Security):* Integrate standard C99 ML-KEM-768 key encapsulation and ChaCha20-Poly1305 AEAD authenticated encryption into a session handshake and transport wrapper.
  3. *Subsystem C (Resilient Comm):* Implement basic packetization, systematic parity block coding (FEC), and Stop-and-Wait / Selective Repeat framing.
  4. *Subsystem D (Channel):* Implement the discrete-time two-state Gilbert-Elliott Markov channel with parameterized loss and latency.
* **Verification & Test Gate:**
  - Automated integration test: 1,000 clean packets transmitted, encrypted, framed, passed through the channel, deframed, authenticated, and delivered with 100% bit-exact equivalence under nominal channel conditions ($P_{\text{loss}} = 0$).

---

### Stage 2: Endpoint Integration & Cross-Layer Signal Bus (Weeks 4–5)
* **Objective:** Connect the preserved PQC NTT fault resilience subsystem (`algorithms/source_ref/mlkem_fault_hooks.c`) to the communication pipeline and build the cross-layer status bus.
* **Core Tasks:**
  1. *Subsystem E Integration:* Wrap the native instrumented ML-KEM-768 decapsulation engine as a callable C library module. Verify that all 9,856 butterflies execute with in-place rollback active.
  2. *Cross-Layer Signal Interface:* Build a shared telemetry status bus reporting endpoint health tokens:
     - `CRYPTO_HEALTH_OK` (0x00)
     - `CRYPTO_RECOVERED_SEU` (0x01 — Rollback succeeded, session valid)
     - `CRYPTO_IMPLICIT_REJECT` (0x02 — Unrecoverable/persistent fault or invalid ciphertext, $K_{\text{rej}}$ generated)
  3. *FIPS 203 Rejection Containment:* Implement strict API fail-stop guards ensuring that receiving a rejection token causes the receiver to safely discard the session without crashing.
* **Verification & Test Gate:**
  - Inject 500 transient butterfly SEUs during active communication; verify that 100% recover locally without triggering link-layer packet retransmissions.

---

### Stage 3: Adaptive Resilience Controller & Baseline Implementations (Weeks 6–8)
* **Objective:** Implement the security-constrained Adaptive Resilience Controller and instantiate Baselines 1 through 4 for rigorous comparative evaluation.
* **Core Tasks:**
  1. *Subsystem F (Adaptive Controller):* Implement the constrained optimization decision engine:
     - Continuously estimates channel loss rate ($\hat{P}_{\text{loss}}$) and burst length ($\hat{L}_{\text{burst}}$).
     - Dynamically selects FEC code rate $R \in \{0.50, 0.75, 0.90\}$ and interleaving depth $D \in \{1, 4, 16\}$.
     - Enforces hard security guards (never disables AEAD, never accepts unverified plaintexts).
  2. *Baseline Harnesses:*
     - Instantiate Baseline 1 (Conventional fixed low FEC).
     - Instantiate Baseline 2 (Fixed heavy FEC + fixed interleaving).
     - Instantiate Baseline 3 (Channel-adaptive only, unmonitored crypto — El Bizri et al. 2026).
     - Instantiate Baseline 4 (Fixed FEC + software-sequential DMR crypto).
  3. *Ablation Suite:* Build toggles for Ablations 6A (No Rollback), 6B (No Interleaving), and 6C (No Cross-Layer Signaling).
* **Verification & Test Gate:**
  - Automated test verifying that hard security guards $\mathbf{C_1}, \mathbf{C_2}, \mathbf{C_3}$ cannot be breached even when the channel loss rate reaches 100%.

---

### Stage 4: Comprehensive Experimental Campaign & Analysis (Weeks 9–10)
* **Objective:** Execute the full 9-scenario experimental test suite across all 6 architectures and generate publication-grade statistical results.
* **Core Tasks:**
  1. *Campaign Execution:* Run $N = 10{,}000$ packets per scenario $\times$ 9 scenarios $\times$ 6 configurations ($540{,}000$ total packet transactions) using deterministic random seeds.
  2. *Metric Logging:* Record raw JSON logs capturing authenticated delivery rate, goodput, latency percentiles ($p50, p95, p99$), spurious retransmissions, and resource use.
  3. *Statistical Evaluation:* Compute Clopper-Pearson exact confidence intervals, Wilson score bounds for zero-SDC validation, and effect sizes (Cohen's $d$).
  4. *Automated Plotting:* Generate publication-ready vector figures (PDF/SVG) for goodput vs. loss, latency vs. burst length, and energy overhead trade-offs.
* **Verification & Test Gate:**
  - All raw datasets verified for schema completeness and seed reproducibility.

---

### Stage 5: Advanced Optional Extensions (Weeks 11–12, Discretionary)
* **Scope:** Only initiated if Stages 1–4 are 100% complete and verified.
* **Potential Extensions:**
  - *Extension A (Physical Microcontroller Benchmark):* Cross-compile the framework for ARM Cortex-M4 (e.g., STM32F4 Discovery board) via FreeRTOS to record hardware cycle counts and memory consumption on space-representative silicon.
  - *Extension B (Multi-Orbit Ephemeris Sim):* Integrate realistic orbital pass contact windows (LEO ground pass of 8 minutes) to simulate end-to-end telemetry downlink pass budgets.

---

## 3. Dependency and Risk Management Matrix

| Risk ID | Description | Severity | Probability | Mitigation Strategy |
| :---: | :--- | :---: | :---: | :--- |
| **R1** | Scope creep into physical RF or orbital simulation | High | Medium | Strictly bound the scope to a software-only discrete-event model; use standard mathematical Markov models rather than physical propagation simulators. |
| **R2** | Modifying or breaking existing PQC fault-resilience code | Critical | Low | Checkpoint already permanently preserved in `archive/pqc-ntt-fault-resilience`; existing code is treated as an isolated read-only library module. |
| **R3** | Complexity of real-time multi-threaded simulation | Medium | Medium | Implement the simulation as a single-threaded, deterministic discrete-event loop; eliminates race conditions and ensures bit-exact reproducibility. |
| **R4** | Controller overhead masking link gains | Medium | Low | Use a table-driven or lightweight state-machine controller evaluating closed-form thresholds ($< 5\,\mu\text{s}$ decision latency). |
| **R5** | Peer reviewer skepticism of novelty | High | Medium | Strictly adhere to Outcome B: frame the work as an applied systems architecture, cross-layer co-design, and empirical evaluation study, avoiding exaggerated theoretical claims. |
