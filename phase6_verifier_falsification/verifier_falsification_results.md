# Phase 6: Experimental Falsification of Recovery-Verifier Trust Assumptions

**Auditor:** Skeptical Cryptographic Implementation Researcher  
**Date:** October 2026  
**Artifact:** `phase6_verifier_falsification/verifier_falsification_results.md`  
**Dataset Reference:** `phase6_verifier_falsification/raw_trial_results.csv` (1,200 trials)

---

## 1. Executive Summary: Arithmetic Consistency vs. Semantic Authenticity

A fundamental premise of software fault recovery is that a verification equation confirms the validity of a restored computational state. The native NTT butterfly monitor evaluates:
$$diff_{\text{retry}} = (u_{\text{new}} - v_{\text{new}} - 2 \cdot t_{\text{retry}}) \pmod{3329}$$
$$sum_{\text{retry}} = (u_{\text{new}} + v_{\text{new}} - 2 \cdot u_{\text{saved}}) \pmod{3329}$$
If both equal zero, the monitor increments `recovered_count` and reports recovery.

**The Central Falsification Result:**
Our independent empirical campaign demonstrates that the recovery verifier **merely verifies arithmetic consistency relative to the inputs supplied to it, but possesses zero capability to verify the authenticity or integrity of those inputs.**

When the snapshot $u_{\text{saved}}$ is corrupted, the recomputation and the verification equation both ingest the corrupted value. The error cancels algebraically, producing:
$$\text{verifier\_passed} = \text{True}, \quad \text{while } (u_{\text{retry}}, v_{\text{retry}}) \neq (u_{\text{ref}}, v_{\text{ref}})$$
in **98.0% of isolated bit-flip trials (`F1`)** and **100.0% of additive snapshot glitch trials (`F2`)**.

---

## 2. Systematic Falsification Across Attack Loci

### 2.1 Locus 1: Saved Operand Corruption Post-Capture (`F1_SAVED_OPERAND_BITFLIP`)
- **Experimental Setup:** Single-shot bit flip on local stack parameter $u_{\text{saved}}$ ($0 \le b \le 15$) after capture.
- **Empirical Findings (100 Trials):**
  - **H1 (False Recovery Certification): 98 / 100 trials (98.0%)** [93.0%, 99.4%].
  - **H2 (Silent Data Corruption): 0 / 100 trials (0.0%)** [0.0%, 3.7%].
  - **Downstream FO Rejection:** 85 trials (85.0%) rejected downstream by FO.
  - **Lattice Rounding Absorption:** 13 trials (13.0%) recovered true key because low-order bits ($b \le 3$) stayed below the $q/4 \approx 832$ decoding threshold.
  - **Arithmetic Overflow Abort:** 2 trials (2.0%) aborted due to sign-bit overflow.
- **Falsification Verdict:** **Hypothesis H1 is REPRODUCED and PROVEN.** The recovery verifier is blind to saved operand corruption.

---

### 2.2 Locus 2: Snapshot Corruption Pre-Rollback (`F2_SNAPSHOT_PRE_RETRY_DIFFUSION`)
- **Experimental Setup:** $+100$ additive glitch on $u_{\text{saved}}$ after mismatch detection, immediately prior to `*r_j = u_saved`.
- **Empirical Findings (100 Trials):**
  - **H1 (False Recovery Certification): 100 / 100 trials (100.0%)** [96.3%, 100.0%].
  - In all 100 trials, the verifier declared recovery while writing garbled coefficients back into the polynomial buffer.
  - In stages 3–7 (70 trials), the error diffused across the polynomial, exceeding the decoding threshold and triggering downstream FO rejection (`REJECTED_DOWNSTREAM_FO`).
  - In stages 1–2 (30 trials), the error remained localized below the threshold, resulting in genuine key agreement.
- **Falsification Verdict:** Falsifies the claim that recovery checks prevent polluted rollback.

---

### 2.3 Locus 3: Corruption of the Verifier's Calculated Value (`F5_VERIFIER_DIFF_CALC_CORRUPT`)
- **Experimental Setup:** Clean retry executed; bit flip applied to $diff_{\text{retry}}$ calculation.
- **Empirical Findings (100 Trials):**
  - **Safe Monitor Rejection: 100 / 100 trials (100.0%)** [96.3%, 100.0%].
  - Zero false recoveries occurred, but **100% false-positive aborts** were induced.
- **Falsification Verdict:** Demonstrates that the verifier's own state represents a single-point-of-failure for availability denial-of-service.

---

### 2.4 Locus 4: Corruption of Verifier Acceptance Predicate (`F6_VERIFIER_RESULT_FORCE_PASS`)
- **Experimental Setup:** Persistent ALU fault present; branch comparison forced to evaluate `diff_retry == 0 && sum_retry == 0`.
- **Empirical Findings (100 Trials):**
  - **H1 (False Recovery): 99 / 100 trials (99.0%)** [94.6%, 99.8%].
  - **Downstream FO Rejection: 97 / 100 trials (97.0%)** [91.5%, 99.0%].
- **Falsification Verdict:** A control-flow glitch on the verifier branch condition masks persistent hardware defects, which are subsequently caught only by outer protocol checks.

---

### 2.5 Locus 5: Multiplier Glitch During Retry (`F7_RETRY_ARITHMETIC_GLITCH`)
- **Experimental Setup:** Bit flip injected into $t_{\text{retry}} = \text{fqmul}(v_{\text{saved}}, \zeta)$ during the retry execution.
- **Empirical Findings (100 Trials):**
  - **H1 (False Recovery): 94 / 100 trials (94.0%)** [87.5%, 97.2%].
  - **Downstream FO Rejection: 91 / 100 trials (91.0%)** [83.8%, 95.2%].
  - **Explanation:** When $t_{\text{retry}}$ is corrupted, both $u_{\text{new}} = u + t_{\text{retry}}$ and $v_{\text{new}} = u - t_{\text{retry}}$ inherit the corrupted product. The difference check $u_{\text{new}} - v_{\text{new}} - 2 \cdot t_{\text{retry}} = 2 \cdot t_{\text{retry}} - 2 \cdot t_{\text{retry}} \equiv 0$ cancels identically!
- **Falsification Verdict:** **New Vulnerability Discovered.** The verifier CANNOT detect multiplier faults occurring during retry unless $t_{\text{retry}}$ is independently recomputed from a separate multiplier unit!

---

### 2.6 Locus 6: Verifier Expected Operand Corruption (`F8_VERIFIER_INPUT_OPERAND_CORRUPT`)
- **Experimental Setup:** Butterfly recomputes cleanly; operand $u_{\text{saved}}$ passed into the verification equation is corrupted *exclusively within the verifier scope*.
- **Empirical Findings (100 Trials):**
  - **Safe Monitor Rejection: 100 / 100 trials (100.0%)** [96.3%, 100.0%].
- **Falsification Verdict:** Proves that the verifier does not check output correctness; it only measures the relative algebraic distance between the recomputed values and its expected parameter.
