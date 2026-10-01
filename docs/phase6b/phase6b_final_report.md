# Phase 6B Final Report: Independent Validation and Robustness Audit

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Repository:** `https://github.com/dhairyahuh/pqc-research`  
**Phase:** 6B — Independent Adversarial Validation and Scientific Audit  
**Date:** October 1, 2026  
**Status:** COMPLETED  

---

## 1. Executive Summary

Phase 6B conducted an independent, adversarial scientific audit of the software resilience mechanisms, empirical data, and claims reported in Phase 6.

The audit verified that while proposed countermeasures (Candidate A1 duplicate decapsulation, Candidate B NTT projection invariants, and Candidate D multi-rail tokens) operate correctly under clean conditions and catch specific classes of single-register transient upsets, their real-world protection envelopes are substantially more constrained than initially reported:
1. **Candidate B (NTT Invariant) has a 100% blind spot (0% detection)** for symmetric butterfly multiplier faults (`INTERMEDIATE_T`) and twiddle factor faults due to the Universal Parity Cancellation Theorem.
2. **Candidate D (Multi-Rail Gate) was eliminated by compiler optimization** under standard production flags (`-O3`), reducing runtime execution to a single hardware condition test.
3. **Candidate A1 (Duplicate Decapsulation) doubles execution latency (+103.9%)** and provides zero protection against common-mode input corruption or persistent faults.
4. **ML-DSA specific protections** (dual-rail commitment hash) were conceptual designs and remain unverified in compiled C code.

---

## 2. Claim-by-Claim Audit Decision Gate

| Claim / Mechanism | Phase 6 Reported Claim | Phase 6B Audit Finding | Audit Status |
|:---|:---|:---|:---:|
| **NTT Projection Invariant Correctness** | $\sum \hat{p}_{2i} \equiv 128 p_0$ holds for all clean inputs. | Verified mathematically and across 1,000 random inputs ($FP = 0.0\%$). | **REPRODUCED** |
| **NTT Invariant Fault Coverage** | 100% fault detection across all tested NTT faults. | Valid **only** for single asymmetric output registers (`OUTPUT_ADD`). Has 0% detection for multiplier accumulators ($t$) and twiddle factors ($\zeta$). | **SUPPORTED WITH NARROWER SCOPE** |
| **Duplicate Decapsulation Coverage** | 100% detection of decapsulation divergence. | Valid **strictly** for independent single transient SEUs during execution. 0% detection for persistent faults, correlated faults, or pre-existing input buffer corruption. | **SUPPORTED WITH NARROWER SCOPE** |
| **Multi-Rail Status Hardening** | Eliminates single-bit return code vulnerabilities at $d_H = 32$. | True in C source code; **eliminated by compiler optimization** in `-O3` binary disassembly. Requires volatile memory barriers to survive compilation. | **SUPPORTED WITH NARROWER SCOPE** |
| **Spacecraft Link Availability** | 99.9% availability achieved via local retry. | Valid strictly for single transient SEUs ($P_{\text{SEU}} = 0.05$) under ideal retry independence ($q_{\text{pers}} = 0$). Drops to 97.4% under Candidate B's blended detection rate. | **SUPPORTED WITH NARROWER SCOPE** |
| **ML-DSA Verification Protection** | Dual-rail hash recomputation verified in C. | Code existed only as documentation design; only the generic multi-rail token was executed in C harness. | **UNVERIFIED IN C** |
| **Novelty of Incomplete NTT Invariant** | Wholly new mathematical analysis. | Derived from classical ABFT Fourier projection principles (Jou & Abraham 1986); application to FIPS 203 incomplete ring is an engineering contribution. | **SUPPORTED WITH NARROWER SCOPE** |

---

## 3. Evidence-Based Recommendation for Next Research Direction

Based on the audit findings:

### **Recommendation: Continue Resilience Engineering with Refined Scope (Phase 7)**
- **Justification:**
  1. The audit clearly demarcated what works and what fails: Dual-modular redundancy (Candidate A1) provides robust transient fault coverage at ~2x latency overhead, while algebraic checksums (Candidate B) provide ultra-lightweight (+7%) protection for memory/register corruptions but cannot protect the multiplier ALU without auxiliary checks.
  2. Multi-rail control-flow hardening requires explicit compiler barriers (`volatile` / inline asm) to survive optimization.
  3. Proceeding to **targeted resilience engineering (Phase 7)** is justified provided:
     - Candidate B is combined with multiplier parity or bound checks to cover the `INTERMEDIATE_T` blind spot.
     - Multi-rail gates enforce compiler optimization barriers.
     - Redundancy is applied selectively to avoid indiscriminate execution doubling.
- **Alternative Directions Rejected:**
  - *Formal Analysis (Phase 6 Roadmap item):* Formal SMT/CBMC verification would formally prove the parity cancellation blind spot, but would not produce working flight software protections.
  - *Pausing for Further Literature:* The literature on ABFT is sufficiently well-mapped by this audit to proceed with informed engineering.

---

## 4. Repository and Test Verification

- All Phase 6B audit deliverables compiled and tested.
- Existing baseline KATs, Phase 2, Phase 3, Phase 4, Phase 5, Phase 6, and new Phase 6B tests pass with 100% success.
- Repository ready for commit, push, and review.
