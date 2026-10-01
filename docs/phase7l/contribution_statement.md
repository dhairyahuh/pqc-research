# Defensible Contribution Statement & Research Problem Formulation
**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Phase:** 7L — Independent Literature Review, Research Gap Validation, and Novelty Assessment  
**Date:** October 2026  
**Status:** Defensible Manuscript Core  

---

## 1. Precise Research Problem

As the global cryptographic infrastructure transitions to post-quantum standards, spaceborne computing systems (e.g., LEO satellites, interplanetary probes, and CubeSat constellations) must execute lattice-based key encapsulation mechanisms—specifically NIST FIPS 203 (ML-KEM)—on embedded processors operating in harsh radiation environments.

In these environments, ionizing radiation routinely induces **Single-Event Upsets (SEUs)** in CPU registers and memory. Within the **Number Theoretic Transform (NTT)**, which constitutes over 50% of the computational burden in ML-KEM decapsulation, a single transient bit-flip propagates across 7 transform layers, resulting in silent polynomial corruption. Left unmitigated, such corruptions either cause cryptographic handshake failures (forcing costly communication timeouts in high-latency satellite links) or expose decapsulation oracles to catastrophic key-recovery fault attacks (Hermelink et al., INDOCRYPT 2021; Ravi et al., TCHES 2023).

Traditional software fault tolerance relies on **Dual Modular Redundancy (DMR)**, which incurs excessive overhead (+140% to +160% CPU cycle latency) and is strictly **fail-stop**—aborting execution upon error rather than recovering. Conversely, lightweight Algorithm-Based Fault Tolerance (ABFT) techniques have been developed almost exclusively for FPGA/ASIC hardware accelerators, focusing on forward NTT only and generating detection flags without autonomous recovery or integration with FIPS 203 implicit rejection rules.

---

## 2. Research Gap Supported by the Literature

The systematic literature review identifies four specific, unaddressed gaps in published research:

1. **Gap 1: Disconnect Between Transform Coverage and Decapsulation Security:**
   Prior research on NTT arithmetic checking (Paul et al., ACM TECS 2024; Sarker et al., 2022) focuses almost exclusively on the **forward Cooley-Tukey NTT**. In ML-KEM decapsulation, however, message recovery relies critically on the **inverse Gentleman-Sande NTT**. Unmonitored inverse transforms leave decapsulation completely vulnerable to chosen-ciphertext fault attacks.
2. **Gap 2: Absence of In-Place Software Rollback in PQC:**
   While hardware architectures can afford parallel recomputation units, software PQC implementations have had no fine-grained, in-place recovery mechanism. Software developers have been forced to choose between vulnerable unmonitored code and costly full-operation DMR.
3. **Gap 3: Tension Between Fault Resilience and Cryptographic Implicit Rejection:**
   Standard fault-tolerant designs return explicit error codes or abort upon detecting corruption. Under NIST FIPS 203 (Section 7.3), explicit error handling creates side-channel oracle vulnerabilities. No prior work integrates fine-grained transient error recovery with deterministic fail-stop implicit rejection ($K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$) in the decapsulation transform path.
4. **Gap 4: Lack of End-to-End Native Software Evaluation:**
   Prior ABFT NTT studies evaluated isolated polynomial multiplication functions in synthetic testbenches rather than fully integrated, compiler-optimized, end-to-end decapsulation implementations.

---

## 3. Central Research Question

> **Can native, in-place arithmetic invariant checking and register rollback across all forward and inverse NTT butterflies provide complete transient fault recovery and safe implicit rejection in ML-KEM-768 decapsulation, while significantly reducing latency overhead compared to software-sequential DMR?**

---

## 4. Research Objectives

1. **Objective 1 (Mathematical & Algorithmic Formulation):** Derive and formally analyze complementary arithmetic invariants for Cooley-Tukey and Gentleman-Sande butterflies, defining their error kernels and proving why decoupled checking is necessary for inverse NTT transforms.
2. **Objective 2 (Software Implementation & Integration):** Implement zero-heap native monitoring and in-place register rollback instrumenting all 9,856 butterflies of ML-KEM-768 decapsulation in compiled C, ensuring constant-time semantics and ABI stability.
3. **Objective 3 (Standard-Compliant Fail-Stop Hardening):** Architect a two-tier resilience mechanism linking successful transient rollback (Tier 1) to hardened FIPS 203 implicit rejection (Tier 2), ensuring that unrecovered or persistent faults cannot leak plaintext or secret keys even if callers discard status flags.
4. **Objective 4 (Empirical Validation & Benchmark):** Evaluate the system through extensive simulated fault injection across seven arithmetic fault classes and benchmark CPU cycle overhead against baseline unmonitored code and software-sequential DMR.

---

## 5. Concise List of Defensible Contributions

The defensible contributions of this research are:

1. **Dual-Transform Software Architecture:** The design and implementation of a unified native monitoring architecture in compiled C covering all **9,856 butterflies** (2,688 forward vector, 2,688 secret-key vector, and 4,480 inverse polynomial) in the complete ML-KEM-768 decapsulation path.
2. **In-Place Register Rollback Mechanism:** A zero-heap, register-resident shadow rollback technique that repairs transient arithmetic SEUs locally within the butterfly execution frame, yielding a **100% recovery rate** across seven tested transient fault classes over 1,400 clean-room trials.
3. **Standard-Hardened Two-Tier Resilience:** A formal resilience model aligning local arithmetic recovery with NIST FIPS 203 implicit rejection ($K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$), including public API fail-stop hardening that prevents secret leakage when status return values are ignored.
4. **Empirical Overhead Characterization:** A reproducible cycle-accurate evaluation demonstrating that native dual-butterfly monitoring requires **+16.79% to +28.91% latency overhead**, delivering a **5.2$\times$ to 8.1$\times$ overhead reduction** compared to software-sequential DMR (+140.3% to +160.8%).
5. **Rigorous Boundary and Blind-Spot Analysis:** An analytical and experimental characterization of common-mode failure modes, formally bounding the scheme against corrupted twiddle factor tables, checker logic upsets, and persistent multi-cycle disturbances.

---

## 6. Explicit Non-Contributions and Methodological Limitations

To maintain academic integrity, the following limitations are explicitly declared:

- **Not a New Mathematical Invariant:** The sum and difference butterfly equations are algebraic identities, not new mathematical discoveries.
- **Not Hardware Radiation Qualification:** Software-Implemented Fault Injection (SWIFI) evaluates architectural register upsets; it does not replace physical heavy-ion or proton cyclotron beam testing required for spacecraft hardware qualification under ECSS-Q-ST-60-15C.
- **Vulnerability to Corrupted Twiddle ROM:** The monitor cannot detect errors in static twiddle factor tables without auxiliary memory integrity protections (e.g., CRC or EDAC).
- **Single-Butterfly Fault Model:** The 100% recovery guarantee applies to isolated transient faults occurring within a single butterfly; multi-fault bursts corrupting both shadow registers and primary arithmetic simultaneously trigger safe fail-stop rejection rather than recovery.
