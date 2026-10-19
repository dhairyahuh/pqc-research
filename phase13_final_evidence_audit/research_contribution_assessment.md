# Research Contribution Assessment & Scientific Evaluation

**Auditor:** Independent Cryptographic Implementation Auditor & Research Methodology Reviewer  
**Date:** October 2026  
**Scope:** Assessment of Scientific Novelty, Evidentiary Support, and Academic Significance  

---

## 1. Strongest Surviving Research Contribution

The primary, defensible research contribution established by this multi-phase study is:

> **Core Scientific Finding:**  
> In lattice-based key encapsulation mechanisms conforming to NIST FIPS 203, augmenting decapsulation with localized retry-and-verify arithmetic monitors introduces an architectural vulnerability: **local verifiers that rely on in-place snapshots of intermediate operands can suffer from severe verifier blindness ($93.5\%$, 95% Wilson CI: $[91.2\%, 95.2\%]$) when reference state is perturbed.**  
> However, this internal blindness **does not breach the end-to-end cryptographic boundary** ($H_2 = 0.0\%$, 95% Wilson CI: $[0.0\%, 0.28\%]$ across 1,300 trials). The outer Fujisaki-Okamoto re-encryption transform functions as an unconditional cryptographic firewall, reliably trapping corrupted decrypted messages and emitting the canonical FIPS 203 implicit rejection key ($K_{\text{bar}} = \text{SHAKE256}(z \parallel c, 32)$).

---

## 2. Assessment of Scientific Novelty

| Dimension | Asserted Claim (Pre-Audit) | Audited Reality (Post-Audit) | Academic Significance |
| :--- | :--- | :--- | :--- |
| **Verifier Blindness ($H_1$)** | Claimed as a zero-day exploit in production ML-KEM binaries. | Demonstrated strictly within specialized software harness models where snapshot variables were directly manipulated. | **Moderate-High:** Highlights a critical architectural pitfall in countermeasure design: *self-referential verifiers verify corrupted computations against corrupted references*. |
| **Silent Data Corruption ($H_2$)** | Hypothesized that verifier blindness enables physical key recovery. | **Refuted empirically across 1,300 trials.** FO re-encryption unconditionally trapped all arithmetic errors. | **High:** Establishes the robust defense-in-depth provided by the FIPS 203 FO loop against internal arithmetic faults. |
| **Production Monitor Resilience** | Claimed unconditional hardware immunity. | Demonstrated 100% genuine recovery under single transient butterfly bit-flips and 100% safe fail-stop under recurring bit-flips in compiled binaries. | **Moderate:** Demonstrates the efficacy of localized rollback for transient SEUs in embedded lattice pipelines. |
| **Implicit Rejection Conformance** | Assumed Phase 10 formula without proof. | Verified independently against NIST FIPS 203 using a clean-room Keccak engine; demonstrated that FIPS 203 absorbs raw ciphertext $c$ rather than $H(c)$. | **Moderate:** Provides cryptographic assurance of compliance with the final NIST FIPS 203 standard. |

---

## 3. Harness-Model Weakness vs. Production Binary Vulnerability

A critical methodological boundary must be maintained in academic framing:

1. **What Was Demonstrated in Software Models:**  
   When an in-place recovery verifier re-reads its reference operands from the same memory or stack frame that was subjected to corruption, the verification check cancels out algebraically:
   $$(u' - v' - 2t) \equiv 0$$
   This proves that **in-place verification without isolated hardware shadow registers is algorithmically flawed**.
2. **What Was NOT Demonstrated in Production Binaries:**  
   In compiled production code (`mlkem768_inst.o`), intermediate butterfly coefficients reside in CPU registers and temporary stack words. An external attacker cannot easily corrupt the snapshot without corrupting the active calculation. Furthermore, the in-tree production source code contains no API or hook that exposes snapshot buffers to external tampering.
3. **Framing Requirement:**  
   Authors must frame verifier blindness as a **cautionary design pattern for hardware/software co-designers**, rather than an exploit demonstrated against compiled `mlkem-native` binaries.

---

## 4. Value Added Beyond Standard ML-KEM Implicit Rejection

A skeptical reviewer might ask: *"Does this paper merely demonstrate that ML-KEM decapsulation performs implicit rejection when given corrupted ciphertexts?"*

The work adds concrete scientific value beyond that trivial observation:
1. **Cross-Layer Fault Dynamics:** It evaluates how internal arithmetic faults interact with outer protocol re-encryption checks.
2. **Failure Analysis of Local Retry Logic:** It provides empirical data showing that localized fault recovery can succeed for transient faults ($100/100$) while failing safely ($100/100$) under persistent faults without ever degrading protocol-level security.
3. **Statistical Decoupling of Subcomponent vs. API Invariants:** It formally models and separates internal monitor declarations ($H_1$) from external API shared-secret acceptance ($H_2$), providing a rigorous methodology for future PQC fault resilience studies.
