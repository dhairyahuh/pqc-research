# Comprehensive Repository Map & Directory Guide

**Repository:** `pqc-research`  
**Active Branch:** `space-resilience-framework`  
**Author:** Dhairya Jain  
**Handover Recipient:** Ayush  
**Date:** October 2026  
**Total File Inventory:** 1,562 files across 43 top-level directories  

This document provides an exhaustive structural and navigational guide to the repository. Ayush can use this map to locate source code, datasets, harnesses, historical phase records, and documentation without breaking dependencies.

---

## 1. Top-Level Directory Distribution

The table below details every top-level directory, its file count, primary purpose, and status:

| Directory | Files | Category | Purpose & Description | Preservation Status |
|:---|:---:|:---|:---|:---|
| [`algorithms/`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/) | 253 | Source Code | Instrumented C implementations of ML-KEM and ML-DSA, native optimized routines, fault hooks, and Python OQS bindings. | **CANONICAL CORE** — Do not move |
| [`bin/`](file:///Users/dhairyajain/Desktop/pqc%20research/bin/) | 49 | Build Artifacts | Compiled object files (`.o`) and executable test binaries. Gitignored by default. | Generated build outputs |
| [`deploy_perf_bundle/`](file:///Users/dhairyajain/Desktop/pqc%20research/deploy_perf_bundle/) | 266 | Bundled Asset | Historical deployment and performance package bundling data, source, and documentation for distribution. | Preserved historical package |
| [`docs/`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/) | 153 | Documentation | Technical documentation, phase changelogs (Phases 0–7L), and handover records (`docs/handover/`). | **CANONICAL DOCS** |
| [`experiments/`](file:///Users/dhairyajain/Desktop/pqc%20research/experiments/) | 56 | Harnesses | Fault injection harnesses (`mlkem768_internal_fault_experiment.c`) and spacecraft protocol simulations (`spacecraft_protocol_sim.py`). | **CANONICAL HARNESSES** |
| [`fault_injection/`](file:///Users/dhairyajain/Desktop/pqc%20research/fault_injection/) | 5 | Framework | Python fault injection definitions (`fault_definitions.py`) and outcome taxonomies. | **CANONICAL CORE** |
| [`literature/`](file:///Users/dhairyajain/Desktop/pqc%20research/literature/) | 19 | Literature | PDFs of foundational papers (Dodd & Massengill, Ravi et al.), candidate shortlists, and review templates. | Reference literature |
| [`paper/`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/) | 26 | Manuscript | Current working manuscript (`manuscript.md`), 9 phase backups (`backup_phase2c` through `backup_phase2r`), BibTeX references, figures, and tables. | **CANONICAL PUBLICATION** |
| [`papers/`](file:///Users/dhairyajain/Desktop/pqc%20research/papers/) | 3 | Roadmaps | Research track maps for Paper Track 1, Track 2, and Track 3. | Track definitions |
| [`research/`](file:///Users/dhairyajain/Desktop/pqc%20research/research/) | 216 | Research Records | Evidence ledger (`EVIDENCE_LEDGER.md`), earlier manuscript drafts (`manuscript_v1`), reframing reports, and radiation scoping notes. | Preserved research records |
| [`research_redesign/`](file:///Users/dhairyajain/Desktop/pqc%20research/research_redesign/) | 24 | Gap Analysis | Systematic research gap reports, literature matrices, and candidate research questions. | Strategic research design |
| [`results/`](file:///Users/dhairyajain/Desktop/pqc%20research/results/) | 63 | Processed Data | Performance distributions (`phase7h/`), end-to-end metrics (`phase7i/`), twiddle pilot records (`phase15q/`), and protocol desync results. | **CANONICAL RESULTS** |
| [`tests/`](file:///Users/dhairyajain/Desktop/pqc%20research/tests/) | 37 | Test Suites | FIPS 203/204 Known Answer Test runners (`test_fips_kats.c`, `kat_mlkem*.c`, `kat_mldsa*.c`). | **CANONICAL TESTS** |
| [`tfib_experiments/`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/) | 70 | Experiment Suite | Step 1, Step 2A/B/C experiment harnesses, runners, PRF seeds, and audit logs. | **CANONICAL TFIB EXPERIMENTS** |
| [`tfib_implementation/`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/) | 9 | Library | TFIB core C library source files and headers (`libtfib.a`). | **CANONICAL LIBRARY** |
| Root Directories (`phase*`) | 200+ | Audit Records | 19 root-level phase audit directories (`phase10_...` through `phase18_audit`). Contain trial CSVs and markdown audit reports. | Preserved historical audits |
| Review Packages | 22 | Review Archives | `Step2C_A_Final_Review_Package/` and `Step2C_A_Test_Label_Fix_Review/`. | Preserved review archives |
| Miscellaneous Root Files | 32 | Root Assets | Master indexes, raw benchmark CSVs (`tfib_benchmark_raw.csv`), trial CSVs, Makefile, README.md, AYUSH.md. | Core repository root |

---

## 2. Navigating Key Subdirectories

### 2.1 Core Implementation (`algorithms/`)
- `algorithms/source_ref/mlkem/`: Reference ML-KEM C implementation modified with resilience instrumentation.
  - `src/poly.c`: NTT transformations (`mlk_poly_ntt`, `mlk_poly_invntt_tomont`) with fault monitoring and register snapshot/rollback hooks.
  - `src/kem.c`: Top-level decapsulation (`mlk_kem_dec_monitored`) featuring reverse dual-rail ciphertext verification and deterministic implicit rejection.
  - `src/indcpa.c`: Core encryption and decryption routines containing the 11 transform call sites.
  - `src/zetas.inc`: Twiddle factor constant table, including research memory-relocated page-isolated arm.
- `algorithms/source_ref/mlkem_fault_hooks.c` & `.h`: Decoupled invariant checking logic ($\Delta_{\text{sum}}, \Delta_{\text{mul}}$, adder rail, multiplier rail), register snapshotting, and rollback retry engine.
- `algorithms/source_ref/mldsa_fault_hooks.c` & `.h`: Prototype fault hooks for ML-DSA.

### 2.2 Manuscript & Publication (`paper/`)
- `paper/manuscript.md`: The active, fully audited research manuscript (SHA-256: `bb6d138a463347153385c69a6e7f2bf133708cdb8738ba66a325e420d58e0b4d`).
- `paper/manuscript.md.backup_phase2*`: 9 sequentially preserved manuscript backups documenting the exact evolution from Phase 2C through Phase 2R.
- `paper/references.bib`: 18 curated BibTeX entries.
- `paper/tables/` & `paper/figures/`: Publication assets.

### 2.3 Primary Raw Datasets
- `phase18_audit/raw_production_trials.csv`: 400 cleanroom production trial records (F12, F4, F5A, F5B).
- `phase11_conformance_audit/invalid_ciphertext_trials.csv`: 100 invalid-ciphertext KAT conformance trials.
- `phase16_targeted_evidence_closure/h1_activation_audit.csv`: 600 circular-verifier blindness trials across T1–T6.
- `tfib_trial_level_results.csv`: 900 canonical campaign trials (150 clean controls, 750 active fault trials).
- `results/phase15q/trial_ledger.csv`: 16 twiddle factor mutation pilot trials (11 active consumed).
- `results/phase7h/processed/phase7h_timing_distribution.json`: Phase 7H isolated baseline vs DMR timing distributions.
- `results/phase7i/processed/phase7i_e2e_results.json`: Phase 7I end-to-end timing metrics and butterfly counts.

### 2.4 Experiment Runners & Test Suites
- `phase18_audit/production_reproducer.c`: Standalone C reproduction harness for production binaries.
- `tests/test_fips_kats.c`: Deterministic NIST FIPS 203 & 204 KAT test runner.
- `experiments/fault_injection/mlkem768_internal_fault_experiment.c`: Internal fault simulation harness.
- `tfib_experiments/tfib_experiment_runner.c`: Core runner for TFIB campaign executions.

---

## 3. Documentation Coverage Report

A fresh inspection of the repository confirms:
- **Total Files Inventoried:** 1,562 files.
- **Files Substantively Reviewed:** All active source files in `algorithms/`, all manuscript drafts in `paper/`, all primary datasets in `phase18_audit/`, `phase11_conformance_audit/`, `phase16_targeted_evidence_closure/`, `results/`, and `tfib_experiments/`, all top-level Makefiles and experiment scripts.
- **Files Indexed & Mapped:** 100% of repository files are categorized by directory and file extension.
- **Tool-Generated / Build Artifacts:** `bin/` (49 files) and `.o` files (22 files) are recognized as transient build outputs and properly gitignored.
- **Historical Packages:** Packages such as `deploy_perf_bundle/` (266 files), `chatgpt/` (6 files), and root-level `phase*` folders are identified as historical artifacts and preserved without destructive reorganization.
- **Unknown Files:** Exactly 0 files have unknown or untraceable origins.
