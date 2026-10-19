# Phase 7: Comprehensive Claim-Evidence Matrix and Audit Verdict

**Auditor:** Independent Cryptographic Implementation Auditor  
**Date:** October 2026  
**Artifact:** `phase7_independent_claim_audit/claim_evidence_matrix.md`

---

## 1. Master Evidence Partition Table

| Category | Claim / Finding | Evidence & Source Location | Audit Verdict |
|---|---|---|---|
| **Reproduced Findings** | **Tautological Verifier Blindness (H1):** The butterfly recovery verifier is blind to corrupted snapshot operands because algebraic error terms cancel out identically in the verification equation. | Tested in `F1` (98/100 passes) and `F2` (100/100 passes); raw trial records in `derived_corrected_trial_results.csv`; verified against corrected multi-polynomial oracle. | **REPRODUCED & PROVEN** |
| **Reproduced Findings** | **Retry Multiplier Glitch Blindness (`F7`):** Multiplier glitches during retry cancel out in the difference check $u_{\text{new}} - v_{\text{new}} - 2 \cdot t_{\text{retry}} \equiv 0$, causing 94% false recovery declarations. | `genuine_phase7_audit_harness.c:215-225`; measured 94/100 verifier passes in `F7`. | **REPRODUCED & PROVEN** |
| **Reproduced Findings** | **Fujisaki-Okamoto Re-encryption Safety Barrier:** In ML-KEM decapsulation, corrupted polynomials cause message decoding errors that fail ciphertext re-encryption ($tmp \neq ct$), safely forcing implicit rejection ($K_{\text{rej}}$). | 517 of 591 blinded trials produced exact byte matches with canonical $ss_{\text{rejection}}$; 0 trials of SDC observed across 1,200 trials. | **REPRODUCED & PROVEN** |
| **Reproduced Findings** | **DSPC Single-Bit Containment (`F11`):** DSPC detects 100% of isolated single-bit snapshot faults, triggering immediate monitor fail-stop. | 100/100 safe monitor rejections in `F11`. | **REPRODUCED & PROVEN** |
| **Reproduced Findings** | **DSPC Affine Linearity Weakness (`F9` & `F10`):** Correlated 2-bit flips on snapshot and checksum token produce an exact collision, bypassing DSPC in 100% of trials; branch skips also bypass in 100% of trials. | `dspc_implementation_audit.md`; measured 100/100 bypasses in `F9` and `F10`. | **REPRODUCED & PROVEN** |
| **Findings Contradicted by Execution** | **Phase 6 Claim:** *"F4 demonstrated 100% H1 false recovery."* | Contradicted. F4 was a 100% clean, genuine recovery (`REC_GENUINE`). Phase 6's H1 metric was an artifact of comparing polynomial #0 against reference polynomial #5. | **CONTRADICTED & WITHDRAWN** |
| **Findings Contradicted by Execution** | **Phase 6 Arithmetic Claim:** *"Bit 15 always causes signed overflow, explaining a theoretical 93.75% pass rate."* | Contradicted. Bit 15 only causes overflow when signs match and $|X| > 32768$ (2 of 6 trials in seed `0x1337C0DE`), resulting in an exact 98.0% pass rate with residue $\pm 2285$. | **CONTRADICTED & RECONCILED** |
| **Findings Contradicted by Execution** | **Hypothesis H2 (Silent Data Corruption) in Decapsulation:** *" Blinding the monitor allows an incorrect shared secret to be accepted as valid by decapsulation."* | Contradicted for isolated decapsulation faults. FO re-encryption prevents SDC in 100% of tested cases (0.0% SDC). | **CONTRADICTED (In Decapsulation)** |
| **Hypotheses Not Yet Tested** | **H2 in Primitives Without FO Re-encryption:** Does snapshot blindness produce SDC in ML-KEM Encapsulation (`mlkem_enc`) or ML-DSA Signature Generation (`mldsa_sign`)? | Untested empirically in this campaign. Neither primitive contains a re-encryption verification loop. | **HYPOTHESIS NOT YET TESTED** |
| **Hypotheses Not Yet Tested** | **Physical Fault Feasibility of Correlated 2-Bit Collisions:** Can multi-spot optical EMFI reliably induce correlated bit flips across disparate registers in silicon? | Untested physically. Demonstrated only in software-constructed models. | **HYPOTHESIS NOT YET TESTED** |
| **Invalid or Inconclusive Experiments** | **Lattice Slack Inconclusive Trials:** Low-order bit flips ($b \le 3$) and localized Stage 1–2 perturbations that did not cross the lattice decoding/compression threshold. | 13 trials in `F1` and 30 trials in `F2` produced true keys because arithmetic error stayed below the quantization threshold. | **INCONCLUSIVE FOR SDC** |

