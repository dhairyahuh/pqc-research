# Phase 00: Existing Repository Audit Report
## ASTRA-Sec Development — Comprehensive Technical Audit of PQC Implementation

**Author:** ASTRA-Sec Development Agent  
**Date:** November 2026  
**Status:** Complete  
**Target Repository:** `https://github.com/dhairyajain/pqc-research`  
**Inspected Commit:** `b39a18a332642a0ac5c2baade629ee8023e435b1`  
**Active Working Branch:** `space-resilience-framework`

---

## 1. Git Repository State & History

### 1.1 Remote Configuration & Branch Topology
- **Remote Origin:** `https://github.com/dhairyajain/pqc-research.git` (also referenced as `dhairyahuh/pqc-research.git`)
- **Active Branch:** `space-resilience-framework`
- **Known Branches:**
  - `main` (upstream default)
  - `archive/pqc-ntt-fault-resilience` (archival record of initial exploratory phase)
  - `space-resilience-framework` (primary active research development branch)

### 1.2 Latest Recorded Commit
- **Commit Hash:** `b39a18a332642a0ac5c2baade629ee8023e435b1`
- **Author:** `dhairya <1008dhairyajain@gmail.com>`
- **Date:** `Mon Oct 19 09:14:09 2026 +0530`
- **Subject:** `feat: integrate PQC fault resilience pre-existing improvements and core evidence artifacts`
- **Preceding Commit:** `ce9c6862367cd3f61bc6971dc66aead9f90f2aed` (`docs: add comprehensive AYUSH.md and complete technical handover documentation`)

---

## 2. Build System & Compilation Instructions

The repository features two parallel build mechanisms:

### 2.1 Primary Build System: `Makefile`
The primary build orchestrator is standard C99/C11 via `Makefile`.
- **Compiler Configuration:** `CC = clang`, `CFLAGS = -O3 -Wall -Wextra -std=c11 -I/opt/homebrew/include`, `LDFLAGS = -L/opt/homebrew/lib -loqs`.
- **Target Architecture:** Pure C99 for Path B (`mlkem-native`), compiled with `-std=c99 -I algorithms/source_ref/mlkem`.
- **Primary Build Targets:**
  - `make bin/test_fips_kats`: Compiles and links the complete 18-vector NIST Known Answer Test runner.
  - `make bin/test_interop`: Compiles Path A (liboqs) vs Path B (`mlkem-native`) cross-validation harness.
  - `make bin/mlkem768_internal_fault_experiment`: Compiles instrumented ML-KEM-768 with internal fault hooks.
  - `make bin/mlkem_campaign_runner`: Compiles multi-level (512/768/1024) fault-injection campaign runner.
  - `make bin/mldsa_campaign_runner`: Compiles multi-level ML-DSA (44/65/87) campaign runner.
- **Cleanroom Build Target:**
  ```bash
  clang -O3 -std=c99 -I algorithms/source_ref/mlkem phase18_audit/production_reproducer.c \
        bin/obj/mlkem768_inst.o bin/obj/mlkem_fault_hooks.o -o phase18_audit/production_reproducer
  ```

### 2.2 Secondary Build System: `CMakeLists.txt`
Used exclusively for building baseline wrapper harnesses against external `liboqs`:
- Locates `liboqs` headers and library in Homebrew paths (`/opt/homebrew/include`, `/opt/homebrew/lib`).
- Builds `ml_kem_harness` and `ml_dsa_harness`.

---

## 3. Cryptographic C Implementation

The core cryptographic algorithms are implemented in `algorithms/source_ref/`:

### 3.1 ML-KEM Implementation (`algorithms/source_ref/mlkem/`)
- **Upstream Origin:** Official `mlkem-native` at commit `fc269bc2d106`.
- **Conformance:** 100% compliant with NIST FIPS 203.
- **Memory Allocation:** Zero dynamic memory allocation (`malloc`/`free` free). All memory is allocated statically or on stack frames.
- **Timing Invariance:** Constant-time arithmetic without secret-dependent branches or secret-indexed memory lookups.
- **Key Files:**
  - `mlkem_native.c` / `mlkem_native.h`: Monolithic unified C unit.
  - `src/kem.c` / `src/kem.h`: Key generation, encapsulation, and decapsulation (`crypto_kem_keypair`, `crypto_kem_enc`, `crypto_kem_dec`).
  - `src/poly.c` / `src/poly.h`: Polynomial arithmetic, Number Theoretic Transforms (`poly_ntt`, `poly_invntt_tomont`).
  - `src/indcpa.c` / `src/indcpa.h`: Underlying IND-CPA public-key encryption scheme.
  - `src/fips202/`: Hermetic SHA-3, SHAKE-128, and SHAKE-256 implementation.

