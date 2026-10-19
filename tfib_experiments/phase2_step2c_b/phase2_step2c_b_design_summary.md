# Phase 2 Step 2C-B: Executive Design Summary & Implementation Roadmap (Revision 3)

**Document:** `phase2_step2c_b_design_summary.md`  
**Phase:** Phase 2 Step 2C-B (Experimental Design — Revision 3)  
**Status:** Methodological Design Specification Only (No Implementation or Execution)  
**Date:** 2026-10-04  
**Target:** ML-KEM-768 with Two-Factor Invariant Butterfly (TFIB)  

---

## 1. Executive Summary

This revised design specification defines the experimental methodology for **Phase 2 Step 2C-B (Revision 3)**, resolving all methodological, statistical, and architectural audit findings from independent research review. It establishes a defensible, reproducible software experiment to evaluate whether separating reference twiddle tables from operational constants across linker sections or virtual pages alters fault detection and recovery under a controlled spatial software memory fault model.

### Core Scope Boundaries:
- **Primary Causal Contrast:** Compares Variant A (Collocated), Variant B (Section-Isolated), and Variant C (Page-Isolated) under an operational-table-relative spatial fault model ($L = 512$ bytes, forward-anchored at $A_{\text{op}}$).
- **Separation of Confounders:** Baseline unguarded ML-KEM (Variant 0) and TFIB-META (Variant E) are strictly isolated as contextual/exploratory studies and excluded from the primary layout comparison.
- **Strictly Software Scope:** Layout separation is defined strictly in terms of host linker sections and virtual memory pages. All claims of physical hardware isolation, radiation hardness, single-event latchup immunity, or spacecraft flight qualification are explicitly disclaimed.

---

## 2. Synthesis of Revised Methodological Elements

```
+---------------------------------------------------------------------------------------------------------+
|                                    STEP 2C-B CORE ARCHITECTURE MATRIX                                   |
+--------------------------+------------------------------------------------------------------------------+
| Research Question        | Does linker-section or virtual-page separation between operational and       |
|                          | reference twiddles measurably reduce reference table corruption under an     |
|                          | operational-table-relative spatial software memory fault model?              |
+--------------------------+------------------------------------------------------------------------------+
| Primary Comparison       | - Variant A (Collocated Baseline): Both tables in __TEXT,__const (+448 B gap)|
| (Isolating Placement)    | - Variant B (Section-Isolated): Reference in __DATA_CONST,__tfib_ref        |
|                          | - Variant C (Page-Isolated): Reference on 16 KB page-aligned boundary        |
+--------------------------+------------------------------------------------------------------------------+
| Invariant Factors        | Identical core ML-KEM-768 code, identical TFIB-REF monitoring algorithms,    |
| Across Primary Variants  | identical twiddle constant data, identical PRF test seeds, identical relative|
|                          | fault interval definition I = [A_op, A_op + L) and XOR mask stream.          |
+--------------------------+------------------------------------------------------------------------------+
| Contextual Controls      | - Variant 0: Native ML-KEM without TFIB (contextual baseline)                |
| (Separated from Primary) | - Variant E: TFIB-META with isolated tags (exploratory architecture)         |
+--------------------------+------------------------------------------------------------------------------+
| Spatial Fault Model      | Half-open virtual address interval I = [A_start, A_start + L) anchored at    |
|                          | operational base: A_anchor = vaddr(_mlk_zetas). Bitwise XOR mutation:        |
|                          | mem[a] ^= mask via domain-separated SHAKE-256. Memory protection toggled via |
|                          | vm_protect (macOS) / mprotect (Linux) and restored post-trial.               |
+--------------------------+------------------------------------------------------------------------------+
| Worked Address Example   | - Observed build gap: mlk_zetas (256B) + 192B padding = 448B to tfib_ref.    |
| (Build-Specific Fact)    | - Forward blast L=512B: Corrupts 256B operational + 64B reference (Dual!).   |
|                          | - Centered blast L=512B: Ends at +384B (Spares reference table!).            |
+--------------------------+------------------------------------------------------------------------------+
| Statistical Framework    | McNemar paired test on discordant pairs (n_01 vs n_10); exact binomial test  |
|                          | for n_disc < 25, continuity-corrected chi-square for n_disc >= 25.           |
|                          | Holm-Bonferroni FWER control (alpha_1 = 0.005, alpha_2 = 0.01).              |
|                          | Two-stage sizing: N_pilot = 50, N_conf calculated via Connor (1987) formula. |
|                          | Pre-registered meaningful effect size threshold: Delta_p >= 10.0%.           |
+--------------------------+------------------------------------------------------------------------------+
| Performance Rationale    | Project-defined software engineering constraint: incremental latency overhead|
|                          | over Variant A must be <= 5.0%. Evaluated over 10,000 runs (median, IQR, CI).|
+--------------------------+------------------------------------------------------------------------------+
| Binary Preflight Gate    | 6-point checklist (B-1 to B-6) verifies symbol existence, section assignment,|
|                          | page alignment, size (256B), disassembly disjointness, and anchor address.   |
|                          | Uses link-time accessor function to resolve static symbol without dlsym.     |
+--------------------------+------------------------------------------------------------------------------+
```

---

## 3. Required Implementation-Stage Work (Prior to Execution)

Step 2C-B cannot be executed using the current repository codebase without completing the following technical implementations:

1. **Spatial Memory Fault Injection Engine:**
   - Extend the test harness to manage virtual page protection via `vm_protect` (macOS) / `mprotect` (Linux), apply contiguous XOR byte perturbations across virtual address spans, and cleanly restore pristine oracle data post-trial.
2. **Link-Time Anchor Accessor:**
   - Add an exported anchor function `tfib_get_operational_zetas_anchor()` in `poly.c` test builds to resolve the address of the static twiddle table $A_{\text{op}}$ under ASLR without relying on `dlsym`.
3. **Automated Preflight Verification Suite:**
   - Construct an automated preflight script implementing checks B-1 through B-6 (`nm`, `otool`, `llvm-objdump`) that gates execution and fails closed on any layout discrepancy.

---

## 4. Design Status & Review Verdict

```text
================================================================================
FINAL STEP 2C-B AUDIT VERDICT:
================================================================================
  VERDICT: [DESIGN READY FOR REVIEW]

  - Methodological Design Revision 3 resolves all 6 audit findings.
  - Spatial fault injector semantics are mathematically closed and relative-anchored.
  - Statistical power is grounded in pilot-contingent sample sizing (Connor 1987).
  - Performance threshold (<= 5.0%) is clearly classified as an engineering constraint.
  - Binary preflight checks (B-1 to B-6) are fully specified and fail-closed.
  - Factor isolation between Variants A, B, and C is strictly enforced.
  - Strictly NO code implementation, fault execution, or Git commits were performed.
================================================================================
```
