# Revision Log — Phase 7 (conservative manuscript revision)

Edited file: `research/manuscript_v1/MANUSCRIPT.md` (only this file was edited).
Backup: `research/manuscript_v1/MANUSCRIPT.pre_phase7.bak.md` (pre-edit copy).
Original SHA-256: `6b53e252e3110a337aff472d31a877d913d779893acb490a944dce46f0986971`.
Sources: `../literature_review_v2/{RELATED_WORK_DRAFT,LITERATURE_REVIEW,NOVELTY_AUDIT,BIBLIOGRAPHY}.md`,
`phase2_4_report/REPORT.md`, `CLAIMS_AND_EVIDENCE.md`, `OPEN_ISSUES.md`. No numbers were changed.

| # | Section | Before (excerpt) | After (excerpt) | Reason | Source | Type |
|---|---|---|---|---|---|---|
| 1 | §1 Abstract | "driven by a **masking mechanism**: a delivery-blocking channel fault…" | "an instance of **fault masking** — an established dependability concept (Avizienis et al. 2004; cf. derating/AVF, Mukherjee et al. 2003), not a mechanism we invent…"; added "literature search was targeted rather than systematic" | Attribute masking as established; stop implying a new mechanism | NOVELTY_AUDIT v2 (E); BIBLIOGRAPHY v2 | **narrows claim** |
| 2 | §2 Contributions (new) | (none — no explicit contributions list) | Added 5 conservatively-worded contributions; "We claim no first-of-its-kind result"; each narrowed with attribution/caveats | Align contributions with the conservative novelty audit | NOVELTY_AUDIT v2 (A–E) | **narrows claim** |
| 3 | §3 Related work | Stub: "verifiable sources only; comparative literature OUTSTANDING" + 4 standard/impl bullets | Full Related Work: fault attacks (Pessl&Prokop, Xagawa, Hermelink, Delvaux, Wang, Ravi), FO defense (Glabush), dependability masking (Avizienis, Mukherjee), network (Hemminger, Jepsen), combined/cross-layer (2024/757, arXiv:2604.08480); explicit targeted-not-systematic disclosure | Integrate reviewed literature; attribute prior work; separate established findings from relevance interpretation | RELATED_WORK_DRAFT v2; BIBLIOGRAPHY v2; SEARCH_LOG v2 | **adds evidence** |
| 4 | §10 Limitations | (vi) ended at timing figures | Added (vii) targeted non-systematic literature search; two unresolved methodology citations; OPEN_ISSUES outstanding | Disclose search limitation per instruction | SEARCH_LOG v2; OPEN_ISSUES | **narrows claim** |
| 5 | §12 Conclusion | "the mechanism is channel masking of the memory fault" | "an **instance of established fault masking** (Avizienis 2004; Mukherjee 2003)… masking is not recovery"; "we make no first-of-its-kind claim"; "systematic literature review … remain to be done" | Attribute masking; remove any novelty overreach | NOVELTY_AUDIT v2 | **narrows claim** |
| 6 | §13 References (new) | (none) | Added a verified reference list with status tags [Vf]/[Vl]/[tool]/[pre]/[partial] | Ensure every in-text citation maps to a bibliography entry; keep partial items flagged | BIBLIOGRAPHY v2 | **adds evidence / presentation** |

## Qualifications preserved (unchanged in meaning)
- All Phase 2/3/4 numbers, the F-conditional framing, paired-bootstrap method, 0-SDC-≠-0-risk,
  masking≠recovery, the six-vs-seven discrepancy flag (§6), and all limitations were preserved; no
  outcome definition, denominator, statistical method, or interpretation was altered.

## Inconsistencies encountered (flagged, not silently resolved)
- The "six vs seven channel classes" discrepancy in `REPORT.md:56`/`IMPLEMENTATION_LOG.md:94` remains
  flagged in §6 (and OPEN_ISSUES); the manuscript continues to use the data-grounded count of seven.
- Two methodology citations (Leveugle; Sangchoolie et al.) are **partial**; cited only with that flag
  and listed as outstanding, per the review artifacts (not promoted to verified).
