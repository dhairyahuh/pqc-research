# Phase 2 — Step 2B Independent Verification & Audit Report

**Audit Target:** Key Generation and Deterministic Randomness Integration (`Phase 2 Step 2B`)  
**Repository:** `pqc-research`  
**Branch:** `space-resilience-framework`  
**Auditor:** Independent Cryptographic Software Verification Auditor  
**Date:** 2026-10-04  
**Audit Verdict:** **CONDITIONAL PASS** (No blocking architectural defects; four non-blocking test-harness/documentation limitations identified)

---

## 1. Executive Summary

This independent audit evaluated Phase 2 Step 2B, which aimed to:
1. Eliminate standard C `srand()` and `rand()` calls from the experimental harness.
2. Decouple keypair generation from in-tree production code (`mlkem768_keypair()`) by delegating to `independent_oracle_keypair_derand()` (`liboqs` v0.16.0).
3. Introduce deterministic pseudorandom seed derivation (`campaign_prf()`) based on FIPS 202 SHAKE-256.

### Summary of Audit Findings
- **Independence Established:** The runner binary no longer invokes `mlkem768_keypair()`, `mlkem768_enc()`, `rand()`, or `srand()`. Disassembly analysis confirms exactly **one** in-tree cryptographic call site: `_mlkem768_dec_monitored` (the decapsulation function under test).
- **Ground-Truth Correctness:** Keypair generation and encapsulation are handled entirely by `liboqs` (v0.16.0). Rejection key derivation is handled by the standalone TweetFIPS-202 implementation.
- **Reproducibility Verified:** Two separate full 900-trial executions produced bit-for-bit identical outputs matching `phase2_step2b_runner_output.csv`. SDC count is confirmed to be **0 / 900**.
- **Limitations & Deficiencies Identified:**
  - **DEF-01 (Assertion Weakness in Test D):** The clean round-trip pipeline test accepts canonical implicit rejection (`rej_match == true`) as non-SDC without asserting `ss_match == true`. On an unfaulted clean run, genuine decapsulation must succeed.
  - **DEF-02 (Test Isolation / Code Duplication):** `test_step2b_validation.c` re-implements `campaign_prf()` locally as a static copy rather than linking the runner's internal symbol.
  - **DEF-03 (Incomplete Test Parameter Variation):** Test B varies `trial`, `mode`, and `persistent`, but omits verifying that altering `locus` produces distinct PRF output. Test E checks `nm` for `_rand`/`_srand`, but omits checking for `mlkem768_keypair` calls in the C harness.
  - **DEF-04 (Terminology Overstatement):** The report is titled "Independent Key Generation and CSPRNG Integration Report" and repeatedly cites "CSPRNG", but the implementation is a **deterministic PRF / seed expansion function based on SHAKE-256 (FIPS 202 XOF)** without dynamic OS entropy or state-machine seeding.

---

## 2. Detailed Verification by Area

### 2.1 Randomness and PRF Correctness
The implementation in `tfib_experiments/tfib_experiment_runner.c` (lines 40–53) defines:
```c
static void campaign_prf(
    uint8_t *out, size_t outlen,
    int trial, tfib_mode_t mode, tfib_fault_locus_t locus, bool persistent
) {
    uint8_t seed_ctx[16];
    uint32_t vals[4] = {
        (uint32_t)(0x1337C0DE + trial * 31),
        (uint32_t)mode,
        (uint32_t)locus,
        persistent ? 1u : 0u
    };
    memcpy(seed_ctx, vals, sizeof(seed_ctx));
    fips202_ref_shake256(out, outlen, seed_ctx, sizeof(seed_ctx));
}
```
**Audit Analysis:**
- **Deterministic Reproducibility:** Because `vals` is explicitly populated and `fips202_ref_shake256` is a pure function, identical inputs always generate identical bytes.
- **Domain Separation:**
  - `trial` indices (0..49) are scaled by 31 and offset by `0x1337C0DE`.
  - `mode` distinguishes `TFIB_MODE_BASELINE (0)`, `TFIB_MODE_REF (1)`, and `TFIB_MODE_META (2)`.
  - `locus` distinguishes fault locations (0..5).
  - `persistent` distinguishes transient (0) vs persistent (1) faults.
  - Within each configuration in `main()`, all 18 test suites invoke unique `(mode, locus, persistent)` tuples.
