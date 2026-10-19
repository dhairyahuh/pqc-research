# Phase 2 — Step 2A: Independent Ciphertext Generation Report

**Document Date:** October 4, 2026  
**Auditor / Verification Engineer:** Skeptical Cryptographic Software Verification Audit  
**Target:** Fault-Campaign Runner (`tfib_experiments/tfib_experiment_runner.c`)  
**Scope:** Phase 2, Step 2A Independent Input Generation (Ciphertext & Valid Expected Secret)  
**Strict Boundary:** No modification to `rand()` in this step; no changes to production ML-KEM arithmetic; no changes to TFIB countermeasure logic; no changes to fault parameters or distribution; Phase 2 Step 2B not started.

---

## 1. Executive Summary & Verdict

### Final Recommendation: **READY FOR STEP 2B**

### Summary of Accomplishments
1. **Elimination of In-Tree Encapsulation:** In `tfib_experiments/tfib_experiment_runner.c`, the call to `mlkem768_enc(ct, ss_enc_scratch, pk)` has been completely removed.
2. **Integration of Independent Deterministic Encapsulation:** The runner now generates trial ciphertexts `ct` and their corresponding authentic shared secrets `ss_expected` directly via `independent_oracle_encaps_derand(ct, ss_expected, pk, seed32)` using `liboqs 0.16.0` (FIPS 203 Algorithm 16).
3. **Symbol & Call-Path Proof:**
   - Object-level symbol analysis confirms `_mlkem768_enc` is completely unreferenced by the runner translation unit (`nm -u` returns 0 matches).
   - Disassembly inspection (`otool -tv`) confirms zero branch/call instructions target `_mlkem768_enc`.
4. **Validation Suite Passes:** Tests A through E passed cleanly with exit code `0`, confirming deterministic reproducibility, complete independence of ciphertext generation, fault-free decapsulation agreement, canonical rejection consistency on mutated ciphertexts, and preservation of historical experimental data.

---

## 2. Initial Repository State

- **Git Branch:** `space-resilience-framework`
- **Head Commit Hash:** `55dd937cbad66b24e5c2c0b89b78fa776801913c`
- **Working Tree Status:** Clean with respect to production code in `algorithms/source_ref/` and `tfib_implementation/`.
- **Pre-Step Residual Defect:** In Step 1, the runner established `ss_expected` via `independent_oracle_decaps`, but still relied on in-tree `mlkem768_enc` to generate the ciphertext bytes `ct`, retaining a residual coupling to the Device Under Test's encapsulation routine.

---

## 3. API Contract and Seed Semantics

### 3.1 Function Signature
Declared in `tfib_experiments/phase11_oracle/independent_oracle.h:54–59`:
```c
int independent_oracle_encaps_derand(
    uint8_t *ct,
    uint8_t *ss,
    const uint8_t *pk,
    const uint8_t *seed32
);
```

### 3.2 Semantic Contract (FIPS 203 Algorithm 16 / ML-KEM.Encaps_internal)
- **Inputs:**
  - `pk`: 1184-byte byte array containing public key $(t \mathbin{\Vert} \rho) \in \mathbb{Z}_q^{3 \times 256} \times \{0,1\}^{256}$.
  - `seed32`: 32-byte uniform random message entropy $m \in \{0,1\}^{256}$.
- **Outputs:**
  - `ct`: 1088-byte ciphertext buffer $(c_1 \mathbin{\Vert} c_2)$.
  - `ss`: 32-byte shared secret buffer $K = G(m \mathbin{\Vert} H(pk))$.
- **Return Value:** `0` on success, `-1` on NULL pointer or backend error.
- **Randomness Handling:** In accordance with the prompt's strict constraints ("Do not replace `rand()` in this step"), `seed32` is drawn using the existing runner randomness mechanism:
  ```c
  uint8_t seed32[32];
  randombytes(seed32, sizeof(seed32));
  ```

---

## 4. Files Modified and Added

1. **`tfib_experiments/tfib_experiment_runner.c` (Modified):**
   - Removed declaration: `int mlkem768_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);`.
   - Removed scratch buffer: `uint8_t ss_enc_scratch[SS_BYTES];`.
   - Replaced in-tree encapsulation call with `independent_oracle_encaps_derand(ct, ss_expected, pk, seed32)`.
   - Added fatal error exit if `independent_oracle_encaps_derand` returns non-zero.
2. **`tfib_experiments/test_step2a_validation.c` (Newly Created):**
   - Implements focused verification tests A, B, C, D, and E.
3. **`tfib_experiments/run_step2a_tests.sh` (Newly Created):**
   - Automated build and test script with strict `set -euo pipefail`.

---

## 5. Before-and-After Input Generation Flow

### 5.1 Before Step 2A (Step 1 Baseline)
```
mlkem768_keypair(pk, sk);
mlkem768_enc(ct, ss_enc_scratch, pk);           <-- In-tree production encapsulation
independent_oracle_decaps(ss_expected, ct, sk); <-- Oracle decapsulates in-tree ct
independent_oracle_compute_rejection(ss_rej_expected, sk, ct);
```

### 5.2 After Step 2A (Independent Input Generation)
```
mlkem768_keypair(pk, sk);
randombytes(seed32, 32);                        <-- Existing campaign randomness draw
independent_oracle_encaps_derand(ct, ss_expected, pk, seed32); <-- External oracle generates BOTH ct and ss_expected
independent_oracle_compute_rejection(ss_rej_expected, sk, ct);
```
- **Ciphertext Provenance:** `ct` is generated exclusively by `liboqs 0.16.0`.
- **Expected Secret Provenance:** `ss_expected` is generated simultaneously by `liboqs 0.16.0` from seed $m$.
- **Rejection Key Provenance:** `ss_rej_expected` is generated by TweetFIPS-202 from $z \mathbin{\Vert} ct$.
- **DUT Role:** Production code is now invoked **strictly** in the decapsulation path under test (`mlkem768_dec_monitored`).

