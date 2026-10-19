# Phase 14 — Persistent-Storage Arm: Design Review and Approval Gate Report

**Date:** 2026-10-11  
**Lead Reviewer:** Skeptical Cryptographic Implementation & Experimental Methodology Reviewer  
**Deliverable Directory:** `research/phase14_persistent_arm_design/`  
**Verdict:** **CONDITIONAL GO** (Design & Feasibility Validated; Implementation Blocked Pending Approval)

---

## 1. Formal Review Recommendation

The design for a research-only persistent-storage fault experiment targeting the operational ML-KEM-768 twiddle-factor table `mlk_zetas` is rated **CONDITIONAL GO**.

### Conditions for the Verdict:
1. **Feasibility Established:** Binary disassembly confirms that compiled NTT and basemul routines load `mlk_zetas` dynamically from memory addresses at runtime (via `adrp` + `ldr` instructions), rather than folding constants into instructions. Dynamic software injection into a relocated `__DATA_CONST` section is feasible without OS crashes (`SIGBUS`), provided linked segment protection (`maxprot`) and page-sized isolation padding are verified.
2. **Implementation Strictly Gated:** **NO code changes have been made to the cryptographic source, SUT, or build system in this phase.** All pre-existing tracked modifications and baseline datasets remain untouched.
3. **Execution Blocked:** Execution of the pilot or full campaign requires separate, explicit approval of the proposed source diff and build rules.
4. **Epistemological Guardrail:** Any future successful results establish exclusively a **software-level memory fault result on a modified research build**. They do not establish physical radiation resilience, SEU susceptibility, or flight qualification.

---

## 2. Preservation Ledger

### 2.1 Git Repository State
* **Branch:** `space-resilience-framework`
* **HEAD Commit:** `4a2c4ebf9274a9188db3610a4f8448902caed056`
* **Status:** Clean review state; zero staged files, zero commits created, zero unstaged changes discarded.

### 2.2 Preservation of the Seven Pre-Existing Tracked Modifications
All seven tracked files previously modified in the workspace were preserved intact:
```text
a3009b5de498ef1855855c4d1767091b80c55b39e1195a1e750b709ad905b614  README.md
a4e253de8165a4f092f0fa93e507ed7b2f4ed3a7b6cac34e951d402f45809ece  experiments/fault_injection/mlkem768_internal_fault_experiment.c
052b7d1637bd457b202af77d9672ec6c05e5c9ffdd09d62b8dfd298fc3404cfd  experiments/system_model/spacecraft_protocol_sim.py
353c280b3d56dc95fc059ead6ab34921c6680de57098e9d3a7b85a5c6e440fd7  fault_injection/fault_models/fault_definitions.py
83323c5733fa88b88fda4afdd5c720d42c14313bff159a87a9cd800b5330b5bd  results/phase7i/processed/phase7i_e2e_results.json
90b34d69cdd4f10e53e9fc8742179e4a6f50449f53379f28fc73a63a42e93433  results/spacecraft_protocol_desync_results.json
b83118c8c8583b8a67565e3fbe643b97c16c5b25a0cae31882347ed3ca4b836a  tests/test_fips_kats.c
```

