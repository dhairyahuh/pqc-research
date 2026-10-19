# Phase 2 — Step 2B Remediation & Closure Report

**Task:** Remediation of Outstanding Findings from Phase 2 Step 2B Independent Audit  
**Repository:** `pqc-research`  
**Branch:** `space-resilience-framework`  
**Engineer:** Skeptical Cryptographic Software Verification Engineer  
**Date:** 2026-10-04  
**Final Remediation Verdict:** **PASS** (All 5 audit findings remediated, tested, and validated with zero regressions)

---

## 1. Executive Summary

This report documents the resolution of all five defects identified during the independent audit of Phase 2 Step 2B (Key Generation and Deterministic Randomness):

| Defect ID | Finding Category | Nature of Defect | Resolution Status |
|---|---|---|:---:|
| **DEF-01** | Test Assertion Strength | Test D accepted implicit rejection (`rej_match == true`) on unfaulted clean runs | **RESOLVED** |
| **DEF-02** | Test Logic Duplication | `campaign_prf()` was copied as a static function in `test_step2b_validation.c` | **RESOLVED** |
| **DEF-03** | PRF Input Differentiation | Test B omitted testing variation across fault loci | **RESOLVED** |
| **DEF-04** | Cryptographic Terminology | Reports and comments claimed "CSPRNG Integration" instead of deterministic PRF | **RESOLVED** |
| **DEF-05** | Portable Serialization | Context serialization relied on host-endian `memcpy(seed_ctx, vals, 16)` | **RESOLVED** |

All remediations were validated against:
1. The independent reference oracle KAT suite (`test_independent_oracle`: 6/6 PASS).
2. The remediated validation test suite (`test_step2b_validation`: 7/7 PASS).
3. Automated mutation testing (`run_step2b_mutation_checks.sh`: 4/4 mutations caught with exit code 1).
4. The full 900-trial experimental campaign (`tfib_experiment_runner`: 900/900 trials passed, 0 SDC, bit-for-bit identical to historical baseline).

---

## 2. Detailed Technical Remediations

### 2.1 DEF-01: Clean-Path Assertion Strengthening
**Audit Finding:** In `test_step2b_validation.c`, Test D previously incremented `sdc_count` only if `!ss_match && !rej_match`. If an implementation defect caused clean decapsulation to fail and return the rejection key, the test would falsely report success.

**Remediation:** In `test_step2b_validation.c`, Test D (`test_d_clean_path_pipeline`) was rewritten with strict clean-path invariants:
```c
/* Clean authentic decapsulation invariants:
 * 1. Output MUST match the independent oracle's valid expected shared secret.
 * 2. Output MUST NOT match the implicit rejection key.
 * 3. Valid shared secret and rejection key MUST be distinct.
 */
bool ss_match = (memcmp(ss_out, ss_expected, SS_BYTES) == 0);
bool rej_match = (memcmp(ss_out, ss_rej, SS_BYTES) == 0);
bool keys_distinct = (memcmp(ss_expected, ss_rej, SS_BYTES) != 0);

if (!ss_match || rej_match || !keys_distinct) {
    clean_failures++;
}
```
**Empirical Verification:** Mutation MUT-1 (corrupting `ss_expected`) and Mutation MUT-2 (forcing `ss_out = ss_rej`) both cause Test D to fail and the test binary to exit with non-zero code `1`.

---

### 2.2 DEF-02 & DEF-05: Shared PRF Header & Explicit Little-Endian Serialization
**Audit Findings:**
- DEF-02: `test_step2b_validation.c` had a duplicated local copy of `campaign_prf()`.
- DEF-05: Serialization in `campaign_prf()` used `memcpy(seed_ctx, vals, 16)`, which relied on host byte ordering and would produce different hashes on big-endian architectures.

**Remediation:**
1. Created `tfib_experiments/campaign_prf.h` as the single authoritative definition of PRF context serialization and expansion.
2. Implemented `campaign_store32_le()` to guarantee explicit little-endian serialization across all architectures:
```c
static inline void campaign_store32_le(uint8_t out[4], uint32_t val) {
    out[0] = (uint8_t)(val & 0xFFu);
    out[1] = (uint8_t)((val >> 8) & 0xFFu);
    out[2] = (uint8_t)((val >> 16) & 0xFFu);
    out[3] = (uint8_t)((val >> 24) & 0xFFu);
}

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
3. Replaced local implementations in both `tfib_experiment_runner.c` and `test_step2b_validation.c` with `#include "campaign_prf.h"`.
4. Added Test G (`test_g_explicit_serialization_kat`) to assert exact byte sequences for known inputs against reference vectors:
   - Input `(trial=0, mode=BASELINE, locus=NONE, persistent=false)` $\implies$ `dec03713000000000000000000000000`.
   - Input `(trial=42, mode=REF, locus=OP_TWIDDLE, persistent=true)` $\implies$ `f4c53713010000000100000001000000`.
   - Output SHAKE-256 hashes verified against KAT constants.

---

### 2.3 DEF-03: Comprehensive PRF Input Differentiation
**Audit Finding:** Test B in `test_step2b_validation.c` varied `trial`, `mode`, and `persistent`, but omitted testing variations of `locus`.

