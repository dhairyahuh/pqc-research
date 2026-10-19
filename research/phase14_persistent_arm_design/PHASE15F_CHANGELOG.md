# Phase 15F Changelog: Provenance Reconciliation and Harness Consistency

**Date:** 2026-10-11  
**Author:** Skeptical Cryptographic Research Engineer  
**Context:** Phase 15F Provenance Reconciliation, Sentinel Hardening, and Schema Alignment  
**Git Branch:** `space-resilience-framework` (HEAD: `4a2c4ebf9274a9188db3610a4f8448902caed056`)  

---

## 1. Summary of Actions Taken

This changelog records all actions taken during Phase 15F to resolve the outstanding findings from the Phase 15E Independent Audit:

1. **Hash Provenance Reconciliation (Task 1 / F-15E-10):**
   - Independently computed SHA-256 digests for all artifacts listed in Phase 15D.
   - Identified and explained the transcription discrepancy in `PHASE15D_REPORT.md` regarding historical artifacts `PHASE15B_REPORT.md` (`0a530225...`) and `PHASE15B_TRIAL_LEDGER.csv` (`5cf48fb9...`).
   - Created `research/phase14_persistent_arm_design/PHASE15F_ERRATA.md` to formally document the reconciliation without altering historical reports in place.
2. **Sentinel Index Validation Hardening (Task 2 / F-15E-08):**
   - Inspected `pilot_runner.c` trial-selection logic.
   - Replaced permissive negative check with strict sentinel validation:
     ```c
     if (pilot_specs[t].target_idx < -1 || pilot_specs[t].target_idx >= 128) {
         /* Fails closed immediately without changing VM protections or table contents */
     }
     ```
   - Explicitly defined `int is_baseline = (pilot_specs[t].target_idx == -1);`.
   - Prevented any negative index other than `-1` from being executed as an unmutated baseline trial.
3. **Authoritative 9-Column Trial Ledger Schema (Task 3 / F-15E-09):**
   - Added `const char *expected_behavior;` to `trial_spec_t` and populated all 16 rows of `pilot_specs` with the exact historical strings.
   - Refactored the summary output loop to emit the authoritative 9-column CSV ledger matching `PHASE15B_TRIAL_LEDGER.csv`:
     `trial_id,target_idx,bit_mask,mutation_status,consumption_status,crypto_endpoint,restoration_status,output_ss,expected_behavior`
   - Explicitly labeled per-trial loop output as `[DIAGNOSTIC TRIAL %d/16]`, cleanly separating verbose execution logs from the authoritative 9-column CSV schema.
4. **Preservation of Repository & Artifacts:**
   - Preserved all historical artifacts (`PHASE15A` through `PHASE15E`) byte-for-byte.
   - Preserved all 7 pre-existing tracked modifications in Git without staging or committing.
   - Executed zero live mutation trials and invoked zero `vm_protect` calls for experiment execution.

---

## 2. Modified and Created Files

### Created Files:
1. `research/phase14_persistent_arm_design/PHASE15F_ERRATA.md`:
   Authoritative hash reconciliation and provenance errata document.
2. `research/phase14_persistent_arm_design/PHASE15F_CHANGELOG.md`:
   This changelog document.

### Modified Files:
1. `research/phase14_persistent_arm_design/pilot_runner.c`:
   - Lines 218–242: Added `expected_behavior` field to `trial_spec_t` and populated `pilot_specs[16]`.
   - Lines 466–480: Enforced `target_idx < -1 || target_idx >= 128` fail-closed bounds checking; defined `is_baseline = (target_idx == -1)`.
   - Lines 645–672: Routed unmutated path strictly through `else if (is_baseline)`, with defensive fail-closed `else`.
   - Lines 678–696: Emitted authoritative 9-column CSV header and rows matching `PHASE15B_TRIAL_LEDGER.csv`.
2. `bin/pilot_runner`:
   Recompiled research binary incorporating the sentinel and schema fixes.

---

## 3. Execution Commands and Validation Records

### 3.1 Compilation (Static Build Verification)
```bash
clang -O3 -Wall -Wextra -std=c11 \
  -I . -I algorithms/source_ref/mlkem \
  research/phase14_persistent_arm_design/pilot_runner.c \
  bin/obj/mlkem768_persistent_reloc.o \
  -o bin/pilot_runner
```
**Observation:** Exited with code 0; zero compiler warnings.

### 3.2 Non-Mutating Oracle Validation (`--check-oracle`)
```bash
./bin/pilot_runner --check-oracle
```
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
**Observation:** Validated independent FIPS 202 / FIPS 203 derivation in non-mutating mode. Zero memory mutations were attempted.

---

## 4. Reconciliation of Phase 15E Findings Matrix

