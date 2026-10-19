# Phase 8: Binary and Build Identity Audit

**Auditor:** Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Target:** Cryptographic Objects, Compilers, Optimization Flags, and Symbol Linkage  

---

## 1. System and Compiler Environment

| Property | Measured Value |
| :--- | :--- |
| **Operating System** | macOS Darwin 27.0.0 (Kernel: `Darwin Kernel Version 27.0.0: Tue Aug 11 21:05:27 PDT 2026; root:xnu-13432.1.9~1/RELEASE_ARM64_T8103`) |
| **Host Architecture** | Apple Silicon ARM64 (`aarch64`) |
| **Primary Compiler** | Apple clang version 21.0.0 (`clang-2100.1.1.101`) |
| **Target Triple** | `arm64-apple-darwin27.0.0` |
| **Thread Model** | `posix` |
| **Installed Directory**| `/Library/Developer/CommandLineTools/usr/bin` |

---

## 2. Cryptographic Object Files & Hashes

The audit examined all object files in `bin/obj/` and their corresponding source files:

| Artifact Path | SHA-256 Checksum | Description |
| :--- | :--- | :--- |
| `bin/obj/mlkem768_inst.o` | `7adc428039c318eb0d71b3fc7e24da602010acf7df5e37183ccba5a22eaef65f` | Instrumented ML-KEM-768 core compiled from `mlkem_native.c` |
| `bin/obj/mlkem_fault_hooks.o` | `e7a90d06019aeb9e3f8b656e19e719985c797c25f629cb987f9d97f83a5fd952` | Production fault hooks & native monitor compiled from `mlkem_fault_hooks.c` |
| `algorithms/source_ref/mlkem_fault_hooks.c` | `624893f5120af442abd9bac3814bac699fbc77cf45667e884ae4959efc60c329` | Production monitor and research fault hook source |
| `algorithms/source_ref/mlkem_fault_hooks.h` | `d7ea2be278e3575971488f237bf30424fa75e533c3a936a29efbbf6c63a6f19a` | Header definitions for fault hooks and native monitor |
| `algorithms/source_ref/mlkem/src/poly.c` | `f06aa12296c3334cd12bc541a5dc5dcb3b22d9e1844653a5c12d8b7014fec304` | In-tree polynomial NTT and butterfly routines |
| `algorithms/source_ref/mlkem/src/kem.c` | `896df5536d1ec6d540220d99fbfaae345adb9b1bc96f0af601276f2efd8dfc26` | In-tree ML-KEM decapsulation and FO verification |
| `algorithms/source_ref/mlkem/src/indcpa.c` | `deec4767a465d71656862d55c26a45775e9bf4328e0837c3cb2e23b6a06ea0ec` | In-tree IND-CPA encryption, decryption, and keygen |
| `phase7_independent_claim_audit/genuine_phase7_audit_harness.c` | `73af81fd7e3a1fa5ad3d0d6a44fe19d5b2006d99a4db36683ff999bd1683a169` | Phase 7 standalone audit harness |

---

## 3. Symbol Inspection (`nm -g`)

### 3.1 Symbols in `bin/obj/mlkem768_inst.o`
Inspection of `nm -g bin/obj/mlkem768_inst.o` reveals which symbols are defined by the cryptographic core versus imported:

```text
000000000001023c T _mlkem768_dec
000000000000f27c T _mlkem768_dec_monitored
000000000000a66c T _mlkem768_indcpa_dec
00000000000007a0 T _mlkem768_poly_decompress_d10
00000000000003d8 T _mlkem768_poly_decompress_d4
0000000000009c18 T _mlkem768_poly_invntt_tomont
0000000000010e88 T _mlkem768_poly_ntt
0000000000011230 T _mlkem768_polyvec_decompress_du
0000000000009bec T _mlkem768_polyvec_invntt_tomont
0000000000005560 T _mlkem768_polyvec_ntt
                 U _hook_decaps_verify_flag
                 U _hook_mid_invntt_butterfly
                 U _hook_mid_invntt_post_diff
                 U _hook_mid_invntt_pre_butterfly
                 U _hook_mid_ntt_butterfly
                 U _hook_mid_ntt_layer_end
                 U _hook_mid_ntt_post_mul
                 U _hook_mid_ntt_pre_butterfly
                 U _hook_post_ntt_coefficient
                 U _invntt_native_monitor_get_persistent_count
                 U _native_invntt_monitor_butterfly
                 U _native_ntt_monitor_butterfly
                 U _ntt_native_monitor_get_persistent_count
```

