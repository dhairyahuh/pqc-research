# Phase 15C — Independent Audit of Phase 15B Evidence

**Auditor:** Independent Skeptical Cryptographic Implementation Auditor  
**Audit Target:** Phase 15B Source, Pilot Runner, Trial Ledger, Build Artifacts, and Technical Report  
**Target Repository State:** Git branch `space-resilience-framework` (HEAD: `4a2c4ebf9274a9188db3610a4f8448902caed056`)  
**Mode:** Strictly Read-Only Audit (Zero compilation, zero fault injection, zero file modifications outside audit deliverables)  
**Date:** 2026-10-11  
**Audit Directory:** `research/phase14_persistent_arm_design/`

---

## Executive Summary

This independent audit conducted a rigorous, line-by-line verification of the Phase 15B controlled persistent-table feasibility pilot artifacts. The audit evaluated:
1. The mathematical and algorithmic validity of the implicit rejection key claim under NIST FIPS 203.
2. The runtime safety, memory semantics, and error handling of the mutation mechanism in `pilot_runner.c`.
3. The cryptographic endpoint classification and test oracle independence.
4. The completeness, consistency, and provenance of the 16-trial ledger (`PHASE15B_TRIAL_LEDGER.csv`).
5. The epistemological boundaries and security claims asserted in `PHASE15B_REPORT.md`.

### Headline Audit Finding:
* **The System Under Test (SUT) decapsulation code correctly implements FIPS 203 implicit rejection**, and the active twiddle-factor mutations do indeed induce message errors that cause the constant-time check to fail and return the deterministic FIPS 203 rejection key.
* **However, the Phase 15B Report and Runner contain two critical evidence defects:**
  1. **Incorrect Specification in Report:** `PHASE15B_REPORT.md` (Section 4.1) erroneously documented the rejection key formula as $K_{rej} = \text{SHAKE256}(z \parallel H(c))$ (the obsolete CRYSTALS-Kyber Round 3 draft formula), whereas FIPS 203 specifies $\bar{K} = J(z \parallel c, 32) = \text{SHAKE256}(z \parallel c, 32)$.
  2. **Absence of Independent Test Oracle in Runner:** `pilot_runner.c` (lines 266–279) did **not** independently compute or check $K_{rej}$. It merely checked `ss_out != test_vector_ss` and blindly assigned the label `"REJECTION"`. No SHAKE256 computation or comparison against a reference rejection key was performed by the test harness.
  3. **Harness Cleanup Vulnerability:** `pilot_runner.c` lacks structured cleanup / transactional rollback; if an error occurs mid-trial (such as `vm_protect` failure post-mutation), the loop breaks without restoring the table or restoring page permissions.
  4. **Overstated Security Claim:** The assertion that "the Fujisaki-Okamoto transform prevented key leakage" is **OVERSTATED** for an implementation feasibility test on a single test vector.

---

## 1. Audit of the FIPS 203 Rejection-Key Computation

### 1.1 Specification Analysis: NIST FIPS 203 vs CRYSTALS-Kyber Round 3
In NIST FIPS 203 (Module-Lattice-Based Key-Encapsulation Mechanism Standard, Section 6.3, Algorithm 17: `ML-KEM.Decaps_internal(dk, c)`):
* **Inputs:**
  * Decapsulation key $dk = (dk_{PKE} \parallel ek_{PKE} \parallel H(ek_{PKE}) \parallel z) \in \mathbb{B}^{384k + 768}$. For ML-KEM-768 ($k=3$), $|dk| = 2400$ bytes.
  * Ciphertext $c \in \mathbb{B}^{32(d_u k + d_v)}$. For ML-KEM-768 ($d_u=10, d_v=4$), $|c| = 1088$ bytes.
* **Step 5 (Rejection Key Derivation):**
  $$\bar{K} \leftarrow J(z \parallel c, 32)$$
  where function $J$ is defined in FIPS 203 Section 4.1 (Table 2 & Eq. 4.4):
  $$J(s, d) := \text{SHAKE256}(s, d)$$
  The input string to SHAKE256 is the exact concatenation of the 32-byte seed $z$ and the 1088-byte ciphertext $c$ (total input length: $32 + 1088 = 1120$ bytes). The requested output length $d$ is 32 bytes (256 bits).

