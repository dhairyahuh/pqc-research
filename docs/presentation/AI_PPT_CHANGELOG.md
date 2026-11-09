# AI PPT FINAL CONTENT — CHANGELOG
## Authoritative Research Identity & Scope Alignment Audit
**Date:** November 3, 2026  
**Scope:** Permanent research programme title restoration, three-level architectural hierarchy implementation, 11-slide presentation alignment, and seven space-system work packages definition.

---

## 1. Critical Research Identity Correction

### A. Primary Research Title Restoration (Permanent & Non-Negotiable)
- **Authoritative Title:** **FAULT RESILIENCE ANALYSIS OF POST-QUANTUM CRYPTOGRAPHIC IMPLEMENTATIONS FOR SPACE SYSTEMS**
- **Correction Applied:** Removed "Software-Level Fault Resilience for ML-KEM-768" as the primary program title. The ML-KEM-768 study is an initial implementation-level case study within the broader space-systems research agenda, not the research programme title itself.
- **Scope Applied:** `README.md`, `PROJECT_OVERVIEW.md`, `paper/manuscript.md`, `research-roadmap.md`, `docs/architecture/RESEARCH_EVOLUTION.md`, `AI_PPT_FINAL_CONTENT.md`, and `PROGRESS_PRESENTATION_OUTLINE.md`.

### B. The Three-Level Research Structure
All documents now formally distinguish:
1. **LEVEL A — OVERALL RESEARCH PROGRAMME:**
   - Permanent Title: *Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems*
   - Scope: Investigating post-quantum cryptographic reliability, fault tolerance, localized recovery, and containment in spaceborne computing environments.
2. **LEVEL B — WORK COMPLETED SO FAR (Initial Implementation Case Study):**
   - Title: *Software-Level Fault Resilience for ML-KEM-768: Dual-Transform NTT Invariant Monitoring, Localized Register Rollback, and Containment*
   - Scope: Evaluating NTT butterfly monitoring (9,856 operations), localized rollback (~0.0101% operation ratio, 100/100 transient recovery), fail-stop implicit rejection containment (200/200 safe stops), 0 SDC across 300 production and 750 campaign trials, and +16.9% decapsulation overhead on production C99 binaries.
3. **LEVEL C — REMAINING RESEARCH & FUTURE WORK (Seven Broad Work Packages):**
   - Scope: Advancing beyond the initial software case study toward complete space-system flight qualification across seven defined work packages.

### C. Standardized Authoritative Research Narrative
The following narrative is established as the central positioning text across all primary documentation:
> *"The research, titled 'Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems', investigates the reliability and fault resilience of post-quantum cryptographic implementations in space-system environments.
> 
> As part of the initial implementation and experimental evaluation, the project has focused on ML-KEM-768, a standardized post-quantum key-encapsulation mechanism under NIST FIPS 203.
> 
> This implementation-level study investigates NTT arithmetic fault detection through dual-transform algebraic invariant monitoring, localized rollback and retry, and fail-stop containment using the Fujisaki–Okamoto implicit rejection mechanism.
> 
> The experimental results obtained so far provide an initial technical foundation for the broader research. However, the overall research objective extends beyond this implementation and includes additional cryptographic implementations, embedded processor evaluation, representative space-relevant fault models, hardware/software co-design, physical fault testing, and eventual spacecraft-level integration and validation."*

---

## 2. Eleven-Slide Academic Presentation Structure

The presentation content in `AI_PPT_FINAL_CONTENT.md` and outline in `PROGRESS_PRESENTATION_OUTLINE.md` have been updated to **exactly 11 slides** matching the required academic storyline:

