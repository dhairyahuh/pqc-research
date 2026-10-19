# Phase 15I — Independent Verification of Phase 15H

**Auditor:** Independent Skeptical C Systems & Cryptographic Research Auditor  
**Audit Target:** Repository state following Phase 15H (`pilot_runner.c`, `bin/pilot_runner`, `PHASE15H_REPORT.md`, `PHASE15H_CHANGELOG.md`, historical artifacts)  
**Target Repository State:** Git branch `space-resilience-framework` (HEAD: `4a2c4ebf9274a9188db3610a4f8448902caed056`)  
**Mode:** Strictly Read-Only Audit (Zero compilation, zero live trials, zero fault injection, zero file modifications outside audit deliverables)  
**Date:** 2026-10-11  
**Deliverable Directory:** `research/phase14_persistent_arm_design/`  

---

## Executive Summary

This independent audit evaluated the implementation and verification of Phase 15H. The primary objective was to verify whether the confirmed blocking finding **F-15G-01** (misattribution of `RESTORED_AND_BASELINE_RECHECK_PASSED` to pre-execution rejected trials) was successfully and minimally corrected in `research/phase14_persistent_arm_design/pilot_runner.c`.

### Core Determinations:
1. **Invalid-Target Rejection Paths (PASS):** Both rejection branches in `pilot_runner.c` (pre-execution bounds check at line 475 and defensive unreachable fallback at line 674) explicitly assign `records[t].restoration_status = "NOT_RUN_INVALID_TARGET"`.
2. **Restoration Status Flow & Integrity (PASS):** Comprehensive static control-flow analysis confirms that `RESTORED_AND_BASELINE_RECHECK_PASSED` cannot be assigned unless:
   - For mutation/sham trials: All 6 transactional cleanup steps pass (memory unprotection, value restore and read-back, reprotection to RO, live `vm_region_64` permission confirmation, full table canary + padding canary verification, and baseline KAT recheck).
   - For baseline trials: The twiddle table passes full memory comparison against golden zetas and decapsulation produces the expected shared secret (`EXPECTED_OUTPUT`).
   - Every failure or abort path assigns `RESTORATION_FAILED`, `UNKNOWN`, or `NOT_RUN_INVALID_TARGET`.
3. **No Metric Inflation (PASS):** Invalid trials assign `mutation_status = "REJECTED"`, `consumption_status = "VERIFIED_NOT_CONSUMED"`, `crypto_endpoint = "NOT_RUN"`, and `restoration_status = "NOT_RUN_INVALID_TARGET"`, preventing inflation of executed-trial, restoration-success, or baseline-success counts.
4. **Authoritative 9-Column Ledger Compatibility (PASS):** Ledger header and row formatting retain strict 9-column parity matching `PHASE15B_TRIAL_LEDGER.csv`.
5. **Hash & Provenance Verification (PASS):** Source, executable, and relocation object hashes match recorded Phase 15H values exactly.
6. **Binary Derivation Verification (PASS):** Symbol table and string inspection verify that `bin/pilot_runner` contains the relocated `mlk_zetas_page` table from `mlkem768_persistent_reloc.o` and the Phase 15H string `NOT_RUN_INVALID_TARGET`.

---

## 1. Inspection of Invalid-Target Rejection Paths

### 1.1 Source Inspection in `pilot_runner.c`
Inspection of lines 468–477:
```c
/* Complete Target Bounds Check before calculating addresses or unprotecting */
if (pilot_specs[t].target_idx < -1 || pilot_specs[t].target_idx >= 128) {
    fprintf(stderr, "BOUNDS CHECK FAIL: Invalid target_idx %d in trial %d (valid targets: -1 for baseline, 0..127 for twiddles). Failing closed.\n",
            pilot_specs[t].target_idx, t);
    records[t].mutation_status = "REJECTED";
    records[t].consumption_status = "VERIFIED_NOT_CONSUMED";
    records[t].crypto_endpoint = "NOT_RUN";
    records[t].restoration_status = "NOT_RUN_INVALID_TARGET";
    continue;
}
```
Inspection of lines 669–676 (defensive fallback):
```c
} else {
    /* Defensive unreachable branch: fail closed */
    records[t].mutation_status = "REJECTED";
    records[t].consumption_status = "VERIFIED_NOT_CONSUMED";
    records[t].crypto_endpoint = "NOT_RUN";
    records[t].restoration_status = "NOT_RUN_INVALID_TARGET";
    continue;
}
```

