# ASTRA-Sec: Research Novelty Investigation, Prior-Art Analysis, and Contribution Discovery

**Phase:** Phase 1 — Deep Research Investigation  
**Research Directorate:** Multidisciplinary Academic Research Team (PQC, Satellite Security, DTN, Fault Injection, Distributed Systems, Experimental CS)  
**Date:** November 2026  
**Status:** Completed & Preserved  
**Target Git Branch:** `astra-sec`  
**Base Commit Hash:** `efb35d5` (originating `73edad8`)  

---

## 1. Executive Summary & Purpose

This directory contains the independent, comprehensive academic novelty investigation for **ASTRA-Sec** (*Post-Quantum End-to-End Secure Messaging and Delay-Tolerant Cryptographic Resilience for Space Networks*).

The central mandate of this phase is to answer the core research question:
> **What specific technical problem can ASTRA-Sec solve that existing research and deployed systems have not adequately solved, and how can we prove that contribution experimentally?**

Rather than treating the existing prototype as self-justifying or assuming that combining disparate technologies (Post-Quantum Cryptography + Delay-Tolerant Networking + Fault Tolerance + Satellites) inherently constitutes novel research, this investigation subjects the project to rigorous peer-review scrutiny across 6 primary literature categories, examines counter-evidence, evaluates competing aerospace systems, ranks 5 distinct candidate contributions, and selects the single most defensible research trajectory.

---

## 2. Directory Structure and Deliverables

| File | Document Title | Primary Focus |
| :--- | :--- | :--- |
| [`01_PROJECT_IMPLEMENTATION_CONTEXT.md`](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase1_novelty/01_PROJECT_IMPLEMENTATION_CONTEXT.md) | Project Implementation Context | Deep audit of what currently exists in the ASTRA-Sec repository vs what is simulated, scaffolded, or planned. |
| [`02_SYSTEMATIC_LITERATURE_REVIEW.md`](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase1_novelty/02_SYSTEMATIC_LITERATURE_REVIEW.md) | Systematic Literature Review | 2016–2026 comprehensive survey across Categories A–F (PQC satellites, ESA E2EQSS/ACES, DTN RFCs, NTT fault attacks, distributed commands, cross-layer state). |
| [`03_BIBLIOGRAPHY_AND_SOURCE_REGISTER.md`](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase1_novelty/03_BIBLIOGRAPHY_AND_SOURCE_REGISTER.md) | Bibliography & Source Register | Verified primary sources with DOIs, URLs, review labels (`FULL TEXT REVIEWED`, etc.), and overlap assessments. |
| [`04_EXISTING_SYSTEMS_AND_PRIOR_ART_MATRIX.md`](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase1_novelty/04_EXISTING_SYSTEMS_AND_PRIOR_ART_MATRIX.md) | Prior-Art Comparison Matrix | 25-column comparative matrix evaluating ASTRA-Sec against ESA E2EQSS, ESA ACES, CCSDS SDLS, NASA ION-DTN, and academic baselines. |
| [`05_FIVE_CANDIDATE_CONTRIBUTIONS.md`](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase1_novelty/05_FIVE_CANDIDATE_CONTRIBUTIONS.md) | Five Candidate Contributions | Deep technical evaluation of Candidates 1 to 5 with problem definitions, gaps, falsifiability, and feasibility. |
| [`06_RESEARCH_GAP_AND_COUNTEREVIDENCE.md`](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase1_novelty/06_RESEARCH_GAP_AND_COUNTEREVIDENCE.md) | Research Gap & Counter-Evidence | The strongest counter-arguments, contradictory literature, and limitations that challenge proposed novelty. |
| [`07_FORMAL_RESEARCH_MODEL.md`](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase1_novelty/07_FORMAL_RESEARCH_MODEL.md) | Formal Research Model | Mathematical system model, network model, cryptographic model, fault model, adversary model, and safety/liveness properties. |
| [`08_RESEARCH_HYPOTHESES_AND_EXPERIMENTS.md`](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase1_novelty/08_RESEARCH_HYPOTHESES_AND_EXPERIMENTS.md) | Hypotheses & Experimental Design | 4 comparison groups (A–D), statistical power sizing, random seed strategies, and 20 specific test scenarios. |
| [`09_TECHNICAL_TRADEOFF_ANALYSIS.md`](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase1_novelty/09_TECHNICAL_TRADEOFF_ANALYSIS.md) | Technical Trade-Off Analysis | Quantitative and qualitative engineering trade-offs (overhead vs coverage, latency vs persistence, security vs availability). |
| [`10_NOVELTY_RANKING_AND_FEASIBILITY.md`](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase1_novelty/10_NOVELTY_RANKING_AND_FEASIBILITY.md) | Weighted Candidate Ranking | Weighted multi-criteria evaluation matrix (Novelty 30%, Depth 20%, Testability 15%, Feasibility 15%, Significance 10%, Reproducibility 10%). |
| [`11_FINAL_RECOMMENDED_RESEARCH_DIRECTION.md`](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase1_novelty/11_FINAL_RECOMMENDED_RESEARCH_DIRECTION.md) | Final Recommended Research Direction | Definitive research identity, paper title, abstract, formal question, hypotheses, and required implementation roadmap. |
| [`12_RESEARCH_CLAIM_AND_EVIDENCE_REGISTER.md`](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase1_novelty/12_RESEARCH_CLAIM_AND_EVIDENCE_REGISTER.md) | Research Claim & Evidence Register | Audit register linking every academic claim to its empirical evidence, confidence level, and boundary conditions. |

---

## 3. Methodological Principles & Anti-Hallucination Rules

In strict adherence to academic standards:
1. **Zero Hallucinated Citations:** All referenced publications possess verified DOIs, real author lists, and confirmed publication venues.
2. **Explicit Evidence Labeling:** Every source is classified as `FULL TEXT REVIEWED`, `OFFICIAL DOCUMENT REVIEWED`, or `ABSTRACT ONLY`.
3. **No Phantom Novelty:** Simply assembling standard libraries (e.g. LibOQS + PyDTN + SQLite) is explicitly categorized as an *engineering integration*, not a scientific research contribution.
4. **Physical Distinctions Maintained:** Software register bit-flip injection is explicitly distinguished from heavy-ion particle radiation testing in cyclotron facilities.
5. **Preservation of Baseline Code:** Application source code and historical experiment logs remain untouched.
