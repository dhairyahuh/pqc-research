# Bibliography — Phase 6 Literature Review (verified references)

Verification tags: **[V-fetched]** = I fetched the publisher/ePrint/CSRC page and confirmed
title+authors+year+venue; **[V-search]** = title/venue confirmed from a search-engine listing of
the authoritative host (ePrint/TCHES) but the full page was not individually fetched this session
(authors/pages not re-verified — treat metadata as provisional); **[tooling]** = software/standard
documentation, not a peer-reviewed paper; **[preprint/abstract]** = preprint, assessed from
abstract/metadata only. Dates of access: 2026-10-11. I did **not** read full PDFs except where
noted; relevance statements are my interpretation and are marked as such in the review.

## Standards & reference implementations (used by the study)
- **[V-fetched]** NIST, *FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard*,
  Aug 2024. https://csrc.nist.gov/pubs/fips/203/final (effective 2024-08-14; ML-KEM derived from
  CRYSTALS-KYBER). — the standard the SUT targets.
- **[tooling]** Open Quantum Safe, *liboqs* v0.16.0 (independent oracle backend; version read from
  the installed library). Project: https://openquantumsafe.org — full citation metadata TBD.
- **[tooling]** Linux `tc-netem` network-emulation qdisc (delay/loss/duplication/reordering/
  corruption). Man page: https://man.archlinux.org/man/tc-netem.8.en — as prior-art for *channel*
  impairment modelling (not used by our harness, which is in-process).

## Fault attacks on ML-KEM/Kyber (areas 1–3)
- **[V-fetched]** P. Pessl, L. Prokop, "Fault Attacks on CCA-secure Lattice KEMs," *IACR TCHES*
  2021(2):37–60. DOI 10.46586/tches.v2021.i2.37-60; ePrint 2021/064. — single instruction-skip in
  the decoding step of decapsulation; discusses FO re-encryption as the classic inverse-operation
  countermeasure.
- **[V-fetched]** J. Hermelink, P. Pessl, T. Pöppelmann, "Fault-enabled chosen-ciphertext attacks
  on Kyber," *INDOCRYPT 2021*; ePrint 2021/1222. — bit-flip + corrective fault turns FO into a
  failure oracle to recover the key.
- **[V-fetched]** K. Xagawa, A. Ito, R. Ueno, J. Takahashi, N. Homma, "Fault-Injection Attacks
  against NIST's PQC Round 3 KEM Candidates," *ASIACRYPT 2021*; ePrint 2021/840. — instruction-skip
  of the FO equality test across Kyber/NTRU/Saber/BIKE/SIKE.
- **[V-fetched]** L. Glabush, F. Günther, K. Hövelmanns, D. Stebila, "Verifiable Decapsulation:
  Recognizing Faulty Implementations of Post-Quantum KEMs," *CRYPTO 2025*; ePrint 2025/450. — ties
  the FO re-encryption check to functionality so a skipped check fails correctness tests; notes the
  real HQC reference-impl omission unnoticed for 19 months.
- **[V-search]** P. Ravi et al., "Side-channel and Fault-injection attacks over Lattice-based
  Post-quantum Schemes (Kyber, Dilithium): Survey and New Results," ePrint 2022/737. — survey +
  countermeasures (authors list not individually re-verified).
- **[V-search]** "Roulette: A Diverse Family of Feasible Fault Attacks on Masked Kyber," *IACR
  TCHES* (tches.iacr.org article 9835). — fault attacks on masked Kyber (authors/year not fetched).
- **[V-search]** "A Practical Fault Injection Attack Scheme Apply to All Phases of ML-KEM and
  ML-DSA," ePrint 2024/1522. — Keccak-targeted FIA across ML-KEM/ML-DSA (not fetched).

## Network/protocol disruption & cross-layer (areas 4–5)
- **[tooling]** Jepsen (K. Kingsbury), distributed-systems fault testing (partitions, crashes,
  clock skew) — methodology reference; not a single peer-reviewed paper. (Described at
  kindatechnical.com listing; canonical source is the Jepsen project site.)
- **[V-search]** S. Hemminger, "Network Emulation with NetEm," *Linux Conf Au* 2005 — canonical
  netem reference (year/venue from general knowledge; **NOT re-verified this session — flag**).
- **[preprint/abstract]** "Post-Quantum Cryptographic Analysis of Message Transformations Across
  the Network Stack," arXiv:2604.08480 (2026). — cross-layer PQC across the stack; about algorithm
  vulnerability per layer, not fault *interaction* (abstract only).

## OUTSTANDING / could not verify this session
- Full author/year verification for all **[V-search]** items.
- Hemminger NetEm paper metadata (**flag**).
- A systematic DBLP/Scholar sweep of each venue; see `SEARCH_LOG.md` limitations.
