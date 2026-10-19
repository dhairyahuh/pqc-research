# Phase 6: Limitations, Failure Modes, and Defensible Research Contribution

**Auditor:** Skeptical Cryptographic Implementation Researcher  
**Date:** October 2026  
**Artifact:** `phase6_verifier_falsification/limitations_and_research_contribution.md`

---

## 1. Explicit Answers to Core Research Questions

### Question 1: Is H1 reproduced, contradicted, or inconclusive?
**Answer: REPRODUCED AND PROVEN.**
Across multiple independent tests (`F1`, `F2`, `F6`, `F7`, `F9`, `F10`), corrupting saved operands or recovery snapshots caused the native butterfly recovery verifier to evaluate to `True` ($diff_{\text{retry}} == 0 \land sum_{\text{retry}} == 0$) and increment `recovered_count` while writing corrupted polynomial coefficients into memory. The rate of false recovery certification reached **98.0%** in isolated bit-flip trials (`F1`) and **100.0%** in snapshot glitch trials (`F2`). The verifier is fundamentally blind to errors in the operands it ingests because of algebraic cancellation.

### Question 2: Is H2 reproduced, contradicted, or inconclusive?
**Answer: CONTRADICTED FOR ISOLATED MONITOR/SNAPSHOT FAULTS IN DECAPSULATION.**
In 1,200 trials across all tested targets, **0 trials produced Silent Data Corruption (0.0% SDC)**. Even when the recovery verifier was completely blinded and certified false recovery, the complete ML-KEM decapsulation procedure safely rejected the corrupted cryptographic state. The outer Fujisaki-Okamoto (FO) transform re-encrypts the decrypted message ($c' = \text{Enc}(pk, m')$) and compares $c'$ with $ct$. Corrupted coefficients altered the decoded message, causing ciphertext mismatch and triggering implicit rejection ($K_{\text{rej}}$ output).

### Question 3: Does DSPC mitigate the demonstrated weakness under the tested models?
**Answer: YES UNDER SINGLE-BIT TRANSIENT MODELS; NO UNDER CORRELATED OR CONTROL-FLOW MODELS.**
- Under single-bit snapshot corruption (`F11`), DSPC achieved **100.0% safe fail-stop rejections** [96.3%, 100.0%].
- Under correlated 2-bit faults targeting both snapshot and checksum (`F9`), DSPC was bypassed in **100.0% of trials** due to affine linearity.
- Under control-flow instruction skips over the branch check (`F10`), DSPC was bypassed in **100.0% of trials**.

---

## 4. Remaining Residual Failure Modes

1. **Primitives Without Fujisaki-Okamoto Transforms:**
   The safety barrier that prevented H2 from becoming Silent Data Corruption is the FO re-encryption loop. Cryptographic primitives that lack an FO loop—such as **ML-KEM Key Encapsulation (`mlkem_enc`)** and **ML-DSA Signature Generation (`mldsa_sign`)**—possess no outer re-encryption check. In those algorithms, internal false recovery from snapshot corruption directly yields corrupted ciphertexts or faulty signatures vulnerable to Fault Exploitation Attacks (e.g. Boneh-DeMillo-Lipton style attacks).
2. **Retry Multiplier Blindness (`F7`):**
   The current butterfly verifier cannot detect multiplier faults that occur during the retry calculation itself, because both difference and sum invariants algebraically cancel when $t_{\text{retry}}$ is perturbed.
3. **Availability Denial of Service (`F5` & `F8`):**
   Glitches targeting the verifier's own inputs or arithmetic units cause false-positive fail-stop aborts on healthy computations, creating a permanent denial-of-service attack surface.

---

## 5. Scope and Limitations of Evidence

In accordance with rigorous academic integrity:
- **No Physical Hardware Equivalence:** All trials were conducted via software-level instrumentation hooks on a POSIX host system. Software bit-flips simulate Single-Event Upsets (SEUs) and clock glitches at the register/memory level, but do not model physical silicon parasitics, thermal effects, or electromagnetic spatial distribution.
- **No Claims of Constant-Time Immunity:** While the cryptographic core uses branchless constant-time conditional moves (`mlk_ct_cmov_zero`), this audit did not perform physical power analysis (DPA/CPA) or timing measurement under hardware side-channel leakage models.
- **No Space-System Flight Readiness:** True flight readiness requires hardware dual-core lockstep (DCLS) processors, ECC-hardened BRAM/registers, and space-qualified rad-hard silicon. Software recovery monitors provide secondary defense-in-depth, not primary rad-hard assurance.

---

## 6. The Smallest Defensible Research Contribution

> **The Defensible Contribution:**
> We have formally and empirically demonstrated that local invariant monitors based on input-dependent recomputation suffer from **Tautological Verifier Blindness**: they verify arithmetic consistency relative to supplied inputs, not semantic authenticity.
> We proved that while this weakness blinds internal recovery monitors in 98% of trials (H1), it does NOT translate into Silent Data Corruption in ML-KEM decapsulation due to the outer Fujisaki-Okamoto re-encryption barrier (refuting H2).
> Finally, we demonstrated that while a Dual-Snapshot Parity Checksum (DSPC) completely cures single-bit snapshot blindness at $O(1)$ overhead, it remains vulnerable to correlated 2-bit linear collisions, delineating the exact theoretical boundary where software-only fault tolerance ends and outer protocol verification or hardware redundancy must take over.
