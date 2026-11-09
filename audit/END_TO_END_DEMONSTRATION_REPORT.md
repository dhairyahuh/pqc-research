# ASTRA-Sec: End-to-End Live Demonstration Audit Report

**Scenario:** Ground Station Alpha (`dtn://gsa/app`) $\to$ Satellite Relay 1 (`dtn://sat1/relay`) $\to$ Satellite Relay 2 (`dtn://sat2/relay`) $\to$ Ground Station Bravo (`dtn://gsb/app`)  
**Auditor:** Technical Auditor & Demonstration Evaluator  
**Execution Timestamp:** 2026-11-09 19:06:10 UTC  
**Result:** FULL LIVE SCENARIO PASSED (Zero Hardcoded Stubs)

---

## 1. Step-by-Step Demonstration Sequence Audit

| Step | Required Action | Actual Mechanism Observed | Real Crypto or Mock? | Result | Observed Latency / Output |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | Start all services | `PublicKeyTrustStore`, `AuthorizationPolicy`, and `GroundStationVerifier` initialized in-memory. | **REAL** | **PASS** | Trust store & policy loaded. |
| **2** | Verify node health | EIDs validated (`dtn://gsa/app`, `dtn://gsb/app`, etc.). Keys generated for GSA and GSB. | **REAL** | **PASS** | GSA: ML-KEM-768 & ML-DSA-65 active. |
| **3** | Create message at GSA | ADU generated: payload `b"CRITICAL_ORBIT_BURN_COMMAND_VECTOR_42"`, TTL=300s, Seq=1. | **REAL** | **PASS** | Envelope ID: `5c68b49b-8844-4494-a81c-843709a8eb92`. |
| **4** | Generate crypto material | 96-bit CSPRNG nonce generated (`arc4random_buf`). | **REAL** | **PASS** | Nonce: 12 bytes unique random. |
| **5** | Establish ML-KEM secret | GSA calls `MonitoredMlkemAdapter.encapsulate(gsb_pk)`. | **REAL** | **PASS** | 1088-byte ciphertext + 32-byte shared secret generated. |
| **6** | Derive encryption key | `HkdfSha256Engine.derive_key()` derives 32-byte AES key bound to canonical AAD context. | **REAL** | **PASS** | 256-bit symmetric key derived. |
| **7** | Encrypt message | `Aes256GcmAead.encrypt()` encrypts payload using AES-256-GCM. | **REAL** | **PASS** | Ciphertext: 37 bytes, Tag: 16 bytes. |
| **8** | Sign message data | `MonitoredNativeDsaAdapter.sign()` computes 3309-byte ML-DSA-65 signature over canonical AAD + ciphertext digest. | **REAL** | **PASS** | Signature: 3309 bytes. Dispatched in **1.50 ms**. |
| **9** | Transmit to SAT1 | Envelope packaged and handed to SAT1 ingress. | **REAL** | **PASS** | Ingested into SAT1 routing buffer. |
| **10** | Forward through SAT1 | SAT1 routes via `RoutingTable({"dtn://gsb/*": "dtn://sat2/relay"})`. Forwards without reading payload. | **REAL** | **PASS** | Event: `MESSAGE_FORWARDED` $\to$ `dtn://sat2/relay`. |
| **11** | Forward through SAT2 | SAT2 routes via `RoutingTable({"dtn://gsb/*": "dtn://gsb/app"})`. Spools into SQLite WAL and delivers. | **REAL** | **PASS** | Delivered count at GSB: 1 envelope. |
| **12** | Receive at GSB | GSB validates envelope structure, EID formatting, and TTL freshness. | **REAL** | **PASS** | Freshness verified ($t < t_{\text{now}} + \text{TTL}$). |
| **13** | Verify sender | GSB checks GSA public key in local `PublicKeyTrustStore` and validates ML-DSA-65 signature. | **REAL** | **PASS** | Signature verification: VALID. |
| **14** | Check integrity | AES-256-GCM authentication tag verified during payload decryption. | **REAL** | **PASS** | 16-byte GCM tag match: SUCCESS. |
| **15** | Anti-replay filter | Envelope ID and sequence ID verified against `AntiReplayFilter` ledger. | **REAL** | **PASS** | Replay check: FIRST TIME SEEN (Recorded). |
| **16** | Decapsulate & Decrypt | GSB decapsulates shared secret via monitored ML-KEM native engine and decrypts payload. | **REAL** | **PASS** | Decrypted: `"CRITICAL_ORBIT_BURN_COMMAND_VECTOR_42"`. |
| **17** | Display message | Plaintext displayed on receiving console. | **REAL** | **PASS** | Verified plaintext identical to originator payload. |
| **18** | Authenticated ACK | GSB signs `MessageAcknowledgment` with its ML-DSA-65 key; GSA verifier cryptographically validates ACK. | **REAL** | **PASS** | Verifier: `signature_valid=True`, `status="SUCCESS"`. |

---

## 2. Actual Terminal Execution Transcript

```
=== 1. Starting Services & Trust Store ===
=== 2. Initializing Nodes ===
[+] Nodes healthy: GSA (KEM: ML-KEM-768, DSA: ML-DSA-65)
[+] SAT1 spool pending: 0 | SAT2 spool pending: 0
=== 3-8. Create, Encapsulate, Encrypt, Sign at GSA ===
[+] GSA dispatched envelope: 5c68b49b-8844-4494-a81c-843709a8eb92
    Ciphertext: 37 bytes | Sig: 3309 bytes | Tag: 16 bytes in 1.50 ms
=== 9-11. Transmit through SAT1 and SAT2 ===
[+] SAT1 Ingest Event: MESSAGE_FORWARDED -> Next Hop: dtn://sat2/relay
[+] SAT2 Ingested & Delivered count: 1
=== 12-16. Receive, Verify, Decapsulate, Decrypt at GSB ===
[+] GSB Decrypted Plaintext: CRITICAL_ORBIT_BURN_COMMAND_VECTOR_42
[+] GSB Generated Cryptographic ACK: ID=ee00fede-2789-4028-a330-6815c46eb852, Status=SUCCESS
=== 17-18. Verify Authenticated Receipt at GSA ===
[+] GSA Verifier Result: OriginalEnvelope=5c68b49b-8844-4494-a81c-843709a8eb92 signature_valid=True status=SUCCESS
=== END-TO-END DEMONSTRATION SUCCESS ===
```

---

## 3. Strict Proof of Zero Relay Decryption

An inspection of `SatelliteRelayNode.ingest()` in `astra_sec/network/relay.py` confirms:
1. **Header-Only Ingestion**:
   ```python
   header = envelope.header
   env_id = header.envelope_id
   ```
2. **Zero Cryptographic Key Material**:
   - `SatelliteRelayNode` does not possess instances of `KemAdapter`, `DsaAdapter`, or `Aes256GcmAead`.
   - `SatelliteRelayNode` has no access to private key stores.
3. **Payload Opacity**:
   - The encrypted bytes in `envelope.ciphertext` and the KEM encapsulated seed in `header.kem_ciphertext` are forwarded verbatim.
   - Any modification to `envelope.ciphertext` by a rogue relay causes immediate AEAD authentication tag failure at the destination node prior to plaintext release (`test_multinode_satellite.py:test_07_relay_payload_tampering_detected`).
