# Phase 2 Step 2C-B: Mathematical Specification of the Spatial Fault Model

**Document:** `phase2_step2c_b_fault_model.md`  
**Phase:** Phase 2 Step 2C-B (Experimental Design — Revision 3)  
**Status:** Methodological Design Specification Only (No Implementation or Execution)  
**Date:** 2026-10-04  
**Target:** ML-KEM-768 with Two-Factor Invariant Butterfly (TFIB)  

---

## 1. Addressing the Injector Confound

In Phase 2 Step 2C-A, fault injection was performed symbolically by modifying C variables passed by pointer (`*zeta_ptr ^= mask`). If an injector locates variables by symbol name or pointer, placing `tfib_zetas_ref` in a different section or page has **zero causal impact** on fault injection.

To rigorously test memory placement hypotheses, Step 2C-B defines an **address-bounded spatial fault model** that operates on contiguous ranges of virtual memory addresses rather than symbol identifiers.

---

## 2. Mathematical Definition of the Spatial Disturbance

### 2.1 Address Interval Definition
A spatial disturbance is defined mathematically as a **half-open virtual address interval**:

$$I = [A_{\text{start}}, A_{\text{end}}) = [A_{\text{anchor}} + \Delta_{\text{offset}}, A_{\text{anchor}} + \Delta_{\text{offset}} + L)$$

where:
- $A_{\text{anchor}} \in \mathbb{N}$: The reference base virtual address in the process address space.
- $\Delta_{\text{offset}} \in \mathbb{Z}$: Byte offset relative to the anchor (primary comparison sets $\Delta_{\text{offset}} = 0$).
- $L \in \mathbb{N}^+$: Length of the contiguous disturbance in bytes ($L \in \{64, 128, 256, 512, 1024\}$; primary benchmark uses $L = 512$).
- $A_{\text{end}} = A_{\text{start}} + L$: The non-inclusive upper boundary virtual address.

### 2.2 Scope of the Interval: Virtual Memory vs Actual Objects
- **Virtual Address Span:** The interval $I$ represents a contiguous range of **host virtual memory bytes**, not a logical array slice.
- **Candidate Address Selection:** Every byte address $a \in I$ is targeted sequentially: $a \in \{A_{\text{start}}, A_{\text{start}} + 1, \dots, A_{\text{end}} - 1\}$.
- **Intervening Padding & Adjacent Objects:** The disturbance is **not** restricted to table boundaries. Any linker padding, alignment bytes, or unrelated read-only objects falling within $[A_{\text{start}}, A_{\text{end}})$ are actively mutated.
- **Out-of-Range & Unmapped Addresses:**
  - Before modifying memory, the injector queries the operating system virtual memory map:
    - On macOS: `vm_region_recurse_64` to verify page mapping and protection attributes.
    - On Linux: Parsing `/proc/self/maps`.
  - If $I$ crosses into unmapped virtual address space, the injector **does not crash**. It mutates only the mapped sub-interval, logs an `UNMAPPED_PAGE_BOUNDARY` event, and continues.
  - If the operational table itself (`_mlk_zetas`) is unmapped or partially mapped, the test fails closed immediately.

### 2.3 Operational-Table-Relative Anchor (Primary Comparison)
To ensure **identical fault exposure across layout variants**, the disturbance anchor for the primary experiment is defined strictly relative to the operational twiddle table:

$$A_{\text{anchor}} \equiv A_{\text{op}} = \text{vaddr}(\_mlk\_zetas)$$

**Why Relative Anchoring is Methodologically Required:**
If the operational table moves between compiler builds or ASLR runs, using a fixed absolute address would strike different data structures in different binaries, creating an uncontrolled confound. Anchoring relative to $A_{\text{op}}$ ensures that **in every variant, the operational table experiences the exact same corruption interval**, allowing the experiment to isolate whether the reference table is within or outside the disturbance radius.

---

## 3. Operational Mutation Semantics & Read-Only Memory Modification

