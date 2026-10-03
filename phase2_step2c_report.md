# Phase 2 Step 2C-A: Countermeasure Independence and Common-Mode Fault Analysis Report

**Auditor / Researcher:** Skeptical Cryptographic Software Verification Specialist  
**Target:** ML-KEM-768 with Two-Factor Invariant Butterfly (TFIB) Countermeasure  
**Repository Working Tree:** `55dd937cbad66b24e5c2c0b89b78fa776801913c` (branch `space-resilience-framework`)  
**Status:** Verification Complete — Conditional Pass (Software Model Validated; Physical Common-Mode Remains Open)  
**Date:** 2026-10-04  

---

## 1. Executive Summary & Central Research Question

This report documents the rigorous investigation of **Phase 2 Step 2C-A**, addressing the central research question:
> **How does shared state or shared fault exposure between the ML-KEM computation and its countermeasure affect fault detection, recovery, and end-to-end correctness?**

Prior audits established that under single-point operational twiddle perturbations, TFIB-REF achieves 100% detection and genuine recovery, while TFIB-META achieves 100% detection and safe fail-stop. This step investigates the **independence boundary**:
1. Does the countermeasure detect faults that target the checker itself rather than the computation?
2. What happens when computation and countermeasure share corrupted state (common-mode failure)?
3. Can an escape from the local arithmetic monitor lead to Silent Data Corruption (SDC), or does the outer Fujisaki-Okamoto (FO) transform contain the failure?

### High-Level Verdict Summary
- **Independence of Storage:** `mlk_zetas` (operational) and `tfib_zetas_ref` (checker) occupy separate read-only memory addresses (`0x1000188a0` vs `0x100018a60`), proving spatial independence within the software binary image.
- **Checker Degradation Robustness:** Corrupting checker-only state or decision logic never induces SDC. Transient checker faults trigger benign retry and recover; persistent checker faults force a safe fail-stop.
- **Simultaneous Common-Mode Failure:** When an identical bit-flip corrupts both operational and reference twiddles, **local monitor detection is 0.0%** ($0/50$ detected). The invariant equations hold over the corrupted value.
- **Outer Cryptographic Safety Net:** Despite 0.0% local detection during common-mode failure, **100% of trials are contained** by the outer Fujisaki-Okamoto re-encryption check, which detects the ciphertext mismatch and outputs the canonical implicit rejection key $K_{\text{rej}}$ ($0$ SDC across 900 trials).

---

## 2. Phase 0 Audit: Architectural Pathways & Dependency Analysis

Through static inspection and binary disassembly of `bin/obj/mlkem768_inst.o`, `tfib_implementation/libtfib.a`, and `tfib_experiments/tfib_experiment_runner`, the operational and verification pathways were mapped:

### 2.1 Operational vs Reference Twiddle Storage
- **Operational Twiddles:** Defined as `static MLK_ALIGN const int16_t mlk_zetas[128]` in `algorithms/source_ref/mlkem/src/zetas.inc`. Stored at `0x1000188a0` in `__TEXT,__const`.
- **Reference Twiddles:** Defined as `const int16_t tfib_zetas_ref[TFIB_ZETA_COUNT]` in `tfib_implementation/tfib_ref.c`. Stored at `0x100018a60` in `__TEXT,__const`.
- **Finding:** While identical in numerical values, they reside in distinct static arrays in separate translation units. A single-word memory corruption targeting one array cannot alter the other in software memory.

### 2.2 Indexing Independence
- Primary computation advances pointers sequentially: $k++$ in forward NTT, $k--$ in inverse NTT.
- Countermeasure recomputes the index algebraically from the butterfly coordinates:
  $$k = (1 \ll (\text{layer} - 1)) + (\text{b\_idx} \gg (8 - \text{layer}))$$
- **Finding:** If an off-by-one or pointer-skipping fault occurs in the operational loop, the checker recalculates the expected twiddle independently, causing $\zeta_{\text{op}} \neq \zeta_{\text{ref}}$, which flags an immediate mismatch.

### 2.3 Shared State and Couplings
1. **Shared Polynomial Buffer (`r`):** Caller-allocated coefficient array modified in-place by butterfly arithmetic and monitored/repaired by the checker.
2. **Shared Caller Stack Frame:** `u_saved` and `v_saved` are saved on the stack of `mlk_ntt_layer` immediately before the butterfly hook and passed by value to the monitor.
3. **Shared Algebraic Modulus:** $q = 3329$ and Montgomery constant $R \equiv 2^{16} \pmod q$ are shared across all arithmetic functions.
4. **Shared Control Flow / Global Mode:** `g_tfib_mode` and `g_tfib_fault` govern dispatch and fault simulation.

