# Phase 9C — Skeptical Novelty Matrix

Classes: **PRIOR** established prior art · **APPLY** application/adaptation of established methods ·
**METHOD** methodological contribution · **DIFF?** potentially differentiated · **OPEN** unresolved
pending additional (systematic) search. Combining two familiar components is not, by itself, novelty.
Consistent with `../literature_review_v2/NOVELTY_AUDIT.md`; citations now DOI-resolved
(`REFERENCE_VERIFICATION.csv`).

## Comparison (closest prior work vs this study)
See `../literature_review_v2/COMPARISON_MATRIX.csv` for the full grid. Summary of the closest prior
work per dimension:
- Memory/decapsulation fault locus: **Pessl & Prokop 2021; Xagawa et al. 2021; Hermelink et al. 2021;
  Delvaux 2022; Wang et al. 2024** — all adversarial attacks; our arm is a non-adversarial resilience
  *measurement* with logical-value faults.
- FO-check integrity: **Glabush et al. 2025** (defense by construction) — complementary to our
  oracle-gated measurement.
- Masking/derating: **Avizienis et al. 2004; Mukherjee et al. 2003** — the concept our observation
  instantiates.
- Channel faults: **Hemminger 2005 (netem); Jepsen** — the impairment lineage.
- Combined/multiple faults & FI methodology: **Sangchoolie et al. 2022; Leveugle et al. 2009;
  ePrint 2024/757 (fault×probing)** — combined/interaction designs predate this work.

## Contribution assessment (A–E)
**A. Reproducible software-only fault-study workflow — METHOD (not a new concept).**
Closest prior art: statistical fault injection (Leveugle et al. 2009) + the dependability outcome
taxonomy (Avizienis et al. 2004). Exact difference: a specific oracle-gated contract that makes
"recovered" unreachable without an independent VALID verdict, plus a ledger and negative tests, as a
reusable artifact. Defensible as an engineering/methodological synthesis, not an invention.

**B. Logical-value memory-fault campaign — APPLY.**
Closest prior art: the ML-KEM/Kyber fault-attack corpus (Pessl & Prokop; Xagawa; Hermelink; Delvaux;
Wang), which already targets decapsulation/NTT/FO. Exact difference: intent and model — *resilience
measurement* under logical-value faults with independent-oracle verdicts and a 0-SDC sampling bound,
not an attack. Not the first fault study of ML-KEM.

**C. Communication/protocol fault campaign — APPLY.**
Closest prior art: netem (Hemminger 2005), Jepsen. Exact difference: ML-KEM-specific separation of
cryptographic verdict from protocol outcome, with a channel-redrawing (non-tautological) retry. The
channel model itself is standard.

**D. Matched cross-layer factorial interaction experiment — DIFF? / OPEN.**
Closest prior art: combined/interaction fault designs exist (Sangchoolie et al. multiple-fault study;
ePrint 2024/757 fault×probing); 2^k/interaction analysis is textbook. Exact difference: the *pairing*
of in-decapsulation crypto-computation faults with channel/protocol faults on a KEM, which we did not
find in the reviewed corpus. **Status OPEN:** IEEE Xplore/ACM DL/SpringerLink/Scholar were not
searched as databases; absence here is not priority. Claim only "to our knowledge within the reviewed
sources," with the limitation stated.

**E. Channel masking vs recovery vs key establishment — PRIOR (concept) + APPLY (instance).**
Closest prior art: fault masking / error containment (Avizienis et al. 2004) and derating/AVF
(Mukherjee et al. 2003) — the concept is established. Exact difference: a cross-layer *instance* (a
channel fault masking an in-decapsulation computation fault) plus the measurement caution that
masking must not be scored as recovery or as key establishment. **Not a new mechanism.**

## Bottom line
No contribution is "first-of-its-kind." The defensible framing is: a methodological workflow (A),
two applications to ML-KEM (B, C), a cross-layer interaction *design* whose crypto×channel pairing is
unresolved-pending-systematic-search (D), and a cross-layer *instance* of an established masking
principle with a useful measurement caution (E).
