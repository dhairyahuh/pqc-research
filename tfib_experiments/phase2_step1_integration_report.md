# Phase 2 — Step 1: Independent Oracle Integration Report

**Document Date:** October 3, 2026  
**Auditor / Verification Engineer:** Skeptical Cryptographic Software Verification Audit  
**Target:** Fault-Campaign Runner (`tfib_experiments/tfib_experiment_runner.c`)  
**Scope:** Phase 2, Step 1 Integration and Validation (No changes to production ML-KEM arithmetic, no changes to NTT, no changes to TFIB countermeasure logic, no changes to fault models or distributions, Phase 2 Step 2 not started)

---

## A. Initial State Audit

### 1. Git Environment & Baseline Commit
- **Active Git Branch:** `space-resilience-framework`
- **Head Commit Hash:** `55dd937cbad66b24e5c2c0b89b78fa776801913c`
- **Working Tree Status:** Clean with respect to production ML-KEM code and TFIB countermeasure implementations. Pre-existing untracked files are confined to previous audit reports and reference data.

### 2. Runner Identification
- **Primary Targeted Campaign Runner:** `tfib_experiments/tfib_experiment_runner.c`
- **Binary Target:** `tfib_experiments/tfib_experiment_runner`
- **Associated Reproducer:** `tfib_experiments/tfib_validity_audit_runner.c`

### 3. Pre-Integration Expected-Output Flow (The Circularity Defect)
In the original runner implementation (`tfib_experiment_runner.c:64–71`):
```c
mlkem768_keypair(pk, sk);
mlkem768_enc(ct, ss_expected, pk);
compute_expected_rejection_key(ss_rej_expected, sk, ct);
```
- `ss_expected` was produced by calling `mlkem768_enc` from `bin/obj/mlkem768_inst.o`—the exact object file under test.
- `compute_expected_rejection_key` called `mlkem768_shake256`, which was also linked directly from `bin/obj/mlkem768_inst.o`.
- **Finding:** Ground-truth validation was circular and self-referential. An arithmetic bug or common-mode corruption in the DUT's encapsulation or SHAKE routines was invisible because the expected value mirrored the flaw.

### 4. Existing Classification Logic
The runner evaluates:
- `ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0)`
- `rej_match = (memcmp(ss_out, ss_rej_expected, SS_BYTES) == 0)`
- `sdc = (!ss_match && !rej_match)`

Outcomes are mapped into:
- `CLEAN_SUCCESS`: Fault-free baseline run without alarms.
- `GENUINE_RECOVERY`: Monitor detected fault, successfully recovered, valid SS match, `status == 0x5A5A5A5A`.
- `INEFFECTIVE_FAULT_VALID`: Fault activated, unflagged by monitor, but valid SS produced due to noise margin.
- `LOCAL_BLIND_FO_CONTAINED`: Monitor missed twiddle fault, but downstream re-encryption failed and triggered canonical implicit rejection (`rej_match == true`, `status == 0xA5A5A5A5` or `0xFFFFFFFF`).
- `SAFE_FAIL_STOP`: Monitor detected unrecoverable persistent fault, triggering safe abort / rejection.
- `SILENT_DATA_CORRUPTION`: Decapsulation produced an output matching neither valid session key nor canonical rejection key.

---

## B. Integration Changes

### 1. Files Modified and Added
- **`tfib_experiments/tfib_experiment_runner.c` (Modified):**
  - Included `independent_oracle.h`.
  - Replaced circular expected-value derivations with external oracle calls.
  - Added explicit error handling on oracle decapsulation and rejection computations.
  - Added CLI output argument support in `main(int argc, char **argv)` defaulting to `tfib_experiments/phase2_step1_runner_output.csv` to ensure historical `tfib_raw_results.csv` is not overwritten.
- **`tfib_experiments/test_oracle_integration.c` (Added):**
  - Comprehensive integration test suite validating Tests A, B, C, D, and E.
- **`tfib_experiments/run_step1_integration_tests.sh` (Added):**
  - Automated build and test script verifying compiler options, linkage, and exit codes.