---

## 3. Experimental Methodology & Suite Taxonomy

A dedicated test suite (`test_step2c_countermeasure_independence.c`) and a comprehensive 900-trial experimental campaign were executed using domain-separated deterministic PRF inputs (`campaign_prf.h`) and the independent reference oracle (`libindependent_oracle.a`).

### 3.1 Taxonomy of Evaluated Suites (18 Suites, 50 Trials Each)

| Suite Family | Configuration | Injection Target | Persistence | Trials |
| :--- | :--- | :--- | :--- | :--- |
| **Control** | BASELINE, TFIB_REF, TFIB_META | None (`TFIB_FAULT_NONE`) | False | 150 |
| **Primary Only** | BASELINE, TFIB_REF, TFIB_META | Operational twiddle $\zeta_{\text{op}}$ | Transient & Persistent | 300 |
| **Checker Only** | TFIB_REF | Reference twiddle $\zeta_{\text{ref}}$ | Transient & Persistent | 100 |
| **Checker Only** | TFIB_META | Precomputed metadata tag | Transient & Persistent | 100 |
| **Checker Logic** | TFIB_REF, TFIB_META | Monitor evaluation predicate (`sum_c ^= 1`) | Transient & Persistent | 200 |
| **Common-Mode** | TFIB_REF | Both $\zeta_{\text{op}}$ and $\zeta_{\text{ref}}$ with identical bit-flip | Transient | 50 |

Total: **900 trials** ($150$ clean baseline + $750$ fault-activated trials).

---

## 4. Quantitative Results & Statistical Analysis

### 4.1 Comprehensive Outcome Breakdown (900 Trials)

```
Config     | Suite                      | Total | Activated | Detected | Recovered | Fail-Stop | FO Contained | Ineffective | SDC
-----------+----------------------------+-------+-----------+----------+-----------+-----------+--------------+-------------+-----
BASELINE   | CLEAN_CONTROL              | 50    | 0         | 0        | 0         | 0         | 0            | 0           | 0
BASELINE   | OP_TWIDDLE_TRANSIENT       | 50    | 50        | 0        | 0         | 0         | 48           | 2           | 0
BASELINE   | OP_TWIDDLE_PERSISTENT      | 50    | 50        | 0        | 0         | 0         | 50           | 0           | 0
TFIB_REF   | CLEAN_CONTROL              | 50    | 0         | 0        | 0         | 0         | 0            | 0           | 0
TFIB_REF   | OP_TWIDDLE_TRANSIENT       | 50    | 50        | 50       | 50        | 0         | 0            | 0           | 0
TFIB_REF   | OP_TWIDDLE_PERSISTENT      | 50    | 50        | 50       | 0         | 50        | 0            | 0           | 0
TFIB_REF   | REF_TWIDDLE_TRANSIENT      | 50    | 50        | 50       | 50        | 0         | 0            | 0           | 0
TFIB_REF   | REF_TWIDDLE_PERSISTENT     | 50    | 50        | 50       | 0         | 50        | 0            | 0           | 0
TFIB_REF   | SIMULTANEOUS_COMMON_MODE   | 50    | 50        | 0        | 0         | 0         | 49           | 1           | 0
TFIB_REF   | CHECKER_LOGIC_TRANSIENT    | 50    | 50        | 50       | 50        | 0         | 0            | 0           | 0
TFIB_REF   | CHECKER_LOGIC_PERSISTENT   | 50    | 50        | 50       | 0         | 50        | 0            | 0           | 0
TFIB_META  | CLEAN_CONTROL              | 50    | 0         | 0        | 0         | 0         | 0            | 0           | 0
TFIB_META  | OP_TWIDDLE_TRANSIENT       | 50    | 50        | 50       | 0         | 50        | 0            | 0           | 0
TFIB_META  | OP_TWIDDLE_PERSISTENT      | 50    | 50        | 50       | 0         | 50        | 0            | 0           | 0
TFIB_META  | META_TAG_TRANSIENT         | 50    | 50        | 50       | 50        | 0         | 0            | 0           | 0
TFIB_META  | META_TAG_PERSISTENT        | 50    | 50        | 50       | 0         | 50        | 0            | 0           | 0
TFIB_META  | CHECKER_LOGIC_TRANSIENT    | 50    | 50        | 50       | 50        | 0         | 0            | 0           | 0
TFIB_META  | CHECKER_LOGIC_PERSISTENT   | 50    | 50        | 50       | 0         | 50        | 0            | 0           | 0
-----------+----------------------------+-------+-----------+----------+-----------+-----------+--------------+-------------+-----
TOTAL      | 18 Suites                  | 900   | 750       | 600      | 250       | 350       | 147          | 3           | 0
```

