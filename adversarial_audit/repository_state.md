# Repository State and Component Inventory

**Audit Date:** 2026-10-02  
**Repository URL:** `https://github.com/dhairyahuh/pqc-research.git`  
**Current Branch:** `space-resilience-framework`  
**Baseline Commit:** `ca38dec3b76f54e405a268c3f06a5f04a13e3660`  
**Target Cryptosystem:** ML-KEM-768 (NIST FIPS 203)  
**Host Architecture:** Apple Silicon ARM64 (macOS 15.x / Darwin 24)  
**Toolchain:** Apple Clang version 17.0.0 (`clang-1700.0.13.5`), Python 3.12.7  

---

## 1. Working Tree Status

```text
On branch space-resilience-framework
Your branch is up to date with 'origin/space-resilience-framework'.

Changes not staged for commit:
  modified:   README.md
  modified:   experiments/fault_injection/mlkem768_internal_fault_experiment.c
  modified:   experiments/system_model/spacecraft_protocol_sim.py
  modified:   fault_injection/fault_models/fault_definitions.py
  modified:   results/spacecraft_protocol_desync_results.json
  modified:   tests/test_fips_kats.c

Untracked files:
  adversarial_audit/
  docs/phase4b-validation-audit.md
  experiments/mathematics/audit_correlated_faults.c
  research_redesign/CANDIDATE_RESEARCH_GAPS.csv
  research_redesign/LITERATURE_MATRIX_RADIATION_PQC.csv
  research_redesign/SYSTEMATIC_RESEARCH_GAP_REPORT.md
  results/mlkem768_internal_fault_validation.json
  tests/kat_mldsa44.c
  tests/kat_mldsa65.c
  tests/kat_mldsa87.c
  tests/kat_mlkem1024.c
  tests/kat_mlkem512.c
  tests/kat_mlkem768.c
  tests/kat_runners.h
```

All production cryptographic code in `algorithms/source_ref/mlkem/src/` is in its clean, pristine baseline state without uncommitted modifications.

---

## 2. Build Configuration

- **C Compiler:** `clang` (Apple Clang C11 / C99 mode)
- **Primary Optimization Flags:** `-O3 -Wall -Wextra -std=c11 -I/opt/homebrew/include`
- **External Dependencies:** `liboqs` (`-L/opt/homebrew/lib -loqs`)
- **Macro Configuration for Path B (mlkem-native):**
  - Parameter Set: `-DMLK_CONFIG_PARAMETER_SET=768`
  - Namespace Prefix: `-DMLK_CONFIG_NAMESPACE_PREFIX=mlkem` (or `mlkem768` for isolated harnesses)
  - Research Hook Instrumentation: `-DMLKEM_RESEARCH_FAULT_HOOKS`

---

## 3. Core Component Inventory

| Component Category | File Path | Current Line Numbers | Primary Symbols / Functions |
| :--- | :--- | :--- | :--- |
| **Twiddle Constants Storage** | [`algorithms/source_ref/mlkem/src/zetas.inc`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/zetas.inc) | Lines 17–30 | `static MLK_ALIGN const int16_t mlk_zetas[128]` |
| **Forward Cooley-Tukey NTT** | [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c) | Lines 378–416<br>Lines 427–450<br>Lines 464–470 | `mlk_ntt_butterfly_block`<br>`mlk_ntt_layer`<br>`mlk_poly_ntt_c` |
| **Inverse Gentleman-Sande NTT** | [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c) | Lines 533–599 | `mlk_poly_invntt_tomont_c` |
| **Mid-NTT Forward Hooks** | [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) | Lines 203–247<br>Lines 250–272<br>Lines 275–300 | `hook_mid_ntt_pre_butterfly`<br>`hook_mid_ntt_post_mul`<br>`hook_mid_ntt_butterfly` |
| **Mid-InvNTT Inverse Hooks** | [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) | Lines 709–742<br>Lines 744–763<br>Lines 765–802 | `hook_mid_invntt_pre_butterfly`<br>`hook_mid_invntt_post_diff`<br>`hook_mid_invntt_butterfly` |
| **Dead Reference Twiddle Array** | [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) | Lines 555–568 | `static const int16_t g_trusted_zetas[128]` (Unreferenced) |
| **Forward NTT Monitor & Rollback** | [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) | Lines 600–664 | `native_ntt_monitor_butterfly` |
| **Inverse NTT Monitor & Rollback** | [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c) | Lines 804–874 | `native_invntt_monitor_butterfly` |
| **Fujisaki-Okamoto Re-encryption** | [`algorithms/source_ref/mlkem/src/kem.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c) | Lines 454–466 | `mlk_indcpa_enc`, `mlk_ct_memcmp` |
| **Dual-Rail Verification & Fail-Stop** | [`algorithms/source_ref/mlkem/src/kem.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c) | Lines 476–510<br>Line 519 | Reverse loop compare, persistent flag quench, `mlk_ct_cmov_zero` |
| **Controlled Fault Harness** | [`experiments/mathematics/audit_correlated_faults.c`](file:///Users/dhairyajain/Desktop/pqc%20research/experiments/mathematics/audit_correlated_faults.c) | Lines 1–349 | `run_audit_suite` (EXP 1 through EXP 6) |
| **16-Class Extended Campaign Harness** | [`experiments/phase7j/phase7j_independent_validator.c`](file:///Users/dhairyajain/Desktop/pqc%20research/experiments/phase7j/phase7j_independent_validator.c) | Lines 215–435 | 1,600-trial validator (J01 through J16) |
| **Comprehensive Regression Suite** | [`tests/test_fips_kats.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tests/test_fips_kats.c) | Lines 1–69 | All 6 FIPS 203 & 204 KAT runners |
| **Raw Extended Trial Dataset** | `results/phase7j/raw/phase7j_extended_trials.json` | Lines 1–1601 | 1,600 raw trial records across 16 threat classes |
