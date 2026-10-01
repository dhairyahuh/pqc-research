# Critical Design Decisions, Open Questions, and Strategic Assessment
**Project:** Adaptive, Resilient, Post-Quantum Space Communication Framework  
**Phase:** Redesign & Strategic Synthesis  
**Date:** October 2026  
**Status:** Defensible Strategic Blueprint  

---

## 1. Key Architectural Decisions & Technical Trade-Offs

### Decision 1: Single-Threaded Deterministic Discrete-Event Simulation vs. Real-Time Sockets
* **Chosen Approach:** Deterministic discrete-event simulation engine executed in a single-threaded loop with explicit PRNG seeds.
* **Rationale:** Real-time multi-threaded socket network simulators introduce non-deterministic OS scheduling jitter, race conditions, and platform-specific timing noise. A discrete-event model guarantees 100% bit-exact reproducibility across any host operating system (macOS, Linux, CI/CD pipelines) and allows executing 500,000 packet transactions in minutes rather than hours.

### Decision 2: Systematic Reed-Solomon Erasure Coding vs. LDPC
* **Chosen Approach:** Packet-level systematic Reed-Solomon / Parity block erasure coding.
* **Rationale:** Reed-Solomon is Maximum Distance Separable (MDS), guaranteeing optimal erasure correction ($e \le N - K$) for packet-level losses with simple algebraic bounds. LDPC requires iterative belief-propagation decoders that add massive code complexity and variable decoding latency unsuitable for deterministic microbenchmarking.

### Decision 3: Inviolable Security Constraints vs. Weighted Multi-Objective Penalty
* **Chosen Approach:** Security invariants (AEAD verification, ML-KEM-768 parameter floor) are formulated as **hard constraints** ($\mathcal{A}_{\text{feasible}} = \emptyset$ if violated), completely excluded from the objective function.
* **Rationale:** In standard weighted multi-objective optimization, a controller can mathematically "compensate" for an authentication bypass or security compromise if the throughput gain is sufficiently high. In high-assurance space avionics, security is an absolute prerequisite, not a negotiable trade-off.

---

## 2. Direct Answers to the Nine Strategic Evaluation Questions

### Question 1: Was the existing work safely checkpointed?
**Yes, completely and verified.**
- **Commit:** `8b2382d6da6be8e05ad9c54fe100bc0d092d6e4c`
- **Archival Branch:** `archive/pqc-ntt-fault-resilience`
- **Archival Tag:** `pqc-ntt-fault-resilience-v1`
- **Remote Push:** Verified on GitHub remote via `git ls-remote`.
- **Working Tree Integrity:** Uncommitted Phase 4B working-tree modifications and untracked KAT files were left completely intact and uncorrupted.
- **Documentation:** A comprehensive `CHECKPOINT_README.md` was created at the repository root.

---

### Question 2: What exactly is preserved?
The complete implementation and experimental validation of the NTT fault resilience research:
1. Native C99 reference implementations of ML-KEM-768 and ML-DSA-65 (`algorithms/source_ref/`).
2. Native in-tree butterfly monitoring instrumenting all 9,856 forward and inverse NTT butterflies in decapsulation.
3. In-place shadow register rollback engine yielding 100% transient fault recovery across 1,400 clean-room trials.
4. Fail-stop FIPS 203 implicit rejection ($K_{\text{rej}}$) and public API hardening.
5. Cycle-accurate benchmarking proving a 5.2$\times$ to 8.1$\times$ latency advantage over software DMR.
6. All historical phase documentation (`docs/phase2` through `docs/phase7l`).
7. Complete automated test suites passing with 100% success (`make test-phase7k` and `./bin/test_fips_kats`).

---

### Question 3: What does the literature already cover?
- **Space Communications & DTN:** Wondmagegn et al. (2025) and Elewaily et al. (2024) survey space channels, atmospheric turbulence, and delay-tolerant bundle protocols. However, they assume endpoint microprocessors compute with 100% perfection and experience zero radiation upsets.
- **Channel-Adaptive PQC:** El Bizri et al. (IEEE ICC 2026) investigate adapting PQC algorithm selection to channel SNR, but their model acts strictly at the link layer without modeling endpoint hardware faults, SEUs, or arithmetic recovery.
- **PQC Fault Attacks & Hardware ABFT:** Ravi et al. (2023) and Hermelink et al. (2021) demonstrate NTT twiddle and decapsulation fault vulnerabilities. Paul et al. (2024) and Sarker et al. (2023) formulate algebraic invariant checks for FPGA hardware, but their schemes are forward-only, detection-only (no recovery), and isolated from communication stacks.

