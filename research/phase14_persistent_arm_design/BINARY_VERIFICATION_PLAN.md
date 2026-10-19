# Phase 14 — Persistent-Storage Fault Arm: Binary Verification Plan

**Author:** Skeptical Cryptographic Implementation & Experimental Methodology Reviewer  
**Target:** Binary Object `mlkem768_persistent_reloc.o` and Final Linked Research Executable vs Baseline  
**Host Architecture:** macOS arm64 (Darwin Mach-O 64-bit, 16 KB Page Size)  
**Toolchain:** Apple Clang 17+ (`/usr/bin/clang`, `xcrun llvm-objdump`, `nm`, `otool`)

---

## 1. Objectives & Inspection Protocol

Binary inspection must prove five non-negotiable properties prior to executing any persistent-storage fault experiment:
1. **Section & Linked Segment Relocation:** The operational table is placed in a custom section (`__DATA_CONST,__zetas_page`), and the linked Mach-O binary grants `maxprot >= VM_PROT_WRITE` (`0x03`).
2. **Page Granularity & Isolation:** The table structure occupies an entire 16 KB page (`16,384` bytes) with zero co-located program constants.
3. **Absence of Constant Folding & Codegen Parity:** Compiler optimization passes (`-O3`) generate explicit memory loads (`ldrsh`, `ldr q`) identical in structure to the baseline build, differing only in PC-relative page displacement.
4. **Linkage & Export Verification:** The table pointer is exposed through the controlled accessor function without polluting the public production ABI.
5. **Zero Impact on Production Build:** Building without `-DMLKEM_RESEARCH_RELOCATE_ZETAS` produces object code byte-for-byte identical to the upstream baseline.

---

## 2. Compilation and Build Commands

### 2.1 Baseline Production Build (Unchanged Upstream)
```bash
clang -O3 -std=c99 \
  -I algorithms/source_ref/mlkem \
  -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem \
  -DMLK_CONFIG_PARAMETER_SET=768 \
  -c algorithms/source_ref/mlkem/mlkem_native.c \
  -o bin/obj/mlkem768.o
```

### 2.2 Relocated Research Build (Subject of Verification)
```bash
clang -O3 -std=c99 \
  -I algorithms/source_ref/mlkem \
  -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem \
  -DMLK_CONFIG_PARAMETER_SET=768 \
  -DMLKEM_RESEARCH_RELOCATE_ZETAS \
  -c algorithms/source_ref/mlkem/mlkem_native.c \
  -o bin/obj/mlkem768_persistent_reloc.o
```

---

## 3. Step-by-Step Binary Verification Commands & Acceptance Criteria

### Check 1: Symbol Table and Section Placement (Intermediate Object)
* **Command:**
  ```bash
  nm -m bin/obj/mlkem768_persistent_reloc.o | grep "zetas"
  ```
* **Expected Output:**
  ```text
  0000000000000000 (__DATA_CONST,__zetas_page) non-external _mlk_zetas_page
  ```
* **Comparison with Baseline:**
  Baseline `bin/obj/mlkem768.o` outputs:
  ```text
  00000000000190c0 (__TEXT,__const) non-external _mlk_zetas
  ```
* **Acceptance Criterion:** The symbol **must** transition out of `(__TEXT,__const)`. If the symbol remains in `__TEXT`, **HALT (SIGBUS risk)**.

---

### Check 2: Linked Executable Segment & Max Protection Inspection
* **Command:**
  ```bash
  otool -l <linked_research_executable> | grep -A 8 "segname __DATA_CONST"
  ```
* **Expected Attributes:**
  * `segname`: `__DATA_CONST`
  * `initprot`: `r--` (`0x01`)
  * `maxprot`: `rw-` (`0x03`) or `rwx` (`0x07`)
* **Acceptance Criterion:** `maxprot` **must** allow write access. If `maxprot == 0x01`, `vm_protect(RW)` is impossible under Darwin XNU $\rightarrow$ **HARD NO-GO**.

---

### Check 3: Page Isolation & Co-Location Audit
Verify that no other symbols share the 16 KB page:
* **Command:**
  ```bash
  PAGE_ADDR=$(nm -n <linked_research_executable> | grep "_mlk_zetas_page" | awk '{print $1}')
  nm -n <linked_research_executable> | awk -v start="0x$PAGE_ADDR" '
    BEGIN { end = strtonum(start) + 16384 }
    strtonum("0x"$1) >= strtonum(start) && strtonum("0x"$1) < end { print }
  '
  ```
