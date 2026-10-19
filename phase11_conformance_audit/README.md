# Phase 11: ML-KEM Conformance and Independent Output Validation

**Auditor:** Skeptical Cryptographic Implementation Auditor  
**Date:** October 2026  
**Target:** ML-KEM-768 Native Implementation (`mlkem-native` commit `fc269bc2d106`)  
**Specification:** NIST FIPS 203 (Module-Lattice-Based Key-Encapsulation Mechanism Standard)  

---

## 1. Executive Summary

Phase 11 rigorously re-examines the cryptographic output checks and implicit-rejection derivations from Phase 10 against the authoritative NIST FIPS 203 standard and the compiled production objects.

### Core Discoveries:
1. **Implicit Rejection Formula Audit:**  
   The Phase 10 rejection key formula `SHAKE256(z || ct)` was audited and proven to be **strictly conformant** with NIST FIPS 203 Section 4.1 Eq. (4.4) and Algorithm 21 Line 7 ($K_{\text{bar}} \leftarrow J(z \parallel c)$). It correctly absorbs the full raw ciphertext $c$ (1,088 bytes) prepended by seed $z$ (32 bytes), totaling 1,120 bytes. This intentionally differs from CRYSTALS-Kyber Round 3, which hashed the ciphertext with SHA3-256 first ($KDF(z \parallel H(c))$, 64 bytes).
2. **Oracle Architectural Independence:**  
   Phase 10 called `mlkem768_shake256` from the production object under test, creating a circular verification loop. Phase 11 constructed a zero-dependency, clean-room Keccak-f[1600] / SHAKE256 engine in C, completely independent of `mlkem768_inst.o`, and verified bit-for-bit equivalence against NIST test vectors.
3. **Cryptographic Output Validation:**  
   - **Valid Ciphertexts ($N=100$):** 100/100 decapsulations matched the independently encapsulated secret byte-for-byte.
   - **Invalid Ciphertexts ($N=100$):** 100/100 controlled mutations (single-bit flips, byte XORs, zeroing, all-ones, modulus overflows) matched the clean-room oracle rejection key byte-for-byte with internal status `0xA5A5A5A5`.
   - **Fault Output Revalidation ($N=400$):** Re-tested Targets F12 (Clean Baseline), F4 (Transient Recovery), F5A (Recurring Bitflip Fail-Stop), and F5B (Stuck-At-Zero Fail-Stop) against the clean-room oracle. Confirmed 100% genuine recovery under transient faults and 100% safe fail-stop under persistent faults.
4. **Cumulative H1/H2 Reconciliation:**  
   Reconstructed cumulative trial totals across Phases 5 through 11. Clarified why clean controls ($N=100$) are excluded from the verifier blindness ($H_1$) denominator but included in the API-level Silent Data Corruption ($H_2$) denominator ($0 / 1,300$, 95% Wilson CI: $[0.0\%, 0.28\%]$).

---

## 2. Directory Artifact Inventory

All Phase 11 artifacts are preserved in this directory:

- [`README.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase11_conformance_audit/README.md): Comprehensive executive audit summary and index.
- [`source_derived_rejection_formula.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase11_conformance_audit/source_derived_rejection_formula.md): Static source-level trace of ciphertext re-encryption, comparison, fallback selection, and key derivation in `kem.c` and `symmetric.h`.
- [`fips203_conformance_check.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase11_conformance_audit/fips203_conformance_check.md): Algorithmic comparison against FIPS 203, KAT test results, and oracle validation report.
- [`independent_output_oracle.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase11_conformance_audit/independent_output_oracle.c): Standalone C source containing clean-room Keccak-f[1600] engine and the 3 validation campaigns.
- [`valid_ciphertext_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase11_conformance_audit/valid_ciphertext_trials.csv): Raw execution log of 100 valid ciphertext decapsulations.
- [`invalid_ciphertext_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase11_conformance_audit/invalid_ciphertext_trials.csv): Raw execution log of 100 controlled ciphertext mutation trials compared against clean-room oracle.
- [`fault_output_revalidation.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase11_conformance_audit/fault_output_revalidation.csv): Raw execution log of 400 production object fault trials (F12, F4, F5A, F5B) compared against clean-room oracle.
- [`h1_h2_dataset_reconciliation.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase11_conformance_audit/h1_h2_dataset_reconciliation.md): Exact raw-dataset reconstruction, denominator accounting, and Wilson confidence intervals across all phases.
- [`claim_evidence_matrix.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase11_conformance_audit/claim_evidence_matrix.md): Formal 6-tier classification of all technical claims.
- [`limitations_and_next_steps.md`](file:///Users/dhairyajain/Desktop/pqc%20research/phase11_conformance_audit/limitations_and_next_steps.md): Methodological boundaries, narrowest defensible claim, and pre-submission roadmap.

---

## 3. Build & Execution Traceability

### 3.1 Environment & Toolchain
- **Compiler:** Apple clang version 21.0.0 (`clang-2100.1.1.101`)
- **Target Architecture:** `arm64-apple-darwin27.0.0`
- **Compiler Flags:** `-O2 -Wall -Wextra -I.`

### 3.2 Production Object Files & Hashes
```text
bin/obj/mlkem768_inst.o:
SHA-256: 7adc428039c318eb0d71b3fc7e24da602010acf7df5e37183ccba5a22eaef65f

bin/obj/mlkem_fault_hooks.o:
SHA-256: e7a90d06019aeb9e3f8b656e19e719985c797c25f629cb987f9d97f83a5fd952
```

### 3.3 Exact Build & Run Command
```bash
clang -O2 -Wall -Wextra -I. \
  phase11_conformance_audit/independent_output_oracle.c \
  bin/obj/mlkem768_inst.o \
  bin/obj/mlkem_fault_hooks.o \
  -o phase11_conformance_audit/independent_output_oracle

./phase11_conformance_audit/independent_output_oracle
```

### 3.4 Deterministic Seed Generation
- **Valid Ciphertexts:** `srand(0x4D4C4B00 + t)` for $t \in [0, 99]$
- **Invalid Ciphertexts:** `srand(0x5A5A0000 + t)` for $t \in [0, 99]$
- **Fault Trials:** `srand(0x1337C0DE + t)` for $t \in [0, 99]$
