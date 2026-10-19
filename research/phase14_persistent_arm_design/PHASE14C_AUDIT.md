# Phase 14C — Final Implementation-Readiness Audit

**Author:** Skeptical Cryptographic Implementation & Experimental Methodology Reviewer  
**Audit Target:** Phase 14B Proposal & Persistent-Storage Fault-Injection Patch  
**Audit Mode:** READ-ONLY AUDIT (Zero Source Modifications, Zero Binary Builds, Zero Injections)  
**Date:** 2026-10-11  
**Deliverable Directory:** `research/phase14_persistent_arm_design/`

---

## 1. Audit Framework and Epistemological Labeling

To ensure scientific rigor, every finding in this audit is explicitly categorized into one of four epistemic tiers:
1. `[EXISTING EVIDENCE]`: Fact verified directly from inspected repository source, build files, object files, or host system utilities.
2. `[STATIC ANALYSIS]`: Logical deduction derived from C language standards (ISO C99), compiler toolchain mechanics, or ABI specifications.
3. `[INFERENCE]`: Methodological conclusion regarding experimental validity, causality, or risk.
4. `[UNTESTED HYPOTHESIS]`: Empirical proposition regarding the unbuilt research binary that can only be confirmed after implementation approval.

---

## 2. Requirement 1: Mach-O Layout and Memory Permissions

### 2.1 Segment Assignment and Linker Mechanics
* `[EXISTING EVIDENCE]`: In the baseline object `bin/obj/mlkem768.o`, `_mlk_zetas` is located in `(__TEXT,__const)` (`nm -m`). Attempting to call `vm_protect(RW)` on `__TEXT` on this host triggers `SIGBUS` (signal 10 / exit 138), verified in Phase 11.
* `[EXISTING EVIDENCE]`: Inspection of the existing linked executable `bin/test_fips_kats` via `otool -l` shows that the linker (`ld64`) creates an `LC_SEGMENT_64` for `__DATA_CONST`:
  ```text
  segname __DATA_CONST
  vmaddr 0x000000010009c000
  vmsize 0x0000000000004000
  maxprot 0x00000003 (VM_PROT_READ | VM_PROT_WRITE)
  initprot 0x00000003
  flags 0x10 (SG_READ_ONLY)
  ```
* `[STATIC ANALYSIS]`: In Mach-O, `__DATA_CONST` is assigned `flags = 0x10` (`SG_READ_ONLY`), meaning dyld maps it read-only at runtime after dynamic binding. However, because `maxprot` is `0x03` (`VM_PROT_READ | VM_PROT_WRITE`), the Darwin kernel allows the process to call `vm_protect(..., VM_PROT_READ | VM_PROT_WRITE)` provided no code-signing violation is incurred.
* `[STATIC ANALYSIS]`: Crucially, `bin/test_fips_kats` demonstrates that `__DATA_CONST` co-locates `__got` (Global Offset Table) and other read-only constants in the same 16 KB segment (`0x10009c000` to `0x1000a0000`).
* `[INFERENCE]`: If `mlk_zetas_page` is placed into `__DATA_CONST` without ensuring that its enclosing segment is isolated, unprotecting that page could alter permissions for unrelated data (such as the GOT).
* `[UNTESTED HYPOTHESIS]`: Whether `ld64` will place `mlk_zetas_page` in a distinct page of `__DATA_CONST` or whether a dedicated custom segment (e.g. `__RESEARCH_DATA`) is required.

### 2.2 Mandatory Post-Build Inspection Protocol (Final Linked Executable)
Before any memory write is attempted in the research binary, the following evidence must be collected from the final linked executable:
1. **Segment & Section Headers (`otool -l <executable>`):**
   * Prove the exact segment name and section name containing `_mlk_zetas_page`.
   * Prove that `maxprot` permits write access (`maxprot >= 0x03`). If `maxprot == 0x01` $\rightarrow$ **HARD NO-GO**.
2. **Runtime Address & Size Query (`vm_region_64`):**
   * In-process query must verify `page_addr == (table_addr & ~(0x4000 - 1))`.
   * Verify `info.protection == VM_PROT_READ` and `(info.max_protection & VM_PROT_WRITE) != 0`.
3. **Round-Trip Permission Verification:**
   * Execute `vm_protect(RW)` $\rightarrow$ write identical byte $\rightarrow$ execute `vm_protect(RO)`. Both calls must return `KERN_SUCCESS` (`kr == 0`).

