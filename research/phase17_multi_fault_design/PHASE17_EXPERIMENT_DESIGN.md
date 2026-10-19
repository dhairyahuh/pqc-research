# Phase 17 — Preregistered Experiment Design: Persistent Arithmetic-Table × Communication-Channel Fault Interaction Campaign

**Author:** Skeptical Cryptographic Systems & Experimental Design Reviewer  
**Date:** 2026-10-11  
**Project:** Cross-Layer Fault Interactions in ML-KEM-768 Key Establishment  
**Status:** PREREGISTERED DESIGN SPECIFICATION (DESIGN ONLY — No Code Modification, No Memory Mutation, No Build Execution)  
**Target Platform:** Darwin ARM64 (Apple Silicon macOS), isolated `(__DATA_CONST,__zetas_page)` mapping  
**Directory:** `research/phase17_multi_fault_design/`  

---

## 1. Evidence Inventory and Verified Starting State

### 1.1 Settled Findings from Previous Phases
Before designing this campaign, all relevant historical artifacts, source implementations, and raw datasets were verified:

1. **Phase 3 Isolated Channel Campaign (`research/results/phase3_channel_v1/raw.jsonl`):**
   - Verified $N = 600$ sessions across 7 fault classes (bit corruption, truncation, loss, delay, duplication, reordering, interruption) + clean baseline.
   - Evaluated protocol outcomes (`KEY_ESTABLISHED`, `RECOVERED_ON_RETRY`, `MALFORMED_MESSAGE`, `MESSAGE_LOST`, `TIMEOUT_RETRY_EXHAUSTED`, `PROTOCOL_ABORT`).
   - Established that channel retries redraw independent channel states, making recovery non-tautological.
2. **Phase 4 Matched Factorial Campaign (`research/results/phase4_combined_v1/raw.jsonl`):**
   - Verified $N = 500$ seeds $\times 4$ matched conditions ($2{,}000$ records).
   - Paired transient logical-value memory faults with channel disturbances.
   - Estimated interaction contrast $\hat{\Delta} = +0.216$ (95% CI: $[+0.180, +0.252]$).
   - **Crucial Limitation Discovered:** The interaction was largely structural: in $40.6\%$ ($203/500$) of trials, channel delivery-blocking faults prevented decapsulation from executing, trivially masking memory fault activation.
3. **Phase 15Q Pilot & Phase 15R Audit (`results/phase15q/`, `PHASE15R_INDEPENDENT_AUDIT.md`):**
   - Verified Darwin ARM64 virtual memory toggling (`vm_protect` RW $\to$ RO) on the isolated 16 KB page `(__DATA_CONST,__zetas_page)` at virtual address `0x100024000`.
   - Verified $16/16$ trials completed with zero kernel traps (`SIGBUS`), zero memory leaks, and $100\%$ byte-identical table restoration and canary integrity across all 16,128 padding bytes.
   - Proved that corrupting active twiddles triggers FIPS 203 Section 7.3 implicit rejection $K_{\text{rej}} = J(z \parallel c, 32)$ under NIST KAT vector #1.
   - Confirmed twiddle index 0 is inactive in the tested implementation.

### 1.2 What Has Been Tested vs. What is Genuinely New

| Experimental Dimension | Phase 4 Combined Campaign | Phase 15Q Pilot | **Proposed Phase 17 Campaign (New)** |
| :--- | :--- | :--- | :--- |
| **Arithmetic Fault Nature** | Transient, logical-value (local C variable XORed) | Persistent in memory (`__DATA_CONST`) | **Persistent in memory (`__DATA_CONST`)** |
| **Fault Duration Across Retries** | Redrawn / transient | Single decapsulation (no retries) | **Persistent across retransmission attempts** |
| **Channel Fault Interaction** | Tested against local logical faults | Not tested (clean inputs only) | **Tested across 7 channel classes** |
| **Input Test Vectors** | Single scenario per seed | Single fixed NIST KAT #1 | **Multi-vector diversified test suite** |
| **Delivery-Blocking vs Cryptographic** | Lumped into single binary $\Delta$ | N/A | **Stratified: Delivery-Blocking vs Payload-Corrupting** |

---

## 2. Research Questions and Preregistered Hypotheses

