# Phase 5: Common Experimental Framework

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Phase:** 5 — Cross-Implementation Fault-Surface Validation  
**Date:** October 1, 2026  
**Status:** COMPLETED  

---

## 1. Framework Objective

Define an implementation-neutral experiment schema that:

1. Preserves the Phase 4 common 8-stage fault pipeline.
2. Accommodates backend-level differences between C reference and AArch64 assembly paths.
3. Records sufficient metadata for reproducibility.
4. Distinguishes between what is being compared and what cannot be compared.

---

## 2. Experiment Record Schema

Each Phase 5 trial record contains:

```json
{
  "trial_id": "p5-kem-ntt-001",
  "algorithm": "ML-KEM-768",
  "implementation": "mlkem-native-c-ref",
  "implementation_version": "vendored-snapshot",
  "build_config": {
    "compiler": "clang-21.0.0",
    "target": "arm64-apple-darwin27",
    "optimization": "-O3",
    "flags": "-DMLK_CONFIG_PARAMETER_SET=768 -DMLKEM_RESEARCH_FAULT_HOOKS"
  },
  "operation": "NTT (forward, Cooley-Tukey)",
  "sub_operation": "Layer 4, Butterfly 0",
  "mathematical_state": "coefficient r[j] after twiddle multiply",
  "injection_location": "hook_mid_ntt_butterfly, layer=4, butterfly=0",
  "fault_class": "ADDITIVE_GLITCH",
  "fault_magnitude": 1,
  "fault_timing": "TRANSIENT",
  "trial_seed": "0x42424242...",
  "expected_mathematical_effect": "Single coefficient delta=+1 in NTT domain, diffusion to 2^(7-4)=8 time-domain coefficients",
  "observed_output": {
    "key_agreement": false,
    "shared_secret_match": false,
    "fo_verify_result": 1,
    "decaps_output_class": "IMPLICIT_REJECTION"
  },
  "detection_behavior": "FO re-encryption mismatch detected",
  "cryptographic_outcome": "IMPLICIT_REJECTION",
  "execution_status": "COMPLETED",
  "instrumentation_confidence": "HIGH — source-level hook at exact mathematical operation",
  "reproducibility": {
    "deterministic_seed": true,
    "baseline_verified": true,
    "repeat_count": 1000
  }
}
```

---

## 3. Cross-Implementation Mapping Classification

For every cross-implementation comparison, each operation-level mapping is assigned one of these classifications:

| Classification | Symbol | Definition | Example |
|:---|:---:|:---|:---|
| **Exact Semantic Match** | ≡ | Same mathematical operation, same intermediate representation, same code path | `poly_ntt()` in C-ref instrumented vs C-ref clean |
| **Equivalent Mathematical Operation** | ≈ | Same mathematical computation, different execution path | C-ref `fqmul` vs AArch64 `ntt_aarch64_asm` |
| **Approximate Operational Match** | ~ | Similar purpose, different algorithmic detail | C-ref scalar butterfly vs SIMD vectorized butterfly |
| **No Valid Mapping** | ∅ | No corresponding operation in comparison implementation | Internal fault hook injection point → opaque binary |

### Phase 5 Operation Mapping Table

| Operation (C Reference) | liboqs AArch64 Equivalent | Mapping |
|:---|:---|:---:|
| `poly_ntt()` (7-layer C scalar) | `ntt_aarch64_asm` (vectorized) | ≈ |
| `poly_invntt_tomont()` | `intt_aarch64_asm` | ≈ |
| `poly_basemul_cached()` | `poly_pointwise_montgomery_aarch64_asm` | ≈ |
| `fqmul()` (Montgomery multiply) | Inline within asm NTT | ~ |
| `poly_cbd_eta1/eta2()` | C-path CBD (no asm observed) | ≡ |
| `poly_compress_d*()` | C-path compression (no asm observed) | ≡ |
| `indcpa_enc()` | `PQCP_MLKEM_NATIVE_*_indcpa_enc` | ≈ |
| `indcpa_dec()` | `PQCP_MLKEM_NATIVE_*_indcpa_dec` | ≈ |
| `poly_ntt()` (ML-DSA 8-layer) | `ntt_aarch64_asm` (ML-DSA vectorized) | ≈ |
| `poly_chknorm()` (ML-DSA) | `poly_chknorm_aarch64_asm` | ≈ |
| `poly_decompose()` (ML-DSA) | `poly_decompose_88_aarch64_asm` | ≈ |
| Internal fault hook injection | Not available | ∅ |

---

## 4. Experiment Categories

### Category 1: Baseline Equivalence Verification
**Purpose:** Confirm that C-ref and liboqs produce identical cryptographic outputs for identical inputs.
**Method:** Deterministic keygen, encaps/sign with fixed seeds; byte-for-byte comparison.
**Mapping:** ≡ at API level.

### Category 2: Instrumentation Transparency Verification
**Purpose:** Confirm that fault hooks do not alter baseline behavior when no fault is armed.
**Method:** Run instrumented build with `g_mlkem_fault.enabled = false`; compare outputs to clean build.
**Mapping:** ≡ (same code, hooks dormant).

### Category 3: Cross-Backend Fault-Free Statistical Comparison
**Purpose:** Compare timing, output distributions, or internal state behavior between backends.
**Method:** Large-trial statistical comparison of encaps/decaps/sign/verify outcomes.
**Mapping:** ≈ (same math, different execution).

### Category 4: Fault Injection (C Reference Only)
**Purpose:** Reproduce Phase 2–4 fault experiments in the instrumented C-ref build.
**Method:** Arm specific hooks, inject at targeted operations, record outcomes.
**Mapping:** Only applicable to instrumented build (∅ for liboqs).

### Category 5: Compiler Sensitivity
**Purpose:** Measure how compiler optimization changes the observable fault surface.
**Method:** Rebuild C-ref at different optimization levels; compare assembly and behavior.
**Mapping:** ≡ (same source, different compilation).

---

## 5. Constraints and Limitations

1. **No internal fault injection into liboqs:** The pre-compiled binary has no hook points. Fault injection experiments are asymmetric — only the C-ref path can be internally instrumented.
2. **No independent replication:** Both implementations derive from the same algorithmic source (pq-code-package). This cannot be used to claim independent verification.
3. **Deterministic seed bridge:** The C-ref uses `mlkem_keypair_derand()` / `mlkem_enc_derand()`, while liboqs uses `OQS_KEM_ml_kem_768_keypair_derand()`. Seed formats must be verified as compatible.
4. **Statistical pooling:** Results from C-ref and liboqs cannot be pooled as independent observations because they share the same algorithm, constants, and mathematical structure.
5. **Assembly path opacity:** The exact register allocation and instruction scheduling in `ntt_aarch64_asm` cannot be inspected without disassembly.

---

## 6. Raw Data Organization

```
results/phase5/
├── raw/
│   ├── baseline_equivalence.json      # Category 1 results
│   ├── instrumentation_transparency.json  # Category 2 results
│   ├── cross_backend_comparison.json  # Category 3 results
│   ├── fault_reproduction.json        # Category 4 results
│   └── compiler_sensitivity.json      # Category 5 results
└── processed/
    ├── equivalence_summary.csv
    ├── fault_reproduction_summary.csv
    ├── compiler_comparison.csv
    └── cross_implementation_statistical_summary.json
```
