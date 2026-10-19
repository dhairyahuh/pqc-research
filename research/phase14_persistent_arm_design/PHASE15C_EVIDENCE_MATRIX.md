# Phase 15C — Evidence Matrix & Verification Ledger

**Auditor:** Independent Skeptical Cryptographic Implementation Auditor  
**Scope:** Trial-by-Trial and Claim-by-Claim Verification of Phase 15B Feasibility Pilot  
**Date:** 2026-10-11  
**Target Directory:** `research/phase14_persistent_arm_design/`

---

## 1. Predeclared 16-Trial Audit & Reconciliation Matrix

| Trial ID | Target Index | Bit Mask | Phase 15B Claimed Endpoint | Actual SUT Shared Secret (Hex First 8 ... Last 8) | Independent Mathematical Reference | Auditor Endpoint Classification | Consumption Status | Restoration Status | Auditor Verdict |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **0** | -1 (None) | `0x0000` | `EXPECTED_OUTPUT` | `0b1b32be...39c8207e` | NIST KAT Shared Secret ($K_{golden}$) | `EXPECTED_OUTPUT` | `VERIFIED_NOT_CONSUMED` | `PASS` | **VERIFIED FROM ARTIFACTS** |
| **1** | 0 ($\zeta_0$) | `0x0001` | `EXPECTED_OUTPUT` | `0b1b32be...39c8207e` | NIST KAT Shared Secret ($K_{golden}$) | `EXPECTED_OUTPUT` | `VERIFIED_NOT_CONSUMED` (Negative Control) | `PASS` | **VERIFIED FROM ARTIFACTS** |
| **2** | 0 ($\zeta_0$) | `0x0000` | `EXPECTED_OUTPUT` | `0b1b32be...39c8207e` | NIST KAT Shared Secret ($K_{golden}$) | `EXPECTED_OUTPUT` (Sham Control) | `VERIFIED_NOT_CONSUMED` | `PASS` | **VERIFIED FROM ARTIFACTS** |
| **3** | 1 ($\zeta_1$) | `0x0001` | `REJECTION` | `f0f0e158...50f3db03` | FIPS 203 $J(z \parallel c, 32)$ | `REJECTION` (Verified independently) | `VERIFIED_CONSUMED` | `PASS` | **SUPPORTED WITH LIMITATIONS** (Runner lacked oracle) |
| **4** | 1 ($\zeta_1$) | `0x0080` | `REJECTION` | `f0f0e158...50f3db03` | FIPS 203 $J(z \parallel c, 32)$ | `REJECTION` (Verified independently) | `VERIFIED_CONSUMED` | `PASS` | **SUPPORTED WITH LIMITATIONS** (Runner lacked oracle) |
| **5** | 1 ($\zeta_1$) | `0x8000` | `REJECTION` | `f0f0e158...50f3db03` | FIPS 203 $J(z \parallel c, 32)$ | `REJECTION` (Verified independently) | `VERIFIED_CONSUMED` | `PASS` | **SUPPORTED WITH LIMITATIONS** (Runner lacked oracle) |
| **6** | 32 ($\zeta_{32}$) | `0x0002` | `REJECTION` | `f0f0e158...50f3db03` | FIPS 203 $J(z \parallel c, 32)$ | `REJECTION` (Verified independently) | `VERIFIED_CONSUMED` | `PASS` | **SUPPORTED WITH LIMITATIONS** (Runner lacked oracle) |
| **7** | 63 ($\zeta_{63}$) | `0x0004` | `REJECTION` | `f0f0e158...50f3db03` | FIPS 203 $J(z \parallel c, 32)$ | `REJECTION` (Verified independently) | `VERIFIED_CONSUMED` | `PASS` | **SUPPORTED WITH LIMITATIONS** (Runner lacked oracle) |
| **8** | 64 ($\zeta_{64}$) | `0x0001` | `REJECTION` | `f0f0e158...50f3db03` | FIPS 203 $J(z \parallel c, 32)$ | `REJECTION` (Verified independently) | `VERIFIED_CONSUMED` | `PASS` | **SUPPORTED WITH LIMITATIONS** (Runner lacked oracle) |
| **9** | 64 ($\zeta_{64}$) | `0x0400` | `REJECTION` | `f0f0e158...50f3db03` | FIPS 203 $J(z \parallel c, 32)$ | `REJECTION` (Verified independently) | `VERIFIED_CONSUMED` | `PASS` | **SUPPORTED WITH LIMITATIONS** (Runner lacked oracle) |
| **10** | 95 ($\zeta_{95}$) | `0x0001` | `REJECTION` | `f0f0e158...50f3db03` | FIPS 203 $J(z \parallel c, 32)$ | `REJECTION` (Verified independently) | `VERIFIED_CONSUMED` | `PASS` | **SUPPORTED WITH LIMITATIONS** (Runner lacked oracle) |
| **11** | 127 ($\zeta_{127}$) | `0x0001` | `REJECTION` | `f0f0e158...50f3db03` | FIPS 203 $J(z \parallel c, 32)$ | `REJECTION` (Verified independently) | `VERIFIED_CONSUMED` | `PASS` | **SUPPORTED WITH LIMITATIONS** (Runner lacked oracle) |
| **12** | 127 ($\zeta_{127}$) | `0xffff` | `REJECTION` | `f0f0e158...50f3db03` | FIPS 203 $J(z \parallel c, 32)$ | `REJECTION` (Verified independently) | `VERIFIED_CONSUMED` | `PASS` | **SUPPORTED WITH LIMITATIONS** (Runner lacked oracle) |
| **13** | 64 ($\zeta_{64}$) | `0x0000` | `EXPECTED_OUTPUT` | `0b1b32be...39c8207e` | NIST KAT Shared Secret ($K_{golden}$) | `EXPECTED_OUTPUT` (Sham Control) | `VERIFIED_NOT_CONSUMED` | `PASS` | **VERIFIED FROM ARTIFACTS** |
| **14** | 2 ($\zeta_2$) | `0x0008` | `REJECTION` | `f0f0e158...50f3db03` | FIPS 203 $J(z \parallel c, 32)$ | `REJECTION` (Verified independently) | `VERIFIED_CONSUMED` | `PASS` | **SUPPORTED WITH LIMITATIONS** (Runner lacked oracle) |
| **15** | -1 (None) | `0x0000` | `EXPECTED_OUTPUT` | `0b1b32be...39c8207e` | NIST KAT Shared Secret ($K_{golden}$) | `EXPECTED_OUTPUT` | `VERIFIED_NOT_CONSUMED` | `PASS` | **VERIFIED FROM ARTIFACTS** |

