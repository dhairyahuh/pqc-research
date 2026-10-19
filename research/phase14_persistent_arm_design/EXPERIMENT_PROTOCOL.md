# Phase 14 — Persistent-Storage Fault Arm: Experiment Protocol

**Author:** Skeptical Cryptographic Implementation & Experimental Methodology Reviewer  
**Target Algorithm:** NIST FIPS 203 ML-KEM-768 Decapsulation (`crypto_kem_dec`)  
**Target Storage Entity:** Twiddle-Factor Table `mlk_zetas` (128 `int16_t` values, 256 bytes)  
**Protocol Phase:** Phase 14 Design Specification (Pilot Execution Preregistration)

---

## 1. Pilot Campaign Scope & Methodological Justification

### 1.1 Feasibility and Hygiene Qualification (Not a Statistical Sample)
The proposed 16-trial pilot is **strictly an engineering feasibility and protocol hygiene qualification**.
* It is **not** a statistically powered sample to estimate fault injection probabilities, vulnerability distributions, or failure rates.
* It exists to validate the 14-step transactional pipeline, confirm page unprotection/reprotection stability, and prove zero cross-trial contamination on deterministic boundary test cases.
* **What the pilot CAN establish:**
  1. Operating system tolerance: Whether Darwin `vm_protect` toggling on `__DATA_CONST` operates without kernel aborts.
  2. Protocol hygiene: Whether the in-place restoration procedure restores bit-identical baseline state across consecutive runs.
  3. Instrumentation neutrality: Whether sham controls (`mask = 0`) prove that VM protection APIs introduce zero computational artifacts.
  4. Sensitivity: Whether twiddle factor corruption propagates through decapsulation into FO rejection.
* **What the pilot CANNOT establish:**
  1. Overall SDC rates of ML-KEM-768.
  2. Statistical distribution of failure modes across the parameter space.
  3. Any physical resilience or radiation vulnerability characteristics.

---

## 2. Pilot Trial Matrix

The 16 pilot trials systematically cover twiddle factor boundaries, operational phases, and bit positions:

| Trial ID | Target Index | Operational Role / Layer | Bit Mask | Rationale |
|:---:|:---:|:---|:---:|:---|
| **0** | — | **Baseline Control** | `0x0000` | Golden reference; unmodified memory page |
| **1** | Index 0 | Reserved / Root ($\zeta_0 = -1044$) | `0x0001` | Test low-order bit on unused/root twiddle |
| **2** | Index 0 | Reserved / Root ($\zeta_0 = -1044$) | `0x0000` | **Sham Control:** unprotect/write-0/reprotect |
| **3** | Index 1 | Forward NTT Layer 1 ($\zeta_1 = -758$) | `0x0001` | LSB flip in top-level butterfly |
| **4** | Index 1 | Forward NTT Layer 1 ($\zeta_1 = -758$) | `0x0080` | Mid-byte flip |
| **5** | Index 1 | Forward NTT Layer 1 ($\zeta_1 = -758$) | `0x8000` | Sign-bit flip |
| **6** | Index 32 | Mid NTT Layer 6 ($\zeta_{32} = 1223$) | `0x0002` | Mid-layer butterfly factor |
| **7** | Index 63 | Forward NTT Layer 7 ($\zeta_{63} = -1275$) | `0x0004` | Final forward layer butterfly |
| **8** | Index 64 | Basemul / Mulcache ($\zeta_{64} = -1103$) | `0x0001` | First mulcache twiddle factor |
| **9** | Index 64 | Basemul / Mulcache ($\zeta_{64} = -1103$) | `0x0400` | Mulcache high-order bit flip |
| **10** | Index 95 | Basemul / Mulcache ($\zeta_{95} = -75$) | `0x0001` | Mid mulcache factor |
| **11** | Index 127 | Basemul & InvNTT ($\zeta_{127} = 1628$) | `0x0001` | Final twiddle entry in table |
| **12** | Index 127 | Basemul & InvNTT ($\zeta_{127} = 1628$) | `0xFFFF` | Full 16-bit word inversion |
| **13** | Index 64 | Basemul / Mulcache | `0x0000` | **Sham Control on active index** |
| **14** | Index 2 | Forward NTT Layer 2 ($\zeta_2 = -359$) | `0x0008` | Secondary branch twiddle |
| **15** | — | **Post-Pilot Baseline Control** | `0x0000` | Final end-to-end clean verification |

---

## 3. 14-Step Deterministic Trial Lifecycle

Every single trial follows an automated 14-step transactional pipeline. Any step failure triggers an immediate abort.

```
       [ Step 1: Pre-trial Baseline Check ]
                      |
       [ Step 2: Resolve Pointer & Golden Snapshot ]
                      |
       [ Step 3: vm_protect(RW) ]
                      |
       [ Step 4: Write (target ^= mask) ]
                      |
       [ Step 5: Read-back Verification == golden ^ mask ]
                      |
       [ Step 6: vm_protect(RO) ]
                      |
       [ Step 7: SUT Execution: crypto_kem_dec ]
                      |
       [ Step 8: Capture Output & Classify State ]
                      |
       [ Step 9: vm_protect(RW) ]
                      |
       [ Step 10: Restore target = golden ]
                      |
       [ Step 11: vm_protect(RO) ]
                      |
       [ Step 12: Full Table SHA-256 Checksum == Golden ]
                      |
       [ Step 13: Post-trial Baseline crypto_kem_dec == K_golden ]
                      |
       [ Step 14: Log Record & Assert Zero Contamination ]
```

