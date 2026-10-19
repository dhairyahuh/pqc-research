# Phase 2 Step 2C-B: Threats to Validity, Risk Analysis & Binary Preflight Verification

**Document:** `phase2_step2c_b_threats_to_validity.md`  
**Phase:** Phase 2 Step 2C-B (Experimental Design — Revision 3)  
**Status:** Methodological Design Specification Only (No Implementation or Execution)  
**Date:** 2026-10-04  
**Target:** ML-KEM-768 with Two-Factor Invariant Butterfly (TFIB)  

---

## 1. Threats to Experimental Validity & Methodological Mitigations

### 1.1 The Symbolic Injector Bypass Confound
- **Hazard:** A software injector accessing variables via compiler-resolved C symbols (`*zeta_ptr ^= mask`) completely ignores object sections and page boundaries. Under symbolic injection, relocating `tfib_zetas_ref` produces zero measurable difference.
- **Design Mitigation:** Step 2C-B explicitly defines **operational-table-relative spatial fault models** (Scenarios 6 & 7 in `phase2_step2c_b_fault_model.md`). The injector corrupts a contiguous address interval $[A_{\text{op}}, A_{\text{op}} + L)$ rather than naming reference variables.
- **Residual Unresolved Risk:** On the macOS ARM64 host platform, constant sections are mapped read-only (`__TEXT,__const` or `__DATA_CONST`). The test harness must dynamically toggle permissions via `vm_protect` or `mprotect`. If permission remapping is blocked by OS integrity policies, spatial fault injection cannot execute.

### 1.2 Resolving Local/Static Symbols Without `dlsym`
- **Hazard:** In production `poly.c`, `mlk_zetas` is declared with internal linkage (`static const int16_t zetas[128]`). Attempting to resolve it via `dlsym(RTLD_DEFAULT, "zetas")` or `dlsym(RTLD_DEFAULT, "mlk_zetas")` fails unconditionally because static symbols are omitted from dynamic symbol export tables (`.dynsym`).
- **Design Mitigation:** The test harness must not rely on dynamic linking APIs. Instead, the test harness build includes a dedicated compilation unit that exports an explicit link-time anchor accessor:
  ```c
  /* tfib_test_anchor.c */
  #include "poly.h"
  extern const int16_t *tfib_get_operational_zetas_anchor(void);
  ```
  This anchor function is compiled directly into the test runner binary, resolving the static symbol address at link time and returning the exact runtime pointer $A_{\text{op}}$, fully compatible with ASLR.

### 1.3 Compiler Optimization, Identical Code Folding (ICF) & Table Coalescing
- **Hazard:** Clang `-O3` and linkers (`ld64` on macOS, `lld` on Linux) perform aggressive identical data folding. Because `mlk_zetas` and `tfib_zetas_ref` contain identical 256-byte numerical contents, an optimizing linker may merge them into a single memory location, destroying layout separation.
- **Design Mitigation:**
  - `tfib_zetas_ref` is declared with external linkage in a separate translation unit and assigned to an explicit, non-standard section (`__DATA_CONST,__tfib_ref`).
  - Preflight check C-1 explicitly verifies that $\text{Addr}(A_{\text{op}}) \neq \text{Addr}(A_{\text{ref}})$ and fails closed if folding is detected.

### 1.4 Virtual Page Alignment vs Physical Isolation
- **Hazard:** Misrepresenting 16 KB virtual page alignment as physical memory protection or radiation hardening.
- **Boundary Clarification:** Virtual page alignment provides **host virtual address distance ($\ge 16\text{ KB}$)** and distinct MMU Page Table Entries (PTEs). It does **not** provide separate silicon dies, separate DRAM banks, or separate physical cache lines.

---

## 2. Exhaustive Specification of Preflight Binary Checks (C-1 to C-6)

Every compiled binary variant must pass this automated 6-point preflight validation gate before launching any fault trials. If any check fails, the test suite **aborts immediately (fails closed)**:

```
+---------------------------------------------------------------------------------------------------------+
|                                    BINARY PREFLIGHT VALIDATION GATES                                    |
+-----+----------------------------+------------------------------------+---------------------------------+
| Ref | Target Property            | Tool / Mechanism                   | Failure Condition               |
+-----+----------------------------+------------------------------------+---------------------------------+
| C-1 | Symbol Identity Separation | nm -m <bin> | grep zetas           | Abort if Addr(op) == Addr(ref)  |
| C-2 | Section Assignment         | otool -l <bin> (or llvm-objdump -h)| Abort if section assignment     |
|     |                            |                                    | does not match variant spec     |
| C-3 | Page Boundary Isolation    | Address arithmetic in preflight    | Abort if Var C is not aligned   |
|     |                            | (Addr(ref) % 16384 == 0)           | to 16,384 bytes                 |
| C-4 | Symbol Size Integrity      | Object header / symbol size check  | Abort if size != 256 bytes      |
| C-5 | Disassembly Disjointness   | llvm-objdump -d <bin>              | Abort if poly.o references ref  |
|     |                            | Inspect NTT load instructions      | or tfib_ref.o references op     |
| C-6 | Injector Address Discovery | Harness runtime self-check: query  | Abort if resolved A_op differs  |
|     |                            | anchor pointer and verify interval | from symbol table or is unmapped|
+-----+----------------------------+------------------------------------+---------------------------------+
```

### Detailed Evaluation of Each Preflight Check:

