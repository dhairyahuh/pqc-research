# Phase 15J — Readiness Assessment for a Limited Persistent-Table Pilot

**Reviewer:** Independent Skeptical Cryptographic Systems Researcher & Experimental Safety Reviewer  
**Audit Target:** Phase 14–15 Architecture, Hardened Pilot Runner (`pilot_runner.c`), Phase 15I Verification Audit, Rollback Protocol, and Experimental Safety Gates  
**Target Repository State:** Git branch `space-resilience-framework` (HEAD: `4a2c4ebf9274a9188db3610a4f8448902caed056`)  
**Mode:** Strictly Read-Only Assessment (Zero code edits, zero builds, zero trial executions, zero memory mutations)  
**Date:** 2026-10-11  
**Directory:** `research/phase14_persistent_arm_design/`  

---

## Executive Summary

This readiness assessment conducts a formal safety, methodological, and scientific evaluation of the proposed 16-trial persistent-table feasibility pilot. Following the resolution and independent verification of finding F-15G-01 in Phases 15H and 15I, this review evaluates whether the research harness meets the rigorous technical standards necessary for human authorization.

This assessment is a **readiness recommendation only**. It does **not** grant authorization to execute live trials or begin Phase 16.

---

## 1. What Exact Hypothesis Would the Proposed Limited Pilot Test?

The proposed 16-trial pilot tests a specific, falsifiable systems-cryptographic hypothesis:

> **Formal Hypothesis:**  
> In the research-relocated ML-KEM-768 decapsulation binary on Darwin ARM64, a single-word bit-flip applied directly to the in-memory operational twiddle-factor table (`mlk_zetas_page` in `__DATA_CONST,__zetas_page`):
> 1. Is actively consumed by compiled polynomial arithmetic (NTT, inverse NTT, and basemul) rather than bypassed via immediate constants or dead-code elimination;
> 2. Causes deterministic divergence in the decapsulation output that is classifiable under the FIPS 203 implicit rejection oracle ($K_{rej} = J(z \parallel c, 32)$); and
> 3. Can be safely injected, observed, and restored in-place to bit-identical baseline state across consecutive executions without triggering kernel memory protection traps, collateral padding corruption, or cross-trial state contamination.

---

## 2. What Can Its Current Trial Design Establish, and What Can It Not Establish?

### 2.1 What the Current Pilot CAN Establish:
1. **Memory Subsystem & OS Tolerance:** Proves whether dynamic virtual memory protection transitions (`vm_protect` RO $\rightarrow$ RW $\rightarrow$ RO) operate stably on macOS Darwin without generating uncatchable kernel panics or protection violations.
2. **Deterministic Arithmetic Consumption:** Confirms that operational constants at boundary indices (root index 0, forward layer 1 index 1, mid-layer index 32, final layer index 63, mulcache index 64, and inverse NTT index 127) are loaded from backing memory during execution.
3. **Endpoint Classification Fidelity:** Empirically verifies whether the Fujisaki-Okamoto (FO) transform detects persistent constant corruption and triggers standard implicit rejection ($K_{rej}$) or produces unrejected altered outputs (`DIFFERENT_OUTPUT`).
4. **Instrumentation Neutrality via Sham Controls:** Validates via Trials 2 and 13 (`bit_mask == 0x0000`) that the memory unprotection, dummy write, and reprotection sequence introduces zero computational artifacts when constant values are unchanged.
5. **Transactional In-Place Hygiene:** Proves whether the 6-step cleanup and verification pipeline can repeatedly restore 100% bit-identical table state.

### 2.2 What the Current Pilot CANNOT Establish:
1. **Physical Radiation Tolerance / SEU Resilience:** Under no circumstances does software memory mutation simulate or predict physical Single-Event Upsets (SEU), multi-cell upsets (MCU), total ionizing dose (TID), or cosmic ray interactions in silicon.
2. **Statistically Significant SDC / Vulnerability Rates:** 16 deterministic boundary trials on a single NIST test vector cannot estimate general Silent Data Corruption (SDC) probabilities across the 2,048-bit parameter space or random message distributions.
3. **Behavior of Production Upstream Binaries:** In unmodified production builds, `mlk_zetas` is located immutably in `__TEXT,__const` protected by Mach-O W^X enforcement. The pilot characterises only the research-instrumented build.
4. **Generalization Across Architectures:** Findings apply strictly to Apple Clang 21 on Darwin ARM64 and cannot be extrapolated to x86_64, RISC-V, or space-grade processors (e.g., RAD750, GR740) without independent compilation and verification.

---

## 3. Are Restoration, Protection Rollback, Canary Verification, Baseline Rechecking, and Failure Handling Sufficiently Specified?

