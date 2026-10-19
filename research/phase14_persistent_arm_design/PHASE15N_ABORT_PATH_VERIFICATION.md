# Phase 15N — Abnormal Termination and Incomplete-Run Verification

**Auditor:** Independent Skeptical Cryptographic Systems Auditor  
**Audit Target:** Control-Flow, Signal Trapping, Termination, and Incomplete-Run Reporting in `pilot_runner.c`  
**Target Repository State:** Git branch `space-resilience-framework` (HEAD: `4a2c4ebf9274a9188db3610a4f8448902caed056`)  
**Audit Mode:** Strictly Read-Only Systems Audit (Zero compilation, zero execution, zero memory mutation)  
**Date:** 2026-10-11  
**Deliverable Path:** `research/phase14_persistent_arm_design/PHASE15N_ABORT_PATH_VERIFICATION.md`  

---

## Executive Summary & Core Determination

This audit resolves the specific question:
> **Core Question:**  
> Can any abnormal or failed trial reach summary reporting in a way that makes an incomplete run look complete, or makes an unexecuted trial appear restored?

### Summary of Audit Findings:
1. **Can an unexecuted trial appear restored?**  
   **NO.** All unexecuted trials ($t+1 \dots 15$) retain uninitialized zero values from `memset(records, 0, sizeof(records))` (line 457). When emitted, their restoration status evaluates to `"UNKNOWN"`. A failed trial ($t$) records `RESTORATION_FAILED` (line 641) or `UNKNOWN` (line 499). Under no condition can an unexecuted or failed trial receive `RESTORED_AND_BASELINE_RECHECK_PASSED`.
2. **Can an incomplete run look complete?**  
   **YES — TO A NAIVE OPERATOR OR INGESTION SCRIPT.**  
   If an in-loop failure triggers an abort via `break;` (line 501 or line 643):
   - The loop terminates prematurely, but control falls through directly to the CSV summary printer (lines 680–703).
   - The summary generator iterates for all 16 indices, printing exactly 16 rows.
   - The runner then executes `return 0;` (line 705), **exiting with return code 0**.
   - A naive operator or script checking only the process return code (`$? == 0`) or counting emitted CSV lines (`wc -l == 17`) will falsely interpret the incomplete run as successful.
3. **Correction of Phase 15M Claim:**  
   Phase 15M stated: *"Aborted runs never print the summary CSV and cannot record false restoration."*  
   - This statement is **partially inaccurate and overgeneralized**.
   - It is **TRUE** for signal abortions (`SIGBUS`/`SIGSEGV`, where `_exit` immediately kills the process) and preflight failures (where `return 1;` terminates before the loop).
   - It is **FALSE** for in-loop error aborts (`break;` at line 501 and line 643). In those cases, the summary CSV **is printed** and the process exits with **code 0**.

### Audit Verdict: **CONDITIONAL**
The code prevents false restoration claims, but because in-loop aborted runs emit 16 CSV rows and return code 0, **rigorous operator-side validation checks are mandatory** to distinguish incomplete runs from complete runs.

---

## 1. Exhaustive Control-Flow Analysis of Termination and Abort Points

The table below catalogs every `return`, `exit`, `break`, and `continue` statement in `pilot_runner.c`:

