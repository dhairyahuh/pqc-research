# Per-Target Production Statistics and Uncertainty Intervals

**Auditor:** Skeptical Cryptographic Software Verification Researcher  
**Date:** October 2026  
**Evidence Source:** [`phase10_corrected_reproduction/raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/raw_production_trials.csv) (400 trials)  
**Binary Executed:** [`phase10_corrected_reproduction/corrected_production_reproducer`](file:///Users/dhairyajain/Desktop/pqc%20research/phase10_corrected_reproduction/corrected_production_reproducer)  

---

## 1. Summary of Corrected Production Execution

All 400 trials were executed strictly against the authentic compiled production objects:
`bin/obj/mlkem768_inst.o` + `bin/obj/mlkem_fault_hooks.o`.

```text
Target Breakdown:
- F12_CLEAN_BASELINE:      100 trials
- F4_TRANSIENT_RECOVERY:   100 trials
- F5A_RECURRING_BITFLIP:   100 trials
- F5B_STUCK_AT_ZERO:       100 trials
Total:                     400 trials
```

---

## 2. Per-Target Statistical Table

*Denominators are strictly 100 trials per target. All confidence intervals are two-sided 95% Wilson score intervals.*

| Target Identifier | Tested Fault Model | Armed | Actually Triggered | Invariant Detected | Recovery Rate | Safe Fail-Stop Rate | SDC Rate ($H_2$) | Primary Outcome Classification |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`F12_CLEAN_BASELINE`** | Uncorrupted Baseline | 0 / 100 | 0 / 100 (0.0%) | 0 / 100 (0.0%) | N/A | N/A | **0.0%** [0.0%, 3.6%] | **`CLEAN_SUCCESS`** (100/100) |
| **`F4_TRANSIENT_RECOVERY`** | Transient Multiplier Flip | 100 / 100 | 100 / 100 (100.0%) | 100 / 100 (100.0%) | **100.0%** [96.3%, 100.0%] | 0.0% [0.0%, 3.6%] | **0.0%** [0.0%, 3.6%] | **`GENUINE_RECOVERY`** (100/100) |
| **`F5A_RECURRING_BITFLIP`** | Recurring Bit Inversion | 100 / 100 | 100 / 100 (100.0%) | 100 / 100 (100.0%) | 0.0% [0.0%, 3.6%] | **100.0%** [96.3%, 100.0%] | **0.0%** [0.0%, 3.6%] | **`SAFE_FAIL_STOP`** (100/100) |
| **`F5B_STUCK_AT_ZERO`** | Hardware Stuck-At-0 | 100 / 100 | 100 / 100 (100.0%) | 100 / 100 (100.0%) | 0.0% [0.0%, 3.6%] | **100.0%** [96.3%, 100.0%] | **0.0%** [0.0%, 3.6%] | **`SAFE_FAIL_STOP`** (100/100) |

---

## 3. Detailed Per-Target Analysis

### 3.1 `F12_CLEAN_BASELINE` (100 Trials)
- **Armed:** 0. **Triggered:** 0.
- **Executed Butterflies:** Exactly 5,376 per trial ($896 \times 6$ polynomials).
- **Mismatches:** 0 across all 100 trials ($0.0\%$, 95% CI: $[0.0\%, 3.6\%]$).
- **Decapsulation Status:** `0x5A5A5A5A` in 100/100 trials.
- **Output Key:** Matches encapsulation shared secret bit-for-bit in 100/100 trials.
- **Outcome:** **100% `CLEAN_SUCCESS`**. Correctly segregated from fault recovery.

### 3.2 `F4_TRANSIENT_RECOVERY` (100 Trials)
- **Armed:** 100. **Triggered:** 100 (`trigger_count == 1`).
- **Detected:** 100/100 (`mismatch_count == 1`).
- **Rollback & Retry:** 100/100 retry attempts verified (`recovered_count == 1`, `persistent_count == 0`).
- **Decapsulation Status:** `0x5A5A5A5A` in 100/100 trials.
- **Output Key:** Matches genuine encapsulation shared secret in 100/100 trials.
- **Outcome:** **100% `GENUINE_RECOVERY`** ($100.0\%$, 95% CI: $[96.3\%, 100.0\%]$).

### 3.3 `F5A_RECURRING_BITFLIP` (100 Trials)
- **Armed:** 100. **Triggered:** 100 (`trigger_count == 6`, across 6 polynomials).
- **Detected:** 100/100 (`mismatch_count == 6`).
- **Recovery Outcome:** 0 recoveries (`recovered_count == 0`, `persistent_count == 6`).
- **Decapsulation Status:** `0xFFFFFFFF` (`MLK_DECAPS_STATUS_FAULT`) in 100/100 trials.
- **Cryptographic Key Output:** Does not match valid key; **matches independently generated expected rejection key $K_{\text{rej}} = \text{SHAKE256}(z \parallel ct)$ in 100/100 trials**.
- **Outcome:** **100% `SAFE_FAIL_STOP`** ($100.0\%$, 95% CI: $[96.3\%, 100.0\%]$).

### 3.4 `F5B_STUCK_AT_ZERO` (100 Trials)
- **Armed:** 100. **Triggered:** 100 (`trigger_count == 6`).
- **Detected:** 100/100 (`mismatch_count == 6`).
- **Recovery Outcome:** 0 recoveries (`recovered_count == 0`, `persistent_count == 6`).
- **Decapsulation Status:** `0xFFFFFFFF` (`MLK_DECAPS_STATUS_FAULT`) in 100/100 trials.
- **Cryptographic Key Output:** Matches independently generated expected rejection key in 100/100 trials.
- **Outcome:** **100% `SAFE_FAIL_STOP`** ($100.0\%$, 95% CI: $[96.3\%, 100.0\%]$).
