# IEEE Candidate Shortlist for Literature Review

**Generated:** 2026-10-17  
**Purpose:** Prioritized list of IEEE-published or IEEE-adjacent papers for manual full-text retrieval  
**Scope:** Fault detection/tolerance in NTT/lattice-based PQC, software fault resilience, radiation effects on crypto hardware  

> **Anti-hallucination notice:** Bibliographic fields below are verified to the extent possible via web search and DOI cross-referencing. Fields marked `[UNVERIFIED]` require confirmation against the actual publication record. No paper contents have been fabricated. Where only abstracts or summaries are available, this is explicitly stated.

---

## Priority Levels
- **P1:** Essential to assessing the core novelty claim (must review full text)
- **P2:** Important method or closely related implementation
- **P3:** Contextual or adjacent research

---

## P1 — Essential for Novelty Assessment

### 1. Sarker, Cintas Canto, Kermani, Azarderakhsh (2023)
- **Title:** "Error Detection Architectures for Hardware/Software Co-Design Approaches of Number-Theoretic Transform"
- **Authors:** Ausmita Sarker, Alvaro Cintas Canto, Mehran Mozaffari Kermani, Reza Azarderakhsh
- **Year:** 2023 (published November 2022)
- **Venue:** IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems (TCAD), Vol. 42, No. 7, pp. 2418–2422
- **DOI:** 10.1109/TCAD.2022.3218614 `[VERIFIED via search]`
- **IEEE Xplore URL:** https://ieeexplore.ieee.org/document/9936916 `[INFERRED from DOI — verify]`
- **Relevance:** Closest IEEE-published NTT error detection work. Uses operand negation/swapping for recomputation-based CED. HW/SW co-design, not pure software. Critical comparison target.
- **Our claims it may affect:** Whether our pure-software approach offers meaningful advantage over HW/SW co-design NTT checking.
- **Full text accessed:** NO
- **Priority:** P1

### 2. Paul, Baidya, Mandal, Guha (2026)
- **Title:** "Efficient Error Detection for Number Theoretic Transform Using Algebraic Invariants Checking for Post-Quantum Cryptography and Fully Homomorphic Encryption on FPGA"
- **Authors:** Rupayan Paul, Prasun Baidya, Swarnendu Mandal, Koushik Guha
- **Year:** 2026
- **Venue:** ACM Transactions on Embedded Computing Systems (TECS), Vol. 25, No. 4, Article 68
- **DOI:** 10.1145/3674838 `[VERIFIED]`
- **Note:** This is ACM-published, NOT IEEE. Included because it is the closest prior art to our algebraic invariant approach.
- **Relevance:** Establishes the Cooley-Tukey sum invariant on FPGA. Does NOT cover inverse GS transforms, software realization, or rollback. Our primary comparison target.
- **Full text accessed:** NO (abstract-level analysis only)
- **Priority:** P1

### 3. Paul et al. (2025) — REMO
- **Title:** "REMO: Recomputation with Modular Offset for Fault Detection in NTT Butterfly Units"
- **Authors:** Rupayan Paul and others
- **Year:** 2025
- **Venue:** arXiv preprint `[UNVERIFIED — may not be IEEE-published]`
- **DOI:** Not confirmed
- **Relevance:** Extends the Paul group's NTT fault detection to modular-offset recomputation. Hardware-focused. Must verify if this overlaps with our algebraic invariant approach.
- **Full text accessed:** NO
- **Priority:** P1

### 4. Fritzmann, Sharif, Müller-Gritschneder et al. (2019)
- **Title:** "Towards Reliable and Secure Post-Quantum Co-Processors based on RISC-V"
- **Authors:** Tim Fritzmann, Umar Sharif, Daniel Müller-Gritschneder, Cezar Reinbrecht, Ulf Schlichtmann, Jorge Sepúlveda
- **Year:** 2019
- **Venue:** Design, Automation & Test in Europe Conference (DATE 2019), pp. 1148–1153
- **DOI:** 10.23919/DATE.2019.8715104 `[VERIFIED]`
- **IEEE Xplore URL:** https://ieeexplore.ieee.org/document/8715104 `[VERIFIED via search]`
- **Relevance:** RISC-V PQC co-processor with fault analysis. Hardware-focused. Establishes the hardware co-processor paradigm our pure-software approach aims to complement.
- **Full text accessed:** NO
- **Priority:** P1

