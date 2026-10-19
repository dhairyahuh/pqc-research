# Source Code & Architecture Index

**Repository:** `pqc-research`  
**Active Branch:** `space-resilience-framework`  
**Author:** Dhairya Jain  
**Handover Recipient:** Ayush  
**Date:** October 2026  

This document provides a function-level, structural index of the primary source code files, experiment harnesses, fault-injection hooks, and verification oracles. All line numbers and identifiers are verified directly from the current repository state.

---

## 1. Core Cryptographic & Resilience Source Code

### 1.1 `algorithms/source_ref/mlkem/src/poly.c` (681 lines)
- **Role:** Implementation of forward Cooley-Tukey NTT and inverse Gentleman-Sande NTT polynomial transformations over $R_q = \mathbb{Z}_{3329}[X]/(X^{256} + 1)$.
- **Key Functions & Line Ranges:**
  - `mlk_poly_sub(mlk_poly *r, const mlk_poly *b)` (Lines 256–265): Subtracts two polynomials in standard representation.
  - `#include "zetas.inc"` (Line 267): Imports the 128-element twiddle factor table.
  - `mlk_poly_ntt_c(mlk_poly *p)` (Lines 475–508): Static forward Cooley-Tukey NTT implementation across 7 butterfly stages.
  - `mlk_poly_ntt(mlk_poly *r)` (Lines 510–525): Top-level wrapper called by `mlk_polyvec_ntt`. Contains fault hook instrumentation.
  - `mlk_poly_invntt_tomont_c(mlk_poly *p)` (Lines 617–654): Static inverse Gentleman-Sande NTT with Montgomery factor scaling.
  - `mlk_poly_invntt_tomont(mlk_poly *r)` (Lines 656–670): Top-level wrapper for inverse transform called by `mlk_indcpa_dec` and `mlk_indcpa_enc`.
- **Instrumentation & Hook Integration:**
  Each butterfly invocation interacts with `algorithms/source_ref/mlkem_fault_hooks.c` to:
  1. Record snapshot registers: `u_saved = *r0`, `v_saved = *r1`, `zeta_saved = zeta`.
  2. Compute butterfly arithmetic.
  3. Evaluate decoupled invariant checks.
  4. Perform in-place register rollback if a mismatch occurs and `retry_count < 2`.
  5. Escalate to fail-stop containment if `retry_count >= 2`.

---

### 1.2 `algorithms/source_ref/mlkem/src/kem.c` (544 lines)
- **Role:** ML-KEM-768 top-level encapsulation and decapsulation orchestration conforming to NIST FIPS 203.
- **Key Functions & Line Ranges:**
  - `crypto_kem_keypair(...)` (Lines 350–390): Generates public encapsulation key and private decapsulation key.
  - `crypto_kem_enc(...)` (Lines 395–435): Encapsulates a shared key, generating ciphertext $c = (c_1, c_2)$.
  - `crypto_kem_dec(...)` (Lines 440–460): Standard API entry point calling `mlk_kem_dec_monitored`.
  - `mlk_kem_dec_monitored(...)` (Lines 462–525): The core monitored decapsulation routine cited in `paper/manuscript.md` (Lines 209–250).
- **Critical Logic Breakdown in `mlk_kem_dec_monitored`:**
  - **Line 466:** Forward ciphertext comparison: `fail = mlk_ct_memcmp(ct, tmp, MLKEM_INDCCA_CIPHERTEXTBYTES);`
  - **Lines 476–481:** Reverse-order dual-rail bitwise comparison to prevent single-event predicate flips:
    ```c
    uint8_t fail_chk = 0;
    for (size_t i = 0; i < MLKEM_INDCCA_CIPHERTEXTBYTES; i++) {
      fail_chk |= (ct[MLKEM_INDCCA_CIPHERTEXTBYTES - 1 - i] ^ tmp[MLKEM_INDCCA_CIPHERTEXTBYTES - 1 - i]);
    }
    fail_chk = mlk_ct_cmask_nonzero_u8(fail_chk);
    ```
  - **Lines 484–494:** Persistent monitor escalation check: If persistent fault counters in forward or inverse monitors exceed 0, forces `fail = 0xFF` and `internal_status = MLK_DECAPS_STATUS_FAULT`.
  - **Lines 497–504:** Dual-rail consistency check: If `fail != fail_chk`, forces `fail = 0xFF`.
  - **Lines 512–516:** Deterministic derivation of implicit rejection key into `ss`: `K_rej = SHAKE256(z || c)`.
  - **Line 519:** Constant-time conditional move selecting authentic key `kr` into return buffer `ss` only if `fail == 0`:
    ```c
    mlk_ct_cmov_zero(ss, kr, MLKEM_SYMBYTES, fail);
    ```

---

