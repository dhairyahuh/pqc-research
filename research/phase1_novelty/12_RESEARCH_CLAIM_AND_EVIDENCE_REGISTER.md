# Phase 1 — Document 12: Research Claim and Evidence Register

**Document ID:** `ASTRA-SEC-PH1-DOC-12`  
**Research Directorate:** Multidisciplinary Academic Evaluation Team  
**Date:** November 2026  
**Status Levels:** `VERIFIED & PROVEN`, `THEORETICALLY ESTABLISHED`, `EMPIRICALLY PROJECTED`, `PROPOSED HYPOTHESIS`  

---

## 1. Research Claim and Evidence Traceability Matrix

| Claim ID | Formal Academic Claim | Evidence Source / Benchmark File | Technical Justification & Limits | Confidence Level | Status |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **CLM-01** | **Low-Overhead Invariant Monitoring ($+2.29\%$)**<br>Software-level sub-word butterfly checking in C99 adds $+2.29\%$ latency ($+0.81\ \mu\text{s}$) over baseline LibOQS. | `data/benchmarks/benchmark_results.json` | Baseline: $35.44\ \mu\text{s}$<br>Monitored: $36.25\ \mu\text{s}$<br>Measured over 1,000 iterations on native ARM64. Stack-allocated, constant-time Montgomery checks. | **VERY HIGH** | **VERIFIED & PROVEN** |
| **CLM-02** | **DMR Latency Penalty ($+101.49\%$)**<br>Standard Dual Modular Redundancy adds $+101.49\%$ latency over baseline. | `data/benchmarks/benchmark_results.json` | Baseline: $35.44\ \mu\text{s}$<br>DMR: $71.41\ \mu\text{s}$<br>Measured over 1,000 iterations. Validates that full duplicate execution doubles CPU runtime. | **VERY HIGH** | **VERIFIED & PROVEN** |
| **CLM-03** | **Single-Bit SEU Fault Coverage ($99.4\%$)**<br>Cooley-Tukey butterfly invariant catches $99.4\%$ of single-bit flips during NTT. | `data/experiments/experiment_results.json` | 994 / 1,000 faults detected in native C campaigns. The remaining $6$ flips occurred on unreferenced representation bits with zero impact on output in $\mathbb{Z}_{3329}$. | **HIGH** | **VERIFIED & PROVEN** |
| **CLM-04** | **Zero Silent Data Corruption ($0.00\%$)**<br>Persistent arithmetic faults never release corrupt plaintext to application Layer 1. | `algorithms/tests/test_fault_injection.c` | Enforced by constant-time fail-stop escalation to FIPS 203 Section 7.3 implicit rejection ($K \leftarrow \text{SHAKE256}(s \parallel c)$). 0 / 3,038 trials produced SDC. | **VERY HIGH** | **VERIFIED & PROVEN** |
| **CLM-05** | **Zero Dynamic Heap Allocation on Flight Path**<br>Cryptographic flight execution paths contain zero calls to `malloc`, `calloc`, or `free`. | Static symbol analysis (`nm -u`) of `libmlkem768_monitored.dylib` | All polynomial coefficient buffers are stack-allocated (`int16_t r[256]`) or statically bounded. Eliminates space heap fragmentation hazards. | **VERY HIGH** | **VERIFIED & PROVEN** |
| **CLM-06** | **Relay Payload Opacity**<br>Intermediate satellite relays route bundles without decrypting or possessing L2 session keys. | Source code audit of `astra_sec/network/relay.py` | Relays inspect Layer 5 BPv7 EIDs and CBOR headers only; do not import KEM adapter or private keys. Plaintext mutual information $\mathcal{I}(P; \text{State}_{\text{relay}}) = 0$. | **VERY HIGH** | **VERIFIED & PROVEN** |
| **CLM-07** | **RFC 9171 BPv7 Wire Conformance**<br>Bundle wire representation conforms to standard CBOR serialization rules. | `tests/unit/test_bpv7_cbor.py` | Verified round-trip encode/decode against independent `cbor2` parser. Primary and Canonical block formats conform to RFC 9171. | **HIGH** | **VERIFIED & PROVEN** |
| **CLM-08** | **Crash-Consistent Anti-Replay across Reboots**<br>Persisting sequence numbers to SQLite WAL before dispatch achieves zero duplicate executions. | `tests/integration/test_adversarial_suite.py` | Verified across `SIGKILL` power-cycle reboots. Replay cache persists in WAL database. | **HIGH** | **VERIFIED & PROVEN** |
| **CLM-09** | **Cross-Layer Telecommand Loss Reduction ($\ge 40\%$)**<br>Coordinating C rollback states with DTN custody reduces message loss under SEUs by $\ge 40\%$. | Proposed hypothesis $H_1$ (To be tested in Phase 2) | Mathematical queuing model predicts that suppressing false DTN drops during transient rollbacks preserves delivery without costly orbital retransmissions. | **MEDIUM-HIGH** | **EMPIRICALLY PROJECTED** |
| **CLM-10** | **At-Most-Once Execution Semantics**<br>5-phase transaction protocol formally guarantees at-most-once telecommand execution. | Formal automaton model in Document 07 | Proof mechanism binds destination WAL transaction ID into the signed ML-DSA-65 ACK. | **HIGH** | **THEORETICALLY ESTABLISHED** |

---

## 2. Evidence Boundary Disclaimers

In compliance with strict anti-hallucination standards:
1. **Radiation Environment Boundary:** All fault injection results are obtained via software bit-flipping in C registers, not physical heavy-ion beam tests.
2. **Space Deployment Boundary:** All multi-node experiments are executed across emulated local processes and network sockets, not orbital spacecraft hardware.
3. **NASA ION Boundary:** NASA/JPL ION-DTN integration is verified via configuration file synthesis (`.ionrc`, `.bprc`) and RFC 9171 wire compatibility, not native `ionadmin` C daemons running on macOS.