- **Input Padding & Bounds:** `sizeof(vals) == 16` and `sizeof(seed_ctx) == 16`. All 16 bytes are initialized via `memcpy`.
- **Portability Note:** Host byte-order is copied directly. On ARM64 (macOS) and x86_64 systems, this produces little-endian byte ordering. On big-endian architectures, the bytes fed into SHAKE-256 would be reversed. For the target platform (Apple Silicon ARM64), behavior is strictly deterministic.
- **Terminology Assessment:** Describing this as a "CSPRNG" is inaccurate. It is a **deterministic seed derivation PRF / XOF expansion**. Because fault-injection research demands perfect reproducibility across re-runs of specific trials, a deterministic PRF is methodologically appropriate, but it should not be claimed as an interactive CSPRNG.

### 2.2 Independent Key Generation
In `run_suite()` (`tfib_experiment_runner.c`, lines 96–107):
```c
uint8_t prf_output[64 + 32];
campaign_prf(prf_output, sizeof(prf_output), t, mode, locus, persistent);

uint8_t *seed64 = prf_output;        /* d || z for KeyGen */
uint8_t *seed32 = prf_output + 64;   /* m for Encaps */

int kp_rc = independent_oracle_keypair_derand(pk, sk, seed64);
```
**Audit Analysis:**
- **Decoupling from In-Tree Keygen:** The call to `mlkem768_keypair()` has been completely removed from `run_suite()`.
- **Seed Mapping:** FIPS 203 Section 5.1 (`ML-KEM.KeyGen_internal`) requires 64 bytes of seed material representing $d \parallel z$. In `liboqs` v0.16.0, `OQS_KEM_ml_kem_768_keypair_derand` accepts exactly 64 bytes (`OQS_KEM_ml_kem_768_length_keypair_seed == 64`). The first 32 bytes provide $d$ (used to derive $\rho$ and $\sigma$ for matrix $\mathbf{A}$ and error vectors), while the remaining 32 bytes provide $z$ (the implicit rejection seed).
- **Oracle Provenance & Isolation:** `liboqs` is dynamically linked from `/opt/homebrew/opt/liboqs/lib/liboqs.0.16.0.dylib`. It does not link to, share globals with, or reuse object code from `bin/obj/mlkem768_inst.o`.
- **Compatibility:** Keys generated by `independent_oracle_keypair_derand` are accepted by `mlkem768_dec_monitored` and achieve 100% successful decapsulation across all clean control trials.

### 2.3 Build and Symbol Verification
Rebuilding from clean source and inspecting binary symbols yielded:
1. **Dynamic Symbols (`nm -u`):** Only `_OQS_KEM_ml_kem_768_*`, `_OQS_init`, and standard libc symbols are imported.
2. **Standard C PRNG Symbols:**
   - `nm tfib_experiment_runner | grep ' U _srand'` -> **0 matches (removed)**
   - `nm tfib_experiment_runner | grep ' U _rand$'` -> **0 matches (removed)**
3. **In-Tree Keypair Symbols:**
   - `_mlkem768_keypair` is present in the object file `bin/obj/mlkem768_inst.o` because that file aggregates all ML-KEM routines.
   - However, disassembly (`otool -tV`) of `tfib_experiment_runner` reveals **0 call-site branches (`bl`) to `_mlkem768_keypair` or `_mlkem768_keypair_derand`**.
4. **Active Production Call Sites:** Disassembly confirms that `_mlkem768_dec_monitored` is the sole in-tree cryptographic routine invoked by the runner.
5. **Residual `randombytes()` Status:** Instrumented execution (`test_randombytes_call_count.c`) confirmed `g_randombytes_call_count == 0`. `randombytes()` is dead code satisfying static link resolution for `mlkem768_inst.o`.

