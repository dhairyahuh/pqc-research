# Citation Integrity and Bibliographic Audit Findings

**Audit Phase:** Phase 17A  
**Date:** October 2026  
**Scope:** Systematic audit of all 18 references cited in `phase17_prior_art/references.md`, `prior_art_matrix.md`, and `manuscript_draft.md`.

---

## 1. Executive Summary

A comprehensive bibliographic verification of all 18 references was conducted, checking listed titles, authors, years, venues, and Digital Object Identifiers (DOIs) via automated resolution and targeted web searches. 

### Key Findings Breakdown:
- **Fully Verified & Accurate (None/Clean):** 6 / 18 (33.3%) — P01, P02, P05, P06, P07, P12, P18.
- **Minor Discrepancies (Formatting/Volume/Author Initials):** 5 / 18 (27.8%) — P08, P10, P11, P14, P16, P17.
- **Major Inaccuracies (Wrong Author, Venue, Year, or Broken DOI):** 3 / 18 (16.7%) — P03, P04, P15.
- **Critical / Unverifiable Citations (Potential Hallucination/Conflation):** 2 / 18 (11.1%) — **P09, P13**.

> [!CAUTION]
> Two references cited in Phase 17 (**P09** and **P13**) cannot be verified in published academic literature and appear to be synthetic or severe conflations. Submitting a manuscript containing unverifiable or fabricated citations would result in immediate desk rejection or severe ethical sanctions. These must be replaced or excised prior to submission.

---

## 2. Detailed Breakdown of Problematic Citations

### 2.1. Critical Severity: Unverifiable or Synthetic Entries

#### Reference P09: "Balancing PQC overhead and efficiency in NTN"
- **Listed Citation:** A. El Bizri et al., *"Balancing PQC overhead and efficiency in non-terrestrial networks,"* in Proc. IEEE International Conference on Communications (ICC), 2026. DOI: `10.1109/ICC59461.2026.11587307`.
- **Verification Attempt:** 
  - Direct DOI resolution and title search yielded no matching paper under this title.
  - An IEEE ICC 2026 publication by A. El Bizri exists, but it is titled *"Consensus-Driven Fuzzy Handover Decision with PureChain Privacy-Preservation in 6G Satellite Networks"*, which focuses on blockchain-based handover, not PQC computational overhead or fault tolerance.
- **Root Cause Assessment:** Model hallucination or erroneous title synthesis during literature compilation.
- **Impact:** Used in manuscript §1 (Introduction) to motivate satellite/NTN compute constraints.
- **Remedy:** **Withdraw citation P09.** Replace with a verified survey on PQC in satellite/aerospace networks (e.g., reference P08 by Hyunmin Kim in *Acta Astronautica* 2026 already covers this adequately, or cite established CCSDS/ESA reports).

#### Reference P13: "Fault-Tolerant PQC on RISC-V"
- **Listed Citation:** T. Fritzmann et al., *"Towards Fault-Tolerant Post-Quantum Cryptography: Hardware and Software Approaches for RISC-V,"* *IEEE Access*, vol. 8, pp. 142100–142115, 2020. DOI: `10.1109/ACCESS.2020.3014761`.
- **Verification Attempt:**
  - DOI `10.1109/ACCESS.2020.3014761` returned HTTP 404 (Not Found).
  - IEEE Xplore database search for this title and author within *IEEE Access* returned zero matches.
  - Fritzmann did co-author relevant PQC hardware papers around this period:
    1. *"Towards Reliable and Secure Post-Quantum Co-Processors based on RISC-V"*, DATE 2019 (Design, Automation & Test in Europe).
    2. *"RISQ-V: Tightly Coupled RISC-V Accelerators for Post-Quantum Cryptography"*, IACR TCHES 2020(4).
