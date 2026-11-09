# Phase 0 Changelog: State-of-the-Art, Research Gap & Contribution Analysis

**Phase:** Phase 0 — State-of-the-Art & Strategic Research Gap Audit  
**Date:** October 1, 2026  
**Status:** COMPLETE & FINALIZED  
**Git Commit:**   <!-- To be populated upon commit creation -->

---

## 1. Phase 0 Objective

The primary objective of Phase 0 was to establish an unassailable scientific ground truth for the university research project:
> **“Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems”**
covering NIST FIPS 203 (ML-KEM) and FIPS 204 (ML-DSA).

Strict Phase 0 discipline was enforced:
- **Zero new production cryptographic code** was implemented.
- **Zero fault hooks or algorithms** were modified.
- **Zero countermeasures** were engineered.
- All existing claims in the repository were audited and categorized into verified facts, formal derivations, empirical results, implementation-specific artifacts, simulation artifacts, and hypotheses.
- A comprehensive academic literature review across 25 primary sources was conducted to identify overlaps, established attacks, and genuine, defensible research gaps.

---

## 2. Files Created in Phase 0

1. `results/literature_matrix.csv`: Comprehensive RFC 4180-compliant matrix mapping 25 primary academic papers, standards, and engineering handbooks across 24 structured criteria.
2. `docs/research_overlap_matrix.md`: Comparative classification of 9 major project directions against existing literature using standardized peer-review categories.
3. `docs/state_of_art_gap_analysis.md`: Detailed 10-section analysis of the state of the art, direct overlaps, what prior work does better, what our repository does differently, candidate gaps, evidence, and novelty risks.
4. `docs/novelty_risk_table.md`: Conservative peer-review risk assessment table evaluating 8 proposed contributions against published works and specifying required proof demonstrations.
5. `docs/PHASE_0_RESEARCH_AUDIT.md`: Master research report containing the factual repository inventory (Sections A–H), the 10-Layer Research Architecture, 4 candidate contributions, and the final STOP POINT section.
6. `docs/phase0-changelog.md`: This comprehensive Phase 0 audit and changelog document.
7. `docs/research-roadmap.md`: Machine-readable, 10-phase research roadmap structuring the project from mathematical foundations through validation.
8. `docs/DEVELOPMENT_PROTOCOL.md`: Engineering and research protocol establishing Git governance, commit standards, and workflow checkpoints for all future phases.

---

## 3. Literature Sources Reviewed

A total of 25 primary sources spanning IACR, IEEE, ACM, Springer, NIST, NASA, ECSS, and CCSDS were audited and cataloged in `results/literature_matrix.csv`:

### A. ML-KEM / Kyber Fault Attacks
- **Pessl & Prokop (TCHES 2021):** *Fault Attacks on CCA-Secure Lattice KEMs* (Plaintext-Checking Oracles via decapsulation decoding and FO equality checks).
- **Hermelink, Pessl, Pöppelmann (INDOCRYPT 2021):** *Fault-Enabled Chosen-Ciphertext Attacks on Kyber* (HPP21, belief propagation key extraction via FO bypass).
- **Delvaux (TCHES 2022):** *Roulette: A Diverse Family of Feasible Fault Attacks on Masked Kyber* (Relaxed fault model targeting CBD sampling and INTT loops).
- **Ravi, Yang, Bhasin, Zhang, Chattopadhyay (TCHES 2023):** *Fiddling the Twiddle Constants: Fault Injection Analysis of the Number Theoretic Transform* (Twiddle factor zeroization).
- **Ravi, Bhasin, Sinha Roy, Chattopadhyay (ACM TECS 2023):** *Side-Channel and Fault-Injection Attacks Over Lattice-Based Post-Quantum Schemes: Survey and New Results*.
- **Jaiswal, Saha, Mukhopadhyay (IEEE TIFS 2024):** *Fault Injection Attacks on the Comparison Step of the Fujisaki-Okamoto Transform* (Booleanisation and `ct_memcmp` exploits).

### B. ML-DSA / Dilithium Fault Attacks
- **Bruinderink & Pessl (CHES 2018):** *Differential Fault Attacks on Deterministic Lattice Signatures* (DFA on deterministic Dilithium signing).
- **Krahmer, Pessl, Land, Güneysu (TCHES 2024):** *Correction Fault Attacks on Randomized CRYSTALS-Dilithium* (Signature correction attack defeating randomized hedging).
- **Bindel, Buchmann, Krämer (FDTC 2016):** *Lattice-Based Signature Schemes and Their Sensitivity to Fault Attacks* (Early taxonomy of rejection sampling vulnerabilities).
- **Bindel, Hambitzer, Krämer (IEEE TR 2017):** *Hampering Fault Attacks Against Lattice-Based Signature Schemes - Countermeasures and Their Efficiency*.

