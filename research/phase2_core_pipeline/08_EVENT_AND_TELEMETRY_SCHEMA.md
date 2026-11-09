# Phase 2 — Document 08: Structured Event and Telemetry Audit Schema

**Document ID:** `ASTRA-SEC-PH2-DOC-08`  
**Evaluation Role:** Senior Backend Systems Engineer & Security Auditor  
**Date:** November 2026  
**Implementation Source:** `astra_sec/schema/network.py` & `astra_sec/schema/messages.py`  

---

## 1. Executive Summary

This document specifies the structured JSON logging schema, telemetry fields, provenance tracking rules, and security sanitization boundaries governing ASTRA-Sec.

Observability data is designed to support academic reproducibility, enabling external researchers to reconstruct the exact cryptographic and networking execution history of every transmitted bundle.

---

## 2. Event Model Specification

Every lifecycle event emitted by a node adheres to a typed Pydantic v2 schema:

```json
{
  "event_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "correlation_id": "36d61003-ad1d-4406-b7db-3ca72fb93fbb",
  "category": "CRYPTOGRAPHIC",
  "event_type": "KEM_DECAPSULATION_COMPLETED",
  "node_eid": "dtn://gsb/app",
  "source_component": "MonitoredNativeKemAdapter",
  "timestamp_utc": 1794285123,
  "monotonic_duration_us": 89.27,
  "previous_state": "INGESTED",
  "new_state": "DECAPSULATED",
  "status": "SUCCESS",
  "error_code": null,
  "details": {
    "algorithm": "ML-KEM-768",
    "monitor_status": "CLEAN",
    "ntt_invariant_checked": true,
    "recovery_attempts": 0
  }
}
```

---

## 3. Event Categories & Lifecycle Types

| Category | Typical Event Types | Responsible Layer |
| :--- | :--- | :--- |
| **`CRYPTOGRAPHIC`** | `KEM_ENCAPSULATE`, `KEM_DECAPSULATE`, `AEAD_ENCRYPT`, `AEAD_DECRYPT` | L3 Post-Quantum / L2 Security |
| **`AUTHENTICATION`** | `DSA_SIGN_GENERATED`, `DSA_VERIFY_SUCCESS`, `DSA_VERIFY_FAILED` | L3 Authentication |
| **`AUTHORIZATION`** | `POLICY_CHECK_AUTHORIZED`, `POLICY_REJECT_REVOKED`, `KEY_ROTATED` | L2 Policy / Trust Store |
| **`TRANSPORT`** | `BPV7_BUNDLE_SERIALIZED`, `BPV7_BUNDLE_PARSED`, `BPSEC_BIB_VERIFIED` | L5 DTN Transport |
| **`STORAGE`** | `SPOOL_ENQUEUE`, `SPOOL_DEFERRED`, `SPOOL_FLUSHED`, `SPOOL_EXPIRED` | L6 Disruption Recovery (WAL) |
| **`NETWORK`** | `LINK_STATE_CHANGED`, `CONTACT_WINDOW_OPEN`, `CONTACT_WINDOW_CLOSED` | L5 Routing |
| **`FAULT`** | `NTT_INVARIANT_VIOLATION`, `TWIDDLE_CORRUPT_DETECTED`, `FAIL_STOP_ENGAGED` | L4 Fault Resilience |
| **`RECOVERY`** | `STACK_ROLLBACK_ATTEMPT`, `STACK_ROLLBACK_SUCCESS`, `RETRY_BUDGET_EXHAUSTED`| L4 Fault Resilience |
| **`ACKNOWLEDGEMENT`**| `ACK_GENERATED`, `ACK_FORWARDED`, `ACK_VERIFIED`, `ACK_REJECTED` | L2 / L7 Verification |

---

## 4. Strict Security Non-Logging Boundaries

To prevent side-channel exposure and data leaks, the logging engine strictly forbids the serialization of sensitive cryptographic material:

> [!CAUTION]
> Under NO circumstances may the following data types appear in structured logs, database event tables, or stdout streams:
> 1. **Secret Key Material:** Private ML-KEM-768 seeds ($s, d$), secret keys ($sk_{\text{kem}}$), and ML-DSA-65 signing keys ($sk_{\text{dsa}}$).
> 2. **Ephemeral Shared Secrets:** 32-byte decapsulated secrets ($K_{\text{shared}}$) or derived symmetric AES keys ($K_{\text{aead}}$).
> 3. **Raw Plaintext Payloads at Relays:** Intermediate satellite relays (`SAT1`, `SAT2`) log message IDs and byte lengths only; the payload bytes must never be accessed or logged.
> 4. **Randomized Nonces:** 96-bit AES-GCM nonces must not be logged alongside plaintext.

---

## 5. Clock Model & Measurement Monotonicity

- **Wall-Clock Timestamps (`timestamp_utc`):** Derived from standard 64-bit UTC seconds since DTN epoch (2000-01-01T00:00:00Z). Used strictly for TTL expiration and contact schedule alignment.
- **Microbenchmark Durations (`monotonic_duration_us`):** Derived strictly from non-decreasing monotonic clocks (`time.perf_counter_ns()`). Immune to NTP time stepping or leap-second adjustments.

---

## 6. Verdict

The telemetry schema provides **comprehensive, structured auditability while strictly enforcing zero leakage of cryptographic keys and plaintext**.
