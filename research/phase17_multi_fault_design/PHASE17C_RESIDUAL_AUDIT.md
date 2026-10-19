# Phase 17C — Independent Audit of Residual Statistical and Implementation-Semantics Defects

**Author:** Skeptical Cryptographic Systems Auditor & Statistical Methodologist  
**Date:** 2026-10-11  
**Project:** Cross-Layer Fault Interactions in ML-KEM-768 Key Establishment  
**Status:** DESIGN AUDIT ONLY (Strictly Read-Only — No Code Modification, No Memory Mutation, No Build Execution)  
**Target Specifications Audited:**
- `research/phase17_multi_fault_design/PHASE17_EXPERIMENT_DESIGN.md` (preserved unchanged)
- `research/phase17_multi_fault_design/PHASE17B_METHODS_CORRECTION.md` (preserved unchanged)
**Deliverable Directory:** `research/phase17_multi_fault_design/`  

---

## 1. Executive Summary & Audit Context

Phase 17B resolved major high-level defects in sample size, fault taxonomy, and test-vector provenance. This Phase 17C audit conducts a fine-grained, independent examination of residual statistical assumptions and low-level C control-flow semantics. 

In strict adherence to experimental safety rules:
- No source files outside the new design audit artifacts were edited.
- No binaries were compiled or linked.
- No live memory mutations or `vm_protect` API calls were executed.
- No campaign runs were initiated.
- All historical Phase 17 and Phase 17B artifacts remain 100% byte-identical.

---

## 2. Section A: Sample-Size Guarantees & Realized SDC Denominator

### 2.1 Planned Stratum Allocation vs. Realized Eligible Observations
In Phase 17B, a 75% allocation to Stratum A (delivery-admitted) was proposed across $N = 400$ seeds, claiming $n_{\text{admitted}} = 300$.
- **The Probabilistic Shortfall Risk:** If channel class assignment is purely probabilistic (i.e. each seed independently draws Stratum A with probability $0.75$), the realized count of admitted seeds follows $\text{Binomial}(400, 0.75)$.
  - Mean = $300$, Standard Deviation $\sigma = \sqrt{400 \times 0.75 \times 0.25} = \sqrt{75} \approx 8.66$.
  - The probability that the realized sample size falls below the required threshold of $300$ is approximately $50\%$. If $n_{\text{realized}} = 285$, the exact Clopper-Pearson bound would be $1 - (0.05)^{1/285} = 1.045\%$, failing the $< 1.0\%$ preregistration criterion.
- **The Inactive Mutation Shortfall Risk:** If a seed draws a dormant index ($k = 0$) or a sham mask (`0x0000`), the twiddle table is not actively corrupted. If these are excluded from the active SDC denominator, $n_{\text{active}}$ shrinks by an additional $\approx 1.5\%$.

### 2.2 Stratified Block Sampling with Fixed Quotas
To eliminate probabilistic shortfall, the design must mandate **fixed quota block sampling**:
1. **Sampling Structure:** The scenario generator generates seeds partitioned into exact pre-allocated strata:
   - **Stratum A (Delivery-Admitted):** Exactly $N_{\text{admitted}} = 300$ active, valid seeds.
   - **Stratum B (Delivery-Blocking):** Exactly $N_{\text{blocking}} = 100$ valid seeds.
   - **Stratum C (Controls):** Exactly $N_{\text{control}} = 20$ dormant/sham seeds (evaluated separately).
2. **Handling Ineligible or Excluded Seeds:**
   - A seed is ineligible if a preflight check fails or an invalid parameter is generated.
   - *Normative Ineligibility Rule:* Ineligible seeds are logged in the authoritative ledger with `status = INELIGIBLE` and retained. They are **not** replaced based on observed experimental outcomes. Instead, master seeds $1, 2, \dots$ are drawn sequentially until the pre-registered quota of eligible scenario definitions is filled prior to runtime execution.

### 2.3 Exact Definition of the Primary SDC Denominator
To prevent unit conflation across sessions, decapsulation invocations, and retransmission attempts, the primary SDC denominator is formally defined as:

$$\mathcal{D}_{\text{SDC}} = \left\{ i \in [1, N] \ \middle\vert \begin{array}{l} \text{Condition } C_{11}, \text{Attempt } a = 1, \\ \text{Twiddle Target } k \in [1, 127], \text{Bitmask } \neq 0x0000, \\ \text{Wire Ciphertext } \tilde{c} \text{ Delivered to Receiver}, \\ \text{Decapsulation Invocation Executed } (decaps\_ran == 1) \end{array} \right\}$$

