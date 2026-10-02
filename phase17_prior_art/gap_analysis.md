# Phase 17: Novelty Differentiation and Prior-Art Gap Analysis

**Auditor:** Independent Research Verification  
**Date:** October 2026  
**Baseline:** Phase 16 Evidence Closure (Commit `ca38dec`)  
**Literature Corpus:** 18 works (P01–P18), see `prior_art_matrix.csv`

---

## 1. Systematic Novelty Assessment

### 1.1 Novelty Claim: Dual-Transform (Forward + Inverse) NTT Algebraic Invariant Monitoring

**Status: NOVEL — No published work provides complete dual-transform invariant coverage in software.**

| Dimension | Paul et al. (P03) | Sarker et al. (P04) | REMO (P17) | **This Work** |
|:---|:---|:---|:---|:---|
| Forward NTT (CT) | ✅ FR-AIC / PR-AIC | ✅ RESO + residue | ✅ Modular offset | ✅ Sum/difference |
| Inverse NTT (GS) | ❌ Not addressed | ❌ Not addressed | ❌ Not addressed | ✅ Sum/multiplier |
| Platform | FPGA only | FPGA/ASIC only | FPGA only | **Software (C)** |
| Butterfly coverage | Forward only | Forward only | CT-BU only | **All 9,856** |

**Evidence:** Searches across IEEE Xplore, ACM DL, IACR ePrint, and arXiv (Oct 2026) returned zero results for software-level algebraic invariant monitoring of Gentleman-Sande Inverse NTT butterflies. All three closest works (P03, P04, P17) are hardware FPGA designs protecting only Forward NTT.

**Risk:** Reviewers may perceive this as an incremental extension of Paul et al. (2024) from hardware to software and from forward to inverse NTT. The manuscript must emphasize: (a) the distinct mathematical derivation for GS butterflies, (b) the fundamentally different software execution model (no pipeline parallelism), and (c) the integration of recovery (not just detection).

---

### 1.2 Novelty Claim: Localized In-Place Register Rollback with Retry

**Status: NOVEL — No published PQC implementation performs autonomous arithmetic recovery.**

| Dimension | P03 (AIC) | P04 (RESO) | P06 (Hermelink) | P11 (SIFA) | **This Work** |
|:---|:---|:---|:---|:---|:---|
| On fault detection | Abort | Abort | Abort / dual-rail | Proves retry is insecure | **Rollback + retry** |
| Recovery capability | None | None | None | N/A (attack) | **100/100 transient** |
| Threat model | Passive faults | Passive faults | Active adversary | Active adversary | **Stochastic SEU** |

**Evidence:** Every published PQC fault-detection scheme (P03, P04, P06, P12, P13, P17) implements detection-only abort. No work attempts autonomous in-place arithmetic recovery for any lattice-based KEM.

**Critical Constraint (SIFA — P11):** Dobraunig et al. (2018) proves that recomputation/retry under active adversarial fault injection leaks secret keys via statistical bias. Our design explicitly restricts retry to **non-adversarial, stochastic cosmic ray environments** where the SIFA threat model does not apply. The manuscript must prominently acknowledge this boundary.

**Risk:** Reviewers familiar with SIFA may reject retry as fundamentally insecure. The manuscript must clearly delineate the threat model boundary: active physical attackers (SIFA applies → fail-stop mandatory) vs. non-adversarial radiation (independent Poisson events → retry is safe).

---

### 1.3 Novelty Claim: Circular Verifier Blindness Discovery (H₁)

**Status: NOVEL OBSERVATION — No published work identifies this failure mode.**

**Description:** When recovery snapshots are stored in-place (same memory region as the computation being protected), a memory corruption fault corrupts both the live computation and the snapshot simultaneously. The post-retry verifier then compares corrupted-vs-corrupted values and falsely passes, achieving 94.0%–100.0% false-pass rates in evaluated configurations.

**Prior-Art Search:** No published work on PQC fault detection discusses the semantic consequence of co-located snapshots and live state under memory corruption. This is a genuinely new failure mode characterization.

**Qualification:** This is demonstrated only in standalone software harness models, not in production compiled code (where the monitor uses separate register-based snapshots).

