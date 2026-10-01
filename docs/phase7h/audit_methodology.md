# Phase 7H: Independent Audit Methodology & Validation Framework

## 1. Objectives & Scope of Independent Audit

Phase 7H serves as a strict, adversarial, independent audit of the native ML-KEM NTT monitor integration and resilience claims presented in Phase 7G. 

The primary objectives are:
1. **Source-Level Verification**: Trace the complete execution pipeline from public API entry points down to individual Cooley-Tukey butterfly operations, verifying compile-time inclusion versus runtime execution.
2. **Instrumentation Validation**: Confirm whether the claimed 5,376 native butterfly evaluations are genuinely executed in production decapsulation or if any code path bypasses them.
3. **Fault-Injection Mechanism Integrity**: Audit all 8 Phase 7G threat classes to verify that injected faults perturb the actual computation registers rather than simulating status flags.
4. **Rollback & Retry Correctness**: Verify the mathematical soundness, bounds safety, and trust boundaries of in-place register rollback.
5. **Raw Data & Serialization Audit**: Independently inspect the 1,200 raw trial records of Phase 7G for missing records, duplicate IDs, cross-configuration state contamination, and classification anomalies.
6. **Empirical Timing & Statistical Characterization**: Calibrate latency distributions, run-to-run variance, and timing ratios between valid and invalid ciphertexts across 2,000 iterations.

---

## 2. Independent Verification Architecture

The audit separates verification into five independent layers:

```
[Layer 1: Static Code Inspection]
   └── poly.c, kem.c, mlkem_fault_hooks.c, Makefile
   └── Macro definitions (-DMLKEM_RESEARCH_FAULT_HOOKS) vs clean reference

[Layer 2: Architectural Execution Tracing]
   └── Verification of 5,376 forward NTT butterflies (2 vectors x 3 poly x 896 butterflies)
   └── Discovery of 4,480 unmonitored inverse NTT butterflies (5 polynomials)

[Layer 3: Adversarial Boundary Testing]
   └── Mathematical proof of symmetric perturbation blind spot in Difference invariant
   └── Mathematical proof of anti-symmetric perturbation blind spot in Sum invariant
   └── Public API mlkem768_dec(..., NULL) fail-stop bypass audit

[Layer 4: Data Pipeline & Serialization Audit]
   └── experiments/phase7h/audit_analysis.py
   └── Identification of Phase 7G JSON counter cross-contamination bug

[Layer 5: Independent Reproducer Campaign]
   └── experiments/phase7h/phase7h_independent_reproducer.c
   └── 1,200 trials with strictly isolated monitor state per configuration
```

---

## 3. Auditing Environment & Target Platform

- **Operating System**: macOS (Darwin 24.x, Apple Silicon ARM64).
- **Toolchain**: Apple Clang version 17.0.0 (clang-1700.0.13.5).
- **Target Implementation**: In-tree NIST FIPS 203 ML-KEM reference implementation (`algorithms/source_ref/mlkem/`).
- **Compilation Flags**: `-O3 -Wall -Wextra -std=c11 -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem768 -DMLK_CONFIG_PARAMETER_SET=768 -DMLKEM_RESEARCH_FAULT_HOOKS`.
- **Baseline Binaries**: `bin/phase7g_native_validation`, `bin/phase7h_independent_reproducer`.