---

## 2. Core Architectural & Experimental Claims Matrix

| Claim Item | Phase 15B Stated Claim | Audited Evidence Basis | Classification | Auditor Notes / Action Required |
|:---|:---|:---|:---:|:---|
| **1. Mach-O Layout & Isolation** | Table `mlk_zetas_page` occupies dedicated 16 KB page in `__DATA_CONST` with zero co-located constants. | Confirmed via `otool -l`, `vm_region_64`, and 16,128 zero padding bytes. | **VERIFIED FROM ARTIFACTS** | Page base is `0x100020000`, size `0x4000`. Canaries clean before and after all 16 trials. |
| **2. Protection Transitions** | `vm_protect` RW $\leftrightarrow$ RO toggles dynamically without `SIGBUS` or kernel traps. | Preflight 4 and trial code executed transitions cleanly. `maxprot = 0x3`. | **VERIFIED FROM ARTIFACTS** | Solves upstream `__TEXT` W^X kernel trap issue. |
| **3. In-Memory Mutation & Volatile Access** | Table modified in-place and verified via readback through volatile pointer. | Code inspection confirms `volatile int16_t *` write and read-back check. | **VERIFIED FROM ARTIFACTS** | Prevents compiler optimization / store-elimination. |
| **4. Negative Control Inactive Index** | Index 0 ($\zeta_0$) mutation produces zero effect on decapsulation. | Trial 1 mutated Index 0; decapsulation produced exact $K_{golden}$. | **VERIFIED FROM ARTIFACTS** | Empirically confirms that NTT layers iterate $k \in [1, 127]$ and ignore $\zeta_0$. |
| **5. Arithmetic Consumption** | Active factor mutations are consumed by NTT arithmetic causing decapsulation failure. | Corrupting active twiddles alters decrypted message $m'$, causing FO re-encryption check $c' \neq c$ to fail. | **SUPPORTED WITH LIMITATIONS** | End-to-end decapsulation failure observed. Intermediate polynomial state was not directly probed. |
| **6. FIPS 203 Implicit Rejection Formula** | Report claimed: $K_{rej} = \text{SHAKE256}(z \parallel H(c))$. | FIPS 203 Alg 17 Step 5 specifies: $\bar{K} = J(z \parallel c, 32) = \text{SHAKE256}(z \parallel c, 32)$. | **CONTRADICTED / INACCURATE** | Report cited obsolete Kyber Round 3 draft formula instead of FIPS 203 standard. |
| **7. Independent Test Oracle** | Report claimed trial output was verified against an independent test oracle. | Runner line 277 merely checks `ss_out != test_vector_ss` and assigns `REJECTION`. | **NOT VERIFIED IN RUNNER** | Runner lacked an independent oracle implementation; it merely performed an inequality check. |
| **8. Reversibility & Zero Contamination** | 16/16 trials restored original table state with zero cross-trial contamination. | All 16 trials restored table, preserved canaries, and reproduced $K_{golden}$ post-trial. | **VERIFIED FROM ARTIFACTS** | Restored bit-for-bit fidelity on all 16 trials. |
| **9. Harness Error-Handling Hygiene** | Harness handles errors safely and restores table state on all failure paths. | Lines 233, 254 execute `break;` on failure, skipping the restoration block. | **FAIL (STRUCTURAL DEFECT)** | Error handling lacks structured cleanup; must be hardened before Phase 16 execution. |
| **10. Security Boundary Claim** | "The Fujisaki-Okamoto transform prevented key leakage." | Tested only 1 test vector under 11 fault trials. Does not protect against PFA or SIFA. | **OVERSTATED** | Must be qualified: FO transform triggered implicit rejection on a single vector; does not prove immunity to fault attacks. |

---

## 3. Summary of Evidence Status

* **Passed & Verified Dimensions (6/10):**
  - Section placement, symbol alignment, and 16 KB page isolation.
  - Runtime memory protection transitions on Darwin XNU.
  - In-place volatile memory mutation and immediate read-back verification.
  - Negative control non-consumption (Index 0).
  - Byte-for-byte table restoration and canary padding hygiene.
  - Zero cross-trial contamination across all 16 trials.

* **Deficiencies & Gaps Identified (4/10):**
  1. *Report Documentation:* Cited obsolete Kyber Round 3 formula rather than FIPS 203.
  2. *Runner Implementation:* Lacks an independent FIPS 203 $K_{rej}$ oracle; relied on an inequality check against $K_{golden}$.
  3. *Harness Robustness:* Lacks structured cleanup handlers on failure paths.
  4. *Claim Boundary:* Overstated claim regarding key leakage prevention.

* **Audit Decision:**
  **CONDITIONAL PASS — SPECIFIC EVIDENCE GAPS REMAIN**
