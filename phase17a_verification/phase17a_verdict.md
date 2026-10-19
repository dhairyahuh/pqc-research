# Phase 17A Verdict: Prior-Art Verification and Manuscript Integrity Audit

**Audit Completion Date:** October 2026  
**Audited Artifacts:** `phase17_prior_art/` (all 7 files) and `phase16_targeted_evidence_closure/`  
**Verdict Authority:** Phase 17A Independent Integrity Audit  

---

## 1. Executive Summary

This audit evaluated the bibliographic integrity, prior-art differentiation, and empirical claim veracity of the Phase 17 research deliverables and manuscript draft (`phase17_prior_art/manuscript_draft.md`).

### Overall Audit Verdict: **CONDITIONAL PASS — REQUIRES TARGETED CORRECTIONS**

The core empirical findings of the research (the software-level dual-invariant checking, localized butterfly rollback, 100/100 transient fault recovery, 200/200 safe aborts, and 0/300 production SDC) are **strictly verified and directly supported** by the Phase 16 evidence baseline and source code.

However, the audit identified **two unverified citations (P09 and P13)**, **three major bibliographic inaccuracies (P03, P04, P15)**, and several **novelty claims that overreach** without acknowledging equivalent hardware-level mathematical principles in prior art (notably Paul et al. 2026). 

The manuscript is **not ready for immediate submission** in its current form, but will be fully defensible once the specific corrections categorized below are applied.

---

## 2. Categorization of Claims and Findings

### Category A: Claims Sufficiently Supported for the Manuscript
The following claims have complete, traceable evidence from the Phase 16 baseline and underlying C source implementation:

1. **Transient Fault Recovery:** 100/100 genuine, localized recoveries under transient 1-bit multiplier faults ($F4$) in ML-KEM-768 decapsulation without triggering full re-encapsulation or session termination (verified in `mlkem_fault_hooks.c:264-276` and `recovery_counter_source_audit.md`).
2. **Persistent / High-Frequency Abort:** 200/200 safe aborts under recurring bit-inversion ($F5A$, 6 injections) and force-value ($F5B$, zeroed multiplier outputs), correctly routing execution to constant-time pseudo-random implicit rejection.
3. **Silent Data Corruption (SDC) Elimination:** Zero SDC instances observed across 300 active software fault-injection trials in production code (95% Wilson score confidence interval: $[0.0\%, 1.26\%]$).
4. **FIPS 203 Implicit Rejection Integrity:** 100/100 invalid ciphertext mutations produce outputs matching the reference specification oracle identically, confirming no leakage of decapsulation failure indicators.
5. **Dual-Rail Defense in Fujisaki-Okamoto Re-encryption:** Verification of ciphertext equality via dual-rail comparison loops (`kem.c:476-504`) correctly thwarts skipping and comparison-bypass faults.
6. **Mathematical Formulation of Gentleman-Sande (GS) Invariant:** The algebraic relation $r_0 + \zeta \cdot r_1 \equiv 2u \pmod q$ for inverse NTT butterflies is mathematically sound and verified.
7. **Threat Model Scope:** The explicit restriction to non-adversarial single-event upsets (SEUs) in space radiation environments is sound and correctly delineates why conditional retry is permissible, avoiding conflict with Statistical Ineffective Fault Attacks (SIFA).

---

### Category B: Claims Requiring Narrower Wording
The following claims are conceptually sound but currently overstated, risking hostile peer review:

1. **Novelty Claim 1 (Dual-Transform Invariant Monitoring):**
   - *Current Formulation:* Claims to introduce the first algebraic invariant verification framework for NTT butterflies.
   - *Issue:* Paul et al. (P03, ACM TECS 2026) published algebraic invariant checking (FR-AIC/PR-AIC) for forward Cooley-Tukey butterflies on FPGA. The underlying mathematical check ($r_0 + r_1 \equiv 2u \pmod q$) is identical in principle.
   - *Required Action:* Narrow claim to: *"the first software-level resilience framework combining both forward Cooley-Tukey and inverse Gentleman-Sande algebraic invariants with localized rollback and retry within a NIST FIPS 203 implementation."*
2. **Novelty Claim 2 (Circular Verifier Blindness):**
   - *Current Formulation:* Claims circular verifier blindness is a "novel failure mode."
   - *Issue:* Corrupted redundancy in shared memory is a well-known failure mechanism in fault tolerance literature (common-mode failure).
   - *Required Action:* Reframe as: *"We identify and quantify a critical instance of common-mode verification failure in NTT butterfly monitoring, termed circular verifier blindness, where co-located memory snapshots are corrupted alongside live execution states..."*
