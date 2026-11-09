# Phase 02: Architecture & Threat Model Report
## ASTRA-Sec Development — Complete System Architecture, Threat Modeling, and Protocol Design

**Author:** ASTRA-Sec Development Agent  
**Date:** November 2026  
**Status:** Architecture Proposal (Review Gated — Implementation Awaits Approval)  
**Associated Architecture Documents:**
- [`docs/architecture.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/architecture.md): 7-Layer Architecture & Sequence Specification
- [`docs/threat-model.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/threat-model.md): Cyber and Radiation Threat Catalog
- [`docs/security-requirements.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/security-requirements.md): 10 Security Pillars & Acceptance Criteria
- [`docs/protocol-specification.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/protocol-specification.md): Wire Format, PQ-DR Ratchet, Nonces
- [`docs/data-flow.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/data-flow.md): Step-by-Step Data Transformations & Lifecycles
- [`docs/trust-boundaries.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/trust-boundaries.md): Trust Zone Delineation & Isolation Contracts

---

## 1. Executive Architecture Summary

ASTRA-Sec establishes the first unified framework integrating **Post-Quantum Cryptography (NIST FIPS 203/204)**, **Delay-Tolerant Networking (IETF RFC 9171 BPv7 / RFC 9172 BPSec)**, and **Software-Level Arithmetic Fault Resilience**.

The architecture operates across seven strictly decoupled functional layers:
- **L1 (Application):** Generates mission telecommands, housekeeping telemetry, and science payloads.
- **L2 (Message Security):** Manages BPSec BCB and BIB extension blocks, authenticated encryption (AES-256-GCM), and Post-Quantum Double Ratchet state evolution.
- **L3 (PQC Services):** Executes constant-time FIPS 203 ML-KEM-768 key encapsulation and FIPS 204 ML-DSA-65 digital signatures.
- **L4 (Fault Resilience):** Actively monitors all 9,856 NTT butterfly operations in decapsulation using sub-word algebraic invariants ($(u'+v') \equiv 2u \pmod q$), register snapshots (`u_saved, v_saved`), localized in-place rollback ($R_{max}=2$), and Twiddle Factor Integrity Binding (`tfib_ref.c`).
- **L5 (DTN Transport):** Packages bundles using RFC 9171 BPv7, managing multi-hop store-carry-forward routing across untrusted relay spacecraft without payload decryption.
- **L6 (Disruption & Recovery):** Coordinates non-volatile flash spooling, sliding-window Bloom filter replay protection, and crash-consistent state resumption.
- **L7 (Ground Verification & Audit):** Ingests FDIR telemetry counters (`astra_pqc_telemetry_t`), logs radiation anomalies, and maintains an immutable verification ledger.
- **Cross-Cutting Control Plane:** Governs node identity, key lifecycle, security policies, and configuration management.

---

## 2. Multi-Hop Reference Scenario Alignment

The design is engineered around the target reference topology:

$$\textbf{Ground Station A (GSA)} \xrightarrow[\text{Uplink}]{\text{RF}} \textbf{Satellite 1 (SAT1)} \xrightarrow[\text{Crosslink}]{\text{ISL}} \textbf{Satellite 2 (SAT2)} \xrightarrow[\text{Downlink}]{\text{RF}} \textbf{Ground Station B (GSB)}$$

- **Nodes initially execute as independent software processes** communicating over local sockets (TCP/UDP convergence layers) simulating free-space propagation delays, occultations, and packet dropouts.
- **Zero Relay Plaintext Exposure:** SAT1 and SAT2 process only L5 primary routing headers. Payload blocks remain encrypted under L2 BCB blocks.

---

## 3. Threat Model Synthesis

The threat model rigorously separates intentional malicious adversaries from accidental physical space radiation faults:
1. **Malicious Threat Actors:** Passive quantum-equipped eavesdroppers ("harvest-now, decrypt-later"), active RF injectors, replay adversaries, and compromised relay spacecraft. Mitigated via FIPS 203 lattice hardness, FIPS 204 signatures, and monotonic ratcheting.
2. **Physical Radiation Environment:** Cosmic ray Single-Event Upsets (SEUs) and Single-Event Transients (SETs) inducing bit-flips in microprocessor ALU registers. Mitigated via L4 algebraic invariants, localized rollback, and persistent fail-stop containment ($\le 0.49\%$ SDC bound).
3. **Common-Mode & Checker Vulnerabilities:** Mitigated by pre-computation register snapshots (eliminating the 98.5% circular verifier failure rate) and TFIB reference tables (closing Theorem 1 twiddle blindness).

---

## 4. Unresolved Security Decisions (Open Items for User Review)

Before initiating Phase 03 implementation, the following five architectural decisions are documented for explicit review:

### Decision 1: Asymmetric Ratchet Trigger Policy
- *Option A:* Purely time-based (e.g., advance asymmetric ratchet every 24 hours of mission elapsed time).
- *Option B:* Purely message-count-based (e.g., advance ratchet every 100 bundles).
- *Option C (Recommended):* Hybrid trigger: advance on message count threshold ($N_{rot} = 100$) OR time threshold ($T = 86{,}400\,\text{s}$), with an explicit override flag in high-priority telecommands.
- *Impact:* Balancing the 1,088-byte ML-KEM ciphertext bandwidth overhead against forward secrecy granularity.

### Decision 2: Bloom Filter Memory Allocation vs Replay Window
- *Option A:* 4,096-bit (512-byte) filter supporting ~500 in-flight bundles with false positive rate $p < 0.01$.
- *Option B (Recommended):* 16,384-bit (2,048-byte) filter supporting ~2,000 in-flight bundles with $p < 0.001$, easily fitting within standard 64 KB microcontroller SRAM.
- *Impact:* Guarantees replay rejection across long store-and-forward delay windows.

### Decision 3: Multi-Thread Re-Entrancy for L4 Monitor State
- *Option A:* Single-threaded global monitor structs (`g_ntt_native_monitor`, `g_tfib_fault`) as currently implemented in `algorithms/source_ref/`.
- *Option B (Recommended):* Refactor L4 to accept an explicit opaque context pointer (`astra_pqc_ctx_t *ctx`), enabling thread-safe decapsulation across concurrent virtual channels on multi-core flight processors.
- *Impact:* Eliminates concurrency risk **RSK-03** identified in the Phase 00 risk register.

### Decision 4: Revocation Beacon Propagation Mechanism
- *Option A:* Reactive: Destination requests revocation check from Ground Station upon encountering unknown key fingerprints.
- *Option B (Recommended):* Proactive: Ground Station broadcasts signed `REVOCATION_BEACON` bundles with highest DTN priority (expedited bundle flags), instructing all intermediate relays to purge cached states.
- *Impact:* Prevents compromised nodes from receiving or forwarding bundles during occultation.

### Decision 5: Non-Volatile Flash Journaling Rate
- *Option A:* Synchronous write on every bundle derivation (maximum durability, higher flash wear).
- *Option B (Recommended):* Asymmetric-only synchronous write: write to NVRAM only when the root key advances via ML-KEM; maintain symmetric chain ratchets in RAM with periodic 60-second checkpoints.
- *Impact:* Protects satellite flash memory from write fatigue while maintaining crash consistency.

---

## 5. Review Gating Notice

> [!IMPORTANT]
> **Implementation Review Gating:**
> In strict accordance with the master project instructions, **no application C code implementation will commence until the architecture, threat model, and unresolved security decisions have been reviewed and approved by the project owner.**
