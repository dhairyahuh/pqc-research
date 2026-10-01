# Systematic Literature Review & Technical Audit
**Project:** Adaptive, Resilient, Post-Quantum Space Communication Framework  
**Phase:** Phase 2 — Brutally Honest Literature and Novelty Audit  
**Date:** October 2026  
**Status:** Peer-Reviewed Systematic Audit  

---

## 1. Executive Framing & Review Methodology

This literature audit investigates the technical state of the art intersecting twelve distinct sub-disciplines:
1. Resilient satellite and deep-space communications (CCSDS standards, telemetry/telecommand TT&C).
2. Space communication channel models (Markov burst error channels, fading, erasures, orbital occultation).
3. Delay/Disruption-Tolerant Networking (DTN / BPv7 RFC 9171 / LTP RFC 5326).
4. Forward Error Correction (FEC), interleaving, and Hybrid Automatic Repeat reQuest (HARQ).
5. Adaptive and cross-layer communication control (AMC, adaptive coding rate, dynamic interleaving).
6. Post-Quantum Cryptography (PQC) for non-terrestrial networks (NTN) and space systems.
7. Secure communication under packet loss and intermittent connectivity (BPSec RFC 9172, AEAD).
8. Fault-tolerant computing and Software-Implemented Fault Injection (SWIFI).
9. Radiation-inspired software fault models (SEU, SET) and their boundaries.
10. Joint communication channel and endpoint computational fault handling.
11. Security-preserving recovery and authenticated data delivery.
12. Formal methods and constrained optimization for resilient communication control.

Every source is analyzed according to four strict evidentiary criteria:
- **Demonstrated Fact:** What the paper concretely implements, evaluates, and proves with data.
- **Author Claim:** What the authors assert or extrapolate in their text.
- **Technical Interpretation:** How the work maps to our space communication problem.
- **Source Limitation:** Missing data, inaccessible full texts, or unsupported assumptions.

---

## 2. In-Depth Analysis of the Five Target Papers

### 2.1 Paper 1: Channel-Adaptive PQC for Non-Terrestrial Networks
* **Citation:** Mustafa El Bizri, Ahmad M. El-Hajj, Layth Sliman, and Ali Massoud Haidar, *"Channel-Adaptive Post-Quantum Cryptography for Secure and Efficient Non-Terrestrial Networks"*, IEEE International Conference on Communications (IEEE ICC 2026), Glasgow, Scotland, May 2026. DOI: `10.1109/ICC59461.2026.11587307`.
* **Problem Addressed:** Post-quantum public-key cryptography introduces significant data overhead (e.g., ML-KEM-768 public keys are 1,184 bytes and ciphertexts are 1,088 bytes, compared to 32–64 bytes for classical ECC). In resource-constrained non-terrestrial networks (NTNs) with fluctuating signal-to-noise ratio (SNR) and high packet error rates, static PQC key exchanges exacerbate link congestion and packet drops.
* **Architecture & System Model:** Satellite-to-ground and aerial wireless communication links operating under time-varying fading channels.
* **Cryptographic Primitives:** NIST PQC KEM candidates (CRYSTALS-Kyber/ML-KEM, Saber, Classic McEliece) and signature candidates (CRYSTALS-Dilithium/ML-DSA).
* **Adaptation Mechanism:** Dynamic channel-adaptive selection: the transmitter switches cryptographic schemes or adjusts rekeying frequency based on instantaneous channel SNR/BER estimates. Under poor channel conditions, the system defers rekeying or switches to lower-bandwidth configurations to minimize frame fragmentation.
* **What the Paper Demonstrates:** Simulation of wireless NTN links shows that adapting PQC negotiation frequency and algorithm parameters reduces transmission delay and prevents queue buffer overflows during channel degradation.
* **Stated & Unstated Limitations:**
  1. *Zero Endpoint Fault Modeling:* The authors assume that onboard satellite microprocessors compute all cryptographic operations with 100% perfection. They model zero Single-Event Upsets (SEUs), zero ALU glitches, and zero memory corruptions.
  2. *Cryptographic Security Invariance:* Adapting algorithm parameters across heterogeneous families (e.g., switching between lattice and code-based schemes) introduces operational complexity and dynamic attack surfaces.
  3. *Isolated Layering:* The adaptation acts strictly on link-level transmission parameters without feedback from the internal health of the cryptographic hardware.
