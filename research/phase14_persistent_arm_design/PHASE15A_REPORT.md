# Phase 15A — Authorized Isolated Research Build and Binary Verification Report (with Errata Corrections)

**Lead Reviewer:** Skeptical Cryptographic Implementation & Experimental Methodology Reviewer  
**Audit Target:** Relocated ML-KEM-768 Twiddle-Factor Table `mlk_zetas_page` (Research Build)  
**Execution Scope:** Isolated compilation and static binary verification only (**Zero fault injections, zero pilot trials executed**)  
**Date:** 2026-10-11  
**Deliverable Directory:** `research/phase14_persistent_arm_design/`

---

## 1. Executive Summary & Authorization Scope

Under Phase 15A, a strictly isolated, research-only build was authorized and implemented.
* **Scope Adherence:** All modifications were guarded behind the compile-time macro `MLKEM_RESEARCH_RELOCATE_ZETAS`. Zero changes were introduced to the production configuration or production build behavior.
* **Stop Conditions Respected:**
  * **Zero fault injections** were executed.
  * **Zero corrupted values** were written to memory.
  * **Zero runtime page protections** were altered in this phase.
  * The **16-trial pilot was NOT executed**.
  * All pre-existing tracked repository modifications (7/7) and historical datasets remain intact.

---

## 2. Compilation Environment and Artifact Hashes

### 2.1 Host Toolchain
* **Compiler:** Apple clang version 21.0.0 (`clang-2100.1.1.101`)
* **Target:** `arm64-apple-darwin27.0.0`
* **Static Linker:** `ld64` / Apple cctools via Command Line Tools
* **Host Kernel:** Darwin 27.0.0 Darwin Kernel Version 27.0.0 arm64 (Apple Silicon M1 / T8103)
* **Host Page Size:** Verified as `16,384` bytes (`0x4000`) via `pagesize`

### 2.2 SHA-256 Binary & Object Hashes
```text
c239e7cf355404af7eb616c58832a6f6b9fbb9c708f83df46c9e5d01264deb9f  bin/obj/mlkem768_persistent_reloc.o
01ae1714be2db8d593ddf7a993ebba48b3daffddc8baf6bc41bec65aa76ad8cf  bin/test_fips_kats_research
7dfd465ec186a857183b04647e09fe0acc9a28e6378b235cb8a77c9c6721c7ba  bin/obj/mlkem768_kat.o
8ca1c3e5bafe5ea4e83e68e26cfbf6df3c4b66644b746ead3e0b1b378d69e499  bin/test_fips_kats
```

---

## 3. Systematic Verification Gate Results & Errata Resolutions

### Gate A — Source and Build Isolation: **PASS**
* **Status:** **PASS**
* **Evidence [Static Analysis & Existing Evidence]:**
  1. The operational table relocation in `algorithms/source_ref/mlkem/src/zetas.inc:17-48` is completely isolated behind `#if defined(MLKEM_RESEARCH_RELOCATE_ZETAS)`. When the macro is undefined, the `#else` branch compiles the exact upstream code: `static MLK_ALIGN const int16_t mlk_zetas[128] = { ... };`.
  2. The accessor functions in `algorithms/source_ref/mlkem/src/poly.c:269-278` are guarded behind the same macro.
  3. `Makefile:64-71` specifies dedicated research targets (`bin/obj/mlkem768_persistent_reloc.o` and `bin/test_fips_kats_research`), leaving production targets (`mlkem768.o`, `mlkem768_kat.o`, `test_fips_kats`) unchanged.
  4. Building without the macro produces identical compilation paths.

---

### Gate B — Linked Binary Layout & Page Isolation
* **Status:**
  * **Static Section Allocation:** **PASS**
  * **Runtime Page Inspection (`vm_region_64`):** **NOT VERIFIED (Pending Pilot Execution)**
