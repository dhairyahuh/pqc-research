# Phase 13 — Search Protocol (TARGETED, not systematic)

Date 2026-10-11. Explicitly a **targeted/structured scoping search**, NOT a systematic review (single
reviewer; no exhaustive enumeration; no registered protocol). Purpose: find whether a defensible
physical-radiation → software-fault mapping exists for this project, and what evidence is missing.

## Research questions
RQ-R1: What are the documented radiation-induced single-event effects (SEU/MBU/MCU/SEFI) in
semiconductor memories/logic, and how device/technology/environment-specific are they?
RQ-R2: How do physical upsets translate to software-visible errors (activation/observability,
derating/AVF, workload dependence)?
RQ-R3: Is there credible prior work connecting radiation effects to (PQC) cryptographic *software*
fault models, specifically ML-KEM/Kyber?

## Search interfaces ACTUALLY used
- A general **web search engine** (snippets/links).
- **Crossref REST API** (`api.crossref.org`) for verified bibliographic metadata/DOIs.
- Publisher/standards pages reached via those results (IEEE DOIs via Crossref; **jedec.org** for the
  JESD89 standard family; MDPI/arXiv abstract pages).
- **NOT used as databases:** IEEE Xplore, NASA NTRS, ACM DL, SpringerLink, DBLP, Google Scholar.
  IEEE items' metadata came from Crossref, not Xplore. Full-text PDFs were **not** read — assessment
  is metadata/abstract-level. This limits recall and depth; disclosed.

## Inclusion criteria (set before screening)
Include: primary radiation-effects measurements/mechanisms (SEU/MBU/MCU/SEFI, cross-sections, SER);
standards for SER measurement; AVF/derating/observability of physical faults; any credible
radiation/fault-tolerance study of (PQC) crypto. Prefer **primary** sources for physical numbers.
## Exclusion criteria
Exclude: PQC performance/benchmarking and side-channel-only hardware papers with no radiation/fault
mechanism; vendor/blog pages as primary evidence; any source whose metadata could not be confirmed.

## Limitations (honest)
- Metadata/abstract-level only; no full-text reading; non-systematic single-reviewer screening.
- No device-specific numeric radiation parameters were extracted or invented.
- Absence of a radiation↔ML-KEM-software mapping in this search is **not** proof none exists.
