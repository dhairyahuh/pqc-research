# Phase 2 Step 2C-B: Experimental Variants & Controlled Architecture Design

**Document:** `phase2_step2c_b_experimental_design.md`  
**Phase:** Phase 2 Step 2C-B (Experimental Design — Revision 3)  
**Status:** Methodological Design Specification Only (No Implementation or Execution)  
**Date:** 2026-10-04  
**Target:** ML-KEM-768 with Two-Factor Invariant Butterfly (TFIB)  

---

## 1. Experimental Isolation Principle: Fair Comparison Design

To draw valid causal conclusions, an experiment must isolate **exactly one independent variable**. In Step 2C-B, the primary factor under investigation is the **memory placement of the reference twiddle table `tfib_zetas_ref` relative to the operational table `mlk_zetas`**.

### 1.1 Invariant vs Variant Factors Across Primary Comparison (Variants A, B, C)

```
+---------------------------------------------------------------------------------------------------------+
|                                    FACTOR ISOLATION SPECIFICATION                                       |
+----------------------------------+------------------------------+---------------------------------------+
| Factor                           | Status Across Var A, B, C    | Enforcement Mechanism                 |
+----------------------------------+------------------------------+---------------------------------------+
| Core Cryptographic Source Code   | STRICTLY INVARIANT           | algorithms/source_ref/mlkem/poly.c    |
| Core Algorithm Parameters        | STRICTLY INVARIANT           | ML-KEM-768 (q=3329, k=3, n=256)       |
| Invariant Butterfly Monitor Code | STRICTLY INVARIANT           | tfib_implementation/tfib_ref.c        |
| Reference Twiddle Constant Data  | STRICTLY INVARIANT           | Exactly identical 128 int16_t values  |
| Operational Table Section/Align  | STRICTLY INVARIANT           | __TEXT,__const, default alignment     |
| Compiler & Optimization Flags    | STRICTLY INVARIANT           | Apple clang, -O3, identical flags     |
| PRF Workload Seeds & Inputs      | STRICTLY INVARIANT           | campaign_prf.h deterministic seeds    |
| Relative Spatial Fault Definition| STRICTLY INVARIANT           | I = [A_op + Delta, A_op + Delta + L)  |
| Fault Mutation Bit-Mask Stream   | STRICTLY INVARIANT           | Domain-separated SHAKE-256 byte stream|
+----------------------------------+------------------------------+---------------------------------------+
| Reference Table Linker Section   | CONTROLLED INDEPENDENT VAR   | Var A: __TEXT,__const (Collocated)    |
|                                  |                              | Var B & C: __DATA_CONST,__tfib_ref    |
+----------------------------------+------------------------------+---------------------------------------+
| Reference Table Virtual Alignment| CONTROLLED INDEPENDENT VAR   | Var A & B: Default (2-byte)           |
|                                  |                              | Var C: 16 KB Page Aligned (16384 B)   |
+----------------------------------+------------------------------+---------------------------------------+
```

### 1.2 Layout-Dependent Detection vs Different Injector Behavior
A critical methodological threat is whether the experiment measures a **layout effect** or merely **different injector behavior**:
- In all three primary variants, the injector mutates the identical virtual address span relative to the operational table: $[A_{\text{op}}, A_{\text{op}} + 512)$ with the identical byte-level XOR mask.
- In Variant A (Collocated), the address span $[A_{\text{op}} + 448, A_{\text{op}} + 512)$ happens to map to the first 64 bytes of `tfib_zetas_ref`.
- In Variants B and C, `tfib_zetas_ref` has been relocated elsewhere in virtual memory, so the address span $[A_{\text{op}} + 448, A_{\text{op}} + 512)$ maps to linker padding or unrelated rodata, leaving `tfib_zetas_ref` uncorrupted.
- Therefore, the injector applies the **exact same spatial perturbation relative to the target computation**. The resulting divergence in checker detection represents a genuine layout-dependent effect on reference-table integrity.

---

## 2. Experimental Variants: Primary vs Exploratory

```
+----------------------------------------------------------------------------------------------------+
|                                      STEP 2C-B VARIANT MATRIX                                      |
+---------+--------------------+-------------------------+-----------------------+-------------------+
| Variant | Configuration Name | Role                    | Reference Section     | Page Alignment    |
+---------+--------------------+-------------------------+-----------------------+-------------------+
| Var A   | TFIB_REF_COLLOC    | PRIMARY COMPARISON      | __TEXT,__const (Same) | Default (+448 B)  |
| Var B   | TFIB_REF_SECTION   | PRIMARY COMPARISON      | __DATA_CONST,__tfib   | Section Boundary  |
| Var C   | TFIB_REF_PAGE_SEP  | PRIMARY COMPARISON      | __DATA_CONST,__tfib   | 16 KB Page Aligned|
+---------+--------------------+-------------------------+-----------------------+-------------------+
| Var 0   | BASELINE_UNGUARDED | CONTEXTUAL CONTROL      | N/A (No Monitor)      | Default (2-byte)  |
| Var E   | TFIB_META_SECTION  | EXPLORATORY COMPARISON  | __DATA_CONST,__tags   | Section / Page    |
+---------+--------------------+-------------------------+-----------------------+-------------------+
```

### 2.1 The Primary Comparison (Variants A, B, C)