- **Session-Level SDC Rate:** Proportions are evaluated strictly on Attempt 1 across distinct master seeds ($|\mathcal{D}_{\text{SDC}}| = n_{\text{active\_admitted}}$).
- **Secondary Pooled Invocations:** Decapsulations occurring during retries ($a > 1$) are reported in a secondary table using **cluster-robust standard errors** clustered at the master seed level, explicitly acknowledging non-independence.

### 2.4 Recalculation of Upper Bounds for Zero SDC Events ($k = 0$)
The table below recalculates the exact mathematical upper bounds across candidate sample sizes:

| Sample Size ($n$) | One-Sided 95% Wilson Score Bound ($z = 1.64485$) | Two-Sided 95% Wilson Score Bound ($z = 1.95996$) | Exact Clopper-Pearson 95% Bound ($1 - 0.05^{1/n}$) | Rule of Three Approximation ($3/n$) | Satisfies $< 1.0\%$ Target? |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **$n = 200$** | **1.3347%** | **1.8847%** | **1.4867%** | 1.5000% | **NO** (Exceeds 1.0%) |
| **$n = 268$** | **0.9994%** | **1.4131%** | **1.1114%** | 1.1194% | **Conditional** (One-sided Wilson only) |
| **$n = 300$** | **0.8938%** | **1.2643%** | **0.9934%** | 1.0000% | **YES** (One-sided & Clopper-Pearson) |
| **$n = 381$** | **0.7051%** | **0.9982%** | **0.7832%** | 0.7874% | **YES** (All methods including Two-sided) |

*Methodological Clarification:* Wilson score is an asymptotic score test inversion with continuity adjustment; it is **not** an exact interval. Clopper-Pearson represents the exact non-parametric binomial confidence limit based on the Beta distribution.

### 2.5 Preregistered Stopping & Shortfall Rule
- **The Realized Bound Commitment:** If post-run accounting reveals $|\mathcal{D}_{\text{SDC}}| < 300$ eligible active trials, the final report **must not** claim an upper bound below 1.0%. It must publish the exact realized Clopper-Pearson bound $p_U = 1 - 0.05^{1/n_{\text{realized}}}$.

---

## 3. Section B: Protocol Contrast Validity & Simplification Boundaries

### 3.1 Audit of the Identity $\hat{\Delta}_{\text{proto}} = 1 - p_{01}$
In Phase 17B, the interaction contrast was stated as $\hat{\Delta}_{\text{proto}} = 1 - p_{01}$, derived from $\hat{\Delta} = p_{11} - p_{10} - p_{01} + p_{00}$ under the assumption that $p_{00} = 1.0$ and $p_{10} = p_{11} = 0.0$.

### 3.2 Failure of the Zero-Completion Assumption on Controls
The assumption $p_{10} = p_{11} = 0.0$ fails under three specific conditions:
1. **Dormant Index 0 ($k = 0$):** Bitflips in `zetas[0]` are mathematically unconsumed. Decapsulation reproduces $K_{\text{golden}}$, yielding $p_{10} = 1.0$.
2. **Sham Controls (`mask = 0x0000`):** No bits are altered. Clean decapsulation succeeds, yielding $p_{10} = 1.0$.
3. **Ineffective Arithmetic Perturbations:** If a twiddle perturbation is annihilated by zero polynomial coefficients in a specific test vector, decapsulation can emit $K_{\text{golden}}$, yielding $p_{10} > 0$.

### 3.3 Population Stratification
To ensure mathematical validity, the protocol contrast must be evaluated over strictly demarcated sub-populations:

- **Population 1 (Active Non-Dormant Twiddle Faults):** $k \in [1, 127]$ and $\text{mask} \neq 0x0000$.
  - *Applicability:* This is the primary population for evaluating persistent arithmetic corruption.
  - *Theoretical Bound:* If all active faults induce implicit rejection, $p_{10} = p_{11} = 0.0$, and the contrast reduces to $\hat{\Delta}_{\text{proto}} = 1.0 - p_{01}$.
- **Population 2 (Negative Controls & Sham Mutations):** $k = 0$ or $\text{mask} = 0x0000$.
  - *Applicability:* Sanity verification of harness transparency.
  - *Expected Value:* $p_{10} = 1.0$, $p_{11} = p_{01} \implies \hat{\Delta}_{\text{proto}} = p_{01} - 1.0 - p_{01} + 1.0 = \mathbf{0.0}$.

### 3.4 Unconstrained General Contrast Specification
The empirical analysis must evaluate the unconstrained empirical contrast:
$$\hat{\Delta}_{\text{proto}} = \hat{p}_{11} - \hat{p}_{10} - \hat{p}_{01} + \hat{p}_{00}$$
The simplified expression $\hat{\Delta} = 1 - p_{01}$ must be reported strictly as a **conditional theoretical benchmark** under Population 1, not as an unexamined algebraic identity.