| Location | Statement | Context | Table State at Execution | Process Exit Code | Summary CSV Printed? |
|:---|:---:|:---|:---|:---:|:---:|
| **Line 202** | `_exit(128 + sig)` | Signal handler (`handle_trap_signal`) | Potentially Writable / Modified | `128 + sig` (138/139) | **NO** |
| **Line 299** | `return 1;` | Oracle empty-string KAT mismatch | Pristine RO | `1` | **NO** |
| **Line 316** | `return 1;` | Oracle `malloc` failure | Pristine RO | `1` | **NO** |
| **Line 334** | `return 1;` | Oracle $K_{rej}$ derivation mismatch | Pristine RO | `1` | **NO** |
| **Line 340** | `return 0;` | Non-mutating `--check-oracle` mode | Pristine RO | `0` | **NO** |
| **Line 350** | `return 1;` | Preflight 1: Symbol pointer NULL | Pristine RO | `1` | **NO** |
| **Line 359** | `return 1;` | Preflight 1: 16 KB alignment failure | Pristine RO | `1` | **NO** |
| **Line 374** | `return 1;` | Preflight 2: `vm_region_64` failure | Pristine RO | `1` | **NO** |
| **Line 392** | `return 1;` | Preflight 2: Region address mismatch | Pristine RO | `1` | **NO** |
| **Line 396** | `return 1;` | Preflight 2: Page not readable | Pristine RO | `1` | **NO** |
| **Line 400** | `return 1;` | Preflight 2: Max protection not writable | Pristine RO | `1` | **NO** |
| **Line 407** | `return 1;` | Preflight 3: Initial table memcmp mismatch | Pristine RO | `1` | **NO** |
| **Line 416** | `return 1;` | Preflight 3: Padding canary non-zero | Pristine RO | `1` | **NO** |
| **Line 425** | `return 1;` | Preflight 4: RW dry-run toggling failure | Pristine RO | `1` | **NO** |
| **Line 431** | `return 1;` | Preflight 4: RO dry-run toggling failure | Pristine RO | `1` | **NO** |
| **Line 439** | `return 1;` | Preflight 5: Baseline decapsulation error | Pristine RO | `1` | **NO** |
| **Line 443** | `return 1;` | Preflight 5: Baseline KAT shared secret mismatch | Pristine RO | `1` | **NO** |
| **Line 476** | `continue;` | Bounds check rejection (`target_idx < -1 \|\| >= 128`)| Pristine RO | N/A (Skips trial) | At normal end |
| **Line 501** | `break;` | Step 1: `vm_protect(RW)` failure | Pristine RO (Unmodified) | **0 (via line 705)** | **YES (16 rows)** |
| **Line 643** | `break;` | Cleanup Step 1–6 failure | Unverified / Corrupted | **0 (via line 705)** | **YES (16 rows)** |
| **Line 675** | `continue;` | Defensive fallback branch | Pristine RO | N/A (Skips trial) | At normal end |
| **Line 705** | `return 0;` | Normal completion of `main()` | Restored Pristine RO | `0` | **YES (16 rows)** |

---

## 2. Detailed Trace of the Five Execution Scenarios

### Path 1: Normal Completion After Successful Restoration
- **Source Lines:** Lines 459–677 (loop body), lines 637–640 (cleanup verification), lines 680–705 (CSV generation).
- **Sequence of Actions:**
  1. For each mutation trial $t$:
     - Table is unprotected to RW (`vm_protect`, line 494).
     - Mutated twiddle is written (`vtable[idx] = target_val`, line 507).
     - Read-back verified (`readback_val == target_val`, line 511).
     - Page reprotected to RO (`vm_protect`, line 521).
     - Decapsulation executed and classified (`EXPECTED_OUTPUT`, `REJECTION`, `DIFFERENT_OUTPUT`, or `NO_OUTPUT`).
     - Cleanup Steps 1–6 execute: table value restored to `orig_val`, read-back matches, page reprotected to RO, live `vm_region_64` verifies read-only status, table canary matches golden zetas, padding canary confirms zero bytes, baseline KAT decapsulation reproduces golden secret.
     - Line 638 sets `records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED"`.
  2. For baseline trials ($t = 0$ and $t = 15$):
     - Line 660 sets `records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED"`.
  3. Loop finishes all 16 trials ($t = 0 \dots 15$).
  4. Lines 686–703 emit exactly 16 valid rows, each with distinct sequential `trial_id` ($0 \dots 15$), expected statuses, valid output hashes, and `RESTORED_AND_BASELINE_RECHECK_PASSED`.
  5. Line 705 executes `return 0;`.

---

### Path 2: Handled Error Followed by Successful Cleanup
- **Scenario A: Pre-Execution Target Bounds Rejection**
  - **Source Lines:** Lines 468–477.
  - **Sequence:** If `target_idx < -1 || target_idx >= 128`, lines 472–475 set `mutation_status = "REJECTED"`, `consumption_status = "VERIFIED_NOT_CONSUMED"`, `crypto_endpoint = "NOT_RUN"`, `restoration_status = "NOT_RUN_INVALID_TARGET"`.
  - Line 476 executes `continue;`.
  - Output ledger row for trial $t$ explicitly records `NOT_RUN_INVALID_TARGET`. Loop continues to completion.
