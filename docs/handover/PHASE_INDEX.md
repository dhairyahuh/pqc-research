# Phase Index & Experimental Registry

**Repository:** `pqc-research`  
**Active Branch:** `space-resilience-framework`  
**Author:** Dhairya Jain  
**Handover Recipient:** Ayush  
**Date:** October 2026  

This document provides a comprehensive, structured index of all recoverable research phases, audits, experimental campaigns, and manuscript revision cycles across the repository.

---

## 1. Foundational & Exploratory Phases (Phases 0–4B)

### Phase 0: Literature & State-of-the-Art Audit
- **Location:** [`docs/phase0-changelog.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/phase0-changelog.md)
- **Objective:** Survey published fault-injection attacks on lattice-based cryptography (e.g., Ravi et al., Hermelink et al., Delvaux).
- **Outcome:** Identified that existing fault defenses predominantly target custom FPGA/ASIC pipelines, leaving general-purpose software ML-KEM reliant on expensive full-algorithm DMR.

### Phase 1: Mathematical Fault Modeling
- **Location:** [`docs/phase1-mathematical-audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/phase1-mathematical-audit.md)
- **Objective:** Formulate mathematical models of arithmetic disturbances in polynomial ring arithmetic over $R_q = \mathbb{Z}_{3329}[X]/(X^{256} + 1)$.
- **Finding:** Forward Cooley-Tukey butterfly outputs satisfy $r_0 + r_1 \equiv 2u \pmod q$, which is algebraically invariant to multiplier outputs $t$ and twiddles $\zeta$.

### Phase 2 & 3: Initial Fault Campaigns (ML-KEM & ML-DSA)
- **Location:** [`docs/phase2-mlkem-fault-campaign-audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/phase2-mlkem-fault-campaign-audit.md), [`docs/phase3-mldsa-fault-campaign-audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/phase3-mldsa-fault-campaign-audit.md)
- **Objective:** Prototype software fault injection across polynomial multiplication and signature loops.
- **Finding:** ML-KEM decapsulation is acutely vulnerable to multiplier faults during inverse NTT, directly inducing SDC in the recovered message $m'$.

### Phase 4A & 4B: Dual-Path Implementation & Spacecraft Protocol Simulation
- **Location:** [`docs/phase4b-validation-audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/phase4b-validation-audit.md), [`experiments/system_model/spacecraft_protocol_sim.py`](file:///Users/dhairyajain/Desktop/pqc%20research/experiments/system_model/spacecraft_protocol_sim.py), [`tests/test_fips_kats.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tests/test_fips_kats.c)
- **Objective:** Implement internal C fault injection hooks, FIPS KAT verification runners, and a CCSDS-inspired spacecraft protocol desynchronization simulator.
- **Finding:** Standardized fault taxonomy into Categories A–F. Established that cryptographic aborts cause frame drops in spacecraft links, demonstrating the value of in-place retry.

---

## 2. Layered ML-KEM Prototyping & Benchmarking (Phases 5–7L)

### Phase 5 & 6: Cross-Implementation Surfaces & Verifier Pitfalls
- **Location:** [`docs/phase5/`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/phase5/), [`docs/phase6/`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/phase6/)
- **Objective:** Evaluate how compiler optimizations affect fault propagation and test whether checkers reading live registers can detect errors.
- **Critical Discovery:** Checkers reading live output registers suffer from common-mode cancellation when multiplier perturbations alter both rails symmetrically. Snapshot-isolated checking is strictly required.

### Phase 7 & 7C: Native Decapsulation Invariant Integration
- **Location:** [`docs/phase7/`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/phase7/), [`docs/phase7c/`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/phase7c/)
- **Objective:** Embed forward NTT Cooley-Tukey invariant monitoring into production C routines without relying on external oracles.
- **Artifact:** Initial version of `algorithms/source_ref/mlkem_fault_hooks.c`.

