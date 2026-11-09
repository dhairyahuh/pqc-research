# ASTRA-Sec Research Manuscript Package

This directory contains the complete scientific manuscript, LaTeX source files, verified bibliography, figures, tables, and supplementary derivations for:

**"ASTRA-Sec: A Fault-Resilient Post-Quantum End-to-End Security Framework for Disruption-Tolerant Satellite Communication"**

---

## Directory Organization

- [`main.tex`](file:///Users/dhairyajain/Desktop/pqc%20research/manuscript/main.tex): Master IEEE/ACM-compliant LaTeX manuscript document.
- [`references.bib`](file:///Users/dhairyajain/Desktop/pqc%20research/manuscript/references.bib): Verified BibTeX bibliography containing primary standards (NIST FIPS 203, FIPS 204, IETF RFC 9171, RFC 9172, CCSDS SDLS) and peer-reviewed literature.
- [`figures/`](file:///Users/dhairyajain/Desktop/pqc%20research/manuscript/figures): High-resolution 300 DPI publication plots.
- [`tables/`](file:///Users/dhairyajain/Desktop/pqc%20research/manuscript/tables): Modular LaTeX tables included in the manuscript.
- [`supplementary/`](file:///Users/dhairyajain/Desktop/pqc%20research/manuscript/supplementary): Formal mathematical invariant derivations and proofs.
- [`reproducibility.md`](file:///Users/dhairyajain/Desktop/pqc%20research/manuscript/reproducibility.md): Deterministic instructions to reproduce every figure, table, and experimental trial.

---

## Compilation

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```
