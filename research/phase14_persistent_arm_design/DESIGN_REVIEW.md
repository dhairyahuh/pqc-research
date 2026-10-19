# Phase 14 — Persistent-Storage Fault Arm: Design Review

**Author:** Skeptical Cryptographic Implementation & Experimental Methodology Reviewer  
**Status:** DESIGN & FEASIBILITY REVIEW ONLY — NO IMPLEMENTATION PERFORMED  
**Target:** Operational ML-KEM-768 Twiddle-Factor Table `mlk_zetas` (`algorithms/source_ref/mlkem/src/zetas.inc`)  
**Platform:** macOS Darwin 24.x / 27.x (Apple Silicon arm64, clang 17+, Mach-O)

---

## 1. Executive Summary & Review Verdict

* **Verdict:** **CONDITIONAL GO (Design Approved for Formal Review; Implementation Blocked Pending Explicit Approval)**
* **Scope Restriction:** This review designs an auditable software-level fault injection experiment targeting the in-memory backing storage of the ML-KEM-768 twiddle-factor table. It **does not implement** the changes, **does not modify** cryptographic source files, and **does not execute** the campaign.
* **Fundamental Claim Boundary:** The proposed intervention is a **software-level memory-mutation experiment on a modified research build**. It **cannot and will not** establish radiation resilience, Single-Event Upset (SEU) physical cross-sections, or hardware-level space qualification.

---

## 2. Baseline Implementation Analysis

### 2.1 Symbol Declaration, Linkage, and Memory Placement
The operational twiddle-factor table for ML-KEM-768 is declared in `algorithms/source_ref/mlkem/src/zetas.inc`:
```c
/* algorithms/source_ref/mlkem/src/zetas.inc:17 */
static MLK_ALIGN const int16_t mlk_zetas[128] = {
    -1044, -758,  -359,  -1517, 1493,  1422,  287,   202, ...
};
```
* **Type & Size:** Array of 128 signed 16-bit integers (`int16_t`), totaling exactly 256 contiguous bytes (`0x100` bytes).
* **Alignment:** `MLK_ALIGN` expands to `__attribute__((aligned(32)))` via `algorithms/source_ref/mlkem/src/sys.h:205`.
* **Linkage:** `static` specifies internal linkage. The symbol is strictly private to the Single Compilation Unit (SCU) `mlkem_native.c`.
* **Binary Section:** Inspecting the compiled baseline object `bin/obj/mlkem768.o` via `nm -m` reveals:
  ```text
  00000000000190c0 (__TEXT,__const) non-external _mlk_zetas
  ```
  The table is placed in the `__TEXT` segment (`__const` section) of the Mach-O binary.

### 2.2 Table Consumption in the NTT Call Graph
`mlkem_native.c` includes `src/poly.c`, which includes `src/zetas.inc`. The table `mlk_zetas` is read in three distinct cryptographic operations:
1. **Multiplication Cache Computation (`mlk_poly_mulcache_compute_c`, `poly.c:288, 292`):**
   ```c
   x->coeffs[2 * i + 0] = mlk_fqmul(a->coeffs[4 * i + 1], mlk_zetas[64 + i]);
   x->coeffs[2 * i + 1] = mlk_fqmul(a->coeffs[4 * i + 3], (int16_t)(-mlk_zetas[64 + i]));
   ```
   Reads indices `64` through `127` (64 elements, 128 bytes).
2. **Forward NTT Layer Computation (`mlk_ntt_layer_c`, `poly.c:447`):**
   ```c
   int16_t zeta = mlk_zetas[k++];
   mlk_ntt_butterfly_block(r, zeta, start, len, layer, layer * MLKEM_Q);
   ```
   Sequential access from index `1` through `127` across layers 1 to 7.
3. **Inverse NTT Layer Computation (`mlk_invntt_layer_c`, `poly.c:546`):**
   ```c
   int16_t zeta = mlk_zetas[k--];
   ```
   Reverse access from index `127` down to `1`.

### 2.3 Runtime Memory Load vs Constant Folding
Disassembly of `bin/obj/mlkem768.o` via `xcrun llvm-objdump -d -r --symbolize-operands` confirms that the compiler (`clang -O3`) **does not fold** table values into immediate instructions. Instead, it generates PC-relative page-addressed memory loads:
```assembly
5ad8: 9000000c   adrp  x12, 0x5000
                 0000000000005ad8: ARM64_RELOC_PAGE21    _mlk_zetas
5adc: 9100018c   add   x12, x12, #0x0
                 0000000000005adc: ARM64_RELOC_PAGEOFF12 _mlk_zetas
...
5ae8: 8b090190   add   x16, x12, x9
5aec: 79c10210   ldrsh w16, [x16, #0x80]
```
Similarly, vectorized loops issue 128-bit SIMD loads (`ldr q2, [x9], #-0x10`). This proves conclusively that `mlk_zetas` is read as an **in-memory operational table** during decapsulation.

---