### 3.5 Disentangling Protocol Failure Modes
Every protocol abort is classified into mutually exclusive causal categories:
1. **`FAIL_CRYPTO_REJECTION`:** Wire frame delivered, decapsulation executed, but FIPS 203 implicit rejection ($K_{\text{rej}}$) caused MAC tag verification failure, exhausting retries.
2. **`FAIL_CHANNEL_DROP`:** Message lost, link interrupted, or deadline expired prior to decapsulation intake.
3. **`FAIL_FRAME_MALFORMED`:** Wire length truncated or framing header invalid before decapsulation.

---

## 4. Section C: Channel Semantics Verification Against C Implementation

An independent inspection of `research/combined_harness/combined_campaign.c` (lines 70–130) traced the exact control flow for all 7 channel classes:

### 4.1 Exhaustive Control-Flow Trace Table

| Channel Class | Code Constant | Frame Intake Reached? | Frame/Seq Validation Passed? | Decapsulation Invoked? (`decaps_ran`) | Ciphertext Bytes Mutated? | Resulting Immediate Outcome | Retry Trigger |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Bit Corruption** | `CH_BIT` (1) | **YES** | **YES** | **YES** | **YES** (`wire[pos] ^= bit`) | `K_MISMATCH` (MAC tag fail) | Retransmission drawn |
| **Duplication** | `CH_DUP` (5) | **YES** | **YES** | **YES** | **NO** (Clean ciphertext) | `K_EST` (Clean key agreed) | No retry (Completes) |
| **Reorder** | `CH_REORDER` (6) | **YES** | **NO** (Seq $-100$) | **YES** | **NO** (Clean ciphertext) | `K_MALFORMED` (Seq out of window) | Retransmission drawn |
| **Truncation** | `CH_TRUNC` (2) | **YES** | **NO** (Length $< WIRE$) | **NO** | N/A (Frame dropped) | `K_MALFORMED` (Length fail) | Retransmission drawn |
| **Packet Loss** | `CH_LOSS` (3) | **NO** | **NO** | **NO** | N/A (Frame dropped) | `K_LOST` (Non-delivery) | Retransmission drawn |
| **Delay** | `CH_DELAY` (4) | **YES** | **NO** (Latency $> D$) | **NO** | N/A (Deadline expired) | `K_TIMEOUT` (Deadline fail) | Retransmission drawn |
| **Interruption** | `CH_INTERRUPT` (7) | **NO** | **NO** | **NO** | N/A (Carrier drop) | `K_LOST` (Link down) | Retransmission drawn |

### 4.2 Material Implementation Findings
1. **The Unique Role of `CH_BIT`:**  
   `CH_BIT` is the **only channel class in the entire codebase that passes a mutated ciphertext $\tilde{c}$ to decapsulation**.
2. **Behavior of `CH_DUP` and `CH_REORDER`:**  
   Both classes invoke decapsulation, but they pass the **clean, unmodified ciphertext $c$**. Under Condition $C_{11}$, they evaluate clean ciphertext $\times$ corrupted twiddle table, which is functionally identical to Condition $C_{10}$.
3. **Guaranteed Decapsulation Denominator Definition:**  
   To guarantee that the primary SDC analysis tests simultaneous dual corruption ($\tilde{c} \times \tilde{\zeta}$), the primary SDC stratum must consist **strictly of `CH_BIT` (Bit Corruption) trials**.
   - Trials under `CH_DUP` and `CH_REORDER` are classified into a secondary "Clean-Wire Decapsulation" sub-stratum.
   - Trials under `CH_TRUNC`, `CH_LOSS`, `CH_DELAY`, and `CH_INTERRUPT` form the "Pre-Execution Delivery-Blocking" stratum.

---

## 5. Section D: Generated-Vector Plan & Independent Verification Protocol

