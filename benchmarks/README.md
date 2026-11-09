# Benchmarks Directory

This directory provides documentation and references for the performance benchmarks conducted on the Apple M3 Pro hardware platform.

## Benchmark Summary

- **Target Architecture:** Apple M3 Pro (12-core CPU, 18-core GPU), 36 GB Unified LPDDR5 Memory.
- **Reference Timing Dataset:** [`tfib_benchmark_raw.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_benchmark_raw.csv) (15,000 raw latency records).
- **Key Latency Findings:**
  - Standard ML-KEM-768 NTT: $8.790\ \mu\text{s}$ mean latency.
  - TFIB-Hardened ML-KEM-768 NTT: $8.973\ \mu\text{s}$ mean latency ($+2.08\%$ overhead).
  - Inverse-NTT Verification: $10.276\ \mu\text{s}$ mean latency ($+16.9\%$ overhead).
  - Dual Modular Redundancy (DMR): $17.521\ \mu\text{s}$ mean latency ($+99.33\%$ overhead).

For complete benchmarking methodology, see [`docs/experiments/BENCHMARKING.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/experiments/BENCHMARKING.md).