* **Historical Divergence (CRYSTALS-Kyber Round 3):**
  In the pre-standardization Kyber Round 3 submission to NIST, decapsulation computed:
  $$K \leftarrow \text{KDF}(z \parallel H(c)) = \text{SHAKE256}(z \parallel \text{SHA3-256}(c), 32)$$
  Here, the ciphertext $c$ was first pre-hashed via $H$ ($\text{SHA3-256}$), resulting in a 64-byte input to SHAKE256. NIST explicitly eliminated the intermediate hash $H(c)$ in the final FIPS 203 standard, feeding raw $c$ directly into $J$.

### 1.2 Implementation Analysis in the Cryptographic Source
Inspection of `algorithms/source_ref/mlkem/src/kem.c` (lines 512–517) confirms:
```c
/* Compute rejection key */
mlk_memcpy(tmp, sk + MLKEM_INDCCA_SECRETKEYBYTES - MLKEM_SYMBYTES,
           MLKEM_SYMBYTES);
mlk_memcpy(tmp + MLKEM_SYMBYTES, ct, MLKEM_INDCCA_CIPHERTEXTBYTES);
mlk_hash_j(ss, tmp, MLKEM_SYMBYTES + MLKEM_INDCCA_CIPHERTEXTBYTES);
```
And in `algorithms/source_ref/mlkem/src/symmetric.h` (lines 34–36):
```c
/* Hash function J, @[FIPS203, Section 4.1, Eq (4.4)] */
#define mlk_hash_j(OUT, IN, INBYTES) \
  mlk_shake256(OUT, MLKEM_SYMBYTES, IN, INBYTES)
```
**Finding:** The SUT source code strictly adheres to FIPS 203 Algorithm 17: it concatenates $z$ (32 bytes) with $ct$ (1088 bytes) into `tmp` (1120 bytes) and evaluates `mlk_shake256(ss, 32, tmp, 1120)`.

### 1.3 Audit of the Phase 15B Report Claim
In `research/phase14_persistent_arm_design/PHASE15B_REPORT.md` (Section 4.1, line 97), the report asserts:
> "*Oracle Verification: In NIST FIPS 203, implicit rejection returns $K_{rej} = \text{SHAKE256}(z || H(c))$. Because ciphertext $c$ and secret key seed $z$ are fixed constants for the reference vector, $K_{rej}$ is a unique, deterministic 32-byte value.*"

**Verdict on Report Formula: INACCURATE / CONTRADICTED BY STANDARD.**  
The report author conflated FIPS 203 with Kyber Round 3 by introducing an extraneous hash $H(c)$. Under FIPS 203, $c$ is not hashed prior to SHAKE256.

### 1.4 Audit of the Phase 15B Runner Oracle
Inspection of `research/phase14_persistent_arm_design/pilot_runner.c` (lines 262–279) reveals:
```c
/* Step 6: Endpoint analysis */
if (dec_rc != 0) {
    records[t].crypto_endpoint = "NO_OUTPUT";
    records[t].consumption_status = "VERIFIED_CONSUMED";
} else if (memcmp(ss_out, test_vector_ss, 32) == 0) {
    records[t].crypto_endpoint = "EXPECTED_OUTPUT";
    ...
} else {
    /* Output changed */
    records[t].crypto_endpoint = "REJECTION";
    records[t].consumption_status = "VERIFIED_CONSUMED";
}
```
**Finding:** `pilot_runner.c` contains **NO independent cryptographic test oracle**. It does not call SHAKE256, does not compute $J(z \parallel c)$, and does not compare `ss_out` against any expected rejection key. It merely checks `memcmp(ss_out, test_vector_ss, 32) != 0` and unconditionally assigns the label `"REJECTION"`. Any corrupted output—including catastrophic silent data corruption (SDC)—would have been labelled `"REJECTION"` by this runner code.

### 1.5 Independent Python Verification of Test Vector Hash
To verify whether the observed shared secret `f0f0e158...` was in fact the correct FIPS 203 rejection key, an independent mathematical computation was performed using the exact test vector constants (`test_vector_sk` and `test_vector_ct` from `references/test_vectors/mlkem_expected_kat.h`):

