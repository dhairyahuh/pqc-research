# Recovery Outcome Validation and Integrity Review

**Auditor:** Skeptical Cryptographic Implementation Auditor  
**Investigation Focus:** The 100 reported recoveries in Baseline Variant A for Target T3 (`T3_SAVED_OPERAND_CORRUPT`) and Target T4 (`T4_RETRY_MULTIPLIER_GLITCH`)  
**Target Code:** `algorithms/source_ref/mlkem_fault_hooks.c:600-664` (NTT monitor) and `804-874` (InvNTT monitor)  

---

## 1. Audit Framework for Recovery Claims

Under cryptographic audit standards, an execution classified as `FAULT_DETECTED_AND_RECOVERED` must satisfy four rigorous criteria:
1. **Physical Recovery Execution**: The recovery rollback and recomputation logic must actually execute (monitored via hardware/software counters).
2. **Independent Ground-Truth Verification**: The recovered output must match ground-truth clean decapsulation ($K_{\text{out}} == K_{\text{expected}}$) byte-for-byte via an independent cryptographic oracle.
3. **Non-Tautological Verification**: The verification check authorizing key release must not rely on the same corrupted operands or constants that caused the error.
4. **Distinction from Downstream Containment**: The recovery must happen at the intermediate layer; it must not be a byproduct of the Fujisaki-Okamoto transform or LWE noise absorption.

---

## 2. In-Depth Trace: Target T3 (Saved Operand Corruption)

### Code Execution Trace
1. **Snapshot Latching** (`algorithms/source_ref/mlkem/src/poly.c:557-558`):
   ```c
   int16_t u_saved = r[j];
   int16_t v_saved = r[j + len];
   ```
2. **Fault Injection** (`algorithms/source_ref/mlkem/src/poly.c:564` $\to$ `mlkem_fault_hooks.c:724`):
   ```c
   *r_j = (int16_t)apply_fault(*r_j, ...);
   ```
3. **Butterfly Computation** (`poly.c:566-575`):
   Operates on the corrupted `*r_j`.
4. **Monitor Verification** (`mlkem_fault_hooks.c:818-829`):
   ```c
   int32_t sum_c = ((int32_t)(*r_j) - (int32_t)(u_saved + v_saved)) % 3329;
   if (sum_c != 0 || diff_c != 0) { ... }
   ```
   Mismatch is detected because `*r_j` was mutated.
5. **Rollback & Recomputation** (`mlkem_fault_hooks.c:837-855`):
   ```c
   *r_j = u_saved;
   *r_j_len = v_saved;
   int16_t t_retry = u_saved;
   int16_t u_new = monitor_barrett_reduce((int16_t)(t_retry + v_saved));
   int16_t d_retry = (int16_t)(v_saved - t_retry);
   int16_t v_new = monitor_fqmul(d_retry, zeta);
   *r_j = u_new;
   *r_j_len = v_new;
   ```
6. **Post-Retry Verification** (`mlkem_fault_hooks.c:857-866`):
   Compares `u_new` and `v_new` against `u_saved` and `v_saved`. Since both checks pass, `recovered_count++`.

### Auditor Verdict on Target T3
- **Claim:** "100% recovery under snapshot corruption."
- **Audit Finding:** **INVALID TARGET SPECIFICATION / MISNOMER**.
  - The hook mutated `*r_j` *after* `u_saved` was latched. The snapshot `u_saved` was **never corrupted**.
  - The mechanism successfully recovered from an *operating register glitch*, but did NOT test snapshot corruption.
- **Tautological Verifier Vulnerability:**
  If an actual radiation SEU corrupts `u_saved` in memory:
  - Line 838 copies the corrupted `u_saved` into `*r_j`.
  - Line 842-845 computes `u_new` and `v_new` using the corrupted `u_saved`.
  - Line 857 verifies `u_new` against the same corrupted `u_saved`.
  - Line 866 increments `recovered_count++` and declares recovery!
  - **Conclusion:** The verifier is tautological with respect to snapshot memory. Corrupting `u_saved` will produce corrupted decapsulation output while reporting false recovery.

---

## 3. In-Depth Trace: Target T4 (Retry Multiplier Glitch)

### Code Execution Trace
1. **Target Arming**: Arms `NTT_LOCUS_INTERMEDIATE_T` during forward Cooley-Tukey NTT.
2. **Context**: Forward NTT is invoked inside ML-KEM decapsulation during the Fujisaki-Okamoto re-encryption step (`indcpa_enc()`).
3. **Fault Injection** (`mlkem_fault_hooks.c:695`):
   Mutates `*t_ptr` (the result of `fqmul(r[j+len], zeta)`) before addition/subtraction.
4. **Butterfly Invariant Check** (`mlkem_fault_hooks.c:618-626`):
   ```c
   t_check = monitor_fqmul(v_saved, zeta);
   diff_c = ((int32_t)(*r_j) - (int32_t)(*r_j_len) - 2 * (int32_t)t_check) % 3329;
   ```
   Since `t` was corrupted, $diff\_c \neq 0$. `mismatch_count++`.
5. **Rollback & Recomputation** (`mlkem_fault_hooks.c:635-650`):
   Restores `u_saved` and `v_saved`. Recomputes `t_retry = fqmul(v_saved, zeta)`.
   Because the fault was transient (`trigger_count == 1`, `persistent == false`), the retry recomputation runs cleanly!
6. **Outcome**:
   `diff_retry == 0 && sum_retry == 0` $\implies$ `recovered_count++`.
   Decapsulation completes, re-encryption ciphertext matches ground-truth ciphertext ($c' == c$), and the decapsulated key matches $K_{\text{expected}}$ byte-for-byte.

### Auditor Verdict on Target T4
- **Claim:** "100% recovery under transient multiplier glitch."
- **Audit Finding:** **GENUINE RECOVERY CONFIRMED**.
  - The fault was injected into intermediate arithmetic.
  - The monitor caught the algebraic mismatch without circular dependency on the faulted value.
  - Rollback restored pristine inputs, recomputation produced correct polynomials, and independent key oracle verified exact cryptographic correctness.

---

## 4. Reconciled Outcome Validation Summary Table

| Target | Locus | Recovery Claim | Actual Mechanism Tested | Oracle Validated? | Auditor Classification |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **T1** | Twiddle ($\zeta$) | 0% (Blind) | Multiplier & checker share $\zeta$; `mismatch=0`. | Yes (FO rejects 97%) | **Blind Monitor; FO Downstream Safe Rejection** |
| **T2** | Reference Table | N/A | No fault injected in A, C, D; simulated in B. | Yes | **Untested / Fault Not Triggered** |
| **T3** | Operand Register | 100% Recovery | Operand `*r_j` glitched after snapshot latched. | Yes ($K_{\text{out}} == K_{\text{exp}}$) | **Register Glitch Recovery (Snapshot Untested)** |
| **T4** | Multiplier ($t$) | 100% Recovery | Transient glitch in $t$ during forward NTT. | Yes ($K_{\text{out}} == K_{\text{exp}}$) | **Genuine Transient Arithmetic Recovery** |
| **T5** | Adder Output | 0% (Safe Rej) | Persistent fault re-triggers on retry loop. | Yes (Rejection Key) | **Genuine Persistent Fault Safe Fallback** |
| **T6** | Clean Baseline | 0% (Clean) | No fault injected; clean reference pass. | Yes ($K_{\text{out}} == K_{\text{exp}}$) | **Genuine Clean Negative Control** |
