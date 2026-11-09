# Repository Cleanup & Evidence Preservation Audit
## Safety Classification, Historical Provenance & Non-Destructive Hygiene Plan

**Audit Policy:** Strict Non-Destructive Principle. In academic research, preservation of empirical provenance and historical auditability strictly supersedes cosmetic cleanliness. No raw CSV, JSON log, historical manuscript backup, or source code file shall be deleted or modified.

---

## 1. Safety Classification Directory

Every major directory, artifact category, and root-level file in this repository is classified below into one of nine explicit preservation categories:

1. **Core Source:** Production C source code, algorithms, and build definitions. (Must retain).
2. **Active Experiment:** Test harnesses, validation suites, and active experiment runners. (Must retain).
3. **Reproducibility Artifact:** Independent verifiers, test vector headers, and pre-compiled object modules. (Must retain).
4. **Raw Evidence:** Primary per-trial CSV logs and execution traces. (Strictly preserved; never modify or delete).
5. **Historical Evidence:** Earlier phase campaign results, sensitivity matrices, and validation logs. (Strictly preserved).
6. **Documentation:** Research timeline, architecture handbooks, audit decisions, and handover manuals. (Must retain).
7. **Manuscript:** Active publication drafts, backup milestone revisions, and BibTeX bibliographies. (Must retain).
8. **Generated Duplicate / Archive Candidate:** Redundant copies of files created during multi-tool workflows. (Retain in current location; candidate for post-submission archiving).
9. **Temporary / Cache / Build Artifact:** OS metadata files and intermediate compiler object caches. (Candidate for safe pruning only after confirming zero unique data).

---

## 2. Directory-by-Directory Classification Table

