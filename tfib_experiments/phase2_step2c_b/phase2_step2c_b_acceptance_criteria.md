# Phase 2 Step 2C-B: Acceptance Criteria & Scientific Decision Framework

**Document:** `phase2_step2c_b_acceptance_criteria.md`  
**Phase:** Phase 2 Step 2C-B (Experimental Design — Revision 3)  
**Status:** Methodological Design Specification Only (No Implementation or Execution)  
**Date:** 2026-10-04  
**Target:** ML-KEM-768 with Two-Factor Invariant Butterfly (TFIB)  

---

## 1. Five-Category Acceptance Framework

To ensure that experimental progression is strictly gated by verifiable evidence rather than assumptions, Step 2C-B defines objective criteria across five formal categories:

```
+---------------------------------------------------------------------------------------------------------+
|                                    STEP 2C-B ACCEPTANCE FRAMEWORK                                       |
+--------------------------+----------------------------------------------------+-------------------------+
| Category                 | Focus Area                                         | Verification Artifact   |
+--------------------------+----------------------------------------------------+-------------------------+
| 1. Design-Completeness   | Mathematical rigor, causal isolation, power rules | Design review approval  |
| 2. Build & Preflight     | Linker sections, page alignment, symbol accessors  | Preflight log & nm map  |
| 3. Experimental Validity | KAT correctness, clean runs, fault exposure parity | Calibration run CSVs    |
| 4. Statistical Reporting | McNemar testing, CIs, power reporting, discordance | Authoritative test CSV  |
| 5. Research-Claim Bounds | Prohibiting physical, radiation, and space claims  | Final manuscript audit  |
+--------------------------+----------------------------------------------------+-------------------------+
```

---

## 2. Objective Acceptance Criteria by Category

### Category 1: Design-Completeness Criteria (Gated Prior to Implementation)
- [ ] **D-1 (Causal Isolation):** The primary comparison strictly isolates table placement across Variants A, B, and C with identical monitoring algorithms, PRF seeds, and operational-table-relative fault blast definitions.
- [ ] **D-2 (Mathematical Fault Model):** The spatial disturbance interval is formally defined as a half-open virtual address range $I = [A_{\text{start}}, A_{\text{end}})$ with deterministic PRF-seeded XOR masks and explicit memory protection protocols.
- [ ] **D-3 (Static Symbol Resolution):** Symbol resolution mechanism does not assume `dlsym` can locate internal static symbols; uses link-time accessor functions.
- [ ] **D-4 (Pilot-Contingent Power):** Statistical sample size adequacy is explicitly conditioned on empirical pilot discordance rates rather than arbitrary a priori power assertions.

### Category 2: Build & Preflight Criteria (Gated Prior to Experiment Execution)
- [ ] **B-1 (Symbol Separation, C-1):** `nm -m` proves $\text{Addr}(\_mlk\_zetas) \neq \text{Addr}(\_tfib\_zetas\_ref)$ (fails closed if linker folding occurs).
- [ ] **B-2 (Section Assignment, C-2):** Object inspection (`otool -l` or `llvm-objdump -h`) proves `_tfib_zetas_ref` is in `__DATA_CONST,__tfib_ref` for Variants B & C and `__TEXT,__const` for Variant A.
- [ ] **B-3 (Page Alignment, C-3):** Address arithmetic proves $\text{Addr}(\_tfib\_zetas\_ref) \equiv 0 \pmod{16384}$ and $|\text{Addr}(\text{ref}) - \text{Addr}(\text{op})| \ge 16,384$ for Variant C.
- [ ] **B-4 (Table Size Integrity, C-4):** Both tables allocate exactly 256 bytes in binary headers.
- [ ] **B-5 (Disassembly Disjointness, C-5):** Disassembly of `mlk_ntt_layer` and `tfib_inv_butterfly_check` shows disjoint constant memory references.
- [ ] **B-6 (Anchor Resolution, C-6):** In-process link-time accessor function returns a valid mapped virtual address for $A_{\text{op}}$ matching binary inspection.

### Category 3: Experimental Validity Criteria (Gated During Execution)
- [ ] **V-1 (Clean KAT Conformance):** All variants achieve 100% test vector match against NIST FIPS 203 KATs ($N=100$ clean trials per variant, zero false alarms).
- [ ] **V-2 (Single-Point Positive Controls):** 100% fault detection ($N=50/50$) under single-locus twiddle perturbations in all monitored variants.
- [ ] **V-3 (Fault Exposure Equivalence):** Harness logs verify that the operational table `_mlk_zetas` receives identical byte mutations across Variants A, B, and C for matching trial seeds.
- [ ] **V-4 (Infrastructure Fault Rate $\le 1.0\%$):** Operating system permission traps (`SIGSEGV` or `vm_protect` errors) occur in $\le 1.0\%$ of total trials; otherwise campaign halts.
- [ ] **V-5 (Deterministic Reproducibility):** Two independent campaign executions with identical PRF seed generate byte-identical CSV logs.

