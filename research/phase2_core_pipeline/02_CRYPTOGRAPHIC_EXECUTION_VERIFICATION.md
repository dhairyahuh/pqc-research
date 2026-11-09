# Phase 2 — Document 02: Cryptographic Execution and Specification Conformance

**Document ID:** `ASTRA-SEC-PH2-DOC-02`  
**Evaluation Role:** Senior C/C++ Cryptographic Engineer & PQC Specialist  
**Date:** November 2026  
**Standards:** NIST FIPS 203 (ML-KEM), NIST FIPS 204 (ML-DSA), NIST SP 800-38D (AES-GCM), RFC 5869 (HKDF)  

---

## 1. Executive Summary

This document verifies the mathematical correctness, parameter conformance, constant-time arithmetic properties, and memory allocation invariants of all cryptographic primitives implemented in ASTRA-Sec.

The cryptographic core executes through dual verified pathways:
1. **Path A (LibOQS Baseline):** Open Quantum Safe `liboqs` v0.16.0 reference implementation.
2. **Path B (Monitored Native C99 Core):** High-assurance C99 implementation with embedded NTT sub-word invariant monitoring (`algorithms/source_ref/`).

---

## 2. ML-KEM-768 Native Execution Architecture

### 2.1 Compilation and Linkage Pipeline
- **Source Files:**
  - `algorithms/source_ref/mlkem_native_monitored.c`
  - `algorithms/source_ref/mlkem/mlkem_native.c`
  - `algorithms/source_ref/mlkem_fault_hooks.c`
  - `src/astra_crypto_bridge.c`
- **Compiler Flags:**
  ```bash
  clang -O3 -Wall -Wextra -Werror -std=c99 -march=native \
        -I algorithms/source_ref/mlkem \
        -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem768 \
        -DMLK_CONFIG_PARAMETER_SET=768 \
        -DMLKEM_RESEARCH_FAULT_HOOKS \
        -dynamiclib -o bin/libastra_crypto.dylib
  ```
- **Dynamic Linker Interface:**
  - Python loads `bin/libastra_crypto.dylib` via `ctypes.CDLL`.
  - Type signatures enforce strict 64-bit pointer and length validation.

### 2.2 Parameter Conformance (NIST FIPS 203 Category 3)
| Parameter Name | FIPS 203 Standard Value | ASTRA-Sec C Definition | Verification Status |
| :--- | :--- | :--- | :--- |
| **Ring Dimension ($n$)** | 256 | `MLKEM_N = 256` | **CONFORMANT** |
| **Module Rank ($k$)** | 3 | `MLKEM_K = 3` | **CONFORMANT** |
| **Modulus ($q$)** | 3,329 | `MLKEM_Q = 3329` | **CONFORMANT** |
| **Public Key Size ($pk$)** | 1,184 bytes | `sizeof(mlkem768_public_key)` | **CONFORMANT** |
| **Secret Key Size ($sk$)** | 2,400 bytes | `sizeof(mlkem768_secret_key)` | **CONFORMANT** |
| **Ciphertext Size ($c$)** | 1,088 bytes | `sizeof(mlkem768_ciphertext)` | **CONFORMANT** |
| **Shared Secret Size ($K$)** | 32 bytes | `32 bytes (256 bits)` | **CONFORMANT** |

### 2.3 Zero Dynamic Allocation Invariant
- Static analysis via `nm -u bin/libastra_crypto.dylib` confirms **zero unresolved external references to `malloc`, `calloc`, `realloc`, or `free`**.
- All polynomial operations allocate intermediate vectors exclusively on the runtime C stack:
  ```c
  // Guaranteed stack allocation on flight path
  int16_t r[MLKEM_N]; // 256 * 2 = 512 bytes on stack
  ```

### 2.4 Constant-Time Execution Properties
- All modular reductions use constant-time Montgomery reduction (`montgomery_reduce`) and Barrett reduction (`barrett_reduce`).
- Conditional additions/subtractions are performed via bitwise arithmetic without data-dependent branching:
  ```c
  int16_t csubq(int16_t a) {
      a -= KYBER_Q;
      a += ((int32_t)a >> 31) & KYBER_Q; // Constant-time arithmetic shift
      return a;
  }
  ```