Without altering historical findings in `PHASE15E_FINDINGS_MATRIX.md`, the resolution status of each item is recorded below:

| Finding ID | Phase 15E Status | Phase 15F Resolution Action | Status Post-Phase 15F |
|:---:|:---:|:---|:---:|
| **F-15E-06** | PASS (LOW) | Documented in `PHASE15E_AUDIT.md` that trap handlers exit with status $128 + \text{sig}$ (138/139), cleanly tearing down the process space. | **RESOLVED / ACKNOWLEDGED** |
| **F-15E-08** | PASS (LOW) | Enforced `target_idx < -1 \|\| target_idx >= 128` fail-closed check; restricted baseline execution strictly to `target_idx == -1`. | **RESOLVED IN CODE** |
| **F-15E-09** | PASS (LOW) | Added `expected_behavior` column to runner summary loop; output schema now matches historical 9-column format. | **RESOLVED IN CODE** |
| **F-15E-10** | FAIL (MEDIUM) | Authored `PHASE15F_ERRATA.md` documenting recomputed digests for `PHASE15B_REPORT.md` (`0a530225...`) and `PHASE15B_TRIAL_LEDGER.csv` (`5cf48fb9...`). | **RESOLVED IN ERRATA** |

---

## 5. Authoritative Artifact SHA-256 Ledger (Phase 15F)

```text
ea253b5bbde2406f3d93061e2e1652e78ba8b3f68c66cf7a774d29f59b18d95d  research/phase14_persistent_arm_design/pilot_runner.c
bbddee21f2d6bbcd44a972da0a7c5b0450f77dc1812b06d70172ae1bc9f352ba  research/phase14_persistent_arm_design/pilot_runner.c.phase15b_bak
8de41e4a7631535d60b1d8b193f518098870b4cf230481aaf0d5fda5f0c03afd  bin/pilot_runner
c239e7cf355404af7eb616c58832a6f6b9fbb9c708f83df46c9e5d01264deb9f  bin/obj/mlkem768_persistent_reloc.o
01ae1714be2db8d593ddf7a993ebba48b3daffddc8baf6bc41bec65aa76ad8cf  bin/test_fips_kats_research
c625b7afdfb311ce0ffbd5da024a54b8f978a7d2f21e2f05e5fb637f04987981  research/phase14_persistent_arm_design/PHASE15A_REPORT.md
0a5302256db2e5b3f70df1820e21f15ac509fa07e1044d02d6a0dda727554e37  research/phase14_persistent_arm_design/PHASE15B_REPORT.md
5cf48fb9ab869cff6345eb1b8d03785ec65d3ab1c2ee76cab29d4ea6bde45d2c  research/phase14_persistent_arm_design/PHASE15B_TRIAL_LEDGER.csv
271f026dc8e8a1ea1802b239c2c162a1d54fa3fa3995b44794a3f7689384cd58  research/phase14_persistent_arm_design/PHASE15C_AUDIT.md
015f8257ca21ea1a103febe93e0d3332a784e0137e1530a0c5e586cf332ff802  research/phase14_persistent_arm_design/PHASE15C_EVIDENCE_MATRIX.md
d7aa35ee06f3e60124671603113f269bd1cf990c5070d9284746bf07bff6cd02  research/phase14_persistent_arm_design/PHASE15D_REPORT.md
accb7e1a4d852b6210e5efcc347b03958d07f631262db9b70ce8d1fe6cce759b  research/phase14_persistent_arm_design/PHASE15D_CHANGELOG.md
18d63baeeca5d6e1c00c08eccb98c06f48d1e5047f7a8868d8aee235d86adc8f  research/phase14_persistent_arm_design/PHASE15E_AUDIT.md
ba26f2257ff0dde4eee14b428a8e6b35ed94af48e9d0eb7e0b49151aeae6bdfe  research/phase14_persistent_arm_design/PHASE15E_FINDINGS_MATRIX.md
```

---

## Final Recommendation

### **READY FOR SEPARATE READ-ONLY REVIEW**

**Rationale:**  
All four items from Phase 15E are fully reconciled:
1. Hash provenance discrepancies are explicitly documented in `PHASE15F_ERRATA.md`.
2. Target index sentinel validation strictly enforces `target_idx == -1` for baseline and rejects `target_idx < -1 || target_idx >= 128`.
3. The runner's summary ledger emits the authoritative 9-column CSV schema matching `PHASE15B_TRIAL_LEDGER.csv`.
4. Diagnostic stdout is cleanly separated from the authoritative ledger format.

*Mandatory Stop Condition: Phase 16 campaign execution remains unauthorized. No live mutation trials or expanded sweeps may proceed without a separate review and approval.*