### 2.4 Test Quality & Controlled Mutation Analysis
Inspection of `tfib_experiments/test_step2b_validation.c` and controlled mutation testing revealed:

| Test ID | Declared Purpose | What It Actually Proves | Defect / Limitation |
|---|---|---|---|
| **Test A** | PRF determinism | Proves local copy of `campaign_prf` returns identical bytes for duplicate inputs | Tests static duplicate, not runner binary |
| **Test B** | Domain separation | Proves output varies when `trial`, `mode`, or `persistent` changes | Omits testing `locus` parameter variation |
| **Test C** | Oracle keypair validity | Proves `liboqs` returns 0 and non-zero key buffers for 64-byte PRF seed | Superficial check (no full math verification) |
| **Test D** | Full pipeline zero SDC | Proves oracle keygen + oracle encaps + in-tree decaps agree on clean runs | **DEF-01: Accepts `rej_match` as success without asserting `ss_match`** |
| **Test E** | Symbol check | Proves `_srand` and `_rand` are not undefined symbols in runner | Checks symbols via `system()`, omits `mlkem768_keypair` |
| **Test F** | PRF output quality | Proves output has $\ge 16$ distinct byte values in 96 bytes | Basic sanity check only |

**Controlled Mutation Results:**
- **Mutation 2 (Tampered Ciphertext):** Altered ciphertext byte `ct[50] ^= 0x55` in the pipeline -> Decapsulation correctly rejected and failed `ss_expected` match -> **Mutation caught (exit code 1)**.
- **Mutation 3 (Tampered Expected Secret):** Altered expected shared secret byte `ss_expected[0] ^= 0x01` -> SDC detected -> **Mutation caught (exit code 1)**.
- **Mutation 4 (Symbol Scanner):** Tested scanner against object with target symbol -> **Target caught (exit code 1)**.

### 2.5 Campaign Reproducibility & Comparability
Two independent executions of the 900-trial campaign were performed:
- `diff -u run1.csv run2.csv` -> **0 differences (Byte-identical)**.
- `diff -u phase2_step2b_runner_output.csv run1.csv` -> **0 differences (Byte-identical)**.

**Detailed Outcome Breakdown (900 Trials):**
- **Clean Controls (150 trials):** 150 `CLEAN_SUCCESS` (100.0%)
- **BASELINE Monitor (150 trials):**
  - Op Twiddle Transient (50 trials): 0 local detections (0.0%), 48 blind FO catches, 2 ineffective valid faults, 0 SDC.
  - Op Twiddle Persistent (50 trials): 0 local detections (0.0%), 50 blind FO catches, 0 SDC.
- **TFIB-REF Strategy (400 trials):**
  - Op Twiddle Transient (50 trials): 50 local detections (100.0%), 50 genuine recoveries (100.0%), 0 SDC.
  - Op Twiddle Persistent (50 trials): 50 local detections (100.0%), 50 safe fail-stops (100.0%), 0 SDC.
  - Ref Twiddle Transient (50 trials): 50 local detections (100.0%), 50 genuine recoveries (100.0%), 0 SDC.
  - Ref Twiddle Persistent (50 trials): 50 local detections (100.0%), 50 safe fail-stops (100.0%), 0 SDC.
  - Simultaneous Common-Mode (50 trials): 0 local detections (0.0%), 49 blind FO catches, 1 ineffective valid fault, 0 SDC.
  - Checker Logic Transient (50 trials): 50 local detections (100.0%), 50 genuine recoveries (100.0%), 0 SDC.
  - Checker Logic Persistent (50 trials): 50 local detections (100.0%), 50 safe fail-stops (100.0%), 0 SDC.