* **Overlap with Proposed System:** High conceptual overlap on *channel-adaptive communication*, but **zero overlap** on *endpoint computational fault resilience*.

---

### 2.2 Paper 2: PQC for Space Systems Systematic Survey
* **Citation:** Hyunmin Kim, *"Post-quantum cryptography for space systems: Algorithms, implementation, and design constraints—A systematic survey"*, *Acta Astronautica*, Vol. 241, April 2026, pp. 278–294. DOI: `10.1016/j.actaastro.2026.04.041`.
* **Problem Addressed:** Comprehensive systematization of post-quantum cryptographic readiness for orbital spacecraft, CubeSats, and deep-space missions facing quantum computing threats.
* **Architecture & Constraints:** Reviews space system constraints across three tiers:
  - *Computational & Energy Constraints:* Strict power limits (0.5W–5W for CubeSat onboard computers) and low clock speeds (50MHz–400MHz on radiation-tolerant processors such as UT699 LEON3-FT or RAD750).
  - *Memory Footprint:* Constrained radiation-hardened SRAM/MRAM (typically 2MB–16MB), creating severe bottlenecks for schemes requiring large keys (e.g., Classic McEliece).
  - *Radiation Susceptibility:* High Linear Energy Transfer (LET) heavy ions and protons inducing Single-Event Upsets (SEU), Single-Event Latchup (SEL), and Total Ionizing Dose (TID) degradation.
* **What the Paper Demonstrates:** Compiles benchmark data from terrestrial microcontrollers (e.g., ARM Cortex-M4 via `pqm4`) and maps them against space avionics processors. Concludes that ML-KEM and ML-DSA offer the best balance of speed and key size for space use, but warns that lattice-based arithmetic (especially polynomial NTT) is exceptionally fragile to transient radiation bit-flips.
* **Stated & Unstated Limitations:**
  - Purely a literature review and survey. The paper does not design, implement, or evaluate a communication protocol, fault-injection engine, or recovery controller.
* **Overlap with Proposed System:** Provides foundational justification and operational constraints for our space framework; no overlap in concrete artifacts or empirical contributions.

---

### 2.3 Paper 3: DTN for Integrated Deep-Space Relay Networks
* **Citation:** Dalia I. Elewaily, Hesham Arafat Ali, Ahmed Ibrahim Saleh, and Mohamed M. Abdelsalam, *"Delay/Disruption-Tolerant Networking-based the Integrated Deep-Space Relay Network: State-of-the-Art"*, *Ad Hoc Networks*, Vol. 152, Jan 2024, Article 103307. DOI: `10.1016/j.adhoc.2023.103307`.
* **Problem Addressed:** Deep-space communications suffer from extreme one-way light time (OWLT) propagation delays (e.g., 3 to 22 minutes for Mars), frequent line-of-sight occultations, and high bit error rates. Traditional TCP/IP fails completely under these conditions.
* **Architecture & Protocols:** Reviews the Delay/Disruption-Tolerant Networking (DTN) architecture, specifically the Bundle Protocol (BPv7, RFC 9171 / CCSDS 734.2-B-1) operating over convergence layers like the Licklider Transmission Protocol (LTP, RFC 5326 / CCSDS 734.1-B-1).
* **Adaptation & Reliability:**
  - *Custody Transfer:* Relay nodes accept custody of bundles and store them in non-volatile memory until guaranteed transfer to the next hop.
  - *Contact Graph Routing (CGR):* Deterministic routing using pre-computed ephemeris contact plans.
  - *Selective Retransmission:* LTP uses checkpointing (CP) and report segments (RS) with selective negative acknowledgments (SNACK) to retransmit only missing segments without conversational round-trip handshakes.
* **Security Findings:** Reviews Bundle Protocol Security (BPSec, RFC 9172). Identifies that cryptographic operations (digital signatures and symmetric AEAD) add massive serialization delays and storage consumption at intermediate relay nodes.
* **Stated & Unstated Limitations:**
  - Classical cryptography only; does not evaluate post-quantum key exchange or lattice signatures.
  - Does not investigate endpoint radiation faults in the processors executing the DTN stack.
* **Overlap with Proposed System:** Informs the design of our *Resilient Communication Layer* (packetization, sequence control, selective recovery without conversational handshakes).

