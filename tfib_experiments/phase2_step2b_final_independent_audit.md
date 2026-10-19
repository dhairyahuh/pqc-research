# Final Independent Audit: Phase 2 Step 2B Remediation & Closure

**Audit Target:** Remediation of Phase 2 Step 2B (Key Generation and Deterministic Randomness)  
**Repository:** `pqc-research`  
**Branch:** `space-resilience-framework`  
**Audited Commit Revision:** `55dd937cbad66b24e5c2c0b89b78fa776801913c`  
**Auditor Role:** Independent Skeptical Cryptographic Software Verification Auditor  
**Host Architecture:** Apple Silicon ARM64 (Apple M3 Pro), macOS Darwin 25.1.0, Apple Clang 17.0.0  
**External Reference Libraries:**
- `liboqs` v0.16.0 (`/opt/homebrew/opt/liboqs/lib/liboqs.0.16.0.dylib`)
- OpenSSL 4.0.2 (`/opt/homebrew/opt/openssl@4/bin/openssl`)
- Python 3 `hashlib` (OpenSSL 3.x backend)
**Audit Date:** 2026-10-04  
**Final Audit Verdict:** **PASS** (All 5 remediation findings verified; zero blocking defects remain; Step 2B is closed)

---

## 1. Executive Summary & Audit Baseline

This final independent audit evaluated the implementation changes made to remediate findings DEF-01 through DEF-05 identified during the initial Phase 2 Step 2B audit. The scope was strictly confined to deterministic PRF seed expansion, independent key generation, test harness assertion hardening, explicit serialization, and terminology correction.

### Audit Summary
1. **Actual Implementation Inspected:** The working tree was inspected without modification. Code changes were verified across `campaign_prf.h`, `tfib_experiment_runner.c`, `test_step2b_validation.c`, `run_step2b_tests.sh`, and `run_step2b_mutation_checks.sh`.
2. **Defect Resolutions Verified:**
   - **DEF-01 (Clean-path assertion):** Real production decapsulation is invoked; assertions strictly enforce `ss_match == true`, `rej_match == false`, and `ss_expected != ss_rej`.
   - **DEF-02 (Shared PRF):** Both the production runner and validation suite link the shared header `campaign_prf.h`. All duplicated local PRF logic was eliminated.
   - **DEF-03 (PRF domain differentiation):** All six fault loci (`NONE`, `OP_TWIDDLE`, `REF_TWIDDLE`, `SIMULTANEOUS`, `CHECKER_LOGIC`, `META_TAG`) are pairwise distinct across all 15 pairings. Trial, mode, and persistence variations were verified.
   - **DEF-04 (Terminology):** Overstated "CSPRNG" claims were replaced with "deterministic SHAKE-256 PRF-based seed expansion".
   - **DEF-05 (Explicit serialization):** Replaced host-endian `memcpy` with explicit little-endian `campaign_store32_le()`. SHAKE-256 KAT values were independently grounded and verified via external OpenSSL 4.0.2 and Python `hashlib`.
3. **Controlled Mutation Testing:** Four distinct mutations (valid secret corruption, rejection key substitution, locus differentiation removal, and serialization endianness inversion) were executed against the actual test harness. All four failed with non-zero exit code `1`.
4. **Campaign Reproducibility:** The 900-trial campaign reproduced bit-for-bit with zero differences against historical baseline `phase2_step2b_runner_output.csv`. Zero Silent Data Corruption (SDC) was observed ($0 / 900$, 95% Clopper-Pearson CI: $[0.00\%, 0.41\%]$).

---

## 2. Verification of Specific Findings

### 2.1 DEF-01: Clean-Path Assertion
**Source Location:** `tfib_experiments/test_step2b_validation.c` (lines 143–194)

The clean valid-path test (`test_d_clean_path_pipeline`) was inspected:
```c
/* Independent oracle keypair generation */
int kp_rc = independent_oracle_keypair_derand(pk, sk, prf_out);
assert(kp_rc == 0);

/* Independent oracle encapsulation */
int enc_rc = independent_oracle_encaps_derand(ct, ss_expected, pk, prf_out + 64);
assert(enc_rc == 0);

/* Independent oracle canonical implicit rejection calculation */
int rej_rc = independent_oracle_compute_rejection(ss_rej, sk, ct);
assert(rej_rc == 0);

/* Production decapsulation under test (clean control, no fault) */
tfib_set_mode(TFIB_MODE_BASELINE);
tfib_fault_reset();
tfib_reset_all_stats();

uint32_t status = 0;
mlkem768_dec_monitored(ss_out, ct, sk, &status);

bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
bool rej_match = (memcmp(ss_out, ss_rej, SS_BYTES) == 0);
bool keys_distinct = (memcmp(ss_expected, ss_rej, SS_BYTES) != 0);

if (!ss_match || rej_match || !keys_distinct) {
    clean_failures++;
}
```
**Auditor Analysis:**
1. **Real Decapsulation Invoked:** The test invokes `_mlkem768_dec_monitored` from `bin/obj/mlkem768_inst.o`, the actual production decapsulation implementation under test.
2. **Independent Ground Truth:** The expected shared secret `ss_expected` is established by `liboqs` v0.16.0 (`independent_oracle_encaps_derand`). The expected rejection key `ss_rej` is established via independent FIPS 202 reference code (`independent_oracle_compute_rejection`).
3. **Simulation vs Production Alignment:** The previous defect allowed `rej_match == true` to pass as non-SDC. Under the remediated code, if decapsulation fails on a valid ciphertext and returns `ss_rej`, `rej_match` evaluates to true, triggering `clean_failures++` and reporting test failure.