---

## 3. Requirement 2: Page Isolation and Loader Verification

### 3.1 Host Page Granularity
* `[EXISTING EVIDENCE]`: Host page size was directly verified using `pagesize` and kernel inspection:
  Host architecture: Darwin 27.0.0 arm64 (Apple Silicon M1 / T8103). Page size: exactly `16,384` bytes (`0x4000`).

### 3.2 Evaluation of the Padded Structure
* `[STATIC ANALYSIS]`: The proposed data structure:
  ```c
  typedef struct {
      int16_t zetas[128];                                      /* 256 bytes */
      uint8_t page_padding[16384 - (128 * sizeof(int16_t))];   /* 16,128 bytes */
  } mlk_isolated_zetas_page_t;
  ```
  has `sizeof(mlk_isolated_zetas_page_t) == 16384` bytes.
* `[STATIC ANALYSIS]`: Declaring this struct with `__attribute__((aligned(16384)))` instructs the compiler and linker to place the symbol at an offset $0 \pmod{16384}$. Because the structure itself is 16,384 bytes, it occupies the entire span from `page_addr` to `page_addr + 0x3FFF`.
* `[INFERENCE]`: Because the structure is exactly 16 KB and 16 KB aligned, the linker cannot place any subsequent symbol within that 16 KB window.

### 3.3 Verification Procedure for Runtime Page Isolation
To prove isolation beyond static compiler attributes:
1. **Symbol Scan (`nm -n <executable>`):**
   Extract the virtual address of `_mlk_zetas_page` and assert that no other symbol has an address in `[page_addr, page_addr + 16384)`.
2. **Padding Guard Audit:**
   The harness must fill `page_padding` with a known pseudorandom canary pattern at initialization. After every trial, verify that all 16,128 canary bytes remain 100% unaltered.
3. **NO-GO Condition:**
   If any other symbol shares the page, or if canary corruption is detected $\rightarrow$ **IMMEDIATE HARD NO-GO**.

---

## 4. Requirement 3: C Semantics and Proof of Actual Consumption

### 4.1 C Language Standards Compliance
* `[STATIC ANALYSIS]`: ISO C99 §6.7.3 Clause 5 states: *"If an attempt is made to modify an object defined with a const-qualified type through use of an lvalue with non-const-qualified type, the behavior is undefined."*
* `[STATIC ANALYSIS]`: In Phase 14, `mlk_zetas` was declared `const` and modified via `(int16_t *)(uintptr_t)`. This introduced undefined behavior (UB).
* `[STATIC ANALYSIS]`: In the Phase 14B revision, `zetas` inside `mlk_isolated_zetas_page_t` is declared **non-const** (`int16_t zetas[128]`). Modifying a non-const object through an lvalue is 100% standard-compliant (defined behavior). Its read-only status is enforced by the operating system virtual memory subsystem (`vm_protect`), accurately modeling hardware ROM/Flash storage.
* `[STATIC ANALYSIS]`: Inside `poly.c`, `mlk_zetas` is defined via macro alias `#define mlk_zetas (mlk_zetas_page.zetas)`. Since `poly.c` functions take `int16_t` values, passing `int16_t` from a non-const array is valid C99 with zero warnings.

### 4.2 Multi-Dimensional Consumption Proof Plan
* `[INFERENCE]`: Disassembly alone is insufficient because it proves only static instruction presence, not dynamic runtime execution. Output change alone is insufficient because it could be caused by collateral corruption or unrelated crashes.
* `[STATIC ANALYSIS]`: Consumption must be proven by combining six complementary evidence streams:
  1. **Disassembly Check:** Disassembly confirms that NTT butterfly loops issue PC-relative memory loads (`ldrsh`, `ldr q`) from the relocated page base.
  2. **Memory Read-Back Check:** Immediate read-back verifies that `target_val == (golden_val ^ mask)`.
  3. **Collateral Guard Check:** Verification that all other 127 twiddle factors and all 16,128 padding bytes remain unaltered.
  4. **Mathematical Oracle Match (Pilot Trial 8):**
     * Twiddle factor $\zeta_{64}$ is used in mulcache computation (`poly.c:288`).
     * Mutating bit 0 of $\zeta_{64}$ alters decrypted message vector $m'$.
     * Re-encryption with altered $m'$ produces $c' \neq c$, causing Fujisaki-Okamoto verification to fail.
     * The implementation must return the exact deterministic implicit rejection key:
       $$K_{rej} = \text{SHAKE256}(z || H(c))$$
     * Matching $K_{rej}$ bit-for-bit proves that the arithmetic distortion was consumed by decapsulation and reached the FO check.
  5. **Sham Control Neutrality:** Executing the unprotection/write/reprotection sequence with `mask = 0` produces $K_{golden}$ bit-for-bit.
  6. **Restoration Check:** Restoring the value and re-protecting RO restores the full table SHA-256 hash and produces $K_{golden}$ on post-trial decapsulation.