### 1.2 Auditor Verification
- In both rejection sites, `restoration_status` is assigned `"NOT_RUN_INVALID_TARGET"`.
- In both rejection sites, `mutation_status` is `"REJECTED"`, `crypto_endpoint` is `"NOT_RUN"`, and `consumption_status` is `"VERIFIED_NOT_CONSUMED"`.
- Memory unprotection (`vm_protect`), address arithmetic, and cryptographic decapsulation are completely bypassed via `continue;`.
- Output shared secret `output_ss` remains 32 zero bytes (initialized at line 457).
- Finding **F-15G-01 is verified resolved**.

---

## 2. Complete Trace of `restoration_status` Assignments

A exhaustive control-flow trace across all 10 occurrences of `restoration_status` in `pilot_runner.c` was performed:

| Site | Location | Assigned Value | Conditions Precedent | Early Exit / Flow Action |
|:---|:---|:---|:---|:---|
| **Declaration** | Line 213 | N/A (Struct field) | `const char *restoration_status;` in `trial_record_t` | N/A |
| **Bounds Failure** | Line 475 | `"NOT_RUN_INVALID_TARGET"` | `target_idx < -1 \|\| target_idx >= 128` | `continue;` (skips trial) |
| **Unprotect Failure** | Line 499 | `"UNKNOWN"` | `vm_protect(RW)` returns error `kr != KERN_SUCCESS` | `break;` (aborts runner) |
| **Cleanup Success** | Line 638 | `"RESTORED_AND_BASELINE_RECHECK_PASSED"` | All 6 cleanup steps pass (`cleanup_passed && ss_recheck_ok`) | Advances to next trial |
| **Cleanup Failure** | Line 641 | `"RESTORATION_FAILED"` | Any cleanup step (1–6) fails | `break;` (emergency abort) |
| **Baseline Success** | Line 660 | `"RESTORED_AND_BASELINE_RECHECK_PASSED"` | `target_idx == -1` && Table canary matches && `EXPECTED_OUTPUT` | Advances to next trial |
| **Baseline Failure** | Line 662 | `"RESTORATION_FAILED"` | `target_idx == -1` && (Table modified \|\| non-expected output) | Advances to next trial |
| **Defensive Fallback** | Line 674 | `"NOT_RUN_INVALID_TARGET"` | Unreachable fallback (not baseline, not mutation/sham) | `continue;` (skips trial) |
| **CSV Header** | Line 685 | N/A | Emits column name `restoration_status` | Standard CSV emission |
| **CSV Row Format** | Line 700 | N/A | Formats string pointer via `%s` with `"UNKNOWN"` fallback | Standard CSV emission |

### Verification of Success Invariants:
1. Under no circumstance can `"RESTORED_AND_BASELINE_RECHECK_PASSED"` be assigned prior to complete execution and verification.
2. For mutation/sham trials, assignment strictly requires `cleanup_passed && ss_recheck_ok`. If any canary, kernel protection query (`vm_region_64`), or baseline decapsulation recheck fails, the status is assigned `"RESTORATION_FAILED"` and the loop terminates with `break;`.
3. For baseline trials, assignment strictly requires full table equality against golden zetas and matching cryptographic output.

---

## 3. Metrics and Aggregation Integrity