- **Scenario B: Post-Mutation Read-Back Mismatch or Reprotection Failure**
  - **Source Lines:** Lines 509–527 & 534–554.
  - **Sequence:**
    - If `readback_val != target_val` (line 514): `mutation_applied = 0`.
    - If `vm_protect(RO)` fails (line 524): `page_is_rw = 1`.
    - Line 534: condition `if (!page_is_rw && mutation_applied)` evaluates to `FALSE`. Decapsulation is skipped; `crypto_endpoint = "NOT_RUN"`, `consumption_status = "UNKNOWN"`.
    - Execution proceeds directly to structured cleanup (lines 565–635).
    - If Cleanup Steps 1–6 succeed (table restored to `orig_val`, canaries pass, baseline KAT passes):
      - Line 638 assigns `records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED"`.
      - Ledger row $t$ shows `mutation_status = "UNKNOWN"`, `crypto_endpoint = "NOT_RUN"`, `restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED"`.
      - **Truthful Interpretation:** The table was restored to baseline, but the mutation was not executed.

---

### Path 3: Cleanup Failure
- **Source Lines:** Lines 640–644, followed by lines 680–705.
- **Sequence of Actions:**
  1. A mutation trial $t$ is executed.
  2. During structured cleanup, any check fails (e.g., read-back mismatch on restore, reprotection error, `vm_region_64` indicates writeable page, table canary mismatch, padding canary non-zero, or baseline KAT decapsulation recheck fails).
  3. `cleanup_passed = 0` or `ss_recheck_ok = 0`.
  4. Line 641: `records[t].restoration_status = "RESTORATION_FAILED";`.
  5. Line 642: `fprintf(stderr, "CRITICAL EMERGENCY: Cleanup failed in trial %d. Terminating runner immediately.\n", t);`.
  6. Line 643: `break;` terminates the `for (int t = 0; t < 16; t++)` loop.
  7. **Critical Fall-Through:**
     - Control exits the loop at line 677 and lands at line 680.
     - Lines 686–703 execute:
       - Rows $0 \dots t-1$ print their completed records.
       - Row $t$ prints `restoration_status = "RESTORATION_FAILED"`.
       - Rows $t+1 \dots 15$ print uninitialized records:
         `trial_id` is printed as `0`.
         `target_idx` is printed as `0`.
         `bit_mask` is printed as `0x0000`.
         `mutation_status`, `consumption_status`, `crypto_endpoint`, and `restoration_status` are all printed as `"UNKNOWN"`.
         `output_ss` is printed as 64 zeros.
     - Line 705 executes `return 0;`.
  8. **Audit Hazard:**
     The process **exits with return code 0** despite an emergency cleanup abort, and prints a 16-row CSV table!

---

### Path 4: SIGBUS / SIGSEGV Termination
- **Source Lines:** Lines 196–203 & 275–280.
- **Sequence of Actions:**
  1. Hardware trap signal 10 (`SIGBUS`) or 11 (`SIGSEGV`) occurs during memory access.
  2. `handle_trap_signal` is invoked by the OS kernel.
  3. Writes emergency diagnostic message to `stderr` using `write()`.
  4. Calls `_exit(128 + sig)`.
  5. The OS kernel immediately terminates the process and unmaps the private Mach-O virtual memory space.
  6. Lines 680–703 are **never reached**.
  7. **Zero CSV rows are printed.**
  8. Exit code is `138` (SIGBUS) or `139` (SIGSEGV).
  9. No trial row is ever emitted claiming restoration.

---

### Path 5: An Incomplete Run with Missing Trial Records
- **Scenarios Producing Incomplete Runs:**
  - **Scenario 5A (Hardware Trap):** Process exits with code 138/139. Output log ends abruptly at the trap banner; 0 CSV rows emitted.
  - **Scenario 5B (Preflight Abort):** Fails Preflights 1–5. Exits with code 1 at lines 350, 359, 374, 392, 396, 400, 407, 416, 425, 431, 439, or 443. Zero trials run; 0 CSV rows emitted.
  - **Scenario 5C (Pre-Trial Unprotect Abort):** Line 494 `vm_protect(RW)` fails. Sets `records[t].restoration_status = "UNKNOWN"`, executes `break;` (line 501), prints 16 CSV rows (with unrun trials as `UNKNOWN`), and exits with code 0.
  - **Scenario 5D (Cleanup Failure Abort):** Cleanup fails. Sets `records[t].restoration_status = "RESTORATION_FAILED"`, executes `break;` (line 643), prints 16 CSV rows (with unrun trials as `UNKNOWN`), and exits with code 0.

---

## 3. Discrepancy Analysis: Phase 15M Claim vs Code Reality

### Phase 15M Claim:
> *"The 9-column summary CSV table is printed only at the conclusion of main(). If a signal occurs during trial execution, the CSV summary is never printed. An abnormally terminated run never claims RESTORED_AND_BASELINE_RECHECK_PASSED."*
> *(PHASE15M_FINAL_PREEXECUTION_AUDIT.md, Section 1.1 & Section 4.2)*

