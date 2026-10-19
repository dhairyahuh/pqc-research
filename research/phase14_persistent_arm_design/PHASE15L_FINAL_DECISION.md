# Phase 15L — Final Human-Authorization Decision Memo

**To:** Human Principal & Senior Cryptographic Systems Lead  
**From:** Conservative Cryptographic Systems Engineer & Skeptical Research Auditor  
**Date:** 2026-10-11  
**Target Repository:** `space-resilience-framework` (HEAD: `4a2c4ebf9274a9188db3610a4f8448902caed056`)  
**Context:** Comprehensive Synthesis of Phases 14A through 15K  
**Deliverable Path:** `research/phase14_persistent_arm_design/PHASE15L_FINAL_DECISION.md`  

---

## Executive Summary & Final Recommendation

### Recommendation: **GO FOR EXPLICIT HUMAN APPROVAL**

**Decision Rationale:**  
Over Phases 14A through 15K, the persistent-storage fault harness for ML-KEM-768 decapsulation underwent rigorous hardening, multiple independent read-only audits, and formal verification:
1. **Isolated Memory Architecture:** The twiddle-factor table `mlk_zetas` was relocated into a dedicated 16 KB virtual memory page in `(__DATA_CONST,__zetas_page)` with 16,128 trailing zero padding canaries, zero co-located symbols, and intact baseline NTT instruction schedules.
2. **Independent Cryptographic Oracles:** A standalone FIPS 202 SHAKE256 implementation and independent FIPS 203 implicit-rejection oracle $J(z \parallel c, 32)$ were installed and validated bit-for-bit against NIST Known-Answer Tests without memory mutation.
3. **Data Model & Schema Alignment:** The authoritative 9-column CSV ledger schema was preserved, and invalid targets fail closed as `NOT_RUN_INVALID_TARGET`, eliminating metric inflation.
4. **Safety & Containment:** A 6-step transactional cleanup pipeline with live kernel permission queries (`vm_region_64`), table/padding canaries, and async-signal-safe trap handlers ensures fail-closed memory protection.

**All technical, architectural, and safety blockers have been resolved.** The system has reached the formal governance threshold: no automated or agentic step can proceed further. Live execution of the 16-trial feasibility pilot requires **explicit, informed human authorization**.

---

## 1. What Exact Empirical Question the 16-Trial Pilot Answers

The 16-trial pilot is an **engineering feasibility and protocol hygiene qualification**, not a statistical radiation survey. It answers one exact, falsifiable empirical question:

> **Empirical Core Question:**  
> When the operational twiddle table (`mlk_zetas`) of a compiled C reference implementation of ML-KEM-768 on Darwin ARM64 is relocated to dynamically protectable memory (`__DATA_CONST`), can single-word bit-flips be applied and observed such that:
> 1. The downstream arithmetic operations (forward NTT, inverse NTT, basemul) actively consume the corrupted twiddle constants at runtime rather than folding them into compile-time immediate values;
> 2. The decapsulation endpoint reliably transitions to either valid Fujisaki-Okamoto implicit rejection ($K_{rej} = J(z \parallel c, 32)$) or observable output deviation (`DIFFERENT_OUTPUT`); and
> 3. The memory page can be transactionally reverted to the bit-identical pristine baseline in-place without generating kernel protection traps, padding contamination, or cross-trial state leakage?

---

## 2. Division of Safeguards: Code-Enforced vs Operator-Required

