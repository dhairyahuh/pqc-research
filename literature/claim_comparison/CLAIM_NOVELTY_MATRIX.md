# Claim-by-Claim Novelty Matrix

**Date:** 2026-10-17  
**Evaluation Scope:** Primary Manuscript ([paper/manuscript.md](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md)) vs. 7 Primary Literature Sources  
**Methodology:** Full-text technical comparison under Mandatory Anti-Hallucination Protocol.

---

## 1. Overview of Seven Analyzed Literature Sources

1. **Sarker et al. (2023)** [IEEE TCAD]: Hardware RENO and operand swapping for forward NTT accelerator on FPGA ($n=512, q=12289$). Detection only, zero recovery.
2. **Paul et al. (2026)** [ACM TECS]: Hardware Algebraic Invariant Checking (FR-AIC, PR-AIC) for forward Cooley-Tukey NTT PE on FPGA ($n=256, q=3329$). Detection only, zero recovery, no Gentleman-Sande INTT invariant.
3. **Paul et al. (2025)** [arXiv REMO]: Hardware Recomputation with Encoded Modular Offsets (REMO) and memory address parity for NTT on FPGA. Detection only, zero recovery.
4. **Fritzmann et al. (2019)** [IEEE DATE]: RISC-V co-processor for NewHope. Soft error characterization and Dual Modular Redundancy (DMR) software re-execution ($>+100\%$ overhead).
5. **Ravi et al. (2023)** [IACR TCHES]: Physical EMFI attack zeroizing twiddle constants on ARM Cortex-M4. 100% key recovery on Kyber/Dilithium, bypassing high-level checks.
6. **Reis et al. (2005)** [IEEE/ACM CGO]: SWIFT compiler-based software fault tolerance. Instruction/register duplication with store checking ($+41\%$ overhead on IA-64). Detection only, exception/restart recovery.
7. **Dodd & Massengill (2003)** [IEEE TNS]: Physical semiconductor physics of Single-Event Upsets (SEU) and Transients (SET) in digital CMOS.

---

## 2. Core Technical Questions on Novelty

