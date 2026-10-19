# Phase 14B — Persistent-Storage Arm: Design Blockers Resolution

**Author:** Skeptical Cryptographic Implementation & Experimental Methodology Reviewer  
**Status:** DESIGN CORRECTION ONLY — NO SOURCE OR BUILD MODIFICATIONS PERFORMED  
**Date:** 2026-10-11  
**Deliverable Directory:** `research/phase14_persistent_arm_design/`

---

## 1. Executive Summary & Review Intent

Phase 14 established the initial conceptual framework for a research-only persistent-storage fault experiment targeting the operational ML-KEM-768 twiddle-factor table `mlk_zetas`. However, a rigorous skeptical review identified seven critical design blockers that must be resolved prior to seeking implementation approval:

1. **Mach-O Layout Gap:** Source section attributes were conflated with linked binary placement; `__DATA_CONST` was assumed to be writable without verifying linker-generated segment protection commands.
2. **Page Isolation Gap:** Page size was assumed rather than verified; alignment was mistakenly assumed to prevent co-locating unrelated constants on the 16 KB page.
3. **Compiler Semantics Gap:** Casting away `const` and adding `volatile` introduces ISO C undefined behavior (UB) and fails to prove that the NTT consumes mutated bytes.
4. **Baseline Equivalence Gap:** Insufficient criteria for verifying that the research build is mathematically and structurally equivalent to the baseline before faults are injected.
5. **Trial Ledger Conflation:** Outcomes conflated fault activation, implicit rejection, SDC, and infrastructure failure without an explicit endpoint contract.
6. **Pilot Justification Gap:** The 16-trial pilot was inadequately justified and risked being interpreted as a statistical sample.
7. **Approval Boundary Ambiguity:** The boundary between existing artifact verification and unbuilt research build hypotheses was insufficiently sharp.

This document resolves all seven issues conclusively.

---

## 2. Issue 1: Mach-O Layout & Linked Segment/Section Verification

### 2.1 Object Attributes vs Final Linked Segment Placement
Specifying `__attribute__((section("__DATA_CONST,__const")))` in C source instructs the compiler to place the symbol in that section in the intermediate object file (`.o`). However:
* In Mach-O, the static linker (`ld64`) takes object sections and maps them into top-level segments (`LC_SEGMENT_64`) in the final executable binary.
* `ld64` assigns segment permissions: `initprot` (initial protection at process startup) and `maxprot` (maximum allowable protection achievable via `vm_protect`).
* If `ld64` assigns `maxprot = VM_PROT_READ` (`0x01`) to the segment enclosing `__DATA_CONST`, any subsequent call to `vm_protect(..., VM_PROT_READ | VM_PROT_WRITE)` will be immediately rejected by the Darwin kernel with `KERN_PROTECTION_FAILURE` (`kr = 2`), regardless of the section name.
* Furthermore, dyld maps `__DATA_CONST` at load time and can apply library validation or code-signing restrictions under macOS Hardened Runtime.

### 2.2 Final Linked Binary Inspection Protocol
We **cannot** claim `__DATA_CONST` is writable merely because the symbol is assigned there in source. The final linked executable must undergo three levels of verification before any fault injection code is executed:

1. **Static Segment Command Verification (`otool -l <binary>`):**
   Examine the `LC_SEGMENT_64` containing the relocated table.
   * `initprot` must be `r--` (`0x01`).
   * `maxprot` **must** include write capability (`rw-` / `0x03` or `rwx` / `0x07`). If `maxprot == 0x01`, `vm_protect` is impossible $\rightarrow$ **HARD NO-GO**.
2. **In-Process Virtual Memory Query (`vm_region_64`):**
   At process startup before injection, the runner must query the memory region enclosing `mlk_zetas`:
   ```c
   vm_address_t addr = (vm_address_t)table_ptr;
   vm_size_t size;
   vm_region_basic_info_data_64_t info;
   mach_msg_type_number_t count = VM_REGION_BASIC_INFO_COUNT_64;
   mach_port_t object_name;
   kern_return_t kr = vm_region_64(mach_task_self(), &addr, &size,
                                   VM_REGION_BASIC_INFO_64,
                                   (vm_region_info_t)&info, &count, &object_name);
   assert(kr == KERN_SUCCESS);
   assert((info.max_protection & VM_PROT_WRITE) != 0);
   ```
