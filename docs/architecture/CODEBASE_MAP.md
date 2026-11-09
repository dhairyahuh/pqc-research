# Master Codebase Map & Technical Navigation Guide

This document provides direct answers and source-level line references to the 10 critical codebase questions required for system understanding, auditability, and defense.

---

## 1. Where Does ML-KEM Decapsulation Begin?
- **Entry Point Function:** [`mlk_kem_dec_monitored()`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c#L403)
- **Source File:** [`algorithms/source_ref/mlkem/src/kem.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c#L399-L435)
- **Execution Role:** Coordinates secret key unpacking, secret key hash verification against FIPS 203 Section 7.3, IND-CPA public key decryption (`mlk_indcpa_dec`), Fujisaki-Okamoto candidate re-encryption, constant-time verification, and implicit rejection key derivation.

---

## 2. Where Are NTT Cooley-Tukey Butterflies Executed?
- **Forward NTT Engine:** [`mlk_poly_ntt_c()`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L475) in [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L475-L509)
  - Evaluates 7 butterfly stages ($128$ butterflies per stage) with Montgomery modular reduction.
- **Inverse NTT Engine:** [`mlk_poly_invntt_tomont_c()`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L617) in [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L617-L655)
  - Transforms frequency-domain polynomials back to standard coordinate representations.

---

## 3. Where Are Twiddle Factors (`zetas`) Defined and Stored?
- **Twiddle Factor Constants:** [`algorithms/source_ref/mlkem/src/zetas.inc`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/zetas.inc)
  - Included directly into the polynomial unit at [`algorithms/source_ref/mlkem/src/poly.c:267`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L267).
- **Relocatable Research Twiddle Page:** Managed via `mlk_zetas_page` and exposed through `mlkem_research_get_zetas_mutable_ptr()` at [`algorithms/source_ref/mlkem/src/poly.c:270-278`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L270-L278) to enable precise, non-destructive software fault injection into volatile table memory.

---

## 4. Where Are Fault Injection Hooks Placed and How Do They Trigger?
- **Hook Definitions & API:** [`algorithms/source_ref/mlkem_fault_hooks.h`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.h#L1-L35)
- **Hook Implementation:** [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c)
- **Trigger Mechanism:** Supports 5 granular injection targets:
  1. `HOOK_TARGET_MID_NTT_BUTTERFLY`: Injects single-bit flips or delta masks mid-butterfly execution.
  2. `HOOK_TARGET_MID_POLYMUL_ACC`: Injects faults during vector accumulation.
  3. `HOOK_TARGET_MID_CBD_SAMPLE`: Injects faults into Centered Binomial Distribution sampling.
  4. `HOOK_TARGET_FO_PREDICATE`: Inverts Fujisaki-Okamoto comparison outputs (Gate A/Gate B).
  5. `mlkem_research_inject_zeta_bit_flip()`: Direct bit flip on target twiddle index.

---

## 5. Where Does the Verifier Circular Dependency Occur?
- **Proof & Reproducer:** [`phase16_targeted_evidence_closure/h1_reproducer.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase16_targeted_evidence_closure/h1_reproducer.c)
- **Phase Documentation:** [`docs/phases/phase-06/README.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/phases/phase-06/README.md)
- **Vulnerability Mechanism:** A naive inverse-NTT sanity verifier recalculates $\mathbf{a}' = \text{InvNTT}(\text{NTT}(\mathbf{a}))$. When twiddle factor table $\zeta$ suffers an SEU bit-flip, both forward and inverse transforms utilize the same corrupted $\zeta$ entries. The error cancels algebraically in the verifier, returning $\mathbf{a}' == \mathbf{a}$ and falsely certifying the corrupted computation as valid.

---

## 6. Where Are TFIB v2 Assertion and Recovery Implemented?
- **Header & Specification:** [`tfib_implementation/tfib_ref.h`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_ref.h)
- **Core Implementation:** [`tfib_implementation/tfib_ref.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_ref.c)
- **Independence Validation:** [`tfib_experiments/test_step2c_countermeasure_independence.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/test_step2c_countermeasure_independence.c)
- **Workflow:**
  1. `tfib_assert_integrity()` computes the lightweight digest of active twiddles and compares with ROM.
  2. If an anomaly is detected, `tfib_restore_from_gold()` restores the table in $< 0.1\ \mu\text{s}$ and increments SEU event counters.

---

## 7. Where Is DMR Implemented and Where Is Overhead Measured?
- **Benchmark Code & Profiles:** [`results/phase7h/processed/phase7h_timing_distribution.json`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase7h/processed/phase7h_timing_distribution.json)
- **Reproducibility Test:** [`tests/phase7k/test_phase7k_reproducibility.py`](file:///Users/dhairyajain/Desktop/pqc%20research/tests/phase7k/test_phase7k_reproducibility.py)
- **Observed Overhead:**
  - Standard ML-KEM-768 Decapsulation baseline: $\approx 8.79\ \mu\text{s}$
  - Full Dual Modular Redundancy (DMR): $+99.33\%$ latency penalty ($\approx 17.52\ \mu\text{s}$)
  - TFIB v2 Assertion: $+2.08\%$ latency penalty ($\approx 8.97\ \mu\text{s}$)

---

## 8. Where Are the Test Suites Located and How to Run Them?
- **C FIPS 203 Known Answer Tests (KATs):**
  ```bash
  ./bin/test_fips_kats
  ```
- **TFIB Step 2C Independence Test Suite (9/9 checks):**
  ```bash
  ./tfib_experiments/test_step2c_countermeasure_independence
  ```
- **Phase 18 Cleanroom Production Reproducer (400 trials):**
  ```bash
  ./phase18_audit/production_reproducer
  ```
- **Python Audit Suites:**
  ```bash
  python3 tests/test_phase4_audit.py
  python3 tests/test_phase5_cross_impl.py
  python3 tests/test_phase6_resilience.py
  python3 tests/phase7k/test_phase7k_reproducibility.py
  ```

---

## 9. Where Are Raw Datasets and Benchmark Scripts Located?
- **Canonical Datasets Manifest:** [`data/manifests/dataset_provenance_manifest.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/data/manifests/dataset_provenance_manifest.csv)
- **Trial-Level Results:** [`tfib_trial_level_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_trial_level_results.csv) (900 trials)
- **Benchmark Raw Latency Data:** [`tfib_benchmark_raw.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_benchmark_raw.csv) (15,000 trials)
- **Cleanroom Trials Data:** [`phase18_audit/raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv) (400 trials)

---

## 10. Where Are Dynamic Allocations (`malloc`) Located or Excluded?
- **Flight Standards Compliance:** Zero dynamic heap allocation (`malloc`/`free` free).
- **Macro Implementation:** [`algorithms/source_ref/mlkem/src/kem.c:412-415`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c#L412-L415) uses `MLK_ALLOC` which binds directly to pre-allocated context buffers or stack arrays in embedded flight configurations.
- **Verification:** Audited in Phase 5 and Phase 18; confirmed stack depth is bounded and invariant.

