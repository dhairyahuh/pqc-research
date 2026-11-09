# Research Phases Master Documentation

This directory provides a consolidated, phase-by-phase chronological archive of the entire PQC Fault Resilience Research Campaign. It spans from initial problem formulation and mathematical modeling through fault injection campaigns, circular dependency discoveries, formal verifier audits, and final cleanroom validation.

## Directory Structure

```text
docs/phases/
├── README.md               <- This document: architecture and overview of phases
├── PHASE_INDEX.md          <- Complete tabular master index of all research phases
├── phase-00/               <- Literature baseline audit, problem formulation, changelog
├── phase-01/               <- Mathematical modeling of NTT butterfly networks & fault propagation
├── phase-02/               <- ML-KEM fault injection campaign, Step 2C countermeasure independence
├── phase-03/               <- ML-DSA fault campaign, digital signature harness audits
├── phase-04/               <- Statistical reanalysis, diffusion laws, spacecraft simulator
├── phase-05/               <- Cross-implementation analysis, trust boundary definition
├── phase-06/               <- Verifier circular dependency discovery, falsification proofs
├── phase-07/               <- Native decapsulation invariants, DMR (+99.33%), inverse NTT (+16.9%)
├── phase-08/               <- Production code path audit and direct symbol linking
├── phase-09/               <- Reproducibility audit and build symbol resolution
├── phase-10/               <- Conformance testing and native reproduction harnesses
├── phase-11/               <- FIPS 203 Section 7.3 implicit rejection oracle conformance (N=100)
├── phase-12/               <- Independent reproducibility and oracle validation
├── phase-13/               <- Evidence audit, baseline reconciliation, and discrepancy checks
├── phase-14/               <- Evidence correction and persistent memory architecture design
├── phase-15/               <- Twiddle corruption pilot study (Phase 15Q, N=16)
├── phase-16/               <- Hypothesis 1 circular verifier vulnerability closure (N=600)
├── phase-17/               <- Prior-art systematic review (17A) and manuscript revision (17B)
├── phase-18/               <- Cleanroom production trial audit (N=400, Gate A vectors)
└── tfib/                   <- Twiddle Factor Integrity Binding (Step 2A, 2B, 2C-A, N=900)
```

## Navigation Guide

1. Consult [`PHASE_INDEX.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/phases/PHASE_INDEX.md) for a summary table of each phase's objectives, code locations, datasets, and verification status.
2. For presentation preparation, refer to the master presentation deliverables in [`docs/presentation/`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/).
3. For architectural and execution details, see [`docs/architecture/`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/architecture/).

