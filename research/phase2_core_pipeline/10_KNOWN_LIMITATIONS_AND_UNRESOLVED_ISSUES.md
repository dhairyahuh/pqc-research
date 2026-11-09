# Phase 2 — Document 10: Known Limitations, Unresolved Issues, and Boundaries

**Document ID:** `ASTRA-SEC-PH2-DOC-10`  
**Evaluation Role:** Principal Systems Architect & Independent Research Auditor  
**Date:** November 2026  
**Auditor Principle:** Complete Scientific Candor (No Disguised Deficiencies)  

---

## 1. Executive Summary

This document explicitly identifies all architectural limitations, unsupported protocol features, emulated components, and physical test boundaries in ASTRA-Sec. 

These items are documented transparently to ensure that academic publications and experimental demonstrations do not overstate the system's operational maturity.

---

## 2. Exhaustive Limitations Register

### 2.1 Limitation 1: Native NASA/JPL ION-DTN Daemon Execution
- **Current Status:** `SIMULATED / BRIDGED VIA RFC 9171 PYTHON ENGINE`
- **Technical Description:** While `astra_sec/dtn/ion_config.py` generates 100% syntactically valid NASA ION configuration files (`.ionrc`, `.bprc`, `.ltprc`, `.ionsec`), the native NASA JPL `ionadmin` and `bpadmin` C daemons are not compiled or executing as system processes on macOS.
- **Root Cause:** NASA ION depends on Linux System V IPC shared-memory structures (`sysv_ipc`) that are deprecated or restricted on Darwin/macOS.
- **Operational Reality:** All live bundles in the automated test suite and dashboard stream through ASTRA-Sec's internal Python RFC 9171 CBOR engine (`astra_sec/dtn/bpv7.py`).

### 2.2 Limitation 2: Software Fault Injection vs Physical Particle Irradiation
- **Current Status:** `SOFTWARE IN-MEMORY BIT-FLIP INJECTION ONLY`
- **Technical Description:** Fault injection is conducted via C function hooks (`astra_inject_ntt_fault`) that mutate CPU registers and stack arrays during execution loops.
- **Boundary:** The system has **not** been tested in a physical cyclotron particle accelerator beam facility (e.g., heavy-ion or high-energy proton beam tests). All Single-Event Upset (SEU) claims reflect software-modeled single-bit flips in accordance with aerospace microprocessor simulation standards.

### 2.3 Limitation 3: Multi-Bit Adversarial Laser Attacks
- **Current Status:** `SUB-WORD INVARIANT BOUNDED TO SINGLE-BIT / UNCORRELATED FAULTS`
- **Technical Description:** The Cooley-Tukey butterfly monitor ($r \equiv t\zeta \pmod q$) achieves $99.4\%$ detection coverage for random single-bit SEUs.
- **Vulnerability:** In an active physical laboratory attack where a sophisticated adversary uses focused infrared laser pulses to simultaneously flip multiple correlated bits in both the accumulator and the twiddle factor, the sub-word invariant can theoretically be bypassed. For worst-case targeted multi-bit laser injection, full hardware Double Modular Redundancy (DMR) remains mathematically superior.

### 2.4 Limitation 4: Bundle Protocol Fragmentation and Reassembly
- **Current Status:** `UNFRAGMENTED BUNDLES ONLY`
- **Technical Description:** RFC 9171 Section 6 specifies bundle fragmentation for payloads that exceed the Maximum Transmission Unit (MTU) of a contact link.
- **Operational Reality:** ASTRA-Sec currently assumes that all telecommands and telemetry payloads fit within a single unfragmented bundle (wire size $\approx 4.6\ \text{KB}$). Bundles exceeding link MTU cannot currently be fragmented across multiple smaller contact frames.

### 2.5 Limitation 5: Bandwidth Inflation of Post-Quantum Signatures
- **Current Status:** `ARCHITECTURAL TRADE-OFF (3,309 B PER ENVELOPE)`
- **Technical Description:** ML-DSA-65 digital signatures require 3,309 bytes. Wrapping a 64-byte telecommand payload into a signed envelope yields a total bundle size of 4,684 bytes—a **$73\times$ bandwidth penalty** compared to classical ECDSA (64 B).
- **Impact:** Unsuitable for extremely narrow satellite downlinks (e.g., amateur VHF/UHF CubeSat links operating at 1,200 or 9,600 baud).

### 2.6 Limitation 6: Persistent Disk I/O vs Hard Real-Time Latency
- **Current Status:** `ARCHITECTURAL TRADE-OFF (22.78 ms DISK LATENCY)`
- **Technical Description:** SQLite Write-Ahead Logging enforces synchronous physical disk barriers (`fsync`) to survive sudden node power-cycles.
- **Impact:** While in-memory forwarding takes only $1.50\ \text{ms}$, physical disk persistence increases pipeline latency to $\approx 22.78\ \text{ms}$. ASTRA-Sec cannot be used for hard real-time satellite formation flying control loops requiring sub-millisecond reactions.

---

## 3. Summary of Operational Claims Status

| Proposed System Claim | Current Operational Reality | Permitted Academic Claim |
| :--- | :--- | :--- |
| **"PQC on Satellites"** | Emulated 4-node local pipeline | "Emulated multi-hop store-and-forward space network" |
| **"NASA ION Integration"** | Config synthesis + CBOR wire compatibility | "RFC 9171 wire-compatible with NASA ION config synthesis" |
| **"Cosmic Radiation Resilience"** | C memory register bit-flip injection | "Software-level fault resilience against simulated SEUs" |
| **"Zero SDC"** | Formally verified in 3,000 trials via implicit rejection | "Zero SDC observed across 3,000 software fault trials" |
| **"At-Most-Once Execution"** | Enforced via SQLite WAL anti-replay sequence | "At-most-once telecommand execution across process reboots" |
