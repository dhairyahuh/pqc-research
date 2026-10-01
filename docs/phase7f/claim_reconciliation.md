# Phase 7F — Cross-Phase Claim Reconciliation Matrix

## 1. Overview and Purpose

This document provides a complete, critical reconciliation of all major scientific claims advanced across the project lifecycle (Phases 6 through 7E), evaluated against the findings of the **Phase 7F Independent Audit**.

Every claim is categorized as:
- **Supported:** Validated by both mathematical proof and independent empirical evidence.
- **Partially Supported:** Valid under restricted conditions, but requires significant caveats or scope restrictions.
- **Contradicted:** Disproven by independent mathematical analysis or empirical testing.
- **Unverified:** Asserted in earlier reports without sufficient experimental or code-level support.

---

## 2. Master Claims Reconciliation Matrix

| Phase | Original Claim | Evidence Source | Phase 7F Independent Validation | Audit Status | Defensible Paper Formulation |
|---|---|---|---|---|---|
| **Phase 6** | Sensitivity-guided targeted checks reduce fault sensitivity at lower overhead than full redundancy. | `experiments/phase6/` | Confirmed that targeted checks on NTT and FO gates reduce failure rates; however, simple projection checks leave substantial blind spots for non-linear corruptions. | **Supported** (with bounded scope) | "Targeted algorithmic invariants provide selective error detection at substantially lower overhead than duplicate execution, but leave class-specific blind spots." |
| **Phase 7** | Layered decapsulation protects against intermediate arithmetic faults in ML-KEM. | `experiments/phase7/` | Phase 7B audit revealed that Phase 7 decapsulation relied on an external `expected_ss` test oracle. | **Partially Supported** (historically flawed) | "Initial prototypes demonstrated layered protection principles, but required subsequent refactoring to eliminate test-oracle dependence." |
| **Phase 7C** | Oracle-free native decapsulation monitoring achieves 100% fault containment. | `experiments/phase7c/` | Verified that `expected_ss` oracle was fully removed from decapsulation. However, Phase 7D audit showed Phase 7C introduced a major timing side-channel on invalid ciphertexts (1.83x latency). | **Partially Supported** | "Native in-tree decapsulation monitoring operates without an external oracle, but unmitigated conditional branches created a timing side-channel on invalid ciphertexts." |
| **Phase 7D** | Timing leak on invalid ciphertexts remediated; constant-time restored (1.00x). | `experiments/phase7d/` | Benchmarks on 2,000 valid vs 2,000 invalid ciphertexts confirm identical latency ($51.5\ \mu\text{s}$ vs $51.5\ \mu\text{s}$, ratio 1.000x). | **Supported** | "Evaluating ciphertext equality via dual-rail reverse accumulation ensures constant-time execution across both valid and invalid ciphertexts." |
| **Phase 7D** | Class 6 (checker perturbation) harness flaw identified; zeta table defect corrected. | `experiments/phase7d/` | Verified that Phase 7C tested checker perturbations with an uninitialized pointer, and Layer 7 inverse zeta table was expanded from 64 to 128 elements in Phase 7D. | **Supported** | "Independent auditing resolved experimental harness defects, including uninitialized checker pointers and truncated twiddle tables." |
| **Phase 7D** | NTT recovery is limited to 14.3% because Layer 7 checks fail on Layers 1–6 faults. | `experiments/phase7d/` | Mathematically proven: butterfly invariants are step invariants. Errors in layer $l$ diffuse to downstream layers, which compute valid transitions on corrupted data. | **Supported** | "Terminal-stage NTT checks cannot recover early-stage intermediate faults because downstream butterfly operations perform algebraically valid transformations on corrupted state." |
| **Phase 7E** | Dual butterfly invariant ($\mathcal{I}_{\text{diff}} \land \mathcal{I}_{\text{sum}}$) has zero algebraic blind spots ($\ker = \{(0,0)\}$). | `experiments/phase7e/` | **Partially Supported.** The kernel is trivial for independent output register perturbations $(u', v')$. However, if intermediate product $t$ is reused to achieve zero multiplications, the checker is **100% blind to multiplier and twiddle faults**. | **Partially Supported** (Crucial Caveat) | "The dual butterfly invariant eliminates all output-register blind spots, but detecting multiplier execution faults requires independent recomputation of intermediate products." |
| **Phase 7E** | Stage-specific monitoring achieves 100% autonomous fault recovery across Layers 1–7. | `results/phase7e/` | **Partially Supported (Simulation Artifact).** In the Phase 7E harness, `mlkem768_poly_ntt_stage_monitored` was bypassed by passing `opt_time_poly = NULL`. Recovery was simulated by setting `flg_e = MLK_STATUS_FAULT` and resetting hooks during retry. | **Partially Supported** | "Architectural simulation indicates that stage-specific fault identification enables 100% recovery of transient butterfly faults via localized re-execution, provided detection occurs before diffusion." |
| **Phase 7E** | Monitoring all 7 layers adds zero extra multiplications and costs only +20.26% overhead. | `results/phase7e/` | **Contradicted in detail.** The +20.26% overhead was measured with NTT checks bypassed (`opt_time_poly = NULL`). Independent microbenchmarking shows active 7-layer monitoring increases single-poly NTT by 4.05 µs (+1,867%), adding $\approx 12\ \mu\text{s}$ (+28.2% total overhead) to decapsulation. | **Contradicted** (Re-quantified) | "Evaluating dual invariants across all 2,688 butterflies adds $\approx 12\ \mu\text{s}$ (+28% overhead) to decapsulation, significantly outperforming duplicate execution (+100%) while incurring measurable arithmetic cost." |
| **All Phases** | Undetected corrupted session key release is 0.0% ($R_U = 0.0\%$). | Raw trial records | Verified across all 1,200 trials (Phase 7C), 1,200 trials (Phase 7D), and 1,050 trials (Phase 7E). Zero corrupted keys were released. | **Supported** | "The multilayered architecture, anchored by Fujisaki-Okamoto re-encryption, provides strict fail-safe behavior ($R_U = 0.0\%$) across all tested fault models." |

---

## 3. Detailed Audit of Critical Controversies

### 3.1 The $t$-Reuse Dilemma: Performance vs Fault Coverage
- **The Tradeoff:**
  - *Option A (Reused $t$):* Cost is 0 extra modular multiplications. Overhead is low. Detects output register flips and adder/subtractor errors. Completely blind to multiplier ALU errors and twiddle corruptions.
  - *Option B (Recomputed $t$):* Doubles modular multiplications in the NTT. Overhead increases by $\approx 12\ \mu\text{s}$. Detects 100% of multiplier and twiddle corruptions.
- **Scientific Resolution:** The publication must present this as a formal Pareto frontier between arithmetic verification overhead and fault-locus coverage, rather than claiming universal detection without cost.

### 3.2 Evaluation Methodology: Simulation vs Native Integration
- Phase 7E created an isolated C prototype `mlkem768_poly_ntt_stage_monitored()` but evaluated multi-layer recovery via simulation flags in the top-level harness.
- This distinction must be made explicit in the paper: Phase 7E demonstrates the *architectural efficacy* of per-stage recovery assuming localized detection, while Phase 7F quantifies the *realized instruction overhead* of the native butterfly monitor.