- **TFIB-META Strategy (350 trials):**
  - Op Twiddle Transient (50 trials): 50 local detections (100.0%), 50 safe fail-stops (100.0%), 0 SDC.
  - Op Twiddle Persistent (50 trials): 50 local detections (100.0%), 50 safe fail-stops (100.0%), 0 SDC.
  - Meta Tag Transient (50 trials): 50 local detections (100.0%), 50 genuine recoveries (100.0%), 0 SDC.
  - Meta Tag Persistent (50 trials): 50 local detections (100.0%), 50 safe fail-stops (100.0%), 0 SDC.
  - Checker Logic Transient (50 trials): 50 local detections (100.0%), 50 genuine recoveries (100.0%), 0 SDC.
  - Checker Logic Persistent (50 trials): 50 local detections (100.0%), 50 safe fail-stops (100.0%), 0 SDC.

**Denominator Analysis:**
- Clean trials: 150
- Faults armed and triggered: 750 / 750 (100.0%)
- Correct outputs (Authentic Key Agreement): 403 / 900 (44.78%)
- Implicit Rejections (Safe Fail-Stop or FO Rejection): 497 / 900 (55.22%)
- Silent Data Corruption: **0 / 900 (0.0%, 95% Clopper-Pearson CI: [0.00%, 0.41%])**

---

## 3. Confirmed Defects and Limitations Table

| Defect ID | Severity | File & Line Reference | Nature of Defect | Impact | Concrete Remediation |
|---|:---:|---|---|---|---|
| **DEF-01** | **Medium** | `test_step2b_validation.c`:152–156 | Assertion Weakness: Test D increments `sdc_count` only if `!ss_match && !rej_match` | If clean decapsulation erroneously fails and returns `ss_rej`, Test D would silently pass | Modify Test D assertion to require `ss_match == true` on unfaulted pipeline trials |
| **DEF-02** | **Low** | `test_step2b_validation.c`:40–53 | Test Harness Code Duplication: `campaign_prf()` is copied as a static function in test file | Test validates the copy, not the runner's internal symbol | Export `campaign_prf` in an internal header or link shared module |
| **DEF-03** | **Low** | `test_step2b_validation.c`:77–95, 165–175 | Incomplete Test Coverage: Test B omits `locus` variation; Test E omits checking `mlkem768_keypair` calls | Incomplete automated regression coverage in C test binary | Add `locus` variation check to Test B; add `mlkem768_keypair` call-site check to Test E |
| **DEF-04** | **Low** | `phase2_step2b_keygen_csprng_report.md`:1, 14, 21 | Terminology Overstatement: Document claims "CSPRNG Integration" when it is a deterministic PRF | Ambiguous/misleading cryptographic characterization in publication claims | Retitle and describe strictly as "Deterministic SHAKE-256 PRF / Seed Expansion" |
| **DEF-05** | **Info** | `tfib_experiment_runner.c`:45–51 | Architecture Dependence: Host endianness is copied directly into `seed_ctx` via `memcpy` | PRF outputs would differ if run on big-endian hardware | Normalize endianness using `htole32` if cross-architecture reproducibility is required |

---

## 4. Final Verdict and Conditions

### Verdict: **CONDITIONAL PASS**

The core technical objectives of Phase 2 Step 2B are **satisfied**:
1. Standard C `rand()` and `srand()` have been eliminated from the experimental runner.
2. Production in-tree keypair generation (`mlkem768_keypair()`) has been completely decoupled from the ground-truth generation path and has 0 call sites.
3. The independent reference oracle (`liboqs` v0.16.0) establishes all ground-truth keys and ciphertexts.
4. The 900-trial campaign is 100% deterministic and reproducible, exhibiting zero Silent Data Corruption across all configurations.

### Conditions for Proceeding to Step 2C:
1. **Acknowledge DEF-01 in Test D:** In any future test harness updates, clean roundtrip tests must explicitly assert `ss_match == true` rather than accepting `rej_match`.
2. **Correct Documentation Terminology (DEF-04):** The manuscript and technical reports must not claim integration of an OS CSPRNG; they must accurately document the mechanism as a **deterministic SHAKE-256 PRF (XOF seed expansion)**.
3. **Do not modify production code:** Step 2C must focus strictly on countermeasure decoupling and relocation of twiddle factor tables without altering arithmetic or monitor logic.

The auditor confirms Phase 2 Step 2B is verified and ready for review.
