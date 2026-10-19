# Phase 5: Source-Level Fault Injection Architecture and Mapping

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Document:** `phase5_recovery_trust_audit/source_level_injection_map.md`

---

## 1. Scope and Design Principles

To adhere strictly to audit principles:
1. **Zero Test-Wrapper Simulation:** No test wrapper artificially assigns return statuses, incremented mismatch counters, or synthetic classifications. The cryptographic decapsulation function (`mlkem768_dec_monitored`) executes in its entirety.
2. **Physical Hardware Fidelity:** Each fault target models a concrete physical disturbance (e.g., Single-Event Upset (SEU) in SRAM, transient register glitch via clock/EM pulsing, or stuck-at line faults).
3. **Isolation and Reproducibility:** Original cryptographic files in `algorithms/source_ref/mlkem/` are preserved. The fault harness links directly with the compiled cryptographic object (`bin/obj/mlkem768_inst.o`) and provides source-level hook implementations to intercept execution at the exact points where recovery trust decisions occur.

---

## 2. Detailed Injection Mechanism by Target

### FT1: Saved Operand Corruption Post-Capture (`SAVED_OPERAND_POST_CAPTURE`)
- **Physical Mechanism:** Radiation-induced SEU in a register holding the spilled local variable `u_saved`, or laser fault targeting SRAM stack memory while butterfly calculations proceed.
- **Source Location:** `algorithms/source_ref/mlkem/src/poly.c:382` (post-capture) / `mlkem_fault_hooks.c:603` (monitor entry).
- **Injection Hook:** Mutates `u_saved` parameter upon entry to `native_ntt_monitor_butterfly` via bit flip ($u_{\text{saved}} \oplus (1 \ll b)$).
- **Execution Flow:**
  1. The initial butterfly completed with true inputs $(u, v)$.
  2. Monitor calculates $diff_c$ and $sum_c$ using corrupted $u_{\text{saved}}$.
  3. Because $sum_c = (r_j + r_{j+\text{len}} - 2 \cdot u_{\text{saved}}) \not\equiv 0 \pmod{3329}$, the monitor flags an invariant violation (`mismatch_count++`).
  4. In-place rollback restores $*r_j = u_{\text{saved}}$ (writing the corrupted snapshot back into the polynomial buffer).
  5. Retry recomputes $u_{\text{new}}$ and $v_{\text{new}}$ from the corrupted operand.
  6. The recovery verifier computes $sum_{\text{retry}} = (u_{\text{new}} + v_{\text{new}} - 2 \cdot u_{\text{saved}}) \pmod{3329}$.
  7. Since $u_{\text{new}} + v_{\text{new}} = 2 \cdot u_{\text{saved}}$, the verifier algebraically obtains $0$.
  8. Monitor concludes the retry was successful (`recovered_count++`, `persistent_count == 0`).
  9. The corrupted polynomial propagates through decapsulation.

---

### FT2: Snapshot Corruption Pre-Retry (`SNAPSHOT_PRE_RETRY`)
- **Physical Mechanism:** Clock glitch during the transition from detection to recovery handler, corrupting the snapshot value in the processor accumulator or register bank before the rollback assignment $*r_j = u_{\text{saved}}$.
- **Source Location:** `mlkem_fault_hooks.c:634` (inside `if (allow_retry)` block).
- **Injection Hook:** Introduces an additive glitch ($u_{\text{saved}} + 100$) specifically after the initial mismatch has triggered, immediately before `*r_j = u_saved;`.
- **Execution Flow:**
  1. Initial butterfly experienced a transient glitch; mismatch is correctly detected.
  2. Before rollback, the snapshot is perturbed.
  3. Recomputation uses perturbed snapshot.
  4. Verifier passes due to tautological algebraic identity.
  5. Recovery falsely declared.

---

### FT3: Monitor State Corruption (`MONITOR_PERSISTENT_COUNT_ZERO`)
- **Physical Mechanism:** Bit flip or zeroing of a peripheral register / static variable in `.bss` / `.data` section representing error flags.
- **Source Location:** `mlkem_fault_hooks.c:658` / `kem.c:486`.
- **Injection Hook:** A persistent fault is injected during retry, correctly triggering `g_ntt_native_monitor.persistent_count++`. Immediately after incrementing, a fault hook zeroes `g_ntt_native_monitor.persistent_count = 0`.
- **Execution Flow:**
  1. Decapsulation proceeds to line 486 of `kem.c`:
     `if (ntt_native_monitor_get_persistent_count() > 0)`
  2. Condition evaluates to `false` because the count was cleared to `0`.
  3. Decapsulation fail-stop is completely bypassed; execution falls through to the FO verification logic.

---

### FT4: Retry Control State Corruption (`MONITOR_ALLOW_RETRY_FORCE`)
- **Physical Mechanism:** Control flow glitch or SEU flipping the configuration byte of the monitor in memory from `allow_retry = false` (Fail-Stop) to `allow_retry = true`.
- **Source Location:** `mlkem_fault_hooks.c:631` (`if (g_ntt_native_monitor.allow_retry)`).
- **Injection Hook:** The system is explicitly configured with `allow_retry = false`. When an invariant violation is detected, a glitch forces `allow_retry` to `true`.
- **Execution Flow:**
  1. Expected behavior in fail-stop mode: immediately increment `persistent_count` and abort.
  2. Corrupted behavior: executes in-place rollback and retry, altering system timing and re-executing vulnerable arithmetic paths.

