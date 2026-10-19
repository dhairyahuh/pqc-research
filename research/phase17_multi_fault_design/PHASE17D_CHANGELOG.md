# Phase 17D Changelog: Final Preregistration Lock

**Document:** `research/phase17_multi_fault_design/PHASE17D_CHANGELOG.md`  
**Date:** 2026-10-11  
**Target Specification:** `PHASE17D_FINAL_PREREGISTRATION.md`  

---

## 1. Summary of Changes and Formal Specifications

1. **Primary Population Frozen (Section 1):**
   - Restricted primary SDC analysis strictly to distinct master seeds in Condition $C_{11}$, Attempt 1, active twiddle mutation ($k \in [1, 127]$, mask $\neq 0$), wire bit mutation via `CH_BIT`, and executed decapsulation.
   - Formally defined a 5-tier Intention-To-Test (ITT) accounting funnel ($N_{\text{assigned}} \to N_{\text{eligible}} \to N_{\text{attempted}} \to N_{\text{completed}} \to N_{\text{analysable}}$).
   - Prespecified rules for handling preflight errors, oracle errors, hardware trap signals, and execution failures without outcome-dependent replacement.
2. **Sampling Plan & Fixed Quotas Frozen (Section 2):**
   - Locked exact fixed quotas: Quota 1 ($N_1 = 300$, primary active `CH_BIT`), Quota 2 ($N_2 = 40$, admitted-clean), Quota 3 ($N_3 = 60$, delivery-blocking), Quota 4 ($N_4 = 20$, negative controls). Total $N = 420$ seeds ($1,680$ trials).
   - Established deterministic sequential pre-allocation filling quotas prior to runtime execution.
   - Prespecified a shortfall rule mandating the reporting of the realized Clopper-Pearson bound if $n_{\text{completed}} < 300$.
3. **Four Matched Conditions Frozen (Section 3):**
   - Defined shared per-seed invariants across all four conditions ($C_{00}, C_{10}, C_{01}, C_{11}$).
   - Disentangled attempt-level fixed parameters (table mutation held across retries) from varying parameters (channel redraw on transient faults).
4. **Oracle and Vector Provenance Frozen (Section 4):**
   - Formally demarcated Vector 0 (1 official NIST KAT vector) from Vectors 1–419 (locally generated deterministic vectors).
   - Specified an automated 4-step cross-implementation preflight verification pipeline (`liboqs` vs SUT).
   - Mandated dynamic rejection oracle evaluation using the exact received wire ciphertext $\tilde{c}$ and per-vector secret seed $z_i$.
5. **Estimands & Statistical Decision Rules Frozen (Section 5):**
   - Prespecified exact one-sided 95% Clopper-Pearson upper bound of $0.9934\%$ ($< 1.0\%$) for $k=0$ at $n=300$.
   - Explicitly acknowledged that $0.9934\%$ does not constitute proof of immunity or zero risk.
   - Specified unconstrained empirical contrast $\hat{\Delta}_{\text{proto}}$ evaluated via paired bootstrap.
6. **Implementation-Gate Review Verdict (Section 6 & 7):**
   - Evaluated 12-item gate checklist: 12/12 PASS.
   - Delivered formal verdict: **`GO TO IMPLEMENTATION REVIEW`** (design locked; no experiment authorized).
