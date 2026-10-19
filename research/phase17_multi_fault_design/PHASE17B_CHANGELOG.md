# Phase 17B Changelog: Methodological Corrections to Multi-Fault Design

**Document:** `research/phase17_multi_fault_design/PHASE17B_CHANGELOG.md`  
**Date:** 2026-10-11  
**Target Specification:** `PHASE17_EXPERIMENT_DESIGN.md` $\rightarrow$ Corrected by `PHASE17B_METHODS_CORRECTION.md`  

---

## 1. Summary of Corrections Applied

1. **Statistical Plan Correction (DEF-01, DEF-02):**
   - Reconciled SDC upper-bound formula discrepancy.
   - Defined target bound under one-sided Wilson ($p_U < 0.89\%$) and Clopper-Pearson ($p_U < 0.993\%$) using adjusted $75\%$ Stratum A allocation ($n_{\text{admitted}} = 300$).
   - Explicitly defined the SDC denominator as **Attempt 1 fault-activated decapsulation invocations** ($N_{\text{admitted}}$ independent seeds).
2. **Channel Fault Taxonomy Reconciliation (DEF-03):**
   - Mapped all proposed events directly to the 7 implemented C classes (`CH_BIT`, `CH_TRUNC`, `CH_LOSS`, `CH_DELAY`, `CH_DUP`, `CH_REORDER`, `CH_INTERRUPT`).
   - Classified burst corruption, byte shifts, and padding modifications as subclasses of `CH_BIT` or `CH_TRUNC`.
   - Explicitly specified probability mass across all 7 classes.
3. **Cryptographic Hypothesis Reframing (DEF-04, DEF-05):**
   - Converted "implicit rejection certainty" into a falsifiable empirical hypothesis ($H_{\text{rej}}$).
   - Separated the 4 cryptographic output classes (`EXPECTED_GOLDEN`, `IMPLICIT_REJECTION`, `SDC`, `EXECUTION_FAILURE`).
   - Disentangled local receiver cryptographic verdict from sender-receiver key agreement.
4. **Vector Inventory Verification (DEF-06):**
   - Disclosed that the workspace contains **1 official NIST KAT vector** in `mlkem_expected_kat.h`.
   - Reclassified the remaining test cases as **locally derived deterministic pseudorandom test vectors** generated via FIPS 203 derandomized APIs.
5. **Scientific Claim Boundary Tightening (DEF-07):**
   - Removed unsupported constant-time and physical radiation claims.
   - Grounded the value of Stratum A in non-trivial cryptographic testing of simultaneous ciphertext and twiddle perturbation ($\tilde{c} \times \tilde{\zeta}$).
