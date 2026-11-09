# Phase 1 — Document 01: Project Implementation Context & System Inventory

**Document ID:** `ASTRA-SEC-PH1-DOC-01`  
**Research Directorate:** Multidisciplinary Academic Evaluation Team  
**Date:** November 2026  
**Repository Branch:** `astra-sec` (HEAD `efb35d5` / `73edad8`)  

---

## 1. Project Background and Architectural Heritage

The ASTRA-Sec research codebase represents an evolution across two distinct research horizons:

1. **Foundational Low-Level Cryptographic Research (C99 Native):**
   - **Research Focus:** "Software-Level Fault Resilience for ML-KEM-768: Dual-Transform NTT Invariant Monitoring, Localized Register Rollback, and Containment".
   - **Target Primitive:** NIST FIPS 203 ML-KEM-768 key encapsulation/decapsulation.
   - **Core Mathematical Defense:** Monitoring sub-word Cooley-Tukey butterfly operations in the Number Theoretic Transform (NTT) using the modular invariant $r \equiv t\zeta \pmod q$, supported by an independent twiddle reference (TFIB-Ref), localized in-place stack rollback ($K \le 2$), and constant-time fail-stop suppression escalating to FIPS 203 implicit rejection.

2. **Network-Level Disruption-Tolerant Extension (Python 3.11+ / Hybrid Architecture):**
   - **Research Focus:** "ASTRA-Sec: Post-Quantum End-to-End Secure Messaging and Delay-Tolerant Cryptographic Resilience for Space Networks".
   - **Target Topology:** 4-node orbital store-and-forward communications network (`Ground Station A -> Satellite Relay 1 -> Satellite Relay 2 -> Ground Station B`).
   - **Core Protocol Layers:** Layer 1 Application Data Units (ADU), Layer 2 Authenticated Envelope Encryption (AES-256-GCM + Canonical AAD), Layer 3 PQC Services (ML-KEM-768 + ML-DSA-65), Layer 5 RFC 9171 BPv7 DTN Transport, Layer 6 SQLite WAL persistent spooling with sliding-window anti-replay, and Layer 7 FDIR telemetry.

---

## 2. Exhaustive Implementation Status Audit

Before identifying research gaps, we classify every existing subsystem based on the Phase 16 forensic audit:

| Subsystem / Component | Underlying Technology | File Location | Operational Reality | Research Utility |
| :--- | :--- | :--- | :--- | :--- |
| **Native ML-KEM-768 Core** | C99, Stack-Allocated, Constant-Time | `algorithms/source_ref/mlkem_native_monitored.c` | **FULLY FUNCTIONAL** | Clean baseline for fault injection; passes 1,000 KAT vectors; zero heap allocation on flight path. |
| **NTT Invariant Monitor** | C99, Modular Montgomery Check | `algorithms/source_ref/mlkem_native_monitored.c` | **FULLY FUNCTIONAL** | Implements $r \equiv t\zeta \pmod q$; detects 99.4% of single-bit SEUs with $+2.29\%$ overhead. |
| **Snapshot Rollback ($K \le 2$)** | C99, Stack Snapshots | `algorithms/source_ref/mlkem_native_monitored.c` | **FULLY FUNCTIONAL** | Bounded local retry; escalates to fail-stop implicit rejection upon second failure. |
| **Fault Injection Harness** | C99, In-Memory Bit-Flipping | `algorithms/source_ref/mlkem_fault_hooks.h` | **FULLY FUNCTIONAL** | Flips bits directly in CPU registers during NTT loops; passes 9 native fault campaigns. |
| **ML-DSA-65 Digital Signature** | C Python ABI bridge to LibOQS | `astra_sec/crypto/dsa.py` | **FULLY FUNCTIONAL** | NIST FIPS 204 compliant (1952 B pk, 4032 B sk, 3309 B sig); verified non-repudiation. |
| **L2 Envelope Encryption** | Python `cryptography` AES-GCM | `astra_sec/crypto/aead.py` | **FULLY FUNCTIONAL** | Encapsulates payloads with canonical AAD binding sender, recipient, epoch, and sequence. |
| **Double Ratchet Engine** | Python HKDF-SHA256 + KEM | `astra_sec/crypto/ratchet.py` | **FULLY FUNCTIONAL** | Provides forward secrecy and break-in recovery across command epochs. |
| **RFC 9171 BPv7 Engine** | Python `cbor2` serialization | `astra_sec/dtn/bpv7.py` | **FULLY FUNCTIONAL** | Pure-Python bundle serializer/parser; conforms to canonical RFC 9171 block formats. |
| **RFC 9172 BPSec Blocks** | Python CBOR extension blocks | `astra_sec/dtn/bpv7.py` | **FUNCTIONAL (BASIC)** | Encapsulates BIB and BCB blocks; supports hop-by-hop integrity checks. |
| **NASA/JPL ION Integration** | Config synthesis (`.ionrc`, `.bprc`) | `astra_sec/dtn/ion_config.py` | **SIMULATED / BRIDGED** | Synthesizes valid ION configuration files, but native `ionadmin` daemon is uninstalled on host OS. |
| **Persistent Spool Engine** | Python SQLite3 in WAL mode | `astra_sec/network/spool.py` | **FULLY FUNCTIONAL** | ACID-compliant bundle persistence; survives process `SIGKILL` and node reboots. |
| **4-Node Relay Topology** | Python In-Memory / HTTP sockets | `astra_sec/network/relay.py` | **FULLY FUNCTIONAL** | Routes bundles across GSA, SAT1, SAT2, GSB without relay payload decryption. |
| **Ground Station Verifier** | Python state tracking & trust | `astra_sec/security/verifier.py` | **FULLY FUNCTIONAL** | Enforces command dispatch authorization, ACK correlation, and replay rejection. |
| **FastHTML/FastAPI Dashboard** | Python Uvicorn + SSE | `astra_sec/ui/` | **FUNCTIONAL TOOLING** | Visualization tool; not part of the scientific core. |

---

## 3. Key Observations for Research Scoping

1. **The Core Cryptographic Novelty Resides in Layer 4:**
   - The C99 implementation of sub-word NTT butterfly invariant monitoring with localized stack rollback ($K \le 2$) is genuinely high-performing ($+2.29\%$ overhead vs $+101.49\%$ for DMR).
   - This capability exists, compiles natively, and has survived 3,000 fault injection tests with 0.00% SDC.

2. **The Multi-Node DTN Extension is Currently an Architectural Integration:**
   - The 4-node store-and-forward satellite pipeline, BPv7 CBOR serialization, and SQLite WAL spooling work reliably as an engineering system.
   - However, simply connecting an NTT fault monitor to a DTN bundle engine does **not** automatically establish academic novelty unless there is a formal, cross-layer coordination protocol that solves an unaddressed scientific failure mode.

3. **The Critical Research Question Identified:**
   - How does a DTN node handle cryptographic failures when transient cosmic SEUs, persistent hardware faults, network link disruptions, and security epoch transitions occur simultaneously?
   - In existing systems (e.g., standard DTN + standard PQC), a decapsulation fault either causes permanent packet drop or naive infinite retransmission. ASTRA-Sec has the unique structural ability to bridge low-level cryptographic rollback states with high-level DTN custody and delivery state transitions.
