# Contributing & Research Integrity Guidelines

This repository contains critical academic research artifacts, empirical datasets, and cryptographically verified test vectors. All collaborators must adhere to the following mandatory safety and scientific protocols.

## 1. Mandatory Scientific Guardrails
1. **Never Fabricate Data:** Never invent test results, commit hashes, trial numbers, or citations. All numerical claims must be directly traceable to raw CSV/JSON records cataloged in [`data/manifests/dataset_provenance_manifest.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/data/manifests/dataset_provenance_manifest.csv).
2. **Preserve Historical Evidence:** Do not delete or overwrite historical phase reports, raw trial ledgers, or benchmark files.
3. **Evidence Distinction:** Distinguish between:
   - `[DIRECTLY OBSERVED]`: Backed by active test output or repository logs.
   - `[INDEPENDENTLY RECOMPUTED]`: Recalculated from raw datasets.
   - `[REPORTED BY PRIOR PHASE]`: Claimed in earlier notes.
   - `[PROPOSED / NOT IMPLEMENTED]`: Future roadmap ideas.

## 2. Codebase Contribution Rules
1. **Flight Software Standards:** No dynamic heap allocations (`malloc`, `calloc`, `free`) in cryptographic execution paths. Use bounded stack or static buffers.
2. **Deterministic Execution:** Cryptographic operations must remain constant-time and invariant with respect to secret data.
3. **Regression Testing:** Before submitting changes, all core tests must pass:
   ```bash
   make all
   ./bin/test_fips_kats
   ./tfib_experiments/test_step2c_countermeasure_independence
   ./phase18_audit/production_reproducer
   pytest tests/
   ```
4. **Git Discipline:** Do not commit temporary binaries, object files, or unverified changes. Do not use destructive git commands (`git reset --hard`, `git clean -fd`).

