# Phase 17E — Independent Preregistration Consistency Audit

**Author:** Independent Statistical & Cryptographic Software Auditor  
**Date:** 2026-10-11  
**Project:** Cross-Layer Fault Interactions in ML-KEM-768 Key Establishment  
**Audit Target:** `PHASE17D_FINAL_PREREGISTRATION.md` and Associated Multi-Fault Design Artifacts  
**Execution Guard:** Strictly read-only audit. No C source code modified, no binaries compiled, no memory mutated, no trials executed, and no git commits or pushes performed. All prior phase artifacts preserved byte-for-byte.

---

## Executive Summary

Phase 17E is an independent, adversarial consistency audit of the Phase 17D Final Preregistration Lock (`PHASE17D_FINAL_PREREGISTRATION.md`). The audit inspected the formal mathematical specifications, combinatorial quota structures, C harness control flow (`research/combined_harness/combined_campaign.c`), reference oracle implementations (`tfib_experiments/phase11_oracle/`), test vector repositories (`references/test_vectors/`), and statistical inference procedures.

### Summary of Audit Findings
1. **Primary SDC Estimand & Accounting:** The primary SDC estimand is mathematically coherent and strictly confined to completed first-attempt decapsulations under Condition $C_{11}$ with active twiddle faults and wire bit inversion (`CH_BIT`). However, the shortfall formula $p_{\text{realized}} = 1 - (0.05)^{1/n_{\text{completed}}}$ fails at the boundary $n_{\text{completed}} = 0$ (division by zero), and the design lacks an attrition buffer for Quota 1 ($N_1 = 300$), where even 2 execution failures push the realized upper bound above $1.0\%$.
2. **Quota Allocation Integrity:** The aggregate arithmetic correctly sums to 420 master seeds ($1,680$ matched records). However, Phase 17D leaves specific combinatorial gaps: it omits the exact breakdown among the four delivery-blocking sub-classes in Quota 3 ($N_3 = 60$) and omits the exact $2 \times 2$ partition between dormant vs. sham and clean vs. corrupted controls in Quota 4 ($N_4 = 20$).
3. **Matched Four-Condition Estimand:** The unconstrained contrast $\hat{\Delta}_{\text{proto}} = \hat{p}_{11} - \hat{p}_{10} - \hat{p}_{01} + \hat{p}_{00}$ correctly avoids assuming $p_{10} = 0$, but unweighted pooling across Quotas 1–3 conflates radically different channel baseline failure rates. Furthermore, the handling of paired incomplete cases (where a seed crashes in one condition) requires explicit formalization.
4. **Channel Harness Semantics:** Direct source inspection of `combined_campaign.c` confirms that `CH_BIT` is indeed the sole fault class that mutates ciphertext bytes delivered to decapsulation. `CH_DUP` and `CH_REORDER` deliver clean ciphertexts to decapsulation, while `CH_TRUNC`, `CH_LOSS`, `CH_DELAY`, and `CH_INTERRUPT` are delivery-blocking and never invoke decapsulation.
5. **Oracle & Vector Provenance:** Static inspection of `independent_oracle.c` confirms that secret key seed $z$ is correctly extracted from $sk[2368..2399]$ and hashed with the exact received wire ciphertext $\tilde{c}$. Inspection of `fips202_ref.c` confirms it is a genuinely distinct, standalone TweetFIPS-202 implementation (not a wrapper). However, while Vector 0 exists as a static NIST KAT, Vectors 1–419 do not yet exist on disk; their validation is merely specified for future preflight execution.
6. **Integrity Re-Classification:** 6 of the 12 items marked "PASS" in Phase 17D are re-classified as "Merely Specified in Preregistration" or "Supported Only by Prior Report," reflecting the boundary between static specification and dynamic execution.

---

## 1. Primary Denominator and Intention-to-Test Accounting

### 1.1 Funnel Status Tracing and State Transitions
Every assigned master seed $i \in [1, N]$ undergoes deterministic transitions across the 5-tier accounting funnel:

```
[ Tier 1: Assigned Scenarios ] (N_assigned = 420; Quota 1: N_1 = 300)
         │
         │  Preflight Keygen & Encaps Cross-Checks (SUT vs. liboqs v0.16.0)
         ▼
[ Tier 2: Eligible Scenarios ] (N_eligible)
         │  - INELIGIBLE_VECTOR if SUT != liboqs
         │  - ORACLE_FAILURE if SHAKE-256 derivation faults
         ▼
[ Tier 3: Attempted Executions ] (N_attempted)
         │  - Darwin ARM64 Virtual Page Unprotected (__DATA_CONST,__zetas_page)
         │  - Active Twiddle Mutated (k in [1, 127], mask != 0)
         │  - Wire Channel Frame Injected (CH_BIT on ciphertext bytes)
         ▼
[ Tier 4: Completed Decapsulations ] (N_completed)
         │  - SIGNAL_TERMINATION if Mach-O access triggers SIGBUS/SIGSEGV
         │  - RESTORATION_FAILED if post-trial table hash != golden
         │  - EXECUTION_FAILURE if mlkem768_dec returns non-zero error code
         ▼
[ Tier 5: Analysable Cryptographic Outcomes ] (N_analysable)
            - 32-Byte Shared Secret Classified:
              * VALID: ss == K_golden
              * REJECT: ss == K_rej(c_wire)
              * SDC: ss != K_golden AND ss != K_rej(c_wire)
```

### 1.2 Target Population of the Primary SDC Estimand
The primary SDC rate estimand $\hat{p}_{\text{SDC}}$ specifically estimates:

$$\theta_{\text{SDC}} = \mathbb{P}\left(ss \neq K_{\text{golden}} \land ss \neq K_{\text{rej}}(\tilde{c}) \ \middle\vert \ C_{11}, \ a = 1, \ k \in [1, 127], \ \text{mask} \neq 0, \ \text{channel} = CH\_BIT, \ \text{decaps\_ran} = 1, \ \text{no\_crash} \right)$$

It is strictly a **conditional cryptographic outcome** evaluating whether the dual-fault interaction causes the decapsulation algorithm to produce an uncontained, non-rejection shared secret when execution runs to completion.

### 1.3 Conditioning Bias and Attrition Accounting
Excluding incomplete executions (e.g., signal terminations, hardware faults, or premature halts) creates potential **conditioning/survival bias**:
- If severe arithmetic corruptions or illegal memory states cause immediate hardware aborts (`SIGBUS`, `SIGSEGV`) rather than returning corrupted values, analyzing only completed executions measures SDC conditional on survival.
- **Mandatory Reporting Rule:** To prevent misleading claims of resilience caused by hardware crashes masking SDC, every report must present a dual accounting table:
  1. The **Cryptographic Integrity Table:** $\hat{p}_{\text{SDC}}$ among completed executions ($n_{\text{completed}}$).
  2. The **Intention-to-Test Reliability Table:** Total failure rate including execution crashes:
     $$\hat{p}_{\text{total\_fail}} = \frac{N_{\text{SDC}} + N_{\text{signal}} + N_{\text{exec\_fail}}}{N_{\text{attempted}}}$$

### 1.4 Boundary Condition at $n_{\text{completed}} = 0$
Phase 17D §2.4 specifies the shortfall formula:
$$p_{\text{realized}} = 1 - (0.05)^{1/n_{\text{completed}}}$$

**Audit Finding (Boundary Defect):** If $n_{\text{completed}} = 0$ (e.g., immediate page unprotect crash or total harness failure), the exponent $1 / 0$ is mathematically undefined.
- **Formal Preregistration Correction:** If $n_{\text{completed}} = 0$, the confidence bound cannot be evaluated ($p_{\text{realized}} = \text{UNDEFINED}$). The campaign outcome must be formally logged as `TOTAL_CAMPAIGN_EXECUTION_FAILURE`, and no upper bound may be reported.

### 1.5 Separation of Execution Failures from SDC
An execution failure (crash, trap signal, or non-zero return code) is an **availability/reliability failure**, not an SDC event. SDC strictly requires that decapsulation returns status code 0 (success) while outputting an undetected, maliciously corrupted shared secret. Counting execution crashes as SDC would confound system crash-stop behavior with cryptographic compromise.

---

## 2. Exact Quota Allocation and Combinatorial Integrity

