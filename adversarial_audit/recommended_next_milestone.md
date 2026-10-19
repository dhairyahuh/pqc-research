# Recommended Next Research Milestone and Roadmap

**Auditor:** Independent Cryptographic Auditor & Implementation Research Team  
**Evaluation Scope:** Actionable Engineering Next Steps and Academic Defense  
**Deliverable Reference:** Phase 7 Final Reconciliation & Space Resilience Milestone  
**Date:** 2026-10-02  

---

## 1. Executive Assessment of Current State

The adversarial repository audit has established:
1. **The Core Cryptographic Implementation is Robust:** All NIST FIPS 203 & 204 Known Answer Tests pass across all parameter sets (ML-KEM-512/768/1024 and ML-DSA-44/65/87). No uncontained key leakage or Silent Data Corruption (SDC) was observed across over 2,500 evaluated injection trials.
2. **Local In-Tree Rollback is Fragile:** Microarchitectural in-place rollback relies on tautological retry verification, fails under corrupted constants and pre-latch memory, and introduces macro-architectural execution timing variance ($\Delta \approx 17\,\mu\text{s}$ to $275\,\mu\text{s}$).
3. **The Novel Path Forward is at the System / Protocol Level:** Rather than attempting to patch microarchitectural rollback on bare-metal registers, the defensible and novel research contribution lies in **coordinating computational fail-stop with protocol-level error control** for simulated space environments.

---

## 2. Recommended Next Milestone: "Fail-Stop Cryptography with Protocol-Level Coordination"

### Objective
Transition the research framework from fragile in-place arithmetic retry to an **authenticated, fail-stop cryptographic endpoint coordinated with an adaptive space communication channel**.

### Concrete Work Packages

#### Work Package 1: Clean-up and Elimination of Microarchitectural Defects (Test-Only)
- **Action 1.1:** Resolve the dead code `g_trusted_zetas[128]` by either deleting it or wiring it into an explicit table-integrity pre-flight verification routine.
- **Action 1.2:** Standardize the hook instrumentation ordering so that test hooks simulating memory upsets occur strictly *before* snapshot latching.
- **Action 1.3:** Replace the tautological retry verification with the Fail-Stop policy (Variant D), which immediately quenches decapsulation upon detecting any unrecoverable state anomaly.

#### Work Package 2: Space Communication Protocol Simulator Integration
- **Action 2.1:** Implement a discrete-event communications simulator (CCSDS Space Packet Protocol / authenticated transport framing).
- **Action 2.2:** Model joint fault processes:
  - *Endpoint Computational Faults:* Radiation SEU flux per orbital regime (LEO, GEO, Deep Space).
  - *Channel Faults:* Bit Error Rate (BER), burst noise, packet loss, and propagation delay ($10\,\text{ms}$ to $2.5\,\text{s}$).
- **Action 2.3:** Implement cross-layer coordination: When decapsulation fail-stop triggers due to an internal computational fault, the endpoint issues an authenticated retransmission request (ARQ) rather than risking an undetected key desynchronization.

#### Work Package 3: Cross-Platform Bare-Metal Validation
- **Action 3.1:** Deploy the fail-stop ML-KEM-768 decapsulation engine to an embedded platform (e.g. ARM Cortex-M4 via `qemu-system-arm` or RISC-V RV32IM via Spike).
- **Action 3.2:** Measure cycle-accurate latency and verify that fail-stop execution exhibits strictly bounded timing divergence.

---

## 3. Concrete Success Criteria

| Milestone Target | Evaluation Metric | Quantitative Threshold | Validation Method |
| :--- | :--- | :---: | :--- |
| **Cryptographic Correctness** | NIST FIPS 203 KAT vectors | **100% PASS** (0 failures) | `make test-kats` |
| **Fault Containment** | Silent Data Corruption (SDC) rate | **$0.0\%$** ($P_{\text{SDC}} < 0.15\%$ at 95% CI) | 2,000+ fault injection trials |
| **Constant-Time Safety** | Timing leakage between valid/invalid CT | **Cohen's $d < 0.05$** ($p > 0.05$) | Welch's t-test / dudect ($N=10,000$) |
| **Protocol Availability** | Session desynchronization under high SEU flux | **$< 0.01\%$** loss rate with ARQ | Discrete-event simulator ($10^5$ packets) |
| **Computational Overhead** | Latency increase relative to unmonitored baseline | **$< 20\%$** runtime overhead | Bare-metal cycle benchmarks |

---

## 4. Final Recommendation to Supervisor

Do not submit or claim novelty on "autonomous in-place rollback for NTT." That mechanism has proven fragile, contains algebraic verification tautologies, and is vulnerable to shared-constant corruptions established by Ravi et al. (TCHES 2023).

Instead, defend the project on:
> *"Fault-Resilient Post-Quantum Space Communications: Empirical Limits of In-Tree Arithmetic Monitoring and a Cross-Layer Coordination Framework for ML-KEM-768."*

This framing is academically defensible, supported by direct empirical data, mathematically sound, and directly addresses the unique challenges of space radiation resilience.