3. **Execution-Time Protection Verification:**
   `vm_protect` must return `KERN_SUCCESS` during the unprotection call, and the subsequent memory write must complete without delivering `SIGBUS` (signal 10) or `SIGSEGV` (signal 11).

---

## 3. Issue 2: Page Isolation & Verified Host Page Granularity

### 3.1 Host Page Size Verification
Rather than assuming a 16 KB page, host inspection commands were executed directly on the evaluation host:
* Shell utility `pagesize`: outputs `16384` bytes.
* C runtime `getpagesize()` / `sysconf(_SC_PAGESIZE)`: returns `16384` bytes (`0x4000`).
* Kernel architecture: Darwin 27.0.0 Apple Silicon arm64 (`PAGE_SIZE = 16384`).

### 3.2 The Insufficiency of Alignment Alone
The operational table `mlk_zetas` consists of 128 `int16_t` values = 256 bytes (`0x100`).
* Declaring `__attribute__((aligned(16384)))` guarantees only that the symbol starts at offset `0x0000` of a 16 KB page.
* It does **not** protect the remaining `16,384 - 256 = 16,128` bytes (`0x0100` through `0x3FFF`) on that page.
* The static linker is permitted to pack other constants, string literals, jump tables, or compiler data into those remaining 16,128 bytes.
* If `vm_protect(page_addr, 16384, ..., VM_PROT_READ | VM_PROT_WRITE)` is called, **all unrelated constants sharing that page become writable**. Any stray write, race condition, or memory corruption would alter unrelated program state undetected.

### 3.3 Guaranteed Page Isolation Design
To guarantee that `mlk_zetas` is the sole inhabitant of its 16 KB page, the research build must enforce both page-alignment and **explicit page-sized allocation padding**:
```c
#if defined(MLKEM_RESEARCH_RELOCATE_ZETAS)
/* Structure guaranteeing exact 16KB page isolation on Apple Silicon */
typedef struct {
    int16_t zetas[128]; /* 256 bytes of operational twiddle factors */
    uint8_t page_padding[16384 - (128 * sizeof(int16_t))]; /* 16,128 bytes of padding */
} mlk_isolated_zetas_page_t;

#if defined(__APPLE__)
__attribute__((section("__DATA_CONST,__zetas_page"), aligned(16384)))
#else
__attribute__((section(".rodata.zetas_page"), aligned(4096)))
#endif
static mlk_isolated_zetas_page_t mlk_zetas_page = {
    .zetas = {
        -1044, -758, -359, -1517, 1493, 1422, 287, 202, ...
    },
    .page_padding = {0}
};

/* Symbol alias for internal NTT access */
#define mlk_zetas (mlk_zetas_page.zetas)
#endif
```

### 3.4 Binary Isolation Proof & Stop Rule
Before executing any trial, the binary layout must be proven via symbol inspection:
```bash
# Verify no other symbol falls in the range [page_addr, page_addr + 16384)
nm -n <binary> | awk -v p=0x<page_addr> '$1 >= p && $1 < p + 16384 { print }'
```
* **Acceptance Criterion:** The only symbol located within `[page_addr, page_addr + 0x4000)` must be `_mlk_zetas_page` (or `_mlk_zetas`).
* **NO-GO Rule:** If any other symbol is co-located on the same page, the experiment is an immediate **HARD NO-GO**.

---

## 4. Issue 3: Compiler Semantics, Undefined Behavior, and Consumption Proof

### 4.1 Eliminating Undefined Behavior (UB)
* **The Problem:** In ISO C99 §6.7.3, modifying an object declared `const` through a non-const pointer cast is **undefined behavior**. If `mlk_zetas` is defined `const`, LLVM Clang is legally permitted to assume its value never changes, license constant propagation, optimize away reads, or assume that no memory write aliases with it.
* **The Solution:** In the modified research build (`MLKEM_RESEARCH_RELOCATE_ZETAS`), the underlying storage `mlk_zetas_page.zetas` is declared **without the `const` qualifier** in C source.
* **Why this is sound:** In standard C, mutating a non-const object is 100% defined behavior. Its read-only semantics during decapsulation are enforced at the OS virtual memory layer (`vm_protect` set to `VM_PROT_READ`), accurately modeling physical hardware ROM/Flash storage.