### 3.2 ML-DSA Implementation (`algorithms/source_ref/mldsa/`)
- **Upstream Origin:** Official `mldsa-native` at commit `88a5369bb911`.
- **Conformance:** 100% compliant with NIST FIPS 204.
- **Files:** `mldsa_native.c`, `src/sign.c`, `src/poly.c`.

---

## 4. Fault-Monitoring Architecture & Implementations

### 4.1 Forward NTT Monitoring & Register Snapshotting
- **Location:** [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L375-L425) & [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L600-L665)
- **Snapshot Mechanism:** Before butterfly execution in `mlk_ntt_butterfly_block`:
  ```c
  int16_t u_saved = r[j];
  int16_t v_saved = r[j + len];
  ```
  Held strictly in local CPU registers.
- **Invariant Evaluation:** Evaluates algebraic identities modulo $q = 3329$:
  $$\Delta_{\text{sum}} = (u' + v' - 2u) \pmod{3329}$$
  $$\Delta_{\text{diff}} = (u' - v' - 2\zeta v) \pmod{3329}$$
  Evaluates in $O(1)$ with 2 additions, 1 multiplication, and **0 modular divisions**.
- **Localized Rollback:** On mismatch, restores `r[j] = u_saved` and `r[j+len] = v_saved`, re-executes butterfly, and bounds retries to $R_{max} = 2$.

