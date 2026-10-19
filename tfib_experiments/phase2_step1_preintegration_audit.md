# Phase 2 — Step 1: Pre-Integration Repository Audit

**Document Date:** October 3, 2026  
**Auditor:** Skeptical Cryptographic Software Verification Engineer  
**Target:** Existing Fault-Campaign Runner Pre-Integration Baseline  
**Scope:** Phase 2, Step 1 Initial Audit (Read-Only Inspection)

---

## 1. Git Repository State

- **Active Branch:** `space-resilience-framework`
- **Head Commit Hash:** `55dd937cbad66b24e5c2c0b89b78fa776801913c`
- **Working Tree Status:** Clean with respect to production code. Uncommitted changes are limited to historical documentation updates and experiment scripts from earlier project phases.
- **Untracked Directories:** `chatgpt/`, `tfib_experiments/`, `adversarial_audit/`, `paper/`, etc.

---

## 2. Identification of Existing Fault-Campaign Runners

Two active fault-campaign runners exist in `tfib_experiments/`:

1. **`tfib_experiments/tfib_experiment_runner.c` (Primary Targeted Campaign Runner):**
   - **File Size / Lines:** 15,765 bytes / 300 lines.
   - **Target Binary:** `tfib_experiments/tfib_experiment_runner`
   - **Output File:** `tfib_raw_results.csv` (16 columns, 900 trials across 18 test suites).
   - **Structure:** Hardcoded execution blocks across three configurations:
     - `BASELINE` (3 suites: `CLEAN_CONTROL`, `OP_TWIDDLE_TRANSIENT`, `OP_TWIDDLE_PERSISTENT`)
     - `TFIB_REF` (8 suites: `CLEAN_CONTROL`, `OP_TWIDDLE_TRANSIENT`, `OP_TWIDDLE_PERSISTENT`, `REF_TWIDDLE_TRANSIENT`, `REF_TWIDDLE_PERSISTENT`, `SIMULTANEOUS_COMMON_MODE`, `CHECKER_LOGIC_TRANSIENT`, `CHECKER_LOGIC_PERSISTENT`)
     - `TFIB_META` (7 suites: `CLEAN_CONTROL`, `OP_TWIDDLE_TRANSIENT`, `OP_TWIDDLE_PERSISTENT`, `META_TAG_TRANSIENT`, `META_TAG_PERSISTENT`, `CHECKER_LOGIC_TRANSIENT`, `CHECKER_LOGIC_PERSISTENT`)
   - **Compilation Command:**
     ```bash
     clang -O3 -Ialgorithms/source_ref/mlkem/include -Itfib_implementation \
       tfib_experiments/tfib_experiment_runner.c bin/obj/mlkem768_inst.o \
       tfib_implementation/libtfib.a -o tfib_experiments/tfib_experiment_runner
     ```

2. **`tfib_experiments/tfib_validity_audit_runner.c` (Parameterized Audit Reproducer):**
   - **File Size / Lines:** 9,782 bytes / 235 lines.
   - **Target Binary:** `tfib_experiments/tfib_validity_audit_runner`
   - **Output Files:** `tfib_trial_level_results.csv` (raw trials) and `tfib_reproduced_results.csv` (aggregated statistics).
   - **Structure:** Table-driven array of `audit_suite_config_t suites[18]`.

Both runners share identical trial setup, expected-value derivation, injection, and outcome classification logic. `tfib_experiment_runner.c` represents the authoritative primary campaign runner.

---

## 3. Existing Expected-Output and Classification Logic

### 3.1 Trace of Expected-Value Derivation
In `tfib_experiments/tfib_experiment_runner.c`:
- **PRNG Setup:**
  ```c
  int randombytes(uint8_t *out, size_t outlen) {
      for (size_t i = 0; i < outlen; i++) out[i] = (uint8_t)(rand() & 0xFF);
      return 0;
  }
  ```
- **Trial Generation (lines 63–66):**
  ```c
  srand(0x1337C0DE + t * 31 + (int)mode * 1000 + (int)locus * 100 + (persistent ? 777 : 0));
  mlkem768_keypair(pk, sk);
  mlkem768_enc(ct, ss_expected, pk);
  compute_expected_rejection_key(ss_rej_expected, sk, ct);
  ```
- **Rejection Key Helper (lines 27–32):**
  ```c
  static void compute_expected_rejection_key(uint8_t ss_rej[SS_BYTES], const uint8_t sk[SK_BYTES], const uint8_t ct[CT_BYTES]) {
      uint8_t z_ct[SS_BYTES + CT_BYTES];
      memcpy(z_ct, sk + SK_BYTES - SS_BYTES, SS_BYTES);
      memcpy(z_ct + SS_BYTES, ct, CT_BYTES);
      mlkem768_shake256(ss_rej, SS_BYTES, z_ct, SS_BYTES + CT_BYTES);
  }
  ```
- **Circularity Finding:**
  - `mlkem768_enc` is linked from `bin/obj/mlkem768_inst.o` (the Device Under Test).
  - `mlkem768_shake256` is also linked from `bin/obj/mlkem768_inst.o`.
  - The expected valid shared secret (`ss_expected`) and expected rejection secret (`ss_rej_expected`) are completely self-referential.

### 3.2 Production Decapsulation Call
- **Invocation (lines 76–78):**
  ```c
  uint32_t status = 0;
  int rc = mlkem768_dec_monitored(ss_out, ct, sk, &status);
  (void)rc;
  ```