### 5.1 Verification of Local Vector Inventory
- **Official KAT Vector:** [references/test_vectors/mlkem_expected_kat.h](file:///Users/dhairyajain/Desktop/pqc%20research/references/test_vectors/mlkem_expected_kat.h) contains strictly **1 static NIST KAT vector** for ML-KEM-768 (`NIST-FIPS203-KAT-768`).
- **Locally Derived Test Vectors:** The remaining 399 vectors must be generated deterministically via standardized PRF seeding.
- **Nomenclature Rule:** Artifacts must strictly refer to *"1 NIST KAT Reference Vector + 399 Locally Generated Deterministic Test Vectors"*.

### 5.2 Four-Step Preflight Verification Pipeline Per Generated Vector
Before any generated vector is admitted into the fault-injection campaign, it must pass a 4-step cross-implementation self-test during preflight:

```
[ Master Seed i ] ---> SHAKE-256 PRF ---> (seed64_i, seed32_i)
                                 |
 [ Step 1: Cross-Implementation Keypair Generation Check ]
   OQS_KEM_ml_kem_768_keypair_derand(pk_liboqs, sk_liboqs, seed64_i)
   mlkem768_keypair_derand(pk_sut, sk_sut, seed64_i)
   ASSERT(memcmp(pk_liboqs, pk_sut, 1184) == 0)
   ASSERT(memcmp(sk_liboqs, sk_sut, 2400) == 0)
                                 |
 [ Step 2: Cross-Implementation Encapsulation Check ]
   OQS_KEM_ml_kem_768_encaps_derand(ct_liboqs, ss_liboqs, pk, seed32_i)
   mlkem768_enc_derand(ct_sut, ss_sut, pk, seed32_i)
   ASSERT(memcmp(ct_liboqs, ct_sut, 1088) == 0)
   ASSERT(memcmp(ss_liboqs, ss_sut, 32) == 0)
                                 |
 [ Step 3: Clean Baseline Decapsulation Check ]
   mlkem768_dec(ss_dec, ct, sk)
   ASSERT(memcmp(ss_dec, ss_liboqs, 32) == 0)
                                 |
 [ Step 4: Standalone Rejection Oracle KAT Pre-Derivation ]
   independent_oracle_compute_rejection(ss_rej, sk, ct)
   ASSERT(memcmp(ss_rej, ss_liboqs, 32) != 0)
   ASSERT(ss_rej matches independent TweetFIPS-202 SHAKE256(z || ct, 32))
```

Only vectors passing all 4 gates with zero differences are serialized into the scenario pool.

---

## 6. Section E: Residual Uncertainty Matrix & Final Decision

### 6.1 Residual Uncertainty Matrix

| Issue Category | Code / Document Evidence | Methodological Resolution | Residual Uncertainty / Limitation |
| :--- | :--- | :--- | :--- |
| **Statistical Bound Realization** | Wilson upper bound on $n=200$ is $1.88\%$; target $< 1.0\%$ requires $n \ge 300$. | Mandated fixed-quota block sampling allocating $300$ active `CH_BIT` trials; exact Clopper-Pearson bound $= 0.993\%$. | Relies on zero SDC events being observed. |
| **Sample Unit Clutter** | Multiple attempts within a seed share secret key and persistent twiddle mutation. | Evaluated primary SDC strictly on Attempt 1 independent draws; secondary pooled attempts evaluated via clustered bootstrap. | Microarchitectural caching across attempts. |
| **Channel Implementation Semantics** | In `combined_campaign.c`, only `CH_BIT` passes corrupted ciphertext; `CH_DUP`/`CH_REORDER` pass clean ciphertext. | Formally partitioned into: (1) Admitted-Corrupted (`CH_BIT`), (2) Admitted-Clean (`CH_DUP`, `CH_REORDER`), (3) Delivery-Blocking (remaining 4 classes). | Abstract simulated framing vs. real CCSDS telemetry transport. |
| **Contrast Degeneracy on Controls** | Dormant Index 0 and sham masks yield $p_{10} = 1.0$, violating $\hat{\Delta} = 1 - p_{01}$. | Partitioned analysis into Population 1 (active mutations) and Population 2 (controls); general contrast unconstrained. | Ineffective twiddle mutations in specific polynomial coefficients. |
| **Vector Provenance** | Only 1 official static NIST KAT vector exists in repo (`mlkem_expected_kat.h`). | Disclosed 1 official KAT + 399 locally derived vectors verified via 4-step cross-implementation pipeline. | Lack of external NIST CAVP server validation. |
| **Scientific Claim Scope** | Rejection fidelity does not certify side-channel or radiation resilience. | Qualified claims strictly to software logical correctness under non-adversarial reliability models. | Silicon physical latch-up / single-event transients. |

---

### 6.2 Final Recommendation

# **CONDITIONAL GO (Design and Methodological Audit Complete; NO-GO for Execution)**

### Explicit Reasons:
1. **Audit Criteria Satisfied:** All statistical, taxonomical, and control-flow defects identified in Phase 17 and Phase 17B have been rigorously audited and resolved with exact mathematical formulas and C code references.
2. **Execution Boundary Enforced:** In strict compliance with instructions, **no implementation code was written, no binaries compiled, no memory mutated, and no trials executed**.
3. **Requirement for Next Phase:** Any future Phase 18 implementation gate must operate under the exact quotas, four-class cryptographic endpoints, and 4-step vector validation pipeline established in this document, and requires separate human operator review and explicit authorization.
