# Phase 15O — Fail-Closed Incomplete-Run Reporting

**Author:** Conservative Cryptographic Systems Engineer & Safety Auditor  
**Date:** 2026-10-11  
**Target Repository State:** Git branch `space-resilience-framework` (HEAD: `4a2c4ebf9274a9188db3610a4f8448902caed056`)  
**Scope:** Resolution of Confirmed Phase 15N Defect in `research/phase14_persistent_arm_design/pilot_runner.c`  
**Deliverable Path:** `research/phase14_persistent_arm_design/PHASE15O_REPORTING_FIX.md`  

---

## 1. Executive Summary & Defect Statement

During the Phase 15N abnormal-termination and incomplete-run verification audit, a critical control-flow defect was identified in `research/phase14_persistent_arm_design/pilot_runner.c`:

### Confirmed Defect:
1. **Unintentional Fall-Through on In-Loop Aborts:**  
   When an in-loop abort occurred at line 501 (unprotect failure `kr != KERN_SUCCESS`) or at line 643 (cleanup failure `!(cleanup_passed && ss_recheck_ok)`), the runner executed `break;`.
2. **Ghost Row Generation:**  
   `break;` jumped out of the trial loop to line 680, where the summary CSV generator executed `for (int t = 0; t < 16; t++)`. Because `records` was zeroed via `memset` at line 457 and trailing trials ($t+1 \dots 15$) were never reached, the runner emitted placeholder records with duplicate `trial_id = 0`, `target_idx = 0`, and all statuses set to `"UNKNOWN"`.
3. **False Exit Status Contract:**  
   Following the emission of the 16 CSV rows, line 705 executed `return 0;`. Consequently, the process terminated with **exit code 0** despite having aborted prematurely due to a critical cleanup or unprotect failure. An automated consumer checking only `$? == 0` or counting lines (`wc -l == 17`) would mistake an aborted run for a successful, complete execution.

Phase 15O corrects this defect, implementing a strict **fail-closed incomplete-run reporting contract**.

---

## 2. Technical Correction Implementation

The correction was applied directly to `research/phase14_persistent_arm_design/pilot_runner.c`:

### 2.1 State Tracking & Pre-Population
- Prior to entering the trial loop, `records[t].trial_id = t`, `target_idx`, `bit_mask`, and `desc` are pre-populated for all 16 slots.
- Two execution-state variables were introduced:
  - `int trials_recorded = 0;`: Tracks the number of trials actually entered and recorded.
  - `int abort_triggered = 0;`: Flags whether any in-loop abort condition was triggered.

### 2.2 Abort Flagging at Failure Sites
Explicit abort flagging (`abort_triggered = 1; break;`) was installed at all three in-loop failure points:
1. **Unprotect Failure (Line 501):**
   ```c
   fprintf(stderr, "ABORT in trial %d: vm_protect(RW) failed with %d\n", t, kr);
   abort_triggered = 1;
   break;
   ```
2. **Cleanup Failure (Line 643):**
   ```c
   records[t].restoration_status = "RESTORATION_FAILED";
   fprintf(stderr, "CRITICAL EMERGENCY: Cleanup failed in trial %d. Terminating runner immediately.\n", t);
   abort_triggered = 1;
   break;
   ```
3. **Baseline Integrity Failure (Line 662):**
   ```c
   records[t].restoration_status = "RESTORATION_FAILED";
   fprintf(stderr, "CRITICAL EMERGENCY: Baseline integrity failure in trial %d. Terminating runner immediately.\n", t);
   abort_triggered = 1;
   break;
   ```

### 2.3 Partial Ledger Emission & Elimination of Placeholders
The summary CSV generator was updated to loop strictly over `t < trials_recorded` rather than hardcoding `16`:
```c
for (int t = 0; t < trials_recorded; t++) { ... }
```
- On an aborted run, only the trials actually reached ($0 \dots t$) are emitted in the partial ledger.
- Ghost/placeholder rows ($t+1 \dots 15$) are **completely eliminated**.
- The section banner dynamically designates partial output:
  `PARTIAL TRIAL LEDGER (ABORTED RUN - %d/16 TRIALS RECORDED)`.