---

## 6. Focused Validation Test Results

Executed via `./tfib_experiments/run_step2a_tests.sh`:

```text
================================================================================
PHASE 2 — STEP 2A: INDEPENDENT CIPHERTEXT GENERATION VALIDATION SUITE
================================================================================

Independent Oracle Initialized: Independent Reference Oracle: Open Quantum Safe (liboqs) v0.16.0 + FIPS 202 Specification Reference (TweetFIPS-202)

[Test A] Deterministic Encapsulation Reproducibility
  - Encapsulation Call 1 RC: 0, Call 2 RC: 0
  - Repeated Ciphertext Byte-Exact Match: YES
  - Repeated Shared Secret Byte-Exact Match: YES
  -> Result: PASS

[Test B] Independent Ciphertext Generation (Call-Path & Symbol Inspection)
  - Runner Object Reference Check (_mlkem768_enc unreferenced): YES
  - Disassembly Branch Target Check (0 calls to _mlkem768_enc): YES
  - Runner Source Check (mlkem768_enc absent): YES
  -> Result: PASS

[Test C] Valid Decapsulation Agreement with Oracle Ciphertext
  - Oracle Encapsulation Return Code: 0
  - Production Decapsulation Status: 0x5A5A5A5A (expected 0x5A5A5A5A)
  - Production Output Matches Oracle Valid Shared Secret: YES
  -> Result: PASS

[Test D] Rejection Expectation Consistency on Mutated Ciphertext
  - Oracle Rejection Calculation Return Code: 0
  - Production Decapsulation Status: 0xA5A5A5A5
  - Production Output Matches Expected Rejection Secret: YES
  - Output Strictly Differs from Valid Shared Secret: YES
  -> Result: PASS

[Test E] Campaign Configuration Preservation & Historical Data Protection
  - Historical tfib_raw_results.csv Untouched: YES
  - Historical tfib_trial_level_results.csv Untouched: YES
  - Step 2A Test Output CSV Written: YES (746 bytes)
  -> Result: PASS

================================================================================
STEP 2A VALIDATION VERDICT: ALL TESTS PASSED (PASS) (0 failures)
================================================================================
```

---

## 7. Source-Level Independence Assessment

| Metric | Verification Method | Result | Status |
| :--- | :--- | :--- | :--- |
| **Translation Unit Symbols** | `nm -u tfib_experiment_runner.o \| grep mlkem768_enc` | 0 occurrences | **Verified** |
| **Disassembly Branch Targets** | `otool -tv tfib_experiment_runner \| grep -E "bl.*_mlkem768_enc$"` | 0 occurrences | **Verified** |
| **Source-Level Invocations** | `grep -n "mlkem768_enc" tfib_experiments/tfib_experiment_runner.c` | 0 occurrences | **Verified** |
| **Decapsulation Independence**| Production decapsulation decapsulates external oracle ciphertext | Matches valid shared secret with 0 differences | **Verified** |

---

## 8. Compatibility Assessment

- **Fault Schedules:** `stage = (t % 7) + 1`, `b_idx = (t * 17) % 128`, `bit = (t % 15) + 1` remain untouched.
- **Fault Loci:** `TFIB_FAULT_NONE`, `TFIB_FAULT_OP_TWIDDLE`, `TFIB_FAULT_REF_TWIDDLE`, `TFIB_FAULT_SIMULTANEOUS`, `TFIB_FAULT_CHECKER_LOGIC`, `TFIB_FAULT_META_TAG` remain untouched.
- **Classification Decisions:** Decision boundaries for `CLEAN_SUCCESS`, `GENUINE_RECOVERY`, `INEFFECTIVE_FAULT_VALID`, `LOCAL_BLIND_FO_CONTAINED`, `SAFE_FAIL_STOP`, and `SILENT_DATA_CORRUPTION` remain identical.
- **Historical Data:** `tfib_raw_results.csv` and `tfib_trial_level_results.csv` confirmed unmodified.

---

## 9. Limitations & Unresolved Issues (Out-of-Scope for Step 2A)

1. **Non-CSPRNG Randomness:** `randombytes` still delegates to standard C `rand()`. (Scheduled for replacement with CSPRNG `arc4random_buf` in Step 2B).
2. **Keypair Generation Provenance:** Keypair generation still calls in-tree `mlkem768_keypair(pk, sk)`. (Scheduled for independent derandomized key generation in Step 2B).
3. **Countermeasure Harness Coupling:** `tfib_meta.c:94` and `tfib_ref.c:54` still contain test-only coupling flags (`locus` and `!persistent`).
4. **Table Colocation:** Twiddle factor tables remain colocated at the 448-byte delta.

---

## 10. Final Recommendation

### **Verdict: READY FOR STEP 2B**

**Justification:**  
The campaign runner now sources all trial ciphertexts and expected valid shared secrets directly from the external reference oracle (`liboqs 0.16.0`). The in-tree encapsulation routine `mlkem768_enc` is completely unreferenced by the runner translation unit and dead in the binary. Historical experimental results remain protected. The prerequisites for Step 2B (CSPRNG integration and keypair independence) are established.

*Strict Scope Boundary Reminder: Execution halted. No changes were made to `rand()`, TFIB internals, or twiddle tables, and Step 2B has not started.*
