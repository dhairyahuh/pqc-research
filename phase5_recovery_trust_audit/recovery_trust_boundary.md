# Phase 5: Recovery-Path and Monitor-State Trust Boundary Analysis

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Target:** ML-KEM-768 (FIPS 203) Implementation with Invariant Fault Monitors  
**Artifact Path:** `phase5_recovery_trust_audit/recovery_trust_boundary.md`

---

## 1. Executive Summary

This document traces the complete recovery trust boundary of the ML-KEM-768 fault-tolerant implementation. The audit inspects the real C source files in `algorithms/source_ref/mlkem/src/poly.c`, `algorithms/source_ref/mlkem/src/kem.c`, and `algorithms/source_ref/mlkem_fault_hooks.c`.

The central objective is to determine whether the recovery mechanism introduces new attack surfaces or false trust assumptions when its own internal state, saved snapshots, or retry logic are subjected to hardware or software faults.

---

## 2. Comprehensive Trust Boundary Mapping

| Subsystem Component | Source File | Exact Line Range | Variables / Data Elements | Architectural Role | Trust Classification |
|---|---|---|---|---|---|
| **Forward NTT Snapshot Capture** | `algorithms/source_ref/mlkem/src/poly.c` | Lines 382–383 | `int16_t u_saved = r[j];`<br>`int16_t v_saved = r[j + len];` | Captures pre-butterfly operands onto the local C stack frame. | **Untrusted snapshot**: Held in volatile registers/stack; unauthenticated and unchecksummed. |
| **Inverse NTT Snapshot Capture** | `algorithms/source_ref/mlkem/src/poly.c` | Lines 557–558 | `int16_t u_saved = r[j];`<br>`int16_t v_saved = r[j + len];` | Captures pre-butterfly operands onto the local C stack frame. | **Untrusted snapshot**: Held in volatile registers/stack; unauthenticated and unchecksummed. |
| **Forward NTT Operands Reused in Retry** | `algorithms/source_ref/mlkem_fault_hooks.c` | Lines 634–640 | `*r_j = u_saved;`<br>`*r_j_len = v_saved;`<br>`int16_t t_retry = monitor_fqmul(v_saved, zeta);`<br>`int16_t u_new = (int16_t)(u_saved + t_retry);`<br>`int16_t v_new = (int16_t)(u_saved - t_retry);` | Restores array values and recomputes the Cooley-Tukey butterfly. | **Tautological dependency**: `u_saved` and `v_saved` are assumed to be clean without integrity checks. |
| **Inverse NTT Operands Reused in Retry** | `algorithms/source_ref/mlkem_fault_hooks.c` | Lines 837–846 | `*r_j = u_saved;`<br>`*r_j_len = v_saved;`<br>`int16_t t_retry = u_saved;`<br>`int16_t u_new = monitor_barrett_reduce((int16_t)(t_retry + v_saved));`<br>`int16_t d_retry = (int16_t)(v_saved - t_retry);`<br>`int16_t v_new = monitor_fqmul(d_retry, zeta);` | Restores array values and recomputes the Gentleman-Sande butterfly. | **Tautological dependency**: In-place rollback copies potentially corrupted stack variables directly into poly array. |
| **Retry & Fail-Stop Control State** | `algorithms/source_ref/mlkem_fault_hooks.c` | Lines 542–553, 669–680 | `g_ntt_native_monitor.allow_retry`<br>`g_ntt_native_monitor.persistent_count`<br>`g_invntt_native_monitor.allow_retry`<br>`g_invntt_native_monitor.persistent_count` | Global state flags governing whether retry is executed and whether persistent faults trigger fail-stop. | **Single Point of Failure (SPOF)**: Single-word integer variables stored in `.data` section with zero redundancy or blinding. |
| **Forward Recovery Verifier Recomputation** | `algorithms/source_ref/mlkem_fault_hooks.c` | Lines 652–653 | `int32_t diff_retry = ((int32_t)u_new - (int32_t)v_new - 2 * (int32_t)t_retry) % 3329;`<br>`int32_t sum_retry  = ((int32_t)u_new + (int32_t)v_new - 2 * (int32_t)u_saved) % 3329;` | Computes difference and sum invariants over recomputed outputs. | **Flawed Oracle**: `sum_retry` checks `u_new + v_new` against `2 * u_saved`. If `u_saved` is corrupted, algebraic cancellation yields 0! |
| **Inverse Recovery Verifier Recomputation** | `algorithms/source_ref/mlkem_fault_hooks.c` | Lines 857–863 | `int32_t sum_retry = ((int32_t)u_new - (int32_t)(u_saved + v_saved)) % 3329;`<br>`int16_t d_verify = (int16_t)(v_saved - u_saved);`<br>`int16_t v_verify = monitor_fqmul(d_verify, zeta);`<br>`int32_t diff_retry = ((int32_t)v_new - (int32_t)v_verify) % 3329;` | Recomputes expected adder sum and difference product against saved inputs. | **Shared Assumption Blindness**: If `u_saved` is corrupted, both recomputation and verification use the same corrupted value. |
| **Recovery Acceptance Decision** | `algorithms/source_ref/mlkem_fault_hooks.c` | Lines 655–659, 865–869 | `if (diff_retry == 0 && sum_retry == 0) { recovered_count++; } else { persistent_count++; }` | Determines whether the retry is marked as successful or escalated to fail-stop. | **Critical Predicate**: A single branch condition deciding whether the failure is masked or flagged. |
| **Decapsulation Fail-Stop Gating** | `algorithms/source_ref/mlkem/src/kem.c` | Lines 483–495 | `if (ntt_native_monitor_get_persistent_count() > 0 \|\| invntt_native_monitor_get_persistent_count() > 0) { fail = 0xFF; *internal_status = MLK_DECAPS_STATUS_FAULT; }` | Reads persistent count and overrides `fail` flag to force implicit rejection and fault status. | **Bridge between Monitor and Protocol**: Relies completely on `persistent_count > 0`. |
| **Downstream Ciphertext Verification** | `algorithms/source_ref/mlkem/src/kem.c` | Lines 466, 477–481 | `fail = mlk_ct_memcmp(ct, tmp, MLKEM_INDCCA_CIPHERTEXTBYTES);`<br>`fail_chk = mlk_ct_cmask_nonzero_u8(fail_chk);`<br>`if (fail != fail_chk) fail = 0xFF;` | Dual-rail comparison of received ciphertext `ct` against re-encrypted ciphertext `tmp`. | **Secondary Defense Barrier**: Fujisaki-Okamoto re-encryption check. Protects decapsulation against arithmetic faults in decrypted message. |
| **Final Output Key Selection** | `algorithms/source_ref/mlkem/src/kem.c` | Lines 512–520 | `mlk_hash_j(ss, tmp, ...);`<br>`mlk_ct_cmov_zero(ss, kr, MLKEM_SYMBYTES, fail);` | Derives rejection key `J(z \|\| ct)` and conditionally overwrites with true key `kr` if `fail == 0`. | **Ultimate Root of Trust**: Output validity is physically decided by the value of `fail`. |