### 2.1 Primary Research Questions
1. **RQ1 (Activation & Precedence):** When a persistent twiddle-table fault in `__DATA_CONST` coexists with an external communication-channel fault, does the channel fault block frame delivery and mask table fault activation, or does decapsulation execute under corrupted arithmetic?
2. **RQ2 (Cryptographic Endpoint Interaction):** When a channel fault delivers a **corrupted ciphertext** $\tilde{c}$ to a receiver operating with a **corrupted persistent twiddle table** $\tilde{\zeta}$, does decapsulation:
   - Reliably enter FIPS 203 implicit rejection $K_{\text{rej}} = J(z \parallel \tilde{c}, 32)$?
   - Suffer Silent Data Corruption (SDC), wherein dual perturbation induces an accidental mathematical cancellation that satisfies re-encryption ($c' == \tilde{c}$)?
   - Result in unhandled process termination or memory trap?
3. **RQ3 (Retransmission Dynamics):** When an initial transmission fails and protocol retransmission triggers, how does the session evolve when the channel fault is transient (clears on retry) but the twiddle table fault is persistent (remains corrupted)?
4. **RQ4 (Interaction Contrast & Separability):** When separating delivery-blocking channel faults from payload-corrupting channel faults, does a non-trivial cryptographic interaction contrast emerge beyond trivial pre-execution masking?

### 2.2 Preregistered Hypotheses
- **$H_1$ (Structural Masking):** Delivery-blocking channel faults (packet loss, truncation, uncorrected timeout) prevent decapsulation invocation, masking persistent table fault activation with $100\%$ consistency.
- **$H_2$ (Retransmission Deadlock under Persistent Corruption):** For transient channel faults, subsequent retransmission delivers a bit-pristine ciphertext $c$, but because the receiver's twiddle table remains persistently mutated, decapsulation deterministically fails re-encryption verification and emits $K_{\text{rej}}$, forcing protocol abort after retry exhaustion ($0.0\%$ session recovery).
- **$H_3$ (Dual-Fault SDC Immunity):** Across all trials where decapsulation processes a channel-corrupted ciphertext under a table-corrupted twiddle factor, the observed shared secret will strictly match the dynamic FIPS 203 rejection oracle $K_{\text{rej}} = \text{SHAKE256}(z \parallel \tilde{c})$, with an empirical SDC rate of $0.00\%$ (upper bound $< 1.0\%$ at 95% confidence).
- **$H_4$ (Non-Degenerate Cryptographic Sub-Stratum):** In the delivery-admitted sub-stratum (channel bit-flips and malformed payload bytes), the interaction contrast on the cryptographic verdict is identically zero, confirming that neither single nor dual faults compromise the constant-time implicit rejection barrier.

---

## 3. Experimental Design and Protocol Specification

### 3.1 Four-Condition Matched Factorial Design
Each Monte-Carlo scenario is evaluated under four paired conditions sharing the identical underlying cryptographic keys, message, and random seed:

```
                          [ Master Seed i ]
                                  |
            +---------------------+---------------------+
            |                                           |
   [ Channel Fault Clean ]                     [ Channel Fault Armed ]
            |                                           |
      +-----+-----+                               +-----+-----+
      |           |                               |           |
   [C00]       [C10]                           [C01]       [C11]
Table Clean  Table Fault                     Table Clean  Table Fault
 (Baseline)   (Table Only)                    (Chan Only)   (Combined)
```

- **Condition $C_{00}$ (Clean Control):** Golden twiddle table, pristine wire channel. (Expected outcome: $100\%$ `KEY_ESTABLISHED`, `VALID_KEY`).
- **Condition $C_{10}$ (Persistent Table Only):** Wire channel pristine; twiddle entry $k$ persistently mutated in `__DATA_CONST` throughout the session.
- **Condition $C_{01}$ (Channel Fault Only):** Golden twiddle table; wire message subjected to channel disturbance. Retries redraw independent channel states.
- **Condition $C_{11}$ (Combined Multi-Fault):** Both faults active. Twiddle table mutated prior to Attempt 1 and held mutated across all retransmission attempts.

### 3.2 Stratified Channel Fault Distribution ($F_{\text{chan}}$)
To prevent delivery-blocking faults from drowning out cryptographic observations, $F_{\text{chan}}$ is explicitly stratified into two balanced tiers ($50\%$ each):

1. **Stratum A: Delivery-Admitted / Cryptographic Perturbations ($50\%$):**
   - Payload bit corruption (single-bit, multi-bit, burst).
   - Ciphertext byte shifts and padding bit-flips.
   - *Characteristic:* Wire bytes arrive at the receiver and invoke decapsulation.
2. **Stratum B: Delivery-Blocking / Protocol Perturbations ($50\%$):**
   - Frame truncation (corrupted framing header / magic word).
   - Complete packet loss (simulated link drop).
   - Excessive propagation delay exceeding deadline $D$ (timeout).
   - *Characteristic:* Receiver drops or rejects the frame prior to decapsulation.

### 3.3 Persistent Table Mutation Distribution ($F_{\text{table}}$)
Twiddle table faults are drawn uniformly from a verified operational catalog:
- **Target Index $k$:** Drawn uniformly from active operational layers:
  - Layer 1 Forward NTT ($k \in [1, 2]$).
  - Mid Layers 2–6 ($k \in [3, 63]$).
  - Layer 7 Forward NTT ($k \in [63, 63]$).
  - Mulcache entries ($k \in [64, 95]$).
  - Basemul / InvNTT entries ($k \in [96, 127]$).
  - Index 0 negative control ($k = 0$, mathematically unused).
- **Bitmask:** Single-bit flips (LSB $0x0001$, mid-byte $0x0080$, sign-bit $0x8000$), multi-bit masks ($0x0400$, $0xFFFF$), and sham controls ($0x0000$).
- **Lifecycle:** Mutated via `vm_protect(RW) \to write \to vm_protect(RO)` prior to session start; held unchanged across retries; restored at session teardown.

### 3.4 Multi-Vector Cryptographic Diversity
Unlike Phase 15Q (which used only NIST KAT vector #1), Phase 17 mandates a diversified test pool:
- $100$ distinct NIST FIPS 203 KAT vectors (KEM-768).
- Keypairs and ciphertexts are indexed deterministically via SHAKE-256 PRF seeds:
  $$\text{Seed}_i \implies (pk_i, sk_i, c_i, K_{\text{golden}, i}, z_i)$$

---

## 4. Sample Size Rationale and Statistical Analysis Plan

### 4.1 Sample Size Justification
- **The Pitfall of Blind Re-use:** Phase 4 used $N = 500$ seeds because logical memory faults allowed non-zero recovery ($p_{10} = 48.0\%$). In persistent table faults, an active twiddle fault unconditionally prevents golden key decapsulation ($p_{10} \equiv 0.0\%$).
- **Powering for the Critical Estimand (SDC Upper Bound):**
  The central scientific question in $C_{11}$ is whether dual corruption induces SDC ($K^* \notin \{K_{\text{golden}}, K_{\text{rej}}\}$).
  - Let $N_{\text{admitted}}$ be the number of $C_{11}$ trials reaching decapsulation. With $50\%$ Stratum A allocation, $N = 400$ total seeds yields $N_{\text{admitted}} \approx 200$ active dual-fault decapsulations.
  - If zero SDC events occur ($0/200$), the 95% Wilson score upper bound on SDC probability is:
    $$p_{\text{upper}} = \frac{0 + \frac{1.96^2}{2}}{200 + 1.96^2} + \frac{1.96 \sqrt{\frac{1.96^2}{4}}}{200 + 1.96^2} \approx \mathbf{1.88\%}$$
  - For $N = 600$ total seeds ($N_{\text{admitted}} \approx 300$), the upper bound drops to $\mathbf{1.26\%}$.
- **Preregistered Sample Size:** $N = \mathbf{400 \text{ seeds}}$ ($1{,}600$ matched trial executions). This strikes the optimal balance between statistical rigor and Darwin ARM64 kernel memory protection cycling overhead ($1{,}600 \times 2 = 3{,}200$ `vm_protect` calls).

### 4.2 Statistical Analysis and Estimands
1. **Primary Protocol Estimand (Session Completion Contrast):**
   $$\hat{\Delta}_{\text{proto}} = p_{11} - p_{10} - p_{01} + p_{00}$$
   Evaluated via paired nonparametric bootstrap over seeds ($B = 10{,}000$, percentile method).
2. **Primary Cryptographic Estimand (SDC Rate):**
   $$\hat{p}_{\text{SDC}} = \frac{\#\{C_{11}: \text{decaps executed} \land ss \notin \{K_{\text{golden}}, K_{\text{rej}}\}\}}{N_{\text{admitted}}}$$
   Reported with exact 95% Wilson score interval with continuity correction.
3. **Secondary Estimand (Retransmission Transition Rate):**
   Proportion of Stratum A trials transitioning from Attempt 1 failure to Attempt 2 implicit rejection vs. protocol abort.

---

## 5. Trial-Level Schema and Masking Taxonomy

### 5.1 12-Column Authoritative Trial Ledger Schema

```sql
CREATE TABLE phase17_trial_ledger (
    seed_id               INTEGER,     -- Unique Monte-Carlo scenario seed
    condition             TEXT,        -- C00, C10, C01, C11
    channel_stratum       TEXT,        -- STRATUM_A_ADMITTED or STRATUM_B_BLOCKING
    channel_class         TEXT,        -- BIT_CORRUPTION, TRUNCATION, LOSS, etc.
    table_target_idx      INTEGER,     -- Twiddle factor index (0..127) or -1 for clean
    table_bitmask         TEXT,        -- Hex mask (e.g. 0x0001)
    attempt_count         INTEGER,     -- Retransmissions executed (1..3)
    decaps_invoked        BOOLEAN,     -- True iff receiver invoked decapsulation
    activation_status     TEXT,        -- ACTIVATED, MASKED_BY_CHANNEL, UNARMED
    crypto_verdict        TEXT,        -- VALID_KEY, REJECTION_KEY, SDC_CORRUPTED, UNAVAILABLE
    protocol_outcome      TEXT,        -- KEY_ESTABLISHED, RECOVERED_RETRY, PROTOCOL_ABORT, etc.
    restoration_hygiene   TEXT         -- PASSED_100PCT, FAILED_ABORT
);
```

### 5.2 Mandatory Separation of Masking vs. Recovery
- **`MASKED_BY_CHANNEL`:** Assigned if and only if `decaps_invoked == FALSE` in Condition $C_{11}$.
  * *Normative Rule:* A masked trial must **never** be labeled as cryptographic recovery or fault tolerance. The session failed at the link layer before arithmetic was tested.
- **`RECOVERED_ON_RETRY`:** Reachable if and only if `crypto_verdict == VALID_KEY` and `attempt_count > 1`.
  * *Normative Rule:* Under Condition $C_{11}$ with active twiddle corruption, this outcome is mathematically impossible unless the twiddle is dormant (Index 0) or sham (`mask = 0`). Any occurrence on active twiddles must be flagged as a critical harness anomaly.

---

## 6. Safety, Memory Protection, and Rollback Requirements

### 6.1 Transactional 14-Step Session Lifecycle
To prevent memory leaks, page permission corruption, or cross-trial contamination on Darwin ARM64, every scenario execution must follow the hardened Phase 14/15 transactional pipeline:

```
[1. Pre-Session Baseline Decapsulation Check (KAT Reference)]
                          |
[2. Resolve mlk_zetas_page Virtual Address & Verify 16KB Alignment]
                          |
[3. Darwin VM Query: Assert Region is __DATA_CONST, Protection is r--]
                          |
[4. If Condition Mutates Table: vm_protect(RW) -> Write -> Read-back Assert]
                          |
[5. vm_protect(RO) -> vm_region_64 Query Confirms Page is r--]
                          |
[6. Execute Protocol Session: Framing -> Channel -> Receiver Pipeline]
                          |
  +-----------------------+-----------------------+
  | (If Retransmission Needed: Channel Redrawn)   |
  | (Twiddle Table Remains in Persistently Mutated RO State) |
  +-----------------------+-----------------------+
                          |
[7. Capture Wire Frames, Shared Secrets, and State Machine Outcomes]
                          |
[8. If Condition Mutated Table: vm_protect(RW) -> Write Golden Twiddle]
                          |
[9. vm_protect(RO) -> vm_region_64 Query Confirms Page is r--]
                          |
[10. SHA-256 Digest Over Full 256-Byte Table Matches Golden Digest]
                          |
[11. Canary Verification: All 16,128 Page Padding Bytes Confirmed Zero]
                          |
[12. Post-Session Baseline Decapsulation Check Matches K_golden Bit-for-Bit]
                          |
[13. Dynamic Rejection Oracle Validation: Compare SS against J(z || c_wire)]
                          |
[14. Commit 12-Column Record to Ledger CSV; Fail Closed on Any Step Failure]
```

### 6.2 Dynamic Rejection Oracle Specification
When a channel fault mutates ciphertext $c \to \tilde{c}$, the FIPS 203 Section 7.3 implicit rejection key changes dynamically:
$$K_{\text{rej}}(\tilde{c}) = \text{SHAKE256}(z \parallel \tilde{c}, 32)$$
- The test harness must compute $K_{\text{rej}}$ using the **delivered wire ciphertext** $\tilde{c}$, not the clean sender ciphertext $c$.
- An independent, cleanroom Keccak-f[1600] implementation must be embedded in the runner to derive $K_{\text{rej}}(\tilde{c})$ without relying on `liboqs` or SUT routines.

---

## 7. Acceptance Criteria and Claim Boundaries

### 7.1 Objective Campaign Acceptance Criteria
1. **Zero Contamination Gate:** $100\%$ of post-session baseline checks across all $1{,}600$ trials must reproduce $K_{\text{golden}}$ bit-for-bit.
2. **Zero Signal Gate:** Zero process terminations via `SIGBUS` or `SIGSEGV` during memory protection transitions.
3. **Zero Orphaned Permissions Gate:** In $100\%$ of trials, `vm_region_64` must verify that the table page returns to `r--` (`VM_PROT_READ`).
4. **Oracle Convergence Gate:** In $100\%$ of trials reaching decapsulation with active faults, output shared secrets must match either $K_{\text{golden}}$ (sham/dormant) or $K_{\text{rej}}(\tilde{c})$ (rejection). Zero SDC events.

### 7.2 Strict Scientific Claim Boundaries

| Permitted Claims (If Accepted) | Strictly Prohibited / Unsupported Claims |
| :--- | :--- |
| Empirical characterization of persistent Mach-O table faults under channel disturbances | Physical space-radiation or single-event upset (SEU) resilience |
| Precise quantification of pre-execution channel masking rates | Operational satellite flight readiness or CCSDS compliance |
| Demonstration of dynamic FIPS 203 implicit rejection fidelity under dual faults | Immunity to physical fault attacks (e.g. laser/glitch key recovery) |
| Statistical upper bound on software SDC under tested distributions | Performance under multi-carrier RF jamming or fading channels |

---

## 8. Feasibility Analysis and Formal GO/NO-GO Recommendation

### 8.1 Critical Evaluation of Scientific Informacy
* **The Skeptical Reviewer's Challenge:**  
  *"If this experiment merely re-measures $\hat{\Delta} = +0.216$ by showing that dropped packets prevent decapsulation, it is scientifically trivial and repeats Phase 4 under a new name."*
* **The Methodological Defense:**  
  This proposed design avoids that triviality through three deliberate structural departures:
  1. **Stratification:** Stratum A isolates delivery-admitted frames ($50\%$), guaranteeing that the cryptographic interaction between a corrupted wire ciphertext $\tilde{c}$ and a corrupted persistent twiddle $\tilde{\zeta}$ is powered and measured independently of packet drops.
  2. **Retransmission Dynamics:** Evaluates what happens when the communication link recovers on retry, but the receiver's memory does not. This directly models autonomous space systems recovering from link fade while suffering persistent memory SEUs.
  3. **Multi-Vector Generalization:** Expands from Phase 15Q's single test vector to 100 diversified KAT scenarios.

### 8.2 Final Recommendation

# **CONDITIONAL GO (Design Approved for Implementation Gate)**

### Explicit Reasons:
1. **Engineering Feasibility is Proven:** The Darwin ARM64 virtual memory isolation and restoration pipeline was empirically qualified with a 100% pass rate in Phase 15Q and audited in Phase 15R.
2. **Scientific Novelty is Distinct:** The design investigates persistent memory persistence across communication retries and dual cryptographic corruption ($\tilde{c} \times \tilde{\zeta}$), addressing an unexplored gap in post-quantum dependable systems.
3. **Execution Condition:** **Execution must NOT proceed immediately.** Implementation of the runner and execution of the $1{,}600$ trials require formal operator review of this preregistration document, followed by explicit authorization in a subsequent phase.
