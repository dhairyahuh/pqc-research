# Fault Hook Semantics and Trigger Accounting Audit

**Auditor:** Skeptical Cryptographic Software Verification Researcher  
**Date:** October 2026  
**Target:** Implementation Semantics of In-Tree Fault Hooks in `mlkem_fault_hooks.c`  

---

## 1. Executive Summary

A critical defect identified in prior audit phases was the conflation of physical fault terminology. Specifically, Phase 9 labeled Target F5 as a "persistent stuck-at fault" while configuring `FAULT_TYPE_BIT_FLIP` with `persistent = true`.

This audit inspects the exact C implementation in [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) to establish:
1. The lifecycle of `mlkem_fault_reset()` and `trigger_count`.
2. The exact mathematical semantics of `FAULT_TYPE_BIT_FLIP` vs `FAULT_TYPE_FORCE_VALUE`.
3. The distinction between recurring bit-inversion and physical Boolean stuck-at faults.

---

## 2. Trigger Accounting and Reset Lifecycle

### 2.1 The `mlkem_fault_reset()` Function
```c
void mlkem_fault_reset(void) {
    memset(&g_mlkem_fault, 0, sizeof(g_mlkem_fault));
    g_mlkem_fault.stage_recorded = -1;
    g_mlkem_fault.butterfly_recorded = -1;
    strcpy(g_mlkem_fault.fault_taxonomy, "NONE");
}
```
- `mlkem_fault_reset()` unconditionally clears the entire global configuration struct `g_mlkem_fault`, zeroing `trigger_count`, `enabled`, and all targeting fields.
- It is invoked internally at the beginning of `mlkem_fault_arm_mid_ntt_locus(...)`.
- **Requirement:** In `corrected_production_reproducer.c`, `mlkem_fault_reset()` and `ntt_native_monitor_reset()` are called prior to every single trial to guarantee independent, non-cumulative trial accounting.

### 2.2 Trigger Accounting Under Transient (`persistent = false`) Execution
In [`mlkem_fault_hooks.c:258-277`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L258-L277):
```c
    if ((g_mlkem_fault.trigger_count == 0 || g_mlkem_fault.persistent) &&
        g_mlkem_fault.target_stage == layer &&
        g_mlkem_fault.target_butterfly == butterfly_idx &&
        g_mlkem_fault.ntt_locus == NTT_LOCUS_INTERMEDIATE_T) {
        ...
        g_mlkem_fault.trigger_count++;
    }
```
- When `persistent = false`, the condition `g_mlkem_fault.trigger_count == 0` is satisfied **only once**.
- When the target butterfly executes during polynomial #0 of the 6 decapsulation polynomials, `trigger_count` transitions from 0 to 1.
- In subsequent polynomials (#1 through #5), `trigger_count > 0`, causing the hook to evaluate to false and bypass injection.
- **Result:** Models an authentic single-event transient upset (SEU). `trigger_count == 1` per trial.

### 2.3 Trigger Accounting Under Persistent (`persistent = true`) Execution
- When `persistent = true`, the condition `(g_mlkem_fault.trigger_count == 0 || g_mlkem_fault.persistent)` evaluates to **true on every encounter**.
- In ML-KEM-768 decapsulation, forward NTT is applied to 6 polynomials (3 in vector $\mathbf{s}$, 3 in vector $\mathbf{e}$).
- The target stage and butterfly execute exactly once per polynomial.
- Consequently, the hook fires 6 times, yielding `trigger_count == 6` at trial completion.
- In addition, during recovery retry inside `native_ntt_monitor_butterfly` ([`mlkem_fault_hooks.c:642-647`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L642-L647)):
  ```c
  if (g_mlkem_fault.persistent && g_mlkem_fault.enabled &&
      g_mlkem_fault.target == HOOK_TARGET_MID_NTT_BUTTERFLY &&
      g_mlkem_fault.target_stage == layer &&
      g_mlkem_fault.target_butterfly == butterfly_idx) {
      u_new ^= (1u << (g_mlkem_fault.bit_to_flip % 16));
  }
  ```
  The persistent fault re-corrupts the recomputed butterfly operand `u_new`, preventing the recovery verifier from clearing the fault.

---

## 3. Disambiguation: Recurring Bit-Inversion vs True Stuck-At Faults

### 3.1 `FAULT_TYPE_BIT_FLIP` (Target F5A)
In `apply_fault` ([`mlkem_fault_hooks.c:61`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L61)):
```c
case FAULT_TYPE_BIT_FLIP:
    return orig ^ (1u << (bit % 32));
```
- This operation unconditionally **inverts** the targeted bit ($0 \to 1$ and $1 \to 0$).
- If applied repeatedly across passes, it toggles the state rather than fixing it to a constant voltage rail.
- **Accurate Scientific Classification:** Target F5A is a **recurring bit-inversion fault**, not a stuck-at fault.

### 3.2 `FAULT_TYPE_FORCE_VALUE` (Target F5B)
In `apply_fault` ([`mlkem_fault_hooks.c:73`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L73)):
```c
case FAULT_TYPE_FORCE_VALUE:
    return forced;
```
- This operation clamps the operand directly to `forced` (e.g., `0`), modeling an actual physical wire tied to GND (Stuck-At-0 / SA0) or VDD (Stuck-At-1 / SA1).
- **Accurate Scientific Classification:** Target F5B is a **true hardware stuck-at-zero fault**.

---

## 4. Auditor Conclusion

In Phase 10, both fault models were implemented and verified independently:
- **Target F5A (`F5A_RECURRING_BITFLIP`):** Evaluates recurring bit-inversion across passes and retry.
- **Target F5B (`F5B_STUCK_AT_ZERO`):** Evaluates physical stuck-at-0 line clamping via `FAULT_TYPE_FORCE_VALUE`.
Both targets achieve **100.0% safe fail-stop rejection** (`status = 0xFFFFFFFF`, implicit rejection key).
