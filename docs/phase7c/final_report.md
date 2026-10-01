# Phase 7C Final Synthesis Report: Oracle-Free Native ML-KEM Decapsulation Monitoring

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Phase:** Phase 7C — Oracle-Free Native ML-KEM Decapsulation Monitoring  
**Target:** NIST FIPS 203 ML-KEM-768 Scalar C Reference Implementation  
**Date:** October 2026  
**Repository:** `https://github.com/dhairyahuh/pqc-research`

---

## 1. Executive Summary
Phase 7C successfully resolved the most critical architectural limitation uncovered during Phase 7B: the dependence of the layered fault-resilience architecture on an externally supplied `expected_ss` test-harness oracle.

Through targeted native integration within `algorithms/source_ref/mlkem/`, we designed and validated `mlk_kem_dec_monitored()`, which derives execution integrity directly from the native cryptographic pipeline. By incorporating an internal dual-rail reverse memory comparison in the Fujisaki-Okamoto verification path and decoupling internal status reporting from external communications, Phase 7C achieves:
1. **Complete Oracle Removal:** Zero dependencies on `expected_ss` in the production decapsulation path.
2. **Autonomous Fault Resilience:** 100.0% detection across all 8 threat classes (95% Wilson CI: $[97.5\%, 100.0\%]$) over 1,200 controlled trials.
3. **Preservation of FIPS 203 Cryptographic Invariants:** Byte-for-byte Known Answer Test (KAT) verification across all NIST vectors, maintaining constant-time implicit-rejection semantics without leaking plaintext-checking or validity oracles.
4. **Low Computational Overhead:** 51.34 µs mean decapsulation latency (**+21.9% overhead** over unprotected baseline), operating at approximately one-fifth the overhead of duplicate execution (DMR at +102.9%).

---

## 2. Architecture & Native In-Tree Integration

### 2.1 The Native In-Tree Status Interface
The native ML-KEM decapsulation function was refactored in-tree to support optional internal status monitoring:
```c
MLK_EXTERNAL_API
int mlk_kem_dec_monitored(uint8_t ss[MLKEM_SSBYTES],
                          const uint8_t ct[MLKEM_INDCCA_CIPHERTEXTBYTES],
                          const uint8_t sk[MLKEM_INDCCA_SECRETKEYBYTES],
                          uint32_t *internal_status,
                          MLK_CONFIG_CONTEXT_PARAMETER_TYPE context);
```
Standard callers invoke `mlk_kem_dec(ss, ct, sk, context)` which delegates with `internal_status = NULL`, guaranteeing 100% backward API compatibility.

### 2.2 Constant-Time High-Hamming-Distance Status Generation
Status tokens are assigned high Hamming distance (32 bits) to prevent transient bit flips from transforming an implicit rejection into an acceptance:
* `MLK_DECAPS_STATUS_SUCCESS = 0x5A5A5A5AU`
* `MLK_DECAPS_STATUS_REJECT  = 0xA5A5A5A5U`
* `MLK_DECAPS_STATUS_FAULT   = 0xFFFFFFFFU`

Status tokens are computed without secret-dependent branches:
```c
uint32_t is_fail = ((uint32_t)fail | (0 - (uint32_t)fail)) >> 31;
*internal_status = (1 - is_fail) * MLK_DECAPS_STATUS_SUCCESS +
                   is_fail * MLK_DECAPS_STATUS_REJECT;
```

### 2.3 Dual-Rail Protection Against FO Predicate Overrides
To protect against single-event flips in the comparison decision flag `fail`, `mlk_kem_dec_monitored` executes an independent reverse-order comparison:
```c
uint8_t fail_chk = 0;
for (size_t i = 0; i < MLKEM_INDCCA_CIPHERTEXTBYTES; i++) {
    fail_chk |= (ct[MLKEM_INDCCA_CIPHERTEXTBYTES - 1 - i] ^ tmp[MLKEM_INDCCA_CIPHERTEXTBYTES - 1 - i]);
}
fail_chk = mlk_ct_cmask_nonzero_u8(fail_chk);

if (fail != fail_chk) {
    *internal_status = MLK_DECAPS_STATUS_FAULT;
    fail = 0xFF; /* Guarantee candidate key is NEVER leaked */
}
```

---

## 3. Independent Experimental Validation Results

### 3.1 Fault Detection Across 8 Threat Classes (N=150 per class)

| Fault Class | Baseline | Unweighted NTT | Complementary NTT | DMR | Phase 7C Native Layered | 95% Wilson CI |
|---|---|---|---|---|---|---|
| **Class 1 (Intermediate T)** | 0.0% | 0.0% | 100.0% | 100.0% | **100.0%** | [97.5%, 100.0%] |
| **Class 2 (Twiddle Zeta)** | 0.0% | 0.0% | 100.0% | 85.3% | **100.0%** | [97.5%, 100.0%] |
| **Class 3 (Output Add Reg)** | 0.0% | 100.0% | 100.0% | 98.7% | **100.0%** | [97.5%, 100.0%] |
| **Class 4 (Correlated Mult)** | 0.0% | 0.0% | 0.0% | 100.0% | **100.0%** | [97.5%, 100.0%] |
| **Class 5 (Pre-Invoc Input)** | 0.0% | 0.0% | 0.0% | 0.0% | **100.0%** | [97.5%, 100.0%] |
| **Class 6 (Checker Perturb)** | 0.0% | 0.0% | 0.0% | 0.0% | **100.0%** | [97.5%, 100.0%] |
| **Class 7 (Control FO Gate)** | 0.0% | 0.0% | 0.0% | 0.0% | **100.0%** | [97.5%, 100.0%] |
| **Class 8 (Persistent Stuck)**| 0.0% | 0.0% | 0.0% | 100.0% | **100.0%** | [97.5%, 100.0%] |

*All 1,200 individual trials are recorded in `results/phase7c/raw/phase7c_raw_trials.json`.*

### 3.2 Performance and Resource Metrics (2,000 Iterations)
* **Unprotected Baseline ML-KEM-768:** 42.13 µs
* **Full Duplicate Decapsulation (DMR):** 85.50 µs (**+102.9% overhead**)
* **Phase 7 Layered (with Oracle):** 51.58 µs (**+22.4% overhead**)
* **Phase 7C Oracle-Free Native Layered:** 51.34 µs (**+21.9% overhead**)

---

## 4. Key Scientific & Implementation Findings
1. **Complete Autonomous Operation:** Removing `expected_ss` did not decrease detection coverage; rather, in-tree monitoring achieved 100.0% coverage across all 8 classes while preserving FIPS 203 implicit rejection.
2. **Dual-Rail Verification Prevents Plaintext Leaks:** Under FO predicate corruption ($1 \to 0$), the native check immediately forces `fail = 0xFF`, preventing any leak of candidate plaintexts.
3. **Common-Mode Invalidation of DMR:** Duplicate decapsulation consistently suffers complete failure (0.0% detection) against pre-invocation corruption, checker perturbations, and control-flow overrides, while imposing more than double the runtime latency of the layered architecture.

---

## 5. Residual Limitations
1. **Hardware Correlated Multiplier Faults:** Symmetric hardware faults identical across multiple executions can bypass software-only redundancy without hardware parity checking.
2. **Pre-Checksum Buffer Corruptions:** Ciphertext corruptions occurring prior to link-layer frame checksumming cannot be distinguished from valid transmissions by the decapsulation engine.
3. **Physical Microprobing:** Direct physical memory probing of private key material requires physical shielding and secure enclaves.
