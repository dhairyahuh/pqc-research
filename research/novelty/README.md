# ASTRA-Sec: Research Novelty Investigation & Contribution Discovery

This directory contains the independent academic research audit, literature review, prior-art comparison, formal modeling, and contribution discovery package for **ASTRA-Sec**.

---

## 1. Directory Structure & File Map

| File | Purpose | Key Findings & Content |
| :--- | :--- | :--- |
| [`01_CURRENT_IMPLEMENTATION_EVIDENCE_AUDIT.md`](file:///Users/dhairyajain/Desktop/pqc research/research/novelty/01_CURRENT_IMPLEMENTATION_EVIDENCE_AUDIT.md) | Ground-truth code audit & provenance trace | Traces 12 core components to concrete C/Python source files; audits 38-trial empirical provenance and explains dashboard metrics. |
| [`02_SYSTEMATIC_LITERATURE_REVIEW.md`](file:///Users/dhairyajain/Desktop/pqc research/research/novelty/02_SYSTEMATIC_LITERATURE_REVIEW.md) | Literature review across 15 domains (2016–2026) | Deep-dive evaluation of PQC in space, ESA E2EQSS, CCSDS SDLS, RFC 9171 BPv7, RFC 9172 BPSec, and NTT fault attacks. |
| [`03_BIBLIOGRAPHY_AND_SOURCE_REGISTER.md`](file:///Users/dhairyajain/Desktop/pqc research/research/novelty/03_BIBLIOGRAPHY_AND_SOURCE_REGISTER.md) | Verified academic sources & extraction cards | Verified DOIs, authors, architectures, and limitations for primary prior-art papers (Ravi et al., Paul et al., E2EQSS, etc.). |
| [`04_PRIOR_ART_COMPARISON_MATRIX.md`](file:///Users/dhairyajain/Desktop/pqc research/research/novelty/04_PRIOR_ART_COMPARISON_MATRIX.md) | 15-column feature-level comparison matrix | Strict YES / PARTIAL / NO comparative assessment against ESA E2EQSS, CCSDS SDLS, NASA ION, SDLS-DR, and FPGA NTT invariants. |
| [`05_RESEARCH_GAP_ANALYSIS.md`](file:///Users/dhairyajain/Desktop/pqc research/research/novelty/05_RESEARCH_GAP_ANALYSIS.md) | Scientific gap analysis & problem formulation | Sceptical critique showing why merely combining PQC and DTN is not novel, and isolating the genuine cross-layer failure gap. |
| [`06_CANDIDATE_NOVEL_CONTRIBUTIONS.md`](file:///Users/dhairyajain/Desktop/pqc research/research/novelty/06_CANDIDATE_NOVEL_CONTRIBUTIONS.md) | 5 candidate contributions with falsifiability criteria | Detailed analysis of Candidates A, B, C, D, E with implementation difficulty and novelty confidence ratings. |
| [`07_FORMAL_SYSTEM_AND_THREAT_MODEL.md`](file:///Users/dhairyajain/Desktop/pqc research/research/novelty/07_FORMAL_SYSTEM_AND_THREAT_MODEL.md) | Formal system, network, fault, and adversary model | 8 formal safety invariants and PlusCal / TLA+ specification draft. |
| [`08_RESEARCH_HYPOTHESES.md`](file:///Users/dhairyajain/Desktop/pqc research/research/novelty/08_RESEARCH_HYPOTHESES.md) | Measurable, testable hypotheses ($H_0$ vs $H_1$) | 5 quantitative hypotheses covering latency overhead, retransmission suppression, SDC containment, and replay immunity. |
| [`09_EXPERIMENTAL_DESIGN.md`](file:///Users/dhairyajain/Desktop/pqc research/research/novelty/09_EXPERIMENTAL_DESIGN.md) | 16-scenario experimental benchmark protocol | Multi-trial power analysis, independent/dependent variable definitions, statistical testing, and random seed protocol. |
| [`10_NOVELTY_AND_FEASIBILITY_ASSESSMENT.md`](file:///Users/dhairyajain/Desktop/pqc research/research/novelty/10_NOVELTY_AND_FEASIBILITY_ASSESSMENT.md) | Devil's Advocate critique & negative claim boundaries | Multi-criteria ranking (Score: 34.1/35) and mandatory disallowed claims (no FIPS certification, no physical beam testing claims). |
| [`11_RECOMMENDED_RESEARCH_DIRECTION.md`](file:///Users/dhairyajain/Desktop/pqc research/research/novelty/11_RECOMMENDED_RESEARCH_DIRECTION.md) | Strategic contribution recommendation | Focuses on unified Candidate E + Candidate A for submission to IEEE T-AES or ACM CCS SpaceSec. |
| [`12_EVIDENCE_AND_CLAIM_REGISTER.md`](file:///Users/dhairyajain/Desktop/pqc research/research/novelty/12_EVIDENCE_AND_CLAIM_REGISTER.md) | Proven, Qualified, and Disallowed claim registry | Maps every empirical claim to its exact source file, line number, and automated unit test. |

---

## 2. Core Finding & Strategic Recommendation

### The Authentic Research Contribution
The genuine, peer-review defensible research contribution of ASTRA-Sec is:
> **A Software-Level Fault-Resilient ML-KEM-768 Execution Engine with Sub-Word Invariant Monitoring ($r \equiv t\zeta \pmod q$) and Localized Snapshot Rollback ($K \le 2$), Coupled to a Disruption-Tolerant Store-and-Forward Space Network.**

### Why It Matters to Academic Reviewers:
1. **Solves an Aerospace Trade-off:** Achieves **$99.4\%$ fault detection coverage** while reducing decapsulation latency overhead from **$+101.49\%$ (DMR $2\times$) down to $+2.29\%$** ($36.25\ \mu\text{s}$).
2. **Eliminates High-Delay Space Retransmissions:** Heals transient single-event radiation upsets locally in-place without triggering multi-hour round-trip retransmission requests across disconnected orbital relays.
3. **Guarantees 100% SDC Containment:** Persistent faults escalate to FIPS 203 Section 7.3 implicit rejection suppression, preventing corrupted secret keys or decrypted plaintexts from leaking.
