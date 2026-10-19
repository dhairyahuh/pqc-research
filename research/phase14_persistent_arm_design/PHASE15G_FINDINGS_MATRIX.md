# Phase 15G — Findings Matrix & Verification Ledger

**Auditor:** Independent Skeptical Cryptographic Research Auditor  
**Audit Target:** Phase 15F Code, Errata, Changelog, and Trial Ledger Architecture  
**Date:** 2026-10-11  
**Target Directory:** `research/phase14_persistent_arm_design/`

---

## Findings Matrix

| Finding ID | Area | Dimension | Status | Severity | Exact Source Reference | Evidence | Impact | Recommended Action |
|:---:|:---|:---|:---:|:---:|:---|:---|:---|:---|
| **F-15G-01** | Check 1 | Invalid-Target Semantics Misattribution | **FAIL** | HIGH | `pilot_runner.c` (lines 475 & 672) | In target bounds failure (`target_idx < -1 \|\| target_idx >= 128`) and unreachable fallback, runner assigns `records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED"`. | Semantically false: trial was aborted prior to execution; no restoration or baseline recheck occurred. Falsely inflates restoration pass metrics and contradicts `crypto_endpoint = "NOT_RUN"` and zeroed `output_ss`. | Refactor assignment to a dedicated truthful status: `NOT_RUN_INVALID_TARGET` (or `NOT_APPLICABLE`). |
| **F-15G-02** | Check 2 | Mixed Diagnostic & CSV Output Stream | **PASS** | MEDIUM | `pilot_runner.c` (lines 465–466, 556–561, 680–703) | Preflight logs, diagnostic trial banners (`--- [DIAGNOSTIC TRIAL %d/16] ---`), and execution traces are printed to `stdout` alongside the summary CSV table. | Directing `stdout` to a file yields a mixed log that fails standard RFC 4180 parsers unless pre-filtered/grepped. | Route diagnostic output to `stderr` or add a `--csv-only` / `--output-ledger <file>` CLI flag in a future phase. |
| **F-15G-03** | Check 2 | Unquoted CSV String Fields | **PASS** | LOW | `pilot_runner.c` (lines 693–702) | `expected_behavior` is printed with `%s` without enclosing double quotes. | Safe for current 16 hardcoded strings (no commas), but fragile if expanded campaign descriptions contain commas. | Update string formatting to use standard RFC 4180 quoting (`\"%s\"`). |
| **F-15G-04** | Check 2 | Authoritative 9-Column Schema Parity | **PASS** | INFORMATIONAL | `pilot_runner.c` (lines 685 & 693–702) | Header and rows emit exactly 9 fields in exact order matching `PHASE15B_TRIAL_LEDGER.csv`: `trial_id,target_idx,bit_mask,mutation_status,consumption_status,crypto_endpoint,restoration_status,output_ss,expected_behavior`. | Establishes 100% schema alignment with historical Phase 15B artifacts. | None required. |
| **F-15G-05** | Check 3 | Hash Provenance Reconciliation | **PASS** | INFORMATIONAL | `PHASE15F_ERRATA.md` (Section 2) | Accurately reconciled historical digests for `PHASE15B_REPORT.md` (`0a530225...`) and `PHASE15B_TRIAL_LEDGER.csv` (`5cf48fb9...`) without altering historical files in place. Superseded hashes clearly noted. | Resolves finding F-15E-10 cleanly and preserves auditable byte history. | None required. |
| **F-15G-06** | Check 4 | Epistemological & Validation Demarcation | **PASS** | INFORMATIONAL | `PHASE15F_CHANGELOG.md` (Sections 3 & 4) | Explicitly partitions static code inspection, Apple Clang compilation, non-mutating oracle check (`--check-oracle`), and unexecuted live fault trials. | Precludes conflating static build correctness with empirical runtime fault resilience. | None required. |

---

## Summary of Findings by Severity

| Severity Level | Count | Finding IDs |
|:---|:---:|:---|
| **CRITICAL** | 0 | None |
| **HIGH** | 1 | **F-15G-01** (Invalid-target restoration status misattribution) |
| **MEDIUM** | 1 | **F-15G-02** (Mixed diagnostic and CSV stream on stdout) |
| **LOW** | 1 | **F-15G-03** (Unquoted CSV string fields) |
| **INFORMATIONAL / PASS** | 3 | **F-15G-04**, **F-15G-05**, **F-15G-06** |

---

## Final Review Recommendation

### **CONDITIONAL — SPECIFIC FINDINGS MUST BE RESOLVED**

**Audit Decision Rationale:**  
Phase 15F successfully resolved the historical hash provenance discrepancies (**F-15E-10**) and aligned the CSV output schema (**F-15E-09**).

However, **Finding F-15G-01** represents a critical semantic defect in the trial ledger data model: assigning `RESTORED_AND_BASELINE_RECHECK_PASSED` to a trial that was aborted prior to execution because of an invalid target index falsely certifies that restoration and baseline cryptographic verification occurred. Before a live feasibility pilot or multi-vector campaign can be authorized:
1. `pilot_runner.c` must be updated to assign `NOT_RUN_INVALID_TARGET` to any pre-execution bounds failure.
2. The binary must be recompiled cleanly and verified in non-mutating mode.

*Mandatory Stop Condition: This audit constitutes a technical review only. Phase 16 campaign planning and live pilot execution remain unauthorized pending resolution of Finding F-15G-01.*
