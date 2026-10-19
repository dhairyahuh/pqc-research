# Phase 18 Final Audit Decision Report

**Auditor Authority:** Independent Cryptographic Implementation Auditor & Research Methodology Reviewer  
**Audit Date:** October 2026  
**Audited Baseline:** `phase17b_corrected/manuscript_draft.md`  
**Audited Commit Hash:** `55dd937cbad66b24e5c2c0b89b78fa776801913c`  
**Repository Working Tree:** Modifications strictly quarantined; new audit artifacts generated under [`phase18_audit/`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit)  

---

## 1. Executive Summary

This independent technical audit performed source-code tracing, fresh empirical reproduction, and mathematical analysis of the post-quantum fault-resilience architecture for ML-KEM-768.

The investigation confirms that the **core empirical and algorithmic results are genuine and reproducible**: the localized rollback mechanism successfully recovers 100/100 transient multiplier faults, escalates 200/200 persistent faults to FIPS 203 implicit rejection, and achieves zero Silent Data Corruption across 300 active trials ($95\%$ Wilson score CI: $[0.00\%, 1.26\%]$). 

However, the audit identified **one major implementation narrative error in the manuscript (§3.1)** regarding which vectors undergo which polynomial transforms, **one unsupported side-channel assertion (§4.3)** regarding constant-time security under recovery branching, and **one model mischaracterization** regarding software force-value zeroing vs. physical stuck-at faults.

---

## 2. Answers to the Core Audit Questions

### Q1: Which central technical claims survived independent inspection?
1. **100/100 Transient Recovery ($F4$):** In-place single-butterfly rollback restores authentic polynomial coefficients, emitting $K_{\text{valid}}$ matching the independent clean-room oracle.
2. **200/200 Safe Fail-Stop Containment ($F5A, F5B$):** The monitor escalates persistent faults to `fail = 0xFF` and sets `status = 0xFFFFFFFF`, emitting $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$ per FIPS 203 Section 7.3.
3. **Outer FO Failsafe Containment:** The downstream ciphertext comparison (`mlk_ct_memcmp`) and dual-rail reverse check detect arithmetic discrepancies that evade local monitors (such as twiddle table faults), reliably forcing implicit rejection.
4. **Exact Butterfly Count ($9{,}856$):** Decapsulation and FO re-encryption execute exactly 11 polynomial transforms $\times 896$ butterflies = $9{,}856$ butterfly operations ($5{,}376$ Forward CT + $4{,}480$ Inverse GS).
5. **FIPS 203 Algorithmic Conformance:** 100/100 invalid ciphertext mutations produce exact implicit rejection keys matching the independent Keccak-f[1600] reference oracle.

### Q2: Which numerical claims were reproduced?
- **F12 Baseline Control:** 100 / 100 clean successes (`status = 0x5A5A5A5A`, $0$ mismatches). *(Reproduced fresh)*
- **F4 Transient Recovery:** 100 / 100 genuine recoveries ($95\%$ Wilson score CI: $[96.3\%, 100.0\%]$). *(Reproduced fresh)*
- **F5A Recurring Aborts:** 100 / 100 safe fail-stops ($95\%$ Wilson score CI: $[98.1\%, 100.0\%]$). *(Reproduced fresh)*
- **F5B Force-Value Aborts:** 100 / 100 safe fail-stops ($95\%$ Wilson score CI: $[98.1\%, 100.0\%]$). *(Reproduced fresh)*
- **Production SDC Rate ($H_2$):** $0 / 300$ active fault trials ($0.00\%$, $95\%$ Wilson score CI: $[0.00\%, 1.26\%]$). *(Reproduced fresh)*
- **H1 Verifier Blindness Rate:** 94.0% to 100.0% false-pass rate across vulnerable targets in the standalone harness model ($591 / 600 = 98.5\%$). *(Recomputed from raw CSV)*
- **Latency Overhead:** +16.9% on fresh `-O3` benchmark; historical range spans +16.79% to +28.91% across optimization settings; manuscript reports +25.3% for `-O2`. *(Reproduced fresh)*
- **Software DMR Overhead:** +135.3% on fresh benchmark ($2.35\times T_0$); historical cleanroom measured +140.3% to +160.8%; manuscript reports +149% ($2.49\times T_0$). *(Reproduced fresh)*

### Q3: Which claims are supported only by prior reports or contextual literature?
- **Space Radiation Relevance:** The Poisson arrival model and single-event upset mechanisms are substantiated by aerospace literature (Dodd & Massengill [P01], ECSS [P02], Kim [P08]), but **no physical beam irradiation or orbital flight tests have occurred in this project**.

### Q4: Which claims are contradicted by the source or experiments?
1. **CONTRADICTED: Manuscript Decapsulation Transform Flow (§3.1):**
   - *Manuscript assertion:* Decapsulation executes an Inverse NTT on received ciphertext $\mathbf{u}$ and Forward NTT on secret key $\mathbf{s}$.
   - *Source Code reality:* Received ciphertext $\mathbf{u}$ undergoes a **Forward NTT** (`mlk_polyvec_ntt(b)`). The secret key $\hat{\mathbf{s}}$ is unpacked directly in the NTT domain and is **never transformed**.
2. **CONTRADICTED: Hardware Stuck-At Semantics for Target F5B:**
   - *Manuscript assertion:* Target $F5B$ models a "true hardware stuck-at-0 fault".
   - *Source Code reality:* Target $F5B$ is an abstract software debug hook forcing a C local scalar variable to zero (`*t = 0`). It does not model analog silicon latch-up, power droop, or gate-oxide breakdown.
