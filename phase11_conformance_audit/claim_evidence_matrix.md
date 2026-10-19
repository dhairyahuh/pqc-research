# Formal Claim-Evidence Matrix and Epistemic Classification

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Scope:** Rigorous Classification of All Experimental Findings Across Phases 1–11  

---

## 1. Epistemic Classification Taxonomy

Every technical claim in this repository is classified under one of the following mutually exclusive tiers:
1. **Independently Validated Against FIPS 203:** Verified against the official NIST FIPS 203 standard, published KAT vectors, and a clean-room independent oracle implementation.
2. **Reproduced Against Production Execution:** Executed directly against the compiled production object files (`bin/obj/mlkem768_inst.o`, `bin/obj/mlkem_fault_hooks.o`) under native ABI calling conventions.
3. **Supported by Source Inspection:** Verified by line-by-line static audit of source files in `algorithms/source_ref/mlkem/src/`.
4. **Demonstrated Only in a Software Model:** Empirically observed only inside specialized harness simulation environments where intermediate variables or control flags were artificially perturbed.
5. **Not Reproduced:** Claimed in earlier project documentation or hypotheses but failed to occur during rigorous testing.
6. **Contradicted:** Directly refuted by empirical execution data or mathematical proof.
7. **Inconclusive:** Ambiguous, unrepeatable, or lacking sufficient statistical power to warrant a definitive conclusion.

---

## 2. Comprehensive Claim-Evidence Matrix

| # | Specific Technical Claim | Primary Evidence Source | Artifact / Trial Basis | Compiler & Build Flags | Exact Object / File Hashes | Epistemic Classification |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- |
| **C1** | **ML-KEM KeyGen, Encaps, and Decaps adhere strictly to NIST FIPS 203 specifications across all security levels.** | `tests/test_fips_kats.c`, `references/test_vectors/mlkem_expected_kat.h` | 9 official NIST CAVP vectors (ML-KEM-512, 768, 1024) | `clang -O3 -Wall -Wextra` | `mlkem768_kat.o`: `7dfd465e...`<br>`mlkem512.o`: `573d8e4b...`<br>`mlkem1024.o`: `73646d1e...` | **Independently Validated Against FIPS 203** |
| **C2** | **The expected implicit-rejection shared secret for ML-KEM-768 is exactly $K_{\text{bar}} = \text{SHAKE256}(z \parallel c, 32)$ ($1,120$ bytes input).** | FIPS 203 Eq. (4.4) & Alg. 21 Line 7; `independent_output_oracle.c` | 100 invalid ciphertext controlled mutation trials; clean-room Keccak | `clang -O2 -I.` | `independent_output_oracle`: clean-room Keccak engine | **Independently Validated Against FIPS 203** |
| **C3** | **FIPS 203 implicit rejection differs from CRYSTALS-Kyber Round 3 by absorbing the unhashed ciphertext $c$ rather than $H(c)$.** | `algorithms/source_ref/mlkem/src/kem.c:513-516`, `symmetric.h:35-36` | Source code audit of buffer concatenation and macro expansion | N/A (Static Source Inspection) | `kem.c` SHA-256: `918653ee...` | **Supported by Source Inspection** |
| **C4** | **In-tree native NTT monitor achieves 100% genuine recovery under single transient butterfly bit-flips (Target F4).** | `phase11_conformance_audit/fault_output_revalidation.csv` | 100 trials executed against production objects | `clang -O3 -fPIC -DMLKEM_RESEARCH_FAULT_HOOKS` | `mlkem768_inst.o`: `7adc4280...`<br>`mlkem_fault_hooks.o`: `e7a90d06...` | **Reproduced Against Production Execution** |
| **C5** | **In-tree native NTT monitor achieves 100% safe fail-stop under recurring bit-flips (F5A) and hardware stuck-at-0 (F5B).** | `phase11_conformance_audit/fault_output_revalidation.csv` | 200 trials executed against production objects | `clang -O3 -fPIC -DMLKEM_RESEARCH_FAULT_HOOKS` | `mlkem768_inst.o`: `7adc4280...`<br>`mlkem_fault_hooks.o`: `e7a90d06...` | **Reproduced Against Production Execution** |
| **C6** | **Dual-rail verification in decapsulation prevents single-locus predicate bypass of the FO comparison.** | `algorithms/source_ref/mlkem/src/kem.c:476-504` | Reverse comparison loop `fail_chk` and persistent count trap | `clang -O3` | `kem.c` lines 476–504 | **Supported by Source Inspection** |
| **C7** | **In-place snapshot recovery verifiers exhibit verifier blindness when reference snapshots are corrupted (Hypothesis $H_1$).** | `phase7_independent_claim_audit/derived_corrected_trial_results.csv` | 561 / 600 false recovery events across targets F1, F2, F3, F6, F9, F10 | Specialized harness simulation | `phase6_reproducer.c`, `phase7_verifier_oracle.c` | **Demonstrated Only in a Software Model** |
| **C8** | **Internal false recovery ($H_1$) leads to Silent Data Corruption / accepted invalid keys at the API boundary ($H_2$).** | Across all 1,300 evaluated trials (Phases 5–11) | 0 / 1,300 accepted invalid keys (95% CI: [0.0%, 0.28%]) | Both production and harness models | All production objects and harness models | **Contradicted** |
| **C9** | **The ML-KEM decapsulation implementation is unconditionally immune to arbitrary physical fault injection.** | Architectural analysis of FO comparison registers | Theoretical boundary audit | N/A | Protocol & Microarchitecture | **Contradicted** |

---

## 3. Epistemic Synthesis & Core Research Insight

1. **Strict Decoupling of $H_1$ and $H_2$:**  
   The empirical evidence definitively proves that $H_1$ (internal monitor blindness) does **not** imply $H_2$ (silent data corruption). The Fujisaki-Okamoto re-encryption check operates as an independent, downstream cryptographic firewall. Even when the internal NTT recovery verifier is completely compromised by snapshot corruption, the recomputed ciphertext $c'$ fails to match the received ciphertext $c$, triggering implicit rejection.
2. **Oracle Validity:**  
   By establishing an independent, clean-room Keccak oracle, Phase 11 confirms that every rejected decapsulation produces the mathematically correct FIPS 203 rejection key $K_{\text{bar}}$, refuting the possibility that the implementation fell back to uninitialized memory, constant zeroes, or a flawed legacy Kyber derivation.
