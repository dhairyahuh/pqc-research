# Phase 7I: Integrated Decapsulation Performance & Benchmark Analysis

## 1. Methodology & Test Environment

All performance benchmarks were collected using `experiments/phase7i/phase7i_e2e_validation_harness.c` compiled under standard optimization flags (`-O3 -march=native`).

- **Target Operation**: Complete `mlkem768_dec` execution path (including hash operations, matrix-vector expansion, NTT, point-wise multiplications, inverse NTT, poly add/sub, compress/decompress, and re-encryption verification).
- **Execution Protocol**:
  - Warmup: 5,000 full decapsulation iterations to stabilize CPU frequency scaling and cache state.
  - Measurement: 2,000 timed iterations per configuration using high-resolution monotonic clock (`clock_gettime(CLOCK_MONOTONIC)`).
  - Test Platform: Apple Silicon (ARM64), Darwin kernel, Clang 17.0.

---

## 2. Integrated Decapsulation Latencies across 5 Configurations

| Configuration | Butterflies Monitored | Mean Latency (µs) | Median Latency (µs) | Std Dev (µs) | 95th Percentile (µs) | Overhead vs Baseline |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Baseline (Unmonitored)** | 0 | 67.79 | 67.00 | 2.74 | 70.00 | **0.00%** (1.00x) |
| **2. Forward-Only Monitor** | 5,376 | 75.92 | 76.00 | 3.12 | 79.00 | **+11.99%** (1.12x) |
| **3. Inverse-Only Monitor** | 4,480 | 72.20 | 72.00 | 2.89 | 75.00 | **+6.50%** (1.065x) |
| **4. Combined (Fwd + Inv)** | **9,856** | **79.18** | **79.00** | **3.05** | **83.00** | **+16.79%** (1.17x) |
| **5. Duplicate DMR Reference**| N/A | 159.78 | 158.00 | 5.82 | 166.00 | **+135.69%** (2.36x) |

---

## 3. Analysis of Computational Overhead

### 3.1. Per-Transform Breakdown
In ML-KEM-768 decapsulation ($k = 3$ polynomials):
1. **Forward NTT Operations**:
   - $\text{poly\_ntt}(\hat{\mathbf{s}})$ is precomputed in secret key.
   - Decapsulation performs forward NTT on recovered message polynomials and re-encryption vector $\mathbf{u}$.
   - Total forward butterflies: **5,376 butterflies**.
   - Added cost for forward invariant checking: $\approx 8.13\ \mu\text{s}$ (+11.99%).
2. **Inverse NTT Operations**:
   - Computes $\text{poly\_invntt\_tomont}$ on product $\hat{\mathbf{s}}^T \hat{\mathbf{u}}$ and re-encrypted ciphertext vectors.
   - Total inverse butterflies: **4,480 butterflies**.
   - Added cost for inverse invariant checking: $\approx 4.41\ \mu\text{s}$ (+6.50%).
3. **Combined Decapsulation Invariant Checking**:
   - Total butterflies monitored per decapsulation: **9,856 butterflies**.
   - Total combined latency: **79.18 µs**, representing **+16.79% overhead** over baseline.

### 3.2. Comparison Against Dual Modular Redundancy (DMR)
Dual Modular Redundancy executes decapsulation twice and compares outputs:
- **DMR Overhead**: +135.69% (159.78 µs vs 67.79 µs). DMR more than doubles execution latency and consumes $2\times$ energy.
- **Overhead Reduction Factor**: The combined native invariant monitor delivers full transform coverage at +16.79% overhead, representing an **8.1x reduction in runtime overhead** compared to DMR:
  $$\frac{\text{Overhead}_{\text{DMR}}}{\text{Overhead}_{\text{Combined}}} = \frac{135.69\%}{16.79\%} \approx 8.08\times$$
- **Resilience Advantage**: DMR only provides *detection*; when a fault occurs, DMR must abort and fail. In contrast, the native invariant monitor provides *in-place autonomous recovery* for transient arithmetic faults.

---

## 4. Memory Footprint and Code Size

- **Shadow Register Overhead**: Local variables inside butterfly macros (`u_shadow`, `v_shadow`, `d_check`) fit entirely within CPU register files (ARM64 general-purpose registers `x0`-`x30` / `w0`-`w30`).
- **RAM Overhead**: The global state structures (`invntt_native_monitor_state_t` and `ntt_native_monitor_state_t`) consume only **48 bytes of BSS memory**, presenting zero heap allocation overhead.
- **Binary Footprint**: Inlining monitor macros increases compiled `.text` size by less than 1.8 KB.