* **Evidence [Static Inspection of Linked Executable `bin/test_fips_kats_research`]:**
  1. **Segment & Protection Attributes (`otool -l`):**
     ```text
     segname __DATA_CONST
      vmaddr 0x0000000100098000
      vmsize 0x0000000000008000  (32,768 bytes = 2 pages)
     maxprot 0x00000003          (VM_PROT_READ | VM_PROT_WRITE)
    initprot 0x00000003
      nsects 3
       flags 0x10                (SG_READ_ONLY)
     ```
     `maxprot` is verified as `0x00000003`, confirming that Darwin XNU permits runtime unprotection to writable via `vm_protect`.
  2. **Section Placement Proof:**
     * **Page 1 (`0x100098000` to `0x10009c000`, 16 KB):**
       * Section `__got` at `0x100098000`, size `0x48`.
       * Section `__const` at `0x100098048`, size `0x120`.
     * **Page 2 (`0x10009c000` to `0x1000a0000`, 16 KB):**
       * Section `__zetas_page` starts at `0x000000010009c000`, size `0x0000000000004000` (16,384 bytes, exactly 1 page).
       * Symbol `_mlk_zetas_page` is at `0x000000010009c000`.
     * **Page 3 (`0x1000a0000` onwards):**
       * Next segment `__LINKEDIT` begins at `0x00000001000a0000`.
  3. **Errata Clarification on Page Isolation:**
     * Static section boundaries prove that `__zetas_page` accounts for 100% of the virtual section space allocated to Page 2 (`0x10009c000` to `0x1000a0000`).
     * Symbol listing `nm -m` shows `_mlk_zetas_page` as the sole symbol.
     * **Limitation:** Static headers define the planned memory layout, but do not prove runtime kernel page table states. Until the process executes and calls `vm_region_64`, live page isolation remains a static deduction, not a dynamic observation.

---

### Gate C — Compiler and Consumption Path
* **Status:**
  * **Static Memory Load Instructions (Indices 1..127):** **PASS**
  * **Static Memory Load for Index 0 ($\zeta_0$):** **N/A (Mathematically Unused by FIPS 203 ML-KEM NTT)**
  * **Dynamic Runtime Consumption under Mutation:** **NOT VERIFIED (Pending Pilot Execution)**
* **Evidence [Disassembly Inspection of `bin/obj/mlkem768_persistent_reloc.o`]:**
  1. **Pilot Trial 8 Target (Index 64, $\zeta_{64} = -1103$):**
     * Function: `_mlkem768_poly_mulcache_compute` (address `0x124b8`).
     * Address `0x124c8`: `adrp x8, page(_mlk_zetas_page + 0x80)` (`ARM64_RELOC_PAGE21 _mlk_zetas_page`, addend `0x80` = 128 bytes = index 64).
     * Address `0x124cc`: `add x8, x8, pageoff(_mlk_zetas_page + 0x80)` (`ARM64_RELOC_PAGEOFF12`).
     * Address `0x124f8`: `ldr q6, [x8]` loads 128-bit vector containing $\zeta_{64..\dots71}$ from memory.
     * Address `0x124fc`: `smull.4s v7, v6, v2` performs multiplication with coefficient vector.
     * **Twiddle factor $\zeta_{64}$ is dynamically loaded from memory, NOT folded into constants.**
  2. **Pilot Trials 11 & 12 Target (Index 127, $\zeta_{127} = 1628$):**
     * Function: `_mlkem768_poly_invntt_tomont` (address `0x9d3c`).
     * Address `0xa428`: `adrp x17, page(_mlk_zetas_page + 0xfe)` (addend `0xfe` = 254 bytes = index 127).
     * Address `0xa42c`: `add x17, x17, pageoff(_mlk_zetas_page + 0xfe)`.
     * Address `0xa430`: `ldrsh w1, [x17], #-0x2` loads $\zeta_{127}$ and decrements pointer backwards.
  3. **Pilot Trial 7 Target (Index 63, $\zeta_{63} = -1275$):**
     * Address `0xa5dc`: `adrp x9` + `add x9` targeting addend `0x7e` (index 63), followed by memory load.
  4. **Pilot Trials 3..5 Target (Index 1, $\zeta_1 = -758$):**
     * Address `0xabe8`: `adrp x9` + `add x9` targeting addend `0x02` (index 1), followed by `ldrsh w10, [x9, #0x1c]`.
  5. **Pilot Trial 1 Target (Index 0, $\zeta_0 = -1044$):**
     * In FIPS 203 ML-KEM, forward NTT iterates layers 1..7 ($k \in [1, 127]$); inverse NTT iterates backwards ($k \in [127, 1]$); basemul reads $k \in [64, 127]$.
     * **Index 0 is never accessed by any NTT butterfly routine.** This explains why faulting Index 0 is designed as a `BENIGN_MASKED` control trial.

---

### Gate D — Clean Cryptographic Baseline
* **Status:**
  * **6 NIST FIPS 203 & 204 Standardized KAT Vectors:** **PASS**
  * **1,000 Deterministic Test Vector Sweep:** **NOT TESTED (Pending Separate Test Harness)**
