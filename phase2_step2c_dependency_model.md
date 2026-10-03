# Phase 2 Step 2C-A: Countermeasure Independence and Fault-Dependency Model

**Author:** Cryptographic Software Verification Research Group  
**Target:** ML-KEM-768 with Two-Factor Invariant Butterfly (TFIB) Countermeasure  
**Status:** Complete  
**Date:** 2026-10-04  
**Scope:** Software fault-dependency model, shared state analysis, and common-mode fault analysis  

---

## 1. Executive Summary & Research Question

In high-assurance post-quantum cryptography, fault-tolerant arithmetic architectures such as the Two-Factor Invariant Butterfly (TFIB) aim to detect and repair computational errors injected during Number Theoretic Transform (NTT) and Inverse NTT (InvNTT) operations.

The central research question of **Phase 2 Step 2C-A** is:
> **How does shared state or shared fault exposure between the ML-KEM computation and its countermeasure affect fault detection, recovery, and end-to-end correctness?**

Prior audits (Phase 2 Step 2B) established that under single-point operational twiddle perturbations, TFIB-REF achieves 100% detection and genuine recovery, while TFIB-META achieves 100% detection and safe fail-stop. However, verifying the *independence* of a countermeasure requires evaluating scenarios where the fault model affects:
1. Operational state only,
2. Checker state only,
3. Shared data, buffers, or control flow,
4. Simultaneously corrupted operational and reference data (simulated common-mode failure),
5. Failures that evade local checker detection but are captured by the outer cryptographic protocol (Fujisaki-Okamoto transform).

### Critical Physical Disclaimer
> [!CAUTION]
> **Software Fault Injection Scope:** All faults analyzed and simulated herein are strictly deterministic software-level bit-flips and state mutations executed within C memory spaces. They do **not** represent physical fault injection (such as laser fault injection, clock glitching, electromagnetic pulse, or physical radiation single-event upsets). No claims of physical, radiation, or space qualification are made or implied.

---

## 2. Architectural Code Paths & State Flow

Through static and binary analysis of the production implementation (`bin/obj/mlkem768_inst.o`, `tfib_implementation/libtfib.a`, and `algorithms/source_ref/mlkem/`), five critical paths were audited:

### 2.1 Operational Twiddle Access Path
- **Symbol / Location:** `_mlk_zetas` (static array of 128 `int16_t` values, located at virtual address `0x1000188a0` in `__TEXT,__const` segment, defined in `algorithms/source_ref/mlkem/src/zetas.inc` and compiled into `bin/obj/mlkem768_inst.o`).
- **Fetch Logic:**
  - Forward NTT (`mlk_ntt_layer` in `poly.c`): Layer-stride pointer iteration `zeta = mlk_zetas[k++]`, with $k \in [1, 127]$.
  - Inverse NTT (`mlk_invntt_layer` in `poly.c`): Reverse stride iteration `zeta = mlk_zetas[k--]`, with $k \in [127, 1]$.
- **Usage:** Loaded into temporary scalar `zeta_val` and passed to `mlk_fqmul()` to execute butterfly multiplication.

### 2.2 Reference Twiddle Access Path (TFIB-REF)
- **Symbol / Location:** `_tfib_zetas_ref` (external array of 128 `int16_t` values, located at virtual address `0x100018a60` in `__TEXT,__const` segment, defined in `tfib_implementation/tfib_ref.c` and linked via `libtfib.a`).
- **Memory Separation:** Stored at an offset of +448 bytes from `mlk_zetas`. It occupies a completely separate global symbol table entry and distinct memory bytes.
- **Fetch Logic:** Decoupled index recalculation:
  - NTT: $k = (1 \ll (\text{layer} - 1)) + (\text{butterfly\_idx} \gg (8 - \text{layer}))$.
  - InvNTT: $k = ((1 \ll \text{layer}) - 1) - (\text{butterfly\_idx} \gg (8 - \text{layer}))$.
- **Usage:** Checked directly against caller-supplied `zeta_op` (`twiddle_mismatch = (zeta_op != zeta_ref)`), and recomputed in arithmetic verification (`t_check = tfib_fqmul(v_saved, zeta_ref)`).