---

## 3. ML-DSA-65 Digital Signature Verification

### 3.1 Parameter Conformance (NIST FIPS 204 Category 3)
- **Public Key Size:** Exactly 1,952 bytes.
- **Secret Key Size:** Exactly 4,032 bytes.
- **Signature Size:** Exactly 3,309 bytes.
- **Verification Paradigm:** Fiat-Shamir with Aborts in $\mathbb{Z}_q[X]/(X^{256}+1)$ with $q=8,380,417$.

### 3.2 Canonical Signable Representation
To prevent encoding ambiguity attacks, ASTRA-Sec enforces deterministic canonical byte serialization before signing:
$$\text{SignableBytes} = \text{SHA256}(\text{HeaderCanonicalBytes} \parallel \text{Ciphertext} \parallel \text{Tag})$$
Any alteration of routing EIDs, sequence IDs, timestamps, or ciphertext invalidates the 3,309-byte signature.

---

## 4. Symmetric Cryptography & Key Schedule

### 4.1 Key Derivation Function (RFC 5869 HKDF-SHA256)
- **Input Key Material (IKM):** 32-byte ML-KEM shared secret $K_{\text{shared}}$.
- **Salt:** Fixed protocol domain salt:
  $$\text{Salt} = \text{SHA256}(\text{"ASTRA-SEC-V1-DOMAIN-SEPARATION-SALT"})$$
- **Info Context:** $\text{Info} = \text{"astra-sec-payload-aead-key-v1"}$.
- **Output:** Derived 32-byte (256-bit) symmetric payload encryption key:
  $$K_{\text{aead}} \leftarrow \text{HKDF-Expand}(\text{HKDF-Extract}(\text{Salt}, K_{\text{shared}}), \text{Info}, 32)$$

### 4.2 AES-256-GCM Envelope Encryption (NIST SP 800-38D)
- **Key Length:** 256 bits (32 bytes).
- **Nonce Length:** 96 bits (12 bytes) generated via CSPRNG (`os.urandom(12)`).
- **Authentication Tag Length:** 128 bits (16 bytes).
- **Canonical AAD:** Binds the entire envelope header:
  $$\text{AAD} = \text{EnvelopeHeader.to\_canonical\_aad()}$$
- **Anti-Nonce-Reuse Defense:** `Aes256GcmAead` maintains a session filter tracking emitted nonces; re-using a nonce under the active key raises `NonceReuseError`.

---

## 5. Verification Results & Test Evidence

### 5.1 NIST Known Answer Tests (KATs)
Executing `./bin/test_fips_kats` validates ASTRA-Sec against official NIST test vectors:
- `NIST-FIPS203-KAT-512`: **PASS** (KeyGen, Encaps, Decaps identical to NIST vectors).
- `NIST-FIPS203-KAT-768`: **PASS** (PK, CT, SS match official FIPS 203 vectors).
- `NIST-FIPS203-KAT-1024`: **PASS** (PK, CT, SS match official FIPS 203 vectors).
- `NIST-FIPS204-KAT-44`: **PASS** (Signature verification passes).
- `NIST-FIPS204-KAT-65`: **PASS** (Signature verification passes).
- `NIST-FIPS204-KAT-87`: **PASS** (Signature verification passes).

### 5.2 Cross-Implementation Interoperability (`./bin/test_interop`)
1. Path B (ASTRA-Sec native C) generated ML-KEM-768 keypair.
2. Path A (LibOQS v0.16.0) encapsulated shared secret using Path B's public key.
3. Path B decapsulated Path A's ciphertext.
4. **Outcome:** Derived 32-byte shared secrets matched byte-for-byte.
5. Path B generated ML-DSA-65 signature; Path A successfully verified the signature and rejected 1-bit corrupted signatures.

---

## 6. Verdict

All cryptographic engines are **100% operational, fully conformant to NIST standards**, and exhibit zero heap allocations on the operational flight path.