### 2.3 SHA-256 Checksums of Baseline Artifacts
```text
755356d937d4b8c7d54e39c34a64ac9ee867be01293dd44f5f53c89ef7f2616c  research/manuscript_v1/MANUSCRIPT_v2.md
303d1abccc4757d49a5c8df5f88080fefef617b7360056db5311bd94354096d4  algorithms/source_ref/mlkem/src/zetas.inc
98c33bcbc5c0a7eeded5722e9f4c8678c58477dd13ae2f097aaf44d25a124afb  algorithms/source_ref/mlkem/mlkem_native.c
f06aa12296c3334cd12bc541a5dc5dcb3b22d9e1844653a5c12d8b7014fec304  algorithms/source_ref/mlkem/src/poly.c
896df5536d1ec6d540220d99fbfaae345adb9b1bc96f0af601276f2efd8dfc26  algorithms/source_ref/mlkem/src/kem.c
deec4767a465d71656862d55c26a45775e9bf4328e0837c3cb2e23b6a06ea0ec  algorithms/source_ref/mlkem/src/indcpa.c
624893f5120af442abd9bac3814bac699fbc77cf45667e884ae4959efc60c329  algorithms/source_ref/mlkem_fault_hooks.c
81af23d3b82cef165978fd37452fb0c7dd1ee167a842c8f6e94e64da701558c3  experiments/mlkem/mlkem_campaign_runner.c
fe3bbb6c1867914b9231e1e2464a6c4d8801d8191f48854f745e61fcd2a8791c  tfib_experiments/tfib_experiment_runner.c
f56956f097b4bdcb9230d1519c1eb575735330c18ce8a3875579331a1625d3bc  tfib_implementation/tfib_hooks.c
e087922abe945dc2b9261e8307ff6be022ecf258f215d728e0d0de4b40208421  tfib_raw_results.csv
cff3514984a2042c2de3dbd53202abc8835faf9ebe3788eea494ce878c8a44f1  tfib_trial_level_results.csv
f16833ff7a2bc131e3b3be97ae342d19fa13a01ea9e4f1d6eabeef3e720cf913  tfib_reproduced_results.csv
72f4de19de678f9a7665411786952981b0e33ebcf1211128db3d72c20bb6ee1d  research/phase11_persistent_feasibility/RESULTS.csv
8310975de5e8131ddbc81fa44fc5fe2ee135581d7a803b114cedd671063fbf45  research/EVIDENCE_LEDGER.md
bf53809037241da2c8082410cf65e13737e27f7558c867a3954c530925953d2d  paper/authoritative_results.csv
0bc1203e17ff23c88c9076763a71563819eb284489cf163abd4e6099e709c8b5  paper/claim_evidence_matrix.csv
```

---

## 3. Resolution of Phase 14B Review Blockers

All seven design blockers raised in Phase 14B have been resolved and documented in `PHASE14B_REVIEW.md`:
1. **Mach-O Layout & Segment Perms:** Distinction between section attributes and linked segment `maxprot` established; static (`otool -l`) and runtime (`vm_region_64`) verification mandated.
2. **Page Isolation:** Host page size verified as 16,384 bytes (`pagesize`); explicit 16 KB padded struct `mlk_isolated_zetas_page_t` enforced to prevent collateral constant co-location.
3. **Compiler Semantics & UB:** Storage declared non-const in C research build; read-only protection enforced via OS memory mapping, eliminating ISO C undefined behavior.
4. **Baseline Equivalence:** Multi-stage equivalence criteria established (NIST KATs, 1,000 deterministic inputs, disassembly instruction schedule diffing).
5. **Trial Ledger & Contract:** Disaggregated 9-column ledger schema implemented; explicit FIPS 203 endpoint contract separating SDC from valid implicit rejection and recovery.
6. **Pilot Scope:** 16-trial pilot formally justified as an engineering feasibility and protocol hygiene test, not a statistical distribution estimate.
7. **Approval Boundary:** Clear separation established between verified existing baseline facts and unbuilt research build hypotheses.

---

## 4. Phase 14 Deliverables Index

All Phase 14/14B deliverables reside in `research/phase14_persistent_arm_design/`:
1. `PHASE14B_REVIEW.md` — Complete skeptical resolution of all 7 design blockers.
2. `PHASE14B_CHANGELOG.md` — Detailed log of updates across all Phase 14 documents.
3. `DESIGN_REVIEW.md` — Core architectural analysis, platform constraints, root cause of SIGBUS, 7 verification guarantees.
4. `BINARY_VERIFICATION_PLAN.md` — Compilation flags, linked segment inspections, page isolation audit, disassembly validation commands.
5. `EXPERIMENT_PROTOCOL.md` — 16-trial pilot matrix, 14-step transactional trial lifecycle, 9-column disaggregated schema, FIPS 203 endpoint contract.
6. `GO_NO_GO_CRITERIA.md` — 4-gate evaluation system, quantitative thresholds, automatic kill-switch conditions.
7. `CLAIM_BOUNDARIES.md` — Demarcation matrix between software fault injection and physical radiation physics, mandatory paper guardrails.
8. `PHASE14_REPORT.md` — Executive summary, preservation hashes, unresolved questions, formal approval request.

---

## 5. Formal Approval Request

Implementation of the persistent-storage arm requires explicit approval for the following discrete changes:

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

**Action Required from User:** Review the Phase 14B design resolution and issue explicit approval before any code modifications or builds are initiated.
