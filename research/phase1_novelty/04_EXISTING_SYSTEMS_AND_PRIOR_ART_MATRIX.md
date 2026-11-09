# Phase 1 — Document 04: Competitive Prior-Art Comparison Matrix

**Document ID:** `ASTRA-SEC-PH1-DOC-04`  
**Research Directorate:** Multidisciplinary Academic Evaluation Team  
**Date:** November 2026  
**Status Values:** `YES` (explicitly demonstrated), `PARTIAL` (limited/partial support), `NO` (verified absent from primary literature), `UNKNOWN` (insufficient evidence), `NOT APPLICABLE` (outside system scope).

---

## 1. 25-Dimension Architectural Comparison Matrix

| # | Comparison Dimension | ESA E2EQSS (2021–24) | ESA ACES / QKD (2022) | CCSDS SDLS (2022) | NASA ION-DTN / BPSec (2020–22) | Ravi et al. DMR (2020) | Paul et al. DSP (2023) | Bausch et al. DTN (2023) | **ASTRA-Sec Proposed** |
| :- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **System / Primary Source** | ESA/ESTEC Contract | ESA Scientific Initiative | CCSDS 355.0-B-1 | NASA JPL / RFC 9172 | IEEE TCAD | IEEE ESL | IEEE Access | This Research |
| **2** | **Publication Year** | 2021–2024 | 2022 | 2022 | 2020–2022 | 2020 | 2023 | 2023 | 2026 |
| **3** | **PQC Algorithms** | `YES` (Kyber/McEliece) | `NO` (Physical QKD) | `NO` (Classical AES) | `NO` (Classical Pre-Shared) | `YES` (Kyber/Saber) | `YES` (Kyber/Dilithium)| `NO` (Ed25519) | `YES` (ML-KEM-768) |
| **4** | **End-to-End Encryption** | `PARTIAL` (Link/GW) | `YES` (Optical Ground) | `NO` (Link Layer) | `PARTIAL` (BPSec Source) | `NOT APPLICABLE` | `NOT APPLICABLE` | `YES` (Application) | `YES` (AES-256-GCM L2) |
| **5** | **Digital Signatures** | `YES` (Dilithium/RSA) | `NO` (Symmetric OTP) | `NO` (MAC only) | `PARTIAL` (BPSec BIB) | `NOT APPLICABLE` | `NOT APPLICABLE` | `YES` (Ed25519) | `YES` (ML-DSA-65) |
| **6** | **Satellite Network Arch** | `YES` (GEO / Ground GW)| `YES` (LEO-Ground Line)| `YES` (Space Link) | `YES` (Multi-Hop Space)| `NOT APPLICABLE` | `NOT APPLICABLE` | `YES` (LEO Constell) | `YES` (4-Node Space) |
| **7** | **DTN Support** | `NO` (Synchronous IP) | `NO` (Direct Optical) | `NO` (Packet Framing) | `YES` (BPv7 RFC 9171) | `NOT APPLICABLE` | `NOT APPLICABLE` | `YES` (BPv7 RFC 9171)| `YES` (BPv7 RFC 9171) |
| **8** | **Persistent Store-Forward**| `NO` | `NO` | `NO` | `YES` (SDR Memory) | `NOT APPLICABLE` | `NOT APPLICABLE` | `YES` (Filesystem) | `YES` (SQLite WAL) |
| **9** | **Crypto Fault Detection** | `NO` (Assumes Rad-Hard) | `NO` | `NO` | `NO` | `YES` (Dual Execution) | `YES` (DSP Invariant)| `NO` | `YES` (NTT $r \equiv t\zeta$) |
| **10**| **Crypto Fault Recovery** | `NO` | `NO` | `NO` | `NO` | `NO` (Re-compute drop) | `NO` (Flag only) | `NO` | `YES` (Rollback $K \le 2$)|
| **11**| **Independent Checker** | `NO` | `NO` | `NO` | `NO` | `NO` (Self-comparison) | `PARTIAL` (DSP logic)| `NO` | `YES` (TFIB-Ref ROM) |
| **12**| **Checker Corruption Guard**| `NO` | `NO` | `NO` | `NO` | `NO` | `NO` | `NO` | `YES` (Invariant check)|
| **13**| **Replay Protection** | `YES` (Sequence counter)| `NO` | `YES` (Anti-replay window)| `PARTIAL` (Timestamp) | `NOT APPLICABLE` | `NOT APPLICABLE` | `YES` (Cache) | `YES` (64-bit Window) |
| **14**| **Duplicate Command Suppress**| `YES` | `NO` | `YES` | `PARTIAL` (Hop drop) | `NOT APPLICABLE` | `NOT APPLICABLE` | `YES` | `YES` (Hash & State) |
| **15**| **Persistent Anti-Replay** | `PARTIAL` (EEPROM counter)| `NO` | `PARTIAL` (Static NVRAM)| `NO` (Volatile ZCO) | `NOT APPLICABLE` | `NOT APPLICABLE` | `NO` (In-memory) | `YES` (ACID WAL DB) |
| **16**| **Key Rotation in Outage** | `NO` (Requires online) | `NO` | `NO` (Manual telecmd)| `NO` (Manual BPSec) | `NOT APPLICABLE` | `NOT APPLICABLE` | `NO` | `YES` (Double Ratchet)|
| **17**| **Authorization Expiry** | `YES` (Cert validity) | `NO` | `NO` | `PARTIAL` (Bundle TTL)| `NOT APPLICABLE` | `NOT APPLICABLE` | `YES` (TTL) | `YES` (Policy & TTL) |
| **18**| **Crash Recovery** | `PARTIAL` (Node reboot)| `NO` | `PARTIAL` (Warm boot) | `PARTIAL` (SDR reload) | `NOT APPLICABLE` | `NOT APPLICABLE` | `NO` | `YES` (WAL Consistent)|
| **19**| **Command Acceptance Semantics**| `PARTIAL` (At-least-once)| `NOT APPLICABLE` | `PARTIAL` (At-least-once)| `NO` (Best-effort DTN)| `NOT APPLICABLE` | `NOT APPLICABLE` | `PARTIAL` | `YES` (At-Most-Once) |
| **20**| **Authenticated ACK** | `YES` (Return frame) | `NO` | `YES` (CLCW report) | `PARTIAL` (Admin record)| `NOT APPLICABLE` | `NOT APPLICABLE` | `YES` (Ed25519) | `YES` (ML-DSA-65) |
| **21**| **Cross-Layer Fault Handl.**| `NO` | `NO` | `NO` | `NO` | `NO` | `NO` | `NO` | **`YES` (Proposed)** |
| **22**| **Formal Verification** | `PARTIAL` (ProVerif IPsec)| `NO` | `NO` | `NO` | `NO` | `NO` | `NO` | `PARTIAL` (State rules)|
| **23**| **Experimental Validation** | `YES` (Alphasat testbed)| `YES` (Optical Ground) | `YES` (ESA/NASA missions)| `YES` (ISS / CubeSats)| `YES` (Simulated laser)| `YES` (FPGA Vivado) | `YES` (Emulated LEO) | `YES` (38-Trial Test) |
| **24**| **Performance Evaluation** | `YES` (Throughput/loss)| `YES` (Key rate) | `YES` (Frame rate) | `YES` (Goodput/storage)| `YES` (+100% latency) | `YES` (+1% FPGA LUTs)| `YES` (Delay/jitter) | `YES` (+2.29% latency)|
| **25**| **Primary Limitation** | Link-level; no DTN; no arithmetic fault checks. | Requires optical LOS; extreme hardware cost. | Static symmetric keys; no multi-hop privacy. | Classical security; uncoordinated crypto drops. | High latency penalty (+100%); no recovery. | Hardware FPGA only; no C CPU implementation. | Classical crypto; no hardware SEU protection. | Software emulation of physical orbital nodes. |