### Phase 7H: Isolated Benchmarking vs. Sequential DMR
- **Location:** [`docs/phase7h/`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/phase7h/), [`results/phase7h/processed/phase7h_timing_distribution.json`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase7h/processed/phase7h_timing_distribution.json)
- **Objective:** Compare native decapsulation latency against unprotected sequential DMR ($2.0\times T_0$).
- **Results:**
  - Baseline Mean: $46.65\,\mu\text{s}$ ($\sigma = 14.32\,\mu\text{s}$, $N=2{,}000$)
  - Sequential DMR Mean: $92.98\,\mu\text{s}$ ($\sigma = 12.97\,\mu\text{s}$, $N=2{,}000$)
  - Measured Overhead: $+99.33\%$ (summary JSON metric; ratio of rounded means is $+99.31\%$)
- **Significance:** Validates that unprotected software duplicate decapsulation requires $\approx +100\%$ overhead.

### Phase 7I: Inverse NTT Decoupled Monitoring & Butterfly Counting
- **Location:** [`docs/phase7i/`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/phase7i/), [`results/phase7i/processed/phase7i_e2e_results.json`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase7i/processed/phase7i_e2e_results.json)
- **Objective:** Implement Gentleman-Sande inverse transform monitoring using decoupled checks (adder rail and multiplier rail) to eliminate expensive modular divisions.
- **Results:**
  - Total Decapsulation Butterflies: Exactly **9,856** (5,376 Forward CT, 4,480 Inverse GS across 11 transforms).
  - Uninstrumented Baseline: $110.77\,\mu\text{s}$ ($\sigma = 4.82\,\mu\text{s}$)
  - Monitored + Rollback: $129.51\,\mu\text{s}$ ($\sigma = 5.14\,\mu\text{s}$)
  - Overhead under `-O3`: **+16.9%** ($1.17\times$ slowdown) on Apple M3 Pro.
- **Experimental Artifact Disclosed:** Duplicate passes run with monitors enabled logged an artificial $+135.3\%$ overhead, superseded by Phase 7H's clean $+99.33\%$ benchmark.

---

## 3. Systematic Auditing, Hardening, and Evidence Closure (Phases 8–18)

