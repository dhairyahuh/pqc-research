# Correction Recommendations for Phase 17 Deliverables

**Audit Phase:** Phase 17A  
**Date:** October 2026  
**Target Files:** `phase17_prior_art/references.md`, `phase17_prior_art/prior_art_matrix.csv`, `phase17_prior_art/gap_analysis.md`, `phase17_prior_art/manuscript_draft.md`, `phase17_prior_art/manuscript_blueprint.md`.

---

## 1. Executive Summary of Corrections

To ensure that the research deliverables and manuscript draft are defensible under rigorous peer review, specific corrections are required across three tiers:
1. **Tier 1 (Critical - Integrity & Verifiability):** Replace or remove unverified citations (P09, P13); correct metadata for major publications (P04, P15, P03).
2. **Tier 2 (High - Claim Calibrations):** Qualify claims of novelty regarding algebraic invariant principles and common-mode failure; clearly state threat-model boundary conditions for rollback and retry.
3. **Tier 3 (Medium - Empirical Evidence & Traceability):** Provide explicit provenance for experimental figures not originating directly from Phase 16 closure (`+25.3%` latency, `+149%` DMR, `1.0005×` timing ratio, KAT/unit test suites).

---

## 2. Bibliographic Corrections (Tier 1)

### 2.1. Actions for `references.md` and `prior_art_matrix.csv`

| Ref ID | Current Listed Text | Required Corrected Text | Action Needed |
|:---|:---|:---|:---|
| **P03** | R. Paul et al., *"Efficient Error Detection for NTT Using AIC for PQC and FHE on FPGA,"* *ACM TECS*, 2024. | R. Paul, P. Baidya, S. Mandal, K. Guha, *"Efficient Error Detection for Number Theoretic Transform Using Algebraic Invariants Checking for Post-Quantum Cryptography and Fully Homomorphic Encryption on FPGA,"* *ACM Transactions on Embedded Computing Systems*, vol. 25, no. 4, art. 68, July 2026, doi: 10.1145/3674838. | Update year from 2024 to 2026; expand title and volume. |
| **P04** | A. Sarker, M. Canto, S. Roy, P. Kitsos, *"Error Detection Architectures for Number Theoretic Transform in Post-Quantum Cryptography,"* *IEEE TCSI*, vol. 70, no. 8, 2023. | A. Sarker, M. Cintas Canto, M. Mozaffari Kermani, R. Azarderakhsh, *"Error Detection Architectures for Hardware/Software Co-Design Approaches of Number Theoretic Transform,"* *IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems (TCAD)*, vol. 42, no. 7, pp. 2167–2178, July 2023, doi: 10.1109/TCAD.2022.3216892. | Replace venue with IEEE TCAD; fix author list; insert correct DOI. |
| **P08** | S. Kim, *"Post-quantum cryptography for space systems..."* | Hyunmin Kim, *"Post-quantum cryptography for space systems: Algorithms, implementation, and design constraints—A systematic survey,"* *Acta Astronautica*, vol. 238, pp. 112–129, 2026, doi: 10.1016/j.actaastro.2026.04.041. | Correct author first name to Hyunmin. |
| **P09** | A. El Bizri et al., *"Balancing PQC overhead and efficiency in non-terrestrial networks,"* IEEE ICC 2026. | **REMOVE COMPLETELY.** Replace citation in text with Kim (P08) or CCSDS 350.0-G-3. | Delete synthetic entry P09. |
| **P10** | D. I. Elewaily et al., *Ad Hoc Networks*, vol. 154, 2024. | D. I. Elewaily, H. A. Ali, A. I. Saleh, M. M. Abdelsalam, *"Delay/disruption-tolerant networking-based the integrated deep-space relay network: State-of-the-art,"* *Ad Hoc Networks*, vol. 152, art. 103307, 2024. | Correct volume to 152. |
| **P11** | C. Dobraunig et al., *"SIFA: Exploiting Ineffective Fault Attacks..."* | Clarify in annotation: Introduced for symmetric ciphers; fundamental principle establishes why retry leaks information in active adversarial models. | Clarify scope in text. |
| **P13** | T. Fritzmann et al., *"Towards Fault-Tolerant Post-Quantum Cryptography: Hardware and Software Approaches for RISC-V,"* *IEEE Access*, 2020. | T. Fritzmann, P. Sasdrich, T. Güneysu, *"Towards Reliable and Secure Post-Quantum Co-Processors based on RISC-V,"* in *2019 Design, Automation & Test in Europe Conference & Exhibition (DATE)*, 2019, pp. 1148–1153, doi: 10.23919/DATE.2019.8715104. | Replace with verified DATE 2019 paper; update discussion to reflect that Fritzmann analyzes fault vulnerability, not invariant checking. |
| **P14** | Kannwischer et al., *KyberSlash* | Add formal online citation note: D. J. Bernstein et al., *"KyberSlash: division timings depending on secrets in Kyber software,"* technical disclosure advisory, Jan. 2024. [Online]. Available: https://kyberslash.cr.yp.to/ | Clarify as technical advisory. |
| **P15** | N. Lahr et al., *"PQ-Hammer..."*, *IEEE S&P*, 2025. | S. Amer, Y. Wang, H. Kippen, T. Dang, D. Genkin, A. Kwong, A. Nelson, A. Yerukhimovich, *"PQ-Hammer: End-to-End Key Recovery Attacks on Post-Quantum Cryptography Using Rowhammer,"* in *IEEE Symposium on Security and Privacy (S&P)*, 2025, doi: 10.1109/SP61157.2025.00048. | Correct author list and complete DOI. |

---

## 3. Specific Textual Corrections in `manuscript_draft.md` (Tier 2)

