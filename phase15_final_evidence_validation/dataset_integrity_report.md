# Historical Dataset Integrity and Aggregation Audit Report

**Auditor:** Skeptical Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Subject:** Exhaustive Audit of Historical CSV Records, Identifier Hygiene, Seed Dependencies, and Aggregation Validity  
**Repository Scope:** All raw CSV files from Phase 5 through Phase 14  

---

## 1. Executive Summary

This report establishes the trial-level data integrity baseline for the ML-KEM-768 fault-resilience research repository. 

Across all examined raw datasets, every trial count has been dynamically verified by parsing actual CSV rows. **No missing rows, truncated records, or internal syntax errors were found.**

However, the audit identified three major methodological and statistical hazards in prior reports:
1. **Target Repurposing and Semantic Drift:** Identifiers such as `F4`, `F5`, and `F12` underwent radical redefinition between Phase 7 (where they denoted harness-level memory corruption) and Phases 8–13 (where they denoted production binary decapsulation).
2. **Seed Reuse and Non-Independence:** Production decapsulation trials (Phases 10, 12, 13) reused identical PRNG seeds across targets (`srand(0x1337C0DE + t)` for $t \in [0, 99]$), creating matched-pair dependencies across operational conditions.
3. **Invalid Statistical Pooling:** Previous phases pooled disparate fault injection mechanisms and execution tiers (combining simulated stack pointer corruption with authentic compiled binaries) into a single aggregate metric (e.g., Phase 13's "93.5% pooled blindness" and "0/1,300 pooled SDC"). This aggregation is statistically and scientifically invalid.

---

## 2. Row-Level Integrity and Trial Accounting

Every historical CSV was audited for total rows, header correctness, unique trial IDs, duplicate rows, and null fields:

| Dataset Path | Phase | Execution Tier | Claimed Rows | Actual Rows | Unique Trial IDs | Duplicate IDs | Corrupt / Null Fields |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `phase5_recovery_trust_audit/raw_trial_results.csv` | 5 | Harness Model | 1,300 | 1,300 | 1,300 | 0 | 0 |
| `phase6_verifier_falsification/raw_trial_results.csv` | 6 | Harness Model | 1,200 | 1,200 | 1,200 | 0 | 0 |
| `phase7_independent_claim_audit/derived_corrected_trial_results.csv` | 7 | Harness Model | 1,200 | 1,200 | 1,200 | 0 | 0 |
| `phase9_reproducibility_audit/raw_trial_results.csv` | 9 | Production Binary | 300 | 300 | 300 | 0 | 0 |
| `phase10_corrected_reproduction/raw_production_trials.csv` | 10 | Production Binary | 400 | 400 | 400 | 0 | 0 |
| `phase11_conformance_audit/invalid_ciphertext_trials.csv` | 11 | Production & Oracle | 100 | 100 | 100 | 0 | 0 |
| `phase11_conformance_audit/valid_ciphertext_trials.csv` | 11 | Production & Oracle | 100 | 100 | 100 | 0 | 0 |
| `phase12_reproducibility_audit/production_reproduction_trials.csv` | 12 | Production Binary | 400 | 400 | 400 | 0 | 0 |
| `phase13_final_evidence_audit/production_trial_recalculation.csv` | 13 | Production Binary | 400 | 400 | 400 | 0 | 0 |

**Finding:** The physical integrity of the raw CSV records is confirmed. The historical data has not been silently modified or repaired.

---

## 3. Detailed Audit of Target Naming Mutation

The following table traces the semantic evolution of targets across project phases:

| Target ID (Phase 14/15) | Phase 5 Name | Phase 6/7 Name | Phase 8–13 Name | Execution Tier | Semantic Mutation & Risk |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **F1** | `FT1_SAVED_OPERAND_POST_CAPTURE` | `F1_SAVED_OPERAND_BITFLIP` | `F1` | Harness Model | In-place snapshot bitflip. Scope unchanged. |
| **F2** | `FT2_SNAPSHOT_PRE_RETRY` | `F2_SNAPSHOT_PRE_RETRY_DIFFUSION` | `F2` | Harness Model | Bias/diffusion in snapshot. Scope unchanged. |
| **F3** | `FT3_MONITOR_PERSISTENT_COUNT_ZERO` | `F3_MONITOR_PERSISTENT_COUNT_ZERO` | `F3` | Harness Model | **Narrative override in Phase 8–13** (claimed 100% false recovery; raw data proves 0%). |
| **F4** | `FT4_MONITOR_ALLOW_RETRY_FORCE` | `F4_MONITOR_ALLOW_RETRY_FORCE` | `F4` (Transient Recovery) | **Production Binary (Shifted)** | **RADICAL SHIFT**: In Phase 6/7, F4 was a harness fault. In Phase 8–13, F4 was completely replaced by a production transient fault test. |
| **F5A** | `FT5_VERIFIER_INPUT_CORRUPT` | `F5_VERIFIER_DIFF_CALC_CORRUPT` | `F5A` (Recurring Bitflip) | **Production Binary (Shifted)** | **RADICAL SHIFT**: In Phase 6/7, F5 was a harness test. In Phase 10–13, F5 became F5A on production binary. |
| **F5B** | [None] | [None] | `F5B` (Force-Value Model) | **Production Binary (Added)** | Added in Phase 10 as software force-value model. |
| **F6** | `FT6_VERIFIER_RESULT_FORCE_ZERO` | `F6_VERIFIER_RESULT_FORCE_PASS` | `F6` | Harness Model | Verifier return code glitch. Scope unchanged. |
| **F7** | `FT7_RETRY_TRANSIENT_CLEAN` | `F7_RETRY_ARITHMETIC_GLITCH` | `F7` | Harness Model | **Inversion in Phase 8–13** (claimed 0%; raw data proves 94% false recovery). |
| **F8** | `FT8_RETRY_PERSISTENT_ALU` | `F8_VERIFIER_INPUT_OPERAND_CORRUPT` | `F8` | Harness Model | Verifier input operand corruption. |
| **F9** | `FT9_FO_PREDICATE_BYPASS_CORRUPT_KEY`| `F9_DSPC_COLLISION_MULTI_BIT` | `F9` | Harness Model | DSPC multi-bit collision. (Phase 13 copied obsolete 93% from P5). |
| **F10** | [None] | `F10_DSPC_STATE_BYPASS` | `F10` | Harness Model | DSPC state bypass. |
| **F11** | [None] | `F11_DSPC_CLEAN_CORRECTION` | `F11` | Harness Model | Single-bit clean correction. |
| **F12** | `FT10_CLEAN_CONTROL` | `F12_CLEAN_BASELINE_CONTROL` | `F12` | **Production Binary (Shifted)** | In Phase 6/7, F12 was a harness control. In Phase 8–13, F12 became clean production decapsulation. |

---

## 4. Evaluation of PRNG Seeds and Sample Independence

In the production decapsulation test runner (`phase13_final_evidence_audit/production_reproducer.c`):
```c
for (int t = 0; t < 100; t++) {
    srand(0x1337C0DE + t);
    mlkem768_keypair(pk, sk);
    mlkem768_enc(ct, ss_expected, pk);
    ...
}
```

### Critical Statistical Caveats:
1. **Matched Pairs Design:** Trial index $t$ in Target F12, Target F4, Target F5A, and Target F5B shares the exact same seed (`0x1337C0DE + t`), producing the exact same keypair $(pk, sk)$ and ciphertext $ct$.
2. **Effective Sample Size:** While 400 decapsulations were performed, they represent 100 distinct cryptographic instances evaluated under 4 experimental conditions.
3. **Statistical Validity:** Calculating separate confidence intervals for each target ($N=100$) is valid because the operational conditions (unfaulted, transient fault, recurring bitflip, force-value zero) are independent treatments. However, pooling all 400 trials to claim a single confidence bound based on 400 degrees of freedom over-represents the diversity of the underlying cryptographic keys.

---

## 5. Statistical Invalidity of Historical Pooling

Phase 13 reported two pooled metrics that must be permanently retracted:
1. **"Global Pooled $H_1$ Blindness = 93.5% (561/600)":**
   - **Why Invalid:** Phase 13 arbitrarily selected 6 harness targets (F1, F2, F3, F6, F9, F10) while excluding others (F7, F8, F11) without a defensible theoretical rationale. Furthermore, the sum of 561 relied on a fabricated count of 100 for F3 (raw: 0) and an erroneous count of 70 for F2 (raw: 100).
   - **Methodological Rule:** Different fault injection mechanisms target fundamentally different failure modes (memory corruption vs control flow vs arithmetic glitches). Pooling them into a single percentage obscures mechanism-specific behavior.
2. **"Global Pooled $H_2$ SDC Absence = 0/1,300 (0.0%, 95% CI: [0.0%, 0.28%])":**
   - **Why Invalid:** This metric combined 900 harness-model trials (which execute synthetic standalone C code) with 400 compiled production binary trials (which execute native NTT and FO routines).
   - **Methodological Rule:** Results from different execution tiers must never be pooled. Production binary resilience must be reported exclusively from production binary executions ($0/400$, 95% CI: $[0.0\%, 0.95\%]$).

---

## 6. Audit Conclusion

All trial counts in Phase 15 are derived directly from actual rows. All target mappings have been uncoupled from historical narrative overrides. The repository evidence is rigorously separated into:
- **Tier 1: Harness Models** ($N=100$ per target, 9 targets evaluated).
- **Tier 2: Production Objects** ($N=100$ per target, 4 targets evaluated).
- **Tier 3: Conformance Vectors** ($N=100$ invalid ciphertext mutations).

Pooling across tiers is strictly prohibited.
