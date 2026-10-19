# Reproducibility Guide and Empirical Audit Manifest

**Project Title:** Software-Level Fault Resilience for ML-KEM-768: Dual-Transform NTT Invariant Monitoring, Localized Register Rollback, and Containment  
**Audited Commit Hash:** `55dd937cbad66b24e5c2c0b89b78fa776801913c`  
**Git Branch:** `space-resilience-framework`  
**Host Architecture:** Apple M3 Pro, 12 CPU cores, macOS Darwin 25.1.0, Apple Clang 17.0.0  
**Artifact Directory:** `paper/`  
**Date:** October 2026  

---

## 1. Quick Reproduction Commands

### 1.1 Compile and Run the Production Fault-Injection Experiment (Table 2 & Table 3)
```bash
# 1. Compile the production reproducer against instrumented production objects
clang -O3 -Wall -Wextra \
  -Ialgorithms/source_ref/include -Ialgorithms/source_ref/cpa -Ialgorithms/source_ref/kem \
  phase18_audit/production_reproducer.c bin/obj/mlkem768_inst.o bin/obj/mlkem_fault_hooks.o \
  -o phase18_audit/production_reproducer

# 2. Execute fresh 400 production trials (F12, F4, F5A, F5B)
./phase18_audit/production_reproducer phase18_audit/raw_production_trials.csv
```
*Expected Output:*
- Total Trials: 400
- F12 (Control): 100/100 Clean Success
- F4 (Transient): 100/100 Recovered (1 retry/fault, valid key $K_{\text{valid}}$)
- F5A (Persistent): 100/100 Fail-Stop (2 retries/fault, rejection key $K_{\text{rej}}$)
- F5B (Force-Value): 100/100 Fail-Stop (2 retries/fault, rejection key $K_{\text{rej}}$)
- Production SDC: 0/300 active trials ($95\%$ Wilson Score CI: $[0.00\%, 1.26\%]$)

---

### 1.2 Run Known Answer Tests (KAT) & Implicit Rejection Oracle (Table 2 KAT Row)
```bash
# Compile and run NIST FIPS 203 KAT test runner
make tests/test_kat_mlkem768
./bin/tests/test_kat_mlkem768
```
*Expected Output:*
- KAT ML-KEM-768: 100/100 tests passed.
- Implicit Rejection Conformance: 100/100 invalid ciphertext mutations produce exact rejection keys matching the independent Keccak SHAKE-256 oracle.

---

### 1.3 Reproduce Performance Benchmarks (Table 4 & Figure 3)
```bash
# Execute production benchmark binary (2,000 measured iterations, 5,000 warmups)
./bin/phase7i_e2e_validation
```
*Expected Output:*
- Baseline Decapsulation: $\sim 110.8\,\mu\text{s}$
- Monitored Decapsulation: $\sim 129.5\,\mu\text{s}$ (+16.9% overhead on `-O3`)
- Sequential Software DMR: $\sim 260.7\,\mu\text{s}$ (+135.3% overhead on `-O3`)

---

## 2. Table-to-Source Evidence Traceability

| Artifact Item | Data Source | Exact Code or File Location | Independent Reproduction Status |
|:---|:---|:---|:---:|
| **Table 1: Transform Breakdown** | Source Code & Formal Flow | `algorithms/source_ref/cpa/indcpa.c:560,568,580,609,621`<br>`algorithms/source_ref/cpa/poly.c:174,218` | **Directly Derived** (11 transforms $\times 896 = 9,856$ butterflies) |
| **Table 2: Fault Injection** | Authoritative CSV | `phase18_audit/raw_production_trials.csv`<br>`phase18_audit/production_reproducer.c` | **Directly Reproduced** (Fresh execution matching historical) |
| **Table 3: H1 Circular Verifier** | Cleanroom CSV | `phase16_targeted_evidence_closure/h1_activation_audit.csv` | **Directly Recomputed** ($591/600 = 98.5\%$ false-pass) |
| **Table 4: Performance** | Benchmark Output | `results/phase7i/processed/phase7i_e2e_results.json`<br>`bin/phase7i_e2e_validation` | **Directly Reproduced** (Apple M3 Pro host) |
| **Figure 1: Architecture** | Vector SVG | `paper/figures/figure1_architecture.svg` | Generated from authoritative two-tier design |
| **Figure 2: Butterfly Flow** | Vector SVG | `paper/figures/figure2_butterfly_flow.svg` | Generated from decoupled CT and GS equations |
| **Figure 3: Latency Trade-off** | Vector SVG | `paper/figures/figure3_timing_tradeoff.svg` | Generated from Table 4 benchmark data |

---

## 3. Statistical Calculations

All confidence intervals in the paper are calculated using Edwin B. Wilson's score interval with continuity correction (Wilson, 1927 [R03]):
$$w = \frac{2n \hat{p} + z^2 \pm \left(z \sqrt{z^2 - \frac{1}{n} + 4n \hat{p} (1 - \hat{p}) + (4\hat{p} - 2)} + 1\right)}{2(n + z^2)}$$
For $z = 1.96$ ($95\%$ two-sided confidence):
- $F4$ ($100/100$): $[96.30\%, 100.00\%]$
- $F5A, F5B$ ($200/200$ combined): $[98.14\%, 100.00\%]$
- $H2$ ($0/300$ SDC): $[0.00\%, 1.26\%]$
- $H1$ ($591/600$ false passes): $[97.10\%, 99.20\%]$

---

## 4. Tests That Could Not Be Run & Methodological Rationale

1. **Physical Cyclotron / Radiation Beam Tests:** Physical particle accelerator irradiation was outside the scope of this pure software research project. The fault model relies on terrestrial software simulation of single-event upsets grounded in nuclear physics literature (Dodd & Massengill [P01], ECSS [P02]).
2. **Side-Channel TVLA on Hardware Power Traces:** While the baseline cryptographic implementation is constant-time, physical oscilloscope power trace acquisition (Test Vector Leakage Assessment) was not conducted. Side-channel claims are strictly qualified.
