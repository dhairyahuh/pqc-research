# Production-Path Experiment Reproduction & Operational Audit

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Target:** In-Tree Fault Hooks & Production Binary Execution (`mlkem768_inst.o`, `mlkem_fault_hooks.o`)  
**Reproduction Executable:** `phase13_final_evidence_audit/production_reproducer`  
**Trial Log Reference:** `phase13_final_evidence_audit/production_trial_recalculation.csv`  

---

## 1. Precise Fault Injection Locus & Call Path

Static code tracing confirms the in-tree production hook call path:
1. `kem.c:438`: `mlk_kem_dec_monitored` invokes `mlk_indcpa_dec(buf, ct, sk, context)`.
2. `indcpa.c:166`: `mlk_indcpa_dec` invokes `mlk_polyvec_invntt_tomont(mp)`.
3. `poly.c:393`: `poly_invntt_tomont` executes Cooley-Tukey butterfly layers and invokes:
   ```c
   hook_mid_ntt_post_mul(layer, b_idx, &t, j, j + len);
   ```
4. `mlkem_fault_hooks.c:250-265`:
   - Checks `g_mlkem_fault.enabled` and `g_mlkem_fault.target == HOOK_TARGET_MID_NTT_BUTTERFLY`.
   - Checks `g_mlkem_fault.target_stage == layer` and `g_mlkem_fault.target_butterfly == butterfly_idx`.
   - Mutates intermediate pointer `*t_ptr` via `apply_fault(...)`.
   - Records `g_mlkem_fault.trigger_count++`.

### Hook Semantics:
- **Transient (F4):** `g_mlkem_fault.persistent = false`. Fires only on `trigger_count == 0`. When the native monitor detects arithmetic mismatch and retries the butterfly, `trigger_count > 0` prevents re-injection, modeling a transient single-event upset.
- **Recurring Inversion (F5A):** `g_mlkem_fault.persistent = true`, `fault_type = FAULT_TYPE_BIT_FLIP`. Fires on every retry, inverting the bit repeatedly.
- **Software Force-Value (F5B):** `g_mlkem_fault.persistent = true`, `fault_type = FAULT_TYPE_FORCE_VALUE`, `forced_value = 0`. Assigns `*t_ptr = 0` on every retry.
- **Clean Baseline (F12):** `g_mlkem_fault.enabled = false`, `armed = 0`, `trigger_count = 0`.

---

## 2. Trial Reset & State Isolation

Between every trial, the harness executes:
```c
mlkem_fault_reset();
ntt_native_monitor_reset();
```
- `mlkem_fault_reset()` clears `g_mlkem_fault` to zero, clearing `armed`, `trigger_count`, and all trace registers.
- `ntt_native_monitor_reset()` resets `mismatch_count`, `retry_attempt_count`, `recovered_count`, and `persistent_count` to zero.
- Re-initialization guarantees zero state leakage or accumulator contamination between successive trials.

---

## 3. Operational Classification Rules

Every trial is classified according to mutually exclusive, deterministic predicates:

```c
/* CLEAN_SUCCESS: Clean baseline control without faults */
if (valid_match && status == 0x5A5A5A5A && mismatch == 0 && rec == 0 && trig == 0)
    classification = "CLEAN_SUCCESS";

/* GENUINE_RECOVERY: Transient fault detected and successfully recovered */
else if (trig > 0 && valid_match && status == 0x5A5A5A5A && rec > 0 && pers == 0)
    classification = "GENUINE_RECOVERY";

/* SAFE_FAIL_STOP: Persistent fault detected, retries exhausted, safe rejection emitted */
else if (trig > 0 && rej_match && status == 0xFFFFFFFF && pers > 0 && !valid_match)
    classification = "SAFE_FAIL_STOP";

/* DOWNSTREAM_FO_REJECTION: Trapped downstream by FO comparison */
else if (trig > 0 && rej_match && status == 0xA5A5A5A5 && !valid_match)
    classification = "DOWNSTREAM_FO_REJECTION";

/* SDC_ACCEPTED_INCORRECT: Silent Data Corruption (API accepts invalid key) */
else if (!valid_match && status == 0x5A5A5A5A)
    classification = "SDC_ACCEPTED_INCORRECT";

/* FAULT_NOT_TRIGGERED: Fault was armed but hook did not fire */
else if (trig == 0 && armed > 0)
    classification = "FAULT_NOT_TRIGGERED";

/* INCONCLUSIVE: State does not match any valid or safe outcome */
else
    classification = "INCONCLUSIVE";
```

---

## 4. Empirical Reproduction Results ($N=400$)

The reproduction binary was compiled and executed:
```bash
clang -O2 -Wall -Wextra -I. \
  phase13_final_evidence_audit/production_reproducer.c \
  bin/obj/mlkem768_inst.o \
  bin/obj/mlkem_fault_hooks.o \
  -o phase13_final_evidence_audit/production_reproducer

./phase13_final_evidence_audit/production_reproducer
```

### Recalculated Outcome Distribution:
| Target ID | Accurate Operational Label | Trials ($N$) | Armed | Actually Triggered | Decaps RC | Internal Status | Valid Key Match | Rejection Key Match | Final Classification |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **F12** | **Clean baseline control, never a recovery event** | 100 | 0 | 0 | 0 | `0x5A5A5A5A` | **100/100** | 0/100 | **CLEAN_SUCCESS (100.0%)** |
| **F4** | **Transient software-modeled bit flip** | 100 | 100 | 100 | 0 | `0x5A5A5A5A` | **100/100** | 0/100 | **GENUINE_RECOVERY (100.0%)** |
| **F5A**| **Recurring software-modeled bit inversion** | 100 | 100 | 100 | 0 | `0xFFFFFFFF` | 0/100 | **100/100** | **SAFE_FAIL_STOP (100.0%)** |
| **F5B**| **Software force-value fault model** | 100 | 100 | 100 | 0 | `0xFFFFFFFF` | 0/100 | **100/100** | **SAFE_FAIL_STOP (100.0%)** |

All 400 trial records are preserved in [`production_trial_recalculation.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/production_trial_recalculation.csv).

---

## 5. Methodological Boundaries

1. **Software vs. Physical Fault Semantics:**  
   Target F5B is strictly a **software force-value model** (`*t_ptr = 0`). It evaluates how the native monitor and recovery logic handle an arithmetic operand forced to zero, but does not model physical hardware stuck-at-zero faults (such as a bonded wire shorted to ground or transistor drain breakdown).
2. **Deterministic Triggering:**  
   In all 300 faulted trials (F4, F5A, F5B), `armed = 100` and `actually_triggered = 100`. No missed triggers occurred.
3. **Absence of Silent Data Corruption:**  
   Zero instances of `SDC_ACCEPTED_INCORRECT` occurred across the 400 production trials ($0/400$, 95% Wilson CI: $[0.0\%, 0.92\%]$).
