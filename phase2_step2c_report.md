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
- **Independence of Storage:** `mlk_zetas` (operational) and `tfib_zetas_ref` (checker) occupy separate read-only memory addresses (`0x1000188a0` vs `0x100018a60`), demonstrating address-level separation within the compiled software binary image.
- **Checker Degradation Robustness:** Corrupting checker-only state or decision logic never induces SDC. Transient checker faults trigger benign retry and recover; persistent checker faults force a safe fail-stop.
- **Simultaneous Paired-Mutation Common-Mode Failure:** When two sequential software mutations apply an identical bit-flip to both the operational twiddle (before butterfly arithmetic) and the reference twiddle (inside the monitor path), **local monitor detection is 0.0%** ($0/50$ detected), because invariant equations evaluate identically over matching operand perturbations. This result demonstrates checker blindness under the specific coordinated software mutations tested; it does not prove physical common-mode fault behavior, general hardware vulnerability, physical independence, or radiation tolerance.
- **Outer Cryptographic Safety Net:** Of the 150 locally blinded trials (100 baseline + 50 simultaneous), **147 (98%) were actively rejected** by the Fujisaki-Okamoto re-encryption check, which detected the ciphertext mismatch and output the canonical rejection key $K_{\text{rej}}$. In the remaining **3 trials (2.0%)**, the intermediate polynomial perturbation induced by the twiddle fault fell within the error-tolerance of the centered binomial decoding stage. Although intermediate computation was altered, the rounding and error-correction during decoding preserved the original message $m$, resulting in the valid shared secret $K_{\text{expected}}$ without triggering Fujisaki-Okamoto rejection. These trials represent secret preservation through decoding error-tolerance rather than active rejection by FO re-encryption. All 150 locally blinded trials produced a valid protocol outcome under the tested pseudo-random trial distribution ($0$ SDC observed).

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
Config     | Suite                      | Total | Activated | Detected | Recovered | Fail-Stop | Active FO Rej | Ineffective† | SDC
-----------+----------------------------+-------+-----------+----------+-----------+-----------+---------------+--------------+-----
BASELINE   | CLEAN_CONTROL              | 50    | 0         | 0        | 0         | 0         | 0             | 0            | 0
BASELINE   | OP_TWIDDLE_TRANSIENT       | 50    | 50        | 0        | 0         | 0         | 48            | 2            | 0
BASELINE   | OP_TWIDDLE_PERSISTENT      | 50    | 50        | 0        | 0         | 0         | 50            | 0            | 0
TFIB_REF   | CLEAN_CONTROL              | 50    | 0         | 0        | 0         | 0         | 0             | 0            | 0
TFIB_REF   | OP_TWIDDLE_TRANSIENT       | 50    | 50        | 50       | 50        | 0         | 0             | 0            | 0
TFIB_REF   | OP_TWIDDLE_PERSISTENT      | 50    | 50        | 50       | 0         | 50        | 0             | 0            | 0
TFIB_REF   | REF_TWIDDLE_TRANSIENT      | 50    | 50        | 50       | 50        | 0         | 0             | 0            | 0
TFIB_REF   | REF_TWIDDLE_PERSISTENT     | 50    | 50        | 50       | 0         | 50        | 0             | 0            | 0
TFIB_REF   | SIMULTANEOUS_COMMON_MODE   | 50    | 50        | 0        | 0         | 0         | 49            | 1            | 0
TFIB_REF   | CHECKER_LOGIC_TRANSIENT    | 50    | 50        | 50       | 50        | 0         | 0             | 0            | 0
TFIB_REF   | CHECKER_LOGIC_PERSISTENT   | 50    | 50        | 50       | 0         | 50        | 0             | 0            | 0
TFIB_META  | CLEAN_CONTROL              | 50    | 0         | 0        | 0         | 0         | 0             | 0            | 0
TFIB_META  | OP_TWIDDLE_TRANSIENT       | 50    | 50        | 50       | 0         | 50        | 0             | 0            | 0
TFIB_META  | OP_TWIDDLE_PERSISTENT      | 50    | 50        | 50       | 0         | 50        | 0             | 0            | 0
TFIB_META  | META_TAG_TRANSIENT         | 50    | 50        | 50       | 50        | 0         | 0             | 0            | 0
TFIB_META  | META_TAG_PERSISTENT        | 50    | 50        | 50       | 0         | 50        | 0             | 0            | 0
TFIB_META  | CHECKER_LOGIC_TRANSIENT    | 50    | 50        | 50       | 50        | 0         | 0             | 0            | 0
TFIB_META  | CHECKER_LOGIC_PERSISTENT   | 50    | 50        | 50       | 0         | 50        | 0             | 0            | 0
-----------+----------------------------+-------+-----------+----------+-----------+-----------+---------------+--------------+-----
TOTAL      | 18 Suites                  | 900   | 750       | 600      | 250       | 350       | 147           | 3            | 0