**Evaluation:** **SUFFICIENTLY SPECIFIED AND HARDENED.**

Control-flow analysis of `pilot_runner.c` confirms comprehensive transactional mechanics:

```
[ Trial Execution ]
         |
         v
[ Cleanup Step 1: vm_protect(RW) ] --------(Fail)-----> [ cleanup_passed = 0 ]
         | (Success)                                              |
         v                                                        |
[ Cleanup Step 2: vtable[idx] = orig_val & Read-Back ] -(Fail)--> |
         | (Success)                                              |
         v                                                        |
[ Cleanup Step 3: vm_protect(RO) ] --------(Fail)-----> |
         | (Success)                                              |
         v                                                        |
[ Cleanup Step 4: vm_region_64 Kernel Query (Prot=RO) ] -(Fail)-> |
         | (Success)                                              |
         v                                                        |
[ Cleanup Step 5: 128-Entry Table & 16KB Padding Canaries ] (Fail)-> |
         | (Success)                                              |
         v                                                        |
[ Cleanup Step 6: Baseline Decapsulation KAT Recheck ] --(Fail)-> |
         | (Success)                                              v
         v                                            [ records[t].restoration_status = "RESTORATION_FAILED" ]
[ records[t].restoration_status =                       [ Terminate Runner Immediately via break; ]
  "RESTORED_AND_BASELINE_RECHECK_PASSED" ]
```

1. **Restoration:** Direct write of `orig_val` through volatile pointer with immediate read-back assertion.
2. **Protection Rollback:** Explicit `vm_protect(RO)` followed by live kernel inquiry via `vm_region_64` verifying `(v_info.protection & VM_PROT_WRITE) == 0`.
3. **Canary Verification:** Dual verification: `memcmp(table_ptr, golden_zetas, 256)` checks table integrity, while a loop across the trailing 16,128 padding bytes asserts zero collateral memory corruption.
4. **Baseline Rechecking:** Execution of `mlkem768_dec` on clean reference inputs verifying shared secret reproduction.
5. **Failure Handling:** Any failure in steps 1–6 flags `"RESTORATION_FAILED"` and executes an emergency loop abort (`break;`). In addition, signal traps for `SIGBUS` and `SIGSEGV` invoke `_exit(128 + sig)`.

---

## 4. Does the Design Distinguish Invalid, Unexecuted, Sham, Ineffective, Detected, Rejected, and Output-Changing Trials Without Conflating Them?

**Evaluation:** **STRICTLY AND ORTHOGONALLY PARTITIONED.**

The runner's 9-column data model separates all experimental outcomes without semantic conflation:

