# Phase 14B Changelog: Design Corrections and Blocker Resolutions

**Date:** 2026-10-11  
**Author:** Skeptical Cryptographic Implementation & Experimental Methodology Reviewer  
**Context:** Phase 14B Design Review & Blocker Closure  

---

## 1. Summary of Actions
This changelog documents all additions and modifications made during Phase 14B to resolve the seven design blockers identified during the skeptical implementation review.

* **Repository Integrity:** No source files (`algorithms/`, `experiments/`, `tests/`), Makefiles, campaign code, raw results, or manuscripts were modified. The pre-existing seven tracked modifications and all historical hashes remain 100% intact.
* **Scope:** All modifications are confined strictly to `research/phase14_persistent_arm_design/`.

---

## 2. New Deliverables Created

### `PHASE14B_REVIEW.md` (Created)
* Comprehensive standalone document resolving all seven issues:
  1. **Mach-O Layout:** Delineates source attributes vs linked `LC_SEGMENT_64` segment permissions (`initprot` vs `maxprot`). Defines binary inspection with `otool -l` and runtime query via `vm_region_64`.
  2. **Page Isolation:** Documents direct host verification of 16 KB page size (`16384` bytes) via `pagesize`. Explains why alignment alone is insufficient and introduces `mlk_isolated_zetas_page_t` with 16,128 bytes of explicit padding.
  3. **Compiler Semantics & UB:** Eliminates ISO C99 §6.7.3 undefined behavior by declaring the research storage non-const in C and enforcing read-only semantics at the OS virtual memory layer. Details disassembly and mathematical sensitivity evidence plans for runtime consumption.
  4. **Baseline Equivalence:** Defines multi-stage equivalence gates (NIST KAT 100% pass, 1,000 clean test vectors bit-identical, and disassembly diffing). Defines acceptable relocation displacement vs unacceptable inner-loop codegen divergence.
  5. **Disaggregated Trial Ledger & Endpoint Contract:** Establishes the 9-column disaggregated schema (`fault_requested`, `activation_verified`, `target_bytes_changed`, `consumption_verified`, `restoration_verified`, `crypto_validity`, `endpoint_outcome`, `sdc_determination`, `hygiene_failure`). Formulates exact FIPS 203 endpoint contract separating $K_{golden}$, valid implicit rejection ($K_{rej}$), and SDC.
  6. **Pilot Justification:** Formally defines the 16-trial pilot as an engineering feasibility and protocol hygiene qualification, not a statistically powered distribution estimate.
  7. **Approval Boundary:** Demarcates verified existing baseline facts from unbuilt research build hypotheses.

### `PHASE14B_CHANGELOG.md` (Created)
* This document, tracking all changes across Phase 14 design artifacts.

---

## 3. Updates to Existing Phase 14 Deliverables

### `DESIGN_REVIEW.md` (Updated)
* **Section 3.2 & 5.1:** Updated memory structure from `const int16_t mlk_zetas[128]` with alignment attribute to `mlk_isolated_zetas_page_t` containing 128 non-const twiddle factors and 16,128 bytes of explicit page padding.
* **Section 5.2:** Updated accessors in `poly.c` to point directly to `mlk_zetas_page.zetas`.
* **Section 7:** Expanded risk analysis to include linked segment `maxprot` verification and ISO C UB elimination.

### `BINARY_VERIFICATION_PLAN.md` (Updated)
* **Check 2:** Added inspection of linked executable `LC_SEGMENT_64` commands via `otool -l` to verify `maxprot >= 0x03` before attempting `vm_protect`.
* **Check 3:** Added automated symbol co-location check via `nm -n` to verify no other program symbols fall within the 16 KB window `[page_addr, page_addr + 16384)`.
* **Check 4:** Added disassembly diffing check (`diff -u`) comparing baseline `mlkem768.o` against `mlkem768_persistent_reloc.o` to detect forbidden loop alterations or spill changes.
* **Runtime Sanity Check:** Updated runtime pseudocode to query `vm_region_64` for `max_protection` before calling `vm_protect`.

### `EXPERIMENT_PROTOCOL.md` (Updated)
* **Section 1.1:** Added explicit methodological justification for the 16-trial pilot as a feasibility and hygiene test, detailing what it can and cannot conclude.
* **Section 4:** Replaced the previous 6-state taxonomy with the disaggregated 9-column ledger schema (`fault_requested`, `activation_verified`, `target_bytes_changed`, `consumption_verified`, `restoration_verified`, `crypto_validity`, `endpoint_outcome`, `sdc_determination`, `hygiene_failure`).
* **Section 4.1 & 4.2:** Added explicit mathematical formulations for FIPS 203 decapsulation outputs ($K_{golden}$ vs $K_{rej}$) and demarcated SDC from valid implicit rejection and recovery.

### `GO_NO_GO_CRITERIA.md` (Updated)
* **Gate 1:** Added Hard NO-GO criteria for linked segment `maxprot < 0x03`, symbol co-location on the 16 KB page, and codegen discrepancies in NTT loop schedules.
* **Gate 2:** Added Hard NO-GO criteria for any corruption detected in the 16,128-byte page padding.

### `PHASE14_REPORT.md` (Updated)
* Updated formal recommendation and ledger to reflect Phase 14B findings, the new `PHASE14B_REVIEW.md`, and the revised proposed source diff.
