# Live Code Demonstration Guide
## 3-to-5 Minute Technical Walkthrough for Presentation Day

**Goal:** Provide a flawless, reproducible, 3-to-5 minute live demonstration showing the C source code architecture, running safe verification commands, and walking through empirical proof without risking accidental data loss.

---

## 0. Golden Rules for the Demonstration

1. **Safety First:** Never run scripts that re-generate raw datasets or overwrite historical CSV results during the live talk.
2. **Deterministic Commands Only:** Run pre-compiled verification binaries that output clean, immediate PASS results in under 2 seconds.
3. **Keep Files Pre-Opened:** Have the 4 primary source files pre-opened in your IDE/editor with line numbers visible.
4. **Follow the 5-Step Story:**
   - Step 1: Prove FIPS compliance (`test_fips_kats`).
   - Step 2: Show the Register Snapshot in `poly.c`.
   - Step 3: Show the Invariant Check & Local Rollback in `mlkem_fault_hooks.c`.
   - Step 4: Show the Hardened Twiddle Binding in `tfib_ref.c` (Theorem 1).
   - Step 5: Run the Countermeasure Independence Test Suite (`test_step2c_countermeasure_independence`).

---

## Step-by-Step Demonstration Script

### Step 1: Demonstrate FIPS Standard Cryptographic Conformance (~45 seconds)

- **What to Run in Terminal:**
  ```bash
  ./bin/test_fips_kats
  ```
- **Execution Time:** ~0.5 seconds `[DIRECTLY OBSERVED]`
- **Expected Output:**
  ```text
  =========================================================================
   NIST FIPS 203 & 204 KNOWN ANSWER TEST (KAT) VERIFICATION SUITE
   Sources: mlkem-native (fc269bc2d106) & mldsa-native (88a5369bb911)
  =========================================================================
  --- [1/6] ML-KEM-512 (FIPS 203) --- PASS
  --- [2/6] ML-KEM-768 (FIPS 203) --- PASS
  --- [3/6] ML-KEM-1024 (FIPS 203) --- PASS
  --- [4/6] ML-DSA-44 (FIPS 204) --- PASS
  --- [5/6] ML-DSA-65 (FIPS 204) --- PASS
  --- [6/6] ML-DSA-87 (FIPS 204) --- PASS
  =========================================================================
   >>> ALL NIST FIPS 203 & 204 TEST VECTORS VERIFIED SUCCESSFULLY (PASS) <<<
  =========================================================================
  ```
- **What to Say Verbally:**  
  *"First, I want to establish our cryptographic foundation. Before adding any fault resilience, our core implementation must strictly adhere to NIST FIPS 203 and 204. As you can see, our compiled binary executes the official NIST Known Answer Tests across ML-KEM-512, 768, and 1024, verifying that key generation, encapsulation, and decapsulation produce byte-identical matching shared keys."*
- **What the Audience Understands:** The underlying codebase is not a toy prototype; it is fully conformant to official NIST FIPS standards.

---

### Step 2: Show Register Snapshotting in `poly.c` (~45 seconds)

- **File to Open in IDE:** [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L390-L425)
- **Function Name:** `mlk_ntt_butterfly_block`
- **Line Range to Highlight:** Lines 390–420
- **Code to Point At:**
  ```c
  #if defined(MLKEM_RESEARCH_FAULT_HOOKS)
    unsigned b_idx = (start / (2 * len)) * len + (j - start);
    int16_t zeta_val = zeta;
    int16_t u_saved = r[j];        // <-- Register snapshot of operand u
    int16_t v_saved = r[j + len];  // <-- Register snapshot of operand v
    
    // Live Cooley-Tukey butterfly arithmetic
    int16_t t = mlk_fqmul(r[j + len], zeta_val);
    r[j + len] = (int16_t)(r[j] - t);
    r[j] = (int16_t)(r[j] + t);

    // Call native invariant monitor
    native_ntt_monitor_butterfly(layer, b_idx, zeta_val, u_saved, v_saved, t, &r[j], &r[j + len]);
  #endif
  ```
- **What to Say Verbally:**  
  *"Here is the heart of our micro-monitoring architecture inside poly.c. In lines 393 and 394, right before each butterfly operation, we preserve the input coefficients in local variables `u_saved` and `v_saved`. The compiler maps these directly to CPU registers. The butterfly executes normally on lines 400 through 406. Immediately after, line 419 calls our native monitor, passing the saved register snapshots along with pointers to the live outputs."*
