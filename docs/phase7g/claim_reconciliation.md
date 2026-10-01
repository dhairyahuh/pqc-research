# Master Cross-Phase Claim Reconciliation Matrix (Phases 6 – 7G)

## 1. Longitudinal Overview & Scientific Context

This document maintains the historical progression of fault resilience claims across the research campaign. No past findings or audit defects are deleted or rewritten; rather, each claim is tracked to its current status based on empirical evidence.

---

## 2. Master Claims Reconciliation Matrix

| Claim ID | Specific Claim | Originating Phase | Status After Phase 7E | Audit Status in Phase 7F | Definite Status in Phase 7G | Evidence / Technical Basis |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CLM-01** | Classical and PQC KEMs experience catastrophic session key divergence under single-bit memory faults | Phase 6 | Empirically Supported | Validated | **Fully Validated** | Standard ML-KEM without monitoring fails into $K_{\text{rej}}$ (>97%) upon internal fault. |
| **CLM-02** | Layered fault detection without an oracle is achievable in native decapsulation | Phase 7C | Supported | Validated | **Fully Validated** | Ciphertext re-encryption and reverse dual-rail flags eliminate oracle dependency. |
| **CLM-03** | Constant-time execution is preserved during fault detection | Phase 7C / 7D | Supported | Partially Qualified | **Validated with Bounds** | Valid vs Invalid ciphertext latency ratio is 1.000x ($53.89\ \mu\text{s}$ vs $53.89\ \mu\text{s}$). |
| **CLM-04** | Dual butterfly difference invariants achieve 100% recovery across all NTT layers | Phase 7E | Claimed 100% | **Contradicted** (Defective Simulation & Multiplier Blind Spot) | **Reconciled & Qualified**: Supported **only** with Recomputed-$t$ on ALU/output register faults; **0% recovery** on twiddle/input faults. | Phase 7G proves Reused-$t$ has a blind spot on $t$ (4% recovery). Recomputed-$t$ achieves 100% on Class 1, 3, 4. |
| **CLM-05** | Intermediate $t$-reuse provides fault detection with zero extra multiplication cost | Phase 7E | Claimed | **Contradicted** (Blind Spot on $t$) | **Refuted**: Cannot detect faults in $t$ | Reused-$t$ results in $D \equiv 0$ even when $t$ is corrupted, causing silent bypass. |
| **CLM-06** | Stage-monitoring overhead is +20.26% vs +100.12% for DMR | Phase 7E | Claimed +20.26% | **Contradicted** (Monitoring bypassed in benchmark) | **Recomputed in Native Code**: Reused-$t$ is **+12.35%**, Recomputed-$t$ is **+15.37%** vs DMR **+100.03%** | Phase 7G instrumented all 5,376 native butterflies during decapsulation and measured real overhead. |
| **CLM-07** | ML-KEM protocol prevents undetected corrupted key release | Phases 7C–7F | Supported | Validated | **Empirically Proven**: $R_U = 0.00\%$ over 1,200 trials | Even when butterfly monitor misses (e.g. Class 2), FO re-encryption forces safe rejection. |
| **CLM-08** | In-place butterfly rollback can recover from persistent hardware faults | Proposed | Rejected | Rejected | **Physically Infeasible & Rejected** | Class 6 experiments show persistent faults fail retry; system safely fails-closed to $K_{\text{rej}}$. |

---

## 3. Detailed Reconciliation of Phase 7E Headline Claims

### Claim 1: "100% Autonomous Recovery Across All NTT Layers"
- **Phase 7E Statement**: Dual invariants enable 100% autonomous recovery across all NTT layers (1,050 trials).
- **Phase 7F Finding**: Trials were executed with `NULL` callbacks in production decapsulation; test runner used simulated status flags; intermediate $t$-reuse had an unacknowledged mathematical blind spot on $t$.
- **Phase 7G Resolution**:
  - Reused-$t$ achieves only **4.00% recovery** on multiplier faults (identical to baseline noise).
  - Recomputed-$t$ achieves **100.00% recovery** on multiplier faults (Class 1) and output register faults (Classes 3 & 4).
  - Faults in twiddle factors (Class 2), inputs (Class 5), or hardware (Class 6) achieve **0.00% recovery** and are instead safely rejected.
  - **Scientific Conclusion**: 100% recovery is physically valid **only** for transient arithmetic faults in the butterfly execution unit (when using Recomputed-$t$), not for all possible NTT-stage faults.

### Claim 2: "+20.26% Decapsulation Overhead"
- **Phase 7E Statement**: Decapsulation latency increased by +20.26%, compared to +100.12% for DMR.
- **Phase 7F Finding**: Production decapsulation was compiled without calling the monitor, so the reported +20.26% was an artifact of test harness wrapping or microbenchmarking.
- **Phase 7G Resolution**:
  - Decapsulation was measured with all 5,376 native butterflies evaluated in-tree.
  - Reused-$t$ overhead: **+12.35%** ($52.48\ \mu\text{s}$ vs $46.71\ \mu\text{s}$).
  - Recomputed-$t$ overhead: **+15.37%** ($53.89\ \mu\text{s}$ vs $46.71\ \mu\text{s}$).
  - DMR overhead: **+100.03%** ($93.43\ \mu\text{s}$ vs $46.71\ \mu\text{s}$).
  - **Scientific Conclusion**: Native in-tree monitoring is actually **more efficient** than Phase 7E estimated, providing complete transient ALU fault recovery at only +15.37% overhead (a 6.5x reduction relative to DMR).
