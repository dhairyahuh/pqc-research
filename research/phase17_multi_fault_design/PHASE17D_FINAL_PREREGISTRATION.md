# Phase 17D — Final Preregistration Lock and Implementation-Gate Review

**Author:** Skeptical Cryptographic Systems Auditor & Statistical Methodologist  
**Date:** 2026-10-11  
**Project:** Cross-Layer Fault Interactions in ML-KEM-768 Key Establishment  
**Status:** FINAL PREREGISTRATION LOCK (DESIGN ONLY — Strictly Read-Only)  
**Deliverable Directory:** `research/phase17_multi_fault_design/`  
**Execution Guard:** No implementation code written, no binaries built, no memory mutated, and no experiments executed.  

---

## 1. Frozen Primary Population and Accounting Funnel

### 1.1 Strict Definition of the Primary Cryptographic Population
The primary Silent Data Corruption (SDC) analysis population is strictly restricted to distinct master seeds meeting all five inclusion criteria:

$$\mathcal{P}_{\text{primary}} = \left\{ i \in [1, N] \ \middle\vert \begin{array}{l} \text{1. Evaluated under Condition } C_{11} \text{ on Attempt } a = 1; \\ \text{2. Twiddle Target } k \in [1, 127] \text{ with Bitmask } \neq 0x0000 \text{ (Active Mutation)}; \\ \text{3. Wire Ciphertext } \tilde{c} \text{ Delivered with Bit Mutation via } CH\_BIT; \\ \text{4. Decapsulation Invoked on Darwin ARM64 } (decaps\_ran == 1); \\ \text{5. Vector Independently Validated during Preflight with Verified Oracle Inputs.} \end{array} \right\}$$

### 1.2 Five-Tier Intention-To-Test (ITT) Accounting Funnel
To guarantee that no experimental anomalies, execution errors, or unexpected outputs are silently discarded or replaced, every drawn master seed must be tracked through a 5-tier accounting funnel:

```
[ Tier 1: Assigned Scenarios (N_assigned) ]
       |  (Static Pre-Allocation via Master PRF Seed)
       v
[ Tier 2: Eligible Scenarios (N_eligible) ]
       |  (Passed Vector Preflight Verification & Valid Parameter Bounds)
       v
[ Tier 3: Attempted Invocations (N_attempted) ]
       |  (Session Initiated; Page Unprotected & Mutated on Darwin ARM64)
       v
[ Tier 4: Completed Decapsulations (N_completed) ]
       |  (Wire Delivered; Decapsulation Executed Without Hardware Trap)
       v
[ Tier 5: Analysable Cryptographic Outcomes (N_analysable) ]
          (32-Byte Secret Classified Against Independent Oracles)
```

### 1.3 Prespecified Rules for Exceptions and Hardware Anomalies
No scenario may be discarded or replaced based on its empirical outcome. Any exception is retained in the authoritative ledger and classified according to prespecified rules:

| Anomaly Category | Trigger Condition | Ledger Status | Impact on Primary SDC Denominator ($\mathcal{D}_{\text{SDC}}$) | Reporting Obligation |
| :--- | :--- | :--- | :---: | :--- |
| **Preflight Vector Failure** | Keygen/encaps mismatch between SUT and `liboqs` | `INELIGIBLE_VECTOR` | Excluded (Detected before session start) | Logged in preflight ledger; reported in attrition table. |
| **Oracle Derivation Error** | TweetFIPS-202 SHAKE-256 rejects vector length | `ORACLE_FAILURE` | Excluded (Harness integrity failure) | Halts runner immediately (Fail-Closed Gate). |
| **Hardware Trap Signal** | Mach-O access triggers `SIGBUS` or `SIGSEGV` | `SIGNAL_TERMINATION` | **Counted as Execution Failure** | Logged as critical reliability failure; triggers process exit. |
| **Restoration Failure** | Post-trial table SHA-256 $\neq$ Golden Digest | `RESTORATION_FAILED` | **Counted in Attrition; Halts Run** | Halts entire campaign immediately to prevent cross-contamination. |
| **Missing Output / Non-Zero RC** | `mlkem768_dec` returns non-zero error code | `EXECUTION_FAILURE` | **Counted as Non-SDC Failure** | Classified under `EXECUTION_FAILURE`; retained in ITT table. |

---

## 2. Frozen Sampling Plan and Fixed Quotas

### 2.1 Elimination of Probabilistic Strata Shortfall
To eliminate the statistical shortfall risk identified in Phase 17C (where a 75% random draw across 400 seeds carries a $\sim 50\%$ risk of failing to reach the $n \ge 300$ threshold), the campaign freezes **exact stratified block quotas**.

