# Phase 7I: Native Inverse NTT Integration Architecture

## 1. Architectural Scope & Decapsulation NTT Coverage

In Phase 7H, the independent audit discovered that earlier monitoring covered only forward NTT operations (5,376 butterflies), leaving 4,480 inverse butterflies completely unmonitored (54.5% coverage).

Phase 7I achieves **100% complete NTT coverage across ML-KEM-768 decapsulation**:

```
Total Decapsulation NTT Operations: 9,856 Butterflies
├── Forward NTT Invocations (Cooley-Tukey, 6 Polynomials)
│   ├── indcpa_dec: 3 polynomials (ciphertext b)     --> 2,688 butterflies [MONITORED]
│   └── indcpa_enc: 3 polynomials (noise sp)          --> 2,688 butterflies [MONITORED]
│   └── Subtotal Forward:                             --> 5,376 butterflies (54.5%)
└── Inverse NTT Invocations (Gentleman-Sande, 5 Polynomials)
    ├── indcpa_dec: 1 polynomial (inner product sb)  -->   896 butterflies [MONITORED]
    ├── indcpa_enc: 3 polynomials (matrix-vector b)   --> 2,688 butterflies [MONITORED]
    └── indcpa_enc: 1 polynomial (ciphertext v)       -->   896 butterflies [MONITORED]
    └── Subtotal Inverse:                             --> 4,480 butterflies (45.5%)
```

---

## 2. In-Tree Inverse Butterfly Instrumentation

In `algorithms/source_ref/mlkem/src/poly.c` (`mlk_invntt_layer`), the native loop is instrumented under `#if defined(MLKEM_RESEARCH_FAULT_HOOKS)`:

```c
static void mlk_invntt_layer(int16_t *r, unsigned layer) {
  ...
  for (start = 0; start < MLKEM_N; start += 2 * len) {
    int16_t zeta = mlk_zetas[k--];
    for (j = start; j < start + len; j++) {
#if defined(MLKEM_RESEARCH_FAULT_HOOKS)
      unsigned b_idx = (start / (2 * len)) * len + (j - start);
      int16_t zeta_val = zeta;
      int16_t u_saved = r[j];
      int16_t v_saved = r[j + len];

      // Native computation
      int16_t t = r[j];
      r[j] = mlk_barrett_reduce((int16_t)(t + r[j + len]));
      int16_t diff = (int16_t)(r[j + len] - t);
      r[j + len] = mlk_fqmul(diff, zeta_val);

      // In-tree monitor & retry
      extern void native_invntt_monitor_butterfly(
          unsigned layer, unsigned butterfly_idx, int16_t zeta,
          int16_t u_saved, int16_t v_saved,
          int16_t *r_j, int16_t *r_j_len
      );
      native_invntt_monitor_butterfly(layer, b_idx, zeta_val, u_saved, v_saved, &r[j], &r[j + len]);
#else
      int16_t t = r[j];
      r[j] = mlk_barrett_reduce((int16_t)(t + r[j + len]));
      r[j + len] = (int16_t)(r[j + len] - t);
      r[j + len] = mlk_fqmul(r[j + len], zeta);
#endif
    }
  }
}
```

---

## 3. Local Register Rollback & Bounded Retry Engine

When an invariant mismatch is detected ($S \not\equiv 0$ or $D \not\equiv 0$):
1. **Local Rollback**:
   The monitor restores pre-butterfly inputs directly:
   `*r_j = u_saved; *r_j_len = v_saved;`
2. **Deterministic Re-Execution**:
   ```c
   int16_t t_retry = u_saved;
   int16_t u_new = monitor_barrett_reduce((int16_t)(t_retry + v_saved));
   int16_t d_retry = (int16_t)(v_saved - t_retry);
   int16_t v_new = monitor_fqmul(d_retry, zeta);
   *r_j = u_new;
   *r_j_len = v_new;
   ```
3. **Secondary Validation**:
   The invariants are re-evaluated.
   - If clean: `g_invntt_native_monitor.recovered_count++` is logged.
   - If repeated failure: `g_invntt_native_monitor.persistent_count++` is logged.
4. **Retry Limit ($N=1$)**:
   The retry path executes at most once per butterfly. Infinite retry loops are structurally impossible.
