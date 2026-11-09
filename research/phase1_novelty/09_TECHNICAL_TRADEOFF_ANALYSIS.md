# Phase 1 — Document 09: Technical Trade-Off and Engineering Cost Analysis

**Document ID:** `ASTRA-SEC-PH1-DOC-09`  
**Research Directorate:** Multidisciplinary Academic Evaluation Team  
**Date:** November 2026  
**Auditor Mandate:** Honest Assessment of Limitations, Penalties, and Engineering Costs  

---

## 1. Introduction: The Conservation of Complexity

No cryptographic or distributed systems protocol provides universal advantages without trade-offs. Enhancing fault resilience, post-quantum security, and disruption tolerance inherently imposes computational, storage, latency, and protocol complexity costs.

This analysis evaluates the 10 fundamental engineering trade-offs governing ASTRA-Sec, identifying precisely where the system is **less optimal** than existing alternatives.

---

## 2. In-Depth Trade-Off Analysis

### 2.1 Fault Detection Coverage vs Computational Overhead
- **The Trade-Off:** Achieving 100% fault detection requires full hardware TMR (300% hardware cost) or DMR (100% time penalty). ASTRA-Sec achieves $99.4\%$ single-bit detection coverage with only $+2.29\%$ latency overhead ($36.25\ \mu\text{s}$ vs $35.44\ \mu\text{s}$).
- **The Penalty:** The remaining $0.6\%$ of single-bit flips occur on unreferenced or masked representation bits. While these do not alter the mathematical polynomial in $\mathbb{Z}_{3329}$, sub-word invariant checking cannot guarantee $100.000\%$ detection of multi-byte adversarial laser attacks designed to flip multiple coefficients simultaneously. For worst-case targeted multi-bit laser fault attacks, full DMR remains mathematically superior.

### 2.2 Localized Rollback ($K \le 2$) vs Immediate Fail-Stop
- **The Trade-Off:** When a fault is detected, ASTRA-Sec attempts localized stack snapshot rollback up to 2 times ($K \le 2$) before triggering fail-stop implicit rejection.
- **The Penalty:** Rollback consumes CPU cycles. Under high radiation flux where persistent stuck bits exist, spending 2 retry iterations wastes energy and introduces variable latency jitter (P99 latency increases from $96.14\ \mu\text{s}$ to $280\ \mu\text{s}$) before ultimately escalating to fail-stop. An immediate fail-stop strategy is strictly constant-time, whereas rollback introduces bounded execution variance.

### 2.3 Persistent WAL Storage vs End-to-End Latency
- **The Trade-Off:** Writing every bundle and anti-replay sequence to disk using SQLite Write-Ahead Logging (WAL) guarantees crash consistency and survivability across sudden satellite power-cycles.
- **The Penalty:** Flash/disk I/O is four orders of magnitude slower than CPU memory operations:
  - In-memory inter-node handoff: $\approx 18\ \mu\text{s}$.
  - SQLite WAL disk synchronization (`fsync`): $\approx 5,600\ \mu\text{s}$ ($5.6\ \text{ms}$) per hop.
  - Across a 4-node network, disk persistence increases pipeline latency from **$1.50\ \text{ms}$ to $22.78\ \text{ms}$** (+1,418% latency penalty). For real-time satellite formation flying requiring sub-millisecond control loops, persistent WAL storage is completely unfeasible.

### 2.4 ML-DSA-65 Digital Signatures vs Telemetry Throughput
- **The Trade-Off:** Traditional satellite telecommand uses symmetric AES-CMAC (16-byte MAC) or ECDSA (64-byte signature). ASTRA-Sec deploys post-quantum ML-DSA-65 signatures (3,309 bytes) to guarantee quantum-safe non-repudiation and delivery authentication.
- **The Penalty:**
  - Signature size overhead: A 64-byte command payload wrapped in an ML-DSA-65 signed envelope balloons to over $3,500\ \text{bytes}$—a **$54\times$ bandwidth inflation**.
  - On low-bandwidth UHF/VHF satellite downlinks (e.g., 9,600 bps), transmitting a 3,500-byte envelope requires $\approx 2.9\ \text{seconds}$ of continuous transmission time, depleting satellite battery reserves.
  - Signature verification takes $\approx 63\ \mu\text{s}$ on modern desktop CPUs, but on an embedded 100 MHz space microprocessor (e.g., LEON3/GR712RC), ML-DSA-65 verification consumes $\approx 45\ \text{ms}$ of dedicated CPU time.

