# Systematic Research Gap Assessment
**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Phase:** 7L — Independent Literature Review, Research Gap Validation, and Novelty Assessment  
**Date:** October 2026  
**Status:** Rigorous Academic Gap Validation  

---

## 1. Assessment Framework & Classification Taxonomy

To prevent unjustified claims of novelty, each candidate contribution of the project is evaluated against the established literature using five standardized academic classifications:

1. **Established Prior Art:** The concept, mathematical formulation, and operational mechanism have been published and experimentally demonstrated in prior literature.
2. **Known Technique Applied to a New Context:** The fundamental principle is established in an adjacent domain (e.g., hardware accelerators, digital signal processing, database systems) and is here adapted to software-level post-quantum cryptography.
3. **Incremental Implementation Contribution:** An engineering optimization or practical adaptation of existing methods that resolves concrete implementation bottlenecks without introducing new theoretical paradigms.
4. **Potentially Novel Contribution:** A distinctive formulation, architectural mechanism, or end-to-end integration that has not been previously published or demonstrated in peer-reviewed literature.
5. **Novelty Uncertain (Insufficient Literature Coverage):** A concept where preliminary evidence suggests distinction, but academic database indexing or source availability cannot definitively rule out overlapping concurrent work.

---

## 2. Evaluation of the Eight Candidate Contributions

### Candidate 1: Complementary Arithmetic Invariants for Forward and Inverse NTT Butterflies
* **Description:** Formulating and evaluating checking equations for Cooley-Tukey (CT) butterflies ($u' + v' \equiv 2u$, $u' - v' \equiv 2v\zeta$) and Gentleman-Sande (GS) butterflies ($u' \equiv u + v$, $v' \equiv \zeta(u - v) \pmod q$).
* **Classification:** **Known Technique Applied to a New Context (Forward CT)** / **Incremental Implementation Contribution (Inverse GS)**
* **Literature Evidence:**
  - *Forward CT:* The sum/difference invariant for Cooley-Tukey butterflies is algebraically analogous to classical Jou & Abraham (1988) FFT checksums and has been directly adapted to forward NTT FPGA accelerators by Paul et al. (ACM TECS 2024/2026) under Algebraic Invariant Checking (FR-AIC). It is therefore *not* theoretically novel for forward NTT.
  - *Inverse GS:* Prior works almost universally omit inverse NTT or assume it mirrors forward CT. Because $\zeta$ does not cancel out in the sum of outputs ($u' + v' = (u+v) + \zeta(u-v)$), the decoupled formulation ($u' = u+v$, $v' = \zeta(u-v)$) requires a recomputed difference check. While this is an algebraic consequence of the GS definition, its explicit implementation and validation in a unified dual-transform software system constitutes a solid incremental engineering contribution.

---

### Candidate 2: Mathematical Characterization of Invariant Error Kernels
* **Description:** Formalizing the undetected fault space as the algebraic kernel of the verification equations:
  $$\ker(\Delta_{\text{sum}}) = \{(\Delta u', \Delta v') \mid \Delta u' + \Delta v' \equiv 0 \pmod q\}$$
  $$\ker(\Delta_{\text{diff}}) = \{(\Delta u', \Delta v') \mid \Delta u' - \Delta v' \equiv 0 \pmod q\}$$
  yielding an undetected intersection only when $\Delta u' \equiv \Delta v' \equiv 0 \pmod q$ for single faults.
* **Classification:** **Established Prior Art (Linear Code / ABFT Theory)**
* **Literature Evidence:**
  - Characterizing the undetectable error space as the kernel of a parity check matrix or invariant operator is the foundational definition of linear error-detecting codes and ABFT (Huang & Abraham 1984, Jou & Abraham 1988).
  - While applying it to modular integer arithmetic modulo $q=3329$ provides mathematical clarity in the manuscript, claiming the mathematical concept of an "error kernel" as a novel contribution would be indefensible. It should be presented as standard analytical modeling.

---

### Candidate 3: Local Rollback and Recomputation in CPU Register State
* **Description:** Maintaining shadow copies of butterfly inputs in CPU registers, detecting transient faults immediately upon butterfly completion, restoring inputs from shadow registers, and re-executing the single butterfly in-place with zero heap allocations.
* **Classification:** **Potentially Novel Contribution (in Software PQC Context)**
* **Literature Evidence:**
  - In hardware literature (Paul et al., Sarker et al., Canto et al.), detected faults merely trigger an external error flag (detection only); hardware systems rely on global pipeline resets or instruction aborts.
  - In software systems, rollback is typically executed at coarse transaction boundaries (checkpointing entire functions or frames), incurring massive memory and cycle overhead.
  - Prior software PQC implementations (e.g., `pqm4`, reference C) rely exclusively on full-function re-execution (DMR). No prior software PQC study has published or benchmarked fine-grained, in-place register rollback at the butterfly level yielding 100% transient recovery with negligible memory footprint.

---

