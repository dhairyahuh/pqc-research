# Phase 14 Final Audit Verdict and Evidence Certification

**Auditor:** Skeptical Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Subject:** Final Certification of ML-KEM-768 Fault Resilience Evidence  
**Status:** Complete Independent Audit and Raw-Data Reconciliation  

---

## 1. Executive Determination

This audit conducted a comprehensive, skeptical verification of the ML-KEM-768 fault-resilience research repository, auditing all underlying CSV datasets, compiler artifacts, C harnesses, and summary matrices. 

The investigation conclusively proved that **Phase 13 did not perform an independent recalculation from raw experimental records**, but rather propagated hardcoded integers derived from historical Phase 8 narrative tables. These historical tables contained severe errors, including misreporting Target F3 as 100% false recovery (raw CSV: 0%) and Target F7 as 0% false recovery (raw CSV: 94%). Furthermore, Phase 13's formal $H_2$ Boolean classification rule was mathematically defective, classifying safe fail-stop aborts as Silent Data Corruption.

Through dynamic raw-data recalculation, rigorous operational redefinition, synthetic classification unit tests, and production object verification, Phase 14 has established the first untainted, auditable baseline for this codebase.

---

## 2. Answers to Mandatory Audit Inquiries

### Question 1: Which Phase 13 numerical results survive raw-data recalculation?
The following results survive because they were verified against raw CSV records or freshly compiled production binaries:
1. **Production Object Recovery and Fail-Stop (Targets F12, F4, F5A, F5B):**
   - Target F12: $100/100$ Clean Success ($100.0\%$, 95% CI: $[96.3\%, 100.0\%]$).
   - Target F4: $100/100$ Genuine Recovery under transient butterfly bitflips ($100.0\%$, 95% CI: $[96.3\%, 100.0\%]$).
   - Target F5A: $100/100$ Safe Fail-Stop under recurring bit-inversions ($100.0\%$, 95% CI: $[96.3\%, 100.0\%]$).
   - Target F5B: $100/100$ Safe Fail-Stop under software force-value faults ($100.0\%$, 95% CI: $[96.3\%, 100.0\%]$).
2. **Absence of Silent Data Corruption ($H_2$):**
   - $0/400$ SDC events observed on production binary decapsulation (95% CI: $[0.0\%, 0.95\%]$).
3. **FIPS 203 Rejection Key Conformance:**
   - $100/100$ exact bit-for-bit matches against clean-room Keccak oracle for $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$.
4. **Harness Model False Recovery for Targets F1, F8, F10, F11:**
   - Target F1 (Saved Operand Bitflip): $98/100$ ($98.0\%$).
   - Target F8 (Verifier Operand Corrupt): $0/100$ ($0.0\%$, safe rejection).
   - Target F10 (DSPC State Bypass): $100/100$ ($100.0\%$).
   - Target F11 (DSPC Single-Bit Flip): $0/100$ ($0.0\%$, safe rejection).

---

### Question 2: Which results must be withdrawn or qualified?
1. **Withdrawn Results:**
   - **Target F3 (Persistent Count Zeroing):** Reported as $100/100$ false recovery ($100.0\%$). **WITHDRAWN**. Raw data proves the verifier rejected all trials ($0/100$, $0.0\%$). The 100% figure was a narrative fabrication.
   - **Target F7 (Retry Arithmetic Glitch):** Reported as $0/100$ ($0.0\%$, safe fail-stop). **WITHDRAWN**. Raw data shows $94/100$ ($94.0\%$) verifier false passes.
   - **Phase 13 Global Pooled $H_1$ Rate ($93.5\%$, 561/600):** **WITHDRAWN**. It pooled non-comparable fault models using corrupted numbers (including the fabricated 100 for F3 and miscalculated 70 for F2).
   - **All Constant-Time Certifications:** **WITHDRAWN**. No timing leakage tests (`dudect` or TVLA) were performed.
   - **All Physical Hardware and Radiation Hardness Claims:** **WITHDRAWN**. Software debug hooks cannot model physical silicon glitch dynamics.
   - **"Unconditional Cryptographic Firewall" Rhetoric:** **WITHDRAWN**. Physical instruction skipping bypasses the FO comparison loop entirely.
