# Phase 2 Step 2C-A: Test Suite Execution Results & Label Audit

## 1. Overview of Verification Test Suites

Three comprehensive automated test scripts validate the cryptographic integrity, mutation sensitivity, and countermeasure independence of the implementation:
1. `run_step2b_tests.sh`: Deterministic PRF, domain separation, and independent oracle validation.
2. `run_step2b_mutation_checks.sh`: Rigorous adversarial mutation checks verifying test harness sensitivity.
3. `run_step2c_tests.sh`: Countermeasure independence, checker degradation, paired software mutations, and full 900-trial campaign execution.

---

## 2. Test Execution Commands and Full Outputs

### 2.1 Step 2B Validation Tests
**Command:**
```bash
./tfib_experiments/run_step2b_tests.sh
```

**Console Output:**
```text
================================================================================
Running Phase 2 Step 2B Build & Test Verification (Remediated)
Working Directory: /Users/dhairyajain/Desktop/pqc research
================================================================================
[*] Step 1: Compiling Independent Oracle Static Library...
make: Nothing to be done for `all'.
[*] Step 2: Compiling Integrated Experiment Runner...
ld: warning: building for macOS-26.5, but linking with dylib '/opt/homebrew/opt/liboqs/lib/liboqs.9.dylib' which was built for newer version 27.0
[*] Step 3: Symbol Verification — No srand/rand calls...
  ✓ No srand/rand undefined symbols
[*] Step 4: Verify mlkem768_keypair is not called...
  ✓ mlkem768_keypair has zero call-site references
[*] Step 5: Compiling Step 2B Validation Test Suite...
ld: warning: building for macOS-26.5, but linking with dylib '/opt/homebrew/opt/liboqs/lib/liboqs.9.dylib' which was built for newer version 27.0
[*] Step 6: Executing Step 2B Validation Test Suite...
================================================================================
Phase 2 — Step 2B Remediation Validation Test Suite
Subject: Deterministic SHAKE-256 PRF + Independent Keypair Generation
================================================================================
  [PASS] Test A: SHAKE-256 PRF determinism (same inputs → identical output)
  [PASS] Test B: PRF domain separation (trial, mode, all 6 loci, persistence all distinct)
  [PASS] Test C: Oracle keypair_derand produces valid non-trivial keys
  [PASS] Test D: Clean valid-path decapsulation matches oracle valid secret and differs from rejection key
  [PASS] Test E: Runner binary has no undefined srand/rand and 0 mlkem768_keypair call sites
  [PASS] Test F: PRF output is non-zero with reasonable byte diversity (>=16 distinct)
  [PASS] Test G: Explicit Little-Endian Serialization & SHAKE-256 KAT (Cases 1 & 2)

================================================================================
RESULTS: 7 passed, 0 failed
================================================================================
================================================================================
PHASE 2 STEP 2B TESTS COMPLETED SUCCESSFULLY (EXIT 0)
================================================================================
```

---

### 2.2 Step 2B Rigorous Mutation Checks
**Command:**
```bash
./tfib_experiments/run_step2b_mutation_checks.sh
```

**Console Output:**
```text
================================================================================
Phase 2 Step 2B Rigorous Mutation Verification
Working Directory: /Users/dhairyajain/Desktop/pqc research
================================================================================
[*] Baseline: Verifying unmutated test suite passes with exit code 0...
ld: warning: building for macOS-26.5, but linking with dylib '/opt/homebrew/opt/liboqs/lib/liboqs.9.dylib' which was built for newer version 27.0
  ✓ Baseline passed (Exit 0)

[*] Mutation 1: Deliberately corrupting expected valid secret in clean-path test...
ld: warning: building for macOS-26.5, but linking with dylib '/opt/homebrew/opt/liboqs/lib/liboqs.9.dylib' which was built for newer version 27.0
  ✓ Mutation 1 successfully caught: Test D failed as expected (Exit code 1)

