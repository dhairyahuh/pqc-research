# ASTRA-Sec: Security & Adversarial Vulnerability Testing Report

**Auditor:** Independent Security Reviewer & Red Team Auditor  
**Threat Model Reference:** `docs/threat-model.md`  
**Scope:** 16 Comprehensive Attack & Failure Scenarios across Cryptographic, Network, and Persistence Layers

---

## 1. Adversarial Test Matrix (16 Scenarios)

| # | Attack / Failure Model | Test Implementation File | Execution Command | Expected Outcome | Actual Outcome | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Ciphertext Modification** | `tests/integration/test_pqc_messaging.py` | `python3 -m unittest tests/integration/test_pqc_messaging.py -k test_02_modified_ciphertext` | Destination AEAD decryption fails; tag mismatch before plaintext release. | `AeadAuthenticationError` raised; payload suppressed. | **PASS** |
| **2** | **Invalid ML-DSA Signature** | `tests/integration/test_pqc_messaging.py` | `python3 -m unittest tests/integration/test_pqc_messaging.py -k test_04_invalid_signature` | Sender verification fails; envelope discarded. | `InvalidSignatureError` raised; message dropped. | **PASS** |
| **3** | **Unauthorized Sender** | `tests/integration/test_pqc_messaging.py` | `python3 -m unittest tests/integration/test_pqc_messaging.py -k test_05_unknown_sender` | Originator not found in `PublicKeyTrustStore`; rejected. | `UntrustedPeerError` raised. | **PASS** |
| **4** | **Replay of Accepted Command** | `tests/integration/test_security_continuity.py` | `python3 -m unittest tests/integration/test_security_continuity.py -k test_01_replay_of_accepted_command_rejected` | Duplicate envelope UUID detected; command blocked. | `ReplayDetectedError` raised. | **PASS** |
| **5** | **Duplicate Bundle at Relay** | `tests/integration/test_security_continuity.py` | `python3 -m unittest tests/integration/test_security_continuity.py -k test_02_duplicate_bundle_suppressed_at_relay` | Intermediate relay drops duplicate without forwarding. | Forwarding event `DROPPED_DUPLICATE` recorded; duplicate suppressed. | **PASS** |
| **6** | **Expired Command (TTL)** | `tests/integration/test_security_continuity.py` | `python3 -m unittest tests/integration/test_security_continuity.py -k test_04_expired_command_rejected` | Envelope older than TTL window rejected as stale. | `MessageExpiredError` raised; command aborted. | **PASS** |
| **7** | **Incorrect Recipient EID** | `tests/integration/test_pqc_messaging.py` | `python3 -m unittest tests/integration/test_pqc_messaging.py -k test_06_incorrect_recipient` | Envelope addressed to third-party rejected by node. | `MismatchedRecipientError` raised. | **PASS** |
| **8** | **Malicious Relay Tampering** | `tests/integration/test_multinode_satellite.py` | `python3 -m unittest tests/integration/test_multinode_satellite.py -k test_07_relay_payload_tampering_detected` | Corrupted relay alters ciphertext bytes in flight; caught at destination. | AEAD tag validation fails at destination; zero plaintext leakage. | **PASS** |
| **9** | **Relay Process Restart** | `tests/integration/test_multinode_satellite.py` | `python3 -m unittest tests/integration/test_multinode_satellite.py -k test_02_relay_restart_with_persistent_spool` | Relay node reboots while bundles are queued in SQLite WAL spool. | Bundles restored from disk upon reboot; forwarding resumes. | **PASS** |
| **10** | **Network Link Blackout** | `tests/integration/test_dtn_disruption.py` | `python3 -m unittest tests/integration/test_dtn_disruption.py -k test_02_network_unavailable_spooled` | Inter-satellite link forced DOWN; bundles held in spool. | Bundles held in `WAITING_CONTACT` state without packet drop. | **PASS** |
| **11** | **Delayed Contact Reconnection** | `tests/integration/test_dtn_disruption.py` | `python3 -m unittest tests/integration/test_dtn_disruption.py -k test_09_valid_message_delivered_after_reconnection` | Link restored after simulated occultation; spooled bundles forwarded. | Spool flushed in FIFO order; recipient verifies and decrypts. | **PASS** |
| **12** | **Transient NTT Fault** | `tests/integration/test_fault_resilience.py` | `python3 -m unittest tests/integration/test_fault_resilience.py -k test_02_transient_fault_recovery_in_flight` | Single-event upset injected during decapsulation NTT. | Local rollback succeeds ($K=1$); shared secret recovered. | **PASS** |
| **13** | **Checker / TFIB Fault** | `tests/unit/test_mlkem_monitored.py` | `python3 -m unittest tests/unit/test_mlkem_monitored.py -k test_05_tfib_ref_resilience` | Twiddle factor mutated; caught via dual-reference table. | TFIB mismatch detected; twiddle fault counter incremented. | **PASS** |
| **14** | **Malformed Key Configuration** | `tests/integration/test_pqc_messaging.py` | `python3 -m unittest tests/integration/test_pqc_messaging.py -k test_11_invalid_key_configuration` | Public keys with truncated byte lengths submitted to trust store. | `ValueError` raised during Pydantic schema validation. | **PASS** |
| **15** | **Corrupted Persistent State** | `tests/integration/test_security_continuity.py` | `python3 -m unittest tests/integration/test_security_continuity.py -k test_09_corrupted_persistent_security_state_fail_stop` | Persistent security database tampered or corrupted. | Fail-stop lockout engaged; node refuses to start or process messages. | **PASS** |
| **16** | **Forged Cryptographic ACK** | `tests/integration/test_security_continuity.py` | `python3 -m unittest tests/integration/test_security_continuity.py -k test_10_invalid_acknowledgement_rejected` | Attacker forges recipient signature on receipt acknowledgment. | `InvalidAcknowledgmentError` raised by verifier. | **PASS** |

---

## 2. Detailed Threat Analysis & Limitations

### 2.1 Threat Model Enforcements
1. **Dolev-Yao Network Adversary**: The attacker can drop, reorder, delay, replay, or inject arbitrary bytes into network traffic. ASTRA-Sec successfully mitigates all Dolev-Yao capabilities through canonical AAD envelope encryption, sequence monotonic IDs, anti-replay filters, and ML-DSA-65 signatures.
2. **Radiation Single-Event Effects (SEE)**: Single-event upsets in operational registers or twiddles are caught by the dual-transform NTT butterfly invariant checker ($r \equiv t\zeta \pmod q$) and TFIB-Ref.

### 2.2 Remaining Security Limitations
- **Quantum Harvest-Now-Decrypt-Later (HNDL)**: Fully mitigated for confidentiality (ML-KEM-768) and authentication (ML-DSA-65).
- **Physical Side-Channel Attacks (SCA / DPA)**: While software execution is constant-time without branching on secret coefficients, physical power and electromagnetic analysis on bare satellite hardware requires hardware-level countermeasures outside the software boundary.
- **Permanent Node Seizure**: If a satellite is physically captured and its non-volatile memory extracted, intermediate spools contain only encrypted envelopes. The attacker cannot decrypt application data without ground station private keys.
