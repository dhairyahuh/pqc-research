# Phase 15A Changelog: Isolated Research Build and Static Binary Verification

**Date:** 2026-10-11  
**Author:** Skeptical Cryptographic Implementation & Experimental Methodology Reviewer  
**Context:** Phase 15A Authorized Isolated Implementation & Verification Only  

---

## 1. Summary of Changes
This changelog records all source, build, and verification modifications authorized under Phase 15A.

* **Production Code Invariant:** The production build configuration and production binaries remain completely unaffected. All additions are compile-time isolated behind `#if defined(MLKEM_RESEARCH_RELOCATE_ZETAS)`.
* **Working-Tree Preservation:** All 7 pre-existing tracked modifications and historical baseline results remain preserved.
* **Stop Conditions Respected:** No fault injection was performed, no corrupted values were written, no page protections were toggled, and the 16-trial pilot was NOT executed.

---

## 2. Modified Repository Files

### 1. `algorithms/source_ref/mlkem/src/zetas.inc`
* Added compile-time guarded struct `mlk_isolated_zetas_page_t` under `#if defined(MLKEM_RESEARCH_RELOCATE_ZETAS)`.
* The struct contains:
  * `int16_t zetas[128]` (256 bytes of non-const twiddle factors).
  * `uint8_t page_padding[16384 - 256]` (16,128 bytes of page-isolation padding).
* Decorated with `__attribute__((section("__DATA_CONST,__zetas_page"), aligned(16384)))`.
* Added macro `#define mlk_zetas (mlk_zetas_page.zetas)`.
* Preserved upstream `static MLK_ALIGN const int16_t mlk_zetas[128]` under `#else`.

### 2. `algorithms/source_ref/mlkem/src/poly.c`
* Added compile-time guarded accessor functions under `#if defined(MLKEM_RESEARCH_RELOCATE_ZETAS)`:
  * `int16_t *mlkem_research_get_zetas_mutable_ptr(void)`: returns `mlk_zetas_page.zetas`.
  * `const int16_t *mlkem_research_get_zetas_table(void)`: returns `mlk_zetas_page.zetas`.

### 3. `Makefile`
* Added research build object rule:
  ```makefile
  $(OBJ_DIR)/mlkem768_persistent_reloc.o: algorithms/source_ref/mlkem/mlkem_native.c | $(OBJ_DIR)
  	$(CC) -O3 -std=c99 -I algorithms/source_ref/mlkem -DMLK_CONFIG_NAMESPACE_PREFIX=mlkem768 -DMLK_CONFIG_PARAMETER_SET=768 -DMLKEM_RESEARCH_RELOCATE_ZETAS -c $< -o $@
  ```
* Added research verification binary rule:
  ```makefile
  $(BIN_DIR)/test_fips_kats_research: tests/test_fips_kats.c tests/kat_mlkem512.c tests/kat_mlkem768.c tests/kat_mlkem1024.c tests/kat_mldsa44.c tests/kat_mldsa65.c tests/kat_mldsa87.c $(OBJ_DIR)/mlkem512.o $(OBJ_DIR)/mlkem768_persistent_reloc.o $(OBJ_DIR)/mlkem1024.o $(OBJ_DIR)/mldsa44.o $(OBJ_DIR)/mldsa65_kat.o $(OBJ_DIR)/mldsa87.o | $(BIN_DIR)
  	$(CC) $(CFLAGS) -I . -I algorithms/source_ref/mlkem -I algorithms/source_ref/mldsa $^ -o $@
  ```

---

## 3. Newly Created Verification Deliverables

### 1. `research/phase14_persistent_arm_design/PHASE15A_REPORT.md`
* Complete report documenting Gate A through Gate E evaluations, compiler information, linked binary addresses, section layout, and the formal recommendation.

### 2. `research/phase14_persistent_arm_design/PHASE15A_CHANGELOG.md`
* This changelog document.
