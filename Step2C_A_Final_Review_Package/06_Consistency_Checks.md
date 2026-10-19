# Phase 2 Step 2C-A: Consistency Checks & Terminology Audit

## 1. Root vs Mirror Byte Identity Comparisons

The Phase 2 Step 2C-A documentation is maintained in dual locations: at the repository root and mirrored in `tfib_experiments/`. Byte-level comparisons using `cmp` were executed to verify complete synchronization.

### Exact Comparison Command
```bash
cmp phase2_step2c_dependency_model.md tfib_experiments/phase2_step2c_dependency_model.md && echo "dependency_model: IDENTICAL"
cmp phase2_step2c_experiment_design.md tfib_experiments/phase2_step2c_experiment_design.md && echo "experiment_design: IDENTICAL"
cmp phase2_step2c_report.md tfib_experiments/phase2_step2c_report.md && echo "report: IDENTICAL"
```

### Actual Output
```text
dependency_model: IDENTICAL
experiment_design: IDENTICAL
report: IDENTICAL
```
**Conclusion:** All three pairs of root and mirrored documentation files are 100% byte-identical.

---

## 2. Documentation Terminology Checks

### 2.1 Terminology: "FO Containment"
- **Search Query:** `grep -rn "FO containment" phase2_step2c* tfib_experiments/phase2_step2c*`
- **Result:**
  - `phase2_step2c_report.md:164`: Used in epistemological separation to describe the high-level boundary: *"Separation of Recovery vs Containment: Local recovery is solely a property of TFIB-REF with an uncorrupted reference table. Outer FO containment is a global property of the Fujisaki-Okamoto transform in ML-KEM. Preservation via decoding slack... is a distinct third outcome..."*
  - `tfib_experiments/phase2_step2c_report.md:164`: Identical line in mirror.
- **Finding:** Correctly scoped. The documentation distinguishes active FO re-encryption rejection from decoding-slack preservation.

### 2.2 Terminology: "100% Containment"
- **Search Query:** `grep -rn "100% containment" phase2_step2c* tfib_experiments/phase2_step2c*`
- **Result:** Zero matches found in the documentation files.
- **Finding:** No sweeping or overstated "100% containment" claims exist in the target documentation.

### 2.3 Terminology: "100% FO containment" Across Entire Repository
- **Search Query:** `grep -rn "100% FO containment" .`
- **Result:**
  - Matched in binary `tfib_experiments/test_step2c_countermeasure_independence`.
  - Matched in source file `tfib_experiments/test_step2c_countermeasure_independence.c:252`:
    ```c
    report("Test 7: Simultaneous common-mode fault confirms local checker blind spot (0% det) but 100% FO containment",
    ```
- **Finding & Discrepancy Note:** This string is a known **stale print label** in the test harness source code. Out of 150 locally blinded trials (50 simultaneous + 100 baseline), 147 were actively rejected by FO re-encryption, while 3 were preserved through decoding error-tolerance. In accordance with audit constraints, historical test code was not silently altered. The discrepancy is documented in `05_Test_Results.md`.

### 2.4 Terminology: "Common-Mode" Claims
- **Search Query:** `grep -rn "common-mode" phase2_step2c_dependency_model.md phase2_step2c_experiment_design.md phase2_step2c_report.md`
- **Audit Review:**
  1. `phase2_step2c_report.md:24`: *"Simultaneous Paired-Mutation Common-Mode Failure: When two sequential software mutations apply an identical bit-flip... local monitor detection is 0.0%... This result demonstrates checker blindness under the specific coordinated software mutations tested; it does not prove physical common-mode fault behavior, general hardware vulnerability, physical independence, or radiation tolerance."*
  2. `phase2_step2c_report.md:169`: Explicitly disclaims physical laser, clock glitch, or multi-register behavior.
  3. `phase2_step2c_dependency_model.md:103`: Table entry explicitly describes the locus as a paired software mutation and states: *"Coordinated software mutations evaluate checker blindness under tested inputs only and do not establish physical common-mode coupling, hardware vulnerability, or physical immunity."*
- **Finding:** All common-mode claims are rigorously qualified as software model proxies. No unverified physical or hardware coupling claims remain.

### 2.5 Terminology: "SDC Rate" & Statistical Bounds
- **Search Query:** `grep -rn "SDC rate" phase2_step2c_dependency_model.md phase2_step2c_experiment_design.md phase2_step2c_report.md`
- **Audit Review:**
  - `phase2_step2c_report.md:137`: Reports exact one-sided 95% binomial upper confidence bound $p_{\text{SDC}} \le 1 - 0.05^{1/750} \approx 0.399\%$.
  - Rule-of-three ($0.400\%$) and Wilson score ($0.490\%$) are explicitly identified by name and provided for comparative completeness.
  - Paired-mutation upper bound ($p_{\text{SDC}} \le 5.82\%$ on $N=50$) is consistently reported across `dependency_model.md`, `experiment_design.md`, and `report.md`.
- **Finding:** Consistent reporting of denominators ($N=750$ and $N=50$) and exact one-sided binomial upper bounds across all documents.

---

## 3. Potential Remaining Overstatements or Caveats

1. **Table Relocation (Step 2C-B) Separation:**
   - The documentation clearly notes that moving table symbols in memory (+448 bytes in Step 2C-A, or separate memory sections in Step 2C-B) establishes logical software separation only.
   - It explicitly notes that physical isolation (e.g., dual-port ROM, independent cache banks, physical shielding) is required for physical common-mode protection and is beyond the scope of software table relocation.
2. **Decoding Error-Tolerance vs FO Containment:**
   - The documentation accurately distinguishes between active cryptographic rejection by FO re-encryption and algorithmic noise absorption by centered binomial decoding. Both prevent SDC, but via different mechanisms.
