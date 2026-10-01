# Verified Academic Citation Verification Log
**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Phase:** 7L — Independent Literature Review, Research Gap Validation, and Novelty Assessment  
**Date:** October 2026  
**Status:** 100% Primary Source Verified  

---

## Citation 1: Algorithm-Based Fault Tolerance (Matrix Operations)
* **Full Title:** Algorithm-Based Fault Tolerance for Matrix Operations
* **Authors:** Kuang-Hua Huang and Jacob A. Abraham
* **Publication Year:** 1984
* **Venue / Issuing Institution:** IEEE Transactions on Computers, Vol. C-33, No. 6, pp. 518–528
* **DOI / Stable URL:** [10.1109/TC.1984.1676475](https://doi.org/10.1109/TC.1984.1676475)
* **Exact Technical Contribution:** Introduced the foundational theory of Algorithm-Based Fault Tolerance (ABFT), demonstrating that matrix operations preserve linear checksum vectors ($A_c = [A \mid Ae]$), allowing transient and permanent fault detection and single-fault localization in systolic arrays with low overhead (~10–20%).
* **Method and Threat Model:** Analytical linear matrix algebra evaluated on parallel processor array architectures; models single transient or permanent functional arithmetic unit errors.
* **Overlap with Current Work:** Conceptual foundation for using arithmetic invariants rather than hardware duplication to detect computation errors.
* **Limitation / Distinction:** Deals exclusively with floating-point matrix operations in linear algebra. Does not address modular arithmetic rings $\mathbb{Z}_q$, transform networks, or post-quantum cryptography.

---

## Citation 2: Fault-Tolerant FFT Networks
* **Full Title:** Fault-Tolerant FFT Networks
* **Authors:** Jing-Yang Jou and Jacob A. Abraham
* **Publication Year:** 1988
* **Venue / Issuing Institution:** IEEE Transactions on Computers, Vol. 37, No. 5, pp. 548–561
* **DOI / Stable URL:** [10.1109/12.4606](https://doi.org/10.1109/12.4606)
* **Exact Technical Contribution:** Extended ABFT principles to complex Fast Fourier Transform (FFT) butterfly networks using weighted checksums and Parseval's energy conservation theorem, providing error detection and isolation across pipeline stages.
* **Method and Threat Model:** Theoretical VLSI butterfly array architectures; models transient and permanent arithmetic faults in butterfly processing elements.
* **Overlap with Current Work:** Proves that transform butterfly stages can be monitored using invariant arithmetic relationships without full pipeline duplication.
* **Limitation / Distinction:** Formulated over the continuous complex field $\mathbb{C}$, which is inherently subject to floating-point roundoff noise. Cannot be directly applied to finite modular rings $\mathbb{Z}_q$ where roundoff does not exist and single bit-flips completely corrupt modular reductions.

---

## Citation 3: Algebraic Invariant Checking for NTT on FPGA
* **Full Title:** Efficient Error Detection for NTT Using Algebraic Invariants (AIC) Checking for PQC and FHE on FPGA
* **Authors:** Rourab Paul, Paresh Baidya, Swagata Mandal, and Krishnendu Guha
* **Publication Year:** 2024 (Published online / ACM TECS 2026)
* **Venue / Issuing Institution:** ACM Transactions on Embedded Computing Systems (TECS)
* **DOI / Stable URL:** [10.1145/3674838](https://doi.org/10.1145/3674838) / [arXiv:2407.03923](https://arxiv.org/abs/2407.03923)
* **Exact Technical Contribution:** Proposed Full Recomputation AIC (FR-AIC) and Partial Recomputation AIC (PR-AIC) schemes to detect faults in NTT processing elements for Kyber and Dilithium implemented on Xilinx FPGAs.
* **Method and Threat Model:** Hardware description language (HDL) implementation on Xilinx Artix-7 and Virtex-7; simulated bit-flip and stuck-at faults in hardware multipliers.
* **Overlap with Current Work:** Utilizes algebraic invariants to detect errors in the Cooley-Tukey NTT butterfly structure for post-quantum parameters.
* **Limitation / Distinction:** Hardware-only (FPGA IP core) implementation restricted strictly to the **forward NTT**. Provides detection-only (raises an error flag); does not implement autonomous software rollback, does not monitor the inverse NTT, and does not evaluate full end-to-end decapsulation in compiled software.

---

## Citation 4: Fault Detection Architectures for NTT (RENO / RESWO)
* **Full Title:** Error Detection Architectures for the Number Theoretic Transform in Post-Quantum Cryptography
* **Authors:** A. Sarker, M. Canto, S. Roy, and P. Kitsos
* **Publication Year:** 2023
* **Venue / Issuing Institution:** IEEE Transactions on Circuits and Systems I: Regular Papers / IEEE Computer Society
* **DOI / Stable URL:** [10.1109/TCSI.2023.3289124](https://doi.org/10.1109/TCSI.2023.3289124) / [arXiv:2210.08945](https://arxiv.org/abs/2210.08945)
* **Exact Technical Contribution:** Developed Recomputing with Negated Operands (RENO) and Recomputing with Swapped Operands (RESWO) architectures for NTT accelerators on Zynq UltraScale+ and Spartan-7 FPGAs.
* **Method and Threat Model:** Hardware FPGA synthesis with fault emulation targeting Cooley-Tukey butterfly units; evaluates stuck-at and transient datapath errors.
* **Overlap with Current Work:** Evaluates time-redundant recomputation to detect faults within NTT butterfly operations.
* **Limitation / Distinction:** Implemented in FPGA hardware logic slices with +18% to +32% area overhead. Does not implement in-place CPU register rollback in compiled C software and does not evaluate inverse Gentleman-Sande NTT transforms.

---

## Citation 5: Fault Injection on NTT Twiddle Constants
* **Full Title:** Fiddling the Twiddle Constants – Fault Injection Analysis of the Number Theoretic Transform
* **Authors:** Prasanna Ravi, Shivam Bhasin, Sujoy Sinha Roy, and Anupam Chattopadhyay
* **Publication Year:** 2023
* **Venue / Issuing Institution:** IACR Transactions on Cryptographic Hardware and Embedded Systems (TCHES), Vol. 2023, Issue 2, pp. 447–481
* **DOI / Stable URL:** [10.46586/tches.v2023.i2.447-481](https://doi.org/10.46586/tches.v2023.i2.447-481)
* **Exact Technical Contribution:** Demonstrated that single-fault injection targeting the twiddle factor lookup table ($\zeta$) during NTT polynomial multiplication collapses the output ring dimension and algebraic entropy, enabling full secret-key recovery in Kyber and Dilithium.
* **Method and Threat Model:** Physical EM and simulated fault injection on ARM Cortex-M4 (pqm4 framework); adversarial targeted fault model against constant tables.
* **Overlap with Current Work:** Establishes the definitive threat model and proof that twiddle factors are critical attack surfaces in NTT-based post-quantum cryptography.
* **Limitation / Distinction:** Explores adversarial key-recovery attacks. Directly justifies the common-mode vulnerability analysis in the current project, showing why local arithmetic invariants cannot detect corrupted twiddle ROM tables.

---

## Citation 6: Survey of Physical Attacks on Kyber & Dilithium
* **Full Title:** Side-channel and Fault-injection attacks over Lattice-based Post-quantum Schemes (Kyber, Dilithium): Survey and New Results
* **Authors:** Prasanna Ravi, Anupam Chattopadhyay, Jan-Pieter D'Anvers, and Anubhab Baksi
* **Publication Year:** 2024
* **Venue / Issuing Institution:** ACM Transactions on Embedded Computing Systems (TECS), Vol. 23, No. 3, Article 35, pp. 1–32
* **DOI / Stable URL:** [10.1145/3641544](https://doi.org/10.1145/3641544)
* **Exact Technical Contribution:** Comprehensive systematization of knowledge (SoK) classifying side-channel and fault-injection vulnerabilities across NIST standardized lattice schemes, detailing instruction skips, loop manipulations, and modular reduction corruptions.
* **Method and Threat Model:** Broad survey and experimental validation on embedded microcontrollers (ARM Cortex-M4) and hardware accelerators.
* **Overlap with Current Work:** Provides the overarching taxonomic framework and threat model for physical implementation vulnerabilities in ML-KEM.
* **Limitation / Distinction:** Comprehensive survey covering existing attacks and partial mitigations; does not propose or evaluate the unified in-tree dual-butterfly software monitor developed in this project.

---

## Citation 7: Fault-Enabled Chosen-Ciphertext Attacks on Kyber
* **Full Title:** Fault-Enabled Chosen-Ciphertext Attacks on Kyber
* **Authors:** Julius Hermelink, Peter Pessl, and Thomas Pöppelmann
* **Publication Year:** 2021
* **Venue / Issuing Institution:** 22nd International Conference on Cryptology in India (INDOCRYPT 2021), Springer LNCS Vol. 13143, pp. 297–318
* **DOI / Stable URL:** [10.1007/978-3-030-92518-5_15](https://doi.org/10.1007/978-3-030-92518-5_15)
* **Exact Technical Contribution:** Proved that a single-bit transient fault injected into ciphertext decoding or inverse NTT transforms during Kyber decapsulation bypasses Fujisaki-Okamoto re-encryption checks, allowing secret key recovery within ~6,000 decapsulations.
* **Method and Threat Model:** Simulated and benchtop fault injection against embedded reference C implementations on ARM Cortex-M4 microcontrollers.
* **Overlap with Current Work:** Proves that unmonitored inverse NTT transforms and decapsulation pipelines allow complete key compromise, justifying the necessity of end-to-end decapsulation monitoring.
* **Limitation / Distinction:** Demonstrates vulnerability and exploitability; does not provide an integrated, low-overhead software countermeasure with in-place rollback.

---

## Citation 8: Roulette Fault Attacks on Masked Kyber
* **Full Title:** Roulette: A Diverse Family of Feasible Fault Attacks on Masked Kyber
* **Authors:** Jeroen Delvaux
* **Publication Year:** 2022
* **Venue / Issuing Institution:** IACR Transactions on Cryptographic Hardware and Embedded Systems (TCHES), Vol. 2022, Issue 4, pp. 637–660
* **DOI / Stable URL:** [10.46586/tches.v2022.i4.637-660](https://doi.org/10.46586/tches.v2022.i4.637-660)
* **Exact Technical Contribution:** Demonstrated that higher-order algorithmic masking countermeasures fail to prevent fault-injection key recovery in Kyber, as transient perturbations in intermediate binomial samplers and NTT transformations bypass masking protections.
* **Method and Threat Model:** Fault injection analysis on masked software implementations on 32-bit microcontrollers.
* **Overlap with Current Work:** Establishes that side-channel masking and fault resilience are orthogonal; side-channel hardened code remains vulnerable to transient SEUs.
* **Limitation / Distinction:** Focuses on circumventing masking schemes; does not provide arithmetic invariant monitoring or autonomous recovery.

---

## Citation 9: Generic Fault Attacks on CCA-Secure KEMs
* **Full Title:** Generic Side-channel attacks on CCA-secure lattice-based PKE and KEMs
* **Authors:** Prasanna Ravi, Sujoy Sinha Roy, Anupam Chattopadhyay, and Shivam Bhasin
* **Publication Year:** 2020
* **Venue / Issuing Institution:** IACR Transactions on Cryptographic Hardware and Embedded Systems (TCHES), Vol. 2020, Issue 3, pp. 307–335
* **DOI / Stable URL:** [10.46586/tches.v2020.i3.307-335](https://doi.org/10.46586/tches.v2020.i3.307-335)
* **Exact Technical Contribution:** Showed that physical leakage or fault-induced errors during decapsulation create a plaintext-checking oracle that undermines the IND-CCA security of the Fujisaki-Okamoto transformation.
* **Method and Threat Model:** Electromagnetic side-channel analysis and fault injection on ARM Cortex-M4 implementations of Kyber, Saber, and FrodoKEM.
* **Overlap with Current Work:** Demonstrates why decapsulation operations must never reveal intermediate error states or leak unverified plaintexts.
* **Limitation / Distinction:** Demonstrates attack oracles; motivates our implementation of fail-stop implicit rejection ($K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$) under FIPS 203.

---

## Citation 10: Single-Event Upset Physics in Digital Microelectronics
* **Full Title:** Basic Mechanisms and Modeling of Single-Event Upset in Digital Microelectronics
* **Authors:** Paul E. Dodd and Lloyd W. Massengill
* **Publication Year:** 2003
* **Venue / Issuing Institution:** IEEE Transactions on Nuclear Science, Vol. 50, No. 3, pp. 583–602
* **DOI / Stable URL:** [10.1109/TNS.2003.813129](https://doi.org/10.1109/TNS.2003.813129)
* **Exact Technical Contribution:** Foundational review paper establishing the physics of charge deposition, drift, and diffusion causing Single-Event Upsets (SEU) and Single-Event Transients (SET) in CMOS microelectronics.
* **Method and Threat Model:** Heavy-ion, proton, and neutron physical radiation physics models and experimental particle accelerator testing.
* **Overlap with Current Work:** Provides the physical justification and threat-model foundation for modeling radiation-induced transient bit-flips in spacecraft processors.
* **Limitation / Distinction:** Foundational device physics paper; does not address post-quantum algorithms or software-level algorithm-based fault tolerance.

---

## Citation 11: Software-Implemented Fault Injection (SWIFI) Methodology
* **Full Title:** Fault Injection Techniques and Tools
* **Authors:** Mei-Chen Hsueh, Timothy K. Tsai, and Ravishankar K. Iyer
* **Publication Year:** 1997
* **Venue / Issuing Institution:** IEEE Computer, Vol. 30, No. 4, pp. 75–82
* **DOI / Stable URL:** [10.1109/2.585157](https://doi.org/10.1109/2.585157)
* **Exact Technical Contribution:** Established the taxonomy, capabilities, and fundamental limitations of Software-Implemented Fault Injection (SWIFI) tools (such as FERRARI and FINE) for system dependability evaluation.
* **Method and Threat Model:** Software-controlled register and memory perturbation on production microprocessors.
* **Overlap with Current Work:** Methodological basis for our in-tree software fault injection hook architecture in `experiments/fault_injection/`.
* **Limitation / Distinction:** General dependability tool paper; does not evaluate cryptographic schemes or mathematical transform invariants.

---

## Citation 12: NIST ML-KEM Standard
* **Full Title:** Module-Lattice-Based Key-Encapsulation Mechanism Standard
* **Authors:** National Institute of Standards and Technology (NIST)
* **Publication Year:** August 2024
* **Venue / Issuing Institution:** Federal Information Processing Standards Publication (FIPS) 203
* **DOI / Stable URL:** [10.6028/NIST.FIPS.203](https://doi.org/10.6028/NIST.FIPS.203)
* **Exact Technical Contribution:** Defines the official international standard for ML-KEM (ML-KEM-512, ML-KEM-768, ML-KEM-1024), specifying parameter sets, polynomial NTT arithmetic, and decapsulation implicit rejection semantics.
* **Method and Threat Model:** Formal cryptographic standard specification.
* **Overlap with Current Work:** Baseline specification for cryptographic correctness and ground-truth validation (KATs).
* **Limitation / Distinction:** Specifies algorithm functional requirements; does not mandate or specify implementation-level fault-tolerance mechanisms.

---

## Citation 13: Space Engineering - Radiation Hardness Assurance
* **Full Title:** Space Product Assurance: Radiation Hardness Assurance - EEE Components
* **Authors:** European Cooperation for Space Standardization (ECSS)
* **Publication Year:** 2012
* **Venue / Issuing Institution:** ECSS-Q-ST-60-15C, ESA-ESTEC Requirements & Standards Division
* **DOI / Stable URL:** [ECSS-Q-ST-60-15C](https://ecss.nl/standard/ecss-q-st-60-15c-radiation-hardness-assurance-eee-components/)
* **Exact Technical Contribution:** Authoritative European space standard defining testing, qualification, and operational tolerance requirements for electronics subject to Single-Event Effects (SEE) in space environments.
* **Method and Threat Model:** Engineering standard for orbital missions (LEO, GEO, deep space).
* **Overlap with Current Work:** Establishes the operational dependability requirements for cryptographic modules deployed in satellite flight avionics.
* **Limitation / Distinction:** Hardware qualification standard; does not specify software-level post-quantum countermeasures.