---

## 3. Deep Analysis of the Recovery Trust Model

### 3.1 Snapshot Capture and Storage Vulnerability
In `poly.c:382-383` and `poly.c:557-558`, the values `u_saved` and `v_saved` are allocated as automatic (stack-allocated) 16-bit signed integers:
```c
int16_t u_saved = r[j];
int16_t v_saved = r[j + len];
```
1. **Zero Integrity Protection:** There is no message authentication code (MAC), parity bit, checksum, or duplicate storage for `u_saved` and `v_saved`.
2. **Temporal Window:** Between capture (line 382/557) and monitor invocation (line 408/589), the butterfly operation executes arithmetic instructions (`mlk_fqmul`, `mlk_barrett_reduce`, adds/subs). Any fault (SEU, register glitch, stack pointer corruption) corrupting `u_saved` or `v_saved` remains undetected at capture.

### 3.2 The Tautological Verification Flaw (Shared Assumption Blindness)
Inspect `native_invntt_monitor_butterfly` in `mlkem_fault_hooks.c:841-865`:
```c
/* In-place recomputation */
int16_t t_retry = u_saved;
int16_t u_new = monitor_barrett_reduce((int16_t)(t_retry + v_saved));
int16_t d_retry = (int16_t)(v_saved - t_retry);
int16_t v_new = monitor_fqmul(d_retry, zeta);

/* Verifier */
int32_t sum_retry = ((int32_t)u_new - (int32_t)(u_saved + v_saved)) % 3329;
int16_t d_verify = (int16_t)(v_saved - u_saved);
int16_t v_verify = monitor_fqmul(d_verify, zeta);
int32_t diff_retry = ((int32_t)v_new - (int32_t)v_verify) % 3329;
```