---

### Question 4: Is there a defensible research gap?
**Yes, under Outcome B (Applied Systems Architecture & Empirical Co-Design).**
- There is a glaring disconnect in published literature: space communication protocols assume perfect onboard processors, while cryptographic fault-tolerance works assume isolated chips with perfect channels.
- **The Defensible Gap:** No existing work has designed, implemented, or empirically evaluated a **unified cross-layer framework that prevents communication-layer adaptation from compromising cryptographic security constraints under concurrent, changing space-channel fades and endpoint radiation SEUs**.

---

### Question 5: What should the final research question be?
> **"How can a software-only communication framework jointly adapt link-layer error control and endpoint cryptographic fault resilience to maximize authenticated telemetry/telecommand delivery across dynamic space channels without violating post-quantum cryptographic security constraints?"**

---

### Question 6: What is the proposed architecture?
A modular 6-layer software architecture:
1. **Application Layer:** Parameterized Telecommand, Housekeeping, and Science Data traffic profiles.
2. **Security Layer:** NIST FIPS 203 (ML-KEM-768) session establishment + ChaCha20-Poly1305 AEAD + 64-bit monotonic anti-replay counter.
3. **Resilient Communication Layer:** Framing, systematic Reed-Solomon erasure coding, block interleaving, and selective-repeat ARQ.
4. **Simulated Channel Layer:** Discrete-time 3-state Gilbert-Elliott Markov channel (Good, Bad, Outage) with variable propagation latency and burst erasures.
5. **Endpoint Computational Fault Subsystem:** Preserved native ML-KEM-768 C code with 9,856 monitored butterflies, in-place register rollback, and fail-stop implicit rejection.
6. **Adaptive Resilience Controller:** Constrained optimization engine observing channel loss and endpoint health, dynamically tuning FEC rate and interleaving depth under strict security guards.

---

### Question 7: What is the mathematical contribution?
- **Nature of Math:** The individual tools (Markov chains, Singleton bounds, error kernels) are established theory.
- **The Core Formulation:** The **Constrained Cross-Layer Optimization Problem**, which formally couples the endpoint arithmetic recovery probability ($R_{\text{rec}}$) with the channel packet erasure distribution $\bar{\epsilon}$ to maximize Effective Authenticated Goodput ($\mathcal{G}$) subject to hard, non-negotiable security invariants ($P_{\text{SDC}} = 0, P_{\text{Leak}} = 0$).

---

### Question 8: What should we implement first?
**Stage 1 (Minimum Viable Framework):**
Build the basic, deterministic software pipeline connecting application payload generation, ML-KEM-768 key encapsulation, ChaCha20-Poly1305 AEAD encryption, fixed packetization, and the two-state Gilbert-Elliott Markov channel. Verify that 1,000 packets transmit, encrypt, cross the channel, decrypt, and authenticate cleanly before introducing adaptive control or fault injection.

---

### Question 9: What are the biggest risks to completing a credible final-year project?
1. **Risk 1: Premature Feature Bloat (Scope Creep):** Attempting to build an entire orbital flight simulator or complex RF wave propagation model. *Mitigation:* Bound scope strictly to discrete-event packet simulation and Markov models.
2. **Risk 2: Breaking the Preserved PQC Baseline:** Modifying existing C reference code in ways that invalidate Phase 7K reproducibility. *Mitigation:* The checkpoint is isolated in `archive/pqc-ntt-fault-resilience`; the C files in `algorithms/source_ref/` are treated as a read-only library.
3. **Risk 3: Overstating Novelty to Academic Reviewers:** Claiming a "fundamental mathematical discovery" by combining existing components. *Mitigation:* Strictly adhere to Outcome B; defend the project as an applied cross-layer engineering architecture and rigorous empirical evaluation study.
