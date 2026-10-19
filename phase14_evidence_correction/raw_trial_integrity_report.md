# Raw Trial Integrity and Historical Telemetry Report

**Auditor:** Skeptical Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Subject:** Integrity, Traceability, and Naming Drift across Historical Trial Datasets  
**Datasets Audited:**
1. `phase5_recovery_trust_audit/raw_trial_results.csv` (1,300 trials)
2. `phase6_verifier_falsification/raw_trial_results.csv` (1,200 trials)
3. `phase7_independent_claim_audit/derived_corrected_trial_results.csv` (1,200 trials)
4. `phase9_reproducibility_audit/raw_trial_results.csv` (300 trials)
5. `phase10_corrected_reproduction/raw_production_trials.csv` (400 trials)
6. `phase12_reproducibility_audit/production_reproduction_trials.csv` (400 trials)
7. `phase13_final_evidence_audit/production_trial_recalculation.csv` (400 trials)

---

## 1. Executive Summary

This report documents the row-by-row integrity of the raw experimental datasets in the repository. 

Key findings:
1. **Row Integrity:** All historical CSV files possess intact rows with complete column headers and zero duplicate `trial_id` values within their respective files. No truncated rows or syntax corruptions were found.
2. **Dataset Divergence:** The repository contains two fundamentally different tiers of experiments:
   - **Tier 1: Harness Models (Phases 5–7):** Synthetic standalone C harness (`genuine_recovery_falsification_harness.c` and `genuine_phase7_audit_harness.c`) evaluating memory corruption in simulated in-place stack snapshots.
   - **Tier 2: Compiled Production Binaries (Phases 9–13):** Authentic compiled C objects (`bin/obj/mlkem768_inst.o` + `bin/obj/mlkem_fault_hooks.o`) exercising the native NTT monitor and Fujisaki-Okamoto loop.
3. **Severe Naming Drift and Target Mutation:** Target labels mutated significantly across phases:
   - In Phase 5, targets were named `FT1` through `FT10`.
   - In Phases 6 and 7, targets were named `F1` through `F12`, all representing harness simulations.
   - In Phase 8, the authors repurposed the IDs `F4`, `F5`, and `F12` to represent *production object* tests, while retaining `F1, F2, F3, F6, F7, F8, F9, F10, F11` as harness simulations.
   - In Phase 10, `F5` was bifurcated into `F5A` (recurring bit-inversion) and `F5B` (force-value to zero).
4. **Seed Reuse across Targets:** Production test suites (Phases 10, 12, 13) seeded RNG with `srand(0x1337C0DE + t)` for $t \in [0, 99]$ across each target. Thus, tests across targets F12, F4, F5A, and F5B represent matched pairs over the exact same 100 keypairs and ciphertexts, rather than 400 independent keys.
5. **Data That Cannot Be Reconciled:** The Phase 8–13 summary tables claimed $H_1 = 100\%$ for Target F3 and $H_1 = 0\%$ for Target F7. Neither claim can be reconciled with raw data: raw CSV records show $H_1 = 0\%$ for F3 and $H_1 = 94\%$ for F7. The reported numbers were narrative fabrications.

---

## 2. Dataset Inventory and Integrity Metrics

