# Environment and Build Manifest

**Auditor:** Skeptical Cryptographic Implementation Auditor  
**Date:** October 2026  
**Target:** ML-KEM-768 Native Implementation & Fault Resilience Research Repository  

---

## 1. Repository and Working-Tree State

- **Repository Origin URL:** `https://github.com/dhairyahuh/pqc-research.git`
- **Active Branch:** `space-resilience-framework`
- **Commit Hash (HEAD):** `ca38dec3b76f54e405a268c3f06a5f04a13e3660`
- **Working-Tree Status:** Dirty (active audit and verification directories: `phase10_corrected_reproduction/`, `phase11_conformance_audit/`, `phase12_reproducibility_audit/`)
- **Host Operating System:** macOS Darwin 27.0.0 (`arm64`)
- **Host Architecture:** Apple Silicon (`arm64-apple-darwin27.0.0`)
- **System Compiler:** Apple clang version 21.0.0 (`clang-2100.1.1.101`)

---

## 2. Compilation and Toolchain Manifest

### 2.1 Production Compilation Commands and Flags
The authentic production object files evaluated throughout this audit were built using the following commands:

```bash
# ML-KEM-768 Instrumented Production Object
clang -O3 -fPIC -Wall -Wextra -I. \
  -DMLKEM_RESEARCH_FAULT_HOOKS \
  -DMLK_CONFIG_PARAMETER_SET=768 \
  -c algorithms/source_ref/mlkem/src/kem.c \
  -o bin/obj/mlkem768_inst.o

# Native Monitor and Mid-NTT Fault Hook Library
clang -O3 -fPIC -Wall -Wextra -I. \
  -c algorithms/source_ref/mlkem_fault_hooks.c \
  -o bin/obj/mlkem_fault_hooks.o
```

### 2.2 Phase 12 Independent Reproducer Build Commands
```bash
# Phase 12 Clean-Room Oracle Boundary Verification
clang -O2 -Wall -Wextra \
  phase12_reproducibility_audit/verify_oracle.c \
  -o phase12_reproducibility_audit/verify_oracle

# Phase 12 Production Reproducer Harness
clang -O2 -Wall -Wextra -I. \
  phase12_reproducibility_audit/production_reproducer.c \
  bin/obj/mlkem768_inst.o \
  bin/obj/mlkem_fault_hooks.o \
  -o phase12_reproducibility_audit/production_reproducer
```

---

## 3. Cryptographic Hashes of Source and Object Files

| File Category | Path | Exact SHA-256 Hash |
| :--- | :--- | :--- |
| **Production Source** | `algorithms/source_ref/mlkem/src/kem.c` | `896df5536d1ec6d540220d99fbfaae345adb9b1bc96f0af601276f2efd8dfc26` |
| **Production Source** | `algorithms/source_ref/mlkem/src/poly.c` | `f06aa12296c3334cd12bc541a5dc5dcb3b22d9e1844653a5c12d8b7014fec304` |
| **Production Header** | `algorithms/source_ref/mlkem/src/symmetric.h` | `168d0ec3bf50bd45cb0a103d7984e9ccf52f78697718b7e85efdf1beda7abc95` |
| **Hook Source** | `algorithms/source_ref/mlkem_fault_hooks.c` | `624893f5120af442abd9bac3814bac699fbc77cf45667e884ae4959efc60c329` |
| **Hook Header** | `algorithms/source_ref/mlkem_fault_hooks.h` | `685e3221785ec2b887e5d017d478ff82c6d4453507b216aa707d716bf9df77f1` |
| **Production Object** | `bin/obj/mlkem768_inst.o` | `7adc428039c318eb0d71b3fc7e24da602010acf7df5e37183ccba5a22eaef65f` |
| **Production Object** | `bin/obj/mlkem_fault_hooks.o` | `e7a90d06019aeb9e3f8b656e19e719985c797c25f629cb987f9d97f83a5fd952` |
| **Phase 10 Harness** | `phase10_corrected_reproduction/corrected_production_reproducer.c` | `d030133ce3c00681a3f31e0da3b29ad9271790580091d1a530f5d9bbcfebedd6` |
| **Phase 11 Oracle** | `phase11_conformance_audit/independent_output_oracle.c` | `e4519ff94116f73f9485dc3dae01cd167c260a838f908e9955194c239920a266` |
| **Phase 12 Harness** | `phase12_reproducibility_audit/production_reproducer.c` | `cf6dcdd93c0bc5f9a2b7201c107be61b24cb912ba4e6b12a838561d2d31e9c56` |
| **Phase 12 Oracle** | `phase12_reproducibility_audit/verify_oracle.c` | `6d68b92b67f1396a84d28fe78df49cf7778b3e817eb664656fa98cba46522c09` |

---

## 4. Historical vs. Newly Reproduced Results

To ensure rigorous transparency, all results in this audit are explicitly partitioned into two temporal categories:

1. **Historical Datasets (Phases 5–9):**  
   - Generated during prior developmental iterations.
   - Evaluated both production objects and custom harness simulation logic (e.g. simulating snapshot buffer corruption via in-memory pointers).
   - Preserved verbatim in `phase5_recovery_trust_audit/`, `phase6_verifier_falsification/`, `phase7_independent_claim_audit/`, `phase8_production_path_audit/`, and `phase9_reproducibility_audit/`.
2. **Newly Reproduced Execution Results (Phases 10–12):**  
   - Executed against the immutable compiled objects `bin/obj/mlkem768_inst.o` and `bin/obj/mlkem_fault_hooks.o`.
   - Verified against the clean-room Keccak-f[1600] independent output oracle.
   - Re-executed in Phase 12 clean state and logged in `phase12_reproducibility_audit/production_reproduction_trials.csv`.