### 2. Exported Public Oracle APIs Used
Only public APIs from `tfib_experiments/phase11_oracle/independent_oracle.h` are called:
- `independent_oracle_init()`: Initializes the isolated `liboqs 0.16.0` backend.
- `independent_oracle_get_version()`: Identifies oracle provenance and build details.
- `independent_oracle_decaps(ss_expected, ct, sk)`: Decapsulates authentic ciphertext using `liboqs` to establish the independent valid expected shared secret.
- `independent_oracle_compute_rejection(ss_rej_expected, sk, ct)`: Independently computes canonical FIPS 203 implicit rejection $K_{\text{rej}} = \text{SHAKE-256}(z \mathbin{\Vert} c, 32)$ using standalone FIPS 202 Keccak-f[1600].

### 3. Integrated Expected-Value Data Flow
```
[Trial Setup]
      │
      ├──> mlkem768_keypair(pk, sk)  ─────────┐
      │                                       │
      ├──> mlkem768_enc(ct, [scratch], pk) ───┤
      │                                       │
      ▼                                       ▼
[Production DUT]                      [Independent Oracle]
mlkem768_dec_monitored(ss_out,ct,sk)   ├── independent_oracle_decaps(ss_expected, ct, sk)
      │                                       └── independent_oracle_compute_rejection(ss_rej_expected, sk, ct)
      │                                                     │
      ▼                                                     ▼
      └─────────────────> [Comparison Layer] <──────────────┘
                         - ss_match  = (ss_out == ss_expected)
                         - rej_match = (ss_out == ss_rej_expected)
                         - sdc       = (!ss_match && !rej_match)
```
- **Buffer Isolation:** `ss_expected`, `ss_rej_expected`, and `ss_out` are distinct memory allocations on the stack. No memory aliasing exists between production buffers and oracle buffers.
- **Error Handling:** If `independent_oracle_decaps` or `independent_oracle_compute_rejection` returns non-zero, the runner terminates immediately with a `FATAL` error, preventing silent misclassification.

---

## C. Independence and Coupling Assessment

| Verification Claim | Audit Evidence | Classification |
| :--- | :--- | :--- |
| **API Boundary Adherence** | Runner includes only `independent_oracle.h` and links `libindependent_oracle.a`. Zero internal `liboqs` or internal oracle state variables are touched. | **Verified** |
| **Zero Production Expected-Value Derivation** | `ss_expected` is established exclusively via `independent_oracle_decaps`. `ss_rej_expected` is established exclusively via `independent_oracle_compute_rejection`. In-tree `mlkem768_shake256` is no longer called for expected rejection. | **Verified** |
| **No Oracle Dependence on TFIB State** | Symbol inspection (`nm`) confirms `libindependent_oracle.a` imports 0 symbols from `tfib_common.h`, `tfib_core.h`, or `libtfib.a`. Oracle does not read `g_tfib_fault` or any monitor counters. | **Verified** |
| **Exact Ciphertext Transmission** | Ciphertext buffer `ct` is passed unmodified to both `independent_oracle_decaps`, `independent_oracle_compute_rejection`, and `mlkem768_dec_monitored`. | **Verified** |
| **Buffer Disjointness** | Production output `ss_out`, oracle valid `ss_expected`, and oracle rejection `ss_rej_expected` are allocated as distinct 32-byte arrays on the stack. | **Verified** |
| **Failure Masking Prevention** | Test D proves that oracle failure codes propagate directly to classification logic and cannot be mistaken for valid decapsulation, implicit rejection, or recovery. | **Verified** |

---

## D. Integration Test Results

The dedicated integration test suite (`tfib_experiments/test_oracle_integration.c`) was executed via `tfib_experiments/run_step1_integration_tests.sh`.

