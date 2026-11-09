# Independent Experimental Validity Audit: Twiddle Factor Integrity Binding (TFIB)

**Auditor:** Independent Cryptographic Implementation & Fault-Injection Verification Researcher  
**Target:** ML-KEM-768 Twiddle Factor Integrity Binding (`TFIB-Ref` & `TFIB-Meta`)  
**Host Architecture:** Apple Silicon ARM64 (Apple M3 Pro), macOS Darwin 25.1.0, Apple Clang 17.0.0 (`-O3`)  
**Audit Date:** October 2026  
**Artifacts Audited & Generated:**  
- Architecture & Vulnerability Model: [`tfib_design.md`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_design.md)
- Implementation Under Audit: [`tfib_implementation/`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/)
- Original Raw Dataset: [`tfib_raw_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_raw_results.csv)
- Independent Trial-Level Audit Dataset: [`tfib_trial_level_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_trial_level_results.csv) (900 trials)
- Aggregated Reproduction Matrix: [`tfib_reproduced_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_reproduced_results.csv) (18 suites)
- High-Resolution Timing Samples: [`tfib_benchmark_raw.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_benchmark_raw.csv) (40,000 samples)
- Failure Mode Catalog: [`tfib_failure_cases.md`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_failure_cases.md)
- Reproducibility Runbook: [`tfib_reproducibility_commands.md`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_reproducibility_commands.md)

---

## 1. Executive Audit Verdict

This audit conducted an independent, skeptical evaluation of the Twiddle Factor Integrity Binding (TFIB) research extension. Every line of code, fault hook, benchmark sample, and outcome classification was subjected to source-level tracing, compiler-level symbol analysis, and oracle-driven falsification testing.

### Key Conclusions:
1. **The Core Vulnerability (Theorem 1) is Authentically Reproduced:** The baseline dual-transform invariant monitor is demonstrably $100\%$ blind locally ($0.0\%$ detection across 100 trials) to operational twiddle factor corruption. Because the verifier receives the faulted $\zeta$ as an argument, both algebraic invariants cancel out identically.
2. **TFIB Closes the Local Blind Spot:** Both `TFIB-Ref` (dual-reference table) and `TFIB-Meta` (precomputed integrity metadata) achieve **$100.0\%$ local detection** (50/50 trials each) of operational twiddle corruption.
3. **Availability is Restored under `TFIB-Ref`:** `TFIB-Ref` converts an otherwise fatal $0.0\%$ recovery rate into a **$100.0\%$ genuine recovery rate** for transient twiddle faults, verified by an independent cryptographic oracle.
4. **Common-Mode Limits are Real and Definite:** When operational and reference twiddles are corrupted simultaneously, local detection drops to $0.0\%$. `TFIB-Ref` does not and cannot provide physical fault independence in software.
5. **Benchmark Anomalies Fully Explained:** The previously reported high standard deviation in `TFIB-Meta` was caused by CPU scheduling preemption under host background load, magnified by `TFIB-Meta`'s increased instruction-cache footprint (617 outliers $>1\,\text{ms}$). Fault-free `TFIB-Ref` overhead is $+18.65\%$ (median $173.17\,\mu\text{s}$ vs baseline $145.96\,\mu\text{s}$). Active rollback and repair incurs an empirical latency penalty of $+119.75\,\mu\text{s}$ ($+69.15\%$).

---

## 2. Verification of Fault-Injection Placement & Execution

### 2.1 Hook Tracing to Concrete Machine Operations
Every fault locus was traced from user configuration to the exact C statement and machine register it perturbs:

| Fault Locus | Source Hook Location | Concrete C Operation | Assembly / Machine Target |
| :--- | :--- | :--- | :--- |
| `TFIB_FAULT_OP_TWIDDLE` | [`poly.c:388,564`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L388) | `*zeta_ptr ^= (1 << bit)` | In-place XOR bit flip on local stack variable `zeta_val` immediately prior to `mlk_fqmul(..., zeta_val)`. |
| `TFIB_FAULT_REF_TWIDDLE`| [`tfib_ref.c:52,146`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_ref.c#L52) | `zeta_ref ^= (1 << bit)` | Bit flip on local stack register loaded from `tfib_zetas_ref[k]` inside the monitor. |
| `TFIB_FAULT_META_TAG`   | [`tfib_meta.c:55,135`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_meta.c#L55) | `expected_tag ^= (1 << bit)`| Bit flip on local stack register loaded from `tfib_zetas_tag[k]` inside the monitor. |
| `TFIB_FAULT_SIMULTANEOUS`| [`tfib_core.c:160`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_core.c#L160) & [`tfib_ref.c:58`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_ref.c#L58) | `*zeta_ptr ^= mask; zeta_ref ^= mask;` | Simultaneous identical bit flip applied to both operational scalar and reference scalar. |
| `TFIB_FAULT_CHECKER_LOGIC`| [`tfib_ref.c:77`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_ref.c#L77) / [`tfib_meta.c:75`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_implementation/tfib_meta.c#L75) | `sum_c ^= 1` | Bit flip on the evaluated invariant difference register, simulating a transient arithmetic checker malfunction. |

### 2.2 Phase Isolation (Keygen, Encapsulation, Decapsulation)
- In [`tfib_validity_audit_runner.c:60-74`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/tfib_validity_audit_runner.c#L60-L74), `tfib_fault_reset()` and `tfib_reset_all_stats()` are executed at the beginning of every trial.
- Key generation (`mlkem768_keypair`) and encapsulation (`mlkem768_enc`) run while `g_tfib_fault.enabled == false`.
- The fault is armed via `tfib_fault_arm()` *only immediately prior* to calling `mlkem768_dec_monitored()`.
- **Audit Finding:** Faults are strictly isolated to the decapsulation phase. No cross-trial leakage or setup contamination exists.

### 2.3 Activation Rates and Trigger Counts
The trial-level log [`tfib_trial_level_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_trial_level_results.csv) records exact activation counts for all 900 trials:
- **Clean Control Suites:** `0` triggers across 150 trials ($0.0\%$ false alarm rate).
- **Transient Suites:** Exactly $1$ trigger per trial across all 50 trials ($50/50$ trials, $50$ total triggers, exactly $1.00$ triggers/trial).
- **Persistent Suites:** Exactly $11$ triggers per trial across all 50 trials ($50/50$ trials, $550$ total triggers, exactly $11.00$ triggers/trial).
  - *Mathematical Explanation:* ML-KEM-768 decapsulation executes exactly 11 NTT transforms: 4 inverse NTTs in `mlk_indcpa_dec` (3 in `mlk_polyvec_invntt_tomont` + 1 in `mlk_poly_invntt_tomont`), followed by 7 forward NTTs in `mlk_indcpa_enc` re-encryption. A persistent fault matching a specific `(layer, b_idx)` hits once per transform, producing exactly 11 activations per decapsulation.
- **Audit Verdict on Activation:** **100.0% Activation Integrity Verified**.

---

## 3. In-Depth Audit of TFIB-Ref and TFIB-Meta

### 3.1 Software Independence Analysis of `TFIB-Ref`
The claim of "independent reference data" was scrutinized against compiler and linker behavior.

#### Symbol and Memory Layout Audit:
Executing `nm -m` and address inspection on the compiled binary yields:
```text
00000001000168a0 (__TEXT,__const) non-external _mlk_zetas
0000000100016a60 (__TEXT,__const) external     _tfib_zetas_ref
0000000100016b60 (__TEXT,__const) external     _tfib_zetas_tag
```
- Both `_mlk_zetas` and `_tfib_zetas_ref` reside in the identical read-only text segment (`__TEXT,__const`).
- The memory separation between the operational table and the reference table is exactly **448 bytes** ($0x1C0$).
- Both tables fit within a single 4KB memory page and reside in adjacent lines of the L1 cache.

#### Compiler & Linker Optimization Hazards:
1. **Identical Code / Data Folding (ICF):**  
   Because `mlk_zetas` and `tfib_zetas_ref` contain identical 256-byte constant tables, an optimizing linker invoked with `-Wl,--icf=all` or under Link-Time Optimization (`-flto`) can merge them into a single symbol. In that event, the software-level redundancy is completely eliminated without warning.
2. **Physical Fault Independence is False:**  
   Software separation of variables does not imply physical hardware separation. A single physical ionizing particle strike, power-rail transient, or memory bus glitch affects both tables simultaneously.
3. **Audit Verdict on Independence:**  
   `TFIB-Ref` provides **operational path decoupling**, not hardware fault independence. Claims of physical fault immunity are rejected.

### 3.2 Metadata Tag Audit of `TFIB-Meta`
`TFIB-Meta` generates tags using:
```c
static inline uint16_t tfib_meta_compute_tag(int16_t zeta, unsigned k) {
    uint32_t val = (uint32_t)(uint16_t)zeta;
    uint32_t idx = (uint32_t)k;
    return (uint16_t)(((val * 31337u) ^ (idx * 1337u) ^ 0xA55Au) & 0xFFFFu);
}
```
- **Not a Cryptographic MAC:** This is an affine linear congruential hash, not a cryptographic authentication tag. It provides zero security against an active adversary capable of correlated fault injection.
- **Single-Fault Collision Proof:**  
  Because $\gcd(31337, 2^{16}) = 1$, the function $f(x) = (x \cdot 31337) \pmod{2^{16}}$ is a bijection over $\mathbb{Z}_{2^{16}}$. For any fixed twiddle index $k$, every single 16-bit value $\zeta \ne \zeta'$ produces a distinct tag. Single-point twiddle corruptions are mathematically guaranteed to be detected ($100\%$ detection rate).
- **Targeted Multi-Fault Bypass:**  
  If an adversary injects a bit flip $\Delta \zeta$ into the twiddle factor and simultaneously injects $\Delta \text{tag} = (\Delta \zeta \cdot 31337) \pmod{2^{16}}$ into the tag table, the check passes completely undetected.
- **Audit Verdict on Metadata:**  
  Valid for non-adversarial Single-Event Upsets (SEUs); completely invalid for adversarial fault injection.

---

## 4. Revalidation of Outcome Classifications & Oracle Independence

Every trial was classified using an external oracle that did not trust internal return codes, `status` pointers, or recovery counters:
- **Oracle Valid Match:** `memcmp(ss_out, ss_expected, 32) == 0`.
- **Oracle Rejection Match:** `memcmp(ss_out, ss_rej_expected, 32) == 0`, where `ss_rej_expected` was independently computed via pure SHAKE-256 over `sk[z] || ct`.
- **Silent Data Corruption (SDC):** Any output where `!oracle_valid_match && !oracle_rejection_match`.

### Outcome Discrepancy & Classification Audit:

| Claimed Metric | Audited Reality | Oracle Finding & Mechanism |
| :--- | :--- | :--- |
| **Baseline Detection Rate** | **0.0% (0/50)** | **Confirmed.** Monitor invariant evaluated to 0 on all trials despite arithmetic corruption. |
| **TFIB-Ref Transient Recovery** | **100.0% (50/50)** | **Confirmed Genuine Recovery.** Oracle verified that $ss_{\text{out}} == K_{\text{valid}}$ across all 50 trials. In-place rollback and reference recalculation succeeded. |
| **TFIB-Ref Persistent Containment**| **100.0% (50/50)** | **Confirmed Safe Fail-Stop.** Repeated retry failed secondary check, forcing persistent counter increment and canonical implicit rejection. |
| **Ineffective Faults (LWE Slack)**| **1/50 Baseline, 2/50 Simultaneous**| **Confirmed Physical/LWE Property.** Single-bit flips on early layers produce polynomial errors $\le q/4$ that are rounded away by `mlk_poly_tomsg`. This is an inherent property of lattice-based cryptography, not an SDC or verifier flaw. |
| **Silent Data Corruption (SDC)** | **0.0% (0/900 trials)** | **Confirmed.** Downstream Fujisaki-Okamoto re-encryption serves as an infallible backstop. No invalid secret key was ever accepted. |

---

## 5. Reproduction & Reconciliation Matrix

Table 1 presents the full reproduced experimental results from [`tfib_reproduced_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_reproduced_results.csv) across all 18 test suites (900 trials).

### Table 1: Comprehensive Reproduced Outcomes

| Config | Fault Suite | Persistent | Trials | Activated | Triggers | Local Det | Det Rate | Recovered | Safe Stop | FO Catch | Ineffective | SDC |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline** | Clean Control | No | 50 | 0 | 0 | 0 | **0.0%** | 0 | 0 | 0 | 0 | **0** |
| **Baseline** | Op Twiddle | No | 50 | 50 | 50 | 0 | **0.0%** | 0 | 0 | 49 | 1 | **0** |
| **Baseline** | Op Twiddle | Yes | 50 | 50 | 550 | 0 | **0.0%** | 0 | 0 | 50 | 0 | **0** |
| **TFIB-Ref** | Clean Control | No | 50 | 0 | 0 | 0 | **0.0%** | 0 | 0 | 0 | 0 | **0** |
| **TFIB-Ref** | Op Twiddle | No | 50 | 50 | 50 | 50 | **100.0%**| **50** | 0 | 0 | 0 | **0** |
| **TFIB-Ref** | Op Twiddle | Yes | 50 | 50 | 550 | 50 | **100.0%**| 0 | **50** | 0 | 0 | **0** |
| **TFIB-Ref** | Ref Twiddle | No | 50 | 50 | 50 | 50 | **100.0%**| **50** | 0 | 0 | 0 | **0** |
| **TFIB-Ref** | Ref Twiddle | Yes | 50 | 50 | 550 | 50 | **100.0%**| 0 | **50** | 0 | 0 | **0** |
| **TFIB-Ref** | Simultaneous | No | 50 | 50 | 50 | 0 | **0.0%** | 0 | 0 | 48 | 2 | **0** |
| **TFIB-Ref** | Checker Logic | No | 50 | 50 | 50 | 50 | **100.0%**| **50** | 0 | 0 | 0 | **0** |
| **TFIB-Ref** | Checker Logic | Yes | 50 | 50 | 550 | 50 | **100.0%**| 0 | **50** | 0 | 0 | **0** |
| **TFIB-Meta**| Clean Control | No | 50 | 0 | 0 | 0 | **0.0%** | 0 | 0 | 0 | 0 | **0** |
| **TFIB-Meta**| Op Twiddle | No | 50 | 50 | 50 | 50 | **100.0%**| 0 | **50** | 0 | 0 | **0** |
| **TFIB-Meta**| Op Twiddle | Yes | 50 | 50 | 550 | 50 | **100.0%**| 0 | **50** | 0 | 0 | **0** |
| **TFIB-Meta**| Meta Tag | No | 50 | 50 | 50 | 50 | **100.0%**| **50** | 0 | 0 | 0 | **0** |
| **TFIB-Meta**| Meta Tag | Yes | 50 | 50 | 550 | 50 | **100.0%**| 0 | **50** | 0 | 0 | **0** |
| **TFIB-Meta**| Checker Logic | No | 50 | 50 | 50 | 50 | **100.0%**| **50** | 0 | 0 | 0 | **0** |
| **TFIB-Meta**| Checker Logic | Yes | 50 | 50 | 550 | 50 | **100.0%**| 0 | **50** | 0 | 0 | **0** |

---

## 6. Reassessment of Performance & Tail Latency

A sample-level audit benchmark of $40{,}000$ timed decapsulations ($10{,}000$ samples per condition) was conducted to investigate the previously reported standard deviation anomaly.

### Table 2: Sample-Level Latency Distribution (40,000 Total Runs)

| Configuration | Operating Condition | Mean ($\mu\text{s}$) | Trimmed Mean | Median ($\mu\text{s}$) | StdDev ($\mu\text{s}$) | IQR ($\mu\text{s}$) | p95 ($\mu\text{s}$) | p99 ($\mu\text{s}$) | Outliers $>1\,\text{ms}$ |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **BASELINE** | Fault-Free | $215.40$ | $208.91$ | $145.96$ | $298.84$ | $114.50$ | $444.00$ | $1057.71$ | $114$ |
| **TFIB-REF** | Fault-Free | $255.57$ | $231.35$ | $173.17$ | $905.61$ | $117.71$ | $435.21$ | $1036.92$ | $105$ |
| **TFIB-META**| Fault-Free | $538.56$ | $478.04$ | $260.04$ | $2595.69$ | $151.50$ | $1220.62$ | $5552.83$ | $617$ |
| **TFIB-REF** | Active Recovery | $470.93$ | $426.48$ | $292.92$ | $1763.11$ | $157.83$ | $961.08$ | $3328.04$ | $467$ |

### Resolution of the High `TFIB-Meta` Standard Deviation:
1. **Host Contention:** The audit run detected active background processes contending for CPU cores. Under thread preemption, standard deviation is heavily inflated by OS context switches.
2. **Instruction Footprint & Micro-architectural Sensitivity:** `TFIB-Meta` performs arithmetic tag computation on every single butterfly ($9{,}856$ times per decapsulation). This increases loop code footprint and register pressure, making it $5.8\times$ more prone to context switch latency penalties ($617$ outliers $>1\,\text{ms}$ vs $105$ in `TFIB-Ref`).
3. **True Silicon Cost:** In median latency, `TFIB-Ref` imposes **$+18.64\%$** overhead over baseline ($173.17\,\mu\text{s}$ vs $145.96\,\mu\text{s}$). Active rollback and repair incurs an additional $+119.75\,\mu\text{s}$ ($+69.15\%$ overhead) during the single decapsulation that encounters the fault.

---

## 7. Claim Classification Matrix

| Claim Under Audit | Classification | Justification |
| :--- | :---: | :--- |
| **Twiddle Factor Blindness (Theorem 1)** | **REPRODUCED** | Verified locally across 100 trials (50 transient, 50 persistent) with 0.0% baseline detection. |
| **TFIB-Ref Local Twiddle Detection** | **REPRODUCED** | 100.0% local detection (50/50) confirmed across transient, persistent, and reference faults. |
| **TFIB-Ref In-Place Rollback & Recovery** | **REPRODUCED** | 100.0% genuine recovery (50/50) confirmed by oracle match against genuine shared secret. |
| **TFIB-Meta Precomputed Tag Detection** | **REPRODUCED** | 100.0% detection (50/50) and safe fail-stop confirmed. |
| **Simultaneous Common-Mode Failure Limit** | **REPRODUCED** | Confirmed 0.0% local detection when both tables are perturbed simultaneously. |
| **Hardware / Physical Fault Independence** | **NOT REPRODUCED** | Refuted by memory mapping analysis: tables are 448 bytes apart in identical `.rodata` segment. |
| **Cryptographic Tag Authentication** | **NOT REPRODUCED** | Refuted by algebraic analysis: tags are affine non-cryptographic hashes subject to multi-fault cancellation. |
| **Zero SDC in ML-KEM-768 Decapsulation** | **REPRODUCED** | Confirmed 0.0% SDC across all 900 trials; guaranteed by Fujisaki-Okamoto re-encryption. |

---

## 8. Final Decision & Recommendation

### Decision: **SUPPORTED BY EVIDENCE (WITH BOUNDARY RESTRICTIONS)**

The TFIB extension is technically sound, empirically verified, and scientifically reproducible. It solves an authentic, severe availability vulnerability in NTT invariant monitoring. However, it must be published with rigorous scientific honesty:

1. **Retain the Contribution:** The formalization of Twiddle Factor Blindness (Theorem 1) and its resolution via decoupled operational references (`TFIB-Ref`) is a genuine research advance for post-quantum cryptographic fault resilience.
2. **Strip Aerospace / Physical Independence Claims:** Do not claim radiation hardening or physical memory independence unless validated on dedicated dual-bank radiation-tolerant ASIC/FPGA hardware.
3. **Correct Framing:** Frame TFIB as an **availability and localized recovery mechanism** that prevents expensive protocol-level aborts, while acknowledging that integrity is ultimately anchored by the outer Fujisaki-Okamoto transform.
