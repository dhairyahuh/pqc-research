# Phase 11: Independent Reference Oracle Validation Report

**Document Date:** October 3, 2026  
**Auditor/Researcher:** Skeptical Cryptographic Software Verification Audit  
**Target:** ML-KEM-768 (FIPS 203) Reference Oracle Implementation  
**Status:** VALIDATED (Phase 1 Complete)

---

## 1. Executive Summary

In Phase 0 of the Phase 11 revalidation audit (`tfib_experiments/phase11_initial_audit.md`), a critical vulnerability was identified in the prior experimental harness: **Oracle Circularity**. The previous test campaign (`phase9_tfib_campaign.c`) utilized the production implementation under test (`mlkem768_dec_inst`) as its ground-truth oracle for evaluating decapsulation validity during fault injection. If an unmonitored invariant or common-mode corruption affected baseline computation, both the DUT and the oracle suffered identical failure modes, rendering undetected corruptions invisible.

To resolve this defect, **Phase 1** established and validated a strictly isolated, specification-conforming independent oracle library (`libindependent_oracle.a`) combining:
1. **Open Quantum Safe (`liboqs 0.16.0`)**: A mature, externally audited post-quantum cryptographic reference library linked via public C APIs (`OQS_KEM_ml_kem_768_*`).
2. **Standalone FIPS 202 Specification Reference (`fips202_ref.c`)**: A zero-dependency, self-contained Keccak-f[1600] / SHAKE-256 implementation adhering strictly to NIST FIPS 202, used to independently verify canonical implicit rejection.

### Validation Outcome
All six verification suites passed without warning or error:
- **NIST FIPS 203 Keypair Generation KAT**: Byte-for-byte exact match (1184-byte PK, 2400-byte SK).
- **NIST FIPS 203 Encapsulation KAT**: Byte-for-byte exact match (1088-byte CT, 32-byte SS).
- **NIST FIPS 203 Decapsulation KAT**: Byte-for-byte exact match on shared secret.
- **Canonical Implicit Rejection Verification**: Exactly matches independent specification calculation $K_{\text{rej}} = \text{SHAKE-256}(z \mathbin{\Vert} c, 32)$ and strictly diverges from $K_{\text{valid}}$.
- **Negative Falsification Tests**: Tampered secret keys, tampered shared secrets, and seed mutations are reliably detected and rejected.
- **Boundary & Malformed Inputs**: All-zeros and all-ones ciphertexts are safely handled with correct implicit rejection semantics.

---

## 2. Oracle Architecture & Independence Analysis

### 2.1 Provenance and Library Configuration
- **Library**: `liboqs` version 0.16.0
- **Source/Distribution**: Homebrew installation at `/opt/homebrew/opt/liboqs`
- **Compiler/Architecture**: Clang / Apple Silicon (AArch64) with native hardware acceleration (`OQS_ENABLE_KEM_ml_kem_768_aarch64 1`).
- **External Dependencies**: Standard C library (`libc`) only.

### 2.2 Strict Architectural Isolation
To prevent any possibility of binary contamination or shared state:
1. **Compilation Isolation**: The oracle module (`tfib_experiments/phase11_oracle/independent_oracle.c` and `fips202_ref.c`) is compiled strictly with standard headers and `<oqs/oqs.h>`.
2. **Zero In-Tree Linkage**: `libindependent_oracle.a` does **not** link against `bin/obj/mlkem768_inst.o`, `algorithms/source_ref/`, or any header from the workspace's instrumented ML-KEM implementation.
3. **Symbol Inspection**: Analysis of `nm libindependent_oracle.a` confirms that the only external symbols imported are standard memory/string functions (`memcpy`, `memcmp`, `memset`, `malloc`, `free`) and public liboqs entrypoints:
   - `OQS_KEM_ml_kem_768_new`
   - `OQS_KEM_ml_kem_768_free`
   - `OQS_KEM_ml_kem_768_keypair_derand`
   - `OQS_KEM_ml_kem_768_encaps_derand`
   - `OQS_KEM_ml_kem_768_decaps`
   No twiddle tables, NTT functions, or global state from the production tree are referenced.

---

## 3. Known Answer Test (KAT) Verification

The oracle was subjected to deterministic Known Answer Tests derived from the official NIST FIPS 203 submission test suite (stored in `references/test_vectors/mlkem_expected_kat.h`).

### 3.1 Test Suite 1: Keypair Generation (`ML-KEM-768`)
- **Inputs**:
  - Deterministic seed $d \in \{0,1\}^{256}$: `d98226ec588e...`
  - Implicit rejection secret $z \in \{0,1\}^{256}$: `893f0b2ff841...`
- **Results**:
  - Expected PK (1184 bytes): `693b4b7f22698cc9...c38c`
  - Oracle PK (1184 bytes):   `693b4b7f22698cc9...c38c`  
    **Result: EXACT MATCH (0 diff bytes)**
  - Expected SK (2400 bytes): `af5439f3db8d4a97...a3d0`
  - Oracle SK (2400 bytes):   `af5439f3db8d4a97...a3d0`  
    **Result: EXACT MATCH (0 diff bytes)**

### 3.2 Test Suite 2: Encapsulation (`ML-KEM-768`)
- **Inputs**:
  - Public Key: Valid KAT public key from Test 1.
  - Deterministic message entropy $m \in \{0,1\}^{256}$: `6bc932db3c6f...`
