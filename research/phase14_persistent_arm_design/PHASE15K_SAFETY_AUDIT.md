# Phase 15K — Abnormal-Termination and Cleanup Safety Audit

**Auditor:** Independent Skeptical C Systems Safety Auditor  
**Audit Target:** `research/phase14_persistent_arm_design/pilot_runner.c`, Phase 15J Readiness Review, Experiment Protocol, Go/No-Go Criteria, and Claim Boundaries  
**Target Repository State:** Git branch `space-resilience-framework` (HEAD: `4a2c4ebf9274a9188db3610a4f8448902caed056`)  
**Audit Mode:** Strictly Read-Only Audit (Zero compilation, zero live trials, zero fault injection, zero memory-protection changes)  
**Date:** 2026-10-11  
**Deliverable Directory:** `research/phase14_persistent_arm_design/`  

---

## Executive Summary

This independent safety audit examined the abnormal-termination, signal-handling, and cleanup mechanics of the persistent-table pilot harness in `pilot_runner.c`. The purpose of this audit was to determine whether failure paths, unprotect/protect transitions, hardware traps, and cleanup routines guarantee fail-closed memory isolation and truthful ledger reporting under all reachable execution conditions.

### Core Determinations:
1. **Mutation-to-Restoration Control Flow (PASS):** Every path from table modification either completes the full 6-step transactional cleanup pipeline or terminates execution immediately via fail-stop mechanisms (`break;` or `_exit()`).
2. **Failure Progression & Containment (PASS):** In-trial non-fatal faults (read-back mismatch post-mutation, reprotection errors, cryptographic rejection, altered output, or decapsulation failure) safely bypass cryptographic execution and route directly into mandatory structured cleanup.
3. **Signal Trapping & Process Destruction (PASS):** Hardware traps (`SIGBUS`, `SIGSEGV`) are trapped by `handle_trap_signal`. The handler executes async-signal-safe immediate process termination via `_exit(128 + sig)`. The handler does **not** attempt in-process cleanup, avoiding unsafe memory operations during a faulted state. Process destruction guarantees complete memory reclamation at the OS kernel boundary. Process exit is **never** recorded as a successful restoration.
4. **Endpoint Independence of Restoration Status (PASS):** Endpoints `NO_OUTPUT`, `REJECTION`, and `DIFFERENT_OUTPUT` can receive `RESTORED_AND_BASELINE_RECHECK_PASSED` strictly and exclusively after all 6 cleanup steps (including full table and padding canaries and baseline KAT decapsulation recheck) succeed.
5. **Enforcement Demarcation (CODE vs DOCS):**
   - *Code-Enforced:* Oracle self-test, Preflights 1–5, per-trial transactional cleanup steps 1–6, Trial 15 baseline control, and table/padding canaries are enforced directly in `pilot_runner.c`.
   - *Document-Specified (External):* Execution of the external multi-vector KAT suite (`./bin/test_fips_kats_research`) is specified in `EXPERIMENT_PROTOCOL.md` and `GO_NO_GO_CRITERIA.md`, but is not invoked internally by `pilot_runner.c`.
6. **Overall Safety Sufficiency (PASS):** For a standalone research binary modifying an isolated 16 KB virtual memory page within its own process address space, the fail-stop and transactional rollback architecture is robust, sufficient, and safe.

---

## 1. Trace of Paths from Mutation to Restoration

The trial lifecycle was traced from the exact moment the twiddle table memory is modified (Step 2 write: `vtable[idx] = target_val;` at line 507) to final restoration:

