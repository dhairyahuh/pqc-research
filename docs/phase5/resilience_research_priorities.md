# Phase 5: Resilience Research Priorities (Analysis Only)

**Phase:** 5 — Cross-Implementation Fault-Surface Validation  
**Date:** October 1, 2026  
**Status:** COMPLETED (ANALYSIS ONLY — NO CODE IMPLEMENTATION)  

---

## 1. Scope Boundary Notice

In strict accordance with Phase 5 guidelines:
- **NO resilience mechanisms have been implemented in Phase 5.**
- This document outlines the prioritized candidate countermeasures derived directly from empirical findings in Phases 1–5, establishing the technical foundation for future resilience phases.

---

## 2. Priority Ranking Matrix

| Priority | Resilience Countermeasure | Target Vulnerability | Overhead Estimate | Feasibility in Flight SW |
|:---:|:---|:---|:---:|:---:|
| **P1** | **Deterministic Decapsulation Dual-Execution / Redundancy** | NTT / accumulator SEUs causing silent session key desync | +90–100% decaps CPU time | High (pure software wrapper) |
| **P2** | **Lightweight Arithmetic Invariant Checksums** | NTT polynomial corruption before compression | +5–12% CPU time, negligible RAM | High (inline algorithm check) |
| **P3** | **Hardware/Software Tri-State Verification Gate** | Single-bit control-flow / return-code flip in `verify()` | <1% CPU time | Very High (redundant boolean checks) |
| **P4** | **Norm Bound Re-evaluation & Hint Integrity Validation** | Signing rejection bypass & biased signature leakage | +8–15% signing CPU time | High |
| **P5** | **Session Key Desync Link Recovery Protocol** | Space-to-ground telemetry lockout from implicit rejection | Protocol level (1 extra RTT on failure) | Moderate (requires ground coordination) |

---

## 3. Justification and Analysis

### 3.1 Priority 1: Dual-Execution / Algorithmic Redundancy for Decapsulation
- **Problem:** Because ML-KEM enforces implicit rejection, any internal fault during decapsulation returns a valid-looking pseudorandom key rather than an explicit error. The ground and space nodes fall out of synchronization.
- **Countermeasure:** Execute decapsulation twice with independent scratchpads, comparing intermediate polynomial hashes or outputs before committing session keys.

### 3.2 Priority 2: Modular Invariant Checks on NTT Outputs
- **Problem:** Full redundant execution doubles latency, which may strain power-constrained CubeSats.
- **Countermeasure:** Evaluate modular sum invariants:
  $$\sum_{i=0}^{255} \hat{a}_i \equiv a_0 \pmod q$$
  This arithmetic invariant holds unconditionally between time-domain and NTT-domain representations and detects single-coefficient errors with high probability at <10% computational overhead.

### 3.3 Priority 3: Hardened Multi-Check Verification Gates
- **Problem:** As demonstrated in Phase 4 and Phase 5, a single memory corruption of a return flag produces a local acceptance of invalid signatures.
- **Countermeasure:** Multi-rail verification using complementary return values (e.g., `0x5A5A` for accept, `0xA5A5` for reject) checked across multiple distinct registers and instructions.
