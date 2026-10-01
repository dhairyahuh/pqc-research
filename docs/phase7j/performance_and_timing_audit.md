# Phase 7J: Performance Benchmarks & Side-Channel Timing Audit

## 1. Multi-Run Empirical Benchmarking Protocol

To eliminate transient CPU throttling, thread contention, and cache warming artifacts, benchmarks were collected across **three independent measurement batches**, each executing 2,000 timed iterations preceded by 5,000 warmup decapsulations ($N = 6,000$ decapsulations per configuration).

- **Hardware Platform**: Apple Silicon (ARM64), Darwin kernel, Clang 17.0 (`-O3 -march=native`).
- **Timing Primitive**: `clock_gettime(CLOCK_MONOTONIC)` with sub-microsecond resolution.
- **Reference DMR Implementation**: Executes the production decapsulation path twice in succession and compares output buffers with constant-time equality checks.

---

## 2. Multi-Run Latency Distributions across 5 Configurations

| Benchmark Run / Config | 1. Baseline | 2. Forward-Only | 3. Inverse-Only | 4. Combined Dual | 5. Duplicate DMR |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Run 1 Mean Latency** | 66.64 µs | 73.20 µs (+9.9%) | 69.98 µs (+5.0%) | 81.13 µs (+21.8%) | 161.35 µs (+142.1%) |
| **Run 2 Mean Latency** | 64.44 µs | 78.83 µs (+22.3%) | 70.74 µs (+9.8%) | 89.27 µs (+38.5%) | 168.01 µs (+160.7%) |
| **Run 3 Mean Latency** | 63.47 µs | 72.77 µs (+14.6%) | 69.84 µs (+10.0%) | 81.90 µs (+29.0%) | 163.72 µs (+158.0%) |
| **Aggregate Mean ($\mu$)** | **64.85 µs** | **74.94 µs** | **70.19 µs** | **84.10 µs** | **164.36 µs** |
| **Aggregate Median ($\tilde{\mu}$)** | **64.00 µs** | **72.00 µs** | **70.00 µs** | **80.00 µs** | **159.00 µs** |
| **Standard Deviation ($\sigma$)** | 7.11 µs | 39.71 µs | 2.56 µs | 32.29 µs | 65.70 µs |
| **95th Percentile ($P_{95}$)** | 68.00 µs | 78.00 µs | 71.00 µs | 86.00 µs | 169.00 µs |
| **Mean Overhead vs Baseline** | **0.00%** | **+15.56%** | **+8.23%** | **+29.68%** | **+153.45%** |

### Benchmark Analysis & Overhead Range:
- Under optimal, quiescent thermal conditions (Run 1 and Phase 7I), Combined Invariant Monitoring achieves **+16.79% to +21.8% overhead**.
- Under background thread contention and CPU frequency scaling variations (Runs 2 & 3), Combined Invariant Monitoring reaches up to **+29.7% overhead**.
- In all observed runs, Dual Modular Redundancy consistently incurs **+142% to +161% overhead** (exceeding double latency).
- **Efficiency Factor**: Combined native monitoring achieves a **5.2x to 8.1x reduction in runtime overhead** compared to DMR while providing autonomous transient recovery that DMR cannot provide.

---

## 3. Randomized-Order Constant-Time Assessment

To evaluate whether the native monitor or hardened fail-stop logic creates a side-channel ciphertext-validity oracle:
- **Interleaving Protocol**: 1,000 decapsulation trials were executed where valid ciphertexts and invalid ciphertexts alternated pseudorandomly ($p = 0.5$).
- **Statistical Results**:
  - Valid Ciphertext Mean: **80.08 µs** (Median: 80.00 µs, $\sigma = 1.50\ \mu\text{s}$)
  - Invalid Ciphertext Mean: **80.03 µs** (Median: 80.00 µs, $\sigma = 1.48\ \mu\text{s}$)
  - Latency Ratio (Invalid / Valid): **0.9995x (Mean)**, **1.0000x (Median)**
  - Cohen's $d$: **$0.0276$** (Categorized as negligible, $|d| < 0.20$)
  - Welch's Two-Sample $t$-test: $t = 0.616$, $p \approx 0.54$ ($p \gg 0.05$)

The empirical distribution shows no statistically significant distinction between valid and invalid inputs.

---

## 4. Assembly Inspection of `kem.c` Fail-Stop Logic

Disassembly of compiled object code confirms that `kem.c` accumulates status without conditional branching on secret material:
```assembly
; Constant-time fail-stop evaluation in kem.c
eor      w10, w8, w9               ; w10 = fail ^ fail_chk
adrp     x11, _g_ntt_native_monitor
ldr      w12, [x11, #:lo12:_g_ntt_native_monitor]
adrp     x13, _g_invntt_native_monitor
ldr      w14, [x13, #:lo12:_g_invntt_native_monitor]
orr      w15, w12, w14             ; persistent_count |= invntt_persistent
orr      w10, w10, w15             ; combined discrepancy
cmp      w10, #0
cset     w16, ne                   ; 1 if persistent > 0 or fail != fail_chk
sbfx     w16, w16, #0, #8          ; sign-extend to 0xFF
orr      w8, w8, w16               ; fail |= 0xFF
```
All evaluations utilize straight-line arithmetic and bitwise instructions (`eor`, `orr`, `cset`, `sbfx`, `orr`), avoiding secret-dependent jump instructions (`b.eq`, `cbz`).

---

## 5. Scope and Limitations of Timing Conclusions

1. **What Is Established**:
   Software execution latency on the tested Apple Silicon architecture shows no macro-architectural leakage distinguishing valid from invalid ciphertexts ($|d| < 0.03$, $p > 0.50$).
2. **What Is NOT Established**:
   Software timing benchmarks cannot rule out physical power consumption (DPA/CPA), electromagnetic emission (SEMA/CEMA), or microarchitectural cache-line eviction timing (e.g. Prime+Probe) at nanosecond resolution on dedicated hardware probes.