#### Variant A: Collocated TFIB-REF (`TFIB_REF_COLLOC`) — Active Baseline
- **Architectural Placement:** Both `mlk_zetas` and `tfib_zetas_ref` are compiled into `__TEXT,__const` separated by a fixed offset of +448 bytes (observed gap of 192 bytes between table boundaries).
- **Intended Layout Property:** Collocated sequential layout in the same binary section.
- **Binary Evidence Required:** `nm -m` shows both symbols in `(__TEXT,__const)`; $\Delta_{\text{vaddr}} = 448$ bytes.
- **Fault Class Affected:** Vulnerable to spatial memory disturbances anchored at `mlk_zetas` whose extent $L > 448$ bytes.

#### Variant B: Linker-Section Isolated TFIB-REF (`TFIB_REF_SECTION`) — Section Separation
- **Architectural Placement:** `tfib_zetas_ref` is directed to a separate object-file section via compiler attribute:
  ```c
  #if defined(__APPLE__)
  __attribute__((section("__DATA_CONST,__tfib_ref")))
  #else
  __attribute__((section(".rodata.tfib_ref")))
  #endif
  const int16_t tfib_zetas_ref[TFIB_ZETA_COUNT] = { ... };
  ```
- **Intended Layout Property:** Places reference constants into a distinct Mach-O section (`__tfib_ref` inside `__DATA_CONST`), breaking contiguous address adjacency with `mlk_zetas` in `__TEXT,__const`.
- **Binary Evidence Required:** `otool -l` / `llvm-objdump -h` proves `_tfib_zetas_ref` resides in `__DATA_CONST,__tfib_ref` while `_mlk_zetas` resides in `__TEXT,__const`.
- **Fault Class Affected:** Protected against contiguous linear buffer overruns or object-section overruns within `__TEXT,__const`.
- **What Remains Unknown:** Depending on linker layout, `__DATA_CONST` may still be placed on an adjacent virtual page.

#### Variant C: Page-Aligned Isolated TFIB-REF (`TFIB_REF_PAGE_SEP`) — Virtual Page Separation
- **Architectural Placement:** Reference constants are placed in `__DATA_CONST,__tfib_ref` with strict host page alignment:
  ```c
  #define HOST_PAGE_SIZE 16384 /* 16 KB on macOS ARM64 */
  __attribute__((aligned(HOST_PAGE_SIZE)))
  __attribute__((section("__DATA_CONST,__tfib_page")))
  const int16_t tfib_zetas_ref[TFIB_ZETA_COUNT] = { ... };
  ```
- **Intended Layout Property:** Guarantees virtual address separation $\Delta_{\text{vaddr}} \ge 16\text{ KB}$ and placement in a distinct Page Table Entry (PTE).
- **Binary Evidence Required:** `nm` shows $\text{Addr}(\text{ref}) \equiv 0 \pmod{16384}$; $|\text{Addr}(\text{ref}) - \text{Addr}(\text{op})| \ge 16,384$.
- **Fault Class Affected:** Protected against any spatial memory disturbance restricted to a 4 KB or 16 KB page boundary.
- **What Remains Unknown:** Page separation in virtual memory does not guarantee separate physical RAM chips, separate cache banks, or separate memory bus lines.

---

### 2.2 Contextual and Exploratory Comparisons (Strictly Segregated)

#### Variant 0: Native ML-KEM Without TFIB (`BASELINE_UNGUARDED`)
- **Role:** Contextual baseline control. Demonstrates arithmetic corruption behavior when no monitor is present.
- **Restriction:** **Must NOT be used to infer a layout effect.** Differences between Variant 0 and Variant A reflect the presence of the monitor, not table placement.

#### Variant E: TFIB-META with Section-Isolated Tags (`TFIB_META_SECTION`)
- **Role:** Exploratory follow-up. Tests whether lightweight 256-byte polynomial metadata tags benefit from section isolation similarly to full twiddle tables.
- **Restriction:** **Must NOT be combined into the primary confirmatory comparison.** TFIB-META has fundamentally different algorithmic checking logic (it fail-stops rather than attempting arithmetic rollback).

---

## 3. Runtime Symbol Resolution & ASLR Handling

A key technical challenge is locating `_mlk_zetas` at runtime:
- In production `poly.c`, the table is defined as `static const int16_t zetas[128] = { ... };`.
- Because it has **internal (static) linkage**, standard dynamic linking tools like `dlsym(RTLD_DEFAULT, "zetas")` **cannot resolve its address**.
- **Architectural Solution for Test Harness:**
  1. The test build must include an explicit, non-static accessor function compiled alongside `poly.c`:
     ```c
     const int16_t *tfib_get_operational_zetas_anchor(void) {
         return zetas;
     }
     ```
  2. At test initialization, the harness invokes `tfib_get_operational_zetas_anchor()` to obtain the actual runtime virtual address $A_{\text{op}}$ directly.
  3. This method is **100% resilient to ASLR**, requires no symbol stripping modifications, and does not depend on fragile debug symbol scraping.

---

## 4. Causal Inference Boundaries: What This Comparison Can and Cannot Prove

### What the Primary Comparison CAN Prove:
- If Variant B or C exhibits higher local detection and recovery than Variant A under an operational-table-relative spatial fault of length $L \in (448, 16384)$ bytes, the experiment proves that **linker-section and page separation prevents reference-table corruption from address-bounded contiguous memory faults in host virtual memory**.
- If Variant B and C exhibit identical failure rates to Variant A, the experiment proves that **section relocation provides no benefit against the modeled fault class**.

### What the Primary Comparison CANNOT Prove:
- It **cannot prove physical fault independence**: Mach-O section placement does not separate silicon dies, flash bitlines, or DRAM arrays.
- It **cannot prove radiation hardness or SEU immunity**: Physical ionizing particles strike silicon coordinates, not linker sections.
- It **cannot prove security against microarchitectural faults**: Laser injection or clock glitches bypass software page tables.
