# Phase 15G — Final Read-Only Review of Phase 15F

**Auditor:** Independent Skeptical Cryptographic Research Auditor  
**Audit Target:** Repository state following Phase 15F (`pilot_runner.c`, `PHASE15F_ERRATA.md`, `PHASE15F_CHANGELOG.md`, historical artifacts)  
**Target Repository State:** Git branch `space-resilience-framework` (HEAD: `4a2c4ebf9274a9188db3610a4f8448902caed056`)  
**Mode:** Strictly Read-Only Audit (Zero compilation, zero live trials, zero fault injection, zero file modifications outside audit reports)  
**Date:** 2026-10-11  
**Deliverable Directory:** `research/phase14_persistent_arm_design/`

---

## Executive Summary

This independent read-only review inspected the implementation and documentation produced during Phase 15F. In accordance with audit standards, all claims in Phase 15F documents were treated as unverified claims subject to direct code and artifact verification.

### Core Audit Determinations:
1. **Invalid-Target Semantics Defect (DEFECT CONFIRMED):** In `pilot_runner.c` (lines 475 & 672), when an invalid target index (`target_idx < -1 || target_idx >= 128`) fails closed, the runner assigns `records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED"`. This semantic assignment is **misleading**. No memory unprotection, mutation, restoration, or baseline decapsulation recheck ever occurred. It falsely certifies that a restoration procedure was executed and passed.
2. **Authoritative Ledger Schema (SCHEMA COMPATIBLE, MIXED STDOUT):** The CSV writer data structures now emit exactly 9 fields in the exact order matching historical `PHASE15B_TRIAL_LEDGER.csv`. However, because this table is printed to `stdout` following verbose diagnostic messages, stdout as a whole is a mixed diagnostic/ledger stream rather than a pure standalone RFC 4180 CSV file.
3. **Hash and Provenance Integrity (PASS):** `PHASE15F_ERRATA.md` correctly reconciled the historical transcription errors in `PHASE15D_REPORT.md` for `PHASE15B_REPORT.md` (`0a530225...`) and `PHASE15B_TRIAL_LEDGER.csv` (`5cf48fb9...`) without altering historical documents in place. The timing and scope of superseded hashes for `pilot_runner.c` and `bin/pilot_runner` were clearly demarcated.
4. **Validation Claims Separation (PASS):** Phase 15F reports properly segregated static code inspection, clean compilation, non-mutating oracle checks, and baseline KAT tests. No live trials or physical fault tolerance claims were made.

---

## 1. Audit of Invalid-Target Semantics in `pilot_runner.c`

### 1.1 Code Inspection of Target Validation
Inspection of `pilot_runner.c` lines 468–477:
```c
/* Complete Target Bounds Check before calculating addresses or unprotecting */
if (pilot_specs[t].target_idx < -1 || pilot_specs[t].target_idx >= 128) {
    fprintf(stderr, "BOUNDS CHECK FAIL: Invalid target_idx %d in trial %d (valid targets: -1 for baseline, 0..127 for twiddles). Failing closed.\n",
            pilot_specs[t].target_idx, t);
    records[t].mutation_status = "REJECTED";
    records[t].consumption_status = "VERIFIED_NOT_CONSUMED";
    records[t].crypto_endpoint = "NOT_RUN";
    records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED";
    continue;
}
```
And lines 668–675 (defensive unreachable branch):
```c
} else {
    /* Defensive unreachable branch: fail closed */
    records[t].mutation_status = "REJECTED";
    records[t].consumption_status = "VERIFIED_NOT_CONSUMED";
    records[t].crypto_endpoint = "NOT_RUN";
    records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED";
    continue;
}
```

### 1.2 Analysis of the Semantics Defect
The assignment `records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED"` upon pre-trial bounds failure is **semantically false and misleading**:
1. **No Restoration Occurred:** The trial was aborted prior to address calculation or memory unprotection. There was no mutation applied, so no restoration procedure was ever executed.
2. **No Baseline Recheck Occurred:** The post-trial decapsulation baseline KAT recheck was never run for this trial.
3. **Internal Data Inconsistency:** In the emitted ledger row, `crypto_endpoint` is `"NOT_RUN"`, and `output_ss` is all zeros (`0000000000000000000000000000000000000000000000000000000000000000`), yet `restoration_status` asserts that a baseline KAT recheck passed.
4. **Downstream Aggregation Hazard:** Any automated auditor or script aggregating trial results by filtering `restoration_status == "RESTORED_AND_BASELINE_RECHECK_PASSED"` would falsely count an invalid, unexecuted trial as a successfully restored and verified run.

### 1.3 Audit Determination & Recommended Status
While bounds checking successfully prevents invalid memory operations (failing closed), the status label must accurately reflect that the trial was not executed.
* **Defect Severity:** HIGH (Semantic misattribution in trial ledger).
* **Recommended Concrete Status:**
  `NOT_RUN_INVALID_TARGET` (or `NOT_APPLICABLE` / `NOT_RUN`).
  For bounds failures and defensive abort branches, the ledger row should record:
  - `mutation_status`: `"REJECTED"`
  - `consumption_status`: `"VERIFIED_NOT_CONSUMED"`
  - `crypto_endpoint`: `"NOT_RUN"`
  - `restoration_status`: `"NOT_RUN_INVALID_TARGET"`

