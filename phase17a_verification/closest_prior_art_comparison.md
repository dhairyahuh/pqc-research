# Closest Prior-Art Comparison: Mechanism-Level Analysis

**Date:** October 2026  
**Purpose:** Compare the actual mechanisms of the three closest prior works with this work to identify genuine vs. superficial differentiation.

---

## 1. Paul et al. (P03) — AIC for NTT on FPGA (ACM TECS, 2026)

### What They Actually Do
- Derive **algebraic invariant checks (AIC)** for the Cooley-Tukey forward NTT butterfly.
- Specifically, they compute invariant relationships between butterfly inputs and outputs and verify them using additional FPGA logic.
- Two variants: **FR-AIC** (full recomputation-based, higher detection rate) and **PR-AIC** (partial, lower overhead).
- Target: **FPGA-based NTT accelerators** for PQC (Kyber/Dilithium) and FHE.
- On fault detection: **abort** (error flag).
- Overhead: +8.5% to +21.4% FPGA LUT utilization.

### What They Do NOT Do
- Do not cover the Gentleman-Sande inverse NTT.
- Do not implement any recovery or rollback mechanism.
- Do not operate in software.
- Do not evaluate in the context of full KEM decapsulation or the FO transform.

### Mechanism Overlap With This Work
- **HIGH.** The mathematical principle is the same: verify algebraic relationships between butterfly inputs and outputs. The CT sum invariant `r0 + r1 = 2u (mod q)` is essentially what both works exploit, though the specific formulation and implementation differ.
- The extension from CT to GS is mathematically straightforward (substitute the GS butterfly equations and derive analogous invariants). This does not require deep mathematical insight but does require explicit derivation and implementation.

### Honest Differentiation
| Dimension | Paul et al. (P03) | This Work |
|:---|:---|:---|
| Transform coverage | Forward CT only | Forward CT + Inverse GS |
| Platform | FPGA hardware | Software (C) |
| On detection | Abort | Rollback + retry (transient) / fail-stop (persistent) |
| Full KEM integration | No | Yes (within FIPS 203 ML-KEM-768 decapsulation) |
| Recovery | None | 100/100 under transient faults |

### Assessment
The differentiation is **genuine but incremental**. The mathematical invariant principle is not novel to this work. The contributions are: (1) the GS inverse NTT derivation, (2) software implementation, (3) recovery mechanism, and (4) full KEM integration. A reviewer could reasonably characterize contributions (1) and (2) as engineering extensions. Contributions (3) and (4) provide the substantive novelty.

---

## 2. Sarker et al. (P04) — Error Detection for NTT (IEEE TCAD, 2023)

### What They Actually Do
- Propose **RESO (Recomputing with Shifted Operands)** and **residue code** techniques for error detection in NTT hardware.
- Detect faults by re-executing NTT computations with operand transformations and comparing results.
- Target: **FPGA/ASIC** hardware implementations.
- Overhead: +18% to +34% FPGA area.

### What They Do NOT Do
- Do not cover inverse NTT.
- Do not implement recovery.
- Do not operate in software.
- The RESO technique is fundamentally different from algebraic invariant checking — it uses operand shifting, not butterfly sum/difference verification.

### Mechanism Overlap With This Work
- **LOW.** RESO is a different detection technique from algebraic invariant checking. The only overlap is the shared goal of detecting NTT computation errors.

### Assessment
This work is **complementary**, not overlapping. It validates that NTT error detection is an active research area, but the detection mechanism is different.

---

## 3. SWIFT (P12) — Software Implemented Fault Tolerance (CGO, 2005)

### What They Actually Do
- Compiler-level instruction duplication for generic software on x86/IA-64.
- Duplicate instructions, compare results, and trap on mismatch.
- Control flow checking via signature validation.
- +41% average execution overhead with high register pressure.

### What They Do NOT Do
- No awareness of cryptographic algebraic structure.
- No NTT-specific invariants.
- No concept of rollback (detection only → trap).
- No integration with any KEM or cryptographic protocol.

### Mechanism Overlap With This Work
- **CONCEPTUAL ONLY.** Both are software-level fault tolerance. But SWIFT is generic instruction duplication while this work uses domain-specific algebraic invariants. The +25.3% overhead vs. +41% comparison is meaningful.

### Assessment
SWIFT is a **baseline comparison point**, not prior art that threatens novelty. The domain-specific algebraic invariant approach is fundamentally different from blind instruction duplication.

---

## 4. Fritzmann et al. (P13) — PQC on RISC-V (DATE 2019 / TCHES 2020)

### Verification Problem
The reference as cited in Phase 17 — "Fault-Tolerant PQC on RISC-V, IEEE Access 2020, DOI: 10.1109/ACCESS.2020.3014761" — **could not be verified**. Web searches return:
1. "Towards Reliable and Secure Post-Quantum Co-Processors based on RISC-V" (DATE 2019)
2. "RISQ-V: Tightly Coupled Accelerators for PQC" (TCHES 2020)

Neither matches the title, venue, or DOI listed. The DOI does not resolve.

### What the DATE 2019 Paper Actually Does (Best Match)
- Fault analysis via simulation-based injection on RISC-V NTT co-processor.
- Measures SDC rate (3.66%–4.96% for different NTT variants).
- Detection via CPU exception handling.
- No algebraic invariant checking.
- No rollback or recovery mechanism.

### Assessment
If the correct paper is the DATE 2019 work, it provides **vulnerability analysis without defenses** — making it a motivation paper, not a defense to compare against. The manuscript's claim that "Fritzmann et al. stops at detection-only abort" must be verified against the actual paper, which may only measure SDC rates without implementing any explicit detection scheme.

---

## 5. Summary: Novelty Position

| Dimension | Status |
|:---|:---|
| CT butterfly invariant principle | **NOT NOVEL** — used by Paul et al. (P03) on FPGA |
| GS inverse NTT invariant derivation | **Novel derivation** (not identified in any prior PQC work) |
| Software implementation of NTT invariants | **Novel platform** (all prior work is FPGA/ASIC) |
| Localized single-butterfly rollback | **Novel mechanism** (no prior PQC work implements recovery) |
| H₁ circular verifier blindness | **Novel observation in PQC context** (underlying common-mode failure principle is established) |
| Integration with FIPS 203 FO implicit rejection | **Novel architectural combination** |
| End-to-end zero SDC under software fault injection | **Novel empirical result** |

**Overall: The work has genuine novelty in the combination, but the manuscript must not overstate the mathematical novelty of the butterfly invariant principle itself.**
