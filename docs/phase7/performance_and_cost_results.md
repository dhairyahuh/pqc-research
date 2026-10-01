# Performance, Memory, and Implementation Cost Results

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Harness Output:** `results/phase7/processed/phase7_resilience_results.json`  
**Benchmarking Environment:** Apple Silicon AArch64, Apple clang 21.0.0 `-O3`, 2,000 iterations

---

## 1. Execution Latency and Computational Overhead

| Configuration | Decapsulation Latency | Relative Overhead | Overhead Category |
| :--- | :---: | :---: | :--- |
| **Config 1: Unprotected Baseline ML-KEM-768** | **42.77 µs** | **1.00x (Reference)** | Baseline |
| **Config 2: Unweighted Parity Invariant** | 43.21 µs | +1.0% (+0.44 µs) | Negligible |
| **Config 3: Complementary NTT Protection** | 43.84 µs | +2.5% (+1.07 µs) | Very Low |
| **Config 4: Full Duplicate Decapsulation (DMR)** | **86.81 µs** | **+103.0% (+44.04 µs)** | Punitive (2x Execution) |
| **Config 5: Layered Architecture** | **52.42 µs** | **+22.6% (+9.65 µs)** | **Moderate & Controlled** |

```text
Decapsulation Latency Comparison (µs)
0 µs            20 µs           40 µs           60 µs           80 µs          100 µs
|---------------+---------------+---------------+---------------+---------------+|
Config 1 (Base):   [42.77 µs]
Config 2 (Unw):    [43.21 µs]
Config 3 (Compl):  [43.84 µs]
Config 4 (DMR):    [======================================================== 86.81 µs]
Config 5 (Layer):  [================================ 52.42 µs]
```

### Breakdown of Layered Architecture Overhead (+9.65 µs)

1. **Layer 1 (Pre-Invocation CRC32-IEEE):** ~1.20 µs (12.4% of added overhead).
2. **Layer 2 (Dual Projections & Invariant Evaluation):** ~6.85 µs (71.0% of added overhead).
3. **Layer 3 (Multi-Rail Barrier Logic & FO Status Gate):** ~0.45 µs (4.7% of added overhead).
4. **Layer 4 (Control Flow & Status Handling):** ~1.15 µs (11.9% of added overhead).

---

## 2. Memory Footprint and Binary Overhead

| Resource Metric | Config 1 (Baseline) | Config 2 (Unweighted) | Config 3 (Complementary) | Config 4 (DMR) | Config 5 (Layered) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Static LUT Overhead** | 0 bytes | 0 bytes | 256 bytes (`inv_zetas`) | 0 bytes | 256 bytes |
| **Peak Stack Allocation** | ~3.8 KB | ~3.8 KB | ~4.0 KB | ~7.6 KB (Dual Buffers) | ~4.1 KB |
| **Binary Text Size (Text)** | 119.7 KB | 120.2 KB | 121.1 KB | 120.8 KB | 122.4 KB |
| **Binary Code Overhead** | 0.0% | +0.4% | +1.2% | +0.9% | **+2.3% (+2.7 KB)** |

---

## 3. Cost-Resilience Trade-Off Analysis

- **Full Duplicate Decapsulation (DMR)** demands more than **double the computational time** (+103.0%) and doubles peak stack memory (~7.6 KB). In constrained space flight computers (e.g. radiation-hardened LEON4 or ARM Cortex-R52 running at 50-200 MHz), doubling decapsulation latency severely restricts communication throughput.
- **The Layered Architecture** introduces only **+22.6% latency overhead**, consumes only **256 bytes of static table space**, and adds **negligible stack overhead (+0.3 KB)**.
- In return, it delivers superior resilience across all 8 threat classes, including classes where DMR has complete 0% failure (pre-invocation buffer corruption and persistent hardware latch-ups).