| Dimension | Safeguards Enforced by Code (`pilot_runner.c`) | Safeguards Required from Operator / Driver Script |
|:---|:---|:---|
| **Cryptographic Preflights** | • Standalone SHAKE256 empty string KAT verified in code.<br>• Independent FIPS 203 $K_{rej}$ derivation verified in code against KAT. | • Verification of binary compilation flags (`-O3 -Wall -Wextra -std=c11`). |
| **System Preflights** | • Preflight 1: Asserts 16 KB page alignment.<br>• Preflight 2: Queries Darwin VM via `vm_region_64` for READ and maxprot WRITE.<br>• Preflight 3: Verifies 256-byte table memcmp and scans 16,128 zero-byte padding canaries.<br>• Preflight 4: Executes RW $\rightarrow$ RO dry-run transition without write.<br>• Preflight 5: Pre-trial clean baseline decapsulation KAT check. | • Running non-mutating `./bin/pilot_runner --check-oracle` prior to live execution.<br>• Ensuring no concurrent processes access the research binary. |
| **Trial Bounds & Safety** | • Fails closed if `target_idx < -1 \|\| target_idx >= 128`.<br>• Assigns `NOT_RUN_INVALID_TARGET` without executing decapsulation or claiming restoration.<br>• Skips decapsulation if mutation read-back or reprotection fails. | • Guaranteeing trial specification files are not modified on disk. |
| **In-Place Cleanup** | • 6-Step Transactional Cleanup: unprotect, restore original value, read-back assertion, reprotect to RO, live `vm_region_64` check, table + padding canaries, and baseline KAT recheck.<br>• Halts runner immediately (`break;`) if any cleanup step fails. | • Monitoring execution logs for any emergency abort message. |
| **Abnormal Termination** | • Traps `SIGBUS` and `SIGSEGV` via `sigaction`.<br>• Handler executes async-signal-safe `_exit(128 + sig)`. | • Inspecting runner exit code ($0$ for clean run; $\ge 128$ for signal). |
| **Post-Run Validation** | • Trial 15 executes post-pilot baseline decapsulation control in code. | • **Mandatory External KAT Suite:** Must execute `./bin/test_fips_kats_research` post-run to verify 100% of NIST test vectors.<br>• Extracting and saving 9-column CSV ledger from mixed stdout stream. |

---

## 3. What Happens Under Abnormal Termination (`SIGBUS` / `SIGSEGV`)

If an unexpected memory fault, alignment violation, or hardware trap occurs while the table is modified or writable:

1. **Process & Memory Behavior:**
   - The signal handler `handle_trap_signal` intercepts the trap, writes an emergency diagnostic to `stderr` using async-signal-safe `write()`, and immediately calls `_exit(128 + sig)`.
   - The handler does **not** attempt in-process cleanup, avoiding recursive faults or non-reentrant kernel calls during a faulted state.
   - The Darwin Mach kernel immediately terminates the process and reclaims the entire private virtual address space. Because `mlk_zetas_page` resides strictly in private user-space virtual memory, **all modified memory state is completely destroyed at the kernel boundary**. No corrupted memory persists on disk, in shared memory, or in other processes.
2. **Trial Ledger & Evidence Behavior:**
   - The 9-column summary CSV table is printed only at the conclusion of `main()`. If a signal occurs during trial execution, **the CSV summary table is never printed**.
   - The trial interrupted by the signal is **never recorded as restored**. It is impossible for an abnormally terminated run to falsely claim `RESTORED_AND_BASELINE_RECHECK_PASSED`.
   - The operator receives exit code `138` (SIGBUS) or `139` (SIGSEGV), and partial execution logs remain in the output stream for forensic diagnosis.

---

## 4. Minimum Operational Requirements for Pilot Execution

If human approval is granted, the following operational protocol is **mandatory**:

```
[ Preflight Gate ]
  |-- 1. Check Git Status: Assert zero untracked changes to SUT and production files.
  |-- 2. Verify SHA-256 Hashes: Confirm pilot_runner.c and bin/pilot_runner match Phase 15H/15I digests.
  |-- 3. Run Non-Mutating Oracle: Execute ./bin/pilot_runner --check-oracle (Assert exit code 0).
  |-- 4. Baseline KAT Suite: Execute ./bin/test_fips_kats_research (Assert 100% KAT pass).
  |
  v
[ Pilot Execution ]
  |-- 5. Execute Runner with Full Stream Capture:
  |      ./bin/pilot_runner > pilot_run.stdout.log 2> pilot_run.stderr.log
  |-- 6. Check Process Exit Code: Assert exit code == 0.
  |
  v
[ Post-Run Verification ]
  |-- 7. Post-Pilot KAT Suite: Re-run ./bin/test_fips_kats_research (Assert 100% KAT pass).
  |-- 8. Ledger Extraction: Filter CSV header and 16 data rows into PHASE15_TRIAL_LEDGER_RUN.csv.
  |-- 9. Checksum Manifest: Compute SHA-256 over all generated logs and ledger files.
```

