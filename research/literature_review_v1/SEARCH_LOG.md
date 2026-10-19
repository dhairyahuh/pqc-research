# Search Log — Phase 6 Literature Review

Date: 2026-10-11. Tool: web search + page fetch from this environment (US-region search; filtering
proxy). Screening: prefer authoritative hosts (IACR ePrint/TCHES, NIST CSRC, ACM/IEEE/Springer,
arXiv); confirm bibliographic fields on the host page before citing; exclude blogs/vendor pages as
primary sources (used only as pointers). "Verified" means I fetched the host page (see
BIBLIOGRAPHY tags).

## Queries run
1. `fault injection attack Kyber ML-KEM decapsulation chosen ciphertext IACR` →
   ePrint 2021/1222, 2021/840, 2022/737, 2025/1956, 2024/1522; TCHES Roulette; IACR news 29686.
2. `Pessl Prokop fault attack CCA-secure lattice KEM Fujisaki-Okamoto re-encryption TCHES` →
   TCHES 8787, ePrint 2021/064 (DOI 10.46586/tches.v2021.i2.37-60), artifact archive.
3. `countermeasure fault detection redundancy re-encryption comparison post-quantum KEM decapsulation`
   → ePrint 2025/450 (Verifiable Decapsulation), TCHES masked polynomial comparison, 2021/840.
4. `cross-layer interaction cryptographic computation fault and network protocol fault combined evaluation`
   → distributed-systems fault tolerance (arXiv 2101.12143), cross-layer PQC (arXiv 2604.08480),
   combined random fault+probing (ePrint 2024/757) — none matched crypto-compute-fault × channel-fault.
5. `reproducible deterministic network fault injection emulation Jepsen netem packet loss reordering testing`
   → tc-netem man page, "Network emulation with NetEm", Jepsen description, chaos proxies.
6. `NIST FIPS 203 Module-Lattice Key-Encapsulation Mechanism standard 2024` → CSRC final (verified).

## Pages fetched & confirmed (full metadata)
- eprint.iacr.org/2021/1222, /2021/840, /2025/450 (title+authors+year+venue confirmed).
- csrc.nist.gov/pubs/fips/203/final (FIPS 203, Aug 2024).
- Pessl&Prokop confirmed via d-nb.info/1228595291/34 + tches listing (DOI + pp.37–60).

## Screening decisions / exclusions
- Excluded side-channel-only papers (e.g., shuffled-Kyber CC-SCA 2025/1956, Curse of Re-encryption)
  as not fault-model matches, except where they bear on the FO re-encryption countermeasure.
- Excluded vendor/blog pages (encryptionconsulting, dev.to, oneuptime) as primary sources.
- Treated "combined random fault + random probing" (ePrint 2024/757) as physical fault+probing,
  NOT crypto-computation × network-protocol — recorded as a near-neighbor, not a match.

## Limitations (important)
- **Not a systematic review.** Six query strings, one search engine, a handful of fetched pages.
- Several items confirmed only from search listings (**[V-search]**), authors/year not re-fetched.
- No DBLP/Scholar/IEEE-Xplore/ACM-DL direct enumeration; recall is incomplete.
- Full PDFs were not read; relevance is judged from abstracts/snippets.
- **Absence of a matching cross-layer fault-interaction paper in these queries is NOT proof of
  novelty.** Broader querying (and expert review) is required before any originality claim.
