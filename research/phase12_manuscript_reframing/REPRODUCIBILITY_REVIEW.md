# Phase 12 — Reproducibility Review

Environment: Apple Silicon arm64, Darwin 27, Apple clang 21, Python 3.9.6 (numpy/scipy/matplotlib),
liboqs 0.16.0 at /opt/homebrew. Deterministic; `export DYLD_LIBRARY_PATH=/opt/homebrew/opt/liboqs/lib`
for C drivers. **Internal reproduction only — not external replication.**

## Commands → artifacts (verified this phase or earlier this session)
| claim | command | expected | artifact |
|---|---|---|---|
| recompute all Phase 2–4 numbers | `python3 research/phase2_4_report/audit/independent_audit.py` | "AUDIT PASSED (0 discrepancies)" | raw.jsonl ×3 |
| Phase 2 dataset | `research/fault_contract/run_phase2.sh` | PASS; raw.jsonl `55ab1f57…` | `phase2_mem_logical_v1/` |
| Phase 3 dataset | `research/channel_harness/run_phase3.sh` | PASS; raw.jsonl `2cf7c29b…` | `phase3_channel_v1/` |
| Phase 4 confirmatory | `research/combined_harness/run_phase4_confirmatory.sh` | PASS; raw.jsonl `d20c0ef5…` | `phase4_combined_v1/` |
| figures/tables | `MPLCONFIGDIR=$TMPDIR/mpl python3 research/phase2_4_report/make_figures.py` | 5 figs, 10 tables | `phase2_4_report/figures,tables` |
| Phase 11 feasibility (model) | `research/phase11_persistent_feasibility/run_feasibility.sh` | 128/128; exit 0 | `RESULTS.csv` |
| contract tests + ASAN/UBSAN | `research/fault_contract/run_phase1_tests.sh` | PASS | — |

## Required source/build to reproduce the campaigns
- SUT object `bin/obj/mlkem768_inst.o` built from `algorithms/source_ref/mlkem/mlkem_native.c` with
  `-DMLKEM_RESEARCH_FAULT_HOOKS` (research build); clean/KAT builds omit the flag (`Makefile`).
- TFIB monitors `tfib_implementation/libtfib.a`; oracle `tfib_experiments/phase11_oracle/libindependent_oracle.a` (liboqs); PRF `campaign_prf.h`.
- Combined coordinator links `mlkem768_inst.o` + `libtfib.a` + `libindependent_oracle.a` + `-loqs`.

## Gaps / caveats
- The three campaign drivers were validated earlier this session; **this phase re-ran only the
  non-destructive `independent_audit.py`** (sufficient to recompute the manuscript numbers from raw).
- A full clean rebuild from source (vs the prebuilt `bin/obj/*.o`) is **not** re-verified this phase.
- Phase 11 reproduces the **mechanism on a model table only**; the real persistent-storage arm is not
  reproducible because it does not exist (would require the approved relocation).
- Bootstrap CIs use fixed RNG seeds (`combined_stats.py` 20261010; audit 424242); agree to ~0.005.
- No external/independent reproduction has been performed.
