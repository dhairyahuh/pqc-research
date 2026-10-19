# Claim-to-Evidence Traceability Matrix

**Auditor:** Skeptical Cryptographic Auditor & Implementation Research Team  
**Audit Target:** Technical Audit Report on Shared-Constant Corruption, Input Latching, and Rollback Integrity  
**Evaluation Date:** 2026-10-02  

---

## 1. Summary of Evaluated Claims

| Claim ID | Claim Summary | Source Location | Evidence Type | Reproduction Status | Contradictions & Discrepancies | Confidence & Scope Limitations |
| :---: | :--- | :--- | :--- | :---: | :--- | :--- |
| **CLM-01** | **Shared Twiddle Factor Verification:** NTT butterfly invariant checker shares the exact same potentially corrupted `zeta` constant as computation. | [`poly.c:408`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L408), [`poly.c:589`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L589), [`mlkem_fault_hooks.c:618`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L618), [`mlkem_fault_hooks.c:825`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L825) | Source Inspection & Dynamic Tracing | **Reproduced** | None. The parameter `zeta_val` is passed by value from the operational loop to the monitor. | High. Applies to all Cooley-Tukey and Gentleman-Sande butterflies in this implementation. |
| **CLM-02** | **Dead Code in Reference Table:** `static const int16_t g_trusted_zetas[128]` declared in monitor code is completely unreferenced. | [`mlkem_fault_hooks.c:555-568`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L555-L568) | Static Analysis & Symbol Grep | **Reproduced** | None. 0 occurrences across all `.c` and `.h` files in the repository. | High. The table exists in memory but is never read by `monitor_fqmul`. |
| **CLM-03** | **Twiddle Invariant Blind Spot:** Corrupting the operational twiddle constant causes 0% local invariant detection ($200/200$ evasions). | [`experiments/mathematics/audit_correlated_faults.c:203-237`](file:///Users/dhairyajain/Desktop/pqc%20research/experiments/mathematics/audit_correlated_faults.c#L203-L237) | Dynamic Execution | **Reproduced** | Earlier reports claimed 100% detection across all NTT fault classes without isolating twiddle constants. | High within evaluated single-bit and multi-bit twiddle perturbations. |
| **CLM-04** | **Fujisaki-Okamoto Safe Rejection:** 188 of 200 twiddle corruption trials are safely rejected via the FO re-encryption check. | [`kem.c:466`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c#L466), [`kem.c:519`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c#L519), `check_exp4` harness | Dynamic Execution & State Log | **Reproduced** | None. Ciphertext comparison detects corrupted re-encryption output and suppresses candidate secret. | High. Returns deterministic $K_{\text{rej}}$ per FIPS 203. |
| **CLM-05** | **Benign-Equivalent Decapsulations:** 12 of 200 twiddle trials return `0x5A5A5A5A` with valid key match `ss == ss_expected`. | `check_exp4`, `check_v_zero`, `check_ct_diffs` | Dynamic Execution & Byte-Level Diff | **Reproduced** | An unverified assertion might assume these 12 trials were undetected silent data corruptions; they are in fact legitimate key matches. | High. Verified byte-exact against clean reference key for all 12 individual trials. |
| **CLM-06** | **Pre-Butterfly Latching Race Condition:** The reported 200/200 detections for input corruption resulted from hook placement *after* `u_saved` was latched. | [`poly.c:557-564`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L557-L564) | Source Code Trace & Comparative Harness | **Reproduced** | The written architectural trace said 0% detection, but EXP 5 reported 100% detection. Race condition in hook ordering reconciles the conflict. | High. True pre-latch memory corruption has 0% detection by local invariants. |
| **CLM-07** | **Tautological Retry Verification:** The post-retry checks `sum_retry` and `diff_retry` are algebraic tautologies ($2u - 2u \equiv 0$, $2t - 2t \equiv 0$). | [`mlkem_fault_hooks.c:652-655`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L652-L655), [`mlkem_fault_hooks.c:857-865`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L857-L865) | Formal Derivation & Exhaustive Parameter Sweep | **Reproduced** | In-tree comments claimed retry verification proved arithmetic integrity; in reality, it is a circular self-consistency check. | High. Verified with $100,000$ random input configurations with 0 failures. |
| **CLM-08** | **Zero Silent Data Corruption (SDC):** No evaluated fault resulted in an incorrect accepted shared secret. | `results/phase7j/raw/phase7j_extended_trials.json`, `audit_correlated_faults.c` | Cumulative Experimental Data ($N=2,000+$) | **Reproduced** | None. The FO transform acts as a robust fail-stop boundary against arithmetic corruption. | High. Wilson score 95% upper bound is $<0.15\%$ across all campaigns. |
| **CLM-09** | **Reconciliation of "450 Trials":** The report's claim of 450 trials evaluated for constant and memory corruption. | Prior report Section 8 vs. Table 7 | Numerical Reconciliation | **Reconciled with Clarification** | The previous report stated "Across all 450 trials...", but Table 7 listed 200 (EXP 4) + 200 (EXP 5A) + 50 (EXP 5B) = 450. | Medium. Explicitly documented below to remove ambiguity. |

---

## 2. Detailed Discrepancy Reconciliation

### 2.1 The "450 Trials" Denominator Audit
In Section 8 of the previous audit report, the text cited:
> *"Across all 450 trials evaluating constant and input memory corruptions, zero silent data corruptions occurred."*

A skeptical audit of the reported sub-experiments reveals:
- **EXP 4 (Twiddle Constant Corruption):** 200 trials
- **EXP 5A (Post-Latch Hook Mutation):** 200 trials
- **EXP 5B (True Pre-NTT Memory Corruption):** 50 trials
- **Sum:** $200 + 200 + 50 = 450$ trials.

However, Table 7 of the report separately listed:
- **Campaign J07:** 100 trials
- **EXP 6 (Persistent Stuck-at):** 200 trials

**Reconciliation Finding:** The previous author summed exclusively the constant-corruption trials ($N=200$), the post-latch input trials ($N=200$), and the minimal pre-latch memory test ($N=50$) to arrive at $450$. The denominator is valid when defined strictly over those three specific test groups, but was confusingly presented without an explicit breakdown.