| Dataset Path | Phase | Execution Tier | Total Rows | Target Count | Unique IDs | Duplicate Rows | Missing Rows | Trial ID Range |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `phase5_recovery_trust_audit/raw_trial_results.csv` | 5 | Harness Model | 1,300 | 10 | 1,300 | 0 | 0 | 1 – 1300 |
| `phase6_verifier_falsification/raw_trial_results.csv` | 6 | Harness Model | 1,200 | 12 | 1,200 | 0 | 0 | 1 – 1200 |
| `phase7_independent_claim_audit/derived_corrected_trial_results.csv` | 7 | Harness Model | 1,200 | 12 | 1,200 | 0 | 0 | 1 – 1200 |
| `phase9_reproducibility_audit/raw_trial_results.csv` | 9 | Production Binary | 300 | 3 | 300 | 0 | 0 | 0 – 299 |
| `phase10_corrected_reproduction/raw_production_trials.csv` | 10 | Production Binary | 400 | 4 | 400 | 0 | 0 | 0 – 399 |
| `phase12_reproducibility_audit/production_reproduction_trials.csv` | 12 | Production Binary | 400 | 4 | 400 | 0 | 0 | 0 – 399 |
| `phase13_final_evidence_audit/production_trial_recalculation.csv` | 13 | Production Binary | 400 | 4 | 400 | 0 | 0 | 0 – 399 |

---

## 3. Analysis of Target Naming Drift and Semantic Divergence

Between Phase 5 and Phase 13, target identifiers underwent radical semantic shifts without explicit deprecation warnings:

```
Phase 5 (Harness)      Phase 6/7 (Harness)               Phase 8-13 (Mixed Harness & Production)
-----------------      -------------------               ---------------------------------------
FT1_SAVED_OPERAND  ->  F1_SAVED_OPERAND_BITFLIP      ->  F1 (Harness Model)
FT2_SNAPSHOT_PRE   ->  F2_SNAPSHOT_PRE_RETRY_DIFF    ->  F2 (Harness Model)
FT3_MONITOR_ZERO   ->  F3_MONITOR_PERSISTENT_COUNT   ->  F3 (Harness Model, Narrative Overridden)
FT4_ALLOW_RETRY    ->  F4_MONITOR_ALLOW_RETRY_FORCE  ->  [REPLACED] F4 Transient Fault (Production Binary)
FT5_VERIFIER_INPUT ->  F5_VERIFIER_DIFF_CALC_CORRUPT ->  [REPLACED] F5A/F5B Persistent Fault (Production Binary)
FT6_RESULT_FORCE   ->  F6_VERIFIER_RESULT_FORCE_PASS ->  F6 (Harness Model)
FT7_RETRY_TRANSI   ->  F7_RETRY_ARITHMETIC_GLITCH    ->  F7 (Harness Model, Narrative Overridden)
FT8_RETRY_PERSIST  ->  F8_VERIFIER_INPUT_OPERAND     ->  F8 (Harness Model)
FT9_FO_PREDICATE   ->  F9_DSPC_COLLISION_MULTI_BIT   ->  F9 (Harness Model)
[None]             ->  F10_DSPC_STATE_BYPASS         ->  F10 (Harness Model)
[None]             ->  F11_DSPC_CLEAN_CORRECTION     ->  F11 (Harness Model)
FT10_CLEAN_CONTROL ->  F12_CLEAN_BASELINE_CONTROL    ->  [REPLACED] F12 Clean Control (Production Binary)
```

### Critical Auditing Caveats:
1. **Target ID Collisions:** In Phase 7, Target 3 is named `F4_MONITOR_ALLOW_RETRY_FORCE` and Target 4 is named `F5_VERIFIER_DIFF_CALC_CORRUPT`. In Phase 8–13, `F4` and `F5` refer to completely different tests executed against `bin/obj/mlkem768_inst.o`. Any analysis pooling Phase 7 by string target ID will silently conflate harness tests with production object tests!
2. **Irreconcilable Narrative Overrides:**
   - **Target F3:** Phase 6/7 raw CSV records show that forcing persistent count to zero resulted in `mismatch_count = 1, recovered_count = 0, verifier_passed = 0`. The monitor arithmetic check rejected the butterfly computation. The trial was safely rejected (`h1 = 0`). Phase 8 claimed $H_1 = 100\%$ on the theoretical premise that zeroing persistent count *should* cause unconditional retry. That claim was never verified by raw data.
   - **Target F7:** Phase 6/7 raw CSV records show `verifier_passed = 94, retry_matches_ref = 0, h1 = 94`. In 94 out of 100 trials, the arithmetic glitch allowed the verifier to pass a corrupt computation. Phase 8–13 claimed F7 had $H_1 = 0\%$ ("Safe fail-stop detected"). This directly contradicts the raw telemetry.