### 2.5 Sliding-Window Replay Protection vs Spacecraft Memory Footprint
- **The Trade-Off:** A 64-bit sliding window maintains bitmap history to admit valid reordered bundles arriving across multipath orbital links while rejecting duplicates.
- **The Penalty:** Under high-volume burst traffic or out-of-order deliveries spanning large time deltas, the sliding window must either expand (consuming scarce radiation-hardened SRAM) or drop valid packets whose sequence lag exceeds the window width ($W > 64$).

### 2.6 Post-Quantum Key Rotation vs Deep-Space Disconnection
- **The Trade-Off:** Double Ratchet key evolution provides forward secrecy and break-in recovery by ratcheting the KDF chain on every command cycle.
- **The Penalty:** If a ground station advances the ratchet while an in-flight bundle is delayed in orbital transit across a multi-day occultation, the delayed bundle becomes un-decryptable unless the spacecraft buffers skipped key states. Buffering skipped ratchet keys degrades forward secrecy and risks memory exhaustion on memory-constrained satellites.

### 2.7 End-to-End Payload Opacity vs Intermediate Relay Observability
- **The Trade-Off:** Layer 2 Envelope Encryption ensures intermediate satellite relays cannot read or tamper with payloads.
- **The Penalty:** Relays cannot perform Deep Packet Inspection (DPI), payload-based content caching, or emergency command validation. If a rogue ground station injects an invalid payload, intermediate satellites waste scarce store-and-forward buffer space transporting garbage traffic that will ultimately be rejected at the destination.

### 2.8 Security Strictness vs Mission Availability
- **The Trade-Off:** ASTRA-Sec enforces strict fail-stop implicit rejection upon unrecoverable faults or invalid signatures.
- **The Penalty:** In critical aerospace emergencies (e.g., a satellite tumbling out of control toward atmospheric re-entry), an operator may need to send an emergency "safe-hold" command under degraded link conditions. ASTRA-Sec's strict fail-stop behavior will unconditionally drop a partially corrupted command, potentially sacrificing the satellite to preserve cryptographic integrity.

---

## 3. Comparative Summary: Where ASTRA-Sec is Worse Than Baselines

| Dimension | Baseline / Alternative System | ASTRA-Sec Approach | The Engineering Trade-Off (Where ASTRA-Sec is Worse) |
| :--- | :--- | :--- | :--- |
| **Bandwidth Overhead** | CCSDS SDLS (AES-CMAC, 16 B tag) | ML-DSA-65 Signature (3,309 B) | **$200\times$ more bandwidth consumed** per command packet. |
| **Pipeline Latency** | Volatile RAM DTN (No WAL disk I/O) | Persistent SQLite WAL per hop | **$15\times$ slower** ($22.78\ \text{ms}$ vs $1.50\ \text{ms}$) due to physical disk sync. |
| **Multi-Bit Laser Attack** | Hardware Dual Modular Redundancy (DMR) | Sub-word Cooley-Tukey Invariant | DMR catches $100\%$ of arbitrary multi-bit faults; sub-word catches $99.4\%$. |
| **Execution Determinism** | Static Fail-Stop (Zero retry) | Localized Rollback ($K \le 2$) | Rollback introduces latency jitter ($96\ \mu\text{s}$ to $280\ \mu\text{s}$) under active faults. |
| **Memory Footprint** | Classical ECC (Ed25519, 64 B keys) | ML-KEM-768 (1,184 B pk, 2,400 B sk) | Requires **$30\times$ more key storage memory** on flight computers. |

---

## 4. Conclusion

ASTRA-Sec is deliberately engineered for **mission-critical telecommand and telemetry security across untrusted, radiation-exposed commercial satellite networks**, where data authenticity and quantum resistance outweigh strict bandwidth minimization. It is not suitable for ultra-low-bandwidth CubeSat beaconing or hard real-time sub-millisecond control loops.

