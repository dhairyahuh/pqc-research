# ASTRA-Sec: Known Limitations, Assumptions & Research Boundaries

This document provides a complete, transparent disclosure of the physical, algorithmic, and operational boundaries of the ASTRA-Sec project.

---

## 1. Space Hardware & Physical RF Boundaries

1. **Software Simulation vs Physical Spacecraft**:
   - The 4-node constellation (GSA, SAT-1, SAT-2, GSB) executes as separate asynchronous software processes communicating via TCP/HTTP and SQLite spools.
   - The system is not deployed on orbiting spacecraft hardware or radiation-hardened microcontrollers (e.g., RAD750, GR740, Vorago VA416x0).
2. **RF Channel Modeling**:
   - Link outages, propagation delays, and contact windows are driven by state machines and SGP4 orbital geometry.
   - Atmospheric scintillation, Doppler frequency shifts, rain fade, and free-space path loss (FSPL) are not physically simulated in RF baseband.

---

## 2. Radiation & Fault Injection Boundaries

1. **Software Bit-Flips vs Ionizing Particle Strikes**:
   - Single-Event Upsets (SEUs) are injected via controlled C memory hooks in software register buffers.
   - While the mathematical transformation of the state vector ($r' = r \oplus 2^b$) is identical to an SEU, this does not model Total Ionizing Dose (TID), Single-Event Latchup (SEL), or Single-Event Functional Interrupts (SEFI).
2. **Fault Coverage Scope**:
   - The mathematical invariant $r \equiv t \cdot \zeta \pmod{3329}$ monitors the Cooley-Tukey NTT polynomial multiplication steps.
   - It does not monitor the SHA-3 / SHAKE Keccak sponge permutations or the AES-256 hardware acceleration blocks directly.

---

## 3. Cryptographic Implementation Boundaries

1. **Post-Quantum Forward Secrecy**:
   - ML-KEM-768 provides lattice-based IND-CCA2 security against quantum key recovery attacks.
   - Bulk application payloads are protected by symmetric AES-256-GCM. Quantum security for symmetric ciphers relies on Grover's algorithm requiring $2^{128}$ operations for 256-bit keys, which provides ample margin.
2. **LibOQS vs Clean-Room Native Source**:
   - ASTRA-Sec includes self-contained clean-room C99 source files (`mlkem-native` and `mldsa-native`).
   - If external `liboqs` is not installed on the host system, the framework automatically uses its native C99 compiled engines with zero functional degradation.

---

## 4. Delay-Tolerant Networking (DTN) Scope

1. **Lightweight BPv7 Engine**:
   - ASTRA-Sec implements RFC 9171 primary blocks, RFC 9172 BPSec BIB blocks, and CBOR payload encodings.
   - It is a focused aerospace research implementation, not a drop-in replacement for the full NASA/JPL Interplanetary Overlay Network (ION-DTN) daemon with full Contact Graph Routing (CGR).
2. **Custody Transfer**:
   - Custody transfer is achieved through persistent SQLite WAL tables and signed acknowledgment bundles.

---

## 5. Astrodynamics & Orbital Visualization

1. **Public TLE Ephemerides vs Spacecraft Housekeeping**:
   - Satellite positions are propagated using real public Two-Line Element (TLE) sets from CelesTrak using SGP4.
   - SAT-1 and SAT-2 use calibrated synthetic TLE ephemerides representing realistic Polar SSO and Inclined LEO orbits; they do not represent operational commercial space assets.
2. **Air-Gapped Operation**:
   - The system is designed to operate 100% offline using `data/orbital/cached_tle.json`. Live network fetching from CelesTrak is an optional convenience feature with an automatic 2.0s fallback to local cache.
