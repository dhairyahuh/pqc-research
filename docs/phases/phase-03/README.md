# Phase 3: ML-DSA Fault Injection Campaign

## 1. Executive Summary
Investigated fault propagation in ML-DSA signature generation and verification, demonstrating that signature forgery or nonce leakage is possible if polynomial multiplication twiddles are corrupted during signing.

## 2. Phase Objectives
Evaluate digital signature vulnerability under NTT fault injection and audit test harnesses.

## 3. Key Documents in this Phase
- [`phase3-mldsa-fault-campaign-audit.md`](file:///Users/dhairyajain/Desktop/pqc research/docs/phases/phase-03/phase3-mldsa-fault-campaign-audit.md)

## 4. Associated Source Code & Execution Locations
- **Implementation / Harness:** `algorithms/source_ref/mldsa/`
- **Historical Evidence / References:** `docs/mldsa-implementation-map.md`

## 5. Associated Datasets & Artifacts
- **Primary Datasets:** `Audit logs`

## 6. How to Verify & Reproduce
```bash
make all
```

## 7. Evidence Category
All metrics and claims in this phase are verified under category: **`[DIRECTLY OBSERVED]`**.