| Slide # | Slide Heading | Purpose & Research Focus |
|:---:|---|---|
| **01** | **Title Slide — Research Overview** | Overall research title, presenter, department, date, and 4 KPI cards summarizing initial case study results. |
| **02** | **Introduction — PQC & Space Systems** | PQC standardization (FIPS 203/204/205), orbital radiation hazard, SEEs (SEUs/SETs), and COTS processor vulnerability. |
| **03** | **Research Background & Problem Statement** | SDC vs Unavailability dilemma, hardware ECC variability on COTS, and circular verifier blindness (98.5%). |
| **04** | **Research Objectives & Scope** | Three-level architecture (Level A Programme $\to$ Level B Case Study $\to$ Level C 7 Work Packages) and 5 core objectives. |
| **05** | **Proposed Research Framework** | Multi-tier pipeline ($\mathcal{O} \to \mathcal{S} \to \mathcal{F} \to \Delta \to \mathcal{P} \to \mathcal{D} \to \mathcal{C}$), four-layer defense stack, and space evaluation metrics. |
| **06** | **Work Completed So Far: ML-KEM-768** | Selection rationale for ML-KEM-768, scope of C99 production integration, 18/18 NIST KATs, and case study positioning. |
| **07** | **Implemented Fault-Resilience Architecture** | CT sum/diff invariants (5,376 ops), GS decoupled invariants (4,480 ops), software-managed snapshot variables, and retry limit. |
| **08** | **Experimental Results & Validation** | Distinct Comparison A (decapsulation +16.9%) and Comparison B (isolated NTT DMR +99.33%), N=400 cleanroom, N=900 campaign, 0 SDC. |
| **09** | **Current Limitations & Research Gaps** | Five declared boundaries: desktop ARM64 only, software bit-flips, Theorem 1 twiddle blindness, timing side-channels, and statistical bounds. |
| **10** | **Future Work & Research Expansion** | Seven Broad Space-System Work Packages (WP1: Broader PQC $\to$ WP7: System-Level Validation). |
| **11** | **Conclusion & Research Roadmap** | Summary of verified achievements, long-term spaceflight horizon, and final research takeaway. |

---

## 3. Seven Broad Space-System Work Packages

Future research is organized across seven comprehensive work packages:
- **WP1 — Broader Cryptographic Evaluation:** ML-DSA (FIPS 204), SLH-DSA (FIPS 205), stateful hash-based signatures, and cross-algorithm vulnerability analysis.
- **WP2 — Embedded and Space-Oriented Computing:** Porting to ARM Cortex-M4/M7, ARM Cortex-R, and aerospace RISC-V RV32IM (NOEL-V) cores; memory and cycle profiling.
- **WP3 — Space-Relevant Fault Modelling:** Modeling SEUs, SETs, and multi-bit radiation bursts across arithmetic, memory, control flow, and constant tables.
- **WP4 — Hardware/Software Fault Resilience:** Collaborative defenses pairing software invariants with hardware ECC, MPUs, watchdogs, and dedicated twiddle factor ROM CRC32 integrity checks.
- **WP5 — Physical Validation:** Controlled laboratory EMFI and voltage/clock glitching; particle accelerator cyclotron beam testing (protons/heavy ions at TRIUMF/LBNL).
- **WP6 — Space-System Integration:** Flight software integration (NASA cFS, RTEMS, FreeRTOS), CCSDS Space Data Link Security (SDLS) standards, and spacecraft FDIR safe-mode interaction.
- **WP7 — System-Level Validation:** Hardware-in-the-loop (HIL) spacecraft communications testbeds measuring link availability, MTTR, and mission reliability.

---

## 4. Preserved Experimental Ground Truths
- All numerical metrics preserved exactly: 9,856 butterflies (5,376 CT + 4,480 GS), 100/100 transient recoveries (Wilson CI: $[96.3\%, 100\%]$), 200/200 safe fail-stops (Wilson CI: $[98.1\%, 100\%]$), 0 SDC across 300 production trials (Wilson CI: $[0.00\%, 1.26\%]$) and 750 campaign trials (Clopper-Pearson bound: $0.49\%$), 591/600 circular verifier false passes, 18/18 NIST KAT vectors pass, +16.9% decapsulation overhead, and 0 dynamic heap allocations.
- Zero source code files, test harnesses, or raw experimental datasets were altered.

---

*End of Changelog — Authoritative Research Identity Confirmed*
