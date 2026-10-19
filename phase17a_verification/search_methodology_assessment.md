# Search Methodology Assessment

**Audit Phase:** Phase 17A  
**Date:** October 2026  
**Subject:** Evaluation of Phase 17 Literature Search Rigor, Transparency, and Limitations

---

## 1. Overview and Assessment Standards

To support strong novelty claims in academic publications, literature reviews must adhere to transparency, traceability, and reproducibility. We evaluate the prior-art survey documented in `phase17_prior_art/` against established academic standards (e.g., PRISMA guidelines for systematic surveys).

### Core Verdict
> [!IMPORTANT]
> The Phase 17 review cannot be characterized as an **"exhaustive"** or **"systematic literature review"** (SLR) in the formal academic sense. It is more accurately designated as a **targeted, structured literature survey**. While it identified critical adjacent works (such as Paul et al. and Sarker et al.), the methodology lacks formal screening logs, PRISMA flow documentation, and comprehensive full-text retrieval, leading directly to the bibliographic errors identified in Phase 17A.

---

## 2. Evaluation of Methodology Components

### 2.1. Search Dates and Repositories
- **Claimed Dates:** October 1–2, 2026.
- **Claimed Databases:** IEEE Xplore, ACM Digital Library, IACR Cryptology ePrint Archive / TCHES, SpringerLink, arXiv, NASA Technical Reports Server (NTRS), ESA/ECSS, and Web search engines.
- **Audit Assessment:** 
  - The coverage across cryptographic venues (IACR, TCHES) and aerospace repositories (ECSS, NASA) is broad in concept.
  - However, no query execution logs or per-database hit counts were retained. For example, executing query 1 (`("ML-KEM" OR "Kyber") AND ("fault tolerance" OR "fault resilience" OR "error detection")`) on IEEE Xplore produces dozens of hits, but the repository contains no record of how many were retrieved, screened, or excluded.

### 2.2. Inclusion and Exclusion Criteria
- **Documented Criteria:** Implicit rather than explicit.
- **Deficiencies:**
  - No explicit threshold for publication type (e.g., peer-reviewed conference/journal vs. arXiv preprints vs. security disclosure websites). As a result, formal standards (FIPS 203), peer-reviewed journal papers (ACM TECS, IEEE TCAD), conference papers (DATE, INDOCRYPT), preprints (arXiv), and raw websites (KyberSlash) were mixed in the matrix without stratified evidentiary weighting.
  - No explicit language or date cutoff criteria were defined.

### 2.3. Handling of Alternate Terminology
- **Positive Aspects:** The search queries appropriately used synonyms such as "fault tolerance," "error detection," "ABFT," "SEU," and "radiation."
- **Gaps Identified:**
  - **Algorithm-Based Fault Tolerance (ABFT):** The literature on ABFT for FFTs and orthogonal transforms (dating back to Jou & Abraham 1986) is extensive. While NTT is a discrete analogue over finite fields, the mathematical techniques of weighted checksums and algebraic invariants in FFTs are heavily related. The survey focused almost exclusively on PQC/hardware-specific literature, neglecting classical software ABFT in discrete signal processing.
  - **Concurrent Error Detection (CED):** Many hardware papers use "CED" rather than "fault tolerance" or "ABFT." While P03 was found, other CED publications on NTT may have been missed due to query constraints.

### 2.4. Full-Text Retrieval and Paywall Constraints
- **Critical Finding:** Several primary works were reviewed solely on the basis of abstracts, paper summaries, or pre-existing citations:
  - **P01 (Dodd & Massengill 2003):** IEEE paywall; abstract only.
  - **P03 (Paul et al. 2026):** ACM paywall (HTTP 403); abstract and citation metadata only.
  - **P04 (Sarker et al. 2023):** IEEE paywall; abstract only.
- **Direct Consequence:** Relying on secondary summaries or automated search snippets directly caused:
  1. The conflation of Fritzmann's DATE 2019 paper with a non-existent *IEEE Access* paper (P13).
  2. The inclusion of a synthetic/unverifiable citation (P09).
  3. The misattribution of author names and journals (P04, P15).

### 2.5. Screening Process and Deduplication
- No screening flowchart or candidate paper count was maintained.
- Without a recorded deduplication process, it is impossible for external reviewers to know whether candidate works discussing software-level NTT checks were considered and discarded, or simply overlooked.

---

## 3. Threats to Validity and Publication Bias

### 3.1. Hardware vs. Software Search Bias
- Nearly all identified prior work on NTT fault detection is implemented on **FPGA or ASIC** platforms (P03, P04, P13, P17).
- While this supports the claim that our work is the first dedicated *software* implementation of butterfly invariants in ML-KEM, it introduces a risk: general software reliability literature (e.g., compiler-based instruction duplication, software assertion checking) might contain relevant implementations that were excluded because they did not mention "NTT" or "ML-KEM" in their titles.

### 3.2. Citation Synthesis Bias
- During AI-assisted research synthesis, there is a recognized risk of "citation hallucinations"—generating plausible-sounding paper titles, authors, and DOIs that merge real themes from disparate papers. P09 and P13 are classic manifestations of this phenomenon.
- Strict verification against authoritative indexing engines (Crossref, IEEE Xplore, DBLP, Google Scholar) is mandatory before manuscript submission.

---

## 4. Recommendations for Academic Transparency

1. **Avoid Overclaiming Literature Exhaustiveness:**
   - In the manuscript's Related Work (§7) and Introduction (§1), replace phrases such as *"systematic literature review"* or *"exhaustive survey of all prior art"* with:
     > *"To our knowledge and based on a targeted survey of post-quantum cryptography fault-tolerance literature..."*
   - This language aligns with academic conventions and prevents hostile reviewer pushback.

2. **Publish Search Methodology Appendix:**
   - If submitted to a venue valuing open science (e.g., IEEE Transactions or ACM TOPS), include the exact search strings and database dates as a short reproducibility note in an appendix.

3. **Mandatory Full-Text Inspection Rule:**
   - Adopt an absolute policy: No paper may be cited in the manuscript unless the authors have personally inspected the full text (via institutional library access, author preprints, or open-access repositories) and verified that the specific page or section substantiates the claimed finding.
