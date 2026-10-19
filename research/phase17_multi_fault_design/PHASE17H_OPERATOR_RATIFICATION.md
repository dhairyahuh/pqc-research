# Phase 17H — Operator Ratification, Integrity Audit, and Next-Phase Decision

**Author:** Independent Cryptographic Software Auditor & Statistical Methodologist  
**Date:** 2026-10-12  
**Project:** Cross-Layer Fault Interactions in ML-KEM-768 Key Establishment  
**Deliverable Directory:** `research/phase17_multi_fault_design/`  
**Execution Guard:** Strictly read-only with respect to code and experiments. No C source code modified, no binaries compiled or linked, no virtual memory mutated, no trials executed, no test vectors generated or validated, and no git commits or pushes performed. All prior phase artifacts preserved byte-for-byte.

---

## 1. Formal Record of Operator Approval and Ratified Design

### 1.1 Approval Metadata and Boundary
- **Approval Timestamp:** Received in conversation on **2026-10-11 at 18:46:06 UTC** `[DIRECTLY OBSERVED]`.
  *(Note: This timestamp is the conversation metadata timestamp supplied by the user interface, not an independently measured local hardware or NTP clock.)*
- **Approval Scope:** The human experimental operator has formally reviewed and explicitly ratified the Phase 17 design choices and defect resolutions formulated across Phases 17D, 17E, 17F, and 17G.
- **Repository Record:** In accordance with the Mandatory Research Integrity Protocol, this document serves as the permanent, append-only repository record establishing formal governance adoption of the multi-fault experimental design.

### 1.2 Formally Ratified Quotas and Combinatorial Plan
The following quota allocations are officially ratified and locked `[DIRECTLY OBSERVED]`:

| Quota ID | Stratum Classification | Twiddle Memory State | Channel Impairment Class | Ratified Master Seed Quota ($N$) | Matched Trial Records ($4N$) | Analytical Purpose |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| **Quota 1** | **Admitted-Corrupted** | Active ($k \in [1, 127]$, mask $\neq 0$) | `CH_BIT` (Wire Ciphertext Bit Inversion) | **$N_1 = 300$** | **1,200** | **Primary Cryptographic SDC Analysis** |
| **Quota 2** | **Admitted-Clean** | Active ($k \in [1, 127]$, mask $\neq 0$) | `CH_DUP` (20) & `CH_REORDER` (20) | **$N_2 = 40$** | **160** | Protocol Sequence Ingress Analysis |
| **Quota 3** | **Delivery-Blocking** | Active ($k \in [1, 127]$, mask $\neq 0$) | `CH_TRUNC` (15), `CH_LOSS` (15), `CH_DELAY` (15), `CH_INTERRUPT` (15) | **$N_3 = 60$** | **240** | Transport Blocking & Masking Analysis |
| **Quota 4** | **Negative Controls** | Dormant ($k=0$) & Sham (mask = 0) | Clean Channel (10) & `CH_BIT` Channel (10) (5 per $2 \times 2$ cell) | **$N_4 = 20$** | **80** | Harness Neutrality & Control Baselines |
| **TOTAL** | — | — | — | **$N = 420$** | **1,680** | **Total Confirmatory Campaign** |

- **Arithmetic Integrity:** $300 + 40 + 60 + 20 = 420$ master seeds; $1,200 + 160 + 240 + 80 = 1,680$ planned records `[INDEPENDENTLY RECOMPUTED]`.
- **Quota 4 Factorial Breakdown (5 seeds per cell):**
  1. Dormant Twiddle ($k = 0$) $\times$ Clean Channel: **$n = 5$** (20 records)
  2. Dormant Twiddle ($k = 0$) $\times$ `CH_BIT` Channel: **$n = 5$** (20 records)
  3. Sham Mutation (Active $k \in [1, 127]$, mask `0x0000`) $\times$ Clean Channel: **$n = 5$** (20 records)
  4. Sham Mutation (Active $k \in [1, 127]$, mask `0x0000`) $\times$ `CH_BIT` Channel: **$n = 5$** (20 records)

