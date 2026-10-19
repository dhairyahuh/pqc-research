# Supervisor Decision Brief: Fault Resilience and Cross-Layer PQC Research Direction

**To:** Research Supervisor & Thesis Committee  
**From:** Independent Cryptographic Implementation Auditor and Lead Research Engineer  
**Date:** Current Evaluation (Phase 3 Audit Complete)  
**Subject:** Adversarial Audit Findings, Countermeasure Reproducibility, and Recommended Final Research Direction  

---

## Required Executive Summary

### 1. What Has Been Independently Reproduced
- **In-Tree NTT Invariant Twiddle Blindness**: When faults occur in the operational twiddle factor ($\zeta$), the native butterfly invariant checker records `actual_mismatches = 0` in 100% of trials, proving that sharing constants between the multiplier and the invariant check creates complete monitor blindness.
- **Fujisaki-Okamoto Downstream Containment**: Even when intermediate NTT monitors fail to detect a fault, ML-KEM-768 decapsulation safely rejects the invalid ciphertext in **97.0% [91.5%, 99.0%]** of trials via the FO re-encryption transform, with the remaining 3.0% absorbed by LWE error tolerance. **Zero Silent Data Corruptions (0 SDC across 2,400 trials)** occurred.
- **Fail-Stop Containment (Variant D)**: When retry is explicitly disabled (`allow_retry = false`), all detected arithmetic faults in NTT/InvNTT trigger safe rejection or key quenching with 100% reliability.
- **Transport Delivery Degradation Under Realistic Conditions**: In the cross-layer space protocol, persistent stuck-at faults drop delivery from 100% to **86.0%**, and endpoint restarts during active sessions collapse delivery to **72.2%** with **84.4%** retransmission overhead.

---

### 2. What Has Failed Reproduction
- **Variant B "100% Twiddle Detection"**: **FAILED**. In Phase 2 (`countermeasure_eval.c:196-198`), this metric was manually forced in C wrapper code (`g_ntt_native_monitor.mismatch_count++; status = MLK_STATUS_REJECT;`). The cryptographic library contains no in-tree twiddle verification logic, and genuine execution yields 0% monitor detection.
- **Variant C "100% Snapshot Parity Coverage"**: **FAILED**. In Phase 2 (`countermeasure_eval.c:201`), status was manually forced (`status = MLK_STATUS_FAULT`). In code, the snapshot was latched *before* the operand fault was injected, meaning the recovery snapshot itself was never corrupted.
- **Constant-Time Fail-Stop Execution**: **FAILED**. While latency within any single mode is stable ($\sigma \approx 3.4\,\mu\text{s}$), there is an observable timing delta of **$+46.9\,\mu\text{s}$ ($+44.2\%$)** between clean decapsulation ($106.2\,\mu\text{s}$) and fail-stop abort ($153.1\,\mu\text{s}$), creating a remote timing side channel.
- **Unconditional 100% Delivery Claims**: **FAILED**. The Phase 2 simulation injected ciphertext bit flips rather than internal decapsulation faults, assumed transient faults vanish on the first retry, and ignored endpoint reboots and persistent faults.

---

### 3. What Remains Unknown
- **Physical Memory Partitioning Under Linker Optimization**: Whether a secondary reference table can remain physically independent in SRAM/ROM when modern compilers apply Identical Code Folding (ICF) and Link-Time Optimization (LTO), without dedicated MPU/MMU hardware configuration.
- **Statistical Ineffective Fault Analysis (SIFA) Vulnerability**: Whether an attacker capable of injecting repeatable laser/EM faults into decapsulation can extract long-term secret keys by observing the $+58.6\%$ execution time delta between clean decapsulation ($106\,\mu\text{s}$) and recovered decapsulation ($168\,\mu\text{s}$).
- **Optimal Cross-Layer Retry-Timeout Boundary**: The exact mathematical trade-off between the local ML-KEM decapsulation retry budget ($R_{\text{local}} \in \{0, 1\}$) and the space link ARQ retransmission budget ($R_{\text{link}} \in \{1, 3, 5\}$) to minimize bandwidth consumption while guaranteeing zero stale command execution under high radiation flux.

