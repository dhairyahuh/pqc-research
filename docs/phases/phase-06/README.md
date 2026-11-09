# Phase 6: Verifier Circular Dependency Discovery & Falsification

## 1. Executive Summary
Critical breakthrough discovery: Inverse-transform sanity verifiers that share the forward NTT twiddle table suffer from circular masking. If twiddles are corrupted, the verifier computes a matching false inverse, blinding the system.

## 2. Phase Objectives
Falsify traditional sanity checks; prove verifiers relying on corrupted twiddles mask faults.

## 3. Key Documents in this Phase
- `docs/phase6/`
- `docs/phase6b/`

## 4. Associated Source Code & Execution Locations
- **Implementation / Harness:** `tests/test_phase6_resilience.py, tests/phase6b/`
- **Historical Evidence / References:** `docs/phase6/ and docs/phase6b/`

## 5. Associated Datasets & Artifacts
- **Primary Datasets:** `Circular dependency formal falsification proofs`

## 6. How to Verify & Reproduce
```bash
python3 tests/test_phase6_resilience.py
```

## 7. Evidence Category
All metrics and claims in this phase are verified under category: **`[DIRECTLY OBSERVED]`**.