### 4.2 Why Separate TUs and `volatile` Do Not Prove Consumption
Using `volatile` in the harness or writing from a separate translation unit (TU) only prevents the compiler from optimizing away the *harness's* write. It provides **zero guarantee** that `poly.c`'s compiled NTT will actually read the mutated value from memory, because:
1. Loops might be unrolled with constants folded into vector registers before the write occurred.
2. Registers holding twiddle factors might be preserved across function calls if inlined.

### 4.3 Disassembly and Runtime Consumption Evidence Plan
Consumption must be proven by two independent evidence layers:
1. **Disassembly Verification:**
   Disassemble `mlkem_poly_invntt_tomont` and `mlkem_poly_mulcache_compute`. Every loop layer must contain explicit memory loads (`ldrsh`, `ldr q`) from the relocated page base address. No butterfly arithmetic may use immediate constant operands for twiddle factors.
2. **Mathematical Sensitivity Verification (Pilot Trial 8):**
   Inject a known fault into mulcache twiddle factor $\zeta_{64}$ (`index 64`, `mask = 0x0001`).
   * The reference message vector $m$ is decrypted via $w = \text{PolyVecInvNTT}(\hat{\mathbf{s}}^T \circ \text{PolyVecNTT}(\mathbf{u}))$.
   * A fault in $\zeta_{64}$ mathematically distorts coefficient $w_0$, causing reconstructed message bit $m'_0 \neq m_0$.
   * Re-encryption with distorted $m'$ produces ciphertext $c' \neq c$, causing Fujisaki-Okamoto re-encryption comparison to fail.
   * Runtime verification confirms that the decapsulation output switches from $K_{golden}$ to $K_{rej} = \text{SHAKE256}(z || H(c))$.
   * This proves conclusively that the mutated memory bytes were physically consumed by the NTT and altered the arithmetic execution path.

---

## 5. Issue 4: Baseline Equivalence Checks & Legitimate Differences

Before any fault is injected, the original baseline build (`mlkem768.o`) and the relocated research build (`mlkem768_persistent_reloc.o`) must be evaluated for strict equivalence.

### 5.1 Prerequisite Equivalence Gates
1. **NIST FIPS 203 KAT Suite:** Both builds must achieve 100% vector passage on all ML-KEM parameter sets (`test_fips_kats`).
2. **Deterministic Output Equivalence:** For a test suite of 1,000 reference ciphertexts and secret keys, decapsulation outputs must match bit-for-bit:
   $$\forall i \in [0, 999], \quad \text{Decaps}_{research}(c_i, sk_i) == \text{Decaps}_{baseline}(c_i, sk_i) == K_{golden, i}$$
3. **Build Flag Parity:** Both objects must be compiled with identical flags:
   `clang -O3 -std=c99 -Wall -Wextra -I algorithms/source_ref/mlkem -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem -DMLK_CONFIG_PARAMETER_SET=768`.

### 5.2 Disassembly Diffing & Legitimate Differences
Disassembly of `mlkem_poly_invntt_tomont`, `mlkem_poly_ntt`, and `mlkem_poly_mulcache_compute` must be compared side-by-side:
* **Legitimate Relocation Differences (Acceptable):**
  * PC-relative displacement offset in `adrp` instructions (reflecting relocation from `__TEXT` to `__DATA_CONST`).
  * Relocation entries in the Mach-O header (`ARM64_RELOC_PAGE21` targeting `_mlk_zetas_page` instead of `_mlk_zetas`).
* **Illegitimate Differences (Invalidating the Comparison $\rightarrow$ STOP):**
  * Any change in total instruction count within the NTT butterfly inner loops.
  * Any change in vector instruction selection (`smull`, `mul`, `addhn`, `shrn`).
  * Any change in register spilling, stack frame allocation, or loop unrolling structure.
  * Failure to inline static helpers that were inlined in the baseline.

---

## 6. Issue 5: Rigorous Trial Ledger & Cryptographic Endpoint Contract

### 6.1 Disaggregated Trial Ledger Schema
To eliminate conflation, the experiment ledger (`PILOT_RESULTS.csv`) must record 9 strictly separated fields for every trial:

| Field Name | Type | Description |
|---|---|---|
| `fault_requested` | `string` | Target index, bit mask, and injection type (e.g. `idx=64,mask=0x0001,single_bit`) |
| `activation_verified` | `bool` | True iff `vm_protect(RW)` and write succeeded without OS signal / trap |
| `target_bytes_changed` | `bool` | True iff read-back immediately post-write equals `golden ^ mask` |
| `consumption_verified` | `string` | `PROVEN_REJECTION`, `PROVEN_SDC`, `MASKED_BENIGN`, or `UNVERIFIED` |
| `restoration_verified` | `bool` | True iff `target = golden`, re-protected RO, and full 256-byte SHA-256 == golden digest |
| `crypto_validity` | `string` | Cryptographic state: `VALID_KEY`, `IMPLICIT_REJECTION`, or `INVALID_KEY` |
| `endpoint_outcome` | `string` | Endpoint state: `SUCCESS_GOLDEN`, `REJECTED_REJ_KEY`, `UNTRACKED_KEY`, `CRASH_SIGNAL` |
| `sdc_determination` | `bool` | True iff `endpoint_outcome == UNTRACKED_KEY` and process exited cleanly |
| `hygiene_failure` | `bool` | True iff post-restoration decapsulation $\neq K_{golden}$ or memory leak detected |

### 6.2 Formal Cryptographic Endpoint Contract
In NIST FIPS 203 ML-KEM-768, decapsulation takes ciphertext $c$ and secret key $sk = (d_K || dk_{PKE} || ek_{PKE} || H(ek) || z)$:
1. Decrypt: $m' = \text{K-PKE.Decrypt}(dk_{PKE}, c)$.
2. Re-encrypt: $(\hat{K}', r') = G(m' || H(ek))$; $c' = \text{K-PKE.Encrypt}(ek_{PKE}, m', r')$.
3. Fujisaki-Okamoto verification:
   $$\text{If } c' == c \implies K = J(\hat{K}' || H(c)) \quad (\text{Valid Shared Secret } K_{golden})$$
   $$\text{If } c' \neq c \implies K = J(z || H(c)) \quad (\text{Implicit Rejection Secret } K_{rej})$$

### 6.3 Demarcation of SDC, Implicit Rejection, and Recovery
* **Valid Implicit Rejection (`crypto_validity == IMPLICIT_REJECTION`):**
  Output equals $K_{rej}$. The Fujisaki-Okamoto check successfully detected the arithmetic error and prevented key compromise.
  * **Critical Clarification:** Implicit rejection is **NOT** "recovery". The session failed; decapsulation did not recover the intended session key. However, it failed **safely**.
* **Silent Data Corruption (`sdc_determination == TRUE`):**
  Strictly defined as: `output != K_golden` **AND** `output != K_rej` **AND** `exit_code == 0`.
  This represents an untracked, corrupted key accepted without rejection.
* **Output Mismatch is NOT Automatically SDC:** An output differing from $K_{golden}$ is expected whenever a fault triggers implicit rejection ($K_{rej}$). Conflating rejection with SDC is scientifically false.

---

## 7. Issue 6: Pilot Justification & Scope

### 7.1 Methodological Justification of the 16-Trial Pilot
The proposed 16-trial pilot is **strictly an engineering feasibility and protocol hygiene qualification**.
* It is **not** a statistically powered sample to estimate fault injection probabilities, vulnerability rates, or distribution tails.
* It exists to validate the 14-step transactional pipeline, confirm page unprotection/reprotection stability, and prove zero cross-trial contamination on deterministic boundary test cases.

### 7.2 What the Pilot Can and Cannot Conclude
* **What the Pilot CAN Conclude:**
  1. Whether `vm_protect` toggling on `__DATA_CONST` operates cleanly without kernel aborts on macOS arm64.
  2. Whether in-place restoration restores bit-identical baseline state across consecutive runs.
  3. Whether sham controls (`mask = 0`) prove that VM protection APIs introduce zero computational artifacts.
  4. Whether NTT twiddle factor corruption propagates through decapsulation into FO rejection.
* **What the Pilot CANNOT Conclude:**
  1. The overall SDC rate of ML-KEM-768 under persistent memory faults.
  2. The relative sensitivity of different polynomial layers across full random fault sweeps.
  3. Any physical resilience or radiation vulnerability characteristics.

