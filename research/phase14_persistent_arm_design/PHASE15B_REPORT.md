# Phase 15B — Controlled Persistent-Table Feasibility Pilot Report

**Author:** Skeptical Cryptographic Implementation Researcher  
**Target:** Operational ML-KEM-768 Twiddle Table `mlk_zetas_page` (Research Build)  
**Execution Binary:** `bin/pilot_runner` (SHA-256: `5c7bb17709b528df4f195a46ab11f11e2ba832349da57702396c8abaa3617949`)  
**Scope:** Reversible Feasibility Pilot Only (16 Predeclared Trials)  
**Date:** 2026-10-11  
**Deliverable Directory:** `research/phase14_persistent_arm_design/`

---

## 1. Executive Summary & Epistemological Boundaries

Phase 15B executed a narrowly scoped, fully reversible feasibility pilot targeting the relocated twiddle-factor storage table `mlk_zetas_page` on Apple Silicon macOS arm64.

### Fundamental Demarcation Principle:
* **What this pilot establishes:**
  1. Operating system feasibility: Memory protection of a dedicated 16 KB page can be toggled (`vm_protect` RW $\rightarrow$ RO) and written to without kernel traps (`SIGBUS`) on Darwin XNU.
  2. Software-level isolation: The table page is completely isolated; zero collateral bytes in the 16,128-byte page padding were altered.
  3. Runtime consumption: Mutating active twiddle factors is directly consumed by ML-KEM-768 NTT arithmetic, producing message distortion that triggers Fujisaki-Okamoto implicit rejection matching the exact theoretical oracle key $K_{rej}$.
  4. Non-consumption verification: Mutating mathematically unused twiddle factor $\zeta_0$ (Index 0) produces zero effect on decapsulation, confirming that static references do not cause spurious consumption.
  5. Hygiene & Reversibility: In 16/16 trials, in-place restoration restored bit-identical baseline state with zero cross-trial contamination.
* **What this pilot CANNOT establish:**
  * **NOT evidence of physical radiation tolerance, TID, SEU, or MCU resilience.**
  * **NOT evidence of production build fault tolerance** (the production binary resides immutably in `__TEXT`).
  * **NOT a statistically powered distribution of fault vulnerability rates.**

---

## 2. Mandatory Preflight Evidence & Decision

Prior to the first mutation, all five mandatory preflight checks were executed inside `bin/pilot_runner`:

```text
--- [PREFLIGHT 1/5] Symbol Resolution & Section Alignment ---
  Resolved symbol address: 0x100020000
  Calculated page base:    0x100020000
  Result: PASS (16KB Page-Aligned)

--- [PREFLIGHT 2/5] Live VM Mapping Query via vm_region_64 ---
  Region mapped address:   0x100020000
  Region mapped size:      0x4000 (16384 bytes)
  Current protection:      r-- (0x1)
  Maximum protection:      rw- (0x3)
  Result: PASS (Darwin VM confirms __DATA_CONST permissions)

--- [PREFLIGHT 3/5] Initial Table Integrity & Padding Canary Check ---
  Result: PASS (Table matches golden digest; 16,128 padding bytes clean)

--- [PREFLIGHT 4/5] Dry-Run Protection Transition (Zero Write) ---
  Result: PASS (vm_protect RW -> RO toggling verified without write)

--- [PREFLIGHT 5/5] Preflight Clean Baseline Decapsulation Check ---
  Expected KAT SS: 0b1b32be26247cbcbe0916f8b0b729699c32a96d51efa4a4cd5b289239c8207e
  Computed KAT SS: 0b1b32be26247cbcbe0916f8b0b729699c32a96d51efa4a4cd5b289239c8207e
  Result: PASS (Cryptographic baseline 100% matches KAT)
```

**Preflight Verdict: GO (All 5 gates passed; 16 predeclared trials authorized).**

---

## 3. Predeclared 16-Trial Pilot Outcomes

All 16 trials completed cleanly with zero crashes, zero signal delivery, and zero infrastructure failures.

### Disaggregated Trial Ledger

| Trial | Target | Mask | Mutation Status | Consumption Status | Cryptographic Endpoint | Restoration Status | Observed Shared Secret (First 8 / Last 8 hex) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **0** | Baseline | `0x0000` | `NOT_ATTEMPTED` | `VERIFIED_NOT_CONSUMED` | `EXPECTED_OUTPUT` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `0b1b32be...39c8207e` ($K_{golden}$) |
| **1** | Index 0 | `0x0001` | `APPLIED` | `VERIFIED_NOT_CONSUMED` | `EXPECTED_OUTPUT` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `0b1b32be...39c8207e` ($K_{golden}$) |
| **2** | Sham (0)| `0x0000` | `APPLIED` | `VERIFIED_NOT_CONSUMED` | `EXPECTED_OUTPUT` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `0b1b32be...39c8207e` ($K_{golden}$) |
| **3** | Index 1 | `0x0001` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158...50f3db03` ($K_{rej}$) |
| **4** | Index 1 | `0x0080` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158...50f3db03` ($K_{rej}$) |
| **5** | Index 1 | `0x8000` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158...50f3db03` ($K_{rej}$) |
| **6** | Index 32| `0x0002` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158...50f3db03` ($K_{rej}$) |
| **7** | Index 63| `0x0004` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158...50f3db03` ($K_{rej}$) |
| **8** | Index 64| `0x0001` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158...50f3db03` ($K_{rej}$) |
| **9** | Index 64| `0x0400` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158...50f3db03` ($K_{rej}$) |
| **10**| Index 95| `0x0001` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158...50f3db03` ($K_{rej}$) |
| **11**| Index 127| `0x0001`| `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158...50f3db03` ($K_{rej}$) |
| **12**| Index 127| `0xFFFF`| `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158...50f3db03` ($K_{rej}$) |
| **13**| Sham(64)| `0x0000` | `APPLIED` | `VERIFIED_NOT_CONSUMED` | `EXPECTED_OUTPUT` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `0b1b32be...39c8207e` ($K_{golden}$) |
| **14**| Index 2 | `0x0008` | `APPLIED` | `VERIFIED_CONSUMED` | `REJECTION` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `f0f0e158...50f3db03` ($K_{rej}$) |
| **15**| Baseline| `0x0000` | `NOT_ATTEMPTED` | `VERIFIED_NOT_CONSUMED` | `EXPECTED_OUTPUT` | `RESTORED_AND_BASELINE_RECHECK_PASSED` | `0b1b32be...39c8207e` ($K_{golden}$) |