### 3.1 Modifying Read-Only Data (`vm_protect` Protocol)
Because constant tables reside in read-only segments (`__TEXT,__const` or `__DATA_CONST`), direct pointer writes trigger a segmentation violation (`EXC_BAD_ACCESS` / `SIGBUS`). The spatial injector must follow a strict three-phase lifecycle:

1. **Pre-Injection Permission Escalation:**
   - Identify all virtual memory pages spanned by $I$:
     $$P_{\text{start}} = \lfloor A_{\text{start}} / \text{PAGE\_SIZE} \rfloor \times \text{PAGE\_SIZE}, \quad P_{\text{end}} = \lceil A_{\text{end}} / \text{PAGE\_SIZE} \rceil \times \text{PAGE\_SIZE}$$
   - On macOS:
     ```c
     kern_return_t kr = vm_protect(mach_task_self(), P_start, P_end - P_start, FALSE,
                                   VM_PROT_READ | VM_PROT_WRITE | VM_PROT_COPY);
     ```
   - On Linux:
     ```c
     int ret = mprotect((void*)P_start, P_end - P_start, PROT_READ | PROT_WRITE);
     ```
2. **Deterministic Mutation Application:**
   - For every mapped byte $a \in I$, apply an in-place bitwise XOR:
     $$\text{mem}[a] \leftarrow \text{mem}[a] \oplus M(a - A_{\text{start}})$$
     where $M: [0, L) \to \{0x01, \dots, 0xFF\}$ is derived from the trial seed via domain-separated SHAKE-256 (`campaign_prf.h`). An all-zero mask byte is rejected and regenerated.
3. **Post-Decapsulation Clean Restoration:**
   - After decapsulation completes, the harness restores pristine byte contents from an immutable golden oracle buffer in heap memory.
   - Page permissions are reset back to read-only (`VM_PROT_READ` / `PROT_READ`).

---

## 4. Five-Tier Taxonomy of Fault Effects

To prevent confusing physical faults, memory corruption, and algorithmic outcomes, the experiment distinguishes five distinct levels:

```
+---------------------------------------------------------------------------------------------------+
|                                FAULT TAXONOMY & EFFECT PROPAGATION                                |
+-------+--------------------------+----------------------------------------------------------------+
| Level | Category                 | Definition & Operational Meaning in Step 2C-B                  |
+-------+--------------------------+----------------------------------------------------------------+
| T-1   | Intended Target          | The virtual address interval I = [A_op, A_op + L).             |
+-------+--------------------------+----------------------------------------------------------------+
| T-2   | Actual Modified Bytes    | The subset of mapped bytes in I where non-zero XOR mask is     |
|       |                          | successfully applied.                                          |
+-------+--------------------------+----------------------------------------------------------------+
| T-3   | Ineffective Faults       | Modified bytes in padding, gap, or unread coefficients that do |
|       |                          | not participate in the decapsulation NTT layers.               |
+-------+--------------------------+----------------------------------------------------------------+
| T-4   | Observed Execution Effect| Local monitor behavior during execution:                       |
|       |                          | - Single Detection & Recovery (reference intact, op corrupted) |
|       |                          | - Checker Blindness (both tables corrupted identically)        |
|       |                          | - Poisoned Rollback (both tables corrupted differently)        |
+-------+--------------------------+----------------------------------------------------------------+
| T-5   | Cryptographic Outcome    | Final end-to-end decapsulation result:                         |
|       |                          | - Valid Key Established (genuine recovery or decoding slack)   |
|       |                          | - Safe Implicit Rejection (FO re-encryption mismatch)          |
|       |                          | - Silent Data Corruption (SDC: invalid shared secret accepted) |
+-------+--------------------------+----------------------------------------------------------------+
```

---

## 5. Worked Address-Range Example (Build-Specific Observation)

> [!NOTE]
> The addresses below are **build-specific empirical observations** from the macOS ARM64 binary compiled in Step 2C-A. They illustrate the mathematical boundary conditions and must be resolved dynamically at runtime by the test harness for any specific build.

### Observed Layout in Step 2C-A Collocated Binary (Variant A):
- Operational table: $A_{\text{op}} = \text{vaddr}(\_mlk\_zetas) = \text{0x100017fc0}$
  - Span: $[\text{0x100017fc0}, \text{0x1000180c0})$ (256 bytes)