### C. NTT Error Detection & Hardware Fault Resilience
- **Mozaffari-Kermani, Azarderakhsh et al. (IEEE TCAD 2023):** *Efficient Algorithm-Level Error Detection for Number-Theoretic Transform Used for Kyber Assessed on FPGAs and ARM* (Algebraic Invariant Checking).
- **Sarker, Mozaffari-Kermani, Azarderakhsh (IEEE TETC 2024):** *Error Detection Schemes Assessed on FPGA for Multipliers in Lattice-Based Key Encapsulation Mechanisms in Post-Quantum Cryptography* (RENO/RESWO recomputation).
- **Fritzmann, Sigl et al. (IEEE TCAS-I 2022):** *Error-Detecting Number Theoretic Transform Architectures for Lattice-Based Cryptography* (Parity-preserving NTT for ASICs).

### D. Cryptographic Specifications & Baseline Designs
- **NIST FIPS 203 (2024):** *Module-Lattice-Based Key-Encapsulation Mechanism Standard (ML-KEM)*.
- **NIST FIPS 204 (2024):** *Module-Lattice-Based Digital Signature Standard (ML-DSA)*.
- **Bos, Ducas, Kiltz, Lepoint, Lyubashevsky, Schanck, Schwabe, Seiler, Stehle (IEEE EuroS&P 2018):** *CRYSTALS-Kyber: A CCA-Secure Module-Lattice-Based KEM*.
- **Ducas, Kiltz, Lepoint, Lyubashevsky, Schwabe, Seiler, Stehle (IACR TCHES 2018):** *CRYSTALS-Dilithium: A Lattice-Based Digital Signature Scheme*.

### E. Formal Verification Literature
- **PQCA / AWS Automated Reasoning Group (2024):** *Formally Verified Implementations of ML-KEM in mlkem-native* (CBMC memory safety and HOL-Light constant-time verification).
- **Barbosa, Barthe, Grégoire, Schwabe, Strub et al. (ACM CCS 2022):** *High-Assurance Post-Quantum Cryptography: Jasmin and EasyCrypt Implementations of Kyber*.
- **Arribas, Wegener, Moradi (IACR TCHES 2021):** *VerFI: A Verification Tool for Fault Injection Resistance of Cryptographic Hardware*.
- **Richter-Brockmann, Sasdrich, Güneysu (IACR TCHES 2023):** *FIVER: Formal Verification of Countermeasures Against Fault Injection Attacks* (Symbolic BDD analysis of RTL).

### F. Space Systems, Radiation & Aerospace Communications
- **NASA (NASA-HDBK-4002A, 2020):** *Mitigating Single Event Effects, Hardware and Software Approaches* (SEU, SET, SEFI fault phenomenology).
- **ECSS (ECSS-Q-ST-60-15C, 2020):** *Space Product Assurance: Radiation Hardness Assurance - EEE Components*.
- **ESA / E2EQSS Consortium (2024):** *End-to-End Quantum-Safe Security for Satellite Data Links (E2EQSS)* (CCSDS SDLS framing constraints).
- **CCSDS (CCSDS 355.0-B-1):** *Space Data Link Security Protocol (SDLS)*.
- **Geissler, Loebenberger et al. (IEEE Aerospace 2023):** *Security Evaluation of Post-Quantum Cryptography in Satellite Networks*.
- **Patranabis & Mukhopadhyay (ACM CSUR 2020):** *Fault Analysis of Cryptographic Implementations: From Classical to Post-Quantum Schemes*.
- **Zhang, Cheng et al. (USENIX Security 2023):** *Rowhammer-Assisted Fault Attacks on Post-Quantum Lattice Cryptography*.

---

## 4. Research Questions Investigated

- **RQ1 (Space Fault Mapping):** What computational and memory fault representations are most faithful to space-radiation Single Event Effects (SEEs) when applied to software-based lattice cryptographic implementations?
- **RQ2 (Differential Algorithmic Response):** How do key encapsulation mechanisms (ML-KEM) and digital signature algorithms (ML-DSA) differ fundamentally in their sensitivity and response to transient memory and computational faults?
- **RQ3 (Vulnerability Distribution):** Which specific cryptographic sub-routines (NTT butterfly stages, Keccak sponge squeezes, rejection sampling, modular reductions, serialization) are most sensitive to faults?
- **RQ4 (Failure Mode Taxonomy):** What is the quantitative distribution of fault outcomes across standardized failure classifications (Correct, Implicit Rejection, Candidate Mismatch, Rejection Loop Hang, Crash)?
- **RQ5 (Selective Resilience):** Can lightweight algorithmic resilience mechanisms achieve high fault detection rates without incurring full duplex (200%) execution overhead?
- **RQ6 (SWaP-C Overhead):** What are the precise computational latency, memory footprint, and power/throughput penalties introduced by resilience mechanisms across embedded space processor architectures?

---

## 5. Important Findings

1. `EMPIRICAL RESULT` **Discovery of NTT Error Absorption by Lossy Compression:**
   In `mlkem-native`, single-bit perturbations injected in **Layer 1** of `mlk_poly_ntt_c()` diffuse across 128 coefficients. The resulting per-coefficient error amplitude falls below the rounding quantization threshold of FIPS 203 compression ($d_u=10, d_v=4$), resulting in **100.0% legitimate decapsulation (`CORRECT_VALID_DECAPSULATION`)**. Conversely, perturbations in Layer 4 and Layer 7 remain localized, exceeding the quantization threshold and triggering **100.0% implicit rejection**.
