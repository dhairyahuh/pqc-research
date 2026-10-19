# Harness vs Production Implementation: Line-by-Line Differential Audit

**Auditor:** Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Comparison Target:**  
- **Production Reference:** [`algorithms/source_ref/mlkem_fault_hooks.c:600-664`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L600-L664)  
- **Phase 7 Harness:** [`phase7_independent_claim_audit/genuine_phase7_audit_harness.c:161-327`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/genuine_phase7_audit_harness.c#L161-L327)  

---

## 1. Executive Summary

Phase 7 reported that it resolved internal false recovery (H1) and DSPC resilience using an independent oracle. However, this audit reveals that **the Phase 7 harness did not execute the production monitor implementation in `mlkem_fault_hooks.c`**.

Instead, the Phase 7 harness linked directly with `bin/obj/mlkem768_inst.o` while omitting `bin/obj/mlkem_fault_hooks.o`, thereby replacing the production monitor with a **reimplementation inside the harness file**.

This reimplementation was not merely an instrumented wrapper: it embedded artificial fault injection hooks, mocked control registers, and implemented the Dual-Snapshot Parity Checksum (DSPC) entirely inside the harness.

---

## 2. Line-by-Line Comparative Mapping

| Aspect / Logic | Production Source (`mlkem_fault_hooks.c`) | Phase 7 Harness (`genuine_phase7_audit_harness.c`) | Audit Assessment |
| :--- | :--- | :--- | :--- |
| **Function Signature** | `void native_ntt_monitor_butterfly(...)` (Lines 600–604) | `void native_ntt_monitor_butterfly(...)` (Lines 161–165) | Identical C signature; harness satisfies linker symbol. |
| **Monitor State Struct** | `ntt_native_monitor_state_t g_ntt_native_monitor` (Lines 596–625) | `monitor_state_t g_ntt_mon` (Lines 39, 177–211) | Reimplemented structure. Harness maintains separate static counters. |
| **Mode & Layer Gating** | Checks `g_ntt_native_monitor.mode == NTT_NATIVE_MONITOR_DISABLED` and `layer_mask` (Lines 605–610) | Checks `g_ntt_mon.mode == 0` (Line 177) | Harness simplifies mode check; layer mask gating omitted. |
| **Reference Capture** | None. (Production code has no concept of oracle reference capture). | Intercepts execution via `g_capture_ref_mode` to record `g_ref_butterflies[poly][layer][b]` (Lines 169–175). | **Harness-only feature.** Necessary for independent reference capture. |
| **Saved Operand Fault (F1)** | **Completely absent.** `u_saved` is a read-only parameter passed by value. | Mutates argument: `u_saved ^= (1 << (g_fault.bit % 16));` (Lines 181–187). | **Harness-only code.** No mechanism in `mlkem_fault_hooks.c` allows bit flips in `u_saved`. |
| **Invariant Checking** | `diff_c = (*r_j - *r_j_len - 2*t_check) % 3329`<br>`sum_c = (*r_j + *r_j_len - 2*u_saved) % 3329` (Lines 623–624) | Identical arithmetic and modulus (Lines 192–193). | **Structurally identical arithmetic.** |
| **Retry Control Override (F4)** | Checks `g_ntt_native_monitor.allow_retry` (Line 631) | Overrides flag: `g_ntt_mon.allow_retry = true;` (Lines 203–208) | **Harness-only code.** In production, `allow_retry` is set globally via `ntt_native_monitor_configure`. |
| **Snapshot Additive Bias (F2)** | **Completely absent.** | Mutates argument: `u_saved = (int16_t)(u_saved + 100);` (Lines 213–218). | **Harness-only code.** In production, `u_saved` cannot be mutated post-detection. |
| **DSPC Mitigation Logic (F9–F11)** | **Completely absent.** In-tree repository contains zero DSPC source code. | Full software implementation: computes `snap_token`, XORs bitflip, checks `test_token != snap_token`, simulates bypass (Lines 220–254). | **Harness-only simulation.** DSPC is a prototype model existing only in experimental harnesses. |
| **Rollback Execution** | `*r_j = u_saved; *r_j_len = v_saved;` (Lines 635–636) | `*r_j = u_saved; *r_j_len = v_saved;` (Lines 256–257) | Identical memory rollback logic. |
| **Retry Butterfly Computation** | `t_retry = monitor_fqmul(v_saved, zeta);`<br>`u_new = (int16_t)(u_saved + t_retry);`<br>`v_new = (int16_t)(u_saved - t_retry);` (Lines 638–640) | Identical arithmetic; adds F7 injection hook `t_retry ^= (1 << bit)` (Lines 259–268). | Production only supports persistent fault re-injection via `g_mlkem_fault.persistent`. |
| **Recovery Verifier Inputs (F8)** | Uses `u_saved` directly in `sum_retry` (Line 653). | Introduces `u_ver_operand` and corrupts it: `u_ver_operand ^= (1 << bit)` (Lines 282–287). | **Harness-only code.** Verifier operand corruption simulated locally. |
| **Recovery Verifier Invariants** | `diff_retry = (u_new - v_new - 2*t_retry) % 3329`<br>`sum_retry = (u_new + v_new - 2*u_saved) % 3329` (Lines 652–653) | Identical arithmetic; adds F5 corruption (`diff_retry++`) and F6 override (`diff_retry = 0; sum_retry = 0;`) (Lines 289–303). | Production has no override hooks on verifier outcome. |
| **Fail-Stop Gate Override (F3)** | `persistent_count++` (Line 658) | Resets counter: `g_ntt_mon.persistent_count = 0;` (Lines 315–319). | **Harness-only code.** Simulates register corruption of monitor persistent count. |

---

## 3. Detailed Arithmetic and Type Differences

Both files implement the butterfly retry arithmetic using C standard types:

```c
int16_t t_retry = monitor_fqmul(v_saved, zeta);
int16_t u_new = (int16_t)(u_saved + t_retry);
int16_t v_new = (int16_t)(u_saved - t_retry);

int32_t diff_retry = ((int32_t)u_new - (int32_t)v_new - 2 * (int32_t)t_retry) % 3329;
int32_t sum_retry  = ((int32_t)u_new + (int32_t)v_new - 2 * (int32_t)u_saved) % 3329;
```

### Analysis of Types:
1. **Operand Widths:** Both files store coefficients as `int16_t` and promote to `int32_t` for the recovery verifier modulus.
2. **Narrowing Cast:** Both files explicitly cast `(int16_t)(u_saved + t_retry)`. Under C99/C11 §6.3.1.3, this narrowing conversion is implementation-defined when the value exceeds $[-32768, 32767]$. On two's complement architectures, this is an arithmetic truncate modulo $2^{16}$.
3. **Difference vs Production:** The mathematical structure of the retry butterfly and verifier in the harness is an exact copy of the production code. **The arithmetic itself is faithful to the production design.**

---

## 4. Verification Assessment

1. **Did the harness use a custom monitor?**  
   **Yes.** The harness provided its own compilation unit defining `native_ntt_monitor_butterfly` and did not link `bin/obj/mlkem_fault_hooks.o`.

2. **Why was this done?**  
   Because the production source in `algorithms/source_ref/mlkem_fault_hooks.c` contains **no hook or mechanism to corrupt saved operands (`u_saved`), monitor state (`persistent_count`), or recovery verifier outcomes (`diff_retry = 0`)**. To test what happens when these internal variables are corrupted by hardware faults, the researchers had to either modify the production library or reimplement the monitor with fault injection points.

3. **Did this invalidate the cryptographic findings?**  
   - For **H1 (Internal False Recovery):** The harness accurately replicated the production monitor's arithmetic logic. The finding that the recovery verifier algorithmically passes under snapshot corruption is mathematically valid and applies equally to the production monitor logic.
   - For **H2 (End-to-End Cryptographic Acceptance):** The harness invoked the **genuine compiled cryptographic binary** (`bin/obj/mlkem768_inst.o`), and the decapsulation checks (FO re-encryption, reverse dual-rail comparison, and constant-time key derivation) were executed entirely by the authentic production code.
   - For **DSPC (Dual-Snapshot Parity Checksum):** DSPC does **not exist** in the production codebase. All DSPC findings describe an experimental prototype constructed within the test harness.