### 4.2 Inverse NTT Monitoring & Decoupled Rails
- **Location:** [`algorithms/source_ref/mlkem/src/poly.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L535-L590) & [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c#L804-L874)
- **Gentleman-Sande Invariant:** Decouples adder-rail ($u' \equiv u + v \pmod q$) from multiplier-rail ($v' \equiv (u - v)\zeta \pmod q$) to preserve division-free verification.

### 4.3 Persistent Fail-Stop & Containment Escalation
- **Location:** [`algorithms/source_ref/mlkem/src/kem.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/kem.c#L484-L520)
- **Mechanism:** If retries exceed $R_{max}=2$, `g_ntt_native_monitor.persistent_count` increments. The outer KEM wrapper intercepts this counter, forces `fail = 0xFF`, and invokes FIPS 203 implicit rejection to output $K_{rej} = \text{SHAKE256}(z \parallel c)$, preventing SDC without throwing unhandled processor traps.

---

## 5. TFIB (Twiddle Factor Integrity Binding) Implementation

Located in `tfib_implementation/`:
- **Problem Solved (Theorem 1):** Proved mathematically that input/output invariants $(u'+v') \equiv 2u \pmod q$ are blind to corrupted twiddle factors $\zeta$ because $\zeta v$ cancels out.
- **Hardened v2 Reference Table:** `tfib_ref.c` introduces `tfib_zetas_ref[128]`, an independent, read-only twiddle reference table.
- **Independent Validation:** Functions `tfib_ref_monitor_ntt_butterfly` and `tfib_ref_monitor_invntt_butterfly` independently recompute twiddle lookups from loop counters, detect table corruption, and repair values in-place.
- **Static Library:** Compiles into `tfib_implementation/libtfib.a`.

---

## 6. Test Harnesses & Experimental Datasets

### 6.1 Test Harnesses
| Harness | Location | Target / Purpose | Status |
|---|---|---|---|
| **FIPS KAT Runner** | `tests/test_fips_kats.c` | Verifies 18/18 official NIST test vectors (ML-KEM & ML-DSA) | **PASS** (18/18) |
| **Path A/B Interop** | `tests/test_interop_path_a_b.c` | Validates cross-implementation interop with `liboqs` | **PASS** |
| **Countermeasure Independence** | `tfib_experiments/test_step2c_countermeasure_independence.c` | 9 automated tests for checker faults and twiddle resilience | **PASS** (9/9) |
| **Production Reproducer** | `phase18_audit/production_reproducer.c` | 400 cleanroom trials on compiled `mlkem768_inst.o` | **PASS** (0 SDC) |

### 6.2 Key Authoritative Datasets
- `phase18_audit/raw_production_trials.csv`: 400 audited trials ($100$ clean, $100$ transient, $200$ persistent stuck-at; 0 SDC).
- `tfib_trial_level_results.csv`: 900 trials ($150$ controls, $750$ active faults; 0 SDC).
- `tfib_benchmark_raw.csv`: 40,000 timing iterations.
- `phase16_targeted_evidence_closure/h1_activation_audit.csv`: 600 trials proving 98.5% circular verifier failure rate.

---

## 7. Licensing & Governance Analysis

> [!WARNING]
> **Licensing Finding:**
> 1. The root repository currently lacks a top-level `LICENSE` or `COPYING` file. Under standard international copyright law, the repository is technically "All Rights Reserved" by the repository owner (`dhairyajain`).
> 2. The embedded cryptographic reference implementation in `algorithms/source_ref/mlkem/` declares `SPDX-License-Identifier: CC-BY-4.0` in its Markdown tree, while upstream `mlkem-native` is dual-licensed under Apache-2.0 and MIT/CC0.
> 3. **Governance Recommendation for ASTRA-Sec:** A formal `LICENSE` file (Apache-2.0 or MIT) should be added to the project root, explicitly documenting upstream attribution for `mlkem-native` and `mldsa-native`.

---

## 8. Exact API Boundaries of Monitored ML-KEM

To ensure clear integration without architectural entanglements, the exact API boundaries are cataloged below:

### 8.1 Cryptographic Public Boundary (FIPS 203)
Defined in `algorithms/source_ref/mlkem/mlkem_native.h`:
```c
int crypto_kem_keypair(uint8_t *pk, uint8_t *sk);
int crypto_kem_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int crypto_kem_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);
```
- Parameters for ML-KEM-768: `CRYPTO_PUBLICKEYBYTES = 1184`, `CRYPTO_SECRETKEYBYTES = 2400`, `CRYPTO_CIPHERTEXTBYTES = 1088`, `CRYPTO_BYTES = 32`.

### 8.2 Invariant Monitoring & Fault State API
Defined in `algorithms/source_ref/mlkem_fault_hooks.h`:
```c
void ntt_native_monitor_reset(void);
void ntt_native_monitor_configure(ntt_native_monitor_mode_t mode, bool allow_retry, uint32_t layer_mask);
uint32_t ntt_native_monitor_get_persistent_count(void);

void native_ntt_monitor_butterfly(
    unsigned layer, unsigned butterfly_idx, int16_t zeta,
    int16_t u_saved, int16_t v_saved, int16_t t_used,
    int16_t *r_j, int16_t *r_j_len
);
void native_invntt_monitor_butterfly(
    unsigned layer, unsigned butterfly_idx, int16_t zeta,
    int16_t u_saved, int16_t v_saved,
    int16_t *r_j, int16_t *r_j_len
);
```

### 8.3 Hardened TFIB API (Twiddle Factor Integrity Binding)
Defined in `tfib_implementation/tfib_ref.h` and `tfib_common.h`:
```c
void tfib_ref_init(void);
void tfib_ref_reset_stats(void);
void tfib_ref_monitor_ntt_butterfly(
    unsigned layer, unsigned b_idx, int16_t zeta_op,
    int16_t u_saved, int16_t v_saved, int16_t t_used,
    int16_t *r_j, int16_t *r_j_len
);
void tfib_ref_monitor_invntt_butterfly(
    unsigned layer, unsigned b_idx, int16_t zeta_op,
    int16_t u_saved, int16_t v_saved,
    int16_t *r_j, int16_t *r_j_len
);
```

> [!IMPORTANT]
> **Safety Rule Verified:**
> Functions are not assumed to be protected merely because they exist. Only the 11 Number Theoretic Transforms (9,856 butterflies) in decapsulation are monitored by invariant hooks. Symmetric primitives (SHA-3/SHAKE-256) and point-wise vector accumulation loops remain outside the NTT invariant monitors, relying on outer Fujisaki-Okamoto verification.
