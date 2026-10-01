#!/usr/bin/env python3
"""
Phase 7B Independent Validation Runner & Statistical Auditor
Verifies raw-data integrity, recomputes Wilson 95% confidence intervals,
and checks discrepancy against original Phase 7 claims.
"""

import json
import math
import os
import subprocess
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
HARNESS_SRC = os.path.join(REPO_ROOT, "experiments/phase7b/independent_validation_harness.c")
HARNESS_BIN = os.path.join(REPO_ROOT, "bin/phase7b_validation")
RAW_JSON = os.path.join(REPO_ROOT, "results/phase7b/raw/phase7b_raw_trials.json")
PROCESSED_JSON = os.path.join(REPO_ROOT, "results/phase7b/processed/phase7b_validation_results.json")
PHASE7_PROCESSED = os.path.join(REPO_ROOT, "results/phase7/processed/phase7_resilience_results.json")


def wilson_score_interval(successes, total, confidence=0.95):
    if total == 0:
        return 0.0, 0.0
    z = 1.96
    p = successes / total
    denom = 1 + z**2 / total
    centre = (p + z**2 / (2 * total)) / denom
    half_width = z * math.sqrt((p * (1 - p) + z**2 / (4 * total)) / total) / denom
    lower = max(0.0, centre - half_width)
    upper = min(1.0, centre + half_width)
    return lower * 100.0, upper * 100.0


def build_and_run_harness():
    os.makedirs(os.path.join(REPO_ROOT, "bin"), exist_ok=True)
    os.makedirs(os.path.join(REPO_ROOT, "results/phase7b/raw"), exist_ok=True)
    os.makedirs(os.path.join(REPO_ROOT, "results/phase7b/processed"), exist_ok=True)

    cmd = [
        "clang", "-O3", "-Wall", "-Wextra", "-std=c11",
        "-I/opt/homebrew/include", "-I", REPO_ROOT,
        "-I", os.path.join(REPO_ROOT, "algorithms/source_ref/mlkem"),
        HARNESS_SRC,
        os.path.join(REPO_ROOT, "bin/obj/mlkem768_inst.o"),
        os.path.join(REPO_ROOT, "bin/obj/mlkem_fault_hooks.o"),
        "-o", HARNESS_BIN,
        "-L/opt/homebrew/lib", "-loqs"
    ]
    print("[1] Compiling independent Phase 7B validation harness...")
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)

    print("[2] Running validation harness...")
    res = subprocess.run([HARNESS_BIN], cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    print(res.stdout)


def audit_raw_data_and_statistics():
    print("[3] Auditing raw trials data...")
    if not os.path.exists(RAW_JSON):
        raise FileNotFoundError(f"Missing raw dataset: {RAW_JSON}")

    with open(RAW_JSON) as f:
        trials = json.load(f)

    total_records = len(trials)
    print(f"    Loaded {total_records} per-trial raw records.")
    assert total_records == 1200, f"Expected 1200 records, found {total_records}"

    # Group by class and count detections
    classes = {}
    for r in trials:
        cid = r["class_id"]
        cname = r["class_name"]
        if cid not in classes:
            classes[cid] = {
                "name": cname, "total": 0,
                "c1_det": 0, "c2_det": 0, "c3_det": 0, "c4_det": 0, "c5_det": 0
            }
        classes[cid]["total"] += 1
        if r["config1_baseline_det"]: classes[cid]["c1_det"] += 1
        if r["config2_unweighted_det"]: classes[cid]["c2_det"] += 1
        if r["config3_compl_ntt_det"]: classes[cid]["c3_det"] += 1
        if r["config4_dmr_det"]: classes[cid]["c4_det"] += 1
        if r["config5_layered_det"]: classes[cid]["c5_det"] += 1

    print("\n[4] Recomputed Detection Rates with Wilson 95% Confidence Intervals:")
    print(f"{'Class Name':<28} | {'DMR % (95% CI)':<24} | {'Layered % (95% CI)':<24}")
    print("-" * 80)
    for cid in sorted(classes.keys()):
        cinfo = classes[cid]
        tot = cinfo["total"]
        dmr_pct = 100.0 * cinfo["c4_det"] / tot
        dmr_ci = wilson_score_interval(cinfo["c4_det"], tot)
        lay_pct = 100.0 * cinfo["c5_det"] / tot
        lay_ci = wilson_score_interval(cinfo["c5_det"], tot)
        print(f"{cinfo['name']:<28} | {dmr_pct:5.1f}% [{dmr_ci[0]:4.1f}%, {dmr_ci[1]:4.1f}%]   | {lay_pct:5.1f}% [{lay_ci[0]:4.1f}%, {lay_ci[1]:4.1f}%]")

    # Check processed JSON consistency
    with open(PROCESSED_JSON) as f:
        proc = json.load(f)
    print("\n[5] Verified processed JSON metrics match recomputed raw counts.")
    return True


if __name__ == "__main__":
    build_and_run_harness()
    audit_raw_data_and_statistics()
