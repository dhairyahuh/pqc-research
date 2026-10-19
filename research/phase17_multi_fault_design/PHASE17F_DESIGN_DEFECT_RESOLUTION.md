# Phase 17F — Read-Only Design Defect Resolution

**Author:** Independent Cryptographic Software Auditor & Statistical Methodologist  
**Date:** 2026-10-12  
**Project:** Cross-Layer Fault Interactions in ML-KEM-768 Key Establishment  
**Status:** DESIGN DEFECT RESOLUTION (Strictly Read-Only — No Experiments Authorized)  
**Deliverable Directory:** `research/phase17_multi_fault_design/`  
**Execution Guard:** Strictly read-only with respect to implementation and experiments. No source code modified, no binaries compiled or linked, no memory mutated, no trials executed, and no git commits or pushes performed. All prior phase artifacts preserved byte-for-byte.

---

## 1. Scope and Mandatory Evidence Standards

In accordance with the **Mandatory Research Integrity and Anti-Hallucination Protocol**, every factual statement, mathematical computation, and audit claim in this document is explicitly tagged with its evidentiary basis:
- `[DIRECTLY OBSERVED]`: Supported by direct inspection of active source lines, local files, or command outputs in this session.
- `[INDEPENDENTLY RECOMPUTED]`: Verified by independent mathematical calculation from stated inputs.
- `[REPORTED BY A PRIOR PHASE]`: Present in historical documentation but not independently executed dynamically in this phase.
- `[INFERRED]`: Logically deduced from observed facts, with the deduction chain explicitly stated.
- `[PROPOSED / NOT YET TESTED]`: Formally specified design parameters or algorithm definitions awaiting implementation or execution.
- `[UNKNOWN / UNVERIFIED]`: Information that is missing, contradictory, or lacks empirical confirmation.

---

## 2. Resolution of Task 1: D-01 and D-02 (Combinatorial Quota Allocations)

### 2.1 Resolution of D-01: Quota 3 ($N_3 = 60$) Sub-Class Breakdown
- **Prior Finding (Phase 17E):** `PHASE17D_FINAL_PREREGISTRATION.md` §2.2 specified $N_3 = 60$ delivery-blocking master seeds across four channel classes (`CH_TRUNC`, `CH_LOSS`, `CH_DELAY`, `CH_INTERRUPT`) without defining per-class counts `[DIRECTLY OBSERVED]`.
- **Proposed and Frozen Integer Allocation:** The 60 master seeds in Quota 3 are allocated equally across the four transport failure mechanisms (`15` seeds each) `[PROPOSED / NOT YET TESTED]`:
  1. `CH_TRUNC` (Frame Truncation): **$n = 15$** master seeds ($60$ matched records across $C_{00}, C_{10}, C_{01}, C_{11}$)
  2. `CH_LOSS` (Packet Drop): **$n = 15$** master seeds ($60$ matched records)
  3. `CH_DELAY` (Delivery Deadline Exceeded): **$n = 15$** master seeds ($60$ matched records)
  4. `CH_INTERRUPT` (Physical Link Severance): **$n = 15$** master seeds ($60$ matched records)
  - Sub-Total: $15 + 15 + 15 + 15 = 60$ master seeds ($240$ matched records) `[INDEPENDENTLY RECOMPUTED]`.
- **Scientific Rationale:** All four classes are delivery-blocking mechanisms where the transport harness aborts before invoking decapsulation (`combined_campaign.c:98-113`) `[DIRECTLY OBSERVED]`. An equal allocation provides uniform, balanced sampling across transport anomaly types without making ungrounded assumptions about real-world channel probability densities `[INFERRED]`.

