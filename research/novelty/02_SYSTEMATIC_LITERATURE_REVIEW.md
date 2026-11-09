# ASTRA-Sec: Systematic Literature Review (2016–2026)

**Authors:** Senior Academic Research Team  
**Evaluation Scope:** 15 Target Research Disciplines across PQC, Space Communications, DTN, Fault Resilience, and Distributed Protocol Verification.  
**Bibliographic Standards:** IEEE, ACM, Springer, Elsevier, USENIX, CCSDS, IETF, ESA, NASA/JPL.

---

## 1. Scope & Methodology

This systematic literature review surveys academic, governmental, and industrial publications between **2016 and 2026**. It evaluates state-of-the-art advancements across 15 distinct research domains to determine where existing technologies succeed, where their operational assumptions fail, and what technical whitespace remains for ASTRA-Sec.

---

## 2. Area-by-Area Deep Dives

### Area A: Post-Quantum Cryptography for Satellite & Space Communications
- **State of the Art:** Satellite systems have lifespans exceeding 10–25 years, exposing downlinks to "Harvest-Now, Decrypt-Later" (HNDL) attacks. In 2026, Kim (*Acta Astronautica*) and related studies surveyed PQC algorithm suitability for space links, standardizing on NIST FIPS 203 (ML-KEM-768) and FIPS 204 (ML-DSA-65) due to their balanced key size and runtime efficiency.
- **Key Finding:** While algorithmic suitability is well established, existing studies evaluate PQC under idealized hardware assumptions, completely ignoring physical single-event radiation upsets during polynomial computation.

### Area B: End-to-End PQC Security Architectures
- **State of the Art:** Contemporary end-to-end PQC frameworks wrap application payloads using hybrid or pure lattice-based envelopes (e.g., ML-KEM + AES-GCM + ML-DSA).
- **Key Finding:** Architectures assume reliable underlying transport (TCP/IP) or continuous point-to-point links. They break down in store-and-forward environments where handshakes cannot complete interactively.

### Area C: ESA E2EQSS (End-to-End Quantum-Safe Security for Satellite Data Links)
- **Primary Source:** European Space Agency ARTES 4S Project, led by VisionSpace Technologies, ATELERIS, ID Quantique, and FHNW (2023–2026).
- **Architecture & Capabilities:** Implements software-based PQC key management (ML-KEM, ML-DSA) and Quantum Random Number Generators (QRNG) on satellite flight processors.
- **Limitations & Gap:** E2EQSS operates exclusively at the **CCSDS Space Data Link Security (SDLS)** layer (Layer 2 frame level for direct, line-of-sight satellite-to-ground contacts). It does NOT support multi-hop store-and-forward Delay-Tolerant Networking (RFC 9171 BPv7), nor does it implement software-level arithmetic fault resilience or localized NTT snapshot rollback.

### Area D: ESA ACES & Space-Based Quantum Security Initiatives
- **Clarification:** The ESA Atomic Clock Ensemble in Space (ACES) is a fundamental physics/relativity experiment (mounted on ISS Columbus). ESA's actual quantum communication projects are EuroQCI initiatives (EAGLE-1, Saga) focusing on physical Quantum Key Distribution (QKD).
- **Key Finding:** Space QKD requires dedicated optical ground stations, fine pointing, and clear weather. Software PQC (algorithmic quantum resistance) is mandatory for RF/TT&C data channels.

### Area E: PQC Integration with CCSDS SDLS (CCSDS 355.0-B / 355.1-B)
- **State of the Art:** Standard SDLS provides frame security using AES-GCM or AES-CMAC. The Extended Procedures (SDLS-EP) address key management. Recent proposals introduce ML-KEM encapsulation into CCSDS Transfer Frames.
- **Key Finding:** SDLS is inherently hop-by-hop or link-by-link at the frame level. When frames traverse intermediate satellite relays or multi-segment ground networks, frames are decrypted at every hop unless tunneled through higher-layer protocols.

### Area F: BPv7 (RFC 9171), BPSec (RFC 9172), and NASA/JPL ION-DTN
- **Primary Sources:** IETF RFC 9171 (BPv7), RFC 9172 (BPSec), RFC 9173 (BPSec Default Security Contexts); NASA/JPL Interplanetary Overlay Network (ION) v4.1.2.
- **Capabilities:** BPSec provides per-block integrity (BIB) and confidentiality (BCB) across asynchronous store-carry-forward topologies.
- **Limitations & Gap:** RFC 9172 intentionally decouples security policy and key management. Standard security contexts specify classical AES-GCM and HMAC-SHA256. BPSec does not define PQC key establishment mechanisms, nor does it address endpoint radiation fault handling during decapsulation.

### Area G: Secure DTN Command and Telemetry Delivery
- **State of the Art:** Command delivery over DTN relies on signed bundles with sequence counters. Recent space mesh protocols explore distributed authorization.
- **Key Finding:** When an uplink command is queued across multi-hour orbital disruptions, stale authorizations, certificate revocations, and key rotations can occur mid-flight, creating undefined state transitions upon bundle arrival.