#### Check C-1: Symbol Identity Separation
- **Property Verified:** Confirms that `_mlk_zetas` and `_tfib_zetas_ref` occupy distinct virtual addresses and have not been folded together by the linker.
- **Mechanism:** `nm -m <binary>` parsed by preflight script.
- **Expected Output:** Two distinct hexadecimal addresses with difference $|\Delta| > 0$.
- **Failure Condition:** Both symbols resolve to the identical virtual address.
- **What It Cannot Establish:** Cannot guarantee that the two addresses reside on distinct virtual pages or separate sections.

#### Check C-2: Section Assignment
- **Property Verified:** Confirms that `_tfib_zetas_ref` is placed in the declared section for each variant:
  - Variant A: `(__TEXT,__const)`
  - Variant B & C: `(__DATA_CONST,__tfib_ref)` or `(__DATA_CONST,__tfib_page)`
- **Mechanism:** `otool -l <binary>` on macOS or `llvm-objdump -h <binary>` on Linux.
- **Failure Condition:** Symbol resides in `__TEXT,__const` for Variant B or C.
- **What It Cannot Establish:** Cannot guarantee that the two sections will not be mapped to adjacent physical memory frames.

#### Check C-3: Page Boundary Isolation (Variant C Only)
- **Property Verified:** Confirms that `_tfib_zetas_ref` is strictly aligned to a 16 KB virtual page boundary: $\text{Addr}(A_{\text{ref}}) \equiv 0 \pmod{16384}$ and $|\text{Addr}(A_{\text{ref}}) - \text{Addr}(A_{\text{op}})| \ge 16384$ bytes.
- **Mechanism:** Arithmetic evaluation of symbol virtual addresses.
- **Failure Condition:** Low 14 bits of address are non-zero, or distance is $< 16,384$ bytes.
- **What It Cannot Establish:** Cannot guarantee that separate virtual pages map to separate DRAM channels or banks.

#### Check C-4: Symbol Size Integrity
- **Property Verified:** Confirms that both tables allocate exactly 256 bytes (128 `int16_t` coefficients) without truncation or padding corruption.
- **Mechanism:** Symbol table byte size inspection via `llvm-nm --print-size` or Mach-O symbol table parsing.
- **Failure Condition:** Size of either symbol $\neq 256$ bytes.
- **What It Cannot Establish:** Cannot verify whether the contents of the bytes are mathematically correct twiddles (verified by KAT).

#### Check C-5: Disassembly Disjointness
- **Property Verified:** Confirms that the cryptographic NTT implementation (`poly.o`) loads twiddles exclusively from $A_{\text{op}}$ and the monitor (`tfib_ref.o`) loads twiddles exclusively from $A_{\text{ref}}$.
- **Mechanism:** Disassembly of `mlk_ntt_layer` and `tfib_inv_butterfly_check` via `llvm-objdump -d`.
- **Failure Condition:** Any cross-referencing or single-table sharing detected in the compiled instruction operands (e.g. `adrp` / `ldr` instructions).
- **What It Cannot Establish:** Cannot detect dynamically computed or register-indirect memory accesses.

#### Check C-6: Injector Address Discovery Runtime Gate
- **Property Verified:** Confirms that the in-process spatial fault injector resolves the runtime address $A_{\text{op}}$ accurately under ASLR and that the entire interval $[A_{\text{op}}, A_{\text{op}} + 512)$ resides within mapped process memory.
- **Mechanism:** Harness self-test calling `tfib_get_operational_zetas_anchor()` and querying memory regions via `vm_region_recurse_64`.
- **Failure Condition:** Anchor pointer returns NULL, address does not match binary map, or memory protection query fails.
- **What It Cannot Establish:** Does not test whether the OS will permit write permission escalation during live injection.

---

## 3. Performance Acceptance Constraint & Measurement Protocol

### 3.1 Rationale for the $\le 5.0\%$ Overhead Threshold
- **Classification:** The $\le 5.0\%$ latency threshold is an **engineering acceptance constraint**, not a primary research outcome or aerospace flight rule.
- **Grounded Technical Rationale:**
  - In Step 2C-A, the collocated TFIB-REF countermeasure introduced a **$+20.61\%$ baseline overhead** ($138.01\ \mu\text{s}$ vs $114.43\ \mu\text{s}$) due to invariant recomputations.
  - Relocating reference constants to a separate section or page changes only their virtual address. On modern CPUs, accessing constants from `__DATA_CONST` instead of `__TEXT,__const` may cause at most one additional D-TLB translation or cache line fill.
  - Setting the maximum permissible incremental overhead to $\le 5.0\%$ over collocated Variant A ensures that the memory layout modification does not introduce performance regressions (e.g. TLB thrashing or unexpected memory barrier stalls).

### 3.2 Rigorous Benchmarking Protocol
- **Workload:** 10,000 clean decapsulations following 1,000 warm-up runs.
- **System Stability Controls:**
  - Process pinned to an isolated high-performance CPU core via thread affinity (`pthread_setaffinity_np` or macOS QoS `QOS_CLASS_USER_INTERACTIVE`).
  - Fixed CPU frequency governor enabled where supported; battery saver and background indexing disabled.
- **Statistical Filtering & Reporting:**
  - Report: Arithmetic Mean, Median, Interquartile Range (IQR), 95th Percentile, 99th Percentile, and 95% bootstrap confidence interval.
  - Outliers exceeding $3 \times \text{IQR}$ from the median (attributable to OS context switches) are logged and excluded from the steady-state latency calculation.
