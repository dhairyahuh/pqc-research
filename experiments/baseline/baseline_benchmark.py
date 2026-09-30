"""
Baseline Benchmark Suite for ML-KEM (FIPS 203) and ML-DSA (FIPS 204).
Measures:
- Latency (mean, median, min, max, std-dev) for each cryptographic operation
- Throughput (operations per second)
- Cryptographic object sizes (public key, secret key, ciphertext, signature)
- Generates JSON summary and formatted comparative reports.
"""

import os
import sys
import time
import json
import statistics
from typing import Dict, List, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from algorithms.oqs_wrapper import MLKEM, MLDSA, get_liboqs_version


def benchmark_operation(func, *args, iterations: int = 200, warmup: int = 20) -> Dict[str, float]:
    """Runs a function for warmup + iterations and computes detailed timing metrics."""
    # Warmup
    for _ in range(warmup):
        func(*args)

    timings: List[float] = []
    for _ in range(iterations):
        t0 = time.perf_counter_ns()
        func(*args)
        t1 = time.perf_counter_ns()
        timings.append((t1 - t0) / 1000.0)  # Microseconds (µs)

    mean_us = statistics.mean(timings)
    median_us = statistics.median(timings)
    stdev_us = statistics.stdev(timings) if len(timings) > 1 else 0.0
    min_us = min(timings)
    max_us = max(timings)
    ops_per_sec = 1_000_000.0 / mean_us if mean_us > 0 else 0.0

    return {
        "mean_us": round(mean_us, 2),
        "median_us": round(median_us, 2),
        "stdev_us": round(stdev_us, 2),
        "min_us": round(min_us, 2),
        "max_us": round(max_us, 2),
        "ops_per_sec": round(ops_per_sec, 1)
    }


def run_kem_benchmarks(iterations: int = 500) -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print(" BENCHMARKING ML-KEM (FIPS 203)")
    print("=" * 70)
    kem_algs = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]
    results = {}

    for alg in kem_algs:
        print(f"\nEvaluating {alg} ({iterations} iterations)...")
        kem = MLKEM(alg)

        # 1. KeyGen
        keygen_metrics = benchmark_operation(kem.keypair, iterations=iterations)
        pk, sk = kem.keypair()

        # 2. Encaps
        encaps_metrics = benchmark_operation(kem.encaps, pk, iterations=iterations)
        ct, ss = kem.encaps(pk)

        # 3. Decaps
        decaps_metrics = benchmark_operation(kem.decaps, ct, sk, iterations=iterations)

        results[alg] = {
            "object_sizes": {
                "public_key_bytes": kem.length_public_key,
                "secret_key_bytes": kem.length_secret_key,
                "ciphertext_bytes": kem.length_ciphertext,
                "shared_secret_bytes": kem.length_shared_secret
            },
            "keygen": keygen_metrics,
            "encaps": encaps_metrics,
            "decaps": decaps_metrics
        }

        print(f"  KeyGen: {keygen_metrics['median_us']} µs (median) | {keygen_metrics['ops_per_sec']} ops/s")
        print(f"  Encaps: {encaps_metrics['median_us']} µs (median) | {encaps_metrics['ops_per_sec']} ops/s")
        print(f"  Decaps: {decaps_metrics['median_us']} µs (median) | {decaps_metrics['ops_per_sec']} ops/s")
        print(f"  Sizes:  PK={kem.length_public_key}B, SK={kem.length_secret_key}B, CT={kem.length_ciphertext}B")

    return results


def run_dsa_benchmarks(iterations: int = 500) -> Dict[str, Any]:
    print("\n" + "=" * 70)
    print(" BENCHMARKING ML-DSA (FIPS 204)")
    print("=" * 70)
    dsa_algs = ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]
    results = {}
    test_msg = b"Baseline benchmark telemetry packet payload: status OK, power 28.4V."

    for alg in dsa_algs:
        print(f"\nEvaluating {alg} ({iterations} iterations)...")
        sig = MLDSA(alg)

        # 1. KeyGen
        keygen_metrics = benchmark_operation(sig.keypair, iterations=iterations)
        pk, sk = sig.keypair()

        # 2. Sign
        sign_metrics = benchmark_operation(sig.sign, test_msg, sk, iterations=iterations)
        signature = sig.sign(test_msg, sk)

        # 3. Verify
        verify_metrics = benchmark_operation(sig.verify, test_msg, signature, pk, iterations=iterations)

        results[alg] = {
            "object_sizes": {
                "public_key_bytes": sig.length_public_key,
                "secret_key_bytes": sig.length_secret_key,
                "signature_bytes": sig.length_signature
            },
            "keygen": keygen_metrics,
            "sign": sign_metrics,
            "verify": verify_metrics
        }

        print(f"  KeyGen: {keygen_metrics['median_us']} µs (median) | {keygen_metrics['ops_per_sec']} ops/s")
        print(f"  Sign:   {sign_metrics['median_us']} µs (median) | {sign_metrics['ops_per_sec']} ops/s")
        print(f"  Verify: {verify_metrics['median_us']} µs (median) | {verify_metrics['ops_per_sec']} ops/s")
        print(f"  Sizes:  PK={sig.length_public_key}B, SK={sig.length_secret_key}B, SIG={sig.length_signature}B")

    return results


def main():
    print("======================================================================")
    print(" PQC SPACE SYSTEMS FAULT RESILIENCE RESEARCH - BASELINE BENCHMARKS")
    print(f" liboqs version: {get_liboqs_version()}")
    print(" Host: Apple M1 (arm64, 8 cores)")
    print("======================================================================")

    kem_results = run_kem_benchmarks(iterations=500)
    dsa_results = run_dsa_benchmarks(iterations=500)

    benchmark_data = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "liboqs_version": get_liboqs_version(),
            "cpu_architecture": "arm64",
            "iterations_per_op": 500
        },
        "ml_kem": kem_results,
        "ml_dsa": dsa_results
    }

    results_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../results"))
    os.makedirs(results_dir, exist_ok=True)
    output_path = os.path.join(results_dir, "baseline_benchmark_results.json")

    with open(output_path, "w") as f:
        json.dump(benchmark_data, f, indent=2)

    print(f"\n[+] Baseline benchmark results successfully saved to: {output_path}")


if __name__ == "__main__":
    main()
