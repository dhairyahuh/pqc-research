# Open Issues, Scientific Boundaries & Decision Log

**Repository:** `pqc-research`  
**Active Branch:** `space-resilience-framework`  
**Author:** Dhairya Jain  
**Handover Recipient:** Ayush  
**Date:** October 2026  

This document logs all fundamental research decisions made during the project, enumerates the residual uncertainties that cannot be resolved from existing evidence, and details the explicit scientific boundaries that Ayush must preserve.

---

## 1. Architectural & Methodological Decisions Log

| Decision ID | Decision Scope | Rationale & Evidence | Impact on Repository & Publication |
| :--- | :--- | :--- | :--- |
| **DEC-01** | Focus Primary Publication on Paper Track 1 | Internal NTT arithmetic resilience is backed by 400 production trials, 900 campaign trials, 600 circular verifier trials, and microsecond rollback. Paper Track 2 (spacecraft protocol simulation) lacked independent empirical channel data. | `paper/manuscript.md` focuses exclusively on Track 1. Track 2 code is preserved in `experiments/system_model/` for future work. |
| **DEC-02** | Decouple Inverse NTT Invariant Checks | Classical GS invariant requires division by $\zeta \pmod q$ or computing $\zeta^{-1} \pmod q$, which is computationally prohibitive in software. Formulated decoupled checks: Adder Rail ($r_0 \equiv u+v$) and Multiplier Rail ($r_1 \equiv (v-u)\zeta$). | Achieves 100% single-rail arithmetic fault detection without runtime modular division overhead. |
| **DEC-03** | Enforce Strict 2-Retry Escalation Limit | Infinite retry loops under persistent physical defects (e.g., stuck-at-1 latches) cause Denial-of-Service and catastrophic timing leakage. Enforcing `retry_count < 2` guarantees prompt fail-stop escalation. | Validated in 200/200 persistent trials (F5A, F5B); deterministically emits $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$. |
| **DEC-04** | Dual-Rail Reverse-Order FO Comparison | Single-event upsets striking comparison flags (`fail = 0`) can bypass rejection. Implementing forward `memcmp` paired with reverse-order bitwise accumulation (`fail_chk`) prevents single-point predicate circumvention. | Implemented in `algorithms/source_ref/mlkem/src/kem.c` (Lines 476–504). |
| **DEC-05** | Qualify Zero Dynamic Allocation Claim | Static inspection of C source reveals zero `malloc`/`free` calls in the monitoring and rollback routines. However, runtime guarantees depend on compiler flags and memory layout. | Table 4 footnote was surgically qualified in Phase 2R.3 to source inspection under the evaluated configuration. |
| **DEC-06** | Preserve All Raw Artifacts & Backups | Moving or deleting historical folders (`deploy_perf_bundle/`, `phase*`) risks breaking relative paths in existing audit scripts. | All 9 manuscript backups and all 19 root-level phase directories are preserved intact. |
| **DEC-07** | Conclude Manuscript Correction Cycle at Phase 2S | All 14 material manuscript claims are fully supported and recomputed. Further edits risk cosmetic churn or desynchronization. | Verdict: **READY WITH EXPLICIT LIMITATIONS**. Ayush should proceed with layout compilation, not text revision. |

---

## 2. Residual Uncertainties & Scientific Boundaries

The following technical boundaries cannot be resolved from existing repository data and must be maintained as explicit limitations:

### 2.1 Unpersisted Raw Latency Samples
- **Issue:** Individual iteration timings for the $N = 2,000$ warm decapsulations were logged to stdout summaries rather than saved as raw CSV distributions on disk.
- **Evidence Reference:** Table 4 footnote 1; `results/phase7i/processed/phase7i_e2e_results.json`.
- **Severity:** Minor / Disclosed.
- **Guidance for Ayush:** Do not attempt to synthesize raw per-iteration samples. Cite the summary mean ($129.51\,\mu\text{s}$ vs $110.77\,\mu\text{s}$) and transparently state that per-iteration raw samples were not persisted to disk.

### 2.2 Dynamic Stack Memory Utilization
- **Issue:** Runtime stack frame expansion during snapshotting and rollback was not instrumented with hardware canaries or high-water marks.
- **Evidence Reference:** `paper/manuscript.md` line 358.
- **Severity:** Minor / Future Work.
- **Guidance for Ayush:** Frame stack profiling as future embedded work when porting to RAM-constrained ARM Cortex-M4 (e.g., 64 KB RAM) platforms.

### 2.3 Microarchitectural Constant-Time Behavior
- **Issue:** Source-level branch-free primitives (e.g., `mlk_ct_cmask_nonzero_u8`, `mlk_ct_cmov_zero`) were audited in C, but compiled binaries have not been tested for side-channel timing leakage using TVLA (Test Vector Leakage Assessment) or `dudect`. Furthermore, detecting a fault conditionally branches into retry rollback.
- **Evidence Reference:** `paper/manuscript.md` Section 7 Item 4.
- **Severity:** Major / Explicit Boundary.
- **Guidance for Ayush:** Never claim certified constant-time execution in either fault-free or active-fault execution. Maintain the explicit disclaimer that this architecture is intended for non-adversarial radiation and functional reliability contexts.

### 2.4 Software Fault Simulation vs. Physical Radiation
- **Issue:** Software bitflips model the architectural consequence of an upset latched into CPU registers. They do not simulate analog transients, charge collection, or multi-cell upsets (MCUs).
- **Evidence Reference:** Dodd & Massengill [P01]; `paper/manuscript.md` Section 2.2 and Section 7 Item 5.
- **Severity:** Major / Scientific Boundary.
- **Guidance for Ayush:** Strictly avoid claiming "radiation hardness," "spaceflight qualification," or "measured in-beam SEU cross-sections." State clearly that physical cyclotron beam testing is required for flight certification.

### 2.5 Twiddle Factor Memory Corruption Pilot Scope
- **Issue:** Phase 15Q evaluated 16 trials on a single reference vector, validating FO containment across 11 active consumed mutations.
- **Evidence Reference:** `results/phase15q/trial_ledger.csv`.
- **Severity:** Moderate / Disclosed Scope.
- **Guidance for Ayush:** Do not claim universal statistical protection across all possible keys and ciphertexts for twiddle table corruption. Maintain the exact framing that Phase 15Q was an exploratory pilot on an evaluated reference vector.

### 2.6 Desktop ARM64 vs. Embedded Platform Target
- **Issue:** Benchmarks were recorded on Apple M3 Pro (macOS Darwin 25.1.0). Target platforms for satellite payloads are typically 32-bit embedded microcontrollers (e.g., ARM Cortex-M4, RISC-V RV32IM, or LEON3/SPARC).
- **Evidence Reference:** `paper/manuscript.md` Section 5.1, Section 8 Item 2.
- **Severity:** Moderate / Future Roadmap.
- **Guidance for Ayush:** Prioritize compiling and profiling the resilience engine on an ARM Cortex-M4 emulator or physical board.
