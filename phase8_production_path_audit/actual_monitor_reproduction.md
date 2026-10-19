# Actual Monitor Reproduction and Production Path Audit

**Auditor:** Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Binary Target:** `bin/obj/mlkem768_inst.o` linked with `bin/obj/mlkem_fault_hooks.o`  
**Test Harness:** [`phase8_production_path_audit/test_production_link.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase8_production_path_audit/test_production_link.c) and [`test_diag_recomputed.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase8_production_path_audit/test_diag_recomputed.c)  

---

## 1. Executive Summary

To satisfy the primary audit requirement of Phase 8 ("*establish whether the tests exercised the actual production monitor implementation or a reimplementation inside the harness*"), we built and executed a test suite linking directly against the compiled production objects:
```bash
clang -O3 -std=c11 -I. -I algorithms/source_ref/mlkem \
  phase8_production_path_audit/test_diag_recomputed.c \
  bin/obj/mlkem768_inst.o bin/obj/mlkem_fault_hooks.o \
  -o bin/phase8_production_test
```
In this binary:
- **No monitor functions are mocked or overridden.**
- `native_ntt_monitor_butterfly` executes from `bin/obj/mlkem_fault_hooks.o`.
- `mlkem768_dec_monitored` executes from `bin/obj/mlkem768_inst.o`.
- Faults are configured using the official in-tree hook API (`mlkem_fault_arm_mid_ntt_locus`).

---

## 2. Reproduction Results on Actual Production Objects

### 2.1 Baseline Clean Execution
- **Configuration:** `ntt_native_monitor_configure(NTT_NATIVE_MONITOR_RECOMPUTED_T, true, 0x7F)`
- **Executed Butterflies:** 5,376 (896 butterflies $\times$ 6 polynomials during FO re-encryption)
- **Mismatches:** 0
- **Recoveries:** 0
- **Persistent:** 0
- **Decapsulation Status:** `0x5A5A5A5A` (`MLK_DECAPS_STATUS_SUCCESS`)
- **Shared Secret:** Exact bitwise match with encapsulation shared secret.

### 2.2 Transient Butterfly Fault (Intermediate $t$ Bitflip)
- **Injection:** `mlkem_fault_arm_mid_ntt_locus(1, 10, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, 0, 0, 0)`
- **Persistence:** `g_mlkem_fault.persistent = false` (transient single-event upset during butterfly multiplication).
- **Execution Log:**
```text
Recomputed T (Transient fault):
After dec: rc=0, status=0x5A5A5A5A (0x5A5A5A5A=SUCCESS, 0xA5A5A5A5=REJECT, 0xFFFFFFFF=FAULT)
Monitor stats: executed=5376, mismatch=1, retry_attempts=1, recovered=1, persistent=0
Shared secret match: YES (GENUINE RECOVERY)
```
- **Audit Findings:**
  1. The production monitor successfully detected the invariant violation (`mismatch=1`).
  2. The production monitor rolled back operands `*r_j = u_saved; *r_j_len = v_saved;`.
  3. The production monitor independently recomputed $t_{\text{retry}}$ and successfully recovered the butterfly (`recovered=1, persistent=0`).
  4. The outer decapsulation procedure completed with `0x5A5A5A5A`, returning the genuine shared secret.
  5. **This independently reproduces genuine recovery on the authentic production monitor path.**

### 2.3 Persistent Butterfly Fault (Stuck-At Bitflip)
- **Injection:** Same butterfly locus with `g_mlkem_fault.persistent = true`.
- **Execution Log:**
```text
Recomputed T (Persistent fault):
After dec: rc=0, status=0xFFFFFFFF
Monitor stats: executed=5376, mismatch=6, retry_attempts=6, recovered=0, persistent=6
Shared secret match: NO (IMPLICIT REJECTION)
```
- **Audit Findings:**
  1. During retry, the persistent fault re-corrupted the recomputed butterfly (`mlkem_fault_hooks.c:646`).
  2. The recovery verifier detected that $diff_{\text{retry}} \ne 0 \lor sum_{\text{retry}} \ne 0$, incrementing `persistent_count`.
  3. Decapsulation checked `ntt_native_monitor_get_persistent_count() > 0` (`kem.c:486`), forced `fail = 0xFF`, and set status to `0xFFFFFFFF` (`MLK_DECAPS_STATUS_FAULT`).
  4. Constant-time conditional move returned $K_{\text{rej}} = \text{SHAKE256}(z \parallel ct)$.
  5. **This independently reproduces safe fail-stop rejection on the authentic production monitor path.**

---

## 3. Scope and Limitations: What Cannot Be Tested on `mlkem_fault_hooks.o`

While the authentic production binary reproduces clean execution, transient recovery, and persistent fail-stop, **it cannot natively execute the fault models investigated in Targets F1, F2, F3, F6, F8, F9, F10, F11**.

### Why?
1. **Pass-by-Value Encapsulation of `u_saved`:**  
   In `poly.c:408`, `u_saved` is passed as a 16-bit integer value on the stack. In `mlkem_fault_hooks.c:600`, `u_saved` is a local argument. The production hook interface provides hooks into intermediate pointers (`&t`, `&zeta`, `&r[j]`), but provides **no hook to perturb `u_saved`**.
2. **Post-Detection Snapshot Corruption (F2):**  
   There is no hook between the detection of an invariant mismatch and the assignment `*r_j = u_saved` in `mlkem_fault_hooks.c:635`.
3. **Absence of DSPC in Repository:**  
   The in-tree library contains no parity checksums or snapshot tokens. DSPC exists solely in experimental test scripts.
4. **State/Control Overrides (F3, F4, F6):**  
   The production monitor provides no hook to force `persistent_count = 0` or override `diff_retry = 0`.

---

## 4. Auditor Conclusion

- **Genuine Production Findings:**  
  Transient recovery (F4 behavior) and persistent fault rejection (F5 behavior) are **empirically reproduced on the actual compiled production objects** (`bin/obj/mlkem768_inst.o` + `bin/obj/mlkem_fault_hooks.o`).
- **Constructed Harness Models:**  
  Target F1 (saved-operand bitflip), Target F2 (snapshot bias), Target F3 (persistent count wipe), Target F6 (verifier bypass), and Targets F9–F11 (DSPC) were tested **exclusively through a harness-level reimplementation of `native_ntt_monitor_butterfly`**.
- **Theoretical vs Empirical Validity:**  
  The mathematical conclusions regarding recovery-verifier blindness under corrupted snapshot inputs are valid as an algorithmic analysis of the recovery design, but **they do not represent an execution of the compiled object `bin/obj/mlkem_fault_hooks.o`**.