---

## 5. Scientific Value vs Limitations: A Balanced Assessment

### 5.1 Real Scientific Value:
1. **Closing the Multi-Stage Parameter Fault Gap:** Prior research (Phases 1–10) utilized Transient Fault Injection in Butterflies (TFIB), which corrupted a single stack variable during a single butterfly loop. Persistent twiddle corruption evaluates a fundamentally distinct threat model: parameter errors that persist across *both* the inverse NTT (polynomial recovery) *and* the forward NTT / basemul (re-encryption).
2. **Empirical FO Avalanche Characterization:** Directly observes whether the Fujisaki-Okamoto transform's ciphertext re-encryption check reliably catches multi-layer parameter skew or permits Silent Data Corruption (SDC).
3. **Engineering Precursor for Phase 16:** Proves whether dynamic memory protection toggling introduces measurement artifacts or performance noise before investing in an expansive 2,048-trial campaign.

### 5.2 Real Scientific Limitations:
1. **Sample Size (16 Trials):** 16 trials represent only 6 out of 128 twiddle indices ($\sim 4.7\%$) and only 13 active fault trials ($\sim 0.63\%$ of the total 2,048-bit parameter space). It is **not** a statistically powered vulnerability survey.
2. **Single Implementation & Architecture:** Conducted exclusively on `mlkem-native` C reference code compiled with Apple Clang 21 on Darwin ARM64. Does not characterize assembly-optimized implementations (AVX2, NEON) or space-grade processors (RAD750, GR740).
3. **Single Test Vector:** Uses 1 NIST test vector; message-dependent sensitivity cannot be generalized.

---

## 6. Permitted Conclusions vs Prohibited Claims

If the pilot executes cleanly and all 16 trials pass, the following strict epistemological boundaries govern all reporting and manuscript writing:

### Permitted Scientific Conclusions:
- "In the research-instrumented ML-KEM-768 C implementation, operational NTT twiddle constants at boundary indices 0, 1, 32, 63, 64, and 127 are actively loaded from memory and consumed by polynomial arithmetic."
- "Tested single-bit and word-level corruptions in active twiddle indices propagate through decapsulation arithmetic and trigger standard FIPS 203 implicit rejection ($K_{rej}$)."
- "Sham controls (`mask == 0x0000`) verify that dynamic virtual memory protection transitions introduce zero computational artifacts."
- "The in-place transactional rollback protocol achieves bit-identical restoration across consecutive executions on Darwin ARM64."

### Strictly Prohibited / Unsupported Claims:
- **PROHIBITED:** Any claim of "radiation tolerance", "radiation hardness", "space qualification", or "flight readiness".
- **PROHIBITED:** Any extrapolation to physical Single-Event Upsets (SEU) or silicon ion strikes.
- **PROHIBITED:** Any claim estimating general SDC rates or mathematical fault-invariance theorems for ML-KEM.
- **PROHIBITED:** Any claim regarding the unmodified production binary (where `mlk_zetas` is immutable in `__TEXT,__const`).

---

## Final Governance Verdict

# **GO FOR EXPLICIT HUMAN APPROVAL**

**Auditor Sign-Off:**  
All technical, cryptographic, memory-safety, and audit prerequisites across Phases 14A through 15K have been satisfied and independently verified. The decision to execute the 16-trial pilot is an executive research policy decision that now rests with the human principal.

*Notice: This memorandum serves as an advisory decision document. It does not authorize the execution of live trials or the commencement of Phase 16.*