### Area H: Key Management, Rotation, and Revocation in Disrupted Networks
- **State of the Art:** Classical PKI (X.509, OCSP, CRLs) requires interactive connectivity to online Certificate Authorities, making it fundamentally incompatible with space DTNs.
- **Key Finding:** Solutions like asynchronous epoch-based trust stores or SDLS-DR (Ledin et al., 2026) provide periodic ratchet updates, but lack fault-aware recovery when decapsulation fails at the destination.

### Area I: PQC Implementation Fault Attacks and NTT Fault Detection
- **Primary Sources:**
  - Ravi et al. (CHES): *"Fiddling the Twiddle Constants"* — Fault injection on NTT twiddle constants recovers ML-KEM secret keys.
  - Bindel et al. / Delvaux: Fault-enabled chosen-ciphertext decryption failure oracle attacks against Kyber Fujisaki-Omoto (FO) transforms.
  - Paul et al. (2026): FPGA-based arithmetic invariant checkers for polynomial multiplication.
- **Key Finding:** Hardware implementations use dual-modular redundancy (DMR) or modular offset checks (REMO). In software, existing defenses rely on full re-execution (DMR $2\times$), incurring $+100\%$ CPU overhead.

### Area J: Software-Level SEU Simulation and Cryptographic Fault Injection
- **State of the Art:** Space processors in LEO/MEO experience Single-Event Upsets (SEUs) from galactic cosmic rays and solar particle events. Software fault injection tools (e.g., Sail, QEMU-based, or C macro hooks) flip bits in registers or memory.
- **Key Finding:** Existing software PQC libraries provide zero resilience: an SEU in an NTT coefficient propagates into corrupted polynomials, resulting in Silent Data Corruption (SDC) or decapsulation failure.

### Area K: Checker Independence, Common-Mode Failures, and Rollback Integrity
- **State of the Art:** If the invariant checker shares registers or memory with the operational NTT, a single radiation strike can blind the verifier (common-mode failure).
- **Key Finding:** Strategy 1 (TFIB-Ref) establishes independent reference constants, but its integration with bounded retry rollback ($K \le 2$) and cryptographic fail-stop suppression in space networks has never been evaluated in an end-to-end communication stack.

### Area L: Cross-Layer Security in Intermittently Connected Networks
- **State of the Art:** Network security (L5 DTN) and cryptographic arithmetic (L4 execution) are traditionally treated as completely independent abstraction layers.
- **The Core Disconnect:** If an SEU corrupts decapsulation at L4, the L5 DTN transport assumes network packet loss or invalid signatures and either drops the bundle or issues a multi-hour retransmission request over space links. Conversely, if L4 aborts silently, L6 persistence cannot determine whether to retry or escalate.

### Area M: Persistent Delivery, Replay Prevention, and Crash Recovery
- **State of the Art:** Persistent anti-replay ledgers use SQLite or embedded key-value stores with Write-Ahead Logging (WAL).
- **Key Finding:** If an endpoint crashes between command decryption and state commit, uncommitted anti-replay records can enable replay attacks upon reboot, or conversely cause permanent command drop.

### Area N: Formal Verification of Security State Machines
- **State of the Art:** TLA+, Alloy, and ProVerif are used to verify cryptographic protocols (TLS 1.3, Signal) and distributed consensus (Raft, Paxos).
- **Key Finding:** No formal model currently bridges physical cryptographic fault recovery transitions with DTN store-and-forward state machines.

### Area O: PQC Performance under Space Flight Constraints
- **State of the Art:** Satellite flight computers (e.g., ARM Cortex-M55, LEON4, RISC-V RV64GC) have severe power and memory constraints (often $<100\ \text{MB}$ RAM for payload).
- **Key Finding:** ML-KEM-768 and ML-DSA-65 are lightweight enough for software execution ($<40\ \mu\text{s}$ decapsulation), but full DMR duplicate execution ($+100\%$ overhead) is unacceptable for high-throughput space downlinks.

---

## 3. Summary of Literature Findings

Existing prior art falls into three isolated silos:
1. **Space Link PQC (ESA E2EQSS, CCSDS SDLS):** Focuses on Layer 2 line-of-sight point-to-point links; ignores store-and-forward DTN and endpoint arithmetic faults.
2. **Space DTN Transport (NASA ION, RFC 9171/9172):** Implements store-carry-forward; ignores PQC integration, asynchronous key lifecycles, and cryptographic execution faults.
3. **PQC Fault Attacks & Hardware Arithmetic Hardening (Ravi et al., REMO):** Hardens standalone FPGA/ASIC butterfly units; ignores software flight computers and end-to-end communication protocols.

**The intersection—software-level fault resilience and SDC suppression coupled to disruption-tolerant store-and-forward space networks—is completely unaddressed in the literature.**