---

## 5. Requirement 4: Clean-Build Equivalence Gate

### 5.1 Defensible Baseline Equivalence Protocol
Before any fault injection is permitted, the research build (`mlkem768_persistent_reloc.o`) must be evaluated against the baseline build (`mlkem768.o`):

1. **Gate A: NIST FIPS 203 KAT Suite:**
   100% of NIST FIPS 203 KAT vectors must pass when linked against the research object (`./bin/test_fips_kats`).
2. **Gate B: 1,000 Deterministic Test Vectors:**
   For a pseudo-randomly generated suite of 1,000 deterministic $(c_i, sk_i)$ pairs, decapsulation outputs must match bit-for-bit:
   $$\text{Decaps}_{research}(c_i, sk_i) == \text{Decaps}_{baseline}(c_i, sk_i) == K_{golden, i}$$
3. **Gate C: Disassembly Diffing (`diff -u`):**
   Disassembly of `mlkem_poly_invntt_tomont`, `mlkem_poly_ntt`, and `mlkem_poly_mulcache_compute` must be compared.

### 5.2 Distinguishing Benign vs Disqualifying Differences
* **Benign Differences (Permitted):**
  * PC-relative displacement offsets in `adrp` instructions.
  * Relocation symbol names in Mach-O headers.
  * Benign local register allocation swaps (e.g. `x16` vs `x17`) that do not alter calling conventions, live ranges, or register spills.
* **Disqualifying Differences (Hard NO-GO):**
  1. **Instruction Schedule Alterations:** Any change in total instruction count inside the NTT inner loops.
  2. **Vectorization Divergence:** Failure of Clang to auto-vectorize loops (e.g. falling back from `ldr q` / `smull2` to scalar loops).
  3. **Inlining Divergence:** Failure to inline static helpers or unintended inlining across major function boundaries.
  4. **Constant Folding:** Elimination of memory loads in favor of immediate values.

---

## 6. Requirement 5: Cryptographic Outcome Contract and Ledger

### 6.1 Disaggregated Ledger Schema (10 Explicit Fields)
To eliminate conflation, the trial record must record 10 mutually exclusive fields:

| Field Name | Type | Definition |
|---|---|---|
| `fault_requested` | `string` | Tuple `(index, mask, phase)` specifying requested injection |
| `fault_activated` | `bool` | True iff `vm_protect(RW)` and write executed without signal/trap |
| `target_bytes_changed` | `bool` | True iff immediate read-back equals `golden ^ mask` |
| `modified_bytes_consumed` | `string` | Categorical: `PROVEN_FO_REJECTION`, `PROVEN_SDC`, `MASKED_BENIGN`, `UNVERIFIED` |
| `restoration_verified` | `bool` | True iff memory restored, re-protected RO, and SHA-256 == golden digest |
| `cryptographic_validity` | `string` | `VALID_KEY`, `IMPLICIT_REJECTION`, or `INVALID_KEY` |
| `endpoint_acceptance` | `string` | `ACCEPTED_SESSION`, `REJECTED_SESSION`, or `CRASH_SIGNAL` |
| `sdc_determination` | `bool` | True iff `endpoint_acceptance == ACCEPTED` AND `cryptographic_validity == INVALID_KEY` |
| `post_contamination` | `bool` | True iff post-trial baseline decapsulation $\neq K_{golden}$ |
| `infrastructure_failure` | `bool` | True iff OS VM error, signal trap, or page canary corruption detected |

### 6.2 Reference Oracles and Epistemic Demarcations
* **Golden Reference Oracle:**
  $$K_{golden} = \text{SHAKE256}(K̄ || H(c))$$
