# Phase 5: Space System Implications

**Phase:** 5 — Cross-Implementation Fault-Surface Validation  
**Date:** October 1, 2026  
**Status:** COMPLETED  

---

## 1. Flight Software and Hardware Context

Spaceborne cryptographic subsystems (e.g., LEO, MEO, GEO satellites, deep-space probes) operate under ionizing radiation fields that induce Single Event Effects (SEEs):
- **Single Event Upsets (SEUs):** Transient bit flips in SRAM cells, CPU registers, or cache tags.
- **Single Event Transients (SETs):** Voltage spikes in combinational logic propagating into pipeline registers.
- **Single Event Functional Interrupts (SEFIs):** Control register upsets triggering processor hangs or reset cycles.

Radiation-tolerant processors used in spacecraft (e.g., BAE RAD750, Cobham GR740 / LEON4, Vorago VA416x0, ARM Cortex-R52/M7 rad-hard variants) operate at modest clock frequencies (50–400 MHz) with strict power envelopes (3–15 W).

---

## 2. Cross-Implementation Findings Applied to Space Missions

### 2.1 Vectorized Assembly vs. Scalar C in Space
- **Energy & Time Exposure Window:**
  - Highly optimized assembly routines (such as liboqs AArch64 or NEON implementations) complete ML-KEM encapsulation ~3–5x faster than unoptimized C code.
  - Faster execution reduces the **integrated flux window** $\int \Phi(t) dt$ during which a radiation particle can strike an active cryptographic state.
  - *Recommendation:* Flight software should utilize vectorized or tightly scheduled assembly to minimize exposure time windows.

### 2.2 Register Exposure vs. Cache Exposure
- **Cache Parity / ECC Protection:**
  - Modern space flight computers (e.g., LEON4, Cortex-R52) feature SECDED (Single Error Correction, Double Error Detection) ECC on L1 instruction and data caches.
  - However, CPU general-purpose and floating-point/vector register files frequently lack parity protection or only have parity detection without correction.
  - Phase 5 showed that `-O3` and vector assembly migrate polynomial state entirely into register files (`q0`-`q31`). An SEU striking an uncorrected vector register during NTT directly corrupts the polynomial without triggering CPU ECC faults.

### 2.3 Protocol Desynchronization Risks in Space Uplinks
- **Silent Key Mismatch:**
  - An SEU in ML-KEM decapsulation triggers implicit rejection: the satellite derives a pseudorandom key $K_{\text{rand}}$, while the ground station possesses the true shared key $K_{\text{true}}$.
  - The communication link silently desynchronizes. All subsequent telecommands (TC) encrypted with $K$ fail authentication.
  - Without explicit link-level recovery, the satellite risks entering a communication lockout until command timeout resets the crypto subsystem.
