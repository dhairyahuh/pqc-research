# Literature Search Strategy & Protocol
**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Phase:** 7L — Independent Literature Review, Research Gap Validation, and Novelty Assessment  
**Date:** October 2026  
**Status:** Complete & Verified  

---

## 1. Search Objectives & Scope

The primary objective of this literature review is to systematically examine the existing state of the art surrounding fault resilience, fault injection attacks, algorithm-based fault tolerance, and space radiation effects in post-quantum cryptographic (PQC) systems—specifically Module-Lattice-Based Key-Encapsulation Mechanisms (ML-KEM / CRYSTALS-Kyber) and Digital Signatures (ML-DSA / CRYSTALS-Dilithium).

The review establishes:
1. What mathematical checking mechanisms, invariants, and error detection schemes have been established for the Number Theoretic Transform (NTT) and modular arithmetic.
2. What physical and simulated fault attack models have been formulated against lattice-based KEMs, Fujisaki-Okamoto (FO) transformations, and NTT butterfly networks.
3. What software-level versus hardware-level fault mitigation approaches exist, comparing their fault coverage, overhead, and architectural assumptions.
4. How software-implemented fault tolerance relates to space radiation environments, Single-Event Upsets (SEUs), and spacecraft avionics standards.
5. Which candidate contributions of the current project are genuinely distinctive versus known prior art or incremental engineering.

---

## 2. Research Areas & Target Domains

The systematic review spans four core interdisciplinary areas:

### Area A: Algorithm-Based Fault Tolerance (ABFT) & Arithmetic Invariants
- Classical ABFT for linear and transform operations (matrices, FFTs, convolutions).
- Checksum and algebraic invariant checking (AIC) in modular arithmetic rings ($\mathbb{Z}_q$).
- Error detection and correction mechanisms tailored to Cooley-Tukey (CT) and Gentleman-Sande (GS) butterfly structures.
- Redundant computation schemes: Recomputation with Negated Operands (RENO), Swapped Operands (RESWO), and Scaled Operands (RECO).
- In-place rollback and recomputation mechanisms in software and hardware architectures.

