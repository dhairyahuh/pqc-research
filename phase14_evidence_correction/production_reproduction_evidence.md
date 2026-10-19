# Production Reproduction Evidence: F4, F5A, F5B, and F12

**Auditor:** Skeptical Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Subject:** Production Binary Fault Reproduction & Telemetry Validation  
**Target Code Under Test:** Compiled `mlkem768_inst.o` + `mlkem_fault_hooks.o`  

---

## 1. Executive Summary

This report documents the independent verification of the production decapsulation implementation under four experimental conditions:
1. **Target F12:** Clean Baseline Control (Unfaulted execution)
2. **Target F4:** Transient Butterfly Fault (Single transient bitflip in intermediate NTT butterfly)
3. **Target F5A:** Recurring Software Bit Inversion (Persistent bitflip across retries)
4. **Target F5B:** Software Force-Value Fault Model (Persistent zeroing of intermediate value)

All 400 trials were executed against the authentic production object files compiled from C source. 

**Key Findings:**
- **Trigger Fidelity:** 100% of armed trials (300/300) reached the target injection hook and registered positive trigger counts. Zero unintended triggers occurred during baseline trials (0/100).
- **State Hygiene:** Rigorous state reset (`mlkem_fault_reset()` and `ntt_native_monitor_reset()`) was executed before every trial. Zero state leakage was observed between consecutive runs.
- **Genuine Recovery in F4:** The native NTT monitor detected the intermediate transient glitch, re-executed the butterfly operation, restored exact arithmetic state, and achieved 100% genuine recovery ($100/100$) producing a valid shared secret ($K_{\text{out}} = K_{\text{valid}}$).
- **Safe Fail-Stop in F5A & F5B:** Under recurring faults, the monitor detected unresolvable arithmetic disparity, set `persistent_count > 0`, aborted NTT execution, and returned `status = 0xFFFFFFFF` while emitting the FIPS 203 implicit rejection key ($K_{\text{out}} = K_{\text{rej}}$).
- **Absence of SDC:** Zero Silent Data Corruption events ($0/400$) occurred.
- **Fault Model Boundary:** F5B is strictly categorized as a **software force-value fault model** (local variable assignment `t = 0` via debug hook). It does **not** model physical silicon stuck-at faults, bus contention, or clock/voltage glitching.

---

## 2. Compilation and Build Provenance

### 2.1 Compiler and Environment
- **Compiler:** Apple clang version 21.0.0 (`clang-2100.1.1.101`)
- **Target Architecture:** `arm64-apple-darwin27.0.0`
- **C Standard:** C99 (`-std=c99`)
- **Optimization:** `-O3`

### 2.2 Bit-for-Bit Object Hash Verification
Both production object files were rebuilt from clean source tree and verified against pre-existing repository objects:

```bash
# Compilation commands
clang -O3 -std=c99 -I algorithms/source_ref/mlkem -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem768 -DMLK_CONFIG_PARAMETER_SET=768 -DMLKEM_RESEARCH_FAULT_HOOKS -c algorithms/source_ref/mlkem/mlkem_native.c -o bin/obj/mlkem768_inst.o

clang -O3 -std=c99 -I algorithms/source_ref/mlkem -DMLKEM_RESEARCH_FAULT_HOOKS -c algorithms/source_ref/mlkem_fault_hooks.c -o bin/obj/mlkem_fault_hooks.o
```

**Cryptographic SHA-256 Hashes:**
- `bin/obj/mlkem768_inst.o`:  
  `7adc428039c318eb0d71b3fc7e24da602010acf7df5e37183ccba5a22eaef65f` (100% Match)
- `bin/obj/mlkem_fault_hooks.o`:  
  `e7a90d06019aeb9e3f8b656e19e719985c797c25f629cb987f9d97f83a5fd952` (100% Match)

---

## 3. Detailed Inspection of Execution Flow

### 3.1 Target F12: Clean Baseline Control (Trials 0–99)
- **Setup:** `mlkem_fault_reset()`, `ntt_native_monitor_reset()`. No fault armed (`g_mlkem_fault.armed = false`).
- **Functions Executed:** `mlkem768_keypair`, `mlkem768_enc`, `mlkem768_dec_monitored`.
- **Observed Behavior:**
  - `g_mlkem_fault.trigger_count = 0`
  - `g_ntt_native_monitor.mismatch_count = 0`
  - `g_ntt_native_monitor.recovered_count = 0`
  - `g_ntt_native_monitor.persistent_count = 0`
  - `status = 0x5A5A5A5A` (`MLK_STATUS_SUCCESS`)
  - `memcmp(ss_out, ss_expected, 32) == 0` (100/100)
- **Classification:** 100/100 `CLEAN_SUCCESS`.

### 3.2 Target F4: Transient Software Bit Flip (Trials 100–199)
- **Setup:**
  ```c
  mlkem_fault_reset();
  mlkem_fault_arm_mid_ntt_locus(stage, b_idx, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
  g_mlkem_fault.persistent = false;
  ntt_native_monitor_reset();
  ```
