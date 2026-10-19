# Phase 17B Revision Summary: Substantive Changes and Unresolved Issues

**Phase:** Phase 17B  
**Date:** October 2026  
**Audited Artifacts:** `phase17_prior_art/` deliverables reconciled to `phase17b_corrected/`  
**Target Submission:** Research Manuscript Revisions

---

## 1. Executive Summary

Phase 17B applied the forensic verification findings from `phase17a_verification/` to systematically revise the research manuscript, bibliography, and evidentiary foundations of the post-quantum fault-resilience architecture. 

All overstatements, unverified constant-time assertions, and problematic citations have been excised. Novelty claims have been narrowed to acknowledge prior art in hardware algebraic invariant checking (Paul et al. 2026), and circular verifier blindness has been properly positioned as a common-mode verification failure in shared memory.

---

## 2. Summary of Substantive Revisions

### 2.1. Manuscript Novelty Claim Calibrations
1. **Cooley-Tukey Invariant Prior Art (NC1):**
   - *Previous Phase 17 Text:* Claimed to introduce the first algebraic invariant verification framework for NTT butterflies.
   - *Phase 17B Correction:* Explicitly acknowledged that Paul et al. (ACM TECS 2026) introduced CT invariant checking for forward NTT on FPGA accelerators. Re-scoped the contribution to: (1) novel derivation of complementary sum and multiplier invariants for the inverse Gentleman-Sande NTT ($r_0 + \zeta r_1 \equiv 2u$), (2) native C software realization covering all 9,856 butterflies, and (3) localized register rollback and single-butterfly retry.
2. **Circular Verifier Blindness Framing (NC2):**
   - *Previous Phase 17 Text:* Described circular verifier blindness as an entirely novel general failure mode.
   - *Phase 17B Correction:* Reframed as an instance of *common-mode verification failure* in modular redundancy where co-located snapshots are corrupted simultaneously with the live execution state.
3. **Threat Model and the SIFA Boundary (NC3):**
   - *Previous Phase 17 Text:* Claimed localized retry was unconditionally safe.
   - *Phase 17B Correction:* Stated explicitly that retry is safe strictly under non-adversarial Poisson radiation SEU models. Formally highlighted that under active physical fault attacks, Statistical Ineffective Fault Attacks (SIFA, Dobraunig et al. 2018) prohibit retry, requiring fail-stop-only operation.
4. **Literature Survey Framing:**
   - *Previous Phase 17 Text:* Described literature work as an "exhaustive" or "systematic literature review."
   - *Phase 17B Correction:* Characterized as a "targeted literature survey of PQC fault-tolerance mechanisms."

---

### 2.2. Quantitative and Empirical Baselines
1. **Silent Data Corruption (SDC):**
   - Reconciled denominator to strictly $n = 300$ active fault trials (excluding $n = 100$ clean controls).
   - Stated as $0 / 300$ observed events with 95% Wilson score confidence interval of $[0.00\%, 1.26\%]$. Excised all claims that zero observed SDCs constitutes mathematical proof of zero SDC probability.
2. **Target F5B Semantics:**
   - Clarified that Target $F5B$ ($t \leftarrow 0$) is an abstract software debug hook forcing intermediate variable zeroing, not a physical silicon stuck-at fault or analog latch-up event.
3. **Execution Latency (+25.3%) and Software DMR (+149%):**
   - Documented exact microbenchmarking methodology: macOS AArch64 (Apple Silicon M-series), Apple Clang 15.0, `-O2`, 10,000 cycles.
   - Explicitly documented that DMR represents single-thread software-sequential duplicate execution ($2.49\times T_0$), and cited the historical cleanroom range (+16.79% to +28.91% for monitoring vs +140.3% to +160.8% for DMR).
4. **Butterfly Operation Count Breakdown (9,856):**
   - Provided complete arithmetic derivation in §3.1: $11 \text{ polynomial transforms} \times 896 \text{ butterflies per polynomial} = 9{,}856 \text{ total monitored operations}$.
5. **Constant-Time Claims:**
   - Excised claims of certified constant-time security. Acknowledged that error-recovery introduces conditional branching, and that formal microarchitectural leakage analysis (TVLA / dudect) on the compiled binary has not been performed.

---

### 2.3. Bibliographic Overhaul
1. **Citation P09 Withdrawn:** Excised synthetic citation to El Bizri et al. (IEEE ICC 2026). Replaced in-text citations with Kim [P08] (Acta Astronautica 2026).
2. **Citation P13 Substituted:** Replaced synthetic IEEE Access citation with verified paper: *T. Fritzmann, P. Sasdrich, and T. Güneysu, "Towards Reliable and Secure Post-Quantum Co-Processors based on RISC-V," DATE 2019*. Replaced claim of an invariant abort engine with an accurate description of DATE 2019 as a fault vulnerability and SDC characterization study.
3. **Metadata Corrected for Major Papers:**
   - **P04:** Corrected venue to *IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems (TCAD)*, vol. 42, no. 7, 2023; corrected author list to Sarker, Cintas Canto, Mozaffari Kermani, and Azarderakhsh; updated DOI.
   - **P15:** Corrected title, DOI, and author list to Samy Amer et al., *IEEE Symposium on Security and Privacy (S&P 2025)*.
   - **P03:** Updated publication year to 2026, *ACM TECS*.
   - **P08:** Corrected first name to Hyunmin Kim, *Acta Astronautica*, 2026.
   - **P10:** Corrected volume to 152, *Ad Hoc Networks*, 2024.

---

## 3. Concise Summary of Unresolved Issues

While the manuscript and supporting artifacts are now internally consistent, academically honest, and traceable to repository data, the following specific items remain unresolved and represent essential future work or pre-submission qualifications:

1. **Embedded Space Processor Evaluation:** All experiments remain desktop-host-measured (macOS AArch64). Microarchitectural execution on real or emulated embedded space cores (e.g., Cobham Gaisler LEON3/SPARC V8 or NOEL-V RISC-V) has not been measured.
2. **Physical Radiation Qualification:** No physical heavy-ion, proton, or neutron beam irradiation testing has been performed; all data stems from software-implemented fault injection.
3. **Formal Microarchitectural Timing Verification:** No TVLA or dudect Welch's t-test has been run on the compiled binary to formally quantify timing side-channel leakage across the fault-recovery pathway.
4. **Twiddle Factor Integrity Hardening:** The butterfly invariants cannot detect corruption residing in the static twiddle factor table ($\zeta$); an orthogonal ROM integrity mechanism (e.g., CRC-32 or hardware parity) remains an open implementation task.
5. **Proceedings Indexing for Preprints:** Citations [P16] (Glabush et al., CRYPTO 2025) and [P17] (Paul et al., REMO) will require permanent volume/page metadata once formally indexed in publisher databases.

---

## 4. Final Status Recommendation

### Final Status: **READY FOR SUPERVISOR REVIEW**

**Justification:**
- All synthetic or unverifiable citations have been excised or replaced with verified primary records.
- All numerical metrics have been reconciled line-by-line with Phase 16 baseline evidence manifests, with explicit denominators ($n=300$) and confidence intervals ($[0.00\%, 1.26\%]$).
- All novelty claims have been appropriately calibrated to acknowledge hardware prior art (Paul et al. 2026) and classical fault tolerance theory (common-mode failure).
- The threat-model boundary with SIFA has been explicitly established.
- The work does not overstate its readiness: limitations regarding desktop emulation, absence of physical beam testing, and microarchitectural timing verification are clearly declared.

The revised package in `phase17b_corrected/` is complete, defensible, and ready for supervisor and co-author review.