---

## 2. Definitive Answers to Audit Questions

### 1. Is H1 genuinely demonstrated using an independent computational oracle?
**YES.** When verified against a multi-polynomial reference oracle, `F1` (98%), `F2` (100%), `F6` (99%), and `F7` (94%) conclusively demonstrate that the recovery verifier certifies recovery on computational states that differ from fault-free execution.

### 2. Is the F1 arithmetic explanation consistent with the measured trials?
**YES, after Phase 7 reconciliation.** The measured 98.0% pass rate is caused by exact signed 16-bit arithmetic: bits 0–14 (94 trials) never overflow; bit 15 overflows in exactly 2 trials (Trials 16 and 64) producing residue $\pm 2285$, and passes without overflow in 4 trials (Trials 32, 48, 80, 96). Total passes = $94 + 4 = 98$ (98.0%).

### 3. Is F2's stage-dependent outcome explanation verified?
**YES.** In Stages 1 and 2 (30 trials), the $+100$ error is diffused across 256 coefficients by subsequent NTT stages, remaining below the 10-bit ciphertext compression threshold ($\Delta_{\text{bin}} \approx 3.25$). The compressed ciphertext matches bit-for-bit ($tmp == ct$), yielding `RECOVERED_GENUINE`. In Stages 3–7 (70 trials), the error crosses the threshold, triggering FO rejection.

### 4. Is F4 correctly classified?
**NO in Phase 6; YES in Phase 7.** Phase 6 erroneously classified F4 as 100% H1 false recovery due to an oracle indexing collision. Phase 7 proves F4 was a **100% genuine recovery** (H1 = 0%, Correct Recovery = 100%).

### 5. Is H2 absent only in the tested cases, or does the evidence support a broader conclusion?
**Absent only in primitives with Fujisaki-Okamoto transforms.** The evidence proves that IND-CCA2 decapsulation is protected by its outer re-encryption loop. However, the evidence does NOT support broader safety for ML-KEM Encapsulation or ML-DSA, where no re-encryption loop exists.

### 6. Which DSPC weaknesses are mathematically established, software-reproduced, or merely hypothesized?
- **Mathematically Established & Software-Reproduced:** Vulnerability to correlated 2-bit linear collisions (`F9`) and control-flow branch skips (`F10`).
- **Merely Hypothesized:** Physical occurrence of correlated 2-bit register flips under optical laser fault injection on modern superscalar silicon.

### 7. What is the smallest defensible research claim that survives this audit?
> **Defensible Claim:** Local invariant recovery monitors in lattice-based NTT pipelines exhibit **Tautological Verifier Blindness** when snapshot inputs are corrupted. While outer Fujisaki-Okamoto re-encryption prevents this component blindness from escalating to system-level Silent Data Corruption in ML-KEM decapsulation, linear software checksums (DSPC) protect only against single-bit faults and fail against correlated 2-bit disturbances.

### 8. What evidence is still missing before writing a research paper?
1. **Testing Primitives Lacking FO Loops:** Empirical verification of H1 leading to SDC in ML-KEM Key Encapsulation (`mlkem_enc`) and ML-DSA Signature Generation (`mldsa_sign`).
2. **Physical Fault Injection:** Hardware validation on a physical microcontroller (e.g. ARM Cortex-M4) using clock glitching or EMFI to validate whether branch skips or snapshot flips occur in actual silicon.