| Formulation | Mathematical Definition | Computed 32-Byte Digest (Hex) | Match with Observed Runner Output |
|:---|:---|:---|:---:|
| **NIST FIPS 203 (Standard)** | $\bar{K} = \text{SHAKE256}(z \parallel c, 32)$ | `f0f0e158ed09b1c27350a0ac9ef3b4e142e7f599688c828935f5047e50f3db03` | **EXACT MATCH (Bit-for-Bit)** |
| **Kyber Round 3 (Report Claim)** | $K = \text{SHAKE256}(z \parallel \text{SHA3-256}(c), 32)$ | `1ab963c5f52751004bee47781ab754c56f0a463673dd9aba6a06916437a6d7e0` | **MISMATCH** |

**Conclusion on Section 1:**
* **SUT Arithmetic & Logic:** **VERIFIED FROM ARTIFACTS** (decapsulation correctly produced FIPS 203 $K_{rej}$).
* **Report Theoretical Citation:** **FAIL** (cited Kyber Round 3 formula $z \parallel H(c)$).
* **Runner Oracle Independence:** **FAIL / NOT VERIFIED** (runner only checked inequality against $K_{golden}$; no independent $K_{rej}$ oracle was executed).

---

## 2. Audit of the Actual Mutation Mechanism

Inspection of `research/phase14_persistent_arm_design/pilot_runner.c` and `bin/pilot_runner` yielded the following findings across the mutation and restoration lifecycle:

### 2.1 Symbol Resolution & Isolation Verification
* **Symbol Pointer Resolution:** In `pilot_runner.c` (line 95), `table_ptr` is acquired via `mlkem_research_get_zetas_mutable_ptr()`. Lines 100–108 verify that `table_ptr == 0x100020000` and `table_ptr & 0x3fff == 0`, confirming 16 KB page alignment.
* **VM Region Query:** Lines 111–150 invoke `vm_region_64()`. The live kernel mapping confirms region base `0x100020000`, size `0x4000` (16,384 bytes), current protection `0x1` (`VM_PROT_READ`), and max protection `0x3` (`VM_PROT_READ | VM_PROT_WRITE`).
* **Canary Padding Check:** Lines 158–166 check 16,128 bytes following the 256-byte table. All padding bytes are confirmed `0x00`.

