# ASTRA-Sec: Requirement Traceability Matrix (RTM)

This matrix maps every architectural requirement across the 7-layer ASTRA-Sec model and the cross-cutting control plane to its actual implementation, test evidence, and execution status.

### Status Definitions (Strict)
1. **COMPLETE AND VERIFIED**: Executable, covered by passing automated unit & integration tests, with validated security behaviour.
2. **IMPLEMENTED BUT NOT VERIFIED**: Code exists and appears complete, but lacks automated tests or execution evidence.
3. **PARTIALLY IMPLEMENTED**: Partial code exists; key edge cases or sub-features are unaddressed.
4. **PLACEHOLDER OR MOCK**: Stub implementation, mock response, or hardcoded simulator.
5. **NOT IMPLEMENTED**: Feature was planned or described in architecture but no source code exists.
6. **BROKEN**: Code exists but fails compilation, throws unhandled exceptions, or breaks tests.
7. **NOT APPLICABLE**: Not required for this implementation phase.

---

## 1. Traceability Matrix

| Req ID | Intended Functionality | Layer | Relevant Source Files | Status | Executable? | Tests Exist? | Tests Pass? | Integration Verified? | Security Validated? | Missing Functionality / Limitations | Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-L1-01** | Application Data Unit (ADU) validation and lifecycle | L1 | `astra_sec/schema/messages.py`, `astra_sec/service/ground_station.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_pipeline_scaffolding.py`, `test_schemas.py` |
| **REQ-L1-02** | Message TTL and monotonic sequencing | L1 | `astra_sec/schema/envelope.py`, `astra_sec/service/ground_station.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_pqc_messaging.py:test_09_expired_message` |
| **REQ-L2-01** | Envelope encryption via AES-256-GCM | L2 | `astra_sec/crypto/aead.py`, `astra_sec/service/ground_station.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_crypto_adapters.py:test_aes256_gcm_aead` |
| **REQ-L2-02** | Canonical Additional Authenticated Data (AAD) binding | L2 | `astra_sec/schema/envelope.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_envelope.py:test_envelope_header_canonical_aad_stability` |
| **REQ-L2-03** | AEAD Nonce uniqueness & anti-reuse enforcement | L2 | `astra_sec/crypto/aead.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_crypto_adapters.py:test_nonce_reuse_prevention` |
| **REQ-L3-01** | Post-quantum key agreement via ML-KEM-768 | L3 | `astra_sec/crypto/mlkem_monitored.py`, `astra_sec/crypto/monitored_c.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_fips_kats.c`, `test_crypto_adapters.py` |
| **REQ-L3-02** | Post-quantum authentication via ML-DSA-65 | L3 | `astra_sec/crypto/monitored_c.py`, `astra_sec/crypto/oqs_adapter.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_interop.c`, `test_crypto_adapters.py` |
| **REQ-L3-03** | Symmetric key derivation via HKDF-SHA256 | L3 | `astra_sec/crypto/aead.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_crypto_adapters.py:test_hkdf_sha256_derivation` |
| **REQ-L3-04** | Double Ratchet key evolution | L3 | `astra_sec/security/lifecycle.py` | **PARTIALLY IMPLEMENTED** | Yes | Yes | Yes | Partial | Partial | Full asymmetric ratchet is simulated via sequential epoch key rotation rather than per-message DH ratchet. | `test_security_continuity.py:test_06_key_rotation` |
| **REQ-L4-01** | Dual-transform NTT butterfly invariant monitoring | L4 | `src/astra_crypto_bridge.c`, `algorithms/source_ref/mlkem_fault_hooks.c` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_mlkem_monitored.py:test_02_transient_fault_recovery` |
| **REQ-L4-02** | Localized snapshot rollback ($K \le 2$) | L4 | `algorithms/source_ref/mlkem_fault_hooks.c`, `tfib_implementation/` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | Phase 7E & Phase 7J C test harnesses |
| **REQ-L4-03** | TFIB-Ref dual-reference twiddle verification | L4 | `tfib_implementation/tfib_ref.c`, `src/astra_crypto_bridge.c` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_mlkem_monitored.py:test_05_tfib_ref_resilience` |
| **REQ-L4-04** | Fail-stop implicit rejection suppression | L4 | `src/astra_crypto_bridge.c`, `astra_sec/crypto/mlkem_monitored.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_fault_resilience.py:test_03_persistent_fault_fail_stop_suppression` |
| **REQ-L5-01** | RFC 9171 Bundle Protocol v7 (BPv7) wire encoding | L5 | `astra_sec/dtn/bpv7.py`, `astra_sec/dtn/cbor.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_bpv7_cbor.py:test_bpv7_bundle_cbor_wire_encoding` |
| **REQ-L5-02** | RFC 9172 BPSec Block Integrity Block (BIB) HMAC-SHA256 | L5 | `astra_sec/dtn/bpsec.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_bpv7_cbor.py:test_bpsec_bib_integrity_and_tampering` |
| **REQ-L5-03** | Zero-decryption relay guarantee | L5 | `astra_sec/network/relay.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_multinode_satellite.py:test_07_relay_payload_tampering_detected` |
| **REQ-L5-04** | NASA/JPL ION-DTN native daemon integration | L5 | `astra_sec/dtn/ion_config.py`, `astra_sec/dtn/contact_plan.py` | **PARTIALLY IMPLEMENTED** | Yes | Yes | Yes | Partial | N/A | Generates ION-DTN `.ionrc`, `.bprc`, `.ionsecrc` config files, but ION C daemons (`ionadmin`, `bpadmin`) are not running on the macOS host. | `test_bpv7_cbor.py:test_ion_node_config_generation` |
| **REQ-L6-01** | Persistent non-volatile message spooling (SQLite WAL) | L6 | `astra_sec/network/spool.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_multinode_satellite.py:test_02_relay_restart_with_persistent_spool` |
| **REQ-L6-02** | Bounded exponential backoff & contact scheduling | L6 | `astra_sec/network/routing.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_dtn_disruption.py:test_03_delayed_contact_window` |
| **REQ-L6-03** | Message reordering and deduplication | L6 | `astra_sec/network/relay.py`, `astra_sec/security/replay.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_multinode_satellite.py:test_05_message_reordering_tolerance` |
| **REQ-L7-01** | Spacecraft FDIR real-time telemetry | L7 | `astra_sec/schema/messages.py`, `astra_sec/service/ground_station.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_fault_resilience.py:test_01_clean_messaging_telemetry` |
| **REQ-L7-02** | Ground-station cryptographic receipt verification | L7 | `astra_sec/security/verifier.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_security_continuity.py:test_10_invalid_acknowledgement_rejected` |
| **REQ-CP-01** | Dynamic public key trust store and peer authorization | Control Plane | `astra_sec/schema/trust.py`, `astra_sec/security/policy.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_security_continuity.py:test_05_revoked_sender_rejected` |
| **REQ-CP-02** | Administrative REST & WebSocket telemetry dashboard | Control Plane | `astra_sec/dashboard/app.py`, `astra_sec/dashboard/static/index.html` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_dashboard.py` (13/13 passing) |
| **REQ-CP-03** | Bearer token authentication on mutating endpoints | Control Plane | `astra_sec/dashboard/app.py` | **COMPLETE AND VERIFIED** | Yes | Yes | Yes | Yes | Yes | None | `test_dashboard.py:test_admin_dispatch_unauthorized_blocked` |

---

## 2. Summary Breakdown

- **Total Requirements Audited:** 25
- **COMPLETE AND VERIFIED:** 23 (92.0%)
- **PARTIALLY IMPLEMENTED:** 2 (8.0%)
  - *REQ-L3-04 (Double Ratchet):* Implemented via sequential epoch key rotation with backward secrecy; full per-message ratchet is planned.
  - *REQ-L5-04 (Native ION C Daemons):* Configuration generator implemented and verified; native ION-DTN C daemon requires Linux/POSIX IPC environment.
- **PLACEHOLDER OR MOCK:** 0 (0.0%)
- **BROKEN:** 0 (0.0%)
- **NOT IMPLEMENTED:** 0 (0.0%)