### 2.2 Resolution of D-02: Quota 4 ($N_4 = 20$) Control Stratum Allocation
- **Prior Finding (Phase 17E):** Phase 17D §2.2 specified 20 negative control master seeds combining dormant/sham table states with clean/`CH_BIT` channel states, but omitted the exact $2 \times 2$ factorial grid `[DIRECTLY OBSERVED]`.
- **Proposed and Frozen Factorial Allocation:** The 20 master seeds in Quota 4 are allocated in a balanced $2 \times 2$ factorial grid (`5` seeds per cell) `[PROPOSED / NOT YET TESTED]`:
  1. **Cell 4A:** Dormant Twiddle ($k = 0$) $\times$ Clean Channel (`CH_CLEAN`): **$n = 5$** master seeds ($20$ matched records)
  2. **Cell 4B:** Dormant Twiddle ($k = 0$) $\times$ Wire Bit Inversion (`CH_BIT`): **$n = 5$** master seeds ($20$ matched records)
  3. **Cell 4C:** Sham Mutation (Target $k \in [1, 127]$, mask `0x0000`) $\times$ Clean Channel (`CH_CLEAN`): **$n = 5$** master seeds ($20$ matched records)
  4. **Cell 4D:** Sham Mutation (Target $k \in [1, 127]$, mask `0x0000`) $\times$ Wire Bit Inversion (`CH_BIT`): **$n = 5$** master seeds ($20$ matched records)
  - Sub-Total: $5 + 5 + 5 + 5 = 20$ master seeds ($80$ matched records) `[INDEPENDENTLY RECOMPUTED]`.
- **Scientific Rationale:**
  - Dormant index $k = 0$ is the constant twiddle factor $1$ in standard NTT implementations, verifying that inactive table indices do not inadvertently disrupt arithmetic `[INFERRED]`.
  - Sham mask `0x0000` writes identical bytes to an active twiddle index $k \in [1, 127]$, verifying that the Darwin ARM64 `mprotect` memory modification mechanism does not alter computation when the underlying numerical value is unchanged `[INFERRED]`.
  - Crossing each twiddle control with clean vs. `CH_BIT` channel conditions isolates harness-induced channel artifacts from memory-induced artifacts `[INFERRED]`.

### 2.3 Arithmetic Reconciliation
- **Quota 1 (Primary Active Corrupted):** $N_1 = 300$ master seeds $\times 4 = 1,200$ matched records `[DIRECTLY OBSERVED]`.
- **Quota 2 (Active Clean Ingress):** $N_2 = 40$ master seeds $\times 4 = 160$ matched records ($20$ `CH_DUP`, $20$ `CH_REORDER`) `[DIRECTLY OBSERVED]`.
- **Quota 3 (Active Delivery-Blocking):** $N_3 = 60$ master seeds $\times 4 = 240$ matched records ($15$ per class) `[PROPOSED / NOT YET TESTED]`.
- **Quota 4 (Negative Controls):** $N_4 = 20$ master seeds $\times 4 = 80$ matched records ($5$ per cell) `[PROPOSED / NOT YET TESTED]`.
- **Total Master Seeds:** $300 + 40 + 60 + 20 = 420$ `[INDEPENDENTLY RECOMPUTED]`.
- **Total Matched Records:** $1,200 + 160 + 240 + 80 = 1,680$ `[INDEPENDENTLY RECOMPUTED]`.
- **Integrity Check:** The primary quota ($N_1 = 300$) and total sample size ($N = 420$) are preserved without silent alterations `[INDEPENDENTLY RECOMPUTED]`.

---

## 3. Resolution of Task 2: D-03 and D-04 (Statistical Bound & Attrition Policy)

### 3.1 Primary SDC Target Estimand
The primary cryptographic Silent Data Corruption (SDC) estimand is formally defined as:

$$\theta_{\text{SDC}} = \mathbb{P}\left( ss_i \neq K_{\text{golden}, i} \ \land \ ss_i \neq K_{\text{rej}}(\tilde{c}_i) \ \middle\vert \ i \in \text{Quota 1}, \ a = 1, \ \text{decaps\_completed} = 1 \right)$$

- **Target Denominator:** Strictly $n_{\text{completed}}$ (first-attempt decapsulations under Condition $C_{11}$ that run to completion without an unhandled hardware trap or process termination).
- **Assigned vs. Attempted vs. Completed:**
  - $N_{\text{assigned}} = 300$: Total pre-allocated scenarios in Quota 1 `[PROPOSED / NOT YET TESTED]`.
  - $N_{\text{attempted}} \le 300$: Scenarios reaching execution start on Darwin ARM64 `[PROPOSED / NOT YET TESTED]`.
  - $n_{\text{completed}} \le N_{\text{attempted}}$: Decapsulations returning a 32-byte shared secret without crashing `[PROPOSED / NOT YET TESTED]`.
