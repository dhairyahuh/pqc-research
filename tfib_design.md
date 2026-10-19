# TFIB Design: Analysis of Twiddle Factor Blindness in ML-KEM-768

**Document:** Phase A Deliverable — Twiddle Factor Integrity Binding (TFIB) Design & Vulnerability Trace  
**Audited Target:** ML-KEM-768 NTT Implementation in `algorithms/source_ref/`  
**Host Architecture:** Apple M3 Pro (ARM64), macOS Darwin 25.1.0, Apple Clang 17.0.0  
**Date:** October 2026  

---

## 1. Executive Problem Statement

In the baseline ML-KEM-768 fault-resilience architecture, localized single-butterfly invariant monitoring continuously tracks $9{,}856$ butterfly operations across 11 forward Cooley-Tukey (CT) and inverse Gentleman-Sande (GS) transforms. While this monitor achieves $100\%$ recovery for transient arithmetic faults on intermediate multipliers ($F4$) and $100\%$ safe fail-stop on persistent faults ($F5A, F5B$), it possesses an architectural blind spot: **Twiddle Factor Blindness (Theorem 1)**.

When a single-event upset (SEU) or memory corruption alters a twiddle factor $\zeta \in \mathbb{Z}_q$, the local invariant checker consumes the exact same corrupted scalar as the live butterfly computation. As a mathematical consequence, both the sum and difference invariants evaluate to zero ($\Delta_{\text{sum}} = 0$, $\Delta_{\text{mul}} = 0$). The local monitor experiences a **$0.0\%$ detection rate**, allowing corrupted intermediate polynomials to commit into the state. While downstream Fujisaki-Okamoto (FO) re-encryption comparison (`mlk_ct_memcmp`) eventually detects the discrepancy and forces implicit rejection, **communication availability is completely destroyed (0% recovery)**, and key renegotiation is required.

The objective of **Twiddle Factor Integrity Binding (TFIB)** is to close this blind spot at the butterfly level, enabling local detection and rollback recovery without relying exclusively on coarse outer FO fail-stops.

---

## 2. Source-Level Inspection of Twiddle Loading and Consumption

