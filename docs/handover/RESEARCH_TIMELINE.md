# Research Timeline & Evolution

**Repository:** `pqc-research`  
**Active Branch:** `space-resilience-framework`  
**Author:** Dhairya Jain  
**Handover Recipient:** Ayush  
**Date:** October 2026  

---

## 1. Overview of Project Epochs

The research in this repository developed across six distinct historical epochs:

```
Epoch 1: Baseline Architecture & Internal Fault Setup (Commits cba1780 -> e42d35f)
   │
   ▼
Epoch 2: Exploratory Foundations & Cross-Algorithm Studies (Phases 0 -> 4)
   │
   ▼
Epoch 3: Layered ML-KEM Fault Resilience Prototyping (Phases 5 -> 7L)
   │     [Checkpoint Tag: pqc-ntt-fault-resilience-v1 on commit 8b2382d]
   ▼
Epoch 4: Formal Systematic Redesign & Cleanroom Auditing (Phases 8 -> 18)
   │
   ▼
Epoch 5: TFIB Step 2 Independence Campaigns (Steps 1 -> 2C-A, Commits 673190d -> 4a2c4eb)
   │
   ▼
Epoch 6: Evidence Reconciliation & Manuscript Surgical Auditing (Phases 2C -> 2S)
```

---

## 2. Chronological Timeline of Historical Milestones

### Epoch 1: Baseline Architecture & Space Systems Simulation
- **Commit `cba1780` — Initial Baseline (Steps 1–10):**
  Established the initial ML-KEM and ML-DSA implementations, modular arithmetic routines, and project layout.
- **Commit `92c08af` — Phase 4A Level 1 Fault Campaign:**
  Implemented dual-path architecture (Path A: reference C; Path B: native optimized) and initial cross-validation testbeds.
- **Commit `e42d35f` — Phase 4B Internal Fault Injection & Spacecraft Protocol Sim:**
  Added internal ML-KEM-768 arithmetic fault hooks, standalone FIPS KAT test runner (`tests/test_fips_kats.c`), and the CCSDS spacecraft protocol desynchronization simulator (`experiments/system_model/spacecraft_protocol_sim.py`).

### Epoch 2: Mathematical Foundations & Multi-Algorithm Surveys (Phases 0–4)
- **Phase 0 (`docs/phase0-changelog.md`):** State-of-the-art literature audit of fault-injection attacks on lattice-based cryptography.
- **Phase 1 (`docs/phase1-mathematical-audit.md`):** Formal mathematical derivation of polynomial ring arithmetic over $R_q = \mathbb{Z}_{3329}[X]/(X^{256} + 1)$ and Cooley-Tukey butterfly arithmetic.
- **Phase 2 (`docs/phase2-mlkem-fault-campaign-audit.md`):** Preliminary software fault injection across ML-KEM components.
- **Phase 3 (`docs/phase3-mldsa-fault-campaign-audit.md`):** Exploration of NTT and signature-level fault injection on ML-DSA (FIPS 204).
- **Phase 4 (`docs/phase4-*`):** Cross-algorithm comparison, space system implications, and preliminary statistical confidence methodology.

### Epoch 3: Layered ML-KEM Fault Resilience Prototyping (Phases 5–7L)
- **Phase 5 (`docs/phase5/`):** Characterization of cross-implementation fault surfaces and ALU-level injection points.
- **Phase 6 & 6B (`docs/phase6/`, `docs/phase6b/`):** Targeted resilience evaluation; verification that unshielded checks fail when registers are shared.
- **Phase 7 & 7B (`docs/phase7/`, `docs/phase7b/`):** Prototyping layered fault resilience on ML-KEM decapsulation.
- **Phase 7C (`docs/phase7c/`):** Implementation of oracle-free native decapsulation monitoring.
- **Phase 7D & 7E (`docs/phase7d/`, `docs/phase7e/`):** Verification of early-stage NTT fault recovery.
- **Phase 7G (`docs/phase7g/`):** Integration of forward NTT Cooley-Tukey invariant monitoring directly into native decapsulation C routines.
- **Phase 7H (`docs/phase7h/`):** Isolated benchmarking of native monitored decapsulation against sequential DMR. Produced `results/phase7h/processed/phase7h_timing_distribution.json` ($N=2,000$), recording $+99.33\%$ DMR overhead (mean $92.98\,\mu\text{s}$ vs $46.65\,\mu\text{s}$).
- **Phase 7I (`docs/phase7i/`):** Extension to Inverse Gentleman-Sande NTT monitoring. Recorded 9,856 total butterflies across 11 transforms in `results/phase7i/processed/phase7i_e2e_results.json`. Historical run logged $+135.3\%$ DMR overhead due to an experimental artifact (monitors active during duplicate pass).
- **Phase 7J, 7K, 7L (`docs/phase7j-l/`):** Independent validation of combined monitoring, publication evidence audit, and literature gap analysis.
- **Checkpoint Tag `pqc-ntt-fault-resilience-v1` (`8b2382d`):** Preserved the complete Phase 7 prototype baseline.

