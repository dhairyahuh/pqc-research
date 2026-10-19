# Phase 8: Production Monitor Path Verification and Harness Validity Audit

**Status:** Completed  
**Auditor:** Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Audit Directory:** [`phase8_production_path_audit/`](file:///Users/dhairyajain/Desktop/pqc%20research/phase8_production_path_audit)  

---

## 1. Overview and Core Findings

Phase 8 was commissioned to determine whether Phase 7 exercised the actual production monitor implementation or a reimplementation inside the harness, verify the independent oracle, and audit C arithmetic, compiler behavior, and the F2 stage outcome explanation.

### Key Audit Findings:
1. **Harness Substitution Identified:**  
   The Phase 7 harness linked directly against `bin/obj/mlkem768_inst.o` but **omitted `bin/obj/mlkem_fault_hooks.o`**. The native monitor function `native_ntt_monitor_butterfly` was reimplemented within `genuine_phase7_audit_harness.c`.
2. **Reason for Substitution:**  
   In the in-tree production source (`algorithms/source_ref/mlkem_fault_hooks.c`), `u_saved` is passed as a value on the stack. There is no hook in production to perturb `u_saved`, force `persistent_count = 0`, or simulate DSPC. The harness reimplementation was necessary to construct these internal fault models.
3. **Reproduction on Authentic Production Objects:**  
   When `bin/obj/mlkem768_inst.o` is linked with the authentic `bin/obj/mlkem_fault_hooks.o`, the production monitor:
   - Successfully recovers transient butterfly faults ($100\%$ genuine recovery).
   - Safely rejects persistent stuck-at faults ($100\%$ fail-stop rejection via implicit rejection).
4. **Oracle Independence Validated:**  
   The 3D multi-polynomial reference oracle (`g_ref_butterflies[6][8][128]`) is completely independent of the monitor and eliminates the Phase 6 collision bug.
5. **C Arithmetic Formally Verified:**  
   The 98.0% pass rate in Target F1 is an exact algebraic consequence of two's-complement arithmetic cancellation combined with bit 15 sign concordance. It is 100% invariant across compiler optimization levels (`-O0` to `-Os`).
6. **F2 Stage Outcome Causal Explanation Confirmed:**  
   Direct empirical measurements confirm that Stages 1 & 2 diffuse the $+100$ bias below the 10-bit compression quantization threshold, yielding genuine recovery ($30\%$), while Stages 3–7 exceed the threshold, triggering safe FO rejection ($70\%$).

---

## 2. Directory Manifest and Deliverables

| Deliverable | Purpose | File Link |
| :--- | :--- | :--- |
| **1. Production Code Path** | Complete decapsulation call graph, source trace, and compilation topology. | [`production_code_path.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase8_production_path_audit/production_code_path.md) |
| **2. Harness vs Production Diff** | Line-by-line differential between production monitor and harness reimplementation. | [`harness_vs_production_diff.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase8_production_path_audit/harness_vs_production_diff.md) |
| **3. Binary & Build Identity** | Hashes, compiler identity, optimization flags, and symbol linkage. | [`binary_and_build_identity.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase8_production_path_audit/binary_and_build_identity.md) |
| **4. Actual Monitor Reproduction** | Empirical execution linking authentic `mlkem_fault_hooks.o` with `mlkem768_inst.o`. | [`actual_monitor_reproduction.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase8_production_path_audit/actual_monitor_reproduction.md) |
| **5. Oracle Independence Audit** | Verification of multi-polynomial indexing and Phase 6 collision root cause. | [`oracle_independence_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase8_production_path_audit/oracle_independence_audit.md) |
| **6. C Arithmetic & Compiler Audit** | ISO C integer promotion, narrowing conversions, and optimization invariance. | [`c_arithmetic_and_compiler_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase8_production_path_audit/c_arithmetic_and_compiler_audit.md) |
| **7. F2 Causal Explanation Audit** | Direct empirical measurements of coefficient diffusion, message bits, and FO ciphertext match. | [`f2_causal_explanation_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase8_production_path_audit/f2_causal_explanation_audit.md) |
| **8. Revised H1 and H2 Results** | Rigorous decoupled hypothesis definitions and master 1,200-trial results matrix. | [`revised_h1_h2_results.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase8_production_path_audit/revised_h1_h2_results.md) |
| **9. Phase 7 Claim Revision** | Reassessment of Phase 7 claims, defining exact defensible scientific boundaries. | [`phase7_claim_revision.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase8_production_path_audit/phase7_claim_revision.md) |
| **10. Audit README** | Executive summary, directory manifest, and reproduction instructions (this file). | [`README.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase8_production_path_audit/README.md) |

---

## 3. Reproduction Instructions

### 3.1 Verify Production Monitor Linkage
To execute the authentic production monitor compiled in `bin/obj/mlkem_fault_hooks.o`:
```bash
clang -O3 -std=c11 -I. -I algorithms/source_ref/mlkem \
  phase8_production_path_audit/test_diag_recomputed.c \
  bin/obj/mlkem768_inst.o bin/obj/mlkem_fault_hooks.o \
  -o bin/phase8_production_test

./bin/phase8_production_test
```

### 3.2 Verify Compiler Invariance for F1 Arithmetic
To test recovery verifier arithmetic across optimization levels (`-O0` to `-Os`):
```bash
for opt in -O0 -O1 -O2 -O3 -Os; do
    clang $opt phase8_production_path_audit/test_compiler_sensitivity.c -o test_comp_$opt
    ./test_comp_$opt
done
```

### 3.3 Verify F2 Diffusion & FO Ciphertext Matching
To reproduce the stage-dependent FO rejection trace:
```bash
clang -O3 -std=c11 -I. -I algorithms/source_ref/mlkem \
  phase8_production_path_audit/check_ct_tmp.c \
  bin/obj/mlkem768_inst.o \
  -o bin/check_ct_tmp

./bin/check_ct_tmp
```
