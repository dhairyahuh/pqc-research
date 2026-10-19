# Comprehensive Claim-Evidence Matrix & Research Disposition

**Auditor:** Skeptical Cryptographic Implementation Auditor  
**Date:** October 2026  
**Scope:** Forensic Traceability and Disposition for Proposed Academic Claims  

---

## 1. Primary Claim-Evidence Matrix

| # | Proposed Research Claim | Supporting Source File & Line Range | Experiment & Raw Data Reference | Execution Path | Independent Reproduction Status | Limitations & Alternative Explanations | Recommended Academic Disposition |
| :-: | :--- | :--- | :--- | :---: | :---: | :--- | :---: |
| **1** | **Local recovery verifiers exhibit verifier blindness under snapshot corruption ($H_1$).** | `phase6_reproducer.c`, `phase7_verifier_oracle.c` | Phase 6/7/8/9/10/11 raw CSVs (Targets F1, F2, F3, F6, F9, F10) | Harness Model Only | **Model-Only Finding** | Exercised only via simulated pointer/variable injection; in-tree production binary does not expose snapshot hooks. | **Qualify & Narrow** (Restrict to model scope) |
| **2** | **Native NTT monitor achieves genuine recovery under transient butterfly faults (F4).** | `poly.c:390-393`, `mlkem_fault_hooks.c:250-265` | `phase12_reproducibility_audit/production_reproduction_trials.csv` (Target F4) | Production Binary | **Independently Reproduced** | Tested only for single-bit flips in intermediate $t$; multi-bit or multi-layer bursts not evaluated in production. | **Retain** |
| **3** | **Native NTT monitor enforces safe fail-stop under persistent faults (F5A, F5B).** | `kem.c:484-489`, `mlkem_fault_hooks.c:250-265` | `phase12_reproducibility_audit/production_reproduction_trials.csv` (Targets F5A, F5B) | Production Binary | **Independently Reproduced** | Evaluated via software hook persistence; does not model analog silicon latch-up. | **Retain** |
| **4** | **Decapsulation implicit rejection conforms exactly to FIPS 203 ($K_{\text{bar}} = J(z \parallel c)$).** | `kem.c:513-516`, `symmetric.h:35-36` | `phase11_conformance_audit/invalid_ciphertext_trials.csv`, `verify_oracle.c` | Production Binary & Clean-Room Oracle | **Independently Reproduced** | Evaluated on 100 controlled mutations; verified bit-for-bit against independent Keccak-f[1600]. | **Retain** |
| **5** | **Zero instances of Silent Data Corruption ($H_2 = 0.0\%$) occurred across tested scenarios.** | `kem.c:454-520` (FO comparison loop) | 1,300 total trials across all phases (`recalculated_h1_h2.csv`) | Production Binary & Harness Models | **Independently Reproduced** | Bounded by sample size (95% CI: $[0.0\%, 0.28\%]$); does not prove mathematical impossibility under arbitrary faults. | **Qualify** (State confidence interval bounds) |
| **6** | **Dual-rail verification prevents single-locus predicate bypass in the decapsulation check.** | `kem.c:476-504` | Source inspection and static structural audit | Production Binary Source | **Supported by Existing Evidence** | Susceptible to simultaneous double-faults forcing both rail variables to zero. | **Qualify** (Explicitly state double-fault limit) |
| **7** | **The implementation exhibits constant-time execution across all decapsulation branches.** | `verify.c`, `poly.c` | Source-level use of bitwise mask arithmetic | Production Binary Source | **Unsupported by Current Evidence** | No cycle-accurate timing or dudect leakage tests executed; compiler optimizations can break constant-time source. | **Withdraw** (Pending microarchitectural timing tests) |
| **8** | **The ML-KEM native implementation possesses physical fault resilience.** | None (Software hooks only) | No physical hardware experiments (EMFI/clock glitching) | None | **Unsupported / Contradicted** | Software hooks cannot model physical silicon fault dynamics. | **Withdraw** |
| **9** | **ML-KEM-768 possesses general or unconditional fault tolerance.** | None | Theoretical protocol boundaries | None | **Unsupported / Overstated** | Unconditional fault tolerance is impossible against targeted attacks on comparison registers. | **Withdraw** |

---

## 2. Synthesis of Dispositions

1. **Retain (3 claims):**  
   Claims 2, 3, and 4 are firmly backed by reproducible execution evidence directly against compiled production binaries and verified by independent oracles.
2. **Qualify and Narrow (3 claims):**  
   Claims 1, 5, and 6 must be strictly qualified: Claim 1 applies only to software models of in-place snapshot verifiers; Claim 5 is bounded by empirical confidence intervals; Claim 6 applies only to single-locus predicate flips.
3. **Withdraw (3 claims):**  
   Claims 7 (constant-time certification), 8 (physical hardware resilience), and 9 (general fault tolerance) lack empirical or physical evidence and must be completely removed from publication drafts.