[*] Mutation 2: Simulating decapsulation returning rejection key on clean ciphertext...
ld: warning: building for macOS-26.5, but linking with dylib '/opt/homebrew/opt/liboqs/lib/liboqs.9.dylib' which was built for newer version 27.0
  ✓ Mutation 2 successfully caught: Test D failed when output matches rejection key (Exit code 1)

[*] Mutation 3: Removing locus input differentiation from campaign_prf context...
ld: warning: building for macOS-26.5, but linking with dylib '/opt/homebrew/opt/liboqs/lib/liboqs.9.dylib' which was built for newer version 27.0
  ✓ Mutation 3 successfully caught: Test B failed when locus differentiation was removed (Exit code 1)

[*] Mutation 4: Altering byte serialization order to big-endian...
ld: warning: building for macOS-26.5, but linking with dylib '/opt/homebrew/opt/liboqs/lib/liboqs.9.dylib' which was built for newer version 27.0
  ✓ Mutation 4 successfully caught: Test G (KAT) failed when serialization was altered (Exit code 1)

================================================================================
ALL 4 RIGOROUS MUTATION CHECKS PASSED (All mutations caught with exit code 1)
================================================================================
```

---

### 2.3 Step 2C Validation Suite & Dedicated Campaign Execution
**Command:**
```bash
./tfib_experiments/run_step2c_tests.sh
```

**Console Output:**
```text
================================================================================
Running Phase 2 Step 2C-A Build, Verification & Experiment Suite
Working Directory: /Users/dhairyajain/Desktop/pqc research
================================================================================
[*] Step 1: Compiling Independent Oracle Static Library...
make: Nothing to be done for `all'.
[*] Step 2: Compiling Step 2C-A Validation Test Suite...
ld: warning: building for macOS-26.5, but linking with dylib '/opt/homebrew/opt/liboqs/lib/liboqs.9.dylib' which was built for newer version 27.0
[*] Step 3: Executing Step 2C-A Validation Test Suite...
================================================================================
Phase 2 — Step 2C-A Validation Test Suite
Subject: Countermeasure Independence, Checker Faults & Common-Mode Resilience
================================================================================
  [PASS] Test 1: TFIB-REF detects operational twiddle transient fault and achieves genuine recovery
  [PASS] Test 2: TFIB-REF detects operational twiddle persistent fault and forces safe fail-stop
  [PASS] Test 3: TFIB-REF checker-only transient fault triggers false-alarm retry and recovers
  [PASS] Test 4: TFIB-REF persistent checker corruption safely forces fail-stop (refuses untrusted checker)
  [PASS] Test 5: TFIB-META handles metadata tag faults (transient recovers, persistent fail-stops)
  [PASS] Test 6: Checker internal logic corruption (sum_c^=1) triggers retry/safe fail-stop without SDC
  [PASS] Test 7: Simultaneous common-mode fault confirms local checker blind spot (0% det) but 100% FO containment
  [PASS] Test 8: Baseline monitor confirms Theorem 1 blind spot (0% det) with safe FO partitioning (0 SDC)
  [PASS] Test 9: Negative tests verify deliberate state corruption and invalid classifications are caught

================================================================================
RESULTS: 9 passed, 0 failed
================================================================================
[*] Step 4: Compiling Integrated Experiment Runner...
ld: warning: building for macOS-26.5, but linking with dylib '/opt/homebrew/opt/liboqs/lib/liboqs.9.dylib' which was built for newer version 27.0
[*] Step 5: Executing Dedicated Step 2C-A Campaign (900 Trials)...
================================================================================
EXECUTING TFIB TARGETED EXPERIMENTAL SUITES ACROSS 3 CONFIGURATIONS
================================================================================

[1/3] Testing Configuration: BASELINE (Original Monitor)
  - Clean Baseline: 50/50 Success, 0 False Alarms
  - Op Twiddle Transient: Detected=0/50 (0.0%), Recovered=0, Blind FO Catches=48, Ineffective Valid=2, SDC=0
  - Op Twiddle Persistent: Detected=0/50 (0.0%), Blind FO Catches=50, Ineffective Valid=0, SDC=0

[2/3] Testing Configuration: TFIB-REF (Strategy 1: Dual Reference)
  - Clean Baseline: 50/50 Success, 0 False Alarms
  - Op Twiddle Transient: Detected=50/50 (100.0%), Recovered=50/50 (100.0%), SDC=0
  - Op Twiddle Persistent: Detected=50/50 (100.0%), Safe Fail-Stops=50/50, SDC=0
  - Ref Twiddle Transient: Detected=50/50 (100.0%), Recovered=50/50 (100.0%), SDC=0
  - Ref Twiddle Persistent: Detected=50/50 (100.0%), Safe Fail-Stops=50/50, SDC=0
  - Simultaneous Common-Mode: Detected Locally=0/50 (0.0%), Blind FO Catches=49, Ineffective Valid=1, SDC=0
  - Checker Logic Transient: Detected=50/50 (100.0%), Recovered=50/50 (100.0%), SDC=0
  - Checker Logic Persistent: Detected=50/50 (100.0%), Safe Fail-Stops=50/50, SDC=0

[3/3] Testing Configuration: TFIB-META (Strategy 2: Metadata Tags)
  - Clean Baseline: 50/50 Success, 0 False Alarms
  - Op Twiddle Transient: Detected=50/50 (100.0%), Safe Fail-Stops=50/50, SDC=0
  - Op Twiddle Persistent: Detected=50/50 (100.0%), Safe Fail-Stops=50/50, SDC=0
  - Metadata Tag Transient: Detected=50/50 (100.0%), Recovered=50/50 (100.0%), SDC=0
  - Metadata Tag Persistent: Detected=50/50 (100.0%), Safe Fail-Stops=50/50, SDC=0
  - Checker Logic Transient: Detected=50/50 (100.0%), Recovered=50/50 (100.0%), SDC=0
  - Checker Logic Persistent: Detected=50/50 (100.0%), Safe Fail-Stops=50/50, SDC=0

================================================================================
ALL AUTOMATED ASSERTIONS PASSED! Total Trials Recorded: 900
Raw dataset successfully written to tfib_experiments/phase2_step2c_trial_results.csv
================================================================================
[*] Step 6: Verifying Trial Results Integrity...
  ✓ Exactly 900 trials recorded with 0 SDC events across all configurations
================================================================================
PHASE 2 STEP 2C-A VALIDATION & CAMPAIGN COMPLETED SUCCESSFULLY (EXIT 0)
================================================================================
```

