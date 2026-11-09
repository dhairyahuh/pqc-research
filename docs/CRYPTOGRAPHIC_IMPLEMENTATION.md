# ASTRA-Sec: Cryptographic Implementation Specification

This document details the low-level C implementation, constant-time design rules, memory safety invariants, and Python ctypes bridges for the ASTRA-Sec post-quantum cryptographic engines.

---

## 1. Algorithm Selection & Standards Conformance

| Primitive | Standard | Parameter Set | Source Implementation | C Source Path |
| :--- | :--- | :--- | :--- | :--- |
| **KEM** | NIST FIPS 203 | ML-KEM-768 | `mlkem-native` (fc269bc2d106) | `algorithms/source_ref/mlkem/` |
| **Signature** | NIST FIPS 204 | ML-DSA-65 | `mldsa-native` (88a5369bb911) | `algorithms/source_ref/mldsa/` |
| **Bulk AEAD** | NIST SP 800-38D | AES-256-GCM | OpenSSL / Cryptography | `astra_sec/crypto/aes_gcm.py` |
| **KDF** | RFC 5869 | HKDF-SHA256 | OpenSSL / Cryptography | `astra_sec/crypto/hkdf.py` |

---

## 2. Low-Level C Coding Standards

All C components in `algorithms/`, `src/`, and `tfib_implementation/` adhere to strict aerospace software constraints:

1. **Zero Dynamic Memory Allocation on Flight Path**:
   - `malloc()`, `calloc()`, `realloc()`, and `free()` are strictly forbidden in cryptographic operational pathways.
   - All buffers for NTT operations, polynomial multiplication, hashing, encapsulation, decapsulation, and signature verification are stack-allocated fixed-size arrays.
2. **Constant-Time Execution**:
   - Secret key material and intermediate ciphertext coefficients never influence CPU branch conditions or table memory lookups.
   - Bitwise multiplexing (`ct_select`) is used for all conditional selections.
3. **Bounded Loops**:
   - Every loop has a demonstrable, compile-time upper bound (e.g., $i \in [0, 255]$ for polynomial degree $n=256$).
4. **Target Standards**:
   - Standard C99 / C11 compiled with `-Wall -Wextra -Werror` clean compilation.

---

## 3. C-Python Bridge (`libastra_crypto`)

The native monitored cryptographic library is compiled from `src/astra_crypto_bridge.c` into `bin/libastra_crypto.dylib` (macOS) or `bin/libastra_crypto.so` (Linux).

### Key Exported C Functions:
```c
// Generate ML-KEM-768 Keypair (1184 bytes PK, 2400 bytes SK)
int astra_mlkem_keypair(uint8_t *pk, uint8_t *sk);

// Encapsulate Shared Secret (1088 bytes CT, 32 bytes SS)
int astra_mlkem_encaps(const uint8_t *pk, uint8_t *ct, uint8_t *ss);

// Decapsulate under Dual-Transform NTT Invariant Monitoring
int astra_mlkem_decaps_monitored(
    const uint8_t *ct,
    const uint8_t *sk,
    uint8_t *ss,
    AstraFaultStatus *fault_status
);

// Sign ADU Envelope using ML-DSA-65 (3309 bytes signature)
int astra_mldsa_sign(
    const uint8_t *sk,
    const uint8_t *msg,
    size_t msg_len,
    uint8_t *sig,
    size_t *sig_len
);

// Verify ML-DSA-65 Signature
int astra_mldsa_verify(
    const uint8_t *pk,
    const uint8_t *msg,
    size_t msg_len,
    const uint8_t *sig,
    size_t sig_len
);
```

### Fault Status Structure:
```c
typedef struct {
    uint32_t twiddle_fault_detected;    // 1 if twiddle invariant r != t*zeta violated
    uint32_t register_fault_detected;   // 1 if coefficient bit-flip detected
    uint32_t recovery_attempted;        // 1 if snapshot rollback engaged
    uint32_t recovery_successful;       // 1 if decapsulation succeeded after rollback
    uint32_t retry_count;               // Localized retry count (0, 1, or 2)
    uint32_t fail_stop_triggered;       // 1 if implicit rejection was forced
} AstraFaultStatus;
```

---

## 4. Key Lifecycle & Trust Management

1. **Originator (GSA)**:
   - Holds GSA ML-DSA-65 Signing Key.
   - Holds GSB ML-KEM-768 Public Encapsulation Key.
   - For each message, encapsulates an ephemeral 32-byte shared secret, expands it via HKDF-SHA256, encrypts payload via AES-256-GCM, and signs the envelope header and ciphertext via ML-DSA-65.
2. **Space Relays (SAT-1, SAT-2)**:
   - Hold no decryption keys. Inspect and update Layer 5 DTN custody and Layer 6 sequence numbers only.
3. **Destination (GSB)**:
   - Holds GSB ML-KEM-768 Decapsulation Secret Key.
   - Holds GSA ML-DSA-65 Public Verification Key.
   - Verifies the ML-DSA signature first. If valid, executes monitored decapsulation. If NTT invariants pass, derives session key and authenticates the AES-GCM tag.
