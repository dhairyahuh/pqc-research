# Phase 9 Report — Literature Validation, Novelty & Source-Consistency

## Executive verdict: **PASS WITH MAJOR CAVEATS**
Basis: the two previously `[partial]` citations were resolved to verified bibliographic metadata via
Crossref; key DOIs were confirmed; the six-vs-seven source-report inconsistency was corrected to agree
with the data (raw records untouched); the transient-identity model-dependence was made explicit; and
no result number changed (numeric-token diff: only citation metadata/pointers changed). The project
is **not** declared submission-ready: a **systematic** database search was not performed (IEEE
Xplore/ACM DL/SpringerLink/USENIX/Scholar/DBLP were not queried as databases), the cross-layer
novelty for contribution D remains **OPEN pending that search**, and the structural gaps from Phase 8
(no persistent-storage arm, no physical experiments, no second independent KEM, no cross-platform
replication, internal-only audit) persist. This is a structured/targeted review, **not** external
replication or peer review.

## Results
- **Databases/sources actually searched:** a general web search engine; **Crossref REST API**
  (metadata/DOIs); direct fetches of IACR ePrint, NIST CSRC, author-hosted PDFs. **Not searched as
  databases:** IEEE Xplore, ACM DL, SpringerLink, USENIX, Google Scholar, DBLP (disclosed in
  `SEARCH_PROTOCOL.md`).
- **Queries/screening:** `SEARCH_LOG.csv` (Phase 6/6B/9), `SCREENED_STUDIES.csv` (included + competing
  work, with exclusions and reasons).
- **Citation verifications completed:** all 10 checklist references plus FIPS 202/203 and tooling →
  `REFERENCE_VERIFICATION.csv`. The two `[partial]` items are now **VERIFIED_METADATA_ONLY**:
  Leveugle et al., DATE 2009, pp.502–506, DOI 10.1109/DATE.2009.5090716; Sangchoolie et al., IEEE TDSC
  19(3):1988–2006 (2022), DOI 10.1109/TDSC.2020.3043023. DOIs also confirmed for Avizienis (TDSC 2004,
  10.1109/TDSC.2004.2) and Mukherjee (MICRO-36 2003, 10.1109/MICRO.2003.1253181).
- **Partial/unverified remaining:** full texts were **not** read for any reference (metadata-only);
  ePrint 2024/757 authors not re-verified; arXiv:2604.08480 is UNVERIFIED (abstract only); liboqs and
  Jepsen are tooling (no current peer-reviewed citation). None of these are load-bearing.
- **Closest prior work:** Pessl & Prokop 2021 (decapsulation fault); Glabush et al. 2025 (FO-check
  defense); Avizienis 2004 + Mukherjee 2003 (masking/derating); Hemminger 2005 / Jepsen (channel
  faults); Sangchoolie 2022 / ePrint 2024/757 (combined/multiple faults).
- **Novelty (A–E)** — see `NOVELTY_MATRIX.md`: A = methodological synthesis; B, C = applications to
  ML-KEM of established fault/channel methods; D = cross-layer *pairing* **DIFF?/OPEN** (not found in
  reviewed corpus, but combined/interaction designs predate this and the search was non-systematic);
  E = cross-layer **instance of established masking/derating** (not a new mechanism). **No
  first-of-its-kind claim.**
- **Source-report corrections:** `REPORT.md` and `IMPLEMENTATION_LOG.md` six→seven (+ clean) fixed.
- **Manuscript edits:** 7 targeted edits (CHANGELOG §9F); no result changed.
- **Unresolved conflicts:** none newly introduced; the only prior inconsistency (six-vs-seven) is now
  resolved consistently across data, source reports, and manuscript.

<!-- P9R-APPEND -->
## Evidence traceability (material corrections)
| correction | source/evidence | where |
|---|---|---|
| 7 fault classes (not 6) + clean | raw `channel_class` = 8 distinct incl CLEAN (fresh recompute) | REPORT.md §Phase 3; IMPLEMENTATION_LOG.md Gate-2; MANUSCRIPT §6 |
| Leveugle DOI/pages | Crossref 10.1109/DATE.2009.5090716 | REFERENCE_VERIFICATION.csv; MANUSCRIPT §13 #18 |
| Sangchoolie DOI/venue/year | Crossref 10.1109/TDSC.2020.3043023, TDSC 19(3):1988–2006, 2022 | REFERENCE_VERIFICATION.csv; MANUSCRIPT §13 #19 |
| Avizienis / Mukherjee DOIs | Crossref 10.1109/TDSC.2004.2 ; 10.1109/MICRO.2003.1253181 | MANUSCRIPT §13 #12,#13 |
| transient identity is model-conditional | Phase 8 finding; combined_campaign retry model | MANUSCRIPT §8 |
| masking attributed to prior art | Avizienis 2004; Mukherjee 2003 (verified) | MANUSCRIPT §1,§3,§12; NOVELTY_MATRIX |

## Repository integrity
- **Start:** branch `space-resilience-framework`, HEAD `4a2c4eb`, 7 tracked modified.
- **End:** branch `space-resilience-framework`, HEAD `4a2c4eb`, 7 tracked modified — **identical.**
- **Protected files unchanged (hash start==end):** PHASE8_AUDIT.md `58d2e542…`; Phase-7 backup
  `6b53e252…`; phase2/3/4 raw.jsonl `55ab1f57…`/`2cf7c29b…`/`d20c0ef5…`; manifests
  `feeaff67…`/`1c9d0f02…`/`41185f3d…`.
- **Edited (untracked) files:** REPORT.md `3593abf5…`→`113b55b8…`; IMPLEMENTATION_LOG.md
  `0f6c6ad2…`→`67705f45…`; MANUSCRIPT.md `7a2b0fdc…`→`0e37903d…` (backup `MANUSCRIPT.pre_phase9.bak.md`
  = `7a2b0fdc…`).
- **No numerical result changed** (numeric-token diff: only DOIs/years/pages and the removed `:56`/
  `:94` pointers differ; result tokens 216/180/252/419/360/477/203/500/750/600/147/350/250 unchanged).
- **CSV sanity:** SEARCH_LOG (6 fields), SCREENED_STUDIES (5), REFERENCE_VERIFICATION (10) — 0
  short rows.
- `git diff --check`: one pre-existing whitespace note in **README.md** (one of the 7 pre-existing
  modifications; **not touched by Phase 9**). No staging/commit/push/reset/clean.

## Readiness
**Completed in Phase 9:** two partial citations resolved (metadata); key DOIs confirmed; six-vs-seven
corrected across data/report/manuscript; transient-identity model-dependence stated; novelty kept
conservative and masking attributed; manuscript citations consistent; repository preserved.
**Still necessary before submission:** a genuine **systematic** database search (IEEE/ACM/Springer/
USENIX/Scholar/DBLP) to settle contribution-D novelty; full-text reading of the cited works; a
physically motivated/alternative F in the main text; fix of README whitespace is out of scope.
**Requires an independent researcher / external replication:** external reproduction of the three
campaigns on different hardware/compiler; a second independent KEM implementation; and ultimately
any physical/radiation/RF validation (out of this paper's software-only scope).

**Operating principle honored:** narrower defensible claims over inflated novelty; documented
unresolved items over invented ones. This is **not** external validation or peer review, and passing
checks do **not** make the paper submission-ready.