"""
Publication-Quality Visualization of Level 1 Fault Injection Results.
Compares outcome distributions between ML-KEM-768 and ML-DSA-65.
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np

def generate_level1_plots():
    results_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../results/level1_fault_experiment_results.json"))
    if not os.path.exists(results_path):
        print("Results file not found.")
        return

    with open(results_path) as f:
        data = json.load(f)

    results_dir = os.path.dirname(results_path)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # 1. ML-KEM-768 Outcomes
    kem_data = data["ml_kem_768"]
    kem_campaigns = list(kem_data.keys())
    
    sdc_rates = [kem_data[c]["counts"]["SILENT_DATA_CORRUPTION"] / 10.0 for c in kem_campaigns]
    crash_rates = [kem_data[c]["counts"]["CRASH"] / 10.0 for c in kem_campaigns]
    correct_rates = [kem_data[c]["counts"]["CORRECT"] / 10.0 for c in kem_campaigns]

    x1 = np.arange(len(kem_campaigns))
    width = 0.55

    ax1.bar(x1, sdc_rates, width, label='Silent Data Corruption (SDC / Desync)', color='#d95f02')
    ax1.bar(x1, crash_rates, width, bottom=sdc_rates, label='Crash / Library Error', color='#7570b3')
    bottom_c = [s + cr for s, cr in zip(sdc_rates, crash_rates)]
    ax1.bar(x1, correct_rates, width, bottom=bottom_c, label='Correct (Masked Bit)', color='#1b9e77')

    ax1.set_title("ML-KEM-768: Level 1 Fault Outcomes (N=1,000 per test)", fontsize=12, fontweight='bold')
    ax1.set_ylabel("Proportion of Injected Faults (%)", fontsize=11)
    ax1.set_xticks(x1)
    ax1.set_xticklabels([c.replace("_", "\n") for c in kem_campaigns], fontsize=9)
    ax1.set_ylim(0, 105)
    ax1.legend(loc='lower left', fontsize=9)
    ax1.grid(True, linestyle="--", alpha=0.6)

    # 2. ML-DSA-65 Outcomes
    dsa_data = data["ml_dsa_65"]
    dsa_campaigns = list(dsa_data.keys())

    rej_rates = [dsa_data[c]["counts"]["EXPECTED_REJECTION"] / 10.0 for c in dsa_campaigns]
    dsa_sdc_rates = [dsa_data[c]["counts"]["SILENT_DATA_CORRUPTION"] / 10.0 for c in dsa_campaigns]

    x2 = np.arange(len(dsa_campaigns))
    ax2.bar(x2, rej_rates, width, label='Expected Rejection (Tamper Caught)', color='#2ca25f')
    ax2.bar(x2, dsa_sdc_rates, width, bottom=rej_rates, label='Silent Data Corruption (SDC)', color='#de2d26')

    ax2.set_title("ML-DSA-65: Level 1 Fault Outcomes (N=1,000 per test)", fontsize=12, fontweight='bold')
    ax2.set_ylabel("Proportion of Injected Faults (%)", fontsize=11)
    ax2.set_xticks(x2)
    ax2.set_xticklabels([c.replace("_", "\n") for c in dsa_campaigns], fontsize=9)
    ax2.set_ylim(0, 105)
    ax2.legend(loc='lower left', fontsize=9)
    ax2.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    out_path = os.path.join(results_dir, "level1_fault_distributions.png")
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"[+] Saved Level 1 fault distributions chart to: {out_path}")

if __name__ == "__main__":
    generate_level1_plots()
