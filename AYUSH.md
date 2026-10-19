# AYUSH.md: Complete Research Handover, Technical Handbook & Architecture Manual

**Project Title:** Software-Level Fault Resilience for ML-KEM-768: Dual-Transform NTT Invariant Monitoring, Localized Register Rollback, and Containment  
**Active Git Branch:** `space-resilience-framework`  
**Current HEAD Commit:** `4a2c4eb` (4 commits ahead of `origin/space-resilience-framework`)  
**Repository Remote:** `https://github.com/dhairyajain/pqc-research.git`  
**Author / Handover From:** Dhairya Jain  
**Handover To:** Ayush  
**Date of Handover:** October 19, 2026  
**Primary Working Manuscript:** [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) (SHA-256: `bb6d138a463347153385c69a6e7f2bf133708cdb8738ba66a325e420d58e0b4d`)  
**Manuscript Verdict:** **READY WITH EXPLICIT LIMITATIONS** (Phase 2S Final Audit)

---

## Table of Contents
1. [Welcome and Handover Purpose](#1-welcome-and-handover-purpose)
2. [Executive Summary](#2-executive-summary)
3. [The Final Research Goal](#3-the-final-research-goal)
4. [Research Questions and Hypotheses](#4-research-questions-and-hypotheses)
5. [What We Have Achieved](#5-what-we-have-achieved)
6. [Current Repository State](#6-current-repository-state)
7. [Research History & Phase-by-Phase Timeline](#7-research-history--phase-by-phase-timeline)
8. [Repository Directory Map](#8-repository-directory-map)
9. [Source-Code Architecture](#9-source-code-architecture)
10. [Code-Level File Index](#10-code-level-file-index)
11. [Mathematical Foundation & Invariant Derivations](#11-mathematical-foundation--invariant-derivations)
12. [Fault Models & Experiment Design](#12-fault-models--experiment-design)
13. [Dataset & Result Provenance Registry](#13-dataset--result-provenance-registry)
14. [Statistics, Formulas, and Numerical Claims](#14-statistics-formulas-and-numerical-claims)
15. [Performance Benchmarking & Reproducibility Assessment](#15-performance-benchmarking--reproducibility-assessment)
16. [Manuscript & Publication Status](#16-manuscript--publication-status)
17. [What NOT to Claim (Scientific Boundaries)](#17-what-not-to-claim-scientific-boundaries)
18. [Known Unresolved Issues & Limitations](#18-known-unresolved-issues--limitations)
19. [Exact Handover Plan for Ayush](#19-exact-handover-plan-for-ayush)
20. [Future Research Roadmap](#20-future-research-roadmap)
21. [Operational Instructions & Reproducibility Commands](#21-operational-instructions--reproducibility-commands)
22. [Git & Collaboration Protocol](#22-git--collaboration-protocol)
23. [Glossary of Terms & Identifiers](#23-glossary-of-terms--identifiers)
24. [First Actions Checklist for Ayush](#24-first-actions-checklist-for-ayush)

---

## 1. Welcome and Handover Purpose

Welcome to the project, Ayush! This document transfers complete research ownership of this repository to you.

You are stepping into a mature, highly audited academic research codebase investigating software-level fault resilience for Post-Quantum Cryptography (PQC), specifically NIST FIPS 203 (ML-KEM-768). Over dozens of research phases, this repository has evolved from initial mathematical derivations and raw fault injection scripts into an end-to-end, publication-grade fault-resilience architecture backed by 400 cleanroom production trials, 900 canonical campaign trials, 600 circular verifier evaluations, and an unbroken 10-milestone manuscript revision register.

This handbook is designed so that you can navigate the entire repository, verify every empirical claim, reproduce every calculation, understand every design decision, and continue the research toward journal/conference publication without needing verbal explanation.

**The Golden Rule of this Repository:**  
Scientific accuracy, traceability, and preservation of evidence strictly supersede speed, cosmetic perfection, or arbitrary refactoring. Never delete raw data, never guess at missing records, and always maintain the traceable chain from mathematics to empirical measurements.

---

## 2. Executive Summary

### Plain-Language Summary
When computers operate in harsh environments—such as satellites in low Earth orbit, deep-space probes, or high-altitude aircraft—ionizing radiation and electrical disturbances can flip bits in processor registers. In post-quantum cryptography, an unmitigated bitflip during key decapsulation can either corrupt the resulting encryption key silently (enabling attackers or eavesdroppers to recover private keys) or crash the system, breaking communication links. 

Existing defenses either require custom hardware chips (which space missions and general-purpose microcontrollers cannot use) or run the entire algorithm twice (Dual Modular Redundancy, or DMR), which doubles execution time and drains battery power.

In this project, we designed a pure-software defense for ML-KEM-768. Instead of running everything twice, our software checks mathematical "invariants" (equations that must always hold true) at the micro-level of single arithmetic operations (Number Theoretic Transform butterflies). If an upset strikes, the processor catches it immediately, restores the two inputs from local CPU registers, and retries just that single operation ($\approx 0.0101\%$ of decapsulation operations) in under a microsecond. If a hardware part is permanently broken, the system cleanly escalates after 2 retries and outputs a standard dummy key, preventing secret data corruption with zero heap memory allocation and only $+16.9\%$ timing overhead.

### Technical Summary
The architecture integrates dual-transform Number Theoretic Transform (NTT) invariant monitoring, localized single-butterfly register snapshotting and rollback, and outer Fujisaki-Okamoto (FO) containment:
1. **Continuous Monitoring:** Monitors all 11 polynomial transforms ($5{,}376$ Forward Cooley-Tukey and $4{,}480$ Inverse Gentleman-Sande butterflies, totaling exactly $9{,}856$ operations). Decouples inverse NTT checks into adder and multiplier rails in $\mathbb{Z}_{3329}$ to eliminate modular division overhead.
2. **Localized Rollback ($F4$):** Transient multiplier upsets are detected and corrected in-place via bounded local retry. Across 100 transient fault trials, the system achieves a $100.0\%$ recovery rate ($95\%$ Wilson CI: $[96.30\%, 100.00\%]$), resolving errors on retry 1 and emitting golden authentic keys $K_{\text{valid}}$.
3. **Deterministic Fail-Stop ($F5A, F5B$):** Persistent multiplier and force-zeroing defects enforce a 2-retry limit, escalate to top-level containment, and force FIPS 203 Section 7.3 implicit rejection ($K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$) in $200/200$ trials ($95\%$ Wilson CI: $[98.12\%, 100.00\%]$).
4. **Zero SDC:** Zero Silent Data Corruption observed across 300 active production trials ($0/300$, $95\%$ Wilson CI: $[0.00\%, 1.26\%]$) and zero SDC across 750 active campaign trials (one-sided $97.5\%$ Clopper-Pearson upper bound: $0.49\%$).
5. **Low Overhead:** Decapsulation latency benchmarks on Apple Silicon ARM64 (`-O3`) measure $+16.9\%$ overhead ($129.51\,\mu\text{s}$ vs $110.77\,\mu\text{s}$, $1.17\times$ slowdown), substantially lower than unprotected sequential DMR ($+99.33\%$). The monitoring routines allocate zero dynamic heap memory ($0\text{ B}$).

---

## 3. The Final Research Goal

The permanent scientific mission of this project is:
> **To develop a mathematically grounded, reproducible, and evidence-backed understanding of fault behavior in post-quantum cryptographic implementations, specifically ML-KEM-768 key establishment, and to determine where selective detection, localized recovery, and fail-stop containment can be justified by a validated fault model.**

To achieve this, every contribution must maintain an unbroken traceable chain:
$$\text{Mathematics} \longrightarrow \text{Specification} \longrightarrow \text{Implementation} \longrightarrow \text{Fault Model} \longrightarrow \text{Injected Fault} \longrightarrow \text{Observed Behavior} \longrightarrow \text{Measured Metric} \longrightarrow \text{Bounded Scientific Conclusion}$$

### Research Tracks & Boundaries
- **Track 1 (Internal Cryptographic Resilience):** Primary active track. Focuses on NTT arithmetic, rollback, and FO failsafes inside decapsulation.
- **Track 2 (Spacecraft Communication Protocol Interactions):** Preserved in `experiments/system_model/spacecraft_protocol_sim.py`. Evaluates CCSDS space packet frame drops during cryptographic aborts. Kept separate from Track 1 to avoid diluting the cryptographic core with uncalibrated channel models.
- **Track 3 (Persistent State & Twiddle Corruption):** Integrated into Track 1 as an explicit boundary. Theorem 1 proves local invariant blindness ($0.0\%$ detection), while Phase 15Q demonstrates outer FO containment on a reference vector.

---

## 4. Research Questions and Hypotheses

The research addresses four core hypotheses:

1. **Hypothesis 1 (Dual-Transform Invariant Completeness):**  
   *Can pure-software algebraic invariant checks detect 100% of single-rail transient and persistent arithmetic faults across both Cooley-Tukey and Gentleman-Sande NTT butterflies without requiring runtime modular division?*  
   **Status:** **CONFIRMED `[DIRECTLY OBSERVED]`**. Decoupled adder/multiplier checks achieve $100\%$ detection across all active trials with zero modular division.

2. **Hypothesis 2 (Localized Rollback Efficiency):**  
   *Can single-butterfly register-level snapshots resolve transient multiplier upsets in-place without full decapsulation restarts, adding negligible recomputation overhead?*  
   **Status:** **CONFIRMED `[DIRECTLY OBSERVED]`**. $100/100$ transient trials recover on retry 1 ($1$ extra butterfly recomputation out of $9,856$, or $\approx 0.0101\%$ operation-count ratio).

3. **Hypothesis 3 (Verifier Domain Isolation):**  
   *Do circular verification architectures that read live output registers suffer from common-mode failure blindness?*  
   **Status:** **CONFIRMED `[DIRECTLY OBSERVED]`**. Standalone circular verifiers exhibit a $98.5\%$ false-pass rate ($591/600$, $[97.2\%, 99.2\%]$), proving snapshot-isolated checking is mandatory.

4. **Hypothesis 4 (Twiddle Factor Blindness & FO Containment):**  
   *Are local algebraic invariants mathematically blind to memory corruption in pre-computed twiddle factor tables, and can downstream FO re-encryption catch the resulting perturbation?*  
   **Status:** **CONFIRMED `[DIRECTLY OBSERVED]`**. Mathematically proved ($0.0\%$ local detection in Theorem 1); empirically verified on an 11-trial active mutation pilot (Phase 15Q) resulting in 100% FO rejection.

---

## 5. What We Have Achieved

| Milestone / Deliverable | Quantitative Achievement | Evidence Status | Primary Artifact |
| :--- | :--- | :---: | :--- |
| **Dual Invariant Engine** | Formulated forward & inverse decoupled checks covering all 9,856 butterflies. | `[DIRECTLY OBSERVED]` | [`poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c), [`mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) |
| **Microsecond Rollback** | 100/100 transient multiplier SEUs recovered at retry 1 ($100.0\%$, $[96.30\%, 100.00\%]$). | `[DIRECTLY OBSERVED]` | [`raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv) |
| **Safe Fail-Stop** | 200/200 persistent & zeroing faults contained ($100.0\%$, $[98.12\%, 100.00\%]$). | `[DIRECTLY OBSERVED]` | [`raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv) |
| **Zero SDC Observed** | 0 SDC across 300 active production trials ($[0.00\%, 1.26\%]$); 0 SDC across 750 campaign trials ($\le 0.49\%$). | `[INDEPENDENTLY RECOMPUTED]` | [`raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv), [`tfib_trial_level_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_trial_level_results.csv) |
| **Common-Mode Proof** | 591/600 circular verifier false passes ($98.5\%$, $[97.2\%, 99.2\%]$) characterized. | `[DIRECTLY OBSERVED]` | [`h1_activation_audit.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/h1_activation_audit.csv) |
| **Twiddle Proof & Pilot** | Theorem 1 proven; 11 active twiddle mutations caught by FO re-encryption. | `[DIRECTLY OBSERVED]` | [`trial_ledger.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase15q/trial_ledger.csv) |
| **Performance Benchmark** | $+16.9\%$ latency overhead under `-O3` ($129.51\,\mu\text{s}$ vs $110.77\,\mu\text{s}$) on Apple M3 Pro. | `[REPORTED BY A PRIOR PHASE]` | [`phase7i_e2e_results.json`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase7i/processed/phase7i_e2e_results.json) |
| **DMR Baseline Proof** | Unprotected sequential DMR measured at $+99.33\%$ overhead ($92.98\,\mu\text{s}$ vs $46.65\,\mu\text{s}$). | `[DIRECTLY OBSERVED]` | [`phase7h_timing_distribution.json`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase7h/processed/phase7h_timing_distribution.json) |
| **Zero Heap Allocation** | 0 B dynamic heap allocation verified via C source inspection. | `[DIRECTLY OBSERVED]` | [`poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c) |
| **Manuscript Provenance** | 10 unbroken manuscript milestones audited; verdict: **READY WITH EXPLICIT LIMITATIONS**. | `[DIRECTLY OBSERVED]` | [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) |

---

## 6. Current Repository State

- **Active Branch:** `space-resilience-framework`
- **Remote Origin:** `https://github.com/dhairyajain/pqc-research.git`
- **Head Commit:** `4a2c4eb` (Local is 4 commits ahead of `origin/space-resilience-framework` with zero divergence).
- **Working Tree:** Contains 10 modified tracked research files representing pre-existing Phase 4B/7/15A work. These must be preserved.
- **Untracked Files:** Contains canonical raw datasets (`phase18_audit/`, `results/phase15q/`), manuscript files (`paper/`), audit packages, and handover documentation (`docs/handover/`, `AYUSH.md`).
- **Active Manuscript:** [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) (SHA-256: `bb6d138a463347153385c69a6e7f2bf133708cdb8738ba66a325e420d58e0b4d`).

---

## 7. Research History & Phase-by-Phase Timeline

For the complete deep-dive timeline and historical phase index, consult:
- [`docs/handover/RESEARCH_TIMELINE.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/handover/RESEARCH_TIMELINE.md)
- [`docs/handover/PHASE_INDEX.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/handover/PHASE_INDEX.md)

### Key Milestones Summary
1. **Initial Foundation (Commits `cba1780` -> `e42d35f`):** Baseline architecture, Phase 4A dual-path implementation, Phase 4B internal fault hooks, FIPS KAT validation, and spacecraft simulator.
2. **Layered Prototyping (Phases 5–7L, Checkpoint `8b2382d`):** Formulation of NTT invariant monitoring, Phase 7H isolated DMR benchmarking ($+99.33\%$), Phase 7I inverse transform monitoring ($+16.9\%$, $9,856$ butterflies).
3. **Auditing & Evidence Closure (Phases 8–18):** Systematic literature matrix, Phase 11 KAT conformance ($N=100$), Phase 15Q twiddle factor pilot ($N=16$), Phase 16 circular verifier study ($N=600$), Phase 18 cleanroom production audit ($N=400$).
4. **TFIB Step 2 Campaigns (Commits `673190d` -> `4a2c4eb`):** 900-trial canonical campaign ($0$ SDC across 750 active trials, $0.49\%$ Clopper-Pearson bound).
5. **Manuscript Evidence Reconciliation (Phases 2C–2S):** Surgical refinement across 10 manuscript milestones, resulting in a fully qualified, evidence-backed manuscript.

---

## 8. Repository Directory Map

For the complete 1,562-file repository directory guide, consult [`docs/handover/REPOSITORY_MAP.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/handover/REPOSITORY_MAP.md).

### Quick Directory Summary
- `algorithms/`: Canonical C source code for ML-KEM-768 and fault hooks.
- `paper/`: Working manuscript (`manuscript.md`), 9 backups (`backup_phase2c` to `backup_phase2r`), BibTeX references.
- `docs/handover/`: Authoritative handover documentation, phase indices, source indices, claim ledgers, and `reproducibility_manifest.json`.
- `phase18_audit/`: 400 cleanroom production trials (`raw_production_trials.csv`) and C reproducer.
- `phase11_conformance_audit/`: 100 invalid-ciphertext conformance trials (`invalid_ciphertext_trials.csv`).
- `phase16_targeted_evidence_closure/`: 600 circular verifier blindness trials (`h1_activation_audit.csv`).
- `tfib_experiments/`: 900 canonical campaign trials (`phase2_step2c_trial_results.csv`), test runners, and PRF seeds.
- `results/`: Performance distributions (`phase7h/`, `phase7i/`), twiddle pilot (`phase15q/`), protocol desync results.
- `tests/`: NIST FIPS 203 & 204 Known Answer Test runners (`test_fips_kats.c`).
- `experiments/`: Fault injection simulation (`mlkem768_internal_fault_experiment.c`) and spacecraft protocol simulator (`spacecraft_protocol_sim.py`).

---

## 9. Source-Code Architecture

For complete function-level maps and line ranges, consult [`docs/handover/SOURCE_CODE_INDEX.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/handover/SOURCE_CODE_INDEX.md).

### Architecture Highlights
- **Transform Call Graph (Table 1):**
  - Forward Cooley-Tukey NTT: 6 transforms ($5{,}376$ butterflies). Call sites: `indcpa.c:619` (decapsulation), `indcpa.c:558` (re-encryption).
  - Inverse Gentleman-Sande NTT: 5 transforms ($4{,}480$ butterflies). Call sites: `indcpa.c:622` (decapsulation), `indcpa.c:564`, `indcpa.c:565` (re-encryption).
  - Secret key vector $\hat{\mathbf{s}} \in R_q^3$ is stored pre-transformed and is **never transformed** during decapsulation.
- **Rollback Engine:** Constrained to single butterflies. Operands $u_{\text{saved}}, v_{\text{saved}}$ are held in CPU registers. If a fault strikes, state is restored and retried in-place up to 2 times.
- **Containment Failsafe (`kem.c:466–525`):**
  Dual-rail reverse comparison (`fail_chk`), monitor persistent counter escalation (`fail = 0xFF`), and constant-time selection (`mlk_ct_cmov_zero`) deterministically emit $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$.

---

## 10. Code-Level File Index

| File Path | Lines | Core Functions & Symbols | Purpose & Fault Model | Status |
|:---|:---:|:---|:---|:---:|
| [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c) | 681 | `mlk_poly_ntt`, `mlk_poly_invntt_tomont` | NTT transform implementation with monitor & rollback hooks. | Canonical Core |
| [`algorithms/source_ref/mlkem/src/kem.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c) | 544 | `crypto_kem_dec`, `mlk_kem_dec_monitored` | Top-level decapsulation, dual-rail FO comparison, constant-time cmov. | Canonical Core |
| [`algorithms/source_ref/mlkem/src/indcpa.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/indcpa.c) | 652 | `mlk_indcpa_dec`, `mlk_indcpa_enc` | IND-CPA encryption/decryption hosting all 11 transform call sites. | Canonical Core |
| [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) | 874 | `ntt_native_monitor_*`, `invntt_native_monitor_*` | Invariant math, snapshot storage, rollback retry engine ($0\text{ B}$ heap). | Canonical Core |
| [`algorithms/source_ref/mlkem_fault_hooks.h`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.h) | 289 | Macro definitions, status codes | Header declarations and monitor counters. | Canonical Core |
| [`algorithms/source_ref/mlkem/src/zetas.inc`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/zetas.inc) | 63 | `mlk_zetas`, `mlk_isolated_zetas_page_t` | Twiddle constants and research memory-relocated page arm. | Canonical Core |
| [`phase18_audit/production_reproducer.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/production_reproducer.c) | 230 | `main`, production trial loop | Standalone C cleanroom test reproducer for compiled binaries. | Canonical Harness |
| [`tests/test_fips_kats.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tests/test_fips_kats.c) | 69 | `main`, KAT verification loops | NIST FIPS 203 & 204 Known Answer Test runner. | Canonical Test |
| [`experiments/system_model/spacecraft_protocol_sim.py`](file:///Users/dhairyajain/Desktop/pqc%20research/experiments/system_model/spacecraft_protocol_sim.py) | 323 | `SpacecraftProtocolSim` | CCSDS space packet protocol desynchronization simulator (Track 2). | Preserved Track 2 |

---

## 11. Mathematical Foundation & Invariant Derivations

### 11.1 Ring Arithmetic
ML-KEM-768 operates over the polynomial quotient ring:
$$R_q = \mathbb{Z}_q[X]/(X^{256} + 1), \quad q = 3329$$
Because $X^{256} + 1 \equiv \prod_{i=0}^{127} (X^2 - \zeta_{2i+1}) \pmod q$, the NTT maps polynomials into 128 quadratic polynomial factors over $\mathbb{Z}_q$.

### 11.2 Forward Cooley-Tukey (CT) Invariant
In each CT butterfly, input coefficients $u, v \in \mathbb{Z}_q$ and twiddle scalar $\zeta \in \mathbb{Z}_q$ compute:
$$t = v \cdot \zeta \pmod q$$
$$r_0 = u + t \pmod q, \quad r_1 = u - t \pmod q$$
Summing the outputs:
$$r_0 + r_1 \equiv (u + t) + (u - t) \equiv 2u \pmod q$$
Because $t$ cancels, the sum is algebraically invariant to multiplier perturbations. To detect symmetric multiplier errors where an attacker or glitch alters $t$ while preserving $r_0 + r_1$, our monitor evaluates two decoupled checks using saved snapshot operands:
$$\Delta_{\text{sum}} = (r_0 + r_1 - 2u_{\text{saved}}) \pmod q$$
$$\Delta_{\text{mul}} = (r_0 - r_1 - 2(v_{\text{saved}} \cdot \zeta)) \pmod q$$
Any non-zero delta flags an immediate detection event.

### 11.3 Inverse Gentleman-Sande (GS) Invariant
In each GS butterfly, inputs $u, v \in \mathbb{Z}_q$ and twiddle $\zeta$ compute:
$$r_0 = u + v \pmod q$$
$$d = v - u \pmod q, \quad r_1 = d \cdot \zeta \pmod q$$
To eliminate modular division in software, the check is decoupled into two forward checks:
$$\text{Check 1 (Adder Rail):} \quad r_0 \equiv u_{\text{saved}} + v_{\text{saved}} \pmod q$$
$$\text{Check 2 (Multiplier Rail):} \quad r_1 \equiv (v_{\text{saved}} - u_{\text{saved}}) \cdot \zeta \pmod q$$

### 11.4 Theorem 1: Twiddle Factor Blindness
**Theorem 1.** *If a butterfly operation and its local invariant checker execute using the identical twiddle factor scalar $\tilde{\zeta} = \zeta \oplus \Delta_\zeta$ loaded from memory, the invariant detection probability is exactly $0.0\%$.*  
*Proof.* The sum invariant $\Delta_{\text{sum}}$ is independent of $\zeta$. The multiplier check evaluates $\tilde{r}_0 - \tilde{r}_1 \equiv 2(v \cdot \tilde{\zeta}) \pmod q$, which matches the recomputed check using $\tilde{\zeta}$ identically. Thus, local arithmetic invariants are completely blind to twiddle memory corruption, proving that downstream Fujisaki-Okamoto re-encryption is mathematically necessary to catch twiddle mutations.

---

## 12. Fault Models & Experiment Design

We evaluate non-adversarial physical fault models reflecting radiation and thermal stress:
1. **$F12$ (Clean Baseline Controls):** Zero faults injected ($N=100$). Validates $0$ false-alarm aborts and $100.0\%$ baseline correctness.
2. **$F4$ (Transient Multiplier SEU):** Single-bit bitflip injected into multiplier product $t$ during execution ($N=100$). Clears on subsequent cycle. Validates $100.0\%$ in-place recovery on retry 1.
3. **$F5A$ (Persistent Multiplier Fault):** Multi-cycle bitmask fault injected repeatedly across consecutive invocations ($N=100$). Exhausts the 2-retry limit and deterministically triggers fail-stop implicit rejection.
4. **$F5B$ (Software Force-Value Zeroing):** Forces intermediate addition/subtraction outputs to zero ($N=100$). Exhausts retry limit and triggers safe fail-stop implicit rejection.
5. **$H1$ (Circular Verifier Vulnerability):** Evaluates checkers reading faulted live registers across 6 datapath sites ($N=600$). Proves $98.5\%$ verifier blindness.
6. **$H2$ (Production SDC Evaluation):** Evaluates all 300 active production trials (F4 + F5A + F5B). Confirms $0$ SDC ($[0.00\%, 1.26\%]$).
7. **Canonical Campaign (Step 2C):** Evaluates 900 trials (150 clean controls, 750 active faults across twiddle, checker logic, and metadata tags). Confirms $0$ SDC ($\le 0.49\%$ Clopper-Pearson bound).

---

## 13. Dataset & Result Provenance Registry

For full dataset schemas and validation records, consult [`docs/handover/DATA_AND_EXPERIMENT_REGISTRY.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/handover/DATA_AND_EXPERIMENT_REGISTRY.md) and [`docs/handover/reproducibility_manifest.json`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/handover/reproducibility_manifest.json).

### Primary Verified Datasets
- `phase18_audit/raw_production_trials.csv` (SHA-256: `9d5ca2df...`): 400 production trials.
- `phase11_conformance_audit/invalid_ciphertext_trials.csv` (SHA-256: `ed73e599...`): 100 KAT trials.
- `phase16_targeted_evidence_closure/h1_activation_audit.csv` (SHA-256: `8684ed49...`): 600 circular verifier trials.
- `tfib_trial_level_results.csv` (SHA-256: `cff35149...`): 900 canonical campaign trials.
- `results/phase15q/trial_ledger.csv` (SHA-256: `5cf48fb9...`): 16 twiddle factor pilot trials.
- `results/phase7h/processed/phase7h_timing_distribution.json` (SHA-256: `08fccaea...`): Phase 7H timing records.
- `results/phase7i/processed/phase7i_e2e_results.json` (SHA-256: `5e294c56...`): Phase 7I latency & butterfly records.

---

## 14. Statistics, Formulas, and Numerical Claims

For complete bidirectional traceability, consult [`docs/handover/CLAIM_TO_EVIDENCE_LEDGER.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/handover/CLAIM_TO_EVIDENCE_LEDGER.md).

### Statistical Formulas
1. **Wilson Score Confidence Interval (Two-Sided 95%):**
   $$\hat{p} = \frac{k}{n}, \quad z = 1.95996$$
   $$\text{CI} = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$
   - For $k=100, n=100$: $[96.30\%, 100.00\%]$
   - For $k=200, n=200$: $[98.12\%, 100.00\%]$
   - For $k=0, n=300$: $[0.00\%, 1.26\%]$
   - For $k=591, n=600$: $[97.17\%, 99.21\%] \longrightarrow [97.2\%, 99.2\%]$
2. **Clopper-Pearson Exact Binomial Upper Bound (One-Sided 97.5%):**
   For $k=0$ observed failures in $n=750$ active trials:
   $$p_U = 1 - (\alpha)^{1/n} = 1 - (0.025)^{1/750} = 0.004906 = 0.4906\% \approx \mathbf{0.49\%}$$

---

## 15. Performance Benchmarking & Reproducibility Assessment

- **Reported Latency Overhead:** $+16.9\%$ under `-O3` ($129.51\,\mu\text{s}$ monitored vs $110.77\,\mu\text{s}$ baseline, $1.17\times$ slowdown) across $N = 2,000$ warm decapsulations.
- **Hardware Platform:** Recorded on Apple Silicon ARM64 (Apple M3 Pro, 12 CPU cores, macOS Darwin 25.1.0) using Apple Clang 17.0.0. Binary reproduction harnesses executed on macOS Darwin 27.0.0.
- **Disclosed Timing Discrepancy:** Standard deviations reflect stdout summary records ($4.82\,\mu\text{s}$ and $5.14\,\mu\text{s}$); an alternate run logged $1.42\,\mu\text{s}$ and $5.61\,\mu\text{s}$. Per-iteration raw samples were not persisted to disk (disclosed in Table 4 footnote 1).
- **Unmeasured `-O2` Projection:** Design blueprints modeled $+25.3\%$ ($1.253 \cdot T_0$), but only `-O3` is empirically supported by compiled logs.
- **Sequential DMR Baseline:** In Phase 7H, unprotected sequential DMR measured $+99.33\%$ overhead (displayed rounded means: $92.98\,\mu\text{s}$ vs $46.65\,\mu\text{s}$, or $+99.31\%$). Historical Phase 7I $+135.3\%$ DMR was an artifact of running duplicate passes with monitors enabled.

---

## 16. Manuscript & Publication Status

- **Working File:** [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md)
- **Provenance Register:** Fully cataloged in [`docs/handover/MANUSCRIPT_VERSION_HISTORY.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/handover/MANUSCRIPT_VERSION_HISTORY.md).
- **Audit Verdict:** **READY WITH EXPLICIT LIMITATIONS** (Determined in Phase 2S).
- **Citation Audit:** 16 in-text citations resolve to 16 bibliography entries; exactly 0 missing, 0 unused, and 0 duplicate entries.
- **Action for Ayush:** Do not apply further cosmetic text edits to `paper/manuscript.md`. Proceed directly to LaTeX conference/journal formatting.

---

## 17. What NOT to Claim (Scientific Boundaries)

Ayush, you must uphold these scientific boundaries in all future writing and presentations:
1. **Never claim physical radiation hardness or space qualification:** We evaluated software-injected architectural register bitflips. We did not conduct physical cyclotron heavy-ion beam testing or measure in-beam SEU cross-sections.
2. **Never claim certified microarchitectural constant-time execution:** While source-level primitives are branch-free, binary timing leakage has not been tested via TVLA or dudect, and fault detection conditionally branches into rollback retry.
3. **Never claim whole-program dynamic memory guarantees:** Source inspection found 0 heap allocations under the evaluated configuration; do not claim a formal universal runtime proof.
4. **Never conflate operation ratio with wall-clock overhead:** The $1/9{,}856 \approx 0.0101\%$ single-butterfly recomputation ratio is an operation-count metric, not end-to-end execution-time overhead ($+16.9\%$).
5. **Never claim universal absence of SDC:** $0/300$ and $0/750$ zero observed SDC results establish statistical upper bounds ($1.26\%$ and $0.49\%$), not absolute mathematical zero risk across all circuits.
6. **Never generalize the twiddle pilot beyond the evaluated vector:** Phase 15Q evaluated 16 trials on a reference vector; it is not a statistical multi-orbit distribution over arbitrary keys.

---

## 18. Known Unresolved Issues & Limitations

For the complete decision and boundary log, consult [`docs/handover/OPEN_ISSUES_AND_DECISIONS.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/handover/OPEN_ISSUES_AND_DECISIONS.md).

1. **Unpersisted Raw Benchmark Iterations (Minor):** Per-iteration timing records were not saved to disk; dispersion metrics rely on stdout logs.
2. **Uninstrumented Stack Memory Utilization (Minor):** Dynamic stack frame growth was not dynamically instrumented.
3. **Platform Scope (Moderate):** Benchmarks were recorded on 64-bit desktop ARM64; embedded profiling on 32-bit Cortex-M4 or RISC-V remains future work.
4. **Twiddle Pilot Sample Size (Moderate):** Phase 15Q was a 16-trial pilot on one test vector.

---

## 19. Exact Handover Plan for Ayush

For your day-by-day onboarding schedule, consult [`docs/handover/AYUSH_NEXT_STEPS.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/handover/AYUSH_NEXT_STEPS.md).

- **Day 1:** Read `AYUSH.md`, read `paper/manuscript.md`, inspect `git status` (preserve 10 modified files), inspect `poly.c` and `kem.c`.
- **Day 2:** Run `test_fips_kats` and `production_reproducer`, recompute Wilson confidence intervals in Python.
- **Day 3–4:** Review `docs/handover/` deep-dive registers; verify dataset hashes against `reproducibility_manifest.json`.
- **Week 2:** Begin future research extensions (ARM Cortex-M4 cross-compilation, dudect timing leakage analysis).

---

## 20. Future Research Roadmap

1. **Embedded Microcontroller Profiling (High Priority):** Port and cross-compile the monitored ML-KEM-768 engine to ARM Cortex-M4 (e.g., STM32F4) and RISC-V RV32IM to measure cycle count and stack growth.
2. **Microarchitectural Leakage Assessment (High Priority):** Execute TVLA / `dudect` across $100{,}000$ fixed-vs-random decapsulations to evaluate binary timing leakage in fault-free execution.
3. **Expanded Randomized Twiddle Campaign (Medium Priority):** Expand Phase 15Q from 16 trials on 1 vector to 500 trials across randomized keys and ciphertexts.
4. **Physical Beam Testing (Long-Term):** Partner with a cyclotron beam facility (e.g., TRIUMF, LBNL) for heavy-ion radiation testing to evaluate physical in-situ SEU cross-sections.

---

## 21. Operational Instructions & Reproducibility Commands

### Build Clean & Run NIST FIPS KATs
```bash
make clean
make bin/test_fips_kats
./bin/test_fips_kats
```

### Build & Run Cleanroom Production Reproducer
```bash
clang -O3 -Wall -Wextra -std=c11 -I. -Ialgorithms/source_ref/mlkem \
  phase18_audit/production_reproducer.c bin/obj/mlkem768_inst.o bin/obj/mlkem_fault_hooks.o \
  -o phase18_audit/production_reproducer
./phase18_audit/production_reproducer
```

### Verify Hashes Against Manifest
```bash
python3 -c '
import json, hashlib
with open("docs/handover/reproducibility_manifest.json") as f:
    m = json.load(f)["artifacts"]
for a in m:
    with open(a["relative_path"], "rb") as fp:
        h = hashlib.sha256(fp.read()).hexdigest()
    assert h == a["sha256"], f"MISMATCH on {a[\x27relative_path\x27]}"
print(f"All {len(m)} manifest artifacts verified with exact SHA-256 matches!")
'
```

---

## 22. Git & Collaboration Protocol

1. **Branch Strategy:** Work on `space-resilience-framework` or create dedicated feature branches (`feature/cortex-m4-port`, `feature/dudect-analysis`).
2. **Preserve Untracked Provenance:** Do not run `git clean -fd` or `git reset --hard`.
3. **Commit Messages:** Follow conventional commits: `feat:`, `research:`, `docs:`, `test:`, `fix:`.
4. **Never Force-Push:** Never run `git push --force`. Always use standard forward commits.

---

## 23. Glossary of Terms & Identifiers

- **PQC:** Post-Quantum Cryptography.
- **ML-KEM:** Module-Lattice-Based Key-Encapsulation Mechanism (NIST FIPS 203, formerly CRYSTALS-Kyber).
- **NTT:** Number Theoretic Transform. Computes quasi-linear polynomial multiplications in ring $R_q$.
- **CT:** Cooley-Tukey butterfly algorithm (time domain to frequency domain; Forward NTT).
- **GS:** Gentleman-Sande butterfly algorithm (frequency domain to time domain; Inverse NTT).
- **SDC:** Silent Data Corruption. Undetected cryptographic corruption yielding an invalid or exploitable shared key.
- **FO Transform:** Fujisaki-Okamoto transform. Converts IND-CPA public key encryption to IND-CCA2 KEM via re-encryption comparison.
- **DMR:** Dual Modular Redundancy. Executing decapsulation twice sequentially ($\ge +100\%$ overhead).
- **F12:** Baseline clean control fault model ($N=100$).
- **F4:** Transient multiplier single-event upset fault model ($N=100$).
- **F5A / F5B:** Persistent multiplier bitmask and force-value zeroing fault models ($N=100$ each).
- **H1:** Harness circular verifier vulnerability evaluation ($N=600$).
- **H2:** Analytical aggregate of 300 active production fault trials ($0/300$ SDC).
- **KAT:** Known Answer Test (NIST conformance validation).

---

## 24. First Actions Checklist for Ayush

Before writing any new code:
- [ ] Read `AYUSH.md` from start to finish.
- [ ] Read [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) to understand the paper's structure and claims.
- [ ] Inspect `git status` and verify that the 10 modified tracked files are present and untouched.
- [ ] Run `make bin/test_fips_kats && ./bin/test_fips_kats` to verify FIPS KAT compliance.
- [ ] Compile and run `phase18_audit/production_reproducer` to observe the 400 cleanroom trials.
- [ ] Run the Python hash validation command in Section 21 to verify all 29 manifest artifacts.
- [ ] Review [`docs/handover/OPEN_ISSUES_AND_DECISIONS.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/handover/OPEN_ISSUES_AND_DECISIONS.md) to internalize what not to claim.
- [ ] Select your first research objective from Section 20 (Roadmap).

Good luck, Ayush! The research is solid, traceable, and ready for you to take it to the finish line.
