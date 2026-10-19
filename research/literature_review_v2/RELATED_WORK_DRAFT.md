# Related Work (manuscript-ready draft v2) — Phase 6B

> Status: DRAFT for insertion into `MANUSCRIPT.md` **after authorization**. All citations are
> verified to an authoritative host (see `BIBLIOGRAPHY.md`); two methodology items (Leveugle;
> Sangchoolie et al.) are marked partial and may be dropped if not confirmed on the publisher page.
> This section is deliberately conservative and is **not** exhaustive (non-systematic search).

## Related work

**Fault attacks on lattice KEMs.** Precisely placed faults can break CCA security of
Fujisaki–Okamoto (FO) based lattice KEMs. Pessl and Prokop recover keys from a single
instruction-skipping fault in the decapsulation decoding step (TCHES 2021). Xagawa et al. show that
skipping the FO equality test compromises Kyber and other Round-3 KEMs (ASIACRYPT 2021). Hermelink,
Pessl, and Pöppelmann use a ciphertext bit-flip plus a corrective fault to turn FO into a
decryption-failure oracle (INDOCRYPT 2021); Delvaux extends this inequality attack to masked Kyber
(TCHES 2022); Wang et al. inject loop-abort faults in Keccak across all phases of ML-KEM/ML-DSA
(ePrint 2024/1522, preprint); Ravi et al. survey side-channel and fault chosen-ciphertext attacks and
countermeasures (ePrint 2022/737, preprint). These are **adversarial** attacks aimed at key recovery.
Our study differs in intent and model: it **measures resilience and availability** under
*logical-value* software faults rather than mounting an attack, and does not extend this attack line.

**Defending the FO check.** Because the FO re-encryption/equality check is security-critical but not
functionally necessary, a faulty implementation can silently omit it. Glabush, Günther, Hövelmanns,
and Stebila propose *verifiable decapsulation*, binding the check to functionality so that omission
also fails correctness tests, motivated by a real HQC implementation that omitted re-encryption
unnoticed for 19 months (CRYPTO 2025). Our contribution is complementary and operational: detection
and recovery are credited only against an independent oracle, and recovery under logical-value faults
is reported as structural.

**Dependability: masking and derating.** The fault→error→failure model and the notions of *masking*
and *error containment* are foundational (Avizienis, Laprie, Randell, and Landwehr, IEEE TDSC 2004),
and *derating* / architectural-vulnerability-factor analysis quantifies the fraction of faults that
become user-visible errors (Mukherjee et al., MICRO 2003). We draw on this directly: the outcome we
label `MASKED_BY_CHANNEL` — a channel disruption preventing an in-decapsulation memory fault from
ever activating — is a cross-layer **instance of established fault masking/derating**, not a new
mechanism. Our methodological point is that such masked outcomes must not be scored as recovery.

**Network/protocol disruption.** Channel-impairment emulation — loss, delay, duplication,
reordering, corruption — is standard (Hemminger, "Network Emulation with NetEm," Linux Conf Au 2005),
and distributed-systems fault testing such as Jepsen injects partitions, crashes, and clock skew. We
reuse these impairment mechanisms in a deterministic in-process emulator around ML-KEM key
establishment, separating the cryptographic verdict from the protocol outcome and using a retry that
redraws the channel so recovery is not tautological.

**Combined and cross-layer faults.** Combined-fault formalisms exist for *physical fault × physical
probing* (ePrint 2024/757), dependability has long studied *multiple faults* (e.g., empirical
single-vs-multiple bit-flip studies), and cross-layer post-quantum analyses consider per-layer
algorithm vulnerability (arXiv:2604.08480, preprint). Within the literature we reviewed we did not
find a matched experiment crossing in-decapsulation crypto-computation faults with channel/protocol
faults on a KEM; we therefore present our combined design as, to our knowledge within the reviewed
sources, a new cross-layer *pairing*, while noting that combined/interaction fault designs are not
themselves new and that our search was not systematic.

> **OUTSTANDING before camera-ready:** systematic database search (IEEE Xplore/ACM DL/DBLP/Scholar);
> confirm Leveugle (DATE 2009) and Sangchoolie et al. (TDSC) on publisher pages or drop them; a
> peer-reviewed citation for liboqs's current API if one is required. See `SEARCH_LOG.md`.