---

## 2. In-Depth Comparative Findings

### Finding 1: The Gap Between Space PQC and Fault Resilience
Space-focused PQC prototypes (e.g., ESA E2EQSS, Bausch et al.) assume that the underlying space processor operates without arithmetic corruption. Conversely, cryptographic fault-injection researchers (e.g., Ravi et al., Primas et al., Paul et al.) evaluate fault attacks strictly on isolated boards or FPGAs without considering the networking dynamics of multi-hop satellite constellations.

### Finding 2: The Latency Chasm (DMR vs Sub-Word Monitoring)
Existing software-level fault tolerance defaults to Dual Modular Redundancy (DMR), duplicating the entire decapsulation routine and imposing a $+101.49\%$ latency penalty. ASTRA-Sec's sub-word butterfly monitoring in C99 achieves comparable fault containment with only $+2.29\%$ overhead.

### Finding 3: The Cross-Layer Disconnect (Dimension 21)
As revealed by Column 21 ("Cross-Layer Fault Handling"), **not a single existing system coordinates low-level cryptographic arithmetic fault recovery with high-level DTN custody and delivery state transitions**. 
- In NASA ION-DTN, an arithmetic decapsulation failure appears as an unexplained payload drop or corrupt bundle, triggering blind retransmissions or complete loss of telecommands.
- In ESA E2EQSS, a failure crashes the synchronous session.
- ASTRA-Sec stands uniquely positioned to define and validate this cross-layer coordination mechanism.
