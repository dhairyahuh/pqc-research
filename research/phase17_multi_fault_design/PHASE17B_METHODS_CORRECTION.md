# Phase 17B — Methodological Correction of the Multi-Fault Experiment Design

**Author:** Skeptical Cryptographic Systems Auditor & Experimental Methodologist  
**Date:** 2026-10-11  
**Project:** Cross-Layer Fault Interactions in ML-KEM-768 Key Establishment  
**Status:** METHODOLOGICAL CORRECTION SPECIFICATION (DESIGN ONLY — Strictly Read-Only)  
**Target File Corrected:** [`research/phase17_multi_fault_design/PHASE17_EXPERIMENT_DESIGN.md`](file:///Users/dhairyajain/Desktop/pqc%20research/research/phase17_multi_fault_design/PHASE17_EXPERIMENT_DESIGN.md) (preserved unchanged)  
**Deliverable Directory:** `research/phase17_multi_fault_design/`  

---

## 1. Methodological Correction Matrix

The table below reconciles every defect, ambiguity, and overstatement identified in the Phase 17 design:

| Defect ID | Section in Phase 17 | Identified Methodological Defect | Empirical & Source Evidence | Required Methodological Resolution | Remaining Uncertainty |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **DEF-01** | §2.2 ($H_3$) vs. §4.1 | **Statistical Inconsistency in SDC Upper Bound:** Claimed SDC upper bound $< 1.0\%$ at 95% confidence, but calculated $0/200 \implies 1.88\%$. | Wilson score formula with $k=0, n=200, z=1.96$: $p_U = \frac{z^2}{n + z^2} = \frac{3.8416}{203.8416} = 1.8847\%$. | Reconcile target bound: for $n=200$, bound is **$1.88\%$ (two-sided)** or **$1.33\%$ (one-sided)**. To achieve $< 1.0\%$, sample size must expand to $n \ge 381$ (two-sided) or $n \ge 268$ (one-sided). | Trade-off between Darwin `vm_protect` API cycling count and target bound precision. |
| **DEF-02** | §4.1, §5.1 | **Ambiguous SDC Denominator:** Mixed session counts, decapsulation invocations, and retransmission attempts. | Protocol sessions execute up to $\text{RETRY\_MAX}=2$ (3 attempts). Attempts within a seed share identical secret keys and persistent mutations (clustered, not independent). | Formally define the primary SDC estimand unit as **Attempt 1 fault-activated decapsulation invocations** ($N_{\text{admitted}}$ independent seeds). Secondary pooled attempts evaluated via clustered bootstrap. | Extent of correlation across attempts within a session. |
| **DEF-03** | §3.2 | **Unreconciled Fault Taxonomy:** Claimed "7 channel classes" but introduced unparameterized events ("burst corruption", "padding bit-flips", "byte shifts"). | Phase 3/4 code (`combined_campaign.c:70-108`) strictly implements 7 classes: `CH_BIT`, `CH_TRUNC`, `CH_LOSS`, `CH_DELAY`, `CH_DUP`, `CH_REORDER`, `CH_INTERRUPT`. | Reconcile taxonomy: classify byte shifts/padding changes strictly as parameter variations of `CH_BIT` (payload bit flips) or `CH_TRUNC` (length alterations). Explicitly specify sampling probabilities for all 7 classes. | Mapping of abstract transport events to physical RF channel fading models. |
| **DEF-04** | §2.2 ($H_2$) | **Prejudged Cryptographic Outcome:** Stated as a fact that "persistent twiddle fault deterministically fails re-encryption and emits $K_{\text{rej}}$". | Re-encryption verification is an empirical test. While true for tested single vector in Phase 15Q, dual perturbation ($\tilde{c} \times \tilde{\zeta}$) could theoretically induce unexpected behavior. | Reframe as a **falsifiable hypothesis** ($H_{\text{rej}}$) tested against four disaggregated endpoints: $K_{\text{rej}}(\tilde{c})$, $K_{\text{golden}}$, SDC, and Execution Error. | Behavior under zero-norm or near-zero error polynomial differences. |
| **DEF-05** | §4.3 | **Conflation of Oracle Verdict & Agreement:** Did not separate local receiver decapsulation verdict from sender-receiver key agreement. | In FIPS 203 implicit rejection, receiver generates valid $K_{\text{rej}}$, but sender holds $K_{\text{golden}}$, creating a key mismatch. | Track receiver cryptographic endpoint (`VERDICT_REJECT`) separately from protocol agreement (`KEY_MISMATCH`). | Impact on higher-layer AEAD session keys. |
| **DEF-06** | §3.4 | **Vector Inventory Overstatement:** Claimed "100 distinct NIST FIPS 203 KAT vectors" locally available. | Inspection of `references/test_vectors/mlkem_expected_kat.h` confirms strictly **1 official NIST KAT vector** is stored locally for ML-KEM-768. | Distinguish the **1 official NIST reference KAT** (Vector 0) from **$N-1$ locally derived pseudorandom test cases** generated via standardized `mlkem768_keypair_derand` / `enc_derand`. | Future NIST CAVP multi-vector file availability. |
| **DEF-07** | §7.2 | **Unsupported Security Claims:** Mentioned constant-time implicit rejection and radiation resilience without qualification. | Localized recovery branches on fault detection; Mach-O software injection does not model physical ionization dynamics. | Strictly qualify all claims to non-adversarial software execution; remove constant-time guarantees under fault-handling conditions. | Hardware-specific microarchitectural timing leakages. |

---

## 2. Revised Hypotheses and Disaggregated Endpoint Definitions

### 2.1 Falsifiable Hypotheses
- **$H_{\text{mask}}$ (Pre-Execution Delivery Masking):** Delivery-blocking channel faults (loss, truncation, timeout) prevent the frame from reaching the cryptographic engine, resulting in zero table fault activations in Condition $C_{11}$.
- **$H_{\text{rej}}$ (Dual-Fault Rejection Convergence):** When a delivery-admitted corrupted ciphertext $\tilde{c}$ is decapsulated using a persistently corrupted twiddle table $\tilde{\zeta}$, the probability of entering FIPS 203 implicit rejection ($ss == K_{\text{rej}}(\tilde{c})$) is $1.0$, with zero occurrences of valid key emission ($K_{\text{golden}}$).
- **$H_{\text{SDC}}$ (Dual-Fault SDC Resistance):** Dual arithmetic perturbation ($\tilde{c} \times \tilde{\zeta}$) will not induce an accidental mathematical cancellation satisfying $c' == \tilde{c}$. The empirical rate of SDC ($ss \notin \{K_{\text{golden}}, K_{\text{rej}}(\tilde{c})\}$) will be $0.00\%$.
- **$H_{\text{retry}}$ (Retransmission Deadlock):** In Condition $C_{11}$, when a transient channel fault clears on Attempt 2, the persistence of the twiddle mutation prevents recovery, resulting in protocol abort after retry budget exhaustion.

### 2.2 Four-Class Cryptographic Endpoint Definitions
For every decapsulation invocation, the output shared secret $ss$ is classified into one of four mutually exclusive endpoints evaluated against independent cleanroom oracles:

1. **`EXPECTED_GOLDEN` ($K_{\text{golden}}$):** $ss == K_{\text{golden}}$. The output matches the authentic shared secret negotiated by the sender.
   - *Expected on:* $C_{00}$ (clean), sham controls (`mask = 0x0000`), and dormant twiddle Index 0.
2. **`IMPLICIT_REJECTION` ($K_{\text{rej}}(\tilde{c})$):** $ss == \text{SHAKE256}(z \parallel \tilde{c}, 32)$.
   - The output matches the exact FIPS 203 Section 7.3 implicit rejection key computed over the **received wire ciphertext** $\tilde{c}$ using secret seed $z$.
   - *Expected on:* Active twiddle mutations and payload-corrupted ciphertexts.
3. **`SILENT_DATA_CORRUPTION` (SDC):** $ss \neq K_{\text{golden}}$ AND $ss \neq K_{\text{rej}}(\tilde{c})$.
   - The output is an unauthenticated, unpredictable 32-byte secret that satisfies neither the golden agreement nor standard implicit rejection.
4. **`EXECUTION_FAILURE`:** `dec_rc != 0`, memory fault, or abnormal termination (`SIGBUS`/`SIGSEGV`).

### 2.3 Distinct Protocol & Key-Agreement Outcomes
Cryptographic output classification is strictly separated from protocol agreement:
- **`KEY_AGREED`:** Receiver $ss ==$ Sender $ss$ (occurs only when $ss == K_{\text{golden}}$).
- **`KEY_MISMATCH`:** Receiver $ss \neq$ Sender $ss$ (occurs when $ss == K_{\text{rej}}(\tilde{c})$ or $ss == \text{SDC}$).
- **`KEY_UNAVAILABLE`:** Decapsulation was not executed due to link-layer delivery drop.

---

## 3. Reconciled Fault Taxonomy and Scenario Generation

### 3.1 Exhaustive Classification of the 7 Channel Fault Classes
Every channel event is mapped directly to the audited Phase 3/4 implementation (`combined_campaign.c:98-109`):

| Channel Class ID | Name in SUT | Wire Mechanism | Delivery Behavior | Decapsulation Invoked? | Retry Trigger |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **CH-1** | `BIT_CORRUPTION` | Invert 1 to 16 bits within ciphertext payload ($pos < 1088$) | **Delivery-Admitted** | **YES** | MAC tag failure or frame parse failure |
| **CH-2** | `DUPLICATION` | Duplicate wire frame injected into link | **Delivery-Admitted** | **YES** | Dropped by sequence window / dedup filter |
| **CH-3** | `REORDER` | Sequence number modified out of window ($seq - 100$) | **Delivery-Admitted** | **YES** | Decapsulates; frame sequence check fails |
| **CH-4** | `TRUNCATION` | Wire length truncated by $1 \le \Delta L \le 64$ bytes | **Delivery-Blocking** | **NO** | Frame length header validation failure |
| **CH-5** | `PACKET_LOSS` | Entire wire packet dropped (zero bytes delivered) | **Delivery-Blocking** | **NO** | Non-delivery / link timeout |
| **CH-6** | `DELAY` | Latency injected exceeding delivery deadline $D$ | **Delivery-Blocking** | **NO** | Deadline expired before frame intake |
| **CH-7** | `INTERRUPTION`| Simulated link drop / carrier disconnect | **Delivery-Blocking** | **NO** | Transport layer link error |

*Rules for Secondary Perturbations:*
- "Burst corruption" is formally defined as multi-bit clustering within `CH-1` (`BIT_CORRUPTION`).
- "Padding alterations" are formally defined as bitflips targeting unused coefficient bits within `CH-1`.
- "Byte shifts" that alter frame alignment are formally classified under `CH-4` (`TRUNCATION` / Framing error).

### 3.2 Channel Sampling Distribution ($F_{\text{chan}}$)
To ensure equal empirical power across delivery behaviors, $F_{\text{chan}}$ samples uniformly across classes:
- **Stratum A (Delivery-Admitted, 50% total mass):**
  - `CH-1 (BIT_CORRUPTION)`: $40\%$ probability mass (primary cryptographic interaction test).
  - `CH-2 (DUPLICATION)`: $5\%$ probability mass.
  - `CH-3 (REORDER)`: $5\%$ probability mass.
- **Stratum B (Delivery-Blocking, 50% total mass):**
  - `CH-4 (TRUNCATION)`: $15\%$ probability mass.
  - `CH-5 (PACKET_LOSS)`: $15\%$ probability mass.
  - `CH-6 (DELAY)`: $10\%$ probability mass.
  - `CH-7 (INTERRUPTION)`: $10\%$ probability mass.

### 3.3 Strict Matched Scenario Invariants
For each master seed $i$, a single scenario descriptor is drawn and shared across all four conditions:
1. `vector_seed`: Seeds the keypair and ciphertext generation.
2. `twiddle_idx`: Target index $k \in [0, 127]$ (applied in $C_{10}, C_{11}$; unused in $C_{00}, C_{01}$).
3. `twiddle_mask`: Mutation bitmask (applied in $C_{10}, C_{11}$; `0x0000` in $C_{00}, C_{01}$).
4. `channel_class`: Selected from CH-1 through CH-7 (applied in $C_{01}, C_{11}$; `CH_CLEAN` in $C_{00}, C_{10}$).
5. `channel_persistence`: `TRANSIENT` ($50\%$, clears on Attempt > 1) or `PERSISTENT` ($50\%$, recurs on retry).
6. **Persistence Rule:** In $C_{11}$, the twiddle table fault is mutated **before Attempt 1** and held mutated across all retransmissions until session termination.

---

## 4. Corrected Sample-Size Calculations and Estimands

### 4.1 Defensible SDC Statistical Power Calculation
To resolve **DEF-01**, the relationship between sample size $n$, target bound $p_U$, and confidence level is rigorously defined.

When zero SDC events are observed ($k = 0$), the upper bound is computed via:
1. **Wilson Score Upper Bound (Without Continuity Correction):**
   $$p_U = \frac{z^2}{n + z^2}$$
2. **Clopper-Pearson Exact Binomial Upper Bound (Rule of Three):**
   $$p_U = 1 - (1 - \alpha)^{1/n} \approx \frac{-\ln(\alpha)}{n} = \frac{2.9957}{n} \quad (\text{for } \alpha = 0.05)$$

The table below presents the exact sample size required for target upper bounds:

| Target 95% Upper Bound | Statistical Method | Required Admitted Trials ($n_{\text{admitted}}$) | Total Seeds at 50% Stratum A ($N$) | Total Condition Trials ($4N$) |
| :---: | :--- | :---: | :---: | :---: |
| **$< 1.00\%$** | Two-Sided Wilson ($z = 1.95996$) | **381** | **762 seeds** | 3,048 trials |
| **$< 1.00\%$** | One-Sided Wilson ($z = 1.64485$) | **268** | **536 seeds** | 2,144 trials |
| **$< 1.00\%$** | Clopper-Pearson / Rule of Three | **300** | **600 seeds** | 2,400 trials |
| **$< 1.88\%$** | Two-Sided Wilson ($z = 1.95996$) | **200** | **400 seeds** | 1,600 trials |
| **$< 1.33\%$** | One-Sided Wilson ($z = 1.64485$) | **200** | **400 seeds** | 1,600 trials |

### 4.2 Preregistered SDC Resolution Strategy
To maintain experimental feasibility on Darwin ARM64 while guaranteeing a strict $< 1.0\%$ upper bound, the design adopts:
- **Allocation Adjustment:** Allocate **$75\%$ probability mass to Stratum A** (delivery-admitted) and **$25\%$ to Stratum B** (delivery-blocking).
- **Seed Size:** $N = \mathbf{400 \text{ seeds}}$ ($1{,}600$ condition executions).
- **Resulting Admitted Sample:** $n_{\text{admitted}} = 400 \times 0.75 = \mathbf{300 \text{ trials}}$.
- **Resulting 95% Upper Bound:**
  - One-Sided Wilson (95% CI): $p_U = \frac{1.64485^2}{300 + 1.64485^2} = \frac{2.7055}{302.7055} = \mathbf{0.89\%} \ (< 1.0\%)$.
  - Exact Clopper-Pearson (95% CI): $p_U = 1 - (0.05)^{1/300} = \mathbf{0.993\%} \ (< 1.0\%)$.
  - Two-Sided Wilson (95% CI): $p_U = \frac{3.8416}{303.8416} = \mathbf{1.26\%}$.

### 4.3 Estimand Definitions
1. **Primary Cryptographic Estimand (Attempt 1 SDC Rate):**
   $$\hat{p}_{\text{SDC}} = \frac{\#\{C_{11}: \text{Attempt 1 executed} \land ss \notin \{K_{\text{golden}}, K_{\text{rej}}(\tilde{c})\}\}}{n_{\text{admitted}}}$$
   Evaluated with exact one-sided and two-sided Wilson intervals over distinct seeds.
2. **Primary Protocol Estimand (Session Completion Contrast):**
   $$\hat{\Delta}_{\text{proto}} = p_{11} - p_{10} - p_{01} + p_{00}$$
   Evaluated via paired nonparametric bootstrap over seeds ($B = 10{,}000$).
   *Explicit Concession:* Because persistent twiddle corruption unconditionally prevents key establishment in active trials ($p_{10} \equiv 0$, $p_{11} \equiv 0$), $\hat{\Delta}_{\text{proto}} = 1.0 - p_{01}$. This contrast reflects protocol retry exhaustion and must not be claimed as an emergent cryptographic discovery.

---

## 5. Vector Inventory Evidence and Feasibility Boundaries

### 5.1 Local Vector Inventory Audit
A file inspection of the workspace revealed:
- `references/test_vectors/mlkem_expected_kat.h`: Contains **exactly 1 static NIST KAT vector** for ML-KEM-768 (`test_vector_d`, `test_vector_z`, `test_vector_m`, `test_vector_pk`, `test_vector_sk`, `test_vector_ct`, `test_vector_ss`).
- `phase12_reproducibility_audit/oracle_test_vectors.csv`: Contains 9 SHAKE256 boundary vectors, not KEM keypairs.
- **Feasibility Resolution:**
  - Vector 0 is the official static NIST KAT vector from `mlkem_expected_kat.h`.
  - Vectors 1 through 399 are **locally generated deterministic test vectors** derived via FIPS 203 Section 6.1 derandomized interfaces (`mlkem768_keypair_derand` and `mlkem768_enc_derand`) seeded via SHAKE-256 PRF.
  - The manuscript must strictly state: *"1 official NIST KAT reference vector + 399 locally derived standards-conformant deterministic test vectors."*

### 5.2 Execution Feasibility & Kernel API Overhead
- In Phase 17, $N = 400$ seeds across 4 conditions yields $1{,}600$ total executions.
- Conditions $C_{10}$ and $C_{11}$ require memory mutation ($800$ mutating executions).
- Each mutating execution performs 2 unprotect/reprotect cycles ($4$ `vm_protect` calls).
- Total kernel protection transitions: $800 \times 4 = \mathbf{3{,}200 \text{ calls}}$.
- In Phase 15Q, 32 calls completed in $< 1.0$ second. $3{,}200$ calls is estimated to take $\approx 10\text{--}15$ seconds on Darwin ARM64, confirming operational feasibility.

---

## 6. Refined Scientific Claims and Epistemological Boundaries

1. **No Claims of Physical Resilience:** Software memory injection in Mach-O virtual memory simulates logical state perturbation; it does not model single-event transients (SETs), latch-up, total ionizing dose (TID), or beam cross-sections.
2. **No Claims of Constant-Time Security:** While fault-free decapsulation is constant-time, error-handling and protocol retransmission branches introduce measurable timing differences.
3. **No Unsubstantiated Novelty Claims:** The cross-layer pairing is novel strictly within the reviewed repository literature. Priority is not claimed against unqueried global databases (IEEE Xplore, ACM DL).
4. **Value of the Delivery-Admitted Stratum:** By isolating Stratum A ($75\%$), this campaign evaluates whether simultaneous corruption of the ciphertext and twiddle factors ($\tilde{c} \times \tilde{\zeta}$) can compromise the Fujisaki-Okamoto re-encryption verification barrier—a meaningful, non-trivial cryptographic hypothesis.

---

## 7. Recommendation for Implementation Review

# **CONDITIONAL GO (Methodological Corrections Accepted)**

### Justification:
The methodological corrections resolve all seven identified defects:
1. SDC statistical powering is reconciled ($75\%$ Stratum A yields $n=300$ admitted trials, achieving $< 1.0\%$ one-sided bound).
2. The 7 channel classes are rigorously mapped and stratified.
3. Cryptographic hypotheses are made strictly falsifiable.
4. Test vector origins are accurately demarcated.
5. In accordance with safety rules, **no code is modified, no binaries built, and no experiments executed in this phase**. Execution is deferred to a future authorized implementation gate.
