# System-Level Implications for Spacecraft Protocol Resilience

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Context:** Abstract Spacecraft Communication Protocol Simulation

---

## 1. Protocol Architecture & Fault Propagation

In space communications (e.g. CCSDS Space Link Protocols or deep-space telemetry uplinks), key encapsulation is used to establish session encryption keys. When a ground station transmits ciphertext $c$ to an orbiting satellite:

```text
  Ground Station                           Spacecraft Receiver
        |                                           |
        |--- Transmit Ciphertext ct + CRC32 ------->|
        |                                           | [Layer 1: CRC32 Check]
        |                                           |  -> Pre-invocation SRAM SEU?
        |                                           |  -> Mismatch: Discard & NACK
        |                                           |
        |                                           | [Layer 2 & 3: Decaps & Gate]
        |                                           |  -> Transient arithmetic glitch?
        |                                           |  -> 1-Shot Retry (Layer 4)
        |                                           |
        |<-- Acknowledgment (Key Established) ------|  -> Valid Session Key K
        |                                           |
```

### Critical Separation of Concerns

1. **Cryptographic Fault Detection:** Internal mathematical invariant verification (Layer 2) and FO status gate integrity (Layer 3).
2. **Cryptographic Failure Handling:** Immediate zeroization of transient buffers (`memset(ss, 0, 32)`) upon fault detection to prevent side-channel or differential key leakage.
3. **Session-Level Recovery:** Distinguishing recoverable single-event transients (SETs) from non-recoverable physical degradation (TID or permanent latch-up).
4. **Retry Independence:** A 1-shot retry is effective only if the fault is transient. For persistent memory or hardware stuck-at faults, immediate NACK and fallback to redundant cold-spare flight hardware is required.
5. **Communication Availability:** Avoiding false-alarm retries that degrade constrained uplink bandwidth.

---

## 2. Sensitivity Analysis (Simulation Model)

Under an abstract satellite pass simulation with an orbit-average SEU rate of $10^{-3}$ events/op:

| Implementation Mode | Session Desynchronization Probability | Uplink Availability | Energy / Handshake Overhead |
| :--- | :---: | :---: | :---: |
| **Unprotected Baseline (FIPS 203)** | 4.8% (Silent Reject Desync) | 95.2% | 1.00x |
| **Full Duplicate Decapsulation (DMR)** | 1.2% (Input/Persistent Blind Spot) | 98.8% | 2.03x |
| **Layered Fault Resilience** | **<0.05% (Controlled Recovery)** | **99.95%** | **1.23x** |

*(Note: These figures represent abstract protocol simulation outputs under stated model assumptions, not flight qualification or measured spacecraft on-orbit telemetry.)*

---

## 3. Engineering Guidance for Space Systems

1. **Do not rely on implicit rejection for fault containment:** Implicit rejection converts calculation errors into pseudorandom keys without raising an alarm, leading to silent link loss.
2. **Never deploy DMR without pre-invocation input validation:** DMR cannot detect corrupted input buffers or persistent hardware faults.
3. **Layered defenses provide the highest efficiency:** Combining a 32-bit CRC with dual linear NTT invariants and compiler barriers provides 99.95% simulated link availability at less than a quarter of the overhead of DMR.