- **Root Cause Assessment:** Conflation of Fritzmann's DATE 2019 paper with a fictitious *IEEE Access* venue and synthetic DOI.
- **Impact:** Cited in the manuscript and prior-art matrix as evidence of prior detection-only abort schemes on RISC-V. Note that Fritzmann's DATE 2019 paper actually performs fault injection to quantify vulnerability (SDC rates), rather than proposing an algebraic invariant detection scheme.
- **Remedy:** **Replace citation P13** with the actual DATE 2019 paper citation:  
  *T. Fritzmann, P. Sasdrich, and T. Güneysu, "Towards Reliable and Secure Post-Quantum Co-Processors based on RISC-V," in 2019 Design, Automation & Test in Europe Conference & Exhibition (DATE), Florence, Italy, 2019, pp. 1148–1153, doi: 10.23919/DATE.2019.8715104.*  
  Concurrently, adjust the text in §7 and the matrix to reflect that Fritzmann DATE 2019 evaluates fault sensitivity, not an invariant monitoring abort engine.

---

### 2.2. Major Severity: Severe Metadata Discrepancies

#### Reference P04: Sarker et al. (Error Detection for NTT)
- **Listed Citation:** A. Sarker, M. Canto, S. Roy, P. Kitsos, *"Error Detection Architectures for Number Theoretic Transform in Post-Quantum Cryptography,"* *IEEE Transactions on Circuits and Systems I: Regular Papers*, vol. 70, no. 8, 2023. DOI: `10.1109/TCSI.2023.3289124`.
- **Verification Findings:**
  - The DOI returned HTTP 404.
  - The actual publication exists in **IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems (TCAD)**, Vol. 42, No. 7, July 2023, pp. 2167–2178.
  - **Actual Title:** *"Error Detection Architectures for Hardware/Software Co-Design Approaches of Number Theoretic Transform"*.
  - **Actual Authors:** A. Sarker, M. Cintas Canto, M. Mozaffari Kermani, and R. Azarderakhsh (NOT "S. Roy" or "P. Kitsos").
- **Remedy:** Completely correct the metadata in `references.md`, `prior_art_matrix.md`, and the manuscript to match the verified IEEE TCAD 2023 article (`doi: 10.1109/TCAD.2022.3216892`).

#### Reference P15: "PQ-Hammer"
- **Listed Citation:** N. Lahr et al., *"PQ-Hammer: Rowhammer Attacks on Lattice-Based Key Encapsulation,"* in *IEEE Symposium on Security and Privacy (S&P)*, 2025. DOI: `10.1109/SP.2025`.
- **Verification Findings:**
  - The listed first author "N. Lahr" is incorrect.
  - The actual accepted IEEE S&P 2025 paper is titled: *"PQ-Hammer: End-to-End Key Recovery Attacks on Post-Quantum Cryptography Using Rowhammer"*, authored by **Samy Amer, Yingchen Wang, Hunter Kippen, Thinh Dang, Daniel Genkin, Andrew Kwong, Alexander Nelson, and Arkady Yerukhimovich**.
  - The DOI `10.1109/SP.2025` is a malformed stub; the actual DOI is `10.1109/SP61157.2025.00048`.
- **Remedy:** Update author list to Amer et al. and correct title and DOI.

#### Reference P03: Paul et al. (AIC for NTT)
- **Listed Citation:** R. Paul, P. Baidya, S. Mandal, K. Guha, *"Efficient Error Detection for NTT Using AIC for PQC and FHE on FPGA,"* *ACM Transactions on Embedded Computing Systems*, 2024. DOI: `10.1145/3674838`.
- **Verification Findings:**
  - Published in **ACM TECS, Vol. 25, Issue 4, Article 68, July 2026** (or accepted late 2025/early 2026), NOT 2024.
  - Full title: *"Efficient Error Detection for Number Theoretic Transform Using Algebraic Invariants Checking for Post-Quantum Cryptography and Fully Homomorphic Encryption on FPGA"*.
- **Remedy:** Correct year to 2026 and expand title.

---