† "Ineffective" denotes trials where intermediate polynomial perturbations fell within the
  error-tolerance of ML-KEM-768 centered binomial decoding. The final message m was preserved,
  producing the valid shared secret K_expected. These trials reflect secret preservation via
  decoding error-tolerance rather than active rejection by the FO re-encryption test.
  "Active FO Rej" denotes trials where the corrupted NTT output altered the decoded plaintext,
  causing FO re-encryption comparison to fail and decapsulation to output K_rej.
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
7. **Simultaneous Paired-Mutation Common-Mode Failure Detection Rate:**
   - Evaluated over $N_{\text{simul}} = 50$: $0 / 50 = \mathbf{0.0\%}$ (95% CI $[0.0\%, 7.11\%]$).
   - **Local Blindness Under Specific Tested Mutations:** When two sequential software mutations apply identical bit-flips to both $\zeta_{\text{op}}$ (before butterfly arithmetic) and $\zeta_{\text{ref}}$ (inside the monitor path), the checker cannot detect the fault locally because arithmetic invariant equations hold over identical perturbations. This demonstrates checker blindness under the specific coordinated software mutations tested; it does not prove physical common-mode fault behavior, general hardware vulnerability, physical independence, or radiation tolerance.
8. **Locally Blinded Trial Outcomes (Under 0% Local Detection):**
   - Total locally blinded trials: Baseline ($N=100$) + Simultaneous ($N=50$) = $150$.
   - **Active FO rejection:** $147 / 150 = \mathbf{98.0\%}$ — the corrupted NTT output altered the decoded plaintext, FO re-encryption comparison failed, and decapsulation output the canonical rejection key $K_{\text{rej}}$.
   - **Secret preservation via decoding slack:** $3 / 150 = \mathbf{2.0\%}$ — the internal coefficient perturbation induced by the twiddle fault fell within the error-tolerance of ML-KEM-768 centered binomial decoding; the final message $m$ was preserved, and decapsulation returned the valid shared secret $K_{\text{expected}}$. These trials were not rejected by FO because the decoded plaintext remained uncorrupted despite intermediate arithmetic perturbation.
   - **Correct end-to-end key outcome:** $150 / 150 = \mathbf{100.0\%}$ under the tested PRF-generated trial distribution (95% CI $[97.55\%, 100.0\%]$). No trial returned an unauthenticated or corrupted key.
9. **Silent Data Corruption (SDC) Rate:**
   - Denominator: All fault-activated trials ($N_{\text{act}} = 750$).
   - SDC Events: $0 / 750 = \mathbf{0.0\%}$.
   - **Exact One-Sided 95% Binomial Upper Confidence Bound:** Across all $N_{\text{act}} = 750$ fault-activated trials (excluding the 150 clean control runs), with 0 observed SDC events, the exact one-sided 95% binomial upper confidence bound on the true SDC rate under independent identically distributed sampling is $p_{\text{SDC}} \le 1 - 0.05^{1/750} \approx \mathbf{0.399\%}$. For comparison, the rule-of-three approximation yields $\frac{3}{750} = 0.400\%$, and the one-sided Wilson score upper bound at $\alpha = 0.05$ is $0.490\%$.
   - **Critical Audit Caveat:** Zero observed SDC does **not** prove zero theoretical SDC risk. The PRF-generated trial distribution does not represent all possible software faults or physical fault distributions.
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
3. When `TFIB_FAULT_SIMULTANEOUS` is injected (two sequential software mutations applying identical bit-flips to the operational and reference twiddles), the local butterfly monitor records 0 mismatches, 0 retries, and 0 recoveries ($100\%$ local blind spot under this paired mutation model).
4. Of the 150 locally blinded trials (50 simultaneous + 100 baseline): 147 produced the canonical rejection key $K_{\text{rej}}$ via active FO re-encryption failure; in 3 trials, intermediate polynomial perturbations fell within the error-tolerance of the centered binomial decoding stage, preserving the final message $m$ and returning valid $K_{\text{expected}}$. No unauthenticated keys were returned.
5. All 9 targeted validation tests in `test_step2c_countermeasure_independence` passed without failure.

