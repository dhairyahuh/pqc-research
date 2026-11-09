# Research Glossary

- **SEU (Single-Event Upset):** A radiation-induced state change (bit flip) in memory cells or registers caused by ionizing radiation (cosmic rays, protons, heavy ions).
- **SET (Single-Event Transient):** A momentary voltage spike or glitch in combinational logic caused by an ionizing particle strike.
- **PQC (Post-Quantum Cryptography):** Cryptographic algorithms thought to be secure against both quantum and classical computers (e.g., lattice-based, hash-based, code-based).
- **ML-KEM (Module-Lattice Key Encapsulation Mechanism):** NIST FIPS 203 standard algorithm (derived from CRYSTALS-Kyber) for post-quantum public-key encryption and key encapsulation.
- **ML-DSA (Module-Lattice Digital Signature Algorithm):** NIST FIPS 204 standard algorithm (derived from CRYSTALS-Dilithium) for digital signatures.
- **NTT (Number Theoretic Transform):** A specialized discrete Fourier transform over a finite ring $\mathbb{Z}_q$, used for $O(n \log n)$ polynomial multiplication in lattice-based cryptography.
- **Twiddle Factors ($\zeta$ / `zetas`):** Precomputed powers of the primitive root of unity used during butterfly stages of the NTT.
- **Cooley-Tukey Butterfly:** An algorithm structure used in decimation-in-time NTT to combine smaller transforms into larger ones.
- **Implicit Rejection (FIPS 203 Section 7.3):** A mechanism in decapsulation where, upon detecting an invalid ciphertext or mismatched re-encryption, the decapsulation engine returns a pseudorandom shared key derived from a secret value rather than an explicit error code, preventing chosen-ciphertext attacks (IND-CCA2).
- **Circular Dependency Masking:** A vulnerability where a verifier uses the same corrupted parameters (e.g., twiddle factors) as the primary execution engine, causing the verifier to validate erroneous outputs as correct.
- **DMR (Dual Modular Redundancy):** Executing an algorithm or function twice and comparing outputs to detect transient faults, incurring $\approx 100\%$ runtime overhead.
- **TFIB (Twiddle Factor Integrity Binding):** Our proposed lightweight countermeasure that cryptographically binds and verifies NTT twiddle factor tables against immutable ROM digests before execution, providing microsecond self-healing with minimal overhead ($+2.08\%$).
- **SWaP-C:** Size, Weight, Power, and Cost constraints typical of aerospace and satellite embedded systems.

