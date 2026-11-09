# ASTRA-Sec Research Manuscript Reproducibility Package

This package provides complete, deterministic instructions to verify all mathematical proofs, benchmark latencies, experimental campaigns, tables, figures, and publication artifacts for **ASTRA-Sec**.

---

## 1. Provenance and Environment Specifications

- **Operating System**: macOS Darwin 24.6.0 (arm64, Apple Silicon)
- **Target Platform**: Apple M3 Pro (12-core CPU, 36 GB LPDDR5)
- **C Compiler**: Apple clang version 17.0.0 (`-O3 -std=c11 -fPIC -Wall -Wextra -Werror`)
- **Python Version**: Python 3.9.6 (64-bit)
- **Cryptographic Libraries**:
  - `liboqs` version 0.16.0 (Open Quantum Safe FIPS 203 & 204 implementations)
  - Native `libastra_crypto` (C99/C11 dual-transform monitored core)
- **Deterministic PRNG Seed**: `42` (applied uniformly across test harnesses and campaigns)

---

## 2. Experimental Data Provenance

All numbers reported in the manuscript are directly extracted from persistent JSON and CSV datasets:

| Data Artifact | Location | Description |
| :--- | :--- | :--- |
| **Micro-Benchmark JSON** | [`data/benchmarks/benchmark_results.json`](file:///Users/dhairyajain/Desktop/pqc%20research/data/benchmarks/benchmark_results.json) | $N=200$ latency trials, statistical distributions, wire sizes |
| **Crypto Latencies CSV** | [`data/benchmarks/raw_crypto_latencies.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/data/benchmarks/raw_crypto_latencies.csv) | Mean, standard deviation, 95% CI, p50, p90, p99 |
| **Fault Campaign JSONL** | [`data/experiments/trials/campaign_results.jsonl`](file:///Users/dhairyajain/Desktop/pqc%20research/data/experiments/trials/campaign_results.jsonl) | 38 adversarial & fault-injection trial records |
| **Fault Coverage Matrix** | [`data/experiments/matrices/fault_coverage_matrix.json`](file:///Users/dhairyajain/Desktop/pqc%20research/data/experiments/matrices/fault_coverage_matrix.json) | 5-group coverage mapping |

---

## 3. End-to-End Reproduction Commands

### Step 1: Run Full Test and Verification Pipeline
```bash
# 1. Run Python unit and integration test suites
make test-python

# 2. Run C Known Answer Tests and baseline harnesses
make test-c

# 3. Comprehensive test suite
make test

# 4. Check system diagnostic health
make health-check
```

### Step 2: Reproduce the 38-Trial Adversarial Fault Campaign
```bash
python3 -m unittest discover -s tests/integration -p "test_adversarial_campaigns.py" -v
python3 scripts/analyze_experiments.py data/experiments/trials/campaign_results.jsonl data/experiments/matrices/fault_coverage_matrix.json
```

### Step 3: Reproduce Performance Benchmarks
```bash
python3 benchmarks/run_comparative_benchmarks.py
python3 benchmarks/analyze_benchmarks.py
```

### Step 4: Re-render Publication Figures
```bash
python3 benchmarks/plot_benchmarks.py
```
This generates 5 high-resolution (300 DPI) plots in `data/benchmarks/plots/` and `manuscript/figures/`:
1. `crypto_latency_comparison.png`
2. `monitored_vs_dmr_overhead.png`
3. `dtn_security_overhead.png`
4. `system_e2e_latency_distribution.png`
5. `storage_and_network_overhead.png`

---

## 4. Manuscript Compilation Instructions

To compile `manuscript/main.tex` into `main.pdf` on any system with a standard TeX Live / MacTeX distribution:

```bash
cd manuscript/
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```
Or using `latexmk`:
```bash
latexmk -pdf main.tex
```