### 5. Ravi, Bhasin, Sinha Roy, Chattopadhyay (2023)
- **Title:** "Fiddling the Twiddle Constants — Fault Injection Analysis of the Number Theoretic Transform"
- **Authors:** Prasanna Ravi, Shivam Bhasin, Sujoy Sinha Roy, Anupam Chattopadhyay
- **Year:** 2023
- **Venue:** IACR TCHES 2023, Issue 2, pp. 447–481
- **DOI:** 10.46586/tches.v2023.i2.447-481 `[VERIFIED]`
- **Note:** IACR/TCHES, not IEEE. Essential because it demonstrates the twiddle factor attack our twiddle blindness finding directly addresses.
- **Full text accessed:** NO
- **Priority:** P1

### 6. Reis, Chang, Vachharajani, Rangan, August (2005)
- **Title:** "SWIFT: Software Implemented Fault Tolerance"
- **Authors:** George A. Reis, Jonathan Chang, Neil Vachharajani, Ram Rangan, David I. August
- **Year:** 2005
- **Venue:** International Symposium on Code Generation and Optimization (CGO 2005), pp. 243–254
- **DOI:** 10.1109/CGO.2005.34 `[VERIFIED]`
- **IEEE Xplore URL:** https://ieeexplore.ieee.org/document/1402472 `[INFERRED — verify]`
- **Relevance:** Primary software DMR baseline. Our manuscript compares overhead directly against SWIFT-style sequential DMR.
- **Full text accessed:** NO
- **Priority:** P1

### 7. Dodd, Massengill (2003)
- **Title:** "Basic Mechanisms and Modeling of Single-Event Upset in Digital Microelectronics"
- **Authors:** Paul E. Dodd, Lloyd W. Massengill
- **Year:** 2003
- **Venue:** IEEE Transactions on Nuclear Science, Vol. 50, No. 3, pp. 583–602
- **DOI:** 10.1109/TNS.2003.813129 `[VERIFIED]`
- **IEEE Xplore URL:** https://ieeexplore.ieee.org/document/1208295 `[INFERRED — verify]`
- **Relevance:** Foundational SEU mechanisms paper. Validates our fault model assumptions.
- **Full text accessed:** NO
- **Priority:** P1

---

## P2 — Important Methods / Closely Related

### 8. Hermelink, Pessl, Pöppelmann (2021)
- **Title:** "Fault-Enabled Chosen-Ciphertext Attacks on Kyber"
- **Authors:** Julius Hermelink, Peter Pessl, Thomas Pöppelmann
- **Year:** 2021
- **Venue:** INDOCRYPT 2021 (LNCS 13143), pp. 297–318
- **DOI:** 10.1007/978-3-030-92518-5_15 `[VERIFIED]`
- **Note:** Springer/IACR, not IEEE. Essential for understanding why fail-stop is necessary.
- **Full text accessed:** NO
- **Priority:** P2

### 9. Delvaux (2022)
- **Title:** "Roulette: A Diverse Family of Feasible Fault Attacks on Masked Kyber"
- **Authors:** Jeroen Delvaux
- **Year:** 2022
- **Venue:** IACR TCHES 2022, Issue 4, pp. 637–660
- **DOI:** 10.46586/tches.v2022.i4.637-660 `[VERIFIED]`
- **Relevance:** Demonstrates SIFA-class attacks on masked Kyber. Informs our explicit exclusion of adversarial fault resistance.
- **Full text accessed:** NO
- **Priority:** P2

### 10. Dobraunig, Eichlseder, Gross, Mangard (2018)
- **Title:** "SIFA: Exploiting Ineffective Fault Attacks on Symmetric Cryptography"
- **Authors:** Christoph Dobraunig, Maria Eichlseder, Hannes Gross, Stefan Mangard
- **Year:** 2018
- **Venue:** IACR TCHES 2018, Issue 3, pp. 1–23
- **DOI:** 10.46586/tches.v2018.i3.1-23 `[VERIFIED]`
- **Relevance:** SIFA methodology. Our security boundary explicitly excludes SIFA-class attacks.
- **Full text accessed:** NO
- **Priority:** P2