**Remediation:** Expanded Test B (`test_b_prf_domain_separation`) to exercise all 6 locus enumerations pairwise:
- `TFIB_FAULT_NONE` (0)
- `TFIB_FAULT_OP_TWIDDLE` (1)
- `TFIB_FAULT_REF_TWIDDLE` (2)
- `TFIB_FAULT_SIMULTANEOUS` (3)
- `TFIB_FAULT_CHECKER_LOGIC` (4)
- `TFIB_FAULT_META_TAG` (5)

Asserts that all $\binom{6}{2} = 15$ pairs produce strictly distinct 96-byte derived outputs. Mutation MUT-3 (forcing `locus = 0` in serialization) fails Test B and returns exit code `1`.

---

### 2.4 DEF-04: Accurate Cryptographic Terminology
**Audit Finding:** Documentation and comments referred to the mechanism as a "CSPRNG", which is inaccurate because no dynamic OS entropy, `/dev/urandom`, or PRNG state machine is involved.

**Remediation:**
1. Updated all titles, comments, and reports to describe the mechanism accurately as:
   **"Deterministic SHAKE-256 PRF-based Seed Expansion"**.
2. Explicitly documented the engineering rationale: fault-injection experimentation requires strict deterministic reproducibility per trial tuple `(trial, mode, locus, persistent)`. An unseeded OS CSPRNG would introduce non-reproducible trial variance.

---

## 3. List of Changed Files

| File | Nature of Change | Rationale |
|---|---|---|
| [`tfib_experiments/campaign_prf.h`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/campaign_prf.h) | **Created** | Shared header containing explicit little-endian serialization (`campaign_store32_le`, `campaign_prf_serialize_context`) and `campaign_prf()`. Resolves DEF-02, DEF-04, DEF-05. |
| [`tfib_experiments/tfib_experiment_runner.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/tfib_experiment_runner.c) | **Modified** | Replaced local static PRF with `#include "campaign_prf.h"`. Updated comments to remove CSPRNG overstatements. |
| [`tfib_experiments/test_step2b_validation.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/test_step2b_validation.c) | **Modified** | Removed duplicate PRF; added DEF-01 clean-path assertions; added DEF-03 locus domain separation; added DEF-05 serialization KAT (Test G). |
| [`tfib_experiments/run_step2b_tests.sh`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/run_step2b_tests.sh) | **Modified** | Added include flags (`-Itfib_experiments`) and updated log messages to use precise PRF terminology. |
| [`tfib_experiments/run_step2b_mutation_checks.sh`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/run_step2b_mutation_checks.sh) | **Created** | Automated mutation test harness verifying that deliberate corruptions fail tests with exit code 1. |
| [`tfib_experiments/phase2_step2b_keygen_csprng_report.md`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/phase2_step2b_keygen_csprng_report.md) | **Modified** | Retitled and updated with accurate cryptographic terminology, test table, and remediation closure documentation. |
| [`tfib_experiments/phase2_step2b_remediation_test_results.md`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/phase2_step2b_remediation_test_results.md) | **Created** | Exact command outputs, exit codes, and campaign metrics. |

---

## 4. Controlled Mutation Verification Summary

Four controlled mutations were executed via `tfib_experiments/run_step2b_mutation_checks.sh`:

```
================================================================================
Phase 2 Step 2B Rigorous Mutation Verification
================================================================================
[*] Baseline: Verifying unmutated test suite passes with exit code 0...
  ✓ Baseline passed (Exit 0)

[*] Mutation 1: Deliberately corrupting expected valid secret in clean-path test...
  ✓ Mutation 1 successfully caught: Test D failed as expected (Exit code 1)

[*] Mutation 2: Simulating decapsulation returning rejection key on clean ciphertext...
  ✓ Mutation 2 successfully caught: Test D failed when output matches rejection key (Exit code 1)

[*] Mutation 3: Removing locus input differentiation from campaign_prf context...
  ✓ Mutation 3 successfully caught: Test B failed when locus differentiation was removed (Exit code 1)

[*] Mutation 4: Altering byte serialization order to big-endian...
  ✓ Mutation 4 successfully caught: Test G (KAT) failed when serialization was altered (Exit code 1)

================================================================================
ALL 4 RIGOROUS MUTATION CHECKS PASSED (All mutations caught with exit code 1)
================================================================================
```

---

## 5. Final Evidence-Based Verdict

### Verdict: **PASS**

**Distinction of Completed Checks vs Unverified Claims:**
- **Completed & Verified:**
  - Independent oracle keypair generation: verified via disassembly (0 in-tree keypair calls) and KATs.
  - Decoupling from libc PRNG: verified via dynamic symbol table inspection (no `_rand` or `_srand`).
  - PRF determinism and domain separation: verified across all trials, modes, loci, and persistence flags.
  - Explicit little-endian encoding: verified via byte KATs and cross-architecture endian equivalence checks.
  - Zero SDC campaign invariant: verified across 900 trials ($0 / 900$, 95% Clopper-Pearson CI: $[0.00\%, 0.41\%]$).
  - Test sensitivity: verified via 4 controlled mutation checks returning exit code 1.
- **Explicit Limitations / Non-Claims:**
  - `campaign_prf()` does not provide information-theoretic unpredictability or dynamic entropy; it is a fixed-seed PRF designed strictly for experimental repeatability.
  - Production decapsulation under test (`mlkem768_dec_monitored`) remains linked via `bin/obj/mlkem768_inst.o`, which is the intended subject of the experiment.

Phase 2 Step 2B is fully remediated, verified, and closed. Step 2C (Countermeasure Decoupling and Table Relocation) is ready to proceed upon authorization.
