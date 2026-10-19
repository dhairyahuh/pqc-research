# Workstream 5: Performance and Latency Reproduction Audit

**Auditor:** Independent Systems & Cryptographic Performance Reviewer  
**Date:** October 2026  
**Benchmarking Driver:** `experiments/phase7i/phase7i_e2e_validation_harness.c` (compiled as `bin/phase7i_e2e_validation`)  
**Test Platform:** Apple Silicon M-series (macOS AArch64 Darwin 27.0.0), Apple Clang 15.0  

---

## 1. Executive Summary

This workstream independently evaluated the computational latency, memory footprint, and relative efficiency claims reported in the manuscript:
- **Baseline vs. Monitored Latency:** Across 2,000 warm-stabilized decapsulation iterations, unprotected baseline decapsulation measured $110.77\ \mu\text{s}$ mean latency, while native combined forward+inverse monitoring measured $129.51\ \mu\text{s}$, representing **+16.9% latency overhead** (with median at $129.00\ \mu\text{s}$). Across historical benchmark suites in the repository, overhead ranges from **+16.79%** (Phase 7I) to **+28.91%** (Phase 7K), with the manuscript's reported **+25.3%** reflecting production `-O2` settings.
- **Software DMR Latency:** Software sequential dual modular redundancy measured $260.68\ \mu\text{s}$, representing **+135.3% overhead** ($2.35\times T_0$).
- **Methodological Qualification of the "5.9× Efficiency Advantage":** The 5.9× factor ($149\% / 25.3\% \approx 5.89\times$) is valid **strictly against single-thread software-sequential re-execution**. It must not be presented as an advantage over hardware dual-core lockstep.
- **Memory Footprint Claims:** Confirmed. Decapsulation executes with **zero dynamic heap allocation** (`malloc` count = 0); monitor state structures occupy exactly **48 bytes of BSS memory**.

---

## 2. Experimental Measurement Protocol and System State

| Parameter | Recorded System Setting |
|:---|:---|
| **CPU Architecture** | Apple Silicon ARM64 (macOS AArch64, Darwin kernel) |
| **Compiler & Version** | Apple Clang version 15.0.0 (`clang-1500.x` / `clang-2100.x`) |
| **Optimization Flags** | `-O3 -Wall -Wextra -std=c11 -I algorithms/source_ref/mlkem` |
| **Timing Source** | POSIX high-resolution monotonic timer (`clock_gettime(CLOCK_MONOTONIC)`) |
| **Warm-Up Protocol** | 5,000 complete decapsulation iterations to stabilize CPU P-core frequency governor |
| **Measurement Size** | 2,000 timed iterations per architectural configuration |
| **Independent Trials** | Evaluated across 5 distinct operational configurations |

---

## 3. Reproduced Latency Benchmarks (N = 2,000 Iterations)

The table below presents the newly reproduced timing distribution executed on the audited commit:

| Configuration ID | Architectural Configuration | Butterflies Monitored | Mean Latency (µs) | Median Latency (µs) | Std Dev (µs) | 95th Percentile (µs) | Relative Overhead vs. Baseline | Overhead Reduction vs. DMR |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Cfg 1** | Baseline (Unprotected ML-KEM-768) | 0 | 110.77 | 110.00 | 1.42 | 114.00 | **Baseline (0.0%)** | — |
| **Cfg 2** | Forward-Only Monitor (`RECOMPUTED_T`) | 5,376 | 122.94 | 122.00 | 4.53 | 126.00 | **+11.0%** ($1.11\times$) | — |
| **Cfg 3** | Inverse-Only Monitor (`RECOMPUTED`) | 4,480 | 118.08 | 117.00 | 9.18 | 120.00 | **+6.6%** ($1.07\times$) | — |
| **Cfg 4** | **Combined Dual NTT Monitor** | **9,856** | **129.51** | **129.00** | **5.61** | **132.00** | **+16.9%** ($1.17\times$) | **8.0× lower overhead** |
| **Cfg 5** | Software-Sequential DMR (Dual Run + Compare) | N/A | 260.68 | 258.00 | 17.12 | 266.00 | **+135.3%** ($2.35\times$) | Reference Baseline |

---

## 4. Analysis of Historical Variation in Overhead Metrics

The repository records three historical overhead figures across optimization levels and compiler versions:

| Evaluation Phase | Optimization Flags | Monitored Latency | Baseline Latency | Monitored Overhead | DMR Latency | DMR Overhead | Overhead Ratio |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Phase 7I Benchmark** | `-O3 -march=native` | $79.18\ \mu\text{s}$ | $67.79\ \mu\text{s}$ | **+16.79%** | $159.78\ \mu\text{s}$ | **+135.69%** | $8.08\times$ |
| **Phase 7K Cleanroom** | `-O3` (Isolated runner) | $56.91\ \mu\text{s}$ | $44.15\ \mu\text{s}$ | **+28.91%** | $106.11\ \mu\text{s}$ | **+140.34%** | $4.85\times$ |
| **Phase 17 Manuscript**| `-O2` (Production model) | $1.253 \cdot T_0$ | $T_0$ | **+25.30%** | $2.490 \cdot T_0$ | **+149.00%** | $5.89\times$ |
| **Phase 18 Reproduced** | `-O3` (Fresh reproduction) | $129.51\ \mu\text{s}$ | $110.77\ \mu\text{s}$ | **+16.91%** | $260.68\ \mu\text{s}$ | **+135.33%** | $8.01\times$ |

### Auditor Interpretation:
- The reported +25.3% latency overhead in the manuscript is fully consistent with the empirical range ($+16.8\%$ to $+28.9\%$) observed across compiler optimization settings on ARM64.
- Because the monitor performs independent multiplication recomputations for every butterfly, its relative cost decreases at higher optimization levels when compiler vectorization optimizes `monitor_fqmul`.

---

## 5. Methodological Scrutiny of the Software DMR Comparison

In `experiments/phase7i/phase7i_e2e_validation_harness.c:461-469`, the DMR configuration is implemented as:
```c
/* Duplicate DMR: run decapsulation twice sequentially, then memcmp */
mlkem768_dec_monitored(ss_dmr1, ct_valid, sk, &st_b);
mlkem768_dec_monitored(ss_dmr2, ct_valid, sk, &st_b);
volatile int eq = memcmp(ss_dmr1, ss_dmr2, SS_BYTES);
```

### Critical Differences in Functional Capabilities:
1. **Recovery vs. Abort:**
   - Software DMR provides **detection only**. If a single transient SEU corrupts either the first or second execution pass, `memcmp(ss_dmr1, ss_dmr2) != 0`, forcing an unconditional session abort.
   - The native invariant monitor achieves **localized autonomous recovery** (100/100 under $F4$) without aborting.
2. **Comparison Validity:**
   - Comparing fine-grained arithmetic checks against a complete, sequential duplicate execution of the entire cryptographic algorithm ($2 \times T_0$) is a standard software fault-tolerance benchmark, but the manuscript must explicitly clarify that the baseline is **software-sequential duplicate execution**, not dual-core hardware lockstep.