---

### 2.4 Paper 4: Performance Analysis of FSO in SAGIN
* **Citation:** Ayalneh Bitew Wondmagegn, Dongwook Won, Quang Tuan Do, Demeke Shumeye Lakew, and Sungrae Cho, *"Performance analysis of FSO-based communications in space-air-ground integrated networks: A comprehensive survey"*, *Computer Networks*, Vol. 271, Oct 2025, Article 111579. DOI: `10.1016/j.comnet.2025.111579`.
* **Problem Addressed:** Free-Space Optical (FSO) satellite communications offer ultra-high data rates (>10 Gbps) and immunity to RF spectrum congestion, but are severely degraded by atmospheric turbulence, cloud blockage, fog attenuation, and satellite pointing errors.
* **Channel Models:** Rigorous mathematical formulations of:
  - *Atmospheric Turbulence:* Log-Normal distributions (weak turbulence) and Gamma-Gamma distributions (moderate-to-strong turbulence).
  - *Pointing Errors:* Rayleigh and Hoyt distributions modeling satellite micro-vibrations and tracking jitter.
  - *Weather Outages:* Multi-state Markov models representing clear sky, haze, and complete cloud obstruction.
* **Mitigation & Adaptation:**
  - *Adaptive Coding & Modulation (ACM):* Dynamic adjustment of optical code rates.
  - *Hybrid FSO/RF Switching:* Diverting high-priority telemetry to a low-rate, weather-resilient RF link when optical links undergo weather outages.
* **Stated & Unstated Limitations:**
  - Focuses on optical physics and physical/link-layer analysis. Does not address post-quantum cryptographic security, session key management, or onboard processor fault resilience.
* **Overlap with Proposed System:** Establishes the mathematical state-transition structure (Markov models of outages and burst losses) implemented in our *Simulated Channel Layer*.

---

### 2.5 Paper 5: Secure Communications for Satellite Internet
* **Citation:** Yu Zhang, Shuangrui Zhao, He Ji, Yuan-Yu Zhang, Yulong Shen, and Xiao-Hong Jiang, *"A Survey of Secure Communications for Satellite Internet Based on Cryptography and Physical Layer Security"*, *IET Information Security*, Oct 2023. DOI: `10.1049/2023/5604802`.
* **Problem Addressed:** Satellite internet constellations face severe security challenges due to open wireless broadcast channels, dynamic topologies, and physical exposure of spacecraft to adversaries.
* **Technological Domains:**
  - *Upper-Layer Cryptography:* Group key management, lightweight mutual authentication, identity-based encryption, and handover authentication protocols.
  - *Physical Layer Security (PLS):* Exploiting wireless channel fading, beamforming, artificial noise injection, and cooperative jamming to achieve positive secrecy capacity against eavesdroppers.
* **What the Paper Demonstrates:** Combining upper-layer cryptographic protocols with physical-layer key extraction provides layered security. However, cryptographic re-authentication during rapid inter-satellite handovers often exceeds latency budgets.
* **Stated & Unstated Limitations:**
  - Evaluates classical symmetric and elliptic-curve cryptography; does not address NIST PQC standards or quantum threats.
  - Assumes fault-free hardware execution.
* **Overlap with Proposed System:** Validates the necessity of multi-layer security framing, but does not address PQC fault resilience or joint channel-computation adaptation.

---

## 3. Review of Supporting Technical Domains

### 3.1 Space Communication Channel Models
In space-to-ground and crosslink communications, channel errors are rarely independent and identically distributed (i.i.d.):
1. **Gilbert-Elliott Two-State Markov Model (Gilbert 1960; Elliott 1963):**
   - The channel alternates between a "Good" state ($G$) and a "Bad" state ($B$).
   - State transition probabilities $P_{GB}$ and $P_{BG}$ model memory and temporal correlation (burstiness).
   - In state $G$, the bit error probability is $e_G \ll 10^{-6}$; in state $B$, the bit error probability is $e_B \approx 0.1$ to $0.5$.
2. **Packet Erasure & Outage Models:**
   - In satellite links subject to antenna slewing, orbital occultation, or atmospheric fades, packets are completely dropped in bursts rather than corrupted bit-by-bit. An outage state transition matrix represents link availability.

