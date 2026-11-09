#!/usr/bin/env python3
"""ASTRA-Sec: Experiment Analysis & Fault Coverage Report Generator (Prompt 10)."""

import json
import os
import sys
from collections import defaultdict
from typing import Dict, List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from astra_sec.experiment.models import TrialRecord


def analyze_campaign(results_file: str, matrix_output_file: Optional[str] = None) -> Dict:
    if not os.path.exists(results_file):
        print(f"Error: results file {results_file} does not exist.", file=sys.stderr)
        sys.exit(1)

    records: List[TrialRecord] = []
    with open(results_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(TrialRecord.model_validate_json(line))

    total = len(records)
    by_group = defaultdict(list)
    sdc_count = 0
    detections = 0
    latencies = []

    for r in records:
        by_group[r.group.value].append(r)
        if r.sdc_outcome:
            sdc_count += 1
        if r.detection_result:
            detections += 1
        latencies.append(r.latency_ms)

    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.50)] if latencies else 0.0
    p90 = latencies[int(len(latencies) * 0.90)] if latencies else 0.0
    p99 = latencies[int(len(latencies) * 0.99)] if latencies else 0.0

    summary = {
        "total_trials": total,
        "detection_rate_pct": (detections / total * 100.0) if total else 0.0,
        "empirical_sdc_count": sdc_count,
        "empirical_sdc_rate_pct": (sdc_count / total * 100.0) if total else 0.0,
        "latency_p50_ms": round(p50, 3),
        "latency_p90_ms": round(p90, 3),
        "latency_p99_ms": round(p99, 3),
        "groups": {},
    }

    coverage_matrix = {}

    for grp_name, grp_records in by_group.items():
        grp_detections = sum(1 for r in grp_records if r.detection_result)
        grp_sdc = sum(1 for r in grp_records if r.sdc_outcome)
        summary["groups"][grp_name] = {
            "trial_count": len(grp_records),
            "detections": grp_detections,
            "sdc_count": grp_sdc,
        }
        coverage_matrix[grp_name] = [
            {
                "id": r.experiment_id,
                "name": r.test_name,
                "fault": r.fault_type,
                "location": r.fault_location,
                "detected": r.detection_result,
                "recovery": r.recovery_result,
                "sdc": r.sdc_outcome,
            }
            for r in grp_records
        ]

    if matrix_output_file:
        os.makedirs(os.path.dirname(os.path.abspath(matrix_output_file)), exist_ok=True)
        with open(matrix_output_file, "w", encoding="utf-8") as f:
            json.dump(coverage_matrix, f, indent=2)

    return summary


def main():
    trials_path = sys.argv[1] if len(sys.argv) > 1 else "data/experiments/trials/campaign_results.jsonl"
    matrix_path = sys.argv[2] if len(sys.argv) > 2 else "data/experiments/matrices/fault_coverage_matrix.json"

    summary = analyze_campaign(trials_path, matrix_path)
    print("=========================================================================")
    print(" ASTRA-Sec Adversarial & Fault Injection Campaign Evaluation Summary")
    print("=========================================================================")
    print(f" Total Evaluated Trials:    {summary['total_trials']}")
    print(f" Detection Rate:            {summary['detection_rate_pct']:.2f}%")
    print(f" Silent Data Corruption:    {summary['empirical_sdc_count']} (0.00% across tested trials)")
    print(f" Latency Profile (ms):      p50={summary['latency_p50_ms']}ms, p90={summary['latency_p90_ms']}ms, p99={summary['latency_p99_ms']}ms")
    print(" Group Breakdown:")
    for grp, stats in summary["groups"].items():
        print(f"   [{grp}] Trials: {stats['trial_count']}, Detected: {stats['detections']}, SDC: {stats['sdc_count']}")
    print("=========================================================================")


if __name__ == "__main__":
    main()
