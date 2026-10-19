# Workstream 3: Independent Experiment Reproduction and Outcome Verification

**Auditor:** Independent Cryptographic Fault-Injection Researcher  
**Date:** October 2026  
**Audited Commit:** `55dd937cbad66b24e5c2c0b89b78fa776801913c`  
**Execution Environment:** macOS AArch64 (Apple Silicon M-series), Apple Clang 15.0  

---

## 1. Executive Summary

This workstream independently re-executed the reported production fault experiments ($F4$, $F5A$, $F5B$, $F12$), re-calculated the harness-level circular verifier blindness rates ($H_1$), and re-evaluated the Silent Data Corruption bounds ($H_2$).

### Overall Findings:
- **100/100 F4 Genuine Recoveries:** Directly reproduced on production objects (`mlkem768_inst.o`, `mlkem_fault_hooks.o`). Every trial demonstrated that the single-butterfly retry path executed, restored authentic outputs, and emitted the exact reference shared secret.
- **200/200 Safe Fail-Stop Aborts (F5A & F5B):** Directly reproduced. In 100/100 recurring fault trials ($F5A$) and 100/100 software force-value trials ($F5B$), the monitor recorded persistent failure and emitted the FIPS 203 implicit rejection key $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$.
- **0/300 Production SDC (H2):** Confirmed across all 300 active fault trials. 95% Wilson score confidence interval is $[0.00\%, 1.26\%]$.
- **H1 Verifier Blindness Reproduction:** Recomputed directly from the 1,200 raw rows of `phase7_independent_claim_audit/derived_corrected_trial_results.csv`. False-pass rates across the vulnerable configurations are confirmed: $F1$ (98.0%), $F2$ (100.0%), $F6$ (99.0%), $F7$ (94.0%), $F9$ (100.0%), $F10$ (100.0%). Crucially, this is verified to be a **harness-model finding**, not a vulnerability of the compiled production binary where snapshots reside in compiler registers.

---

## 2. Production Experiment Reproduction Matrix ($F12, F4, F5A, F5B$)

An independent reproducer driver was compiled and executed:  
**Source:** [`phase18_audit/production_reproducer.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/production_reproducer.c)  
**Output CSV:** [`phase18_audit/raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv)

### Compilation Command:
```bash
clang -O3 -std=c99 -I algorithms/source_ref/mlkem \
  -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem768 -DMLK_CONFIG_PARAMETER_SET=768 \
  -DMLKEM_RESEARCH_FAULT_HOOKS \
  -c algorithms/source_ref/mlkem/mlkem_native.c -o bin/obj/mlkem768_inst.o

clang -O3 -std=c99 -I algorithms/source_ref/mlkem \
  -DMLKEM_RESEARCH_FAULT_HOOKS \
  -c algorithms/source_ref/mlkem_fault_hooks.c -o bin/obj/mlkem_fault_hooks.o

clang -O3 -Wall -Wextra -std=c11 -I . -I algorithms/source_ref/mlkem \
  phase18_audit/production_reproducer.c \
  bin/obj/mlkem768_inst.o bin/obj/mlkem_fault_hooks.o \
  -o phase18_audit/production_reproducer -L/opt/homebrew/lib -loqs

./phase18_audit/production_reproducer
```

### Reproduction Results Table (N = 400 Trials):
| Experiment ID | Target Locus | Fault Injection Model | Active Trials | Observed Trigger Count | Mismatch Count | Retry Count | Recovered Count | Persistent Count | Decaps Status Code | Oracle Key Match | Classified Outcome | Reproduction Status |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|:---:|
| **F12** | Clean Baseline | None (Control) | 100 | 0 | 0 | 0 | 0 | 0 | `0x5A5A5A5A` | $K == K_{\text{valid}}$ (100/100) | `CLEAN_SUCCESS` (100/100) | **REPRODUCED** |
| **F4** | CT Multiplier ($t$) | Transient 1-bit XOR | 100 | 1 | 1 | 1 | 1 | 0 | `0x5A5A5A5A` | $K == K_{\text{valid}}$ (100/100) | `GENUINE_RECOVERY` (100/100) | **REPRODUCED** |
| **F5A** | CT Multiplier ($t$) | Recurring 1-bit XOR (6×) | 100 | 6 | 1 | 1 | 0 | 1 | `0xFFFFFFFF` | $K == K_{\text{rej}}$ (100/100) | `SAFE_FAIL_STOP` (100/100) | **REPRODUCED** |
| **F5B** | CT Multiplier ($t$) | Software Force-Value ($t \leftarrow 0$) | 100 | 6 | 1 | 1 | 0 | 1 | `0xFFFFFFFF` | $K == K_{\text{rej}}$ (100/100) | `SAFE_FAIL_STOP` (100/100) | **REPRODUCED** |

---

## 3. Deep Dive into Target Validations

### 3.1. Target F4: Verification of Genuine Recovery Pathway
To confirm that $F4$ does not merely report a superficial counter increment while bypassing arithmetic repair:
1. **Trigger Evidence:** In every trial, `trigger_count == 1` was recorded by the injection hook.
2. **Detection Evidence:** `mismatch_count == 1` proves the parity invariant detected the fault.
3. **Execution of Retry:** `retry_attempt_count == 1` confirms the branch into `allow_retry` was taken.
4. **Parity Re-verification:** `recovered_count` was incremented, which requires `diff_retry == 0 && sum_retry == 0` upon fresh calculation.
5. **Cryptographic Proof:** In all 100 trials, the returned shared secret matched $K_{\text{valid}}$ byte-for-byte (`memcmp == 0`). If the retry had failed to repair the butterfly coefficient, the downstream FO re-encryption would have detected a ciphertext mismatch and emitted $K_{\text{rej}}$, or caused SDC. The emission of $K_{\text{valid}}$ constitutes cryptographic proof of complete state recovery.

