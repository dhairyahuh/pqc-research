# Search Log v2 — Phase 6B

Date 2026-10-11. Continues `../literature_review_v1/SEARCH_LOG.md` (preserved). Same environment:
a general web search engine + direct fetches of authoritative host pages/PDFs.

## IMPORTANT coverage disclosure (what was and was NOT searched)
- I used a **general web search engine** plus **direct page fetches** of IACR ePrint, NIST CSRC,
  author-hosted PDFs (landwehr.org), and reached ACM DL / IEEE / ResearchGate records **via those
  search results**.
- I did **NOT** log into or query as databases: **IEEE Xplore, ACM Digital Library, DBLP, Google
  Scholar, USENIX, Springer**. Where those appear below, the metadata came from a search listing or
  an author-hosted copy, not from the database's own interface. Items so sourced are tagged
  `[V-host-listing]` and should be re-confirmed on the publisher page before camera-ready.
- No full PDFs were read end-to-end; relevance is judged from abstracts/records.

## v2 queries
1. `Avizienis Laprie Randell Landwehr basic concepts taxonomy dependable secure computing ... masking`
   → TDSC 2004 taxonomy (author PDF). [fetched via listing of landwehr.org]
2. `Mukherjee architectural vulnerability factor AVF derating logical masking soft errors MICRO 2003`
   → MICRO 2003 (ACM DL 10.5555/956417.956570) + IEEE Micro 2003 (10.1109/MM.2003.1261389).
3. `combined multiple fault injection interaction effect experiment dependability double fault campaign`
   → Statistical Fault Injection (Leveugle, DATE 2009); single-vs-multiple bit-flip study
   (Sangchoolie et al., TDSC); FI campaign EDA/surveys.
4. `Roulette diverse family feasible fault attacks masked Kyber TCHES authors year` → Delvaux,
   TCHES 2022, ePrint 2021/1622 (author via IACR cryptodb authorkey 9041).
5. `Hemminger "Network Emulation with NetEm" Linux Conf Au 2005 proceedings` → GÉANT record
   confirming S. Hemminger, LCA 2005, April 2005 (lca2005 abstract id 163).
6. Fetched for metadata: ePrint 2022/737 (Ravi et al.), ePrint 2024/1522 (Wang et al.).

## Citation chaining performed
- From Hermelink et al. (2021/1222) → Pessl & Prokop (2021/064) [cited as the first practical fault
  attack] and → Delvaux "Roulette" (which extends Hermelink's inequality attack).
- From Avizienis TDSC → masking/derating → Mukherjee AVF (MICRO 2003).

## Resolved from v1
Ravi 2022/737 (authors + preprint status); Roulette (Delvaux, TCHES 2022, 2021/1622); 2024/1522
(full title + authors); Hemminger NetEm (LCA 2005) — v1 flag cleared.

## Still inaccessible / partial (disclosed, not implied-searched)
- IEEE Xplore / ACM DL / DBLP / Scholar not queried as databases.
- Leveugle (DATE 2009) and Sangchoolie (TDSC) publisher pages not fetched (venue/year partial).
- No systematic enumeration ⇒ recall remains incomplete; **absence of a matching cross-layer
  crypto×channel fault-interaction paper is still NOT proof of novelty.**