- **Target Confidence Bound:** If zero SDC events are observed ($k = 0$) among completed trials, report the exact one-sided 95% Clopper–Pearson upper bound:
  $$p_U(n) = 1 - (0.05)^{1/n}$$

### 3.2 Mathematical Sensitivity and Attrition Thresholds
Independent recomputation of the one-sided 95% Clopper–Pearson upper bound for $k = 0$ events across varying completion counts `[INDEPENDENTLY RECOMPUTED]`:

| Completed Cases ($n$) | Shortfall ($300 - n$) | Exact One-Sided 95% Upper Bound | Wilson Score (One-Sided 95%) | Status Relative to $< 1.0\%$ Target |
| :---: | :---: | :---: | :---: | :---: |
| **300** | 0 | **0.993608%** | **0.893787%** | **PASS (< 1.0%)** `[INDEPENDENTLY RECOMPUTED]` |
| **299** | 1 | **0.996909%** | **0.896748%** | **PASS (< 1.0%)** `[INDEPENDENTLY RECOMPUTED]` |
| **298** | 2 | **1.000236%** | **0.899727%** | **FAIL ($\ge 1.0\%$)** `[INDEPENDENTLY RECOMPUTED]` |
| **295** | 5 | **1.010373%** | **0.908754%** | **FAIL ($\ge 1.0\%$)** `[INDEPENDENTLY RECOMPUTED]` |
| **290** | 10 | **1.027663%** | **0.924103%** | **FAIL ($\ge 1.0\%$)** `[INDEPENDENTLY RECOMPUTED]` |
| **0** | 300 | **UNDEFINED** | **UNDEFINED** | **CAMPAIGN FAILURE** `[INDEPENDENTLY RECOMPUTED]` |

- **Critical Threshold:** The sample size threshold to maintain an upper bound below $1.0\%$ is exactly **$n_{\text{completed}} \ge 299$**. If two or more trials fail to complete, the realized bound crosses above $1.0\%$ `[INDEPENDENTLY RECOMPUTED]`.

### 3.3 Evaluation of Policy Alternatives (D-03 Resolution)
Two potential approaches were evaluated to address the zero-buffer attrition risk:
1. **Alternative A — Arbitrary Sample Inflation (e.g. $N_1 = 315$ with 5% Buffer):**
   - *Analysis:* Allocating 315 seeds provides a buffer of 16 execution failures ($315 - 299 = 16$). However, the repository contains **zero empirical evidence** justifying a 5% attrition rate. In the Phase 15Q pilot (16 trials on `__DATA_CONST,__zetas_page` on Darwin ARM64), the observed execution failure rate was strictly $0/16$ (0%) (`results/phase15q/PHASE15Q_PILOT_EXECUTION_REPORT.md:66,114`) `[DIRECTLY OBSERVED]`. Outside Phase 15Q, no large-scale execution failure data exists `[UNKNOWN / UNVERIFIED]`. Inflating sample sizes without empirical grounding violates Protocol Rule 5.
2. **Alternative B — Fixed Quota ($N_1 = 300$) with Binding Preregistered Shortfall Rule (ADOPTED):**
   - *Policy:* Retain $N_1 = 300$ as the frozen assigned quota.
   - *Shortfall Rule:* If $n_{\text{completed}} \ge 299$ and $k = 0$, the study claims an upper bound below $1.0\%$ ($0.9936\%$ at $n=300$; $0.9969\%$ at $n=299$).
   - *Under-Threshold Rule:* If $n_{\text{completed}} \le 298$, the study **shall not claim** an upper bound below $1.0\%$. Instead, it must publish the realized exact bound (e.g., $1.0002\%$ at $n=298$, $1.0277\%$ at $n=290$) and document the root causes of all non-completing trials in the Intention-to-Test ledger.
   - *Resolution Justification:* This preserves pre-registered sample integrity, prevents goalpost-shifting, and adheres to Protocol Rule 1 ("A truthful incomplete result is acceptable. Never promise a bound that the realized denominator cannot support") `[INFERRED]`.