### 2.2 Frozen Quota Allocation Table

| Quota ID | Architectural Stratum | Twiddle Mutation Category | Channel Class Allocation | Frozen Seed Quota ($N$) | Matched Trial Records ($4N$) | Role in Analysis |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| **Quota 1** | **Admitted-Corrupted** | Active ($k \in [1, 127]$, mask $\neq 0$) | `CH_BIT` (Ciphertext Bit Inversion) | **$N_1 = 300$** | **1,200** | **Primary Cryptographic SDC Analysis** |
| **Quota 2** | **Admitted-Clean** | Active ($k \in [1, 127]$, mask $\neq 0$) | `CH_DUP` (20) & `CH_REORDER` (20) | **$N_2 = 40$** | **160** | Secondary Protocol Sequence Analysis |
| **Quota 3** | **Delivery-Blocking** | Active ($k \in [1, 127]$, mask $\neq 0$) | `CH_TRUNC`, `LOSS`, `DELAY`, `INTERRUPT` | **$N_3 = 60$** | **240** | Protocol Masking & Attrition Analysis |
| **Quota 4** | **Negative Controls** | Dormant ($k=0$) & Sham (mask = 0) | Clean (10) & `CH_BIT` (10) | **$N_4 = 20$** | **80** | Harness Neutrality & Negative Control |
| **TOTAL** | — | — | — | **$N = 420$** | **1,680** | Total Confirmatory Campaign |

### 2.3 Non-Replacement Quota Acquisition Rule
1. Master seeds $i = 1, 2, 3, \dots$ are evaluated sequentially during preflight.
2. For each master seed, candidate parameters are generated deterministically.
3. If an eligible scenario satisfies Quota 1, it is placed in Quota 1 until exactly 300 eligible definitions are obtained.
4. Quotas 2, 3, and 4 are filled similarly until all 420 scenario definitions are locked.
5. The complete scenario manifest is hashed with SHA-256 and frozen **before any runtime memory mutation occurs**. No post-hoc replacement is permitted during or after execution.

### 2.4 Preregistered Shortfall Rule
If runtime hardware traps or unhandled execution errors reduce the realized completed count of Quota 1 trials below 300 ($n_{\text{completed}} < 300$):
- The report **shall not claim** an upper bound below 1.0%.
- The report shall explicitly publish the realized exact Clopper-Pearson bound:
  $$p_{\text{realized}} = 1 - (0.05)^{1/n_{\text{completed}}}$$
- The shortfall count and exact root causes shall be documented in the final audit ledger.

---

## 3. Frozen Matched Four-Condition Design

### 3.1 Per-Seed Matched Scenario Invariants
For every master seed $i$, the following parameters are drawn once and held strictly identical across all four conditions ($C_{00}, C_{10}, C_{01}, C_{11}$):
- `vector_id`: Master seed $i \implies pk_i, sk_i, c_i, z_i, K_{\text{golden}, i}$.
- `table_target_idx`: Twiddle factor index $k \in [0, 127]$.
- `table_bitmask`: 16-bit mutation mask (e.g. `0x0001`, `0x8000`, `0x0000`).
- `channel_class`: Assigned channel class (`CH_BIT`, `CH_TRUNC`, etc.).
- `channel_event_params`: Bit position $pos \in [0, 1087]$, bitmask $1 \ll b$, truncation length, latency.
- `channel_persistence`: `TRANSIENT` ($50\%$) or `PERSISTENT` ($50\%$).
- `retry_budget`: $\text{RETRY\_MAX} = 2$ (up to 3 attempts total).
- `deadline`: Logical delivery deadline $D = 100$.

### 3.2 Four-Condition Execution Matrix

| Condition | Memory Table State | Wire Channel State | Persistent Lifetime Rule | Primary Scientific Purpose |
| :---: | :--- | :--- | :--- | :--- |
| **$C_{00}$** | Pristine (`golden_zetas`) | Clean (`CH_CLEAN`) | Table unmodified throughout session | Clean baseline verification ($p_{00} \equiv 1.0$) |
| **$C_{10}$** | Mutated ($k, mask$) | Clean (`CH_CLEAN`) | Mutated before Attempt 1; held across retries | Isolated persistent-table effect ($p_{10}$) |
| **$C_{01}$** | Pristine (`golden_zetas`) | Armed (`channel_class`) | Redrawn on retry if `TRANSIENT` | Isolated channel effect ($p_{01}$) |
| **$C_{11}$** | Mutated ($k, mask$) | Armed (`channel_class`) | Mutated before Attempt 1; held across retries | Combined multi-fault interaction ($p_{11}$) |