### Candidate 4: Integrated Monitoring Across Complete ML-KEM-768 Decapsulation
* **Description:** In-tree native instrumentation covering all 9,856 forward and inverse NTT butterflies across the vector NTT ($3 \times 896 = 2{,}688$), secret-key vector NTT ($3 \times 896 = 2{,}688$), and message-recovery inverse NTT ($4{,}480$) in compiled C.
* **Classification:** **Potentially Novel Contribution (as an Engineering Integration Study)**
* **Literature Evidence:**
  - Existing academic papers evaluate NTT fault tolerance in isolated testbenches (testing single polynomial multiplication or standalone NTT functions).
  - Attacks by Hermelink et al. (INDOCRYPT 2021) and Delvaux (TCHES 2022) prove that leaving any transform unmonitored compromises the entire decapsulation routine.
  - This project is the first known software implementation that demonstrates end-to-end, compiler-integrated coverage across the complete decapsulation transform path of standard NIST FIPS 203 ML-KEM-768.

---

### Candidate 5: Recovery and Safe Rejection as Separate Resilience Outcomes
* **Description:** A two-tier architectural model that distinguishes Tier 1 (autonomous transient recovery via local rollback) from Tier 2 (hardened fail-stop implicit rejection yielding $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$ under persistent or multi-stage disturbances).
* **Classification:** **Potentially Novel Contribution**
* **Literature Evidence:**
  - Prior fault-tolerance literature treats fault resilience as binary: either the system corrects the fault (masking/recovery) or it crashes/aborts.
  - In cryptographic standards (NIST FIPS 203 Section 7.3), aborting or returning error codes creates chosen-ciphertext side channels. However, blind re-encryption under corrupted NTT state can leak private key data.
  - Formulating autonomous recovery and FIPS 203 implicit rejection as a coordinated two-tier defense—and demonstrating that failed recovery deterministically defaults to safe implicit rejection even when callers discard error pointers—is a novel architectural bridge between fault tolerance and post-quantum standards.

---

### Candidate 6: Empirical Performance Comparison Against Software-Sequential DMR
* **Description:** Conducting rigorous cycle-accurate benchmarking comparing native dual-butterfly monitoring (+16.79% to +28.91% latency overhead) against software-sequential DMR (+140.3% to +160.8% latency overhead).
* **Classification:** **Incremental Implementation Contribution / Empirical Resilience Evaluation**
* **Literature Evidence:**
  - DMR is the canonical baseline in software fault tolerance. Comparing a new lightweight check against DMR is standard experimental practice.
  - The empirical findings are highly valuable: demonstrating a **5.2$\times$ to 8.1$\times$ reduction in overhead** relative to DMR in compiled software provides strong empirical evidence, but the comparison methodology itself is established prior art.

---

### Candidate 7: Fault-Model Limitations (Corrupted Twiddles, Checker Faults, Persistent SEUs)
* **Description:** Formalizing and empirically proving the structural boundaries of local invariant checking:
  1. *Corrupted Twiddle ROM:* A faulted $\zeta$ corrupts both the computation and the checker, rendering faults invisible.
  2. *Checker Faults:* Faults in the verification code cause false positives or undetected errors.
  3. *Persistent / Stuck-at Upsets:* Local rollback fails when register/memory cells remain corrupted across recomputation cycles.
* **Classification:** **Known Limitation Applied to this Architecture / Analytical Validation**
* **Literature Evidence:**
  - Twiddle factor attacks were comprehensively demonstrated by Ravi et al. (TCHES 2023).
  - Inherent limits of self-checking circuits under checker faults have been known since Carter & Schneider (1968).
  - Demonstrating these limitations with raw experimental data in the repository reflects rigorous scientific honesty, but the limitations themselves are known theoretical realities.

---

### Candidate 8: Implications of Software Fault Resilience for Space Systems
* **Description:** Evaluating how software-level butterfly monitoring and rollback mitigate Single-Event Upsets (SEUs) in COTS-based spacecraft on-board data handling (OBDH) without requiring radiation-hardened hardware.
* **Classification:** **Known Technique Applied to a New Context**
* **Literature Evidence:**
  - Space radiation physics (Dodd & Massengill 2003) and radiation hardness assurance standards (ECSS-Q-ST-60-15C, NASA-HDBK-4002A) are well-established.
  - Adapting software-implemented fault tolerance to space avionics is an active field of applied engineering. Positioned as an applied systems study for satellite communications, this contribution is valuable context, not foundational theory.

---

## 3. Summary Classification Matrix

| # | Candidate Contribution | Academic Classification | Novelty Status |
| :---: | :--- | :--- | :--- |
| **1** | Complementary Forward/Inverse Invariants | Known Technique Applied to New Context / Incremental | Incremental Formulation |
| **2** | Mathematical Error Kernel Characterization | Established Prior Art | Non-Novel (Standard Theory) |
| **3** | Local In-Place Register Rollback in Software | Potentially Novel Contribution | **Defensible Software Contribution** |
| **4** | End-to-End Decapsulation Transform Coverage | Potentially Novel Contribution | **Defensible Integration Contribution** |
| **5** | Two-Tier Recovery vs. Safe Implicit Rejection | Potentially Novel Contribution | **Defensible Architectural Contribution** |
| **6** | Empirical Benchmark vs. Software DMR | Incremental / Empirical Evaluation | Standard Experimental Benchmark |
| **7** | Twiddle & Checker Limitation Analysis | Known Limitation / Analytical Validation | Robust Experimental Boundary |
| **8** | Space-System Resilience Implications | Known Technique Applied to New Context | Applied Domain Context |