### 3.2. Targets F5A & F5B: Verification of Fail-Stop Escalation
1. **Trigger Evidence:** `trigger_count == 6` confirms persistent injection across multiple passes.
2. **Escalation Evidence:** `persistent_count >= 1` was set because the fault remained present during retry recomputation (`diff_retry != 0`).
3. **Status Propagation:** In `mlkem_fault_hooks.c:596`, `ntt_native_monitor_get_persistent_count()` returned $> 0$. In `kem.c:489`, this forced `fail = 0xFF` and `internal_status = 0xFFFFFFFF`.
4. **Conformance Proof:** In all 200 trials, the output secret matched $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$ identically. Zero trials emitted invalid keys.

---

## 4. Re-evaluation of H1: Circular Verifier Blindness (Harness Model)

**Dataset:** `phase7_independent_claim_audit/derived_corrected_trial_results.csv` (1,200 rows)  
**Metric Definition:** Verifier Blindness occurs when `verifier_passed == 1` despite `retry_matches_ref == 0` (the verifier accepts a corrupted state because its reference snapshot was also corrupted).

### Recomputed Breakdown across all 12 Target Configurations:
| Target ID | Target Name | Description | Tested Trials | False Passes Observed | Empirical Blindness Rate | Status in Manuscript |
|:---:|:---|:---|:---:|:---:|:---:|:---|
| **0** | `F1_SAVED_OPERAND_BITFLIP` | 1-bit flip in saved snapshot operand | 100 | 98 | **98.0%** | Cited in §5.2 |
| **1** | `F2_SNAPSHOT_PRE_RETRY_DIFFUSION` | Multi-bit snapshot corruption | 100 | 100 | **100.0%** | Cited in §5.2 |
| **2** | `F3_MONITOR_PERSISTENT_COUNT_ZERO` | Tampered persistent count | 100 | 0 | 0.0% | Control target |
| **3** | `F4_MONITOR_ALLOW_RETRY_FORCE` | Forced retry override | 100 | 0 | 0.0% | Control target |
| **4** | `F5_VERIFIER_DIFF_CALC_CORRUPT` | Corrupted difference check | 100 | 0 | 0.0% | Control target |
| **5** | `F6_VERIFIER_RESULT_FORCE_PASS` | Forced boolean verifier return | 100 | 99 | **99.0%** | Cited in §5.2 (as InvNTT) |
| **6** | `F7_RETRY_ARITHMETIC_GLITCH` | Recomputation glitch | 100 | 94 | **94.0%** | Cited in §5.2 (as InvNTT) |
| **7** | `F8_VERIFIER_INPUT_OPERAND_CORRUPT` | Operand tampering | 100 | 0 | 0.0% | Control target |
| **8** | `F9_DSPC_COLLISION_MULTI_BIT` | Multi-bit state collision | 100 | 100 | **100.0%** | Cited in §5.2 (as PolyMul) |
| **9** | `F10_DSPC_STATE_BYPASS` | State pointer bypass | 100 | 100 | **100.0%** | Cited in §5.2 (as PolyMul) |
| **10**| `F11_DSPC_CLEAN_CORRECTION` | Nominal recovery baseline | 100 | 0 | 0.0% | Control baseline |
| **11**| `F12_CLEAN_BASELINE_CONTROL` | Unfaulted baseline | 100 | 0 | 0.0% | Control baseline |

**Auditor Note on H1:** Across the six vulnerable configurations ($F1, F2, F6, F7, F9, F10$), the false-pass rates range between **94.0% and 100.0%** ($591 / 600$ trials = $98.5\%$). The manuscript's claim of 94.0–100.0% false-pass rate is strictly supported by the raw CSV data.

---

## 5. Re-evaluation of H2: Silent Data Corruption (SDC)

### SDC Classification Rule:
$$\text{SDC} \iff (K_{\text{actual}} \neq K_{\text{valid}}) \land (K_{\text{actual}} \neq K_{\text{rej}}) \land (\text{internal\_status} \neq \text{FAULT})$$

### Production Evaluation Denominator:
- Active fault trials: $n = 100\ (F4) + 100\ (F5A) + 100\ (F5B) = 300\ \text{trials}$.
- Clean controls: $n = 100\ (F12)$ are excluded from the fault denominator.

### Outcome:
- Total SDC events observed: **0 / 300** ($0.00\%$).
- 95% Wilson score confidence interval:
  $$\text{Center} = \frac{0 + 1.95996^2 / (2 \times 300)}{1 + 1.95996^2 / 300} = \frac{1.9207}{1.0128} = 0.00637$$
  $$\text{Upper Bound} = 0.00637 + \frac{1.95996 \times \sqrt{0 + 1.95996^2 / (4 \times 300^2)}}{1.0128} = 0.01262 \implies \mathbf{1.26\%}$$
- **Verdict:** Fully supported. Upper bound is $1.26\%$.
