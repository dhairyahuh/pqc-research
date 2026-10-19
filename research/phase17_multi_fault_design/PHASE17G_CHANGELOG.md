# Phase 17G Changelog: Residual Design Clarification and Evidence Audit

**Document:** `research/phase17_multi_fault_design/PHASE17G_CHANGELOG.md`  
**Date:** 2026-10-12  
**Target Specification:** `PHASE17G_RESIDUAL_CLARIFICATION.md`  
**Author:** Independent Cryptographic Software Auditor & Statistical Methodologist  
**Status:** AUDIT COMPLETED — Strictly Read-Only  

---

## 1. Summary of Actions and Deliverables

Phase 17G executed a residual design clarification and evidentiary audit under the **Mandatory Research Integrity and Anti-Hallucination Protocol**. The audit operated under strict read-only constraints:
- No existing source code or prior phase artifacts were modified.
- No binaries were compiled, linked, or executed.
- No virtual memory was mutated.
- No test vectors were generated or validated.
- No experiments or trials were run.
- No Git commits, pushes, cleans, or discards were performed.

Created files:
1. `research/phase17_multi_fault_design/PHASE17G_RESIDUAL_CLARIFICATION.md`
2. `research/phase17_multi_fault_design/PHASE17G_CHANGELOG.md`

All prior artifacts in `research/phase17_multi_fault_design/` (Phases 17, 17B, 17C, 17D, 17E, 17F) were preserved byte-for-byte.

---

## 2. Key Audit Findings by Task

1. **Task 2: Allocation-Status Ambiguity (Section 2):**
   - Formally separated four lifecycle statuses: Arithmetic Consistency (`[INDEPENDENTLY RECOMPUTED]`), Design Specification (`[DIRECTLY OBSERVED]`), Formal Adoption (`[UNKNOWN / UNVERIFIED]`), and Empirical Execution (`[PROPOSED / NOT YET TESTED]`).
   - Determined that while Quota 3 (15 seeds per blocking class) and Quota 4 (5 seeds per control cell) are mathematically consistent and specified in Phase 17F, their formal adoption by a human operator is not established in the record (`[UNKNOWN / UNVERIFIED]`). Retained them as unadopted design proposals.
   - Preserved top-level quotas ($N_1 = 300, N_2 = 40, N_3 = 60, N_4 = 20$; total $N = 420$, $1,680$ matched records).

2. **Task 3: Statistical Target and Clopper–Pearson Bound (Section 3):**
   - Derived the one-sided 95% Clopper–Pearson upper bound formula from first principles: $p_U = 1 - 0.05^{1/n}$.
   - Proved mathematically that obtaining an upper bound strictly below 1.0% requires $n_{\text{completed}} \ge 299$ ($p_U(298) = 1.0002\% \ge 1.0\%$; $p_U(299) = 0.9969\% < 1.0\%$).
   - Defined the boundary rule for $n = 0$: evaluates to `INCONCLUSIVE_NO_COMPLETED_TRIALS` without a numerical bound.
   - Reframed pilot uncertainty: noted that Phase 15Q's 0/16 crash count carries an upper bound of $\sim 18.75\%$, meaning campaign-wide attrition remains unknown.

3. **Task 4: Separation of Protocol Success from Cryptographic Integrity (Section 4):**
   - Defined three distinct outcome families:
     - Family A (Protocol Endpoint): Validly codes crashes as $Y_{\text{proto}} = 0$ (protocol failure).
     - Family B (Cryptographic Integrity Endpoint): Evaluates SDC among completed decapsulations; crashes can NEVER be coded as SDC.
     - Family C (Execution/Reliability Endpoint): Explicitly accounts for crashes, signals, and protection errors.
   - Mandated dual reporting: Cryptographic Integrity Table vs. ITT Reliability Table.

4. **Task 5: Channel-Stratified Estimands and Weighting (Section 5):**
   - Formalized the matched interaction contrast $\Delta_c = p_{11}(c) - p_{10}(c) - p_{01}(c) + p_{00}(c)$ and master-seed pairing.
   - Declared channel-stratified estimates as **PRIMARY**.
   - Declared equal-weight aggregate ($1/7$) as strictly **EXPLORATORY**, clarifying that it represents an artificial theoretical construct rather than a physical link distribution.

5. **Task 6: Channel Terminology and Model Scope (Section 6):**
   - Directly inspected `combined_campaign.c` lines 10–108.
   - Replaced "physical link severance" with **"modeled channel interruption"** (`CH_INTERRUPT`).
   - Re-affirmed that the software harness is a software emulator and does NOT represent a physical RF/radiation experiment or validated space transport stack.

6. **Task 7: Test Vector Provenance and Inventory (Section 7):**
   - Reconciled inventory: Vector 0 is the single existing static NIST KAT on disk (`references/test_vectors/mlkem_expected_kat.h`).
   - Confirmed that zero locally generated vectors exist on disk.
   - Formally designated Vectors 1–419 as runtime preflight generation specifications.

7. **Task 8: Defect Evidence Matrix (Section 8):**
   - Mapped all six defects across lifecycle status, design vs execution resolution, and blocking gates.

8. **Task 9: Gate Decision (Section 9):**
   - Delivered formal verdict: **`CONDITIONAL — DESIGN DECISIONS STILL OPEN`**.
   - Justification: Formal operator adoption of sub-class allocations remains unrecorded; design proposals await operator sign-off.