### 1.3 Ratified Matched Four-Condition Structure
For every master seed $i \in [1, 420]$, four matched conditions are evaluated using identical cryptographic keypairs, twiddle targets, channel parameters, and retry budgets `[DIRECTLY OBSERVED]`:
- **$C_{00}$:** Pristine arithmetic table (`golden_zetas`), clean channel (`CH_CLEAN`). Baseline protocol fidelity.
- **$C_{10}$:** Mutated arithmetic table ($k, \text{mask}$), clean channel (`CH_CLEAN`). Isolated table fault effect.
- **$C_{01}$:** Pristine arithmetic table (`golden_zetas`), armed channel class. Isolated channel fault effect.
- **$C_{11}$:** Mutated arithmetic table ($k, \text{mask}$), armed channel class. Multi-fault interaction effect.
- **Persistence Rules:**
  - *Memory Table:* Mutated prior to Attempt 1 and held in place across all retransmission attempts ($a \in [1, 3]$). Restored only after terminal session exit `[DIRECTLY OBSERVED]`.
  - *Channel Fault:* Evaluated under assigned persistence mode (`TRANSIENT` clears after Attempt 1; `PERSISTENT` recurs across Attempts 2 and 3) `[DIRECTLY OBSERVED]`.

### 1.4 Ratified Analysis Plan and Outcome Separation
1. **Primary Protocol Contrast:** Evaluated strictly as **channel-stratified interaction contrasts** $\hat{\Delta}_c = \hat{p}_{11}(c) - \hat{p}_{10}(c) - \hat{p}_{01}(c) + \hat{p}_{00}(c)$ for each channel class $c$ `[DIRECTLY OBSERVED]`.
2. **Exploratory Aggregate Contrast:** Any summary contrast across the seven active classes is designated strictly **EXPLORATORY** and applies **equal weights of $1/7$** `[DIRECTLY OBSERVED]`.
   - *Epistemological Qualification:* The equal weight $1/7$ is an artificial, researcher-defined standardized construct to balance modeled failure mechanisms, NOT an empirical estimate of real-world physical channel failure densities `[INFERRED]`.
3. **No Zero-Assumption:** The analysis makes no assumption that $p_{10} = 0$ or $p_{11} = 0$; all probabilities are estimated empirically `[INFERRED]`.
4. **Three Distinct Outcome Families:**
   - **Family A (Protocol Endpoint, $Y_{\text{proto}}$):** Evaluates whether endpoints establish matching keys within the retry budget. Execution crashes are coded as $Y_{\text{proto}} = 0$ (protocol failure) in the primary Intention-to-Test analysis, with complete-case pairing reported as sensitivity `[INFERRED]`.
   - **Family B (Cryptographic-Integrity Endpoint, $Y_{\text{crypto}}$):** Evaluates SDC among completed decapsulations ($ss \neq K_{\text{golden}} \land ss \neq K_{\text{rej}}(\tilde{c})$). Execution crashes are availability failures and **CANNOT be coded as SDC** `[INFERRED]`.
   - **Family C (Execution/Reliability Endpoint, $Y_{\text{exec}}$):** Tracks process crashes (`CRASH_SIGNAL`), `mprotect` errors, restoration failures, and non-zero return codes in a separate reliability table `[DIRECTLY OBSERVED]`.
5. **Denominator Non-Conflation:** A confidence bound derived from completed decapsulations ($n_{\text{completed}}$) describes only cryptographic integrity conditional on survival; it **does NOT describe all assigned or attempted trials** `[INFERRED]`.

---

## 2. Statistical Corrections and Exact Recomputations

### 2.1 Primary SDC Upper Bound Derivation
For zero observed SDC events ($k = 0$) in $n$ eligible, completed first-attempt decapsulations, the exact one-sided 95% Clopper–Pearson upper bound is:

$$p_U(n) = 1 - (0.05)^{1/n}$$

Independent recomputation with full floating-point precision `[INDEPENDENTLY RECOMPUTED]`:
- **$n = 300$:** $p_U(300) = 1 - (0.05)^{1/300} = 0.009936082... \implies \mathbf{0.993608\% < 1.0\%}$
- **$n = 299$:** $p_U(299) = 1 - (0.05)^{1/299} = 0.009969150... \implies \mathbf{0.996915\% < 1.0\%}$
- **$n = 298$:** $p_U(298) = 1 - (0.05)^{1/298} = 0.010002431... \implies \mathbf{1.000243\% \ge 1.0\%}$
- **$n = 0$:** Evaluating $1 - 0.05^{1/0}$ attempts division by zero. The endpoint is formally defined as **`INCONCLUSIVE_NO_COMPLETED_TRIALS`**, reporting NO numerical bound.

