# Phase 2 — Step 2B Remediation: Test Execution Results

**Date:** 2026-10-04  
**Host Architecture:** Apple Silicon ARM64 (Apple M3 Pro), macOS Darwin 25.1.0, Apple Clang 17.0.0  
**liboqs Version:** 0.16.0 (`/opt/homebrew/opt/liboqs/lib/liboqs.0.16.0.dylib`)  
**Active Branch:** `space-resilience-framework`  

---

## 1. Summary of Executed Commands and Exit Codes

| Step ID | Command / Target | Description | Exit Code | Verdict |
|---|---|---|:---:|:---:|
| **REM-01** | `test_independent_oracle` | Unit tests and FIPS 203 KAT verification for independent oracle | `0` | **PASS** |
| **REM-02** | `test_step2b_validation` | Remediated Step 2B validation suite (7 tests) | `0` | **PASS** |
| **REM-03** | `run_step2b_mutation_checks.sh` | 4 controlled mutation tests (deliberate corruptions) | `0` (all 4 caught with exit 1) | **PASS** |
| **REM-04** | `tfib_experiment_runner` | Full 900-trial campaign with remediated shared PRF header | `0` | **PASS** |
| **REM-05** | `diff -u phase2_step2b_runner_output.csv ...` | Bit-for-bit campaign comparison against baseline | `0` (0 diffs) | **PASS** |

---

## 2. Validation Test Suite Breakdown (`test_step2b_validation`)

Command: `./tfib_experiments/test_step2b_validation` (Exit Code: `0`)

```
================================================================================
Phase 2 — Step 2B Remediation Validation Test Suite
Subject: Deterministic SHAKE-256 PRF + Independent Keypair Generation
================================================================================
  [PASS] Test A: SHAKE-256 PRF determinism (same inputs → identical output)
  [PASS] Test B: PRF domain separation (trial, mode, all 6 loci, persistence all distinct)
  [PASS] Test C: Oracle keypair_derand produces valid non-trivial keys
  [PASS] Test D: Clean valid-path decapsulation matches oracle valid secret and differs from rejection key
  [PASS] Test E: Runner binary has no undefined srand/rand and 0 mlkem768_keypair call sites
  [PASS] Test F: PRF output is non-zero with reasonable byte diversity (>=16 distinct)
  [PASS] Test G: Explicit Little-Endian Serialization & SHAKE-256 KAT (Cases 1 & 2)

================================================================================
RESULTS: 7 passed, 0 failed
================================================================================
```

---

## 3. Controlled Mutation Results (`run_step2b_mutation_checks.sh`)

Command: `./tfib_experiments/run_step2b_mutation_checks.sh` (Exit Code: `0`)

Each mutation was compiled in an isolated temporary directory and executed against the test harness:

| Mutation | Description | Target Finding | Expected Failure | Actual Exit Code | Result |
|---|---|---|---|:---:|:---:|
| **MUT-1** | Injected 1-byte corruption into expected valid secret: `ss_expected[0] ^= 0xFF` | DEF-01 | Test D FAIL | `1` | **Caught** |
| **MUT-2** | Forced clean decapsulation output to match rejection key: `ss_out = ss_rej` | DEF-01 | Test D FAIL | `1` | **Caught** |
| **MUT-3** | Removed locus input differentiation from `campaign_prf`: forced `locus = 0` | DEF-03 | Test B FAIL | `1` | **Caught** |
| **MUT-4** | Inverted 32-bit serialization byte order from little-endian to big-endian | DEF-05 | Test G FAIL | `1` | **Caught** |

All 4 mutations were successfully caught by the test assertions and produced non-zero exit codes.

---

## 4. Full Campaign Execution & Invariant Verification

Command: `./tfib_experiments/tfib_experiment_runner tfib_experiments/phase2_step2b_final_output.csv` (Exit Code: `0`)  
Comparison: `diff -u tfib_experiments/phase2_step2b_runner_output.csv tfib_experiments/phase2_step2b_final_output.csv` (Exit Code: `0`)

- **Total Trials:** 900
- **Clean Controls:** 150 / 150 `CLEAN_SUCCESS`
- **Faults Triggered:** 750 / 750 (100.0%)
- **Monitor Detections:** 600 / 750 (80.0%)
- **Genuine Recoveries:** 250 / 750 (33.3%)
- **Implicit Rejections (Safe Fail-Stop / FO Containment):** 497 / 900 (55.2%)
- **Silent Data Corruption (SDC):** **0 / 900 (0.0%)**
- **CSV Determinism:** Exactly 901 lines, 0 diffs against historical baseline.
