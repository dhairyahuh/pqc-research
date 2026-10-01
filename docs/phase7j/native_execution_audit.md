# Phase 7J: Native Execution Path & Execution Count Audit

## 1. Complete Decapsulation Call Graph Trace

To verify that claimed monitoring and recovery operations execute within the production library, the complete decapsulation call hierarchy was audited in `algorithms/source_ref/mlkem/`:

```
mlkem768_dec(ss, ct, sk)                         [kem.c:533]
 └── mlk_kem_dec_monitored(ss, ct, sk, NULL, ctx) [kem.c:403]
      │
      ├── mlk_indcpa_dec(buf, ct, sk, ctx)       [indcpa.c:598]
      │    ├── mlk_polyvec_ntt(b)                [indcpa.c:619]  --> 3 polys x 896 bflies = 2,688 Fwd
      │    │    └── mlk_ntt_layer(...)           [poly.c:52]     --> Native forward monitor
      │    │
      │    └── mlk_poly_invntt_tomont(sb)        [indcpa.c:622]  --> 1 poly  x 896 bflies =   896 Inv
      │         └── mlk_invntt_layer(...)        [poly.c:125]    --> Native inverse monitor
      │
      ├── mlk_hash_g(kr, buf, 64)                [kem.c:452]
      │
      ├── mlk_indcpa_enc(tmp, buf, pk, coins, ctx)[indcpa.c:537]  (Re-encryption)
      │    ├── mlk_polyvec_ntt(sp)               [indcpa.c:558]  --> 3 polys x 896 bflies = 2,688 Fwd
      │    │    └── mlk_ntt_layer(...)           [poly.c:52]     --> Native forward monitor
      │    │
      │    ├── mlk_polyvec_invntt_tomont(b)      [indcpa.c:564]  --> 3 polys x 896 bflies = 2,688 Inv
      │    │    └── mlk_invntt_layer(...)        [poly.c:125]    --> Native inverse monitor
      │    │
      │    └── mlk_poly_invntt_tomont(v)         [indcpa.c:565]  --> 1 poly  x 896 bflies =   896 Inv
      │         └── mlk_invntt_layer(...)        [poly.c:125]    --> Native inverse monitor
      │
      ├── mlk_ct_memcmp(ct, tmp, 1088)           [kem.c:466]
      ├── Dual-Rail Comparator Loop              [kem.c:477]
      ├── Fail-Stop Persistent Counter Check     [kem.c:486]
      ├── mlk_hash_j(ss, z || ct, 1120)          [kem.c:516]     (Implicit Rejection Hash)
      └── mlk_ct_cmov_zero(ss, kr, 32, fail)     [kem.c:519]     (Constant-Time Multiplexing)
```

---

## 2. Mathematical Composition of Butterfly Invocations

For ML-KEM-768 ($k = 3$ polynomials per vector, degree $N = 256$):
1. **Forward NTT Butterflies**:
   - Each polynomial transform consists of 7 layers of 128 butterflies = $7 \times 128 = 896$ butterflies.
   - Vector $\mathbf{b}$ in `indcpa_dec`: $3 \times 896 = 2,688$ butterflies.
   - Vector $\mathbf{sp}$ in `indcpa_enc`: $3 \times 896 = 2,688$ butterflies.
   - **Total Forward NTT**: $2,688 + 2,688 = \mathbf{5,376}$ butterflies.
2. **Inverse NTT Butterflies**:
   - Polynomial $sb$ in `indcpa_dec`: $1 \times 896 = 896$ butterflies.
   - Vector $\mathbf{b}$ in `indcpa_enc`: $3 \times 896 = 2,688$ butterflies.
   - Polynomial $v$ in `indcpa_enc`: $1 \times 896 = 896$ butterflies.
   - **Total Inverse NTT**: $896 + 2,688 + 896 = \mathbf{4,480}$ butterflies.
3. **Grand Total Monitored Butterflies**:
   $$\text{Total} = 5,376 + 4,480 = \mathbf{9,856} \text{ butterflies per decapsulation}$$

---

## 3. Dynamic Execution-Count Verification

The independent binary `bin/phase7j_independent_validator` directly checked the global monitor counters across configurations:

| Monitor Configuration | Forward Butterfly Count | Inverse Butterfly Count | Total Butterfly Count | Mismatch Count (Clean Input) | Audit Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1. Unmonitored Baseline** | 0 | 0 | 0 | 0 | **VERIFIED (Clean Bypass)** |
| **2. Forward-Only Monitor** | 5,376 | 0 | 5,376 | 0 | **VERIFIED (Exact 5,376)** |
| **3. Inverse-Only Monitor** | 0 | 4,480 | 4,480 | 0 | **VERIFIED (Exact 4,480)** |
| **4. Combined Dual Monitor** | 5,376 | 4,480 | **9,856** | 0 | **VERIFIED (100% Coverage)** |

### Zero False-Alarm Rate
Across all 9,856 monitored butterflies on uncorrupted inputs, `mismatch_count` was strictly **0**. The monitor introduces zero false positives during clean cryptographic operation.

---

## 4. In-Place Rollback and Retry Path Audit

Within `algorithms/source_ref/mlkem_fault_hooks.c`:
- **Local Shadow Registers**: The inputs $u = r[j]$ and $v = r[j + \text{len}]$ are preserved in local register shadow variables before any in-place modification.
- **Rollback Operation**: On invariant failure, `*r_j = u_saved; *r_j_len = v_saved;` restores the pristine state directly in memory/registers.
- **Bounded Retry ($N_{\text{max\_retries}} = 1$)**: The butterfly executes exactly one recomputation attempt. If the recomputation passes, `recovered_count` is incremented. If it fails again (e.g. persistent stuck-at fault), `persistent_count` is incremented and registers are zeroized.
- **Fail-Stop Quenching**: In `kem.c`, any persistent fault unconditionally sets `fail = 0xFF`, bypassing the candidate shared secret and returning the deterministic rejection key $K_{\text{rej}}$.