**Mathematical Conclusion:** Exactly **299 completed eligible observations** with zero SDC events are necessary and sufficient to obtain an upper bound strictly below 1.0%. At $n \le 298$, the upper bound crosses above 1.0% `[INDEPENDENTLY RECOMPUTED]`.

### 2.2 Correction of Historical Pilot Confidence Bound Wording
In Phase 17G §3.5, the historical Phase 15Q pilot (0 execution failures in 16 trials) was cited as having a "95% upper bound of 18.75% by the rule of three".
- **Statistical Correction:**
  - The exact one-sided 95% binomial upper bound for 0 failures in 16 trials is:
    $$p_U(16) = 1 - (0.05)^{1/16} = 1 - \exp\left(\frac{\ln 0.05}{16}\right) = 0.1707497... \implies \mathbf{17.07\%} \quad \text{`[INDEPENDENTLY RECOMPUTED]`}$$
  - The rule-of-three calculation $3/16 = 0.1875 \implies \mathbf{18.75\%}$ is a **convenient conservative approximation**, NOT the exact bound `[INDEPENDENTLY RECOMPUTED]`.
  - Both figures establish that a 16-trial sample carries immense statistical uncertainty (upper bound $\approx 17.1\%$ to $18.8\%$), and cannot be used to infer zero attrition across 1,680 trials `[INFERRED]`.

---

## 3. Independent Repository and Design Audit