* **Evidence [Execution of `bin/test_fips_kats_research` vs `bin/test_fips_kats`]:**
  1. Executing `bin/test_fips_kats_research` ran the embedded NIST FIPS 203 & 204 test suite:
     * ML-KEM-512 (KeyGen, Encaps, Decaps): **PASS**
     * ML-KEM-768 (KeyGen, Encaps, Decaps): **PASS**
     * ML-KEM-1024 (KeyGen, Encaps, Decaps): **PASS**
     * ML-DSA-44 (Sign, Verify, Tamper-Reject): **PASS**
     * ML-DSA-65 (Sign, Verify, Tamper-Reject): **PASS**
     * ML-DSA-87 (Sign, Verify, Tamper-Reject): **PASS**
  2. All computed values matched expected standardized hex outputs bit-for-bit.
  3. Output of `bin/test_fips_kats_research` matched baseline `bin/test_fips_kats` bit-for-bit.
  4. **Errata Clarification:** Phase 14B proposed an extended 1,000-vector sweep. This sweep was not embedded in `test_fips_kats.c` and has not yet been run; only the 6 NIST KAT vectors were executed and verified.

---

### Gate E — Protection-Transition Readiness
* **Status:**
  * **Static Capability Verification:** **PASS**
  * **Runtime `vm_protect` Execution:** **NOT VERIFIED (Pending Pilot Execution)**
* **Evidence [Mach-O Load Commands and Memory Map]:**
  1. The Mach-O load command `LC_SEGMENT_64` for `__DATA_CONST` grants `maxprot = 0x03` (`VM_PROT_READ | VM_PROT_WRITE`).
  2. Page 2 (`0x10009c000` to `0x1000a0000`) is occupied exclusively by `__zetas_page` (16,384 bytes).
  3. In strict compliance with the Phase 15A stop conditions, zero `vm_protect` calls were invoked, zero table values were mutated, and no faults were injected.

---

## 4. Artifact & Build Discrepancy Reconciliation

* **Observation:** Recompiling `bin/obj/mlkem768_kat.o` without `-DMLKEM_RESEARCH_RELOCATE_ZETAS` produced an object of identical size (129,760 bytes), with identical symbols (`_mlk_zetas` at `0x190c0`), but byte differences in `_mlkem768_dec_monitored`.
* **Root Cause Diagnosis:**
  1. `bin/obj/mlkem768_kat.o` was compiled on Oct 1 under Darwin 26.5 SDK (`LC_BUILD_VERSION minos 26.5 sdk 26.5`).
  2. The current host environment has been upgraded to Darwin 27.0.0 (`Apple clang version 21.0.0`).
  3. Disassembly diffing confirms that the difference is strictly an instruction reordering of two independent bitwise instructions inside `mlk_kem_dec_monitored` (Phase 7i monitoring logic).
  4. All cryptographic NTT butterfly loops, basemul routines, and polynomial arithmetic in `poly.c` are structurally identical.

---

## 5. Final Errata Scorecard

| Gate / Claim | Scope | Evaluation Method | Status |
|:---:|:---|:---|:---:|
| **Gate A** | Source & Build Isolation | Macro isolation verified; production targets intact | **PASS** |
| **Gate B (Static)** | Section Placement | Segment `maxprot = 0x03`; `__zetas_page` size 16KB | **PASS** |
| **Gate B (Runtime)** | Live VM Region Inspection | In-process `vm_region_64` memory query | **NOT VERIFIED** |
| **Gate C (Static)** | Table Memory Loads | Disassembly confirms `adrp` + `ldr` for indices 1..127 | **PASS** |
| **Gate C (Index 0)**| Memory Load for $\zeta_0$ | Index 0 unused by ML-KEM NTT arithmetic | **PASS (N/A)** |
| **Gate C (Dynamic)**| Dynamic Mutation Consumption| Runtime error propagation into FO rejection | **NOT VERIFIED** |
| **Gate D (KATs)** | NIST Standardized KAT Suite | 6 NIST FIPS 203 & 204 test vectors | **PASS** |
| **Gate D (1000-vec)**| Extended Sweep | 1,000 pseudo-random vector comparison | **NOT TESTED** |
| **Gate E (Static)** | Protection Capability | Segment `maxprot == 0x03` | **PASS** |
| **Gate E (Runtime)**| Dynamic Toggling | `vm_protect(RW) -> write -> vm_protect(RO)` | **NOT VERIFIED** |

---

## 6. Final Recommendation

**READY FOR SEPARATE PILOT APPROVAL**

All static build, binary layout, instruction scheduling, and standardized KAT baseline requirements have passed. The discrepancies identified in the Phase 15A report have been fully reconciled with concrete artifact evidence.

The unverified items (runtime `vm_region_64` query, dynamic mutation consumption, and runtime `vm_protect` toggling) are precisely the experimental actions that require pilot execution. They are correctly gated behind Phase 15B approval.
