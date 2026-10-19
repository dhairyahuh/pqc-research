# Targeted Contribution Analysis and Prior Art Landscape

**Date:** October 2026  
**Subject:** Comparative Positioning of Software-Level Fault Resilience in ML-KEM-768  
**Scope:** NTT Invariant Monitoring, Common-Mode Blind Spots, Localized Rollback, and Outer FO Containment  

---

## 1. Taxonomic Review of Closest Prior Art

| Reference | Domain / Target | Mechanism | Capabilities | Documented Limitations | Relation to This Work |
|:---|:---|:---|:---|:---|:---|
| **Paul et al. (2026)**<br>*ACM TECS* [P03] | FPGA / Hardware NTT (PQC & FHE) | Algebraic invariant checking on Cooley-Tukey (CT) butterflies. | High detection probability ($>99.9\%$) in dedicated hardware pipeline registers. | Hardware-only; did not implement or evaluate Gentleman-Sande (GS) inverse invariants; no localized software rollback; no KEM protocol-level containment analysis. | **Closest arithmetic antecedent.** Established algebraic CT invariant on FPGA. We adapt this principle to software, introduce decoupled GS inverse checking, and implement localized rollback. |
| **Sarker et al. (2023)**<br>*IEEE TCAD* [P04] | HW/SW Co-Design NTT | Residue checking and parity prediction in hardware accelerators. | Low hardware overhead; concurrent error detection for polynomial multiplication. | Requires specialized ASIC/FPGA arithmetic units; inapplicable to pure C/C++ software deployments (e.g., COTS space avionics). | Demonstrates the need for pure software-level fault detection architectures on general-purpose processors without custom hardware extensions. |
| **Fritzmann et al. (2019)**<br>*DATE* [P13] | RISC-V Hardware Co-Processor | Redundant arithmetic and instruction-level fault detection for lattice crypto. | Detects control-flow and datapath faults on custom RISC-V extensions. | Requires hardware ISA modification; incurs substantial area overhead; lacks fine-grained single-butterfly rollback. | Reinforces the distinction between custom hardware co-processors and commodity C-level software implementations. |
| **Ravi et al. (2023)**<br>*TCHES* [P05] | NTT Software / Twiddle Tables | Fault injection attacks on twiddle factors ($\zeta$) during forward/inverse NTT. | Demonstrates that corrupting a single twiddle constant induces exploitable key-recovery equations. | Offensive attack study; did not design a software defense or rollback mechanism. | **Core motivation.** Demonstrates why twiddle tables are high-value targets. Crucially, our analysis proves that local butterfly invariants are completely blind to twiddle faults ($0.0\%$ detection), necessitating outer FO re-encryption as a failsafe. |
| **Hermelink et al. (2021)**<br>*INDOCRYPT* [P06] | Kyber Decapsulation | Fault-enabled chosen-ciphertext attacks exploiting decapsulation failures. | Demonstrates full key recovery if faulted decapsulation leaks plaintext or circumvents FO check. | Offensive attack analysis; did not provide defensive rollback. | Demonstrates that any fault resilience mechanism must guarantee strict FIPS 203 implicit rejection if recovery cannot be completed. |
| **Delvaux (2022)**<br>*TCHES* [P07] | Masked Kyber Decapsulation | Ineffective fault analysis (SIFA) on masked polynomial operations. | Bypasses masking countermeasures via statistical fault analysis. | Offensive attack analysis; focus on high-order DPA/FA combinations. | Informs our security boundary: localized retry is non-adversarial (SEU) resilience, not certified SIFA resistance. |
| **Reis et al. (2005)**<br>*CGO (SWIFT)* [P12] | General Software Fault Tolerance | Compiler-level instruction duplication (DMR) with majority voting. | Transparent fault tolerance on general-purpose software. | Incurs $>130\%$ to $160\%$ execution time slowdown; high register pressure; lacks domain-specific algebraic pruning. | Serves as our primary software baseline. We demonstrate that algebraic invariant monitoring achieves equal detection at $+16.9\%$ to $+25.3\%$ overhead vs $+135\%$ to $+149\%$ for SW DMR. |
| **Glabush et al. (2025)**<br>*CRYPTO* [P16] | Protocol-Level KEM | Verifiable decapsulation via zero-knowledge proofs / cryptographic commitments. | Proves decapsulation correctness to remote parties without leaking secret keys. | Massive computational overhead (orders of magnitude); designed for external verifiability rather than local micro-rollback. | Distinguishes our internal, microsecond-level localized rollback from external protocol-level verification proofs. |

---

## 2. Evaluation of Candidate Contributions

### Candidate 1: A Particular Combination of Forward (CT) and Inverse (GS) NTT Invariants
- **Prior Status:** Cooley-Tukey invariant ($r_0 + r_1 \equiv 2u \pmod q$) was formalized by Paul et al. (2026) for FPGA. Inverse Gentleman-Sande monitoring in pure software with decoupled add/mul checks is unaddressed in published software literature.
- **Evaluation:** **Defensible Novelty in Software Integration.** Adapting CT and deriving/implementing decoupled GS checking ($r_0 \equiv u + v$, $r_1 \equiv (v - u)\zeta$) without costly modular inversions in software is a genuine engineering and architectural contribution.

