# Citation Change Log and Bibliographic Audit Reconciliation

**Phase:** Phase 17B  
**Date:** October 2026  
**Audited Artifacts:** `phase17_prior_art/references.md`, `prior_art_matrix.csv`, and `manuscript_draft.md`  
**Target Repository:** `phase17b_corrected/`

---

## 1. Overview

During the Phase 17A audit, every reference cited in Phase 17 was cross-referenced against digital libraries (IEEE Xplore, ACM DL, SpringerLink, IACR, ScienceDirect/Elsevier) and DOI resolvers. This log records every change, withdrawal, and correction implemented in `phase17b_corrected/references.md` and `phase17b_corrected/manuscript_draft.md`.

---

## 2. Summary of Changes

| Category | Count | Reference IDs |
|:---|:---:|:---|
| **Fully Verified / Unchanged** | 5 | P01, P02, P05, P06, P07, P18 |
| **Metadata Corrections (Major & Minor)** | 7 | P03, P04, P08, P10, P11, P14, P15 |
| **Substituted / Replaced Reference** | 1 | P13 (Replaced synthetic IEEE Access with DATE 2019) |
| **Formally Withdrawn Reference** | 1 | P09 (Excised from text and bibliography) |
| **Unresolved / Monitored Status** | 2 | P16, P17 (Preprints without permanent DOI) |

---

## 3. Detailed Item-by-Item Change Log

### 3.1. Formally Withdrawn Citation

#### [P09] El Bizri et al. (IEEE ICC 2026)
- **Original Entry:** M. El Bizri et al., *"Balancing PQC security overhead and communication efficiency in non-terrestrial networks,"* in *Proc. IEEE International Conference on Communications (ICC)*, 2026. DOI: `10.1109/ICC59461.2026.11587307`.
- **Reason for Withdrawal:** The cited paper does not exist in published IEEE proceedings. The DOI fails to resolve. A paper by A. El Bizri at ICC 2026 exists, but addresses blockchain handover in 6G networks, not PQC computational overhead or fault resilience. This entry was a synthetic/hallucinated citation.
- **Action Taken:** **Completely removed from `references.md` and `prior_art_matrix.csv`.** In-text citations in §1 and §7 were replaced with Kim [P08] (Acta Astronautica 2026) and Elewaily et al. [P10].

---

### 3.2. Substituted Citation

#### [P13] Fritzmann et al. (PQC on RISC-V)
- **Original Entry:** T. Fritzmann et al., *"Towards Fault-Tolerant Post-Quantum Cryptography: Analyzing and Protecting the NTT on RISC-V,"* *IEEE Access*, vol. 8, pp. 140590–140605, 2020. DOI: `10.1109/ACCESS.2020.3014761`.
- **Reason for Substitution:** DOI returned HTTP 404; IEEE Access search yielded zero matching papers. Fritzmann did author relevant papers on RISC-V PQC co-processors, specifically at DATE 2019 and TCHES 2020.
- **Corrected Entry:**  
  *T. Fritzmann, P. Sasdrich, and T. Güneysu, "Towards Reliable and Secure Post-Quantum Co-Processors based on RISC-V," in 2019 Design, Automation & Test in Europe Conference & Exhibition (DATE), Florence, Italy, 2019, pp. 1148–1153. DOI: 10.23919/DATE.2019.8715104.*
- **Manuscript Text Adjustment:** Withdrew the incorrect claim that Fritzmann et al. proposed an invariant detection/abort engine. The manuscript now accurately describes DATE 2019 as a fault vulnerability and SDC characterization study on RISC-V NTT coprocessors.

---

### 3.3. Major Metadata Corrections

#### [P04] Sarker et al. (NTT Error Detection)
- **Original Entry:** A. Sarker, M. Canto, S. Roy, and P. Kitsos, *"Error detection architectures for the number theoretic transform in post-quantum cryptography,"* *IEEE Transactions on Circuits and Systems I: Regular Papers*, vol. 70, no. 11, pp. 4467–4480, 2023. DOI: `10.1109/TCSI.2023.3289124`.
- **Discrepancy:** The venue was listed as IEEE TCSI, authors included Roy and Kitsos, and DOI returned 404.
- **Corrected Entry:**  
  *A. Sarker, M. Cintas Canto, M. Mozaffari Kermani, and R. Azarderakhsh, "Error Detection Architectures for Hardware/Software Co-Design Approaches of Number Theoretic Transform," IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems (TCAD), vol. 42, no. 7, pp. 2167–2178, July 2023. DOI: 10.1109/TCAD.2022.3216892.*

#### [P15] Amer et al. ("PQ-Hammer")
- **Original Entry:** N. Lahr et al., *"PQ-Hammer: Rowhammer attacks on lattice-based key encapsulation mechanisms,"* in *IEEE Symposium on Security and Privacy (S&P 2025)*. DOI: `10.1109/SP.2025`.
- **Discrepancy:** First author listed as "N. Lahr"; DOI was an incomplete stub (`10.1109/SP.2025`).
- **Corrected Entry:**  
  *S. Amer, Y. Wang, H. Kippen, T. Dang, D. Genkin, A. Kwong, A. Nelson, and A. Yerukhimovich, "PQ-Hammer: End-to-End Key Recovery Attacks on Post-Quantum Cryptography Using Rowhammer," in IEEE Symposium on Security and Privacy (S&P 2025), pp. 48–65. DOI: 10.1109/SP61157.2025.00048.*

#### [P03] Paul et al. (AIC for NTT on FPGA)
- **Original Entry:** R. Paul, P. Baidya, S. Mandal, and K. Guha, *"Efficient error detection for NTT using algebraic invariants (AIC) checking for PQC and FHE on FPGA,"* *ACM Transactions on Embedded Computing Systems*, 2024. DOI: `10.1145/3674838`.
- **Discrepancy:** Publication year listed as 2024; actually published in ACM TECS Vol. 25, Issue 4, Article 68 in July 2026.
- **Corrected Entry:** Updated publication year to 2026 and expanded title to match official ACM DL record.

---

### 3.4. Minor Hygiene and Formatting Corrections

1. **[P08] Kim (Space PQC Survey):**
   - Listed author as "S. Kim"; corrected to **Hyunmin Kim**, *Acta Astronautica*, vol. 238, pp. 112–129, 2026.
2. **[P10] Elewaily et al. (DTN Review):**
   - Listed volume as 154; corrected to **vol. 152**, article 103307, 2024.
3. **[P11] Dobraunig et al. (SIFA):**
   - Clarified that SIFA was originally introduced for symmetric ciphers, and that its core mathematical theorem (bias in effective vs ineffective fault sets) establishes why conditional retry is fundamentally vulnerable to physical adversaries.
4. **[P14] Bernstein et al. (KyberSlash):**
   - Formatted as an online responsible disclosure technical advisory (`https://kyberslash.cr.yp.to/`), noting it is not a peer-reviewed conference paper.

---

### 3.5. Unresolved / Monitored Status

1. **[P16] Glabush et al. (Verifiable Decapsulation):**
   - Accepted at CRYPTO 2025; currently available as IACR ePrint Report 2024/1825. Will require Springer LNCS volume/page numbers once the final proceedings are indexed.
2. **[P17] Paul et al. (REMO):**
   - Circulating as an arXiv preprint. The permanent conference/proceedings citation should be inserted upon formal publication.
