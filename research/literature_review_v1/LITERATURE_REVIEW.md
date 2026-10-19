# Literature Review — Phases 2–4 positioning (Phase 6)

Scope note: bounded by a non-systematic search (`SEARCH_LOG.md`). "Demonstrated" = what a source
states; "Relevance" = my interpretation. Verification tags per `BIBLIOGRAPHY.md`.

## 1. Fault attacks on ML-KEM/Kyber decapsulation (areas 1–3)
**Demonstrated.** A mature adversarial line shows single, well-placed faults break CCA security of
lattice KEMs: Pessl & Prokop [V-fetched, TCHES 2021/064] use one instruction-skip in the decoding
step of decapsulation; Xagawa et al. [V-fetched, ASIACRYPT 2021/840] skip the FO equality test
across nine KEMs; Hermelink et al. [V-fetched, INDOCRYPT 2021/1222] combine a ciphertext bit-flip
with a corrective fault to turn FO into a failure oracle; Ravi et al. [V-search, 2022/737] survey
SCA+FIA chosen-ciphertext faults and countermeasures. Glabush et al. [V-fetched, CRYPTO 2025/450]
move to defense, re-designing FO so a skipped re-encryption check also breaks correctness, and note
a real HQC implementation omitted this check unnoticed for 19 months.
**Relevance / contrast.** These establish that the FO re-encryption/equality check is the critical,
fault-sensitive locus — which our study treats as the containment mechanism (FO rejection), not a
target. Crucially, prior work is **adversarial** (physical/instruction-skip, key recovery). Our
Phase 2 is **non-adversarial resilience measurement** with *logical-value* faults and an
independent-oracle taxonomy; it is not a new attack, and we say so. Our observed "0 SDC / 750" is a
sampling bound, consistent with (not contradicting) the attack literature, which generally requires
*precise* faults rather than random logical-value perturbations.

## 2. Fault detection, recovery, safe rejection (area 2)
**Demonstrated.** The classic countermeasure is the FO inverse-operation (re-encrypt-and-compare);
Pessl & Prokop and Xagawa et al. show its criticality; Glabush et al. make its presence verifiable
by construction. **Relevance.** Our contract operationalizes a *measurement* discipline: detection,
recovery, and safe-fail are only credited against an **independent oracle**, and "recovery" is
explicitly structural (logical-value) — distinct from the construction-level guarantee of 2025/450.

## 3. Network/protocol disruption (area 4)
**Demonstrated.** Impairment emulation (loss/delay/duplication/reordering/corruption) is standard
via `tc-netem` [tooling]; Jepsen [tooling] injects partitions/crashes/clock-skew and checks
consistency. **Relevance.** Our Phase 3 reuses these *mechanisms* but in-process and deterministic,
around ML-KEM, with a protocol-outcome taxonomy kept separate from the cryptographic verdict and a
*meaningful* retry (fixing a tautological-retry pitfall). This is integration, not a new channel
model.

## 4. Cross-layer fault interactions (area 5) — the gap
**Demonstrated (near-neighbors).** "Combined random fault + random probing" [V-search, 2024/757]
formalizes *physical fault × physical probing*; cross-layer PQC-across-the-stack preprints
(arXiv:2604.08480 [preprint/abstract]) study per-layer algorithm vulnerability, not fault
interaction; distributed-systems fault tolerance addresses availability but not crypto-computation
faults. **Relevance.** Within the reviewed literature I found **no** matched design crossing
*in-decapsulation computation faults* with *channel/protocol faults* on a KEM. This is the most
promising positioning for Phase 4 — but, per the brief, absence in my search is **not** proof of
novelty; a systematic cross-layer search is outstanding.

## 5. Experimental methodology (area 6)
**Demonstrated.** Deterministic/stochastic network fault-injection and factorial/interaction designs
are established in dependability and statistics generally. **Relevance.** Our use of a paired 2×2
design, an interaction contrast Δ with a *paired bootstrap over seeds*, explicit conditioning on a
researcher-defined distribution F, and a joint-weight sensitivity analysis is a defensible, if not
unprecedented, application; the honesty guards (0-SDC ≠ 0 risk; masking ≠ recovery; frame-relative
inference) are the methodological emphasis.

## 6. Critical assessment & positioning
The study's defensible position is **not** "a new fault attack on ML-KEM" (that space is crowded and
adversarial) but **a reproducible, independent-oracle-gated cross-layer resilience methodology** plus
**a specific channel-masks-computation interaction observation**. The masking *concept* is known in
dependability (derating/logical masking) — flagged for citation — so novelty rests on the specific
cross-layer instantiation and the measurement discipline, both software-only and F-conditional.
Outstanding before any strong claim: systematic cross-layer search, dependability-masking citations,
and verification of all [V-search] items.
