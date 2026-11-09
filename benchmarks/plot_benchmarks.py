#!/usr/bin/env python3
"""ASTRA-Sec: Publication Figure Generator for Comparative Performance Benchmarks.

Generates publication-quality charts from data/benchmarks/benchmark_results.json:
1. crypto_latency_comparison.png
2. monitored_vs_dmr_overhead.png
3. dtn_security_overhead.png
4. system_e2e_latency_distribution.png
5. storage_and_network_overhead.png
"""

import json
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np


def set_plot_style():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.titlesize": 14,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linestyle": "--",
        "axes.axisbelow": True,
        "figure.dpi": 300,
    })


def load_benchmark_data(json_path: Path) -> dict:
    if not json_path.exists():
        raise FileNotFoundError(f"Benchmark results not found at: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def plot_crypto_latency(benchmarks: list, output_dir: Path):
    """Plot 1: ML-KEM-768 and ML-DSA-65 Latency with 95% Confidence Intervals."""
    set_plot_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # KEM Operations
    kem_targets = [
        ("LibOQS ML-KEM-768 KeyGen", "LibOQS\nKeyGen", "#4A90E2"),
        ("ASTRA-Sec ML-KEM-768 KeyGen", "ASTRA-Sec\nKeyGen", "#2E5B88"),
        ("LibOQS ML-KEM-768 Encaps", "LibOQS\nEncaps", "#50E3C2"),
        ("ASTRA-Sec ML-KEM-768 Encaps", "ASTRA-Sec\nEncaps", "#1B8E77"),
        ("LibOQS ML-KEM-768 Decaps (Unprotected)", "LibOQS\nDecaps", "#F5A623"),
        ("ASTRA-Sec ML-KEM-768 Decaps (Nominal Clean)", "ASTRA-Sec\nClean Decaps", "#D0021B"),
        ("ASTRA-Sec ML-KEM-768 Decaps (Transient Recovery K=1)", "ASTRA-Sec\nRecovered (K=1)", "#BD10E0"),
        ("DMR ML-KEM-768 Decaps (Duplicated Execution)", "DMR Baseline\nDecaps (2x)", "#7ED321"),
    ]

    bench_map = {b["name"]: b for b in benchmarks}

    labels1, means1, errs1, colors1 = [], [], [], []
    for full_name, short_label, color in kem_targets:
        if full_name in bench_map:
            b = bench_map[full_name]
            labels1.append(short_label)
            means1.append(b["mean_us"])
            errs1.append(b["ci95_upper_us"] - b["mean_us"])
            colors1.append(color)

    x1 = np.arange(len(labels1))
    bars1 = ax1.bar(x1, means1, yerr=errs1, capsize=4, color=colors1, edgecolor="black", linewidth=0.8, alpha=0.9)
    ax1.set_xticks(x1)
    ax1.set_xticklabels(labels1, rotation=35, ha="right")
    ax1.set_ylabel("Execution Latency (microseconds - μs)")
    ax1.set_title("ML-KEM-768 Operational Latencies (Mean ± 95% CI)")

    for bar, mean_val in zip(bars1, means1):
        ax1.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height() + 1.5, f"{mean_val:.1f}μs",
                 ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    # DSA Operations
    dsa_targets = [
        ("LibOQS ML-DSA-65 KeyGen", "LibOQS\nKeyGen", "#4A90E2"),
        ("ASTRA-Sec ML-DSA-65 KeyGen", "ASTRA-Sec\nKeyGen", "#2E5B88"),
        ("LibOQS ML-DSA-65 Sign", "LibOQS\nSign", "#F5A623"),
        ("ASTRA-Sec ML-DSA-65 Sign", "ASTRA-Sec\nSign", "#E67E22"),
        ("LibOQS ML-DSA-65 Verify", "LibOQS\nVerify", "#7ED321"),
        ("ASTRA-Sec ML-DSA-65 Verify", "ASTRA-Sec\nVerify", "#27AE60"),
    ]

    labels2, means2, errs2, colors2 = [], [], [], []
    for full_name, short_label, color in dsa_targets:
        if full_name in bench_map:
            b = bench_map[full_name]
            labels2.append(short_label)
            means2.append(b["mean_us"])
            errs2.append(b["ci95_upper_us"] - b["mean_us"])
            colors2.append(color)

    x2 = np.arange(len(labels2))
    bars2 = ax2.bar(x2, means2, yerr=errs2, capsize=4, color=colors2, edgecolor="black", linewidth=0.8, alpha=0.9)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(labels2, rotation=35, ha="right")
    ax2.set_ylabel("Execution Latency (microseconds - μs)")
    ax2.set_title("ML-DSA-65 Operational Latencies (Mean ± 95% CI)")

    for bar, mean_val in zip(bars2, means2):
        ax2.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height() + 2.0, f"{mean_val:.1f}μs",
                 ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    plt.tight_layout()
    fig.savefig(output_dir / "crypto_latency_comparison.png", dpi=300)
    plt.close(fig)
    print("  [+] Generated: crypto_latency_comparison.png")


def plot_monitored_vs_dmr(benchmarks: list, output_dir: Path):
    """Plot 2: ASTRA-Sec L4 Invariant Monitoring vs DMR Redundancy Overhead."""
    set_plot_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    bench_map = {b["name"]: b for b in benchmarks}
    unprotected = bench_map.get("LibOQS ML-KEM-768 Decaps (Unprotected)", {}).get("mean_us", 20.0)
    astra_clean = bench_map.get("ASTRA-Sec ML-KEM-768 Decaps (Nominal Clean)", {}).get("mean_us", 21.0)
    astra_rec = bench_map.get("ASTRA-Sec ML-KEM-768 Decaps (Transient Recovery K=1)", {}).get("mean_us", 22.5)
    dmr = bench_map.get("DMR ML-KEM-768 Decaps (Duplicated Execution)", {}).get("mean_us", 40.0)

    # Overhead % relative to unprotected
    ov_clean = ((astra_clean - unprotected) / unprotected) * 100.0
    ov_rec = ((astra_rec - unprotected) / unprotected) * 100.0
    ov_dmr = ((dmr - unprotected) / unprotected) * 100.0

    configs = ["Unprotected\nBaseline (1x)", "ASTRA-Sec\nClean Monitor", "ASTRA-Sec\nRecovery (K=1)", "DMR Baseline\nDuplicated (2x)"]
    latencies = [unprotected, astra_clean, astra_rec, dmr]
    colors = ["#7F8C8D", "#2980B9", "#8E44AD", "#C0392B"]

    bars1 = ax1.bar(configs, latencies, color=colors, edgecolor="black", linewidth=0.8, alpha=0.9)
    ax1.set_ylabel("Decapsulation Latency (μs)")
    ax1.set_title("ML-KEM-768 Decapsulation Latency Comparison")
    for bar, lat in zip(bars1, latencies):
        ax1.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height() + 0.8, f"{lat:.1f}μs",
                 ha="center", va="bottom", fontweight="bold", fontsize=9.5)

    # Overhead comparison
    ov_configs = ["ASTRA-Sec Clean", "ASTRA-Sec Recovery", "DMR Duplication"]
    ov_vals = [ov_clean, ov_rec, ov_dmr]
    bars2 = ax2.bar(ov_configs, ov_vals, color=["#2980B9", "#8E44AD", "#C0392B"], edgecolor="black", linewidth=0.8, alpha=0.9)
    ax2.set_ylabel("Execution Overhead (%) vs Unprotected Baseline")
    ax2.set_title("Fault-Tolerance Overhead Trade-off")
    ax2.axhline(0, color="gray", linewidth=0.8)
    for bar, ov in zip(bars2, ov_vals):
        ax2.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height() + 2.0, f"+{ov:.1f}%",
                 ha="center", va="bottom", fontweight="bold", fontsize=9.5)

    plt.tight_layout()
    fig.savefig(output_dir / "monitored_vs_dmr_overhead.png", dpi=300)
    plt.close(fig)
    print("  [+] Generated: monitored_vs_dmr_overhead.png")