### 3.3 Attempt-Level Fixed vs. Varying Parameters
- **Fixed Across Attempts:**
  - In $C_{10}$ and $C_{11}$, the twiddle table mutation is applied to Darwin ARM64 virtual memory prior to Attempt 1 and **remains in place across Attempts 1, 2, and 3**. It is restored only after the session reaches a terminal state.
- **Varying Across Attempts:**
  - If `channel_persistence == TRANSIENT`, Attempt 1 applies the channel fault, but Attempts 2 and 3 deliver clean wire frames (link clears).
  - If `channel_persistence == PERSISTENT`, the channel fault recurs on Attempts 2 and 3.

---

## 4. Oracle and Vector Provenance Pipeline

### 4.1 Strict Vector Provenance Demarcation
- **Official NIST Reference Vector (Vector 0):** Vector 0 is the static test vector defined in `references/test_vectors/mlkem_expected_kat.h` (NIST FIPS 203 KAT reference).
- **Locally Generated Test Vectors (Vectors 1 through 419):** Vectors 1–419 are **locally generated deterministic test vectors** derived via standardized FIPS 203 derandomized interfaces. Artifacts shall not describe them as official NIST-published vectors.

### 4.2 Independent Cross-Implementation Verification Pipeline
Prior to freezing the scenario pool, every generated vector must pass an automated 4-step cross-check:

```
                  Master Seed i
                        |
            SHAKE-256 PRF ("kemkp" / "kemenc")
                        |
            seed64_i (64B)   seed32_i (32B)
                   |                |
    +--------------+                +--------------+
    |                                              |
[ Step 1: Keypair Cross-Check ]     [ Step 2: Encaps Cross-Check ]
  mlkem-native (pk, sk)               mlkem-native (ct, ss)
          vs.                                 vs.
  liboqs v0.16.0 (pk, sk)             liboqs v0.16.0 (ct, ss)
  ASSERT(pk match && sk match)        ASSERT(ct match && ss match)
                   |                               |
                   +---------------+---------------+
                                   |
                   [ Step 3: Decaps Baseline Check ]
                     mlkem-native decaps(ct, sk) == ss
                     ASSERT(dec_rc == 0 && ss match)
                                   |
                   [ Step 4: Standalone Rejection Check ]
                     TweetFIPS-202 SHAKE256(z || ct, 32) == Krej
                     ASSERT(Krej != ss)
```

If any vector fails any check, it is marked `BLOCKED` and excluded before runner compilation.

### 4.3 Dynamic Wire-Ciphertext Rejection Oracle
During Condition $C_{11}$ execution under `CH_BIT`, ciphertext $c$ is corrupted into $\tilde{c}$.
- The rejection oracle **must derive** $K_{\text{rej}}(\tilde{c})$ using the **exact 1088 bytes delivered to the receiver** ($\tilde{c}$) and the secret key seed $z_i$ extracted from $sk_i$:
  $$K_{\text{rej}}(\tilde{c}) = \text{SHAKE256}(z_i \parallel \tilde{c}, 32)$$
- The oracle implementation must reside in a standalone compilation unit (`fips202_ref.c`), completely independent of the SUT and `liboqs`.

---

## 5. Frozen Estimands and Statistical Decision Rules

### 5.1 Primary Cryptographic Estimand (Attempt 1 SDC Rate)
The primary endpoint evaluates the empirical SDC rate within Quota 1 ($N_1 = 300$ active `CH_BIT` trials):