### 11. Amer, Wang, Kippen et al. (2025)
- **Title:** "PQ-Hammer: End-to-End Key Recovery Attacks on Post-Quantum Cryptography Using Rowhammer"
- **Authors:** S. Amer, Y. Wang, H. Kippen, T. Dang, Daniel Genkin, Andrew Kwong, A. Nelson, A. Yerukhimovich
- **Year:** 2025
- **Venue:** IEEE Symposium on Security and Privacy (S&P 2025), pp. 48–65
- **DOI:** 10.1109/SP61157.2025.00048 `[VERIFIED]`
- **IEEE Xplore URL:** https://ieeexplore.ieee.org/document/10835724 `[INFERRED — verify]`
- **Relevance:** Hardware-induced fault attack on PQC via Rowhammer. Shows physical attack vector our work does not defend against but contextualizes.
- **Full text accessed:** NO
- **Priority:** P2

### 12. Glabush, Günther, Hövelmanns, Stebila (2025)
- **Title:** "Verifiable Decapsulation: Recognizing Faulty Implementations of Post-Quantum KEMs"
- **Authors:** L. Glabush, Felix Günther, K. Hövelmanns, Douglas Stebila
- **Year:** 2025
- **Venue:** CRYPTO 2025 (IACR ePrint 2024/1825)
- **DOI:** Not yet confirmed `[UNVERIFIED]`
- **Relevance:** Protocol-level verifiable decapsulation. Different architectural layer from our localized rollback.
- **Full text accessed:** NO
- **Priority:** P2

### 13. Hsueh, Tsai, Iyer (1997)
- **Title:** "Fault Injection Techniques and Tools"
- **Authors:** Mei-Chen Hsueh, Timothy K. Tsai, Ravishankar K. Iyer
- **Year:** 1997
- **Venue:** IEEE Computer, Vol. 30, No. 4, pp. 75–82
- **DOI:** 10.1109/2.585157 `[VERIFIED]`
- **Relevance:** Seminal fault injection survey. Validates our SWIFI methodology choice.
- **Full text accessed:** NO
- **Priority:** P2

### 14. Sarker, Cintas Canto, Kermani, Azarderakhsh — NTT Polynomial Multiplier (TCSI)
- **Title:** "Error Detection Schemes for Number Theoretic Transform Utilized in Fully Homomorphic Encryption" `[TITLE UNVERIFIED — may differ]`
- **Authors:** Ausmita Sarker, Alvaro Cintas Canto, Mehran Mozaffari Kermani, Reza Azarderakhsh
- **Year:** 2023
- **Venue:** IEEE Transactions on Circuits and Systems I (TCSI) `[UNVERIFIED — verify exact venue]`
- **Relevance:** Companion work to #1 above. RESO (Recomputing with Shifted Operands) for NTT. Hardware-focused.
- **Full text accessed:** NO
- **Priority:** P2

---

## P3 — Contextual / Adjacent Research

### 15. Kim (2026)
- **Title:** "Post-Quantum Cryptography for Space Systems: Algorithms, Implementation, and Design Constraints — A Systematic Survey"
- **Authors:** H. Kim
- **Year:** 2026
- **Venue:** Acta Astronautica, Vol. 238, pp. 112–129
- **DOI:** 10.1016/j.actaastro.2026.04.041 `[VERIFIED]`
- **Note:** Not IEEE. Space PQC survey contextualizing the application domain.
- **Full text accessed:** NO
- **Priority:** P3

### 16. Bernstein et al. (2024)
- **Title:** "KyberSlash: Division Timings Depending on Secrets in Kyber Software"
- **Authors:** Daniel J. Bernstein and others
- **Year:** 2024
- **Venue:** Technical Disclosure Advisory (kyberslash.cr.yp.to)
- **Note:** Not peer-reviewed. Timing side-channel, not fault injection. Contextual.
- **Full text accessed:** NO (web advisory)
- **Priority:** P3

