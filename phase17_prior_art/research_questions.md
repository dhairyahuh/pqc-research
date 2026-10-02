# Formal Research Questions and Hypotheses

**Date:** October 2026  
**Evidence Baseline:** Phase 16 Evidence Closure (Commit `ca38dec`)

---

## Primary Research Question (RQ)

> **RQ:** Can dual-transform (forward and inverse) NTT algebraic invariant monitoring with localized register rollback achieve autonomous transient fault recovery in ML-KEM-768 software implementations while maintaining zero silent data corruption under stochastic single-event upset fault models?

---

## Decomposed Sub-Questions

### RQ1: Dual-Transform Invariant Coverage
> Does a complementary algebraic invariant formulation covering both Cooley-Tukey Forward NTT and Gentleman-Sande Inverse NTT achieve complete butterfly monitoring across all 9,856 decapsulation butterfly operations?

**Status:** Supported. The implementation monitors all forward (CT sum/difference) and inverse (GS sum/multiplier) butterflies.

### RQ2: Autonomous Recovery Under Transient Faults
> Can localized in-place register rollback achieve genuine recovery from transient single-bit ALU faults without triggering a full decapsulation restart?

**Status:** Supported. 100/100 genuine recoveries under Target F4 (transient single-bit multiplier XOR).  
**Confidence Interval:** 95% Wilson score CI: [96.3%, 100.0%].

### RQ3: Safe Degradation Under Persistent Faults
> Does the monitor correctly escalate to fail-stop (implicit rejection) when faults persist beyond a single retry attempt?

**Status:** Supported. 200/200 safe fail-stop aborts under Targets F5A (recurring XOR) and F5B (force-value).

### RQ4: End-to-End Silent Data Corruption Suppression
> Is silent data corruption (SDC)—defined as emission of an incorrect shared secret without detection—prevented across all evaluated fault classes?

**Status:** Supported. 0/300 SDC events across active fault trials.  
**Confidence Interval:** 95% Wilson score CI: [0.0%, 1.26%].

### RQ5: Performance Overhead Acceptability
> Does the dual-transform monitoring overhead remain below 30% of clean decapsulation latency, and is it substantially lower than software dual modular redundancy (DMR)?

**Status:** Supported. +25.3% vs. clean; +149% for software DMR (5.9× more efficient).

---

## Hypotheses

### H₁: Circular Verifier Blindness
> **Hypothesis:** In-place snapshot recovery verifiers that share the same memory region as the computation being protected will exhibit systematically high false-pass rates under memory corruption faults, because the snapshot itself is corrupted simultaneously with the live state.

**Status:** Supported in harness model. False-pass rates: 94.0%–100.0% across 6 vulnerable targets.  
**Scope:** Standalone software harness only. Production code uses separate register-based snapshots.

### H₂: FO Re-Encryption Containment
> **Hypothesis:** Even when local NTT arithmetic verifiers are blind (H₁ active), the outer Fujisaki-Okamoto re-encryption check in ML-KEM decapsulation will prevent corrupted intermediate states from releasing incorrect shared secrets.

**Status:** Supported. 0/300 SDC across production fault trials where the local verifier operates correctly (F4) and where the monitor escalates to fail-stop (F5A, F5B).

---

## Null Hypotheses (for Statistical Testing)

### H₀₁: No Recovery Benefit
> The localized rollback mechanism provides no improvement over simple abort-on-detection (recovery rate = 0%).

**Rejection:** F4 achieves 100/100 recovery. Fisher exact test: $p < 10^{-30}$.

### H₀₂: Non-Zero SDC Rate
> The SDC rate is non-zero under production fault injection.

**Result:** Cannot reject at the observation level (0/300), but the 95% upper bound is 1.26%. The manuscript claims zero *observed* SDC, not zero *theoretical* SDC.

---

## Explicit Non-Claims

The following are **not** claimed and must not appear in the manuscript:

1. ❌ Physical radiation hardness or space qualification.
2. ❌ Protection against active adversarial fault injection (SIFA/DFA).
3. ❌ Certified constant-time execution (no TVLA/dudect conducted).
4. ❌ Protection against twiddle factor memory corruption.
5. ❌ Protection against FO comparison instruction skip attacks.
6. ❌ Mathematical impossibility of SDC (only empirical bound reported).
7. ❌ Evaluation on embedded space processors (desktop host only).