$$\hat{p}_{\text{SDC}} = \frac{\#\{i \in \text{Quota 1} : ss_i \neq K_{\text{golden}, i} \land ss_i \neq K_{\text{rej}}(\tilde{c}_i)\}}{n_{\text{completed}}}$$

- **Primary Statistical Decision Rule:**
  If zero SDC events are observed ($k = 0$) across $n_{\text{completed}} = 300$ completed trials, the report shall state:
  - **Exact One-Sided 95% Clopper-Pearson Upper Bound:** $\mathbf{0.9934\%}$ (strictly $< 1.0\%$).
  - **One-Sided 95% Wilson Score Bound:** $\mathbf{0.8938\%}$.
  - **Two-Sided 95% Wilson Score Bound:** $\mathbf{1.2643\%}$.
- **Epistemological Boundary:** An upper bound of $0.993\%$ **does not constitute proof of zero risk or mathematical immunity**. It establishes an empirical upper bound of $0.993\%$ at 95% confidence under the tested model and sample size.

### 5.2 Secondary Protocol Estimand (Unconstrained Interaction Contrast)
The protocol-level interaction contrast is evaluated as an unconstrained empirical estimand:

$$\hat{\Delta}_{\text{proto}} = \hat{p}_{11} - \hat{p}_{10} - \hat{p}_{01} + \hat{p}_{00}$$

- **Inference Method:** Evaluated via paired nonparametric bootstrap over master seeds ($B = 10{,}000$, percentile method).
- **Stratified Reporting:**
  - Evaluated separately for Population 1 (Active Non-Dormant Twiddle Faults, Quotas 1–3) and Population 2 (Negative Controls, Quota 4).
  - Explicitly classified by failure mechanism: `FAIL_CRYPTO_REJECTION`, `FAIL_CHANNEL_DROP`, `FAIL_FRAME_MALFORMED`, and `EXECUTION_FAILURE`.

### 5.3 Handling of Repeated Retransmission Attempts
- **Primary Analysis:** Restricted strictly to Attempt 1 ($a = 1$) independent observations across distinct master seeds.
- **Secondary Retransmission Analysis:** Retransmissions ($a \in [2, 3]$) within a session share secret keys and persistent mutations. They shall be evaluated using **cluster-robust standard errors** clustered at the master seed level.

---

## 6. Implementation-Gate Verification Checklist

The checklist below inspects all prerequisite artifacts and verifies whether the design is locked for implementation:

| Gate Item | Requirement Description | Verification Evidence | Static vs. Dynamic Status | Verdict |
| :---: | :--- | :--- | :---: | :---: |
| **G-01** | Primary SDC population strictly restricted to Attempt 1 active twiddle $\times$ `CH_BIT` | `PHASE17D_FINAL_PREREGISTRATION.md` §1.1 | Static Inspection (Design) | **PASS** |
| **G-02** | Fixed quota block sampling locks exactly $N_1 = 300$ eligible active `CH_BIT` cases | `PHASE17D_FINAL_PREREGISTRATION.md` §2.2 | Static Inspection (Design) | **PASS** |
| **G-03** | Exact Clopper-Pearson bound calculation mathematically verified ($0.993\% < 1.0\%$) | $1 - 0.05^{1/300} = 0.009934$ (§5.1) | Mathematical Derivation | **PASS** |
| **G-04** | Intention-To-Test accounting table pre-specified for execution anomalies | `PHASE17D_FINAL_PREREGISTRATION.md` §1.3 | Static Inspection (Design) | **PASS** |
| **G-05** | Negative controls (Index 0, sham) partitioned into separate Quota 4 ($N=20$) | `PHASE17D_FINAL_PREREGISTRATION.md` §2.2 | Static Inspection (Design) | **PASS** |
| **G-06** | Channel control flow traced: `CH_BIT` verified as sole ciphertext-mutating class | `combined_campaign.c:98-125` | Source Code Inspection | **PASS** |
| **G-07** | Vector inventory verified: 1 static NIST KAT + 419 locally generated cases | `references/test_vectors/mlkem_expected_kat.h` | Workspace File Inspection | **PASS** |
| **G-08** | 4-step cross-implementation vector validation pipeline defined (`liboqs` vs SUT) | `PHASE17D_FINAL_PREREGISTRATION.md` §4.2 | Static Inspection (Design) | **PASS** |
| **G-09** | Dynamic rejection oracle uses received ciphertext $\tilde{c}$ and matching seed $z_i$ | `independent_oracle.c:59-65` | Source Code Inspection | **PASS** |
| **G-10** | Unconstrained protocol contrast $\hat{\Delta}_{\text{proto}}$ defined without assuming $p_{10}=0$ | `PHASE17D_FINAL_PREREGISTRATION.md` §5.2 | Mathematical Derivation | **PASS** |
| **G-11** | Darwin ARM64 virtual memory isolation qualified on `(__DATA_CONST,__zetas_page)` | Phase 15Q pilot & Phase 15R audit | Prior Audited Artifacts | **PASS** |
| **G-12** | Compilation and execution deferred until separate authorized implementation gate | Read-only constraint enforced | Process Boundary | **PASS** |

---

## 7. Final Implementation-Gate Recommendation

# **GO TO IMPLEMENTATION REVIEW**

### Summary of Recommendation:
1. **Design is Completely Locked:** All statistical plans, population boundaries, sampling quotas, control-flow mappings, and oracle validation pipelines are mathematically exact, grounded in actual C source code, and formally frozen.
2. **Methodological Deficiencies Resolved:** The sample-size plan guarantees an exact Clopper-Pearson upper bound of $0.9934\%$ ($< 1.0\%$) across 300 active `CH_BIT` decapsulations without outcome-dependent replacement.
3. **Execution Guard Maintained:** **No experiment is authorized or executed by this document.** The transition from locked preregistration to C runner implementation requires formal human operator review and explicit authorization in a subsequent phase.