### 3.1 Trace of Channel Harness Semantics
Direct source inspection of [combined_campaign.c](file:///Users/dhairyajain/Desktop/pqc%20research/research/combined_harness/combined_campaign.c#L10-L125) lines 10–125 confirms `[DIRECTLY OBSERVED]`:
- Line 10–12: Harness comment explicitly states that channel faults are a software emulator and NOT physical radiation/RF qualification `[DIRECTLY OBSERVED]`.
- Line 70: Channel enum defines `CH_CLEAN`, `CH_BIT`, `CH_TRUNC`, `CH_LOSS`, `CH_DELAY`, `CH_DUP`, `CH_REORDER`, `CH_INTERRUPT` `[DIRECTLY OBSERVED]`.
- Lines 98–109: Only `CH_BIT` modifies wire ciphertext bytes (`wire[pos] ^= mask`, $pos < 1088$) `[DIRECTLY OBSERVED]`.
- Lines 100–103, 111–112: `CH_TRUNC`, `CH_LOSS`, `CH_DELAY`, and `CH_INTERRUPT` are delivery-blocking mechanisms where the transport harness returns before decapsulation (`decaps_ran = 0`) `[DIRECTLY OBSERVED]`.
- Lines 105–106: `CH_DUP` and `CH_REORDER` alter transport sequence metadata but deliver bit-for-bit clean ciphertext to decapsulation (`decaps_ran = 1`) `[DIRECTLY OBSERVED]`.

### 3.2 Trace of Independent Rejection Oracle
Direct source inspection of [independent_oracle.c](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/phase11_oracle/independent_oracle.c#L59-L79) and [fips202_ref.c](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/phase11_oracle/fips202_ref.c#L1-L85) confirms `[DIRECTLY OBSERVED]`:
- The rejection secret is derived via $K_{\text{rej}} = \text{SHAKE256}(z \parallel \tilde{c}, 32)$, extracting $z$ from `sk[2368..2399]` and hashing it with the post-channel wire ciphertext `ct2` `[DIRECTLY OBSERVED]`.
- `fips202_ref.c` is an 86-line standalone, clean-room implementation of Keccak-f[1600] based on TweetFIPS-202, completely independent of `mlkem-native` and `liboqs` `[DIRECTLY OBSERVED]`.

### 3.3 Test Vector Inventory Audit
Filesystem inspection across the repository confirms `[DIRECTLY OBSERVED]`:
- **Existing Static Official KAT Material:** Exactly **ONE static test vector** exists on disk in [mlkem_expected_kat.h](file:///Users/dhairyajain/Desktop/pqc%20research/references/test_vectors/mlkem_expected_kat.h) `[DIRECTLY OBSERVED]`.
- **Existing Locally Generated Vectors:** Exactly **ZERO** locally generated test vectors exist as pre-computed files on disk `[DIRECTLY OBSERVED]`.
- **Planned Vectors 1–419:** Strictly specifications for runtime preflight generation and validation; they do NOT yet exist on disk and have NOT been validated `[PROPOSED / NOT YET TESTED]`.

---

## 4. Evidentiary Synthesis Matrix

| Item / Claim | Evidentiary Basis | Operational Finding | Lifecycle Status |
| :--- | :---: | :--- | :---: |
| **Quota Allocation ($420$ seeds, $1,680$ records)** | `[DIRECTLY OBSERVED]` | Ratified by operator; arithmetically exact | **FORMALLY ADOPTED** |
| **Quota 3 Sub-Classes ($15$ each across 4 blocking classes)** | `[DIRECTLY OBSERVED]` | Ratified by operator; balanced transport coverage | **FORMALLY ADOPTED** |
| **Quota 4 Factorial Cells ($5$ each across $2 \times 2$ grid)** | `[DIRECTLY OBSERVED]` | Ratified by operator; controls table & harness artifacts | **FORMALLY ADOPTED** |
| **Primary SDC Upper Bound ($0.9936\% < 1.0\%$ at $n=300$)** | `[INDEPENDENTLY RECOMPUTED]` | Exact Clopper–Pearson derivation verified | **FORMALLY ADOPTED** |
| **Minimum Threshold ($n \ge 299$ needed for $< 1.0\%$)** | `[INDEPENDENTLY RECOMPUTED]` | $p_U(298) = 1.0002\% \ge 1.0\%$; $p_U(299) = 0.9969\% < 1.0\%$ | **FORMALLY ADOPTED** |
| **Shortfall Rule Policy** | `[DIRECTLY OBSERVED]` | Report realized bound if $n \le 298$; do not inflate quota | **FORMALLY ADOPTED** |
| **Shortfall Boundary ($n=0 \implies \text{UNDEFINED}$)** | `[INDEPENDENTLY RECOMPUTED]` | Inconclusive status; division by zero prevented | **FORMALLY ADOPTED** |
| **Outcome Family Separation (A: Proto, B: Crypto, C: Exec)** | `[INFERRED]` | Crashes coded as $Y=0$ for Proto, NEVER as SDC | **FORMALLY ADOPTED** |
| **Primary Analysis: Channel-Stratified Contrasts** | `[DIRECTLY OBSERVED]` | Eliminates arbitrary pooling distortion | **FORMALLY ADOPTED** |
| **Exploratory Aggregate: Equal $1/7$ Weighting** | `[INFERRED]` | Artificial standardized metric; not real link distribution | **FORMALLY ADOPTED** |
| **Channel Model Scope (`combined_campaign.c`)** | `[DIRECTLY OBSERVED]` | Software emulator; "modeled channel interruption" | **VERIFIED IN SOURCE** |
| **Vector Inventory (1 static KAT; 419 preflight specs)** | `[DIRECTLY OBSERVED]` | Only Vector 0 exists on disk; 1–419 to be generated | **VERIFIED ON DISK** |

---

## 5. Next-Phase Decision and Evidence-Based Rationale

### 5.1 Evaluation of Next-Phase Candidates
1. **Design Closure:** **COMPLETED.** All six design defects (D-01 through D-06), combinatorial quotas, matched condition rules, estimand families, weighting structures, and statistical boundary rules are now fully specified and formally ratified by the human experimental operator. No design ambiguities remain open on paper.
2. **Preflight Feasibility and Implementation Review:** The project is now ready for **Phase 18: Implementation Review and Isolated Harness Verification**. This phase must:
   - Review and verify the standalone C runner source code implementing the ratified 4-strata quotas ($N = 420$).
   - Implement the deterministic preflight generator and cross-implementation validation pipeline (`liboqs v0.16.0` vs. SUT) for Vectors 1–419.
   - Verify Darwin ARM64 virtual memory isolation on `(__DATA_CONST,__zetas_page)` using dry-run memory protection checks without executing fault trials.
3. **Campaign Execution:** **STRICTLY PROHIBITED.** No experimental trials, memory mutations, or fault injection runs are authorized until the implementation review is formally audited and approved.

### 5.2 Final Status Verdict

# **DESIGN CLOSED — READY FOR SEPARATE IMPLEMENTATION REVIEW**

### 5.3 Authorization Statement
**Authorization Scope:** This status confirms that the multi-fault experimental design is formally closed and approved for separate implementation review. **It does NOT authorize compiling binaries, mutating virtual memory, linking test harnesses, generating vector corpora, or executing experimental trials.** Those actions require separate, explicit operator authorization.

---

## 6. Cryptographic Hash and Repository Verification

### 6.1 Verified SHA-256 Hashes of Artifacts
Computed via `shasum -a 256` on actual on-disk file bytes `[DIRECTLY OBSERVED]`:

| Deliverable Path | SHA-256 Digest | Status |
| :--- | :--- | :---: |
| `PHASE17_EXPERIMENT_DESIGN.md` | `36180af5fbf45a3f50b36f52d6375725020dd9577dfa5b89e40252e5e9479887` | Preserved Unchanged `[DIRECTLY OBSERVED]` |
| `PHASE17B_METHODS_CORRECTION.md` | `9180a13c1cf98050f05f3a426cc0d1102ce34c9d76ad48c9d51015f2931a25d4` | Preserved Unchanged `[DIRECTLY OBSERVED]` |
| `PHASE17B_CHANGELOG.md` | `f126e778f46dc562266408b80f8d373900e7d85dcdb3655ef68dfdcac7fa9edc` | Preserved Unchanged `[DIRECTLY OBSERVED]` |
| `PHASE17C_RESIDUAL_AUDIT.md` | `0e6c6e26120864297c592f26d7f77dd8c3fc10d7d3518f62fa4ffd2d08404c12` | Preserved Unchanged `[DIRECTLY OBSERVED]` |
| `PHASE17C_CHANGELOG.md` | `b5d99bb289b316c6f1515d0c31f21c25da11c4871929dd2bc480b044d2d1bccf` | Preserved Unchanged `[DIRECTLY OBSERVED]` |
| `PHASE17D_FINAL_PREREGISTRATION.md` | `474e72b8fd4516bc5723701d168eb58cffdd6f2a444caa302e4a6207a0a9b71d` | Preserved Unchanged `[DIRECTLY OBSERVED]` |
| `PHASE17D_CHANGELOG.md` | `6c3de8cf3c2ab52300394e8ccb5e1e3b8599c8553d201013f9c8057028b9a708` | Preserved Unchanged `[DIRECTLY OBSERVED]` |
| `PHASE17E_INDEPENDENT_AUDIT.md` | `259b0732c0d5032239462fb35d85e133e19173991e3cefedb7ebfe2d1796db88` | Preserved Unchanged `[DIRECTLY OBSERVED]` |
| `PHASE17E_CHANGELOG.md` | `e7f108543d9fda3e8b4c4334d39149e57a38daedc1546bdc6f6ce8c39aae4f11` | Preserved Unchanged `[DIRECTLY OBSERVED]` |
| `PHASE17F_DESIGN_DEFECT_RESOLUTION.md` | `4c03e400eadae58588123873af55ba739e95576bffbed65c7b1c467d2d194b5b` | Preserved Unchanged `[DIRECTLY OBSERVED]` |
| `PHASE17F_CHANGELOG.md` | `5a40bac63dbd8436ace673a224f9dc916e96893b06a5e5b4e3c4d1af78ac9b48` | Preserved Unchanged `[DIRECTLY OBSERVED]` |
| `PHASE17G_RESIDUAL_CLARIFICATION.md` | `15817685d30d9151629c62f36aaec45361de8f833c73f406af279863fb921541` | Preserved Unchanged `[DIRECTLY OBSERVED]` |
| `PHASE17G_CHANGELOG.md` | `577eb085492cc40947c0a450b07b78b7ee262aa8933621197257b7ade2433cd6` | Preserved Unchanged `[DIRECTLY OBSERVED]` |
| `PHASE17H_OPERATOR_RATIFICATION.md` | *(Computed upon file write)* | **New Deliverable** `[DIRECTLY OBSERVED]` |
| `PHASE17H_CHANGELOG.md` | *(Computed upon file write)* | **New Deliverable** `[DIRECTLY OBSERVED]` |

### 6.2 Git Repository State
- Verified via `git status` `[DIRECTLY OBSERVED]`.
- Branch: `space-resilience-framework`.
- Pre-existing working tree modifications preserved untouched.
- Zero files staged, committed, pushed, or reverted.