- Reference table: $A_{\text{ref}} = \text{vaddr}(\_tfib\_zetas\_ref) = \text{0x100018180}$
  - Span: $[\text{0x100018180}, \text{0x100018280})$ (256 bytes)
- Spatial Gap between table boundaries:
  $$\text{Gap} = A_{\text{ref}} - (A_{\text{op}} + 256) = \text{0x100018180} - \text{0x1000180c0} = \text{0xC0} = 192 \text{ bytes}$$
- Start-to-Start Offset:
  $$\Delta_{\text{start}} = A_{\text{ref}} - A_{\text{op}} = \text{0x100018180} - \text{0x100017fc0} = \text{0x1C0} = 448 \text{ bytes}$$

```
Address: 0x100017fc0        0x1000180c0        0x100018180        0x100018280
Layout:  [  mlk_zetas (256B)  ] [ Gap: 192B ]   [ tfib_zetas_ref (256B) ]
Interval:
Blast 1: [========= L = 512B, Anchor = A_op = 0x100017fc0 ==========>] (Overlaps 64B of Ref!)
Blast 2:       [==== L = 512B, Centered at Midpoint = 0x100018040 ====>] (Ends at 0x100018140 - SPARES Ref!)
```

### Case Analysis of Disturbance Interval $I = [A_{\text{start}}, A_{\text{start}} + L)$:

#### Case 1: Forward-Anchored Disturbance ($A_{\text{start}} = A_{\text{op}} = \text{0x100017fc0}$, $L = 512$ bytes)
- Disturbance bounds: $[\text{0x100017fc0}, \text{0x1000181c0})$
- Coverage of `mlk_zetas`: $[\text{0x100017fc0}, \text{0x1000180c0})$ $\to$ **100% (256/256 bytes corrupted)**.
- Coverage of intermediate gap: $[\text{0x1000180c0}, \text{0x100018180})$ $\to$ 192 bytes corrupted (padding/ineffective).
- Coverage of `tfib_zetas_ref`: $[\text{0x100018180}, \text{0x1000181c0})$ $\to$ **64 bytes corrupted (first 32 coefficients)**.
- **Outcome in Variant A:** **Dual-table corruption occurs.** Local checker reference is corrupted; in-place repair arithmetic is poisoned.
- **Outcome in Variant B/C:** $A_{\text{ref}} \ge A_{\text{op}} + 16,384$. The disturbance interval $[\text{0x100017fc0}, \text{0x1000181c0})$ does not reach $A_{\text{ref}}$. `tfib_zetas_ref` is **100% uncorrupted**. Local checker detects the twiddle mismatch and recovers cleanly.

#### Case 2: Midpoint-Centered Disturbance ($A_{\text{start}} = A_{\text{op}} + 128 - 256 = A_{\text{op}} - 128$, $L = 512$ bytes)
- Disturbance bounds: $[A_{\text{op}} - 128, A_{\text{op}} + 384) = [\text{0x100017f40}, \text{0x100018140})$.
- End of disturbance is $\text{0x100018140} < A_{\text{ref}} (\text{0x100018180})$.
- Coverage of `tfib_zetas_ref`: **0 bytes**.
- **Outcome:** Reference table is spared even in Variant A!
- **Methodological Rule:** A 512-byte blast does **not** inherently corrupt both tables unless the anchor and offset are explicitly forward-directed ($\Delta_{\text{offset}} = 0$). The experimental protocol mandates forward anchoring for the primary comparison.

---

## 6. Prohibited Physical Claims

- The spatial disturbance model evaluates **host virtual address proximity only**.
- Virtual address proximity **does not imply physical silicon proximity**. In modern DRAM and NAND flash, virtual addresses undergo multiple levels of non-linear address translation (MMU paging, memory controller interleaving, bank hashing, and row-column multiplexing).
- Corrupting contiguous bytes in virtual memory **does not simulate a physical heavy-ion strike or localized laser irradiation**.