### 5.2 Inferences (Logically Deduceable from Model)
1. **Separation of Recovery vs Containment:** Local recovery is solely a property of TFIB-REF with an uncorrupted reference table. Outer FO containment is a global property of the Fujisaki-Okamoto transform in ML-KEM. Preservation via decoding slack (where intermediate polynomial distortion does not alter the final decoded message) is a distinct third outcome — it represents algorithmic error-tolerance rather than active monitor detection or FO re-encryption rejection.
2. **Checker Integrity Requirement:** An in-place recovery countermeasure cannot recover from a persistent checker corruption; it must fail-stop to prevent poisoning the computation with invalid reference data.
3. **Independent Stride Invariance:** Algebraic recalculation of twiddle indices from $(layer, b\_idx)$ protects against loop counter faults in the caller.

### 5.3 Unverified Hypotheses & Model Limitations
1. **Software Fault Model Limitation:** Injected faults are software bit-flips in C variables. They do **not** model clock glitching, laser injection, or electromagnetic fault injection where transient hardware behavior could alter pipeline execution, bypass branch checks, or induce multi-register corruption. The `TFIB_FAULT_SIMULTANEOUS` mode implements two sequential software mutations (operational twiddle before butterfly, reference twiddle inside monitor); this evaluates checker blindness under the specific coordinated software mutations tested and does not prove physical common-mode fault behavior, shared silicon vulnerability, or general hardware susceptibility.
2. **Single-Core Colocation Risk:** In hardware, operational and reference twiddles would likely share the same memory bus, cache hierarchy, or on-chip ROM. An address decoder fault or flash bit-line failure could corrupt both simultaneously. Virtual address separation, linker-section separation, page separation, cache separation, and physical fault isolation are distinct properties. Table relocation alone does not prevent physical common-mode corruption.
3. **Co-located Stack Frames:** $u_{\text{saved}}$ and $v_{\text{saved}}$ share the execution stack with other NTT variables. A fault corrupting the stack pointer or writing across frame boundaries could corrupt both operational data and saved rollback state simultaneously.

---

## 6. Constraints Compliance Confirmation

- **Core Algorithm Integrity:** `mlkem768_dec_monitored` and the underlying arithmetic routines in `algorithms/source_ref/mlkem/` were **not modified**.
- **Historical Output Integrity:** `tfib_experiments/phase2_step2b_runner_output.csv` and prior campaign CSVs remain byte-identical and unmodified.
- **Table Relocation Segregation:** Table relocation (Step 2C-B) has **not** been implemented or combined with this step. Step 2C-B is a proposed architectural experiment motivated by the observed paired-mutation blind spot, the current software placement of the two tables, and the unresolved question of whether alternative placement changes fault exposure under a clearly specified model.
- **Physical Qualification Claims:** Strictly disclaimed. No radiation, space, or physical qualification is claimed.
- **Step 2C-B Prerequisite:** Step 2C-B has **not** been initiated pending this review.

---

## 7. Concise Final Verdict

### What this experiment establishes:
1. **Countermeasure Independence:** TFIB-REF and TFIB-META operate independently of primary operational twiddles for single-locus faults. Faults affecting the checker itself are detected and safely handled (recovery for transient, fail-stop for persistent) with 0% false acceptance.
2. **Common-Mode Boundary:** Local butterfly invariant checks have an inherent mathematical blind spot against paired software mutations that identically corrupt both operands ($\zeta_{\text{op}} \oplus \delta = \zeta_{\text{ref}} \oplus \delta \implies \text{Invariant holds}$). This observation is established under the paired software mutation model; it does not establish physical common-mode susceptibility or radiation tolerance.
3. **End-to-End Correctness Under Local Blindness:** Of the 150 locally blinded trials, 147 (98.0%) were actively rejected by FO re-encryption, and in 3 trials (2.0%), intermediate arithmetic perturbations were absorbed by decoding error-tolerance, preserving the final secret $K_{\text{expected}}$. All 150 produced a correct end-to-end key outcome (0 observed SDC events across all $N_{\text{act}} = 750$ fault-activated trials [900 total trials]; exact one-sided 95% binomial upper confidence bound $p_{\text{SDC}} \le 0.399\%$ on $N_{\text{act}} = 750$, and $p_{\text{SDC}} \le 5.82\%$ on the $N_{\text{simul}} = 50$ paired-mutation suite).

### What remains unknown:
1. Physical behavior under microarchitectural hardware fault injection (laser, clock glitch, EMP).
2. The effect of shared bus or shared cache corruption if operational and reference twiddles are relocated or co-located on specific hardware memory pages (the subject of proposed Step 2C-B; virtual address separation, linker-section separation, page separation, cache separation, and physical fault isolation are distinct, unresolved properties).
3. The resilience of stack-saved operand snapshots against correlated multi-word stack corruptions.

**Verdict: CONDITIONAL PASS** (Software independence and common-mode boundaries fully mapped and verified; proceed to Step 2C-B only after formal review).
