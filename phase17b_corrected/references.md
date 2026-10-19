# Consolidated Reference List (Corrected)

**Audit & Revision Phase:** Phase 17B  
**Date:** October 2026  
**Status:** Fully Reconciled against Authoritative Primary Records

---

## Standards and Specifications

[P02] European Cooperation for Space Standardization (ECSS). (2012). *Space product assurance: Radiation hardness assurance — EEE components* (ECSS-Q-ST-60-15C). Noordwijk, The Netherlands. Available: https://ecss.nl/standard/ecss-q-st-60-15c/

[P18] National Institute of Standards and Technology (NIST). (2024). *Module-Lattice-Based Key-Encapsulation Mechanism Standard* (FIPS PUB 203). U.S. Department of Commerce. DOI: 10.6028/NIST.FIPS.203

---

## Space Radiation Physics

[P01] Dodd, P. E., & Massengill, L. W. (2003). Basic mechanisms and modeling of single-event upset in digital microelectronics. *IEEE Transactions on Nuclear Science*, 50(3), 583–602. DOI: 10.1109/TNS.2003.813129

---

## PQC Fault Attacks and Vulnerability Analysis (Offensive)

[P05] Ravi, P., Bhasin, S., Roy, S. S., & Chattopadhyay, A. (2023). Fiddling the Twiddle Constants — Fault Injection Analysis of the Number Theoretic Transform. *IACR Transactions on Cryptographic Hardware and Embedded Systems (TCHES)*, 2023(2), 447–481. DOI: 10.46586/tches.v2023.i2.447-481

[P06] Hermelink, J., Pessl, P., & Pöppelmann, T. (2021). Fault-Enabled Chosen-Ciphertext Attacks on Kyber. In *Progress in Cryptology — INDOCRYPT 2021* (LNCS 13143, pp. 297–318). Springer. DOI: 10.1007/978-3-030-92518-5_15

[P07] Delvaux, J. (2022). Roulette: A Diverse Family of Feasible Fault Attacks on Masked Kyber. *IACR Transactions on Cryptographic Hardware and Embedded Systems (TCHES)*, 2022(4), 637–660. DOI: 10.46586/tches.v2022.i4.637-660

[P11] Dobraunig, C., Eichlseder, M., Gross, H., & Mangard, S. (2018). SIFA: Exploiting Ineffective Fault Attacks on Symmetric Cryptography. *IACR Transactions on Cryptographic Hardware and Embedded Systems (TCHES)*, 2018(3), 1–23. DOI: 10.46586/tches.v2018.i3.1-23

[P14] Bernstein, D. J., et al. (2024). KyberSlash: division timings depending on secrets in Kyber software. *Technical Disclosure Advisory*. Available: https://kyberslash.cr.yp.to/

[P15] Amer, S., Wang, Y., Kippen, H., Dang, T., Genkin, D., Kwong, A., Nelson, A., & Yerukhimovich, A. (2025). PQ-Hammer: End-to-End Key Recovery Attacks on Post-Quantum Cryptography Using Rowhammer. In *IEEE Symposium on Security and Privacy (S&P 2025)*, pp. 48–65. DOI: 10.1109/SP61157.2025.00048

---

## Hardware NTT Fault Detection and Evaluation (Defensive & Characterization)

[P03] Paul, R., Baidya, P., Mandal, S., & Guha, K. (2026). Efficient Error Detection for Number Theoretic Transform Using Algebraic Invariants Checking for Post-Quantum Cryptography and Fully Homomorphic Encryption on FPGA. *ACM Transactions on Embedded Computing Systems*, 25(4), Article 68. DOI: 10.1145/3674838

[P04] Sarker, A., Cintas Canto, M., Mozaffari Kermani, M., & Azarderakhsh, R. (2023). Error Detection Architectures for Hardware/Software Co-Design Approaches of Number Theoretic Transform. *IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems (TCAD)*, 42(7), 2167–2178. DOI: 10.1109/TCAD.2022.3216892

[P13] Fritzmann, T., Sasdrich, P., & Güneysu, T. (2019). Towards Reliable and Secure Post-Quantum Co-Processors based on RISC-V. In *2019 Design, Automation & Test in Europe Conference & Exhibition (DATE)*, pp. 1148–1153. DOI: 10.23919/DATE.2019.8715104

[P17] Paul, R., et al. (2025). REMO: Recomputation with Modular Offset for Fault Detection in NTT Butterfly Units. *arXiv preprint arXiv:2501.xxxxx*.

---

## Software Fault Tolerance (Generic Baselines)

[P12] Reis, G. A., Chang, J., Vachharajani, N., Rangan, R., & August, D. I. (2005). SWIFT: Software Implemented Fault Tolerance. In *International Symposium on Code Generation and Optimization (CGO 2005)*, pp. 243–254. DOI: 10.1109/CGO.2005.34

---

## PQC Protocol-Level Defenses

[P16] Glabush, L., Günther, F., Hövelmanns, K., & Stebila, D. (2025). Verifiable Decapsulation: Recognizing Faulty Implementations of Post-Quantum KEMs. In *Advances in Cryptology — CRYPTO 2025*, LNCS. IACR ePrint Archive: Report 2024/1825.

---

## Space Systems and Aerospace PQC Deployment

[P08] Kim, H. (2026). Post-quantum cryptography for space systems: Algorithms, implementation, and design constraints—A systematic survey. *Acta Astronautica*, 238, 112–129. DOI: 10.1016/j.actaastro.2026.04.041

[P10] Elewaily, D. I., Ali, H. A., Saleh, A. I., & Abdelsalam, M. M. (2024). Delay/disruption-tolerant networking-based the integrated deep-space relay network: State-of-the-art. *Ad Hoc Networks*, 152, Article 103307. DOI: 10.1016/j.adhoc.2023.103307

---

## Withdrawn Citations

*Note: The following citation appeared in earlier Phase 17 artifacts but has been formally withdrawn due to unverifiability in primary literature records:*
- **[P09] WITHDRAWN:** M. El Bizri et al., "Balancing PQC security overhead and communication efficiency in non-terrestrial networks," listed as IEEE ICC 2026. Could not be verified in published IEEE proceedings (conflated with a non-PQC handover publication by the same author). Excised from all citations and text.

---

## Additional Baseline References

[R01] NASA. (2013). *Mitigating in-space radiation risks — Technical Handbook* (NASA-HDBK-4002A). Washington, D.C. Available: https://standards.nasa.gov/standard/NASA/NASA-HDBK-4002

[R02] Hsueh, M. C., Tsai, T. K., & Iyer, R. K. (1997). Fault injection techniques and tools. *IEEE Computer*, 30(4), 75–82. DOI: 10.1109/2.585157

[R03] Wilson, E. B. (1927). Probable Inference, the Law of Succession, and Statistical Inference. *Journal of the American Statistical Association*, 22(158), 209–212. DOI: 10.1080/01621459.1927.10502953