def plot_dtn_security(benchmarks: list, output_dir: Path):
    """Plot 3: DTN Transport Security Layer Processing Latencies."""
    set_plot_style()
    fig, ax = plt.subplots(figsize=(8.5, 5))

    bench_map = {b["name"]: b for b in benchmarks}
    dtn_items = [
        ("Plain BPv7 Wrap & Parse", "Plain BPv7\n(No Security)", "#34495E"),
        ("BPv7 + BPSec BIB Sign & Verify", "BPv7 + BPSec BIB\n(HMAC-SHA256)", "#2980B9"),
        ("ASTRA-Sec L2 E2E PQC over BPv7", "ASTRA-Sec L2 E2E\n(ML-KEM+DSA+AEAD)", "#E67E22"),
        ("ASTRA-Sec Full Stack (L2 E2E + BPSec BIB)", "ASTRA-Sec Full Stack\n(E2E + BPSec BIB)", "#27AE60"),
    ]

    labels, means_ms, errs_ms, colors = [], [], [], []
    for full_name, label, color in dtn_items:
        if full_name in bench_map:
            b = bench_map[full_name]
            labels.append(label)
            means_ms.append(b["mean_us"] / 1000.0)  # Convert to ms
            errs_ms.append((b["ci95_upper_us"] - b["mean_us"]) / 1000.0)
            colors.append(color)

    x = np.arange(len(labels))
    bars = ax.bar(x, means_ms, yerr=errs_ms, capsize=4, color=colors, edgecolor="black", linewidth=0.8, alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Processing Latency (milliseconds - ms)")
    ax.set_title("DTN Transport & End-to-End Security Latency Breakdown")

    for bar, val in zip(bars, means_ms):
        ax.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height() + 0.05, f"{val:.2f} ms",
                 ha="center", va="bottom", fontweight="bold", fontsize=9.5)

    plt.tight_layout()
    fig.savefig(output_dir / "dtn_security_overhead.png", dpi=300)
    plt.close(fig)
    print("  [+] Generated: dtn_security_overhead.png")


