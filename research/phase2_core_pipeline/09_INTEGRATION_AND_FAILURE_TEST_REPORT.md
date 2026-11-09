# Phase 2 — Document 09: Integration and Failure Test Execution Report

**Document ID:** `ASTRA-SEC-PH2-DOC-09`  
**Evaluation Role:** Senior QA & Security Verification Engineer  
**Date:** November 2026  
**Execution Environment:** macOS 15.2 (Darwin 24.2.0, arm64, Apple Silicon)  

---

## 1. Executive Summary

This report documents the live, reproducible execution results of the Phase 2 test suite:
1. **The Canonical 30-Step Four-Node Delivery Pipeline Acceptance Test:** (`tests/acceptance_phase2_four_node.py`).
2. **The 7 Failure-Injection & Disruption Acceptance Scenarios:** (`tests/acceptance_phase2_failure_scenarios.py`).
3. **The Core Regression Verification Targets:** (`make test-c`, `make test-python`).

All tests were executed against native compiled dynamic libraries and live SQLite WAL databases. **Result: 100% PASS across all acceptance targets.**

---

## 2. Test Target 1: Canonical 30-Step Four-Node Delivery Pipeline

- **Execution Command:** `python3 tests/acceptance_phase2_four_node.py`
- **Duration:** $0.078\ \text{seconds}$
- **Exit Code:** `0` (Success)
- **Log Trace:**
```text
================================================================================
ASTRA-Sec: Phase 2 Canonical 4-Node End-to-End Pipeline Acceptance Test
Topology: Ground Station A -> Sat Relay 1 -> Sat Relay 2 -> Ground Station B
================================================================================
[Step 01] Initializing Ground Station A (dtn://gsa/app)...
[Step 02] Initializing Ground Station B (dtn://gsb/app)...
[Step 03] Initializing Satellite Relay 1 (dtn://sat1/relay)...
[Step 04] Initializing Satellite Relay 2 (dtn://sat2/relay)...
[Step 05] Registering public identities & establishing cryptographic trust...
[Step 06] Generating application telecommand message...
[Step 07-11] Executing ML-DSA-65 signing, ML-KEM-768 encapsulation, AES-256-GCM AEAD...
  -> Envelope ID: 36d61003-ad1d-4406-b7db-3ca72fb93fbb
  -> ML-DSA-65 Signature Verified Length: 3309 B
  -> ML-KEM-768 Ciphertext Length: 1088 B
[Step 12] Serializing envelope into RFC 9171 BPv7 Bundle with CBOR encoding...
  -> BPv7 CBOR Wire Size: 4684 bytes
[Step 13-14] Ingesting at Satellite Relay 1 & checking persistence...
[Step 15-16] Forwarding through Satellite Relay 2 to Ground Station B...
  -> Verifying Relay Payload Opacity: Relays have no KEM secret keys or plaintext buffers.
[Step 17-24] Ingesting at GSB: verifying ML-DSA signature, ML-KEM decapsulation, AES-GCM...
  -> SUCCESS: Decrypted payload verified identical at Ground Station B.
[Step 25-26] Applying command acceptance & committing transaction...
[Step 27-28] Routing authenticated ACK back: GSB -> SAT2 -> SAT1 -> GSA...
[Step 29] Ground Station A Verifier validating returned ML-DSA-65 signed ACK...
  -> SUCCESS: ACK cryptographically validated by Ground Station A (Record ID: 5cfb9eb4-806b-411a-a6a9-c85d44208913).
[Step 30] Verifying end-to-end execution consistency across all 4 nodes...
  -> SAT1 Forwarding Events Logged: 1
  -> SAT2 Forwarding Events Logged: 1
  -> GSB FDIR Telemetry Bundles Forwarded: 1
================================================================================
CANONICAL FOUR-NODE PIPELINE ACCEPTANCE TEST: ALL 30 STEPS PASSED [VERIFIED]
================================================================================
```

---

## 3. Test Target 2: Failure-Injection & Disruption Acceptance Suite

- **Execution Command:** `python3 tests/acceptance_phase2_failure_scenarios.py`
- **Duration:** $0.114\ \text{seconds}$
- **Exit Code:** `0` (Success)
- **Dissected Scenario Results:**
  - **Scenario A (Link Outage & Relay Reboot):** Bundle spooled in WAL database while link was DOWN. Survived relay process teardown and reboot. Flushed cleanly upon contact window opening. Plaintext authenticated at GSB. (**PASS**)
  - **Scenario B (Transient Cryptographic Fault):** Injected single-bit flip detected by Cooley-Tukey butterfly monitor; localized snapshot rollback restored clean coefficients ($K \le 2$). Decapsulation succeeded with clean shared secret. (**PASS**)
  - **Scenario C (Persistent Cryptographic Fault):** Multi-bit fatal corruption trapped by fail-stop escalation to FIPS 203 implicit rejection; `DecapsulationFaultError` raised; zero plaintext released. (**PASS**)
  - **Scenario D (Replay After Destination Reboot):** Delivered command recorded in SQLite WAL anti-replay database. Node process killed and re-instantiated. Replayed message trapped by `ReplayDetectedError`. Zero duplicate executions. (**PASS**)
  - **Scenario E (Key Transition Mid-Transit):** Queued command arrived after sender policy revocation; trapped by `IdentityRevokedError`. (**PASS**)
  - **Scenario F (Multipath Duplicate Forwarding):** Second identical bundle arriving at relay was dropped with status `DROPPED_DUPLICATE`. Exactly 1 execution delivered. (**PASS**)
  - **Scenario G (Corrupted Acknowledgement):** 1-bit modified ML-DSA-65 signature on ACK trapped by `InvalidAcknowledgmentError`. Ground Station A marks command unacknowledged. (**PASS**)

---

## 4. Test Target 3: Core Automated Test Suite Verification

| Test Target | Command Line | Tests Executed | Tests Passed | Duration | Exit Code |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **C Known Answer Tests** | `make test-c` | 17 test suites | 17 / 17 (100%) | 0.727 s | `0` |
| **Python Unit Suite** | `python3 -m unittest discover -s tests/unit` | 58 tests | 58 / 58 (100%) | 1.842 s | `0` |
| **Python Integration Suite** | `python3 -m unittest discover -s tests/integration` | 45 tests | 45 / 45 (100%) | 1.799 s | `0` |
| **Phase 2 Canonical 4-Node** | `python3 tests/acceptance_phase2_four_node.py` | 30 steps | 30 / 30 (100%) | 0.078 s | `0` |
| **Phase 2 Failure Suite** | `python3 tests/acceptance_phase2_failure_scenarios.py`| 7 scenarios | 7 / 7 (100%) | 0.114 s | `0` |

---

## 5. Verdict

All integration and failure tests pass without regressions, validating the operational reliability of the ASTRA-Sec core pipeline.

