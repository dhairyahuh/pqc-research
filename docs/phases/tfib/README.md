# TFIB: Twiddle Factor Integrity Binding

## 1. Executive Summary
Complete implementation and empirical validation of TFIB v2: achieves 100% detection of constant table SEUs, provides microsecond self-healing, and adds only +2.08% runtime overhead.

## 2. Phase Objectives
Proposed v2 countermeasure: ROM hash binding, runtime assertion, self-healing restoration.

## 3. Key Documents in this Phase
- [`tfib_analysis.md`](file:///Users/dhairyajain/Desktop/pqc research/docs/phases/tfib/tfib_analysis.md)
- [`tfib_design.md`](file:///Users/dhairyajain/Desktop/pqc research/docs/phases/tfib/tfib_design.md)
- [`tfib_execution_log.md`](file:///Users/dhairyajain/Desktop/pqc research/docs/phases/tfib/tfib_execution_log.md)
- [`tfib_failure_cases.md`](file:///Users/dhairyajain/Desktop/pqc research/docs/phases/tfib/tfib_failure_cases.md)
- [`tfib_reproducibility_commands.md`](file:///Users/dhairyajain/Desktop/pqc research/docs/phases/tfib/tfib_reproducibility_commands.md)
- [`tfib_validity_audit.md`](file:///Users/dhairyajain/Desktop/pqc research/docs/phases/tfib/tfib_validity_audit.md)

## 4. Associated Source Code & Execution Locations
- **Implementation / Harness:** `tfib_implementation/tfib_ref.c, tfib_experiments/test_step2c_countermeasure_independence.c`
- **Historical Evidence / References:** `tfib_implementation/ and tfib_experiments/`

## 5. Associated Datasets & Artifacts
- **Primary Datasets:** `tfib_trial_level_results.csv, tfib_benchmark_raw.csv, tfib_raw_results.csv`

## 6. How to Verify & Reproduce
```bash
./tfib_experiments/test_step2c_countermeasure_independence
```

## 7. Evidence Category
All metrics and claims in this phase are verified under category: **`[DIRECTLY OBSERVED]`**.
