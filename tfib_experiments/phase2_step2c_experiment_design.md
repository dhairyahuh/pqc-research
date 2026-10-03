# Phase 2 Step 2C-A: Countermeasure Independence Controlled Experiment Design

**Author:** Cryptographic Software Verification Research Group  
**Target:** ML-KEM-768 with Two-Factor Invariant Butterfly (TFIB) Countermeasure  
**Status:** Approved for Implementation  
**Date:** 2026-10-04  
**Scope:** Controlled experimental framework for evaluating countermeasure independence, common-mode fault exposure, and end-to-end containment  

---

## 1. Experimental Overview & Hypotheses

The objective of Phase 2 Step 2C-A is to systematically test the resilience of the Two-Factor Invariant Butterfly (TFIB) countermeasure when faults target the computation, the checker, shared state, or both simultaneously.

### Core Scientific Questions
1. Does the countermeasure maintain detection independence when faults affect the checker itself rather than the computation?
2. How does the system respond when an identical fault strikes both computation and verification state (common-mode failure)?
3. Does failure of the local countermeasure compromise the end-to-end security of ML-KEM-768, or does the Fujisaki-Okamoto transform provide a foolproof outer safety net?

```
                                      +------------------------------------+
                                      |   Deterministic Campaign PRF       |
                                      |   (SHAKE-256 Domain-Separated)     |
                                      +-----------------+------------------+
                                                        |
                                +-----------------------+-----------------------+
                                |                                               |
                   [Independent KeyGen]                            [Independent Encaps]
                   pk, sk via Oracle                               ct, ss_expected, ss_rej
                                |                                               |
                                +-----------------------+-----------------------+
                                                        |
                                                        v
                                       +--------------------------------+
                                       |      Production Target:        |
                                       |    mlkem768_dec_monitored()    |
                                       +----------------+---------------+
                                                        |
                                      +-----------------+-----------------+
                                      |                                   |
                         [Butterfly Arithmetic]              [TFIB Invariant Monitor]
                         zeta_op from mlk_zetas              zeta_ref from tfib_zetas_ref
                                      |                                   |
                                      +-----------------+-----------------+
                                                        |
                                                        v
                                       +--------------------------------+
                                       |    Fujisaki-Okamoto (FO)       |
                                       |   Re-encryption Verification   |
                                       +----------------+---------------+
                                                        |
                                +-----------------------+-----------------------+
                                |                                               |
                        [ss == ss_expected]                             [ss == ss_rej]
                         GENUINE_RECOVERY                                SAFE_FAIL_STOP
                                                                     LOCAL_BLIND_FO_CONTAINED
```

---

## 2. Controlled Experiment Specifications

Five controlled experiment families are designed to isolate each fault interaction category.

### Experiment 1: Fault Affects Primary Computation Only (`OP_TWIDDLE`)
- **Hypothesis:** Perturbing the operational twiddle $\zeta_{\text{op}}$ during forward/inverse NTT without corrupting the checker will be detected with 100% reliability by both TFIB-REF and TFIB-META. TFIB-REF will achieve genuine in-place recovery for transient faults and safe fail-stop for persistent faults. TFIB-META will force safe fail-stop for all operational twiddle faults due to the lack of an in-place repair table.
- **Injection Point:** `hook_mid_ntt_pre_butterfly` / `hook_mid_invntt_pre_butterfly` in `poly.c`.
- **Mechanism:** Bit-flip injection `*zeta_ptr ^= (1 << bit)` targeting layer $l \in [1, 7]$, butterfly index $b \in [0, 127]$, and bit $i \in [1, 15]$.
- **Duration / Persistence:**
  - *Transient:* `persistent = false`, active for exactly one butterfly invocation.
  - *Persistent:* `persistent = true`, re-injected on retry.
- **Independent Expected Outputs:**
  - Clean / Recovered: $ss = ss_{\text{expected}}$ from independent oracle.
  - Fail-stop / Rejection: $ss = ss_{\text{rej\_expected}}$ from independent oracle TweetFIPS-202 implementation.
