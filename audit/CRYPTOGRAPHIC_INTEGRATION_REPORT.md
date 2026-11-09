# ASTRA-Sec: Cryptographic Implementation & Security Integration Audit

**Auditor:** Independent Cryptographic Reviewer  
**Standard Benchmarks:** NIST FIPS 203, NIST FIPS 204, NIST SP 800-38D, RFC 5869  
**Audit Scope:** C source code, Python ctypes wrapper, key lifecycle, constant-time guarantees, and side-channel/SDC containment.

---

## 1. Cryptographic Algorithms & Parameter Sets

| Service | Algorithm Standard | Parameter Set | Key / Ciphertext Sizes | Implementation Provenance |
| :--- | :--- | :--- | :--- | :--- |
| **Key Encapsulation** | NIST FIPS 203 | ML-KEM-768 | PK: 1184 B, SK: 2400 B, CT: 1088 B, SS: 32 B | Native monitored C (`mlkem-native` base + TFIB-Ref) |
| **Digital Signatures** | NIST FIPS 204 | ML-DSA-65 | PK: 1952 B, SK: 4032 B, Sig: 3309 B | Native C (`mldsa-native` clean ref) + LibOQS 0.16.0 |
| **Payload Encryption** | NIST SP 800-38D | AES-256-GCM | Key: 256 bits (32 B), Nonce: 96 bits (12 B), Tag: 128 bits (16 B) | Python `cryptography` (OpenSSL 3.0 backend) |
| **Key Derivation** | RFC 5869 | HKDF-SHA256 | PRK: 32 B, Output Key: 32 B, Context: Canonical AAD | Python `cryptography` |

---

## 2. Call Stack Trace: Application to Native C Engine

The call pathway from the top-level ground station service down to the low-level NTT butterfly invariant monitor was traced:

```
[L1/L2] GroundStationNode.send_message() (astra_sec/service/ground_station.py)
   │
   ├──> [L3] MonitoredMlkemAdapter.encapsulate(peer_pk) (astra_sec/crypto/mlkem_monitored.py)
   │       └──> ctypes.CDLL("bin/libastra_crypto.dylib").astra_mlkem_encaps()
   │               └──> astra_crypto_bridge.c: astra_mlkem_encaps()
   │                       └──> mlkem768_enc() (algorithms/source_ref/mlkem/mlkem_native.c)
   │
   ├──> [L2] HkdfSha256Engine.derive_key(shared_secret, info=aad) (astra_sec/crypto/aead.py)
   │
   ├──> [L2] Aes256GcmAead.encrypt(key, nonce, payload, associated_data=aad)
   │
   └──> [L3] MonitoredNativeDsaAdapter.sign(dsa_sk, signable_bytes) (astra_sec/crypto/monitored_c.py)
           └──> ctypes.CDLL("bin/libastra_crypto.dylib").astra_mldsa_sign()
                   └──> astra_crypto_bridge.c: astra_mldsa_sign()
                           └──> mldsa_signature() (algorithms/source_ref/mldsa/mldsa_native.c)

[L1/L2] GroundStationNode.receive_message() (astra_sec/service/ground_station.py)
   │
   ├──> [L3] MonitoredNativeDsaAdapter.verify(sender_pk, signature, signable_bytes)
   │
   ├──> [L3/L4] MonitoredMlkemAdapter.decapsulate_with_telemetry(ct, sk)
   │       └──> ctypes.CDLL("bin/libastra_crypto.dylib").astra_mlkem_decaps_monitored()
   │               │
   │               └──> astra_crypto_bridge.c: astra_mlkem_decaps_monitored()
   │                       │
   │                       ├──> tfib_set_mode(TFIB_MODE_REF)
   │                       └──> mlkem768_dec_monitored(ss, ct, sk, &raw_status)
   │                               │
   │                               ├──> NTT Invariant Checking (r == t * zeta mod q)
   │                               ├──> TFIB-Ref Twiddle Verification (strategy 1)
   │                               └──> Local Snapshot Rollback (K <= 2)
   │
   ├──> [L2] HkdfSha256Engine.derive_key(ss, info=aad)
   │
   └──> [L2] Aes256GcmAead.decrypt(key, nonce, ciphertext, tag, associated_data=aad)
```

---

## 3. Alternative & Reference Engine Integration

ASTRA-Sec implements a dual-engine architecture managed by `CryptoEngineFactory` (`astra_sec/crypto/factory.py`):
1. **Primary Path (Intended Research Path):**
   - Native C monitored library (`bin/libastra_crypto.dylib`).
   - Features active NTT monitoring and TFIB-Ref twiddle verification.
2. **Secondary Path (Reference Baseline):**
   - LibOQS 0.16.0 wrappers (`OqsKemAdapter`, `OqsDsaAdapter`).
   - Used for cross-engine interoperability verification (`test_interop.c`) and baseline comparative benchmarking.

Execution of `CryptoEngineFactory.get_engine_status()` confirms that both engines are operational, with the native monitored engine designated as preferred.

---

## 4. Key Security & Nonce Handling Controls

1. **Deterministic AEAD Nonce Uniqueness**:
   - `Aes256GcmAead` enforces strict in-memory tracking of all generated 96-bit nonces.
   - Re-using a nonce under the same key immediately triggers a `NonceReuseError` (`test_crypto_adapters.py:test_nonce_reuse_prevention`).
2. **Zero Dynamic Allocation on Operational Path**:
   - C cryptographic routines in `algorithms/source_ref/` and `src/` allocate intermediate polynomial arrays exclusively on the stack. `malloc()` and `free()` are absent from operational transform routines.
3. **Secret Redaction**:
   - The `KeyPair` model (`astra_sec/schema/envelope.py`) overrides `__repr__` and `__str__` to output `[REDACTED]`.
   - The REST API endpoints (`/api/nodes`, `/api/topology`) emit only truncated 16-character SHA-256 fingerprints of public keys; secret keys are absent from all schemas and serializers.
4. **Silent Data Corruption (SDC) Prevention**:
   - If an uncorrectable persistent hardware fault occurs during decapsulation, `MonitoredMlkemAdapter` suppresses the output, triggers fail-stop handling, and raises `MonitoredMlkemError`. Under no circumstances is a corrupted or partial shared secret made available to the application layer.