### 2.1 Arithmetic Verification
The overall quota allocation specifies:
- Quota 1 (Primary Admitted-Corrupted): $N_1 = 300$ master seeds $\times 4 = 1,200$ matched records.
- Quota 2 (Admitted-Clean): $N_2 = 40$ master seeds $\times 4 = 160$ matched records.
- Quota 3 (Delivery-Blocking): $N_3 = 60$ master seeds $\times 4 = 240$ matched records.
- Quota 4 (Negative Controls): $N_4 = 20$ master seeds $\times 4 = 80$ matched records.
- **Total:** $N = 300 + 40 + 60 + 20 = 420$ master seeds; $420 \times 4 = 1,680$ matched trial records.
The arithmetic totals match exactly.

### 2.2 Residual Specification Gaps in Sub-Class Allocations

Despite the correct top-level sums, Phase 17D §2.2 fails to specify the internal integer distributions for Quotas 3 and 4:

#### Gap 2A: Quota 3 ($N_3 = 60$) Sub-Class Breakdown
Phase 17D lists: `CH_TRUNC`, `LOSS`, `DELAY`, `INTERRUPT` with $N_3 = 60$, but does not freeze the per-class allocation.
- **Audit Identification:** Are the 60 seeds divided equally (15 each), or weighted according to realistic channel failure distributions?
- **Preregistration Gap:** Left unspecified in Phase 17D.
- **Mandated Frozen Sub-Allocation:** To prevent post-hoc adjustment, Quota 3 must be formally frozen as:
  - `CH_TRUNC` (Truncation): **$n = 15$**
  - `CH_LOSS` (Packet Drop): **$n = 15$**
  - `CH_DELAY` (Timeout): **$n = 15$**
  - `CH_INTERRUPT` (Link Down): **$n = 15$**
  - Total: $15 + 15 + 15 + 15 = 60$.

#### Gap 2B: Quota 4 ($N_4 = 20$) Control Stratum $2 \times 2$ Grid
Phase 17D lists: "Dormant ($k=0$) & Sham (mask = 0) | Clean (10) & `CH_BIT` (10)" with $N_4 = 20$, but does not freeze the $2 \times 2$ factorial grid.
- **Audit Identification:** Does the design draw 5 of each cell, or 10 dormant and 10 sham with random channel allocation?
- **Preregistration Gap:** The exact cell counts are omitted.
- **Mandated Frozen Sub-Allocation:** Quota 4 must be formally frozen as:
  - Dormant ($k=0$) $\times$ Clean Channel: **$n = 5$**
  - Dormant ($k=0$) $\times$ `CH_BIT` Channel: **$n = 5$**
  - Sham Target (mask = `0x0000`) $\times$ Clean Channel: **$n = 5$**
  - Sham Target (mask = `0x0000`) $\times$ `CH_BIT` Channel: **$n = 5$**
  - Total: $5 + 5 + 5 + 5 = 20$.

---

## 3. Matched Four-Condition Estimand and Interaction Contrast

### 3.1 Paired Four-Condition Data Structure
For each master seed $i \in [1, N]$, the experiment observes a quadruple of protocol completion indicators:

$$\mathbf{Y}_i = \left( Y_{i, 00}, \ Y_{i, 10}, \ Y_{i, 01}, \ Y_{i, 11} \right) \in \{0, 1\}^4$$

where $Y_{i, c} = 1$ if key establishment completes successfully and both endpoints reach a shared secret matching $K_{\text{golden}, i}$ within the retry budget, and $Y_{i, c} = 0$ otherwise.

### 3.2 Unconstrained Interaction Contrast
The secondary protocol-interaction estimand is defined as:

$$\hat{\Delta}_{\text{proto}} = \hat{p}_{11} - \hat{p}_{10} - \hat{p}_{01} + \hat{p}_{00}$$

where $\hat{p}_c = \frac{1}{N} \sum_{i=1}^N Y_{i, c}$.
- **No Zero-Assumption:** The estimator makes no assumption that $p_{10} = 0$ or $p_{11} = 0$. In active non-dormant twiddle faults, empirical evidence indicates $p_{10} \approx 0$ and $p_{11} \approx 0$, yielding $\hat{\Delta}_{\text{proto}} \approx 1 - \hat{p}_{01}$. In negative controls (Quota 4), $p_{10} \approx 1$, yielding $\hat{\Delta}_{\text{proto}} \approx 0$.

