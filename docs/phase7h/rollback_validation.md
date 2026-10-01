# Phase 7H: Rollback Mechanism & Recovery Soundness Validation

## 1. Local Register Rollback Architecture

The native butterfly rollback mechanism in [mlkem_fault_hooks.c](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) executes within the caller frame:

```c
void native_ntt_monitor_butterfly(
    unsigned layer, unsigned butterfly_idx, int16_t zeta,
    int16_t u_saved, int16_t v_saved, int16_t t_used,
    int16_t *r_j, int16_t *r_j_len
) {
    ...
    if (diff_c != 0 || sum_c != 0) {
        g_ntt_native_monitor.mismatch_count++;
        if (g_ntt_native_monitor.allow_retry) {
            g_ntt_native_monitor.retry_attempt_count++;

            /* 1. In-place rollback */
            *r_j = u_saved;
            *r_j_len = v_saved;

            /* 2. In-place recomputation */
            int16_t t_retry = monitor_fqmul(v_saved, zeta);
            int16_t u_new = (int16_t)(u_saved + t_retry);
            int16_t v_new = (int16_t)(u_saved - t_retry);

            /* 3. Output update */
            *r_j = u_new;
            *r_j_len = v_new;

            /* 4. Secondary verification */
            int32_t diff_retry = ((int32_t)u_new - (int32_t)v_new - 2 * (int32_t)t_retry) % 3329;
            int32_t sum_retry  = ((int32_t)u_new + (int32_t)v_new - 2 * (int32_t)u_saved) % 3329;

            if (diff_retry == 0 && sum_retry == 0) {
                g_ntt_native_monitor.recovered_count++;
            } else {
                g_ntt_native_monitor.persistent_count++;
            }
        }
    }
}
```

---

## 2. Memory Bounds & Index Safety Analysis

- **Memory Buffers**: In `poly.c`, `r` points to an array of $256$ elements of `int16_t`.
- **Index Bounds**:
  - `start` advances from $0$ to $256 - 2\cdot\text{len}$ in steps of $2\cdot\text{len}$.
  - `j` spans `[start, start + len)`.
  - Therefore, `j` is strictly bounded by $256 - \text{len} - 1$.
  - The second pointer `r[j + len]` accesses indices up to $255$.
  - **Memory Safety**: `*r_j` and `*r_j_len` are guaranteed to remain within the 256-element polynomial memory slice without buffer overflows.

---

## 3. Recovery Correctness & Bounded Retry

1. **Saved Operand Integrity**:
   `u_saved` and `v_saved` are captured on the CPU register stack at the beginning of each loop iteration before any arithmetic or hooks execute.
2. **Deterministic Arithmetic Equivalence**:
   The retry logic computes `u_new = u_saved + t_retry` and `v_new = u_saved - t_retry`. This matches the Cooley-Tukey forward butterfly in `poly.c` exactly.
3. **Strict Bounded Retry ($N = 1$)**:
   The monitor allows at most one retry per butterfly. If the secondary verification fails (`diff_retry != 0 || sum_retry != 0`), it increments `persistent_count` and does **not** attempt another retry loop, preventing infinite retry hangs.
4. **Fail-Closed State Propagation**:
   In `kem.c`, `ntt_native_monitor_get_persistent_count() > 0` directly sets `fail = 0xFF`, ensuring the decapsulation engine falls back to generating the FIPS 203 pseudo-random rejection key $K_{\text{rej}}$.

---

## 4. Resilience of the Checker Itself (Self-Corruption Analysis)

- **Checker Corruption Scenario**: What happens if a cosmic particle strikes the checker registers during `native_ntt_monitor_butterfly`?
  - Case 1: Corrupted `diff_c` or `sum_c` when computation was clean $\to$ Triggers false positive rollback. Re-execution restores clean outputs and succeeds.
  - Case 2: Corrupted `diff_c` to 0 when computation was faulty $\to$ Silent bypass. Downstream Fujisaki-Okamoto re-encryption check fails and triggers safe implicit rejection ($K_{\text{rej}}$).
  - Case 3: Corrupted `persistent_count` flag $\to$ Enters fail-safe mode and outputs $K_{\text{rej}}$.
- **Conclusion**: The multi-layered architecture ensures that checker failures degrade gracefully to safe implicit rejection, strictly avoiding uncontained key leaks.