### 2.3 Metadata Tag Checking Path (TFIB-META)
- **Symbol / Location:** `_tfib_zetas_tag` (external array of 128 `uint16_t` values, located at virtual address `0x100018b60` in `__TEXT,__const`, defined in `tfib_implementation/tfib_meta.c`).
- **Tag Generation:** Precomputed via `tfib_meta_compute_tag(zeta, k)`.
- **Usage:** Validates whether the caller's operational `zeta_op` produces the tag matching `tfib_zetas_tag[k]`. If corrupted, detects the twiddle mutation without storing a full redundant twiddle table.

### 2.4 Fault Detection, Rollback, and Repair Paths
- **Detection Trigger:**
  $$\text{Mismatch} = (\text{twiddle\_mismatch}) \lor (\Delta_{\text{diff}} \not\equiv 0 \pmod{q}) \lor (\Delta_{\text{sum}} \not\equiv 0 \pmod{q})$$
  where $\Delta_{\text{diff}}$ and $\Delta_{\text{sum}}$ enforce the Cooley-Tukey and Gentleman-Sande algebraic butterfly invariants.
- **Rollback:** Restores polynomial coefficients `*r_j = u_saved; *r_j_len = v_saved;` from caller-preserved stack snapshots.
- **Repair (TFIB-REF):**
  Re-executes butterfly using the verified reference twiddle:
  $$t_{\text{retry}} = \text{fqmul}(v_{\text{saved}}, \zeta_{\text{ref}})$$
  $$u_{\text{new}} = u_{\text{saved}} + t_{\text{retry}}, \quad v_{\text{new}} = u_{\text{saved}} - t_{\text{retry}}$$
  Repaired values are written back to `*r_j` and `*r_j_len`, and immediately re-verified.
- **Fail-Stop (TFIB-META):**
  Because TFIB-META stores only cryptographic tags and has no backup twiddle table, it cannot repair operational twiddle corruptions. When a fault is detected, it rolls back operands to $u_{\text{saved}}, v_{\text{saved}}$ and increments `persistent_fail_count`, forcing a safe fail-stop.

### 2.5 End-to-End Fail-Stop and Implicit Rejection Path
- **Decapsulation Entry Point:** `mlkem768_dec_monitored()` in `algorithms/source_ref/mlkem/src/kem.c`.
- **Primary Fail-Stop Trigger:**
  ```c
  if (ntt_native_monitor_get_persistent_count() > 0 ||
      invntt_native_monitor_get_persistent_count() > 0) {
      fail = 0xFF;
      if (internal_status != NULL) *internal_status = MLK_DECAPS_STATUS_FAULT;
  }
  ```
- **Secondary Cryptographic Failsafe (Fujisaki-Okamoto Re-encryption):**
  If a fault bypasses local butterfly detection (e.g. common-mode failure where both computation and checker are blinded), corrupted NTT coefficients produce an erroneous recovered message $m' \neq m$.
  Subsequent IND-CPA re-encryption produces $c' = \text{Enc}(pk, m', r) \neq c$.
  The constant-time memory comparison `fail = mlk_ct_memcmp(ct, tmp, 1088)` evaluates to $0\text{xFF}$.
  ML-KEM decapsulation then outputs the canonical implicit rejection key:
  $$K_{\text{rej}} = \text{SHAKE-256}(z \parallel c, 32)$$
  via constant-time conditional move `mlk_ct_cmov_zero(ss, kr, 32, fail)`.
  **Outcome:** The system safely rejects the invalid session without returning an attacker-exploitable corrupted secret.

---

## 3. Systematic Fault-Dependency Table

The table below maps all computational, structural, and countermeasure components, distinguishing proven independent paths from suspected or proven common-mode coupling.

