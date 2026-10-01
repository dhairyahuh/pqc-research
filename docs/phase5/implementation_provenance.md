# Phase 5: Implementation Provenance and Independence Analysis

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Phase:** 5 — Cross-Implementation Fault-Surface Validation  
**Date:** October 1, 2026  
**Status:** COMPLETED  

---

## 1. Objective

Determine the actual implementation lineage, selected backend, shared code paths, and
true independence of every tested implementation and configuration before conducting
any cross-implementation comparison.

---

## 2. Tested Implementations

### 2.1 Implementation A: mlkem-native / mldsa-native (C Reference Path)

| Property | Value |
|:---|:---|
| **Repository** | `https://github.com/pq-code-package/mlkem-native` (ML-KEM) |
| | `https://github.com/pq-code-package/mldsa-native` (ML-DSA) |
| **Version** | Vendored snapshot in `algorithms/source_ref/mlkem/` and `algorithms/source_ref/mldsa/` |
| **Build mode** | Single Compilation Unit (SCU), C reference backend only |
| **Compiler** | Apple clang 21.0.0 (clang-2100.1.1.101) |
| **Target** | `arm64-apple-darwin27.0.0` |
| **Optimization** | `-O3 -std=c99` |
| **Native backends** | `MLK_CONFIG_USE_NATIVE_BACKEND_ARITH` NOT set → C reference fallback |
| **Instrumentation** | Source-level fault hooks via `MLKEM_RESEARCH_FAULT_HOOKS` / `MLDSA_RESEARCH_FAULT_HOOKS` |
| **NTT implementation** | C reference: scalar Cooley-Tukey butterflies with `fqmul()` |
| **Parameter sets** | ML-KEM-512/768/1024 via `MLK_CONFIG_PARAMETER_SET`; ML-DSA-44/65/87 via `MLD_CONFIG_PARAMETER_SET` |

### 2.2 Implementation B: liboqs 0.16.0 (Pre-Built Binary)

| Property | Value |
|:---|:---|
| **Package** | `liboqs 0.16.0` via Homebrew |
| **Library** | `/opt/homebrew/lib/liboqs.0.16.0.dylib` |
| **Build date** | September 30, 2026 |
| **Compiler** | Unknown (Homebrew build, likely Apple clang) |
| **Target** | `arm64-apple-darwin` (AArch64) |
| **ML-KEM backend** | `PQCP_MLKEM_NATIVE` with `_AARCH64` suffix — **mlkem-native AArch64 assembly path** |
| **ML-DSA backend** | `PQCP_MLDSA_NATIVE` with `_AARCH64` suffix — **mldsa-native AArch64 assembly path** |
| **Kyber backend** | `PQCLEAN_KYBER*_AARCH64` (legacy Kyber, distinct from ML-KEM FIPS 203) |
| **ARM NEON** | `OQS_USE_ARM_NEON_INSTRUCTIONS` is UNDEF in config — assembly path likely uses raw AArch64 intrinsics |
| **Instrumentation** | None — opaque pre-compiled binary, no fault hooks available |
| **Parameter sets** | ML-KEM-512/768/1024 (`OQS_KEM_ml_kem_*`); ML-DSA-44/65/87 (`OQS_SIG_ml_dsa_*`) |

---

## 3. Implementation Independence Matrix

| Dimension | Implementation A (mlkem-native C ref) | Implementation B (liboqs 0.16.0) | Independence Assessment |
|:---|:---|:---|:---|
| **Algorithm Source** | pq-code-package mlkem-native / mldsa-native | pq-code-package mlkem-native / mldsa-native **via liboqs wrapper** | **SAME ALGORITHMIC SOURCE** |
| **NTT Code** | C reference scalar butterflies | AArch64 assembly NTT (`ntt_aarch64_asm`) | **Different execution path** |
| **Polynomial Arithmetic** | C reference `basemul` / `poly_pointwise_montgomery` | AArch64 assembly `poly_pointwise_montgomery_aarch64_asm` | **Different execution path** |
| **CBD / Noise Sampling** | C reference `cbd2()` / `cbd3()` | Shared C path (no assembly override observed) | **Likely same code** |
| **Hashing (FIPS 202)** | C reference SHAKE/SHA3 | liboqs OpenSSL-backed or C fallback | **Potentially different** |
| **Random Number Generation** | Custom `randombytes()` bridge | `OQS_randombytes()` | **Different** |
| **Build Compiler** | Apple clang 21.0.0, known | Homebrew build, likely Apple clang, version unknown | **Potentially same compiler** |
| **Optimization Level** | `-O3` (known) | Unknown (Homebrew default) | **Unknown** |
| **Fault Instrumentation** | Full source-level hooks at NTT, CBD, PolyMul, FO, norm checks | None — opaque binary | **Asymmetric** |
| **API Surface** | Direct function calls (`mlkem_keypair_derand`, etc.) | OQS wrapper API (`OQS_KEM_ml_kem_768_*`) | **Different API** |

