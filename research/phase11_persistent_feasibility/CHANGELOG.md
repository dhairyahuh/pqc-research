# Phase 11 — Changelog

READ/BUILD scope: inspected SUT source + binary; ran isolated spikes and one isolated prototype.
**No** modification to mlkem_native, campaign code, statistical-analysis code, raw datasets,
manifests, preregistration, the manuscript, or any prior-phase artifact. **No** git
stage/commit/push/reset/clean/stash. Branch `space-resilience-framework`, HEAD `4a2c4eb`, 7
pre-existing tracked modifications — all unchanged.

## Files created (all new, isolated under research/phase11_persistent_feasibility/)
- `FEASIBILITY_REPORT.md` — root cause, evidence, 8-question assessment, CONDITIONAL GO decision.
- `DESIGN.md` — implemented prototype + the (approval-gated) real-arm plan and files it would touch.
- `reader.c`, `proto.c`, `run_feasibility.sh` — the isolated feasibility prototype (model table in
  `__DATA_CONST`; no SUT change).
- `RESULTS.csv` — 128 deterministic trials (prototype output).
- `REPRODUCE.md` — exact commands + expected output.
- `CHANGELOG.md` — this file.

## Protected files confirmed UNCHANGED (hash start == end)
MANUSCRIPT.md `0e37903d…`; PHASE8_AUDIT.md `58d2e542…`; PHASE9_REPORT.md `0161b2a4…`; phase2/3/4
raw.jsonl `55ab1f57…`/`2cf7c29b…`/`d20c0ef5…`. `mlkem_native` source and `zetas.inc` not modified.
