# Phase 15H — Change Log: Minimal Correction of Invalid-Target Semantics

**Engineer / Auditor:** Conservative C Systems Engineer & Skeptical Cryptographic Research Auditor  
**Date:** 2026-10-11  
**Scope:** Resolution of Confirmed Finding F-15G-01 from `PHASE15G_AUDIT.md`  
**Target Repository:** `space-resilience-framework` (HEAD: `4a2c4ebf9274a9188db3610a4f8448902caed056`)  
**Directory:** `research/phase14_persistent_arm_design/`  

---

## 1. Summary of Changes

Phase 15H implements the minimal justified correction to resolve Finding **F-15G-01** (Invalid-Target Semantics Misattribution).

### Core Changes:
1. **Source Correction (`pilot_runner.c`):**
   - Lines 475 & 674: Replaced `"RESTORED_AND_BASELINE_RECHECK_PASSED"` with `"NOT_RUN_INVALID_TARGET"`.
   - Guaranteed that any trial rejected pre-execution due to invalid target index (`target_idx < -1 || target_idx >= 128`) assigns a truthful restoration status that does not claim restoration or baseline KAT verification occurred.
2. **Binary Recompilation (`bin/pilot_runner`):**
   - Cleanly rebuilt using standard Apple Clang `-O3 -Wall -Wextra -std=c11` compiler flags linking the relocatable object `bin/obj/mlkem768_persistent_reloc.o`.
3. **Non-Mutating Verification:**
   - Executed `--check-oracle` mode confirming that the independent FIPS 202 SHAKE256 self-test and $J(z \parallel c, 32)$ rejection-key oracle run cleanly without memory protection modification or table mutation.
4. **Historical & Git Preservation:**
   - Preserved all historical reports, errata, matrices, and backups byte-for-byte.
   - Left all 7 pre-existing modified files in Git untouched.

---

## 2. Modified and Created Files

### Created Files:
1. `research/phase14_persistent_arm_design/PHASE15H_REPORT.md`:
   Authoritative engineering report detailing the defect, resolution, hash ledger, and final verdict.
2. `research/phase14_persistent_arm_design/PHASE15H_CHANGELOG.md`:
   This change log.

### Modified Files:
1. `research/phase14_persistent_arm_design/pilot_runner.c`:
   - Line 475: Bounds check failure branch (`target_idx < -1 || target_idx >= 128`) now sets `records[t].restoration_status = "NOT_RUN_INVALID_TARGET";`.
   - Line 674: Defensive unreachable fallback branch now sets `records[t].restoration_status = "NOT_RUN_INVALID_TARGET";`.
2. `bin/pilot_runner`:
   - Recompiled binary reflecting the status fix.

---

## 3. Code Diff

```diff
--- a/research/phase14_persistent_arm_design/pilot_runner.c
+++ b/research/phase14_persistent_arm_design/pilot_runner.c
@@ -472,7 +472,7 @@ int main(int argc, char **argv) {
             records[t].mutation_status = "REJECTED";
             records[t].consumption_status = "VERIFIED_NOT_CONSUMED";
             records[t].crypto_endpoint = "NOT_RUN";
-            records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED";
+            records[t].restoration_status = "NOT_RUN_INVALID_TARGET";
             continue;
         }
 
@@ -670,7 +670,7 @@ int main(int argc, char **argv) {
             records[t].mutation_status = "REJECTED";
             records[t].consumption_status = "VERIFIED_NOT_CONSUMED";
             records[t].crypto_endpoint = "NOT_RUN";
-            records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED";
+            records[t].restoration_status = "NOT_RUN_INVALID_TARGET";
             continue;
         }
     }
```

---

## 4. Execution Commands and Validation Records

### 4.1 Compilation (Static Build Verification)
```bash
clang -O3 -Wall -Wextra -std=c11 \
  -I . -I algorithms/source_ref/mlkem \
  research/phase14_persistent_arm_design/pilot_runner.c \
  bin/obj/mlkem768_persistent_reloc.o \
  -o bin/pilot_runner
```
- **Compiler:** Apple clang version 21.0.0 (`clang-2100.1.1.101`)
- **Target:** `arm64-apple-darwin27.0.0`
- **Exit Code:** `0`
- **Diagnostic Output:** None (clean compilation, zero warnings).

### 4.2 Non-Mutating Validation (`--check-oracle`)
```bash
./bin/pilot_runner --check-oracle
```
- **Exit Code:** `0`
- **Output:**
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

---

## 5. Authoritative SHA-256 Digest Verification

```text
39f7e83140e1a8ebceb3e2fc091382cad918fff8eb381b73db551bbbcab4b871  research/phase14_persistent_arm_design/pilot_runner.c
d9da42c33cf45816800e0591cfbc0c0700bb6033883f601aa6f7b834cedd716e  bin/pilot_runner
c239e7cf355404af7eb616c58832a6f6b9fbb9c708f83df46c9e5d01264deb9f  bin/obj/mlkem768_persistent_reloc.o
bbddee21f2d6bbcd44a972da0a7c5b0450f77dc1812b06d70172ae1bc9f352ba  research/phase14_persistent_arm_design/pilot_runner.c.phase15b_bak
0a5302256db2e5b3f70df1820e21f15ac509fa07e1044d02d6a0dda727554e37  research/phase14_persistent_arm_design/PHASE15B_REPORT.md
5cf48fb9ab869cff6345eb1b8d03785ec65d3ab1c2ee76cab29d4ea6bde45d2c  research/phase14_persistent_arm_design/PHASE15B_TRIAL_LEDGER.csv
d305ae1710b30ad835754578eb89038903e2c4004d4145d00fe71df94a7bcf02  research/phase14_persistent_arm_design/PHASE15F_ERRATA.md
d20986483251844a541baedfa94a69c15a9832f5029a8f9844634e81f6c95b34  research/phase14_persistent_arm_design/PHASE15F_CHANGELOG.md
4722015c8cc4c97e6ac81177f74c8a024b0894894cccca42d926259c4ec742e9  research/phase14_persistent_arm_design/PHASE15G_AUDIT.md
ef7ad7c87e1a6dd48ea8e73d6ebf4aa7321cb26e7bb6487bb8cb7bacfa895c45  research/phase14_persistent_arm_design/PHASE15G_FINDINGS_MATRIX.md
```

---

## 6. Findings Matrix Status

| Finding ID | Title | Prior Status (15G) | Status Post-15H | Notes |
|:---:|:---|:---:|:---:|:---|
| **F-15G-01** | Invalid-Target Semantics Misattribution | FAIL (High) | **RESOLVED** | Replaced with `"NOT_RUN_INVALID_TARGET"` at lines 475 & 674. |
| **F-15G-02** | Mixed Diagnostic & CSV Output Stream | PASS (Medium) | OPEN (Non-blocking) | stdout contains diagnostic banners; parsers must filter for CSV header or regex. |
| **F-15G-03** | Unquoted CSV String Fields | PASS (Low) | OPEN (Non-blocking) | Safe for 16 hardcoded strings; quoting recommended if strings become arbitrary. |

---

## 7. Mandatory Constraints Adherence Confirmation

- **Zero Live Pilot Trials Executed:** Verified.
- **Zero Twiddle Table Mutations:** Verified.
- **Zero Memory Protection Manipulations for Testing:** Verified.
- **Zero Modifications to Production Cryptographic Sources:** Verified.
- **Byte-for-Byte Preservation of Historical Files:** Verified.
- **Preservation of Pre-Existing Git Modifications:** Verified.