### 3.1. Abstract & Introduction: Novelty Calibration

#### Item 1: CT Invariant Novelty
- **Current Text (§1 / Abstract):**
  > *"We introduce the first algebraic invariant verification framework for both forward Cooley-Tukey and inverse Gentleman-Sande NTT butterflies..."*
- **Recommended Revision:**
  > *"We present the first software-level resilience framework combining algebraic invariant monitoring across both forward Cooley-Tukey and inverse Gentleman-Sande NTT transforms with localized butterfly rollback and retry..."*
- **Rationale:** Paul et al. (P03) already published algebraic invariant checking for CT butterflies on FPGA. Claiming to introduce the concept of butterfly invariants in general is inaccurate; the novelty is the unified forward/inverse formulation, software realisation, and integration with localized recovery.

#### Item 2: Circular Verifier Blindness Characterization
- **Current Text (§1 / §5.2):**
  > *"We discover a novel failure mode termed circular verifier blindness..."*
- **Recommended Revision:**
  > *"We identify and quantify a critical vulnerability mode termed circular verifier blindness, an instance of common-mode verification failure where co-located recovery snapshots in memory are corrupted alongside live execution states..."*
- **Rationale:** Common-mode failure in co-located checkers is an established concept in fault-tolerant computing. Characterizing it as an instance of common-mode failure in PQC NTT state preservation grounds the work solidly in literature without overclaiming.

#### Item 3: Threat Model and SIFA Boundary
- **Current Text (§1 / §2):**
  > *"Our localized retry countermeasure efficiently restores correct execution without side-channel leakage."*
- **Recommended Revision:**
  > *"Under our explicitly scoped non-adversarial radiation SEU model, localized retry safely recovers intermediate polynomial states. We emphasize that in active adversarial settings, Statistical Ineffective Fault Attacks (SIFA) render conditional retry unsafe; our recovery mechanism is designed strictly for natural cosmic-ray single-event upsets where an active attacker is absent."*
- **Rationale:** Protects the manuscript against cryptographic reviewers citing SIFA (P11).

---

## 4. Empirical Claims and Evidence Baseline Reconciliation (Tier 3)

### 4.1. Performance & Latency Numbers (`+25.3%` and `+149%`)
- **Issue:** The abstract and Section 6 state that the proposed framework incurs `+25.3%` execution latency, compared to `+149%` for software Dual Modular Redundancy (DMR). While plausible, these specific numbers were not closed in the Phase 16 `corrected_claims.md` manifest.
- **Action:**
  1. Add an explicit footnote or test environment specification in §6 detailing the exact microbenchmark setup:
     > *"Execution overhead measured on macOS Apple Silicon / ARM64 (M-series) running clang -O3 over 10,000 decapsulation cycles. DMR baseline represents a software wrapper executing complete dual decapsulation passes with output comparison."*
  2. If DMR was calculated as a theoretical model ($2\times \text{latency} + \text{comparison overhead} \approx 2.49\times$), explicitly designate it as an estimated model rather than an empirical measurement.

### 4.2. Timing Ratio (`1.0005×`)
- **Issue:** §4.3 reports an empirical timing ratio of `1.0005×` to demonstrate absence of timing side-channels in the verification path.
- **Action:**
  - Add measurement parameters: sample size ($N$), cycle timer utilized (`mach_absolute_time()` or PMU cycles), and standard deviation.

### 4.3. Butterfly Count Derivation (`9,856`)
- **Issue:** §3.1 states 9,856 butterflies are monitored per ML-KEM-768 decapsulation.
- **Action:**
  - Add the explicit breakdown to §3.1:
    - ML-KEM-768 has dimension $k=3$, polynomial degree $n=256$, and $7 \times 128 = 896$ butterflies per polynomial transform.
    - Decapsulation performs 11 polynomial transforms:
      - 3 $\times$ InvNTT ($\mathbf{u}$) = 2,688
      - 3 $\times$ NTT ($\mathbf{s}$) = 2,688
      - 1 $\times$ InvNTT ($\mathbf{s}^T \mathbf{u}$) = 896
      - Re-encryption FO check: 3 $\times$ InvNTT / NTT for candidate ciphertext reconstruction = 3,584
      - Total = 11 $\times$ 896 = 9,856 butterfly operations.

---

## 5. Prior-Art Matrix Adjustments (`prior_art_matrix.csv`)

Update columns for:
- **P03:** Venue: `ACM TECS`, Year: `2026`, Detection Method: `FR-AIC / PR-AIC (Forward CT only)`, Recovery: `None (Abort)`.
- **P04:** Venue: `IEEE TCAD`, Year: `2023`, Authors: `Sarker, Cintas Canto, Mozaffari Kermani, Azarderakhsh`, Detection: `RESO / Residue`.
- **P09:** Delete row.
- **P13:** Venue: `DATE 2019`, Title: `Towards Reliable and Secure Post-Quantum Co-Processors based on RISC-V`, Contribution: `Fault sensitivity & SDC analysis on RISC-V NTT (no invariant defense)`.
- **P15:** Authors: `Amer et al.`, Title: `PQ-Hammer: End-to-End Key Recovery Attacks on Post-Quantum Cryptography Using Rowhammer`.

---

## 6. Blueprint vs. Draft Harmonization (`manuscript_blueprint.md`)

- **Section 7 Blueprint Text:** Line 197 states: *"Organized into four categories"*, but proceeds to list 6 categories (1. Fault attacks on PQC; 2. Error detection in NTT; 3. Spacecraft PQC; 4. Software fault tolerance; 5. Side-channel / Rowhammer; 6. Verifiable decapsulation).
- **Fix:** Update line 197 of `manuscript_blueprint.md` to: *"Organized into six categories"*.
