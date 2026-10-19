# Phase 2 Step 2C-B: Research Question, Theoretical Framework & Separation Taxonomy

**Document:** `phase2_step2c_b_research_question.md`  
**Phase:** Phase 2 Step 2C-B (Experimental Design — Revision 3)  
**Status:** Methodological Design Specification Only (No Implementation or Execution)  
**Date:** 2026-10-04  
**Target:** ML-KEM-768 with Two-Factor Invariant Butterfly (TFIB)  

---

## 1. Context, Motivation & Step 2C-A Baseline

In Phase 2 Step 2C-A, the Two-Factor Invariant Butterfly (TFIB) countermeasure was evaluated against single-point twiddle faults and coordinated paired software mutations:
1. **Single-Locus Independence:** For single-point perturbations targeting either the operational twiddle table `mlk_zetas` or the reference twiddle table `tfib_zetas_ref`, TFIB-REF demonstrated 100% detection ($N=50/50$ transient and $N=50/50$ persistent) and either genuine in-place recovery (transient) or safe fail-stop (persistent).
2. **Paired-Mutation Checker Blindness:** When both $\zeta_{\text{op}}$ and $\zeta_{\text{ref}}$ were perturbed with identical bit-flips via sequential software mutations, the local butterfly invariant check ($\Delta_{\text{diff}} \equiv 0 \pmod q$) recorded $0/50$ detections. While downstream Fujisaki-Okamoto (FO) re-encryption (147/150 trials) and centered binomial decoding error-tolerance (3/150 trials) prevented Silent Data Corruption (SDC), the local arithmetic monitor was completely blinded under matching operand corruption.
3. **Observed Binary Collocation:** Static binary inspection of the Step 2C-A executable on macOS ARM64 revealed that `mlk_zetas` (static in `poly.o`) and `tfib_zetas_ref` (global in `tfib_ref.o`) reside in the identical read-only Mach-O section (`__TEXT,__const`) separated by an offset of only **+448 bytes** (e.g. observed at `0x100017fc0` and `0x100018180`). Each table is 256 bytes (128 `int16_t` values), meaning the unmapped/padding gap between the end of `mlk_zetas` and the start of `tfib_zetas_ref` is only 192 bytes.

Step 2C-B investigates whether relocating reference constants across linker sections or virtual pages provides measurable protection against spatial multi-word memory disturbances that could bridge this narrow 192-byte gap under a software-level spatial memory fault model.

---

## 2. Central Research Question

> **Primary Research Question:** Does enforcing linker-section or virtual-page separation between operational twiddle constants and reference constants measurably reduce the probability of simultaneous reference-table corruption under an operational-table-relative spatial software fault model, thereby preserving local TFIB fault detection and recovery?

### Boundary of Investigation:
- **Primary Comparison (Confirmatory):** Isolates table placement exclusively across Variant A (Collocated), Variant B (Section-Isolated), and Variant C (Page-Isolated).
- **Secondary / Exploratory Questions (Non-Confirmatory):**
  - How does baseline ML-KEM without TFIB (Variant 0) fail under identical spatial memory disturbances?
  - Does lightweight polynomial metadata (Variant E, TFIB-META) exhibit different layout sensitivity than full twiddle tables?
  - What is the effect of absolute-address disturbances across binaries with shifting ASLR layouts?

---

## 3. Falsifiable Hypotheses

To prevent confirmation bias, Step 2C-B defines two mutually exclusive, falsifiable hypotheses for the primary comparison:

### Null Hypothesis ($H_0$)
> **$H_0$:** Enforcing linker-section separation (Variant B) or page-level isolation (Variant C) between `mlk_zetas` and `tfib_zetas_ref` produces **no statistically significant reduction** in reference-table corruption rates or improvement in local detection/recovery rates ($\Delta p < 0.10$ or $p \ge 0.01$ via McNemar's paired test with Holm-Bonferroni correction) compared to the collocated layout (Variant A) under the defined operational-table-relative spatial fault model.

*Implication:* If $H_0$ is supported, table placement in the binary image is orthogonal to fault resilience under the evaluated spatial disturbance model. Section or page relocation cannot be justified as an architectural countermeasure for twiddle integrity in software.

### Alternative Hypothesis ($H_1$)
> **$H_1$:** Enforcing linker-section or page-level isolation **measurably improves local fault detection and recovery** (with a pre-registered minimum practically meaningful effect size $\Delta p \ge 10.0\%$ and $p < 0.01$) by preventing bounded spatial memory disturbances anchored at the operational table from reaching and corrupting the reference table, thereby preserving reference-table integrity.

*Necessary Falsification Conditions:*
- $H_1$ is **falsified** if spatial memory disturbances affecting the operational table corrupt the reference table at statistically indistinguishable rates across collocated and isolated variants ($p \ge 0.01$).
- $H_1$ is **falsified** if section/page separation prevents reference corruption but introduces unrecoverable secondary faults (e.g. unhandled page faults, unexpected segfaults, or control-flow corruption) that degrade overall execution availability.
- $H_1$ is **vacuously inapplicable** if tested using a symbolic injector (which accesses variables by C pointer regardless of address placement).

---

## 4. Five-Tier Taxonomy of Memory Separation

Scientific rigor demands that logical compile-time constructs are never conflated with physical hardware isolation. Step 2C-B formally defines five levels of separation:

```
+---------------------------------------------------------------------------------------------------+
|                              MEMORY SEPARATION ABSTRACTION LEVELS                                 |
+---------+--------------------------+----------------------------------+---------------------------+
| Level   | Designation              | Implementation Mechanism         | Evaluation in Step 2C-B   |
+---------+--------------------------+----------------------------------+---------------------------+
| Level 1 | Logical Symbol           | Distinct C identifiers in        | Evaluated in Step 2C-A;   |
|         | Separation               | separate translation units       | baseline control here     |
+---------+--------------------------+----------------------------------+---------------------------+
| Level 2 | Linker-Section           | Compiler section attributes      | Evaluated in Step 2C-B    |
|         | Separation               | (__attribute__((section(...))))  | (Primary Variant B)       |
+---------+--------------------------+----------------------------------+---------------------------+
| Level 3 | Virtual Address /        | Page-alignment attributes        | Evaluated in Step 2C-B    |
|         | Page Separation          | (aligned(16384)); distinct PTEs  | (Primary Variant C)       |
+---------+--------------------------+----------------------------------+---------------------------+
| Level 4 | Process / Enclave        | Separate address spaces;         | Unverified hypothesis;    |
|         | Isolation                | hardware IPC or RPC boundaries   | out of scope for 2C-B     |
+---------+--------------------------+----------------------------------+---------------------------+
| Level 5 | Physical Hardware        | Separate silicon macros, dual-   | Strictly out of scope;    |
|         | Isolation                | port ROM, isolated power rails   | impossible on host OS     |
+---------+--------------------------+----------------------------------+---------------------------+
```

### Clarification of Evaluated Levels:
- **Level 1 (Logical Symbol Separation):** `mlk_zetas` (in `poly.o`) and `tfib_zetas_ref` (in `tfib_ref.o`) are distinct symbols, but the linker places them sequentially in `__TEXT,__const`.
- **Level 2 (Linker-Section Separation):** `tfib_zetas_ref` is placed in a separate named section (`__DATA_CONST,__tfib_ref`). This breaks contiguous placement within `__TEXT,__const` but does not guarantee distinct virtual memory pages or non-adjacent allocation.
- **Level 3 (Virtual Page Separation):** `tfib_zetas_ref` is forced onto a separate 16 KB virtual page via `__attribute__((aligned(16384)))`. This guarantees distinct Page Table Entries (PTEs) and a virtual address distance $\ge 16\text{ KB}$ in host virtual memory.
- **Levels 4 & 5 (Process / Hardware Isolation):** **Strictly Disclaimed.** Software section relocation and virtual page alignment do **not** evaluate physical memory banks, cache line conflict misses, shared memory bus contention, or silicon-level radiation tolerance. No claims of space, physical, or radiation qualification can be drawn from Level 2 or Level 3 software experiments.
