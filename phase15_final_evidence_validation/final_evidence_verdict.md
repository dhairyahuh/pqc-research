# Phase 15 Final Evidence Verdict and Research Claim Freeze

**Auditor:** Skeptical Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Subject:** Final Verdict on Evidence Validity, Claim Safety, and Formal Evidence Freeze  

---

## 1. Executive Determination

Following an exhaustive, trial-level validation across all 15 project phases, this audit issues a definitive certification of the ML-KEM-768 fault-resilience evidence package. 

All numerical claims in this phase are traced to raw, individual CSV rows. Historical calculation errors and fabrications (including the Phase 13 pipeline defects and Phase 8 narrative overrides) have been documented, reconciled, and corrected. 

The research repository is hereby placed under a **Formal Evidence Freeze**. No further fault campaigns, ad-hoc countermeasure expansions, or arbitrary aggregations are permitted.

---

## 2. Definitive Inventory: Safe vs. Unsafe Claims

### 2.1 Claims Certified as Safe to Enter the Manuscript
1. **In-Place Snapshot Circular Blindness ($H_1$):**
   - *Certified Scope:* Software harness models simulating in-place memory corruption (Targets F1, F2, F6, F7, F9, F10).
   - *Empirical Evidence:* False-pass rates of $94.0\%$ to $100.0\%$ when intermediate snapshots are corrupted.
   - *Framing:* An architectural cautionary design pitfall demonstrating why naive rollback/retry patterns fail in cryptographic software.
2. **Genuine Recovery Under Transient Faults (F4):**
   - *Certified Scope:* Authentic compiled production objects (`mlkem768_inst.o` + `mlkem_fault_hooks.o`).
   - *Empirical Evidence:* $100/100$ genuine recoveries ($100.0\%$, 95% CI: $[96.3\%, 100.0\%]$) under intermediate butterfly bitflips, producing valid shared secrets ($K_{\text{out}} = K_{\text{valid}}$).
3. **Safe Fail-Stop Under Recurring and Force-Value Faults (F5A, F5B):**
   - *Certified Scope:* Authentic compiled production objects.
   - *Empirical Evidence:* $200/200$ safe fail-stops ($100.0\%$, 95% CI: $[98.1\%, 100.0\%]$) returning status `0xFFFFFFFF` and emitting the conformant rejection key $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$.
   - *Constraint:* F5B must remain strictly labeled as a software force-value model.
4. **Absence of SDC ($H_2 = 0.0\%$) Under Tested Software Faults:**
   - *Certified Scope:* Compiled production binary decapsulation.
   - *Empirical Evidence:* $0/400$ SDC events ($0.0\%$, 95% Wilson CI: $[0.0\%, 0.95\%]$).
   - *Constraint:* Bounded strictly by empirical sample size; must not claim universal or unconditional physical impossibility.
5. **FIPS 203 Rejection Conformance:**
   - *Certified Scope:* Production decapsulation implicit rejection loop.
   - *Empirical Evidence:* $100/100$ bit-for-bit matches against clean-room Keccak oracle for $K = \text{J}(z \parallel c)$.

---

### 2.2 Claims Certified as Unsafe (Withdrawn or Strictly Qualified)
1. **Target F3 100% Blindness Claim:** **WITHDRAWN**. Raw data shows $0/100$ ($0.0\%$) false recovery (safe monitor rejection).
2. **Target F7 0% Blindness Claim:** **WITHDRAWN**. Raw data shows $94/100$ ($94.0\%$) verifier false passes.
3. **Global Pooled Rates (561/600 $H_1$, 0/1,300 $H_2$):** **WITHDRAWN**. Pooling across disparate mechanisms and execution tiers is statistically invalid.
4. **Constant-Time Security Certifications:** **WITHDRAWN**. No timing leakage measurements (TVLA/dudect) were conducted.
5. **Physical Silicon / Radiation Hardness Claims:** **WITHDRAWN**. Software debug hooks cannot model analog hardware dynamics.
6. **"Unconditional Cryptographic Firewall" Rhetoric:** **WITHDRAWN**. Physical instruction skipping bypasses the FO comparison loop entirely.
7. **Absolute Academic Novelty Claims:** **MARKED UNRESOLVED**. Must be qualified as subject to a comprehensive comparative prior-art literature review.

---

## 3. Four-Part Evidence Freeze Decision

### 3.1 What Is Conclusively Established:
- Checkpointed NTT recovery that verifies against in-place snapshots is vulnerable to circular blindness ($H_1$) under internal memory corruption.
- In authentic compiled C code, native butterfly monitoring achieves genuine recovery under isolated transient bitflips and safe fail-stop under recurring faults.
- In software-modeled executions, outer Fujisaki-Okamoto re-encryption consistently prevents corrupted butterfly states from producing accepted invalid shared secrets ($H_2 = 0/400$, 95% CI: $[0.0\%, 0.95\%]$).
- Decapsulation implicit rejection conforms bit-for-bit to FIPS 203 Algorithm 17.

### 3.2 What Is Only Suggested (Plausible Hypotheses):
- Dual-rail status encoding in C source provides structural defense against single-locus predicate bypass, but machine-code emission could be subverted by compiler dead-code elimination or register reuse.
- Microarchitectural side-channel leakage during retry execution could leak secret polynomial coefficients, but this has not been measured experimentally.

### 3.3 What Remains Unknown:
- Behavior under physical hardware fault injection (EMFI, body bias, optical laser fault injection, clock glitching).
- Whether physical instruction skips on `mlk_ct_memcmp` or pointer aliasing ($c' \equiv c$) can defeat the outer FO check in silicon.
- Whether circular verifier blindness in lattice-based NTT recovery has been previously documented in hardware fault detection literature.

### 3.4 Manuscript Drafting Sufficiency Determination:
**THE EVIDENCE IS SUFFICIENT TO BEGIN DRAFTING THE MANUSCRIPT.**

The evidence package in `phase15_final_evidence_validation/` is clean, traceable, and empirically sound. It supports a focused, impactful research paper centered on:
> *"The interplay between internal arithmetic recovery verifier blindness and end-to-end Fujisaki-Okamoto re-encryption containment in ML-KEM-768 under software fault models."*

Drafting may proceed immediately under the claim boundaries established in this freeze.