3. **Novelty Claim 3 (Monitoring + Retry + Implicit Rejection Combination):**
   - *Required Action:* Explicitly state in the Abstract and §2 that the viability of retry hinges strictly upon the non-adversarial threat model; acknowledge that under active physical fault injection (SIFA), retry leaks secret key information.
4. **Literature Survey Scope:**
   - *Current Formulation:* Described in Phase 17 as an "exhaustive" or "systematic review."
   - *Required Action:* Reframe as a "targeted literature survey of PQC fault-tolerance mechanisms."

---

### Category C: Claims Requiring Additional Evidence / Provenance
The following quantitative statements in the draft are plausible but lack direct backing in the Phase 16 evidence closure documents:

1. **Execution Latency Overhead (`+25.3%`):** Must cite the specific benchmarking methodology (macOS ARM64, clang -O3, 10,000 decapsulation cycles).
2. **DMR Comparison Baseline (`+149%`):** Must clarify whether this was an empirical test wrapper or an analytical model ($2.49\times T_0$).
3. **Side-Channel Timing Ratio (`1.0005×`):** Must provide the sample size and measurement variance or qualify it as preliminary microbenchmarking.
4. **Butterfly Count Breakdown (`9,856`):** Must add the arithmetic step showing $11 \times 896$ butterflies across the InvNTT, NTT, and FO re-encryption stages.

---

### Category D: Claims and Citations That Must Be Withdrawn or Replaced
The following entries are invalid and cannot appear in an academic publication:

1. **Withdraw Reference P09:** A. El Bizri et al., *"Balancing PQC overhead and efficiency in non-terrestrial networks,"* IEEE ICC 2026. This paper cannot be verified and appears to be a hallucinated/synthetic citation. Replace with verified literature (e.g., Kim P08 or ESA/ECSS reports).
2. **Replace Reference P13:** T. Fritzmann et al., *"Towards Fault-Tolerant Post-Quantum Cryptography: Hardware and Software Approaches for RISC-V,"* *IEEE Access* 2020. The DOI does not resolve and the paper does not exist as cited. Replace with:  
   *T. Fritzmann, P. Sasdrich, and T. Güneysu, "Towards Reliable and Secure Post-Quantum Co-Processors based on RISC-V," in DATE 2019.*  
   Simultaneously withdraw the claim that Fritzmann proposed an invariant detection/abort engine (DATE 2019 evaluates fault sensitivity/SDC rates).
3. **Correct Reference P04:** Change venue from IEEE TCSI to IEEE TCAD (2023), fix author list to Sarker, Cintas Canto, Mozaffari Kermani, and Azarderakhsh, and correct title.
4. **Correct Reference P15:** Change first author from "N. Lahr" to Samy Amer et al. (IEEE S&P 2025).
5. **Correct Reference P03:** Update publication year from 2024 to 2026.

---

## 3. Publication Readiness Assessment

| Evaluation Dimension | Status | Notes |
|:---|:---|:---|
| **Core Scientific Findings** | **VERIFIED** | Experimental results (F4, F5A, F5B, SDC, FO) are authentic and robust. |
| **Mathematical Correctness** | **VERIFIED** | CT and GS invariant derivations are completely sound. |
| **Bibliographic Integrity** | **FAILED (Remediable)** | 2 critical invalid citations (P09, P13) must be replaced/excised; 3 major metadata errors require correction. |
| **Novelty Framing** | **CONDITIONAL** | Needs narrower wording to acknowledge Paul et al. (P03) and general common-mode failure principles. |
| **Phase 16 Baseline Conformance** | **VERIFIED** | Denominator of 300, 0 SDC, Wilson score CI, and 100/100 recoveries match Phase 16 baseline. |

---

## 4. Next Phase Roadmap

With the completion of Phase 17A, the audit process is officially closed. No broad research campaigns or additional experimental expansions are required.

The path to submission consists of three concrete steps:
1. **Apply Tier 1 & Tier 2 Corrections:** Implement the exact edits detailed in `correction_recommendations.md` directly into `references.md`, `prior_art_matrix.csv`, and `manuscript_draft.md`.
2. **Select Publication Venue:** Submit to an appropriate aerospace/dependability or applied crypto venue (e.g., *IEEE Transactions on Aerospace and Electronic Systems (TAES)*, *IEEE Transactions on Dependable and Secure Computing (TDSC)*, *IEEE Aerospace Conference*, or *CHES/CARDIS* depending on emphasis).
3. **Final Manuscript Packaging:** Compile final PDF, bundle verification code, and prepare the submission package.
