# Reproducibility — Manuscript v1

Exact commands, expected outputs, and artifact hashes grounded in the recorded manifests.
Environment: Apple Silicon arm64, Darwin 27, Apple clang 21, Python 3.9.6 (numpy/scipy/matplotlib),
liboqs 0.16.0 at `/opt/homebrew/lib`. Set `export DYLD_LIBRARY_PATH=/opt/homebrew/opt/liboqs/lib`
for the C drivers and `export MPLCONFIGDIR="$TMPDIR/mpl"` for figures. No network; no new tools.

## Datasets and SHA-256 (verified against manifests)
| dataset | path | sha256 |
|---|---|---|
| Phase 2 | `research/results/phase2_mem_logical_v1/raw.jsonl` | `55ab1f572a3e2db37c59e602d6fc8862f165d95e95f5f38f78e8b4f5821b6a60` |
| Phase 3 | `research/results/phase3_channel_v1/raw.jsonl` | `2cf7c29bab0bca24986142932421925c74d9c2502fc3f0b729afdc97636c0102` |
| Phase 4 | `research/results/phase4_combined_v1/raw.jsonl` | `d20c0ef5adddb5df5dd9c0246239465bfe047ed0b10c2079605bdfaeb3f9d09f` |

## Commands and expected outputs
```bash
# Independent audit — recomputes every metric from raw; expect "AUDIT PASSED (0 discrepancies)"
python3 research/phase2_4_report/audit/independent_audit.py          # exit 0

# Regenerate figures + tables from verified raw data
export MPLCONFIGDIR="$TMPDIR/mpl"
python3 research/phase2_4_report/make_figures.py                     # 5 figures, 10 tables, exit 0

# Reproduce datasets from scratch (deterministic; byte-identical to the hashes above)
export DYLD_LIBRARY_PATH=/opt/homebrew/opt/liboqs/lib
research/fault_contract/run_phase2.sh            # PHASE 2 DRIVER: PASS; raw.jsonl 55ab1f57…
research/channel_harness/run_phase3.sh           # PHASE 3 DRIVER: PASS; raw.jsonl 2cf7c29b…
research/combined_harness/run_phase4_confirmatory.sh  # PHASE 4 CONFIRMATORY: PASS; raw.jsonl d20c0ef5…

# Fault-contract unit/negative + ASAN/UBSAN + fuzz checks
research/fault_contract/run_phase1_tests.sh      # PHASE 1 SUITE: PASS
python3 research/channel_harness/test_channel_contract.py  # == PASSED (0 failures) ==
```

## Key numbers reproduced by the audit (exit 0)
- Phase 2: 900 trials, 750 activated, 600 detected, 0 SDC; outcomes 150/250/350/147/3.
- Phase 3: 600 sessions; EST100/REC200/MALF100/LOST100/TIMEOUT50/ABORT50; crypto VALID350/REJECT50/UNAVAIL200.
- Phase 4: p = 100.0/48.0/56.4/26.0%; Δ̂ +0.216 CI [+0.180,+0.252]; masking 203/500; Δ_persistent
  +0.419 [+0.360,+0.477]; Δ_transient 0 (max|d_i|=0); Δ_P−T +0.419 [+0.360,+0.477]; joint grid
  [+0.052,+0.471].

## Scope of reproducibility
Deterministic given the recorded seeds and this environment. Re-runs are byte-identical (same
SHA-256). Cross-platform/compiler reproducibility is **untested**. Bootstrap CIs use fixed RNG seeds
(`combined_stats.py` 20261010; audit 424242) and agree to within Monte-Carlo error (~0.005).