```
[ Step 2: vtable[idx] = target_val ] (Table Modified in Memory)
         |
         v
[ Step 3: Immediate Read-Back Check ]
   |-- Match: mutation_applied = 1
   \-- Mismatch: mutation_applied = 0 (Logs CRITICAL; does not break; proceeds to Step 4)
         |
         v
[ Step 4: Re-protect Page to Read-Only (vm_protect RO) ]
   |-- Success: page_is_rw = 0
   \-- Failure: page_is_rw = 1 (Logs CRITICAL; does not break; proceeds to Step 5)
         |
         v
[ Step 5: Execution Decision (Condition: !page_is_rw && mutation_applied) ]
   |-- TRUE: Run mlkem768_dec()
   |     |-- Normal Output: crypto_endpoint = "EXPECTED_OUTPUT"
   |     |-- Rejection: crypto_endpoint = "REJECTION"
   |     |-- Altered Secret: crypto_endpoint = "DIFFERENT_OUTPUT"
   |     \-- Decapsulation Error (dec_rc != 0): crypto_endpoint = "NO_OUTPUT"
   \-- FALSE (Reprotect Failed OR Read-Back Mismatched):
         crypto_endpoint = "NOT_RUN", consumption_status = "UNKNOWN"
         |
         v
[ Mandatory Structured Cleanup Pipeline (Steps 1–6) ]
   |
   |-- Cleanup Step 1: vm_protect(RW) [if page was RO]
   |     \-- Failure: cleanup_passed = 0
   |
   |-- Cleanup Step 2: Restore vtable[idx] = orig_val & Verify Read-Back
   |     \-- Read-back mismatch: cleanup_passed = 0
   |
   |-- Cleanup Step 3: vm_protect(RO)
   |     \-- Failure: cleanup_passed = 0
   |
   |-- Cleanup Step 4: Live Kernel Query via vm_region_64
   |     \-- Protection not strictly RO: cleanup_passed = 0
   |
   |-- Cleanup Step 5: Integrity Canaries
   |     |-- Table Canary (memcmp 256 bytes golden): mismatch -> cleanup_passed = 0
   |     \-- Padding Canary (16,128 bytes clean zeros): mismatch -> cleanup_passed = 0
   |
   \-- Cleanup Step 6: Post-Trial Baseline Decapsulation Recheck (if cleanup_passed == 1)
         \-- Non-zero return OR ss != test_vector_ss: ss_recheck_ok = 0, cleanup_passed = 0
         |
         v
[ Restoration Status Assignment ]
   |-- IF cleanup_passed && ss_recheck_ok:
   |     records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED"
   |     (Proceed to next trial)
   \-- ELSE:
         records[t].restoration_status = "RESTORATION_FAILED"
         (EMERGENCY ABORT: break; terminates trial loop immediately)
```

---

## 2. Failure Handling Taxonomy: Containment vs Immediate Termination

Control-flow analysis partitions all potential failure conditions into two mutually exclusive behaviors:

### 2.1 In-Trial Containment (Proceeds to Cleanup to Restore Table)
These failures prevent cryptographic execution but allow the harness to execute structured cleanup:
1. **Read-back Mismatch Post-Mutation (line 514):** Sets `mutation_applied = 0`. Skips `mlkem768_dec()`, routes directly to cleanup to restore `orig_val`.
2. **Reprotection Failure Post-Mutation (line 524):** Leaves `page_is_rw = 1`. Skips `mlkem768_dec()`, routes directly to cleanup. Because the page is already writable, Cleanup Step 1 is bypassed and Cleanup Step 2 immediately overwrites `target_val` with `orig_val`.
3. **Decapsulation Return Error (`dec_rc != 0`):** Classified as `NO_OUTPUT`. Output secret zeroed. Routes directly to cleanup.
4. **Cryptographic Implicit Rejection (`REJECTION`):** Normal expected cryptographic outcome. Routes directly to cleanup.
5. **Cryptographic Output Alteration (`DIFFERENT_OUTPUT`):** Output captured. Routes directly to cleanup.

### 2.2 Immediate Termination (Halts Runner Execution)
These failures immediately break out of the trial loop or terminate the OS process:
1. **Pre-Trial Unprotect Failure (lines 495–502):** `vm_protect(RW)` returns non-zero. Sets status to `"UNKNOWN"` and executes `break;` (table was never modified).
2. **Any Cleanup Failure (lines 641–644):** If any of Cleanup Steps 1–6 fail, the runner sets `restoration_status = "RESTORATION_FAILED"` and invokes `break;`. No further trials are executed.
3. **Hardware Trap Signals (`SIGBUS`, `SIGSEGV`):** Signal handler invokes `_exit(128 + sig)`, immediately terminating the process.
4. **Preflight Check Failures (Preflights 1–5):** Process exits with return code `1` prior to executing Trial 0.

---

## 3. Signal Trapping and Process Termination Mechanics