### 2.2 Memory Mutation & Volatile Semantics
* **Protection Transition:** Lines 226 and 251 toggle permissions via `vm_protect(mach_task_self(), page_addr, 0x4000, FALSE, ...)`. Transitions RW $\rightarrow$ RO execute cleanly without Darwin XNU traps (`SIGBUS`).
* **Volatile Mutation:** Line 237 casts to `volatile int16_t *vtable = (volatile int16_t *)table_ptr;` and performs the write `vtable[idx] = target_val;`. This prevents compiler store-elimination.
* **Read-Back Verification:** Line 241 performs an immediate read-back: `int16_t readback_val = vtable[idx];` and checks `readback_val == target_val`.
* **C Typing & Sign/Unsign Conversion Analysis:**
  * In `pilot_runner.c` (line 223): `int16_t target_val = orig_val ^ mask;`
  * `orig_val` is `int16_t` (signed), `mask` is `uint16_t` (unsigned).
  * Under C99 §6.3.1.8 (Usual arithmetic conversions), both operands promote to signed `int` on 32-bit/64-bit systems. The bitwise XOR produces an `int`.
  * Assigning back to `int16_t target_val` invokes C99 §6.3.1.3: if the resulting value exceeds the range of signed 16-bit integers, the conversion is implementation-defined. On ARM64 (two's complement), this safely retains the two's-complement bit pattern, but standard hygiene would benefit from explicit casting: `(int16_t)((uint16_t)orig_val ^ mask)`.

### 2.3 Bounds Checking Defect
* In `pilot_specs[16]`, target indices are hardcoded (values $-1, 0, 1, 2, 32, 63, 64, 95, 127$).
* However, in `pilot_runner.c` (line 219):
  `int is_mutation = (pilot_specs[t].target_idx >= 0 && pilot_specs[t].bit_mask != 0);`
  There is **no upper bounds check** (`target_idx < 128`). While safe for the 16 predeclared trial specs, this represents an omission for any expanded campaign runner.

### 2.4 Error Handling & Structured Cleanup Vulnerability
* In lines 233, 247, 254, 292, and 299 of `pilot_runner.c`:
  When any `vm_protect` or verification step fails, the harness executes `break;`.
* **Critical Finding:** If `vm_protect(RO)` fails at line 254 (post-mutation), the loop breaks immediately. **The restore block (lines 287–300) is completely bypassed.**
* This would leave:
  1. The mutated value residing permanently in memory.
  2. The page potentially in read-write state.
  3. No cleanup or post-trial recheck performed.
* `pilot_runner.c` lacks structured cleanup (e.g. `goto cleanup;` or RAII rollback). While all 16 trials in Phase 15B took the happy path, the harness lacks robust failure-path hygiene.

### 2.5 Restoration & Recheck Verification
* Lines 303–322 verify that after every trial:
  1. `memcmp(table_ptr, golden_zetas, sizeof(golden_zetas)) == 0` (100% table restoration).
  2. All 16,128 canary padding bytes remain `0x00`.
  3. Post-trial decapsulation reproduces $K_{golden}$ bit-for-bit.
* **Finding:** In all 16 trials executed during Phase 15B, restoration succeeded without cross-trial contamination.

### 2.6 Arithmetic Consumption Distinction
* The runner successfully demonstrated negative control non-consumption:
  * **Trial 1 (Index 0, Root factor):** Mutated with mask `0x0001`. Verified written and read back. Decapsulation returned $K_{golden}$ bit-for-bit (`VERIFIED_NOT_CONSUMED`).
  * **Trials 3..12, 14 (Active factors):** Mutated. Decapsulation returned rejection key (`VERIFIED_CONSUMED`).
* **Finding:** The runner successfully distinguishes an in-memory mutation from an arithmetically consumed mutation.

---

## 3. Audit of Cryptographic Endpoints and Security Claims

### 3.1 Endpoint Classification Audit
Phase 15B defined five cryptographic endpoint states: `EXPECTED_OUTPUT`, `DIFFERENT_OUTPUT`, `REJECTION`, `NO_OUTPUT`, and `NOT_RUN`.

* **Audit Finding on `REJECTION`:**
  As established in Section 1.4, `pilot_runner.c` assigned `REJECTION` based strictly on `ss_out != test_vector_ss`. It did not verify that `ss_out == K_rej`.
  Although independent verification confirms that `ss_out` equalled $K_{rej}$, the runner's decision logic was fundamentally an inequality check (`ss_out != K_golden`), which cannot differentiate between implicit rejection and silent data corruption (SDC).

### 3.2 Evaluation of the Statement: "The Fujisaki-Okamoto transform prevented key leakage"
In `PHASE15B_REPORT.md` (Section 4.1, line 102), the report states:
> "*The Fujisaki-Okamoto transform triggered implicit rejection and selected $K_{rej}$ safely.*"
> "*The Fujisaki–Okamoto transform prevented key leakage.*"

**Classification: OVERSTATED.**

**Justification:**
1. **Single-Vector Evaluation:** The pilot evaluated exactly one deterministic test vector ($c, sk$) across 11 fault trials. It did not evaluate multi-ciphertext interactions or chosen-ciphertext attacks.
2. **Persistent Fault Analysis (PFA) Vulnerability:** In post-quantum lattice schemes, persistent faults in twiddle tables or NTT constants alter the algebraic decoding syndrome across multiple decapsulations. Even if every individual decapsulation results in implicit rejection ($K_{rej}$), an adversary observing multiple rejection outcomes or execution times under chosen ciphertexts can reconstruct secret key coefficients (e.g., via Statistical Inactive Fault Analysis / Fault-Assisted Decryption Failure attacks).
3. **Black-Box vs Physical Model:** The Fujisaki-Okamoto transform guarantees IND-CCA2 security in the random oracle model under uncorrupted execution. It is **not** a fault-tolerant countermeasure designed to prevent key extraction under persistent internal hardware/memory faults.
4. **Scope Demarcation:** Observing that decapsulation returned $K_{rej}$ rather than a broken key for a single KAT ciphertext demonstrates that the integrity check failed as expected; it does **not** prove that key leakage was prevented.

---

## 4. Reconciliation of the 16-Trial Ledger

A byte-level reconciliation was conducted across `pilot_runner.c`, stdout execution logs, `PHASE15B_TRIAL_LEDGER.csv`, and `PHASE15B_REPORT.md`.

### 4.1 Trial Ledger Structure and Completeness
* **Trial Count:** Exactly 16 trials (IDs 0 through 15) are present in `PHASE15B_TRIAL_LEDGER.csv`. No trials are missing, duplicated, or out of order.
* **Target Coverage:**
  * Clean Baseline: Trials 0 and 15 (Target -1, Mask 0x0000).
  * Inactive Factor Control: Trial 1 (Target 0, Mask 0x0001).
  * Sham Controls: Trial 2 (Target 0, Mask 0x0000) and Trial 13 (Target 64, Mask 0x0000).
  * Active Forward NTT: Trials 3, 4, 5 (Target 1; LSB, mid, sign flips), Trial 6 (Target 32), Trial 7 (Target 63), Trial 14 (Target 2).
  * Active Mulcache / Basemul: Trials 8, 9 (Target 64), Trial 10 (Target 95), Trials 11, 12 (Target 127).

### 4.2 Discrepancy Between Runner Stdout and CSV Columns
* In `pilot_runner.c` (lines 359–369), the runner's summary loop prints 7 CSV columns:
  `trial_id,target_idx,bit_mask,mutation_status,consumption_status,crypto_endpoint,restoration_status`
* In `PHASE15B_TRIAL_LEDGER.csv`, the file contains 9 columns:
  `trial_id,target_idx,bit_mask,mutation_status,consumption_status,crypto_endpoint,restoration_status,output_ss,expected_behavior`
* **Audit Finding:** The columns `output_ss` (32-byte hex shared secret) and `expected_behavior` (descriptive string) were captured from the runner's verbose execution logs (`print_hex32(ss_out)`) and merged into the final CSV. While scientifically informative, this indicates that the committed CSV was post-processed rather than the direct raw stdout redirection of the runner's summary block.

### 4.3 Sham Control Execution Verification
* Did Trials 2 and 13 actually execute the complete protection transition and memory write?
* Inspection of `pilot_runner.c` (lines 217–248) confirms:
  When `is_sham` is true (`target_idx >= 0 && bit_mask == 0`), the runner executes:
  1. `vm_protect(RW)`
  2. `vtable[idx] = orig_val ^ 0x0000` (actual memory write of original value)
  3. `vtable[idx]` read-back verification
  4. `vm_protect(RO)`
  5. Decapsulation and post-trial baseline check.
* **Finding:** Sham controls executed genuine memory protection toggles and memory writes, proving that the protection transition itself does not alter cryptographic execution.

### 4.4 Reference Hash Reconciliation
All hashes reported in Section 5 of `PHASE15B_REPORT.md` were independently verified against workspace files:
* `algorithms/source_ref/mlkem/src/zetas.inc`: `a977992b2729a50066b115a11bbbe382172312763c5ad2d80f2a76eeacbf7468` — **VERIFIED**
* `algorithms/source_ref/mlkem/src/poly.c`: `d59bf9a84501029393ff028ca9f1236ff5813c6a61f64b215d3f4a12aba59bc2` — **VERIFIED**
* `Makefile`: `b842eee9df30d0b96fe9c6c14a499aec5568196a7ce3694a72a4bde94647c5a7` — **VERIFIED**
* `bin/obj/mlkem768_persistent_reloc.o`: `c239e7cf355404af7eb616c58832a6f6b9fbb9c708f83df46c9e5d01264deb9f` — **VERIFIED**
* `bin/test_fips_kats_research`: `01ae1714be2db8d593ddf7a993ebba48b3daffddc8baf6bc41bec65aa76ad8cf` — **VERIFIED**
* `bin/pilot_runner`: `5c7bb17709b528df4f195a46ab11f11e2ba832349da57702396c8abaa3617949` — **VERIFIED**
* `research/phase14_persistent_arm_design/PHASE15A_REPORT.md`: `c625b7afdfb311ce0ffbd5da024a54b8f978a7d2f21e2f05e5fb637f04987981` — **VERIFIED**

---

## 5. Reassessment of Central Claims

Each core technical claim from Phase 15B is classified according to the auditor taxonomy:

| Dimension / Claim | Classification | Evidence & Auditor Justification |
|:---|:---:|:---|
| **Runtime Protection Transitions** | **VERIFIED FROM ARTIFACTS** | Mach-O `__DATA_CONST` live query confirms `maxprot = 0x3`. `vm_protect` RW $\leftrightarrow$ RO transitions execute without kernel traps (`SIGBUS`). |
| **Page Isolation & Canary Integrity** | **SUPPORTED WITH LIMITATIONS** | Table is isolated in a 16 KB page via 16,128 bytes of padding; zero canary corruption in all 16 trials. Limitation: `vm_protect` operates at page granularity. |
| **Volatile Mutation & Readback** | **VERIFIED FROM ARTIFACTS** | Memory writes through `volatile` pointer verified by immediate read-back before reprotecting page. |
| **Arithmetic Consumption** | **SUPPORTED WITH LIMITATIONS** | Observed end-to-end decapsulation failure across active twiddle factors, while unused factor (Index 0) produces zero effect. Limitation: Intermediate polynomial coefficients not probed directly. |
| **FIPS 203 Rejection Key Endpoint** | **NOT VERIFIED IN PILOT RUNNER** | Pilot runner contained no oracle checking $K_{rej}$; report cited obsolete Kyber Round 3 formula. (Independent audit mathematically confirmed SUT output equals FIPS 203 $K_{rej}$, but runner failed to test this). |
| **Restoration & Zero Contamination** | **VERIFIED FROM ARTIFACTS** | 16/16 trials restored golden twiddle factors bit-for-bit; padding remained clean; post-trial baseline KAT passed. |
| **Key Leakage Prevention Claim** | **OVERSTATED** | Feasibility pilot on 1 test vector cannot prove immunity to persistent fault analysis, side channels, or multi-ciphertext attacks. |

---

## 6. Audit Findings, Corrective Actions, and Final Recommendation

### 6.1 Identified Deficiencies Requiring Remediation
1. **Runner Oracle Deficiency:** `pilot_runner.c` must be updated to independently compute $J(z \parallel c, 32)$ and verify that `ss_out` equals $K_{rej}$ bit-for-bit, rather than relying on `ss_out != K_golden`.
2. **Formula Documentation Error:** `PHASE15B_REPORT.md` must be amended (via errata) to state the standard FIPS 203 formula $\bar{K} = J(z \parallel c, 32) = \text{SHAKE256}(z \parallel c, 32)$ instead of the Kyber Round 3 draft formula $z \parallel H(c)$.
3. **Harness Error-Handling Hardening:** The test harness must implement structured cleanup (e.g. `goto cleanup;` or signal handlers) to guarantee table restoration and page reprotection even if an unexpected error occurs mid-trial.
4. **Bounds Checking:** Add explicit bounds check (`target_idx >= 0 && target_idx < 128`) before any memory dereference.
5. **Security Claim Qualification:** The claim that "the Fujisaki-Okamoto transform prevented key leakage" must be qualified or retracted in project documentation.

---

### Final Recommendation

## **CONDITIONAL PASS — SPECIFIC EVIDENCE GAPS REMAIN**

**Rationale:**  
The engineering feasibility and physical isolation of the relocated persistent twiddle table on Apple Silicon Darwin arm64 is **empirically proven and verified**. The memory protection transitions, volatile writes, canary isolation, and zero-contamination restoration operate flawlessly.

However, because the pilot runner lacked an independent FIPS 203 rejection oracle and the Phase 15B report misstated the rejection key formula, **Phase 16 campaign planning may proceed conceptually, but NO campaign execution or multi-vector sweep may begin until the runner oracle and harness error handling are formally corrected and verified.**