### Auditor Evaluation:
1. **Accurate Aspects:**
   - For **signal termination** (`SIGBUS`/`SIGSEGV`), the statement is **100% accurate**: `_exit` bypasses `main()`, and no CSV is printed.
   - For **restoration status integrity**, the statement is **100% accurate**: no unexecuted or failed trial ever claims `RESTORED_AND_BASELINE_RECHECK_PASSED`.
2. **Inaccurate / Overgeneralized Aspects:**
   - Phase 15M's phrasing implies that *any* aborted run prevents CSV printing.
   - **In reality:** If an abort occurs due to a cleanup failure (line 643) or an unprotect failure (line 501), the runner executes `break;`, which drops directly into the CSV generator (lines 680–703) and exits with `return 0;`.
   - The CSV **is printed**, and the exit code is **0**.

---

## 4. Minimum Operator-Side Verification Protocol to Detect Incomplete Runs

Because the runner exits with code 0 upon in-loop cleanup failure (`break;`), an operator **must never rely solely on `$? == 0`** or on counting CSV rows. The following 5 automated checks are **mandatory**:

```bash
#!/bin/bash
# Mandatory Automated Post-Run Verification Driver

LOG_STDOUT="pilot_run.stdout.log"
LOG_STDERR="pilot_run.stderr.log"
CSV_OUT="PHASE15_TRIAL_LEDGER_RUN.csv"

# Check 1: Process Exit Code must be 0
if [ $? -ne 0 ]; then
    echo "FAIL: Process exited with non-zero code" && exit 1
fi

# Check 2: Stderr must contain zero error or abort banners
if grep -qE "(CRITICAL|EMERGENCY|BOUNDS CHECK FAIL|CLEANUP FAIL|ABORT)" "$LOG_STDERR"; then
    echo "FAIL: Emergency abort or cleanup failure detected on stderr" && exit 1
fi

# Check 3: Extract CSV table and assert exactly 16 data rows
grep -E "^[0-9]+,[0-9\-]+,0x[0-9a-fA-F]{4}," "$LOG_STDOUT" > "$CSV_OUT"
ROW_COUNT=$(wc -l < "$CSV_OUT" | tr -d ' ')
if [ "$ROW_COUNT" -ne 16 ]; then
    echo "FAIL: Expected 16 CSV rows, found $ROW_COUNT" && exit 1
fi

# Check 4: Assert all 16 Trial IDs are strictly sequential (0 to 15)
# In an aborted run, unexecuted rows have trial_id == 0
TRIAL_IDS=$(awk -F',' '{print $1}' "$CSV_OUT" | tr '\n' ' ')
EXPECTED_IDS="0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 "
if [ "$TRIAL_IDS" != "$EXPECTED_IDS" ]; then
    echo "FAIL: Incomplete run detected! Trial IDs do not match sequence 0..15: $TRIAL_IDS" && exit 1
fi

# Check 5: Assert zero RESTORATION_FAILED or UNKNOWN statuses in restoration_status
if grep -qE "(RESTORATION_FAILED|UNKNOWN)" "$CSV_OUT"; then
    echo "FAIL: Incomplete run detected! Found failed or unknown trial records in CSV" && exit 1
fi

# Check 6: Assert Trial 15 is a passing baseline control
TRIAL_15_STATUS=$(grep "^15," "$CSV_OUT" | awk -F',' '{print $7}')
if [ "$TRIAL_15_STATUS" != "RESTORED_AND_BASELINE_RECHECK_PASSED" ]; then
    echo "FAIL: Post-pilot baseline Trial 15 did not pass" && exit 1
fi

echo "PASS: Run verified complete and valid"
```

---

## Final Review Verdict

# **CONDITIONAL**

### Rationale:
1. **Status Truthfulness:** Verified. An unexecuted or failed trial **cannot** claim `RESTORED_AND_BASELINE_RECHECK_PASSED`.
2. **Incomplete Run Exposure:** If a cleanup failure occurs (line 643), the runner executes `break;`, emits a 16-row CSV table with unexecuted placeholders (`trial_id = 0`, status `UNKNOWN`), and exits with `return 0;`.
3. **Condition for Execution Authorization:** Before human authorization is granted, the operator must adopt the automated post-run driver script specified in Section 4 (verifying sequential trial IDs 0..15, zero `UNKNOWN`/`RESTORATION_FAILED` statuses, and clean `stderr`) rather than relying on the process return code alone.

*Notice: This audit is strictly read-only. It does not authorize execution.*