---

## 4. Critical Finding: Shared Algorithmic Source

**liboqs 0.16.0 does NOT provide an independent ML-KEM or ML-DSA implementation.**

Symbol analysis of `/opt/homebrew/lib/liboqs.0.16.0.dylib` reveals:

```
_PQCP_MLKEM_NATIVE_MLKEM768_AARCH64_ntt_aarch64_asm
_PQCP_MLKEM_NATIVE_MLKEM768_AARCH64_indcpa_enc
_PQCP_MLKEM_NATIVE_MLKEM768_AARCH64_indcpa_dec
_PQCP_MLDSA_NATIVE_MLDSA65_AARCH64_ntt_aarch64_asm
_PQCP_MLDSA_NATIVE_MLDSA65_AARCH64_poly_ntt
_PQCP_MLDSA_NATIVE_MLDSA65_AARCH64_keypair
```

These are **mlkem-native and mldsa-native symbols** with the AArch64 backend selected at liboqs build time.

### What this means for the research:

1. **The two "implementations" share the same mathematical algorithm, same specification interpretation, same constant tables, and same high-level control flow.**
2. **They differ in execution path**: C reference scalar operations vs. AArch64 assembly vectorized operations.
3. **This is a backend comparison, not an independent implementation comparison.**
4. **Cross-implementation reproducibility (RQ4) cannot be fully answered** because no genuinely independent implementation is available in this environment.

### What the comparison CAN validly assess:

| Valid Comparison | Rationale |
|:---|:---|
| API-level functional equivalence | Same algorithm, different backend → should produce identical outputs for identical inputs |
| Backend-dependent fault surface differences | AArch64 assembly uses different register allocation, SIMD lanes, and instruction scheduling |
| Compiler-induced behavioral variation | Same C source compiled with different options may produce different fault surfaces |
| Instrumentation transparency | Verify that fault hooks do not alter baseline cryptographic behavior |

### What the comparison CANNOT validly claim:

| Invalid Claim | Reason |
|:---|:---|
| "Independent implementation confirms our results" | Same source codebase |
| "Fault behavior is universal across all ML-KEM implementations" | Only one algorithmic source tested |
| "Implementation diversity provides redundancy" | No true diversity exists between these paths |

---

## 5. Alternative Independent Implementations (Assessment)

| Implementation | Algorithm | Language | Status | Independence |
|:---|:---|:---|:---|:---|
| **CRYSTALS-Kyber reference** (pq-crystals) | Kyber (pre-FIPS) | C | Available in liboqs as `PQCLEAN_KYBER*_AARCH64` | **Partially independent** (pre-FIPS, different constant generation) |
| **BoringSSL ML-KEM** | ML-KEM (FIPS 203) | C | Not installed | **Genuinely independent** |
| **AWS-LC ML-KEM** | ML-KEM (FIPS 203) | C | Not installed | **Potentially independent** |
| **rustpq / pqcrypto** | ML-KEM | Rust (wraps C) | Not installed | **Wrapper, not independent** |
| **CRYSTALS-Dilithium reference** (pq-crystals) | Dilithium (pre-FIPS) | C | Not available separately | **Pre-FIPS, partially independent** |

**Assessment:** No genuinely independent FIPS 203/204 implementation is available in the current environment. The research must document this limitation and frame cross-implementation results accordingly.

---

## 6. Comparability Classification

For every experimental comparison in Phase 5, the following classification applies:

| Classification | Definition | Applicable When |
|:---|:---|:---|
| **Backend Equivalence Test** | Same algorithm, same source, different execution backend | C ref vs AArch64 asm within mlkem-native/mldsa-native |
| **Compiler Sensitivity Test** | Same source, different compiler or optimization settings | `-O0` vs `-O3`, debug vs release |
| **Instrumentation Transparency Test** | Verify fault hooks do not alter correct behavior | Instrumented vs clean builds with identical inputs |
| **API Interoperability Test** | Keys/ciphertexts/signatures cross-validated between API paths | Path A (liboqs) vs Path B (source-ref) |
| **NOT: Independent Replication** | Two distinct algorithmic implementations producing equivalent results | Not achievable with available tools |

---

## 7. Provenance Verification Commands

```bash
# Verify liboqs ML-KEM backend
nm /opt/homebrew/lib/liboqs.dylib | grep "MLKEM_NATIVE.*768"

# Verify liboqs ML-DSA backend  
nm /opt/homebrew/lib/liboqs.dylib | grep "MLDSA_NATIVE.*65"

# Verify build config
grep "ml_kem\|ml_dsa" /opt/homebrew/include/oqs/oqsconfig.h

# Verify no AVX2 (x86) — only AArch64
grep "AVX2\|ARM_NEON\|aarch64" /opt/homebrew/include/oqs/oqsconfig.h
```