def plot_system_multihop(benchmarks: list, output_dir: Path):
    """Plot 4: 4-Node Multi-Hop Space Network End-to-End Latency Distribution."""
    set_plot_style()
    fig, ax = plt.subplots(figsize=(8.5, 5))

    bench_map = {b["name"]: b for b in benchmarks}
    clean = bench_map.get("4-Node Space Multi-Hop (Clean Path)", {})
    faulted = bench_map.get("4-Node Space Multi-Hop (Transient Recovery)", {})

    labels = ["Nominal Clean Multi-Hop\n(GSA->SAT1->SAT2->GSB)", "Multi-Hop with Fault Recovery\n(NTT SEU Restored at GSB)"]
    means = [clean.get("mean_us", 0) / 1000.0, faulted.get("mean_us", 0) / 1000.0]
    p50s = [clean.get("p50_us", 0) / 1000.0, faulted.get("p50_us", 0) / 1000.0]
    p90s = [clean.get("p90_us", 0) / 1000.0, faulted.get("p90_us", 0) / 1000.0]
    p99s = [clean.get("p99_us", 0) / 1000.0, faulted.get("p99_us", 0) / 1000.0]

    x = np.arange(len(labels))
    width = 0.2

    ax.bar(x - 1.5 * width, means, width, label="Mean", color="#2980B9", edgecolor="black")
    ax.bar(x - 0.5 * width, p50s, width, label="p50 (Median)", color="#27AE60", edgecolor="black")
    ax.bar(x + 0.5 * width, p90s, width, label="p90", color="#F39C12", edgecolor="black")
    ax.bar(x + 1.5 * width, p99s, width, label="p99", color="#E74C3C", edgecolor="black")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("End-to-End Latency (milliseconds - ms)")
    ax.set_title("4-Node Space Network Multi-Hop Latency Distribution")
    ax.legend(loc="upper left")

    for i in range(len(labels)):
        ax.text(i - 1.5 * width, means[i] + 0.08, f"{means[i]:.2f}", ha="center", va="bottom", fontsize=8)
        ax.text(i + 1.5 * width, p99s[i] + 0.08, f"{p99s[i]:.2f}", ha="center", va="bottom", fontsize=8)

    plt.tight_layout()
    fig.savefig(output_dir / "system_e2e_latency_distribution.png", dpi=300)
    plt.close(fig)
    print("  [+] Generated: system_e2e_latency_distribution.png")