---

### 2.2 DEF-02: Shared PRF Implementation
**Source Locations:**
- Header: `tfib_experiments/campaign_prf.h` (lines 1–72)
- Runner Inclusion: `tfib_experiments/tfib_experiment_runner.c` (line 12)
- Test Suite Inclusion: `tfib_experiments/test_step2b_validation.c` (line 28)

**Auditor Analysis:**
1. The static local copy of `campaign_prf()` previously duplicated in `test_step2b_validation.c` has been completely deleted.
2. Both `tfib_experiment_runner.c` and `test_step2b_validation.c` include `campaign_prf.h`.
3. Disassembly of `tfib_experiment_runner` confirms inline expansion of `campaign_store32_le` and call to `_fips202_ref_shake256` at address `0x1000013e0`.
4. There is no hidden duplicate serialization or derivation logic in either file.

---

### 2.3 DEF-03: PRF Domain Differentiation
**Source Location:** `tfib_experiments/test_step2b_validation.c` (lines 66–122)

The PRF context layout is defined in `campaign_prf.h`:
```c
static inline void campaign_prf_serialize_context(
    uint8_t seed_ctx[CAMPAIGN_PRF_SEED_BYTES],
    int trial, tfib_mode_t mode, tfib_fault_locus_t locus, bool persistent
) {
    uint32_t trial_word = (uint32_t)(CAMPAIGN_SEED_BASE_MAGIC + (uint32_t)trial * 31u);
    campaign_store32_le(seed_ctx + 0, trial_word);
    campaign_store32_le(seed_ctx + 4, (uint32_t)mode);
    campaign_store32_le(seed_ctx + 8, (uint32_t)locus);
    campaign_store32_le(seed_ctx + 12, persistent ? 1u : 0u);
}
```
**Auditor Analysis:**
1. **Locus Representation:** Loci are represented as 32-bit unsigned integers:
   `TFIB_FAULT_NONE` (0), `TFIB_FAULT_OP_TWIDDLE` (1), `TFIB_FAULT_REF_TWIDDLE` (2), `TFIB_FAULT_SIMULTANEOUS` (3), `TFIB_FAULT_CHECKER_LOGIC` (4), `TFIB_FAULT_META_TAG` (5).
2. **Pairwise Distinction:** Test B computes outputs for all six loci under fixed parameters `(trial=0, mode=REF, persistent=false)` and verifies that all $\binom{6}{2} = 15$ pairs are distinct (`diff_locus == true`).
3. **Collision Resistance within Domain:**
   - Trial word: `0x1337C0DE + trial * 31`. For $t \in [0, 49]$, $trial\_word \in [0x1337C0DE, 0x1337C6CD]$, with minimum step 31.
   - Mode word: $0, 1, 2$.
   - Locus word: $0, 1, 2, 3, 4, 5$.
   - Persistence word: $0, 1$.
   No overlapping inputs exist within the campaign domain.

---

### 2.4 DEF-04: Terminology and Cryptographic Characterization
**Audited Artifacts:**
- `tfib_experiments/campaign_prf.h` (comments at lines 49–54)
- `tfib_experiments/tfib_experiment_runner.c` (comments at lines 62–63)
- `tfib_experiments/test_step2b_validation.c` (header and test logs)
- `tfib_experiments/run_step2b_tests.sh` (title and comments)
- `tfib_experiments/phase2_step2b_keygen_csprng_report.md` (re-titled and updated)

**Auditor Analysis:**
1. Claims of "CSPRNG Integration" have been purged from source comments, test outputs, and technical documentation.
2. The mechanism is consistently and precisely characterized as:
   **"Deterministic SHAKE-256 PRF-based Seed Expansion"**.
3. Documentation explicitly clarifies that no hardware entropy or dynamic OS CSPRNG state is used, justifying this design decision by the necessity of repeatable fault-injection trials.

---

