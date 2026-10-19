# Phase 9A — Search Protocol (STRUCTURED / TARGETED, not systematic)

This is explicitly a **structured, targeted review**, NOT a systematic review (PRISMA-grade). It
does not satisfy systematic-review standards (single reviewer, no exhaustive database enumeration,
no registered protocol). Honest coverage statement below.

## Sources actually used
- **Accessed:** a general web search engine; **Crossref REST API** (`api.crossref.org`, public) for
  bibliographic metadata/DOIs; direct fetches of **IACR ePrint**, **NIST CSRC**, and author-hosted
  PDFs (e.g. landwehr.org). IACR TCHES/cryptodb records via the host.
- **NOT accessed as databases:** IEEE Xplore, ACM Digital Library, SpringerLink, USENIX, Google
  Scholar, DBLP. Where IEEE/ACM items appear, their metadata came from **Crossref** or a search
  listing, not from the publisher's own search interface. This is a real limitation on recall.

## Inclusion criteria (defined before final screening)
Include a study if it concerns at least one of: (i) fault injection/attacks on ML-KEM/Kyber/lattice
KEMs or the FO transform/implicit rejection; (ii) software/logical fault models, containment, or
masking/derating; (iii) communication/protocol fault emulation (loss/delay/dup/reorder/interruption/
retry); (iv) cross-layer crypto×network fault interaction; (v) fault-injection experimental
methodology (statistical FI, factorial/interaction designs). Include **competing/negative** evidence
(prior art that would reduce novelty), not only supportive work.

## Exclusion criteria
Exclude: side-channel-only work not bearing on fault/FO; pure performance benchmarking; vendor/blog
pages as primary sources (used only as pointers); items whose authoritative metadata could not be
confirmed (marked UNVERIFIED/DROPPED rather than cited).

## Screening & dedup
Single-reviewer title/abstract screening against the criteria; dedup by DOI/ePrint number/title.
Full text was generally **not** read end-to-end; relevance judged from abstract/record (recorded per
item in `REFERENCE_VERIFICATION.csv`).

## Queries
Recorded in `SEARCH_LOG.csv` (Phase 6, 6B, and 9). Phase 9 added Crossref metadata lookups to resolve
the two `[partial]` citations and confirm DOIs.

## Limitations (honest)
- Non-systematic, single-reviewer; paywalled databases not enumerated ⇒ **recall is incomplete**.
- Absence of an exact cross-layer crypto×channel fault-interaction match in this corpus is **not**
  proof of priority (novelty for contribution D remains "unresolved pending additional search").
- Crossref confirms metadata/DOIs, not that a paper supports a specific technical claim; claim-level
  relevance is my interpretation, flagged as such.