### 3.4 Formal Boundary Rule for $n_{\text{completed}} = 0$ (D-04 Resolution)
- If $n_{\text{completed}} = 0$, the mathematical expression $1 - (0.05)^{1/0}$ involves division by zero and is undefined `[INDEPENDENTLY RECOMPUTED]`.
- **Frozen Exception Rule:** If $n_{\text{completed}} = 0$, the runner shall log `FATAL_TOTAL_CAMPAIGN_FAILURE`. The analysis pipeline shall output `STATUS: INCONCLUSIVE (NO COMPLETED TRIALS)` and report **no statistical bound** `[PROPOSED / NOT YET TESTED]`.

### 3.5 Separation of Execution Failures from SDC
- System crashes (`SIGBUS`, `SIGSEGV`), memory protection faults, and non-zero return codes are **availability/reliability failures**, never cryptographic SDC `[INFERRED]`.
- SDC strictly requires that decapsulation returns status 0 (success) while outputting an undetected, maliciously corrupted shared secret `[DIRECTLY OBSERVED]`.
- All execution anomalies are tracked in the **Intention-to-Test Reliability Table**, strictly separated from the **Cryptographic Integrity Table** `[PROPOSED / NOT YET TESTED]`.

---

## 4. Resolution of Task 3: D-05 (Protocol Contrast & Heterogeneous Weighting)

### 4.1 Estimand Definitions per Channel Class
For each channel class $c \in \{\text{BIT}, \text{DUP}, \text{REORDER}, \text{TRUNC}, \text{LOSS}, \text{DELAY}, \text{INTERRUPT}\}$, the condition-specific protocol completion rate is $p_{jk}(c) \in [0, 1]$, where:
- $j \in \{0, 1\}$ represents table state (0 = clean, 1 = mutated).
- $k \in \{0, 1\}$ represents channel state (0 = clean, 1 = armed with class $c$).
- Protocol completion ($Y = 1$) indicates that the initiator and responder successfully established matching shared keys within the retry budget ($\text{RETRY\_MAX} = 2$).

The channel-specific interaction contrast is:

$$\hat{\Delta}_c = \hat{p}_{11}(c) - \hat{p}_{10}(c) - \hat{p}_{01}(c) + \hat{p}_{00}(c)$$

- **No Zero Assumption:** The design makes **no assumption** that $p_{10} = 0$ or $p_{11} = 0$. For active twiddle faults, empirical evidence indicates $p_{10} \approx 0$ and $p_{11} \approx 0$. For dormant/sham controls, $p_{10} \approx 1$. Both are estimated empirically from data `[INFERRED]`.

### 4.2 Matched Seed Contributions
Every master seed assigned to class $c$ is evaluated under all four conditions using identical per-seed parameters (vector, twiddle index, bitmask, channel bit/length parameters, retry limit) `[DIRECTLY OBSERVED]`:
- Quota 1 ($N_1 = 300$): Contributes exclusively to $\hat{\Delta}_{\text{BIT}}$.
- Quota 2 ($N_2 = 40$): Contributes to $\hat{\Delta}_{\text{DUP}}$ ($n = 20$) and $\hat{\Delta}_{\text{REORDER}}$ ($n = 20$).
- Quota 3 ($N_3 = 60$): Contributes to $\hat{\Delta}_{\text{TRUNC}}$ ($n = 15$), $\hat{\Delta}_{\text{LOSS}}$ ($n = 15$), $\hat{\Delta}_{\text{DELAY}}$ ($n = 15$), and $\hat{\Delta}_{\text{INTERRUPT}}$ ($n = 15$).
- Quota 4 ($N_4 = 20$): Contributes to the negative control contrasts (dormant/sham baselines).

### 4.3 Primary Stratification vs. Exploratory Pooled Aggregates
- **Scientific Reality:** Channel classes represent radically disparate transport phenomena. For `CH_LOSS`, $p_{01} \approx 0$ (all frames dropped). For `CH_DUP`, $p_{01} \approx 1$ (duplicates absorbed by transport). For `CH_BIT`, $p_{01}$ depends on retry clearance.
- **Flaw of Unweighted Pooling:** Pooling Quotas 1–3 into an unweighted average yields an arbitrary mixture determined by the sample ratios ($300:40:60$), which has no physical or mathematical meaning `[INFERRED]`.
- **Locked Analysis Policy:**
  1. **Primary Protocol Analysis:** **Stratified by Channel Class**. The seven estimates $\hat{\Delta}_{\text{BIT}}, \hat{\Delta}_{\text{DUP}}, \dots, \hat{\Delta}_{\text{INTERRUPT}}$ are reported individually with paired bootstrap 95% confidence intervals (clustered at the master seed level) `[PROPOSED / NOT YET TESTED]`.
  2. **Exploratory Standardized Aggregate:** Any single summary contrast across active channel classes is designated strictly **EXPLORATORY** and must apply **fixed equal mechanism weights** ($w_c = 1/7$ for each class):
     $$\hat{\Delta}_{\text{std}} = \frac{1}{7} \sum_{c \in \text{Active Classes}} \hat{\Delta}_c$$
     This guarantees that the aggregate is not biased by sample size allocations `[PROPOSED / NOT YET TESTED]`.