### 3.3 Heterogeneous Stratum Weighting
**Audit Finding (Methodological Defect):** Pooling Quotas 1, 2, and 3 into an unweighted aggregate $\hat{\Delta}_{\text{proto}}$ combines radically different channel classes:
- For `CH_LOSS` and `CH_INTERRUPT`, $p_{01} \approx 0$ (channel blocks completion).
- For `CH_BIT`, $p_{01} \approx 1$ if retransmissions are transient, or $p_{01} \approx 0$ if persistent.
- For `CH_DUP`, $p_{01} \approx 1$ (duplicates are handled transparently).
An unweighted average across 300 `CH_BIT`, 40 `CH_DUP`/`CH_REORDER`, and 60 blocking faults produces an arbitrary mixture ratio ($300:40:60$).
- **Mandated Reporting Rule:** $\hat{\Delta}_{\text{proto}}$ must be reported:
  1. **Stratified by Channel Class:** Separately for `CH_BIT`, `CH_DUP`/`REORDER`, and delivery-blocking classes.
  2. **Standardized Stratum-Weighted Contrast:** If an aggregate number is reported, weights must be fixed explicitly:
     $$\hat{\Delta}_{\text{std}} = \sum_{s} w_s \hat{\Delta}_s, \quad \text{with prespecified } w_s.$$

### 3.4 Handling of Incomplete Paired Cases
If seed $i$ suffers an execution crash (e.g. `SIGSEGV`) in Condition $C_{11}$:
- **Complete-Case Strategy:** Dropping seed $i$ entirely from all four conditions preserves exact pairing across conditions, but reduces the sample size.
- **ITT Failure Imputation Strategy:** Treating execution crash as a protocol failure ($Y_{i, 11} = 0$) preserves the full master seed denominator.
- **Mandated Rule:** The primary protocol analysis shall use **ITT Failure Imputation** ($Y=0$ for execution crashes), with a sensitivity analysis conducted under **Complete-Case Pairing**. Under no circumstances may different seed sets be compared marginally across conditions.

---

## 4. Channel Harness Behavior and Activation Audit

