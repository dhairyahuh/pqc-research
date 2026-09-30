# Cryptographic Implementation Provenance Document

## 1. Architectural Separation

This research project maintains a strict dual-implementation architecture:
- **Path A (External / Black-Box Reference):** `liboqs` dynamic library (Open Quantum Safe) accessed via C ABI and Python `ctypes`. Used for standard baseline measurements, API/boundary testing, Level 1 input fault injection, and cross-validation oracle.
- **Path B (Source-Level Research Implementation):** Pure C90 source code from the Linux Foundation Post-Quantum Cryptography Alliance (PQCA), compiled natively and instrumented for Level 2 (memory buffers), Level 3 (intermediate mathematical states), and algorithmic fault resilience.

---

## 2. Implementation Specifications

### Implementation A: Open Quantum Safe (`liboqs`)
```text
Implementation: liboqs
Repository: https://github.com/open-quantum-safe/liboqs
Version: 0.16.0
Commit: Homebrew bottle release 0.16.0 (git tag 0.16.0)
License: MIT License
Algorithm: ML-KEM-512, ML-KEM-768, ML-KEM-1024, ML-DSA-44, ML-DSA-65, ML-DSA-87
Standard: NIST FIPS 203 (ML-KEM), NIST FIPS 204 (ML-DSA)
Reference: Open Quantum Safe project documentation and releases
Optimizations: Auto-detected ARM64 NEON optimizations enabled in dynamic library
Platform: macOS 27.0 (Darwin 27.0.0, arm64, Apple M1)
Compiler: Apple Clang 21.0.0
Modifications: None (unmodified upstream binary library)
Reason for modifications: N/A - Path A serves strictly as an uncorrupted external oracle.
```

### Implementation B1: `mlkem-native` (PQCA / Linux Foundation)
```text
Implementation: mlkem-native
Repository: https://github.com/pq-code-package/mlkem-native
Version: Development trunk (main branch)
Commit: fc269bc2d1068486625a3775310c2c1f28d74732
Date: 2026-09-27
License: Apache-2.0 / ISC / MIT
Algorithm: ML-KEM-512, ML-KEM-768, ML-KEM-1024
Standard: NIST FIPS 203 (August 2024 final standard)
Reference: Derived from PQ-Crystals Kyber reference implementation; formally verified with CBMC
Optimizations: C90 portable reference with optional native ARM64 NEON assembly
Platform: macOS 27.0 (Darwin 27.0.0, arm64, Apple M1)
Compiler: Apple Clang 21.0.0
Modifications: None initially; cleanly segregated for research instrumentation hooks
Reason for modifications: Exposes internal NTT butterfly loops, CBD sampling, matrix multiplication, and FO re-encryption checks for Level 2 and Level 3 fault injection.
```

### Implementation B2: `mldsa-native` (PQCA / Linux Foundation)
```text
Implementation: mldsa-native
Repository: https://github.com/pq-code-package/mldsa-native
Version: Development trunk (main branch)
Commit: 14d195a82dd27ed6bac35b403f5386bf43a893d3
Date: 2026-09-23
License: Apache-2.0 / ISC / MIT
Algorithm: ML-DSA-44, ML-DSA-65, ML-DSA-87
Standard: NIST FIPS 204 (August 2024 final standard)
Reference: Derived from PQ-Crystals Dilithium reference implementation; formally verified with CBMC
Optimizations: C90 portable reference with optional native ARM64 NEON assembly
Platform: macOS 27.0 (Darwin 27.0.0, arm64, Apple M1)
Compiler: Apple Clang 21.0.0
Modifications: None initially; cleanly segregated for research instrumentation hooks
Reason for modifications: Exposes rejection sampling loop counters, infinity norm checks, HighBits/LowBits decomposition, and hint generation for Level 2 and Level 3 fault injection.
```

---

## 3. Relationship to Standards and Cross-Validation

Both Path A and Path B implement the exact finalized NIST standards:
- **ML-KEM (FIPS 203):** Prime modulus $q=3329$, ring $R_q = \mathbb{Z}_q[X]/(X^{256}+1)$, Centered Binomial Distribution with $\eta_1, \eta_2$, Fujisaki-Okamoto transform with implicit rejection.
- **ML-DSA (FIPS 204):** Prime modulus $q=8380417$, ring $R_q = \mathbb{Z}_q[X]/(X^{256}+1)$, Fiat-Shamir with Aborts, infinity-norm bound checks, context string support.

Prior to introducing any fault instrumentation, Path B outputs are verified for strict byte-level interoperability against Path A (`liboqs`) and NIST Known Answer Tests (KAT).