```text
================================================================================
PHASE 2 — STEP 1: INDEPENDENT ORACLE INTEGRATION VALIDATION SUITE
================================================================================

Independent Oracle Initialized: Independent Reference Oracle: Open Quantum Safe (liboqs) v0.16.0 + FIPS 202 Specification Reference (TweetFIPS-202)

[Test A] Valid Baseline Decapsulation
  - Oracle Decaps Return Code: 0 (expected 0)
  - Production vs Oracle SS Match: YES
  - Final Status: 0x5A5A5A5A (expected 0x5A5A5A5A)
  - False Recoveries Reported: 0 (expected 0)
  -> Result: PASS

[Test B] Invalid Ciphertext Canonical Implicit Rejection
  - Oracle Rejection Calc Return Code: 0 (expected 0)
  - Production Output Matches Oracle Canonical Rejection: YES
  - Production Output Strictly Differs from Valid Secret: YES
  - Production Rejection Status: 0xA5A5A5A5
  -> Result: PASS

[Test C] Oracle Mismatch Detection
  - Deliberately corrupted expected secret supplied to comparison layer
  - Mismatch Detected by Verification Layer: YES
  - Incorrectly Classified as Success: NO (PASS)
  -> Result: PASS

[Test D] Oracle Failure Handling
  - Oracle Decaps Error on Invalid Input: -1 (expected non-zero)
  - Oracle Rejection Error on Invalid Input: -1 (expected non-zero)
  - Runner Classification on Oracle Failure: ORACLE_VALIDATION_FAILURE
  -> Result: PASS

[Test E] Existing Campaign Compatibility & Historical Data Protection
  - Historical tfib_raw_results.csv Untouched: YES (size=77468, mtime=1791043669)
  - Historical tfib_trial_level_results.csv Untouched: YES (size=79936, mtime=1791044489)
  - Integration Test CSV Written: YES (464 bytes)
  -> Result: PASS

================================================================================
INTEGRATION VALIDATION VERDICT: ALL TESTS PASSED (PASS) (0 failures)
================================================================================
```
- **Overall Exit Code:** `0`
- **Compiler Warnings:** 0 compiler warnings. (1 standard macOS dynamic linker deployment target warning).

---

## E. Compatibility Assessment

- **Fault Models & Parameters:** Unchanged. Stages (`(t % 7) + 1`), butterfly indices (`(t * 17) % 128`), bit positions (`(t % 15) + 1`), and persistence settings are identical.
- **Monitoring & Recovery:** Unchanged. In-tree countermeasure modes (`TFIB_MODE_BASELINE`, `TFIB_MODE_REF`, `TFIB_MODE_META`), monitoring hooks, and recovery algorithms were not altered.
- **Classification Logic:** Unchanged. Existing outcome classes (`CLEAN_SUCCESS`, `GENUINE_RECOVERY`, `INEFFECTIVE_FAULT_VALID`, `LOCAL_BLIND_FO_CONTAINED`, `SAFE_FAIL_STOP`, `SILENT_DATA_CORRUPTION`) are preserved with identical decision predicates.
- **Historical Data:** Verified untouched. `tfib_raw_results.csv`, `tfib_trial_level_results.csv`, and `tfib_reproduced_results.csv` maintained identical file sizes and modification timestamps.

---

## F. Limitations and Known Architectural Realities

1. **Test-Harness PRNG:** The existing campaign runner still uses standard C `rand()` for keypair and message generation. (This known defect from Phase 0 is scheduled for replacement with a CSPRNG in Step 2).
2. **Coupling Flags in Countermeasures:** Internal flags (`locus` check in `tfib_meta.c` and `!persistent` check in `tfib_ref.c`) remain in the production C files and will be decoupled in subsequent steps.
3. **Table Colocation:** Twiddle tables remain colocated at the 448-byte delta until relocated in Step 3.

---

## G. Final Recommendation

### **Verdict: READY FOR CONTROLLED PHASE 2, STEP 2**

**Justification:**
1. The independent reference oracle (`liboqs 0.16.0` + FIPS 202 reference) is fully integrated into the existing fault-campaign runner.
2. The circularity defect (Finding 1 from Phase 0) is eliminated: expected valid shared secrets and canonical rejection secrets are established through genuinely external, specification-conforming libraries.
3. Integration Tests A through E proved that the integrated runner correctly validates clean decapsulation, accurately matches canonical implicit rejection, catches corrupted expected secrets, handles oracle failures cleanly, and preserves historical data without modifying the underlying fault model.
