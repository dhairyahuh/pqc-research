# Phase 17F Changelog: Read-Only Design Defect Resolution

**Document:** `research/phase17_multi_fault_design/PHASE17F_CHANGELOG.md`  
**Date:** 2026-10-12  
**Target Specification:** `PHASE17F_DESIGN_DEFECT_RESOLUTION.md`  
**Author:** Independent Cryptographic Software Auditor & Statistical Methodologist  
**Status:** DESIGN DEFECTS RESOLVED — Strictly Read-Only  

---

## 1. Summary of Actions and Deliverables

Phase 17F applied the **Mandatory Research Integrity and Anti-Hallucination Protocol** to resolve all six open design defects (D-01 through D-06) identified during the Phase 17E consistency audit.

The phase operated under strict read-only constraints:
- No source code was modified or added.
- No binaries were compiled or linked.
- No virtual memory was mutated.
- No trials were executed.
- No Git commits, pushes, cleans, or discards were performed.

Created files:
1. `research/phase17_multi_fault_design/PHASE17F_DESIGN_DEFECT_RESOLUTION.md`
2. `research/phase17_multi_fault_design/PHASE17F_CHANGELOG.md`

All prior artifacts in `research/phase17_multi_fault_design/` (Phases 17, 17B, 17C, 17D, 17E) were preserved byte-for-byte.

---

## 2. Key Resolutions by Task

1. **Task 1: Combinatorial Quota Allocations (D-01 & D-02):**
   - **D-01:** Quota 3 ($N_3 = 60$) sub-classes frozen as exactly 15 master seeds each for `CH_TRUNC`, `CH_LOSS`, `CH_DELAY`, and `CH_INTERRUPT` ($15 \times 4 = 60$ seeds, $240$ matched records).
   - **D-02:** Quota 4 ($N_4 = 20$) control stratum frozen as exactly 5 master seeds per cell in a balanced $2 \times 2$ factorial grid (dormant/sham $\times$ clean/corrupted; $5 \times 4 = 20$ seeds, $80$ matched records).
   - **Arithmetic Reconciliation:** Verified that total master seeds equal $300 + 40 + 60 + 20 = 420$ and total matched records equal $1,200 + 160 + 240 + 80 = 1,680$ without altering primary quota $N_1 = 300$.

2. **Task 2: Statistical Bound & Attrition Policy (D-03 & D-04):**
   - **D-03:** Compared arbitrary sample inflation against keeping $N_1 = 300$ with the shortfall rule. Acknowledged that the repository contains zero empirical evidence supporting a 5% attrition rate (Phase 15Q pilot showed 0/16 crashes). Retained $N_1 = 300$ as the frozen quota and bound the study to the preregistered shortfall rule. Recomputed the exact sensitivity threshold: $n_{\text{completed}} \ge 299$ is required to claim $< 1.0\%$ Clopper–Pearson upper bound; if $n \le 298$, the study reports the realized bound without claiming $< 1.0\%$.
   - **D-04:** Added formal exception rule for $n_{\text{completed}} = 0$: if zero trials complete, $1 - 0.05^{1/0}$ is undefined; the campaign halts with status `TOTAL_CAMPAIGN_EXECUTION_FAILURE` and no bound is claimed.
   - Enforced strict distinction: hardware traps and crashes are availability/reliability failures tracked in the Intention-to-Test ledger, never cryptographic SDC.

3. **Task 3: Protocol Contrast & Heterogeneous Weighting (D-05):**
   - Formalized channel-specific estimands $\hat{\Delta}_c = \hat{p}_{11}(c) - \hat{p}_{10}(c) - \hat{p}_{01}(c) + \hat{p}_{00}(c)$ without assuming $p_{10} = 0$ or $p_{11} = 0$.
   - Declared channel-stratified contrasts as **PRIMARY**.
   - Declared pooled aggregate contrasts as strictly **EXPLORATORY**, requiring equal mechanism weights ($w = 1/7$) to eliminate sample-ratio distortion.
   - Formalized missing data handling: primary analysis uses Intention-to-Test failure imputation ($Y=0$ for crashes); complete-case pairing reported as secondary sensitivity check.

4. **Task 4: Test Vector Provenance & Inventory (D-06):**
   - Verified that exactly ONE static test vector exists in the repository (`references/test_vectors/mlkem_expected_kat.h`, official NIST FIPS 203 KAT).
   - Confirmed that zero locally generated test vectors currently exist as pre-computed files.
   - Formally demarcated Vectors 1–419 as runtime preflight generation specifications, not existing or validated files.

5. **Task 5: Defect Action Verification:**
   - Evaluated D-01 through D-06 across evidence source, design resolution, what is settled by design alone, and what requires future implementation/execution.

6. **Task 6: Defensible Gate Decision:**
   - Delivered formal verdict: **`PASS — READY FOR SEPARATE IMPLEMENTATION REVIEW`**.
   - Confirmed that all design-level decisions are closed on paper, while maintaining the strict boundary that no compilation, memory mutation, or execution is authorized.
