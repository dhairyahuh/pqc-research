# Phase 15K — Findings Matrix & Safety Verification Ledger

**Auditor:** Independent Skeptical C Systems Safety Auditor  
**Audit Target:** Abnormal Termination, Signal Trapping, and Cleanup Safety Paths in `pilot_runner.c`  
**Date:** 2026-10-11  
**Target Directory:** `research/phase14_persistent_arm_design/`  

---

## Safety Findings Matrix

| Finding ID | Area | Dimension | Status | Severity | Exact Source Reference | Reachable Conditions | Evidence | Impact | Classification |
|:---:|:---|:---|:---:|:---:|:---|:---|:---|:---|:---:|
| **F-15K-01** | Control Flow | Mutation-to-Restoration Flow | **PASS** | HIGH | `pilot_runner.c` (lines 507–645) | Active in every mutation/sham trial after table write. | Code traces show all reachable paths from Step 2 write either reach Cleanup Step 6 or break immediately. | Guarantees structured cleanup is reached unless process is killed. | Directly Verified Fact |
| **F-15K-02** | Signal Safety | Async-Signal-Safe Termination | **PASS** | INFORMATIONAL | `pilot_runner.c` (lines 196–203 & 275–280) | Delivery of `SIGBUS` or `SIGSEGV` during execution. | `handle_trap_signal` writes error message via `write()` and calls `_exit(128 + sig)`. Does not invoke non-reentrant cleanup. | Avoids signal handler reentrancy deadlocks; OS kernel reclaims private address space cleanly. | Directly Verified Fact |
| **F-15K-03** | Status Flow | Gating of Restoration Status | **PASS** | HIGH | `pilot_runner.c` (lines 626–645) | Any non-expected endpoint (`REJECTION`, `DIFFERENT_OUTPUT`, `NO_OUTPUT`). | Assignment of `RESTORED_AND_BASELINE_RECHECK_PASSED` strictly guarded by `if (cleanup_passed && ss_recheck_ok)`. | Precludes false restoration claims if canary, reprotection, or baseline KAT fails. | Directly Verified Fact |
| **F-15K-04** | Enforcement | Code-Enforced vs External Gates | **PASS** | INFORMATIONAL | `pilot_runner.c` (lines 294–449 vs `EXPERIMENT_PROTOCOL.md`) | Runner startup and post-trial protocol. | Preflights 1–5, canaries, and Trial 15 baseline are code-enforced. Post-run FIPS 203 KAT suite (`bin/test_fips_kats_research`) is specified in docs but not executed internally. | Requires external test execution wrapper or operator command post-pilot. | Directly Verified Fact |
| **F-15K-05** | Containment | Pre-Decapsulation Safety Gate | **PASS** | HIGH | `pilot_runner.c` (lines 534–554) | Post-mutation reprotect failure (`kr != 0`) OR read-back mismatch. | Guard `if (!page_is_rw && mutation_applied)` skips `mlkem768_dec()`, marks `crypto_endpoint = "NOT_RUN"`, and routes to cleanup. | Prevents executing cryptographic functions while memory page is left writable or corrupted. | Directly Verified Fact |
| **F-15K-06** | OS Safety | Private Process VM Teardown | **PASS** | HIGH | Mach-O `__DATA_CONST` layout and Darwin VM | Any abnormal termination, abort, or signal exit. | Page is mapped within private process virtual memory; not shared memory, disk mmap, or kernel storage. | Abnormal exit cleanly destroys corrupted table at kernel boundary without leaving persistent artifacts. | Static Inference (Darwin VM) |

---

## Summary of Findings by Severity

| Severity Level | Count | Finding IDs | Audit Verdict |
|:---|:---:|:---|:---:|
| **CRITICAL DEFECTS** | 0 | None | N/A |
| **HIGH-INTEGRITY PATHS (PASS)** | 4 | **F-15K-01**, **F-15K-03**, **F-15K-05**, **F-15K-06** | Verified Robust |
| **INFORMATIONAL / OPERATIONAL** | 2 | **F-15K-02**, **F-15K-04** | Formally Demarcated |

---

## Final Review Recommendation

# **PASS — SAFETY PATHS ADEQUATELY SPECIFIED**

**Auditor Conclusion:**  
The cleanup, failure-handling, and abnormal-termination paths in `pilot_runner.c` meet rigorous systems-safety and cryptographic-audit standards. Non-expected cryptographic outcomes cannot claim restoration success without verified baseline reproduction, hardware memory traps fail-stop safely through kernel process teardown, and in-flight failures safely revert to mandatory cleanup.

*Mandatory Stop Condition: This safety audit constitutes a technical verification of abnormal-termination mechanics only. It does not authorize the execution of live pilot trials or the commencement of Phase 16.*
