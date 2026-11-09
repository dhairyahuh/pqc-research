# ASTRA-Sec: Cryptographic Protocol Specification
## The Post-Quantum Resilient Bundle Security Protocol (PQ-BPSec Specification)

**Author:** ASTRA-Sec Development Agent  
**Date:** November 2026  
**Status:** Protocol Specification (Review Gated)  
**Standard Profiles:** IETF RFC 9171 (BPv7), IETF RFC 9172 (BPSec), NIST FIPS 203, NIST FIPS 204, NIST SP 800-38D, RFC 5869

---

## 1. Protocol Architecture & Overview

The **ASTRA-Sec Protocol** defines an RFC 9172-compliant Post-Quantum Security Context and asynchronous ratcheting state machine for Delay-Tolerant Networking in space systems.

### Protocol Highlights
1. **Asymmetric Key Exchange:** NIST FIPS 203 **ML-KEM-768** providing 256-bit quantum-safe shared secrets.
2. **Asymmetric Origin Authentication:** NIST FIPS 204 **ML-DSA-65** providing post-quantum non-repudiation.
3. **Payload Confidentiality & Integrity:** **AES-256-GCM** (NIST SP 800-38D) with authenticated associated data.
4. **Key Evolution:** **Post-Quantum Double Ratchet (PQ-DR)** combining symmetric KDF chains with asymmetric ML-KEM steps.
5. **Endpoint Fault Resilience:** Integrated with L4 invariant monitoring and localized rollback ($R_{max}=2$).

---

## 2. Byte-Level Wire Format & Envelope Layout

All messages traverse the space network formatted as standard RFC 9171 bundles encapsulating RFC 9172 extension blocks. The binary layout of the ASTRA-Sec Cryptographic Envelope is specified below:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Magic: "ASTR"                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Protocol Version        |         Security Flags        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                  Bundle Sequence ID (64-bit)                  |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                   Ratchet Step Index (64-bit)                 |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                   Creation Timestamp (64-bit)                 |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Time-To-Live (32-bit)                   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                    Sender EID (Fixed 64 bytes)                +
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                  Destination EID (Fixed 64 bytes)             +
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+            ML-KEM-768 Ciphertext (1,088 bytes)                +
|            (Transports Ephemeral Shared Secret)               |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|               AES-256-GCM Deterministic IV (12 bytes)         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Encrypted Payload Length                   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+             Encrypted Payload Data (Variable Length)          +
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                 AES-256-GCM Auth Tag (16 bytes)               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+             ML-DSA-65 Signature (2,420 bytes)                 +
|             (Covers Envelope Header + Ciphertext + Tag)       |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### 2.1 Field Definitions
- **Magic (32 bits):** ASCII string `0x41535452` (`"ASTR"`).
- **Protocol Version (16 bits):** `0x0001` (Version 1).
- **Security Flags (16 bits):** Bit 0: Encrypted (BCB); Bit 1: Signed (BIB); Bit 2: Ratchet Step Triggered; Bit 3: Telemetry Alert Attached.
- **Bundle Sequence ID (64 bits):** Strictly monotonic sender sequence counter.
- **Ratchet Step Index (64 bits):** Ephemeral ratchet epoch counter.
- **Creation Timestamp (64 bits):** UTC seconds since space epoch (2020-01-01 00:00:00 UTC).
- **Time-To-Live (32 bits):** Validity duration in seconds.
- **Sender / Destination EIDs (64 bytes each):** Null-terminated DTN URIs (`dtn://gsa/app`, `dtn://gsb/app`).
- **ML-KEM-768 Ciphertext (1,088 bytes):** Ephemeral ciphertext $c = \text{ML-KEM.Encaps}(pk_{dest})$.
- **AES-GCM IV (12 bytes):** Deterministic nonce constructed from epoch and sequence counters.
- **Payload Data (Variable):** Plaintext encrypted under $K_{msg}$.
- **GCM Auth Tag (16 bytes):** 128-bit MAC over ciphertext and Authenticated Associated Data (AAD).
- **ML-DSA-65 Signature (2,420 bytes):** Digital signature over all preceding envelope bytes.

---

## 3. Cryptographic Lifecycle Operations

### 3.1 Key Establishment & Ratchet Derivation
ASTRA-Sec implements the **Post-Quantum Double Ratchet (PQ-DR)** state machine:

```
[ Root Key K_root ] ───┬───> HKDF-Expand(K_root, "ratchet-step") ───> New Root Key K_root'
                       │
                       └───> HKDF-Expand(K_root, "chain-key")    ───> Chain Key K_chain
                                                                            │
                       ┌────────────────────────────────────────────────────┘
                       ▼
               [ Chain Key K_chain ]
                       ├──> HKDF-Expand(K_chain, "msg-key")  ───> Message Key K_msg (AES-256)
                       └──> HKDF-Expand(K_chain, "advance")  ───> Next Chain Key K_chain'
```

1. **Symmetric KDF Chain:** For each bundle within a ratchet epoch, a fresh message key $K_{msg}$ is derived via HKDF-SHA256, advancing $K_{chain} \to K_{chain}'$. Prior keys are securely zeroized (`explicit_bzero`), ensuring **forward secrecy**.
2. **Asymmetric Ratchet Step:** When an ephemeral ML-KEM key exchange occurs, the sender encapsulates a fresh shared secret $ss = \text{ML-KEM.Encaps}(pk_{ephem})$. The root key evolves:
   $$K_{root}' = \text{HKDF-Extract}(K_{root}, ss)$$
   This provides **post-compromise recovery (self-healing)**.

### 3.2 Authenticated Associated Data (AAD) Construction
To prevent splicing, re-ordering, or cross-mission replay, AES-GCM processes the following canonical AAD:
$$\text{AAD} = \text{Magic} \parallel \text{Version} \parallel \text{Sequence\_ID} \parallel \text{Ratchet\_Step} \parallel \text{Timestamp} \parallel \text{Sender\_EID} \parallel \text{Dest\_EID}$$
If any header field is modified by an attacker, GCM tag verification fails immediately.

### 3.3 Deterministic Nonce / IV Formulation
To prevent IV reuse across flight computer restarts, the 96-bit (12-byte) AES-GCM IV is constructed deterministically:
- Bytes 0–3: Sender Node Unique ID (32 bits).
- Bytes 4–7: Ratchet Step Index low 32 bits.
- Bytes 8–11: Bundle Sequence Counter low 32 bits.
Because `(Ratchet_Step, Bundle_Sequence)` is strictly monotonic, nonces never repeat under a single key.

### 3.4 Signature Coverage (ML-DSA-65)
The ML-DSA-65 signature covers the entire binary envelope from byte 0 through the end of the GCM tag:
$$\sigma = \text{ML-DSA.Sign}(sk_{sender}, \text{Envelope}[0 \dots \text{End\_of\_GCM\_Tag}])$$
This binds the routing headers, cryptographic parameters, ciphertext, and authentication tag into a single unforgeable unit.

---

## 4. Disruption, Replay, and Restart Management

### 4.1 Replay State Management
1. **Window-Based Sequence Tracking:** Destination maintains a monotonic high-water mark sequence number $S_{max}$ per sender EID.
2. **Fixed-Size Bloom Filter:** Out-of-order bundles within the window are recorded in a 4,096-bit Bloom filter using MurmurHash3 and Jenkins hash functions.
3. **Rejection Rule:** If `Sequence_ID <= S_max - WINDOW_SIZE` or if `BloomFilter_Contains(Bundle_ID)`, the bundle is discarded before cryptographic processing.

### 4.2 Endpoint Restart & Crash Recovery
1. **Atomic State Journaling:** Before transmitting or accepting a bundle, the node writes its ratchet state (`N_step`, `K_chain`, `S_max`) to non-volatile flash (NVRAM) using double-buffering with CRC32 checksums:
   ```c
   typedef struct {
       uint32_t crc32;
       uint64_t ratchet_step;
       uint64_t last_sequence_id;
       uint8_t  chain_key[32];
   } astra_nvram_journal_t;
   ```
2. **Crash Resumption:** Upon reboot, the bootloader verifies the journal CRC32 and restores the latest valid state. If power was lost during a write, the system rolls back to the previous intact buffer.

### 4.3 Key Rotation & Revocation Protocol
1. **Automatic Rotation:** The asymmetric ratchet triggers a rotation every $N_{rot} = 100$ bundles or every 24 hours of mission elapsed time.
2. **Revocation Broadcast:** If an endpoint private key is compromised, Ground Station A issues a signed `REVOCATION_BEACON` signed by the master mission key, containing the revoked node EID and public key fingerprint. Relays purge all buffered bundles matching the revoked identity.
