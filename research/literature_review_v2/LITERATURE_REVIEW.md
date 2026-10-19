# Literature Review v2 — Phase 6B synthesis

Updates v1 with resolved citations and a dependability-masking foundation. Coverage limits in
`SEARCH_LOG.md`; tags in `BIBLIOGRAPHY.md`. "Demonstrated" = source's own claim; "Relevance" = my
interpretation.

## 1. Fault attacks on ML-KEM/Kyber (areas 1–3)
Unchanged in substance from v1, now fully attributed: Pessl & Prokop (TCHES 2021), Xagawa et al.
(ASIACRYPT 2021), Hermelink et al. (INDOCRYPT 2021), Delvaux "Roulette" (TCHES 2022, ePrint
2021/1622), Wang et al. "Mind the Faulty Keccak" (2024/1522, preprint), Ravi et al. survey (2022/737,
preprint). These are **adversarial** fault attacks (physical/instruction-skip/Keccak loop-abort),
targeting key recovery and generally defeating or probing countermeasures. Glabush et al.
(CRYPTO 2025) move to defense (verifiable decapsulation). Our Phase 2 is non-adversarial resilience
measurement with logical-value faults — same loci, different intent.

## 2. Dependability foundations: masking, containment, derating (NEW in v2)
Avizienis, Laprie, Randell & Landwehr (IEEE TDSC 2004) give the canonical fault→error→failure model
and define **masking** and **error containment**. Mukherjee et al. (MICRO 2003 / IEEE Micro 2003)
quantify **derating / AVF** — the fraction of faults that become user-visible errors. **Relevance
(decisive):** our `MASKED_BY_CHANNEL` outcome is a concrete, cross-layer **instance** of this
established masking/derating principle (a channel fault prevents the memory fault from producing a
user-visible effect). We therefore attribute the concept and claim only the specific instantiation
and the measurement caution (masking ≠ recovery).

## 3. Network/protocol disruption & testing (area 4)
netem (Hemminger, LCA 2005) and Jepsen are the lineage for channel-impairment and distributed-fault
testing. Our Phase 3 reuses these mechanisms in-process and deterministically, with the KEM-specific
separation of cryptographic verdict from protocol outcome and a non-tautological retry.

## 4. Cross-layer interaction (area 5) — the remaining gap, cautiously stated
Combined-fault formalism exists for *physical fault × physical probing* (ePrint 2024/757); cross-layer
PQC preprints address per-layer algorithm vulnerability (arXiv:2604.08480), not fault interaction;
dependability has long studied *multiple faults* (single-vs-multiple bit-flip empirical studies). I
found **no** matched design crossing in-decapsulation crypto-computation faults with channel/protocol
faults on a KEM — but the search was non-systematic, so this is a cautious observation, not a novelty
proof. The *design pattern* (combined/interaction faults) is itself not new.

## 5. Methodology (area 6)
Statistical fault injection (Leveugle et al.) and interaction/factorial designs are established; our
contribution is their careful application with a paired bootstrap over seeds, explicit F-conditioning,
sensitivity analysis, and honesty guards (0-SDC ≠ 0 risk; masking ≠ recovery; frame-relative Δ).

## 6. Positioning (conservative)
The defensible contribution is a **reproducible, independent-oracle-gated cross-layer resilience
methodology** plus **a specific cross-layer instance of (established) fault masking**. It is not a new
attack, not a new channel model, and not a new masking principle. Strong-novelty claims are not
supported; the main open originality question (the crypto×channel interaction design) depends on a
systematic search that remains outstanding.
