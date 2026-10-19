# Raw Data Integrity Audit Across Phases 5–11

**Auditor:** Skeptical Cryptographic Implementation Auditor  
**Date:** October 2026  
**Scope:** Forensic Traceability, File Integrity, and Labeling Anomalies Across All Historical Phase CSVs  

---

## 1. Inventory and Hash Verification of Raw Data Files

Every raw trial file in the repository was inspected for byte-level integrity:

| Phase | Raw Data Filepath | File Size (Bytes) | Row Count | SHA-256 Hash |
| :--- | :--- | :---: | :---: | :--- |
| **Phase 5** | `phase5_recovery_trust_audit/raw_trial_results.csv` | 124,649 | 1,300 | `23ca1087cf2ffdbd36da283f51197ea4fbe431522f183c274211158a7413a967` |
| **Phase 6** | `phase6_verifier_falsification/raw_trial_results.csv` | 156,664 | 1,200 | `184fc3777d13b4eeb6e8e815e961c0e9d6d5ef0f51d8b1e4284897d1e89dfbe7` |
| **Phase 7** | `phase7_independent_claim_audit/derived_corrected_trial_results.csv` | 158,929 | 1,200 | `55d3e09848f07fb1f99a8039ea861a9b2d861642289fcf290135d97f3747cb90` |
| **Phase 9** | `phase9_reproducibility_audit/raw_trial_results.csv` | 25,610 | 300 | `602264c7608ea8344eebfe97645169a842f1f6c09aa30bfa511b05814ce34907` |
| **Phase 10**| `phase10_corrected_reproduction/raw_production_trials.csv` | 37,418 | 400 | `0e386ab0fe6b2a0953ef054fb4a7df2d596495bca612e4c49aa5cfa7975cf523` |
| **Phase 11**| `phase11_conformance_audit/fault_output_revalidation.csv` | 124,294 | 400 | `49635b719001379eb05ad88df302e1c94b79669527ec3c399b5314eb44747eb1` |
| **Phase 12**| `phase12_reproducibility_audit/production_reproduction_trials.csv` | 159,850 | 400 | `f2d1e2e92cf0e6dbf0e4b85da01f37e40cf7d288a38bc16db8ba21ee62eb2957` |

---

## 2. Integrity and Anomaly Analysis

### 2.1 Duplicate Trial Identifiers and Trial Counts
- **Trial ID Uniqueness:** Every CSV file exhibits 100% unique trial identifiers within its own dataset (e.g. 1,300 unique IDs in Phase 5; 1,200 in Phase 6/7; 400 in Phases 10–12).
- **Trial Count Uniformity:** Every target in every phase was tested with exactly $N=100$ trials. No truncated runs or missing records were identified.

### 2.2 Seed Analysis and PRNG Determinism
- **Phase 5 & 6:** Seed generation used deterministic seed schedules (`0x1337C0DE + t` or loop indices).
- **Phase 10, 11, and 12:** All fault trials across Targets F12, F4, F5A, and F5B used the explicit deterministic seed schedule `srand(0x1337C0DE + t)`. This ensures exact cycle-by-cycle reproducibility across test executions while testing 100 distinct ephemeral keypairs and ciphertexts.
- **Valid and Invalid Ciphertext Seeds:** Phase 11 and 12 used `0x4D4C4B00 + t` and `0x5A5A0000 + t` to eliminate overlap with the fault injection campaigns.

### 2.3 Labeling Inconsistencies and Classification Drift

The audit uncovered four major classification and labeling discrepancies across earlier phases:

1. **Phase 9 Target F12 Misclassification (`GENUINE_RECOVERY` vs. `CLEAN_SUCCESS`):**  
   - *Anomaly:* In `phase9_reproducibility_audit/raw_trial_results.csv`, all 100 trials of F12 (Clean Baseline Control) were logged as `GENUINE_RECOVERY`.
   - *Cause:* The Phase 9 evaluation script assigned `GENUINE_RECOVERY` to any trial returning `status == 0x5A5A5A5A` without checking whether a fault had been armed or triggered.
   - *Correction:* Corrected in Phase 10, 11, and 12 by introducing rule `trig == 0 && mismatch == 0 && rec == 0 -> CLEAN_SUCCESS`.
2. **Phase 8 Typo in Pooled $H_1$ Narrative ($461$ vs. $561$):**  
   - *Anomaly:* In `phase8_production_path_audit/revised_h1_h2_results.md` Section 3.1, the prose stated: *"Occurs in 461 of 1,200 trials"*.
   - *Cause:* Clerical arithmetic error. The table rows in that same document clearly showed $98 + 70 + 100 + 100 + 93 + 100 = 561$.
   - *Correction:* Formally audited and corrected to $561 / 600$ in Phase 10.
3. **Phase 5 vs. Phase 6 Target Renaming:**  
   - In Phase 5, targets were named `FT1` through `FT10`.
   - In Phase 6, they were renamed `F1` through `F12` to decouple unmitigated and mitigated configurations into distinct target rows.
4. **Phase 9 Merged Target F5 vs. Phase 10/11/12 Bifurcation (F5A and F5B):**  
   - *Anomaly:* Phase 9 tested a single `F5_PERSISTENT_REJECTION` target using bit-flip semantics.
   - *Correction:* Phase 10 bifurcated this into `F5A` (recurring bit-inversion) and `F5B` (software force-value model $t \leftarrow 0$) to distinguish persistent oscillatory bit flips from stuck-at-zero faults. Both produce identical safe fail-stop outcomes (`status = 0xFFFFFFFF`).

---

## 3. Operational Definitions of $H_1$ and $H_2$

To prevent ambiguity, operational definitions were strictly maintained during recalculation:

- **Operational $H_1$ (Internal False Recovery):**  
  The internal recovery monitor records successful recovery (`recovered_count > 0` or internal status `0x5A5A5A5A`), but the recovered arithmetic polynomial state differs from an independently computed fault-free reference:
  $$H_1 \iff (\text{Monitor Declares Success}) \land (\mathbf{r}_{\text{recovered}} \ne \mathbf{r}_{\text{reference}})$$
- **Operational $H_2$ (Accepted Invalid Output / Silent Data Corruption):**  
  The complete decapsulation routine emits an invalid shared secret ($K_{\text{out}} \ne K_{\text{valid}}$), yet accepts it as valid without triggering implicit rejection:
  $$H_2 \iff (\text{Status} = \text{0x5A5A5A5A} \land K_{\text{out}} \ne K_{\text{valid}}) \lor (K_{\text{out}} \ne K_{\text{valid}} \land K_{\text{out}} \ne K_{\text{rej}})$$
