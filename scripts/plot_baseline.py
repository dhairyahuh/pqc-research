"""
Plotting script for baseline PQC benchmark latency and memory footprint.
Generates publication-quality charts for research analysis.
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np

def generate_plots():
    results_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../results/baseline_benchmark_results.json"))
    if not os.path.exists(results_path):
        print(f"Error: {results_path} does not exist.")
        return

    with open(results_path) as f:
        data = json.load(f)

    results_dir = os.path.dirname(results_path)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # 1. Latency Bar Chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # ML-KEM Latencies
    kem_algs = list(data["ml_kem"].keys())
    keygen_kem = [data["ml_kem"][alg]["keygen"]["median_us"] for alg in kem_algs]
    encaps_kem = [data["ml_kem"][alg]["encaps"]["median_us"] for alg in kem_algs]
    decaps_kem = [data["ml_kem"][alg]["decaps"]["median_us"] for alg in kem_algs]

    x = np.arange(len(kem_algs))
    width = 0.25

    ax1.bar(x - width, keygen_kem, width, label='KeyGen', color='#2b5c8f')
    ax1.bar(x, encaps_kem, width, label='Encaps', color='#4682b4')
    ax1.bar(x + width, decaps_kem, width, label='Decaps', color='#70a1d7')

    ax1.set_title("ML-KEM (FIPS 203) Baseline Latency", fontsize=12, fontweight='bold')
    ax1.set_ylabel("Execution Time (µs)", fontsize=11)
    ax1.set_xticks(x)
    ax1.set_xticklabels(kem_algs, fontsize=10)
    ax1.legend()
    ax1.grid(True, linestyle="--", alpha=0.6)

    # ML-DSA Latencies
    dsa_algs = list(data["ml_dsa"].keys())
    keygen_dsa = [data["ml_dsa"][alg]["keygen"]["median_us"] for alg in dsa_algs]
    sign_dsa = [data["ml_dsa"][alg]["sign"]["median_us"] for alg in dsa_algs]
    verify_dsa = [data["ml_dsa"][alg]["verify"]["median_us"] for alg in dsa_algs]

    x2 = np.arange(len(dsa_algs))
    ax2.bar(x2 - width, keygen_dsa, width, label='KeyGen', color='#a83232')
    ax2.bar(x2, sign_dsa, width, label='Sign', color='#e05d5d')
    ax2.bar(x2 + width, verify_dsa, width, label='Verify', color='#f39c9c')

    ax2.set_title("ML-DSA (FIPS 204) Baseline Latency", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Execution Time (µs)", fontsize=11)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(dsa_algs, fontsize=10)
    ax2.legend()
    ax2.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    latency_chart_path = os.path.join(results_dir, "baseline_latency.png")
    plt.savefig(latency_chart_path, dpi=200)
    plt.close()
    print(f"[+] Saved baseline latency plot to: {latency_chart_path}")

    # 2. Cryptographic Object Sizes
    fig, (ax3, ax4) = plt.subplots(1, 2, figsize=(14, 5))

    pk_kem = [data["ml_kem"][alg]["object_sizes"]["public_key_bytes"] for alg in kem_algs]
    sk_kem = [data["ml_kem"][alg]["object_sizes"]["secret_key_bytes"] for alg in kem_algs]
    ct_kem = [data["ml_kem"][alg]["object_sizes"]["ciphertext_bytes"] for alg in kem_algs]

    ax3.bar(x - width, pk_kem, width, label='Public Key', color='#1b7837')
    ax3.bar(x, sk_kem, width, label='Secret Key', color='#7fbf7b')
    ax3.bar(x + width, ct_kem, width, label='Ciphertext', color='#d9f0d3')

    ax3.set_title("ML-KEM Cryptographic Object Sizes", fontsize=12, fontweight='bold')
    ax3.set_ylabel("Size (Bytes)", fontsize=11)
    ax3.set_xticks(x)
    ax3.set_xticklabels(kem_algs, fontsize=10)
    ax3.legend()
    ax3.grid(True, linestyle="--", alpha=0.6)

    pk_dsa = [data["ml_dsa"][alg]["object_sizes"]["public_key_bytes"] for alg in dsa_algs]
    sk_dsa = [data["ml_dsa"][alg]["object_sizes"]["secret_key_bytes"] for alg in dsa_algs]
    sig_dsa = [data["ml_dsa"][alg]["object_sizes"]["signature_bytes"] for alg in dsa_algs]

    ax4.bar(x2 - width, pk_dsa, width, label='Public Key', color='#762a83')
    ax4.bar(x2, sk_dsa, width, label='Secret Key', color='#af8dc3')
    ax4.bar(x2 + width, sig_dsa, width, label='Signature', color='#e7d4e8')

    ax4.set_title("ML-DSA Cryptographic Object Sizes", fontsize=12, fontweight='bold')
    ax4.set_ylabel("Size (Bytes)", fontsize=11)
    ax4.set_xticks(x2)
    ax4.set_xticklabels(dsa_algs, fontsize=10)
    ax4.legend()
    ax4.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    sizes_chart_path = os.path.join(results_dir, "baseline_sizes.png")
    plt.savefig(sizes_chart_path, dpi=200)
    plt.close()
    print(f"[+] Saved baseline sizes plot to: {sizes_chart_path}")

if __name__ == "__main__":
    generate_plots()