### 3.1 Code Inspection of Signal Trapping
In `pilot_runner.c` (lines 196–203 & 275–280):
```c
static volatile sig_atomic_t g_signal_received = 0;
static void handle_trap_signal(int sig) {
    g_signal_received = sig;
    const char msg[] = "\n!!! CRITICAL TRAP SIGNAL INTERCEPTED IN RUNNER !!!\n";
    write(STDERR_FILENO, msg, sizeof(msg) - 1);
    _exit(128 + sig);
}
```
Traps are installed via `sigaction` for `SIGBUS` (signal 10) and `SIGSEGV` (signal 11).

### 3.2 Safety Analysis of the Signal Handler
1. **Can a Signal Occur While Table is Modified or Writable?**  
   *Yes.* If a memory trap, bus error, or hardware fault occurs during Steps 2–6 (e.g. while page is RW or during NTT computation on corrupted twiddles), `SIGBUS` or `SIGSEGV` will be delivered.
2. **Does the Handler Perform In-Process Cleanup?**  
   *No.* The handler performs **only emergency process termination** via `_exit(128 + sig)`.
3. **Systems Safety Rationale:**  
   In C systems programming on POSIX/Darwin systems, attempting memory modifications or calling non-async-signal-safe functions (like `vm_protect`, `printf`, `malloc`, or cryptographic functions) from within a `SIGSEGV`/`SIGBUS` handler is unsafe and can lead to deadlocks, recursive faults, or kernel crashes. Terminating immediately via `_exit` is the only standard-conformant, async-signal-safe response.
4. **No False Restoration Claim:**  
   Because the process terminates immediately, the trial loop does not complete, no CSV row claiming restoration is emitted, and `records[t].restoration_status` is never set to `RESTORED_AND_BASELINE_RECHECK_PASSED`.
5. **Operating System Boundary Isolation:**  
   Because the twiddle table resides in private process virtual memory (Mach-O `__DATA_CONST`), process termination by the Darwin kernel completely deallocates and unmaps the process address space. No corrupted memory state can persist on disk or affect other system processes.

---

## 4. Verification of Restoration Status Invariants for All Cryptographic Outcomes

Inspection of lines 534–560 and 626–645 verifies the relationship between cryptographic endpoints and restoration status:

| Cryptographic Endpoint | Condition | Cleanup Execution | Restoration Status Assigned |
|:---|:---|:---:|:---:|
| **`EXPECTED_OUTPUT`** | Baseline or unconsumed mutation | Full Steps 1–6 Required | `RESTORED_AND_BASELINE_RECHECK_PASSED` (if all 6 steps pass) |
| **`REJECTION`** | Valid FO rejection key $K_{rej}$ | Full Steps 1–6 Required | `RESTORED_AND_BASELINE_RECHECK_PASSED` (if all 6 steps pass) |
| **`DIFFERENT_OUTPUT`** | Altered shared secret ($K \neq K_{golden} \land K \neq K_{rej}$) | Full Steps 1–6 Required | `RESTORED_AND_BASELINE_RECHECK_PASSED` (if all 6 steps pass) |
| **`NO_OUTPUT`** | Decapsulation runtime error (`dec_rc != 0`) | Full Steps 1–6 Required | `RESTORED_AND_BASELINE_RECHECK_PASSED` (if all 6 steps pass) |
| **Any Endpoint** | Any Cleanup Step (1–6) Fails | Failed during cleanup | `RESTORATION_FAILED` (Loop terminates via `break;`) |

**Directly Verified Finding:**  
Every non-expected outcome (`NO_OUTPUT`, `REJECTION`, `DIFFERENT_OUTPUT`) is required to undergo and pass the exact same 6-step transactional cleanup pipeline (including the full 256-byte table comparison, 16,128-byte padding scan, and baseline KAT recheck) before receiving `RESTORED_AND_BASELINE_RECHECK_PASSED`. There is zero path where a non-expected cryptographic outcome bypasses cleanup or assumes restoration succeeded.

---

## 5. Distinction Between Code-Enforced Gates and Document-Specified Procedures

A rigorous audit was performed comparing code implementation in `pilot_runner.c` against specifications in `EXPERIMENT_PROTOCOL.md` and `GO_NO_GO_CRITERIA.md`:

| Requirement / Gate | Code-Enforced in `pilot_runner.c` | Document-Specified Only | Verification Evidence & Analysis |
|:---|:---:|:---:|:---|
| **Independent SHAKE256 Self-Test** | **YES** | YES | Lines 294–303: Enforced at runner launch; returns code 1 on failure. |
| **Independent $K_{rej}$ Derivation** | **YES** | YES | Lines 305–336: Bit-identical check against KAT reference; returns code 1 on failure. |
| **Preflight 1: Symbol & 16KB Alignment** | **YES** | YES | Lines 346–361: Asserts table is 16KB-aligned; returns code 1 on failure. |
| **Preflight 2: Live VM Mapping Query** | **YES** | YES | Lines 363–402: Calls `vm_region_64`; asserts read and maxprot write permissions. |
| **Preflight 3: Initial Table & Padding Canaries**| **YES** | YES | Lines 404–419: Compares 256 bytes golden zetas and scans 16,128 zero padding bytes. |
| **Preflight 4: Protection Transition Dry-Run** | **YES** | YES | Lines 421–433: Toggles RW $\rightarrow$ RO without write; returns code 1 on failure. |
| **Preflight 5: Preflight Baseline Decapsulation**| **YES** | YES | Lines 435–449: Decapsulates test vector; asserts exact match to golden secret. |
| **Per-Trial Bounds Validation** | **YES** | YES | Lines 468–477: Fails closed on invalid target index; assigns `NOT_RUN_INVALID_TARGET`. |
| **Per-Trial Canaries & Reprotection** | **YES** | YES | Lines 565–624: Verifies live `vm_region_64` RO, table memcmp, and padding zeros. |
| **Per-Trial Post-Restoration KAT Recheck**| **YES** | YES | Lines 626–635: Executes `mlkem768_dec`; asserts $ss == test\_vector\_ss$. |
| **Emergency Abort on Cleanup Failure** | **YES** | YES | Lines 641–643: Sets `RESTORATION_FAILED` and halts loop immediately (`break;`). |
| **Trial 15 Post-Pilot Baseline Control** | **YES** | YES | Hardcoded as Trial 15 in `pilot_specs[15]` (`target_idx = -1`). |
| **Post-Pilot Multi-Vector FIPS 203 KAT Suite**| **NO** | **YES** | **Document-only requirement.** `pilot_runner.c` does **not** invoke `./bin/test_fips_kats_research`. This must be run by an external operator or shell wrapper. |
| **Cryptographic Hash Manifest Auditing** | **NO** | **YES** | Document-only procedure. Hashing artifacts is conducted externally via `shasum -a 256`. |

---

## 6. Assessment of Abort and Recovery Policy Sufficiency

### 6.1 Evaluation Context
The SUT is an in-memory C post-quantum cryptographic implementation running as a user-space research process under macOS Darwin on Apple Silicon.

### 6.2 Evaluation Dimensions:
1. **Memory Isolation:** The mutated table `mlk_zetas_page` is isolated on a dedicated 16 KB virtual memory page with 16,128 trailing zero-byte canaries in `__DATA_CONST`. It shares no pages with other symbols or stack frames.
2. **Transactional Reversibility:** Within normal execution, any mutation is contained within a tightly scoped block and restored within milliseconds.
3. **Emergency Halting:** Any cleanup failure triggers immediate `break;`, preserving diagnostic logs and preventing cumulative damage.
4. **Abnormal Signal Handling:** Trapping `SIGBUS`/`SIGSEGV` and calling `_exit(128 + sig)` is the correct systems response. Because memory is private to the process, kernel teardown cleanly eliminates corrupted state without risk of persistent corruption.

### 6.3 Audit Finding:
The abort and recovery policy is **thoroughly sufficient and well-specified** for this research executable.

---

## Final Audit Verdict

# **PASS — SAFETY PATHS ADEQUATELY SPECIFIED**

### Safety Audit Conclusion:
The abnormal-termination, signal-handling, and cleanup architectures in `pilot_runner.c` are conservative, robust, and correctly implemented. Hardware traps fail-stop safely at the OS boundary, cleanup checks strictly gate the restoration success status, and invalid/failed trials cannot falsely record successful restoration.

*Mandatory Stop Condition: This passing safety audit evaluates technical code safety and control flow. It does not authorize the execution of live pilot trials or the commencement of Phase 16.*