**Algebraic Proof of Tautology:**
Assume a fault corrupts $u_{\text{saved}} \to u_{\text{saved}} + \delta$.
- $u_{\text{new}} \equiv (u_{\text{saved}} + \delta) + v_{\text{saved}} \pmod{3329}$.
- $v_{\text{new}} \equiv (v_{\text{saved}} - (u_{\text{saved}} + \delta)) \cdot \zeta \pmod{3329}$.
- $d_{\text{verify}} = v_{\text{saved}} - (u_{\text{saved}} + \delta) = d_{\text{retry}}$.
- $v_{\text{verify}} = d_{\text{verify}} \cdot \zeta = v_{\text{new}}$.

Verifier checks:
1. $\text{sum\_retry} = u_{\text{new}} - ((u_{\text{saved}} + \delta) + v_{\text{saved}}) \equiv 0 \pmod{3329}$.
2. $\text{diff\_retry} = v_{\text{new}} - v_{\text{verify}} \equiv 0 \pmod{3329}$.

**Consequence:** The recovery verifier tests whether the *recomputation was consistent with the inputs given to it*. It CANNOT test whether the inputs given to it are authentic! Thus, snapshot corruption guarantees a false recovery declaration:
$$\text{recovered\_count} \leftarrow \text{recovered\_count} + 1, \quad \text{persistent\_count} = 0.$$

### 3.3 Monitor State Vulnerability (`persistent_count`)
In `kem.c:486-494`, fail-stop enforcement is governed solely by:
```c
if (ntt_native_monitor_get_persistent_count() > 0 ||
    invntt_native_monitor_get_persistent_count() > 0)
{
    fail = 0xFF;
    *internal_status = MLK_DECAPS_STATUS_FAULT;
}
```
If a persistent fault occurs and sets `persistent_count = 1`, a subsequent fault (e.g. single-event upset or memory write) that clears `persistent_count` to `0` removes the monitor's ability to trigger fail-stop.

### 3.4 Decapsulation Output Decision & The Fujisaki-Okamoto Transform
Even if the monitor is completely blinded (declares false recovery), output validity is ultimately decided by:
```c
fail = mlk_ct_memcmp(ct, tmp, MLKEM_INDCCA_CIPHERTEXTBYTES);
...
mlk_ct_cmov_zero(ss, kr, MLKEM_SYMBYTES, fail);
```
If decapsulation processes corrupted coefficients, the decrypted message $m'$ is corrupted, so the re-encrypted ciphertext $tmp = \text{Enc}(pk, m') \neq ct$.
Thus, $fail = 0xFF$, and the rejection key $K_{\text{rej}}$ is returned.

**Critical Architectural Insight:**
1. A snapshot or monitor fault alone in ML-KEM decapsulation leads to **False Recovery Certification with Downstream Implicit Rejection**.
2. To achieve **Silent Data Corruption (SDC)**—where a corrupted key $K'$ is accepted as valid—an adversary must corrupt the monitor state AND bypass or fault the FO comparison predicate (`fail = 0`).
3. In cryptographic primitives without an FO re-encryption loop (such as ML-KEM Encapsulation or ML-DSA signature generation), snapshot corruption translates immediately to **Silent Data Corruption**.