### 2.4 Explicit Machine-Verifiable Completion Markers & Non-Zero Exit
Following ledger emission, an explicit evaluation of completion determines the process exit code:
```c
if (abort_triggered || trials_recorded < 16) {
    printf("\n>>> PILOT RUN ABORTED: INCOMPLETE RUN (%d/16 TRIALS PROCESSED) (STATUS: FAILED) <<<\n", trials_recorded);
    return 1;
}

printf("\n>>> PILOT RUN COMPLETE: 16/16 TRIALS PROCESSED (STATUS: SUCCESS) <<<\n");
return 0;
```

---

## 3. Strict Exit-Status Contract

The process exit code now strictly reflects the operational state of the runner:

| Exit Code | Runner State | Description | Summary CSV State |
|:---:|:---|:---|:---:|
| **`0`** | **Complete Success** | All 16 trials completed successfully; Trial 15 baseline passed; zero aborts. | Complete 16-row CSV emitted. Marker: `PILOT RUN COMPLETE`. |
| **`1`** | **Preflight Abort** | Preflight 1–5 or oracle check failed prior to Trial 0. | Zero CSV rows emitted. Error logged to `stderr`. |
| **`1`** | **In-Loop Abort** | Unprotect failed (Step 1), cleanup failed, or baseline check failed. | Partial CSV emitted ($N < 16$ rows). Marker: `PILOT RUN ABORTED`. |
| **`138`** | **SIGBUS Trap** | Hardware bus error trapped by `handle_trap_signal`. | Zero CSV rows emitted; `_exit(138)` invoked. |
| **`139`** | **SIGSEGV Trap** | Segmentation violation trapped by `handle_trap_signal`. | Zero CSV rows emitted; `_exit(139)` invoked. |

---

## 4. Partial-Output Classification Semantics for Operators

When an operator or automated workflow evaluates pilot outputs, partial results must be classified according to the following deterministic rules:

### Case A: Process Exits with Code 1 and Partial CSV ($N < 16$ Rows)
- **Status:** `INCOMPLETE_RUN_ABORTED`.
- **Classification:**
  - Rows $0$ through $N-2$: Valid completed trials with verified restoration.
  - Row $N-1$: The aborted trial. If `restoration_status == "RESTORATION_FAILED"`, the table cleanup failed and runner halted to prevent contamination. If `restoration_status == "UNKNOWN"`, memory unprotection failed prior to mutation.
  - Rows $N$ through $15$: Unexecuted; omitted from the CSV ledger.
- **Operator Action:** The run is invalid. The pilot must be marked **FAILED**. Memory state was restored or process halted. Do not proceed to campaign.

### Case B: Process Exits with Code 138 or 139 (Signal Termination)
- **Status:** `CRASH_SIGNAL`.
- **Classification:** An uncatchable memory trap occurred. The OS kernel unmapped the address space via `_exit()`. No CSV was emitted.
- **Operator Action:** The run is invalid. Inspect `stderr` for fault diagnostic. Re-verify Mach-O binary section alignment and protections.

### Case C: Process Exits with Code 0 and Exactly 16 Rows
- **Status:** `VALID_COMPLETE_RUN`.
- **Classification:** All 16 trials executed. All 16 rows show `RESTORED_AND_BASELINE_RECHECK_PASSED` (or `NOT_RUN_INVALID_TARGET`). Marker reads `PILOT RUN COMPLETE: 16/16 TRIALS PROCESSED (STATUS: SUCCESS)`.
- **Operator Action:** Proceed to post-run verification (re-run `./bin/test_fips_kats_research`).

---

## 5. Non-Mutating Validation Record

### 5.1 Compilation Verification
- **Command:**
  ```bash
  clang -O3 -Wall -Wextra -std=c11 \
    -I . -I algorithms/source_ref/mlkem \
    research/phase14_persistent_arm_design/pilot_runner.c \
    bin/obj/mlkem768_persistent_reloc.o \
    -o bin/pilot_runner
  ```
- **Exit Code:** `0` (Zero warnings).

### 5.2 Non-Mutating Oracle Verification (`--check-oracle`)
- **Command:**
  ```bash
  ./bin/pilot_runner --check-oracle
  ```