- **Decision Criteria:**
  - *Detection:* `tfib_get_total_mismatches() > 0`
  - *Recovery:* $ss == ss_{\text{expected}} \land \text{status} == 0\text{x}5A5A5A5A \land \text{recovered\_count} > 0$
  - *Safe Fail-Stop:* $ss == ss_{\text{rej\_expected}} \land (\text{status} == 0\text{xFFFFFFFF} \lor \text{status} == 0\text{xA5A5A5A5})$
  - *SDC:* $ss \neq ss_{\text{expected}} \land ss \neq ss_{\text{rej\_expected}}$
- **Trial Count & Rationale:** 50 transient + 50 persistent trials across each configuration (300 total). Sample size $N=50$ gives statistical power to detect any defect rate exceeding $5.8\%$ at $95\%$ confidence (rule of three: upper bound $\approx 3/50 = 6\%$).

---

### Experiment 2: Fault Affects Reference or Checker Only (`REF_TWIDDLE` & `META_TAG`)
- **Hypothesis:** Perturbing verification-only data ($\zeta_{\text{ref}}$ in TFIB-REF or precomputed tag in TFIB-META) models false alarms caused by memory degradation in the countermeasure. The monitor will detect the mismatch. For transient faults, the rollback and retry will successfully verify against clean state, restoring clean execution. For persistent faults, the checker will refuse to certify the operation and trigger a safe fail-stop, preventing silent corruption.
- **Injection Point:**
  - TFIB-REF: `tfib_ref.c:49-54` (`TFIB_FAULT_REF_TWIDDLE`).
  - TFIB-META: `tfib_meta.c:53-58` (`TFIB_FAULT_META_TAG`).
- **Mechanism:** Bit-flip applied exclusively to the checker's local reference value prior to comparison.
- **Duration / Persistence:** Transient (cleared on retry) vs Persistent (re-applied on retry).
- **Decision Criteria:**
  - *Transient Recovery:* $ss == ss_{\text{expected}} \land \text{recovered\_count} > 0 \land \text{status} == 0\text{x}5A5A5A5A$.
  - *Persistent Safe Fail-Stop:* $ss == ss_{\text{rej\_expected}} \land \text{persistent\_fail\_count} > 0$.
  - *SDC:* $ss \neq ss_{\text{expected}} \land ss \neq ss_{\text{rej\_expected}}$.
- **Trial Count:** 50 transient + 50 persistent trials for each mode (200 total).

---

### Experiment 3: Fault Affects Checker Decision Logic (`CHECKER_LOGIC`)
- **Hypothesis:** Perturbing the checker's invariant evaluation predicate (`sum_c ^= 1`) simulates an ALU bit-flip or branch misprediction inside the monitor itself. The monitor will interpret this as a butterfly mismatch, trigger a rollback, and retry. If transient, the retry succeeds; if persistent, the system safely fail-stops. Under no circumstance does an internal checker bug cause SDC.
- **Injection Point:** `tfib_ref.c:77` and `tfib_meta.c:75` (`TFIB_FAULT_CHECKER_LOGIC`).
- **Mechanism:** Inverting the low bit of `sum_c` during monitor evaluation.
- **Duration / Persistence:** Transient vs Persistent.
- **Decision Criteria:**
  - *Detection:* `tfib_get_total_mismatches() > 0`.
  - *Recovery (Transient):* $ss == ss_{\text{expected}} \land \text{status} == 0\text{x}5A5A5A5A$.
  - *Safe Fail-Stop (Persistent):* $ss == ss_{\text{rej\_expected}} \land \text{status} \in \{0\text{xFFFFFFFF}, 0\text{xA5A5A5A5}\}$.
  - *SDC:* $ss \notin \{ss_{\text{expected}}, ss_{\text{rej\_expected}}\}$.
- **Trial Count:** 50 transient + 50 persistent trials for TFIB-REF and TFIB-META (200 total).

---

