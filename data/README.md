# Data Directory and Provenance Guide

This directory documents the data architecture, provenance tracking, and storage layout for all raw experimental datasets, processed matrices, and verification outputs across the research phases.

## 1. Directory Structure

```text
data/
├── README.md                           <- This document
├── raw/                                <- Raw experimental outputs and telemetry logs
├── processed/                          <- Aggregated statistical summaries and distributions
└── manifests/
    └── dataset_provenance_manifest.csv <- Cryptographic SHA-256 provenance manifest
```

## 2. Dataset Provenance Manifest

All primary datasets used to substantiate claims in the research manuscript and presentation are cryptographically fingerprinted in [`data/manifests/dataset_provenance_manifest.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/data/manifests/dataset_provenance_manifest.csv).

| Dataset Name | Relative Path | Size (Bytes) | Rows / Records | Generation Phase | Provenance Type |
|---|---|---|---|---|---|
| `tfib_benchmark_raw.csv` | `tfib_benchmark_raw.csv` | 1,376,991 | 15,000 | TFIB / Step 2C-A | Directly Observed Benchmark Data |
| `tfib_trial_level_results.csv` | `tfib_trial_level_results.csv` | 79,936 | 900 | TFIB / Step 2C-A | Directly Observed Experiment Data |
| `tfib_raw_results.csv` | `tfib_raw_results.csv` | 77,468 | 900 | TFIB / Step 2C-A | Directly Observed Experiment Data |
| `raw_production_trials.csv` | `phase18_audit/raw_production_trials.csv` | 38,018 | 400 | Phase 18 | Directly Observed Cleanroom Trials |
| `valid_ciphertext_trials.csv` | `phase11_conformance_audit/valid_ciphertext_trials.csv` | 17,878 | 100 | Phase 11 | Directly Observed Conformance Trials |
| `invalid_ciphertext_trials.csv` | `phase11_conformance_audit/invalid_ciphertext_trials.csv` | 20,710 | 100 | Phase 11 | Directly Observed Conformance Trials |
| `h1_activation_audit.csv` | `phase16_targeted_evidence_closure/h1_activation_audit.csv` | 331,739 | 600 | Phase 16 | Directly Observed Experiment Data |
| `trial_ledger.csv` | `results/phase15q/trial_ledger.csv` | 3,299 | 16 | Phase 15Q | Directly Observed Pilot Trials |
| `phase7h_timing_distribution.json` | `results/phase7h/processed/phase7h_timing_distribution.json` | 583 | JSON | Phase 7H | Processed Benchmark Data |
| `phase7i_e2e_results.json` | `results/phase7i/processed/phase7i_e2e_results.json` | 687 | JSON | Phase 7I | Processed Experiment Data |
| `sensitivity_matrix.csv` | `results/phase2/processed/sensitivity_matrix.csv` | 26,651 | 256 | Phase 2 | Processed Analysis Data |
| `closest_prior_art_comparison.csv` | `docs/audits/evidence-audits/closest_prior_art_comparison.csv` | 2,752 | 10 | Phase 17A | Literature Analysis Data |

## 3. Preserving Functional Locations

To prevent breaking existing test harnesses, benchmark scripts, and C executables, source CSV files are maintained in their native execution locations:
- Phase 18 cleanroom trial CSV is located in [`phase18_audit/raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv).
- Phase 11 conformance trial CSVs are located in [`phase11_conformance_audit/`](file:///Users/dhairyajain/Desktop/pqc%20research/phase11_conformance_audit/).
- Phase 16 Hypothesis 1 trial CSV is located in [`phase16_targeted_evidence_closure/`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/).
- Canonical TFIB experiment and benchmark CSVs remain at the root level where test harnesses execute them.

All files are cataloged and indexed here to guarantee non-destructive research reproducibility.