### 2.3. Minor Severity: Metadata Hygiene & Clarifications

1. **P08 (Kim - Space PQC Survey):**
   - Listed author is "S. Kim"; verified author is **Hyunmin Kim**, *Acta Astronautica*, 2026.
2. **P10 (Elewaily et al. - DTN):**
   - Listed volume 154; verified volume is **152**, pp. 293–311, 2024.
3. **P11 (SIFA):**
   - Title in `references.md` omitted "on Symmetric Cryptography", making it appear applicable to asymmetric/PQC directly. Clarify that Dobraunig et al. introduced SIFA for symmetric ciphers, and subsequent work (Hermelink P06, Delvaux P07) ported SIFA-style reasoning to Kyber.
4. **P14 (KyberSlash):**
   - Identified as a responsible disclosure website (`https://kyberslash.cr.yp.to/`), not a peer-reviewed paper. The citation must be explicitly formatted as an online technical disclosure / security advisory.
5. **P16 (Glabush et al. - Verifiable Decapsulation) & P17 (Paul et al. - REMO):**
   - Correctly marked as preprints/CRYPTO 2025/arXiv, but exact arXiv numbers should be added once permanently indexed.

---

## 3. In-Text Claim Attribution Audit

Beyond bibliographic details, we audited whether the cited sources actually support the specific claims attributed to them in the text of `manuscript_draft.md`:

| Citation | Attributed Statement in Manuscript | Actual Finding in Cited Work | Alignment Verdict |
|:---|:---|:---|:---|
| **P03 (Paul)** | "Restricted to forward CT-NTT on FPGA; detection-only abort" | Confirmed. Focuses on CT-butterfly on FPGA, outputs error flag upon invariant violation. | **SUPPORTED** |
| **P04 (Sarker)** | "Evaluated RESO on FPGA; area overhead +18–34%" | Confirmed in TCAD paper. Uses operand-shifting detection on hardware NTT. | **SUPPORTED** |
| **P05 (Ravi)** | "Twiddle injection enables secret key recovery" | Confirmed. TCHES 2023 paper demonstrates that faulting twiddle factors during NTT decapsulation leads to plaintext/key extraction. | **SUPPORTED** |
| **P06 (Hermelink)** | "Identifies FO bypass vulnerabilities and dual-rail countermeasures" | Confirmed. Analyzes fault attacks on Kyber FO transform and recommends dual-rail verification. | **SUPPORTED** |
| **P11 (SIFA)** | "Retry on error leaks secret information under adversarial fault injection" | Confirmed. SIFA proves that conditional execution/retry based on intermediate fault status leaks key bits under active adversary. | **SUPPORTED** (Validates threat model boundary) |
| **P12 (SWIFT)** | "Generic software fault tolerance incurs +41% overhead" | Confirmed. CGO 2005 paper reports ~41% average runtime overhead for compiler-level instruction duplication. | **SUPPORTED** |
| **P13 (Fritzmann)** | "Detection-only abort on RISC-V" | **MISATTRIBUTED**. Fritzmann DATE 2019 performs fault sensitivity analysis and error rate measurement, not an invariant detection/abort engine. | **MISMATCH** |

---

## 4. Remediation Checklist for Final Manuscript

1. [ ] Remove P09 from bibliography; update §1 text to cite Kim (P08) for aerospace PQC constraints.
2. [ ] Replace P13 with Fritzmann et al., DATE 2019; revise discussion in §7 and Table 1 to accurately describe DATE 2019 as fault vulnerability evaluation rather than an architectural abort engine.
3. [ ] Correct P04 to Sarker et al., IEEE TCAD 2023 with accurate author list and DOI.
4. [ ] Correct P15 to Amer et al., IEEE S&P 2025.
5. [ ] Update P03 publication year from 2024 to 2026.
6. [ ] Correct author name in P08 to Hyunmin Kim and volume in P10 to 152.
7. [ ] Clearly tag P14 as an online security advisory.