### Epoch 4: Systematic Research Redesign & Deep Auditing (Phases 8–18)
- **Commits `fd82ad3`, `d3517dc`, `ca38dec`:** Systematic literature matrix, adversarial audit, and formulation of Research Tracks 1, 2, and 3.
- **Phase 8 & 9 (`phase8_production_path_audit/`, `phase9_reproducibility_audit/`):** Audited the production compilation path and independent reproduction pipelines.
- **Phase 10 & 11 (`phase10_corrected_reproduction/`, `phase11_conformance_audit/`):** Corrected test harnesses; produced the 100-trial invalid ciphertext KAT dataset (`invalid_ciphertext_trials.csv`) validating $100\%$ conformant implicit rejection.
- **Phase 12 & 13 (`phase12_reproducibility_audit/`, `phase13_final_evidence_audit/`):** Reframed claims away from overbroad hardware claims; radiation scoping analysis.
- **Phase 14 & 15 (`phase14_evidence_correction/`, `phase15_final_evidence_validation/`):** Hardened assertions; page-isolated twiddle factor table design (`zetas.inc`).
- **Phase 15Q (`results/phase15q/`):** Dedicated 16-trial pilot on a reference test vector evaluating twiddle factor memory corruption. Confirmed Theorem 1 (local invariant blindness) and outer FO containment (11 active consumed mutations deterministically forced implicit rejection).
- **Phase 16 (`phase16_targeted_evidence_closure/`):** Evaluated circular-verifier blindness across 600 trials (`h1_activation_audit.csv`), demonstrating a $98.5\%$ false-pass rate ($591/600$) when checkers consume faulted live registers.
- **Phase 17, 17A, 17B (`phase17_prior_art/`, `phase17a_verification/`, `phase17b_corrected/`):** Comprehensive prior-art comparison, draft manuscript blueprint, and citation audit.
- **Phase 18 (`phase18_audit/`):** Cleanroom production trial audit. Generated `raw_production_trials.csv` across 400 production trials (100 F12, 100 F4, 100 F5A, 100 F5B).

### Epoch 5: TFIB Step 2 Independence Campaigns (Commits 673190d -> 4a2c4eb)
- **Step 1 & 2A (`tfib_experiments/`):** Integration tests and independent input validation.
- **Step 2B (`tfib_experiments/phase2_step2b_*`):** Remediation of CSPRNG seeding in keygen and runner mutation checks.
- **Step 2C / 2C-A (Commits `673190d`, `c1bfb15`, `4a2c4eb`):** Countermeasure independence validation across the 900-trial canonical campaign (`tfib_trial_level_results.csv`: 150 controls, 750 active trials; $0$ SDC, $1$-sided $97.5\%$ Clopper-Pearson upper bound: $0.49\%$). Clarified test label definitions.

### Epoch 6: Evidence Reconciliation & Manuscript Surgical Auditing (Phases 2C–2S)
- **Phase 2C (`paper/manuscript.md.backup_phase2c`):** Working manuscript baseline.
- **Phase 2E (`backup_phase2e`):** First-round qualification of empirical evidence; removed unsubstantiated hardware claims.
- **Phase 2G (`backup_phase2g`):** Explicitly distinguished software architectural fault injection from physical semiconductor radiation mechanisms, adding Dodd & Massengill [P01] citations.
- **Phase 2I (`backup_phase2i`):** Disclosed that primary benchmark records were recorded on Apple M3 Pro, while binary reproduction occurred under macOS Darwin 27.0.0.
- **Phase 2K (`backup_phase2k`):** Added Table 1 detailing the authoritative call graph of all 11 polynomial transforms ($9,856$ butterflies).
- **Phase 2N (`backup_phase2n`):** Separated production suite ($N=400$, 300 active) from canonical campaign ($N=900$, 750 active) and KAT conformance ($N=100$).
- **Phase 2P (`backup_phase2p`):** Corrected Table 2 provenance footnote to prevent confusing Row H2 with an independent raw data target; clarified $0.0101\%$ single-butterfly operation ratio vs end-to-end execution time.
- **Phase 2Q (2Q.1–2Q.4):** Read-only audit of SDC definitions and circular-verifier predicates.
- **Phase 2Q.3 (`backup_phase2q`):** Surgically corrected Table 3 aggregate circular-verifier Wilson interval to $[97.2\%, 99.2\%]$ ($591/600$).
- **Phase 2R (2R.1–2R.2):** Final consistency and allocation-claim evidence audit.
- **Phase 2R.3 (`backup_phase2r` -> `paper/manuscript.md`):** Surgically replaced overstrong Table 4 footnote assertion with: *"Source inspection found no dynamic memory allocation calls in the butterfly monitoring and rollback routines under the evaluated configuration."*
- **Phase 2S:** Read-only final review. Recomputed all statistical intervals and verified that the manuscript is **READY WITH EXPLICIT LIMITATIONS**.