## 3. Platform-Specific Enforcement & Root Cause of SIGBUS

### 3.1 Darwin / Mach-O Hardened Protections (`__TEXT` Segment)
* On Apple Silicon (arm64 Darwin), the kernel memory manager (XNU) enforces strict W^X (Write XOR Execute) and Code Signing validation on the `__TEXT` segment.
* All sections within `__TEXT` (`__TEXT,__text`, `__TEXT,__const`) are mapped with `VM_PROT_READ | VM_PROT_EXECUTE`.
* Attempting to call `vm_protect(mach_task_self(), page, size, FALSE, VM_PROT_READ | VM_PROT_WRITE)` on a code-signed `__TEXT` page triggers kernel-level violation or hardware page protection traps, resulting in an immediate **`SIGBUS` (Exit Code 138)**.
* **Conclusion:** Injecting persistent faults into `mlk_zetas` in its upstream baseline section (`__TEXT,__const`) is **physically blocked by the operating system**.

### 3.2 Relocation to `__DATA_CONST` & Page Isolation Requirements
* The Mach-O segment `__DATA_CONST` is designed for data that is initialized at binary load time and then protected read-only (`VM_PROT_READ`). It does **not** have `VM_PROT_EXECUTE`.
* As demonstrated empirically in Phase 11 (`research/phase11_persistent_feasibility/` 128/128 successful trials), memory pages in `__DATA_CONST` can be dynamically altered using `vm_protect(..., VM_PROT_READ | VM_PROT_WRITE)`, written to, and restored to `VM_PROT_READ` without triggering kernel traps.
* **Critical Page-Granularity Hazard:** On Apple Silicon, virtual memory page granularity is verified as **16 KB (16,384 bytes)** (`PAGE_SIZE = 0x4000`), whereas `mlk_zetas` is only **256 bytes**.
  * Calling `vm_protect` on the page containing `mlk_zetas` changes permissions for an entire 16 KB window.
  * If alignment alone (`aligned(16384)`) is used without sizing padding, the static linker (`ld64`) can place other constants in the remaining `16,384 - 256 = 16,128` bytes on that page!
  * Making that page writable would unintentionally expose unrelated constants to write permissions.
  * **Design Requirement:** `mlk_zetas` must be isolated by both page alignment AND explicit padding of the full 16 KB structure (`mlk_isolated_zetas_page_t`), ensuring zero collateral constants share the page.
* **Linked Binary Verification Requirement:** We cannot assume `__DATA_CONST` is writable merely because of source attributes. The linked binary must be verified with `otool -l` to confirm `maxprot` permits write access (`0x03`), and verified at runtime with `vm_region_64`.

---

## 4. Distinction Between Four Research Artifacts

To prevent methodological conflation, this design strictly differentiates four entities:
```
+-----------------------------------------------------------------------------+
| 1. Original Baseline Implementation                                          |
|    - Upstream mlkem-native source (zetas.inc unchanged).                    |
|    - mlk_zetas resides in (__TEXT,__const).                                 |
|    - Used for production builds and NIST FIPS 203 KAT verification.         |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| 2. Modified Research Build                                                  |
|    - Compile-time macro guarded: MLKEM_RESEARCH_RELOCATE_ZETAS.             |
|    - mlk_zetas declared non-const in C and page-padded to full 16KB.         |
|    - Relocated to dedicated section (__DATA_CONST,__zetas_page).             |
|    - Protected read-only at runtime via OS virtual memory.                   |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| 3. Model-Table Prototype (Phase 11 Artifact)                                |
|    - Synthetic isolated table in proto.c + reader.c.                        |
|    - Proved vm_protect RW -> write -> read-back -> restore -> RO mechanics. |
|    - Did NOT run ML-KEM cryptographic decapsulation.                        |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| 4. Operational Persistent Storage Corruption (Proposed Phase 15 Pilot)      |
|    - Mutates actual relocated mlk_zetas in memory.                           |
|    - Executes full crypto_kem_dec (decapsulation + FO re-encryption).       |
|    - Restores mlk_zetas to golden values and verifies 100% clean baseline. |
+-----------------------------------------------------------------------------+
```

---

## 5. Minimal Research-Only Source & Build Intervention

### 5.1 Eliminating Undefined Behavior & Enforcing Page Isolation
In standard ISO C99 §6.7.3, modifying an object declared `const` via casting is undefined behavior. In the research build, the underlying table is declared **non-const** in C source and padded to 16 KB. Its read-only status is enforced by OS memory protection, completely eliminating undefined behavior.

