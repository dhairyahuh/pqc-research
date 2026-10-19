# Project Overview: Software-Level Fault Resilience for ML-KEM-768

**Repository:** `pqc-research`  
**Active Branch:** `space-resilience-framework`  
**Author:** Dhairya Jain  
**Handover Recipient:** Ayush  
**Date:** October 2026  
**Primary Manuscript:** [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) (SHA-256: `bb6d138a463347153385c69a6e7f2bf133708cdb8738ba66a325e420d58e0b4d`)

---

## 1. Executive Summary

This repository houses the research, source code, experiment harnesses, raw datasets, verification oracles, and scientific manuscript for an end-to-end software-level fault-resilience architecture for Post-Quantum Cryptography (PQC), specifically **ML-KEM-768** (standardized in NIST FIPS 203).

In high-reliability and radiation-exposed environments (e.g., small satellite avionics, deep-space communication links, high-altitude aerospace platforms, and critical embedded controllers), computational hardware is subject to single-event upsets (SEUs) and persistent latch defects. Unmitigated arithmetic faults during cryptographic decapsulation risk inducing **Silent Data Corruption (SDC)**—which can enable fault-based private key recovery attacks—or triggering unnecessary full-algorithm aborts that degrade communication availability.

To address this challenge without relying on custom hardware accelerators (e.g., ASIC/FPGA) or incurring the severe $\ge +100\%$ latency overhead of full-operation Dual Modular Redundancy (DMR), this project designs, implements, and empirically validates:
1. **Dual-Transform NTT Invariant Monitoring:** Continuous software monitoring across all 11 polynomial Number Theoretic Transforms ($5{,}376$ Forward Cooley-Tukey and $4{,}480$ Inverse Gentleman-Sande butterflies, totaling exactly $9{,}856$ butterfly operations) during decapsulation and Fujisaki-Okamoto (FO) re-encryption.
2. **Localized Single-Butterfly Register Rollback:** Bounded in-place retry ($u_{\text{saved}}, v_{\text{saved}}$ stored in local CPU registers) that resolves transient multiplier upsets in a single retry iteration ($\approx 0.0101\%$ recomputation ratio) without restarting decapsulation.
3. **Deterministic Fail-Stop Containment:** Safe escalation on persistent hardware defects or software force-value faults after 2 retries, forcing top-level implicit rejection ($K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$) and preventing authentic key emission.

---

## 2. The Final Research Goal

The overarching scientific goal of this research project is:

> **To develop a mathematically grounded, reproducible, and evidence-backed understanding of fault behavior in post-quantum cryptographic implementations, specifically ML-KEM-768 key establishment, and to determine where selective detection, localized recovery, and fail-stop containment can be justified by a validated fault model.**

To achieve publication-grade scientific defensibility, every claim in this project must adhere to an unbroken traceable chain:
$$\text{Mathematics} \longrightarrow \text{Specification} \longrightarrow \text{Implementation} \longrightarrow \text{Fault Model} \longrightarrow \text{Injected Fault} \longrightarrow \text{Observed Behavior} \longrightarrow \text{Measured Metric} \longrightarrow \text{Bounded Scientific Conclusion}$$

### Research Principles
- **Justified Characterization:** Countermeasures and resilience mechanisms must be justified by empirically observed fault behavior, not assumed to work because they seem plausible in theory.
- **Traceable Denominators:** Denominators, exclusions, populations, and control baselines must remain completely explicit. Data from disparate test harnesses or configurations must never be pooled silently.
- **Honest Limitations:** Software bitflips abstract architectural register upsets; they do not simulate physical semiconductor physics (charge deposition, multi-cell upsets, analog transients). Physical cyclotron beam testing and microarchitectural side-channel evaluation are explicit future steps.

---

## 3. Paper Tracks & Research Boundaries

The repository contains work across three distinct research tracks established during project framing:

### Paper Track 1: Internal Fault Detection & Localized Recovery (PRIMARY & ACTIVE)
- **Status:** **COMPLETE & AUDITED** (Subject of `paper/manuscript.md`, audited through Phase 2S).
- **Core Contribution:** Dual-transform NTT invariants, single-butterfly register rollback, zero dynamic memory allocation, and outer FO failsafe.
- **Target:** Algorithmic arithmetic fault resilience inside the ML-KEM-768 decapsulation engine.

### Paper Track 2: Cross-Layer Fault Interactions & Spacecraft Protocols (DEFERRED)
- **Status:** **DEFERRED** (Separate research direction; artifacts preserved in `experiments/system_model/spacecraft_protocol_sim.py` and `results/spacecraft_protocol_desync_results.json`).
- **Core Question:** How do internal cryptographic failures desynchronize higher-level CCSDS space packet protocols and ground-station state machines?
- **Decision:** Keep distinct from Track 1 to avoid diluting the cryptographic core. Track 2 requires its own systematic channel-fault models before submission.

### Paper Track 3: Persistent State Faults & Twiddle Factor Blindness (INTEGRATED BOUNDARY)
- **Status:** **INTEGRATED AS A THEORETICAL & PILOT BOUNDARY** in Track 1.
- **Core Question:** Can arithmetic invariants detect faults in shared read-only constant memory tables (NTT twiddle factors $\zeta$)?
- **Finding:** Proved mathematically (Theorem 1) that local invariants have exactly $0.0\%$ detection probability against twiddle corruption. Evaluated via a 16-trial pilot (Phase 15Q) demonstrating that outer FO re-encryption catches the resulting ciphertext mismatch.

