# Genuine Outcome-Observation Fault Test Plan

**Standard:** FIPS 203 / ML-KEM-768 Experimental Verification  
**Harness Target:** `phase3_harness_audit/harness/genuine_countermeasure_test.c`  
**Execution Objective:** Evaluate ML-KEM-768 decapsulation countermeasures under genuine software fault injection without manual metric assignments or harness-level simulated logic.

---

## 1. Experimental Integrity Rules

1. **Zero Status Overrides**: The harness must never assign `status = ...`, `mismatch_count++`, or `recovered_count++` in test wrappers. All status codes and counter values must originate solely from the execution of `mlkem768_dec_monitored()` in `bin/obj/mlkem768_inst.o` and `bin/obj/mlkem_fault_hooks.o`.
2. **Independent Oracle**: Decapsulation outputs must be compared against precomputed, cryptographic ground truth:
   - $K_{\text{expected}} = \text{ML-KEM.Decaps}(c, sk)$ (clean reference decapsulation)
   - $K_{\text{rej}} = J(z \parallel c_{\text{invalid}})$ (implicit rejection ground truth)
3. **Trigger Verification**: Every trial must record whether the injected fault actually triggered (`g_mlkem_fault.trigger_count > 0`). Inactive or unreachable faults must be classified as `FAULT_NOT_TRIGGERED`.
4. **Physical Reality Constraints**: Software bit flips must be documented as register or memory bit inversions, not described as "physical electromagnetic glitches" or "hardware SEUs".
5. **Full State Capture**: Every trial must log trial ID, variant ID, target ID, stage, butterfly index, target bit, latency ($\mu\text{s}$), triggered status, actual mismatch count, actual recovery count, raw status word, exact key comparison flags, and final classification.

---

## 2. Tested Variants

| Variant ID | Name | Configuration & Execution Logic |
| :--- | :--- | :--- |
| **0** | `VARIANT_A_IN_TREE_BASELINE` | Native NTT/InvNTT butterfly invariant monitors (`RECOMPUTED_T` / `RECOMPUTED`), rollback retry enabled (`allow_retry = true`). |
| **1** | `VARIANT_B_GENUINE_TABLE_CHECK` | Native monitors enabled; executes an actual pre-flight table comparison against an independent reference table before decapsulation. |
| **2** | `VARIANT_C_GENUINE_DIVERSE_VERIFY`| Native monitors enabled; executes diverse re-computation verification without manual status forcing. |
| **3** | `VARIANT_D_GENUINE_FAIL_STOP` | Native monitors enabled; retry explicitly disabled (`allow_retry = false`), forcing immediate constant-time fail-stop upon detection. |

---

## 3. Targeted Fault Classes

| Target ID | Name | Injection Locus | Injection Model | Feasibility & Limitations |
| :--- | :--- | :--- | :--- | :--- |
| **T1** | `T1_OPERATIONAL_TWIDDLE` | Mid-NTT butterfly twiddle operand ($\zeta$) before `fqmul` | Single-bit flip (bits 0..15) | Tests whether the butterfly invariant check detects twiddle corruption. |
| **T2** | `T2_REFERENCE_TABLE_CORRUPT` | Reference twiddle table array in static memory | Single-bit corruption in reference constants | Tests whether pre-flight table checks generate false-positive aborts when reference memory is corrupted. |
| **T3** | `T3_SAVED_OPERAND_CORRUPT` | InvNTT butterfly input operand ($u$) | Single-bit flip in operand register | Tests recovery rollback behavior and snapshot integrity. |
| **T4** | `T4_RETRY_MULTIPLIER_GLITCH` | Intermediate multiplier result ($t$) before addition | Single-bit flip (transient) | Tests whether transient multiplier faults recover successfully on retry. |
| **T5** | `T5_PERSISTENT_STUCK_AT` | Butterfly adder output ($r[j]$) | Persistent bit flip (`persistent = true`) | Tests behavior when a fault persists through the retry loop. |
| **T6** | `T6_CLEAN_CONTROL` | None (no fault armed) | Pristine baseline | Positive control for false-alarm rate and baseline latency. |

---

## 4. Independent Classification Oracle

Let $S$ be the returned status word, $K_{\text{out}}$ be the 32-byte decapsulated key, $M$ be the actual mismatch counter, and $R$ be the actual recovery counter:

```
IF target == T6 (Clean Control):
    IF S == 0x5A5A5A5A AND K_out == K_expected AND M == 0:
        CLASSIFICATION = CORRECT_CLEAN_EXECUTION
    ELSE:
        CLASSIFICATION = FALSE_POSITIVE_FAULT

ELSE IF target == T2 AND variant == 1 (Reference Table Check):
    IF pre-flight table mismatch detected:
        CLASSIFICATION = FALSE_POSITIVE_ABORT (Reference Memory Corrupted)

ELSE IF triggered == 0:
    CLASSIFICATION = FAULT_NOT_TRIGGERED

ELSE IF S == 0x5A5A5A5A AND K_out == K_expected AND R > 0:
    CLASSIFICATION = FAULT_DETECTED_AND_RECOVERED

ELSE IF S == 0x5A5A5A5A AND K_out == K_expected AND M == 0:
    CLASSIFICATION = BENIGN_EQUIVALENT_ABSORBED (LWE Slack / High-Bit Invariance)

ELSE IF (S == 0xA5A5A5A5 OR S == 0xFFFFFFFF) AND (K_out == K_rej OR K_out != K_expected):
    CLASSIFICATION = FAULT_DETECTED_AND_SAFELY_REJECTED

ELSE IF S == 0x5A5A5A5A AND K_out != K_expected:
    CLASSIFICATION = SILENT_DATA_CORRUPTION (CRITICAL INTEGRITY FAILURE)

ELSE:
    CLASSIFICATION = INCONCLUSIVE_OR_INVALID
```

---

## 5. Build and Execution Instructions

### Compilation
```bash
clang -O3 -Wall -Wextra -std=c11 \
  -I. -I algorithms/source_ref/mlkem \
  phase3_harness_audit/harness/genuine_countermeasure_test.c \
  bin/obj/mlkem768_inst.o \
  bin/obj/mlkem_fault_hooks.o \
  -o /tmp/genuine_countermeasure_test
```

### Execution
```bash
/tmp/genuine_countermeasure_test
```

Output is recorded in: `phase3_harness_audit/countermeasure_results.csv`.