- **Exit Code:** `0`
- **Output:**
  ```text
  =======================================================================
   PHASE 15D: HARDENED PERSISTENT-TABLE FEASIBILITY RUNNER
   Target: mlk_zetas_page (ML-KEM-768 relocated twiddle table)
  =======================================================================

  --- [ORACLE VALIDATION] Independent FIPS 202 SHAKE256 Self-Test ---
    SHAKE256("", 32) matches NIST FIPS 202 KAT:
    46b9dd2b0ba88d13233b3feb743eeb243fcd52ea62b81b82b50c27646ed5762f
    Result: PASS

  --- [ORACLE DERIVATION] Independent FIPS 203 Rejection Key Derivation ---
    Concatenation length: 1120 bytes (32-byte z + 1088-byte ciphertext c)
    Derived FIPS 203 K_rej: f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03
    Expected KAT K_rej:    f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03
    Result: PASS (Independent Oracle Bit-Identical to Expected FIPS 203 KAT)

  >>> Oracle check completed successfully (--check-oracle mode). Exiting without memory mutation. <<<
  ```

### 5.3 Binary String Verification
- **Command:**
  ```bash
  strings bin/pilot_runner | grep -E "(PILOT RUN COMPLETE|PILOT RUN ABORTED|PARTIAL TRIAL LEDGER)"
  ```
- **Output:**
  ```text
   PARTIAL TRIAL LEDGER (ABORTED RUN - %d/16 TRIALS RECORDED)
  >>> PILOT RUN ABORTED: INCOMPLETE RUN (%d/16 TRIALS PROCESSED) (STATUS: FAILED) <<<
  >>> PILOT RUN COMPLETE: 16/16 TRIALS PROCESSED (STATUS: SUCCESS) <<<
  ```
- **Confirmation:** Completion markers and partial ledger banners are verified present in the compiled executable.

---

## 6. Cryptographic Hash Provenance Ledger

| Artifact Path | Prior Hash (Phase 15H/15I) | Authoritative Hash (Phase 15O) | Status |
|:---|:---|:---|:---:|
| `pilot_runner.c` | `39f7e831...` | `292e15b63a9d260f6aededc0f86e0ce1b0e6d897a4e44307447d96eaa8f0ebce` | **UPDATED (Phase 15O fix)** |
| `bin/pilot_runner` | `d9da42c3...` | `6a671b96ee1869ed1630f7c42f1cdeca8fd16b24467d1e2289a3fdb08bdea9b6` | **RECOMPILED (Phase 15O)** |
| `bin/obj/mlkem768_persistent_reloc.o` | `c239e7cf...` | `c239e7cf355404af7eb616c58832a6f6b9fbb9c708f83df46c9e5d01264deb9f` | Preserved byte-for-byte |
| `PHASE15B_REPORT.md` | `0a530225...` | `0a5302256db2e5b3f70df1820e21f15ac509fa07e1044d02d6a0dda727554e37` | Preserved byte-for-byte |
| `PHASE15B_TRIAL_LEDGER.csv` | `5cf48fb9...` | `5cf48fb9ab869cff6345eb1b8d03785ec65d3ab1c2ee76cab29d4ea6bde45d2c` | Preserved byte-for-byte |
| `PHASE15F_ERRATA.md` | `d305ae17...` | `d305ae1710b30ad835754578eb89038903e2c4004d4145d00fe71df94a7bcf02` | Preserved byte-for-byte |
| `PHASE15M_FINAL_PREEXECUTION_AUDIT.md` | `999eff24...` | `999eff240dd685969ac3ef846ea00fad0bca5b754e98d859fdbbdd9ecd86406c` | Preserved byte-for-byte |
| `PHASE15N_ABORT_PATH_VERIFICATION.md` | `af8f43fc...` | `af8f43fc98ea759ed0a12956098f6d1d473abfc5fa6cb35e21167e587f757413` | Preserved byte-for-byte |

---

## Final Governance Status

The Phase 15N defect is **completely resolved**. Incomplete or aborted runs cannot produce an exit code of 0, cannot emit ghost placeholder rows with duplicate trial IDs, and cannot be mistaken for complete executions.

*Notice: This fix and non-mutating validation does not authorize live pilot execution. The pilot remains halted pending explicit human decision.*