**Key Takeaway:**  
The native monitor routines `_native_ntt_monitor_butterfly` and `_ntt_native_monitor_get_persistent_count` are **undefined (`U`)** in `bin/obj/mlkem768_inst.o`. They are expected to be supplied at link time.

### 3.2 Symbols in `bin/obj/mlkem_fault_hooks.o`
Inspection of `nm -g bin/obj/mlkem_fault_hooks.o`:

```text
0000000000002a50 D _g_invntt_native_monitor
0000000000002a28 D _g_ntt_native_monitor
00000000000015bc T _hook_decaps_verify_flag
0000000000002170 T _hook_mid_invntt_butterfly
000000000000203c T _hook_mid_invntt_post_diff
0000000000001d9c T _hook_mid_invntt_pre_butterfly
00000000000009f0 T _hook_mid_ntt_butterfly
0000000000000c2c T _hook_mid_ntt_layer_end
000000000000083c T _hook_mid_ntt_post_mul
0000000000000590 T _hook_mid_ntt_pre_butterfly
000000000000168c T _hook_post_ntt_coefficient
0000000000001d60 T _invntt_native_monitor_configure
0000000000001d90 T _invntt_native_monitor_get_persistent_count
0000000000001d3c T _invntt_native_monitor_reset
0000000000000048 T _mlkem_fault_arm_mid_ntt
0000000000000110 T _mlkem_fault_arm_mid_ntt_locus
00000000000023c8 T _native_invntt_monitor_butterfly
0000000000001b30 T _native_ntt_monitor_butterfly
0000000000001af4 T _ntt_native_monitor_configure
0000000000001b24 T _ntt_native_monitor_get_persistent_count
0000000000001ad0 T _ntt_native_monitor_reset
```

**Key Takeaway:**  
`bin/obj/mlkem_fault_hooks.o` provides the canonical production definitions of `_native_ntt_monitor_butterfly` and `_ntt_native_monitor_get_persistent_count`.

---

## 4. Linkage Comparison: Phase 7 Harness vs Production Build

### Phase 7 Build Command:
```bash
clang -O3 -Wall -Wextra -std=c11 \
  -I. -I algorithms/source_ref/mlkem \
  phase7_independent_claim_audit/genuine_phase7_audit_harness.c \
  bin/obj/mlkem768_inst.o \
  -o bin/phase7_audit_harness
```
*Note that `bin/obj/mlkem_fault_hooks.o` was completely omitted from the link command!*  
The symbol `_native_ntt_monitor_butterfly` was resolved by the harness's own local function `native_ntt_monitor_butterfly` defined in `genuine_phase7_audit_harness.c:161-327`.

### True Production Build Command:
```bash
clang -O3 -Wall -Wextra -std=c11 \
  -I. -I algorithms/source_ref/mlkem \
  production_test.c \
  bin/obj/mlkem768_inst.o \
  bin/obj/mlkem_fault_hooks.o \
  -o bin/production_test
```
In this build, `_native_ntt_monitor_butterfly` is resolved by the compiled object `bin/obj/mlkem_fault_hooks.o`.

---

## 5. Verification Conclusion

1. The cryptographic core (`bin/obj/mlkem768_inst.o`) used in Phase 7 is the authentic, compiled in-tree ML-KEM-768 library.
2. The monitor and recovery path (`native_ntt_monitor_butterfly`) used in Phase 7 was **NOT** linked from `bin/obj/mlkem_fault_hooks.o`. It was defined directly inside `genuine_phase7_audit_harness.c`.
3. Consequently, all results in Phase 5, Phase 6, and Phase 7 that evaluate internal recovery verifier blindness exercised a **reimplementation of the monitor logic inside the test harness**, rather than the object code in `bin/obj/mlkem_fault_hooks.o`.
