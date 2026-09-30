# Authoritative References and Implementation Traceability Matrix

## 1. Primary Standards & Normative References

1. **[FIPS-203] National Institute of Standards and Technology (NIST)**  
   *Module-Lattice-Based Key-Encapsulation Mechanism Standard (ML-KEM)*  
   Federal Information Processing Standards Publication (FIPS) 203, August 13, 2024.  
   DOI: [10.6028/NIST.FIPS.203](https://doi.org/10.6028/NIST.FIPS.203)

2. **[FIPS-204] National Institute of Standards and Technology (NIST)**  
   *Module-Lattice-Based Digital Signature Standard (ML-DSA)*  
   Federal Information Processing Standards Publication (FIPS) 204, August 13, 2024.  
   DOI: [10.6028/NIST.FIPS.204](https://doi.org/10.6028/NIST.FIPS.204)

3. **[FIPS-205] National Institute of Standards and Technology (NIST)**  
   *Stateless Hash-Based Digital Signature Standard (SLH-DSA)*  
   Federal Information Processing Standards Publication (FIPS) 205, August 13, 2024.  
   DOI: [10.6028/NIST.FIPS.205](https://doi.org/10.6028/NIST.FIPS.205)

4. **[FIPS-202] National Institute of Standards and Technology (NIST)**  
   *SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions*  
   FIPS PUB 202, August 2015.  
   DOI: [10.6028/NIST.FIPS.202](https://doi.org/10.6028/NIST.FIPS.202)

5. **[ECSS-Q-ST-60-15C] European Cooperation for Space Standardization**  
   *Space Product Assurance: Radiation Hardness Assurance - EEE Components*  
   ECSS Secretariat, ESA-ESTEC, Noordwijk, Netherlands.

6. **[NASA-HDBK-4002A] National Aeronautics and Space Administration**  
   *Mitigating Single Event Effects, Hardware and Software Approaches*  
   NASA Technical Handbook, Washington, DC.

---

## 2. Implementation Decisions Traceability Matrix

| Component | Standard / Section | Source Reference | Design Decision | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| **KEM Engine** | FIPS 203 §6, §7 | `liboqs` 0.16.0 (`kem_ml_kem.c`) | Use audited C library via native dynamic binding | Prevents subtle cryptographic vulnerabilities while maintaining native execution speed. |
| **Signature Engine** | FIPS 204 §5, §6 | `liboqs` 0.16.0 (`sig_ml_dsa.c`) | Use Tier-1 FIPS 204 implementation | Adheres to context string parameters and strict infinity-norm rejection sampling. |
| **Cross-Verification** | FIPS 203 / 204 | OpenSSL 3.6.4 / 4.0.3 CLI & Provider | Dual-engine verification | Guarantees standards compliance and eliminates single-vendor implementation bias. |
| **Implicit Rejection** | FIPS 203 §7.3 | Algorithm 17 (ML-KEM.Decaps) | Explicitly evaluate SDC vs failure detection | Fundamental to assessing mission desynchronization risks in space downlinks. |
| **Rejection Sampling** | FIPS 204 §5.3 | Algorithm 7 (ML-DSA.Sign) | Instrument loop counter and norm checks | Critical vulnerability locus for SEFI and key leakage analysis. |