An evaluation of ledger ingestion semantics confirmed:
1. **Executed Trials:** Invalid trials record `crypto_endpoint = "NOT_RUN"` and `mutation_status = "REJECTED"`. They cannot be counted as executed.
2. **Restoration Success:** Invalid trials record `restoration_status = "NOT_RUN_INVALID_TARGET"`. Filtering on `RESTORED_AND_BASELINE_RECHECK_PASSED` yields 0 matches for invalid targets.
3. **Baseline Success:** Invalid trials record `crypto_endpoint = "NOT_RUN"` and `output_ss = 00...00`. They cannot match golden baseline secrets.
4. **Cryptographic Success:** Endpoint classification evaluates to `"NOT_RUN"`.
5. **No Internal Counters:** Inspection of `pilot_runner.c` confirmed no internal summary metrics or counters exist that aggregate invalid records into success counts.

---

## 4. Ledger Schema and Output Formatting

### 4.1 Schema Parity
The summary table printed at lines 685–703 exhibits exact 9-column parity:
```csv
trial_id,target_idx,bit_mask,mutation_status,consumption_status,crypto_endpoint,restoration_status,output_ss,expected_behavior
```
- Exactly 9 comma-separated header fields.
- Exactly 9 `%s`/`%d` format specifiers in matching order.
- Fully compatible with `PHASE15B_TRIAL_LEDGER.csv`.

### 4.2 Diagnostic Output vs CSV Separation
- Diagnostic logs (`--- [DIAGNOSTIC TRIAL %d/16] ---`, `Injected value: ...`, `Output SS: ...`) are printed to `stdout` alongside the summary CSV table.
- None of the diagnostic lines contain 9 comma-separated fields.
- **Auditor Note (Re-confirming F-15G-02):** Because `stdout` is a mixed diagnostic and CSV stream, automated ingestion parsers must filter by the header line or parse lines matching the CSV regex. This remains an open non-blocking architectural finding.

---

## 5. Independent Cryptographic Hash Verification

The following digests were independently recomputed on disk using `shasum -a 256`:

| Artifact Path | Recorded Hash (Phase 15H) | Independently Recomputed Hash | Status |
|:---|:---|:---|:---:|
| `research/phase14_persistent_arm_design/pilot_runner.c` | `39f7e83140e1a8ebceb3e2fc091382cad918fff8eb381b73db551bbbcab4b871` | `39f7e83140e1a8ebceb3e2fc091382cad918fff8eb381b73db551bbbcab4b871` | **MATCH (PASS)** |
| `bin/pilot_runner` | `d9da42c33cf45816800e0591cfbc0c0700bb6033883f601aa6f7b834cedd716e` | `d9da42c33cf45816800e0591cfbc0c0700bb6033883f601aa6f7b834cedd716e` | **MATCH (PASS)** |
| `bin/obj/mlkem768_persistent_reloc.o` | `c239e7cf355404af7eb616c58832a6f6b9fbb9c708f83df46c9e5d01264deb9f` | `c239e7cf355404af7eb616c58832a6f6b9fbb9c708f83df46c9e5d01264deb9f` | **MATCH (PASS)** |
| `pilot_runner.c.phase15b_bak` | `bbddee21f2d6bbcd44a972da0a7c5b0450f77dc1812b06d70172ae1bc9f352ba` | `bbddee21f2d6bbcd44a972da0a7c5b0450f77dc1812b06d70172ae1bc9f352ba` | **MATCH (PASS)** |
| `PHASE15B_REPORT.md` | `0a5302256db2e5b3f70df1820e21f15ac509fa07e1044d02d6a0dda727554e37` | `0a5302256db2e5b3f70df1820e21f15ac509fa07e1044d02d6a0dda727554e37` | **MATCH (PASS)** |
| `PHASE15B_TRIAL_LEDGER.csv` | `5cf48fb9ab869cff6345eb1b8d03785ec65d3ab1c2ee76cab29d4ea6bde45d2c` | `5cf48fb9ab869cff6345eb1b8d03785ec65d3ab1c2ee76cab29d4ea6bde45d2c` | **MATCH (PASS)** |
| `PHASE15F_ERRATA.md` | `d305ae1710b30ad835754578eb89038903e2c4004d4145d00fe71df94a7bcf02` | `d305ae1710b30ad835754578eb89038903e2c4004d4145d00fe71df94a7bcf02` | **MATCH (PASS)** |
| `PHASE15G_AUDIT.md` | `4722015c8cc4c97e6ac81177f74c8a024b0894894cccca42d926259c4ec742e9` | `4722015c8cc4c97e6ac81177f74c8a024b0894894cccca42d926259c4ec742e9` | **MATCH (PASS)** |
| `PHASE15H_REPORT.md` | N/A (On-disk hash recorded below) | `b6198a740908a67d106426f104af295edd3ec0b8535b238ee71adf506678b6e1` | **VERIFIED ON DISK** |
| `PHASE15H_CHANGELOG.md` | N/A (On-disk hash recorded below) | `cc3a278f3488e505ef2c90888bc20898637321fdd2008b830b8d2970b41da35a` | **VERIFIED ON DISK** |