---

### FT5: Verifier Input Corruption (`VERIFIER_INPUT_CORRUPT`)
- **Physical Mechanism:** Glitch on address bus or register during the operand fetch for the verification equation.
- **Source Location:** `mlkem_fault_hooks.c:860` (`int16_t d_verify = (int16_t)(v_saved - u_saved);`).
- **Injection Hook:** Inverts bit $b$ of $d_{\text{verify}}$ right before computing $v_{\text{verify}} = \text{fqmul}(d_{\text{verify}}, \zeta)$.
- **Execution Flow:**
  1. The butterfly retry recomputation produced completely clean, correct outputs.
  2. The verifier checks $v_{\text{new}}$ against $v_{\text{verify}}$.
  3. Because $d_{\text{verify}}$ was glitched, $diff_{\text{retry}} \neq 0$.
  4. The monitor declares a false persistent failure (`persistent_count++`).
  5. Decapsulation triggers unnecessary fail-stop abort (spurious denial of service).

---

### FT6: Verifier Result Corruption (`VERIFIER_RESULT_FORCE_ZERO`)
- **Physical Mechanism:** Instruction skip or condition-code flag glitch (`Z-flag` force set) on the recovery branch condition `if (diff_retry == 0 && sum_retry == 0)`.
- **Source Location:** `mlkem_fault_hooks.c:655` / `mlkem_fault_hooks.c:865`.
- **Injection Hook:** A persistent fault is injected so that $diff_{\text{retry}} \neq 0$. Right before the branch evaluation, a fault hook forces `diff_retry = 0` and `sum_retry = 0`.
- **Execution Flow:**
  1. Arithmetic output is corrupt.
  2. Verifier evaluation is corrupted to 0.
  3. Monitor branches to `recovered_count++` instead of `persistent_count++`.
  4. False recovery is certified.

---

### FT7: Transient ALU Glitch with Clean Retry (`RETRY_TRANSIENT_CLEAN`)
- **Physical Mechanism:** Single-event transient (SET) on multiplier during first pass; no fault on second pass.
- **Source Location:** `poly.c:389` (`mlk_fqmul`).
- **Injection Hook:** Standard transient bit flip on intermediate product $t$; `g_mlkem_fault.persistent = false`.
- **Execution Flow:**
  1. Mismatch caught by monitor.
  2. Clean retry executed.
  3. Verifier checks clean outputs and passes.
  4. Decapsulation outputs authentic shared secret matching external oracle.

---

### FT8: Persistent ALU Fault (`RETRY_PERSISTENT_ALU`)
- **Physical Mechanism:** Permanent hardware defect (stuck-at line or latch failure) in arithmetic logic unit.
- **Source Location:** `poly.c:389` (`mlk_fqmul`).
- **Injection Hook:** Bit flip re-applied identically during initial computation and retry recomputation; `g_mlkem_fault.persistent = true`.
- **Execution Flow:**
  1. Initial mismatch detected.
  2. Retry recomputes, but fault strikes again.
  3. Verifier detects non-zero difference.
  4. Monitor sets `persistent_count = 1`.
  5. Decapsulation enforces `fail = 0xFF` and sets `status = MLK_DECAPS_STATUS_FAULT`.

---

### FT9: Combined Fault: Monitor Blinded + Downstream FO Bypass (`FO_PREDICATE_BYPASS_CORRUPT_KEY`)
- **Physical Mechanism:** Coordinated multi-fault injection: fault 1 blinds or clears the monitor's fail-stop indicator (`persistent_count = 0`), and fault 2 glitches the decapsulation comparison flag (`fail = 0`).
- **Source Location:** `kem.c:471` (`hook_decaps_verify_flag`) and `kem.c:486`.
- **Injection Hook:** A persistent fault corrupts the decrypted polynomial; `persistent_count` is forced to 0, and `hook_decaps_verify_flag` forces `*fail_flag = 0`.
- **Execution Flow:**
  1. Decrypted message is erroneous.
  2. Monitor fail-stop does not trigger because `persistent_count == 0`.
  3. Fujisaki-Okamoto comparison yields mismatch, but `fail` is glitched to `0`.
  4. Dual-rail check in `kem.c:497`: if only `fail` was glitched, `fail != fail_chk` catches it! To bypass, both flags or ciphertext comparison must be bypassed.
  5. If bypassed, `mlk_ct_cmov_zero(ss, kr, MLKEM_SYMBYTES, 0)` copies the corrupted decrypted session key $kr$ directly to output $ss$.
  6. **Result:** Silent Data Corruption (SDC).

---

### FT10: Clean Baseline Control (`CLEAN_CONTROL`)
- **Physical Mechanism:** Pristine nominal execution.
- **Source Location:** None.
- **Injection Hook:** No hooks armed; verifies baseline functionality and oracle alignment.
