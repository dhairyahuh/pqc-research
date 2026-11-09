# Phase 1: Mathematical Modeling of NTT Butterfly Networks

## 1. Executive Summary
Proved the upper bound of error diffusion: a single corrupted coefficient in layer L propagates to at most 2^L coefficients. Proved that twiddle factor corruption in root stages leads to catastrophic full-polynomial diffusion.

## 2. Phase Objectives
Formalize Cooley-Tukey NTT butterfly equations, error diffusion bounds, and probability bounds.

## 3. Key Documents in this Phase
- [`phase1-mathematical-audit.md`](file:///Users/dhairyajain/Desktop/pqc research/docs/phases/phase-01/phase1-mathematical-audit.md)

## 4. Associated Source Code & Execution Locations
- **Implementation / Harness:** `algorithms/source_ref/mlkem/ntt.c`
- **Historical Evidence / References:** `docs/mathematics/`

## 5. Associated Datasets & Artifacts
- **Primary Datasets:** `Mathematical derivations documented in markdown`

## 6. How to Verify & Reproduce
```bash
make all
```

## 7. Evidence Category
All metrics and claims in this phase are verified under category: **`[DIRECTLY OBSERVED]`**.
