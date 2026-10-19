# Phase 15H — Minimal Correction of Invalid-Target Trial Semantics

**Author:** Conservative C Systems Engineer & Skeptical Cryptographic Research Auditor  
**Date:** 2026-10-11  
**Target Repository State:** Git branch `space-resilience-framework` (HEAD: `4a2c4ebf9274a9188db3610a4f8448902caed056`)  
**Scope:** Resolution of Confirmed Blocking Finding **F-15G-01** from `PHASE15G_AUDIT.md` Only  
**Directory:** `research/phase14_persistent_arm_design/`  

---

## 1. Executive Summary & Defect Statement

During the Phase 15G independent read-only review, blocking finding **F-15G-01** was identified:
In `research/phase14_persistent_arm_design/pilot_runner.c` (at lines 475 and 674), when an invalid target index (`target_idx < -1 || target_idx >= 128`) was rejected before trial execution, the harness assigned:
```c
records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED";
```
This semantic assignment was **factually false and misleading**:
1. **No Restoration Occurred:** The trial was aborted prior to computing memory offsets or unprotecting the twiddle table; no mutation was applied, so no restoration routine was ever invoked.
2. **No Baseline Recheck Occurred:** The post-trial decapsulation KAT recheck was never executed for an aborted trial.
3. **Data Model Contradiction:** The emitted 9-column ledger row recorded `crypto_endpoint = "NOT_RUN"` and `output_ss = 0000...0000`, yet claimed in `restoration_status` that baseline rechecking had passed.
4. **Aggregation Hazard:** Any downstream automated parser filtering by `restoration_status == "RESTORED_AND_BASELINE_RECHECK_PASSED"` would falsely count invalid, unexecuted trials as successful restorations and successful baseline verifications.

Phase 15H implements the minimal justified correction to resolve Finding F-15G-01 without modifying production code, historical audit ledgers, or running live fault injection.

---

## 2. Minimal Correction Implementation

The correction was strictly confined to `research/phase14_persistent_arm_design/pilot_runner.c`:
1. In the pre-execution target bounds check (`target_idx < -1 || target_idx >= 128`), `records[t].restoration_status` was updated to `"NOT_RUN_INVALID_TARGET"`.
2. In the defensive unreachable fallback branch (`else` after valid mutation/sham and baseline cases), `records[t].restoration_status` was identically updated to `"NOT_RUN_INVALID_TARGET"`.

### Exact Source Diff
```diff
--- research/phase14_persistent_arm_design/pilot_runner.c (Phase 15F)
+++ research/phase14_persistent_arm_design/pilot_runner.c (Phase 15H)
@@ -472,7 +472,7 @@
             records[t].mutation_status = "REJECTED";
             records[t].consumption_status = "VERIFIED_NOT_CONSUMED";
             records[t].crypto_endpoint = "NOT_RUN";
-            records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED";
+            records[t].restoration_status = "NOT_RUN_INVALID_TARGET";
             continue;
         }
 
@@ -670,7 +670,7 @@
             records[t].mutation_status = "REJECTED";
             records[t].consumption_status = "VERIFIED_NOT_CONSUMED";
             records[t].crypto_endpoint = "NOT_RUN";
-            records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED";
+            records[t].restoration_status = "NOT_RUN_INVALID_TARGET";
             continue;
         }
```

### Truthful Rejection Invariants
For any invalid trial (`target_idx < -1 || target_idx >= 128`):
- `mutation_status`: `"REJECTED"` (mutation was denied prior to execution)
- `consumption_status`: `"VERIFIED_NOT_CONSUMED"` (table was never modified or consumed)
- `crypto_endpoint`: `"NOT_RUN"` (decapsulation endpoint was not executed)
- `restoration_status`: `"NOT_RUN_INVALID_TARGET"` (no restoration or recheck executed)
- `output_ss`: 64 zeros (`0000000000000000000000000000000000000000000000000000000000000000`)
- `expected_behavior`: Predeclared specification description preserved

---

## 3. Four-Way Semantic Partitioning

The trial harness now strictly partitions all trial targets into four mutually exclusive classes:

| Class | Target Condition | Mutation Status | Consumption Status | Crypto Endpoint | Restoration Status |
|:---|:---|:---:|:---:|:---:|:---:|
| **Valid Baseline** | `target_idx == -1` | `NOT_ATTEMPTED` | `VERIFIED_NOT_CONSUMED` | Classified (`EXPECTED_OUTPUT`) | `RESTORED_AND_BASELINE_RECHECK_PASSED` (if table clean) |
| **Valid Mutation** | `0 <= target_idx < 128` && `bit_mask != 0` | `APPLIED` | Classified (`VERIFIED_CONSUMED` / `VERIFIED_NOT_CONSUMED`) | Classified (`EXPECTED_OUTPUT` / `REJECTION` / `DIFFERENT_OUTPUT` / `NO_OUTPUT`) | `RESTORED_AND_BASELINE_RECHECK_PASSED` (if transactional cleanup passes) |
| **Valid Sham** | `0 <= target_idx < 128` && `bit_mask == 0` | `APPLIED` | `VERIFIED_NOT_CONSUMED` | `EXPECTED_OUTPUT` | `RESTORED_AND_BASELINE_RECHECK_PASSED` (if transactional cleanup passes) |
| **Invalid Target** | `target_idx < -1` \|\| `target_idx >= 128` | `REJECTED` | `VERIFIED_NOT_CONSUMED` | `NOT_RUN` | `NOT_RUN_INVALID_TARGET` |

---

## 4. Summary Counters, Aggregation, and Schema Review

1. **Counters & Aggregations:** Review of `pilot_runner.c` confirmed there are no internal summary counters or aggregators computing pass rates. The runner directly prints each trial record.
2. **Downstream Aggregation Safety:** Any external analysis script evaluating `restoration_status == "RESTORED_AND_BASELINE_RECHECK_PASSED"` will now correctly exclude invalid targets.
3. **9-Column Schema Preservation:** The schema header:
   `trial_id,target_idx,bit_mask,mutation_status,consumption_status,crypto_endpoint,restoration_status,output_ss,expected_behavior`
   remains byte-compatible with the schema established in `PHASE15B_TRIAL_LEDGER.csv` and confirmed in Phase 15F/15G. Field count (9) and field order are 100% preserved.

---

## 5. Non-Mutating Validation Record

All validation in Phase 15H was strictly non-mutating:

### 5.1 Compilation
- **Compiler:** Apple clang version 21.0.0 (`clang-2100.1.1.101`, `arm64-apple-darwin27.0.0`)
- **Command:**
  ```bash
  clang -O3 -Wall -Wextra -std=c11 \
    -I . -I algorithms/source_ref/mlkem \
    research/phase14_persistent_arm_design/pilot_runner.c \
    bin/obj/mlkem768_persistent_reloc.o \
    -o bin/pilot_runner
  ```
- **Exit Code:** `0`
- **Compiler Warnings:** Zero warnings.

### 5.2 Non-Mutating Oracle Verification (`--check-oracle`)
- **Command:**
  ```bash
  ./bin/pilot_runner --check-oracle
  ```
- **Exit Code:** `0`
- **Execution Log:**
  ```text
  =======================================================================
   PHASE 15D: HARDENED PERSISTENT-TABLE FEASIBILITY RUNNER
   Target: mlk_zetas_page (ML-KEM-768 relocated twiddle table)
  =======================================================================

  --- [ORACLE VALIDATION] Independent FIPS 202 SHAKE256 Self-Test ---
    SHAKE256("", 32) matches NIST FIPS 202 KAT:
    46b9dd2b0ba88d13233b3feb743eeb243fcd52ea62b81b82b50c27646ed5762f
    Result: PASS

  --- [ORACLE DERIVATION] Independent FIPS 203 Rejection Key Derivation ---
    Concatenation length: 1120 bytes (32-byte z + 1088-byte ciphertext c)
    Derived FIPS 203 K_rej: f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03
    Expected KAT K_rej:    f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03
    Result: PASS (Independent Oracle Bit-Identical to Expected FIPS 203 KAT)

  >>> Oracle check completed successfully (--check-oracle mode). Exiting without memory mutation. <<<
  ```
- **Confirmation:** The independent SHAKE256 self-test and $J(z \parallel c, 32)$ rejection-key oracle passed bit-for-bit without executing memory protection changes or table mutations.

---

## 6. Cryptographic Hash Provenance & File Integrity Ledger

The following table records the SHA-256 digests across all versions, explicitly distinguishing Phase 15H artifacts from all prior phases:

| File / Artifact Path | Phase 15B / 15D / 15F Hash | Phase 15H Authoritative SHA-256 | Status |
|:---|:---|:---|:---:|
| `research/phase14_persistent_arm_design/pilot_runner.c` | `ea253b5bbde2406f3d93061e2e1652e78ba8b3f68c66cf7a774d29f59b18d95d` (15F) | `39f7e83140e1a8ebceb3e2fc091382cad918fff8eb381b73db551bbbcab4b871` | **UPDATED (Phase 15H fix)** |
| `bin/pilot_runner` | `8de41e4a7631535d60b1d8b193f518098870b4cf230481aaf0d5fda5f0c03afd` (15F) | `d9da42c33cf45816800e0591cfbc0c0700bb6033883f601aa6f7b834cedd716e` | **RECOMPILED (Phase 15H)** |
| `bin/obj/mlkem768_persistent_reloc.o` | `c239e7cf355404af7eb616c58832a6f6b9fbb9c708f83df46c9e5d01264deb9f` | `c239e7cf355404af7eb616c58832a6f6b9fbb9c708f83df46c9e5d01264deb9f` | **PRESERVED BYTE-FOR-BYTE** |
| `pilot_runner.c.phase15b_bak` | `bbddee21f2d6bbcd44a972da0a7c5b0450f77dc1812b06d70172ae1bc9f352ba` | `bbddee21f2d6bbcd44a972da0a7c5b0450f77dc1812b06d70172ae1bc9f352ba` | **PRESERVED BYTE-FOR-BYTE** |
| `PHASE15B_REPORT.md` | `0a5302256db2e5b3f70df1820e21f15ac509fa07e1044d02d6a0dda727554e37` | `0a5302256db2e5b3f70df1820e21f15ac509fa07e1044d02d6a0dda727554e37` | **PRESERVED BYTE-FOR-BYTE** |
| `PHASE15B_TRIAL_LEDGER.csv` | `5cf48fb9ab869cff6345eb1b8d03785ec65d3ab1c2ee76cab29d4ea6bde45d2c` | `5cf48fb9ab869cff6345eb1b8d03785ec65d3ab1c2ee76cab29d4ea6bde45d2c` | **PRESERVED BYTE-FOR-BYTE** |
| `PHASE15F_ERRATA.md` | `d305ae1710b30ad835754578eb89038903e2c4004d4145d00fe71df94a7bcf02` | `d305ae1710b30ad835754578eb89038903e2c4004d4145d00fe71df94a7bcf02` | **PRESERVED BYTE-FOR-BYTE** |
| `PHASE15F_CHANGELOG.md` | `d20986483251844a541baedfa94a69c15a9832f5029a8f9844634e81f6c95b34` | `d20986483251844a541baedfa94a69c15a9832f5029a8f9844634e81f6c95b34` | **PRESERVED BYTE-FOR-BYTE** |
| `PHASE15G_AUDIT.md` | `4722015c8cc4c97e6ac81177f74c8a024b0894894cccca42d926259c4ec742e9` | `4722015c8cc4c97e6ac81177f74c8a024b0894894cccca42d926259c4ec742e9` | **PRESERVED BYTE-FOR-BYTE** |
| `PHASE15G_FINDINGS_MATRIX.md` | `ef7ad7c87e1a6dd48ea8e73d6ebf4aa7321cb26e7bb6487bb8cb7bacfa895c45` | `ef7ad7c87e1a6dd48ea8e73d6ebf4aa7321cb26e7bb6487bb8cb7bacfa895c45` | **PRESERVED BYTE-FOR-BYTE** |

---

## 7. Remaining Limitations & Boundaries

1. **Non-Mutating Verification Only:** The rejection paths were verified by static source code analysis and clean compilation. No live trial was executed in this phase to trigger the rejection runtime banner, strictly honoring the mandatory non-mutation constraint.
2. **Stdout Stream Mixing (Finding F-15G-02):** Diagnostic banners (`--- [DIAGNOSTIC TRIAL %d/16] ---`) and execution logs are emitted to `stdout` alongside the CSV summary table. Ingestion tools must grep for the CSV header or parse lines matching the CSV regex.
3. **Unquoted String Fields (Finding F-15G-03):** The `expected_behavior` field does not use enclosing double quotes. This is safe for the hardcoded 16 trial strings (which contain no commas), but would need RFC 4180 quoting if expanded to arbitrary text.
4. **No Live Pilot or Phase 16 Authorization:** Phase 15H is strictly a corrective repair of the trial ledger semantics. It does not grant authorization to execute a live pilot or commence Phase 16.

---

## 8. Explicit Non-Mutation Confirmation

**Confirmation Statement:**  
During Phase 15H, **no live pilot trials were executed**, **no twiddle table memory was mutated**, **no fault injection was performed**, and **no memory protection attributes (`vm_protect`) were modified for experimental purposes**. Unrelated pre-existing Git modifications were fully preserved.

---

## Final Verdict

# **CORRECTION VERIFIED — READY FOR A SEPARATE REVIEW**

Finding **F-15G-01** is resolved. Pre-execution invalid-target rejections can no longer record `RESTORED_AND_BASELINE_RECHECK_PASSED` in the trial ledger.