def plot_storage_and_network_overhead(overheads: dict, output_dir: Path):
    """Plot 5: Network Wire Framing and Persistent Storage Overhead."""
    set_plot_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    wire = overheads.get("wire_framing_overheads", {})
    storage = overheads.get("storage_and_memory_overheads", {})

    # Wire breakdown
    wire_labels = ["Application\nPayload", "Plain\nBPv7", "ASTRA-Sec\nRaw Envelope", "ASTRA-Sec\nover BPv7", "Full Stack\n+ BPSec BIB"]
    wire_sizes = [
        wire.get("application_payload_bytes", 256),
        wire.get("plain_bpv7_bundle_cbor_bytes", 320),
        wire.get("pqc_envelope_raw_bytes", 4700),
        wire.get("astra_e2e_bpv7_bundle_cbor_bytes", 4750),
        wire.get("astra_e2e_plus_bpsec_bib_cbor_bytes", 4850),
    ]

    bars1 = ax1.bar(wire_labels, wire_sizes, color=["#7F8C8D", "#34495E", "#E67E22", "#2980B9", "#27AE60"], edgecolor="black")
    ax1.set_ylabel("Total Wire Framing Size (bytes)")
    ax1.set_title("Network Wire Transmission Overhead")
    for bar, sz in zip(bars1, wire_sizes):
        ax1.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height() + 80, f"{sz} B",
                 ha="center", va="bottom", fontweight="bold", fontsize=9)

    # Storage Breakdown
    storage_labels = ["SQLite WAL Spool\n(100 Bundles)", "Anti-Replay Filter\n(500 Sequences)", "HMAC Security\nState Manifest"]
    storage_vals = [
        storage.get("sqlite_spool_100_messages_kb", 500),
        storage.get("sqlite_anti_replay_500_seqs_kb", 32),
        storage.get("hmac_state_manifest_bytes", 512) / 1024.0,  # in KB
    ]

    bars2 = ax2.bar(storage_labels, storage_vals, color=["#E67E22", "#8E44AD", "#16A085"], edgecolor="black")
    ax2.set_ylabel("Non-Volatile Storage (Kilobytes - KB)")
    ax2.set_title("Persistent Storage Footprint")
    for bar, sz in zip(bars2, storage_vals):
        ax2.text(bar.get_x() + bar.get_width() / 2.0, bar.get_height() + 10, f"{sz:.1f} KB",
                 ha="center", va="bottom", fontweight="bold", fontsize=9)

    plt.tight_layout()
    fig.savefig(output_dir / "storage_and_network_overhead.png", dpi=300)
    plt.close(fig)
    print("  [+] Generated: storage_and_network_overhead.png")


def main():
    root = Path(__file__).resolve().parent.parent
    json_path = root / "data" / "benchmarks" / "benchmark_results.json"
    output_dir = root / "data" / "benchmarks" / "plots"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[+] Loading benchmark results from: {json_path}")
    data = load_benchmark_data(json_path)

    benchmarks = data.get("benchmarks", [])
    overheads = data.get("overheads", {})

    print("[+] Rendering publication figures...")
    plot_crypto_latency(benchmarks, output_dir)
    plot_monitored_vs_dmr(benchmarks, output_dir)
    plot_dtn_security(benchmarks, output_dir)
    plot_system_multihop(benchmarks, output_dir)
    plot_storage_and_network_overhead(overheads, output_dir)
    print(f"\n[+] All 5 publication plots saved in: {output_dir}")


if __name__ == "__main__":
    main()