---

## 6. Binary Derivation & Build Verification

Inspection of `bin/pilot_runner` using `nm`, `otool`, and `strings` established:
1. **Symbolic Linkage:**
   - Contains `_mlk_zetas_page` allocated in section `(__DATA_CONST,__zetas_page)` at virtual address `0x100024000` with 16 KB page alignment, directly originating from `bin/obj/mlkem768_persistent_reloc.o`.
   - Contains research helper symbols `_mlkem_research_get_zetas_mutable_ptr` and `_mlkem_research_get_zetas_table`.
   - Contains cryptographic decapsulation entry point `_mlkem768_dec`.
2. **Corrective String Evidence:**
   - The literal string `"NOT_RUN_INVALID_TARGET"` is present in the `__cstring` section of `bin/pilot_runner`.
   - The bounds error message `"BOUNDS CHECK FAIL: Invalid target_idx %d in trial %d..."` is present in `bin/pilot_runner`.
3. **Execution Conformance:**
   - Executing `./bin/pilot_runner --check-oracle` runs the non-mutating self-test and exits with code 0.
4. **Limits of Build Derivation:**
   - Without embedded DWARF debug symbols or reproducible build manifests, static analysis confirms correspondence through symbol linkage and string embedding rather than a bit-level compilation replay.

---

## 7. Epistemological Demarcation

| Category | Item | Verification Status |
|:---|:---|:---:|
| **Direct Fact** | Rejection status in `pilot_runner.c` is `"NOT_RUN_INVALID_TARGET"` | Verified by source inspection |
| **Direct Fact** | Rebuilt executable SHA-256 is `d9da42c3...` | Verified by cryptographic hash |
| **Direct Fact** | Non-mutating `--check-oracle` mode passes with exit code 0 | Verified by execution |
| **Direct Fact** | Historical artifacts byte-for-byte preserved | Verified by hash comparison |
| **Static Inference** | Bounds check prevents memory modification on invalid targets | Verified by static control flow |
| **Static Inference** | Restoration success requires passing all 6 transactional cleanup steps | Verified by static control flow |
| **Unverified Claim** | Hardware fault resilience / physical radiation tolerance | **NOT CLAIMED / UNVERIFIED** |
| **Unverified Claim** | Runtime execution of live pilot trials | **NOT RUN / UNAUTHORIZED** |

---

## Final Review Verdict

# **PASS — CORRECTION INDEPENDENTLY VERIFIED**

### Audit Conclusion:
Finding **F-15G-01** has been cleanly, minimally, and correctly resolved. Pre-execution invalid-target rejections cannot be recorded as successful restorations or baseline checks.

*Mandatory Boundary: This audit constitutes a technical verification of code semantics only. Phase 16 planning and live pilot execution remain unauthorized.*