### Detailed Step Specifications:
* **Step 1 (Pre-trial Sanity):** Run ML-KEM-768 decapsulation on fixed reference ciphertext $c_{ref}$ and secret key $sk_{ref}$. Verify shared secret $K == K_{golden}$.
* **Step 2 (Snapshot):** Obtain pointer via `mlkem_research_get_zetas_mutable_ptr()`. Verify full table matches the 256-byte golden digest `303d1abccc4757d49a5c8df5f88080fefef617b7360056db5311bd94354096d4`.
* **Step 3 (Unprotect):** Call `vm_protect(mach_task_self(), page_addr, 0x4000, FALSE, VM_PROT_READ | VM_PROT_WRITE)`. Assert `kr == KERN_SUCCESS`.
* **Step 4 (Inject):** Mutate entry: `ptr[target_idx] ^= mask`. Use `volatile` write through separate compilation unit.
* **Step 5 (Read-back):** Assert `ptr[target_idx] == (golden[target_idx] ^ mask)`. If assertion fails, set `activation_verified = false` and jump to Step 9.
* **Step 6 (Re-protect):** Call `vm_protect(..., VM_PROT_READ)`. Assert `kr == KERN_SUCCESS`.
* **Step 7 (Decapsulate):** Call `crypto_kem_dec(ss_out, c_ref, sk_ref)`.
* **Step 8 (Capture & Classify):** Record `ss_out`. Compare against $K_{golden}$ and the theoretical implicit rejection key $K_{rej} = \text{SHAKE256}(z || H(c_{ref}))$.
* **Step 9 (Re-unprotect):** Call `vm_protect(..., VM_PROT_READ | VM_PROT_WRITE)`.
* **Step 10 (Restore):** `ptr[target_idx] = golden[target_idx]`.
* **Step 11 (Re-protect):** Call `vm_protect(..., VM_PROT_READ)`.
* **Step 12 (Integrity Check):** Compute SHA-256 over entire 256 bytes of `mlk_zetas`. Assert hash equals golden digest.
* **Step 13 (Contamination Guard):** Execute `crypto_kem_dec` again with unmodified reference vector. Assert `ss_out == K_{golden}`.
* **Step 14 (Persistence Check):** Write trial record to structured CSV ledger.

---

## 4. Cryptographic Endpoint Contract & Disaggregated Trial Ledger

### 4.1 FIPS 203 Endpoint Contract
Decapsulation takes ciphertext $c$ and secret key $sk = (d_K || dk_{PKE} || ek_{PKE} || H(ek) || z)$:
1. Decrypt: $m' = \text{K-PKE.Decrypt}(dk_{PKE}, c)$.
2. Re-encrypt: $(\hat{K}', r') = G(m' || H(ek))$; $c' = \text{K-PKE.Encrypt}(ek_{PKE}, m', r')$.
3. FO Verification:
   * If $c' == c \implies K = J(\hat{K}' || H(c)) \quad (K_{golden})$
   * If $c' \neq c \implies K = J(z || H(c)) \quad (K_{rej})$

### 4.2 Demarcation: SDC vs Implicit Rejection vs Recovery
* **Valid Implicit Rejection:** SUT returns $K_{rej}$. Arithmetic failure was successfully detected by FO transform, preventing key leakage. **This is NOT recovery** (the session failed to decrypt the message), but it failed **safely**.
* **Silent Data Corruption (SDC):** SUT returns $K^* \notin \{K_{golden}, K_{rej}\}$ without an error. SDC means corrupted data was accepted without detection.
* **Output Mismatch is NOT SDC:** An output mismatch is the expected behavior of implicit rejection ($K_{rej} \neq K_{golden}$). It must not be labeled SDC.

### 4.3 9-Column Trial Ledger Schema (`PILOT_RESULTS.csv`)

| Field Name | Type | Description |
|---|---|---|
| `fault_requested` | `string` | Target index, bit mask, and injection description |
| `activation_verified` | `bool` | True iff `vm_protect(RW)` and write succeeded cleanly |
| `target_bytes_changed` | `bool` | True iff post-write read-back equals `golden ^ mask` |
| `consumption_verified` | `string` | `PROVEN_REJECTION`, `PROVEN_SDC`, `MASKED_BENIGN`, or `UNVERIFIED` |
| `restoration_verified` | `bool` | True iff table restored, re-protected RO, and SHA-256 equals golden hash |
| `crypto_validity` | `string` | `VALID_KEY`, `IMPLICIT_REJECTION`, or `INVALID_KEY` |
| `endpoint_outcome` | `string` | `SUCCESS_GOLDEN`, `REJECTED_REJ_KEY`, `UNTRACKED_KEY`, `CRASH_SIGNAL` |
| `sdc_determination` | `bool` | True iff `endpoint_outcome == UNTRACKED_KEY` and exit code 0 |
| `hygiene_failure` | `bool` | True iff post-restoration decapsulation $\neq K_{golden}$ or memory leak |

---

## 5. Automated Reproducibility Procedure

The proposed pilot harness must be runnable via a single deterministic script:
```bash
./research/phase14_persistent_arm_design/run_pilot_check.sh
```
The script must:
1. Verify prerequisite compiler and host tools.
2. Build the relocated research object and pilot runner binary.
3. Verify binary symbols, section placement, and 16 KB page isolation.
4. Execute the 16 pilot trials, streaming real-time status to stdout.
5. Generate `PILOT_RESULTS.csv` containing the 9 disaggregated columns.
6. Assert `hygiene_failure == 0` and `activation_verified == true`.