### 17. Elewaily, Ali, Saleh, Abdelsalam (2024)
- **Title:** "Delay/Disruption-Tolerant Networking-based Integrated Deep-Space Relay Network: State-of-the-Art"
- **Authors:** D. I. Elewaily, H. A. Ali, A. I. Saleh, M. M. Abdelsalam
- **Year:** 2024
- **Venue:** Ad Hoc Networks, Vol. 152, Art. 103307
- **DOI:** 10.1016/j.adhoc.2023.103307 `[VERIFIED]`
- **Note:** Not IEEE. DTN context for space comm motivation.
- **Full text accessed:** NO
- **Priority:** P3

### 18. Wilson (1927)
- **Title:** "Probable Inference, the Law of Succession, and Statistical Inference"
- **Authors:** Edwin B. Wilson
- **Year:** 1927
- **Venue:** JASA, Vol. 22, No. 158, pp. 209–212
- **DOI:** 10.1080/01621459.1927.10502953 `[VERIFIED]`
- **Relevance:** Wilson score confidence interval used in our statistical reporting.
- **Full text accessed:** NO (mathematical reference only)
- **Priority:** P3

### 19. NASA (2013)
- **Title:** "Mitigating In-Space Radiation Risks — Technical Handbook"
- **Organization:** NASA
- **Number:** NASA-HDBK-4002A
- **Year:** 2013
- **Relevance:** Radiation environment reference for fault model motivation.
- **Full text accessed:** NO
- **Priority:** P3

### 20. ECSS-Q-ST-60-15C (2012)
- **Title:** "Space Product Assurance: Radiation Hardness Assurance — EEE Components"
- **Organization:** ECSS
- **Year:** 2012
- **Relevance:** Radiation hardness standard reference. We explicitly do NOT claim compliance.
- **Priority:** P3

---

## Additional IEEE Candidates to Investigate

The following topics should be searched for additional candidates once P1 full texts are reviewed:

1. **IEEE VLSI/TVLSI:** Fault-tolerant NTT architectures for lattice crypto (2022–2026)
2. **IEEE TNS:** Any radiation testing of PQC hardware implementations
3. **IEEE S&P / NDSS:** Additional fault attack papers on ML-KEM/Dilithium
4. **IEEE DATE / DAC / ICCAD:** PQC accelerator fault detection schemes
5. **IEEE TCAS-I/II:** Redundancy schemes for modular arithmetic

---

## Questions Remaining After This Shortlist

1. **Has any published work demonstrated software-level NTT fault recovery (not just detection)?** The search results consistently describe hardware detection. This may be our key novelty gap, but it cannot be confirmed without full-text review of #1 and #2.

2. **Has localized single-butterfly rollback been published in any form?** No evidence found, but absence of evidence ≠ evidence of absence. Full-text review required.

3. **Are there IEEE TNS papers specifically testing PQC crypto hardware under radiation?** The search suggests this intersection is very new (post-2025). No specific papers found, but the search was not exhaustive.

4. **Do any additional Sarker/Kermani group papers cover software-only NTT fault detection?** Their body of work appears hardware-focused, but full-text review of #1 and #14 is needed.

---

## Full Texts to Obtain First (Prioritized)

1. **#1 — Sarker et al. (2023) TCAD** — DOI: 10.1109/TCAD.2022.3218614
2. **#2 — Paul et al. (2026) ACM TECS** — DOI: 10.1145/3674838
3. **#5 — Ravi et al. (2023) TCHES** — DOI: 10.46586/tches.v2023.i2.447-481
4. **#4 — Fritzmann et al. (2019) DATE** — DOI: 10.23919/DATE.2019.8715104
5. **#6 — Reis et al. (2005) CGO** — DOI: 10.1109/CGO.2005.34
6. **#3 — Paul REMO (2025)** — search arXiv for full text
7. **#7 — Dodd & Massengill (2003)** — DOI: 10.1109/TNS.2003.813129

These 7 papers are the minimum needed for a credible novelty assessment.