| Experimental Category | `target_idx` / `bit_mask` | `mutation_status` | `consumption_status` | `crypto_endpoint` | `restoration_status` |
|:---|:---|:---:|:---:|:---:|:---:|
| **Invalid Target** | `< -1` or `>= 128` | `REJECTED` | `VERIFIED_NOT_CONSUMED` | `NOT_RUN` | `NOT_RUN_INVALID_TARGET` |
| **Unexecuted Abort** | Valid (unprotect fail) | `REJECTED` | `UNKNOWN` | `NOT_RUN` | `UNKNOWN` |
| **Valid Sham Control** | `idx >= 0`, `mask == 0` | `APPLIED` | `VERIFIED_NOT_CONSUMED` | `EXPECTED_OUTPUT` | `RESTORED_AND_BASELINE_RECHECK_PASSED` |
| **Ineffective (Unconsumed)**| `idx >= 0`, `mask != 0` | `APPLIED` | `VERIFIED_NOT_CONSUMED` | `EXPECTED_OUTPUT` | `RESTORED_AND_BASELINE_RECHECK_PASSED` |
| **Detected / Rejected** | `idx >= 0`, `mask != 0` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` |
| **Output-Changing (SDC)** | `idx >= 0`, `mask != 0` | `APPLIED` | `VERIFIED_CONSUMED` | `DIFFERENT_OUTPUT` | `RESTORED_AND_BASELINE_RECHECK_PASSED` |
| **Crash / No Output** | `idx >= 0`, `mask != 0` | `APPLIED` | `VERIFIED_CONSUMED` | `NO_OUTPUT` | `RESTORED_AND_BASELINE_RECHECK_PASSED` |

- Phase 15H eliminated the prior bug where invalid targets claimed restoration and baseline success.
- Each column reflects an independent dimension: operation attempt, arithmetic consumption, cryptographic behavior, and memory restoration.

---

## 5. What is the Minimum Evidence Needed Before a Human Can Authorize the Pilot?

A human principal should require the following concrete evidence before granting execution authorization:

1. **Independent Verification Audit (Completed):** Phase 15I read-only audit confirming that Finding F-15G-01 is resolved and that the binary contains the corrected code and symbols.
2. **Preflight Oracle Check (Passed):** Verification that `./bin/pilot_runner --check-oracle` runs cleanly with exit code 0, confirming bit-identical FIPS 202 and FIPS 203 oracle derivations without mutating memory.
3. **Clean Preflight Dry-Run Protocol:** Agreement that the runner executes its 5 mandatory preflight checks (symbol alignment, live VM mapping, initial table canary, protection dry-run toggling, and baseline KAT) before attempting Trial 0.
4. **Strict Epistemological Framing Agreement:** Written sign-off that results will be interpreted strictly under `CLAIM_BOUNDARIES.md` (software memory fault model, not radiation testing).
5. **Unmodified Production Baseline Preservation:** Confirmation that production cryptographic source files remain 100% untampered and verified against NIST KATs.

All technical prerequisites (1–3, 5) have been verified in the repository. Prerequisite 4 requires human executive sign-off.

---

## 6. What Abort Conditions and Post-Run Integrity Checks Must Be Mandatory?

### 6.1 Mandatory Pre-Run & In-Run Abort Conditions (Kill Switch):
The runner process must immediately abort execution if any of the following occur:
1. **Preflight Failure:** Any non-zero exit in Preflights 1 through 5.
2. **Kernel Error:** Any call to `vm_protect` returning a status other than `KERN_SUCCESS` (`0`).
3. **Hardware Trap Signal:** Interception of `SIGBUS`, `SIGSEGV`, or `SIGILL`.
4. **Read-back Discrepancy:** Mutation read-back mismatch or restoration read-back mismatch.
5. **Permission Leak:** `vm_region_64` reporting write permissions active after reprotection.
6. **Padding Contamination:** Any non-zero byte detected in the 16,128-byte page padding canary.
7. **Cross-Trial Contamination:** Post-trial baseline decapsulation producing a shared secret differing from `test_vector_ss`.

### 6.2 Mandatory Post-Run Integrity Checks:
Following completion of the 16 trials:
1. **Final Baseline Control (Trial 15):** Verification that Trial 15 reproduces the golden shared secret.
2. **Full FIPS 203 KAT Suite:** Execution of `./bin/test_fips_kats_research` to verify that 100% of NIST test vectors pass on the research binary following pilot completion.
3. **Ledger Schema Audit:** Independent programmatic parsing of emitted ledger rows verifying field counts, checksums, and absence of `RESTORATION_FAILED` records.

---

## 7. Would the Result Materially Strengthen the Manuscript, or is the Experiment Unlikely to Add Enough Scientific Value?

### 7.1 Scientific Evaluation:
- **Comparison to Prior Work (TFIB):** The project previously executed extensive Transient Fault Injection in Butterflies (TFIB, Phases 1–10). TFIB modeled computational register/ALU glitches by corrupting a single stack variable during a single butterfly loop.
- **Added Scientific Value of Persistent Arm:**
  1. *Dual-Phase Parameter Faults:* Corrupting backing memory tests what occurs when the constant remains corrupted across *both* the inverse NTT (during polynomial recovery) *and* the forward NTT / basemul (during re-encryption).
  2. *Multi-Layer Propagation:* A corrupted table entry affects every butterfly in every layer that references that twiddle factor, testing whether the FO transform's error avalanche behaves differently under multi-stage parameter skew.
- **Scientific Caveat & Value Cap:**
  - A 16-trial pilot is **an engineering feasibility qualification**, not a statistically significant dataset.
  - It does **not** provide publishable vulnerability rates.
  - Its value is strictly enabling: it either qualifies the automated harness for a full 2,048-trial campaign (Phase 16) or disqualifies the approach if Darwin VM overhead or table relocation introduces uncontrolled confounders.

### 7.2 Net Scientific Assessment:
The pilot adds material scientific value **only as an engineering milestone toward characterising multi-stage constant corruption in lattice KEMs**. It must be strictly framed as a software-level memory fault model. If so framed, it meaningfully strengthens the manuscript by demonstrating whether the FO transform's re-encryption check reliably catches persistent parameter skew.

---

## Final Readiness Recommendation

# **READY FOR HUMAN APPROVAL**

### Rationale:
1. All technical defects, including blocking finding **F-15G-01**, have been corrected and independently audited (Phase 15I).
2. The trial harness incorporates rigorous preflights, 6-step transactional cleanup, kernel permission verification, padding canaries, and emergency abort traps.
3. The claim boundaries, trial taxonomy, and abort criteria are fully formalized.
4. All repository files are cleanly reconciled, and historical artifacts are preserved byte-for-byte.

*Notice: This evaluation certifies engineering readiness. It does not authorize the execution of live pilot trials or the commencement of Phase 16. Execution requires explicit human authorization.*
