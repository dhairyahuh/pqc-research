# FAULT RESILIENCE ANALYSIS OF POST-QUANTUM CRYPTOGRAPHIC IMPLEMENTATIONS FOR SPACE SYSTEMS
## Project Overview & Research Architecture

**Primary Research Title:**  
**FAULT RESILIENCE ANALYSIS OF POST-QUANTUM CRYPTOGRAPHIC IMPLEMENTATIONS FOR SPACE SYSTEMS**

**Current Implementation Focus:**  
*Software-Level Fault Resilience for ML-KEM-768 Decapsulation*

---

## 1. Authoritative Research Narrative

> "The research, titled 'Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems', investigates the reliability and fault resilience of post-quantum cryptographic implementations in space-system environments.
> 
> As part of the initial implementation and experimental evaluation, the project has focused on ML-KEM-768, a standardized post-quantum key-encapsulation mechanism under NIST FIPS 203.
> 
> This implementation-level study investigates NTT arithmetic fault detection through dual-transform algebraic invariant monitoring, localized rollback and retry, and fail-stop containment using the Fujisaki–Okamoto implicit rejection mechanism.
> 
> The experimental results obtained so far provide an initial technical foundation for the broader research. However, the overall research objective extends beyond this implementation and includes additional cryptographic implementations, embedded processor evaluation, representative space-relevant fault models, hardware/software co-design, physical fault testing, and eventual spacecraft-level integration and validation."

---

## 2. The Three-Level Research Structure

```text
+---------------------------------------------------------------------------------------------------------+
| LEVEL A — OVERALL RESEARCH PROGRAMME (PERMANENT TITLE)                                                  |
| "Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems"             |
| The complete research agenda: evaluating and improving PQC reliability under space radiation, SEUs,    |
| hardware resource constraints, and orbital operational environments.                                    |
+---------------------------------------------------------------------------------------------------------+
                                                     │
                                                     ▼
+---------------------------------------------------------------------------------------------------------+
| LEVEL B — WORK COMPLETED SO FAR (INITIAL IMPLEMENTATION CASE STUDY)                                     |
| "Software-Level Fault Resilience for ML-KEM-768"                                                        |
| • Standardized primitive: NIST FIPS 203 ML-KEM-768 (Kyber)                                              |
| • Micro-level invariant monitoring across all 9,856 NTT butterflies (5,376 CT + 4,480 GS)                |
| • Localized single-butterfly register rollback (~0.0101% operation-count retry ratio, 100/100 recovered)|
| • Deterministic fail-stop containment via FIPS 203 Section 7.3 implicit rejection (200/200 safe stops) |
| • Cleanroom & canonical validation: 0 SDC across 300 production trials & 750 campaign trials            |
| • Apple Silicon ARM64 benchmark: +16.9% decapsulation latency overhead under -O3; 0 dynamic heap bytes  |
| • Disclosed limitation: Theorem 1 twiddle-factor blindness of local monitors                           |
+---------------------------------------------------------------------------------------------------------+
                                                     │
                                                     ▼
+---------------------------------------------------------------------------------------------------------+
| LEVEL C — REMAINING RESEARCH & FUTURE WORK (SEVEN BROAD WORK PACKAGES)                                  |
| • WP1: Broader Cryptographic Evaluation (ML-DSA, SLH-DSA, stateful hash signatures, cross-algorithm)     |
| • WP2: Embedded & Space-Oriented Computing (ARM Cortex-M4, RISC-V RV32IM, memory/stack/cycles)          |
| • WP3: Space-Relevant Fault Modelling (SEUs, SETs, multi-bit bursts, memory, control flow)              |
| • WP4: Hardware/Software Fault Resilience (hardware ECC, memory protection, twiddle CRC32 binding)     |
| • WP5: Physical Validation (laboratory EMFI, voltage/clock glitching, cyclotron beam irradiation)       |
| • WP6: Space-System Integration (spacecraft OBC, NASA cFS, RTEMS, CCSDS SDLS, FDIR safe-mode)          |
| • WP7: System-Level Validation (hardware-in-the-loop testbed, mission availability & link reliability) |
+---------------------------------------------------------------------------------------------------------+
```