---

## 2. Ledger Correctness and Schema Compatibility

### 2.1 Schema Verification
Inspection of the CSV generation logic in `pilot_runner.c` (lines 680–704):
* **Header (line 685):**
  `trial_id,target_idx,bit_mask,mutation_status,consumption_status,crypto_endpoint,restoration_status,output_ss,expected_behavior`
  Exactly 9 comma-separated fields.
* **Row Formatting (lines 693–702):**
  `printf("%d,%d,0x%04x,%s,%s,%s,%s,%s,%s\n", ...)`
  Exactly 9 comma-separated format specifiers in the documented order.
* **Comparison with Historical Phase 15B CSV:**
  The schema exhibits 100% field count and column name parity with `PHASE15B_TRIAL_LEDGER.csv`.

### 2.2 Field Safety: Commas, Quotes, and Newlines
* `expected_behavior` strings in `pilot_specs[16]` (lines 225–240) were checked:
  - None contain commas.
  - None contain double quotes.
  - None contain carriage returns or newline characters.
* *Observation:* The printf statement formats strings with `%s` rather than RFC 4180 quotes (`\"%s\"`). While safe for the 16 predeclared strings, future test campaigns with free-text descriptions containing commas would break parsing unless quoted.

### 2.3 Diagnostic Messages vs Machine-Readable Stream
Inspection of runner stdout demonstrates:
1. Lines 465–466: `--- [DIAGNOSTIC TRIAL %d/16] %s ---`
2. Lines 556–560: `Injected value: ...`, `Output SS: ...`, `Restoration: ...`
3. Lines 682–684: Section header text preceding the CSV header.

**Audit Determination:**
The summary ledger block is schema-compatible with `PHASE15B_TRIAL_LEDGER.csv`. However, because it is printed to `stdout` along with diagnostic logs, stdout is a **mixed diagnostic stream**. Downstream automated ingestion must either grep for the header line or parse lines matching `%d,%d,0x%04x,...`. In a future release, diagnostic logs should be routed to `stderr` or the ledger written to a standalone file (`--output-ledger <file>`).

---

## 3. Hash and Provenance Integrity

### 3.1 Review of `PHASE15F_ERRATA.md`
Inspection of `PHASE15F_ERRATA.md` confirms:
1. **Accurate Path References:** All reconciled digests refer to explicit repository paths (`research/phase14_persistent_arm_design/PHASE15B_REPORT.md` and `PHASE15B_TRIAL_LEDGER.csv`).
2. **Historical Byte Preservation:** The errata document explicitly notes that the actual historical files have remained unchanged on disk with digests:
   - `PHASE15B_REPORT.md`: `0a5302256db2e5b3f70df1820e21f15ac509fa07e1044d02d6a0dda727554e37`
   - `PHASE15B_TRIAL_LEDGER.csv`: `5cf48fb9ab869cff6345eb1b8d03785ec65d3ab1c2ee76cab29d4ea6bde45d2c`
   The erroneous digests in `PHASE15D_REPORT.md` (`c6bb...` and `7973...`) were correctly identified as documentation transcription errors, not modified files.
3. **Timing and Scope of Superseded Artifacts:**
   The updates to `pilot_runner.c` (`ea253b5b...`) and `bin/pilot_runner` (`8de41e4a...`) made during Phase 15F are clearly designated as **SUPERSEDED** relative to Phase 15D, preventing anachronistic hash claims.

---

## 4. Validation Claims Separation

Inspection of `PHASE15F_CHANGELOG.md` confirms strict epistemological boundaries:
* **Separation of Modes:** The changelog explicitly partitions:
  - Static code inspection of bounds and data structures.
  - Apple Clang compilation (`-O3 -Wall -Wextra -std=c11`).
  - Read-only, non-mutating oracle check (`--check-oracle`).
  - Unexecuted live fault trials.
* **Absence of Overstated Inferences:** The changelog does **not** infer live physical fault resilience from software compilation or non-mutating execution. It clearly states that zero memory mutations were executed.

---

## Final Review Verdict

## **CONDITIONAL — SPECIFIC FINDINGS MUST BE RESOLVED**

### Rationale:
The provenance reconciliation in `PHASE15F_ERRATA.md` and the 9-column CSV ledger alignment successfully resolve Findings F-15E-09 and F-15E-10.

However, **Finding F-15G-01** (assigning `RESTORED_AND_BASELINE_RECHECK_PASSED` to pre-execution invalid-target rejections) represents a critical semantic contradiction in the trial ledger data model. Before any live feasibility pilot or campaign execution is authorized:
1. `pilot_runner.c` must be updated to assign a dedicated, truthful restoration status (e.g., `NOT_RUN_INVALID_TARGET`) when bounds checking rejects a trial.
2. The runner must be recompiled cleanly and verified in non-mutating mode.

*Mandatory Stop Condition: This audit constitutes a technical review only. Phase 16 campaign planning and live pilot execution remain unauthorized pending resolution of Finding F-15G-01.*