```c
/* algorithms/source_ref/mlkem/src/zetas.inc */
#if defined(MLKEM_RESEARCH_RELOCATE_ZETAS)
/* Research-only persistent storage fault arm:
 * Explicit 16KB page-isolated, non-const storage structure */
typedef struct {
    int16_t zetas[128];
    uint8_t page_padding[16384 - (128 * sizeof(int16_t))];
} mlk_isolated_zetas_page_t;

#if defined(__APPLE__)
__attribute__((section("__DATA_CONST,__zetas_page"), aligned(16384)))
#else
__attribute__((section(".rodata.zetas_page"), aligned(4096)))
#endif
static mlk_isolated_zetas_page_t mlk_zetas_page = {
    .zetas = {
#else
static MLK_ALIGN const int16_t mlk_zetas[128] = {
#endif
    -1044, -758,  -359,  -1517, 1493,  1422,  287,   202, ...
};
#if defined(MLKEM_RESEARCH_RELOCATE_ZETAS)
#define mlk_zetas (mlk_zetas_page.zetas)
#endif
```

### 5.2 Controlled Accessor Interface in `poly.c`
```c
/* algorithms/source_ref/mlkem/src/poly.c */
#if defined(MLKEM_RESEARCH_RELOCATE_ZETAS)
/* Research-only accessor providing clean pointer for harness */
int16_t *mlkem_research_get_zetas_mutable_ptr(void) {
    return mlk_zetas_page.zetas;
}
const int16_t *mlkem_research_get_zetas_table(void) {
    return mlk_zetas_page.zetas;
}
#endif
```

### 5.3 Build Target Separation in `Makefile`
The production objects (`bin/obj/mlkem768.o` and `bin/obj/mlkem768_kat.o`) and the KAT runner (`bin/test_fips_kats`) **must never** compile with `-DMLKEM_RESEARCH_RELOCATE_ZETAS`.
A dedicated research object target is specified:
```makefile
$(OBJ_DIR)/mlkem768_persistent_reloc.o: algorithms/source_ref/mlkem/mlkem_native.c | $(OBJ_DIR)
	$(CC) -O3 -std=c99 -I algorithms/source_ref/mlkem \
	  -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem \
	  -DMLK_CONFIG_PARAMETER_SET=768 \
	  -DMLKEM_RESEARCH_RELOCATE_ZETAS \
	  -c $< -o $@
```

---

## 6. Seven Verification Guarantees & Stop Conditions

| # | Requirement | Verification Mechanism | Failure Condition | Stop Rule |
|---|---|---|---|---|
| 1 | **Table Bytes Changed** | Read-back of `target_addr` immediately post-write equals `golden ^ mask`. | Read-back equals golden or invalid value. | **Immediate ABORT:** Fault activation failure; do not execute SUT. |
| 2 | **Bytes Consumed by SUT** | Disassembly proves NTT loads from `_mlk_zetas`; output deviates predictably or triggers implicit rejection. | SUT output identical to golden despite corrupted active twiddle factor. | **Flag INVESTIGATE:** Possible compiler hoisting or unused index. |
| 3 | **Baseline Reproducible** | Trial 0 (unmodified) executes `crypto_kem_dec` and produces NIST KAT shared secret $K_{golden}$. | Trial 0 output $\neq K_{golden}$. | **Immediate ABORT:** Build corruption or environment instability. |
| 4 | **Table Restored Exactly** | In-place restore of `target_addr = golden`; SHA-256 hash of entire 256 bytes of `mlk_zetas` matches golden hash `303d1a...`. | Post-restore hash mismatch. | **Emergency STOP:** Backing store corrupted; halt all execution. |
| 5 | **Zero Trial Contamination** | Post-restore baseline decapsulation executed every trial; output must match $K_{golden}$. | Post-restore decapsulation output $\neq K_{golden}$. | **Emergency STOP:** State leakage between trials. |
| 6 | **Sham Control Validation** | Run trial with `mask = 0x0000` through full `vm_protect(RW) -> write -> vm_protect(RO)` lifecycle. | Output $\neq K_{golden}$ or crash. | **Immediate ABORT:** Memory permission toggle alone causes side effects. |
| 7 | **Production Invariance** | Production object `mlkem768.o` and KAT runner compiled without macro match original hashes; 100% KATs pass. | Binary hash differs or KAT fails. | **Hard NO-GO:** Upstream production baseline violated. |

---

## 7. Reviewer Assessment & Risk Analysis

1. **Risk of Compiler Optimization Invalidation:**  
   If the compiler treats data as immutable across repeated decapsulation calls, it could theoretically hoist reads out of loops or inline constants.  
   *Mitigation:* By defining `zetas` without `const` in the research build and performing writes via a separate TU, LLVM Clang cannot assume the values are compile-time constants. Disassembly inspection must verify explicit loads.
2. **Risk of Collateral Page Contamination:**  
   Apple Silicon 16 KB page size means modifying permissions affects 16,384 bytes.  
   *Mitigation:* The 16 KB padded structure `mlk_isolated_zetas_page_t` ensures `mlk_zetas` occupies the entire 16 KB page exclusively.
3. **Risk of Conflating Failure Modes:**  
   Conflating implicit rejection with recovery or SDC corrupts scientific conclusions.  
   *Mitigation:* Strict 9-column disaggregated trial ledger and formal endpoint contract segregation implemented in `EXPERIMENT_PROTOCOL.md`.