### 2.5 DEF-05: Explicit Serialization & Grounded KAT
**Source Locations:**
- Serialization: `tfib_experiments/campaign_prf.h` (lines 21–46)
- KAT Verification: `tfib_experiments/test_step2b_validation.c` (lines 231–280)

**Independent External Calculation:**
To confirm that expected KAT constants are not circular, the auditor independently calculated the expected bytes using OpenSSL 4.0.2 and Python 3.12 `hashlib.shake_256`:

#### Context 1: `trial=0, mode=BASELINE (0), locus=NONE (0), persistent=false (0)`
- Expected LE 16-byte Context:
  `[0xDE, 0xC0, 0x37, 0x13, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]`
- OpenSSL 4.0.2 CLI command:
  ```bash
  python3 -c "import sys; sys.stdout.buffer.write(bytes.fromhex('dec03713000000000000000000000000'))" \
    | /opt/homebrew/opt/openssl@4/bin/openssl dgst -shake256 -xoflen 32
  ```
- Output: `0411ef6015d2306932f336f82f05ebe9b7f0973cc3bbe3114808626e38721e77` (Matches Test G `expected_hash1` exactly).

#### Context 2: `trial=42, mode=REF (1), locus=OP_TWIDDLE (1), persistent=true (1)`
- `trial_word = 0x1337C0DE + 42 * 31 = 0x1337C5F4`
- Expected LE 16-byte Context:
  `[0xF4, 0xC5, 0x37, 0x13, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00]`
- OpenSSL 4.0.2 CLI command:
  ```bash
  python3 -c "import sys; sys.stdout.buffer.write(bytes.fromhex('f4c53713010000000100000001000000'))" \
    | /opt/homebrew/opt/openssl@4/bin/openssl dgst -shake256 -xoflen 32
  ```
- Output: `53d6c8237067695242c5f6a04558a8a28e5b1e5444991bb437a75573819f7bc2` (Matches Test G `expected_hash2` exactly).

**Auditor Analysis:**
The serialization is explicitly little-endian, architecture-neutral, and independently validated against NIST-compliant FIPS 202 implementations outside the project codebase.

---

## 3. Mutation Testing Audit

The mutation runner `tfib_experiments/run_step2b_mutation_checks.sh` was audited line-by-line:

```bash
./tfib_experiments/run_step2b_mutation_checks.sh
```

| Mutation ID | Target Code | Injected Fault | Expected Behavior | Observed Result | Exit Code | Verdict |
|---|---|---|---|---|:---:|:---:|
| **MUT-1** | `test_step2b_validation.c` | `ss_expected[0] ^= 0xFF` in `test_d` | Test D reports FAIL | Mismatch detected on valid key | `1` | **PASS** |
| **MUT-2** | `test_step2b_validation.c` | `memcpy(ss_out, ss_rej, SS_BYTES)` in `test_d` | Test D reports FAIL | Rejection match rejected on clean run | `1` | **PASS** |
| **MUT-3** | `campaign_prf.h` | `campaign_store32_le(seed_ctx + 8, 0u)` | Test B reports FAIL | Loci pair collision detected | `1` | **PASS** |
| **MUT-4** | `campaign_prf.h` | Inverted word order to big-endian | Test G reports FAIL | KAT context and hash mismatch | `1` | **PASS** |

**Auditor Assessment of Mutation Integrity:**
1. **Relevance:** MUT-1 and MUT-2 directly attack the clean valid-path assertion logic in `test_d`. MUT-3 attacks the production PRF header context encoding. MUT-4 attacks the production PRF endian serialization.
2. **Harness Execution:** All mutations build a complete test binary and execute `main()`. They do not rely on ad-hoc print inspections or simulated return values.
3. **Working Tree Restoration:** Mutations are applied to temporary files in `/tmp/step2b_mutation_*` with trap cleanup. The working tree was confirmed clean before and after execution.

---

## 4. Independent Campaign Verification & SDC Analysis

### 4.1 Reproduction Commands & Results

The auditor independently ran all verification targets from clean state:

```bash
# 1. Oracle Unit & KAT Verification
./tfib_experiments/phase11_oracle/test_independent_oracle
# Exit code: 0, Output: ALL TESTS PASSED (PASS)

# 2. Step 2B Validation Suite
./tfib_experiments/test_step2b_validation
# Exit code: 0, Output: RESULTS: 7 passed, 0 failed

# 3. Controlled Mutation Checks
./tfib_experiments/run_step2b_mutation_checks.sh
# Exit code: 0, Output: ALL 4 RIGOROUS MUTATION CHECKS PASSED

# 4. Full 900-Trial Campaign Execution
./tfib_experiments/tfib_experiment_runner tfib_experiments/phase2_step2b_audit_verify.csv
# Exit code: 0, Output: ALL AUTOMATED ASSERTIONS PASSED! Total Trials Recorded: 900

# 5. Determinism Check against Baseline
diff -u tfib_experiments/phase2_step2b_runner_output.csv tfib_experiments/phase2_step2b_audit_verify.csv
# Exit code: 0 (Zero diffs)
rm -f tfib_experiments/phase2_step2b_audit_verify.csv
```