### Category 4: Statistical Reporting Criteria (Gated for Results Publication)
- [ ] **S-1 (Paired Unit Accounting):** Primary analysis utilizes exact pairing on trial seed index $j$ across Variants A, B, and C.
- [ ] **S-2 (Appropriate Test Selection):** Uses exact conditional binomial test when $n_{\text{disc}} < 25$ and continuity-corrected McNemar when $n_{\text{disc}} \ge 25$.
- [ ] **S-3 (FWER Multi-Comparison Control):** Enforces Holm–Bonferroni step-down adjustment ($\alpha_1 = 0.005, \alpha_2 = 0.01$).
- [ ] **S-4 (Explicit Reporting of CIs & Trial Breakdown):** Reports Agresti–Min 99% CIs, exact trial counts for effective, ineffective padding, and infrastructure abort cases.

### Category 5: Research-Claim Restrictions (Strict Disclaimers)
- [ ] **R-1 (No Physical Isolation Claims):** No claims that linker sections or virtual pages provide silicon-level or physical hardware separation.
- [ ] **R-2 (No Radiation Hardness Claims):** No claims of SEU, SEL, or radiation resilience based on software layout experiments.
- [ ] **R-3 (No Real-Time Flight Qualification Claims):** The $\le 5.0\%$ latency threshold is labeled strictly as a project-defined software engineering constraint, not a spacecraft avionics timing qualification.

---

## 3. Scientific Decision Matrix: Unbiased Outcome Interpretation

A scientifically valid experiment must permit the hypothesis to be rejected. Step 2C-B pre-registers five explicit outcome scenarios:

```
+---------------------------------------------------------------------------------------------------------+
|                                    SCIENTIFIC DECISION MATRIX                                           |
+--------------------------+------------------------------+--------------------+--------------------------+
| Outcome Category         | Measured Empirical Evidence  | Statistical Rule   | Authoritative Conclusion |
+--------------------------+------------------------------+--------------------+--------------------------+
| Outcome 1:               | Delta_p >= 10.0%;            | McNemar p < 0.005  | H1 Supported. Section    |
| Confirmed Layout Benefit | Var C recovery > Var A;      | (Holm-Bonferroni   | isolation prevents dual- |
|                          | Overrun protected; OH <= 5%  | adjusted)          | table spatial corruption.|
+--------------------------+------------------------------+--------------------+--------------------------+
| Outcome 2:               | Delta_p < 5.0%;              | McNemar p >= 0.01; | H0 Supported (Valid      |
| High-Value Null Result   | Var A, B, C detection/recov  | equivalence bounds | Negative Result). Layout |
|                          | identical within 99% CI      | [-0.05, 0.05]      | is orthogonal to faults. |
+--------------------------+------------------------------+--------------------+--------------------------+
| Outcome 3:               | Benefit observed ONLY for    | p < 0.005 on       | Bounded Benefit. Spatial |
| Narrow Spatial Benefit   | specific blast length L;     | spatial blasts;    | isolation works only for |
|                          | identical on all other models| p >= 0.01 on rest  | contiguous blasts.       |
+--------------------------+------------------------------+--------------------+--------------------------+
| Outcome 4:               | Local detection improves     | p < 0.005 local;   | Redundant Local Benefit. |
| Redundant Local Benefit  | (Var C > Var A), but end-to- | p >= 0.01 on SDC   | FO re-encryption already |
|                          | end SDC rate is 0% in both   | (both 0 SDCs)      | provides containment.    |
+--------------------------+------------------------------+--------------------+--------------------------+
| Outcome 5:               | Incremental latency > 5.0%   | Latency delta      | Engineering Invalidation.|
| Unacceptable Overhead    | or binary text expands >10%  | p < 0.001          | Security benefit negated |
|                          |                              |                    | by latency regression.   |
+--------------------------+------------------------------+--------------------+--------------------------+
```

### Nuanced Interpretation Guidance:
- **Outcome 2 is a Success, Not a Failure:** Demonstrating that software section placement provides no protection against spatial faults is an authoritative, high-value scientific finding that prevents embedded practitioners from deploying ineffective linker tricks.
- **Outcome 4 Demands Nuance:** If Variant C prevents local checker blindness, but both Variant A and Variant C achieve 0 SDC due to outer FO re-encryption (147/150 rejections, 3/150 decoding slack), the result must be reported as a **defense-in-depth availability improvement for local recovery, not an improvement in end-to-end secrecy**.

---

## 4. Mandatory Halt & Abort Conditions

The experimental pipeline must immediately abort (fail closed) upon encountering any of the following:
1. **Injector Asymmetry:** Operational table mutations differ between variants for the same trial seed.
2. **Preflight Check Failure:** Any of B-1 through B-6 fails.
3. **Infrastructure Fault Spikes:** OS memory protection traps or segmentation faults exceed 1.0% of trials.
4. **KAT Regression:** Any clean trial produces an incorrect shared secret or false alarm.