### 1.3 `algorithms/source_ref/mlkem/src/indcpa.c` (652 lines)
- **Role:** IND-CPA underlying public-key encryption and decryption routines where the 11 transform call sites reside.
- **Authoritative Transform Call Sites (Table 1 in Manuscript):**
  - **Decapsulation Forward NTT:** Line 619 (`mlk_indcpa_dec`) calls `mlk_polyvec_ntt(b)` (transforms 3-poly ciphertext vector $\mathbf{u}$, executing $3 \times 896 = 2{,}688$ Cooley-Tukey butterflies).
  - **Decapsulation Inverse NTT:** Line 622 (`mlk_indcpa_dec`) calls `mlk_poly_invntt_tomont(sb)` (transforms 1-poly decrypted message difference, executing 896 Gentleman-Sande butterflies).
  - **Re-encryption Forward NTT:** Line 558 (`mlk_indcpa_enc`) calls `mlk_polyvec_ntt(sp)` (transforms 3-poly ephemeral noise vector $\mathbf{r}$, executing $3 \times 896 = 2{,}688$ Cooley-Tukey butterflies).
  - **Re-encryption Inverse NTT (Candidate Vector):** Line 564 (`mlk_indcpa_enc`) calls `mlk_polyvec_invntt_tomont(b)` (transforms candidate 3-poly vector $\mathbf{u}'$, executing $3 \times 896 = 2{,}688$ Gentleman-Sande butterflies).
  - **Re-encryption Inverse NTT (Candidate Scalar):** Line 565 (`mlk_indcpa_enc`) calls `mlk_poly_invntt_tomont(v)` (transforms candidate scalar poly $v'$, executing 896 Gentleman-Sande butterflies).
  - **Total Accounting:** Exactly **11 polynomial transforms** and **9,856 total butterflies**.

---

### 1.4 `algorithms/source_ref/mlkem_fault_hooks.c` (874 lines) & `.h` (289 lines)
- **Role:** Dedicated runtime invariant monitor, fault injector, snapshot storage, and retry engine.
- **Key Modules & Logic:**
  - **Snapshot Storage:** Thread-safe or local register-allocated storage for butterfly operands: `u_saved`, `v_saved`, `zeta_saved`.
  - **Forward CT Invariant Check:**
    $$\Delta_{\text{sum}} = (r_0 + r_1 - 2u_{\text{saved}}) \pmod q$$
    $$\Delta_{\text{mul}} = (r_0 - r_1 - 2(v_{\text{saved}} \cdot \zeta)) \pmod q$$
    Verified using Montgomery multiplication and branch-free accumulation.
  - **Inverse GS Decoupled Check:**
    Check 1 (Adder Rail): $r_0 \equiv u_{\text{saved}} + v_{\text{saved}} \pmod q$
    Check 2 (Multiplier Rail): $r_1 \equiv (v_{\text{saved}} - u_{\text{saved}}) \cdot \zeta \pmod q$
    Completely avoids runtime modular inversion or division in $\mathbb{Z}_q$.
  - **Rollback Engine:**
    Tracks `retry_count`. On first mismatch (`retry_count == 0`), restores `*r0 = u_saved`, `*r1 = v_saved`, increments counter, and triggers in-place re-execution.
    On recurring mismatch (`retry_count >= 2`), increments `persistent_count`, flags error status, and escalates to top-level containment.
  - **Dynamic Allocation Audit:** Contains **zero** calls to dynamic heap allocators (`malloc`, `calloc`, `realloc`, `free`). Memory overhead is strictly $0\text{ B}$.

---

### 1.5 `algorithms/source_ref/mlkem/src/zetas.inc` (63 lines)
- **Role:** 128-element array of Montgomery-domain twiddle factors $\zeta \in \mathbb{Z}_{3329}$.
- **Research Arm (`MLKEM_RESEARCH_RELOCATE_ZETAS`):**
  Defines an isolated, non-const $16\text{ KB}$ page-aligned structure (`mlk_isolated_zetas_page_t`) used during Phase 15A/15Q memory fault experiments to prevent undefined behavior (UB) and operating system memory protection faults when injecting bitflips into twiddle factor storage.

---

## 2. Reproduction Harnesses & Verification Tools

### 2.1 `phase18_audit/production_reproducer.c` (230 lines)
- **Role:** Standalone cleanroom C test harness compiled directly against production object files (`bin/obj/mlkem768_inst.o`, `bin/obj/mlkem_fault_hooks.o`).
- **Functionality:**
  - Executes the 400 cleanroom production trials (F12, F4, F5A, F5B).
  - Employs independent oracles to verify that F4 transient faults recover golden authentic keys ($K_{\text{valid}}$) and that F5 persistent faults deterministically emit standard implicit rejection keys ($K_{\text{rej}}$).
  - Logs structured trial results to `phase18_audit/raw_production_trials.csv`.

### 2.2 `tests/test_fips_kats.c` (69 lines) & `tests/kat_mlkem*.c`
- **Role:** Official NIST FIPS 203 & 204 Known Answer Test (KAT) validation suite.
- **Functionality:** Validates deterministic KeyGen, Encapsulation, Decapsulation, Signing, and Verification against official NIST test vectors across all parameter sets (ML-KEM-512/768/1024, ML-DSA-44/65/87).

### 2.3 `experiments/fault_injection/mlkem768_internal_fault_experiment.c` (490 lines)
- **Role:** Internal fault simulation harness used during Phase 4B and Level 1 exploratory fault campaigns.
- **Capabilities:** Injects targeted single-bit and multi-bit disturbances across intermediate polynomial arrays, NTT stages, and verification predicates.

### 2.4 `experiments/system_model/spacecraft_protocol_sim.py` (323 lines)
- **Role:** Event-driven simulation modeling a spacecraft communication session using CCSDS space packets over an intermittent, high-latency satellite link (Paper Track 2).
- **Evaluates:** How cryptographic aborts vs. localized retries impact protocol frame retransmission, timeout cascades, and link availability.
