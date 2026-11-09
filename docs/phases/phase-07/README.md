# Phase 7: Native Decapsulation Invariants & Benchmarks

## 1. Executive Summary
Benchmarked complete decapsulation pipelines on Apple M3 Pro. Full DMR incurred +99.33% overhead, inverse NTT checking incurred +16.9%, motivating the need for an ultra-lightweight (<3%) ROM-bound integrity countermeasure.

## 2. Phase Objectives
Implement native decapsulation invariants, benchmark DMR (+99.33%) and inverse NTT (+16.9%).

## 3. Key Documents in this Phase
- `docs/phase7/`
- `docs/phase7b/`
- `docs/phase7h/`
- `docs/phase7i/`
- `docs/phase7k/`

## 4. Associated Source Code & Execution Locations
- **Implementation / Harness:** `tests/phase7k/test_phase7k_reproducibility.py`
- **Historical Evidence / References:** `docs/phase7*/`

## 5. Associated Datasets & Artifacts
- **Primary Datasets:** `results/phase7h/processed/phase7h_timing_distribution.json, results/phase7i/processed/phase7i_e2e_results.json`

## 6. How to Verify & Reproduce
```bash
python3 tests/phase7k/test_phase7k_reproducibility.py
```

## 7. Evidence Category
All metrics and claims in this phase are verified under category: **`[DIRECTLY OBSERVED]`**.
