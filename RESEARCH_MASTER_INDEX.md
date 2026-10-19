# RESEARCH MASTER INDEX

**Project:** Software-Level Fault Resilience for ML-KEM-768  
**Date:** 2026-10-17  
**Repository:** `/Users/dhairyajain/Desktop/pqc research`  
**Branch:** `space-resilience-framework` (HEAD: `4a2c4eb`)  
**Baseline Checkpoint:** `pqc-ntt-fault-resilience-v1` (tag on `8b2382d`)

---

## 1. Project Objective and Current Scope

**Core Research Question:** Can pure-software algebraic invariant monitoring with localized single-butterfly register rollback provide complete transient fault recovery and safe fail-stop containment in ML-KEM-768 decapsulation, while significantly reducing overhead compared to software DMR?

**Scope Boundaries:**
- Target: ML-KEM-768 (FIPS 203) NTT butterflies during decapsulation and FO re-encryption.
- Fault model: Non-adversarial transient SEU and persistent register/ALU faults. Not claiming SIFA/DFA resistance.
- Platform: Software C implementation on commodity processors (tested on Apple Silicon arm64).
- Not claiming: Physical radiation qualification, hardware fault injection, or cross-platform portability validation.

---

## 2. Paper-Track Index

### Paper Track 1 — Internal Fault Detection & Localized Recovery (PRIMARY)
- **Status:** KEEP — strongest candidate, most evidence
- **Provisional Title:** "Software-Level Dual-Transform NTT Invariant Monitoring with Localized Register Rollback for ML-KEM-768"
- **Research Map:** [RESEARCH_MAP.md](file:///Users/dhairyajain/Desktop/pqc%20research/papers/paper-01-internal-fault-detection/RESEARCH_MAP.md)

### Paper Track 2 — Cross-Layer Fault Interactions (DEFERRED)
- **Status:** DEFER — spacecraft protocol sim exists but lacks sufficient independent evidence
- **Research Map:** [RESEARCH_MAP.md](file:///Users/dhairyajain/Desktop/pqc%20research/papers/paper-02-cross-layer-fault-interactions/RESEARCH_MAP.md)

### Paper Track 3 — Persistent State Faults (DEFERRED)
- **Status:** DEFER — twiddle-factor blindness documented but multi-fault campaign incomplete
- **Research Map:** [RESEARCH_MAP.md](file:///Users/dhairyajain/Desktop/pqc%20research/papers/paper-03-persistent-state-faults/RESEARCH_MAP.md)

---

## 3. Source-Code and Experiment-Harness Map

### Core Implementation
| Component | Path | Status |
|:---|:---|:---|
| ML-KEM-768 reference (modified) | [algorithms/source_ref/mlkem/](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/) | Modified in working tree |
| Fault hooks (ML-KEM) | [mlkem_fault_hooks.c](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) | Modified in working tree |
| TFIB core library | [tfib_implementation/](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/) | 9 files, `libtfib.a` built |
| Independent oracle | [phase11_oracle/](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/phase11_oracle/) | liboqs-based, VERIFIED |
| Python fault injection | [fault_injection/](file:///Users/dhairyajain/Desktop/pqc%20research/fault_injection/) | Python fault models |
| Makefile | [Makefile](file:///Users/dhairyajain/Desktop/pqc%20research/Makefile) | Modified in working tree |

### Experiment Harnesses
| Harness | Path |
|:---|:---|
| TFIB experiment runner | [tfib_experiment_runner.c](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/tfib_experiment_runner.c) |
| TFIB benchmark | [tfib_benchmark.c](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/tfib_benchmark.c) |
| Step 2C independence test | [test_step2c_countermeasure_independence.c](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/test_step2c_countermeasure_independence.c) |
| Internal fault experiment | [mlkem768_internal_fault_experiment.c](file:///Users/dhairyajain/Desktop/pqc%20research/experiments/fault_injection/mlkem768_internal_fault_experiment.c) |
| Spacecraft protocol sim | [spacecraft_protocol_sim.py](file:///Users/dhairyajain/Desktop/pqc%20research/experiments/system_model/spacecraft_protocol_sim.py) |
| Gate A validator | [validate_vectors.c](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase18_gate_a/validate_vectors.c) |
| Gate B validator | [validate_ledger.py](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase18_gate_b/validate_ledger.py) |

---

## 4. Dataset and Evidence Map

### Primary Raw Data (CANONICAL — do not move or delete)
| Dataset | Path | Status |
|:---|:---|:---|
| Step 2C-A trials (900 rows) | [phase2_step2c_trial_results.csv](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/phase2_step2c_trial_results.csv) | REPRODUCED (L5) |
| TFIB benchmark raw | [tfib_benchmark_raw.csv](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_benchmark_raw.csv) | REPORTED |
| Level 1 fault results | [level1_fault_experiment_results.json](file:///Users/dhairyajain/Desktop/pqc%20research/results/level1_fault_experiment_results.json) | REPORTED |
| Baseline benchmarks | [baseline_benchmark_results.json](file:///Users/dhairyajain/Desktop/pqc%20research/results/baseline_benchmark_results.json) | REPORTED |
| Gate A vectors & records | [phase18_gate_a/](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase18_gate_a/) | REPORTED |

---

## 5. Test-Vector Inventory
| Vectors | Path | Source |
|:---|:---|:---|
| FIPS KAT ML-KEM-512/768/1024 | [tests/kat_mlkem*.c](file:///Users/dhairyajain/Desktop/pqc%20research/tests/) | NIST FIPS 203 |
| FIPS KAT ML-DSA-44/65/87 | [tests/kat_mldsa*.c](file:///Users/dhairyajain/Desktop/pqc%20research/tests/) | NIST FIPS 204 |
| Campaign PRF seeds | [campaign_prf.h](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/campaign_prf.h) | SHAKE-256 based |
| Reference test vectors | [references/test_vectors/](file:///Users/dhairyajain/Desktop/pqc%20research/references/test_vectors/) | NIST reference |

---

## 6. Manuscript Inventory
| Document | Path |
|:---|:---|
| Primary manuscript | [manuscript.md](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) |
| BibTeX references (18 entries) | [references.bib](file:///Users/dhairyajain/Desktop/pqc%20research/paper/references.bib) |
| Contribution analysis | [contribution_analysis.md](file:///Users/dhairyajain/Desktop/pqc%20research/contribution_analysis.md) |
| Final contribution decision | [final_contribution_decision.md](file:///Users/dhairyajain/Desktop/pqc%20research/final_contribution_decision.md) |
| Systematic gap report | [SYSTEMATIC_RESEARCH_GAP_REPORT.md](file:///Users/dhairyajain/Desktop/pqc%20research/research_redesign/SYSTEMATIC_RESEARCH_GAP_REPORT.md) |

---

## 7. Audit/Report Inventory

**Total phase-related markdown files: 422** `[DIRECTLY OBSERVED]`

- 19 root-level `phase*` directories with CSV data + reports
- 17 `docs/phase*` subdirectories (phases 0–7l)  
- `research/` subdirs: phase2_4_report through phase18_gate_b
- `tfib_experiments/` phase 11 and phase 2 step reports

---

## 8. Known Contradictions and Unresolved Questions

1. **Platform contradiction:** Manuscript says "Apple M3 Pro"; CHECKPOINT_README and evidence ledger say "M1/T8103". `[DIRECTLY OBSERVED]`
2. **Circular verifier rate:** Manuscript says 98.5% (591/600); contribution_analysis says "94.0% to 100.0%". `[DIRECTLY OBSERVED]`  
3. **Butterfly count coverage:** 9,856 butterflies claimed monitored; per-butterfly coverage not independently verified against `poly.c` instrumentation. `[REPORTED]`
4. **Gate B validator unexecuted.** `[REPORTED]`
5. **Working tree diverges from last commit** (10 modified tracked files). `[DIRECTLY OBSERVED]`

---

## 9. Evidence Status Summary

| Claim | Status |
|:---|:---|
| FIPS KATs pass | REPRODUCED (partial) |
| Oracle correct | REPRODUCED |
| SHAKE-256 correct | VERIFIED |
| Step 2C-A deterministic | REPRODUCED |
| Step 2C-A counts (900 trials) | REPRODUCED |
| Injection is symbolic | VERIFIED |
| 100% transient recovery | REPORTED |
| 100% persistent fail-stop | REPORTED |
| Zero SDC | REPORTED |
| +16.9% overhead | REPORTED (platform unclear) |
| Twiddle blindness 0.0% | REPORTED |

---

## 10. Blockers
1. Literature review requires full-text PDFs
2. Platform contradiction must be resolved
3. Working tree not committed
4. Gate B validator unexecuted

---

## 11. Git Working-Tree Changes (PRESERVE)

**Modified:** Makefile, README.md, poly.c, zetas.inc, mlkem768_internal_fault_experiment.c, spacecraft_protocol_sim.py, fault_definitions.py, phase7i_e2e_results.json, spacecraft_protocol_desync_results.json, test_fips_kats.c

**Untracked:** 100+ files/directories. No git operations performed.

---

## 12. Cross-References
- [Migration Manifest](file:///Users/dhairyajain/Desktop/pqc%20research/archive/MIGRATION_MANIFEST.md)
- [IEEE Candidate Shortlist](file:///Users/dhairyajain/Desktop/pqc%20research/literature/ieee_candidates/IEEE_CANDIDATE_SHORTLIST.md)
- [Extraction Template](file:///Users/dhairyajain/Desktop/pqc%20research/literature/extraction/EXTRACTION_TEMPLATE.md)
- [Evidence Ledger](file:///Users/dhairyajain/Desktop/pqc%20research/research/EVIDENCE_LEDGER.md)
- [Paper Track 1 Map](file:///Users/dhairyajain/Desktop/pqc%20research/papers/paper-01-internal-fault-detection/RESEARCH_MAP.md)

---

## 13. Next Three Highest-Priority Actions

1. **Resolve platform contradiction (M1 vs M3 Pro)** — determine which hardware produced canonical benchmarks
2. **Obtain and review P1-priority IEEE full texts** — critical path to novelty assessment
3. **Rebuild FIPS KATs from clean source** — upgrade evidence ledger L2 to full REPRODUCED