2. `FORMAL RESULT` & `EMPIRICAL RESULT` **Fujisaki-Okamoto Transform Predicate Disambiguation:**
   - Inverting the verification flag ($0 \to 1$) on valid ciphertext triggers 100.0% implicit rejection key derivation ($K_{rej}$).
   - Inverting the flag ($1 \to 0$) on 1-bit corrupted ciphertext within LWE decryption error slack ($\pm q/4 \approx \pm 832$) recovers the ground key ($K_{ground}$), because message decoding succeeds.
   - Inverting the flag ($1 \to 0$) on severely corrupted ciphertext merely produces an out-of-sync candidate key ($K_{cand} \neq K_{ground} \neq K_{rej}$). Bypassing the FO check does NOT grant session key access when the underlying ciphertext is corrupted.
3. `SIMULATION-SPECIFIC RESULT` **Telecommand Framing Rejection of Desynchronized Keys:**
   In unauthenticated mode, 100.0% of frames decrypted with mismatched keys fail framing validation (`FORMAT_REJECTED`) due to 4-byte magic sync word mismatch ($p \approx 1 - 2^{-32}$). The widely assumed risk of "silent execution of corrupted commands" is disproved under structured telecommand framing.

---

## 6. Existing Work We Must NOT Reclaim

To maintain absolute academic integrity:
1. **DO NOT CLAIM** discovery of FO transform comparison vulnerability (published by Pessl 2021, Hermelink 2021, Jaiswal 2024).
2. **DO NOT CLAIM** physical radiation hardness based on software bit-flips (NASA and ECSS require beam testing and LET thresholds).
3. **DO NOT CLAIM** that NTT faults universally cause implicit rejection (Layer 1 proves error absorption).
4. **DO NOT CLAIM** that FO bypass under corrupt ciphertext breaks ML-KEM security.

---

## 7. Candidate Gaps (To Be Validated in Future Phases)

- **Gap 1 (Mathematical Foundation):** Analytical modeling of NTT linear error diffusion vs. non-linear lossy compression quantization rounding thresholds in FIPS 203.
- **Gap 2 (System Model):** End-to-end propagation of PQC cryptographic session desynchronization into CCSDS-compliant telecommand framing pipelines and autonomous recovery.
- **Gap 3 (Resilience):** Software-only, sensitivity-guided selective algorithmic assertions achieving $>95\%$ fault coverage with $<25\%$ CPU overhead on general-purpose flight processors.
- **Gap 4 (Implementation):** Cross-implementation fault behavior divergence between CBMC-verified portable C90 (`mlkem-native`) and SIMD-optimized dynamically linked C (`liboqs`).

---

## 8. Current Hypotheses

- `HYPOTHESIS` Wide polynomial buffers ($k \times 256 \times 16$ bits) exhibit higher upset probability per execution than scalar state under physical uniform radiation flux.
- `HYPOTHESIS` ML-DSA rejection sampling loops are uniquely vulnerable to Single Event Functional Interrupts (SEFIs) inducing execution hangs.
- `HYPOTHESIS` Closed-form error bounds $|\delta|_{\max}$ can be derived proving exact absorption limits across all FIPS 203 parameter sets (512, 768, 1024).
- `HYPOTHESIS` Lightweight polynomial assertions can detect intermediate corruptions with $<25\%$ CPU overhead.

---

## 9. Current Limitations

- Software memory bit-flips are an abstract operational proxy, not physical ionizing radiation.
- ML-DSA has KAT validation passing, but lacks internal mid-operation fault hooks.
- Spacecraft telecommand simulation is an abstract Python model, not an embedded flight-qualified protocol stack.
- Resilience directories currently contain empty stubs.

---

## 10. Tests Performed

All repository test suites executed cleanly with zero warnings and 100% reproducibility:

1. **`make test`:**
   - Path A ML-KEM Baseline Harness: **PASS**
   - Path A ML-DSA Baseline Harness: **PASS**
   - Path A vs. Path B Interoperability Test: **PASS**
   - Comprehensive NIST FIPS 203 & 204 KAT Verification (18 test vectors): **PASS (18/18)**
   - Phase 4B Internal Fault Experiment ($N=100$ and $N=1,000$ sweeps): **PASS**
2. **Python Test Suites:**
   - `python3 tests/test_ml_kem_correctness.py`: **PASS (4/4 tests)**
   - `python3 tests/test_ml_dsa_correctness.py`: **PASS (5/5 tests)**
   - `python3 experiments/system_model/spacecraft_protocol_sim.py`: **PASS (1000/1000 framing rejection; 1000/1000 session recovery)**
3. **Data Integrity Audits:**
   - `results/literature_matrix.csv`: **PASS (25 unique papers, 24 valid columns, zero syntax errors, zero missing required fields)**.
   - Local path audit: **PASS (Zero absolute paths in Phase 0 markdown and CSV files)**.

---
*Changelog finalized. Awaiting Git commit hash generation.*
