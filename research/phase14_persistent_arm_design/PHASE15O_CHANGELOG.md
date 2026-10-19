# Phase 15O — Change Log: Fail-Closed Incomplete-Run Reporting

**Author:** Conservative Cryptographic Systems Engineer & Safety Auditor  
**Date:** 2026-10-11  
**Scope:** Resolution of Phase 15N Incomplete-Run Fall-Through Defect  
**Target Repository:** `space-resilience-framework` (HEAD: `4a2c4ebf9274a9188db3610a4f8448902caed056`)  
**Directory:** `research/phase14_persistent_arm_design/`  

---

## 1. Summary of Changes

Phase 15O resolves the defect identified in `PHASE15N_ABORT_PATH_VERIFICATION.md`, where in-loop aborts (`break;` at lines 501, 643, and 662) fell through to the summary CSV printer and terminated with exit code 0 while printing placeholder records with duplicate `trial_id = 0` and `UNKNOWN` statuses.

### Modifications in `pilot_runner.c`:
1. **Metadata Pre-Population & State Tracking:**
   - Pre-populates `records[t].trial_id = t`, `target_idx`, `bit_mask`, and `desc` for all 16 slots before loop execution.
   - Adds execution state variables: `int trials_recorded = 0;` and `int abort_triggered = 0;`.
2. **Fail-Closed In-Loop Aborts:**
   - Unprotect failure (Step 1): sets `abort_triggered = 1; break;`.
   - Cleanup failure (Step 1–6): sets `abort_triggered = 1; break;`.
   - Baseline decapsulation integrity failure: sets `abort_triggered = 1; break;`.
3. **Partial Ledger Emission:**
   - Summary CSV loop iterates strictly over `t < trials_recorded` rather than hardcoding `16`.
   - Incomplete runs emit only the trials reached ($0 \dots t$), eliminating ghost/placeholder records.
   - Section header dynamically indicates `PARTIAL TRIAL LEDGER (ABORTED RUN - %d/16 TRIALS RECORDED)` on abort.
4. **Machine-Verifiable Completion Markers & Non-Zero Exit Code:**
   - Incomplete/aborted runs print `>>> PILOT RUN ABORTED: INCOMPLETE RUN (%d/16 TRIALS PROCESSED) (STATUS: FAILED) <<<` and return `1`.
   - Successful runs print `>>> PILOT RUN COMPLETE: 16/16 TRIALS PROCESSED (STATUS: SUCCESS) <<<` and return `0`.
5. **Binary Recompilation:**
   - Cleanly rebuilt `bin/pilot_runner` using Apple Clang `-O3 -Wall -Wextra -std=c11`.
6. **Non-Mutating Verification:**
   - Verified `--check-oracle` mode passes with exit code 0.
   - Verified completion strings present in compiled binary.

---

## 2. Source Code Diff

