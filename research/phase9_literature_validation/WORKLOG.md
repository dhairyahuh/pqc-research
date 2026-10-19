# Phase 9 Work Log — protected files & intended edits (written BEFORE edits)

## Protected files (must NOT change) — start SHA-256
| file | sha256 |
|---|---|
| research/manuscript_v1/MANUSCRIPT.md (will edit — see below; backup first) | 7a2b0fdc… |
| research/manuscript_v1/PHASE8_AUDIT.md | 58d2e542… |
| research/manuscript_v1/MANUSCRIPT.pre_phase7.bak.md (Phase 7 backup — never overwrite) | 6b53e252… |
| research/results/phase2_mem_logical_v1/raw.jsonl | 55ab1f57… |
| research/results/phase3_channel_v1/raw.jsonl | 2cf7c29b… |
| research/results/phase4_combined_v1/raw.jsonl | d20c0ef5… |
| phase2/phase3/phase4 manifests | feeaff67… / 1c9d0f02… / 41185f3d… |

Raw datasets, manifests, campaign/analysis code, preregistration, and all v1/v2 literature artifacts
are **not** to be modified. No git stage/commit/push/reset/clean/stash. Branch
`space-resilience-framework`, HEAD `4a2c4eb` must be unchanged at end.

## Intended edits this phase (scoped, evidence-supported)
1. **`research/phase2_4_report/REPORT.md`** (start 3593abf5…): line ~56 "six fault classes" →
   "seven fault classes + a clean control" (data shows 7 + CLEAN). Evidence: raw `channel_class` = 8
   distinct incl CLEAN.
2. **`research/IMPLEMENTATION_LOG.md`** (start 0f6c6ad2…): line ~94 "6 channel-fault classes" →
   "7 channel-fault classes (+ clean)".
3. **`research/manuscript_v1/MANUSCRIPT.md`** (backup first → `MANUSCRIPT.pre_phase9.bak.md`):
   (a) promote the two [partial] methodology citations to verified with Crossref DOIs; (b) add a
   clause that the transient-stratum structural identity is model-/retry-budget-conditional; (c) no
   numeric changes.

New files only under `research/phase9_literature_validation/` plus the manuscript Phase-9 backup.
If any edit risks disturbing pre-existing tracked work, STOP and report (none of the above are
tracked files; all are untracked research artifacts).
