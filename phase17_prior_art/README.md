# Phase 17: Systematic Prior-Art Review and Research Manuscript Preparation

**Date:** October 2026  
**Repository:** `https://github.com/dhairyahuh/pqc-research`  
**Branch:** `space-resilience-framework`  
**Baseline Commit:** `ca38dec`

---

## Deliverables

| File | Description | Status |
|:---|:---|:---|
| `prior_art_matrix.csv` | 18-work systematic literature matrix with structured metadata | Complete |
| `gap_analysis.md` | Novelty differentiation, prior-art gap analysis, and threats to novelty | Complete |
| `manuscript_blueprint.md` | Section-by-section manuscript content plan with evidence mappings | Complete |
| `research_questions.md` | Formal research questions, hypotheses, null hypotheses, and non-claims | Complete |
| `references.md` | Consolidated reference list organized by category | Complete |
| `manuscript_draft.md` | Full manuscript draft | Complete |

---

## Literature Search Methodology

### Databases Searched
- IEEE Xplore
- ACM Digital Library
- IACR Cryptology ePrint Archive / TCHES
- SpringerLink
- arXiv
- NASA Technical Reports Server (NTRS)
- ESA/ECSS publications
- Web search (Google Scholar equivalent)

### Search Queries
1. `("ML-KEM" OR "Kyber") AND ("fault tolerance" OR "fault resilience" OR "error detection")`
2. `("NTT" OR "Number Theoretic Transform") AND ("invariant" OR "ABFT" OR "rollback" OR "recovery")`
3. `("SEU" OR "radiation") AND ("post-quantum" OR "lattice cryptography")`
4. `("spacecraft" OR "satellite") AND ("PQC" OR "ML-KEM") AND ("fault" OR "reliability")`
5. `("SIFA" OR "recomputation" OR "retry") AND ("lattice-based" OR "Kyber")`
6. `("KyberSlash" OR "timing") AND ("ML-KEM" OR "Kyber")`
7. `("Rowhammer") AND ("Kyber" OR "ML-KEM" OR "lattice")`
8. `("verifiable decapsulation") AND ("ML-KEM" OR "Kyber")`
9. `("REMO" OR "recomputation") AND ("NTT") AND ("FPGA")`
10. `("Fujisaki-Okamoto") AND ("fault injection" OR "bypass")`

### Search Dates
- October 1–2, 2026

### New Works Identified (Not in Phase 16 Baseline)
1. **P14 — KyberSlash** (Kannwischer et al., 2024): Timing side-channel in division operations.
2. **P15 — PQ-Hammer** (Lahr et al., 2025): Rowhammer key recovery against lattice KEMs.
3. **P16 — Verifiable Decapsulation** (Glabush et al., 2025): Protocol-level FO binding defense.
4. **P17 — REMO** (Paul et al., 2025): FPGA CT-BU fault detection with modular offset.
5. **P18 — FIPS 203** (NIST, 2024): ML-KEM standard specification (formally cataloged).

---

## Novelty Verdict

The systematic review confirms that **no published work provides**:
1. Software-level dual-transform (forward + inverse) NTT algebraic invariant monitoring.
2. Autonomous localized register rollback for any lattice-based KEM.
3. Characterization of circular verifier blindness under co-located memory corruption.

The contribution is defensible under the Phase 16 bounded thesis, subject to the threat model and limitation constraints documented in `gap_analysis.md`.