---

## 8. Issue 7: Clear Demarcation of the Approval Boundary

To maintain complete methodological integrity, we explicitly distinguish what is verified from existing workspace artifacts today from what remains an unbuilt research hypothesis:

### 8.1 Facts Verified Today from Existing Workspace Artifacts:
1. `bin/obj/mlkem768.o` places `_mlk_zetas` in `(__TEXT,__const)` (Mach-O object inspection).
2. Compiled code loads `_mlk_zetas` dynamically from memory via `adrp` + `ldrsh` / `ldr q` (disassembly inspection).
3. Directly attempting `vm_protect(RW)` on `__TEXT` on this host triggers `SIGBUS` (signal 10 / exit 138), verified in Phase 11.
4. Host page size is verified as 16,384 bytes (`pagesize`).
5. All seven pre-existing tracked modifications and baseline datasets are preserved intact.

### 8.2 Hypotheses Requiring Explicit Implementation Approval:
1. Whether Clang compiles the proposed `mlk_zetas_page` into `__DATA_CONST` without warnings.
2. Whether `ld64` assigns `maxprot >= VM_PROT_WRITE` to the resulting linked binary segment.
3. Whether disassembly of the research build confirms zero changes to inner-loop instruction schedules.
4. Whether the 16-trial pilot completes with zero cross-trial contamination.

**No claim of binary feasibility for the modified build is made until that build is explicitly approved, compiled, and audited.**

---

## 9. Revised Decision & Approval Request

* **Revised Verdict:** **CONDITIONAL GO** (Design approved; Implementation strictly blocked).
* **Pre-conditions for Implementation:**
  1. Formal approval of the exact source diff and build rules.
  2. Execution of Gate 1 binary inspection before attempting any memory write.
  3. Execution of the 16-trial pilot before considering any larger campaign.

### Exact Proposed Changes Requiring Approval:
```diff
--- a/algorithms/source_ref/mlkem/src/zetas.inc
+++ b/algorithms/source_ref/mlkem/src/zetas.inc
@@ -14,6 +14,19 @@
  * Table of zeta values used in the reference NTT and inverse NTT.
  * See autogen for details.
  */
+#if defined(MLKEM_RESEARCH_RELOCATE_ZETAS)
+/* Research-only persistent storage fault arm:
+ * 16KB page-isolated, non-const storage to eliminate UB and collateral page exposure */
+typedef struct {
+    int16_t zetas[128];
+    uint8_t page_padding[16384 - (128 * sizeof(int16_t))];
+} mlk_isolated_zetas_page_t;
+
+__attribute__((section("__DATA_CONST,__zetas_page"), aligned(16384)))
+static mlk_isolated_zetas_page_t mlk_zetas_page = {
+    .zetas = {
+#else
 static MLK_ALIGN const int16_t mlk_zetas[128] = {
+#endif
     -1044, -758,  -359,  -1517, 1493,  1422,  287,   202, ...
@@ -30,2 +43,5 @@
 };
+#if defined(MLKEM_RESEARCH_RELOCATE_ZETAS)
+#define mlk_zetas (mlk_zetas_page.zetas)
+#endif

--- a/algorithms/source_ref/mlkem/src/poly.c
+++ b/algorithms/source_ref/mlkem/src/poly.c
@@ -268,6 +268,16 @@
 #include "zetas.inc"
 
+#if defined(MLKEM_RESEARCH_RELOCATE_ZETAS)
+int16_t *mlkem_research_get_zetas_mutable_ptr(void)
+{
+  return mlk_zetas_page.zetas;
+}
+const int16_t *mlkem_research_get_zetas_table(void)
+{
+  return mlk_zetas_page.zetas;
+}
+#endif
```

```makefile
# Addition to Makefile (isolated research target; leaves existing targets untouched):
$(OBJ_DIR)/mlkem768_persistent_reloc.o: algorithms/source_ref/mlkem/mlkem_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mlkem \
	  -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem \
	  -DMLK_CONFIG_PARAMETER_SET=768 \
	  -DMLKEM_RESEARCH_RELOCATE_ZETAS \
	  -c $< -o $@
```

**Approval Gate:** No files outside `research/phase14_persistent_arm_design/` have been or will be touched without explicit user instruction.