---

## 4. High-Level Architectural Flow

During ML-KEM-768 decapsulation (`crypto_kem_dec`), the core architecture executes in four protective tiers:

```
                  ┌────────────────────────────────────────┐
                  │ 1. Received Ciphertext c = (c1, c2)    │
                  └──────────────────┬─────────────────────┘
                                     │
                                     ▼
                  ┌────────────────────────────────────────┐
                  │ 2. Unpack u in R_q^3, v in R_q         │
                  └──────────────────┬─────────────────────┘
                                     │
                                     ▼
         ┌────────────────────────────────────────────────────────┐
         │ 3. Polynomial Transforms with Invariant Monitoring     │
         │    - 3 Forward Cooley-Tukey NTTs (vector u)            │
         │    - 1 Inverse Gentleman-Sande NTT (message poly)      │
         │                                                        │
         │    [For each butterfly operation]:                     │
         │    a. Snapshot registers: u_saved, v_saved, zeta_saved │
         │    b. Execute butterfly arithmetic                     │
         │    c. Decoupled Invariant Verification:                │
         │       CT: Delta_sum == 0 && Delta_mul == 0             │
         │       GS: Adder Rail == 0 && Multiplier Rail == 0      │
         │                                                        │
         │    [If Mismatch]:                                      │
         │       retry_count < 2  -> Restore snapshot & retry     │
         │       retry_count >= 2 -> Escalate fail=0xFF, abort    │
         └───────────────────────────┬────────────────────────────┘
                                     │
                                     ▼
                  ┌────────────────────────────────────────┐
                  │ 4. Decrypted Message m'                │
                  └──────────────────┬─────────────────────┘
                                     │
                                     ▼
         ┌────────────────────────────────────────────────────────┐
         │ 5. Fujisaki-Okamoto Re-encryption (c' == c?)           │
         │    - 3 Forward CT NTTs (ephemeral vector r)            │
         │    - 4 Inverse GS NTTs (candidate u', v')              │
         │    - Monitored identically via steps 3a-3c             │
         └───────────────────────────┬────────────────────────────┘
                                     │
                                     ▼
         ┌────────────────────────────────────────────────────────┐
         │ 6. Dual-Rail Ciphertext Verification & Key Selection   │
         │    - Forward ct_memcmp(c, c')                          │
         │    - Reverse-order bitwise dual-rail comparison        │
         │    - Persistent monitor counter escalation check       │
         │                                                        │
         │    fail == 0  -> Emit K_valid (Authentic Key)          │
         │    fail != 0  -> Emit K_rej = SHAKE256(z || c)         │
         │                  (Deterministic Implicit Rejection)    │
         └────────────────────────────────────────────────────────┘
```

---

## 5. Summary of Validated Empirical Claims

All claims below have been independently recomputed from primary CSV and JSON artifacts in the repository:

| Metric / Result | Empirical Value | Denominator / Dataset | Statistical Uncertainty | Supporting Artifact |
| :--- | :---: | :---: | :---: | :--- |
| **Monitored Butterflies** | **9,856** | 11 transforms (6 CT, 5 GS) | Exact count from C call graph | [`indcpa.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/indcpa.c), [`poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c) |
| **Transient Recovery ($F4$)** | **100.0%** | 100 trials | $95\%$ Wilson CI: $[96.30\%, 100.00\%]$ | [`raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv) |
| **Persistent Fail-Stop ($F5A, F5B$)** | **100.0%** | 200 trials (100 each) | $95\%$ Wilson CI: $[98.12\%, 100.00\%]$ | [`raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv) |
| **Clean Control Success ($F12$)** | **100.0%** | 100 trials | $95\%$ Wilson CI: $[96.30\%, 100.00\%]$ | [`raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv) |
| **Production SDC ($H2$)** | **0.00%** | 300 active trials | $95\%$ Wilson CI: $[0.00\%, 1.26\%]$ | [`raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv) |
| **Canonical Campaign SDC** | **0.00%** | 750 active trials (900 total) | 1-sided 97.5% Clopper-Pearson: $\le 0.49\%$ | [`tfib_trial_level_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_trial_level_results.csv) |
| **Circular Verifier Blindness** | **98.5%** | 600 trials across T1–T6 | $95\%$ Wilson CI: $[97.2\%, 99.2\%]$ | [`h1_activation_audit.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/h1_activation_audit.csv) |
| **Latency Overhead (`-O3`)** | **+16.9%** | $N=2{,}000$ warm decapsulations | $129.51\,\mu\text{s}$ vs $110.77\,\mu\text{s}$ ($1.17\times$ slowdown) | [`phase7i_e2e_results.json`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase7i/processed/phase7i_e2e_results.json) |
| **Sequential DMR Benchmark** | **+99.33%** | $N=2{,}000$ iterations | Displayed means: $92.98\,\mu\text{s}$ vs $46.65\,\mu\text{s}$ (+99.31%) | [`phase7h_timing_distribution.json`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase7h/processed/phase7h_timing_distribution.json) |
| **Dynamic Memory Allocation** | **0 B** | Static C source inspection | Zero `malloc`/`free` calls in monitor/rollback | [`poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c), [`mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) |