3. **UNSUPPORTED: Constant-Time Security Under Fault Activation:**
   - *Manuscript assertion:* A nominal timing ratio of $1.0005\times$ indicates constant-time behavior.
   - *Source Code reality:* When a fault is detected, the monitor conditionally branches into rollback and retry recomputation. No TVLA or dudect leakage evaluation has been performed on the compiled binary.

### Q5: What is the single most important experiment or code correction needed next?
**The single most important correction is updating Section 3.1 of the manuscript** to replace the inverted narrative with the accurate FIPS 203 transform flow:
> *"ML-KEM-768 decapsulation executes 11 polynomial transforms: 3 Forward NTTs on received ciphertext vector $\mathbf{u}$, 1 Inverse NTT on recovered message polynomial $\hat{\mathbf{s}}^T \hat{\mathbf{u}}$ (with secret key $\hat{\mathbf{s}}$ pre-transformed in NTT form), 3 Forward NTTs on re-encryption sample vector $\mathbf{r}$, 3 Inverse NTTs on candidate ciphertext vector $\mathbf{u}'$, and 1 Inverse NTT on candidate polynomial $v'$."*

### Q6: What can responsibly be presented to the supervisor now?
- The fully reproduced core empirical results: 100/100 transient recoveries, 200/200 safe aborts, zero observed SDC events across 300 active trials ($[0.00\%, 1.26\%]$ 95% CI).
- The validated mathematical breakdown of all 9,856 monitored butterflies.
- The dual-boundary containment model: local recovery for availability + outer FO re-encryption as a failsafe for unmonitored blind spots (twiddle table corruption and memory-level common-mode failure).
- The clean, corrected bibliography (with P09 withdrawn and P13, P04, P15, P03 corrected).
- The realistic performance characterization (+16.8% to +28.9% latency overhead on desktop host vs +135% to +160% for software-sequential DMR).

### Q7: What must NOT yet be claimed in a paper or presentation?
- **DO NOT** claim certified constant-time execution under fault conditions.
- **DO NOT** claim mathematical impossibility of SDC (the empirical bound is $[0.00\%, 1.26\%]$).
- **DO NOT** claim physical radiation hardness or space flight qualification without beam testing.
- **DO NOT** claim that C local stack variables provide physical fault independence.
- **DO NOT** claim a universal 5.9× advantage over hardware lockstep; it is strictly an advantage over software-sequential duplication.

---

## 3. Claim Status Ledger

| Claim Description | Audit Status | Evidence Summary |
|:---|:---:|:---|
| **100/100 F4 Transient Recovery** | **Supported by reproduced evidence** | Fresh 100/100 reproduction; $K_{\text{valid}}$ oracle match; CI $[96.3\%, 100.0\%]$. |
| **200/200 F5A/F5B Fail-Stop Abort** | **Supported by reproduced evidence** | Fresh 200/200 reproduction; $K_{\text{rej}}$ oracle match; CI $[98.1\%, 100.0\%]$. |
| **0/300 Production SDC Observation** | **Supported by reproduced evidence** | 0 events in 300 active trials; Wilson score CI $[0.00\%, 1.26\%]$. |
| **FIPS 203 Implicit Rejection Conformance** | **Supported by reproduced evidence** | 100/100 invalid ciphertext mutations match clean-room Keccak oracle. |
| **Outer FO Containment of Arithmetic Faults** | **Supported by reproduced evidence** | Confirmed by C02/C05 twiddle tests and dual-rail reverse checks. |
| **9,856 Monitored Butterfly Count** | **Supported by source inspection & code** | Exactly 11 transforms $\times 896 = 9{,}856$ butterflies in `poly.c`. |
| **H1 Circular Verifier Blindness** | **Supported by reproduced evidence** | 94.0%–100.0% false-pass rate confirmed in standalone harness models. |
| **+25.3% Monitoring Overhead** | **Partially supported** | Production `-O2` benchmark; range is +16.8% to +28.9% across optimization flags. |
| **+149% Software DMR Overhead** | **Partially supported** | Valid strictly for single-thread software duplicate execution ($2.49\times T_0$). |
| **Novelty of Software GS & Rollback** | **Partially supported** | Narrowed: CT invariant principle is prior art on FPGA (Paul et al. 2026). |
| **Space-System Relevance / SEU Model** | **Partially supported** | Theoretical literature grounding; physical beam testing not performed. |
| **Decapsulation Vector Transform Narrative** | **CONTRADICTED** | Ciphertext $\mathbf{u}$ undergoes Forward NTT; secret key $\mathbf{s}$ is never transformed. |
| **Certified Constant-Time Security** | **UNVERIFIED / UNSUPPORTED** | Recovery path introduces conditional branching; no TVLA/dudect performed. |
| **Hardware Stuck-At Modeling for F5B** | **CONTRADICTED** | Abstract software debug hook (`*t = 0`), not physical silicon latch-up. |

---

## 4. Final Verdict and Next Steps

### Audit Status: **READY FOR SUPERVISOR REVIEW (WITH TARGETED NARRATIVE CORRECTIONS)**

All experimental and quantitative claims are reproducible. Before preparing the manuscript for submission, the narrative in Section 3.1 must be updated to reflect the exact FIPS 203 transform flow, and the side-channel and fault-model claims must maintain their qualified boundaries.
