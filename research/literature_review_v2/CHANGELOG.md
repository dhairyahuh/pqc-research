# Changelog — Phase 6 → Phase 6B (literature_review_v1 → v2)

Phase 6 artifacts in `../literature_review_v1/` are **preserved unchanged**. This v2 supersedes them
only where noted.

## Citations resolved (were [V-search] / flagged / tooling in v1)
- **Ravi et al. 2022/737** → authors confirmed (P. Ravi, A. Chattopadhyay, J. P. D'Anvers, A. Baksi)
  and status corrected to **preprint** (not formally published).
- **"Roulette"** → attributed: **J. Delvaux**, TCHES 2022, ePrint **2021/1622** (IACR cryptodb +
  artifact archive). v1 had it unattributed.
- **ePrint 2024/1522** → full title "**Mind the Faulty Keccak** …" and authors (Wang, Yu, Qu, Zhang,
  Li, Zhang, Gu, SJTU) resolved; mechanism = loop-abort faults in Keccak.
- **Hemminger NetEm** → confirmed **Linux Conf Au 2005 (April 2005)** via GÉANT record; v1 flag cleared.
- **liboqs** → kept as tooling; explicitly chose **not** to cite the 2016 "Open Quantum Safe" paper
  to avoid overclaiming API currency.

## New sources added (dependability foundation + methodology)
- **Avizienis, Laprie, Randell, Landwehr, IEEE TDSC 2004** — masking / error containment taxonomy.
- **Mukherjee et al., MICRO 2003 (+ IEEE Micro 2003)** — derating / AVF.
- **Leveugle et al., Statistical Fault Injection (DATE 2009)** and **Sangchoolie et al., single-vs-
  multiple bit-flip (TDSC)** — methodology; marked **partial** (publisher pages not fetched).

## Claims that CHANGED
- **Contribution E (MASKED_BY_CHANNEL): downgraded** from v1 "(2) potentially differentiated" to
  **"(3) narrow — an application of established fault-masking/derating."** Counterevidence: Avizienis
  (masking) + Mukherjee (derating) establish the concept. Novelty now limited to the specific
  cross-layer instantiation + the "masking ≠ recovery" caution, with the concept explicitly attributed.
- **Contribution D: narrowed** — combined/interaction fault designs are not new in general
  (multiple-fault dependability studies; combined fault+probing 2024/757); differentiation limited to
  the crypto×channel pairing, with coverage caveat.
- **Contributions A, B, C: narrowed** with explicit counterevidence (statistical-FI; the ML-KEM
  attack corpus; netem/Jepsen). Framing shifted to "measurement/integration/synthesis," not "first/new."
- Added a **counterevidence** line to every contribution (acceptance criterion 4).

## What remains OPEN
- No database-level search (IEEE Xplore/ACM/DBLP/Scholar) — recall incomplete; cross-layer novelty
  (D) remains cautiously stated, not proven.
- Leveugle and Sangchoolie venue/year unverified on publisher pages (may be dropped).
- liboqs lacks a current-API peer-reviewed citation.

## Decision
Citations proposed for the manuscript are now primary-source/authoritative-record verified (or
dropped/flagged). Novelty is conservatively framed with counterevidence and the masking concept
properly attributed. **Recommendation: READY for a conservative manuscript edit** (insert
`RELATED_WORK_DRAFT.md` and narrow the contribution statements), with the OUTSTANDING systematic
search disclosed as a limitation — pending explicit authorization. `MANUSCRIPT.md` is unmodified.
