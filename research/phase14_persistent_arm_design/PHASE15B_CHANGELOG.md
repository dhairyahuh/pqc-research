# Phase 15B Changelog: Controlled Persistent-Table Feasibility Pilot

**Date:** 2026-10-11  
**Author:** Skeptical Cryptographic Implementation Researcher  
**Context:** Phase 15B Controlled Persistent-Table Feasibility Pilot Execution  

---

## 1. Summary of Actions
This changelog documents all actions taken during Phase 15B to execute a strictly scoped, reversible feasibility pilot targeting the relocated operational twiddle table `mlk_zetas_page`.

* **Repository Integrity:** All 7 pre-existing tracked modifications and historical datasets were preserved intact. No changes were made to production cryptographic sources, headers, or production build configurations.
* **Scope Adherence:** All pilot activities used exclusively the isolated research build artifact (`bin/obj/mlkem768_persistent_reloc.o`) and the dedicated pilot harness (`research/phase14_persistent_arm_design/pilot_runner.c` -> `bin/pilot_runner`).
* **Preflight Compliance:** All 5 mandatory preflight checks (symbol alignment, live `vm_region_64` query, canary integrity, dry-run protection toggling, and clean baseline KAT decapsulation) passed with zero warnings before the first mutation.
* **Predeclared Pilot:** Exactly 16 predeclared trials were executed, verified, and logged in `PHASE15B_TRIAL_LEDGER.csv`.

---

## 2. Modified and Created Files

### Created Research Artifacts:
1. `research/phase14_persistent_arm_design/pilot_runner.c`:
   Dedicated pilot harness implementing the 5 preflight checks, transactional in-memory mutation/restoration lifecycle, canary padding verification, and per-trial logging.
2. `bin/pilot_runner`:
   Compiled research binary linking `pilot_runner.c` with `bin/obj/mlkem768_persistent_reloc.o`.
3. `research/phase14_persistent_arm_design/PHASE15B_TRIAL_LEDGER.csv`:
   Structured CSV recording the 16 trials with disaggregated fields: `trial_id`, `target_idx`, `bit_mask`, `mutation_status`, `consumption_status`, `crypto_endpoint`, `restoration_status`, `output_ss`, and `expected_behavior`.
4. `research/phase14_persistent_arm_design/PHASE15B_REPORT.md`:
   Comprehensive pilot feasibility report summarizing preflight evidence, trial outcomes, cryptographic oracle observations, and recommendations.
5. `research/phase14_persistent_arm_design/PHASE15B_CHANGELOG.md`:
   This changelog document.