### Candidate 2: Characterization of Common-Mode Failures and Verifier Blindness
- **Prior Status:** Abstract common-mode failure is well known in fault-tolerant computing (Avizienis, Laprie). However, specific experimental proof of *circular verifier blindness* (where a fault checker consumes the already-corrupted live output rather than independent snapshots) had not been experimentally quantified for NTT butterflies.
- **Evaluation:** **Defensible Methodology Contribution.** Demonstrating that circular checkers suffer $94.0\%$ to $100.0\%$ false-pass rates under data-source corruption directly proves that register-level snapshot isolation is mandatory for invariant integrity. Furthermore, proving that *twiddle factor corruption* is undetectable by local arithmetic invariants ($0.0\%$ detection probability) rigorously establishes the architectural boundary between local monitoring and outer FO containment.

### Candidate 3: Bounded Localized Recovery and Measured Overhead Trade-offs
- **Prior Status:** Prior defensive works either abort immediately (zero availability) or restart the entire KEM decapsulation from scratch ($1.0\times$ KEM re-execution penalty per transient fault).
- **Evaluation:** **Primary Core Contribution.** Single-butterfly localized rollback restores live polynomial state in-place, incurring only a $1.0$-butterfly retry cost ($0.01\%$ execution delta per transient fault) instead of full-algorithm recomputation, while preserving $100\%$ valid key generation ($K_{\text{valid}}$) under transient SEUs.

### Candidate 4: Systematic Experimental Characterization of Fault Behavior in ML-KEM
- **Prior Status:** Prior experimental campaigns focus almost exclusively on key-recovery fault attacks (offensive) or simulation in high-level Python models.
- **Evaluation:** **Defensible Empirical Contribution.** End-to-end evaluation executing on compiled C production objects across 400 clean trials, 600 harness trials, and 2,000 benchmark runs, establishing an empirical upper bound of $1.26\%$ on SDC at $95\%$ confidence.

---

## 3. What is Demonstrably New vs. What is Not New

### What is Demonstrably New:
1. **First End-to-End Software Architecture Combining Dual CT/GS Invariants with Localized Rollback for ML-KEM-768:** Unifying 5,376 forward CT and 4,480 inverse GS monitored butterflies in a standard C implementation.
2. **Decoupled Software Invariant Equations for Inverse NTT:** Verifying Gentleman-Sande butterflies via pre-reduction adder and forward re-multiplication ($r_1 \equiv (v_{\text{saved}} - u_{\text{saved}})\zeta$), circumventing modular division in software.
3. **Empirical Quantitation of Single-Butterfly Rollback:** Demonstrating that 100/100 transient multiplier upsets are resolved in-place with exactly 1 retry, avoiding full decapsulation restart.
4. **Formal Separation of Local Arithmetic Invariants and Outer FO Containment:** Proving mathematically and empirically that twiddle factor corruption bypasses local invariants ($0\%$ detection) and relies entirely on downstream ciphertext re-encryption comparison (`mlk_ct_memcmp`) to force implicit rejection.
5. **Direct Performance Comparison against Software DMR:** Documenting that algebraic monitoring achieves equivalent single-fault coverage at $+16.9\%$ to $+25.3\%$ latency vs $+135\%$ to $+149\%$ for software duplication.

### What is NOT New:
1. The mathematical concept of the Cooley-Tukey sum invariant in $\mathbb{Z}_q$ (established on FPGA by Paul et al., 2026).
2. The Fujisaki-Okamoto transform and implicit rejection specification (standardized in FIPS 203 Section 7.3).
3. The general concept of rollback and retry in computing (established in classical fault-tolerant systems, e.g., Randell 1975, Reis et al. 2005).
4. Physical radiation hardness or beam-tested single-event upset cross-sections (not tested in this project).

---

## 4. Defensible, Narrow Contribution Statement

For inclusion in the paper's Introduction and Abstract:

> **Defensible Contribution:**  
> This paper presents the design, implementation, and empirical validation of a software-level fault-resilience architecture for ML-KEM-768 decapsulation. We demonstrate that:
> 1. Adapting Cooley-Tukey forward invariants and deriving decoupled Gentleman-Sande inverse invariants in software enables continuous monitoring of all $9{,}856$ decapsulation and re-encryption butterflies at a latency overhead of $+16.9\%$ to $+25.3\%$, compared to $+135\%$ to $+149\%$ for sequential software duplication.
> 2. Localized single-butterfly snapshotting and bounded rollback resolve $100\%$ of transient arithmetic faults in-place with a single retry, preserving full availability without restarting decapsulation.
> 3. Persistent arithmetic faults reliably trigger fail-stop escalation ($200/200$), zeroing intermediate state and enforcing FIPS 203 Section 7.3 implicit rejection with zero observed Silent Data Corruption across 300 active trials ($95\%$ Wilson score upper bound of $1.26\%$).
> 4. We formally establish the detection boundaries of algebraic invariants: while local monitors detect internal arithmetic faults, they are intrinsically blind to twiddle factor memory corruption ($0.0\%$ detection probability). We show that downstream Fujisaki-Okamoto re-encryption comparison acts as an indispensable outer failsafe, containing twiddle faults and preventing key leakage.