### 3.2 Error Control Coding & Hybrid ARQ (HARQ)
1. **Forward Error Correction (FEC):**
   - *Reed-Solomon (RS) Codes:* CCSDS 131.0-B-4 standardizes $RS(255, 223)$, capable of correcting up to $t = 16$ symbol errors per block.
   - *Convolutional & LDPC Codes:* High coding gain near Shannon capacity, but sensitive to burst errors without interleaving.
2. **Interleaving:**
   - Block and convolutional interleaving spreads contiguous channel burst errors across multiple code words, converting bursty errors into isolated random errors that FEC decoders can easily correct.
3. **Hybrid ARQ Schemes (Lin & Costello 2004):**
   - *Type-I HARQ:* Each transmitted packet contains payload and parity bits for error detection and correction. If the FEC decoder detects uncorrectable errors, the receiver requests retransmission.
   - *Type-II HARQ (Incremental Redundancy):* Initial transmission sends information bits with minimal parity; subsequent retransmissions send incremental parity blocks, accumulated in the receiver buffer (Chase combining or code combining).

### 3.3 Post-Quantum Cryptographic Protocols in Space
1. **Key Encapsulation (ML-KEM / FIPS 203):**
   - Establishes a 256-bit symmetric shared secret ($K$).
   - ML-KEM-768 requires transmitting a 1,088-byte ciphertext. If packet loss fragments this ciphertext, decapsulation fails completely.
2. **Authenticated Encryption with Associated Data (AEAD):**
   - ChaCha20-Poly1305 (RFC 8439) or AES-GCM (NIST SP 800-38D) provides confidentiality, ciphertext integrity, and authenticated associated data (AAD) for message headers.
   - Replay protection requires monotonically increasing 64-bit sequence numbers.

### 3.4 Software Fault Injection (SWIFI) vs. Radiation Physics
- **Radiation Physics (Dodd & Massengill, IEEE TNS 2003):** Heavy ions crossing silicon deplete charge, causing instantaneous Single-Event Transients (SET) in combinational logic and Single-Event Upsets (SEU) in flip-flops.
- **SWIFI Boundary (Hsueh et al., IEEE Computer 1997):** Software-implemented fault injection modifies architectural CPU registers or memory words at instruction boundaries. It cannot emulate analog charge sharing, clock jitter, or latchup. Therefore, software frameworks model **algorithmic and architectural resilience**, not physical semiconductor qualification.

---

## 4. Critical Synthesis: The Core Research Disconnect

A systematic cross-analysis of the surveyed literature reveals a stark, pervasive gap:

| Literature Domain | Focus on Channel State | Focus on Endpoint Hardware Health | Joint Adaptive Coordination |
| :--- | :---: | :---: | :---: |
| **Space Communications & DTN** (Elewaily, CCSDS) | **High** (Models delay, loss, burst fading) | **Zero** (Assumes crypto processor never faults) | **None** |
| **Channel-Adaptive PQC** (El Bizri et al.) | **High** (Adapts PQC parameters to SNR) | **Zero** (Assumes fault-free computation) | **None** |
| **PQC Fault Attacks & ABFT** (Ravi, Hermelink, Paul) | **Zero** (Direct pin injection, isolated functions) | **High** (Evaluates arithmetic SEUs in NTT) | **None** |
| **Physical Layer Security** (Zhang et al.) | **High** (Exploits fading for secrecy) | **Zero** (Ignores internal processor upsets) | **None** |

**The Unaddressed Reality:** In an operational spacecraft, channel degradation and cosmic radiation occur **simultaneously**:
1. When an antenna enters a fading channel, packet loss increases, requiring FEC and retransmissions.
2. Simultaneously, space radiation induces Single-Event Upsets in the onboard processor executing ML-KEM decapsulation.
3. If the cryptographic engine experiences an internal arithmetic fault, existing systems either:
   - Abort silently or output an implicit rejection key ($K_{\text{rej}}$), causing legitimate retransmitted packets to fail AEAD authentication, misleading the communication layer into assuming the wireless link is completely broken; OR
   - Blindly retransmit unverified ciphertexts, wasting scarce satellite transmitter energy and bandwidth.

**Conclusion:** No published work unifies **communication-layer adaptation (FEC/ARQ)** with **endpoint cryptographic fault resilience (in-place NTT rollback and safe implicit rejection)** under a joint, security-constrained optimization policy.