### 4.2 Why Identical Results are Expected Despite Serialization Refactoring
The previous implementation used `memcpy(seed_ctx, vals, 16)` where `vals` was an array of four `uint32_t` values. On the ARM64 target platform (little-endian), a 32-bit unsigned integer in memory is stored with least significant byte first. The refactored `campaign_store32_le()` explicitly stores bytes as `val & 0xFF`, `(val >> 8) & 0xFF`, `(val >> 16) & 0xFF`, `(val >> 24) & 0xFF`.

Because these two operations generate byte-identical byte streams on little-endian hardware, the input to `fips202_ref_shake256()` is mathematically unchanged. Consequently:
- Derived seeds $(d, z, m)$ are unchanged.
- Public/secret keypairs generated by `liboqs` are unchanged.
- Ciphertexts generated by `liboqs` are unchanged.
- Injected fault trigger locations and outcomes are unchanged.
The refactoring achieved cross-platform architecture independence without introducing non-deterministic drift.

### 4.3 End-to-End Cryptographic SDC Analysis
In `run_suite()` (`tfib_experiment_runner.c`, lines 107–110):
```c
bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
bool rej_match = (memcmp(ss_out, ss_rej_expected, SS_BYTES) == 0);
bool sdc = (!ss_match && !rej_match);
```
- Every trial evaluates `ss_out` against `ss_expected` (derived from `independent_oracle_encaps_derand`) and `ss_rej_expected` (derived from `independent_oracle_compute_rejection`).
- SDC classification is strictly end-to-end: if decapsulation produces a shared secret that matches neither the authentic session key nor the canonical rejection key, it is classified as `SILENT_DATA_CORRUPTION`.

**Outcome Breakdown (900 Total Trials):**
- Authentic Shared Secret Match: **403 / 900** (44.78%)
  - Clean Controls: 150
  - Genuine Monitor Recoveries: 250
  - Ineffective Faults Absorbed by Noise Margin: 3
- Canonical Implicit Rejections: **497 / 900** (55.22%)
  - Safe Fail-Stops: 350
  - Local Blind FO Containment: 147
- Silent Data Corruption (SDC): **0 / 900** (0.0%)

**Statistical Risk Caveat:**
Observing 0 SDC events across $N = 900$ trials does not prove that SDC is physically impossible. Under the exact fault space evaluated (single-bit twiddle factor perturbations across stages 1–7 and butterfly indices 0–127), the Clopper-Pearson 95% confidence interval for the probability of SDC is $[0.00\%, 0.41\%]$. The empirical evidence firmly supports the claim that TFIB prevents silent corruption under the specified fault model, bounded by this statistical threshold.

---

## 5. Audit Checklist & Verification Matrix

| Verification Requirement | Auditor Assessment | Evidence |
|---|:---:|---|
| Working tree revision recorded | Verified | Commit `55dd937cbad66b24e5c2c0b89b78fa776801913c` |
| No production cryptographic code modified | Verified | `git diff` confirms zero changes to `algorithms/source_ref/` or `tfib_implementation/` |
| In-tree keygen decoupled | Verified | Disassembly confirms 0 call sites to `mlkem768_keypair` |
| Standard C PRNG eliminated | Verified | `nm -u` confirms zero references to `_rand` or `_srand` |
| DEF-01 remediated | Verified | `test_d` strictly enforces `ss_match == true` & `rej_match == false` |
| DEF-02 remediated | Verified | `campaign_prf.h` is unified single source of truth |
| DEF-03 remediated | Verified | All 6 loci pairwise distinct in Test B |
| DEF-04 remediated | Verified | Terminology updated to deterministic PRF seed expansion |
| DEF-05 remediated | Verified | Little-endian serialization KAT verified via OpenSSL 4.0.2 & Python 3.12 |
| Mutation checks pass | Verified | 4/4 mutations fail test harness with exit code 1 |
| 900-trial campaign reproduced | Verified | Byte-identical output matching baseline CSV with 0 SDC |

---

## 6. Final Audit Verdict

### Verdict: **PASS**

All five findings from the Phase 2 Step 2B independent audit (DEF-01 through DEF-05) have been completely remediated, independently inspected, and verified through automated test suites, rigorous mutation testing, and full campaign reproduction. No remaining defects were identified.

### Closure Status
**Phase 2 Step 2B is CLOSED and ready for sign-off.**  
Authorization is granted to proceed to **Phase 2 Step 2C (Countermeasure Decoupling and Table Relocation)**.