* **Implicit Rejection Oracle:**
  $$K_{rej} = \text{SHAKE256}(z || H(c))$$
  where $z$ is the 32-byte rejection seed embedded in $sk$, and $H(c)$ is the SHA3-256 digest of ciphertext $c$.
* **Implicit Rejection is NOT Recovery:**
  Labeling implicit rejection as "recovery" is scientifically false. The cryptographic session failed to decrypt the message; however, it failed **securely** by returning an unlinkable rejection key.
* **Output Mismatch is NOT SDC:**
  An output mismatch is expected whenever a fault triggers implicit rejection ($K_{rej} \neq K_{golden}$). SDC occurs **only** when an invalid key $K^* \notin \{K_{golden}, K_{rej}\}$ is returned without error.

---

## 7. Requirement 6: Pilot Adequacy and Scope

### 7.1 Methodological Boundary
* `[INFERENCE]`: The 16-trial pilot is an **engineering feasibility and experimental hygiene qualification**. It is **not** a statistically powered sample to estimate fault rates or vulnerability distributions.
* `[STATIC ANALYSIS]`: What the pilot CAN establish:
  1. Darwin XNU memory protection stability under dynamic toggling.
  2. Protocol hygiene: zero cross-trial contamination across 16 sequential runs.
  3. Neutrality of VM protection toggling via sham controls (`mask = 0`).
  4. End-to-end sensitivity: proof that twiddle factor errors propagate into FO rejection.
* `[STATIC ANALYSIS]`: What the pilot CANNOT establish:
  1. Overall SDC probability across ML-KEM-768 parameter space.
  2. Comparative vulnerability across polynomial layers.
  3. Any physical radiation resilience or flight qualification.

### 7.2 Handling Inconclusive or Infrastructure-Failed Trials
* `[INFERENCE]`: If any trial experiences an infrastructure failure (`vm_protect != 0`, signal interception, canary corruption, or post-restoration contamination), the trial is **not** retried or discarded.
* `[INFERENCE]`: An infrastructure failure immediately triggers the **EMERGENCY STOP kill-switch**, terminating the pilot and invalidating the campaign until root-cause resolution.

---

## 8. Final Audit Verdict and Testable Pass/Fail Gates

### 8.1 Formal Verdict
**Verdict: CONDITIONAL GO**

The design, source patch specification, binary inspection commands, trial ledger, and claim boundaries are fully specified and methodologically sound. However, because this phase is strictly read-only, implementation approval must remain conditional on passing a sequence of testable, objective gates.

### 8.2 Sequential Pass/Fail Gates for Implementation

```
+-----------------------------------------------------------------------------+
| Stage A: Design Review Gate (RESOLVED TODAY)                                |
| [PASS] Page isolation structure defined (16KB padded struct).               |
| [PASS] Non-const C typing specified to eliminate ISO C99 UB.                 |
| [PASS] 10-field trial ledger and reference oracles formulated.              |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Stage B: Build & Binary Layout Gate (AFTER APPROVAL)                        |
| Gate B1: Research build compiles cleanly without warnings.                  |
| Gate B2: `otool -l` confirms segment `maxprot >= 0x03`.                     |
| Gate B3: `nm -n` confirms zero other symbols in [page_addr, page_addr+16KB).|
| Gate B4: Disassembly diffing confirms zero forbidden codegen divergence.     |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Stage C: Cryptographic Baseline Gate (AFTER APPROVAL)                       |
| Gate C1: 100% of NIST FIPS 203 KAT vectors pass on research binary.         |
| Gate C2: 1,000 deterministic test vectors match baseline bit-for-bit.       |
| Gate C3: Clean production build matches original baseline hash byte-for-byte|
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| Stage D: Pilot Execution & Hygiene Gate (AFTER APPROVAL)                    |
| Gate D1: Standalone `vm_protect` round-trip completes with code 0.          |
| Gate D2: 2/2 sham controls yield $K_{golden}$ with zero drift.              |
| Gate D3: Trial 8 demonstrates FO rejection matching oracle $K_{rej}$.       |
| Gate D4: 16/16 post-restoration trials pass with zero contamination.        |
| Gate D5: Zero infrastructure failures or canary corruptions.                |
+-----------------------------------------------------------------------------+
```

### 8.3 Preservation Confirmation
* Working tree: all 7 pre-existing tracked modifications preserved.
* Repository state: clean review state (0 staged, 0 commits, 0 resets).
* Zero cryptographic source or build files were modified in this audit.