For the comprehensive visual progression and architectural breakdown, refer to [`docs/architecture/RESEARCH_EVOLUTION.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/architecture/RESEARCH_EVOLUTION.md).

---

## 3. Project Background & Space-Systems Motivation

Post-quantum cryptography (PQC) standards—formalized by NIST in August 2024 as FIPS 203 (ML-KEM) and FIPS 204 (ML-DSA)—are slated for widespread deployment across defense, telecommunications, and aerospace infrastructure. Future spaceborne platforms (CubeSats, satellite mega-constellations in Low Earth Orbit, and interplanetary probes) must transition to PQC to secure uplinks, crosslinks, and downlinks against adversarial interception and future quantum cryptanalysis.

However, satellites and aerospace controllers operate in harsh environments exposed to single-event upsets (SEUs)—bit-flips induced by ionizing radiation, power rail transients, and thermal stress. In post-quantum lattice cryptography, polynomial algebra over finite rings relies heavily on the Number Theoretic Transform (NTT) for quasi-linear multiplication.

---

## 4. Current Implementation and Experimental Progress: ML-KEM-768

In ML-KEM-768, key decapsulation executes **9,856 butterfly operations** across 11 polynomial transforms (6 Forward Cooley-Tukey and 5 Inverse Gentleman-Sande). When an arithmetic bit-flip occurs:
- **Silent Data Corruption (SDC):** The decapsulation routine emits an undetected corrupted key, potentially exposing communication channels to cryptanalytic breakdown.
- **Availability Loss:** Unmitigated faults trigger unnecessary aborts or link renegotiation storms. Sequential Dual Modular Redundancy (DMR) doubles runtime (+99.33% overhead at the isolated NTT level), exceeding tight spacecraft power and thermal budgets.
- **Circular Verifier Blindness:** Naive software checkers that read back live output registers fail due to common-mode blindness, exhibiting a **98.5% false-pass rate** (591/600 trials across 6 H1-relevant targets).

### Implemented Architecture: Dual Invariants + Local Rollback
Our architecture establishes a lightweight, pure-software defense directly integrated into standard C99 production binaries:
1. **Micro-Level Dual-Transform Monitoring:** Intercepts all 9,856 NTT butterflies, evaluating forward CT ($\Delta_{\text{sum}}, \Delta_{\text{diff}}$) and inverse GS ($\Delta_{\text{add}}, \Delta_{\text{mul}}$) algebraic invariants without runtime modular division.
2. **Localized Register Rollback:** Restores operands from software-managed snapshot variables, recovering transient faults on retry 1 with only a single-butterfly recomputation (~0.0101% operation-count ratio, distinct from wall-clock overhead).
3. **Deterministic Fail-Stop Containment:** Escalates persistent faults to FIPS 203 Section 7.3 implicit rejection ($K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$), suppressing authentic key selection.
4. **Key Empirical Results:**
   - 100/100 transient recoveries (Wilson CI: $[96.3\%, 100\%]$).
   - 200/200 persistent fail-stops (Wilson CI: $[98.1\%, 100\%]$).
   - **0 SDC observed across 300 active production trials** (Wilson CI: $[0.00\%, 1.26\%]$) and **0 SDC across 750 active campaign trials** (Clopper-Pearson bound: $0.49\%$).
   - Latency overhead: **+16.9%** for full decapsulation under `-O3` on Apple Silicon ARM64.
   - Dynamic heap memory: **0 bytes** in monitoring and rollback code paths.

---

## 5. Remaining Research & Future Work: Seven Work Packages

To evolve the initial software foundation into the complete space-system research program, remaining work is organized into seven work packages:

1. **Work Package 1 — Broader Cryptographic Evaluation:** Evaluate additional PQC implementations (ML-DSA under FIPS 204, SLH-DSA under FIPS 205); compare algorithmic structures and fault vulnerabilities across key-encapsulation and digital-signature implementations.
2. **Work Package 2 — Embedded and Space-Oriented Computing:** Port implementations to ARM Cortex-M4/M7, ARM Cortex-R, and RISC-V RV32IM platforms; evaluate memory, execution time, energy, and cycle constraints.
3. **Work Package 3 — Space-Relevant Fault Modelling:** Study SEUs, SETs, and multiple-bit faults across registers, memory, arithmetic operations, and control flow; correlate software-injected faults with physical behavior.
4. **Work Package 4 — Hardware/Software Fault Resilience:** Explore hardware ECC, memory protection, watchdogs, and redundancy; develop independent integrity checks (CRC32/checksums) for twiddle factors to resolve Theorem 1 blindness.
5. **Work Package 5 — Physical Validation:** Conduct controlled laboratory fault injection (EMFI, voltage glitching) and radiation testing at cyclotron facilities; compare experimental observations with software models.
6. **Work Package 6 — Space-System Integration:** Integrate into spacecraft onboard computing architectures (NASA cFS, RTEMS, FreeRTOS), CCSDS SDLS space communications protocols, and spacecraft FDIR safe-mode systems.
7. **Work Package 7 — System-Level Validation:** Construct representative spacecraft communication and cryptographic testbeds; measure end-to-end reliability, availability, MTTR, and resource consumption.

---

## 6. Primary Documentation & Presentation Materials

- **Manuscript:** [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md)
- **Roadmap:** [`research-roadmap.md`](file:///Users/dhairyajain/Desktop/pqc%20research/research-roadmap.md)
- **Evolution Map:** [`docs/architecture/RESEARCH_EVOLUTION.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/architecture/RESEARCH_EVOLUTION.md)
- **Presentation Materials:** [`docs/presentation/`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/)
  - `AI_PPT_FINAL_CONTENT.md`: 11-slide academic progress deck ready for AI presentation generators
  - `AI_PPT_FACT_CHECK.md`: Fact-check register with empirical sources and confidence bounds
  - `AI_PPT_CHANGELOG.md`: Full audit log of applied corrections
