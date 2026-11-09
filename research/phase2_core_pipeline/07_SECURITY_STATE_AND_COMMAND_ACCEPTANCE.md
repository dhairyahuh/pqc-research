# Phase 2 — Document 07: Security State, Anti-Replay, and Command Acceptance Semantics

**Document ID:** `ASTRA-SEC-PH2-DOC-07`  
**Evaluation Role:** Security Verification Researcher & Protocol Architect  
**Date:** November 2026  
**Implementation Source:** `astra_sec/security/` & `astra_sec/service/ground_station.py`  

---

## 1. Executive Summary

This document specifies the exact security conditions, state transitions, anti-replay mechanisms, and commit points governing telecommand acceptance and acknowledgement in ASTRA-Sec.

### The Cardinal Rule:
> **Successful bundle delivery is NOT successful command acceptance. Successful decryption is NOT authorization. An acknowledgement (ACK) must NEVER be emitted before atomic non-volatile transaction commit.**

---

## 2. The 18-Stage End-to-End Command Lifecycle

```mermaid
sequenceDiagram
    autonumber
    participant GSA as Ground Station A (Sender)
    participant RELAY as Satellite Relays (SAT1 / SAT2)
    participant GSB as Ground Station B (Destination)

    Note over GSA: Stage 1-3: Cryptographic Origin
    GSA->>GSA: 1. Generate telecommand payload ADU
    GSA->>GSA: 2. Encapsulate ML-KEM-768 & derive AES key via HKDF
    GSA->>GSA: 3. Encrypt payload (AES-GCM) & sign envelope (ML-DSA-65)
    
    Note over GSA,RELAY: Stage 4-6: Disruption-Tolerant Transport
    GSA->>RELAY: 4. Serialize into BPv7 bundle & transmit
    RELAY->>RELAY: 5. Queue in non-volatile SQLite WAL spool
    RELAY->>RELAY: 6. Forward across contact windows (Zero Plaintext Access)
    
    Note over RELAY,GSB: Stage 7-12: Cryptographic Ingestion & Verification
    RELAY->>GSB: 7. Ingest bundle at destination endpoint
    GSB->>GSB: 8. Verify destination EID matches node
    GSB->>GSB: 9. Verify sender authorization in Trust Store / Policy
    GSB->>GSB: 10. Verify freshness (TTL) & Persistent Anti-Replay Filter
    GSB->>GSB: 11. Verify ML-DSA-65 digital signature
    GSB->>GSB: 12. Execute monitored ML-KEM decapsulation (NTT Invariant Check)
    
    Note over GSB: Stage 13-15: Atomic Command Commit & Execution
    GSB->>GSB: 13. Verify AES-256-GCM authentication tag & decrypt
    GSB->>GSB: 14. Command Accepted: Pre-commit sequence to SQLite WAL
    GSB->>GSB: 15. Command Committed & Executed (At-Most-Once Semantics)
    
    Note over GSB,GSA: Stage 16-18: Authenticated Reverse Delivery Receipt
    GSB->>GSB: 16. Generate MessageAcknowledgment (status: SUCCESS)
    GSB->>GSB: 17. Authenticate ACK with GSB ML-DSA-65 signature
    GSB->>GSA: 18. Route ACK via DTN relays to GSA Verifier
    GSA->>GSA: Verifier correlates ACK with dispatched envelope & verifies signature
```

---

## 3. The 5-Phase Cryptographic Transaction Protocol (C4AP)

To prevent the "Restart-Replay Vulnerability" (where a satellite watchdog reboot erases volatile replay caches and allows re-execution of earlier commands), ASTRA-Sec enforces a 5-phase transaction protocol:

```
[Phase 1: Authenticated]
  ├── ML-DSA-65 signature verified under sender's public key
  └── ML-KEM decapsulation completed with status == SUCCESS
             │
             ▼
[Phase 2: Accepted]
  ├── Destination EID confirmed
  ├── Sender authorization confirmed in Trust Store
  └── Timestamp within TTL validity window
             │
             ▼
[Phase 3: Pre-Committed in WAL]
  ├── Write sequence mark (source_eid, sequence_id, envelope_id) to PersistentSecurityState
  └── SQLite synchronous disk barrier (COMMIT transaction)
             │
             ▼
[Phase 4: Executed]
  └── Dispatch plaintext telecommand to spacecraft subsystem (e.g., thruster burn)
             │
             ▼
[Phase 5: Acknowledged]
  ├── Construct MessageAcknowledgment binding envelope_id and commit timestamp
  ├── Sign ACK with destination ML-DSA-65 private key
  └── Dispatch ACK into reverse DTN return path
```

### Invariant:
If a power-cycle reboot occurs at Phase 3, the database WAL already contains the sequence mark. Upon reboot, any replayed delivery attempt is rejected at Phase 2 as a duplicate.

---

## 4. Failure Mode Matrix & Enforced Defensive Reactions

| Failure Condition | Detection Stage | Architectural Defensive Action | Plaintext Exposed? | ACK Emitted? |
| :--- | :--- | :--- | :--- | :--- |
| **Tampered Ciphertext** | Stage 13 (AEAD) | `DecryptionError` raised; tag check fails. | **NO (Zero)** | **NO** |
| **Tampered Header / AAD** | Stage 13 (AEAD) | Tag verification fails; header cannot be altered in transit. | **NO (Zero)** | **NO** |
| **1-Bit Mutated Signature**| Stage 11 (ML-DSA) | `SignatureVerificationError` raised; bundle dropped. | **NO (Zero)** | **NO** |
| **Unauthorized Sender** | Stage 9 (Policy) | `UnauthorizedSenderError` raised; peer dropped. | **NO (Zero)** | **NO** |
| **Mismatched Destination** | Stage 8 (Router) | `DestinationMismatchError` raised. | **NO (Zero)** | **NO** |
| **Expired Command TTL** | Stage 10 (Replay) | `MessageExpiredError` raised; bundle wiped. | **NO (Zero)** | **NO** |
| **Replay Attempt** | Stage 10 (Replay) | `ReplayDetectedError` raised; duplicate dropped. | **NO (Zero)** | **NO** |
| **Replay After Reboot** | Stage 10 (Replay) | Sequence ID matches persistent WAL record; rejected. | **NO (Zero)** | **NO** |
| **Persistent KEM Fault** | Stage 12 (NTT) | Monitored KEM escalates to fail-stop implicit rejection. | **NO (Zero)** | **NO** |
| **Revoked Sender Key** | Stage 9 (Policy) | `IdentityRevokedError` raised immediately. | **NO (Zero)** | **NO** |
| **Corrupted ACK Signature**| Stage 18 (Verifier)| Verifier rejects ACK; marks original command unacknowledged.| N/A | Rejected |

---

## 5. Verdict

ASTRA-Sec's command acceptance rules are **atomic, crash-consistent, fail-closed, and guarantee zero duplicate command executions across unannounced system reboots**.

