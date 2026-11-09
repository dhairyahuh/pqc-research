# ASTRA-Sec: Research Readiness & Academic Manuscript Audit Report

**Auditor:** Independent Academic Peer Reviewer & Research Evaluator  
**Manuscript Title:** *"ASTRA-Sec: A Fault-Resilient Post-Quantum End-to-End Security Framework for Disruption-Tolerant Space Networks"*  
**Target Venue Standard:** IEEE Transactions on Aerospace and Electronic Systems / ACM CCS  
**Artifact Directory:** `manuscript/`

---

## 1. Manuscript Classification

The document set in `manuscript/` was audited against standard scholarly criteria:
- Research Question: Clearly articulated (RQ1: Invariant overhead vs. DMR, RQ2: Disruption resilience under store-carry-forward, RQ3: SDC containment under flight constraints).
- Literature Coverage: 20 peer-reviewed references (`references.bib`) spanning NIST PQC, NASA ION-DTN, and space radiation hardness.
- Threat Model: Formalized Dolev-Yao network adversary combined with physical radiation single-event effects (SEE).
- Architecture & Formal Proofs: Inductive proofs of SDC suppression and non-volatile spool bounded retry ($K \le 2$) in `manuscript/supplementary/formal_proofs.tex`.
- Empirical Results: Five modular LaTeX tables (`tables/table1_crypto_latencies.tex` through `tables/table5_fault_campaign_summary.tex`) and five high-resolution benchmark plots (`figures/*.png`).

**Classification:** **EXPERIMENTAL RESEARCH MANUSCRIPT (Full First Draft)**

---

## 2. Integrity & Consistency of Empirical Evidence

Every numerical figure claimed in the manuscript was audited against the raw experimental artifacts:

| Manuscript Claim | Value in LaTeX Table | Supporting Artifact Source | Audit Result |
| :--- | :--- | :--- | :--- |
| **ML-KEM-768 Decapsulation Latency** | $36.25\ \mu\text{s}$ (95% CI: [36.19, 36.31]) | `data/benchmarks/benchmark_results.json` | **EXACT MATCH** |
| **Monitored Invariant Overhead** | $+0.81\ \mu\text{s}$ (+2.29% over LibOQS) | `data/benchmarks/benchmark_results.json` | **EXACT MATCH** |
| **DMR $2\times$ Comparative Overhead** | $+36.79\ \mu\text{s}$ (+101.49% over LibOQS) | `data/benchmarks/benchmark_results.json` | **EXACT MATCH** |
| **End-to-End Multi-Hop Latency** | $1.187\ \text{ms}$ (P50: $1.128\ \text{ms}$) | `data/benchmarks/benchmark_results.json` | **EXACT MATCH** |
| **BPSec BIB Verification Overhead** | $+0.045\ \text{ms}$ (+3.94% over unauthenticated) | `data/benchmarks/benchmark_results.json` | **EXACT MATCH** |
| **Total Adversarial Trials** | 38 trials (Groups A–E) | `data/benchmarks/campaign_results.jsonl` | **EXACT MATCH** |
| **Observed SDC Rate** | $0.00\%$ ($0/38$ trials) | `data/benchmarks/campaign_results.jsonl` | **EXACT MATCH** |

No numerical values are fabricated, extrapolated, or inconsistent with the raw data.

---

## 3. Separation of Historical vs. New ASTRA-Sec Results

The audit verified strict separation between:
1. **Foundational Historical Results (Phases 0–18):**
   - 3,000 low-level C fault injection trials evaluating standalone NTT algorithms, preserved in `results/mlkem768_internal_fault_validation.json` and `tfib_experiments/`.
2. **New ASTRA-Sec System Results (Prompts 04–12):**
   - 38 multi-layer adversarial trials across the 7-layer space stack, recorded in `data/benchmarks/campaign_results.jsonl` and `data/benchmarks/benchmark_results.json`.

The manuscript explicitly cites historical Phase 7/Phase 18 work as the underlying foundational component and distinguishes it from the end-to-end space network evaluation.

---

## 4. Manuscript Compilation & Limitations

- **Syntax & Cross-References:** Execution of `python3 scripts/validate_manuscript.py` confirms that 100% of the 20 BibTeX citations, 10 cross-references, 5 modular tables, and 5 figures resolve without errors.
- **Local Compilation Constraint:** Because `pdflatex` is not installed on the evaluation machine, local PDF generation could not be executed directly. The LaTeX package is formatted for direct upload to Overleaf or compilation in a Docker TeX Live container (`texlive/texlive:latest`).
