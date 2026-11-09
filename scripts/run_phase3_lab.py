#!/usr/bin/env python3
"""ASTRA-Sec Phase 3: Experimental Laboratory Command-Line Interface.

Provides a unified interface to validate configurations, execute pilots,
run experimental groups, and analyze raw measurement distributions.

Usage:
    python3 scripts/run_phase3_lab.py --list
    python3 scripts/run_phase3_lab.py --validate
    python3 scripts/run_phase3_lab.py --pilot
    python3 scripts/run_phase3_lab.py --run research/phase3_experimental_lab/configs/group_a_baseline_non_pqc.json
    python3 scripts/run_phase3_lab.py --group A
    python3 scripts/run_phase3_lab.py --analyze <manifest_file>
"""

import argparse
import glob
import json
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from research.phase3_experimental_lab.harness.config import ExperimentConfig
from research.phase3_experimental_lab.harness.orchestrator import ExperimentOrchestrator


CONFIGS_DIR = os.path.abspath("research/phase3_experimental_lab/configs")


def list_configs():
    print("=" * 80)
    print("ASTRA-Sec Phase 3: Available Experiment Configurations")
    print("=" * 80)
    files = sorted(glob.glob(os.path.join(CONFIGS_DIR, "*.json")))
    if not files:
        print("No configuration files found in", CONFIGS_DIR)
        return

    for f in files:
        try:
            cfg = ExperimentConfig.load_from_file(f)
            print(f"[{cfg.group}] {cfg.scenario_id:<20} | {cfg.experiment_name:<40} | ({os.path.basename(f)})")
        except Exception as e:
            print(f"[ERR] Failed to parse {os.path.basename(f)}: {e}")


def validate_configs():
    print("=" * 80)
    print("ASTRA-Sec Phase 3: Validating Experiment Configurations")
    print("=" * 80)
    files = sorted(glob.glob(os.path.join(CONFIGS_DIR, "*.json")))
    all_ok = True
    for f in files:
        try:
            cfg = ExperimentConfig.load_from_file(f)
            h = cfg.compute_config_hash()
            print(f"[VALID] {os.path.basename(f):<35} (Scenario: {cfg.scenario_id}, Hash: {h[:12]})")
        except Exception as e:
            print(f"[INVALID] {os.path.basename(f)}: {e}")
            all_ok = False
    if all_ok:
        print(">>> ALL CONFIGURATIONS VALID [PASS] <<<")
    return all_ok


def run_experiment(config_path: str):
    print("=" * 80)
    print(f"ASTRA-Sec Phase 3: Executing Experiment from {os.path.basename(config_path)}")
    print("=" * 80)
    cfg = ExperimentConfig.load_from_file(config_path)
    orchestrator = ExperimentOrchestrator(cfg)
    result = orchestrator.run()

    print("\n--- EXPERIMENT EXECUTION RESULTS ---")
    print(f"Experiment ID:     {result['experiment_id']}")
    print(f"Status:            {result['status']}")
    print(f"Raw Output JSONL:  {result['raw_output_path']}")
    print(f"Manifest JSON:     {result['manifest_path']}")

    summary = result["summary"]
    print(f"Total Attempted:   {summary['total_attempted']}")
    print(f"Delivered Count:   {summary['delivered_count']} ({summary['delivery_rate_pct']}%)")
    print(f"Throughput:        {summary['throughput_msg_per_sec']} msg/sec")
    print(f"Total Duration:    {summary['total_duration_seconds']} s")

    dist = summary["latency_distribution_us"]
    print(f"Latency P50:       {dist['median']} us ({dist['median'] / 1000.0:.2f} ms)")
    print(f"Latency P95:       {dist['p95']} us ({dist['p95'] / 1000.0:.2f} ms)")
    print(f"Latency P99:       {dist['p99']} us ({dist['p99'] / 1000.0:.2f} ms)")
    print(f"Mean ± Std:        {dist['mean']} ± {dist['std']} us")
    print(f"99% Conf Interval: [{dist['ci_lower']}, {dist['ci_upper']}] us")

    res = summary["resource_utilization"]
    print(f"Mean CPU:          {res.get('mean_cpu_percent', 0.0)}%")
    print(f"Peak RSS Memory:   {res.get('peak_rss_bytes', 0) / (1024 * 1024):.2f} MB")
    print("=" * 80)
    return result["status"] == "COMPLETED"


def run_group(group_id: str):
    files = sorted(glob.glob(os.path.join(CONFIGS_DIR, "*.json")))
    matching = []
    for f in files:
        try:
            cfg = ExperimentConfig.load_from_file(f)
            if cfg.group.upper() == group_id.upper():
                matching.append(f)
        except Exception:
            pass

    if not matching:
        print(f"No experiment configurations found for group '{group_id}'.")
        return False

    print(f"Executing {len(matching)} experiments for Group {group_id.upper()}...")
    success = True
    for f in matching:
        ok = run_experiment(f)
        if not ok:
            success = False
    return success


def analyze_manifest(manifest_path: str):
    if not os.path.exists(manifest_path):
        print("Manifest not found:", manifest_path)
        return False
    with open(manifest_path, "r", encoding="utf-8") as f:
        m = json.load(f)
    print("=" * 80)
    print(f"MANIFEST ANALYSIS: {m['experiment_id']}")
    print("=" * 80)
    print(f"Scenario ID:    {m['configuration']['scenario_id']}")
    print(f"Baseline:       {m['configuration']['baseline']}")
    print(f"Git Commit:     {m['environment']['git_commit'][:8]} (Branch: {m['environment']['git_branch']})")
    print(f"Delivery Rate:  {m['summary_statistics']['delivery_rate_pct']}%")
    print(f"Throughput:     {m['summary_statistics']['throughput_msg_per_sec']} msg/sec")
    dist = m['summary_statistics']['latency_distribution_us']
    print(f"Latency P50:    {dist['median']} us")
    print(f"Latency P95:    {dist['p95']} us")
    print(f"Latency P99:    {dist['p99']} us")
    return True


def main():
    parser = argparse.ArgumentParser(description="ASTRA-Sec Phase 3 Experimental Lab Runner")
    parser.add_argument("--list", action="store_true", help="List all available experiment configurations")
    parser.add_argument("--validate", action="store_true", help="Validate all experiment configurations")
    parser.add_argument("--pilot", action="store_true", help="Execute the baseline validation pilot")
    parser.add_argument("--run", type=str, help="Path to experiment configuration JSON file to run")
    parser.add_argument("--group", type=str, help="Experiment group identifier to run (e.g., A, B, D, G)")
    parser.add_argument("--analyze", type=str, help="Path to manifest JSON file to inspect")

    args = parser.parse_args()

    if args.list:
        list_configs()
    elif args.validate:
        ok = validate_configs()
        sys.exit(0 if ok else 1)
    elif args.pilot:
        pilot_path = os.path.join(CONFIGS_DIR, "pilot.json")
        ok = run_experiment(pilot_path)
        sys.exit(0 if ok else 1)
    elif args.run:
        ok = run_experiment(args.run)
        sys.exit(0 if ok else 1)
    elif args.group:
        ok = run_group(args.group)
        sys.exit(0 if ok else 1)
    elif args.analyze:
        ok = analyze_manifest(args.analyze)
        sys.exit(0 if ok else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
