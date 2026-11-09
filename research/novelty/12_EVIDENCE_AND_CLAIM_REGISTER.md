# ASTRA-Sec: Evidence & Claim Register

**Auditors:** Senior Academic Research Team  
**Purpose:** Formal registry classifying every system claim into PROVEN, QUALIFIED, or DISALLOWED, linked directly to source files and test evidence.

---

## 1. Proven Claims (Supported by Direct Execution & Tests)

| Claim ID | Claim Statement | Source Evidence File | Test Verification Case | Status |
| :--- | :--- | :--- | :--- | :---: |
| **CLM-01** | **Monitored Decapsulation Overhead**<br>ML-KEM-768 invariant monitoring adds $+2.29\%$ latency ($+0.81\ \mu\text{s}$) over LibOQS baseline. | `data/benchmarks/benchmark_results.json` | `benchmarks/run_comparative_benchmarks.py:benchmark_mlkem` | **PROVEN** |
| **CLM-02** | **DMR Comparative Advantage**<br>Invariant monitoring is $50.4\%$ faster than Dual Modular Redundancy ($36.25\ \mu\text{s}$ vs $73.04\ \mu\text{s}$). | `data/benchmarks/benchmark_results.json` | `benchmarks/run_comparative_benchmarks.py:benchmark_dmr` | **PROVEN** |
| **CLM-03** | **End-to-End Multi-Hop Latency**<br>4-node space communication (GSA $\to$ SAT1 $\to$ SAT2 $\to$ GSB) completes in $1.187\ \text{ms}$ (P50: $1.128\ \text{ms}$). | `data/benchmarks/benchmark_results.json` | `benchmarks/run_comparative_benchmarks.py:benchmark_multihop` | **PROVEN** |
| **CLM-04** | **Zero Relay Decryption**<br>Intermediate satellites inspect routing metadata only; ciphertext remains encrypted under AES-256-GCM. | `astra_sec/network/relay.py:100` | `tests/integration/test_multinode_satellite.py:test_07_relay_payload_tampering_detected` | **PROVEN** |
| **CLM-05** | **Transient Fault Rollback**<br>Single-event twiddle bit-flips are detected and recovered locally via snapshot rollback ($K=1$). | `src/astra_crypto_bridge.c:98` | `tests/integration/test_fault_resilience.py:test_02_transient_fault_recovery_in_flight` | **PROVEN** |
| **CLM-06** | **Zero SDC under Fault Injection**<br>Zero Silent Data Corruption events observed across evaluated adversarial trials; persistent faults escalate to implicit rejection. | `data/experiments/trials/campaign_results.jsonl` | `tests/integration/test_fault_resilience.py:test_03_persistent_fault_fail_stop_suppression` | **PROVEN** |
| **CLM-07** | **Persistent Replay Immunity**<br>Replayed command UUIDs are blocked following destination node process reboots. | `astra_sec/security/replay.py:82` | `tests/integration/test_security_continuity.py:test_08_restart_after_command_acceptance` | **PROVEN** |
| **CLM-08** | **Disruption Spool Survival**<br>Spooled bundles survive satellite relay reboots and flush automatically upon link restoration. | `astra_sec/network/spool.py:63` | `tests/integration/test_multinode_satellite.py:test_02_relay_restart_with_persistent_spool` | **PROVEN** |
| **CLM-09** | **NIST KAT Vector Conformity**<br>Native ML-KEM and ML-DSA implementations produce identical outputs to official NIST FIPS 203/204 test vectors. | `tests/test_fips_kats.c` | `./bin/test_fips_kats` (6/6 passing vectors) | **PROVEN** |

---

## 2. Qualified Claims (Must Include Explicit Academic Disclaimers)

| Claim ID | Claim Statement | Mandatory Academic Qualification |
| :--- | :--- | :--- |
| **QUAL-01** | *"Zero SDC Guarantee"* | Must be phrased as: *"Zero SDC was observed across 3,000 algorithmic fault trials and 38 protocol integration trials under the tested single-event upset model. This does not constitute a formal mathematical proof of zero failure under arbitrary continuous multi-bit damage."* |
| **QUAL-02** | *"DTN BPv7 Compliance"* | Must be phrased as: *"ASTRA-Sec implements an independent, specification-compliant pure-Python RFC 9171 BPv7 engine with RFC 8949 CBOR wire formatting. While it generates configuration scripts for NASA/JPL ION-DTN, it does not execute against live `ionadmin` C daemons on macOS workstations."* |
| **QUAL-03** | *"Constant-Time Execution"* | Must be phrased as: *"The C cryptographic arithmetic avoids secret-dependent branching and lookup tables. However, localized snapshot rollback introduces bounded variable cycle counts ($K \le 2$) upon detecting faults, which must be accounted for in physical fault-attack threat models."* |

---

## 3. Disallowed Claims (Strictly Prohibited from Papers & Reports)

| Claim ID | Disallowed Claim | Reason for Prohibition |
| :--- | :--- | :--- |
| **DIS-01** | *"FIPS 203 / FIPS 204 Certified"* | The implementation targets the FIPS standards, but has not completed formal NIST Cryptographic Module Validation Program (CMVP) certification. |
| **DIS-02** | *"Physical Space Radiation Validated"* | Experiments used software fault injection (bit-flips and twiddle mutations in C) to simulate ionizing radiation; no cyclotron or space beam experiments were conducted. |
| **DIS-03** | *"Native NASA ION Daemon Active on macOS"* | The native ION C binary (`ionadmin`) is uninstalled; transport is handled by ASTRA-Sec's internal Python BPv7 engine. |
| **DIS-04** | *"Universal Zero SDC under Arbitrary Faults"* | Multi-bit concurrent corruption affecting both the operational twiddle table and the reference table simultaneously (common-mode failure) could theoretically evade Strategy 1 detection. |
| **DIS-05** | *"Signal Per-Message Double Ratchet Fully Implemented"* | Key updates currently operate on an epoch rotation schedule rather than a per-message ephemeral KEM exchange. |