- **What the Audience Understands:** The snapshotting mechanism incurs zero heap allocations and operates entirely in local CPU registers.

---

### Step 3: Show Invariant Verification & In-Place Rollback in `mlkem_fault_hooks.c` (~60 seconds)

- **File to Open in IDE:** [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L614-L663)
- **Function Name:** `native_ntt_monitor_butterfly`
- **Line Range to Highlight:** Lines 614–663
- **Code to Point At:**
  ```c
  // Dual-rail algebraic invariant checks modulo 3329
  diff_c = ((int32_t)(*r_j) - (int32_t)(*r_j_len) - 2 * (int32_t)t_check) % 3329;
  sum_c  = ((int32_t)(*r_j) + (int32_t)(*r_j_len) - 2 * (int32_t)u_saved) % 3329;

  if (diff_c != 0 || sum_c != 0) {
      g_ntt_native_monitor.mismatch_count++;

      if (g_ntt_native_monitor.allow_retry) {
          // In-place localized rollback: restore operands
          *r_j = u_saved;
          *r_j_len = v_saved;

          // Retry single butterfly
          int16_t t_retry = monitor_fqmul(v_saved, zeta);
          int16_t u_new = (int16_t)(u_saved + t_retry);
          int16_t v_new = (int16_t)(u_saved - t_retry);

          *r_j = u_new;
          *r_j_len = v_new;

          // Re-verify repaired calculation
          int32_t diff_retry = ((int32_t)u_new - (int32_t)v_new - 2 * (int32_t)t_retry) % 3329;
          int32_t sum_retry  = ((int32_t)u_new + (int32_t)v_new - 2 * (int32_t)u_saved) % 3329;

          if (diff_retry == 0 && sum_retry == 0) {
              g_ntt_native_monitor.recovered_count++;
          } else {
              g_ntt_native_monitor.persistent_count++;
          }
      }
  }
  ```
- **What to Say Verbally:**  
  *"Now let us look at the detection and recovery logic in `mlkem_fault_hooks.c`. On lines 623 and 624, the monitor evaluates the sum and difference invariants modulo 3329. If either check is non-zero, an error occurred. Notice lines 635 and 636: we immediately restore the original operands into the array from `u_saved` and `v_saved`. We recompute just that single butterfly, write the repaired values, and verify the retry. If the error was a transient SEU, it verifies cleanly and increments `recovered_count`. If it remains corrupted, it increments `persistent_count`, which escalates downstream."*
- **What the Audience Understands:** This is the exact mechanism that achieves 100% transient recovery without restarting decapsulation.

---

### Step 4: Show the Hardened Twiddle Binding in `tfib_ref.c` (~45 seconds)