| Path | File / Folder Purpose | Classification | Current Status | Recommended Action | Safety Justification |
|---|---|:---:|:---:|:---:|---|
| **`algorithms/`** | ML-KEM & ML-DSA source trees (`source_ref/`), reference implementations, and baseline wrappers. | **Core Source** | Active & Production | **Retain in place** | Contains the core cryptographic algorithms and fault hooks. Moving would break Makefile include paths. |
| **`tfib_implementation/`** | Hardened v2 Twiddle Factor Integrity Binding source (`tfib_ref.c`, `tfib_meta.c`, `tfib_core.c`, `libtfib.a`). | **Core Source** | Active & Hardened | **Retain in place** | Implements the v2 trusted reference twiddle checking and localized recovery. |
| **`tfib_experiments/`** | Canonical 900-trial experiment runner, independence test suites, and benchmark harnesses. | **Active Experiment** | Active & Validated | **Retain in place** | Contains active verification binaries and Step 2C-A runners. |
| **`phase18_audit/`** | 400-trial cleanroom production reproducer, raw trials CSV, and final audit decision reports. | **Raw Evidence & Active Experiment** | Complete & Certified | **Retain in place** | Contains primary Table 2 evidence (`raw_production_trials.csv`). |
| **`paper/`** | Working publication manuscript (`manuscript.md`), 10 historical milestone backups, figures, and `references.bib`. | **Manuscript** | Active & Audited | **Retain in place** | Primary working paper for submission. Backups preserve the 10-milestone audit trail. |
| **`papers/`** | Historical 3-paper framing drafts (`paper-01`, `paper-02`, `paper-03`). | **Historical Evidence** | Preserved | **Retain in place** | Preserves research track separation and persistent state framing. |
| **`docs/`** | Detailed research phase logs (Phase 0 through Phase 7L), mathematical audits, and handover manuals (`docs/handover/`). | **Documentation** | Comprehensive | **Retain in place** | Complete research documentation and historical phase audit trail. |
| **`docs/presentation/`** | Presentation outline, master progress report, defense question bank, and demo scripts. | **Documentation** | New Deliverables | **Retain in place** | Created specifically for tomorrow's presentation and defense. |
| **`results/`** | Historical processed results, sensitivity matrices, and JSON distributions from Phases 2, 7G, 7H, 7I, 15Q. | **Historical Evidence** | Preserved | **Retain in place** | Houses DMR baseline timing (`phase7h`) and inverse transform benchmarks (`phase7i`). |
| **`bin/`** | Compiled binaries and object files (`bin/obj/mlkem768_inst.o`, `test_fips_kats`, `production_reproducer`). | **Reproducibility Artifact** | Compiled | **Retain in place** | Pre-compiled binaries allow instant demonstration during presentation. |
| **`tests/`** | Correctness tests, FIPS KAT verification, and cross-implementation test scripts. | **Active Experiment** | Active | **Retain in place** | Unit testing infrastructure. |
| **`fault_injection/`** | Architectural fault injector framework modules. | **Core Source** | Preserved | **Retain in place** | Provides supporting injection interfaces. |
| **`adversarial_audit/`** | Adversarial review scripts and research gap assessments from Phase 1. | **Historical Evidence** | Audited | **Retain in place** | Contains evidence supporting research question formulation. |
| **`research_redesign/`** | Literature access registers, systematic search protocols, and gap closure matrices. | **Documentation** | Complete | **Retain in place** | Documents systematic literature review protocol. |
| **`Step2C_A_Final_Review_Package/`** | Audit review package for the Step 2C-A campaign. | **Documentation** | Complete | **Retain in place** | Documentation package for Step 2C-A review. |
| **`Step2C_A_Test_Label_Fix_Review/`** | Clarification audit for Step 2C-A Test 7 label. | **Documentation** | Complete | **Retain in place** | Traceability record for commit `4a2c4eb`. |
| **`deploy_perf_bundle/`** | Standalone deployment bundle prepared for external benchmarking. | **Generated Duplicate** | Complete | **Candidate for archive** | Duplicate copy of production sources; do not delete before submission. |
| **`chatgpt/`** | Duplicate benchmark scripts and validity logs generated during parallel LLM audits. | **Generated Duplicate** | Historical | **Candidate for archive** | Duplicates `tfib_benchmark_raw.csv` and `tfib_benchmark_audit.c`. Retain for provenance. |
| **`phase10_corrected_reproduction/`** | Historical Phase 10 conformance audit files. | **Historical Evidence** | Complete | **Retain in place** | Preserves reproducibility audit history. |
| **`phase11_conformance_audit/`** | FIPS 203 Section 7.3 implicit rejection oracle conformance dataset ($N=100$). | **Raw Evidence** | Complete | **Retain in place** | Primary evidence for Section 7.3 oracle matching. |
| **`phase12_reproducibility_audit/`** | Production reproducer validation files. | **Historical Evidence** | Complete | **Retain in place** | Traceability artifact. |
| **`phase13_final_evidence_audit/`** | Evidence reconciliation logs. | **Documentation** | Complete | **Retain in place** | Traceability artifact. |
| **`phase14_evidence_correction/`** | Evidence correction logs. | **Documentation** | Complete | **Retain in place** | Traceability artifact. |
| **`phase15_final_evidence_validation/`**| Evidence validation logs. | **Documentation** | Complete | **Retain in place** | Traceability artifact. |
| **`phase16_targeted_evidence_closure/`**| Circular verifier study raw dataset ($N=600$, `h1_activation_audit.csv`). | **Raw Evidence** | Complete | **Retain in place** | Primary evidence for Hypothesis 1 and Table 3. |
| **`phase17_prior_art/`** | Prior art review documents. | **Documentation** | Complete | **Retain in place** | Traceability artifact. |
| **`phase17a_verification/`** | DOI and bibliographic citation verification records. | **Documentation** | Complete | **Retain in place** | Verification record for citations. |
| **`phase17b_corrected/`** | Corrected manuscript draft, references list, and numerical reconciliation. | **Manuscript / Audit** | Complete | **Retain in place** | Intermediary manuscript milestone. |
| **`phase2_independent_validation/`**| Early countermeasure measurement logs. | **Historical Evidence** | Complete | **Retain in place** | Historical benchmark comparisons. |
| **`phase3_harness_audit/`** | Harness audit and supervisor decision brief. | **Documentation** | Complete | **Retain in place** | Historical decision brief. |
| **`phase4_evidence_reconciliation/`**| Timing claim reviews and baseline reconciliation. | **Documentation** | Complete | **Retain in place** | Historical reconciliation. |
| **`phase5_recovery_trust_audit/`** | Early recovery trust audit records. | **Documentation** | Complete | **Retain in place** | Historical audit trail. |
| **`phase6_verifier_falsification/`** | Falsification trials for circular verifiers. | **Historical Evidence** | Complete | **Retain in place** | Predecessor to Phase 16 circular verifier study. |
| **`phase7_independent_claim_audit/`** | Independent claim audit records and trial results. | **Historical Evidence** | Complete | **Retain in place** | Historical audit trail. |
| **`phase8_production_path_audit/`** | Production path audit tests and trace files. | **Historical Evidence** | Complete | **Retain in place** | Production link verification. |
| **`phase9_reproducibility_audit/`** | Reproducibility audit records. | **Documentation** | Complete | **Retain in place** | Historical audit trail. |
| **`references/`** | Known Answer Test (KAT) reference headers. | **Reproducibility Artifact** | Active | **Retain in place** | Header files needed by `test_fips_kats`. |
| **`requirements/`** | Project requirement tracking documents. | **Documentation** | Historical | **Retain in place** | Foundational requirement specifications. |
| **`research/`** | Phase 18 Gate A corpus, manifest, and validation records ($N=420$). | **Raw Evidence** | Complete | **Retain in place** | Contains deterministic PRF vector corpus. |
| **`resilience/`** | Baseline resilience framework interfaces. | **Core Source** | Preserved | **Retain in place** | Interfaces used in earlier resilience builds. |
| **`scripts/`** | Analysis and verification utility scripts. | **Active Experiment** | Active | **Retain in place** | Python and shell automation utilities. |

