# Phase 2: ML-KEM Fault Injection Campaign & Step 2C

## 1. Executive Summary
Evaluated fault sensitivity across all 256 coefficients and twiddles. Proved Step 2C countermeasure independence: TFIB protection operates orthogonally to algorithm-level DMR and implicit rejection.

## 2. Phase Objectives
Execute single-bit flip campaigns on ML-KEM-768 NTT; model countermeasure independence.

## 3. Key Documents in this Phase
- [`phase2-mlkem-fault-campaign-audit.md`](file:///Users/dhairyajain/Desktop/pqc research/docs/phases/phase-02/phase2-mlkem-fault-campaign-audit.md)
- [`phase2_step2c_report.md`](file:///Users/dhairyajain/Desktop/pqc research/docs/phases/phase-02/phase2_step2c_report.md)
- [`phase2_step2c_experiment_design.md`](file:///Users/dhairyajain/Desktop/pqc research/docs/phases/phase-02/phase2_step2c_experiment_design.md)
- [`phase2_step2c_dependency_model.md`](file:///Users/dhairyajain/Desktop/pqc research/docs/phases/phase-02/phase2_step2c_dependency_model.md)

## 4. Associated Source Code & Execution Locations
- **Implementation / Harness:** `tfib_experiments/test_step2c_countermeasure_independence.c`
- **Historical Evidence / References:** `results/phase2/`

## 5. Associated Datasets & Artifacts
- **Primary Datasets:** `results/phase2/processed/sensitivity_matrix.csv`

## 6. How to Verify & Reproduce
```bash
./tfib_experiments/test_step2c_countermeasure_independence
```

## 7. Evidence Category
All metrics and claims in this phase are verified under category: **`[DIRECTLY OBSERVED]`**.