---

### 4.2 Explicit Metric Definitions and Rates

To adhere strictly to cryptographic auditing standards, every denominator is defined explicitly:

1. **Total Campaign Trials:** $N_{\text{total}} = 900$
2. **Clean Baseline Trials:** $N_{\text{clean}} = 150$ (False alarm rate: $0/150 = 0.0\%$, 95% CI $[0.0\%, 2.45\%]$)
3. **Fault-Activated Trials:** $N_{\text{act}} = 750$
4. **Independent Fault Trials (Excluding Baseline & Common-Mode):** $N_{\text{indep}} = 600$
   - Operational faults, checker-only faults, and checker logic faults in TFIB-REF and TFIB-META.
   - **Local Detection Rate:** $600 / 600 = \mathbf{100.0\%}$ (95% CI $[99.38\%, 100.0\%]$).
5. **Recovery Rate:**
   - Evaluated over detected transient repairable trials in TFIB-REF (Op twiddle, Ref twiddle, Checker logic): $150 / 150 = \mathbf{100.0\%}$ (95% CI $[97.55\%, 100.0\%]$).
   - Evaluated over detected transient tag/logic trials in TFIB-META: $100 / 100 = \mathbf{100.0\%}$ (95% CI $[96.34\%, 100.0\%]$).
   - In TFIB-META under operational twiddle faults: $0 / 100 = \mathbf{0.0\%}$ (expected: TFIB-META has no repair table and must fail-stop).
6. **Safe Fail-Stop Rate:**
   - Evaluated over detected persistent faults in TFIB-REF: $150 / 150 = \mathbf{100.0\%}$ (95% CI $[97.55\%, 100.0\%]$).
   - Evaluated over detected persistent or non-repairable faults in TFIB-META: $200 / 200 = \mathbf{100.0\%}$ (95% CI $[98.15\%, 100.0\%]$).
7. **Simultaneous Common-Mode Failure Detection Rate:**
   - Evaluated over $N_{\text{simul}} = 50$: $0 / 50 = \mathbf{0.0\%}$ (95% CI $[0.0\%, 7.11\%]$).
   - **Local Blindness Confirmed:** When both twiddles share identical bit-flips, the checker cannot detect the fault locally.
8. **Cryptographic FO Containment Rate (Under Local Monitor Blindness):**
   - In Baseline ($N=100$) + Simultaneous ($N=50$): $147$ trials triggered canonical rejection key $K_{\text{rej}}$ via FO re-encryption failure, and $3$ trials were ineffective (perturbation absorbed by ML-KEM noise slack, decoding correct message $m$).
   - **Safe Containment Rate:** $150 / 150 = \mathbf{100.0\%}$ (95% CI $[97.55\%, 100.0\%]$).
9. **Silent Data Corruption (SDC) Rate:**
   - Denominator: All fault-activated trials ($N_{\text{act}} = 750$).
   - SDC Events: $0 / 750 = \mathbf{0.0\%}$.
   - **Rule-of-Three Upper Bound:** With 0 observed events in 750 trials, the true SDC rate $p_{\text{SDC}} < \frac{3}{750} \approx \mathbf{0.40\%}$ at 95% confidence (Wilson score upper bound: $0.49\%$).
   - **Critical Audit Caveat:** Zero observed SDC does **not** prove zero theoretical risk under arbitrary physical fault injections.
10. **Invalid / Inconclusive Trials:** $0 / 900 = 0.0\%$.

---

### 4.3 Runtime and Memory Overhead

As measured empirically in `tfib_benchmark_results.csv`:
- **Baseline (Original Monitor):** $114.43\ \mu\text{s}$ mean execution time (Reference: $0.0\%$ overhead, 20 bytes stack).
- **TFIB-REF (Strategy 1):** $138.01\ \mu\text{s}$ mean execution time ($+20.61\%$ computational overhead, $+548$ bytes static table storage).
- **TFIB-META (Strategy 2):** $136.30\ \mu\text{s}$ mean execution time ($+19.11\%$ computational overhead, $+548$ bytes static tag storage).

---

## 5. Epistemological Separation: Observed vs Inferred vs Unverified

To maintain rigorous scientific standards, claims are categorized by their evidential status:

### 5.1 Directly Observed Results (Empirical Ground Truth)
1. In software execution on the host architecture (macOS ARM64), `mlk_zetas` and `tfib_zetas_ref` reside at distinct memory offsets in `__TEXT,__const`.
2. When faults are injected exclusively into `zeta_ref`, `tfib_zetas_tag`, or checker arithmetic predicates, the checker detects the condition, initiates rollback/retry, and either recovers (if transient) or safely fail-stops (if persistent).
3. When `TFIB_FAULT_SIMULTANEOUS` is injected, the local butterfly monitor records 0 mismatches, 0 retries, and 0 recoveries ($100\%$ local blind spot).
4. In all 50 simultaneous fault trials and all 100 baseline fault trials where local detection was 0%, the output of decapsulation was either canonical valid $K_{\text{expected}}$ (due to decoding slack) or canonical rejection key $K_{\text{rej}}$ (due to FO re-encryption check). Zero unauthenticated keys were returned.
5. All 9 targeted validation tests in `test_step2c_countermeasure_independence` passed without failure.

### 5.2 Inferences (Logically Deduceable from Model)
1. **Separation of Recovery vs Containment:** Local recovery is solely a property of TFIB-REF with an uncorrupted reference table. In contrast, safe containment is a global property of the Fujisaki-Okamoto transform in ML-KEM.
2. **Checker Integrity Requirement:** An in-place recovery countermeasure cannot recover from a persistent checker corruption; it must fail-stop to prevent poisoning the computation with invalid reference data.
3. **Independent Stride Invariance:** Algebraic recalculation of twiddle indices from $(layer, b\_idx)$ protects against loop counter faults in the caller.

### 5.3 Unverified Hypotheses & Model Limitations
1. **Software Fault Model Limitation:** Injected faults are software bit-flips in C variables. They do **not** model clock glitching, laser injection, or electromagnetic fault injection where transient hardware behavior could alter pipeline execution, bypass branch checks, or induce multi-register corruption.
2. **Single-Core Colocation Risk:** In hardware, operational and reference twiddles would likely share the same memory bus, cache hierarchy, or on-chip ROM. An address decoder fault or flash bit-line failure could corrupt both simultaneously.
3. **Co-located Stack Frames:** $u_{\text{saved}}$ and $v_{\text{saved}}$ share the execution stack with other NTT variables. A fault corrupting the stack pointer or writing across frame boundaries could corrupt both operational data and saved rollback state simultaneously.

---

## 6. Constraints Compliance Confirmation

- **Core Algorithm Integrity:** `mlkem768_dec_monitored` and the underlying arithmetic routines in `algorithms/source_ref/mlkem/` were **not modified**.
- **Historical Output Integrity:** `tfib_experiments/phase2_step2b_runner_output.csv` and prior campaign CSVs remain byte-identical and unmodified.
- **Table Relocation Segregation:** Table relocation (Step 2C-B) has **not** been implemented or combined with this step.
- **Physical Qualification Claims:** Strictly disclaimed. No radiation, space, or physical qualification is claimed.
- **Step 2C-B Prerequisite:** Step 2C-B has **not** been initiated pending this review.

---

## 7. Concise Final Verdict

### What this experiment establishes:
1. **Countermeasure Independence:** TFIB-REF and TFIB-META operate independently of primary operational twiddles for single-locus faults. Faults affecting the checker itself are detected and safely handled (recovery for transient, fail-stop for persistent) with 0% false acceptance.
2. **Common-Mode Boundary:** Local butterfly invariant checks have an inherent mathematical blind spot against simultaneous common-mode faults ($\zeta_{\text{op}} \oplus \delta = \zeta_{\text{ref}} \oplus \delta \implies \text{Invariant holds}$).
3. **End-to-End Cryptographic Containment:** The Fujisaki-Okamoto transform provides a reliable outer barrier. Even when local invariant monitoring fails completely, downstream ciphertext re-encryption comparison prevents Silent Data Corruption, guaranteeing safe implicit rejection ($0.0\%$ SDC across 900 trials; upper bound $p_{\text{SDC}} < 0.40\%$).

### What remains unknown:
1. Physical behavior under microarchitectural hardware fault injection (laser, clock glitch, EMP).
2. The effect of shared bus or shared cache corruption if operational and reference twiddles are relocated or co-located on specific hardware memory pages (the subject of Step 2C-B).
3. The resilience of stack-saved operand snapshots against correlated multi-word stack corruptions.

**Verdict: CONDITIONAL PASS** (Software independence and common-mode boundaries fully mapped and verified; proceed to Step 2C-B only after formal review).
