# Phase 4 — Research Contribution & Novelty Review

**Project Title:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Standards:** NIST FIPS 203 (ML-KEM) & NIST FIPS 204 (ML-DSA)  
**Document Version:** 1.0.0-NOVELTY-REVIEW  
**Date:** October 1, 2026  
**Status:** COMPLETE & INDEPENDENTLY AUDITED  

---

## 1. Executive Summary

Phase 4 revisits the Phase 0 State-of-the-Art and Research Gap Analysis ([`docs/state_of_art_gap_analysis.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/state_of_art_gap_analysis.md)) and Novelty Risk Table ([`docs/novelty_risk_table.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/novelty_risk_table.md)) in light of the concrete empirical findings from Phases 1, 2, 3, and 4.

The purpose of this review is to maintain strict academic honesty:
- **Disentangle genuine research contributions from known literature phenomena.**
- **Downgrade or remove claims** that overgeneralized experimental artifacts.
- **Formally categorize** every aspect of the project into:
  1. *Fully Supported Novel Research Contributions*
  2. *Established in Prior Literature (Confirmatory / Independent Replication)*
  3. *Valuable Software Engineering & Infrastructure Contributions*
  4. *Hypotheses Requiring Further Formal or Physical Experimentation*
  5. *Claims Removed or Formally Narrowed*

---

## 2. Comprehensive Contribution Breakdown

### 2.1 Fully Supported Novel Research Contributions
These findings represent original scientific contributions that advance the state of the art in post-quantum cryptographic fault resilience:

1. **Analytical & Empirical Characterization of Dynamic Quantization Margin Absorption:**
   - *Status:* **GENUINELY NOVEL.**
   - *Prior Literature:* Earlier works assumed either zero fault tolerance in PQC or treated compression as an unanalyzed black box.
   - *Our Contribution:* Proved the Dynamic Quantization Tolerance Theorem ($T_{\text{worst}} = 0$ in real numbers, $1$ in discrete integers) and demonstrated that while single coefficients absorb small perturbations with high empirical probability ($99.5\%$ at $d=4$, $69.2\%$ at $d=10$), the joint probability across a diffused multi-coefficient error vector decays exponentially ($P_{\text{joint}} \approx P_{\text{single}}^W \to 0$).
2. **Exact Algebraic Bounding of Decapsulation Decoding Slack ($|\Delta| \le 12$):**
   - *Status:* **NOVEL REFINEMENT.**
   - *Prior Literature:* The $q/4$ decoding threshold is standard in LWE theory, but its interaction with implementation-level butterfly arithmetic was uncharacterized.
   - *Our Contribution:* Formally bounded the exact implementation-level threshold ($|\Delta| \le 12$) for NTT Layer 1 single register perturbations in ML-KEM-768 decapsulation, showing precisely why smaller faults are masked while larger faults trigger implicit rejection.
3. **Cross-Algorithm NTT Diffusion Duality ($2^{8-L}$ vs. $2^{9-L}$):**
   - *Status:* **NOVEL COMPARATIVE FORMALIZATION.**
   - *Prior Literature:* Butterfly structures are textbook signal processing; however, the cross-algorithm structural comparison between ML-KEM's incomplete 7-layer NTT and ML-DSA's complete 8-layer NTT had not been systematically unified into a single predictive fault diffusion framework.
4. **End-to-End Cryptographic-to-Protocol Failure Mapping for Space Systems:**
   - *Status:* **NOVEL DOMAIN APPLICATION.**
   - *Prior Literature:* PQC fault attacks focus almost exclusively on mathematical key recovery in smart cards. Space systems literature focuses on SEUs in memory without considering PQC algorithms.
   - *Our Contribution:* Successfully bridged the gap by mapping cryptographic outcome states (implicit rejection, candidate key mismatch, attempt budget exhaustion) to multi-stage spacecraft telecommand parsing and autonomous retransmission handshakes.

---

### 2.2 Established in Prior Literature (Independent Confirmatory Replication)
These aspects of our work replicate phenomena already documented in academic literature, serving as independent scientific validation:

1. **Fujisaki-Okamoto Equality Predicate Inversion:**
   - *Prior Literature:* Ravi et al. (CHES 2019, TCHES 2020), Pessl et al. (Crypto 2017) demonstrated that bypassing ciphertext comparison in post-quantum KEMs disrupts CCA security.
   - *Our Work:* Independently replicated on `mlkem-native` (C90), verifying that Case B2 produces candidate key mismatch (`CANDIDATE_KEY_MISMATCH`) and silent session desynchronization.