---

### 1.4 Novelty Claim: End-to-End SDC Suppression via FO Re-encryption

**Status: CONFIRMATORY — Extends known FO security property to fault resilience context.**

**Relationship to Prior Art:**
- Hermelink et al. (P06) identifies FO comparison as a vulnerability target.
- Glabush et al. (P16) proposes "verifiable decapsulation" to bind re-encryption to the KDF.
- Our work empirically demonstrates that even when internal NTT arithmetic is corrupted and the local verifier is blind (H₁), the outer FO re-encryption consistently catches the corruption (0/300 SDC across active fault trials).

**This is not a novel claim about the FO transform itself.** It is an empirical confirmation that the known IND-CCA2 security mechanism provides a practical fault-containment boundary in software.

---

### 1.5 Claim Fully Covered by Prior Art (No Novelty)

| Claim | Prior Art | Status |
|:---|:---|:---|
| FIPS 203 implicit rejection conformance | FIPS 203 (P18) specification | **Conformance test, not novel** |
| Constant-time execution | KyberSlash (P14) highlights the requirement; we lack TVLA/dudect validation | **Withdrawn** |
| Physical radiation hardness | Dodd & Massengill (P01), ECSS (P02) | **Withdrawn** |

---

## 2. Consolidated Gap-to-Contribution Mapping

| Research Gap | Gap Source | This Work's Contribution | Evidence Status |
|:---|:---|:---|:---|
| GAP-01: Adversarial abort vs. autonomous availability | Dobraunig (P11) vs. Kim (P08) / Dodd (P01) | Localized rollback + fail-stop dual-mode | Supported (n=300, 0 SDC) |
| GAP-02: Inverse NTT unmonitored | Paul (P03), Sarker (P04), REMO (P17) | Complete dual-transform invariant formulation | Supported (9,856 butterflies) |
| GAP-03: Hardware-only detection, no software recovery | P03, P04, P13, P17 | Software C implementation with register rollback | Supported (100/100 recovery) |
| GAP-04: Circular verifier blindness undocumented | No prior art found | H₁ characterization with 94–100% false-pass | Supported (harness model) |

---

## 3. Threats to Novelty

### 3.1 Immediate Threats

1. **Paul et al. (P03) extension to inverse NTT:** If Paul et al. publishes a follow-up extending AIC to GS-InvNTT before our submission, our dual-transform claim is preempted. **Mitigation:** Submit promptly; emphasize software (not FPGA) and recovery (not detection-only).

2. **SIFA dismissal:** Reviewers may argue that any retry mechanism is categorically insecure regardless of threat model. **Mitigation:** Formalize the threat model boundary in Section 2 of the manuscript; cite Dobraunig et al. explicitly and explain why Poisson cosmic ray events are not equivalent to adversarial fault injection.

3. **Insufficient sample size:** $n = 300$ is modest for security claims. **Mitigation:** Report the exact Wilson score confidence interval ($[0.0\%, 1.26\%]$) and explicitly state that mathematical impossibility of SDC is not claimed.

### 3.2 Manageable Risks

4. **Desktop-only evaluation:** Results are on macOS AArch64, not LEON3/RISC-V. **Mitigation:** Explicitly label all results as "host platform evaluation" and propose QEMU cross-compilation as future work.

5. **No physical radiation beam testing.** **Mitigation:** The manuscript title, abstract, and claims must never state "radiation-hardened" or "space-qualified."

---

## 4. Final Prior-Art Verdict

The systematic review of 18 works across IEEE, ACM, IACR, ECSS, and NIST publications confirms:

> **No published work provides software-level dual-transform (forward + inverse) NTT algebraic invariant monitoring with autonomous localized register rollback for any lattice-based KEM. The identification of circular verifier blindness under co-located memory corruption is a novel failure mode characterization.**

The contribution is defensible under the strictly bounded thesis established in Phase 16, provided the manuscript:
1. Restricts the threat model to non-adversarial stochastic SEUs.
2. Explicitly addresses the SIFA boundary.
3. Reports results as desktop software evaluation (not space-qualified hardware).
4. Uses the corrected $n = 300$ denominator with Wilson score CIs.
