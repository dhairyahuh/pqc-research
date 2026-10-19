# Phase 9 Changelog

Branch `space-resilience-framework`, HEAD `4a2c4eb` (unchanged). No git stage/commit/push/reset/clean.
All edited files are untracked research artifacts; the 7 pre-existing tracked modifications are
untouched.

## Files modified (old → new SHA-256)
| file | old | new | reason |
|---|---|---|---|
| research/phase2_4_report/REPORT.md | 3593abf5… | 113b55b8… | §Phase 3 "six fault classes" → "seven fault classes + a clean (non-fault) baseline — eight distinct `channel_class`"; data/spec grounded (9D) |
| research/IMPLEMENTATION_LOG.md | 0f6c6ad2… | 67705f45… | "6 channel-fault classes" → "7 … + a clean baseline (8 distinct values)" (9D) |
| research/manuscript_v1/MANUSCRIPT.md | 7a2b0fdc… | 0e37903d… | 9F edits (below). Backup `MANUSCRIPT.pre_phase9.bak.md` = 7a2b0fdc… (byte copy of pre-edit) |

## Manuscript edits (9F) — no result number changed (verified by numeric-token diff)
1. §3 intro: "two methodology items are marked *partial*" → "all cited items now carry Crossref/host-verified metadata". *(presentation; evidence: REFERENCE_VERIFICATION.csv)*
2. §3 combined-faults: "Sangchoolie et al., *partial*" → "Sangchoolie et al. 2022". *(citation resolved)*
3. §3 OUTSTANDING blockquote: dropped the "confirm the two partial citations" item (now resolved); kept the systematic-search item. *(narrows an open item)*
4. §6 discrepancy note: "flagged (not resolved)" → "corrected in Phase 9" (source reports now say seven; raw records untouched). *(resolves documentation inconsistency)*
5. §8 transient identity: added "This identity is **conditional on the fault model, transient-duration semantics, protocol implementation, and retry budget**, and is not a general theorem." *(adds limitation; Phase 8 finding)*
6. §10 limitations: the two citations noted as **resolved via Crossref (metadata; full text not read)**, systematic search still outstanding. *(updates status honestly)*
7. §13 references: Avizienis (DOI 10.1109/TDSC.2004.2), Mukherjee (MICRO-36 DOI 10.1109/MICRO.2003.1253181), Leveugle (DATE'09 DOI 10.1109/DATE.2009.5090716, pp.502–506), Sangchoolie (IEEE TDSC 2022 19(3):1988–2006, DOI 10.1109/TDSC.2020.3043023) — [partial] promoted to verified metadata. *(adds verified evidence)*

## Files created
`research/phase9_literature_validation/`: WORKLOG.md, SEARCH_PROTOCOL.md, SEARCH_LOG.csv,
SCREENED_STUDIES.csv, REFERENCE_VERIFICATION.csv, NOVELTY_MATRIX.md, CHANGELOG.md, PHASE9_REPORT.md.
`research/manuscript_v1/MANUSCRIPT.pre_phase9.bak.md` (pre-edit backup; Phase 7 backup untouched).

## Protected files confirmed UNCHANGED (same hash start→end)
PHASE8_AUDIT.md 58d2e542…; MANUSCRIPT.pre_phase7.bak.md 6b53e252…; phase2/3/4 raw.jsonl
55ab1f57…/2cf7c29b…/d20c0ef5…; manifests feeaff67…/1c9d0f02…/41185f3d….
