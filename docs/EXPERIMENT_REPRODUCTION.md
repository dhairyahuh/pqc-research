# ASTRA-Sec: Experiment Reproduction Guide

This document contains exact, verified commands and instructions to reproduce the statistical experiments, Known Answer Tests (KATs), fault injection campaigns, and benchmarks reported in the ASTRA-Sec research project.

---

## 1. Cryptographic Baseline Verification (FIPS 203 & FIPS 204 KATs)

Execute the complete NIST Known Answer Test suite verifying both Path A (liboqs) and Path B (native clean-room C) implementations:

```bash
# Compile and run the FIPS 203/204 KAT runner
make test-c
```

### Expected Output Interpretation:
```text
=========================================================================
 NIST FIPS 203 & 204 KNOWN ANSWER TEST (KAT) VERIFICATION SUITE
=========================================================================
--- [1/6] ML-KEM-512 (FIPS 203) ---   Result: PASS
--- [2/6] ML-KEM-768 (FIPS 203) ---   Result: PASS
--- [3/6] ML-KEM-1024 (FIPS 203) ---  Result: PASS
--- [4/6] ML-DSA-44 (FIPS 204) ---    Result: PASS
--- [5/6] ML-DSA-65 (FIPS 204) ---    Result: PASS
--- [6/6] ML-DSA-87 (FIPS 204) ---    Result: PASS
```
All KAT vectors must report `PASS`. Any mismatch indicates broken compiler flags or corrupted math primitives.

---

## 2. ML-KEM-768 Fault Injection Campaign (38-Trial Core Matrix)

To execute the 38-trial empirical fault injection campaign evaluating NTT butterfly SEU bit-flips, twiddle corruption, and Fujisaki-Okamoto predicate bypassing:

```bash
# Build and run the native fault injection experiment
./bin/mlkem768_internal_fault_experiment
```

### Outputs Generated:
- Raw execution log: stdout
- Processed trial results: `results/mlkem768_internal_fault_validation.json`
- Statistical summary: Confirms $100.0\%$ detection rate for all targeted twiddle and butterfly SEU bit-flips, with $0.00\%$ Silent Data Corruption (SDC).

---

## 3. Experimental Laboratory Testbed (Phase 3 Campaigns)

ASTRA-Sec includes a fully reproducible experimental laboratory orchestrator:

```bash
# 1. Validate all experiment configuration manifests
make lab-validate

# 2. Run the fast pilot suite (verifies all 6 experimental groups)
make lab-pilot

# 3. Run the full multi-group experimental campaign
make lab-campaign
```

### Campaign Configurations Executed:
- `research/phase3_experimental_lab/configs/group_a_baseline_non_pqc.json`: Classical baseline (RSA-3072 / ECDH).
- `research/phase3_experimental_lab/configs/group_b_baseline_unmonitored_pqc.json`: Standard unmonitored ML-KEM-768.
- `research/phase3_experimental_lab/configs/group_d_full_astra_sec.json`: Full ASTRA-Sec 7-layer stack.
- `research/phase3_experimental_lab/configs/group_e_payload_scaling.json`: ADU sizes from 64 B to 64 KB.
- `research/phase3_experimental_lab/configs/group_g_impairment.json`: Contact loss, bit error rates, out-of-order delivery.
- `research/phase3_experimental_lab/configs/group_j_fault_campaign.json`: Single and multi-bit SEU sweeps.

All trial logs are recorded with fixed random seeds (`seed: 42`, `seed: 1337`) in `results/phase3/` and summarized in `results/phase3_laboratory_summary.json`.

---

## 4. Cryptographic Micro-Benchmarks

To benchmark individual cryptographic primitives, DTN framing, and network wire serialization:

```bash
python3 benchmarks/micro_benchmarks.py
```

### Metrics Produced:
- ML-KEM-768 Keygen latency ($\mu\text{s}$)
- ML-KEM-768 Encapsulation latency ($\mu\text{s}$)
- Monitored ML-KEM-768 Decapsulation latency ($\mu\text{s}$)
- ML-DSA-65 Signing latency ($\mu\text{s}$)
- ML-DSA-65 Verification latency ($\mu\text{s}$)
- AES-256-GCM AEAD throughput ($\text{MB/s}$)
- RFC 9171 BPv7 CBOR framing overhead ($\mu\text{s}$)

Results are exported to CSV format in `/tmp/raw_crypto_latencies.csv` and JSON format in `/tmp/benchmark_results.json`.

---

## 5. Live Telemetry Overhead Benchmark

To verify that the microsecond-resolution telemetry engine adheres to the $<1.0\%$ overhead bound:

```bash
python3 -c "
from astra_sec.service.telemetry_benchmark import measure_instrumentation_overhead
report = measure_instrumentation_overhead(n_iterations=50)
print('Baseline Latency:   ', report.baseline_latency_us, 'us')
print('Instrumented Latency:', report.instrumented_latency_us, 'us')
print('Absolute Overhead:  ', report.overhead_us, 'us')
print('Relative Overhead:  ', f'{report.overhead_percent:.2f}%')
print('Status:             ', report.status)
"
```

Expected output: Relative overhead $\approx 0.81\% < 1.0\%$ (`PASS`).