- The return code `rc` is ignored. Status values observed:
  - `0x5A5A5A5A`: Success / Decapsulated cleanly (or recovered).
  - `0xA5A5A5A5`: Implicit rejection triggered.
  - `0xFFFFFFFF`: Unrecoverable fault / abort flag.

### 3.3 Existing Classification Tree
- **Classification Variables (lines 80–86):**
  - `fault_act = (g_tfib_fault.trigger_count > 0)`
  - `mon_det = (tfib_get_total_mismatches() > 0)`
  - `rec_att = mon_det`
  - `rec_succ = (tfib_get_total_recoveries() > 0)`
  - `ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0)`
  - `rej_match = (memcmp(ss_out, ss_rej_expected, SS_BYTES) == 0)`
  - `sdc = (!ss_match && !rej_match)`

- **Outcome Categories (lines 89–111):**
  1. `CLEAN_SUCCESS`: `!fault_act && locus == TFIB_FAULT_NONE`
  2. `GENUINE_RECOVERY`: `ss_match && status == 0x5A5A5A5A && rec_succ`
  3. `INEFFECTIVE_FAULT_VALID`: `!mon_det && fault_act && ss_match && status == 0x5A5A5A5A`
  4. `LOCAL_BLIND_FO_CONTAINED`: `rej_match && (status == 0xFFFFFFFF || status == 0xA5A5A5A5) && !mon_det`
  5. `SAFE_FAIL_STOP`: `rej_match && (status == 0xFFFFFFFF || status == 0xA5A5A5A5) && mon_det`
  6. `SILENT_DATA_CORRUPTION`: `sdc` (neither valid match nor rejection match)
  7. `INCONCLUSIVE`: Fall-through condition

---

## 4. Runner Coupling to TFIB State

The existing runner directly interacts with the following TFIB state variables and functions declared in `tfib_common.h` and `tfib_core.h`:
1. `tfib_set_mode(mode)`: Sets active monitoring strategy (`TFIB_MODE_BASELINE`, `TFIB_MODE_REF`, `TFIB_MODE_META`).
2. `tfib_fault_reset()`: Clears active fault parameters and trigger count.
3. `tfib_reset_all_stats()`: Resets monitor mismatch and recovery counters.
4. `tfib_fault_arm(locus, stage, b_idx, bit, persistent)`: Arms a targeted single-event fault.
5. `g_tfib_fault.trigger_count`: Directly reads global fault trigger count.
6. `tfib_get_total_mismatches()`: Reads monitor detection counter.
7. `tfib_get_total_recoveries()`: Reads successful recovery counter.

---

## 5. Independent Oracle Public API & Assets

Located in `tfib_experiments/phase11_oracle/`:
- **Static Library:** `tfib_experiments/phase11_oracle/libindependent_oracle.a`
- **Header:** `tfib_experiments/phase11_oracle/independent_oracle.h`
- **Exported Public Functions:**
  - `int independent_oracle_init(void)`: Initializes `liboqs` backend.
  - `const char *independent_oracle_get_version(void)`: Returns oracle provenance string.
  - `int independent_oracle_keypair_derand(uint8_t *pk, uint8_t *sk, const uint8_t *seed64)`
  - `int independent_oracle_encaps_derand(uint8_t *ct, uint8_t *ss, const uint8_t *pk, const uint8_t *seed32)`
  - `int independent_oracle_decaps(uint8_t *ss, const uint8_t *ct, const uint8_t *sk)`: Isolated `liboqs 0.16.0` decapsulation.
  - `int independent_oracle_compute_rejection(uint8_t *ss_rej, const uint8_t *sk, const uint8_t *ct)`: Independent FIPS 202 SHAKE-256 canonical implicit rejection.
- **Link Dependencies:** `-L/opt/homebrew/opt/liboqs/lib -loqs`

---

## 6. Inventory of Historical Experimental Data Files

The following files represent historical baseline data that **MUST NOT BE OVERWRITTEN OR DELETED**:
- `tfib_raw_results.csv` (139 KB, 901 lines)
- `tfib_trial_level_results.csv` (80 KB, 901 lines)
- `tfib_reproduced_results.csv` (1.4 KB, 19 lines)
- `tfib_benchmark_raw.csv` (1.38 MB, 30,001 lines)
- `tfib_experiments/tfib_benchmark_results.csv`
- All files in `chatgpt/`

---

## 7. Integration Plan for Step 1

To preserve historical CSV files and maintain strict backward compatibility while integrating the independent oracle:
1. Update runner compilation flags to include `-Itfib_experiments/phase11_oracle` and link `tfib_experiments/phase11_oracle/libindependent_oracle.a -L/opt/homebrew/opt/liboqs/lib -loqs`.
2. Replace in-tree `compute_expected_rejection_key` with `independent_oracle_compute_rejection`.
3. In each trial, independently verify the expected valid shared secret using `independent_oracle_decaps(ss_oracle_valid, ct, sk)` to eliminate reliance on DUT `mlkem768_enc` / `mlkem768_inst.o`.
4. Add explicit error handling: if the independent oracle fails (`rc != 0`), record an explicit validation error rather than misclassifying the trial.
5. Ensure distinct output buffers for oracle calculations and production decapsulation to prevent memory aliasing.
6. Verify integration using dedicated integration test programs without modifying existing fault parameters or overwriting historical results.