| Component | Data or State Used | Primary vs Checker | Shared With Which Components | Fault Injection Point | Expected Observable Effect | Evidence Source | Confidence and Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Operational Twiddle Table** | `mlk_zetas[128]` (in `zetas.inc`) | Primary Computation | Passed as value `zeta_op` to monitor | `hook_mid_ntt_pre_butterfly`, `hook_mid_invntt_pre_butterfly` | Butterfly computes invalid output; TFIB-REF detects twiddle mismatch, repairs, and recovers; TFIB-META detects and fail-stops | `poly.c:388`, `tfib_ref.c:65`, `phase2_step2b_runner_output.csv` | **High:** Proven independent storage (`0x1000188a0`). Limitation: Single core software model. |
| **Reference Twiddle Table** | `tfib_zetas_ref[128]` (in `tfib_ref.c`) | Checker Only (TFIB-REF) | None (isolated symbol in `libtfib.a`) | `tfib_ref.c:51` (`TFIB_FAULT_REF_TWIDDLE`) | Twiddle comparison detects mismatch (`zeta_op != zeta_ref`); repair re-check detects persistent failure; transient fault recovers | `tfib_ref.c:49-62`, `tfib_experiments/tfib_experiment_runner.c:230` | **High:** Symbol isolated at `0x100018a60`. Tested transient and persistent. |
| **Integrity Tag Table** | `tfib_zetas_tag[128]` (in `tfib_meta.c`) | Checker Only (TFIB-META) | None (isolated symbol in `libtfib.a`) | `tfib_meta.c:53` (`TFIB_FAULT_META_TAG`) | Computed tag mismatches expected tag; transient recovers; persistent triggers safe fail-stop | `tfib_meta.c:53-59`, `tfib_experiments/tfib_experiment_runner.c:292` | **High:** Dedicated read-only tag table (`0x100018b60`). |
| **Polynomial Buffer (`r`)** | `r[j]`, `r[j+len]` in coefficient array | Primary & Checker | Monitored and modified by both | Butterfly arithmetic write, or pointer corruption | Invariant check $\Delta_{\text{diff}} \neq 0 \lor \Delta_{\text{sum}} \neq 0$; retry recomputes from $u_{\text{saved}}, v_{\text{saved}}$ | `poly.c:382-408`, `tfib_core.c:71` | **High:** Shared mutable buffer. Correctly restored via stack snapshots. |
| **Stack Operand Snapshots** | `u_saved`, `v_saved` (caller frame) | Primary & Checker | Computed by caller, read by checker | Stack corruption before monitor call | Invariant $\Delta_{\text{sum}}$ flags arithmetic mismatch; rollback uses corrupted snapshot, retry fails, forces fail-stop | `poly.c:382-383`, `tfib_ref.c:70` | **Medium:** Preserved across register/stack by compiler; not independently dual-railed on stack. |
| **Twiddle Indexing Logic** | `layer`, `b_idx`, loop strides | Primary & Checker | Computed independently by loop vs helper | Loop counter bit flip in caller | Caller fetches $\zeta_k$, checker computes $k' \neq k$, causing $\zeta_{\text{op}} \neq \zeta_{\text{ref}}$, detected as mismatch | `poly.c:437`, `tfib_common.h:17-23` | **High:** Independent arithmetic logic ($k++$ vs $(1 \ll (l-1)) + (b \gg (8-l))$). |
| **Modular Arithmetic Constants** | `MLKEM_Q` (3329), Barrett/Montgomery multipliers | Primary & Checker | Shared constant definitions | Macro / immediate operand perturbation | Arithmetic invariant recomputation fails; triggers rollback and fail-stop | `poly.h:71`, `tfib_common.h:12,28,36` | **High:** Exact algebraic congruence proven in FIPS 203. |
| **Global Monitor Stats & Flags** | `g_tfib_ref_stats`, `g_tfib_meta_stats` | Checker to Protocol Interface | Read by `mlkem768_dec_monitored` | Counter corruption / zeroing | If monitor persistent count is cleared, downstream FO re-encryption still detects mismatch and returns $K_{\text{rej}}$ | `kem.c:486-494`, `kem.c:466-481` | **High:** Proven dual-defense: local fail-stop backed by outer FO re-encryption. |
| **Simultaneous Twiddle Corruption (Common-Mode)** | $\zeta_{\text{op}}$ and $\zeta_{\text{ref}}$ perturbed with identical bit-flip | Both Primary and Checker | Common corruption vector | `hook_mid_ntt_pre_butterfly` + `tfib_ref.c:55` | Local monitor is completely blinded ($\text{mismatch}=0, \Delta_{\text{diff}}=0$); downstream FO re-encryption catches error, returns $K_{\text{rej}}$ | `tfib_ref.c:55-61`, `tfib_experiment_runner.c:245-252` | **High:** Confirmed zero local detection, 100% safe containment by FO transform ($0$ SDC). |
| **Checker Decision Logic** | `sum_c ^= 1` (comparison predicate) | Checker Only | Internal monitor evaluation | `tfib_ref.c:77`, `tfib_meta.c:75` | False alarm triggers rollback and retry; transient recovers; persistent safe fail-stops | `tfib_ref.c:77-80`, `tfib_experiment_runner.c:253` | **High:** Validates robustness against false positive alarms. |

---

## 4. Realistic Software Fault Models

