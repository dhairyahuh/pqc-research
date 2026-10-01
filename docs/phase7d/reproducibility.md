# Reproducibility Guide: Phase 7D Adversarial Validation

## 1. Experimental Environment and Platform Baseline

- **Operating System:** macOS Darwin 24.3.0 (Darwin Kernel Version 24.3.0)
- **Host Architecture:** Apple Silicon AArch64 (ARMv8.5-A with NEON, AES, SHA extensions)
- **Compiler Version:** Apple clang version 17.0.0 (`clang-1700.0.13.5`)
- **Compilation Flags:** `-O3 -Wall -Wextra -std=c11 -I/opt/homebrew/include`
- **Linker Flags:** `-L/opt/homebrew/lib -loqs`
- **Runtime Libraries:** liboqs (Open Quantum Safe), Standard C Library (libc)
- **Target Implementation:** NIST FIPS 203 ML-KEM-768 Scalar C Reference Implementation (`algorithms/source_ref/mlkem/`)

---

## 2. Deterministic Seeds and PRNG Configuration

To ensure 100% reproducible trial generation across all campaigns:
- **Trial Seed Formula:**
  $$\text{Seed}(c, t) = c \times 10000 + t + 777$$
  where $c \in [0, 7]$ denotes the fault class index and $t \in [0, 149]$ denotes the trial index within the class.
- **Trial Count:** 150 trials per threat class across 8 classes = **1,200 total injection trials**.
- **Benchmark Iterations:** 2,000 warmed-up iterations per configuration, preceded by 5,000 iteration CPU cache/DVFS warmup.

---

## 3. Statistical Analysis Methodology

For each fault class and outcome metric, detection rates and recovery rates are accompanied by **Wilson score 95% confidence intervals**:

$$\hat{p} \pm \frac{z}{1 + \frac{z^2}{n}} \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}$$

where $z = 1.96$ for a two-sided 95% confidence interval, $n = 150$ is the sample size per class, and $\hat{p}$ is the sample proportion.

For $n = 150$ and $\hat{p} = 1.000$ (100.0%), the Wilson 95% confidence interval is:
$$[97.53\%, 100.00\%]$$
Zero observed failures in 150 trials establishes that the true detection probability is at least $97.53\%$ with $95\%$ confidence; it does **not** prove universal $100\%$ immunity.

---

## 4. Step-by-Step Reproduction Commands

### Step 1: Build Phase 7D Validation Harness
```bash
make phase7d
```

### Step 2: Run Phase 7D Adversarial Validation Campaign & Benchmarks
```bash
make test-phase7d
```

### Step 3: Run Full Automated Verification Suite
```bash
python3 -m unittest discover tests/phase7d -v
```

### Step 4: Verify Non-Regression on Prior Phases
```bash
make test-phase7c
make test-phase7b
make test-phase7
make test
```

---

## 5. Artifact Directory Structure

- `docs/phase7d/`: Architectural threat model, implementation audit, constant-time audit, recovery analysis, claim reconciliation, reproducibility.
- `experiments/phase7d/phase7d_adversarial_harness.c`: Adversarial fault injection harness and calibrated benchmark runner.
- `results/phase7d/raw/phase7d_adversarial_trials.json`: Individual records for all 1,200 trials with deterministic seeds and failure logs.
- `results/phase7d/processed/phase7d_adversarial_results.json`: Processed detection, recovery, safe-rejection, and calibrated latency metrics with 95% Wilson CIs.
- `tests/phase7d/test_phase7d_adversarial.py`: Unit tests verifying schema, detection limits, constant-time assembly properties, and KAT regression.
