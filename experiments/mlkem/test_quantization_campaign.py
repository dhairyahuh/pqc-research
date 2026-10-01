#!/usr/bin/env python3
"""
Quantization Absorption and Boundary Tolerance Campaign
Validates Phase 1 mathematical model:
  T_worst(d, q) = 0
  T(x, d, q) = min(M^+(x), M^-(x))
where Compress_d(x) = round( (2^d / q) * x ) mod 2^d
"""

import json
import math
import os
import sys

Q = 3329

def compress(x, d):
    # FIPS 203: Compress_d(x) = round((2^d / q) * x) mod 2^d
    # in integer arithmetic: ( (x << d) + (q // 2) ) // q mod (1 << d)
    val = (((x % Q) << d) + (Q // 2)) // Q
    return val % (1 << d)

def decompress(y, d):
    # FIPS 203: Decompress_d(y) = round((q / 2^d) * y)
    val = (y * Q + (1 << (d - 1))) >> d
    return val % Q

def compute_local_slack(x, d):
    """
    Computes M^+(x) and M^-(x): the positive and negative additive perturbations
    required to change Compress_d(x).
    """
    base_comp = compress(x, d)
    # Find M^+
    m_plus = 1
    while compress(x + m_plus, d) == base_comp and m_plus < Q:
        m_plus += 1
    # Find M^-
    m_minus = 1
    while compress(x - m_minus, d) == base_comp and m_minus < Q:
        m_minus += 1
    return m_plus, m_minus, min(m_plus, m_minus)

def run_quantization_campaign():
    print("=" * 70)
    print("RUNNING QUANTIZATION ABSORPTION & SLACK EXPERIMENT (PHASE 2 / RQ2.4, RQ2.8)")
    print("=" * 70)

    d_values = [4, 5, 10, 11]
    deltas = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    
    results = {
        "metadata": {
            "experiment": "EXP-QUANT-ABSORPTION-08",
            "q": Q,
            "d_values": d_values,
            "deltas": deltas,
            "num_coefficients_evaluated": Q
        },
        "worst_case_tolerance": {},
        "distance_distribution": {},
        "absorption_by_delta": {},
        "boundary_conditioned_absorption": {}
    }

    for d in d_values:
        print(f"\n--- Analyzing d = {d} (2^d = {1 << d}, bin width ~ {Q / (1 << d):.2f}) ---")
        min_slack = 999999
        slack_map = {}
        dist_groups = {}
        
        # Precompute slack once for each x in Z_q
        for x in range(Q):
            m_p, m_m, local_t = compute_local_slack(x, d)
            slack_map[x] = (m_p, m_m, local_t)
            if local_t < min_slack:
                min_slack = local_t
            dist_groups.setdefault(local_t, []).append(x)
            
        print(f"Observed worst-case local tolerance T_worst(d={d}): {min_slack}")
        results["worst_case_tolerance"][str(d)] = min_slack

        # Absorption probability vs delta
        abs_prob = {}
        for delta in deltas:
            absorbed_count = 0
            decomp_exact_count = 0
            for x in range(Q):
                c_orig = compress(x, d)
                c_fault = compress((x + delta) % Q, d)
                if c_orig == c_fault:
                    absorbed_count += 1
                    if decompress(c_orig, d) == decompress(c_fault, d):
                        decomp_exact_count += 1
            prob = absorbed_count / Q
            abs_prob[str(delta)] = {
                "absorption_probability": prob,
                "absorbed_count": absorbed_count,
                "total": Q
            }
            print(f"  Delta = {delta:3d} | Absorbed: {absorbed_count:4d}/{Q} ({prob*100:6.2f}%)")
        results["absorption_by_delta"][str(d)] = abs_prob

        # Absorption conditioned on distance to boundary D(x) = min(M+, M-)
        cond_abs = {}
        for delta in [1, 2, 4, 8]:
            cond_abs[str(delta)] = {}
            for d_dist, xs in sorted(dist_groups.items()):
                absorbed = sum(1 for x in xs if compress(x, d) == compress(x + delta, d))
                cond_abs[str(delta)][str(d_dist)] = {
                    "total_xs": len(xs),
                    "absorbed": absorbed,
                    "prob": absorbed / len(xs)
                }
        results["boundary_conditioned_absorption"][str(d)] = cond_abs

    # Write output
    out_dir = "results/phase2/raw"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "quantization_absorption.json")
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] Raw results saved to: {out_file}")

    # Generate CSV summary
    summary_dir = "results/phase2/processed"
    os.makedirs(summary_dir, exist_ok=True)
    csv_file = os.path.join(summary_dir, "quantization_absorption_summary.csv")
    with open(csv_file, "w") as f:
        f.write("d,delta,absorbed_count,total,absorption_rate\n")
        for d in d_values:
            for delta in deltas:
                dat = results["absorption_by_delta"][str(d)][str(delta)]
                f.write(f"{d},{delta},{dat['absorbed_count']},{dat['total']},{dat['absorption_probability']:.6f}\n")
    print(f"[+] Summary CSV saved to: {csv_file}")
    print("=" * 70)

if __name__ == "__main__":
    run_quantization_campaign()
