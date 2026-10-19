# Phase 7: Forensic Source-Level Audit of Phase 6 Claims and Harness

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Target:** ML-KEM-768 Implementation & Phase 6 Artifacts  
**Artifact:** `phase7_independent_claim_audit/phase6_source_audit.md`  
**Reference Harness:** `phase6_verifier_falsification/genuine_recovery_falsification_harness.c`  
**Cryptographic Object:** `bin/obj/mlkem768_inst.o` (SHA-256: `3b3eb759dd186a5df469bfd97157832626e95bfadce7bf9ca4d71542fbc94a9a`)

---

## 1. Scope and Preserved Baseline Inspection

We audited the Phase 6 artifact suite in `phase6_verifier_falsification/`. All original Phase 6 files, CSV records, and binaries have been preserved without modification. All new analytical data and corrected harnesses reside strictly inside `phase7_independent_claim_audit/`.

### 1.1 Compilation and Linkage Identity
- **Compiler:** Apple Clang version 17.0.0 (`clang -O3 -Wall -Wextra -std=c11`)
- **Include Paths:** `-I. -I algorithms/source_ref/mlkem`
- **Linked Cryptographic Binary:** `bin/obj/mlkem768_inst.o`
- **Compiler Invariant Confirmation:** Inspection of symbol table via `nm bin/obj/mlkem768_inst.o` confirms that the cryptographic core is compiled from real `poly.c`, `kem.c`, and `indcpa.c` with native verification and fault hooks enabled (`MLKEM_RESEARCH_FAULT_HOOKS`).

---

## 2. Source-Level Hook and Variable Injection Map

The table below documents the exact source lines, memory locations, and execution timing for every fault model tested in Phase 6:

| Target ID | Hook Function & Source File | Line Range | Variable & Memory Class | Relative Timing | Subsystem Impact |
|---|---|---|---|---|---|
| `F1` | `native_ntt_monitor_butterfly`<br>([`genuine_recovery_falsification_harness.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase6_verifier_falsification/genuine_recovery_falsification_harness.c#L198-L203)) | Lines 198–203 | `u_saved`<br>(Stack parameter passed by value) | Post-capture (line 382 of `poly.c`), pre-mismatch check | Local snapshot and rollback source |
| `F2` | `hook_mid_ntt_post_mul` & `native_ntt_monitor_butterfly` | Lines 145–150,<br>220–225 | `*t_ptr` (stack pointer)<br>`u_saved` (stack parameter) | During mul (`t_ptr`),<br>Post-mismatch pre-rollback (`u_saved`) | Multiplier output then snapshot before rollback |
| `F3` | `native_ntt_monitor_butterfly` | Lines 275–280 | `g_ntt_mon.persistent_count`<br>(Global static variable in `.bss`) | Post-increment in recovery verifier | Monitor state / Decapsulation fail-stop gate |
| `F4` | `native_ntt_monitor_butterfly` | Lines 210–215 | `g_ntt_mon.allow_retry`<br>(Global static variable in `.bss`) | Post-mismatch detection | Monitor control flow in fail-stop mode |
| `F5` | `native_ntt_monitor_butterfly` | Lines 260–264 | `diff_retry`<br>(Local 32-bit stack variable) | Post-recomputation, pre-branch | Recovery verifier output |
| `F6` | `native_ntt_monitor_butterfly` | Lines 266–271 | `diff_retry`, `sum_retry`<br>(Local 32-bit stack variables) | Post-recomputation, pre-branch | Recovery verifier output |
| `F7` | `native_ntt_monitor_butterfly` | Lines 240–245 | `t_retry`<br>(Local 16-bit stack variable) | During `monitor_fqmul` in retry | Retry recomputation arithmetic |
| `F8` | `native_ntt_monitor_butterfly` | Lines 252–257 | `u_ver_operand`<br>(Local 16-bit stack variable) | Inside verifier difference check | Verifier expected input operand |
| `F9` | `native_ntt_monitor_butterfly` | Lines 228–234 | `u_saved`, `snap_token`<br>(Stack variables) | Pre-rollback DSPC check | Mitigation snapshot & token |
| `F10`| `native_ntt_monitor_butterfly` | Lines 238–241 | `token_mismatch`<br>(Local boolean flag) | At DSPC branch evaluation | Mitigation branch decision |
| `F11`| `native_ntt_monitor_butterfly` | Lines 228–230 | `u_saved`<br>(Stack variable) | Pre-rollback DSPC check | Mitigation input |
| `F12`| None | N/A | None | N/A | Nominal clean baseline |

---

## 3. Identification of the Phase 6 Oracle Reference Collision Bug

Our audit uncovered a critical flaw in the Phase 6 reference oracle implementation:

### 3.1 The Bug in `genuine_recovery_falsification_harness.c`
In lines 85–92:
```c
/* Reference Butterfly Lookup: [layer 1..7][butterfly 0..127] */
typedef struct {
    int16_t u;
    int16_t v;
} butterfly_ref_t;

static butterfly_ref_t g_ref_butterflies[8][128];
static bool g_capture_ref_mode = false;
```
During the baseline capture run (`main()` lines 343–349):
```c
g_capture_ref_mode = true;
uint8_t ss_dummy[SS_BYTES];
uint32_t status_dummy = 0;
mlkem768_dec_monitored(ss_dummy, ct_valid, sk, &status_dummy);
g_capture_ref_mode = false;
```

### 3.2 Architectural Analysis of Decapsulation
In ML-KEM-768, `mlkem768_dec_monitored` invokes `mlk_indcpa_enc` to perform Fujisaki-Okamoto re-encryption.
Inside `mlk_indcpa_enc`:
1. `polyvec_ntt(&sp)` executes NTT on **3 polynomials** ($sp[0], sp[1], sp[2]$).
2. Matrix-vector multiplication and subsequent transforms execute NTT on additional polynomials.
In total, **exactly 6 polynomial NTT invocations** take place sequentially during one decapsulation call.

### 3.3 The Failure Mechanism
Because `g_ref_butterflies` had dimensions `[8][128]` instead of `[poly_idx][8][128]`:
- Polynomial #0 stored its butterflies into `g_ref_butterflies`.
- Polynomial #1 overwrote `g_ref_butterflies`.
- Polynomials #2, #3, #4, and #5 consecutively overwrote `g_ref_butterflies`.
At the end of capture mode, `g_ref_butterflies` held **only the butterfly coefficients of polynomial #5**.

During the active trials:
- When a fault was injected into polynomial #0 (the first polynomial transformed), the retry output `g_trace.retry_u` was compared against `g_ref_butterflies[stage][butterfly]`—which belonged to polynomial #5!
- Consequently, `retry_matches_ref` evaluated to `False`, falsely reporting that the recomputation did not match the fault-free reference.

This explains why **`F4_MONITOR_ALLOW_RETRY_FORCE` was misclassified as 100/100 H1 false recovery in Phase 6**, even though it was a completely successful, clean recovery!
In Phase 7, we expanded the reference oracle to 3D: `g_ref_butterflies[6][8][128]`, tracking `g_current_poly_idx`, completely eliminating the oracle collision.