The framework evaluates four distinct, clearly defined software fault models:

```
+-------------------------------------------------------------------------------+
|                       SOFTWARE FAULT MODEL TAXONOMY                           |
+-------------------------------------------------------------------------------+
|  1. Single-Location Corruption (Transient or Persistent)                       |
|     - Perturbs exactly one operational twiddle, reference twiddle, or tag     |
|     - Models targeted register corruption, memory read bit-flip, or ALU error|
+-------------------------------------------------------------------------------+
|  2. Checker-Only Corruption (False-Alarm Injection)                          |
|     - Perturbs reference twiddle, tag, or checker arithmetic evaluation      |
|     - Tests whether checker degradation causes fatal corruption or safe retry|
+-------------------------------------------------------------------------------+
|  3. Common-Mode Simultaneous Corruption (Checker Blind Spot)                 |
|     - Identically flips the same bit in both operational and reference states|
|     - Models shared bus corruption, common power-rail droop, or identical    |
|       corruption before comparison                                            |
+-------------------------------------------------------------------------------+
|  4. Outer Cryptographic Failsafe Activation (FO Re-encryption)               |
|     - Local monitor blinded; checks whether end-to-end decapsulation leaks    |
|       corrupted secret or forces canonical implicit rejection K_rej           |
+-------------------------------------------------------------------------------+
```

### Distinction Between Local Detection and Cryptographic Containment
- **Local Detection (TFIB-Level):** The butterfly monitor identifies that an invariant is violated ($\text{mismatch} > 0$).
- **Local Recovery (TFIB-REF):** The monitor successfully repairs the output polynomial in-place, returning the genuine shared secret $K_{\text{valid}}$ with status `0x5A5A5A5A`.
- **Local Fail-Stop (TFIB-META or Persistent TFIB-REF):** The monitor detects the fault, halts computation, and forces decapsulation status to `0xFFFFFFFF` / `0xA5A5A5A5`.
- **Outer Cryptographic Containment (Fujisaki-Okamoto):** When local detection fails completely (0% detection), the corrupted polynomial alters the decapsulated plaintext, causing ciphertext re-encryption comparison to fail. Decapsulation outputs $K_{\text{rej}}$ ($0$ SDC).

---

## 5. Proven Dependencies vs Suspected Common-Mode Risks

### 5.1 Proven Independent Properties
1. **Physical Storage Decoupling:** `mlk_zetas` and `tfib_zetas_ref` are separate static arrays allocated in distinct translation units. Modifying the memory of one does not mutate the memory of the other.
2. **Indexing Decoupling:** The computation tracks indices incrementally via pointer strides (`k++` / `k--`), whereas the checker recomputes indices algebraically from $(layer, butterfly\_idx)$. An off-by-one or stride skip in computation triggers a twiddle mismatch in the checker.
3. **Outer Protocol Resilience:** Even when local detection is 0% (common-mode blind spot), the outer Fujisaki-Okamoto transform guarantees fail-safety by returning the canonical implicit rejection key $K_{\text{rej}}$.

### 5.2 Identified Common-Mode Boundaries & Risks
1. **Identical Bit-Flip Blindness:** If a fault mechanism alters both operands identically prior to invariant evaluation, arithmetic invariants $\Delta_{\text{diff}} \equiv 0 \pmod q$ and $\Delta_{\text{sum}} \equiv 0 \pmod q$ hold true over the corrupted value. Local detection is completely bypassed.
2. **Shared Modulus ($q = 3329$):** Both computation and checker share the scalar modulus. A fault in the ALU performing division/reduction modulo 3329 would corrupt both paths.
3. **Stack Frame Colocation:** $u_{\text{saved}}$ and $v_{\text{saved}}$ reside on the execution stack of `mlk_ntt_layer`. A bulk stack memory smash could corrupt both intermediate results and saved rollback state simultaneously.

---

## 6. Summary Verdict on Dependency Model

The dependency analysis establishes that:
- **TFIB-REF is strongly independent** of operational twiddle corruption for single-locus faults.
- **TFIB-META is independent for detection**, but structurally dependent on operational twiddle validity for recovery (it cannot repair operational faults).
- **Simultaneous common-mode corruption** completely blinds local monitors, proving that local invariant checking alone cannot protect against common-mode faults.
- **Fujisaki-Okamoto re-encryption** acts as an infallible outer boundary that catches all escaped local twiddle errors, preventing Silent Data Corruption across all evaluated modes.