---

## 3. Audit of Test 7 Label & Correction of Stale Terminology

### Audit Identification of Stale String
In the test execution output for Step 2C, Test 7 prints:
```text
[PASS] Test 7: Simultaneous common-mode fault confirms local checker blind spot (0% det) but 100% FO containment
```
Source code location: `tfib_experiments/test_step2c_countermeasure_independence.c:252`.

### Why "100% FO Containment" is Inaccurate and Stale
1. In the actual campaign and test runs, out of 150 locally blinded trials across all architectures (50 simultaneous paired mutations + 100 baseline twiddle trials):
   - **147 trials (98.0%)** resulted in active FO re-encryption rejection (`$ss = ss_{\text{rej}}$`).
   - **3 trials (2.0%)** resulted in clean valid secret preservation (`$ss = ss_{\text{expected}}$`) because the arithmetic perturbation was within the centered binomial decoding error-tolerance.
2. In the 3 decoding-slack trials, FO re-encryption comparison **did not fail** and did not actively reject the ciphertext; rather, the valid key was preserved natively by the decoding algorithm.
3. Therefore, attributing 100% of the non-SDC outcomes to "FO containment" conflates active cryptographic rejection with algorithmic decoding error-tolerance.

### Required Precise Scientific Wording
The accurate description established in the updated documentation is:
> **“Simultaneous paired software mutations demonstrated local checker blindness in the tested cases. End-to-end key outcomes were correct through active FO rejection or decoding preservation.”**

### Policy on Code and Test Output
Per packaging constraints, `tfib_experiments/test_step2c_countermeasure_independence.c` has **not** been modified, preserving historical code integrity. The label in Test 7 is explicitly identified and audited here as a known stale print label.
