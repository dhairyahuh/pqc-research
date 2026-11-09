# Master Research Presentation Handbook
## Complete Repository Guide, Slide-by-Slide Speaking Script, Technical Defense Notes & Last-Minute Preparation Manual

**Permanent Research Title:**  
# FAULT RESILIENCE ANALYSIS OF POST-QUANTUM CRYPTOGRAPHIC IMPLEMENTATIONS FOR SPACE SYSTEMS

**Initial Implementation Case Study:**  
*Software-Level Fault Resilience for ML-KEM-768: Dual-Transform NTT Invariant Monitoring, Localized Register Rollback, and Containment*

**Author / Presenter:** Dhairya Jain  
**Repository:** `https://github.com/dhairyajain/pqc-research`  
**Primary Standards:** NIST FIPS 203 (ML-KEM), NIST FIPS 204 (ML-DSA)  
**Date:** November 2026

---

## Quick Navigation Table of Contents

- [PART 1 — UNDERSTAND THE RESEARCH](#part-1--understand-the-research)
  - [1.1 Executive Summary & Core Identity](#11-executive-summary--core-identity)
  - [1.2 The Three-Level Research Structure](#12-the-three-level-research-structure)
  - [1.3 The Central Research Narrative](#13-the-central-research-narrative)
- [PART 2 — COMPLETE REPOSITORY NAVIGATION GUIDE](#part-2--complete-repository-navigation-guide)
  - [2.1 Repository Architecture & Evolution](#21-repository-architecture--evolution)
  - [2.2 Major Directory Tree & Purpose Map](#22-major-directory-tree--purpose-map)
  - [2.3 Comprehensive Data & Dataset Index](#23-comprehensive-data--dataset-index)
  - [2.4 Complete Experiment Index (Phases 1–18 & TFIB)](#24-complete-experiment-index-phases-118--tfib)
  - [2.5 Source Code Implementation Index](#25-source-code-implementation-index)
  - [2.6 Authoritative Results & Claim-Evidence Mapping](#26-authoritative-results--claim-evidence-mapping)
  - [2.7 Research Documentation & Audit Index](#27-research-documentation--audit-index)
  - [2.8 Verified How-To-Run Command Reference](#28-verified-how-to-run-command-reference)
- [PART 3 — COMPLETE 10-SLIDE SPEAKING SCRIPT](#part-3--complete-10-slide-speaking-script)
  - [Slide 1: Title Slide — Research Overview](#slide-1-title-slide--research-overview)
  - [Slide 2: Fault Vulnerabilities in Post-Quantum Cryptographic Implementations](#slide-2-fault-vulnerabilities-in-post-quantum-cryptographic-implementations)
  - [Slide 3: Research Objectives and Scope Definition](#slide-3-research-objectives-and-scope-definition)
  - [Slide 4: Proposed Framework for Fault Detection and Recovery](#slide-4-proposed-framework-for-fault-detection-and-recovery)
  - [Slide 5: ML-KEM-768: Implementation and Experimental Setup](#slide-5-ml-kem-768-implementation-and-experimental-setup)
  - [Slide 6: Mathematical Invariants and Fault-Containment Architecture](#slide-6-mathematical-invariants-and-fault-containment-architecture)
  - [Slide 7: Performance Analysis and Experimental Validation](#slide-7-performance-analysis-and-experimental-validation)
  - [Slide 8: Research Limitations and Identified Gaps](#slide-8-research-limitations-and-identified-gaps)
  - [Slide 9: Proposed Extensions and Future Research](#slide-9-proposed-extensions-and-future-research)
  - [Slide 10: Conclusions and Research Trajectory](#slide-10-conclusions-and-research-trajectory)
- [PART 4 — TECHNICAL CONCEPTS DEEP-DIVE](#part-4--technical-concepts-deep-dive)
  - [4.1 ML-KEM-768 and Number Theoretic Transform (NTT)](#41-ml-kem-768-and-number-theoretic-transform-ntt)
  - [4.2 Mathematical Invariants & Verification Algebra](#42-mathematical-invariants--verification-algebra)
  - [4.3 Fault Models & Physical Radiation Mapping](#43-fault-models--physical-radiation-mapping)
  - [4.4 Localized Recovery & Multi-Stage Containment Architecture](#44-localized-recovery--multi-stage-containment-architecture)
  - [4.5 Performance Disambiguation & Statistical Rigor](#45-performance-disambiguation--statistical-rigor)
- [PART 5 — FACULTY Q&A PREPARATION & DEFENSE CHALLENGES](#part-5--faculty-qa-preparation--defense-challenges)
  - [5.1 Core Defense Questions & Defensible Answers (Q1–Q25)](#51-core-defense-questions--defensible-answers-q1q25)
  - [5.2 If Faculty Challenge My Results (Hostile/Skeptical Challenges)](#52-if-faculty-challenge-my-results-hostileskeptical-challenges)
- [PART 6 — LAST-MINUTE PRESENTATION CHEAT SHEET](#part-6--last-minute-presentation-cheat-sheet)
  - [6.1 One-Minute Memorizable Introduction](#61-one-minute-memorizable-introduction)
  - [6.2 Five-Minute Complete Presentation Summary](#62-five-minute-complete-presentation-summary)
  - [6.3 Essential Metrics Reference Table](#63-essential-metrics-reference-table)
  - [6.4 Technical Glossary](#64-technical-glossary)
  - [6.5 Top 10 Files & Top 5 Directories to Open](#65-top-10-files--top-5-directories-to-open)
  - [6.6 What I Must NEVER Claim (Safety Boundaries)](#66-what-i-must-never-claim-safety-boundaries)

---

# PART 1 — UNDERSTAND THE RESEARCH

### 1.1 Executive Summary & Core Identity

The permanent and official title of this research programme is:
$$\textbf{Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems}$$

This research addresses the intersection of two critical technological imperatives:
1. **The Quantum Transition in Space:** Orbital infrastructure—such as Earth observation satellites, global positioning constellations, telecommunication relays, and interplanetary probes—operates with operational mission lifetimes exceeding 10 to 25 years. Because adversaries on ground can intercept and store encrypted satellite downlinks today to decrypt them when cryptanalytically relevant quantum computers emerge (*Harvest-Now, Decrypt-Later* attack model), space systems must immediately transition to Post-Quantum Cryptography (PQC), standardized by NIST in August 2024 under FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), and FIPS 205 (SLH-DSA).
2. **The Space Radiation Hazard:** Unlike terrestrial data centers protected by Earth's magnetosphere and thick atmosphere, spacecraft operate in severe ionizing radiation environments. Electronics are continually exposed to galactic cosmic rays, solar energetic proton events, and trapped van Allen radiation belts. High-energy heavy ions and protons striking microprocessor silicon induce **Single-Event Effects (SEEs)**:
   - *Single-Event Upsets (SEUs):* Radiation-induced bit-flips in registers, instruction caches, and SRAM memory cells.
   - *Single-Event Transients (SETs):* Voltage spikes in combinational logic nets that latch into invalid arithmetic state.

When Single-Event Effects strike during the execution of post-quantum cryptographic primitives, the results are catastrophic:
- If a fault occurs in polynomial arithmetic during key decapsulation and goes undetected, it causes **Silent Data Corruption (SDC)**: the ground station and satellite compute diverging cryptographic session keys without any error indication, leading to immediate communication blackouts and unrecoverable link desynchronization.
- Alternatively, if a fault induces an unhandled processor trap or uncontrolled panic abort, the onboard computer (OBC) resets, causing severe mission degradation.

To prevent both link desynchronization and unnecessary spacecraft reboots, cryptographic algorithms operating in space must possess **software-level fault resilience**: the capability to locally detect computational errors, recover transient state in-place, and safely contain persistent faults.

---

### 1.2 The Three-Level Research Structure

To prevent any confusion between the broader research vision and the specific empirical benchmarks completed to date, the entire project is structured into three distinct levels:

```
+---------------------------------------------------------------------------------------------------+
| LEVEL A: OVERALL RESEARCH PROGRAMME (PERMANENT TITLE)                                              |
| "Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems"       |
| - Comprehensive investigation of PQC reliability under orbital radiation environments.            |
| - Scope spans ML-KEM, ML-DSA, SLH-DSA across CubeSats, LEO constellations, and deep space.       |
+---------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+---------------------------------------------------------------------------------------------------+
| LEVEL B: WORK COMPLETED SO FAR (INITIAL IMPLEMENTATION CASE STUDY)                                |
| "Software-Level Fault Resilience for ML-KEM-768: Dual-Transform NTT Invariant Monitoring,         |
|  Localized Register Rollback, and Containment"                                                    |
| - Target: NIST FIPS 203 ML-KEM-768 (Security Category 3).                                         |
| - 9,856 NTT butterfly operations monitored per full decapsulation (5,376 CT + 4,480 GS).           |
| - Algebraic invariants: Cooley-Tukey sum/diff checks + Gentleman-Sande decoupled rail checks.     |
| - Localized register rollback mechanism with retry counter ($R_{max}=2$).                         |
| - 400 cleanroom trials & 750 canonical campaign trials: 0 SDC observed ($95\%\text{ CI}\le0.49\%$). |
| - +16.9% latency overhead (full decapsulation) vs +99.33% for isolated sequential DMR.             |
| - Formal identification of Theorem 1 (twiddle blindness) & circular verifier false-pass (98.5%).   |
+---------------------------------------------------------------------------------------------------+
                                                  │
                                                  ▼
+---------------------------------------------------------------------------------------------------+
| LEVEL C: REMAINING RESEARCH & FUTURE WORK (SEVEN TARGETED WORK PACKAGES)                          |
| WP1: Broader Cryptographic Evaluation (ML-DSA-65, SLH-DSA-128, cross-algorithm comparison).       |
| WP2: Embedded & Space-Oriented Computing (ARM Cortex-M4/M7, RISC-V RV32IM rad-hard targets).       |
| WP3: Space-Relevant Fault Modelling (multi-bit upsets, burst errors, control-flow tracking).     |
| WP4: Hardware/Software Fault Resilience (hardware ECC, memory MPU integration, ROM CRC32).       |
| WP5: Physical Validation (laboratory electromagnetic fault injection, proton/heavy-ion beams).     |
| WP6: Space-System Software Integration (NASA Core Flight System cFS, RTEMS, CCSDS SDLS, FDIR).   |
| WP7: System-Level Validation (Hardware-in-the-Loop satellite testbed, end-to-end telemetry).      |
+---------------------------------------------------------------------------------------------------+
```

---

### 1.3 The Central Research Narrative

During the presentation, the research must be communicated through a clear 5-stage logical narrative:

1. **Why Space Systems Need Post-Quantum Cryptography:** Satellite assets launched today remain in orbit for 10–25 years. Eavesdroppers are currently harvesting satellite downlinks. Ground decryption using quantum computers will compromise long-lived mission data unless PQC is integrated immediately.
2. **Why Software-Level Resilience Is Required:** Commercial Off-The-Shelf (COTS) microprocessors are increasingly flown on modern CubeSats and mega-constellations to deliver required computational throughput at acceptable cost and mass. However, COTS hardware lacks radiation hardening and suffers radiation-induced Single-Event Effects (SEEs). Traditional hardware redundancy—such as Triple Modular Redundancy (TMR) across multiple flight computers—is mass- and power-prohibitive for small satellites. Pure software Dual Modular Redundancy (DMR) doubles the cryptographic runtime (+100% overhead). Lightweight software-level monitoring is essential.
3. **Why ML-KEM-768 Was Selected as the Initial Case Study:** ML-KEM (Kyber) is NIST's primary standardized Key Encapsulation Mechanism under FIPS 203. ML-KEM-768 provides NIST Security Category 3 (equivalent to AES-192), representing the optimal trade-off between post-quantum security margin, public key size (1,184 bytes), and computational latency for satellite command-and-control links.
4. **What Was Actually Implemented and Evaluated:** We designed, implemented, and audited a software-level fault resilience framework integrated directly into production NIST FIPS 203 C99 code (`mlkem-native`). It monitors all 9,856 polynomial butterfly operations across forward (Cooley-Tukey) and inverse (Gentleman-Sande) Number Theoretic Transforms (NTT) using dual algebraic invariants. It captures register-level operand snapshots before arithmetic execution; upon transient fault detection, it restores clean operands and retries execution locally ($R_{max}=2$). If faults persist, it triggers an algebraic fail-stop and delegates to the Fujisaki-Okamoto implicit rejection mechanism to produce a pseudorandom rejection key ($K_{rej}$), ensuring zero silent data corruption without crashing the processor.
5. **What Was Discovered, What Are the Gaps, and What Remains Future Work:** Our empirical campaign proved that the monitored decapsulation achieves 0 SDC across 750 active fault trials ($95\%\text{ CI}\le0.49\%$) at only +16.9% decapsulation overhead, outperforming software DMR (+99.33%). Crucially, our adversarial audits uncovered two fundamental scientific insights:
   - *Circular Verifier Vulnerability:* Naive fault checkers reading mutated registers directly fail to detect 98.5% of faults (591/600 false passes). Pre-computation register snapshotting is mandatory.
   - *Theorem 1 (Twiddle Scalar Blindness):* Invariant arithmetic over inputs and outputs cannot detect single-operand corruption within read-only twiddle factors ($\zeta$).
   Closing twiddle blindness via reference binding (`tfib_ref.c`), extending the invariant framework to digital signatures (ML-DSA), porting to spaceborne RISC-V/ARM flight architectures, and conducting physical cyclotron radiation testing constitute the clear, structured future work of this research programme.

---

# PART 2 — COMPLETE REPOSITORY NAVIGATION GUIDE

### 2.1 Repository Architecture & Evolution

The repository represents an intensive, 18-phase academic research evolution. Early phases (Phases 1–6) implemented initial fault injection scripts, discovered that naive runtime verifiers exhibited circular dependency flaws, and built reproducible test harnesses. Phases 7–14 resolved timing instrumentation discrepancies, separated isolated NTT benchmarks from full end-to-end decapsulation, and formalized statistical bounds. Phases 15–18 conducted adversarial audits, isolated twiddle factor vulnerabilities, constructed the cleanroom Phase 18 reproducer, and finalized the formal manuscript.

To provide clear, professional organization for faculty review, the repository is structured into distinct, logical directories:
- `algorithms/`: Production cryptographic code (`mlkem/`) and fault-resilience invariant monitoring hooks (`mlkem_fault_hooks.c`).
- `tfib_implementation/`: Hardened v2 implementation containing twiddle factor integrity binding (`tfib_ref.c`, `tfib_core.c`).
- `data/`: Raw and processed empirical experimental datasets.
- `experiments/`: Campaign runners, fault injection drivers, and reproducibility scripts.
- `benchmarks/`: Nanosecond-precision timing harnesses for baseline, monitored, and DMR implementations.
- `tests/`: Automated unit tests, KAT vector runners, and countermeasure independence validation.
- `paper/`: Complete IEEE-style research manuscript, BibTeX database, and formal review milestones.
- `docs/`: In-depth architecture specifications, gap analyses, and presentation assets.
- `bin/`: Compiled executable binaries for verification and live demonstration.

---

### 2.2 Major Directory Tree & Purpose Map

Below is the authoritative directory map of the research repository:

| Directory | Primary Purpose | Key Files & Artifacts | Related Phases | What to Open First |
|---|---|---|---|---|
| [`algorithms/source_ref/mlkem/`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/) | Reference NIST FIPS 203 ML-KEM implementation (`mlkem-native` commit `fc269bc2d106`). | [`kem.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c), [`poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c), [`indcpa.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/indcpa.c) | Phase 1, Phase 8, Phase 18 | `src/poly.c` (Lines 375–425 for forward butterfly block) |
| [`algorithms/source_ref/`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/) | Integrated invariant monitoring hooks and rollback logic. | [`mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c), [`mlkem_fault_hooks.h`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.h) | Phase 6, Phase 7, Phase 18 | `mlkem_fault_hooks.c` (Lines 600–665 CT monitor; Lines 804–874 GS monitor) |
| [`tfib_implementation/`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/) | Hardened v2 implementation with Twiddle Factor Integrity Binding (TFIB). | [`tfib_ref.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_ref.c), [`tfib_core.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_core.c), [`tfib.h`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib.h) | Step 2C, TFIB Pilot | `tfib_ref.c` (reference twiddle table `tfib_zetas_ref[128]`) |
| [`phase18_audit/`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/) | Production cleanroom audit harness, compiled objects, and raw trial records. | [`production_reproducer.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/production_reproducer.c), [`raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv) | Phase 18 Cleanroom Audit | `raw_production_trials.csv` (400 audited production trials) |
| [`tfib_experiments/`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/) | Canonical 900-trial experimental harness and independence test suite. | [`tfib_experiment_runner.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/tfib_experiment_runner.c), [`test_step2c_countermeasure_independence.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/test_step2c_countermeasure_independence.c) | Canonical Step 2C | `test_step2c_countermeasure_independence.c` |
| [`paper/`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/) | Academic research manuscript and verified citation database. | [`manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md), [`references.bib`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/references.bib) | Phase 2S Final Audit | `manuscript.md` (Sections 3, 4, 5) |
| [`docs/presentation/`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/) | Presentation decks, fact-check registers, design briefs, and Q&A guides. | [`AI_PPT_FINAL_CONTENT.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/AI_PPT_FINAL_CONTENT.md), [`AI_PPT_FACT_CHECK.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/AI_PPT_FACT_CHECK.md), [`DEFENSE_QUESTION_BANK.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/DEFENSE_QUESTION_BANK.md) | Progress Presentation | `AI_PPT_FINAL_CONTENT.md` |
| [`bin/`](file:///Users/dhairyajain/Desktop/pqc%20research/bin/) | Verified compiled executable binaries for immediate execution. | `test_fips_kats`, `production_reproducer`, `tfib_experiment_runner` | Continuous Build | Run `./bin/test_fips_kats` |
| Root Datasets | Authoritative root CSV files summarizing multi-phase empirical validation. | [`tfib_trial_level_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_trial_level_results.csv), [`authoritative_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/authoritative_results.csv) | Consolidated Audit | `tfib_trial_level_results.csv` |

---

### 2.3 Comprehensive Data & Dataset Index

The following table provides the definitive register of all experimental datasets across the repository:

| Dataset / File Name | Exact Repository Path | Type | Sample Size ($N$) | Contents & Recorded Variables | Related Experiment / Phase |
|---|---|:---:|:---:|---|---|
| **Raw Production Trials** | [`phase18_audit/raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv) | Raw CSV | $400$ trials | `trial_id, suite, fault_type, seed, detected, recovered, fail_stop, sdc, retries_taken, elapsed_cycles` | Phase 18 Production Cleanroom Audit |
| **Canonical Trial Results** | [`tfib_trial_level_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_trial_level_results.csv) | Raw CSV | $900$ trials | `trial_id, test_suite, fault_mode, injected, detected, recovered, fail_stop, sdc_occurred, fo_rejected, execution_time_ns` | Step 2C Canonical Campaign |
| **Raw 40k Benchmark** | [`tfib_benchmark_raw.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_benchmark_raw.csv) | Raw CSV | $40{,}000$ runs | `iteration, configuration, operation, latency_ns, cycles, cache_misses` | Step 2C Statistical Benchmark |
| **H1 Activation Audit** | [`phase16_targeted_evidence_closure/h1_activation_audit.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/h1_activation_audit.csv) | Raw CSV | $1{,}200$ rows ($600$ paired) | `trial_id, target_var, injected_val, live_val, verifier_result, circular_blindness_flag` | Phase 16 Verifier Audit |
| **Phase 15Q Trial Ledger** | [`results/phase15q/trial_ledger.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase15q/trial_ledger.csv) | Raw CSV | $16$ trials | `trial_id, fault_target, zeta_idx, bit_pos, detected_ntt, fo_rejected, sdc_status` | Phase 15Q Twiddle Mutation Pilot |
| **Phase 7H DMR Timing** | [`results/phase7h/processed/phase7h_timing_distribution.json`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase7h/processed/phase7h_timing_distribution.json) | Processed JSON | $2{,}000$ runs | Baseline NTT ($46.65\,\mu\text{s}$) vs Sequential DMR NTT ($92.98\,\mu\text{s}$): $+99.33\%$ overhead | Phase 7H Isolated NTT DMR Study |
| **Phase 7I E2E Timing** | [`results/phase7i/processed/phase7i_e2e_results.json`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase7i/processed/phase7i_e2e_results.json) | Processed JSON | $2{,}000$ runs | Baseline Decaps ($110.77\,\mu\text{s}$) vs Monitored Decaps ($129.51\,\mu\text{s}$): $+16.90\%$ overhead | Phase 7I End-to-End Decapsulation Study |
| **Authoritative Matrix** | [`authoritative_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/authoritative_results.csv) | Consolidated CSV | Summary Matrix | Formal claim-to-metric mapping across detection, recovery, latency, and KAT conformance | Phase 13 Final Audit |
| **Claim Evidence Matrix** | [`claim_evidence_matrix.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/claim_evidence_matrix.csv) | Consolidated CSV | Traceability Matrix | Explicit traceability cross-reference between manuscript statements and data rows | Phase 13 Final Reconciliation |

---

### 2.4 Complete Experiment Index (Phases 1–18 & TFIB)

The following table details the core experimental milestones conducted in this research:

| Phase | Core Objective | Primary Experiment Script / Source | Input Test Vectors / Data | Output Data / Artifacts | Main Empirical Finding |
|---|---|---|---|---|---|
| **Phase 1–5** | Initial fault injection harness & recovery trust audit | `experiments/run_fault_injection.sh` | Pseudorandom polynomial vectors | `results/phase5_recovery_trust_audit/` | Discovered that unvalidated recovery loops could be hijacked by persistent faults. |
| **Phase 6** | Runtime verifier falsification & dependency audit | `phase6_verifier_falsification/verifier_test.c` | Mutated butterfly registers | `phase6_verifier_falsification/results.csv` | Demonstrated that verifiers reading modified registers suffer circular masking. |
| **Phase 7H** | Isolated NTT Double Modular Redundancy (DMR) baseline | `benchmarks/bench_ntt_dmr.c` | Standard ML-KEM-768 polynomials ($q=3329$) | `results/phase7h/processed/phase7h_timing_distribution.json` | Measured sequential software DMR latency at $92.98\,\mu\text{s}$ vs $46.65\,\mu\text{s}$ baseline (**$+99.33\%$**). |
| **Phase 7I** | End-to-end monitored decapsulation benchmark | `benchmarks/bench_e2e_decaps.c` | NIST KAT-derived ciphertext and private key pairs | `results/phase7i/processed/phase7i_e2e_results.json` | Measured monitored decapsulation at $129.51\,\mu\text{s}$ vs $110.77\,\mu\text{s}$ baseline (**$+16.90\%$** under `-O3`). |
| **Phase 11** | Standards conformance & KAT audit | `phase11_conformance_audit/audit_kats.c` | 18 NIST KAT vectors | `phase11_conformance_audit/conformance_report.txt` | 18/18 KAT vectors verified passing (ML-KEM and ML-DSA); baseline cryptographic validity locked. |
| **Phase 15Q** | Twiddle factor mutation vulnerability pilot | `experiments/phase15q_twiddle_pilot.c` | Mutated $\zeta$ twiddle tables | `results/phase15q/trial_ledger.csv` | Proved Theorem 1: Twiddle-only mutations bypass operand invariants but are caught by FO re-encryption. |
| **Phase 16** | Circular verifier targeted falsification closure | `phase16_targeted_evidence_closure/test_h1.c` | Target variables across 6 execution points | `phase16_targeted_evidence_closure/h1_activation_audit.csv` | Quantified circular blindness at 591/600 false passes (**98.5%**); enforced mandatory snapshotting. |
| **Phase 17** | Prior art comparative audit & gap analysis | Literature review protocol | 24 surveyed IEEE/ACM/IACR papers | `docs/state_of_art_gap_analysis.md` | Identified zero prior works combining NTT invariant monitoring, localized rollback, and FO fail-stop. |
| **Phase 18** | Cleanroom production reproduction audit | `phase18_audit/production_reproducer.c` | Compiled `mlkem768_inst.o` production object | `phase18_audit/raw_production_trials.csv` | 400 cleanroom trials: 100 clean, 100 transient recoveries, 200 persistent fail-stops, **0 SDC** ($95\%\text{ CI}\le1.26\%$). |
| **TFIB (Step 2C)** | Hardened v2 twiddle integrity & canonical campaign | `tfib_experiments/tfib_experiment_runner.c` | 18 test suites ($N=900$) | `tfib_trial_level_results.csv`, `tfib_benchmark_raw.csv` | Closed Theorem 1 via reference twiddles; 0 SDC across 750 active trials ($95\%\text{ CI}\le0.49\%$). |

---

### 2.5 Source Code Implementation Index

The table below indexes all critical implementation files, their language, purpose, and key functional routines:

| File Name | Exact Repository Path | Language | Architecture Role | Critical Functions & Line Ranges |
|---|---|:---:|---|---|
| `poly.c` | [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c) | C99 | Core NTT polynomial arithmetic with integrated monitor hooks | `mlk_ntt_butterfly_block` (Lines 375–425; operand snapshotting and CT hooks); `mlk_invntt_layer` (Lines 535–590; GS hooks) |
| `mlkem_fault_hooks.c` | [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) | C99 | Invariant verification, register rollback, and error counters | `native_ntt_monitor_butterfly` (Lines 600–665; CT sum/diff checks); `native_invntt_monitor_butterfly` (Lines 804–874; decoupled GS checks) |
| `kem.c` | [`algorithms/source_ref/mlkem/src/kem.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c) | C99 | Full KEM keygen, encaps, and decaps with fail-stop interception | `crypto_kem_dec` (Lines 484–520; checks monitor fail counter, forces `fail = 0xFF`, delegates to FO implicit rejection) |
| `tfib_ref.c` | [`tfib_implementation/tfib_ref.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_ref.c) | C99 | Hardened v2 reference twiddle table binding | `tfib_zetas_ref[128]` (Lines 18–45; read-only hardened lookup table); `tfib_verify_twiddle_integrity` |
| `production_reproducer.c` | [`phase18_audit/production_reproducer.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/production_reproducer.c) | C99 | Cleanroom audit harness testing compiled production binary | `run_cleanroom_suite` (executes 100 clean, 100 F4 transient, 100 F5A stuck-at, 100 F5B memory stuck-at) |
| `test_step2c_countermeasure_independence.c` | [`tfib_experiments/test_step2c_countermeasure_independence.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/test_step2c_countermeasure_independence.c) | C99 | 9-test automated countermeasure independence validation | `test_twiddle_mutation_detection`, `test_checker_logic_fault_injection`, `test_fail_stop_containment` |
| `test_fips_kats.c` | [`tests/test_fips_kats.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tests/test_fips_kats.c) | C99 | NIST Known Answer Test validation runner | `run_mlkem_kats`, `run_mldsa_kats` (verifies 18/18 standard vectors) |

---

### 2.6 Authoritative Results & Claim-Evidence Mapping

Every metric and scientific assertion made in this project is directly traceable to audited data files in the repository:

| # | Scientific Claim / Metric | Exact Evidence File | Relevant Section / Field / Lines | What It Conclusively Proves |
|---|---|---|---|---|
| **1** | **9,856 NTT operations monitored** | [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c) | Lines 375–425, 535–590; Section 4 of `paper/manuscript.md` | Full decapsulation executes $5{,}376$ forward CT butterflies ($6\times896$) and $4{,}480$ inverse GS butterflies ($5\times896$). |
| **2** | **100/100 transient recoveries** | [`phase18_audit/raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv) | Suite `F4_TRANSIENT_RECOVERY` (Rows 102–201) | 100% of injected transient single-bit operand faults were detected and recovered locally in $\le2$ retries. |
| **3** | **200/200 persistent fail-stops** | [`phase18_audit/raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv) | Suites `F5A_STUCK_AT_REG` & `F5B_STUCK_AT_MEM` (Rows 202–401) | Injected permanent stuck-at faults exhausted retry limits, invoked fail-stop, and produced FIPS 203 rejection keys. |
| **4** | **0 SDC across 300 production trials** | [`phase18_audit/raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv) | Column `sdc` across 300 active trials (Rows 102–401) | Zero silent data corruptions observed. Clopper-Pearson exact 95% confidence interval upper bound is $\le 1.26\%$. |
| **5** | **0 SDC across 750 campaign trials** | [`tfib_trial_level_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_trial_level_results.csv) | Column `sdc_occurred` across 750 active trials | Zero silent data corruptions observed. Clopper-Pearson exact 95% confidence interval upper bound is $\le 0.49\%$. |
| **6** | **+16.9% decapsulation overhead** | Phase 7I stdout logs & [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) | Table 2; Section 5.1 of `paper/manuscript.md` | Measured on Apple M3 Pro, Apple Clang 17, `-O3`: Baseline decaps $110.77\,\mu\text{s}$ vs Monitored $129.51\,\mu\text{s}$ ($N=2{,}000$). |
| **7** | **+99.33% isolated NTT DMR overhead** | [`results/phase7h/processed/phase7h_timing_distribution.json`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase7h/processed/phase7h_timing_distribution.json) | Keys `"baseline_mean_ns": 46650`, `"dmr_mean_ns": 92988` | Sequential software DMR for isolated NTT transforms requires $+99.33\%$ latency overhead ($N=2{,}000$). |
| **8** | **+17.27% Phase 7I monitor overhead** | [`results/phase7i/processed/phase7i_e2e_results.json`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase7i/processed/phase7i_e2e_results.json) | Keys `"isolated_ntt_baseline_us": 68.47`, `"isolated_ntt_monitored_us": 80.30` | Isolated monitored NTT transform latency compared to unmonitored NTT in Phase 7I benchmark ($N=2{,}000$). |
| **9** | **591/600 circular verifier false-passes** | [`phase16_targeted_evidence_closure/h1_activation_audit.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/h1_activation_audit.csv) | Column `circular_blindness_flag` across 600 injected trials | 98.5% false-pass rate for naive verifiers reading live mutated registers; proves requirement for pre-computation snapshots. |
| **10** | **18/18 NIST KAT vectors passing** | [`bin/test_fips_kats`](file:///Users/dhairyajain/Desktop/pqc%20research/bin/test_fips_kats) execution logs | Runner terminal output | 100% of standard Known Answer Test vectors pass (ML-KEM-512/768/1024 and ML-DSA-44/65/87). Proves baseline KAT conformance. |
| **11** | **Retry threshold $R_{max}=2$** | [`algorithms/source_ref/mlkem_fault_hooks.h`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.h) | `#define MLKEM_MAX_RETRIES 2` | Maximum retry budget allocated for transient rollback before escalating to persistent fail-stop containment. |
| **12** | **Theorem 1 twiddle blindness proof** | [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) & [`results/phase15q/trial_ledger.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase15q/trial_ledger.csv) | Section 4.4, Theorem 1 | Proves mathematically that $\sum u_i = \sum v_i$ invariant is blind to corrupted twiddle factors $\zeta$; solved by TFIB binding. |

---

### 2.7 Research Documentation & Audit Index

Key analytical documents and architectural specifications are organized across `docs/` and root:
- [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md): Full academic research paper (~7,500 words, 4 formal tables, 24 verified references).
- [`PROJECT_OVERVIEW.md`](file:///Users/dhairyajain/Desktop/pqc%20research/PROJECT_OVERVIEW.md): Executive summary of research programme identity, mathematical foundations, and empirical results.
- [`research-roadmap.md`](file:///Users/dhairyajain/Desktop/pqc%20research/research-roadmap.md): Complete engineering specification for Work Packages 1 through 7.
- [`docs/architecture/RESEARCH_EVOLUTION.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/architecture/RESEARCH_EVOLUTION.md): Detailed architectural record of repository evolution, audit phases, and lessons learned.
- [`docs/presentation/AI_PPT_FINAL_CONTENT.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/AI_PPT_FINAL_CONTENT.md): The authoritative 10-slide source text designed for slide generation and presentation.
- [`docs/presentation/AI_PPT_FACT_CHECK.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/AI_PPT_FACT_CHECK.md): Comprehensive fact-checking register verifying every single metric, claim, and source file.
- [`docs/presentation/DEFENSE_QUESTION_BANK.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/DEFENSE_QUESTION_BANK.md): In-depth 22-question defense preparation bank covering faculty challenges.

---

### 2.8 Verified How-To-Run Command Reference

Every verification program in this repository has been compiled and validated. You can execute these commands directly from the repository root:

```bash
# 1. Verify Baseline Cryptographic Correctness (18/18 NIST KAT Vectors)
# Working Directory: /Users/dhairyajain/Desktop/pqc research
./bin/test_fips_kats
# Expected Output: [PASS] All 18 KAT vectors matched NIST reference values (ML-KEM & ML-DSA).

# 2. Execute Cleanroom 400-Trial Production Reproducer
# Working Directory: /Users/dhairyajain/Desktop/pqc research
./phase18_audit/production_reproducer
# Expected Output: [SUMMARY] Total: 400 | Clean: 100/100 | Recovered: 100/100 | Fail-Stop: 200/200 | SDC: 0/400

# 3. Run Automated Countermeasure Independence Test Suite (9 Test Scenarios)
# Working Directory: /Users/dhairyajain/Desktop/pqc research
./tfib_experiments/test_step2c_countermeasure_independence
# Expected Output: [PASS] All 9 independence and hardening tests passed successfully.

# 4. Execute the Canonical 900-Trial Experimental Campaign
# Working Directory: /Users/dhairyajain/Desktop/pqc research
./tfib_experiments/tfib_experiment_runner
# Expected Output: Executes 18 test suites, records results into tfib_trial_level_results.csv (0 SDC).

# 5. Compile and Inspect Production Object Files
# Working Directory: /Users/dhairyajain/Desktop/pqc research
make -B bin/test_fips_kats
# Expected Output: Clean compilation of C99 cryptographic sources using standard Clang/GCC flags.
```

---

# PART 3 — COMPLETE 10-SLIDE SPEAKING SCRIPT

Every slide section below contains the exact material needed to deliver an authoritative presentation:
- **A. What is on this slide:** Visual layout and core bullet points.
- **B. EXACTLY what I should speak:** Word-for-word, natural first-person oral script including slide transitions.
- **C. Explain it to me:** Conceptual background explaining why this slide exists and what it means.
- **D. Important numbers:** Exhaustive list of numbers on the slide, their origin, and calculation.
- **E. Where to find evidence:** Exact file paths and line numbers.
- **F. 3–5 likely faculty questions:** Specific questions faculty will ask and concise defensible answers.

---

### Slide 1: Title Slide — Research Overview

#### A. What is on this slide
- **Permanent Title:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems
- **Subtitle:** Investigating Cryptographic Reliability, Localized Recovery, and Containment Under Orbital Fault Environments
- **Case Study Subtitle:** Software-Level Fault Resilience for ML-KEM-768 Decapsulation
- **Presenter & Details:** Dhairya Jain, Department of Computer Science & Engineering, November 2026.
- **Standards:** NIST FIPS 203 (ML-KEM), NIST FIPS 204 (ML-DSA).
- **Metric Cards:** Space Systems Programme | 9,856 NTT Butterflies Monitored | +16.9% Latency Overhead | 0 SDC ($N=300$, $95\%\text{ CI}\le1.26\%$).

#### B. EXACTLY what I should speak
> "Good morning, respected committee members and faculty. Today, I am presenting our research titled **'Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems.'**
> 
> As satellite platforms and orbital infrastructure transition to post-quantum cryptography to safeguard long-lived communications against future quantum computers, they face an immediate and severe operational hazard: cosmic radiation. High-energy particles induce computational bit-flips in flight microprocessors, which can silently corrupt cryptographic keys or cause complete communication blackouts.
> 
> In this presentation, I will establish our broader space-systems research programme, present our initial software-level implementation progress on NIST FIPS 203 ML-KEM-768 decapsulation, analyze our empirical fault-injection findings and identified limitations, and map out the remaining work packages required for spacecraft flight qualification.
> 
> Let us begin by examining the specific vulnerability landscape of post-quantum cryptography operating in space."

#### C. Explain it to me
This slide immediately establishes academic credibility and clarity of scope. It prevents the common pitfall where faculty ask, *"Is this just a paper on ML-KEM, or is this about space systems?"* By stating the permanent title upfront and clarifying that ML-KEM-768 is our **initial implementation case study** within a comprehensive 7-work-package space programme, you set the exact right expectations. The four metric cards demonstrate that this is not theoretical speculation—it is supported by working C99 implementation and rigorous empirical benchmarking.

#### D. Important numbers
- **9,856:** Total polynomial butterfly operations monitored during a single ML-KEM-768 decapsulation ($5{,}376$ forward Cooley-Tukey + $4{,}480$ inverse Gentleman-Sande).
- **+16.9%:** End-to-end decapsulation latency overhead under `-O3` optimization ($129.51\,\mu\text{s}$ monitored vs $110.77\,\mu\text{s}$ baseline).
- **0 SDC:** Zero silent data corruptions observed across 300 audited active fault trials in cleanroom testing.
- **$\le 1.26\%$:** Exact Clopper-Pearson 95% confidence interval upper bound for 0 observed SDC events in $N=300$ trials.

#### E. Where to find evidence
- Research title and abstract: [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) (Lines 1–35).
- Research programme structure: [`PROJECT_OVERVIEW.md`](file:///Users/dhairyajain/Desktop/pqc%20research/PROJECT_OVERVIEW.md) (Section 1).
- 400-trial cleanroom dataset: [`phase18_audit/raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv).

#### F. 3–5 likely faculty questions with concise answers
1. *Why is this titled "Space Systems" if your experiments were run on a workstation?*  
   **Answer:** "The overall research programme addresses spaceborne cryptographic reliability under cosmic radiation. Space systems increasingly deploy commercial microcontrollers that suffer Single-Event Upsets. Our current progress represents Level B: the core algorithmic fault-resilience case study evaluated under register-level fault injection models. Work Package 5 in our roadmap covers cyclotron beam testing on physical rad-hard hardware."
2. *Why focus specifically on ML-KEM-768?*  
   **Answer:** "ML-KEM-768 is NIST's primary standardized Key Encapsulation Mechanism under FIPS 203, providing NIST Category 3 security (equivalent to AES-192). It represents the exact operational sweet spot for satellite telecommand and key establishment links."
3. *What does SDC mean in this context?*  
   **Answer:** "Silent Data Corruption means the decapsulation routine computes a corrupted session key without detecting the fault or raising an error flag. This causes the satellite and ground station to silently diverge, severing encrypted communication."

---

### Slide 2: Fault Vulnerabilities in Post-Quantum Cryptographic Implementations

#### A. What is on this slide
- **Heading:** Fault Vulnerabilities in Post-Quantum Cryptographic Implementations
- **The Space Radiation Hazard:** High-energy protons and heavy ions cause Single-Event Effects (SEEs) in orbital microprocessors: SEUs (register bit-flips) and SETs (combinational transients).
- **The Classical Dilemma in Key Decapsulation:**
  - *Undetected Fault:* Causes Silent Data Corruption (SDC). The ground station and satellite derive different keys, severing the link.
  - *Unmitigated Abort:* Traditional countermeasures trigger panic stops or processor resets, causing spacecraft reboot loops and link dropouts.
- **Limitations of Existing Defenses:**
  - *Hardware Redundancy (TMR):* Prohibitive mass, power, and cost for CubeSats and small satellites.
  - *Software Dual Modular Redundancy (DMR):* Doubles execution time (+99.33% measured latency overhead).
  - *Fujisaki-Okamoto (FO) Transform Alone:* Re-encryption detects ciphertext tampering, but cannot pinpoint where an arithmetic fault occurred or recover transient errors locally.

#### B. EXACTLY what I should speak
> "Moving to Slide 2, let us examine why post-quantum cryptography is uniquely vulnerable to space radiation.
> 
> In low Earth orbit and deep space, satellites are subjected to energetic cosmic rays and solar particles. When an ionizing particle strikes a microprocessor register or arithmetic logic unit, it induces a Single-Event Upset—a bit-flip—or a Single-Event Transient.
> 
> In post-quantum lattice-based algorithms like ML-KEM, cryptographic keys are encapsulated in high-degree polynomial rings. During decapsulation, millions of modular additions and multiplications occur. If a radiation particle flips even a single bit in an intermediate polynomial coefficient, the system faces a dangerous dilemma:
> 
> First, if the fault is undetected, the satellite derives an incorrect session key while believing it succeeded. This is Silent Data Corruption. Because the ground station has the correct key and the satellite has a corrupt key, all subsequent encrypted telemetry and telecommands fail. The link is completely severed.
> 
> Second, if the system uses naive fault detection that simply panics and reboots the flight computer, the satellite enters an availability blackout.
> 
> Furthermore, existing defenses do not solve this efficiently: hardware Triple Modular Redundancy is too heavy and power-hungry for small satellites; pure software DMR doubles cryptographic execution time; and the Fujisaki-Okamoto re-encryption check, while catching invalid outputs, provides zero internal error diagnosis and cannot recover transient faults.
> 
> This brings us directly to our research objectives."

#### C. Explain it to me
This slide sets up the conflict. Faculty must understand that in space, you cannot simply say *"if there's an error, throw an exception and reboot."* Rebooting a satellite can cause attitude control loss, antenna pointing failure, and missed ground station passes. At the same time, you cannot allow incorrect keys to pass through (SDC). The core contribution is balancing **security** (preventing SDC) with **availability** (recovering transient faults without rebooting).

#### D. Important numbers
- **$+99.33\%$:** Measured latency overhead of sequential software Double Modular Redundancy on isolated NTT transforms ($92.98\,\mu\text{s}$ vs $46.65\,\mu\text{s}$ baseline).
- **10–25 years:** Typical operational mission lifetime of high-value space orbital assets.

#### E. Where to find evidence
- Radiation effects in space: [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) (Section 1, Lines 40–85).
- DMR baseline benchmark data: [`results/phase7h/processed/phase7h_timing_distribution.json`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase7h/processed/phase7h_timing_distribution.json).
- Gap analysis against prior art: [`docs/state_of_art_gap_analysis.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/state_of_art_gap_analysis.md).

#### F. 3–5 likely faculty questions with concise answers
1. *Why doesn't the Fujisaki-Okamoto transform in ML-KEM protect against faults?*  
   **Answer:** "The FO transform was designed for IND-CCA2 security against active chosen-ciphertext attacks by re-encrypting the decrypted message and comparing ciphertexts. While it rejects corrupted ciphertexts at the very end of decapsulation, it treats all arithmetic errors as malicious attacks, immediately discarding the key. It cannot distinguish transient cosmic ray strikes from attacks, cannot recover operands, and provides zero fault localization."
2. *Why is hardware redundancy like TMR not sufficient?*  
   **Answer:** "Triple Modular Redundancy requires tripling the processor cores and voting logic, which dramatically increases power, mass, and thermal dissipation. For modern CubeSats and mega-constellations operating on tight SWaP (Size, Weight, and Power) budgets, software-level resilience on commercial COTS processors is essential."
3. *What is the difference between an SEU and an SET?*  
   **Answer:** "An SEU (Single-Event Upset) is a radiation-induced state change in a memory element or register latch. An SET (Single-Event Transient) is a transient voltage spike generated in combinational logic that can propagate and be latched into a register on a clock edge."

---

### Slide 3: Research Objectives and Scope Definition

#### A. What is on this slide
- **Heading:** Research Objectives and Scope Definition
- **Primary Research Question:** How can software-level arithmetic invariants detect and recover radiation-induced computational faults in post-quantum key decapsulation without exceeding satellite SWaP constraints?
- **Four Core Research Objectives:**
  1. *Sub-Word Invariant Monitoring:* Design mathematical invariants to verify forward (Cooley-Tukey) and inverse (Gentleman-Sande) NTT butterfly operations with zero modular divisions.
  2. *Localized In-Place Recovery:* Implement register-level snapshotting to recover transient faults in-place within the active execution frame without restarting decapsulation.
  3. *Multi-Stage Containment:* Enforce bounded retry thresholds ($R_{max}=2$) and fail-stop escalation to prevent persistent fault escape and guarantee zero SDC.
  4. *Rigorous Empirical Validation:* Benchmark latency overhead against standard unmonitored code and validate resilience across hundreds of active fault trials.
- **Explicit Scope Boundaries:** Level A Programme vs Level B Case Study vs Level C Future Work.

#### B. EXACTLY what I should speak
> "Turning to Slide 3, this brings us to our research objectives and precise scope definition.
> 
> Our central research question asks: **How can software-level algebraic invariants detect and recover radiation-induced faults in post-quantum key decapsulation, maintaining mathematical correctness while remaining well below the overhead of dual modular redundancy?**
> 
> To answer this, we formulated four primary objectives:
> 
> First, to design lightweight algebraic invariants tailored to both forward Cooley-Tukey and inverse Gentleman-Sande NTT butterflies, ensuring zero high-latency modular divisions.
> 
> Second, to engineer a localized rollback mechanism using pre-computation register snapshots, enabling immediate in-place re-execution of corrupted butterflies without restarting the entire decapsulation routine.
> 
> Third, to establish a multi-stage containment pipeline that bounds retries to a maximum of two attempts, cleanly escalating persistent faults to fail-stop containment and FIPS 203 implicit rejection.
> 
> And fourth, to validate this implementation through rigorous statistical fault injection and nanosecond-precision benchmarking against NIST Known Answer Tests.
> 
> I must explicitly emphasize our scope boundaries: the overall programme addresses space systems, while the implementation presented today covers Level B—our C99 case study on ML-KEM-768 decapsulation.
> 
> Let us now inspect the architectural framework designed to achieve these objectives."

#### C. Explain it to me
This slide defines the contract between the researcher and the examination panel. By stating four clear, testable objectives, you control the scope of the defense. It shows intellectual discipline: you are not claiming to have built a satellite flight computer today; you have designed, implemented, and audited the mathematical fault-resilience engine for the core post-quantum algorithm, with clear boundaries.

#### D. Important numbers
- **4:** Core research objectives.
- **$R_{max}=2$:** Maximum retry limit before persistent fault escalation.
- **0:** Modular divisions used in the invariant verification algebra (all checks use modular additions and multiplications).

#### E. Where to find evidence
- Research scope definition: [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) (Section 1.2).
- Project objectives: [`PROJECT_OVERVIEW.md`](file:///Users/dhairyajain/Desktop/pqc%20research/PROJECT_OVERVIEW.md) (Section 3).
- Evolution history: [`docs/architecture/RESEARCH_EVOLUTION.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/architecture/RESEARCH_EVOLUTION.md).

#### F. 3–5 likely faculty questions with concise answers
1. *Why did you limit retries to exactly $R_{max}=2$?*  
   **Answer:** "In orbital radiation environments, true Single-Event Transients resolve within one to two clock cycles. If an arithmetic fault persists after two re-executions, it is highly likely to be a permanent hardware defect or stuck-at latch fault. Allowing unbounded retries would create infinite loops and violate real-time satellite deadlines."
2. *Why focus exclusively on decapsulation rather than key generation or encapsulation?*  
   **Answer:** "On spacecraft, key decapsulation is the primary operational primitive executed by the satellite during uplink telecommand authentication and session key establishment. Furthermore, decapsulation contains both forward and inverse NTT operations, making it the most computationally complex and vulnerable phase."
3. *What do you mean by 'zero modular divisions'?*  
   **Answer:** "Modular division in prime fields requires computing modular inverses, typically via the Extended Euclidean Algorithm or Fermat's Little Theorem ($a^{q-2} \pmod q$), costing hundreds of CPU cycles. Our invariants use only modular additions and multiplications, preserving execution efficiency."

---

### Slide 4: Proposed Framework for Fault Detection and Recovery

#### A. What is on this slide
- **Heading:** Proposed Framework for Fault Detection and Recovery
- **Architecture Overview:** Three-stage defense-in-depth pipeline:
  1. *Stage 1: Pre-Computation Snapshotting:* Preserves clean register operands ($u_{saved}, v_{saved}$) prior to butterfly execution.
  2. *Stage 2: Invariant Monitoring & Localized Rollback:* Executes butterfly, evaluates algebraic invariant; on transient mismatch, restores snapshot and retries ($R \le 2$).
  3. *Stage 3: Escalation & Containment:* If retries exceed limit, triggers persistent fail-stop, forces FIPS 203 implicit rejection key ($K_{rej}$), avoiding SDC and crashes.
- **Conceptual Flowchart Diagram:**
  - `Input Operands` $\to$ `Snapshot Registers` $\to$ `Butterfly Execution` $\to$ `Invariant Check`
  - If Valid $\to$ `Proceed to Next Butterfly`
  - If Invalid ($R < 2$) $\to$ `Rollback to Snapshot & Retry`
  - If Invalid ($R \ge 2$) $\to$ `Escalate to Fail-Stop Counter` $\to$ `FIPS 203 Implicit Rejection`

#### B. EXACTLY what I should speak
> "Moving to Slide 4, here is our proposed fault detection and recovery framework.
> 
> Rather than treating cryptographic routines as monolithic black boxes, our framework operates at the sub-word arithmetic layer through a three-stage defense-in-depth pipeline.
> 
> In Stage 1, before any butterfly arithmetic begins, the processor takes an immediate snapshot of the input coefficients into dedicated registers—saving $u$ and $v$. This snapshotting is critical: as I will show in our limitations analysis, verifiers that attempt to check arithmetic using mutated registers suffer a 98.5% blindness rate due to circular dependency.
> 
> In Stage 2, the butterfly executes, and our algebraic invariant checker immediately verifies mathematical consistency. If an ionizing particle causes a transient upset, the invariant check fails. The handler immediately restores the clean operands from the register snapshot and retries the butterfly. Because this recovery is purely localized within CPU registers, it requires zero stack unwinding, zero heap reallocation, and zero function re-entry.
> 
> In Stage 3, if the fault is persistent—such as a permanent stuck-at register fault—the retry counter exceeds our threshold of $R_{max}=2$. Instead of crashing the processor or allowing corrupt coefficients to propagate into the key material, the framework triggers an algebraic fail-stop. It increments a persistent failure counter which is intercepted by the outer KEM wrapper, forcing the execution to complete deterministically by outputting the standard FIPS 203 pseudorandom rejection key.
> 
> This guarantees two vital properties: **availability** through localized transient recovery, and **security** through guaranteed containment of persistent faults.
> 
> Let us look at how this is instantiated in the ML-KEM-768 algorithm."

#### C. Explain it to me
This slide presents the core architectural innovation. It explains how localized recovery and global containment work together. The key insight is that software recovery must be *localized* (at the butterfly layer) to be fast, but fault containment must be *global* (escalating to the KEM level) to prevent SDC when faults are permanent. It shows that our framework handles both transient and permanent faults gracefully.

#### D. Important numbers
- **3:** Defense-in-depth stages (Snapshotting, Local Rollback, Global Containment).
- **0:** Memory reallocations or stack unwinding calls required during rollback.
- **$R_{max}=2$:** Maximum retry attempts per butterfly block.

#### E. Where to find evidence
- Rollback logic implementation: [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) (Lines 600–665).
- KEM fail-stop interception: [`algorithms/source_ref/mlkem/src/kem.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c) (Lines 484–520).
- Architectural specification: [`PROJECT_OVERVIEW.md`](file:///Users/dhairyajain/Desktop/pqc%20research/PROJECT_OVERVIEW.md) (Section 4).

#### F. 3–5 likely faculty questions with concise answers
1. *Where are the snapshots stored? Doesn't saving registers consume precious SRAM?*  
   **Answer:** "The snapshots are held purely in local processor registers allocated by the C compiler (`u_saved`, `v_saved`), costing zero dynamic heap allocation and negligible stack overhead. They exist only for the duration of the butterfly block execution."
2. *What happens if the snapshot registers themselves are hit by radiation?*  
   **Answer:** "If the snapshot register is corrupted, the invariant check will either fail during the initial execution or during retry, causing the system to escalate safely to fail-stop containment. Crucially, it cannot cause Silent Data Corruption."
3. *Why delegate to FIPS 203 implicit rejection instead of returning an error code?*  
   **Answer:** "In post-quantum protocols, returning distinct error codes for decapsulation failures can open side-channel or oracle attacks. By deterministically completing the Fujisaki-Okamoto implicit rejection, the implementation returns a pseudorandom rejection key, safely terminating the protocol without revealing internal state."

---

### Slide 5: ML-KEM-768: Implementation and Experimental Setup

#### A. What is on this slide
- **Heading:** ML-KEM-768: Implementation and Experimental Setup
- **Cryptographic Baseline:**
  - NIST FIPS 203 reference implementation (`mlkem-native` commit `fc269bc2d106`).
  - Prime modulus $q = 3329$, polynomial degree $n = 256$, matrix dimension $k = 3$.
  - 100% C99 with zero heap allocation (`malloc`-free).
- **Arithmetic Breakdown per Decapsulation:**
  - Forward NTT (Cooley-Tukey): 6 transforms $\times$ 896 butterflies = **5,376 operations**.
  - Inverse NTT (Gentleman-Sande): 5 transforms $\times$ 896 butterflies = **4,480 operations**.
  - **Total Operations Monitored:** $5{,}376 + 4{,}480 = \mathbf{9{,}856}$ **butterflies**.
- **Experimental Fault-Injection Harness:**
  - Register-level software fault injection simulating Single-Event Upsets (SEUs) and Single-Event Transients (SETs).
  - Four distinct test suites: Clean Baseline ($N=100$), Transient Operand Single-Bit Faults ($N=100$), Persistent Register Stuck-At ($N=100$), Persistent Memory Stuck-At ($N=100$).
  - Evaluated on compiled production binary (`mlkem768_inst.o`) via cleanroom reproducer.

#### B. EXACTLY what I should speak
> "On Slide 5, we examine the cryptographic implementation details and our experimental setup.
> 
> Our implementation is built directly upon the official NIST FIPS 203 reference code from `mlkem-native`, written in standard C99 with zero dynamic memory allocation. ML-KEM-768 operates over polynomial rings with degree $n=256$ and prime modulus $q=3329$, using a $3\times3$ polynomial matrix.
> 
> To understand the monitoring surface, let us analyze the arithmetic operations executed during a single full decapsulation call.
> 
> Each Number Theoretic Transform consists of 7 layers of 64 butterfly operations, yielding exactly 896 butterflies per polynomial transform.
> 
> During decapsulation, re-encryption and polynomial arithmetic require 6 forward NTT calls, totaling **5,376 Cooley-Tukey butterflies**. Inverting the polynomials back to normal domain requires 5 inverse NTT calls, totaling **4,480 Gentleman-Sande butterflies**.
> 
> Combined, our framework actively monitors exactly **9,856 butterfly operations per decapsulation**.
> 
> To evaluate resilience under orbital fault conditions, we engineered a cleanroom fault-injection harness that operates directly on the compiled production object files. We injected single-bit transient SEU flips into butterfly registers, permanent stuck-at-1 register faults, and persistent memory faults across 400 audited production trials.
> 
> Next, let us examine the mathematical invariants that monitor these 9,856 operations."

#### C. Explain it to me
This slide provides the exact arithmetic grounding for the presentation. Faculty love to see that you understand the low-level algorithmic mechanics of ML-KEM. Explaining why there are 9,856 operations ($6\times896$ forward and $5\times896$ inverse) proves you have mastered the internals of FIPS 203 decapsulation. It also clarifies that the testing was performed on real, compiled production objects, not an artificial toy simulator.

#### D. Important numbers
- **$q = 3329$:** ML-KEM prime modulus.
- **$n = 256$:** Polynomial degree.
- **$k = 3$:** Module dimension for Security Category 3 (ML-KEM-768).
- **896:** Butterflies per 256-degree polynomial ($7 \text{ layers} \times 64 \text{ butterflies/layer} \times 2 \text{ coefficients/butterfly} = 128 \times 7 = 896$).
- **5,376:** Forward Cooley-Tukey butterflies monitored ($6 \times 896$).
- **4,480:** Inverse Gentleman-Sande butterflies monitored ($5 \times 896$).
- **9,856:** Total monitored operations per decapsulation ($5{,}376 + 4{,}480$).
- **400:** Audited cleanroom production trials ($100$ clean, $100$ transient, $100$ stuck-at reg, $100$ stuck-at mem).

#### E. Where to find evidence
- Forward NTT implementation: [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c) (Lines 375–425).
- Inverse NTT implementation: [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c) (Lines 535–590).
- Cleanroom test script: [`phase18_audit/production_reproducer.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/production_reproducer.c).
- Raw trial data: [`phase18_audit/raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv).

#### F. 3–5 likely faculty questions with concise answers
1. *Where do the 6 forward NTTs and 5 inverse NTTs come from in decapsulation?*  
   **Answer:** "In ML-KEM-768 decapsulation, the secret key vector $s$ is already stored in NTT domain. The received ciphertext vector $u$ has $k=3$ polynomials converted via forward NTT ($3$ NTTs). Re-encryption in the Fujisaki-Okamoto transform computes $A \times r$, where the public matrix $A$ ($3\times3$) multiplies vector $r$ ($k=3$), requiring $3$ forward NTTs on $r$. This gives $3+3=6$ forward NTTs ($5{,}376$ CT butterflies). For inverse NTTs: inner product $s^T \cdot u$ requires $1$ inverse NTT to recover message $m'$. Then re-encryption computes $A \times r + e$, requiring $k=3$ inverse NTTs, plus $1$ inverse NTT for $t^T \cdot r + e_2$, giving $1+3+1=5$ inverse NTTs ($4{,}480$ GS butterflies)."
2. *Is your code standard-compliant?*  
   **Answer:** "Yes. The underlying implementation is byte-level identical to the official reference code of NIST FIPS 203, fully passing all 18 standard Known Answer Test (KAT) vectors."
3. *Why did you evaluate on production object files rather than in a mock simulator?*  
   **Answer:** "Mock simulators often obscure compiler optimizations, register spills, and pipeline reordering. Testing the compiled `mlkem768_inst.o` binary ensures that our monitoring and rollback logic function correctly in real, optimized machine code."

---

### Slide 6: Mathematical Invariants and Fault-Containment Architecture

#### A. What is on this slide
- **Heading:** Mathematical Invariants and Fault-Containment Architecture
- **Forward Cooley-Tukey Invariant:**
  - Arithmetic: $u' = u + \zeta \cdot v \pmod q$, $\quad v' = u - \zeta \cdot v \pmod q$.
  - Invariant Check: $(u' + v') \equiv 2u \pmod q \quad \text{and} \quad (u' - v') \equiv 2\zeta v \pmod q$.
  - Cost: 2 modular additions, 0 modular divisions.
- **Inverse Gentleman-Sande Decoupled Invariant:**
  - Arithmetic: $u' = u + v \pmod q$, $\quad v' = (u - v) \cdot \zeta \pmod q$.
  - Invariant Check: Decoupled sum/difference rails with modular multiplication verification ($v' \cdot \zeta^{-1} \equiv u - v \pmod q$ or Montgomery constant formulation).
- **Formal Invariant Blindness (Theorem 1):**
  - Identifies that input/output invariants are mathematically blind to corrupted twiddle factors $\zeta$ if both outputs are computed consistently.
  - Solution in Hardened v2: Reference Twiddle Factor Integrity Binding (`tfib_ref.c`).

#### B. EXACTLY what I should speak
> "Turning to Slide 6, let us examine the mathematical core of our detection engine.
> 
> To detect computational faults without the 100% latency penalty of Dual Modular Redundancy, we derive algebraic invariants directly from the butterfly arithmetic.
> 
> In the forward Cooley-Tukey butterfly, two input coefficients $u$ and $v$ are transformed using twiddle factor $\zeta$ to produce $u' = u + \zeta v$ and $v' = u - \zeta v \pmod q$.
> 
> Notice the algebraic symmetry: if we add the two outputs, $u' + v'$, the terms involving $\zeta v$ cancel out, yielding exactly $2u \pmod q$. If we subtract them, $u' - v'$, the $u$ terms cancel, yielding $2\zeta v \pmod q$.
> 
> Our monitor verifies these identities. Crucially, this check requires only two modular additions and one modular multiplication—it requires **zero modular divisions**.
> 
> For the inverse Gentleman-Sande butterfly, the subtraction precedes multiplication by $\zeta$. We decouple the adder-rail and multiplier-rail checks to maintain division-free algebraic verification.
> 
> However, rigorous research requires identifying where the mathematics can fail. Through formal analysis, we established **Theorem 1: The Twiddle Scalar Blindness Theorem**.
> 
> If an energetic particle corrupts the twiddle factor $\zeta$ inside memory, the butterfly will compute incorrect outputs that nonetheless satisfy the invariant $u' + v' \equiv 2u \pmod q$ because the algebraic cancellation still holds!
> 
> To close this gap in our hardened v2 implementation, we developed Twiddle Factor Integrity Binding, binding the active twiddle table against a trusted reference structure.
> 
> Now let us look at the experimental performance and validation results."

#### C. Explain it to me
This is the most academically impressive slide in the deck. It shows that you did not just write code—you derived algebraic invariants that exploit the mathematical symmetry of the Number Theoretic Transform. More importantly, presenting Theorem 1 demonstrates profound scientific maturity: rather than hiding a limitation, you proved the mathematical boundary where input-output invariants are blind (twiddle corruption) and showed how you solved it in v2.

#### D. Important numbers
- **$2u \pmod q$:** Cooley-Tukey sum invariant value.
- **$2\zeta v \pmod q$:** Cooley-Tukey difference invariant value.
- **0:** Modular divisions used across all forward and inverse monitors.
- **Theorem 1:** Formal theorem proving invariant blindness to twiddle factor mutations.

#### E. Where to find evidence
- CT invariant implementation: [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) (Lines 600–665).
- GS invariant implementation: [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) (Lines 804–874).
- Theorem 1 proof: [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) (Section 4.4, Lines 245–280).
- Reference twiddle binding: [`tfib_implementation/tfib_ref.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_ref.c) (Lines 18–45).

#### F. 3–5 likely faculty questions with concise answers
1. *What if a fault hits both $u'$ and $v'$ simultaneously such that their sum remains $2u$?*  
   **Answer:** "For a fault to bypass both the sum and difference invariants simultaneously, the injected error $\Delta u'$ and $\Delta v'$ must satisfy $\Delta u' = -\Delta v'$ and $\Delta u' = \Delta v'$, which implies $\Delta u' = \Delta v' = 0 \pmod q$. Thus, no single additive fault can bypass both invariants simultaneously."
2. *What is Theorem 1 in simple terms?*  
   **Answer:** "Theorem 1 states that because the sum invariant $(u' + v') \equiv 2u \pmod q$ depends only on the input operand $u$ and cancels out the twiddle factor $\zeta$, any corruption residing strictly within $\zeta$ preserves the sum equality. The difference invariant checks $2\zeta v$, but if the checker reads the corrupted $\zeta$ from the same register, it computes a matching corrupted product, falsely passing the check."
3. *How did you resolve Theorem 1?*  
   **Answer:** "In our hardened v2 implementation (`tfib_ref.c`), we introduced Twiddle Factor Integrity Binding, which binds the active twiddle table against a hardened, read-only reference table `tfib_zetas_ref[128]`, ensuring twiddle integrity before butterfly execution."

---

### Slide 7: Performance Analysis and Experimental Validation

#### A. What is on this slide
- **Heading:** Performance Analysis and Experimental Validation
- **Empirical Latency Benchmarks ($N=2,000$ iterations):**
  - Baseline Decapsulation: $110.77\,\mu\text{s}$.
  - Monitored Decapsulation: $129.51\,\mu\text{s}$.
  - **Latency Overhead:** **+16.90%** (under Apple Clang 17, `-O3`).
  - *Comparison:* Sequential Software DMR on isolated NTT requires **+99.33%** ($92.98\,\mu\text{s}$ vs $46.65\,\mu\text{s}$).
- **Fault-Injection Campaign Results (Cleanroom $N=400$):**
  - Clean Baseline: 100/100 Successful Decapsulations (0 False Alarms).
  - Transient Injections (F4): 100/100 Detected and Recovered Locally ($\le2$ Retries).
  - Persistent Register Faults (F5A): 100/100 Escalated to Fail-Stop (Rejection Key $K_{rej}$).
  - Persistent Memory Faults (F5B): 100/100 Escalated to Fail-Stop (Rejection Key $K_{rej}$).
  - **Silent Data Corruption (SDC):** **0 / 300 active trials** ($95\%\text{ CI: } \le 1.26\%$).
  - **Canonical Campaign (N=900):** **0 / 750 active trials** ($95\%\text{ CI: } \le 0.49\%$).

#### B. EXACTLY what I should speak
> "Moving to Slide 7, we present the empirical performance analysis and experimental validation.
> 
> A primary critique of fault-tolerant software is performance degradation. To evaluate this rigorously, we conducted high-precision nanosecond timing benchmarks across 2,000 iterations under standard compiler optimization (`-O3`).
> 
> Unmonitored baseline ML-KEM-768 decapsulation executes in 110.77 microseconds. With all 9,856 butterfly operations actively monitored and snapshot-protected, the monitored decapsulation executes in 129.51 microseconds.
> 
> This represents a modest latency overhead of **+16.90%**.
> 
> In contrast, we measured sequential software Double Modular Redundancy on isolated NTT transforms, which required **+99.33%** overhead—virtually doubling the execution time. Our invariant monitoring achieves comprehensive coverage at a fraction of DMR's cost.
> 
> Next, let us examine our fault injection validation. In our audited cleanroom campaign of 400 production trials:
> 
> In the clean baseline suite, 100 out of 100 trials completed successfully with zero false alarms.
> 
> In the transient fault suite, 100 out of 100 injected single-bit operand faults were detected by our invariants, rolled back to register snapshots, and successfully recomputed without corrupting the session key.
> 
> In the persistent stuck-at register and memory suites, all 200 trials exhausted the retry budget, cleanly escalated to fail-stop containment, and produced the standard FIPS 203 implicit rejection key.
> 
> Across all 300 active fault trials in the production audit, we observed **exactly zero Silent Data Corruption events**, establishing a 95% Clopper-Pearson upper bound of 1.26%. In our larger 900-trial canonical campaign, across 750 active fault trials, zero SDC was observed, tightening the bound to **$\le 0.49\%$**.
> 
> Let us now critically address the research limitations and identified gaps."

#### C. Explain it to me
This slide delivers the core empirical proof. It directly contrasts your +16.9% overhead against the +99.33% overhead of DMR, proving the practical value of your approach. It also presents the exact trial breakdown: 100% transient recovery, 100% persistent fail-stop, and 0 SDC. Highlighting the statistical confidence intervals ($1.26\%$ and $0.49\%$) demonstrates that you understand the difference between sample observations and statistical bounds.

#### D. Important numbers
- **$110.77\,\mu\text{s}$:** Baseline decapsulation execution time.
- **$129.51\,\mu\text{s}$:** Monitored decapsulation execution time.
- **+16.90%:** Measured end-to-end decapsulation overhead ($N=2{,}000$).
- **+99.33%:** Measured sequential DMR overhead on isolated NTT transforms ($N=2{,}000$).
- **100/100:** Clean baseline success rate (0 false alarms).
- **100/100:** Transient fault recovery rate.
- **200/200:** Persistent fault fail-stop containment rate.
- **0 / 300:** Observed SDC in cleanroom production trials.
- **$\le 1.26\%$:** 95% Clopper-Pearson confidence bound for $N=300$.
- **0 / 750:** Observed SDC in canonical campaign trials.
- **$\le 0.49\%$:** 95% Clopper-Pearson confidence bound for $N=750$.

#### E. Where to find evidence
- Cleanroom trial dataset: [`phase18_audit/raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv).
- Canonical campaign dataset: [`tfib_trial_level_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_trial_level_results.csv).
- End-to-end timing JSON: [`results/phase7i/processed/phase7i_e2e_results.json`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase7i/processed/phase7i_e2e_results.json).
- DMR timing JSON: [`results/phase7h/processed/phase7h_timing_distribution.json`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase7h/processed/phase7h_timing_distribution.json).

#### F. 3–5 likely faculty questions with concise answers
1. *Why is the decapsulation overhead +16.9% when isolated NTT monitoring is +17.27%?*  
   **Answer:** "The full ML-KEM-768 decapsulation includes non-NTT operations, such as SHA-3 / SHAKE hashing and vector point-wise additions. Because our monitoring hooks are applied specifically to the 11 NTT transforms (9,856 butterflies), the overall decapsulation latency overhead amortizes to +16.9%."
2. *Can you claim that your system has a 0% probability of SDC?*  
   **Answer:** "No, claiming a zero probability of SDC is scientifically unprovable through empirical sampling. We observed 0 SDC events across 750 active trials, which allows us to claim a rigorous 95% Clopper-Pearson statistical upper bound of $\le 0.49\%$."
3. *How was the DMR benchmark conducted?*  
   **Answer:** "In Phase 7H, we implemented sequential software DMR on the NTT transform, executing the forward transform twice and comparing all 256 output coefficients. That benchmark yielded $92.98\,\mu\text{s}$ compared to $46.65\,\mu\text{s}$ baseline, confirming a +99.33% overhead."

---

### Slide 8: Research Limitations and Identified Gaps

#### A. What is on this slide
- **Heading:** Research Limitations and Identified Gaps
- **Critical Self-Audit & Defensible Limitations:**
  1. *Circular Verifier Blindness:* Verifiers that inspect mutated registers directly suffer a **98.5% false-pass rate** (591/600 false passes). Pre-computation snapshots are mandatory.
  2. *Twiddle Factor Scalar Blindness (Theorem 1):* Operand invariants cannot detect corruptions confined strictly to twiddle lookup tables.
  3. *Control-Flow and Instruction Skip Vulnerability:* Invariant checks verify arithmetic operands, not instruction program counters or branching logic.
  4. *Software vs Physical Fault Injection:* Workstation-based register simulation does not replicate physical particle ionization, charge deposition, or multi-bit SRAM cluster upsets.
  5. *Single Algorithm Focus:* Evaluated on ML-KEM-768 decapsulation; does not yet validate digital signatures (ML-DSA) or other security categories.

#### B. EXACTLY what I should speak
> "Moving to Slide 8, an essential requirement of rigorous scientific research is identifying vulnerabilities and limitations through adversarial self-auditing.
> 
> In our research, we actively attacked our own framework and uncovered five distinct limitations:
> 
> First, we discovered the **Circular Verifier Flaw**. In early implementations, runtime checkers read operands directly from live registers after the butterfly executed. When we subjected this to adversarial testing across 600 trials, the checker produced **591 false passes—a 98.5% failure rate**. Why? Because when the register holding the coefficient was mutated, the verifier used the mutated value in both sides of its check! This proved that pre-computation register snapshotting is mathematically mandatory.
> 
> Second, as formalized in Theorem 1, our operand invariants exhibit twiddle scalar blindness: corruptions restricted entirely to twiddle factors preserve algebraic symmetry and bypass operand checks.
> 
> Third, our invariant checks protect arithmetic data paths, but do not detect instruction skips or corrupted program counters. An instruction skip that bypasses the monitor entirely would not be trapped by arithmetic invariants.
> 
> Fourth, our experiments were conducted via software-level register mutation on a host CPU. While this faithfully models Single-Event Upsets in register latches, it does not capture physical semiconductor charge deposition or multi-cell radiation cluster upsets.
> 
> And fifth, our current implementation evaluates ML-KEM-768; it does not yet extend to digital signatures such as ML-DSA.
> 
> These identified gaps directly inform our future research trajectory."

#### C. Explain it to me
Faculty respect a candidate who candidly discusses limitations far more than one who claims perfection. By presenting the 98.5% circular verifier flaw (and how snapshotting fixed it) and acknowledging the difference between software fault injection and physical cyclotron radiation, you demonstrate advanced critical thinking. You preempt faculty attacks by showing you already discovered and analyzed the flaws yourself.

#### D. Important numbers
- **591 / 600:** False passes recorded by circular/unshielded verifiers.
- **98.5%:** Failure/blindness rate of verifiers reading mutated live registers.
- **5:** Explicit architectural limitations identified.

#### E. Where to find evidence
- Circular verifier audit dataset: [`phase16_targeted_evidence_closure/h1_activation_audit.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/h1_activation_audit.csv).
- Discussion of limitations: [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) (Section 6, Lines 380–430).
- Fact check documentation: [`docs/presentation/AI_PPT_FACT_CHECK.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/AI_PPT_FACT_CHECK.md) (Claim 7 & 12).

#### F. 3–5 likely faculty questions with concise answers
1. *Why did the circular verifier fail in 591 out of 600 trials?*  
   **Answer:** "In Phase 16, we tested unshielded verifiers that recalculated $u$ by subtracting $v'$ from $u'$. Because the register was already overwritten with corrupt data, the check $(u'_{corrupt} + v'_{corrupt}) \equiv 2u_{corrupt}$ remained algebraically consistent with the mutated state. Only independent register snapshotting before execution breaks this circularity."
2. *If an instruction skip bypasses the invariant check, how is the system protected?*  
   **Answer:** "Arithmetic invariants cannot detect control-flow hijacking. As detailed in Work Package 3 of our roadmap, software control-flow integrity (CFI) through branch tracing and hardware watchdog timers must complement arithmetic invariant checks."
3. *Why didn't you perform physical radiation testing?*  
   **Answer:** "Beam time at a cyclotron facility (such as Texas A&M or Lawrence Berkeley) costs thousands of dollars per hour and requires dedicated rad-hard test boards. Establishing the algorithmic correctness and software fault bounds via simulation is the mandatory precursor, captured as Work Package 5 in our roadmap."

---

### Slide 9: Proposed Extensions and Future Research

#### A. What is on this slide
- **Heading:** Proposed Extensions and Future Research
- **Seven Structured Work Packages (Level C Roadmap):**
  - **WP1: Broader Cryptographic Evaluation:** Extend invariants to NIST FIPS 204 (ML-DSA-65) and FIPS 205 (SLH-DSA).
  - **WP2: Embedded & Space-Oriented Computing:** Target ARM Cortex-M4/M7 and rad-hard RISC-V (RV32IM / NOEL-V) architectures.
  - **WP3: Space-Relevant Fault Modelling:** Multi-bit upsets, burst errors, and compiler-aware Control-Flow Integrity (CFI).
  - **WP4: Hardware/Software Fault Resilience:** Integration with hardware ECC, Memory Protection Units (MPUs), and twiddle CRC32 binding.
  - **WP5: Physical Validation:** Laboratory Electromagnetic Fault Injection (EMFI), laser pulsing, and cyclotron proton beam irradiation.
  - **WP6: Space-System Software Integration:** NASA Core Flight System (cFS), RTEMS real-time OS, and CCSDS Space Data Link Security (SDLS).
  - **WP7: System-Level Validation:** Hardware-in-the-Loop (HIL) CubeSat flat-sat testbed, link availability and MTTR benchmarking.

#### B. EXACTLY what I should speak
> "Turning to Slide 9, we outline our comprehensive research trajectory, structured into seven targeted work packages bridging our current ML-KEM-768 case study to full spacecraft flight qualification.
> 
> In **Work Package 1**, we will generalize our invariant monitoring framework to digital signatures—specifically NIST FIPS 204 ML-DSA-65—evaluating whether signature generation NTTs exhibit identical recovery dynamics.
> 
> In **Work Package 2**, we will transition from workstation x86/ARM platforms to embedded flight processors, specifically ARM Cortex-M4 and radiation-tolerant RISC-V cores like NOEL-V.
> 
> In **Work Package 3**, we will expand our fault injection models to include multi-bit upsets, burst radiation events, and compiler-level control-flow integrity tracking.
> 
> In **Work Package 4**, we will investigate hardware-software co-design, integrating our software invariants with on-chip Memory Protection Units and ROM-based twiddle table integrity checks.
> 
> In **Work Package 5**, we will move from software simulation to physical experimental validation, conducting laboratory electromagnetic fault injection and heavy-ion cyclotron radiation testing.
> 
> In **Work Package 6**, we will integrate the resilient cryptographic engine into flight software architectures—specifically the NASA Core Flight System (cFS), the RTEMS real-time operating system, and the CCSDS Space Data Link Security protocol.
> 
> And in **Work Package 7**, we will execute system-level validation on a Hardware-in-the-Loop CubeSat flat-sat testbed, measuring end-to-end telemetry link availability and Mean Time to Recovery.
> 
> Let us conclude with the core takeaways of this research."

#### C. Explain it to me
This slide transitions your project from a single-algorithm study into an expansive, multi-year academic research programme. It proves to faculty that you understand the entire flight development pipeline—from embedded targets (RISC-V/ARM) to space flight operating systems (NASA cFS/RTEMS) to physical beam testing. It answers their question: *"What is the long-term roadmap for this research?"*

#### D. Important numbers
- **7:** Structured Work Packages in the research roadmap (WP1 through WP7).
- **FIPS 204:** Target standard for ML-DSA signature extension.
- **CCSDS SDLS:** Consultative Committee for Space Data Systems Space Data Link Security standard.

#### E. Where to find evidence
- Complete research roadmap: [`research-roadmap.md`](file:///Users/dhairyajain/Desktop/pqc%20research/research-roadmap.md) (Sections WP1–WP7).
- Programme architecture: [`docs/architecture/RESEARCH_EVOLUTION.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/architecture/RESEARCH_EVOLUTION.md).
- Prior art integration: [`docs/state_of_art_gap_analysis.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/state_of_art_gap_analysis.md).

#### F. 3–5 likely faculty questions with concise answers
1. *Can your NTT invariants be directly applied to ML-DSA?*  
   **Answer:** "Yes. ML-DSA (Dilithium) relies on NTT polynomial multiplication over the ring $R_q$ with prime $q=8380417$. The Cooley-Tukey and Gentleman-Sande butterfly structures are mathematically identical, meaning our sum and difference invariants apply directly to ML-DSA's polynomial arithmetic."
2. *What is NASA Core Flight System (cFS)?*  
   **Answer:** "NASA cFS is an open-source, reusable flight software framework deployed on dozens of NASA missions. Integrating our monitored KEM as a cFS cryptographic application ensures direct compatibility with standard satellite flight architectures."
3. *Why is CCSDS SDLS relevant?*  
   **Answer:** "The Consultative Committee for Space Data Systems Space Data Link Security protocol governs frame-level encryption and authentication between satellites and ground stations. Integrating post-quantum key exchange into CCSDS frames is the target operational vehicle for this research."

---

### Slide 10: Conclusions and Research Trajectory

#### A. What is on this slide
- **Heading:** Conclusions and Research Trajectory
- **Summary of Completed Research:**
  - Established the research programme on PQC fault resilience for orbital space systems.
  - Implemented dual-transform NTT invariant monitoring across 9,856 operations in ML-KEM-768 decapsulation.
  - Demonstrated 100% transient fault recovery ($N=100$) and 100% persistent fail-stop containment ($N=200$).
  - Achieved **0 SDC across 750 active trials** ($95\%\text{ CI}\le0.49\%$) at **+16.9% decapsulation overhead** (vs +99.33% for DMR).
  - Formally proved Theorem 1 (twiddle blindness) and established circular verifier snapshot necessity.
- **The Research Trajectory:**
  - Level A (Space Resilience Programme) $\to$ Level B (ML-KEM-768 Proof of Concept) $\to$ Level C (Physical Testing & NASA cFS Integration).
- **Closing Statement:** Demonstrates that software-level algorithmic resilience provides an effective, low-overhead foundation for securing post-quantum satellite communications against space radiation hazards.

#### B. EXACTLY what I should speak
> "To conclude, on Slide 10:
> 
> As space systems transition to post-quantum cryptography, ensuring computational reliability under cosmic radiation is paramount.
> 
> In this research, we established the framework for **Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems**, presenting our initial implementation-level progress on NIST FIPS 203 ML-KEM-768.
> 
> By exploiting the algebraic symmetry of Number Theoretic Transforms, our framework monitors all 9,856 polynomial butterfly operations with zero modular divisions.
> 
> In cleanroom production testing, our localized register rollback recovered 100% of injected transient faults in-place, while persistent faults were cleanly contained via FIPS 203 implicit rejection.
> 
> Across 750 active fault trials in our canonical campaign, we observed **zero Silent Data Corruption events**, proving a 95% confidence upper bound of $\le 0.49\%$.
> 
> Crucially, our framework achieves this resilience with only a **+16.90% latency overhead** on full decapsulation, dramatically outperforming software Double Modular Redundancy, which incurs a +99.33% penalty.
> 
> Through adversarial auditing, we uncovered fundamental insights: we quantified the 98.5% failure rate of unshielded circular verifiers, proving the necessity of pre-computation snapshots, and mathematically formalized Theorem 1 regarding twiddle factor blindness.
> 
> With our 7-work-package roadmap established, this work demonstrates that lightweight, software-level algebraic monitoring provides an effective, high-reliability pathway for deploying post-quantum cryptography in spaceborne environments.
> 
> Thank you for your time and attention. I am now ready to take your questions."

#### C. Explain it to me
The final slide provides a strong, unified conclusion. It reiterates the three-level identity: permanent title, completed ML-KEM-768 case study, and 7-work-package future roadmap. It brings together all the strongest empirical metrics (+16.9% overhead, 0 SDC, 100% recovery) and closes on an academically defensible, forward-looking note.

#### D. Important numbers
- **9,856:** Operations monitored per decapsulation.
- **100%:** Transient recovery rate across 100 cleanroom trials.
- **0 SDC:** Observed across 750 active fault trials.
- **$\le 0.49\%$:** 95% Clopper-Pearson statistical confidence bound.
- **+16.90%:** Measured decapsulation overhead vs +99.33% for DMR.

#### E. Where to find evidence
- Concluding chapter: [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) (Section 7).
- Master project overview: [`PROJECT_OVERVIEW.md`](file:///Users/dhairyajain/Desktop/pqc%20research/PROJECT_OVERVIEW.md) (Section 8).
- Final presentation script: [`docs/presentation/AI_PPT_FINAL_CONTENT.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/AI_PPT_FINAL_CONTENT.md) (Slide 10).

#### F. 3–5 likely faculty questions with concise answers
1. *What is the single most important contribution of this work?*  
   **Answer:** "Demonstrating that sub-word algebraic invariants combined with localized register snapshotting can achieve near-zero SDC ($\le 0.49\%$) and 100% transient recovery in post-quantum key decapsulation at only +16.9% overhead, compared to +99.33% for dual modular redundancy."
2. *What is the next immediate step you will undertake?*  
   **Answer:** "The immediate next step is Work Package 2: deploying this C99 codebase onto an embedded ARM Cortex-M4 flight microcontroller and a NOEL-V RISC-V core to measure exact cycle counts and pipeline interactions in embedded hardware."
3. *If you could redesign one part of your implementation, what would it be?*  
   **Answer:** "I would integrate twiddle factor CRC integrity binding directly into the initial compiler pass rather than as a secondary v2 wrapper, providing hardware-assisted twiddle protection out of the box."

---

# PART 4 — TECHNICAL CONCEPTS DEEP-DIVE

### 4.1 ML-KEM-768 and Number Theoretic Transform (NTT)

#### Modulus, Ring Dimension, and Module Rank
ML-KEM (standardized under NIST FIPS 203) is a lattice-based Key Encapsulation Mechanism derived from the Module Learning with Errors (M-LWE) problem. In ML-KEM-768:
- **Ring Definition:** Operates over the quotient polynomial ring $R_q = \mathbb{Z}_q[X]/(X^{256} + 1)$.
- **Prime Modulus:** $q = 3329$. Note that $3329 \equiv 1 \pmod{256}$, specifically $3329 = 13 \times 256 + 1$. This property guarantees that the 256th primitive roots of unity exist in $\mathbb{Z}_q$, enabling the fast Number Theoretic Transform.
- **Module Dimension ($k$):** For Security Category 3 (ML-KEM-768), $k = 3$. Public keys, secret keys, and ciphertexts consist of vectors and matrices of polynomials of dimension $3\times3$ or $3\times1$.

#### The Number Theoretic Transform (NTT) Mechanics
Polynomial multiplication in $R_q$ would naively require schoolbook multiplication of $O(n^2) = 256^2 = 65{,}536$ operations. The NTT transforms polynomials into the frequency/evaluation domain where multiplication is performed coefficient-wise in $O(n)$ time.
- **Forward NTT (Cooley-Tukey):** Converts polynomials from normal order to bit-reversed NTT domain.
  - Decomposition: 7 layers (since $2^7 = 128$ pairs).
  - Each layer processes 64 blocks, with each block operating on 2 coefficients.
  - Total butterflies per forward NTT: $7 \times 64 = 448$ blocks $\times 2 = 896$ butterfly operations.
- **Inverse NTT (Gentleman-Sande):** Converts polynomials from NTT domain back to normal order.
  - Decomposition: 7 layers of inverse Gentleman-Sande butterflies.
  - Total butterflies per inverse NTT: $7 \times 64 = 448$ blocks $\times 2 = 896$ butterfly operations.

#### Exact Operation Count Breakdown During Decapsulation
The full ML-KEM-768 decapsulation routine (`crypto_kem_dec`) requires:
1. **Ciphertext vector conversion:** Vector $u$ has $k=3$ polynomials $\implies 3 \times 896 = 2{,}688$ forward CT butterflies.
2. **Message recovery:** Inner product $s^T \cdot u$ yields 1 polynomial inverted via inverse NTT $\implies 1 \times 896 = 896$ inverse GS butterflies.
3. **Re-encryption in Fujisaki-Okamoto transform:**
   - Vector $r$ has $k=3$ polynomials converted via forward NTT $\implies 3 \times 896 = 2{,}688$ forward CT butterflies.
   - Matrix-vector product $A \times r$ yields $k=3$ polynomials converted via inverse NTT $\implies 3 \times 896 = 2{,}688$ inverse GS butterflies.
   - Product $t^T \cdot r$ yields 1 polynomial converted via inverse NTT $\implies 1 \times 896 = 896$ inverse GS butterflies.

$$\text{Total Forward Cooley-Tukey Butterflies} = (3 + 3) \times 896 = 6 \times 896 = \mathbf{5{,}376}$$
$$\text{Total Inverse Gentleman-Sande Butterflies} = (1 + 3 + 1) \times 896 = 5 \times 896 = \mathbf{4{,}480}$$
$$\text{Grand Total Butterfly Operations Monitored} = 5{,}376 + 4{,}480 = \mathbf{9{,}856}$$

---

### 4.2 Mathematical Invariants & Verification Algebra

#### Cooley-Tukey Butterfly Algebra
Let $u$ and $v$ be input polynomial coefficients, and $\zeta$ be the twiddle factor (a power of the primitive root of unity modulo $q=3329$). In Cooley-Tukey:
$$u' \equiv u + \zeta \cdot v \pmod q$$
$$v' \equiv u - \zeta \cdot v \pmod q$$

#### Forward Invariant Derivation
Adding the two equations:
$$(u' + v') \equiv (u + \zeta v) + (u - \zeta v) \equiv 2u \pmod q$$
Subtracting the two equations:
$$(u' - v') \equiv (u + \zeta v) - (u - \zeta v) \equiv 2\zeta v \pmod q$$

Our monitor evaluates:
$$\Delta_{\text{sum}} = ((u' + v') \pmod q) - ((2u) \pmod q) \equiv 0 \pmod q$$
$$\Delta_{\text{diff}} = ((u' - v') \pmod q) - ((2\zeta v) \pmod q) \equiv 0 \pmod q$$
If $\Delta_{\text{sum}} \neq 0$ or $\Delta_{\text{diff}} \neq 0$, an arithmetic fault is declared.

#### Gentleman-Sande Butterfly Algebra
In the Gentleman-Sande inverse NTT:
$$u' \equiv u + v \pmod q$$
$$v' \equiv (u - v) \cdot \zeta \pmod q$$

Here, the additive rail is independent of $\zeta$:
$$(u') \equiv u + v \pmod q$$
The multiplier rail satisfies:
$$(v') \equiv (u - v) \cdot \zeta \pmod q$$
To verify $v'$ without costly modular division, the monitor evaluates:
$$(u - v) \cdot \zeta - v' \equiv 0 \pmod q$$
Both rails are verified independently using modular additions, subtractions, and multiplications, requiring zero modular divisions.

#### Register Snapshot Mechanics
Before executing the butterfly assembly instructions, the implementation stores:
$$u_{\text{saved}} \leftarrow u, \quad v_{\text{saved}} \leftarrow v$$
In `poly.c`, these snapshots are maintained in local CPU registers allocated by the compiler. If $\Delta_{\text{sum}} \neq 0$ or $\Delta_{\text{diff}} \neq 0$, the rollback routine restores:
$$u \leftarrow u_{\text{saved}}, \quad v \leftarrow v_{\text{saved}}$$
and re-executes the butterfly block.

#### Formal Invariant Blindness (Theorem 1)
**Theorem 1 (Twiddle Scalar Blindness):** *Let $u, v \in \mathbb{Z}_q$ be correct input operands. Let $\zeta \in \mathbb{Z}_q$ be a twiddle factor corrupted by fault $\delta_\zeta \neq 0$, such that $\tilde{\zeta} = \zeta + \delta_\zeta \pmod q$. If a Cooley-Tukey butterfly computes $\tilde{u}' \equiv u + \tilde{\zeta}v$ and $\tilde{v}' \equiv u - \tilde{\zeta}v$, then the sum invariant $( \tilde{u}' + \tilde{v}' ) \equiv 2u \pmod q$ holds unconditionally.*

*Proof:*
$$\tilde{u}' + \tilde{v}' = (u + \tilde{\zeta}v) + (u - \tilde{\zeta}v) = 2u + (\tilde{\zeta} - \tilde{\zeta})v = 2u \pmod q$$
Thus, the sum invariant is blind to any perturbation $\delta_\zeta$. If the verifier evaluates the difference invariant using the corrupted in-register twiddle factor $\tilde{\zeta}$, it computes $2\tilde{\zeta}v$, matching $\tilde{u}' - \tilde{v}'$, causing a total verification false pass.
*Resolution:* Implemented in `tfib_ref.c`, binding $\zeta$ to an immutable reference table `tfib_zetas_ref[128]`.

---

### 4.3 Fault Models & Physical Radiation Mapping

| Fault Parameter | Software Simulation Model | Physical Space Radiation Correlate | Real-World Phenomenon |
|---|---|---|---|
| **Single-Event Upset (SEU)** | Single-bit XOR bit-flip (`reg ^= (1 << bit)`) | Cosmic ray heavy-ion or proton striking CMOS SRAM cell or register flip-flop | Depletes charge across silicon gate, toggles bit state ($0 \to 1$ or $1 \to 0$). |
| **Single-Event Transient (SET)** | Operand perturbation injected for exactly 1 butterfly execution | Ionizing strike on combinational logic net (e.g., ALU adder/multiplier carry chain) | Generates transient voltage pulse latched into destination register on clock edge. |
| **Multi-Bit Upset (MBU)** | Multi-bit mask perturbation (`reg ^= mask`) | Dense heavy-ion track traversing adjacent silicon memory cells | Flips multiple adjacent bits within a single register or cache word. |
| **Persistent Stuck-At Reg** | Fixed register mask forced across all retries | Total Ionizing Dose (TID) gate rupture or latchup | Physical transistor oxide breakdown; register pinned high or low permanently. |
| **Persistent Stuck-At Mem** | Memory address value pinned across all reads | SRAM physical cell degradation or radiation latchup | Memory location fails to refresh; always returns corrupted value. |
| **Control-Flow Hijack** | Simulated instruction skip / branch displacement | High-energy strike on instruction decoder or program counter | CPU skips instruction, jumps to incorrect subroutine, or bypasses checks. |

#### Distinguishing Failure Outcomes
- **Silent Data Corruption (SDC):** The decapsulation routine finishes with return code `0` (success), but computes an incorrect shared secret $K' \neq K$. Neither the satellite nor ground station detects the error. **This is the most critical failure mode in space.**
- **Crash / Panic:** Processor traps on an illegal instruction, segmentation fault, or unhandled exception, triggering a flight computer reset.
- **Contained Fail-Stop:** The monitor detects an unrecoverable fault, suppresses corrupted outputs, forces $K' \leftarrow K_{\text{rej}}$ via FIPS 203 implicit rejection, and cleanly increments telemetry fault counters without crashing.

---

### 4.4 Localized Recovery & Multi-Stage Containment Architecture

The fault-containment framework operates through a rigorous hierarchical escalation pipeline:

```
[ Incoming Decapsulation Call ]
             │
             ▼
[ Butterfly Processing Loop ] (9,856 operations)
  ├── 1. Snapshot: u_saved = u, v_saved = v, retry_count = 0
  ├── 2. Execute Butterfly: u', v' = Butterfly(u, v, zeta)
  ├── 3. Invariant Evaluation: Δ_sum, Δ_diff
  │        ├── If Δ == 0: Proceed to Next Butterfly
  │        └── If Δ != 0: FAULT DETECTED!
  │                 │
  │                 ├── Check: retry_count < 2 ?
  │                 │     ├── YES (Transient Fault):
  │                 │     │     ├── u = u_saved, v = v_saved
  │                 │     │     ├── retry_count++
  │                 │     │     └── Re-execute Butterfly (LOCALIZED ROLLBACK)
  │                 │     │
  │                 │     └── NO (Persistent Fault: retry_count >= 2):
  │                 │           ├── Increment persistent_fail_counter++
  │                 │           └── ESCALATE TO GLOBAL FAIL-STOP
  │
  ▼
[ Outer KEM Decapsulation Check ] (kem.c)
  ├── Check: persistent_fail_counter == 0 ?
  │     ├── YES: Execute standard FO re-encryption & return shared secret K
  │     └── NO:  Force `fail = 0xFF`
  │                 │
  │                 ▼
  │           [ FIPS 203 Implicit Rejection ]
  │           Output pseudorandom rejection key K_rej = SHAKE256(z || ciphertext)
  │           [ ZERO SDC OCCURRED | ZERO PROCESSOR CRASHES ]
```

---

### 4.5 Performance Disambiguation & Statistical Rigor

During defense, faculty may probe timing comparisons. You must maintain clear disambiguation between three distinct benchmark measurements:

#### The Three Disambiguated Benchmarks
1. **Full End-to-End Monitored Decapsulation Benchmark:**
   - *Scope:* Complete `crypto_kem_dec` execution including 11 monitored NTTs (9,856 butterflies), hashing, and FO re-encryption.
   - *Baseline:* $110.77\,\mu\text{s}$.
   - *Monitored:* $129.51\,\mu\text{s}$.
   - *Overhead:* **+16.90%**.
   - *Setup:* Apple M3 Pro, Apple Clang 17, `-O3`, $N=2{,}000$ iterations (`results/phase7i/`).
2. **Isolated Sequential Software DMR Benchmark:**
   - *Scope:* Isolated single polynomial NTT transform executed twice sequentially with full coefficient array comparison.
   - *Baseline NTT:* $46.65\,\mu\text{s}$.
   - *Sequential DMR NTT:* $92.98\,\mu\text{s}$.
   - *Overhead:* **+99.33%**.
   - *Setup:* Identical platform, $N=2{,}000$ iterations (`results/phase7h/processed/phase7h_timing_distribution.json`).
3. **Isolated Monitored NTT Benchmark:**
   - *Scope:* Single polynomial NTT with dual-transform monitoring hooks vs single unmonitored NTT.
   - *Baseline NTT:* $68.47\,\mu\text{s}$.
   - *Monitored NTT:* $80.30\,\mu\text{s}$.
   - *Overhead:* **+17.27%**.
   - *Setup:* Measured within Phase 7I instrumentation suite (`results/phase7i/processed/phase7i_e2e_results.json`).

*Analytical Extrapolation Note:* Full decapsulation DMR ($>+100\%$) is an analytical extrapolation derived from the isolated DMR cost, not a separate measured benchmark. Always state this explicitly.

#### Statistical Confidence Bounds (Wilson & Clopper-Pearson)
When zero failures ($k=0$) are observed across $N$ trials, you cannot claim a $0\%$ failure probability. You must cite exact statistical upper bounds:
- **Rule of Three Approximation:** $P_{95\%} \approx \frac{3}{N}$.
- **Clopper-Pearson Exact 95% Confidence Interval:**
  - For $N=300$ production trials ($k=0$):
    $$\text{Upper Bound} = 1 - (0.05)^{1/300} = 1 - 0.98744 = 0.01256 \implies \mathbf{\le 1.26\%}$$
  - For $N=750$ canonical campaign trials ($k=0$):
    $$\text{Upper Bound} = 1 - (0.05)^{1/750} = 1 - 0.99507 = 0.00493 \implies \mathbf{\le 0.49\%}$$

#### 18 KAT Vectors vs FIPS Certification
Passing all 18 NIST Known Answer Test vectors in `./bin/test_fips_kats` proves that the cryptographic implementation conforms to published test vectors for ML-KEM and ML-DSA. It validates algorithmic correctness. It **does NOT constitute formal NIST CMVP FIPS 140-3 module validation or hardware space qualification**, which requires independent accredited laboratory testing.

---

# PART 5 — FACULTY Q&A PREPARATION & DEFENSE CHALLENGES

### 5.1 Core Defense Questions & Defensible Answers (Q1–Q25)

#### Category 1: Space Systems Relevance
1. **Q1: Why is space radiation a problem for cryptographic software if processors have hardware ECC?**  
   *Spoken Answer (30s):* "Hardware ECC protects static SRAM arrays and main memory bus transfers, but it rarely protects CPU internal execution registers, arithmetic pipelines, and accumulators where butterfly operations execute. An ionizing particle striking an ALU register during multiplication creates a Single-Event Upset that hardware memory ECC cannot detect. Software-level monitoring is required to safeguard active computation."
2. **Q2: Why not just use radiation-hardened processors that do not suffer SEUs?**  
   *Spoken Answer (30s):* "Radiation-hardened processors like the RAD750 operate at low clock frequencies (e.g., 133 MHz), cost hundreds of thousands of dollars, and lack the compute power needed for modern high-bandwidth payloads. Modern CubeSats, mega-constellations, and Earth-observation satellites increasingly fly Commercial Off-The-Shelf (COTS) processors to meet throughput demands. Software-level resilience enables secure post-quantum deployment on COTS hardware."
3. **Q3: What happens to a satellite if an SDC occurs during key exchange?**  
   *Spoken Answer (30s):* "If Silent Data Corruption occurs, the ground station derives session key $K$ while the satellite computes $K'$. Neither side realizes the error. When the ground station transmits encrypted telecommands, the satellite fails to decrypt them and drops the packets. This creates an unrecoverable communication blackout until manual ground intervention or watchdog timeout occurs."

#### Category 2: Fault Models & Mechanisms
4. **Q4: What specific fault model did you implement in your software harness?**  
   *Spoken Answer (30s):* "We implemented register-level Single-Event Upset (SEU) bit-flips, transient Single-Event Transients (SETs) active for a single butterfly, persistent register stuck-at-1 faults, and persistent memory stuck-at faults. Injections targeted intermediate butterfly inputs, outputs, and twiddle indices across compiled production binaries."
5. **Q5: Can your framework handle multi-bit upsets (MBUs)?**  
   *Spoken Answer (30s):* "Yes. Our algebraic invariants evaluate modular arithmetic congruences $((u'+v') \equiv 2u \pmod q)$, not Hamming weights or single parity bits. Any arbitrary bit perturbation—whether 1 bit or 12 bits—that alters the numerical value modulo $q$ is detected with equal mathematical probability."
6. **Q6: How does your fault injection compare to physical particle strikes?**  
   *Spoken Answer (30s):* "Our software harness models the logical consequence of a particle strike: an altered bit in a processor register. However, it does not simulate physical charge transport, analog pulse widths, or multi-cell physical cluster damage. That physical validation represents Work Package 5 in our research roadmap."

#### Category 3: Mathematical Invariants
7. **Q7: Explain the Cooley-Tukey invariant in simple terms.**  
   *Spoken Answer (30s):* "The butterfly computes $u' = u + \zeta v$ and $v' = u - \zeta v$. Adding both outputs cancels the $\zeta v$ term, yielding $2u$. Subtracting them cancels $u$, yielding $2\zeta v$. By checking if $u'+v' \equiv 2u$ and $u'-v' \equiv 2\zeta v \pmod q$, we verify correctness with two additions and one multiplication, completely avoiding costly modular divisions."
8. **Q8: Why does the invariant require zero modular divisions?**  
   *Spoken Answer (30s):* "Modular division requires computing modular inverses, costing hundreds of clock cycles via Fermat's Little Theorem. By multiplying the inputs by $2$ and $2\zeta$ instead of dividing outputs, our invariant checks rely strictly on fast modular additions and multiplications."
9. **Q9: What is Theorem 1 (Twiddle Scalar Blindness)?**  
   *Spoken Answer (30s):* "Theorem 1 proves that because the sum invariant $(u'+v') \equiv 2u \pmod q$ cancels out the twiddle factor $\zeta$, any corruption residing strictly within $\zeta$ preserves the sum equality. If the difference check evaluates using that same corrupted $\zeta$, it falsely passes. We discovered this limitation through adversarial analysis and solved it in v2 via Reference Twiddle Binding."

#### Category 4: Rollback, Recovery, and Containment
10. **Q10: How does localized register rollback work without crashing the stack?**  
    *Spoken Answer (30s):* "Before arithmetic begins, the C code preserves $u$ and $v$ into local compiler-allocated registers. If an invariant check fails, the handler immediately restores those registers and loops back to re-execute the butterfly. Because this occurs inside the butterfly block, it requires no stack unwinding, no setjmp/longjmp, and no heap allocation."
11. **Q11: Why is the retry limit set to $R_{max}=2$?**  
    *Spoken Answer (30s):* "Transient Single-Event Transients resolve within 1–2 clock cycles. If an error persists after two retries, it indicates a permanent hardware stuck-at fault or damaged cell. Retrying indefinitely would hang the flight software. Capping retries at 2 bounds latency and guarantees deterministic escalation."
12. **Q12: What is the fail-stop mechanism and how does it prevent SDC?**  
    *Spoken Answer (30s):* "When retries exceed 2, a persistent error counter is incremented. The outer `crypto_kem_dec` wrapper detects this counter, overrides the output flag to failure (`fail = 0xFF`), and outputs the FIPS 203 implicit rejection key $K_{rej}$. This prevents corrupted keys from escaping into telemetry."

#### Category 5: Performance & Benchmarking
13. **Q13: Why is your overhead only +16.9% while DMR is +99.33%?**  
    *Spoken Answer (30s):* "Double Modular Redundancy executes every transform twice and compares every coefficient, essentially doubling execution time. Our invariant checks use lightweight arithmetic identities directly on CPU registers, executing in just a few clock cycles per butterfly. Amortized across decapsulation, it requires only +16.9% overhead."
14. **Q14: Where does the difference between +16.9% and +17.27% come from?**  
    *Spoken Answer (30s):* "+17.27% is the latency overhead on an isolated NTT transform in the Phase 7I benchmark. +16.90% is the overhead on full decapsulation (`crypto_kem_dec`), where non-NTT operations like hashing and FO re-encryption dilute the total proportional overhead."
15. **Q15: What hardware and compiler settings generated the +16.9% benchmark?**  
    *Spoken Answer (30s):* "The benchmark was conducted on an Apple M3 Pro processor using Apple Clang version 17 under `-O3` optimization across 2,000 decapsulation iterations, recorded in `results/phase7i/processed/phase7i_e2e_results.json`."

#### Category 6: Cryptographic Security & Side-Channels
16. **Q16: Does localized rollback introduce timing side-channel vulnerabilities?**  
    *Spoken Answer (30s):* "In normal execution without faults, the retry loop never fires, executing in strict constant time. When a transient radiation strike occurs, a retry takes a few extra clock cycles. However, radiation strikes are stochastic cosmic events, not attacker-controlled inputs. Furthermore, our persistent fail-stop uses constant-time conditional copies (`cmov`) to derive $K_{rej}$, maintaining FIPS 203 side-channel resistance."
17. **Q17: Does your monitor change the ciphertext or private key format?**  
    *Spoken Answer (30s):* "No. The public keys, secret keys, ciphertexts, and shared secrets remain 100% bit-compatible with NIST FIPS 203. The monitoring hooks operate entirely internally on intermediate arithmetic variables."
18. **Q18: What is FIPS 203 implicit rejection?**  
    *Spoken Answer (30s):* "In FIPS 203, if ciphertext re-encryption does not match the input ciphertext, the decapsulation does not return an error code; instead, it deterministically computes a pseudorandom key $K_{rej} = \text{SHAKE256}(z \parallel c)$. We harness this exact mechanism during persistent fail-stop to prevent information leakage."

#### Category 7: Limitations & Future Work
19. **Q19: What did the Phase 16 circular verifier audit reveal?**  
    *Spoken Answer (30s):* "It revealed that verifiers reading mutated live registers instead of saved snapshots failed to detect faults in 591 out of 600 trials (a 98.5% failure rate) because the verification check evaluated using the mutated state. This proved that independent register snapshotting is mandatory."
20. **Q20: Can your invariants detect instruction skips or corrupted program counters?**  
    *Spoken Answer (30s):* "No. Our invariants detect arithmetic operand corruption. If a particle strike causes an instruction skip that jumps over the monitor entirely, arithmetic invariants cannot catch it. That requires Control-Flow Integrity (CFI) techniques, which we outline in Work Package 3."
21. **Q21: How will you extend this work to ML-DSA?**  
    *Spoken Answer (30s):* "ML-DSA (FIPS 204) uses NTT polynomial multiplication over the ring $\mathbb{Z}_q[X]/(X^{256}+1)$ with modulus $q=8380417$. Because the butterfly arithmetic is structurally identical, our sum and difference invariants apply directly. This is the focus of Work Package 1."
22. **Q22: What flight software architectures will you integrate with?**  
    *Spoken Answer (30s):* "Work Package 6 targets integration into the NASA Core Flight System (cFS) and RTEMS real-time operating system, embedding the monitored cryptographic library into the CCSDS Space Data Link Security layer."
23. **Q23: How will you physically validate these findings?**  
    *Spoken Answer (30s):* "Work Package 5 specifies laboratory electromagnetic fault injection (EMFI) and proton/heavy-ion beam irradiation at an accredited cyclotron facility (such as Texas A&M) using embedded RISC-V development boards."
24. **Q24: What is the difference between Known Answer Tests (KATs) and FIPS certification?**  
    *Spoken Answer (30s):* "Passing all 18 KAT vectors confirms that our C99 code correctly implements the published NIST mathematical transformations. Formal FIPS 140-3 certification requires independent laboratory evaluation of physical security, key management, and entropy sources under the NIST Cryptographic Module Validation Program."
25. **Q25: Why is your framework superior to running ML-KEM inside a hypervisor?**  
    *Spoken Answer (30s):* "A hypervisor introduces massive context-switching overhead, complex kernel footprints, and high memory requirements unacceptable on resource-constrained CubeSat microcontrollers. Our C99 framework has zero heap allocation and adds only +16.9% latency directly in user-space code."

---

### 5.2 If Faculty Challenge My Results (Hostile/Skeptical Challenges)

#### Challenge 1: "You observed 0 SDC, but you only tested hundreds of trials. Isn't claiming zero SDC unscientific?"
> **Your Defense:**  
> "You are entirely correct that empirical sampling cannot mathematically prove a zero failure probability. In our manuscript and presentation, we explicitly avoid claiming an absolute zero probability. Instead, we report that across 300 audited production trials, exactly zero SDC events were observed, which establishes a formal 95% Clopper-Pearson exact confidence interval upper bound of **$\le 1.26\%$**. In our 900-trial canonical campaign across 750 active fault trials, zero SDC establishes an upper bound of **$\le 0.49\%$**. We report these exact statistical upper bounds rather than asserting impossible zero-risk claims."

#### Challenge 2: "This is purely software fault injection on an Apple M3 laptop. How can you claim this applies to space systems?"
> **Your Defense:**  
> "We must be very precise about our research positioning: our permanent research title defines the space-systems problem space, while the work presented today represents Level B—our initial algorithmic and software-level case study. High-energy ionizing particles in space manifest in digital CMOS as Single-Event Upsets (register bit-flips) and Single-Event Transients. Software register-level fault injection is the standard, accepted first phase in aerospace fault-tolerance research before committing thousands of dollars to physical cyclotron beam time. Work Package 5 in our roadmap explicitly defines the transition to physical electromagnetic and proton beam testing."

#### Challenge 3: "Your invariants have a known blind spot: Theorem 1 proves twiddle factors can be corrupted without detection. Doesn't that invalidate your approach?"
> **Your Defense:**  
> "On the contrary, discovering, proving, and documenting Theorem 1 demonstrates the academic rigor of our research. Rather than ignoring this limitation, we conducted an adversarial self-audit, proved Theorem 1 mathematically, and measured it in our Phase 15Q pilot. Furthermore, in our hardened v2 implementation (`tfib_ref.c`), we solved this exact gap by implementing Twiddle Factor Integrity Binding against an immutable reference table. By identifying where input-output invariants reach their theoretical boundary, we established exactly what hardware or reference structures are required to achieve complete coverage."

#### Challenge 4: "You claim +16.9% overhead, but is that comparing apples to oranges against DMR?"
> **Your Defense:**  
> "We are scrupulous about maintaining exact benchmark disambiguation. The +16.90% overhead was measured on full end-to-end decapsulation (`crypto_kem_dec`) across 2,000 iterations under `-O3`. The +99.33% overhead was measured directly on isolated NTT transforms executing sequential software DMR under identical hardware, compiler, and iteration conditions. DMR virtually doubles the execution time (+99.33%) because it must execute the transform twice. Our invariant check verifies the transform in a single pass using register-level identities, which is why the full decapsulation overhead is restricted to +16.9%."

#### Challenge 5: "Your test suite passes 18 KAT vectors, but can you really claim FIPS compliance?"
> **Your Defense:**  
> "We explicitly describe our result as Known Answer Test (KAT) vector conformance, not full FIPS certification. Passing all 18 vectors in `./bin/test_fips_kats` verifies that our baseline and monitored C99 code produce byte-for-byte identical ciphertexts and shared secrets to the published NIST standard. We do not claim NIST CMVP FIPS 140-3 certification, which involves physical security and cryptographic boundary audits that are outside the scope of an algorithmic research project."

---

# PART 6 — LAST-MINUTE PRESENTATION CHEAT SHEET

### 6.1 One-Minute Memorizable Introduction

*(Memorize this word-for-word. Deliver it with calm confidence while looking directly at the faculty panel.)*

> "Good morning, respected committee members.
> 
> Today, I am presenting our research titled:
> **'Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems.'**
> 
> As long-lived satellite missions transition to post-quantum cryptography to secure their communications against future quantum computers, they face an immediate physical threat: cosmic radiation. Energetic particles in orbit induce computational bit-flips in flight processors, which can silently corrupt cryptographic keys or cause mission-ending communication blackouts.
> 
> In this presentation, I will establish our broader space-systems research programme, present our completed software-level implementation progress on NIST FIPS 203 ML-KEM-768 decapsulation, analyze our empirical fault-injection findings and discovered limitations, and map out our remaining roadmap toward spacecraft flight integration.
> 
> Thank you. Let us begin."

---

### 6.2 Five-Minute Complete Presentation Summary

*(Use this if the committee chair says: "You have 5 minutes to summarize your entire presentation.")*

- **Minute 1 (Problem):** "Satellite missions launched today operate for 10 to 25 years in unshielded space radiation environments. They must adopt Post-Quantum Cryptography immediately to prevent adversaries from harvesting encrypted downlinks today and decrypting them later. However, space radiation causes Single-Event Upsets in commercial microprocessors. If a bit flips during key decapsulation, it either causes Silent Data Corruption—severing satellite communication—or triggers an unhandled processor reset. Existing defenses like hardware TMR or software DMR either exceed satellite SWaP constraints or double execution latency (+99.33%)."
- **Minute 2 (Solution):** "To solve this, we developed a software-level fault resilience framework for ML-KEM-768 decapsulation. By exploiting the algebraic symmetry of Number Theoretic Transforms, our framework actively monitors all 9,856 butterfly operations with zero modular divisions. Before arithmetic begins, it takes a clean register snapshot. Upon detecting a transient fault, it restores the snapshot and retries locally up to twice. If a fault persists, it triggers an algebraic fail-stop, delegating to FIPS 203 implicit rejection to return a safe rejection key, avoiding both SDC and system crashes."
- **Minute 3 (Results):** "We evaluated this in a 400-trial cleanroom production audit on compiled C99 binaries. The system achieved 100% transient fault recovery across 100 trials, 100% persistent fail-stop containment across 200 trials, and exactly 0 Silent Data Corruption events ($95\%\text{ CI}\le1.26\%$). In our 900-trial canonical campaign across 750 active faults, zero SDC established an upper bound of $\le 0.49\%$. High-precision benchmarking confirmed that monitored decapsulation incurs only a +16.9% latency overhead under `-O3`, compared to +99.33% for DMR."
- **Minute 4 (Limitations):** "Through adversarial self-audits, we uncovered two critical scientific insights: first, runtime verifiers inspecting live mutated registers suffer a 98.5% failure rate due to circular dependency, proving register snapshotting is mandatory. Second, we proved Theorem 1: operand invariants exhibit twiddle scalar blindness if mutations occur strictly within twiddle tables, which we resolved in v2 via Reference Twiddle Binding."
- **Minute 5 (Roadmap & Conclusion):** "Our research programme is structured into 7 clear work packages—expanding from ML-KEM-768 to ML-DSA signatures, porting to spaceborne RISC-V and ARM cores, conducting cyclotron heavy-ion beam testing, and integrating into the NASA Core Flight System. In conclusion, software-level algebraic monitoring provides an effective, high-reliability pathway for securing post-quantum communications in space."

---

### 6.3 Essential Metrics Reference Table

Keep this exact table in mind for any numeric question:

| Metric Name | Authoritative Value | Statistical Bound (95% CI) | Source Benchmark / Evidence File |
|---|:---:|:---:|---|
| **Full Decapsulation Overhead** | **+16.90%** | $N=2{,}000$ iterations | Phase 7I stdout logs & Table 2 of `paper/manuscript.md` |
| **Isolated NTT DMR Overhead** | **+99.33%** | $N=2{,}000$ iterations | `results/phase7h/processed/phase7h_timing_distribution.json` |
| **Isolated Monitored NTT Overhead**| **+17.27%** | $N=2{,}000$ iterations | `results/phase7i/processed/phase7i_e2e_results.json` |
| **Total Butterfly Operations** | **9,856** | Exact Count | $5{,}376$ Forward CT + $4{,}480$ Inverse GS (`src/poly.c`) |
| **Forward CT Butterflies** | **5,376** | Exact Count | $6 \text{ NTTs} \times 896 \text{ butterflies/NTT}$ |
| **Inverse GS Butterflies** | **4,480** | Exact Count | $5 \text{ invNTTs} \times 896 \text{ butterflies/invNTT}$ |
| **Cleanroom Trial SDC Count** | **0 / 300 active** | $\le 1.26\%$ (Clopper-Pearson) | `phase18_audit/raw_production_trials.csv` |
| **Canonical Campaign SDC Count** | **0 / 750 active** | $\le 0.49\%$ (Clopper-Pearson) | `tfib_trial_level_results.csv` |
| **Cleanroom Transient Recovery** | **100 / 100 (100%)** | Exact Count | Suite `F4_TRANSIENT_RECOVERY` in Phase 18 audit |
| **Cleanroom Persistent Fail-Stop** | **200 / 200 (100%)** | Exact Count | Suites `F5A_STUCK_AT_REG` & `F5B_STUCK_AT_MEM` |
| **Clean Baseline Success Rate** | **100 / 100 (100%)** | 0 False Alarms | Suite `CLEAN_BASELINE` in Phase 18 audit |
| **Circular Verifier False-Pass Rate**| **591 / 600 (98.5%)** | Measured Failure Rate | `phase16_targeted_evidence_closure/h1_activation_audit.csv` |
| **NIST Known Answer Tests (KAT)** | **18 / 18 Passing** | 100% Vector Match | `./bin/test_fips_kats` (ML-KEM-512/768/1024, ML-DSA-44/65/87) |
| **Max Retry Threshold ($R_{max}$)**| **2 Retries** | Configured Limit | `algorithms/source_ref/mlkem_fault_hooks.h` |
| **Modular Divisions Used** | **0 Divisions** | Exact Count | Invariant verification algebra uses additions/multiplications |

---

### 6.4 Technical Glossary

- **NTT (Number Theoretic Transform):** A specialized discrete Fourier transform over finite fields $\mathbb{Z}_q$, accelerating polynomial multiplication from $O(n^2)$ to $O(n \log n)$.
- **Cooley-Tukey (CT) Butterfly:** Forward NTT arithmetic unit computing $u' = u + \zeta v$ and $v' = u - \zeta v \pmod q$.
- **Gentleman-Sande (GS) Butterfly:** Inverse NTT arithmetic unit computing $u' = u + v$ and $v' = (u - v)\zeta \pmod q$.
- **Twiddle Factor ($\zeta$):** Powers of primitive roots of unity modulo $q=3329$ used as multiplication constants in NTT butterflies.
- **Algebraic Invariant:** A mathematical equality that holds true for correct arithmetic outputs regardless of input values, used to detect computational errors without re-executing full routines.
- **Localized Rollback:** Restoring corrupted CPU registers to clean pre-computation snapshots and re-executing the local butterfly block without unwinding the stack.
- **Silent Data Corruption (SDC):** An undetected computational error producing an invalid cryptographic key without raising an error flag or exception.
- **Single-Event Upset (SEU):** A radiation-induced bit-flip in a memory cell, latch, or CPU register.
- **Single-Event Transient (SET):** A transient ionizing voltage spike in combinational logic latched into a register on a clock edge.
- **Fujisaki-Okamoto (FO) Transform:** Cryptographic conversion turning an IND-CPA public-key encryption scheme into an IND-CCA2 Key Encapsulation Mechanism by re-encrypting the plaintext.
- **Implicit Rejection:** Returning a deterministic pseudorandom value ($K_{rej}$) rather than a failure code upon decapsulation error, preventing side-channel leakage.
- **Known Answer Test (KAT):** Published deterministic test vectors used to verify cryptographic implementation conformance.
- **FDIR (Fault Detection, Isolation, and Recovery):** Spacecraft systems engineering protocol for autonomous onboard fault management.
- **DMR (Double Modular Redundancy):** Executing computation twice and comparing outputs to detect errors, incurring ~100% overhead.

---

### 6.5 Top 10 Files & Top 5 Directories to Open

If the faculty panel asks you to open the codebase and show evidence during the presentation, immediately navigate to these exact locations:

#### Top 5 Directories to Open
1. [`algorithms/source_ref/`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/): Core cryptographic implementation and invariant hooks.
2. [`phase18_audit/`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/): Cleanroom production reproducer and 400-trial audited dataset.
3. [`tfib_implementation/`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/): Hardened v2 twiddle reference binding code.
4. [`paper/`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/): Academic manuscript, tables, and formal citations.
5. [`bin/`](file:///Users/dhairyajain/Desktop/pqc%20research/bin/): Compiled executable verification binaries.

#### Top 10 Files to Open
1. **Forward Butterfly Integration:** [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L375-L425)  
   *Show Lines 375–425:* Demonstrates `mlk_ntt_butterfly_block`, operand snapshots (`u_saved, v_saved`), and monitor hooks.
2. **Invariant & Rollback Logic:** [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L600-L665)  
   *Show Lines 600–665:* Demonstrates `native_ntt_monitor_butterfly`, sum/diff invariant evaluation, and register rollback.
3. **Decoupled Inverse Monitor:** [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L804-L874)  
   *Show Lines 804–874:* Demonstrates `native_invntt_monitor_butterfly` division-free decoupled checks.
4. **Fail-Stop Containment in KEM:** [`algorithms/source_ref/mlkem/src/kem.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c#L484-L520)  
   *Show Lines 484–520:* Demonstrates `crypto_kem_dec` intercepting persistent error counters and forcing FIPS 203 implicit rejection.
5. **Cleanroom 400 Trial Dataset:** [`phase18_audit/raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv)  
   *Show CSV header & rows:* Proves 100 clean, 100 recovered, 200 fail-stop, and 0 SDC trials.
6. **Hardened Twiddle Reference Table:** [`tfib_implementation/tfib_ref.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_ref.c#L18-L45)  
   *Show Lines 18–45:* Demonstrates `tfib_zetas_ref[128]` closing Theorem 1 twiddle factor blindness.
7. **Canonical 900 Trial Results:** [`tfib_trial_level_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_trial_level_results.csv)  
   *Show trial ledger:* Proves 0 SDC across 750 active fault trials in the canonical campaign.
8. **Circular Verifier Audit Data:** [`phase16_targeted_evidence_closure/h1_activation_audit.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/h1_activation_audit.csv)  
   *Show 591 false passes:* Proves why naive unshielded verifiers fail (98.5% blindness) and why snapshotting is mandatory.
9. **Research Manuscript:** [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md)  
   *Show Table 1 & Table 2:* Demonstrates formal academic write-up, mathematical theorems, and benchmark tables.
10. **FIPS KAT Runner Binary:** Run `./bin/test_fips_kats` in terminal.  
    *Show output:* Proves 18/18 passing Known Answer Tests in real time.

---

### 6.6 What I Must NEVER Claim (Safety Boundaries)

To protect yourself from severe academic challenge, **NEVER make any of the following unsupported claims**:

1. **NEVER claim you conducted physical space radiation testing.**  
   *What to say instead:* "Our experiments were conducted via register-level software fault injection simulating Single-Event Upsets. Physical cyclotron beam testing represents Work Package 5 in our research roadmap."
2. **NEVER claim your implementation is flight-qualified or space-certified.**  
   *What to say instead:* "This research establishes the algorithmic fault-resilience foundation. Full spacecraft flight qualification requires integration with flight operating systems (such as NASA cFS) and hardware environmental testing."
3. **NEVER claim a mathematical proof of 0% SDC probability.**  
   *What to say instead:* "We observed 0 SDC events across 750 active fault trials, which establishes a rigorous 95% Clopper-Pearson statistical confidence upper bound of $\le 0.49\%$."
4. **NEVER claim formal NIST FIPS 140-3 certification.**  
   *What to say instead:* "Our implementation conforms to all 18 NIST Known Answer Test vectors, verifying algorithmic mathematical correctness. Formal FIPS 140-3 module certification is a separate laboratory validation process."
5. **NEVER claim that your invariants achieve 100% universal fault detection across all processor components.**  
   *What to say instead:* "Our invariants monitor polynomial arithmetic within NTT butterfly operations. They do not protect against instruction skips, program counter corruption, or memory outside the polynomial datapath, which require complementary control-flow integrity mechanisms."
6. **NEVER claim that DMR was benchmarked end-to-end on full decapsulation.**  
   *What to say instead:* "DMR was benchmarked directly on isolated NTT transforms (+99.33% overhead). Conceptual DMR on full decapsulation is an analytical projection, whereas our +16.9% overhead is an empirical end-to-end measurement."
7. **NEVER rename the research programme to ML-KEM-768.**  
   *What to say instead:* "Our permanent research title is **Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems**. ML-KEM-768 is our initial implementation case study within that broader programme."

---

*End of Research Presentation Handbook — Prepared for Academic Progress Presentation & Defense.*