---

## 4. Evaluation of Random Seeds and Independence Assumptions

In the production reproduction trial pipelines (Phases 10, 12, 13):
```c
for (int t = 0; t < 100; t++) {
    srand(0x1337C0DE + t);
    mlkem768_keypair(pk, sk);
    mlkem768_enc(ct, ss_expected, pk);
    ...
}
```
### Implications for Statistical Analysis:
1. **Matched Pair Design:** Target F12 trial $t$, Target F4 trial $t$, Target F5A trial $t$, and Target F5B trial $t$ share identical public keys $pk$, secret keys $sk$, and ciphertexts $ct$.
2. **Degrees of Freedom:** The 400 production trials evaluate 100 distinct cryptographic instances under 4 different operational conditions.
3. **Statistical Limitation:** Calculating confidence intervals assuming 400 independently and identically distributed (i.i.d.) random cryptographic keys is technically an over-estimate of sample diversity; the sample space of keys is $N = 100$. However, because each target executes an independent operational condition (clean, transient, recurring, force-zero), per-target statistics ($N=100$) remain strictly valid.

---

## 5. Classification Reconciliation Across Historical Datasets

| Phase | Raw Outcome Column | Classifications Observed | Status Code Used | Telemetry Integrity |
| :---: | :--- | :--- | :---: | :--- |
| **5** | `classification` | `REJECTED_DOWNSTREAM_FO`, `SAFELY_REJECTED_MONITOR`, `RECOVERED_GENUINE`, `INCONCLUSIVE`, `CORRECT_CLEAN_EXECUTION` | `0x5A5A5A5A`, `0xA5A5A5A5` | Intact, but uses non-production mock status values. |
| **6** | `classification` | Same as Phase 5 | `0x5A5A5A5A`, `0xA5A5A5A5` | Reference values in `ref_u, ref_v` were buggy (-1); corrected in Phase 7. |
| **7** | `classification` | Same as Phase 5 | `0x5A5A5A5A`, `0xA5A5A5A5` | Fully reconciled reference values; verified oracle computations. |
| **9** | `outcome` | `GENUINE_RECOVERY`, `SAFE_FAIL_STOP` | `0x5A5A5A5A`, `0xFFFFFFFF` | Authentic production status codes; 300 trials. |
| **10** | `outcome` | `CLEAN_SUCCESS`, `GENUINE_RECOVERY`, `SAFE_FAIL_STOP` | `0x5A5A5A5A`, `0xFFFFFFFF` | Authentic production status codes; 400 trials. |
| **12** | `classification` | `CLEAN_SUCCESS`, `GENUINE_RECOVERY`, `SAFE_FAIL_STOP` | `0x5A5A5A5A`, `0xFFFFFFFF` | Includes full 32-byte hex hashes of outputs and oracles. |
| **13** | `classification` | `CLEAN_SUCCESS`, `GENUINE_RECOVERY`, `SAFE_FAIL_STOP` | `0x5A5A5A5A`, `0xFFFFFFFF` | Bit-for-bit identical to Phase 12 reproduction. |

---

## 6. Audit Conclusion

The raw records in [`derived_corrected_trial_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase7_independent_claim_audit/derived_corrected_trial_results.csv) (Phase 7) and [`production_trial_recalculation.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase13_final_evidence_audit/production_trial_recalculation.csv) (Phase 13/14) are structurally sound and complete. 

However, all subsequent summaries in Phases 8, 9, 10, 11, 12, and 13 failed to parse the raw Phase 7 CSV, relying instead on flawed narrative tables. Phase 14 establishes the first genuine, dynamic recalculation directly from these raw CSV files.