- **Results**:
  - Expected Ciphertext (1088 bytes): `12f94ef4e4f6ea11...bd0a`
  - Oracle Ciphertext (1088 bytes):   `12f94ef4e4f6ea11...bd0a`  
    **Result: EXACT MATCH (0 diff bytes)**
  - Expected Shared Secret (32 bytes): `0b1b32be26247cbc...207e`
  - Oracle Shared Secret (32 bytes):   `0b1b32be26247cbc...207e`  
    **Result: EXACT MATCH (0 diff bytes)**

### 3.3 Test Suite 3: Decapsulation (`ML-KEM-768`)
- **Inputs**:
  - Authentic Ciphertext: KAT ciphertext from Test 2.
  - Authentic Secret Key: KAT secret key from Test 1.
- **Results**:
  - Expected Shared Secret (32 bytes): `0b1b32be26247cbc...207e`
  - Oracle Decapsulated SS (32 bytes): `0b1b32be26247cbc...207e`  
    **Result: EXACT MATCH (0 diff bytes)**

---

## 4. Canonical Implicit Rejection Verification

### 4.1 Specification Requirement (FIPS 203, Algorithm 17)
Under FIPS 203 §7.3, when a decapsulating entity receives an invalid ciphertext $c$ (i.e., re-encrypting the decrypted message produces $c' \neq c$), the scheme must return the pseudo-random implicit rejection key:
$$K_{\text{rej}} = \text{SHAKE-256}(z \mathbin{\Vert} c, 32)$$
where $z$ is the 32-byte rejection seed stored in bytes $[2368, 2399]$ of the 2400-byte decapsulation key.

### 4.2 Independent Verification Architecture
To eliminate dependence on liboqs's internal hashing routines, a standalone FIPS 202 reference implementation (`fips202_ref.c`) was authored based on the Keccak permutation specification. 
- Input buffer: $z \mathbin{\Vert} c$ (32 bytes $z$ + 1088 bytes corrupted ciphertext = 1120 bytes total).
- Hash function: SHAKE-256 squeezed to 32 bytes.
- Independent reference output:
  `e282585337f644231c9a85e64b40600b3c6830087fbed2f5cfa6d18e3b237e1b`
- Cross-validation: Confirmed identical output against Python 3 standard library `hashlib.shake_256(z + c).digest(32)`.
- Liboqs decapsulation of the corrupted ciphertext produced:
  `e282585337f644231c9a85e64b40600b3c6830087fbed2f5cfa6d18e3b237e1b`
- **Result**: Byte-for-byte exact match with independent calculation; completely distinct from valid shared secret $K_{\text{valid}}$.

---

## 5. Falsification, Negative, and Boundary Testing

To verify that the test runner correctly rejects non-conforming or corrupted data, extensive negative tests were executed:

| Test Identifier | Mutation Applied | Expected Outcome | Oracle Observation | Result |
| :--- | :--- | :--- | :--- | :--- |
| **SS-Tamper** | Corrupted 1st byte of expected SS | Mismatch flagged | Correctly flagged failure | PASS |
| **SK-Tamper** | Inverted 1st byte of secret key | Decaps failure / invalid SS | Shared secret diverged | PASS |
| **Seed-Mutation**| Modified 1st byte of seed $d$ | Distinct PK generated | Generated completely distinct PK | PASS |
| **CT-Zeros** | Ciphertext set to 1088 zero bytes | Rejected via implicit key | Emitted non-zero pseudorandom $K_{\text{rej}}$ | PASS |
| **CT-Ones** | Ciphertext set to 1088 0xFF bytes | Rejected via implicit key | Emitted non-zero pseudorandom $K_{\text{rej}}$ | PASS |

---

## 6. Artifact Inventory & Reproducibility

All components of the Phase 1 independent reference oracle are committed in the directory `tfib_experiments/phase11_oracle/`:

| File | Description |
| :--- | :--- |
| `independent_oracle.h` | Clean public C API declaring derandomized keypair, encaps, decaps, and canonical rejection functions. |
| `independent_oracle.c` | Wrapper implementation delegating to `liboqs` C API. |
| `fips202_ref.h` | Standalone header declaring `fips202_ref_shake256`. |
| `fips202_ref.c` | Self-contained, specification-adherent C implementation of Keccak-f[1600] and SHAKE-256. |
| `libindependent_oracle.a` | Compiled static library containing oracle symbols without any in-tree linkage. |
| `test_independent_oracle.c` | Comprehensive test runner executing all 6 KAT, rejection, and negative test suites. |
| `Makefile` | Build configuration compiling and linking the static library and test harness. |
| `run_oracle_tests.sh` | Shell script automating clean build, execution, and validation of JSON test report. |
| `kat_validation_results.json`| Machine-readable JSON output documenting pass/fail status and verification flags. |

### How to Reproduce
From the repository root:
```bash
cd tfib_experiments/phase11_oracle
./run_oracle_tests.sh
```
Exit code `0` confirms 100% verification across all test groups.

---

## 7. Scope Boundary and Next Steps

With Phase 1 complete, the experimental framework now possesses an unimpeachable, external ground-truth oracle for ML-KEM-768 decapsulation and implicit rejection.

**Strict Boundary Reminder:**
As instructed, Phase 2 (Fault Campaign Correction and Harness Decoupling) has **not** been executed. The production campaign runner (`tfib_experiments/phase9_tfib_campaign.c`) and table allocations remain in their pre-audit state pending explicit review and approval of this Phase 1 deliverable.
