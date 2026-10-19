# Migration Manifest

**Date:** 2026-10-17  
**Purpose:** Document proposed and completed file organization changes.  
**Policy:** No files deleted. Only conservative moves to `archive/scratch/` after dependency verification. Canonical evidence, source code, raw data, and anything required for reproducibility stays in place.

---

## Files NOT Moved (Canonical / Reproducibility-Critical)

These files remain in their original locations. They are original evidence, source code, or required by build/test/experiment scripts.

### Source Code (do not move)
- `algorithms/source_ref/mlkem/` — instrumented ML-KEM implementation
- `algorithms/source_ref/mlkem_fault_hooks.c/.h` — fault hook integration
- `algorithms/source_ref/mldsa_fault_hooks.c/.h` — ML-DSA hooks
- `algorithms/oqs_wrapper.py` — Python OQS bindings
- `tfib_implementation/` — TFIB core library (libtfib.a + sources)
- `tfib_experiments/` — all experiment harnesses, runners, compiled binaries
- `fault_injection/` — Python fault injection framework
- `resilience/` — redundancy, integrity, retry, checkpoint modules
- `Makefile`, `CMakeLists.txt` — build system

### Raw Data (do not move)
- `tfib_experiments/phase2_step2c_trial_results.csv` — canonical 900-trial dataset (SHA-256 verified)
- `tfib_benchmark_raw.csv` — benchmark raw data (1.3 MB)
- `tfib_raw_results.csv`, `tfib_reproduced_results.csv`, `tfib_trial_level_results.csv`
- `results/` — all JSON/CSV result files
- `authoritative_results.csv`
- `claim_evidence_matrix.csv`, `closest_prior_art_comparison.csv`
- All CSVs in `phase*` root directories (contain trial-level data)

### Manuscripts and Critical Documents (do not move)
- `paper/` — manuscript, references, figures, tables
- `RESEARCH_MASTER_INDEX.md` — new central index
- `CHECKPOINT_README.md` — checkpoint documentation
- `README.md` — project README
- `contribution_analysis.md` — prior art positioning
- `final_contribution_decision.md` — research verdict
- `manuscript_corrections.md` — errata
- `research/EVIDENCE_LEDGER.md` — evidence tracking

### Test Vectors (do not move)
- `tests/` — FIPS KAT files, test suites
- `references/` — bibliography, test vectors

### Research Documents (do not move — referenced by other documents)
- `research/` — evidence ledger, architecture, fault model, experimental protocol, literature reviews, phase reports
- `research_redesign/` — systematic gap report, literature matrices

---

## Files Created (New Organization)

| New Path | Purpose |
|:---|:---|
| `RESEARCH_MASTER_INDEX.md` | Central index |
| `papers/paper-01-internal-fault-detection/RESEARCH_MAP.md` | Paper Track 1 map |
| `papers/paper-02-cross-layer-fault-interactions/RESEARCH_MAP.md` | Paper Track 2 map |
| `papers/paper-03-persistent-state-faults/RESEARCH_MAP.md` | Paper Track 3 map |
| `literature/ieee_candidates/IEEE_CANDIDATE_SHORTLIST.md` | IEEE paper shortlist |
| `literature/extraction/EXTRACTION_TEMPLATE.md` | PDF review template |
| `archive/MIGRATION_MANIFEST.md` | This file |

---

## Files Identified as SAFE TO ARCHIVE (but NOT moved yet)

The following files are candidates for moving to `archive/scratch/` in a future step. They are documented here for review. **No moves performed in this task** because:
1. Several are referenced by other phase reports (creating dependency chains)
2. Moving them provides low value vs. the risk of breaking references
3. The research record should be preserved during the convergence week

### Duplicate Root-Level Files (copies exist in `tfib_experiments/`)
| File (root) | Duplicate in | Notes |
|:---|:---|:---|
| `phase2_step2c_dependency_model.md` | `tfib_experiments/phase2_step2c_dependency_model.md` | Identical content |
| `phase2_step2c_experiment_design.md` | `tfib_experiments/phase2_step2c_experiment_design.md` | Identical content |
| `phase2_step2c_report.md` | `tfib_experiments/phase2_step2c_report.md` | Identical content |
| `phase2_step2c_trial_results.csv` | `tfib_experiments/phase2_step2c_trial_results.csv` | Identical content |
| `research_inventory.md` | `paper/research_inventory.md` | Identical content |

### Duplicate Root-Level Files (copies exist in `chatgpt/`)
| File (root) | Duplicate in | Notes |
|:---|:---|:---|
| `tfib_benchmark_raw.csv` | `chatgpt/tfib_benchmark_raw.csv` | Identical (1.3 MB each) |
| `tfib_reproduced_results.csv` | `chatgpt/tfib_reproduced_results.csv` | Identical |
| `tfib_trial_level_results.csv` | `chatgpt/tfib_trial_level_results.csv` | Identical |

### Redundant Review Packages
| Directory | Notes |
|:---|:---|
| `Step2C_A_Final_Review_Package/` | Bundled copies of Step 2C-A docs (236 KB) |
| `Step2C_A_Test_Label_Fix_Review/` | Test label fix review (36 KB) |
| `deploy_perf_bundle/` | Deployment performance bundle (4.9 MB) |

### Phase Report Directories (19 root-level)
These contain CSV data + markdown audit reports. Many are superseded by later phases but some contain unique raw trial data. Individual assessment needed before any move.

### `chatgpt/` Directory
Contains duplicated data files and audit runner source. The source files (`tfib_benchmark_audit.c`, `tfib_validity_audit_runner.c`) appear to be copies of files in `tfib_experiments/`. The `README.md` may contain useful provenance notes.

---

## Recommended Future Archiving (After Convergence Week)

Once the primary paper is submitted:
1. Move duplicate root-level `.md` and `.csv` files to `archive/scratch/duplicates/`
2. Move `Step2C_A_*` review packages to `archive/scratch/review_packages/`
3. Move `deploy_perf_bundle/` to `archive/scratch/deploy/`
4. Move `chatgpt/` to `archive/scratch/chatgpt_audit/`
5. Consolidate 19 root-level `phase*` directories into `archive/phases/`
6. Update any cross-references before moving

**Current policy: No moves performed. Clutter is documented, not forced.**