---

## 4. Key Scientific Observations

### 4.1 Convergence to Exact Fujisaki-Okamoto Rejection Key ($K_{rej}$)
Across all 11 active twiddle-factor mutation trials (Trials 3..12, 14), decapsulation returned:
```text
f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03
```
* **Oracle Verification:** In NIST FIPS 203, implicit rejection returns $K_{rej} = \text{SHAKE256}(z || H(c))$. Because ciphertext $c$ and secret key seed $z$ are fixed constants for the reference vector, $K_{rej}$ is a unique, deterministic 32-byte value.
* **Significance:** The output in every active fault trial matched $K_{rej}$ bit-for-bit. This proves that:
  1. The mutated twiddle factor was directly read by the NTT machine code.
  2. The arithmetic distortion propagated into decrypted polynomial $w$, corrupting message $m'$.
  3. Re-encryption with corrupted $m'$ produced $c' \neq c$, causing the constant-time comparison to fail.
  4. The Fujisaki-Okamoto transform triggered implicit rejection and selected $K_{rej}$ safely.
  5. Zero silent data corruption (SDC) occurred in these 11 trials.

### 4.2 Proof of Non-Consumption on Unused Index 0 (Trial 1)
In Trial 1, bit 0 of Index 0 ($\zeta_0 = -1044$) was flipped (`0xfbec` $\rightarrow$ `0xfbed`). The mutation was verified via immediate read-back.
* **Observation:** Decapsulation returned $K_{golden}$ (`0b1b32be...`).
* **Explanation:** FIPS 203 ML-KEM NTT iterates layer indices $k \in [1, 127]$; basemul iterates $k \in [64, 127]$. Index 0 is never accessed.
* **Significance:** This proves that static presence of the table does not cause spurious consumption and validates the negative control.

### 4.3 Neutrality of Sham Controls (Trials 2 and 13)
In Trials 2 and 13, the harness executed the complete `vm_protect(RW) -> write(mask=0) -> vm_protect(RO)` lifecycle.
* **Observation:** Decapsulation produced $K_{golden}$ bit-for-bit.
* **Significance:** Toggling page protections alone induces zero computational side-effects.

### 4.4 100% Restoration and Hygiene
* In every trial, in-place restoration returned `table_ptr` to the golden 256-byte table.
* In every trial, all 16,128 bytes of page padding remained clean (zero canary corruption).
* In every trial, post-trial baseline decapsulation reproduced $K_{golden}$ bit-for-bit.
* **Zero cross-trial contamination occurred.**

---

## 5. Artifact Provenance and Preservation Ledger

```text
a977992b2729a50066b115a11bbbe382172312763c5ad2d80f2a76eeacbf7468  algorithms/source_ref/mlkem/src/zetas.inc
d59bf9a84501029393ff028ca9f1236ff5813c6a61f64b215d3f4a12aba59bc2  algorithms/source_ref/mlkem/src/poly.c
b842eee9df30d0b96fe9c6c14a499aec5568196a7ce3694a72a4bde94647c5a7  Makefile
c239e7cf355404af7eb616c58832a6f6b9fbb9c708f83df46c9e5d01264deb9f  bin/obj/mlkem768_persistent_reloc.o
01ae1714be2db8d593ddf7a993ebba48b3daffddc8baf6bc41bec65aa76ad8cf  bin/test_fips_kats_research
5c7bb17709b528df4f195a46ab11f11e2ba832349da57702396c8abaa3617949  bin/pilot_runner
c625b7afdfb311ce0ffbd5da024a54b8f978a7d2f21e2f05e5fb637f04987981  research/phase14_persistent_arm_design/PHASE15A_REPORT.md
```

All 7 pre-existing tracked modifications remain 100% preserved.

---

## 6. Pilot Limitations & Recommendation

### Limitations:
1. **Sample Size:** 16 trials qualify experimental feasibility and hygiene only; they do not establish empirical fault rates or multi-fault interactions.
2. **Platform Specificity:** Proven strictly on Darwin arm64 under Mach-O virtual memory.
3. **Physical Non-Equivalence:** Software virtual memory mutation does not model silicon physical SEU/MCU ionization dynamics.

### Recommendation:
**FEASIBILITY AND HYGIENE QUALIFICATION COMPLETE (PILOT PASSED 16/16)**

The persistent-table fault injection mechanism is empirically proven to be safe, isolated, observable, and reversible on the modified research build. Any subsequent expansion (e.g. multi-bit sweeps or systematic layer evaluations) should proceed only under a separate, formal Phase 16 campaign plan.
