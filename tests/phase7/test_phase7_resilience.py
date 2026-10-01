#!/usr/bin/env python3
"""
Phase 7 Automated Test Suite: Layered Fault Resilience Verification
Validates reproducibility, data consistency, and mathematical bounds for ML-KEM-768.
"""

import json
import os
import subprocess
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
PROCESSED_JSON = os.path.join(REPO_ROOT, "results/phase7/processed/phase7_resilience_results.json")
RAW_JSON = os.path.join(REPO_ROOT, "results/phase7/raw/phase7_raw_trials.json")
HARNESS_BIN = os.path.join(REPO_ROOT, "bin/phase7_layered")


class TestPhase7Resilience(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Build and run harness if binary doesn't exist
        if not os.path.exists(HARNESS_BIN):
            subprocess.run(["make", "phase7"], cwd=REPO_ROOT, check=True)
        if not os.path.exists(PROCESSED_JSON):
            subprocess.run([HARNESS_BIN], cwd=REPO_ROOT, check=True)

    def test_harness_binary_execution(self):
        """Verify phase 7 native harness builds and executes successfully."""
        res = subprocess.run([HARNESS_BIN], cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Harness failed with stderr: {res.stderr}")
        self.assertIn("PHASE 7 EXPERIMENTAL CAMPAIGN COMPLETED", res.stdout)

    def test_results_json_schema(self):
        """Verify processed JSON schema matches Phase 7 requirements."""
        self.assertTrue(os.path.exists(PROCESSED_JSON), "Processed JSON results missing")
        with open(PROCESSED_JSON) as f:
            data = json.load(f)
        
        self.assertEqual(data.get("phase"), 7)
        self.assertIn("benchmarks", data)
        self.assertIn("fault_coverage", data)
        
        bench = data["benchmarks"]
        self.assertIn("config1_baseline_us", bench)
        self.assertIn("config4_duplicate_dmr_us", bench)
        self.assertIn("config5_layered_architecture_us", bench)

    def test_overhead_bounds(self):
        """Verify latency bounds: DMR must be ~100%, Layered must be < 35%."""
        with open(PROCESSED_JSON) as f:
            data = json.load(f)
        bench = data["benchmarks"]
        
        dmr_overhead = bench["config4_overhead_pct"]
        layered_overhead = bench["config5_overhead_pct"]
        
        self.assertGreater(dmr_overhead, 80.0, f"DMR overhead should be ~100%, found {dmr_overhead}%")
        self.assertLess(layered_overhead, 35.0, f"Layered overhead should be < 35%, found {layered_overhead}%")

    def test_dmr_common_mode_blind_spot(self):
        """Verify DMR has 0% detection on pre-invocation corruption and persistent stuck faults."""
        with open(PROCESSED_JSON) as f:
            data = json.load(f)
        fc = data["fault_coverage"]
        
        # Class 5: Pre-invocation input corruption
        self.assertEqual(fc["class_5"]["config4_duplicate_dmr_pct"], 0.0)
        # Class 8: Persistent stuck faults
        self.assertEqual(fc["class_8"]["config4_duplicate_dmr_pct"], 0.0)

    def test_layered_architecture_superiority(self):
        """Verify Layered Architecture achieves >= 95% detection across all classes."""
        with open(PROCESSED_JSON) as f:
            data = json.load(f)
        fc = data["fault_coverage"]
        
        for c in range(1, 9):
            key = f"class_{c}"
            rate = fc[key]["config5_layered_pct"]
            self.assertGreaterEqual(rate, 95.0, f"Class {c} layered detection {rate}% < 95.0%")

    def test_raw_trials_metadata(self):
        """Verify raw trials metadata file is present and valid."""
        self.assertTrue(os.path.exists(RAW_JSON), "Raw metadata file missing")
        with open(RAW_JSON) as f:
            raw = json.load(f)
        self.assertEqual(raw.get("status"), "COMPLETE")
        self.assertEqual(raw.get("total_trials"), 1200)


if __name__ == "__main__":
    unittest.main()
