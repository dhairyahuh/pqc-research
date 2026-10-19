# Bibliography v2 — Phase 6B (verification completed)

Tags: **[V-fetched]** host page fetched this session, full metadata confirmed; **[V-host-listing]**
confirmed from the authoritative host's own listing/record (IACR cryptodb, TCHES/ACM/IEEE record,
project page) though the full page/PDF was not re-fetched; **[tooling]** software/standard.
Access date 2026-10-11. Coverage limits in `SEARCH_LOG.md`. Relevance notes are my interpretation.

## Standards & reference implementations
- **[V-fetched]** NIST, *FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard*,
  2024-08-14. https://csrc.nist.gov/pubs/fips/203/final
- **[tooling]** Open Quantum Safe, *liboqs* (v0.16.0 used). https://openquantumsafe.org — a
  software library; no single peer-reviewed "liboqs paper" is cited (the project site/README is
  the authoritative record). The companion paper "Open Quantum Safe" (Stebila & Mosca, SAC 2016)
  predates liboqs's current KEM API and is **not** cited to avoid overclaiming currency.
- **[V-fetched/tooling]** S. Hemminger, "Network Emulation with NetEm," *Linux Conference Australia*,
  April 2005 (confirmed via GÉANT record citing lca2005 abstract id 163). Resolves the v1 flag.

## Fault attacks on ML-KEM/Kyber (areas 1,3)
- **[V-fetched]** P. Pessl, L. Prokop, "Fault Attacks on CCA-secure Lattice KEMs," *IACR TCHES*
  2021(2):37–60. DOI 10.46586/tches.v2021.i2.37-60; ePrint 2021/064.
- **[V-fetched]** J. Hermelink, P. Pessl, T. Pöppelmann, "Fault-enabled chosen-ciphertext attacks
  on Kyber," *INDOCRYPT 2021*; ePrint 2021/1222.
- **[V-fetched]** K. Xagawa, A. Ito, R. Ueno, J. Takahashi, N. Homma, "Fault-Injection Attacks
  against NIST's PQC Round 3 KEM Candidates," *ASIACRYPT 2021*; ePrint 2021/840.
- **[V-fetched]** P. Ravi, A. Chattopadhyay, J. P. D'Anvers, A. Baksi, "Side-channel and
  Fault-injection attacks over Lattice-based Post-quantum Schemes (Kyber, Dilithium): Survey and
  New Results," ePrint 2022/737 (2022). **Preprint — not formally published** (confirmed). (Was
  [V-search] in v1; authors now verified.)
- **[V-host-listing]** J. Delvaux, "Roulette: A Diverse Family of Feasible Fault Attacks on Masked
  Kyber," *IACR TCHES 2022*; ePrint 2021/1622 (IACR artifact archive tches/2022/a23; author via
  IACR cryptodb). (Was unattributed "Roulette" in v1; author/venue now resolved.)
- **[V-fetched]** Y. Wang, J. Yu, S. Qu, X. Zhang, X. Li, C. Zhang, D. Gu, "Mind the Faulty Keccak:
  A Practical Fault Injection Attack Scheme Apply to All Phases of ML-KEM and ML-DSA," ePrint
  2024/1522 (2024, preprint). (Full title + authors now resolved; loop-abort faults in Keccak.)

## Detection / defense of the FO check (area 2)
- **[V-fetched]** L. Glabush, F. Günther, K. Hövelmanns, D. Stebila, "Verifiable Decapsulation:
  Recognizing Faulty Implementations of Post-Quantum KEMs," *CRYPTO 2025*; ePrint 2025/450.

## Dependability: fault masking / derating / containment (areas 1,5 — NEW in v2)
- **[V-fetched]** A. Avizienis, J.-C. Laprie, B. Randell, C. Landwehr, "Basic Concepts and Taxonomy
  of Dependable and Secure Computing," *IEEE Trans. Dependable and Secure Computing* 1(1):11–33,
  2004 (author-hosted PDF landwehr.org/2004-aviz-laprie-randell.pdf). — defines fault→error→failure,
  **error containment**, and **masking**; establishes masking as a foundational concept.
- **[V-host-listing]** S. S. Mukherjee, C. Weaver, J. Emer, S. K. Reinhardt, T. Austin, "A
  Systematic Methodology to Compute the Architectural Vulnerability Factors for a High-Performance
  Microprocessor," *MICRO 2003* (ACM DL 10.5555/956417.956570; companion IEEE Micro 2003
  "Measuring Architectural Vulnerability Factors," DOI 10.1109/MM.2003.1261389). — **AVF / derating /
  masking**: fraction of faults that become user-visible errors.

## Methodology: fault-injection campaigns & multiple faults (area 6 — NEW in v2)
- **[V-host-listing]** R. Leveugle, A. Calvez, P. Maistri, P. Vanhauwaert, "Statistical Fault
  Injection: Quantified Error and Confidence," *DATE 2009* (ResearchGate record; venue to confirm
  on IEEE Xplore). — confidence/sample-size in fault campaigns. **Partially verified (venue).**
- **[V-host-listing]** B. Sangchoolie, K. Pattabiraman, J. Karlsson, "An Empirical Study of the
  Impact of Single and Multiple Bit-Flip Errors in Programs," *IEEE TDSC* (ResearchGate record;
  27M experiments). — multiple-fault empirical study. **Partially verified (authors/venue to
  confirm on the publisher page).**

## Cross-layer (area 5)
- **[preprint/abstract]** "Post-Quantum Cryptographic Analysis of Message Transformations Across
  the Network Stack," arXiv:2604.08480 (2026) — per-layer PQC vulnerability, not fault interaction.
- **[V-host-listing]** "Formal Definition and Verification for Combined Random Fault and Random
  Probing Security," ePrint 2024/757 — combined *physical fault × physical probing* (near-neighbor,
  not crypto×network).

## Still UNRESOLVED / partial
- Leveugle (DATE 2009) and Sangchoolie (TDSC) exact venue/year not fetched from publisher — marked
  partial. liboqs lacks a current-API peer-reviewed citation (tooling record only).
