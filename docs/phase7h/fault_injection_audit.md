# Phase 7H: Fault-Injection Mechanism Audit & Threat Class Characterization

## 1. Systematic Audit of Fault Classes

Each of the 8 fault classes evaluated in Phase 7G was audited against the native C implementation:

| Class | Injected Locus in Code | Native Injection Point | Perturbation Mechanism | Actual Computation Perturbed? | Monitor Detection Mechanism |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Class 1** | `hook_mid_ntt_post_mul` | Intermediate product `t` before add/sub | Single bit flip (`*t ^= (1 << b)`) | **Yes** (directly mutates `t`) | **Recomputed-$t$ Only**: Invariant checks against $t_{\text{check}} = \text{fqmul}(v, \zeta)$. |
| **Class 2** | `hook_mid_ntt_pre_butterfly` | Twiddle operand `zeta_val` before `fqmul` | Single bit flip (`zeta_val ^= (1 << b)`) | **Yes** (modifies multiplier operand) | **None (Bypassed)**: Checker receives the same mutated `zeta_val`. |
| **Class 3** | `hook_mid_ntt_butterfly` | Output register `*r_j` after add | Single bit flip (`*r_j ^= (1 << b)`) | **Yes** (directly mutates output) | **Both Modes**: Difference and sum checks detect mismatch. |
| **Class 4** | `hook_mid_ntt_butterfly` | Output register `*r_j` after add | Additive glitch (`*r_j += delta`) | **Yes** (directly mutates output) | **Both Modes**: Difference and sum checks detect mismatch. |
| **Class 5** | Pre-decapsulation input | Ciphertext byte array `ct_corrupted` | Single bit flip (`ct[i] ^= (1 << b)`) | **Yes** (modifies external ciphertext) | **FO Re-encryption**: Fails re-encryption check in `kem.c`. |
| **Class 6** | `hook_mid_ntt_butterfly` | Output register with `persistent = true` | Repeated bit flip on every retry | **Yes** (simulates stuck ALU line) | **Persistent Fail-Stop**: Repeated failure sets `persistent_count > 0`. |
| **Class 7** | `hook_decaps_verify_flag` | Comparison flag `fail` in `kem.c` | Toggled comparison (`fail ^= 1`) | **Yes** (corrupts FO condition flag) | **Reverse Dual-Rail**: Caught by `fail != fail_chk`. |
| **Class 8** | Negative control | None | None | **No** (Nominal execution) | **Zero False Positives**: Authentic session key produced. |

---

## 2. In-Depth Audit of Class 1: Intermediate Product $t$

- **Target Variable**: Intermediate Montgomery product $t = \text{fqmul}(v, \zeta)$ in `poly.c` line 389.
- **Verification of Genuine Physical Perturbation**: The hook `hook_mid_ntt_post_mul(&t)` directly modifies the pointer value `*t_ptr`. This modified `t` is directly fed into `r[j + len] = r[j] - t` and `r[j] = r[j] + t`. The fault is strictly computational, not a harness mock.
- **The Multiplier Blind Spot**:
  When $t$ is corrupted to $t^* = t \oplus \delta$:
  $$r[j] = u + t^*, \quad r[j+\text{len}] = u - t^*$$
  The difference check evaluates:
  $$D = (r[j] - r[j+\text{len}]) - 2t_{\text{check}} = 2t^* - 2t_{\text{check}} \pmod q$$
  - Under Reused-$t$, $t_{\text{check}} = t^*$. Thus $D \equiv 0 \pmod q$, completely bypassing detection.
  - Under Recomputed-$t$, $t_{\text{check}} = \text{fqmul}(v, \zeta) = t$. Thus $D = 2(t^* - t) = 2\delta \not\equiv 0 \pmod q$.
- **Audit Conclusion**: The multiplier blind spot is mathematically proven and empirically verified. Reused-$t$ achieved only 4.7% recovery (benign collisions), while Recomputed-$t$ achieved 100.0% recovery.

---

## 3. In-Depth Audit of Class 2: Twiddle Factor Corruption ($\zeta$)

- **Target Variable**: Twiddle coefficient `zeta_val` in `poly.c` line 381.
- **Root Cause of Non-Detection**:
  In `poly.c`, `zeta_val` is passed to `native_ntt_monitor_butterfly(..., zeta_val, ...)`.
  Inside `native_ntt_monitor_butterfly`:
  ```c
  if (g_ntt_native_monitor.mode == NTT_NATIVE_MONITOR_RECOMPUTED_T) {
      t_check = monitor_fqmul(v_saved, zeta);
  }
  ```
  The checker recomputes using the **same** corrupted `zeta_val`.
- **The Dead `g_trusted_zetas` Table**:
  In [mlkem_fault_hooks.c](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) line 555, a static constant array `g_trusted_zetas[128]` is declared, but it is **never referenced anywhere in the codebase**.
- **Cryptographic Backstop**: Although the butterfly monitor is blind to twiddle corruption, the altered polynomial produces an invalid decapsulation candidate $\mathbf{m}^*$, which fails Fujisaki-Okamoto re-encryption ($\hat{c}' \neq c$). This triggers safe implicit rejection ($K_{\text{rej}}$) in 96.7% of trials (with the remaining 3.3% being benign non-functional bit flips), yielding **0.0% undetected key corruption**.

---

## 4. In-Depth Audit of Class 4: Asymmetric vs Symmetric Perturbations

- **Discrepancy Uncovered in Phase 7G**:
  In Phase 7G, Class 4 was titled "Symmetric Output Perturbation," but the code executed:
  ```c
  mlkem_fault_arm_mid_ntt_locus(stage, butterfly, NTT_LOCUS_OUTPUT_ADD, FAULT_TYPE_ADDITIVE_GLITCH, 0, delta, 0);
  ```
  This applied an additive glitch **only** to $r[j]$ (`NTT_LOCUS_OUTPUT_ADD`).
- **Mathematical Analysis of Genuine Symmetric Faults**:
  If a physical single event upset perturbs both adjacent registers simultaneously:
  $$u^* = u' + \Delta, \quad v^* = v' + \Delta$$
  Then:
  $$D = (u^* - v^*) - 2t = (u' + \Delta) - (v' + \Delta) - 2t = (u' - v') - 2t \equiv 0 \pmod q$$
  The **Difference check completely misses symmetric faults** ($D \equiv 0$).
  However, the **Sum check** detects it:
  $$S = (u^* + v^*) - 2u = (u' + \Delta) + (v' + \Delta) - 2u = 2\Delta \not\equiv 0 \pmod q$$
- **Anti-Symmetric Dual Faults ($u' + \Delta, v' - \Delta$)**:
  Conversely, an anti-symmetric fault bypasses the Sum check ($S \equiv 0$), but is caught by the Difference check ($D = 2\Delta$).
- **Audit Conclusion**: The dual invariant (`Diff && Sum`) is mathematically necessary to provide comprehensive coverage against arbitrary two-register perturbations.