### 4.1 Static Source Code Inspection of `combined_campaign.c`
The channel fault injection logic was directly inspected in [combined_campaign.c](file:///Users/dhairyajain/Desktop/pqc%20research/research/combined_harness/combined_campaign.c#L98-L130):

```c
// research/combined_harness/combined_campaign.c:98-113
if(ch_active){
    switch(ch_class){
        case CH_LOSS:      r.kind=K_LOST; r.effect="LOST"; return r;
        case CH_INTERRUPT: r.kind=K_LOST; r.effect="LINK_DOWN"; return r;
        case CH_DELAY:     latency=DEADLINE+1+(int)(rr%50); eff="DELAYED"; break;
        case CH_TRUNC:     wlen=WIRE-(1+(size_t)(rr%64)); eff="TRUNCATED"; break;
        case CH_BIT:       { size_t pos=rr%CT; wire[pos]^=(uint8_t)(1<<((rr>>8)&7)); eff="CORRUPTED"; } break;
        case CH_DUP:       eff="DUPLICATED"; break;
        case CH_REORDER:   eff="REORDERED"; break;
        default: break;
    }
}
r.effect=eff;
if(latency>DEADLINE){ r.kind=K_TIMEOUT; r.effect="DELAYED"; return r; }
if(wlen < (size_t)WIRE){ r.kind=K_MALFORMED; return r; }   /* truncation */
const uint8_t *ct2=wire, *enc2=wire+CT, *tag2=wire+CT+FRAME;
```

### 4.2 Reconciliation of Channel Classes with Decapsulation Activation

| Channel Class | Wire Payload Modification | Harness Transport Action | Decapsulation Invoked? (`decaps_ran`) | Ciphertext Received by Decapsulation |
| :--- | :--- | :--- | :---: | :--- |
| **`CH_BIT`** | `wire[pos] ^= mask` ($pos < 1088$) | Delivered to receiver | **YES (`decaps_ran = 1`)** | **Corrupted Ciphertext $\tilde{c}$** |
| **`CH_DUP`** | Wire bytes unmodified | Delivered to receiver | **YES (`decaps_ran = 1`)** | Clean Ciphertext $c$ |
| **`CH_REORDER`** | Wire bytes unmodified | Delivered to receiver | **YES (`decaps_ran = 1`)** | Clean Ciphertext $c$ |
| **`CH_TRUNC`** | Truncated by $1..64$ bytes | Returns `K_MALFORMED` (L112) | **NO (`decaps_ran = 0`)** | None (Transport aborts) |
| **`CH_DELAY`** | Wire bytes unmodified | Returns `K_TIMEOUT` (L111) | **NO (`decaps_ran = 0`)** | None (Deadline expires) |
| **`CH_LOSS`** | Frame discarded | Returns `K_LOST` (L100) | **NO (`decaps_ran = 0`)** | None (Frame dropped) |
| **`CH_INTERRUPT`** | Link disabled | Returns `K_LOST` (L101) | **NO (`decaps_ran = 0`)** | None (Link down) |

### 4.3 Conclusion on Channel Activation
The source code inspection confirms with 100% certainty that:
1. `CH_BIT` is the **only** channel fault class that delivers a modified ciphertext to the decapsulation engine.
2. Quota 1 is correctly and uniquely eligible for primary cryptographic SDC analysis.
3. Classes in Quota 2 test protocol handling of sequence anomalies with clean cryptographic inputs.
4. Classes in Quota 3 test transport recovery without cryptographic decapsulation.

---

## 5. Vector Provenance and Oracle Independence Audit

### 5.1 Test Vector Inventory: Static KAT vs. Local Vectors
- **Vector 0 (Static Reference KAT):** Inspected [references/test_vectors/mlkem_expected_kat.h](file:///Users/dhairyajain/Desktop/pqc%20research/references/test_vectors/mlkem_expected_kat.h). It contains exactly **1 static test vector** (derived from the official NIST FIPS 203 reference suite with fixed `test_vector_d`, `test_vector_z`, `test_vector_m`).
- **Vectors 1 through 419:** Do **not** exist on disk as pre-computed artifacts.
- **Audit Finding:** Phase 17D §4.2 specifies a 4-step preflight verification pipeline to generate and cross-check these 419 vectors at runtime. **Phase 17D does not contain executed validation evidence for all 420 vectors**; it merely specifies the generation algorithm and preflight assertions. This distinction must be explicitly acknowledged.

### 5.2 Secret Key Seed $z$ Extraction and Oracle Wiring
Inspected [tfib_experiments/phase11_oracle/independent_oracle.c](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/phase11_oracle/independent_oracle.c#L59-L79):

```c
// tfib_experiments/phase11_oracle/independent_oracle.c:70-77
const uint8_t *z = sk + (ORACLE_MLKEM768_SK_BYTES - ORACLE_MLKEM768_SS_BYTES);

uint8_t z_c[ORACLE_MLKEM768_SS_BYTES + ORACLE_MLKEM768_CT_BYTES];
memcpy(z_c, z, ORACLE_MLKEM768_SS_BYTES);
memcpy(z_c + ORACLE_MLKEM768_SS_BYTES, ct, ORACLE_MLKEM768_CT_BYTES);

/* Use standalone specification-based reference SHAKE-256 */
fips202_ref_shake256(ss_rej, ORACLE_MLKEM768_SS_BYTES, z_c, sizeof(z_c));
```

- **FIPS 203 Standard Compliance:** Under FIPS 203 Section 6.1 (Algorithm 17), $dk_{\text{ML-KEM}} = (dk_{\text{PKE}} \parallel ek \parallel H(ek) \parallel z)$, where $z \in \mathbb{B}^{32}$. For ML-KEM-768, $sk$ is 2,400 bytes, and $z$ occupies bytes 2368..2399 ($2400 - 32$). The pointer arithmetic `sk + 2368` correctly and uniquely extracts $z$.
- **Wire Ciphertext Coupling:** In `combined_campaign.c:122`, the pointer passed to `independent_oracle_compute_rejection(ss_rej, sk, ct2)` is `ct2 = wire`, which holds the post-channel wire buffer. Thus, the rejection oracle hashes the exact corrupted wire bytes $\tilde{c}$, strictly satisfying Algorithm 17 ($K_{\text{rej}} = \text{SHAKE256}(z \parallel \tilde{c}, 32)$).

### 5.3 Independent SHAKE-256 Implementation Audit
Inspected [tfib_experiments/phase11_oracle/fips202_ref.c](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/phase11_oracle/fips202_ref.c):
- `fips202_ref.c` is an 86-line standalone C implementation of the Keccak-f[1600] permutation based on the TweetFIPS-202 reference algorithm.
- It defines explicit round constants `RC[24]`, rotation offsets `r_rot[24]`, permutation indices `pi_idx[24]`, and implements the $\theta, \rho, \pi, \chi, \iota$ transformations from first principles.
- It contains **zero includes** of `mlkem-native` headers, zero inline assembly, and no calls into `liboqs`.
- **Conclusion:** It is a **genuinely distinct, clean-room implementation**, not a wrapper or separate compilation unit of the SUT codebase.

---

## 6. Statistical Claims and Confidence Bound Audit

### 6.1 Exact Clopper–Pearson Upper Bound at $n = 300$
For $k = 0$ observed SDC events in $n = 300$ independent trials, the one-sided 95% Clopper–Pearson upper bound $p_U$ solves:

$$(1 - p_U)^{300} = 0.05 \implies p_U = 1 - (0.05)^{1/300}$$

- **Independent Mathematical Derivation:**
  $$p_U = 1 - \exp\left(\frac{\ln 0.05}{300}\right) = 1 - \exp\left(\frac{-2.99573227}{300}\right) = 1 - \exp(-0.00998577) = 0.00993608$$
  $$\mathbf{p_U = 0.9936\% \quad (< 1.0000\%)}$$
- Phase 17D reported $0.9934\%$ (a negligible rounding discrepancy of $0.0002\%$). Both values satisfy the preregistered threshold ($< 1.0\%$).

### 6.2 Zero-Buffer Attrition Sensitivity
Evaluating the Clopper–Pearson bound for minor sample shortfalls reveals extreme sensitivity:

| Completed Trials ($n_{\text{completed}}$) | Shortfall Count | Exact One-Sided 95% Upper Bound | Preregistration Target ($< 1.0\%$) |
| :---: | :---: | :---: | :---: |
| **300** | 0 | **0.9936%** | **PASS (< 1.0%)** |
| **299** | 1 | **0.9969%** | **PASS (< 1.0%)** |
| **298** | 2 | **1.0002%** | **FAIL ($\ge 1.0\%$)** |
| **295** | 5 | **1.0104%** | **FAIL ($\ge 1.0\%$)** |
| **290** | 10 | **1.0277%** | **FAIL ($\ge 1.0\%$)** |

**Critical Methodological Risk:** The quota of exactly $N_1 = 300$ provides an attrition buffer of **exactly one single trial** ($n \ge 299$). If just **two** trials encounter an unhandled hardware trap or Mach-O page access failure, the realized bound will cross above $1.0\%$.
- While Phase 17D includes a shortfall reporting rule, an experimental design intended to demonstrate an upper bound below 1.0% should ideally allocate a 5% preflight safety margin (e.g. $N_1 = 315$).

### 6.3 Resampling and Repeated Attempts
- **Attempt 1 Independence:** Attempt 1 trials across distinct master seeds utilize independently drawn cryptographic keys, twiddle targets, and bitmasks. Observations are independent and identically distributed, satisfying binomial assumptions.
- **Retransmission Clustering:** Attempts 2 and 3 within a seed share the secret key $sk$ and the persistent memory mutation. The preregistration correctly mandates cluster-robust standard errors or cluster bootstrap clustered at the master seed level.
- **Epistemological Guard:** An empirical upper bound of $0.994\%$ **does not prove zero risk or mathematical immunity**. It establishes an empirical upper bound of $0.994\%$ at 95% confidence under the tested model and sample size.

---

## 7. Gate and Evidence Integrity Re-Evaluation

Every gate item claimed as "PASS" in Phase 17D §6 has been independently audited and re-classified according to its actual evidentiary foundation:

| Gate ID | Requirement Description | Phase 17D Claim | Independent Audit Evidentiary Classification | Re-Evaluated Verdict |
| :---: | :--- | :---: | :--- | :---: |
| **G-01** | Primary SDC population restricted to Attempt 1 active twiddle $\times$ `CH_BIT` | PASS | **Merely Specified in Preregistration** (Design specification locked) | **PASS (Design)** |
| **G-02** | Fixed quota block sampling locks exactly $N_1 = 300$ eligible active `CH_BIT` cases | PASS | **Merely Specified in Preregistration** (Top quota locked; sub-quotas have gaps) | **CONDITIONAL** |
| **G-03** | Exact Clopper–Pearson bound calculation mathematically verified ($0.9936\% < 1.0\%$) | PASS | **Mathematically Derived** (Independently verified in §6.1) | **PASS** |
| **G-04** | Intention-To-Test accounting table pre-specified for execution anomalies | PASS | **Merely Specified in Preregistration** (Funnel defined; $n=0$ boundary unhandled) | **CONDITIONAL** |
| **G-05** | Negative controls partitioned into separate Quota 4 ($N=20$) | PASS | **Merely Specified in Preregistration** ($2 \times 2$ grid unpartitioned) | **CONDITIONAL** |
| **G-06** | Channel control flow traced: `CH_BIT` verified as sole ciphertext-mutating class | PASS | **Verified by Direct Source Inspection** (`combined_campaign.c:98-125`) | **PASS** |
| **G-07** | Vector inventory verified: 1 static NIST KAT + 419 locally generated cases | PASS | **Verified by Direct Source Inspection** (Vector 0); **Merely Specified** (Vectors 1–419) | **PASS (Clarified)** |
| **G-08** | 4-step cross-implementation vector validation pipeline defined (`liboqs` vs SUT) | PASS | **Merely Specified in Preregistration** (Design pipeline defined; not executed) | **PASS (Design)** |
| **G-09** | Dynamic rejection oracle uses received ciphertext $\tilde{c}$ and matching seed $z_i$ | PASS | **Verified by Direct Source Inspection** (`independent_oracle.c:59-79`) | **PASS** |
| **G-10** | Unconstrained protocol contrast $\hat{\Delta}_{\text{proto}}$ defined without assuming $p_{10}=0$ | PASS | **Mathematically Derived** (Contrast formula valid; weighting needs stratification) | **PASS** |
| **G-11** | Darwin ARM64 virtual memory isolation qualified on `(__DATA_CONST,__zetas_page)` | PASS | **Supported Only by Prior Report** (Phase 15Q pilot / 15R audit reports) | **PASS (Prior Evidence)** |
| **G-12** | Compilation and execution deferred until separate authorized implementation gate | PASS | **Verified by Direct Process Inspection** (No binaries compiled, tree clean) | **PASS** |

---

## 8. Cryptographic Hash Integrity Audit

All artifacts in `research/phase17_multi_fault_design/` were independently hashed using SHA-256 and verified against previously recorded values:

| File Path | Recorded Hash (Phase 17D) | Independently Computed Hash (Phase 17E) | Status |
| :--- | :--- | :--- | :---: |
| `PHASE17_EXPERIMENT_DESIGN.md` | `36180af5fbf45a3f50b36f52d6375725020dd9577dfa5b89e40252e5e9479887` | `36180af5fbf45a3f50b36f52d6375725020dd9577dfa5b89e40252e5e9479887` | **MATCH** |
| `PHASE17B_METHODS_CORRECTION.md` | `9180a13c1cf98050f05f3a426cc0d1102ce34c9d76ad48c9d51015f2931a25d4` | `9180a13c1cf98050f05f3a426cc0d1102ce34c9d76ad48c9d51015f2931a25d4` | **MATCH** |
| `PHASE17B_CHANGELOG.md` | `f126e778f46dc562266408b80f8d373900e7d85dcdb3655ef68dfdcac7fa9edc` | `f126e778f46dc562266408b80f8d373900e7d85dcdb3655ef68dfdcac7fa9edc` | **MATCH** |
| `PHASE17C_RESIDUAL_AUDIT.md` | `0e6c6e26120864297c592f26d7f77dd8c3fc10d7d3518f62fa4ffd2d08404c12` | `0e6c6e26120864297c592f26d7f77dd8c3fc10d7d3518f62fa4ffd2d08404c12` | **MATCH** |
| `PHASE17C_CHANGELOG.md` | `b5d99bb289b316c6f1515d0c31f21c25da11c4871929dd2bc480b044d2d1bccf` | `b5d99bb289b316c6f1515d0c31f21c25da11c4871929dd2bc480b044d2d1bccf` | **MATCH** |
| `PHASE17D_FINAL_PREREGISTRATION.md` | `474e72b8fd4516bc5723701d168eb58cffdd6f2a444caa302e4a6207a0a9b71d` | `474e72b8fd4516bc5723701d168eb58cffdd6f2a444caa302e4a6207a0a9b71d` | **MATCH** |
| `PHASE17D_CHANGELOG.md` | `6c3de8cf3c2ab52300394e8ccb5e1e3b8599c8553d201013f9c8057028b9a708` | `6c3de8cf3c2ab52300394e8ccb5e1e3b8599c8553d201013f9c8057028b9a708` | **MATCH** |

---

## 9. Defect Action Matrix and Required Resolutions

| Defect ID | Description | Severity | Impact on Process | Precise Evidence Needed to Close |
| :---: | :--- | :---: | :--- | :--- |
| **D-01** | **Quota 3 Sub-Class Underspecification:** The 60 delivery-blocking seeds are not partitioned among TRUNC, LOSS, DELAY, and INTERRUPT. | Minor | Limits Sub-Class Inferences | Explicitly freeze the sub-allocation as exactly 15 seeds per class in the runner pre-allocation manifest. |
| **D-02** | **Quota 4 Control Stratum Underspecification:** The 20 control seeds are not partitioned across the $2 \times 2$ grid (dormant/sham $\times$ clean/corrupted). | Minor | Limits Baseline Contrasts | Explicitly freeze the $2 \times 2$ grid as exactly 5 seeds per cell in the runner pre-allocation manifest. |
| **D-03** | **Zero-Buffer Attrition Risk in Quota 1:** $N_1 = 300$ allows only 1 execution failure before the upper bound exceeds $1.0\%$. | Moderate | Risks Realized Claim Target | Pre-allocate a 5% buffer ($N_1 = 315$) or enforce strict adherence to the shortfall rule if $n_{\text{completed}} < 299$. |
| **D-04** | **Shortfall Boundary Division by Zero:** $p_{\text{realized}} = 1 - 0.05^{1/n}$ is undefined if $n_{\text{completed}} = 0$. | Minor | Mathematical Edge Case | Formalize rule: $n_{\text{completed}} = 0 \implies \text{UNDEFINED}$ (mark run as `TOTAL_CAMPAIGN_FAILURE`). |
| **D-05** | **Secondary Protocol Contrast Weighting:** Unweighted contrast over Quotas 1–3 creates an arbitrary mixture of channel baselines. | Minor | Limits Secondary Aggregate Claims | Mandate stratified reporting by channel class and define explicit weights for aggregate contrasts. |
| **D-06** | **Clarification of Test Vector Status:** Report must distinguish Vector 0 (existing static KAT) from Vectors 1–419 (pending preflight generation). | Minor | Reporting Precision | Formally document that Vectors 1–419 are generated and verified during runner preflight, not pre-existing static files. |

---

## 10. Required Final Verdict

# **CONDITIONAL — SPECIFIC DESIGN DEFECTS REMAIN**

### Justification for Verdict:
1. **Core Architecture and Math are Sound:** The primary estimand definition, the sample size of 300 achieving $0.9936\% < 1.0\%$, the source-verified restriction to `CH_BIT`, and the clean-room TweetFIPS-202 rejection oracle are robust and mathematically valid.
2. **Specific Deficiencies Prevent Unconditional Pass:**
   - Combinatorial gaps remain in Quota 3 (sub-class counts) and Quota 4 ($2 \times 2$ control grid).
   - Quota 1 has zero margin for hardware attrition ($n \ge 299$ required).
   - Edge case $n=0$ in the shortfall formula is mathematically undefined.
   - Secondary protocol contrasts require mandatory stratification to avoid arbitrary baseline confounding.
3. **Execution Guard Maintained:** **This audit does NOT authorize the campaign.** All six identified defects can be closed during the formal implementation review and embedded directly into the runner's pre-allocation manifest before compiling or executing trials.
