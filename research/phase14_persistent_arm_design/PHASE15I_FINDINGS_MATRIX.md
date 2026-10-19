# Phase 15I — Findings Matrix & Verification Ledger

**Auditor:** Independent Skeptical C Systems & Cryptographic Research Auditor  
**Audit Target:** Phase 15H Source, Executable, Ledger Schema, and Documentation  
**Date:** 2026-10-11  
**Target Directory:** `research/phase14_persistent_arm_design/`  

---

## Findings Matrix

| Finding ID | Area | Dimension | Status | Severity | Exact Source Reference | Evidence | Impact | Recommended Action |
|:---:|:---|:---|:---:|:---:|:---|:---|:---|:---|
| **F-15I-01** | Task 1 | Invalid-Target Semantics Correction | **PASS** | HIGH (Resolved) | `pilot_runner.c` (lines 475 & 674) | Both bounds check failure (`target_idx < -1 \|\| target_idx >= 128`) and defensive fallback assign `records[t].restoration_status = "NOT_RUN_INVALID_TARGET"`. | Resolves F-15G-01 completely; eliminates false restoration claims on rejected trials. | None required (Resolved). |
| **F-15I-02** | Task 2 | Cleanup Invariant & Status Integrity | **PASS** | HIGH | `pilot_runner.c` (lines 493–645) | Static control-flow trace confirms `RESTORED_AND_BASELINE_RECHECK_PASSED` cannot be reached without passing all 6 transactional cleanup steps (mutation) or baseline verification. | Prevents unverified or partial executions from recording restoration success. | None required (Verified). |
| **F-15I-03** | Task 3 | Trial Metrics Non-Inflation | **PASS** | HIGH | `pilot_runner.c` (lines 472–476) | Rejected records set `mutation_status = "REJECTED"`, `crypto_endpoint = "NOT_RUN"`, `consumption_status = "VERIFIED_NOT_CONSUMED"`, and `output_ss = 00...00`. | Automated parsers filtering by standard success criteria will not inflate counts. | None required (Verified). |
| **F-15I-04** | Task 4 | Authoritative 9-Column Schema Parity | **PASS** | INFORMATIONAL | `pilot_runner.c` (lines 685 & 693–702) | Header and rows emit exactly 9 fields matching `PHASE15B_TRIAL_LEDGER.csv` field order. | Maintains 100% data schema compatibility across phases. | None required (Verified). |
| **F-15I-05** | Task 4 | Mixed Diagnostic & CSV Output Stream | **PASS** | MEDIUM (Open non-blocking) | `pilot_runner.c` (lines 465–466, 556–561, 680–703) | Diagnostic messages and banners are printed to `stdout` alongside summary CSV. | Parsers must filter by header line or CSV regex to extract clean table. | Route diagnostic output to `stderr` or add `--output-ledger` in future release. |
| **F-15I-06** | Task 4 | Unquoted CSV String Fields | **PASS** | LOW (Open non-blocking) | `pilot_runner.c` (line 702) | `expected_behavior` formatted as `%s` without RFC 4180 quotes. | Safe for current 16 hardcoded strings (no commas); fragile if extended to free text. | Add quotes (`\"%s\"`) when expanding campaign descriptors. |
| **F-15I-07** | Task 5 | Cryptographic Hash Verification | **PASS** | INFORMATIONAL | `pilot_runner.c`, `bin/pilot_runner`, `mlkem768_persistent_reloc.o` | Independently recomputed SHA-256 digests match recorded Phase 15H values bit-for-bit. | Guarantees code and binary provenance integrity. | None required (Verified). |
| **F-15I-08** | Task 6 | Binary Derivation & Symbol Linkage | **PASS** | INFORMATIONAL | `bin/pilot_runner` (`nm`, `otool`, `strings`) | Verified inclusion of `_mlk_zetas_page` from `mlkem768_persistent_reloc.o` and `"NOT_RUN_INVALID_TARGET"` string. | Confirms binary was built from inspected source and relocation object. | None required (Verified). |

---

## Summary of Findings by Severity

| Severity Level | Count | Finding IDs | Status |
|:---|:---:|:---|:---:|
| **CRITICAL** | 0 | None | N/A |
| **HIGH** | 3 | **F-15I-01**, **F-15I-02**, **F-15I-03** | **ALL PASS / RESOLVED** |
| **MEDIUM** | 1 | **F-15I-05** (Mixed diagnostic and CSV stream) | Open Non-Blocking |
| **LOW** | 1 | **F-15I-06** (Unquoted CSV string fields) | Open Non-Blocking |
| **INFORMATIONAL** | 3 | **F-15I-04**, **F-15I-07**, **F-15I-08** | **ALL PASS** |

---

## Final Review Recommendation

# **PASS — CORRECTION INDEPENDENTLY VERIFIED**

**Audit Determination:**  
The minimal correction in Phase 15H resolves Finding **F-15G-01**. The invalid-target rejection logic truthfully reports trial status, enforces full fail-closed semantics, preserves the authoritative 9-column CSV ledger schema, and leaves all historical and git-tracked artifacts untouched.

*Mandatory Stop Condition: This verification confirms technical code semantics only. Authorization for live trials or Phase 16 remains withheld.*