### 2.1 Storage and Definition
In the production C implementation, twiddle factors are stored as a static array in [`algorithms/source_ref/mlkem/src/zetas.inc`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/zetas.inc#L17):
```c
static MLK_ALIGN const int16_t mlk_zetas[128] = {
    -1044,  -758,   -359,  -1037,   1493,  ...
};
```
The array contains 128 16-bit signed integers representing powers of the 256-th primitive root of unity in bit-reversed order modulo $q = 3329$.

### 2.2 Forward Cooley-Tukey NTT Twiddle Consumption
In [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L435-L450):
```c
/* mlk_ntt_layer */
k = 1u << (layer - 1);
len = (unsigned)MLKEM_N >> layer;
for (start = 0; start < MLKEM_N; start += 2 * len) {
    int16_t zeta = mlk_zetas[k++];  // <-- Loaded from memory
    mlk_ntt_butterfly_block(r, zeta, start, len, layer, layer * MLKEM_Q);
}
```
Inside `mlk_ntt_butterfly_block` ([`poly.c:380-408`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L380-L408)):
```c
int16_t zeta_val = zeta;  // <-- Assigned to local variable
...
hook_mid_ntt_pre_butterfly(layer, b_idx, &zeta_val, &r[j], &r[j + len], j, j + len);
int16_t t = mlk_fqmul(r[j + len], zeta_val); // <-- Consumed by live computation
...
native_ntt_monitor_butterfly(layer, b_idx, zeta_val, u_saved, v_saved, t, &r[j], &r[j + len]);
```

### 2.3 Inverse Gentleman-Sande NTT Twiddle Consumption
In [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L535-L590):
```c
/* mlk_invntt_layer */
len = (unsigned)MLKEM_N >> layer;
k = (1u << layer) - 1;
for (start = 0; start < MLKEM_N; start += 2 * len) {
    int16_t zeta = mlk_zetas[k--]; // <-- Loaded in reverse order
    for (j = start; j < start + len; j++) {
        int16_t zeta_val = zeta;
        ...
        hook_mid_invntt_pre_butterfly(layer, b_idx, &zeta_val, &r[j], &r[j + len], j, j + len);
        int16_t diff = (int16_t)(r[j + len] - t);
        r[j + len] = mlk_fqmul(diff, zeta_val); // <-- Consumed by live computation
        ...
        native_invntt_monitor_butterfly(layer, b_idx, zeta_val, u_saved, v_saved, &r[j], &r[j + len]);
    }
}
```

---

## 3. Analysis of Existing Monitor's Twiddle Acquisition

The critical vulnerability lies in the parameter signature and call site of the butterfly monitor functions:

In [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L600-L625):
```c
void native_ntt_monitor_butterfly(
    unsigned layer, unsigned butterfly_idx, int16_t zeta,
    int16_t u_saved, int16_t v_saved, int16_t t_used,
    int16_t *r_j, int16_t *r_j_len
) {
    ...
    if (g_ntt_native_monitor.mode == NTT_NATIVE_MONITOR_RECOMPUTED_T) {
        t_check = monitor_fqmul(v_saved, zeta); // <-- Uses the caller-supplied zeta!
    } else {
        t_check = t_used;
    }

    diff_c = ((int32_t)(*r_j) - (int32_t)(*r_j_len) - 2 * (int32_t)t_check) % 3329;
    sum_c  = ((int32_t)(*r_j) + (int32_t)(*r_j_len) - 2 * (int32_t)u_saved) % 3329;
```

**The Vulnerability Trace:**
1. The monitor receives `int16_t zeta` by value directly from the caller in `poly.c`.
2. The caller in `poly.c` passes `zeta_val`, which is the exact same variable that was passed into `hook_mid_ntt_pre_butterfly` and used in `mlk_fqmul`.
3. If `zeta_val` is faulted, `t = mlk_fqmul(v, zeta_val)` uses the corrupted value $\tilde{\zeta}$.
4. Inside the monitor, `t_check = monitor_fqmul(v_saved, zeta)` also uses $\tilde{\zeta}$.
5. Therefore:
   $$r_0 = u + v\tilde{\zeta}, \quad r_1 = u - v\tilde{\zeta}$$
   $$r_0 - r_1 = 2v\tilde{\zeta} = 2 t_{\text{check}} \implies \text{diff\_c} = 0$$
   $$r_0 + r_1 = 2u \implies \text{sum\_c} = 0$$
6. Both residual checks equal zero identically. **The checker is mathematically blind to any mutation of $\zeta$.**

---

## 4. Minimal Reproducible Proof of Shared-State Failure

We compiled and executed a standalone diagnostic (`test_twiddle_blindness.c`) targeting `NTT_LOCUS_TWIDDLE_ZETA` during stage 3 butterfly executions across 10 independent trials.

### Empirical Output:
```text
Trial 0: trigger=1, monitor_mismatch=0, status=0xA5A5A5A5, ss_match=0, rej_match=1
Trial 1: trigger=1, monitor_mismatch=0, status=0xA5A5A5A5, ss_match=0, rej_match=1
Trial 2: trigger=1, monitor_mismatch=0, status=0xA5A5A5A5, ss_match=0, rej_match=1
Trial 3: trigger=1, monitor_mismatch=0, status=0xA5A5A5A5, ss_match=0, rej_match=1
Trial 4: trigger=1, monitor_mismatch=0, status=0xA5A5A5A5, ss_match=0, rej_match=1
Trial 5: trigger=1, monitor_mismatch=0, status=0xA5A5A5A5, ss_match=0, rej_match=1
Trial 6: trigger=1, monitor_mismatch=0, status=0xA5A5A5A5, ss_match=0, rej_match=1
Trial 7: trigger=1, monitor_mismatch=0, status=0xA5A5A5A5, ss_match=0, rej_match=1
Trial 8: trigger=1, monitor_mismatch=0, status=0xA5A5A5A5, ss_match=0, rej_match=1
Trial 9: trigger=1, monitor_mismatch=0, status=0xA5A5A5A5, ss_match=0, rej_match=1

SUMMARY: Blind Passes = 10/10 (Local Detection Rate = 0.0%), Outer FO Catches = 10/10
```

### Interpretation:
- `trigger = 1`: The fault injection hook successfully flipped a bit in `zeta_val`.
- `monitor_mismatch = 0`: In 10/10 trials, the native invariant monitor registered zero mismatches.
- `recovered_count = 0`: Local rollback was never attempted.
- `status = 0xA5A5A5A5`: The local monitor reported clean execution, but downstream FO re-encryption detected $c' \neq c$ and forced implicit rejection.
- **Result:** $0.0\%$ local fault detection; $0.0\%$ transient fault recovery.

---

## 5. Candidate TFIB Architectural Strategies

To resolve this limitation without replacing the entire cryptographic implementation, we design two distinct strategies:

```
[Strategy 1: TFIB-Ref (Dual-Reference Table)]
Operational Path:              Verification Path:
mlk_zetas[k]  ────────► Butterfly Core
                            ▲
                            │ (Compare zeta_op ^ zeta_ref)
mlk_zetas_ref[k] ───────────┴────────► Invariant Checker & Rollback

----------------------------------------------------------------------

[Strategy 2: TFIB-Meta (Precomputed Integrity Tags)]
Operational Path:              Metadata Verification:
mlk_zetas[k]  ────────► Butterfly Core
      │
      ▼
Compute Tag: H(zeta) ──► Compare with mlk_zetas_tag[k] ──► Invariant Checker
```

### Strategy 1: Independently Validated Twiddle Reference (TFIB-Ref)
- **Concept:** Maintain an independent reference array `mlk_zetas_ref[128]` stored in a separate memory page or initialized with negated/permuted representations.
- **Verification Rule:** The monitor does not trust the passed `zeta_val`. It independently loads `zeta_ref = mlk_zetas_ref[k]` and evaluates:
  $$\Delta_{\zeta} = \text{zeta\_op} \oplus \text{zeta\_ref}$$
  $$\Delta_{\text{mul}} = (r_0 - r_1 - 2(v_{\text{saved}} \cdot \zeta_{\text{ref}})) \pmod q$$
- **Rollback Capability:** If $\text{zeta\_op}$ is corrupted while $\text{zeta\_ref}$ is intact, the monitor can restore the operands and retry the butterfly using the verified $\zeta_{\text{ref}}$.
- **Trust Assumptions:** Assumes an SEU strikes either the operational memory space or the reference memory space, but does not corrupt both to identical bit patterns simultaneously.

### Strategy 2: Twiddle Integrity Metadata (TFIB-Meta)
- **Concept:** Store compact integrity metadata for each twiddle factor, such as a 16-bit cryptographic checksum or non-linear tag $T_k = \text{Tag}(\zeta_k)$.
- **Verification Rule:** Before committing the butterfly, the monitor recomputes the tag over the operational $\zeta$ and verifies $\text{Tag}(\zeta) == \text{mlk\_zetas\_tag}[k]$.
- **Rollback Capability:** Flags twiddle corruption immediately before error propagation. If persistent, triggers immediate fail-stop.
- **Trust Assumptions:** Assumes bitflips in $\zeta$ do not create collisions with respect to the metadata tag function (collision probability $\approx 2^{-16} \approx 1.5 \times 10^{-5}$).

---

## 6. Conclusion and Next Steps

The source-code trace and minimal diagnostic confirm that twiddle factor blindness is an active, reproducible limitation of the existing monitor. 

In **Phase B**, we will implement both `TFIB-Ref` and `TFIB-Meta` in `tfib_implementation/`, keeping the baseline monitor intact for comparative benchmarking. In **Phase C**, we will subject both configurations to targeted operational, reference, metadata, and concurrent fault injections.
