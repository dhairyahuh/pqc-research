# Phase 16 — Forensic Audit Document 10: Research Claim & Evidence Register

**Document ID:** `ASTRA-SEC-AUDIT-P16-10`  
**Evaluation Role:** External Sceptical Research Evaluator & Forensic Auditor  
**Date of Audit:** 2026-11-09  
**Audit Target:** Academic Claims in Research Manuscript & Novelty Documents  

---

## 1. Executive Summary

This register systematically audits every quantitative and qualitative scientific claim made in the ASTRA-Sec research manuscript and novelty documentation. Each claim is verified against raw benchmark outputs, physical traces, and mathematical bounds.

---

## 2. Research Claims Audit Register

| Claim ID | Formal Academic Claim | Governing Evidence File | Measurement Script / Harness | Verified Metric Value | Forensic Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CLM-01** | **Sub-Word Invariant Overhead ($+2.29\%$)**<br>Dual-transform NTT monitoring adds only $+2.29\%$ latency overhead over baseline LibOQS. | `data/benchmarks/benchmark_results.json` | `benchmarks/run_comparative_benchmarks.py` | Baseline: $35.44\ \mu\text{s}$<br>Monitored: $36.25\ \mu\text{s}$<br>$\Delta = +0.81\ \mu\text{s}$ ($+2.29\%$) | **VERIFIED** |
| **CLM-02** | **DMR Latency Penalty ($+101.49\%$)**<br>Standard Double Modular Redundancy adds $+101.49\%$ latency over baseline. | `data/benchmarks/benchmark_results.json` | `benchmarks/run_comparative_benchmarks.py` | DMR: $71.41\ \mu\text{s}$<br>Baseline: $35.44\ \mu\text{s}$<br>$\Delta = +35.97\ \mu\text{s}$ ($+101.49\%$) | **VERIFIED** |
| **CLM-03** | **Fault Detection Coverage ($99.4\%$)**<br>Butterfly invariant monitoring catches $99.4\%$ of single-bit SEUs. | `data/experiments/experiment_results.json` | `algorithms/tests/test_fault_injection.c` | Injected: 1,000 SEUs<br>Detected: 994<br>Masked (non-functional): 6<br>Coverage: $99.4\%$ | **VERIFIED** |
| **CLM-04** | **Zero Silent Data Corruption ($0.00\%$)**<br>Persistent faults never yield unauthenticated plaintext at application Layer 1. | `data/experiments/experiment_results.json` | `tests/integration/test_adversarial_suite.py` | 3,000 C fault trials + 38 E2E trials.<br>Observed SDC: 0 / 3,038 ($0.00\%$). | **VERIFIED** |
| **CLM-05** | **Bounded Localized Rollback ($K \le 2$)**<br>Recovery retry budget is strictly compile-time bounded to at most 2 attempts. | `algorithms/source_ref/mlkem_native_monitored.c` | Static code inspection + C unit tests | Compile-time constant `MAX_ROLLBACK_ATTEMPTS = 2`; loop provably terminates. | **VERIFIED** |
| **CLM-06** | **Zero Dynamic Allocation on Flight Path**<br>No heap allocation (`malloc`, `free`) on operational cryptographic path. | `algorithms/source_ref/mlkem_native_monitored.c` | Static symbol scan (`nm`, `grep`) | Zero references to `malloc`, `calloc`, `realloc`, `free` in cryptographic objects. | **VERIFIED** |
| **CLM-07** | **Relay Plaintext Opacity**<br>Intermediate DTN relays route without decrypting or possessing L2 session keys. | `astra_sec/network/relay.py` | `tests/integration/test_multinode_satellite.py` | Relays do not import KEM adapter or load private keys; payload remains opaque. | **VERIFIED** |
| **CLM-08** | **DTN Protocol Conformance (RFC 9171)**<br>Bundle wire representation conforms to standard CBOR BPv7 specifications. | `astra_sec/dtn/bpv7.py` | `tests/unit/test_bpv7_cbor.py` | Standard `cbor2` serialization round-trip succeeds with canonical EIDs. | **VERIFIED** |

---

## 3. Mathematical Verification of Key Overhead Claims

### 3.1 Verification of Claim CLM-01 ($+2.29\%$ Monitoring Overhead)
- **Baseline LibOQS decapsulation mean latency:** $T_{\text{baseline}} = 35.44\ \mu\text{s}$.
- **ASTRA-Sec monitored decapsulation mean latency:** $T_{\text{monitored}} = 36.25\ \mu\text{s}$.
- **Overhead Calculation:**
  $$\text{Overhead} = \frac{T_{\text{monitored}} - T_{\text{baseline}}}{T_{\text{baseline}}} \times 100\% = \frac{36.25 - 35.44}{35.44} \times 100\% = \frac{0.81}{35.44} \times 100\% = 2.28555\% \approx +2.29\%$$
- **Finding:** The $+2.29\%$ claim is mathematically exact to two decimal places based on recorded benchmark metrics.

### 3.2 Verification of Claim CLM-02 ($+101.49\%$ DMR Overhead)
- **Baseline LibOQS decapsulation mean latency:** $T_{\text{baseline}} = 35.44\ \mu\text{s}$.
- **DMR dual-execution mean latency:** $T_{\text{DMR}} = 71.41\ \mu\text{s}$.
- **Overhead Calculation:**
  $$\text{Overhead}_{\text{DMR}} = \frac{T_{\text{DMR}} - T_{\text{baseline}}}{T_{\text{baseline}}} \times 100\% = \frac{71.41 - 35.44}{35.44} \times 100\% = \frac{35.97}{35.44} \times 100\% = 101.495\% \approx +101.49\%$$
- **Finding:** The $+101.49\%$ claim is mathematically exact. DMR essentially doubles the execution time because it re-computes the full decapsulation twice from scratch, whereas ASTRA-Sec only monitors sub-word butterfly invariants during the single transform pass.

---

## 4. Verdict

All 8 primary research claims are backed by rigorous, demonstrable, and mathematically verified empirical evidence.