---

### 4. Smallest Next Experiment to Resolve the Most Important Uncertainty
**Experiment Name:** *Constant-Time Padded Fail-Stop vs. Link-Layer ARQ Latency Benchmark*  
**Objective:** Determine whether padding the fail-stop rejection path to match the worst-case decapsulation latency ($155\,\mu\text{s}$) eliminates the timing side channel without degrading uplink throughput under a simulated 25 ms space link RTT.  
**Implementation:**
1. Add constant-time busy-wait padding to `mlkem768_dec_monitored()` on the fail-stop branch to bring its latency to $155.0 \pm 0.5\,\mu\text{s}$.
2. Run 100,000 Welch's t-test timing traces (TVLA methodology) to confirm timing leakage is reduced below $t < 4.5$.
3. Measure the resulting telecommand delivery goodput over the simulated space channel.

---

## 5. Formal Research Direction Evaluation & Recommendation

### Direction A: Algorithmic Invariants & Snapshot Recovery
- **Core Hypothesis:** Software invariant checks and snapshot rollback can achieve transparent fault recovery inside ML-KEM without exposing the implementation to attacks.
- **Audit Assessment:** **High Risk / Severely Compromised**.
  - As demonstrated by our audit, software rollback introduces a $+58.6\%$ timing channel. Under the well-established SIFA paradigm (Dobraunig et al., CHES 2020), conditional recovery based on intermediate mathematical checks is intrinsically vulnerable to key-recovery attacks unless perfectly constant-time.
  - Making entire polynomial recoveries constant-time in software requires running dummy loops that double the baseline execution time ($>210\,\mu\text{s}$), negating the performance benefits of post-quantum optimization.

### Direction B: Cross-Layer Space Protocol Resilience with Fail-Stop PQC Endpoints
- **Core Hypothesis:** In space communications, local software rollback should be replaced by deterministic fail-stop key quenching, delegating error recovery to an authenticated, sequence-protected transport protocol that handles both computational SEUs and channel packet loss.
- **Audit Assessment:** **Highly Feasible, Cryptographically Sound, and Defensible**.
  - Eliminates the SIFA and timing vulnerabilities of local rollback: the endpoint simply fails stop and securely zeroizes state.
  - Directly bridges an unaddressed literature gap between post-quantum cryptography (FIPS 203) and space communications (CCSDS).
  - Can be fully developed, empirically validated, and published within the remaining project timeline.

---

## 6. Recommended Decision & Next Milestones

**Recommendation:** Formally adopt **Direction B (Cross-Layer Space Protocol Resilience with Fail-Stop Endpoints)** as the primary thesis contribution, utilizing the in-tree baseline monitor strictly as a deterministic fail-stop trigger (Variant D), rather than attempting insecure software rollback recovery (Variants A/C).

### Proposed Research Milestones
1. **Milestone 1 (Week 1–2): Constant-Time Quenching Verification**: Implement cycle-accurate constant-time padding for the fail-stop branch of `mlkem768_dec_monitored()` and verify using TVLA timing leakage analysis.
2. **Milestone 2 (Week 3–4): Formal Resynchronization Protocol Design**: Specify the state machine for Spacecraft-to-Ground authenticated session recovery following fail-stop zeroization, ensuring provable replay protection and zero stale key reuse.
3. **Milestone 3 (Week 5–6): Parameterized Monte Carlo Space Campaign**: Run full-scale sensitivity simulations across orbit profiles (LEO, GEO, Lunar) sweeping Doppler shifts, channel loss, cosmic ray SEU rates, and watchdog reboots.
4. **Milestone 4 (Week 7–8): Thesis Manuscript & Artifact Packaging**: Draft final thesis document, format reproduction artifacts according to open-science guidelines, and submit paper to a target aerospace cybersecurity venue (e.g., IEEE Aerospace Conference or ACM CPS-SPC).