| Question | Assessment | Detailed Technical Rationale |
|:---|:---|:---|
| **1. Is the mathematical method new?** | **PARTIALLY KNOWN / EXTENDED** | The linear sum check $(U+V) \pm (U-V') \equiv 2U \text{ or } 2V$ is algebraically known for Cooley-Tukey butterflies (published in hardware by Paul et al., July 2026). However, the mathematical formulation of the **inverse Gentleman-Sande (GS) butterfly invariant** ($(A-B)\cdot \zeta \equiv \dots$) is *unaddressed* in Paul (2026), Sarker (2023), and Paul (2025). |
| **2. Is the implementation architecture new?** | **POTENTIALLY NOVEL** | Prior invariant checking schemes (Sarker 2023, Paul 2026, Paul 2025) are exclusively **hardware FPGA/ASIC accelerators**. Our implementation is the first **pure software realization** in C99 for standard CPU pipelines with zero dynamic heap allocation and minimal register spill. |
| **3. Is the localized recovery mechanism new?** | **HIGHLY NOVEL** | **All** prior NTT fault-tolerance works (Sarker, Paul, Fritzmann) are **detection-only** (asserting an error flag / aborting) or rely on **full-routine re-execution** (DMR). No prior work implements **localized 1-butterfly register rollback and in-place recomputation** for NTT. |
| **4. Is the application to ML-KEM-768 new?** | **INCREMENTAL** | Applying fault defenses to Kyber/ML-KEM is standard in recent literature (Paul 2026, Paul 2025, Ravi 2023). The novelty is not ML-KEM itself, but covering all 11 forward CT and inverse GS transforms with localized recovery. |
| **5. Is the experimental result new?** | **NOVEL & DEFENSIVE** | 900-trial reproducible campaign demonstrating 100% recovery for transient computational faults with 0 SDC ($0/300$, upper bound $<1.26\%$) and $+16.9\%$ decapsulation latency overhead (`-O3`, M1). |
| **6. Is the demonstrated limitation new?** | **HIGHLY NOVEL** | Explicit characterization that internal algebraic invariant checking is **completely blind (0.0% local detection)** to persistent twiddle-factor memory corruption, but that the **outer Fujisaki-Okamoto (FO) re-encryption check acts as a deterministic cryptographic failsafe (0 SDC)**. Ravi 2023 showed the attack; we characterize the defense boundary. |
| **7. Is the combination sufficiently useful?** | **STRONGLY DEFENSIVE** | Yes. Combining lightweight software invariant checking with localized register rollback and FO protocol containment provides an end-to-end, bounded, low-overhead software defense. |

---

## 3. Claim-by-Claim Detailed Comparison Matrix

```
Legend for Novelty Status:
- Supported & Novel: Genuinely new technical contribution supported by empirical code/data.
- Supported & Extended: Extends known principles into an unaddressed domain (e.g., software, INTT).
- Known: Pre-existing in published literature; must be cited as prior art, not claimed as original.
- Contradicted / Unverified: Discrepancy between manuscript wording and underlying evidence.
```

### Claim 1: Dual-Transform NTT Invariant Monitoring (Forward CT + Inverse GS)
- **Manuscript Wording:** "First software-level realization of dual-transform invariant monitoring covering all 11 forward and inverse polynomial transforms in ML-KEM-768 decapsulation." ([manuscript.md:L42-45](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md#L42-L45))
- **Our Evidence:** `algorithms/source_ref/mlkem/src/poly.c:174,218` (5,376 CT + 4,480 GS = 9,856 total monitored butterflies); `tests/test_fips_kats.c`.
- **Closest Prior Work:** Paul et al. (2026) [ACM TECS, p. 9–10, Eq. 5–6, Alg. 2]; Sarker et al. (2023) [IEEE TCAD, p. 2419–2420].
- **Prior Method:** Hardware FPGA circuits for forward Cooley-Tukey butterflies. INTT is mentioned in passing without butterfly equations or error checking.
- **Concrete Difference:** Our work implements algebraic invariants in software for **both** forward CT ($U+V, U-V'$) and inverse GS ($(A-B)\zeta$) transforms across all 11 decapsulation operations.
- **Overlap:** The mathematical linear sum check for CT butterflies is identical in principle to Paul et al. (2026).
- **Novelty Status:** **Supported & Extended.**
- **Evidence Confidence:** `[DIRECTLY OBSERVED]` in `poly.c`.
- **Manuscript Action:** **Narrow and qualify.** Acknowledge Paul et al. (2026) for the forward CT algebraic principle; emphasize our contribution as extending the algebraic formulation to inverse GS butterflies and realizing it in software.

---

### Claim 2: Localized Single-Butterfly Register Rollback and In-Place Recovery
- **Manuscript Wording:** "In-place single-butterfly rollback mechanism that restores corrupted register state and recomputes the butterfly locally, achieving 100% transient fault recovery without routine re-execution." ([manuscript.md:L46-47](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md#L46-L47))
- **Our Evidence:** `poly.c:182-198, 226-242`; `experiments/fault_injection/mlkem768_internal_fault_experiment.c`; 900-trial campaign in `authoritative_results.csv` (250/250 transient faults successfully recovered).
- **Closest Prior Work:** Fritzmann et al. (2019) [IEEE DATE, p. 4, Sec. VI-A]; Reis et al. (2005) [IEEE/ACM CGO, p. 244, Sec. 3.1]; Paul et al. (2026) [ACM TECS, p. 18, Sec. 6].
- **Prior Method:**
  - Fritzmann: Full routine re-execution (DMR).
  - Reis (SWIFT): Aborts execution or branches to exception/checkpoint handler.
  - Paul (2026): Detection only (`Fault=1`), explicitly leaving correction to future work.
- **Concrete Difference:** Prior works either abort or re-execute the entire NTT ($2\times$ cost). We snapshot the two butterfly registers ($a, b$) prior to arithmetic, verify the invariant post-computation, and restore/recompute in-place within a bounded retry loop ($M=2$).
- **Overlap:** None. Localized rollback at the butterfly granularity is entirely absent from prior NTT literature.
- **Novelty Status:** **Supported & Highly Novel.**
- **Evidence Confidence:** `[DIRECTLY OBSERVED & INDEPENDENTLY RECOMPUTED]`.
- **Manuscript Action:** **Retain as primary centerpiece contribution.**

---

### Claim 3: Persistent Twiddle-Factor Corruption Blindness and Outer FO Containment
- **Manuscript Wording:** "Characterization of the invariant failure boundary: internal algebraic invariants exhibit complete blindness to twiddle-factor corruption, but the outer Fujisaki-Okamoto re-encryption check acts as an architectural failsafe, ensuring zero Silent Data Corruption." ([manuscript.md:L48-49](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md#L48-L49))
- **Our Evidence:** `research/EVIDENCE_LEDGER.md:L116-126` (147/147 persistent twiddle faults caused local invariant pass, but 100% caught by FO check); `authoritative_results.csv:H1_AGG` (591/600 circular verifier false-pass).
- **Closest Prior Work:** Ravi et al. (2023) [IACR TCHES, pp. 447–481].
- **Prior Method:** Ravi showed that zeroizing twiddle constants bypasses signature verification and enables full key extraction on Kyber and Dilithium.
- **Concrete Difference:** Ravi demonstrated the attack. We establish the *defensive boundary*: proving that local butterfly invariant checking is blind to twiddle faults because the arithmetic remains consistent with the corrupt twiddle, but revealing that the outer FO check in decapsulation prevents key/plaintext leakage by triggering implicit rejection ($c^* \neq c$).
- **Overlap:** Ravi established the criticality and exploitability of twiddle constants.
- **Novelty Status:** **Supported & Novel.**
- **Evidence Confidence:** `[DIRECTLY OBSERVED & VERIFIED IN LEDGER]`.
- **Manuscript Action:** **Retain and emphasize.** Frame this as an architectural cross-layer failure-mode characterization.

---

### Claim 4: Performance Latency Overhead of +16.9% Under `-O3`
- **Manuscript Wording:** "Latency overhead of +16.9% under -O3 (129.51 us vs. 110.79 us) on an Apple M3 Pro, achieving a 5.9x efficiency advantage over software DMR (+135.3%)." ([manuscript.md:L21-23, L302](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md#L21-L23))
- **Our Evidence:** `paper/tables/table4_performance_comparison.csv`; `phase18_audit/performance_reproduction.md`; `results/phase7i/processed/phase7i_e2e_results.json`.
- **Closest Prior Work:** Fritzmann et al. (2019) (DMR $>+100\%$); Reis et al. (2005) (SWIFT $+41\%$ on IA-64); Paul et al. (2026) ($+28\%$ area on FPGA).
- **Prior Method:** Macro DMR duplication or generic compiler duplication.
- **Concrete Difference:** Our domain-specific monitoring introduces $+16.9\%$ latency overhead on Apple Silicon, vs. $+135.3\%$ for sequential software DMR.
- **Contradiction / Discrepancy Identified:**
  1. **Platform Provenance:** Manuscript claims "Apple M3 Pro", but actual benchmark machine is an **Apple M1** (MacBookAir10,1, Darwin 27.0.0, 8 cores). The claim of M3 Pro is contradicted by the host evidence.
  2. **Comparison Scope:** The "5.9x efficiency advantage" is valid *strictly against single-threaded software sequential DMR*, not hardware lockstep.
- **Novelty Status:** **Supported Empirical Finding, but Platform String Contradicted.**
- **Evidence Confidence:** `[DIRECTLY OBSERVED NUMBERS, PLATFORM CONFLICT]`.
- **Manuscript Action:** **Correct platform specification from "Apple M3 Pro" to "Apple M1 (ARM64)". Explicitly restrict the "5.9x efficiency" claim to software sequential DMR.**

---

### Claim 5: 0/300 Silent Data Corruption (SDC) Rate and Confidence Bounds
- **Manuscript Wording:** "Zero silent data corruption observed across all active trials, establishing an empirical upper bound of 1.26% at 95% confidence." ([manuscript.md:L17](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md#L17))
- **Our Evidence:** `authoritative_results.csv:H2_SDC` ($0/300$, Wilson/Clopper-Pearson bound $[0.00\%, 1.26\%]$); `research/EVIDENCE_LEDGER.md` (Over 900 total trials: 750 active faults, 0 SDC, one-sided $97.5\%$ bound $\le 0.49\%$).
- **Closest Prior Work:** Fritzmann et al. (2019) [IEEE DATE, Table II, p. 4] (Unprotected SDC rate $3.66\%-4.96\%$; DMR residual SDC $0.72\%-0.80\%$).
- **Prior Method:** Fritzmann evaluated 10,000 simulated soft error trials and observed residual SDC under DMR.
- **Concrete Difference:** Our rollback and FO failsafe achieved $0$ SDC across all 300 active butterfly trials and all 750 campaign trials.
- **Overlap:** Standard SDC classification terminology follows established reliability literature (Fritzmann 2019, Reis 2005).
- **Novelty Status:** **Supported.**
- **Evidence Confidence:** `[INDEPENDENTLY RECOMPUTED]`.
- **Manuscript Action:** **Retain.** Clarify the sample populations: 300 active trials in the targeted validation campaign (bound $1.26\%$) vs. 750 activated faults in the full 900-trial campaign (bound $0.49\%$).

---

### Claim 6: Circular Verifier Blindness of 98.5% (94.0% to 100.0%)
- **Manuscript Wording:** "Common-mode data-source corruption exhibits 94.0% to 100.0% verifier blindness in circular models (aggregate 98.5%)." ([claim_evidence_matrix.csv:CLM-06](file:///Users/dhairyajain/Desktop/pqc%20research/claim_evidence_matrix.csv))
- **Our Evidence:** `phase16_targeted_evidence_closure/h1_activation_*.csv` ($T_1=98.0\%, T_2=94.0\%, T_3=100.0\%, T_4=100.0\%, T_5=99.0\%, T_6=100.0\%$; aggregate $591/600 = 98.5\%$).
- **Closest Prior Work:** Fritzmann et al. (2019) (noted common-mode faults bypass DMR); Reis et al. (2005) (store vulnerability window).
- **Prior Method:** Qualitative identification that shared sources cause common-mode failures.
- **Concrete Difference:** Empirical quantification of false-pass rates across 6 distinct circular verification models where the checker re-reads corrupted state.
- **Novelty Status:** **Supported Methodology Finding.**
- **Evidence Confidence:** `[DIRECTLY OBSERVED & INDEPENDENTLY RECOMPUTED]`.
- **Manuscript Action:** **Retain.** State both numbers clearly: individual models span 94.0%–100.0%, with pooled aggregate at 98.5% ($591/600$).

---

### Claim 7: Scope of Fault Model vs. Space Radiation Physics
- **Manuscript Wording:** Mentions "radiation-induced single-event upsets (SEUs)" and space deployment contexts ([manuscript.md:L12, L26](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md#L12)).
- **Our Evidence:** Software fault injection harness (`poly.c`, `mlkem768_internal_fault_experiment.c`).
- **Closest Prior Work:** Dodd & Massengill (2003) [IEEE TNS, pp. 583–602].
- **Prior Method:** Dodd & Massengill establish that physical SEUs require charge collection ($Q_{\text{coll}} \ge Q_{\text{crit}}$) from ionizing particle tracks, while SETs require electrical, logical, and temporal propagation.
- **Concrete Difference:** Our software fault injection mutates CPU registers and C variables. It does *not* simulate silicon charge transport, analog transients, or multi-cell upsets (MCUs).
- **Novelty Status:** **Must Be Bounded & Qualified.**
- **Evidence Confidence:** `[SUPPORTED BY PRIMARY SOURCE: DODD 2003]`.
- **Manuscript Action:** **Qualify and bound.** Strictly describe our model as an *architectural register single-event upset model*. Explicitly disclaim physical semiconductor radiation testing. Cite Dodd & Massengill (2003) to clearly define the boundary between architectural register bit-flips and physical silicon radiation physics.

---

## 4. Summary of Manuscript Adjustments Required

1. **Platform Correction:** Replace all references to "Apple M3 Pro" with "Apple M1 (AArch64, Darwin 27.0.0)".
2. **Prior Art Positioning:** Cite Paul et al. (ACM TECS 2026) for forward Cooley-Tukey algebraic invariants on FPGA; claim our novelty in extending invariants to inverse Gentleman-Sande butterflies, realizing the technique in pure software, and introducing localized single-butterfly register rollback.
3. **Efficiency Qualification:** Clarify that the $+16.9\%$ vs. $+135.3\%$ ($5.9\times$) efficiency advantage applies specifically against single-thread software sequential re-execution (DMR), not hardware lockstep.
4. **Physical Scope Disclaimer:** Frame resilience strictly around *architectural register upsets*, referencing Dodd & Massengill (2003) to delineate software models from physical radiation testing.
