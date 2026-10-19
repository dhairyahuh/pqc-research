# Production Reproduction Protocol & Trial Audit

**Auditor:** Skeptical Cryptographic Implementation Auditor  
**Date:** October 2026  
**Target:** ML-KEM-768 Production Binary Execution Reproduction  
**Harness:** `phase12_reproducibility_audit/production_reproducer.c`  
**Trial Log:** `phase12_reproducibility_audit/production_reproduction_trials.csv`  

---

## 1. Reproduction Protocol and Target Taxonomy

The reproduction suite tests 400 distinct trials directly against the compiled production object files (`bin/obj/mlkem768_inst.o` and `bin/obj/mlkem_fault_hooks.o`). Every trial is executed through the public C API function `mlkem768_dec_monitored(...)`.

### 1.1 Target Specifications and Accurate Scientific Labels

| Target ID | Accurate Scientific Label | Evaluated Fault Semantics | Injection Locus | Hook Source Function & Location | Persistence Setting |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **F12** | **Clean baseline control, never a recovery event** | None (`armed = 0`, `triggered = 0`) | None | None | `false` |
| **F4** | **Transient software-modeled bit flip** | Single-bit inversion on intermediate $t$ | Mid-NTT Post-Mul | `hook_mid_ntt_post_mul` (`mlkem_fault_hooks.c:250-265`) | `false` |
| **F5A**| **Recurring software-modeled bit inversion** | Bit inversion re-applied on every retry attempt | Mid-NTT Post-Mul | `hook_mid_ntt_post_mul` (`mlkem_fault_hooks.c:250-265`) | `true` |
| **F5B**| **Software force-value fault model** | Forced assignment $t \leftarrow 0$ on every retry attempt | Mid-NTT Post-Mul | `hook_mid_ntt_post_mul` (`mlkem_fault_hooks.c:250-265`) | `true` |

> **Auditor Note on Nomenclature:**  
> Previous project reports informally referred to F5B as "hardware stuck-at-zero". In this audit, it is strictly designated as a **software force-value fault model** because it is executed via software memory reassignment in C (`*t_ptr = 0`), without physical electrical pull-down or transistor-level fault injection.

---

## 2. Injection Hook Call Path Verification

Static audit confirms the production hook call chain:
1. `kem.c:438` calls `mlk_indcpa_dec(buf, ct, sk, context)`.
2. `indcpa.c:166` calls `mlk_polyvec_invntt_tomont(mp)`.
3. `poly.c:393` within the Cooley-Tukey NTT butterfly loop invokes:
   ```c
   hook_mid_ntt_post_mul(layer, b_idx, &t, j, j + len);
   ```
4. In `mlkem_fault_hooks.c:250-265`:
   - If `g_mlkem_fault.persistent == false`: the hook fires only when `g_mlkem_fault.trigger_count == 0`. When the monitor detects the error and retries the butterfly, `trigger_count > 0` prevents re-injection, modeling a transient fault.
   - If `g_mlkem_fault.persistent == true`: the hook fires on both initial execution and all subsequent retries, modeling a permanent/recurring fault.
5. In `kem.c:484-489`:
   ```c
   if (ntt_native_monitor_get_persistent_count() > 0 ||
       invntt_native_monitor_get_persistent_count() > 0)
   {
     fail = 0xFF; /* Force implicit rejection regardless of internal_status pointer */
     if (internal_status != NULL) {
       *internal_status = MLK_DECAPS_STATUS_FAULT;
     }
   }
   ```
   If the persistent count is non-zero, implicit rejection is unconditionally enforced.

---

## 3. Operational Classification Rules

Every trial is evaluated against mutually exclusive and exhaustive classification rules:

```c
/* Rule 1: Clean Baseline Control */
if (valid_match && status == 0x5A5A5A5A && mismatch == 0 && rec == 0 && trig == 0)
    outcome = "CLEAN_SUCCESS";

/* Rule 2: Transient Fault Genuine Recovery */
else if (trig > 0 && valid_match && status == 0x5A5A5A5A && rec > 0 && pers == 0)
    outcome = "GENUINE_RECOVERY";

/* Rule 3: Safe Fail-Stop Rejection */
else if (trig > 0 && rej_match && status == 0xFFFFFFFF && pers > 0 && !valid_match)
    outcome = "SAFE_FAIL_STOP";

/* Rule 4: Downstream FO Rejection (FO Trap) */
else if (trig > 0 && rej_match && status == 0xA5A5A5A5 && !valid_match)
    outcome = "DOWNSTREAM_FO_REJECTION";

/* Rule 5: Silent Data Corruption (SDC) */
else if (!valid_match && status == 0x5A5A5A5A)
    outcome = "SDC_ACCEPTED_INCORRECT";

/* Rule 6: Fault Not Triggered */
else if (trig == 0 && armed > 0)
    outcome = "FAULT_NOT_TRIGGERED";

/* Rule 7: Inconclusive */
else
    outcome = "INCONCLUSIVE";
```

---

## 4. Empirical Reproduction Results ($N=400$)

All 400 trials were compiled and executed fresh via `phase12_reproducibility_audit/production_reproducer.c`:

| Target ID | Evaluated Fault Model | Trials | Armed | Triggered | Mismatch Count | Recovered Count | Persistent Count | Decaps RC | Internal Status | Valid Key Match | Rejection Key Match | Final Classification |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **F12** | Clean Baseline Control | 100 | 0 | 0 | 0 | 0 | 0 | 0 | `0x5A5A5A5A` | **100/100** | 0/100 | **CLEAN_SUCCESS (100%)** |
| **F4** | Transient Software Bit-Flip | 100 | 100 | 100 | 1 | 1 | 0 | 0 | `0x5A5A5A5A` | **100/100** | 0/100 | **GENUINE_RECOVERY (100%)** |
| **F5A**| Recurring Software Bit-Inversion | 100 | 100 | 100 | 3 | 1 | 2 | 0 | `0xFFFFFFFF` | 0/100 | **100/100** | **SAFE_FAIL_STOP (100%)** |
| **F5B**| Software Force-Value Model | 100 | 100 | 100 | 3 | 1 | 2 | 0 | `0xFFFFFFFF` | 0/100 | **100/100** | **SAFE_FAIL_STOP (100%)** |

All raw trial records, hex outputs, and comparisons are preserved in [`production_reproduction_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase12_reproducibility_audit/production_reproduction_trials.csv).

---

## 5. Audit of Differences Between Historical and Reproduced Runs

1. **Resolution of Phase 9 Target F12 Bug:**  
   Phase 9's automated harness logged Target F12 as `GENUINE_RECOVERY` due to a loose check on `status == 0x5A5A5A5A`. In Phase 12, rule `mismatch == 0 && rec == 0 && trig == 0` strictly guarantees classification as `CLEAN_SUCCESS`.
2. **Elimination of Production Library Rejection-Key Helper:**  
   In Phase 10, expected rejection keys were computed by calling `mlkem768_shake256` from `mlkem768_inst.o`. In Phase 12, all 400 trials were verified against the clean-room Keccak oracle. Every single fail-stop output matched the oracle's independent calculation of $J(z \parallel c)$.
3. **Execution Integrity:**  
   Zero failed, zero unhandled, and zero inconclusive trials were observed.
