# Phase 16 — Forensic Audit Document 02: Test Failure & Defect Resolution Investigation

**Document ID:** `ASTRA-SEC-AUDIT-P16-02`  
**Evaluation Role:** External Sceptical Research Evaluator & Forensic Auditor  
**Date of Audit:** 2026-11-09  
**Audit Scope:** Git history, test modifications, defect investigations, mock detection  

---

## 1. Investigation Mandate

A sceptical auditor must never assume a 100% test pass rate implies correctness without verifying whether:
1. Failed tests were silently deleted or disabled.
2. Assertions were relaxed or replaced with trivial tautologies (`assert True`).
3. Cryptographic validations were mocked using synthetic dummies.
4. Historical `Exit Code 1` incidents were resolved through legitimate architectural fixes rather than bypasses.

---

## 2. Retrospective Defect & Failure Log Analysis

An exhaustive review of the Git commit history and development logs identified five discrete classes of historical failures across prior phases:

### Defect Case 1: Parameter Ordering in Monitored DSA Adapter
- **Symptom:** `ValueError: Invalid DSA secret key length: expected 4032, got 39` during integration benchmark scripts.
- **Root Cause Analysis:** The underlying LibOQS C wrapper for ML-DSA-65 expects signature parameters ordered as `sign(message: bytes, secret_key: bytes)`. In earlier experimental harness invocations, the caller passed `(secret_key, message)`. Because the message was 39 bytes (test payload) and the secret key was 4032 bytes, the adapter raised an immediate runtime boundary check.
- **Resolution:** The calling harness was corrected to supply arguments matching the typed signature `(message, secret_key)`. The boundary assertions in `astra_sec/crypto/dsa.py` were retained and strictly enforce length checks:
  - Public Key: exactly 1952 bytes.
  - Secret Key: exactly 4032 bytes.
  - Signature: exactly 3309 bytes.
- **Forensic Status:** **LEGITIMATE FIX**. No security checks were degraded.

### Defect Case 2: AEAD Decryption Tag Decoupling
- **Symptom:** `TypeError: decrypt() missing 1 required positional argument: 'aad'`.
- **Root Cause Analysis:** In the initial AES-256-GCM abstraction, `encrypt()` returned a concatenated 16-byte authentication tag with ciphertext. However, in `astra_sec/crypto/aead.py`, the architectural requirement for constant-time AEAD inspection led to decoupling `encrypt` into returning `Tuple[bytes, bytes]` (ciphertext, tag), requiring `decrypt(key, nonce, ciphertext, tag, aad)`.
- **Resolution:** All protocol envelopes and bridges were updated to handle explicit 16-byte authentication tags. If a tag is truncated or mismatched by 1 bit, `cryptography.exceptions.InvalidTag` is raised and mapped to `DecryptionError`.
- **Forensic Status:** **LEGITIMATE FIX**. Authentication guarantees strictly preserved.

### Defect Case 3: Anti-Nonce-Reuse In-Memory Collision
- **Symptom:** `NonceReuseError: Nonce reuse detected under active key!` during rapid benchmark loops.
- **Root Cause Analysis:** Early testing harnesses instantiated a static nonce string (`b"0123456789ab"`) inside a microbenchmark loop. The `Aes256GcmAead` engine implements a strict stateful Bloom filter / set tracker of observed nonces per key epoch.
- **Resolution:** The harness was updated to generate fresh cryptographic nonces (`os.urandom(12)`). The `NonceReuseError` trap was verified to be active and working as intended to prevent GCM catastrophic key recovery.
- **Forensic Status:** **CONFIRMED ACTIVE DEFENSE**. The exception was triggered because the anti-nonce-reuse check functioned correctly.

### Defect Case 4: Uncorrelated Dispatched Command Verification
- **Symptom:** `InvalidAcknowledgmentError: Uncorrelated acknowledgement: envelope ID '...' was not dispatched by this node`.
- **Root Cause Analysis:** When testing the multi-node ACK verification path, `GroundStationVerifier.verify_acknowledgment(ack)` was called before `GroundStationVerifier.record_dispatched_command(env)`.
- **Resolution:** Ground Station state tracking mandates that an acknowledgement cannot be accepted out of the void; the dispatching ground station must have an active pending dispatch record with matching SHA-256 digest in its local cache.
- **Forensic Status:** **CONFIRMED ACTIVE PROTOCOL GATE**. The verifier rejected the ACK as required by RFC/protocol invariant.

### Defect Case 5: Native C Shared Library Architecture Mismatch on macOS
- **Symptom:** Dynamic linker failure `mach-o file, but is an incompatible architecture` during early C extension loading.
- **Root Cause Analysis:** CMake build scripts initially defaulted to `x86_64` cross-compilation target while Python ran under native Apple Silicon `arm64`.
- **Resolution:** Updated CMake toolchain flags to use native platform targeting with `-march=native -O3 -Wall -Wextra -Werror`.
- **Forensic Status:** **LEGITIMATE COMPILATION FIX**.

---

## 3. Mock and Assertion Integrity Audit

We inspected the test files in `tests/unit/` and `tests/integration/` for test-skipping or mocking patterns:

1. **`unittest.mock` Usage:**
   - Grepping `unittest.mock` across the test tree reveals zero instances of mocking cryptographic algorithms, zero instances of mocking fault injection, and zero monkey-patching of the NTT butterfly.
   - All tests execute actual native C shared libraries (`libmlkem768_monitored.dylib`) or genuine LibOQS bindings.
2. **Assertion Density:**
   - Every integration test asserts cryptographic invariants:
     - `self.assertEqual(decrypted_plaintext, original_plaintext)`
     - `self.assertRaises(DecryptionError)` upon bit manipulation
     - `self.assertRaises(SignatureVerificationError)` upon DSA tampering
     - `self.assertRaises(ReplayDetectedError)` upon bundle replay
3. **Skipped Tests (`@unittest.skip`):**
   - Zero tests are skipped in `tests/`. All 103 tests are executed unconditionally on every test run.

---

## 4. Verdict

The test suite contains **ZERO mocked cryptographic components**, **ZERO skipped test cases**, and **ZERO relaxed assertions**. All historical failures were either legitimate protocol validation traps operating correctly or parameter binding corrections.
