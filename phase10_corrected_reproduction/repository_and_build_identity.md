# Repository and Build Identity Audit

**Auditor:** Skeptical Cryptographic Software Verification Researcher  
**Date:** October 2026  
**Scope:** Verification of Source Code, Object Integrity, Toolchain, and Compilation Flags  

---

## 1. Repository State and Version Control Metadata

| Parameter | Recorded Value |
| :--- | :--- |
| **Git Commit Hash** | `ca38dec3b76f54e405a268c3f06a5f04a13e3660` |
| **Branch** | `main` |
| **Repository Root** | `/Users/dhairyajain/Desktop/pqc research` |
| **Working Tree Status** | Tracked modifications in `README.md`, `experiments/fault_injection/...`, `tests/test_fips_kats.c`. Prior audit directories `phase2` through `phase9` strictly preserved. |

---

## 2. Toolchain and Build Configuration

| Component | Specification |
| :--- | :--- |
| **Host System** | macOS Darwin 27.0.0 (Apple Silicon ARM64, `Darwin Dhairyas-MacBook-Air.local 27.0.0`) |
| **Compiler** | Apple clang version 21.0.0 (`clang-2100.1.1.101`) |
| **Target Architecture** | `arm64-apple-darwin27.0.0` |
| **C Language Standards** | ISO C99 (`-std=c99`) for object compilation; ISO C11 (`-std=c11`) for test harnesses |
| **Optimization Level** | `-O3` (with `-Wall -Wextra`) |

---

## 3. Cryptographic Object Integrity & SHA-256 Checksums

The precompiled objects in `bin/obj/` were verified against fresh, independent rebuilds directly from the in-tree source files:

```bash
# Rebuild command for ML-KEM-768 core
clang -O3 -std=c99 -I algorithms/source_ref/mlkem \
  -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem768 -DMLK_CONFIG_PARAMETER_SET=768 \
  -DMLKEM_RESEARCH_FAULT_HOOKS \
  -c algorithms/source_ref/mlkem/mlkem_native.c -o /tmp/obj_rebuild/mlkem768_inst.o

# Rebuild command for fault hooks and native monitor
clang -O3 -std=c99 -I algorithms/source_ref/mlkem \
  -DMLKEM_RESEARCH_FAULT_HOOKS \
  -c algorithms/source_ref/mlkem_fault_hooks.c -o /tmp/obj_rebuild/mlkem_fault_hooks.o
```

### Checksum Verification Table:
| Object File | Repository Path | Rebuilt Path | SHA-256 Hash | Verification Status |
| :--- | :--- | :--- | :--- | :---: |
| `mlkem768_inst.o` | `bin/obj/mlkem768_inst.o` | `/tmp/obj_rebuild/mlkem768_inst.o` | `7adc428039c318eb0d71b3fc7e24da602010acf7df5e37183ccba5a22eaef65f` | **BIT-FOR-BIT IDENTICAL** |
| `mlkem_fault_hooks.o` | `bin/obj/mlkem_fault_hooks.o` | `/tmp/obj_rebuild/mlkem_fault_hooks.o` | `e7a90d06019aeb9e3f8b656e19e719985c797c25f629cb987f9d97f83a5fd952` | **BIT-FOR-BIT IDENTICAL** |

---

## 4. Key Implementation Files and Functional Mapping

| Functionality | Implementation Source File | Primary Functions / Symbols |
| :--- | :--- | :--- |
| **Fault Arming & Config** | [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) | `mlkem_fault_arm_mid_ntt_locus`, `mlkem_fault_reset` |
| **Butterfly Fault Hooks** | [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) | `hook_mid_ntt_post_mul`, `apply_fault` |
| **Native NTT Monitor & Recovery**| [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) | `native_ntt_monitor_butterfly`, `ntt_native_monitor_configure` |
| **Forward NTT Butterfly Loop** | [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c) | `mlk_ntt_butterfly_block`, `mlk_ntt_layer` |
| **FO Re-encryption & Verification**| [`algorithms/source_ref/mlkem/src/kem.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c) | `mlk_kem_dec_monitored`, `mlk_ct_memcmp` |
| **Constant-Time Output Selection**| [`algorithms/source_ref/mlkem/src/kem.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c) | `mlk_ct_cmov_zero`, `mlk_hash_j` |
| **Rejection Key Generation** | [`algorithms/source_ref/mlkem/src/fips202/fips202.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/fips202/fips202.c) | `mlkem768_shake256` |
