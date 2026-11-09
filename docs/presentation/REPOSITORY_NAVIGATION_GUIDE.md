# Repository Navigation Guide
## Fast Index to Core Code, Evidence Data, Benchmarks, and Documentation

This guide provides direct clickable links and paths to all critical research assets in this repository. Use this to quickly navigate the codebase during your presentation preparation and defense.

---

## 1. Core Cryptographic Implementation & Monitoring

| Component | Path | Key File(s) & Lines | Description |
|---|---|---|---|
| **Core ML-KEM Source** | [`algorithms/source_ref/mlkem/`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/) | [`kem.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c), [`poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c), [`indcpa.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/indcpa.c) | Official NIST FIPS 203 reference implementation (`mlkem-native` fc269bc2d106) with zero heap allocation. |
| **Cooley-Tukey Butterfly** | [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L375-L425) | `mlk_ntt_butterfly_block` (Lines 375–425) | Implements forward NTT butterflies with register snapshotting (`u_saved, v_saved`) and monitor hooks. |
| **Gentleman-Sande Butterfly**| [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L535-L590) | `mlk_invntt_layer` (Lines 535–590) | Implements inverse NTT butterflies with operand snapshots and inverse monitor hooks. |
| **Baseline Monitor** | [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L600-L665) | `native_ntt_monitor_butterfly` (Lines 600–665) | Implements difference/sum invariant checks and in-place register rollback. |
| **Decoupled Inverse Monitor**| [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L804-L874) | `native_invntt_monitor_butterfly` (Lines 804–874) | Implements decoupled adder-rail and multiplier-rail checks (zero modular divisions). |
| **Persistent Fault Quenching**| [`algorithms/source_ref/mlkem/src/kem.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c#L484-L520) | `crypto_kem_dec` (Lines 484–520) | Intercepts persistent monitor counter, forces `fail = 0xFF`, and outputs FIPS 203 rejection key. |
| **Hardened v2 Twiddle Binding**| [`tfib_implementation/`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/) | [`tfib_ref.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_ref.c), [`tfib_core.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_core.c) | Implements trusted reference twiddle table `tfib_zetas_ref[128]` to close Theorem 1 twiddle blindness. |

---

## 2. Active Experiments & Test Suites

| Component | Path | Binary / Script | Description |
|---|---|---|---|
| **FIPS KAT Verification** | [`tests/test_fips_kats.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tests/test_fips_kats.c) | `./bin/test_fips_kats` | Verifies full Known Answer Tests for ML-KEM-512/768/1024 and ML-DSA-44/65/87. |
| **Cleanroom 400 Reproducer**| [`phase18_audit/production_reproducer.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/production_reproducer.c) | `./phase18_audit/production_reproducer` | Runs 400 cleanroom trials on compiled production binaries (`mlkem768_inst.o`). |
| **Countermeasure Independence**| [`tfib_experiments/test_step2c_countermeasure_independence.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/test_step2c_countermeasure_independence.c) | `./tfib_experiments/test_step2c_countermeasure_independence` | 9-test automated suite verifying twiddle detection, checker-logic resilience, and fail-stop containment. |
| **Canonical Campaign Runner**| [`tfib_experiments/tfib_experiment_runner.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/tfib_experiment_runner.c) | `./tfib_experiments/tfib_experiment_runner` | Executes the 900-trial canonical campaign across 18 experimental suites. |
| **Benchmark Suite** | [`tfib_experiments/tfib_benchmark.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/tfib_benchmark.c) | `./tfib_experiments/tfib_benchmark` | Captures high-precision nanosecond timings for Baseline, TFIB-Ref, and TFIB-Meta. |

---

## 3. Raw Empirical Datasets & Benchmark Records

| Dataset Description | Path | Sample Count ($N$) | Key Findings |
|---|---|:---:|---|
| **Cleanroom Production Trials** | [`phase18_audit/raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv) | $400$ trials | 100/100 Clean Success, 100/100 Transient Recovery, 200/200 Fail-Stop, **0/300 SDC**. |
| **Canonical Campaign Results** | [`tfib_trial_level_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_trial_level_results.csv) | $900$ trials | 150 controls + 750 active faults across 18 suites; **0/750 SDC** ($\le 0.49\%$ bound). |
| **Raw 40,000-Run Benchmark** | [`tfib_benchmark_raw.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_benchmark_raw.csv) | $40{,}000$ runs | Baseline median $145.96\,\mu\text{s}$, TFIB-Ref median $173.15\,\mu\text{s}$ (+18.63% overhead). |
| **Circular Verifier Blindness**| [`phase16_targeted_evidence_closure/h1_activation_audit.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/h1_activation_audit.csv) | $600$ trials | 591/600 false passes (**98.5% blindness**) for unshielded verifiers reading live registers. |
| **Twiddle Mutation Pilot** | [`results/phase15q/trial_ledger.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase15q/trial_ledger.csv) | $16$ trials | 11 active twiddle mutations caught by downstream FO re-encryption with 0 SDC. |
| **DMR Latency Baseline** | [`results/phase7h/processed/phase7h_timing_distribution.json`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase7h/processed/phase7h_timing_distribution.json) | $2{,}000$ iterations | Sequential software DMR measured at **$+99.33\%$** latency overhead. |
| **End-to-End Decapsulation**| [`results/phase7i/processed/phase7i_e2e_results.json`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase7i/processed/phase7i_e2e_results.json) | $2{,}000$ iterations | Monitored decapsulation measured at **$+16.9\%$** latency overhead under `-O3`. |

---

## 4. Manuscript & Publication Materials

| Document | Path | Status | Key Information |
|---|---|:---:|---|
| **Primary Working Manuscript** | [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) | **Ready with Limitations** | $\approx 7{,}500$ words, 4 formal tables, 24 verified references. |
| **BibTeX Citations** | [`paper/references.bib`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/references.bib) | Verified | 24 audited digital library entries (DOIs cross-checked). |
| **Manuscript Milestone Backups**| [`paper/manuscript.md.backup_phase2c`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/) through `backup_phase2r` | Preserved | Complete unbroken 10-milestone revision register. |
| **Literature Gap Analysis** | [`docs/state_of_art_gap_analysis.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/state_of_art_gap_analysis.md) | Complete | Comprehensive comparative study against prior literature. |
| **Literature Access Register** | [`research_redesign/LITERATURE_ACCESS_REGISTER.md`](file:///Users/dhairyajain/Desktop/pqc%20research/research_redesign/LITERATURE_ACCESS_REGISTER.md) | Verified | Access levels for reviewed papers (IEEE, ACM, Elsevier). |

---

## 5. Handover Manuals & Research History

| Guide / History | Path | Target Audience | Key Contents |
|---|---|:---:|---|
| **AYUSH Handover Handbook** | [`AYUSH.md`](file:///Users/dhairyajain/Desktop/pqc%20research/AYUSH.md) | New Researcher | Complete 24-section technical handbook, glossary, and handover protocol. |
| **Research Master Index** | [`RESEARCH_MASTER_INDEX.md`](file:///Users/dhairyajain/Desktop/pqc%20research/RESEARCH_MASTER_INDEX.md) | Full Team | Directory and phase index across the entire repository. |
| **Phase-by-Phase Timeline** | [`docs/handover/RESEARCH_TIMELINE.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/handover/RESEARCH_TIMELINE.md) | History | Chronological milestone progression from Phase 0 to Phase 18. |
| **Phase Experimental Registry**| [`docs/handover/PHASE_INDEX.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/handover/PHASE_INDEX.md) | History | Complete experimental catalog across all research phases. |
| **Claim-to-Evidence Ledger** | [`docs/handover/CLAIM_TO_EVIDENCE_LEDGER.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/handover/CLAIM_TO_EVIDENCE_LEDGER.md) | Audit | Explicit traceability mapping from claims to primary data files. |

---

## 6. Tomorrow's Presentation Deliverables

| Deliverable | Path | Purpose |
|---|---|---|
| **Master Research Progress Report** | [`docs/presentation/RESEARCH_PROGRESS_MASTER.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/RESEARCH_PROGRESS_MASTER.md) | Comprehensive 16-section master progress document covering mathematics, architecture, evidence, benchmarks, and limitations. |
| **Presentation Outline & Notes** | [`docs/presentation/PROGRESS_PRESENTATION_OUTLINE.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/PROGRESS_PRESENTATION_OUTLINE.md) | 14-slide presentation roadmap with exact key points, diagrams, and verbatim oral speaker scripts (~12–15 min). |
| **Defense Question Bank** | [`docs/presentation/DEFENSE_QUESTION_BANK.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/DEFENSE_QUESTION_BANK.md) | 22 comprehensive defense questions across 8 categories with 20–40s spoken answers and technical deep dives. |
| **Live Code Demo Guide** | [`docs/presentation/LIVE_CODE_DEMO_GUIDE.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/LIVE_CODE_DEMO_GUIDE.md) | Step-by-step 3–5 minute live code demonstration script with exact line numbers, commands, and expected outputs. |
| **Repository Cleanup Audit** | [`docs/presentation/REPOSITORY_CLEANUP_AUDIT.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/REPOSITORY_CLEANUP_AUDIT.md) | Preservation classification table and safe post-presentation archiving recommendations. |
| **Repository Navigation Guide** | [`docs/presentation/REPOSITORY_NAVIGATION_GUIDE.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/REPOSITORY_NAVIGATION_GUIDE.md) | This document: fast reference index with clickable links to all repository assets. |

