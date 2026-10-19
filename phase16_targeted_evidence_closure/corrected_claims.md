# Corrected Research Claims and Epistemological Boundaries

**Auditor:** Skeptical Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Subject:** Formal Claim Qualification, Telemetry Grounding, and Discarded Overstatements  

---

## 1. Executive Summary

This document establishes the authoritative wording for all academic claims supported by the Phase 16 evidence package. 

Every claim has been audited to separate:
- **Directly Observed Telemetry:** Variables recorded in trial CSV rows and verified byte-for-byte against independent oracles.
- **Inferred Control-Flow States:** Control-flow transitions proven by source code structure but not serialized as dedicated CSV columns.
- **Unverified Assumptions:** Hypotheses regarding physical hardware behavior, compiler optimizations, or universal mathematical bounds that exceed empirical observation.

All hyperbolic words ("unconditional," "guaranteed," "cryptographic firewall," "constant-time") have been excised.

---

## 2. Reconciled Research Claims

### Claim 1: Circular Verifier Blindness in In-Place Snapshot Recovery ($H_1$)
- **Original Phase 15 Formulation:** *"In-place snapshotting creates local verifier blindness ($H_1$) under memory corruption."*
- **Audit Findings:** 
  - *Directly Observed Fields:* Pre-retry values (`pre_retry_u, pre_retry_v`), retry values (`retry_u, retry_v`), difference checks (`diff_retry, sum_retry`), and verifier decisions (`verifier_passed`).
  - *Inferred Field:* Actual fault trigger event is not logged in a dedicated CSV column in `derived_corrected_trial_results.csv`; activation is inferred from downstream `mismatch_count > 0`.
  - *Scope:* Evaluated strictly in standalone software harness models simulating in-place stack corruption.
- **Authoritative Corrected Claim:**
  > *"In standalone software harness models simulating in-place snapshot memory corruption, local recovery verifiers consistently validate corrupted butterfly computations against corrupted snapshots, exhibiting false-pass rates between $94.0\%$ and $100.0\%$ across vulnerable configurations (Targets F1, F2, F6, F7, F9, F10)."*
- **Disposition:** **Supported with Qualification (Restricted to Software Harness Models).**

---

### Claim 2: Genuine Recovery Under Transient Butterfly Faults (Target F4)
- **Original Phase 15 Formulation:** *"Native NTT monitor achieves genuine recovery under transient butterfly faults (F4)."*
- **Audit Findings:**
  - *Directly Observed Fields:* `actually_triggered = 1`, `mismatch_count = 1`, `recovered_count = 1`, `persistent_count = 0`, `internal_status = 0x5A5A5A5A`, and `actual_ss_hex == oracle_valid_hex` across all 100 trials.
  - *Inferred Field:* Intermediate post-retry butterfly coefficients ($u_{\text{new}}, v_{\text{new}}$) are local variables in `poly.c` and not serialized to CSV.
  - *Causal Chain:* Source code inspection proves `recovered_count` cannot increment unless post-retry parity verification satisfies `diff_retry == 0 && sum_retry == 0`.
- **Authoritative Corrected Claim:**
  > *"The compiled production NTT monitor achieves 100/100 genuine recoveries under evaluated transient single-bit butterfly multiplier faults, re-executing butterfly logic and restoring authentic valid key output (95% Wilson score CI: $[96.3\%, 100.0\%]$)."*
- **Disposition:** **Supported with Qualification (Acknowledge Intermediate Unserialized Fields).**

---

### Claim 3: Safe Fail-Stop Under Persistent and Force-Value Faults (Targets F5A, F5B)
- **Original Phase 15 Formulation:** *"Native NTT monitor enforces safe fail-stop under recurring bit-inversion and force-value faults (F5A, F5B)."*
- **Audit Findings:**
  - *Directly Observed Fields:* `actually_triggered = 6`, `persistent_count >= 1`, `mismatch_count >= 1`, `internal_status = 0xFFFFFFFF`, and `actual_ss_hex == oracle_rej_hex` across all 200 trials.
  - *Model Semantics:* Target F5B is an abstract software debug hook forcing `*t = 0`. It does not model analog silicon latch-up.
- **Authoritative Corrected Claim:**
  > *"The compiled production NTT monitor enforces 200/200 safe fail-stop aborts under recurring bit-inversion and software force-value fault models, returning status `0xFFFFFFFF` and emitting the conformant FIPS 203 implicit rejection key $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$."*
- **Disposition:** **Supported with Qualification (Strictly Labeled Software Force-Value Model).**

---

### Claim 4: Absence of Silent Data Corruption Across Production Fault Trials
- **Original Phase 15 Formulation:** *"Absence of Silent Data Corruption ($H_2 = 0.0\%$) across 400 production trials."*
- **Audit Findings:**
  - *Denominator Defect:* Previous phases inflated the denominator by including 100 unfaulted baseline control trials (Target F12).
  - *Corrected Denominator:* Exactly 300 active production fault-injection trials were executed (100 each for F4, F5A, F5B).
  - *Zero-Event Bound:* $0 / 300$ active fault trials yielded SDC, establishing an empirical upper bound of $1.26\%$ at 95% confidence.
- **Authoritative Corrected Claim:**
  > *"Zero Silent Data Corruption events were observed across 300 active production fault-injection trials (0/300, 95% Wilson score CI: $[0.0\%, 1.26\%]$); clean baseline control trials (n=100) are reported separately."*
- **Disposition:** **Supported with Qualification (Corrected Denominator $n = 300$).**

---

### Claim 5: FIPS 203 Decapsulation Implicit Rejection Conformance
- **Original Phase 15 Formulation:** *"Decapsulation implicit rejection conforms exactly to FIPS 203 ($K = \text{J}(z \parallel c)$)."*
- **Audit Findings:**
  - *Directly Observed Fields:* Evaluated across 100 controlled single-bit ciphertext mutations in `invalid_ciphertext_trials.csv`. 100/100 emitted keys matched the clean-room Keccak-f[1600] oracle.
- **Authoritative Corrected Claim:**
  > *"ML-KEM-768 decapsulation implicit rejection conforms bit-for-bit with NIST FIPS 203 Section 7.3 across 100 invalid ciphertext mutations verified against an independent clean-room Keccak-f[1600] oracle."*
- **Disposition:** **Supported.**

---

### Claim 6: Containment Capability of the Outer Fujisaki-Okamoto Transform
- **Original Phase 15 Formulation:** *"Outer Fujisaki-Okamoto re-encryption prevents Silent Data Corruption across all relevant faults."*
- **Audit Findings:**
  - *Physical Limitation:* In silicon, clock glitching, laser fault injection, instruction skipping on `mlk_ct_memcmp`, or pointer aliasing ($c' \equiv c$) bypass the FO check entirely.
- **Authoritative Corrected Claim:**
  > *"Under the evaluated software fault models targeting internal NTT stages, outer FO re-encryption consistently prevented corrupted intermediate states from releasing invalid shared secrets; however, physical fault injection bypassing the comparison loop remains unaddressed."*
- **Disposition:** **Supported with Qualification (Explicitly State Physical Bypass Vectors).**

---

### Claims 7 & 8: Constant-Time Execution and Physical Radiation Hardening
- **Original Formulations:** Claims of certified constant-time security and physical radiation hardness.
- **Audit Findings:** No microarchitectural timing leakage measurements (TVLA/dudect) were conducted. No physical hardware or particle beam testing was executed.
- **Authoritative Disposition:** **COMPLETELY WITHDRAWN.**
