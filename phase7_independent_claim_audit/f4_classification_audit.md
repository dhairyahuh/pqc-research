# Phase 7: Forensic Audit and Correction of Target F4 Classification

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Artifact:** `phase7_independent_claim_audit/f4_classification_audit.md`  
**Dataset Reference:** `phase6_verifier_falsification/raw_trial_results.csv` & `derived_corrected_trial_results.csv`

---

## 1. The F4 Contradiction in the Phase 6 Report

In `phase6_verifier_falsification/recalculated_statistics.md`, Target `F4_MONITOR_ALLOW_RETRY_FORCE` was reported with the following mutually contradictory metrics:
- **Internal False Recovery (H1):** **100 / 100 trials (100.0%)**
- **Correct Recovery:** **100 / 100 trials (100.0%)**
- **Dominant Classification:** **`RECOVERED_GENUINE` (100 / 100)**
- **Silent Data Corruption (H2):** **0 / 100 trials (0.0%)**

An event cannot logically be both a **False Recovery** (recovering a corrupted state) and a **Genuine Recovery** (recovering the authentic fault-free state) simultaneously.

This audit traces the execution of all 100 trials of `F4` to identify the origin of this contradiction.

---

## 2. Step-by-Step Trace of F4 Execution

Target `F4` tests an unauthorized retry triggered by a fault in fail-stop mode:

1. **Initial Setup:**
   The monitor is initialized in fail-stop mode with `allow_retry = false`.
2. **Fault Injection:**
   A transient bit flip is injected into intermediate product $t$ during butterfly multiplication via `hook_mid_ntt_post_mul`:
   $$t_{\text{faulted}} = t_{\text{clean}} \oplus (1 \ll b)$$
   The butterfly outputs $r_j = u + t_{\text{faulted}}$ and $r_{j+\text{len}} = u - t_{\text{faulted}}$ are **genuinely corrupted**.
3. **Detection:**
   `native_ntt_monitor_butterfly` evaluates:
   $$diff_c = 2(t_{\text{faulted}} - t_{\text{clean}}) \not\equiv 0 \pmod{3329}$$
   The invariant violation is correctly detected (`mismatch_count++`).
4. **Control-Flow Corruption:**
   A fault flips the monitor's configuration byte `allow_retry = true`.
5. **Rollback & Retry Recomputation:**
   The monitor executes rollback:
   $$r_j = u_{\text{saved}}, \quad r_{j+\text{len}} = v_{\text{saved}}$$
   Crucially, in Target F4, **the snapshot operands $u_{\text{saved}}$ and $v_{\text{saved}}$ were never corrupted**.
   The retry recomputes:
   $$t_{\text{retry}} = \text{fqmul}(v_{\text{saved}}, \zeta) = t_{\text{clean}}$$
   $$u_{\text{new}} = u_{\text{saved}} + t_{\text{retry}} = u_{\text{ref}}$$
   $$v_{\text{new}} = u_{\text{saved}} - t_{\text{retry}} = v_{\text{ref}}$$
6. **Verifier Decision:**
   The recovery verifier checks:
   $$diff_{\text{retry}} = (u_{\text{new}} - v_{\text{new}} - 2 \cdot t_{\text{retry}}) \equiv 0 \pmod{3329}$$
   $$sum_{\text{retry}} = (u_{\text{new}} + v_{\text{new}} - 2 \cdot u_{\text{saved}}) \equiv 0 \pmod{3329}$$
   Both evaluate to 0. The verifier passes (`recovered_count++`).
7. **Decapsulation Outcome:**
   The decapsulation executes to completion and outputs the authentic shared secret:
   $$ss_{\text{out}} == ss_{\text{expected}}, \quad status == \text{MLK\_STATUS\_SUCCESS}$$

---

## 3. Root Cause of the Contradictory H1 Classification in Phase 6

Why did Phase 6 report `h1_false_recovery = 1` for all 100 trials of F4?

In Phase 6's harness (`genuine_recovery_falsification_harness.c:380`):
```c
/* Reference Butterfly Comparison */
int16_t ref_u = g_ref_butterflies[g_fault.stage][g_fault.butterfly].u;
int16_t ref_v = g_ref_butterflies[g_fault.stage][g_fault.butterfly].v;
bool retry_matches_ref = (g_trace.trace_captured) ?
    (g_trace.retry_u == ref_u && g_trace.retry_v == ref_v) : false;

/* Evaluate Hypotheses */
bool h1_false_recovery = (g_trace.trace_captured && g_trace.verifier_passed && !retry_matches_ref);
```

As uncovered in Section 3 of [`phase6_source_audit.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/phase6_source_audit.md):
- In ML-KEM-768 decapsulation, 6 polynomial NTTs are executed sequentially.
- Phase 6's reference table `g_ref_butterflies[8][128]` stored only the butterfly coefficients of **polynomial #5**.
- In Target F4, the fault struck during **polynomial #0**.
- The recomputed output `g_trace.retry_u` was authentic and identical to the fault-free coefficients of polynomial #0.
- However, the oracle compared it against the reference of polynomial #5!
- Since polynomial #0 differs from polynomial #5, `retry_matches_ref` evaluated to `False`.
- This triggered `h1_false_recovery = True` in every trial!

---

## 4. Reconciled and Corrected Metrics for Target F4

With the multi-polynomial reference oracle in Phase 7 (`g_ref_butterflies[6][8][128]`), the trial results are reconciled:

| Metric | Phase 6 (Uncorrected / Erroneous) | Phase 7 (Corrected / Audited) | Discrepancy Cause |
|---|---|---|---|
| **Trials Tested ($n$)** | 100 | 100 | Identical execution |
| **Fault Triggered** | 100 | 100 | Identical execution |
| **Pre-Retry Corruption** | 100 (Corrupted) | 100 (Corrupted) | Initial butterfly $t$ was glitched |
| **Post-Retry State** | 100 (Clean) | 100 (Clean) | Retry restored true coefficients |
| **Retry Matches Reference** | **0 / 100 (0.0%)** | **100 / 100 (100.0%)** | **Fixed oracle reference collision** |
| **H1 False Recovery Count** | **100 / 100 (100.0%)** | **0 / 100 (0.0%)** | **Corrected false-positive artifact** |
| **Correct Recovery (`REC_GENUINE`)**| 100 / 100 (100.0%) | 100 / 100 (100.0%) | Unchanged; true recovery occurred |
| **Silent Data Corruption (H2)** | 0 / 100 (0.0%) | 0 / 100 (0.0%) | Unchanged; authentic key released |

### Audit Decision:
Target `F4` was a **100% genuine recovery**. The claim in Phase 6 that F4 demonstrated internal false recovery is **CONTRADICTED AND WITHDRAWN**.