2. **ML-DSA Norm Check and Verification Bypass:**
   - *Prior Literature:* Bindel et al. (TCHES 2018), Ravi et al. (CHES 2021) demonstrated fault attacks on Dilithium/ML-DSA rejection sampling and verification gates.
   - *Our Work:* Independently verified that inverting the constant-time comparison flag (`cmp = 0`) in native C software results in 100% acceptance of invalid signatures.
3. **Serialized Secret-Key Component Sensitivity:**
   - *Prior Literature:* Memory fault attacks on private seed buffers and vector arrays are well-known in embedded security.
   - *Our Work:* Validated the concrete memory layout decomposition ($s, pk, H(pk), z$ in ML-KEM; $\mathbf{s}_1, \mathbf{s}_2, \rho, tr, K$ in ML-DSA) on modern reference C codebases.

---

### 2.3 Software Engineering & Infrastructure Contributions
These items represent high-quality research infrastructure rather than theoretical cryptographic breakthroughs:

1. **Unified Dual-Path Multi-Level Test Harness:**
   - Modular C harness executing all 6 FIPS 203 & FIPS 204 parameter sets (ML-KEM-512/768/1024 and ML-DSA-44/65/87) with bit-exact KAT validation against `liboqs 0.16.0`.
2. **Non-Invasive C Fault Injection Hook Subsystem:**
   - Precision hooks embedded at real internal computational loci (`mlk_ntt_butterfly_block`, `mld_ntt_butterfly_block`, accumulators, norm checks, and decision predicates) introducing zero functional overhead when inactive.
3. **Reproducible Automated Campaign Pipeline:**
   - Parameter-driven YAML orchestrator executing $>230,000$ trials across 239 configurations with deterministic PRNG seeding and automated Wilson confidence interval calculation.
4. **Abstract Spacecraft Communication Receiver:**
   - Multi-stage telecommand receiver simulation featuring magic byte synchronization, sequence window tracking, opcode parsing, semantic payload validation, and autonomous handshake recovery.

---

### 2.4 Hypotheses Requiring Further Experimentation
These questions remain open and are assigned to future research phases:

1. **Multi-Bit / Multi-Location Simultaneous Transients:**
   - Phase 2 and Phase 3 focused primarily on single-event upsets per operation. Multi-cell upsets (MCUs) striking adjacent coefficients simultaneously require further combinatorial investigation.
2. **Formal Verification of Assertion Invariants (Phase 6):**
   - Symbolic execution (SMT/Z3) and bounded model checking (CBMC) of the proposed software-only resilience assertions to formally prove complete single-fault coverage.
3. **Physical Microcontroller Glitching (Future Hardware Work):**
   - Validating whether physical electromagnetic pulses (EMP) or voltage drop transients on ARM Cortex-M4 / RISC-V physical silicon replicate the exact software-simulated injection behaviors.

---

### 2.5 Claims Formally Removed or Narrowed

| Original Informal Claim | Audit Action | Scientific Rationale | Corrected Formulation |
|:---|:---:|:---|:---|
| *"Decapsulation NTT Layer 1 faults are unconditionally masked by $q/4$ decoding slack."* | **NARROWED** | Peak error scales linearly with fault magnitude. Faults with $|\Delta| \ge 13$ exceed the slack budget ($832.25$) and flip message bits. | *Layer 1 single register faults are masked if and only if $|\Delta| \le 12$.* |
| *"ML-DSA verification decision bypass represents a successful signature forgery attack."* | **CORRECTED** | The underlying cryptographic equation is not satisfied; it represents a software execution / Boolean variable override. | *Bypassing the verification gate demonstrates a software execution-integrity vulnerability, not a mathematical cryptographic forgery.* |
| *"Rejection sampling acts as a complete privacy firewall against secret key extraction."* | **NARROWED** | If the norm check itself is bypassed, out-of-bounds signatures emitted onto the wire leak private key information to lattice analysis. | *Rejection sampling contains arithmetic faults under nominal control flow, but norm check bypasses create potential side-channel leakage.* |
| *"The software demonstrates fault resilience for space flight qualification."* | **REMOVED** | Software simulation on host CPUs cannot assess physical radiation hardness, latchup, or TID. | *All space-system conclusions represent abstract protocol simulations and do not claim physical flight qualification.* |

---

## 3. Summary of Research Standing

With the completion of Phase 4, the project has transitioned from preliminary exploratory experiments to a **scientifically defensible, peer-review-grade research body**. 

By explicitly acknowledging prior literature, bounding our novel mathematical derivations, and correcting earlier overstatements, the research is now on solid ground to proceed to subsequent comparative and resilience engineering phases.