```diff
--- a/research/phase14_persistent_arm_design/pilot_runner.c
+++ b/research/phase14_persistent_arm_design/pilot_runner.c
@@ -456,12 +456,16 @@ int main(int argc, char **argv) {
     trial_record_t records[16];
     memset(records, 0, sizeof(records));
-
     for (int t = 0; t < 16; t++) {
         records[t].trial_id = t;
         records[t].target_idx = pilot_specs[t].target_idx;
         records[t].bit_mask = pilot_specs[t].bit_mask;
         records[t].desc = pilot_specs[t].desc;
+    }
+
+    int trials_recorded = 0;
+    int abort_triggered = 0;
+
+    for (int t = 0; t < 16; t++) {
+        trials_recorded = t + 1;
         printf("-----------------------------------------------------------------------\n");
         printf("--- [DIAGNOSTIC TRIAL %d/16] %s ---\n", t, pilot_specs[t].desc);
@@ -496,6 +500,7 @@ int main(int argc, char **argv) {
                 records[t].crypto_endpoint = "NOT_RUN";
                 records[t].restoration_status = "UNKNOWN";
                 fprintf(stderr, "ABORT in trial %d: vm_protect(RW) failed with %d\n", t, kr);
+                abort_triggered = 1;
                 break;
             }
             page_is_rw = 1;
@@ -637,6 +642,7 @@ int main(int argc, char **argv) {
             } else {
                 records[t].restoration_status = "RESTORATION_FAILED";
                 fprintf(stderr, "CRITICAL EMERGENCY: Cleanup failed in trial %d. Terminating runner immediately.\n", t);
+                abort_triggered = 1;
                 break;
             }
@@ -656,6 +662,9 @@ int main(int argc, char **argv) {
                 records[t].restoration_status = "RESTORED_AND_BASELINE_RECHECK_PASSED";
             } else {
                 records[t].restoration_status = "RESTORATION_FAILED";
+                fprintf(stderr, "CRITICAL EMERGENCY: Baseline integrity failure in trial %d. Terminating runner immediately.\n", t);
+                abort_triggered = 1;
+                break;
             }
@@ -675,10 +684,14 @@ int main(int argc, char **argv) {
     /* 3. GENERATE AUTHORITATIVE 9-COLUMN TRIAL LEDGER (CSV FORMAT)  */
     /* ------------------------------------------------------------- */
     printf("\n=======================================================================\n");
-    printf(" AUTHORITATIVE TRIAL LEDGER (CSV FORMAT - 9 COLUMNS)\n");
+    if (abort_triggered || trials_recorded < 16) {
+        printf(" PARTIAL TRIAL LEDGER (ABORTED RUN - %d/16 TRIALS RECORDED)\n", trials_recorded);
+    } else {
+        printf(" AUTHORITATIVE TRIAL LEDGER (CSV FORMAT - 9 COLUMNS)\n");
+    }
     printf("=======================================================================\n");
     printf("trial_id,target_idx,bit_mask,mutation_status,consumption_status,crypto_endpoint,restoration_status,output_ss,expected_behavior\n");
-    for (int t = 0; t < 16; t++) {
+    for (int t = 0; t < trials_recorded; t++) {
         char ss_hex[65];
         for (int b = 0; b < 32; b++) {
             sprintf(ss_hex + b * 2, "%02x", records[t].output_ss[b]);
@@ -696,6 +709,12 @@ int main(int argc, char **argv) {
                pilot_specs[t].expected_behavior ? pilot_specs[t].expected_behavior : "UNKNOWN");
     }
 
+    if (abort_triggered || trials_recorded < 16) {
+        printf("\n>>> PILOT RUN ABORTED: INCOMPLETE RUN (%d/16 TRIALS PROCESSED) (STATUS: FAILED) <<<\n", trials_recorded);
+        return 1;
+    }
+
+    printf("\n>>> PILOT RUN COMPLETE: 16/16 TRIALS PROCESSED (STATUS: SUCCESS) <<<\n");
     return 0;
 }
```

---

## 3. Compilation and Validation Records

### 3.1 Compilation
```bash
clang -O3 -Wall -Wextra -std=c11 \
  -I . -I algorithms/source_ref/mlkem \
  research/phase14_persistent_arm_design/pilot_runner.c \
  bin/obj/mlkem768_persistent_reloc.o \
  -o bin/pilot_runner
```
- **Compiler:** Apple clang version 21.0.0 (`clang-2100.1.1.101`, `arm64-apple-darwin27.0.0`)
- **Exit Code:** `0` (Zero compiler warnings).

### 3.2 Non-Mutating Validation (`--check-oracle`)
```bash
./bin/pilot_runner --check-oracle
```
- **Exit Code:** `0`
- **Output:** Verified bit-for-bit match of SHAKE256 empty string KAT and FIPS 203 rejection key derivation.

### 3.3 Binary String Verification
```bash
strings bin/pilot_runner | grep -E "(PILOT RUN COMPLETE|PILOT RUN ABORTED|PARTIAL TRIAL LEDGER)"
```
- **Output:**
```text
 PARTIAL TRIAL LEDGER (ABORTED RUN - %d/16 TRIALS RECORDED)
>>> PILOT RUN ABORTED: INCOMPLETE RUN (%d/16 TRIALS PROCESSED) (STATUS: FAILED) <<<
>>> PILOT RUN COMPLETE: 16/16 TRIALS PROCESSED (STATUS: SUCCESS) <<<
```

---

## 4. Cryptographic Hash Provenance Ledger

| File | SHA-256 Hash |
|:---|:---|
| `research/phase14_persistent_arm_design/pilot_runner.c` | `292e15b63a9d260f6aededc0f86e0ce1b0e6d897a4e44307447d96eaa8f0ebce` |
| `bin/pilot_runner` | `6a671b96ee1869ed1630f7c42f1cdeca8fd16b24467d1e2289a3fdb08bdea9b6` |
| `bin/obj/mlkem768_persistent_reloc.o` | `c239e7cf355404af7eb616c58832a6f6b9fbb9c708f83df46c9e5d01264deb9f` |

---

## 5. Preservation and Governance Adherence

- **Live Pilot Trials Executed:** 0.
- **Twiddle Table Mutations:** 0.
- **Page Protection Changes for Testing:** 0.
- **Production Code Changes:** 0.
- **Historical Phase Artifacts Altered:** 0.
- **Pre-Existing Git Modifications:** Preserved intact.