2. **Qualified Results:**
   - **Target F2 (Snapshot Pre-Retry Diffusion):** Reported as $70.0\%$ in Phase 13. Must be **QUALIFIED and CORRECTED to $100.0\%$ ($100/100$)** for local verifier blindness. The 70 count was downstream FO rejections, not verifier blindness.
   - **Target F6 (Verifier Flag Forced Pass):** Corrected from $100.0\%$ to $99.0\%$ ($99/100$).
   - **Target F9 (DSPC Multi-Bit Collision):** Corrected from $93.0\%$ to $100.0\%$ ($100/100$).
   - **Target F5B:** Must be strictly qualified as a **software force-value fault model**, not physical stuck-at-zero silicon behavior.

---

### Question 3: Whether $H_1$ is genuinely demonstrated in the stated models?
**YES, but strictly as an architectural pitfall within software simulation models.**

The evidence proves that when an internal recovery monitor uses in-place, unauthenticated snapshot memory, corrupting the snapshot or the verifier state induces **circular verifier blindness**: the verifier evaluates corrupted outputs against its own corrupted baseline and declares success. This occurred in $98\%$ (F1), $100\%$ (F2), $99\%$ (F6), $94\%$ (F7), $100\%$ (F9), and $100\%$ (F10) of trials in the software testbed.

Crucially, however, $H_1$ was **not** observed in the compiled production objects (`mlkem768_inst.o`), because the native monitor does not pass vulnerable stack snapshots across unchecked memory boundaries.

---

### Question 4: What can be concluded about $H_2$ in the tested scenarios?
**Across all 400 compiled production decapsulation trials, zero Silent Data Corruption events occurred ($H_2 = 0/400$, 95% Wilson score CI: $[0.0\%, 0.95\%]$).**

Under the tested software fault models targeting the internal NTT stages:
1. Every injected fault that corrupted intermediate polynomial arithmetic caused the reconstructed ciphertext $c'$ to differ from the received ciphertext $c$.
2. Constant-time memory comparison (`mlk_ct_memcmp`) consistently detected this disparity.
3. The implementation safely routed output selection to the FIPS 203 implicit rejection key $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$.

However, this empirical finding does **not** prove mathematical impossibility of SDC under arbitrary physical attacks. Physical instruction skips on `mlk_ct_memcmp` or pointer corruption aliasing $c'$ to $c$ would defeat this defense.

---

### Question 5: The strongest defensible research question?
The strongest, most impactful, and defensible research question is:

> **"In lattice-based key encapsulation mechanisms (ML-KEM-768), does local checkpoint-and-verify arithmetic recovery introduce circular verifier blindness under internal memory corruption, and does outer Fujisaki-Okamoto re-encryption reliably suppress resulting end-to-end silent data corruption under software fault models?"**

This question focuses on an authentic architectural trade-off, avoids unsupported physical claims, and is directly answered by the empirical evidence.

---

### Question 6: Whether the evidence is now sufficient to begin drafting the manuscript?
**YES, subject to two mandatory conditions:**

1. **Condition 1 (Strict Claim Scoping):** The manuscript must explicitly restrict all $H_1$ verifier blindness claims to the software harness architecture, acknowledge the absence of physical fault experiments, withdraw all constant-time claims, and state empirical confidence intervals ($[0.0\%, 0.95\%]$) rather than claiming "unconditional" security.
2. **Condition 2 (Prior-Art Literature Review):** Formal academic novelty must be documented through a systematic prior-art comparative literature review comparing circular verifier blindness against existing post-quantum fault detection literature (e.g., Ravi et al., CHES 2020; Delvaux, 2022). Until this literature review is completed and written into the related work section, novelty must be characterized as an open research question.

---

## 3. Final Certification

The deliverables in `phase14_evidence_correction/` represent the complete, corrected, auditable truth of this repository. All historical fabrications and calculation errors have been purged. The repository is certified ready for academic manuscript drafting under the defined claim boundaries.