### Area B: Cryptographic Fault Attacks on Lattice-Based Cryptography
- Physical and logical fault injection attacks against Module Learning With Errors (M-LWE) and Module Learning With Rounding (M-LWR).
- Differential Fault Analysis (DFA) and Ineffective Fault Analysis (IFA) against ML-KEM/Kyber decapsulation.
- Fault attacks targeting the Fujisaki-Okamoto (FO) re-encryption loop and ciphertext comparison gates ($c == c'$).
- Twiddle factor manipulation attacks (e.g., zeroizing twiddle constants to collapse ring dimension and entropy).
- Fault-assisted plaintext-checking and chosen-ciphertext attacks exploiting error feedback or side channels.

### Area C: PQC Implementation Resilience & Software Hardening
- Fault-resistant software and hardware implementations of ML-KEM and ML-DSA.
- Dual Modular Redundancy (DMR), Triple Modular Redundancy (TMR), and selective redundancy.
- Comparative overheads (cycle latency, code size, memory footprint) across microcontrollers (e.g., ARM Cortex-M4 / pqm4), general-purpose CPUs (x86_64, AArch64), and FPGAs/ASICs.
- Fail-stop semantics, implicit rejection handling ($K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$ under FIPS 203), and exception containment.

### Area D: Space Systems, Radiation Environments, & Fault Injection Methodology
- Radiation-induced Single-Event Effects (SEE): Single-Event Upsets (SEU), Single-Event Transients (SET), and Multiple-Node Upsets (MNU).
- Radiation hardness assurance standards: ECSS-Q-ST-60-15C, NASA-HDBK-4002A.
- Spacecraft on-board data handling (OBDH), payload cryptography, and telemetry/telecommand (TT&C) security constraints.
- Epistemological and experimental limitations of software-implemented fault injection (SWIFI) versus beam testing (heavy ion, proton, pulsed laser).

---

## 3. Search Databases & Information Sources

The search utilized authoritative academic repositories, peer-reviewed publishers, and standardization bodies:
1. **IACR Cryptology ePrint Archive & TCHES:** Premier venue for cryptographic hardware and embedded systems (CHES / TCHES).
2. **IEEE Xplore Digital Library:** IEEE Transactions on Computers (TC), IEEE Transactions on Nuclear Science (TNS), IEEE Transactions on Information Forensics and Security (TIFS), IEEE TCAD, IEEE Aero.
3. **ACM Digital Library:** ACM Transactions on Embedded Computing Systems (TECS), ACM CCS.
4. **SpringerLink:** Lecture Notes in Computer Science (LNCS) proceedings for EUROCRYPT, CRYPTO, ASIACRYPT, INDOCRYPT, CARDIS, COSADE.
5. **NIST Information Technology Laboratory:** Federal Information Processing Standards (FIPS 203, FIPS 204, FIPS 205, SP 800-series).
6. **Space Agencies:** NASA Technical Reports Server (NTRS), European Cooperation for Space Standardization (ECSS).

---

## 4. Search Strings & Query Formulations

The search queries executed across databases included:

| Query ID | Search String Formulation | Primary Target Area |
| :--- | :--- | :--- |
| **Q1** | `("Number Theoretic Transform" OR "NTT") AND ("fault detection" OR "invariant" OR "ABFT")` | Area A |
| **Q2** | `("Algebraic Invariant Checking" OR "AIC" OR "RENO" OR "RESWO") AND "NTT"` | Area A |
| **Q3** | `("ML-KEM" OR "Kyber") AND ("fault injection" OR "fault attack" OR "DFA")` | Area B |
| **Q4** | `("twiddle" OR "twiddle factor") AND ("fault" OR "corruption") AND ("NTT" OR "Kyber")` | Area B |
| **Q5** | `("Fujisaki-Okamoto" OR "FO transform") AND ("fault" OR "bypass" OR "implicit rejection")` | Area B |
| **Q6** | `("fault tolerant" OR "redundancy" OR "self-checking") AND ("ML-KEM" OR "Kyber" OR "Dilithium")` | Area C |
| **Q7** | `("Dual Modular Redundancy" OR "DMR") AND ("post-quantum" OR "ML-KEM") AND overhead` | Area C |
| **Q8** | `("single-event upset" OR "SEU") AND ("cryptography" OR "post-quantum" OR "spacecraft")` | Area D |
| **Q9** | `("software fault injection" OR "SWIFI") AND ("radiation" OR "space") AND limitations` | Area D |

---

## 5. Inclusion and Exclusion Criteria

To ensure high rigor, academic defensibility, and prevent the inclusion of unreliable or unverified sources, explicit criteria were applied:

### Inclusion Criteria:
1. **Peer-reviewed publication or formal standard:** Published in peer-reviewed conferences (e.g., CHES, IEEE S&P, CCS, INDOCRYPT), journals (e.g., IEEE TC, IEEE TNS, ACM TECS), or official standardization documents (NIST FIPS, ECSS, NASA standards).
2. **Direct technical relevance:** Must address fault injection, error detection, arithmetic transformations, post-quantum cryptography, or radiation effects in computing systems.
3. **Primary source availability:** Full text accessible and verifiable with complete bibliographic metadata (authors, year, venue, DOI or stable archival URL).
4. **Methodological transparency:** Clear specification of threat models, experimental setups, platforms, and mathematical formulations.

### Exclusion Criteria:
1. **Unverified preprints without citation stability:** Non-archival preprints lacking technical validation or peer review, unless foundational and universally cited in the cryptographic community (e.g., standard ePrint reports by recognized algorithm authors).
2. **Secondary summaries or blog posts:** Commercial marketing whitepapers, unsubstantiated vendor benchmarks, or high-level slide decks lacking formal proofs and experimental datasets.
3. **Generic fault tolerance unrelated to transforms or cryptography:** Redundancy papers on generic enterprise databases or network protocols with no relevance to modular arithmetic, NTT, or cryptographic state integrity.
4. **Fabricated or unconfirmed citations:** Any source whose bibliographic identity or technical claims could not be directly verified.

---

## 6. Synthesis & Analysis Workflow

Every retained paper was systematically analyzed according to:
1. **Threat Model:** Transient bit flips, single-event upsets, clock/voltage glitching, EM injection, stuck-at faults, or adversarial fault injection.
2. **Mathematical Target:** Modular reduction (Montgomery, Barrett), Cooley-Tukey butterfly, Gentleman-Sande butterfly, twiddle factor ROM/table, hash cores (Keccak/SHAKE), or control logic.
3. **Protection Level:** Algorithmic/mathematical invariants, temporal redundancy (recomputation), hardware spatial redundancy (DMR/TMR), parity/checksum trees, or constant-time masking.
4. **Resilience Outcome:** Error detection only (flag), safe fail-stop/abort, local autonomous recovery (rollback/recomputation), or implicit rejection.
5. **Evaluation Metric:** Overhead (latency percentage, gate count, slice count, memory footprint), undetected error probability ($P_{\text{undetected}}$), recovery rate ($R_{\text{recovery}}$).