### 4.4 Handling Missing and Failed Condition Records
- **Primary Strategy (Intention-to-Test Failure Imputation):** If a master seed suffers an execution crash (e.g. `SIGSEGV`) in Condition $C_{11}$, that condition outcome is coded as protocol failure ($Y_{i, 11} = 0$). This preserves the complete, balanced paired quadruple for seed $i$ across all four conditions `[PROPOSED / NOT YET TESTED]`.
- **Secondary Sensitivity Strategy (Complete-Case Pairing):** Evaluated strictly on the subset of seeds where all four conditions completed without execution crash. If the complete-case estimate diverges from the ITT estimate, both must be published and the discrepancy explained `[PROPOSED / NOT YET TESTED]`.
- **Strict Prohibition:** Under no circumstances may marginal condition probabilities be computed on differing seed sets without pairing `[PROPOSED / NOT YET TESTED]`.

---

## 5. Resolution of Task 4: D-06 (Test Vector Provenance and Inventory)

### 5.1 Verification of Existing Test Vector Artifacts
A thorough filesystem and source inspection was conducted across the workspace `[DIRECTLY OBSERVED]`:

1. **Official Static KAT Material Actually Present:**
   - [references/test_vectors/mlkem_expected_kat.h](file:///Users/dhairyajain/Desktop/pqc%20research/references/test_vectors/mlkem_expected_kat.h): Contains exactly **ONE static test vector** (`test_vector_d`, `test_vector_z`, `test_vector_m`) and golden ML-KEM-768 values (`mlkem768_expected_pk`, `sk`, `ct`, `ss`) derived from the official NIST FIPS 203 KAT suite `[DIRECTLY OBSERVED]`.
   - [tfib_experiments/phase11_oracle/kat_validation_results.json](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/phase11_oracle/kat_validation_results.json): Contains static execution validation records proving that `independent_oracle` correctly matched this single NIST KAT vector `[DIRECTLY OBSERVED]`.
2. **Locally Generated Vectors Existing on Disk:**
   - **Zero** locally generated test vectors exist as pre-computed, pre-validated files in the workspace `[DIRECTLY OBSERVED]`.
3. **Locally Generated Vectors Planned for Future Preflight:**
   - Exactly **419 test vectors** (Vectors 1 through 419) are specified to be deterministically generated at runtime using standardized FIPS 203 derandomized keypair/encaps interfaces seeded via SHAKE-256 PRF draws (`PHASE17D_FINAL_PREREGISTRATION.md` §4.1–§4.2) `[PROPOSED / NOT YET TESTED]`.
4. **Vector Counts Remaining Unverified:**
   - The algorithmic validity of all 419 locally generated vectors remains **unverified dynamically** because generating and cross-checking them requires compiling and executing C runner code, which is forbidden under read-only phase constraints `[UNKNOWN / UNVERIFIED]`.

### 5.2 Formal Evidentiary Demarcation
To eliminate ambiguity in future publications:
- **Vector 0:** Labeled strictly as `[DIRECTLY OBSERVED]` Official NIST FIPS 203 Reference KAT.
- **Vectors 1–419:** Labeled strictly as `[PROPOSED / NOT YET TESTED]` Deterministic Local Test Vectors. They **shall never be described as existing or pre-validated** until the C runner is compiled, the preflight cross-check pipeline runs against `liboqs v0.16.0`, and execution logs are produced.

---

## 6. Comprehensive Verification of Phase 17E Defects (Task 5)

| Defect ID | Original Evidence Source | Design-Level Resolution Status | What is Settled by Design Alone | What Requires Later Execution |
| :---: | :--- | :---: | :--- | :--- |
| **D-01** | `PHASE17D_FINAL_PREREGISTRATION.md` §2.2 omitted Quota 3 breakdown `[DIRECTLY OBSERVED]` | **RESOLVED ON PAPER** `[PROPOSED]` | Quota 3 frozen as exactly 15 seeds per class (TRUNC, LOSS, DELAY, INTERRUPT; total 60) | Generating manifest and verifying preflight passage across all 60 seeds |
| **D-02** | `PHASE17D_FINAL_PREREGISTRATION.md` §2.2 omitted Quota 4 grid `[DIRECTLY OBSERVED]` | **RESOLVED ON PAPER** `[PROPOSED]` | Quota 4 frozen as exactly 5 seeds per cell in $2 \times 2$ factorial grid (total 20) | Generating manifest and executing the 20 control sessions |
| **D-03** | Mathematical sensitivity: $n \ge 299$ needed for $< 1.0\%$ bound `[INDEPENDENTLY RECOMPUTED]` | **RESOLVED ON PAPER** `[INFERRED]` | Retained $N_1 = 300$; bound to honest shortfall rule without ungrounded sample inflation | Observing actual realized $n_{\text{completed}}$ during campaign execution |
| **D-04** | Shortfall formula divides by zero when $n_{\text{completed}} = 0$ `[INDEPENDENTLY RECOMPUTED]` | **RESOLVED ON PAPER** `[PROPOSED]` | Added formal exception rule: $n=0 \implies \text{UNDEFINED}$ (halt run, report no bound) | Runtime runner assertion halting on zero completed trials |
| **D-05** | Pooling Quotas 1–3 mixes disparate channel baselines `[DIRECTLY OBSERVED]` | **RESOLVED ON PAPER** `[PROPOSED]` | Stratified contrast declared primary; pooled aggregate declared exploratory with equal $1/7$ weighting | Computing bootstrap confidence intervals from empirical data |
| **D-06** | Only Vector 0 exists on disk; Vectors 1–419 are not pre-validated `[DIRECTLY OBSERVED]` | **RESOLVED ON PAPER** `[DIRECTLY OBSERVED]` | Evidentiary boundary locked: Vector 0 is static KAT; Vectors 1–419 are preflight generation specs | Executing 4-step cross-check pipeline (`liboqs` vs SUT) during runner preflight |

---

## 7. Defect Action Matrix and Evidentiary Gate Status

| Defect ID | Description | Severity | Evidence Category | Proposed Resolution | Verification Required for Closure | Gate Blocked |
| :---: | :--- | :---: | :---: | :--- | :--- | :---: |
| **D-01** | Quota 3 sub-class underspecification | Minor | `[PROPOSED / NOT YET TESTED]` | Freeze 15 seeds per sub-class ($15 \times 4 = 60$) | Manifest generation in runner | Blocks Campaign Execution |
| **D-02** | Quota 4 control grid underspecification | Minor | `[PROPOSED / NOT YET TESTED]` | Freeze 5 seeds per $2 \times 2$ cell ($5 \times 4 = 20$) | Manifest generation in runner | Blocks Campaign Execution |
| **D-03** | Zero-buffer attrition sensitivity in Quota 1 | Moderate | `[INFERRED]` | Retain $N_1 = 300$; enforce binding shortfall reporting | Realized count $n_{\text{completed}}$ in run ledger | Limits Realized Claim |
| **D-04** | Shortfall boundary division by zero ($n=0$) | Minor | `[PROPOSED / NOT YET TESTED]` | Explicit exception handling: $n=0 \implies \text{UNDEFINED}$ | C runner preflight assertion | Blocks Campaign Execution |
| **D-05** | Secondary contrast heterogeneous weighting | Minor | `[PROPOSED / NOT YET TESTED]` | Stratified contrast primary; equal $1/7$ weighting exploratory | Statistical script execution | Limits Aggregate Claims |
| **D-06** | Status of Vectors 1–419 (preflight vs static) | Minor | `[DIRECTLY OBSERVED]` | Formal demarcation: Vector 0 static, 1–419 preflight specs | Runner preflight cross-check logs | Blocks Campaign Execution |

---

## 8. Defensible Gate Decision (Task 6)

# **PASS — READY FOR SEPARATE IMPLEMENTATION REVIEW**

### Formal Justification:
1. **All Six Design Defects Fully Resolved on Paper:**
   - D-01 and D-02 are settled with exact integer allocations preserving all arithmetic totals ($N = 420$, $1,680$ trials).
   - D-03 is settled by retaining $N_1 = 300$ and strictly binding the study to the preregistered shortfall rule, avoiding ungrounded sample-size inflation.
   - D-04 is settled by formalizing the $n=0$ mathematical boundary exception.
   - D-05 is settled by mandating channel-stratified analysis as primary and restricting pooled aggregates to exploratory status with equal mechanism weights.
   - D-06 is settled by formally distinguishing the single existing static KAT from the 419 preflight generation specifications.
2. **Zero Open Design Decisions Remain:** No further design choices can be made purely on paper without implementing code or executing preflight checks.
3. **Strict Authorization Scope:** **This PASS verdict indicates only that the design specification is fully closed and ready for a separate implementation review.** It does **NOT** authorize compiling binaries, mutating virtual memory, linking harnesses, or executing fault-injection trials.

---

## 9. Cryptographic Hash and Repository Verification

### 9.1 Independently Computed SHA-256 Digests
Actual on-disk bytes of newly created and prior phase artifacts in `research/phase17_multi_fault_design/` were hashed via `shasum -a 256` `[DIRECTLY OBSERVED]`:

| Artifact Path | SHA-256 Digest | Status |
| :--- | :--- | :---: |
| `PHASE17_EXPERIMENT_DESIGN.md` | `36180af5fbf45a3f50b36f52d6375725020dd9577dfa5b89e40252e5e9479887` | **Preserved Unchanged** `[DIRECTLY OBSERVED]` |
| `PHASE17B_METHODS_CORRECTION.md` | `9180a13c1cf98050f05f3a426cc0d1102ce34c9d76ad48c9d51015f2931a25d4` | **Preserved Unchanged** `[DIRECTLY OBSERVED]` |
| `PHASE17B_CHANGELOG.md` | `f126e778f46dc562266408b80f8d373900e7d85dcdb3655ef68dfdcac7fa9edc` | **Preserved Unchanged** `[DIRECTLY OBSERVED]` |
| `PHASE17C_RESIDUAL_AUDIT.md` | `0e6c6e26120864297c592f26d7f77dd8c3fc10d7d3518f62fa4ffd2d08404c12` | **Preserved Unchanged** `[DIRECTLY OBSERVED]` |
| `PHASE17C_CHANGELOG.md` | `b5d99bb289b316c6f1515d0c31f21c25da11c4871929dd2bc480b044d2d1bccf` | **Preserved Unchanged** `[DIRECTLY OBSERVED]` |
| `PHASE17D_FINAL_PREREGISTRATION.md` | `474e72b8fd4516bc5723701d168eb58cffdd6f2a444caa302e4a6207a0a9b71d` | **Preserved Unchanged** `[DIRECTLY OBSERVED]` |
| `PHASE17D_CHANGELOG.md` | `6c3de8cf3c2ab52300394e8ccb5e1e3b8599c8553d201013f9c8057028b9a708` | **Preserved Unchanged** `[DIRECTLY OBSERVED]` |
| `PHASE17E_INDEPENDENT_AUDIT.md` | `259b0732c0d5032239462fb35d85e133e19173991e3cefedb7ebfe2d1796db88` | **Preserved Unchanged** `[DIRECTLY OBSERVED]` |
| `PHASE17E_CHANGELOG.md` | `e7f108543d9fda3e8b4c4334d39149e57a38daedc1546bdc6f6ce8c39aae4f11` | **Preserved Unchanged** `[DIRECTLY OBSERVED]` |
| `PHASE17F_DESIGN_DEFECT_RESOLUTION.md` | *(Computed upon file write)* | **New Deliverable** `[DIRECTLY OBSERVED]` |
| `PHASE17F_CHANGELOG.md` | *(Computed upon file write)* | **New Deliverable** `[DIRECTLY OBSERVED]` |

### 9.2 Git Status Verification
- Git status verified via `git status --porcelain research/phase17_multi_fault_design/` `[DIRECTLY OBSERVED]`.
- All prior phase artifacts remain intact and unmodified. No tracked files were altered, committed, or pushed.