- **Functions & Hooks Executed:**
  - `poly.c:390-393`: `hook_mid_ntt_post_mul` triggers on stage/index match during initial butterfly evaluation.
  - Bit $b \in [0, 15]$ of intermediate butterfly coefficient $t$ is inverted (`t ^= (1 << bit)`).
  - Parity check in monitor detects $\Delta \ne 0 \lor \Sigma \ne 0$. Monitor increments `mismatch_count` and triggers retry.
  - On retry, hook evaluates `g_mlkem_fault.persistent == false` and does **not** inject (`trigger_count = 1`).
  - Butterfly recalculates cleanly; verifier detects $\Delta_{\text{retry}} = 0 \land \Sigma_{\text{retry}} = 0$.
  - Monitor increments `recovered_count`, clears `mismatch_count`, and continues NTT.
- **Observed Behavior:**
  - `g_mlkem_fault.trigger_count = 1`
  - `g_ntt_native_monitor.recovered_count = 1`
  - `g_ntt_native_monitor.persistent_count = 0`
  - `status = 0x5A5A5A5A`
  - `memcmp(ss_out, ss_expected, 32) == 0` (100/100)
- **Classification:** 100/100 `GENUINE_RECOVERY`.

### 3.3 Target F5A: Recurring Software-Modeled Bit Inversion (Trials 200–299)
- **Setup:**
  ```c
  mlkem_fault_reset();
  mlkem_fault_arm_mid_ntt_locus(stage, b_idx, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_BIT_FLIP, bit, 0, 0);
  g_mlkem_fault.persistent = true;
  ntt_native_monitor_reset();
  ```
- **Functions & Hooks Executed:**
  - Hook injects on initial butterfly pass (`trigger_count = 1`). Mismatch detected.
  - Retry executes; hook injects **again** because `persistent == true` (`trigger_count = 2`).
  - Monitor detects recurring error, increments `persistent_count = 1`, and returns error to caller.
  - `kem.c:484-489`: Fail-stop handler catches abort, executes fallback derivation $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$, sets `status = 0xFFFFFFFF`, and returns.
- **Observed Behavior:**
  - `g_mlkem_fault.trigger_count = 2`
  - `g_ntt_native_monitor.persistent_count = 1`
  - `status = 0xFFFFFFFF` (`MLK_STATUS_FAIL_STOP`)
  - `memcmp(ss_out, ss_rej_oracle, 32) == 0` (100/100)
  - `memcmp(ss_out, ss_expected, 32) != 0` (100/100)
- **Classification:** 100/100 `SAFE_FAIL_STOP`.

### 3.4 Target F5B: Software Force-Value Fault Model (Trials 300–399)
- **Setup:**
  ```c
  mlkem_fault_reset();
  mlkem_fault_arm_mid_ntt_locus(stage, b_idx, NTT_LOCUS_INTERMEDIATE_T, FAULT_TYPE_FORCE_VALUE, 0, 0, 0);
  g_mlkem_fault.persistent = true;
  ntt_native_monitor_reset();
  ```
- **Model Semantics:** Software debug hook unconditionally forces local C variable `*t = 0`. This is an abstract software-level model of catastrophic line failure, **not** an analog model of CMOS transistor latch-up or power-rail short.
- **Observed Behavior:**
  - Recurring zeroing forces retry to fail identically (`trigger_count = 2`).
  - Safe fail-stop triggered (`status = 0xFFFFFFFF`).
  - `memcmp(ss_out, ss_rej_oracle, 32) == 0` (100/100).
- **Classification:** 100/100 `SAFE_FAIL_STOP`.

---

## 4. Independent Output Oracle Verification

To guarantee that telemetry comparisons were not circular, all shared secret outputs were compared against an **independent clean-room oracle**:
- **Clean-room implementation:** Implemented in `production_reproducer.c` as a standalone Keccak-f[1600] permutation and SHAKE256 extendable-output function, compiled completely independently of `symmetric.h` or liboqs.
- **Rejection Key Oracle:** $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$ computed using independent buffer concatenation.
- **Hex Transparency:** All emitted and oracle keys are recorded byte-for-byte in [`production_trial_recalculation.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/production_trial_recalculation.csv) as 64-character lowercase hexadecimal strings (`actual_ss_hex`, `oracle_valid_hex`, `oracle_rej_hex`), allowing third-party verification without re-running binaries.

---

## 5. Outcome Summary Table (Production Objects)

| Target ID | Fault Type | Model Level | Trials | Triggered | Clean Success | Genuine Recovery | Safe Fail-Stop | SDC ($H_2$) | 95% Wilson CI for $H_2$ |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **F12** | None | Production Binary | 100 | 0 | 100 | 0 | 0 | **0** | [0.0%, 3.7%] |
| **F4** | Transient Bitflip | Production Binary | 100 | 100 | 0 | 100 | 0 | **0** | [0.0%, 3.7%] |
| **F5A** | Recurring Bitflip | Production Binary | 100 | 100 | 0 | 0 | 100 | **0** | [0.0%, 3.7%] |
| **F5B** | Force-Value Zero | Production Binary | 100 | 100 | 0 | 0 | 100 | **0** | [0.0%, 3.7%] |
| **Total** | -- | **Production Binary** | **400** | **300** | **100** | **100** | **200** | **0** | **[0.0%, 0.95%]** |

**Conclusion:** The compiled production decapsulation implementation exhibits robust genuine recovery under transient faults and fail-stop safety under recurring software faults, with zero observed Silent Data Corruption ($0/400$, 95% CI: $[0.0\%, 0.95\%]$).
