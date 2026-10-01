#!/usr/bin/env python3
"""
Phase 7B Automated Validation Test Suite
Independently verifies raw-data integrity, statistical claims, and mathematical bounds.
"""

import json
import os
import subprocess
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RAW_JSON = os.path.join(REPO_ROOT, "results/phase7b/raw/phase7b_raw_trials.json")
PROCESSED_JSON = os.path.join(REPO_ROOT, "results/phase7b/processed/phase7b_validation_results.json")
HARNESS_BIN = os.path.join(REPO_ROOT, "bin/phase7b_validation")


class TestPhase7bValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure harness has run and produced datasets
        if not os.path.exists(RAW_JSON) or not os.path.exists(PROCESSED_JSON):
            runner = os.path.join(REPO_ROOT, "experiments/phase7b/validation_runner.py")
            subprocess.run(["python3", runner], cwd=REPO_ROOT, check=True)

    def test_raw_records_count_and_schema(self):
        """Verify that exactly 1,200 individual raw records exist with valid schemas."""
        self.assertTrue(os.path.exists(RAW_JSON))
        with open(RAW_JSON) as f:
            records = json.load(f)
        self.assertEqual(len(records), 1200)
        
        required_keys = {
            "trial_index", "class_id", "class_name", "layer", "delta",
            "config1_baseline_det", "config2_unweighted_det",
            "config3_compl_ntt_det", "config4_dmr_det", "config5_layered_det"
        }
        for r in records[:50]: # Sample check
            self.assertTrue(required_keys.issubset(r.keys()))

    def test_unweighted_parity_cancellation_confirmed(self):
        """Verify mathematically established 0.0% detection for unweighted invariant on Class 1 & 2."""
        with open(RAW_JSON) as f:
            records = json.load(f)
        c1_unw = sum(1 for r in records if r["class_id"] == 1 and r["config2_unweighted_det"])
        c2_unw = sum(1 for r in records if r["class_id"] == 2 and r["config2_unweighted_det"])
        self.assertEqual(c1_unw, 0, f"Unweighted invariant should have 0 detections on Class 1, found {c1_unw}")
        self.assertEqual(c2_unw, 0, f"Unweighted invariant should have 0 detections on Class 2, found {c2_unw}")

    def test_dmr_common_mode_blind_spot_confirmed(self):
        """Verify DMR 0.0% detection on pre-invocation input corruption and persistent stuck faults."""
        with open(RAW_JSON) as f:
            records = json.load(f)
        c5_dmr = sum(1 for r in records if r["class_id"] == 5 and r["config4_dmr_det"])
        c8_dmr = sum(1 for r in records if r["class_id"] == 8 and r["config4_dmr_det"])
        self.assertEqual(c5_dmr, 0, f"DMR should have 0 detections on pre-invocation corruption, found {c5_dmr}")
        self.assertEqual(c8_dmr, 0, f"DMR should have 0 detections on persistent stuck faults, found {c8_dmr}")

    def test_layered_detection_bounds(self):
        """Verify Layered Architecture achieves >= 95.0% detection on all classes."""
        with open(PROCESSED_JSON) as f:
            proc = json.load(f)
        cov = proc["coverage_reproduced"]
        for cname, stats in cov.items():
            if cname == "trials_per_class" or not isinstance(stats, dict):
                continue
            rate = stats["config5_pct"]
            self.assertGreaterEqual(rate, 95.0, f"Class {cname} layered detection {rate}% < 95.0%")

    def test_recomputed_stats_match_processed_json(self):
        """Verify mathematical identity between raw records and processed JSON dataset."""
        with open(RAW_JSON) as f:
            records = json.load(f)
        with open(PROCESSED_JSON) as f:
            proc = json.load(f)

        classes_map = {
            1: "intermediate_t", 2: "twiddle_zeta", 3: "output_add", 4: "correlated_mult",
            5: "pre_invocation_input", 6: "checker_perturb", 7: "control_fo_gate", 8: "persistent_stuck"
        }
        for cid, cname in classes_map.items():
            tot = sum(1 for r in records if r["class_id"] == cid)
            c5_det = sum(1 for r in records if r["class_id"] == cid and r["config5_layered_det"])
            expected_pct = round(100.0 * c5_det / tot, 2)
            actual_pct = proc["coverage_reproduced"][cname]["config5_pct"]
            self.assertAlmostEqual(expected_pct, actual_pct, places=2)


if __name__ == "__main__":
    unittest.main()