---

## 3. Root-Level Files Classification & Action Plan

| Root File Name | Purpose & Contents | Category | Recommendation |
|---|---|:---:|---|
| **`AYUSH.md`** | Comprehensive research handover handbook (October 19, 2026). | **Documentation** | **Retain in place** (Primary technical onboarding manual). |
| **`RESEARCH_MASTER_INDEX.md`** | Master index across all research phases and artifacts. | **Documentation** | **Retain in place** (Comprehensive reference index). |
| **`CHECKPOINT_README.md`** | Preserved checkpoint documentation for NTT fault resilience. | **Documentation** | **Retain in place** (Preserves Phase 7L checkpoint status). |
| **`README.md`** | Repository root README. | **Documentation** | **Retain in place** (Top-level overview). |
| **`Makefile`** | Primary project build file. | **Core Source** | **Retain in place** (Builds all test targets). |
| **`CMakeLists.txt`** | Supporting CMake configuration. | **Core Source** | **Retain in place** (Build definition). |
| **`tfib_benchmark_raw.csv`** | 40,000 raw decapsulation timing records across 4 conditions. | **Raw Evidence** | **STRICTLY RETAIN IN PLACE** (Primary performance evidence). |
| **`tfib_trial_level_results.csv`**| 900 canonical campaign trials (18 suites $\times$ 50 trials). | **Raw Evidence** | **STRICTLY RETAIN IN PLACE** (Primary Table 4 evidence). |
| **`tfib_raw_results.csv`** | Duplicate raw record of 900 canonical trials. | **Raw Evidence** | **Retain in place** (Backup raw record). |
| **`tfib_reproduced_results.csv`**| Summary table of the 18 reproduced suites. | **Historical Evidence** | **Retain in place** (Fast reference summary). |
| **`authoritative_results.csv`** | Authoritative claim-by-claim result matrix. | **Historical Evidence** | **Retain in place** (Claim reconciliation). |
| **`claim_evidence_matrix.csv`** | Audit matrix mapping claims to evidence files. | **Documentation** | **Retain in place** (Audit matrix). |
| **`closest_prior_art_comparison.csv`**| Comparison against Paul et al. and generic DMR. | **Documentation** | **Retain in place** (Literature review artifact). |
| **`contribution_analysis.md`** | Deep analysis of project scientific contributions. | **Documentation** | **Retain in place** (Contribution review). |
| **`experimental_gap_closure.md`** | Gap closure strategy documentation. | **Documentation** | **Retain in place** (Audit document). |
| **`final_contribution_decision.md`**| Formal decision log on paper contributions. | **Documentation** | **Retain in place** (Audit decision). |
| **`manuscript_corrections.md`** | Log of manuscript adjustments across phases. | **Documentation** | **Retain in place** (Revision history). |
| **`phase2_step2c_dependency_model.md`**| Countermeasure independence dependency model. | **Documentation** | **Retain in place** (Design specification). |
| **`phase2_step2c_docs_final.diff`**| Git diff of Step 2C-A documentation refinements. | **Documentation** | **Retain in place** (Review package). |
| **`phase2_step2c_experiment_design.md`**| Experiment design for the 900-trial campaign. | **Documentation** | **Retain in place** (Methodology document). |
| **`phase2_step2c_report.md`** | Detailed report of Step 2C-A campaign outcomes. | **Documentation** | **Retain in place** (Campaign report). |
| **`phase2_step2c_trial_results.csv`**| Precursor raw trial dataset for Step 2C-A. | **Raw Evidence** | **Retain in place** (Historical raw data). |
| **`research_extension_proposal.md`**| Proposal for post-submission extensions. | **Documentation** | **Retain in place** (Future roadmap). |
| **`research_inventory.md`** | Inventory of all research assets. | **Documentation** | **Retain in place** (Audit inventory). |
| **`tags_out.txt`** | Generated compiler tag output. | **Temporary Artifact** | **Candidate for pruning post-presentation**. |
| **`tfib_analysis.md`** | Primary scientific analysis of the TFIB extension. | **Documentation** | **Retain in place** (Core analysis document). |
| **`tfib_design.md`** | Architectural design and Theorem 1 proof for TFIB. | **Documentation** | **Retain in place** (Design specification). |
| **`tfib_execution_log.md`** | Execution trace of the 900-trial campaign. | **Documentation** | **Retain in place** (Execution trace). |
| **`tfib_failure_cases.md`** | In-depth analysis of common-mode twiddle failures. | **Documentation** | **Retain in place** (Failure analysis). |
| **`tfib_reproducibility_commands.md`**| Exact terminal commands to reproduce TFIB. | **Documentation** | **Retain in place** (Operational manual). |
| **`tfib_validity_audit.md`** | Independent validity audit of the TFIB extension. | **Documentation** | **Retain in place** (Audit report). |
| **`.DS_Store`** | macOS Finder metadata files. | **Temporary Artifact** | **Safe to remove** (Zero scientific value). |

---

## 4. Post-Presentation Archiving Recommendations

After the progress presentation and before final journal submission, consider the following non-destructive hygiene actions:
1. **Remove OS Artifacts:** Safely remove `.DS_Store` files across directories (`find . -name ".DS_Store" -delete`).
2. **Move Duplicate Bundles to `archive/`:** Move `deploy_perf_bundle/` and `chatgpt/` into `archive/external_bundles/` using `git mv` so history is preserved without cluttering root.
3. **Consolidate Root Markdown Summaries:** Move root-level campaign reports (e.g. `phase2_step2c_report.md`, `phase2_step2c_experiment_design.md`) into `docs/campaigns/` using `git mv`.
4. **Preserve Raw CSVs in Place:** Keep all `.csv` files in their original locations to ensure automated scripts and relative paths in Python tools do not break.