- **File to Open in IDE:** [`tfib_implementation/tfib_ref.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_ref.c#L40-L70)
- **Function Name:** `tfib_ref_monitor_ntt_butterfly`
- **Line Range to Highlight:** Lines 40–70
- **Code to Point At:**
  ```c
  unsigned k = tfib_twiddle_idx_ntt(layer, b_idx);
  int16_t zeta_ref = tfib_zetas_ref[k];

  /* 1. Direct Twiddle Reference Check (Closes Theorem 1 Blind Spot) */
  bool twiddle_mismatch = (zeta_op != zeta_ref);

  /* 2. Recomputed Arithmetic Checks using Independent Reference */
  int16_t t_check = tfib_fqmul(v_saved, zeta_ref);
  int32_t diff_c = ((int32_t)(*r_j) - (int32_t)(*r_j_len) - 2 * (int32_t)t_check) % MLKEM_Q;
  int32_t sum_c  = ((int32_t)(*r_j) + (int32_t)(*r_j_len) - 2 * (int32_t)u_saved) % MLKEM_Q;
  ```
- **What to Say Verbally:**  
  *"Now I want to show how we closed the critical vulnerability of Twiddle Factor Blindness—Theorem 1. In our baseline monitor, if the twiddle table in memory was corrupted, the local monitor consumed the same corrupted twiddle, rendering the invariant blind. In our hardened v2 implementation, line 41 independently calculates the canonical twiddle index `k` from the loop indices, and line 42 fetches `zeta_ref` from an independent lookup table. Line 65 directly detects twiddle corruption, and line 98 uses `zeta_ref` to repair the butterfly in-place."*
- **What the Audience Understands:** The v2 implementation actively detects memory faults in constant tables that completely fool traditional invariant checks.

---

### Step 5: Run the Countermeasure Independence Test Suite (~60 seconds)

- **What to Run in Terminal:**
  ```bash
  ./tfib_experiments/test_step2c_countermeasure_independence
  ```
- **Execution Time:** ~0.2 seconds `[DIRECTLY OBSERVED]`
- **Expected Output:**
  ```text
  ================================================================================
  Phase 2 — Step 2C-A Validation Test Suite
  Subject: Countermeasure Independence, Checker Faults & Common-Mode Resilience
  ================================================================================
    [PASS] Test 1: TFIB-REF detects operational twiddle transient fault and achieves genuine recovery
    [PASS] Test 2: TFIB-REF detects operational twiddle persistent fault and forces safe fail-stop
    [PASS] Test 3: TFIB-REF checker-only transient fault triggers false-alarm retry and recovers
    [PASS] Test 4: TFIB-REF persistent checker corruption safely forces fail-stop (refuses untrusted checker)
    [PASS] Test 5: TFIB-META handles metadata tag faults (transient recovers, persistent fail-stops)
    [PASS] Test 6: Checker internal logic corruption (sum_c^=1) triggers retry/safe fail-stop without SDC
    [PASS] Test 7: Paired software mutations demonstrate local checker blindness; no SDC observed in this test
    [PASS] Test 8: Baseline monitor confirms Theorem 1 blind spot (0% det) with safe FO partitioning (0 SDC)
    [PASS] Test 9: Negative tests verify deliberate state corruption and invalid classifications are caught

  ================================================================================
  RESULTS: 9 passed, 0 failed
  ================================================================================
  ```
- **What to Say Verbally:**  
  *"To prove these countermeasures in action, I am running our countermeasure independence test suite. In less than one second, 9 automated test scenarios execute directly on compiled production objects. Notice Test 1: TFIB-REF catches operational twiddle transients and achieves 100% genuine recovery. Notice Test 4 and Test 6: when the checker logic itself is corrupted, the system safely forces fail-stop implicit rejection rather than trusting corrupted logic. And notice Test 8: the baseline monitor confirms Theorem 1's blind spot, while our outer Fujisaki-Okamoto check ensures zero SDC. All 9 tests pass cleanly."*
- **What the Audience Understands:** The system has been subjected to rigorous adversarial testing, including faults in the checkers themselves, with all tests passing.

---

### Backup Command: Run the 400-Trial Cleanroom Production Reproducer

If a professor asks: *"Can you show the 400 cleanroom trials on the production binary?"*
- **Run:**
  ```bash
  ./phase18_audit/production_reproducer
  ```
- **Execution Time:** ~1.2 seconds `[DIRECTLY OBSERVED]`
- **Output:**
  ```text
  Successfully executed 400 independent production trials and wrote phase18_audit/raw_production_trials.csv
  ```
- **Show Results via Python One-Liner:**
  ```bash
  python3 -c "
  import csv, collections
  with open('phase18_audit/raw_production_trials.csv') as f:
      print(collections.Counter((r['target'], r['outcome']) for r in csv.DictReader(f)))
  "
  ```
- **Output:**
  `Counter({('F12_CLEAN_BASELINE', 'CLEAN_SUCCESS'): 100, ('F4_TRANSIENT_RECOVERY', 'GENUINE_RECOVERY'): 100, ('F5A_RECURRING_BITFLIP', 'SAFE_FAIL_STOP'): 100, ('F5B_FORCE_VALUE_ZERO', 'SAFE_FAIL_STOP'): 100})`
- **Say:** *"Across 400 cleanroom trials, we observe 100% clean success, 100% transient recovery, 100% persistent fail-stop, and zero SDC."*

---

## Summary of Demonstration Files

| File | Exact Line Range | Core Purpose in Demo |
|---|:---:|---|
| [`poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c) | Lines 390–420 | Show operand snapshotting in CPU registers (`u_saved, v_saved`) |
| [`mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) | Lines 614–663 | Show difference invariant check and localized single-butterfly rollback |
| [`tfib_ref.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_ref.c) | Lines 40–70 | Show independent twiddle lookup and Theorem 1 twiddle cross-check |
| [`kem.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c) | Lines 484–520 | Show persistent fault quenching and deterministic FIPS 203 implicit rejection |

