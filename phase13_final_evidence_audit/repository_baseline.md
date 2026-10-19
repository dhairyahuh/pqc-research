# Phase 13 Repository Baseline & Build Provenance

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Target:** ML-KEM-768 Native Implementation & Fault Resilience Research Repository  

---

## 1. Git Repository State & Working Tree

- **Repository Origin URL:** `https://github.com/dhairyahuh/pqc-research.git`
- **Active Branch:** `space-resilience-framework`
- **Commit Hash (HEAD):** `ca38dec3b76f54e405a268c3f06a5f04a13e3660`
- **Working-Tree Status:** Dirty (modified tracked files from earlier experiments; untracked audit directories `phase2` through `phase13`)
- **Modified Tracked Files:**
  - `README.md`
  - `experiments/fault_injection/mlkem768_internal_fault_experiment.c`
  - `experiments/system_model/spacecraft_protocol_sim.py`
  - `fault_injection/fault_models/fault_definitions.py`
  - `results/spacecraft_protocol_desync_results.json`
  - `tests/test_fips_kats.c`

---

## 2. Toolchain & Build Environment

- **Host Operating System:** macOS Darwin 27.0.0 (`arm64`)
- **Hardware Architecture:** Apple Silicon (`arm64-apple-darwin27.0.0`)
- **C Compiler:** Apple clang version 21.0.0 (`clang-2100.1.1.101`)
- **Compilation Standard:** `-std=c99` (core algorithms) / `-std=c11` (top-level harnesses)

---

## 3. Production Object Reproducibility Verification

To verify whether the recorded production object files in `bin/obj/` can be reproduced deterministically from the repository source code, the objects were rebuilt using the Makefile configuration and compared byte-for-byte:

```bash
# Rebuild ML-KEM-768 instrumented production object
clang -O3 -std=c99 -I algorithms/source_ref/mlkem \
  -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem768 \
  -DMLK_CONFIG_PARAMETER_SET=768 \
  -DMLKEM_RESEARCH_FAULT_HOOKS \
  -c algorithms/source_ref/mlkem/mlkem_native.c \
  -o /tmp/rebuilt_mlkem768_inst.o

# Rebuild fault hook object
clang -O3 -std=c99 -I algorithms/source_ref/mlkem \
  -DMLKEM_RESEARCH_FAULT_HOOKS \
  -c algorithms/source_ref/mlkem_fault_hooks.c \
  -o /tmp/rebuilt_mlkem_fault_hooks.o
```

### Hash Verification Results:
| Object File | Repository Path | SHA-256 Hash | Rebuilt Object Hash | Verification Result |
| :--- | :--- | :--- | :--- | :---: |
| **ML-KEM-768 Instrumented** | `bin/obj/mlkem768_inst.o` | `7adc428039c318eb0d71b3fc7e24da602010acf7df5e37183ccba5a22eaef65f` | `7adc428039c318eb0d71b3fc7e24da602010acf7df5e37183ccba5a22eaef65f` | **BIT-FOR-BIT MATCH** |
| **Native Fault Hooks** | `bin/obj/mlkem_fault_hooks.o` | `e7a90d06019aeb9e3f8b656e19e719985c797c25f629cb987f9d97f83a5fd952` | `e7a90d06019aeb9e3f8b656e19e719985c797c25f629cb987f9d97f83a5fd952` | **BIT-FOR-BIT MATCH** |

**Conclusion:** The production object files in `bin/obj/` are 100% deterministically reproducible from the source code under Apple clang 21.0.0.

---

## 4. Source File Cryptographic Manifest

| File Category | File Path | Exact SHA-256 Hash |
| :--- | :--- | :--- |
| **Core Aggregation Source** | `algorithms/source_ref/mlkem/mlkem_native.c` | `98c33bcbc5c0a7eeded5722e9f4c8678c58477dd13ae2f097aaf44d25a124afb` |
| **Decapsulation Implementation** | `algorithms/source_ref/mlkem/src/kem.c` | `896df5536d1ec6d540220d99fbfaae345adb9b1bc96f0af601276f2efd8dfc26` |
| **NTT & Butterfly Pipeline** | `algorithms/source_ref/mlkem/src/poly.c` | `f06aa12296c3334cd12bc541a5dc5dcb3b22d9e1844653a5c12d8b7014fec304` |
| **IND-CPA Public Key Encryption**| `algorithms/source_ref/mlkem/src/indcpa.c` | `deec4767a465d71656862d55c26a45775e9bf4328e0837c3cb2e23b6a06ea0ec` |
| **Constant-Time Verification** | `algorithms/source_ref/mlkem/src/verify.c` | `f8f89f1b8c8e5811ce134c0d90fb7828027336afeed231dc3ccb7ee6b73b9335` |
| **Symmetric Macro Header** | `algorithms/source_ref/mlkem/src/symmetric.h` | `168d0ec3bf50bd45cb0a103d7984e9ccf52f78697718b7e85efdf1beda7abc95` |
| **Fault Injection Hook Engine** | `algorithms/source_ref/mlkem_fault_hooks.c` | `624893f5120af442abd9bac3814bac699fbc77cf45667e884ae4959efc60c329` |
| **Fault Injection Hook Header** | `algorithms/source_ref/mlkem_fault_hooks.h` | `685e3221785ec2b887e5d017d478ff82c6d4453507b216aa707d716bf9df77f1` |

---

## 5. Stale Files, Untracked Artifacts, and Discrepancies

1. **Untracked Directories:** The repository contains audit artifacts from prior experimental phases (`phase2_independent_validation/` through `phase12_reproducibility_audit/`), which represent the chronological progression of audits and bug corrections.
2. **Reconciled Historical Discrepancies:**
   - **Phase 8 Narrative Typo:** Phase 8 prose reported 461 H1 events while its data table summed to 561. This clerical typo was rectified in Phase 10.
   - **Phase 9 Target F12 Label:** Phase 9 logged F12 (clean baseline) as `GENUINE_RECOVERY` due to an automated script condition checking `status == 0x5A5A5A5A` without asserting `mismatch == 0`. This was rectified in Phase 10, 11, 12, and 13 to `CLEAN_SUCCESS`.
   - **Phase 10 Oracle Circularity:** Phase 10 used `mlkem768_shake256` from `mlkem768_inst.o` to compute rejection keys. Phase 11, 12, and 13 eliminated this dependency by deploying a standalone clean-room Keccak engine.
