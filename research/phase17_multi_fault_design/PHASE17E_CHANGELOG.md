# Phase 17E Changelog: Independent Preregistration Consistency Audit

**Document:** `research/phase17_multi_fault_design/PHASE17E_CHANGELOG.md`  
**Date:** 2026-10-11  
**Audit Target:** `PHASE17D_FINAL_PREREGISTRATION.md`  
**Auditor:** Independent Statistical & Cryptographic Software Auditor  
**Status:** AUDIT COMPLETED — Strictly Read-Only  

---

## 1. Summary of Audit Scope and Deliverables

Phase 17E performed a rigorous, adversarial consistency audit of the Phase 17D Final Preregistration Lock. In accordance with strict audit guardrails, no C implementation code was written or modified, no binaries were compiled, no memory was mutated, and no experiments were executed.

The audit produced:
- `research/phase17_multi_fault_design/PHASE17E_INDEPENDENT_AUDIT.md`
- `research/phase17_multi_fault_design/PHASE17E_CHANGELOG.md`

All prior artifacts across Phases 17, 17B, 17C, and 17D were verified byte-for-byte and preserved unchanged.

---

## 2. Key Audit Findings by Category

1. **Primary Denominator & ITT Accounting (Section 1):**
   - Traced the 5-tier accounting funnel ($N_{\text{assigned}} \to N_{\text{eligible}} \to N_{\text{attempted}} \to N_{\text{completed}} \to N_{\text{analysable}}$).
   - Formally defined the target SDC population as conditional on surviving completed decapsulations with active twiddle and wire bit corruption (`CH_BIT`).
   - Mandated separate dual reporting: Cryptographic SDC table vs. Intention-to-Test Total Failure table to prevent conditioning/survival bias.
   - Identified and resolved the boundary defect where $n_{\text{completed}} = 0$ results in division by zero in the Clopper–Pearson shortfall formula.
   - Enforced strict distinction: hardware traps and execution crashes are reliability failures, not cryptographic SDC.

2. **Quota Allocation & Combinatorial Integrity (Section 2):**
   - Verified that top-level quota arithmetic matches exactly ($300 + 40 + 60 + 20 = 420$ seeds; $420 \times 4 = 1,680$ records).
   - Identified two residual combinatorial specification gaps:
     - Quota 3 ($N_3 = 60$) omitted the per-class integer breakdown among `CH_TRUNC`, `LOSS`, `DELAY`, and `INTERRUPT`. Frozen at 15 seeds per sub-class.
     - Quota 4 ($N_4 = 20$) omitted the $2 \times 2$ grid partition (dormant/sham $\times$ clean/corrupted). Frozen at 5 seeds per cell.

3. **Matched Four-Condition Estimand (Section 3):**
   - Formalized the paired data structure $\mathbf{Y}_i = (Y_{i, 00}, Y_{i, 10}, Y_{i, 01}, Y_{i, 11})$.
   - Verified that $\hat{\Delta}_{\text{proto}}$ is unconstrained and does not assume $p_{10} = 0$.
   - Identified that unweighted pooling across Quotas 1–3 creates an arbitrary mixture of heterogeneous channel baselines; mandated channel-stratified reporting and explicit stratum weighting.
   - Formulated missing-data rules: primary protocol analysis uses ITT failure imputation ($Y=0$ for crashes), with complete-case analysis as a sensitivity check.

4. **Channel Harness Semantics Audit (Section 4):**
   - Directly inspected `research/combined_harness/combined_campaign.c` lines 98–130.
   - Confirmed that `CH_BIT` is the sole class corrupting ciphertext bytes delivered to decapsulation.
   - Confirmed that `CH_DUP` and `CH_REORDER` invoke decapsulation with clean ciphertexts.
   - Confirmed that `CH_TRUNC`, `CH_LOSS`, `CH_DELAY`, and `CH_INTERRUPT` terminate prior to decapsulation (`decaps_ran = 0`).

5. **Oracle and Vector Provenance (Section 5):**
   - Confirmed that only 1 static NIST KAT vector exists in the repository (`references/test_vectors/mlkem_expected_kat.h`). Clarified that Vectors 1–419 are specifications for future runtime generation and preflight verification, not pre-existing static files.
   - Directly inspected `tfib_experiments/phase11_oracle/independent_oracle.c` lines 59–79; verified that $z$ is extracted from `sk[2368..2399]` and hashed with the exact wire ciphertext $\tilde{c}$.
   - Directly inspected `tfib_experiments/phase11_oracle/fips202_ref.c`; confirmed it is a genuinely distinct, clean-room TweetFIPS-202 Keccak implementation.

6. **Statistical Inference & Confidence Bounds (Section 6):**
   - Independently calculated the exact one-sided 95% Clopper–Pearson upper bound at $n=300$ as $0.9936\%$ ($< 1.0\%$).
   - Highlighted zero-buffer attrition sensitivity: at $n=299$, $p_U = 0.9969\%$; at $n=298$, $p_U = 1.0002\% \ge 1.0\%$. Quota 1 permits at most one execution failure before exceeding the $< 1.0\%$ threshold.
   - Re-affirmed that confidence bounds represent empirical sample limits, not mathematical proofs of immunity.

7. **Gate Evidence Re-Classification & Verdict (Sections 7, 9, 10):**
   - Re-classified Phase 17D gate items G-01 through G-12 into objective evidentiary classes.
   - Delivered formal verdict: **`CONDITIONAL — SPECIFIC DESIGN DEFECTS REMAIN`**.
   - Tabulated six specific defects (D-01 through D-06) with concrete closing requirements.
