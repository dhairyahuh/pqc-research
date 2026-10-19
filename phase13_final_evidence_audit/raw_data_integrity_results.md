# Raw Data Integrity Audit & Forensic Reconstruction

**Auditor:** Skeptical Cryptographic Implementation Auditor  
**Date:** October 2026  
**Scope:** File Integrity, Row Counts, Seed Schedules, and Classification Drift Across Phases 5–13  

---

## 1. Forensic Inventory of Historical Raw Datasets

All raw trial logs preserved in the repository were evaluated for file size, row count, schema consistency, and SHA-256 hash:

| Phase | Relative Filepath | Size (Bytes) | Rows | Unique Trial IDs | SHA-256 Hash |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Phase 5** | `phase5_recovery_trust_audit/raw_trial_results.csv` | 124,649 | 1,300 | 1,300 / 1,300 | `23ca1087cf2ffdbd36da283f51197ea4fbe431522f183c274211158a7413a967` |
| **Phase 6** | `phase6_verifier_falsification/raw_trial_results.csv` | 156,664 | 1,200 | 1,200 / 1,200 | `184fc3777d13b4eeb6e8e815e961c0e9d6d5ef0f51d8b1e4284897d1e89dfbe7` |
| **Phase 7** | `phase7_independent_claim_audit/derived_corrected_trial_results.csv` | 158,929 | 1,200 | 1,200 / 1,200 | `55d3e09848f07fb1f99a8039ea861a9b2d861642289fcf290135d97f3747cb90` |
| **Phase 9** | `phase9_reproducibility_audit/raw_trial_results.csv` | 25,610 | 300 | 300 / 300 | `602264c7608ea8344eebfe97645169a842f1f6c09aa30bfa511b05814ce34907` |
| **Phase 10**| `phase10_corrected_reproduction/raw_production_trials.csv` | 37,418 | 400 | 400 / 400 | `0e386ab0fe6b2a0953ef054fb4a7df2d596495bca612e4c49aa5cfa7975cf523` |
| **Phase 11**| `phase11_conformance_audit/fault_output_revalidation.csv` | 124,294 | 400 | 400 / 400 | `49635b719001379eb05ad88df302e1c94b79669527ec3c399b5314eb44747eb1` |
| **Phase 12**| `phase12_reproducibility_audit/production_reproduction_trials.csv` | 185,729 | 400 | 400 / 400 | `e5a968846c48325dbfeadfe60f85cf75eb37a5ea79c7e0c46b621e25e9854d9b` |
| **Phase 13**| `phase13_final_evidence_audit/production_trial_recalculation.csv` | 185,729 | 400 | 400 / 400 | `e5a968846c48325dbfeadfe60f85cf75eb37a5ea79c7e0c46b621e25e9854d9b` |

---

## 2. Integrity Analysis Findings

### 2.1 Trial Count Uniformity & ID Uniqueness
- Every evaluated target across every phase contains exactly $N=100$ trials.
- No partial, truncated, or duplicate trial records exist within any individual dataset.
- Trial identifiers are strictly monotonic ($1 \dots N$ or $0 \dots N-1$).

### 2.2 PRNG Determinism & Seed Schedules
- **Fault Reproduction Suite (F12, F4, F5A, F5B):**  
  In Phases 10, 11, 12, and 13, all fault trials used the deterministic seed schedule `srand(0x1337C0DE + t)`. This ensures exact reproducibility across runs while generating 100 distinct ephemeral keypairs and ciphertexts.
- **Valid and Invalid Ciphertext Campaigns:**  
  Phase 11 used `srand(0x4D4C4B00 + t)` (valid) and `srand(0x5A5A0000 + t)` (invalid), avoiding seed collision with fault injection campaigns.

---

## 3. History of Anomalies and Classification Drift

The audit confirmed four historical anomalies and verified their resolution:

1. **Phase 9 Target F12 Misclassification:**  
   - In Phase 9, all 100 trials of Target F12 (clean baseline) were labeled `GENUINE_RECOVERY` because the automated evaluation script checked `status == 0x5A5A5A5A` without checking whether a fault had triggered.
   - This was corrected in Phases 10–13 by requiring `trig == 0 && mismatch == 0 && rec == 0 -> CLEAN_SUCCESS`.
2. **Phase 8 Narrative Text Typo:**  
   - In Phase 8, the narrative summary stated "461 of 1,200 trials" exhibited H1, while the data table in the same report summed to 561 ($98 + 70 + 100 + 100 + 93 + 100$).
   - This was a clerical typo in the text and was rectified in Phase 10.
3. **Phase 5 to Phase 6 Target Renaming:**  
   - Targets `FT1` through `FT10` in Phase 5 were expanded and renamed `F1` through `F12` in Phase 6 to decouple unmitigated and mitigated sub-experiments into distinct target rows.
4. **Phase 10 Production Oracle Circularity:**  
   - In Phase 10, expected rejection keys were computed by calling `mlkem768_shake256` from `mlkem768_inst.o`.
   - In Phases 11–13, this was replaced with an independent clean-room Keccak oracle.