### Experiment 4: Fault Affects Both Through Simultaneous Corruption (`SIMULTANEOUS`)
- **Hypothesis:** When an identical bit-flip $\delta$ is applied simultaneously to both $\zeta_{\text{op}}$ and $\zeta_{\text{ref}}$, the local checker will evaluate:
  $$\zeta_{\text{op}} \oplus \delta = \zeta_{\text{ref}} \oplus \delta \implies \text{twiddle\_mismatch} = \text{false}$$
  $$t_{\text{check}} = \text{fqmul}(v_{\text{saved}}, \zeta_{\text{ref}} \oplus \delta) = t_{\text{used}} \implies \Delta_{\text{diff}} \equiv 0 \pmod q$$
  Local detection will be completely blinded (0% detection rate). However, because the corrupted twiddle distorts the NTT result, IND-CPA decryption yields an incorrect plaintext $m' \neq m$. Re-encryption yields $c' \neq c$, causing constant-time FO comparison to fail and decapsulation to output canonical $K_{\text{rej}}$.
  **Outcome:** Local monitor fails silently, but outer Fujisaki-Okamoto transform guarantees 100% safe rejection ($SDC = 0$).
- **Injection Point:** `hook_mid_ntt_pre_butterfly` (perturbs $\zeta_{\text{op}}$) + `tfib_ref.c:55-61` (perturbs $\zeta_{\text{ref}}$ with identical bit mask).
- **Mechanism:** `zeta_op ^= mask; zeta_ref ^= mask;`.
- **Duration / Persistence:** Transient simultaneous fault.
- **Decision Criteria:**
  - *Local Blindness:* `tfib_get_total_mismatches() == 0`.
  - *FO Containment:* $ss == ss_{\text{rej\_expected}} \land \text{status} \in \{0\text{xFFFFFFFF}, 0\text{xA5A5A5A5}\}$.
  - *Classification:* `LOCAL_BLIND_FO_CONTAINED`.
  - *SDC:* $ss \notin \{ss_{\text{expected}}, ss_{\text{rej\_expected}}\}$.
- **Trial Count:** 50 trials.

---

### Experiment 5: Fault Bypasses Detection but is Contained by End-to-End Behavior
- **Hypothesis:** Evaluating the baseline configuration (original unhardened monitor) under operational twiddle faults demonstrates the Theorem 1 blind spot ($0\%$ detection). The experiment proves that all faults evading local detection are partitioned cleanly into two safe sets:
  1. *Ineffective Faults:* The polynomial perturbation falls within the decoding error-tolerance (slack) of ML-KEM-768; the message $m$ decodes cleanly, producing valid $ss = ss_{\text{expected}}$ (`INEFFECTIVE_FAULT_VALID`).
  2. *Contained Corruptions:* The perturbation causes decoding error; FO re-encryption detects $c' \neq c$ and forces canonical implicit rejection $ss = ss_{\text{rej}}$ (`LOCAL_BLIND_FO_CONTAINED`).
  Under no condition does an undetected fault escape to cause SDC.
- **Injection Point:** Baseline monitor with `TFIB_FAULT_OP_TWIDDLE` (Transient and Persistent).
- **Trial Count:** 50 transient + 50 persistent trials (100 total).

---

## 3. Comprehensive Trial Matrix (900 Total Trials)