* **Acceptance Criterion:** The only symbol printed must be `_mlk_zetas_page`. If ANY other symbol falls in that 16 KB range, unrelated data is exposed $\rightarrow$ **HARD NO-GO**.

---

### Check 4: Disassembly & Codegen Parity Comparison
Compare the disassembled instruction sequences between baseline and research objects:
* **Command:**
  ```bash
  xcrun llvm-objdump -d --no-show-raw-insn bin/obj/mlkem768.o > /tmp/base_disasm.s
  xcrun llvm-objdump -d --no-show-raw-insn bin/obj/mlkem768_persistent_reloc.o > /tmp/reloc_disasm.s
  diff -u /tmp/base_disasm.s /tmp/reloc_disasm.s
  ```
* **Acceptance Criterion:**
  * Permitted differences: Page displacement offsets in `adrp` and symbol relocation names.
  * Forbidden differences: Changes in vector instruction selection, loop bounds, instruction counts, register spills, or failure to inline functions. Any forbidden difference $\rightarrow$ **HARD NO-GO**.

---

### Check 5: Accessor Interface Verification
* **Command:**
  ```bash
  nm -m bin/obj/mlkem768_persistent_reloc.o | grep "mlkem_research_get_zetas"
  ```
* **Expected Output:**
  ```text
  00000000000... (__TEXT,__text) external _mlkem_research_get_zetas_mutable_ptr
  00000000000... (__TEXT,__text) external _mlkem_research_get_zetas_table
  ```
* **Acceptance Criterion:** Accessors must exist as external text symbols returning the relocated table address.

---

### Check 6: Production Invariance Regression Check
Compile clean baseline without macro and compare SHA-256 against existing tracked object:
* **Command:**
  ```bash
  clang -O3 -std=c99 -I algorithms/source_ref/mlkem \
    -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem -DMLK_CONFIG_PARAMETER_SET=768 \
    -c algorithms/source_ref/mlkem/mlkem_native.c -o /tmp/mlkem768_check.o
  
  cmp bin/obj/mlkem768.o /tmp/mlkem768_check.o
  ```
* **Acceptance Criterion:** `cmp` returns code `0` (zero byte differences). Uninstrumented production builds remain 100% bit-for-bit invariant.

---

## 4. In-Process Runtime VM Protection Verification

Before launching any fault campaign, a standalone harness test must verify Mach VM behavior on the relocated table:
```c
/* Pseudocode Runtime Sanity Check */
kern_return_t kr;
mach_port_t task = mach_task_self();
uintptr_t table_addr = (uintptr_t)mlkem_research_get_zetas_mutable_ptr();
vm_address_t page_addr = table_addr & ~(0x4000 - 1);

/* Step 1: Query initial protection and maxprot */
vm_region_basic_info_data_64_t info;
mach_msg_type_number_t count = VM_REGION_BASIC_INFO_COUNT_64;
mach_port_t object_name;
vm_size_t size;
kr = vm_region_64(task, &page_addr, &size, VM_REGION_BASIC_INFO_64, (vm_region_info_t)&info, &count, &object_name);
assert(kr == KERN_SUCCESS);
assert(info.protection == VM_PROT_READ);
assert((info.max_protection & VM_PROT_WRITE) != 0);

/* Step 2: Test unprotection to RW */
kr = vm_protect(task, page_addr, 0x4000, FALSE, VM_PROT_READ | VM_PROT_WRITE);
if (kr != KERN_SUCCESS) {
    fprintf(stderr, "ABORT: vm_protect(RW) failed with code %d\n", kr);
    exit(1);
}

/* Step 3: Test safe write */
volatile int16_t *ptr = (volatile int16_t *)table_addr;
int16_t orig = ptr[0];
ptr[0] = orig ^ 0x0001;
assert(ptr[0] == (orig ^ 0x0001));
ptr[0] = orig; /* Restore */

/* Step 4: Re-protect to RO */
kr = vm_protect(task, page_addr, 0x4000, FALSE, VM_PROT_READ);
assert(kr == KERN_SUCCESS);
```
* **Acceptance Criterion:** The runtime sequence must complete with exit code 0 and zero signals. Any `SIGBUS` or `KERN_PROTECTION_FAILURE` indicates an immediate **HARD NO-GO**.