### Phase 11: Conformance Audit & Independent Oracle Validation
- **Location:** [`phase11_conformance_audit/`](file:///Users/dhairyajain/Desktop/pqc%20research/phase11_conformance_audit/)
- **Objective:** Verify implicit rejection compliance against a standalone FIPS 203 Section 7.3 SHAKE-256 oracle.
- **Dataset:** [`invalid_ciphertext_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase11_conformance_audit/invalid_ciphertext_trials.csv) ($N=100$).
- **Outcome:** $100/100$ ($100.0\%$, $95\%$ Wilson CI: $[96.30\%, 100.00\%]$) conformant implicit rejections matching the oracle.

### Phase 15Q: Twiddle Factor Memory Corruption Pilot
- **Location:** [`results/phase15q/`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase15q/)
- **Objective:** Empirically evaluate the security boundary established by Theorem 1 (local invariant blindness to twiddle factor corruption).
- **Dataset:** [`trial_ledger.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase15q/trial_ledger.csv) ($N=16$ trials on a reference vector).
- **Findings:**
  - 11 active mutations directly altered consumed twiddle factors (`zetas[1, 2, 32, 63, 64, 95, 127]`).
  - All 11 active consumed mutations bypassed local butterfly monitors ($0.0\%$ local detection), but triggered FO re-encryption ciphertext mismatch.
  - Deterministically emitted $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$ with zero observed SDC.
  - 5 controls (2 baseline matches, 1 root twiddle, 2 sham zero masks) behaved as expected.

### Phase 16: Circular-Verifier Blindness Study (H1)
- **Location:** [`phase16_targeted_evidence_closure/`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/)
- **Objective:** Quantify false-pass rates of unshielded circular verifiers across 6 datapath corruption sites.
- **Dataset:** [`h1_activation_audit.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/h1_activation_audit.csv) ($N=600$ trials across T1–T6).
- **Results:**
  - T1 (CT Multiplier): 98/100 false passes ($98.0\%$, $[93.0\%, 99.5\%]$)
  - T2 (CT Subtractor): 94/100 false passes ($94.0\%$, $[87.5\%, 97.2\%]$)
  - T3 (GS Adder): 100/100 false passes ($100.0\%$, $[96.3\%, 100.0\%]$)
  - T4 (GS Multiplier): 100/100 false passes ($100.0\%$, $[96.3\%, 100.0\%]$)
  - T5 (Twiddle Scale): 99/100 false passes ($99.0\%$, $[94.6\%, 99.8\%]$)
  - T6 (In-Place Array): 100/100 false passes ($100.0\%$, $[96.3\%, 100.0\%]$)
  - Total Aggregate: **591/600** false passes (**98.5%**, $95\%$ Wilson CI: $[97.2\%, 99.2\%]$).

### Phase 18: Cleanroom Production Trial Audit (H2)
- **Location:** [`phase18_audit/`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/)
- **Objective:** Execute cleanroom fault injection on compiled production binaries (`bin/obj/mlkem768_inst.o`, `bin/obj/mlkem_fault_hooks.o`).
- **Dataset:** [`raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv) ($N=400$).
- **Results:**
  - F12 (Clean Baseline Controls): 100/100 ($100.0\%$) `CLEAN_SUCCESS`, zero false alarms.
  - F4 (Transient Multiplier SEU): 100/100 ($100.0\%$) `GENUINE_RECOVERY` at `retry_count==1`, authentic key emitted.
  - F5A (Persistent Multiplier Fault): 100/100 ($100.0\%$) `SAFE_FAIL_STOP` at `retry_count==2`, implicit rejection key emitted.
  - F5B (Force-Value Zeroing): 100/100 ($100.0\%$) `SAFE_FAIL_STOP` at `retry_count==2`, implicit rejection key emitted.
  - H2 (Production SDC): **0/300** active trials ($0.00\%$, $95\%$ Wilson CI: $[0.00\%, 1.26\%]$).

---

## 4. TFIB Step 2 Campaigns & Countermeasure Independence

### Step 2C & 2C-A: Canonical 900-Trial Campaign
- **Location:** [`tfib_experiments/`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/), [`Step2C_A_Final_Review_Package/`](file:///Users/dhairyajain/Desktop/pqc%20research/Step2C_A_Final_Review_Package/)
- **Objective:** Evaluate countermeasure independence and SDC across 900 trials.
- **Dataset:** [`tfib_trial_level_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_trial_level_results.csv) ($N=900$).
- **Composition:** 150 clean controls + 750 active fault trials across diverse suites (twiddle, checker logic, metadata tags).
- **Result:** **0 SDC events out of 750 active trials**; exact one-sided $97.5\%$ Clopper-Pearson upper confidence bound is **0.49%**.

---

## 5. Manuscript Revision & Evidence-Reconciliation Chain (Phases 2C–2S)

| Phase | Target Document | Action / Evidence Addressed | Pre-Edit SHA-256 | Post-Edit SHA-256 |
| :--- | :--- | :--- | :--- | :--- |
| **2C** | `paper/manuscript.md` | Working manuscript baseline | — | `1b1ec761...` |
| **2E** | `manuscript.md.backup_phase2e` | Initial evidence qualification; pruned ungrounded claims | `1b1ec761...` | `50362dbd...` |
| **2G** | `manuscript.md.backup_phase2g` | Distinguished software faults from physical radiation | `50362dbd...` | `629c0c05...` |
| **2I** | `manuscript.md.backup_phase2i` | Platform clarification: Apple M3 Pro benchmarks vs M1 reproduction | `629c0c05...` | `e5c865f2...` |
| **2K** | `manuscript.md.backup_phase2k` | Added Table 1 call graph with exact 9,856 butterfly counting | `e5c865f2...` | `07ca24c5...` |
| **2N** | `manuscript.md.backup_phase2n` | Strict population separation (400 production vs 750 campaign vs 100 KAT) | `07ca24c5...` | `d4954605...` |
| **2P** | `manuscript.md.backup_phase2p` | Table 2 provenance footnote; clarified 0.0101% operation ratio | `d4954605...` | `dc04325d...` |
| **2Q.3** | `manuscript.md.backup_phase2q` | Table 3 circular verifier interval corrected to $[97.2\%, 99.2\%]$ | `dc04325d...` | `8696496b...` |
| **2R.3** | `paper/manuscript.md` | Table 4 footnote allocation claim qualified to source inspection | `1837fe53...` | `bb6d138a...` |
| **2S** | `paper/manuscript.md` | Read-only final review; verdict: **READY WITH EXPLICIT LIMITATIONS** | `bb6d138a...` | `bb6d138a...` (Unchanged) |
