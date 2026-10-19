# Repository and Build Identity Audit

**Auditor:** Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Audit Target:** Repository State, Object Reproducibility, Toolchain, and Compilation Flags  

---

## 1. Repository Status and Commit Metadata

| Parameter | Recorded Value |
| :--- | :--- |
| **Git Commit Hash** | `ca38dec3b76f54e405a268c3f06a5f04a13e3660` |
| **Branch** | `main` |
| **Repository Root** | `/Users/dhairyajain/Desktop/pqc research` |
| **Working Tree Status** | Modified tracked files: `README.md`, `experiments/fault_injection/...`, `tests/test_fips_kats.c`. Uncommitted audit directories preserved: `phase2` through `phase8`. |
| **Preservation Rule** | All artifacts from Phases 1 through 8 are strictly preserved and unmodified. |

---

## 2. Toolchain and Build Environment

| Component | Specification |
| :--- | :--- |
| **Host System** | macOS Darwin 27.0.0 (Apple Silicon ARM64, `Darwin Dhairyas-MacBook-Air.local 27.0.0`) |
| **C Compiler** | Apple clang version 21.0.0 (`clang-2100.1.1.101`) |
| **Target Architecture** | `arm64-apple-darwin27.0.0` |
| **Linker** | Apple cctools / ld64 |
| **C Standards Tested** | ISO C99 (`-std=c99`) and ISO C11 (`-std=c11`) |

---

## 3. Object-File Bit-for-Bit Rebuild Verification

To test whether the precompiled objects used in Phase 8 were genuine artifacts of the current source tree, the auditor independently recompiled both core objects from source and performed cryptographic SHA-256 hash comparisons:

### 3.1 Rebuild Commands
```bash
# 1. Rebuild ML-KEM-768 core instrumented object
clang -O3 -std=c99 \
  -I algorithms/source_ref/mlkem \
  -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem768 \
  -DMLK_CONFIG_PARAMETER_SET=768 \
  -DMLKEM_RESEARCH_FAULT_HOOKS \
  -c algorithms/source_ref/mlkem/mlkem_native.c \
  -o /tmp/obj_rebuild/mlkem768_inst.o

# 2. Rebuild ML-KEM fault hooks and native monitor object
clang -O3 -std=c99 \
  -I algorithms/source_ref/mlkem \
  -DMLKEM_RESEARCH_FAULT_HOOKS \
  -c algorithms/source_ref/mlkem_fault_hooks.c \
  -o /tmp/obj_rebuild/mlkem_fault_hooks.o
```

### 3.2 SHA-256 Hash Comparison

| Object File | Repository Object Hash (`bin/obj/`) | Rebuilt Object Hash (`/tmp/obj_rebuild/`) | Match Status |
| :--- | :--- | :--- | :---: |
| `mlkem768_inst.o` | `7adc428039c318eb0d71b3fc7e24da602010acf7df5e37183ccba5a22eaef65f` | `7adc428039c318eb0d71b3fc7e24da602010acf7df5e37183ccba5a22eaef65f` | **BIT-FOR-BIT IDENTICAL** |
| `mlkem_fault_hooks.o` | `e7a90d06019aeb9e3f8b656e19e719985c797c25f629cb987f9d97f83a5fd952` | `e7a90d06019aeb9e3f8b656e19e719985c797c25f629cb987f9d97f83a5fd952` | **BIT-FOR-BIT IDENTICAL** |

**Auditor Finding:**  
The object files in `bin/obj/` are **100% bit-for-bit reproducible** from the in-tree source files `algorithms/source_ref/mlkem/mlkem_native.c` and `algorithms/source_ref/mlkem_fault_hooks.c`. No undocumented compiler flags, intermediate patches, or binary modifications exist.

---

## 4. Source Files SHA-256 Checksums

| Source File | SHA-256 Checksum | Role in Build |
| :--- | :--- | :--- |
| `algorithms/source_ref/mlkem/mlkem_native.c` | `668615c486333917462fa112a297e596bb05bb062a4f6645367615024467c699` | Single Compilation Unit bundling ML-KEM-768 |
| `algorithms/source_ref/mlkem/src/poly.c` | `f06aa12296c3334cd12bc541a5dc5dcb3b22d9e1844653a5c12d8b7014fec304` | Forward NTT, butterflies, hook calls |
| `algorithms/source_ref/mlkem/src/kem.c` | `896df5536d1ec6d540220d99fbfaae345adb9b1bc96f0af601276f2efd8dfc26` | Decapsulation, FO re-encryption, dual rail |
| `algorithms/source_ref/mlkem/src/indcpa.c` | `deec4767a465d71656862d55c26a45775e9bf4328e0837c3cb2e23b6a06ea0ec` | IND-CPA dec and enc routines |
| `algorithms/source_ref/mlkem_fault_hooks.c` | `624893f5120af442abd9bac3814bac699fbc77cf45667e884ae4959efc60c329` | Production monitor and fault injection hooks |
| `algorithms/source_ref/mlkem_fault_hooks.h` | `d7ea2be278e3575971488f237bf30424fa75e533c3a936a29efbbf6c63a6f19a` | Monitor declarations and API structures |