| Config | Fault Suite Name | Locus Enum | Persistence | Trials | Expected Detection | Expected Outcome Class |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BASELINE** | `CLEAN_CONTROL` | `TFIB_FAULT_NONE` | False | 50 | 0% (0/50) | `CLEAN_SUCCESS` (100%) |
| **BASELINE** | `OP_TWIDDLE_TRANSIENT` | `TFIB_FAULT_OP_TWIDDLE` | False | 50 | 0% (0/50) | `LOCAL_BLIND_FO_CONTAINED` / `INEFFECTIVE` |
| **BASELINE** | `OP_TWIDDLE_PERSISTENT` | `TFIB_FAULT_OP_TWIDDLE` | True | 50 | 0% (0/50) | `LOCAL_BLIND_FO_CONTAINED` / `INEFFECTIVE` |
| **TFIB_REF** | `CLEAN_CONTROL` | `TFIB_FAULT_NONE` | False | 50 | 0% (0/50) | `CLEAN_SUCCESS` (100%) |
| **TFIB_REF** | `OP_TWIDDLE_TRANSIENT` | `TFIB_FAULT_OP_TWIDDLE` | False | 50 | 100% (50/50) | `GENUINE_RECOVERY` (100%) |
| **TFIB_REF** | `OP_TWIDDLE_PERSISTENT` | `TFIB_FAULT_OP_TWIDDLE` | True | 50 | 100% (50/50) | `SAFE_FAIL_STOP` (100%) |
| **TFIB_REF** | `REF_TWIDDLE_TRANSIENT` | `TFIB_FAULT_REF_TWIDDLE` | False | 50 | 100% (50/50) | `GENUINE_RECOVERY` (100%) |
| **TFIB_REF** | `REF_TWIDDLE_PERSISTENT` | `TFIB_FAULT_REF_TWIDDLE` | True | 50 | 100% (50/50) | `SAFE_FAIL_STOP` (100%) |
| **TFIB_REF** | `SIMULTANEOUS_COMMON_MODE` | `TFIB_FAULT_SIMULTANEOUS` | False | 50 | 0% (0/50) | `LOCAL_BLIND_FO_CONTAINED` (100%) |
| **TFIB_REF** | `CHECKER_LOGIC_TRANSIENT` | `TFIB_FAULT_CHECKER_LOGIC` | False | 50 | 100% (50/50) | `GENUINE_RECOVERY` (100%) |
| **TFIB_REF** | `CHECKER_LOGIC_PERSISTENT` | `TFIB_FAULT_CHECKER_LOGIC` | True | 50 | 100% (50/50) | `SAFE_FAIL_STOP` (100%) |
| **TFIB_META** | `CLEAN_CONTROL` | `TFIB_FAULT_NONE` | False | 50 | 0% (0/50) | `CLEAN_SUCCESS` (100%) |
| **TFIB_META** | `OP_TWIDDLE_TRANSIENT` | `TFIB_FAULT_OP_TWIDDLE` | False | 50 | 100% (50/50) | `SAFE_FAIL_STOP` (100%) |
| **TFIB_META** | `OP_TWIDDLE_PERSISTENT` | `TFIB_FAULT_OP_TWIDDLE` | True | 50 | 100% (50/50) | `SAFE_FAIL_STOP` (100%) |
| **TFIB_META** | `META_TAG_TRANSIENT` | `TFIB_FAULT_META_TAG` | False | 50 | 100% (50/50) | `GENUINE_RECOVERY` (100%) |
| **TFIB_META** | `META_TAG_PERSISTENT` | `TFIB_FAULT_META_TAG` | True | 50 | 100% (50/50) | `SAFE_FAIL_STOP` (100%) |
| **TFIB_META** | `CHECKER_LOGIC_TRANSIENT` | `TFIB_FAULT_CHECKER_LOGIC` | False | 50 | 100% (50/50) | `GENUINE_RECOVERY` (100%) |
| **TFIB_META** | `CHECKER_LOGIC_PERSISTENT` | `TFIB_FAULT_CHECKER_LOGIC` | True | 50 | 100% (50/50) | `SAFE_FAIL_STOP` (100%) |

**Total:** 18 distinct experimental suites $\times$ 50 trials = **900 trials**.

---

## 4. Negative Test Plan (Adversarial Verification)

To prove that the validation harness itself does not pass vacuously, the following negative assertions are mandatory:
1. **Deliberate Corrupted Reference Key Injection:** Verify that if the oracle expected valid secret is corrupted, the clean-path test immediately fails with exit code 1.
2. **Corrupted Rejection Key Injection:** Verify that if decapsulation produces a bogus secret that matches neither $ss_{\text{expected}}$ nor $ss_{\text{rej}}$, it is flagged as SDC.
3. **Simultaneous Bypass Detection:** Assert that when `SIMULTANEOUS_COMMON_MODE` is executed, local detection is strictly 0, and that if any test harness attempted to label it as `GENUINE_RECOVERY`, the assertion triggers a failure.
4. **Checker Corruption Negative Test:** Assert that a persistent checker corruption cannot masquerade as clean execution.
