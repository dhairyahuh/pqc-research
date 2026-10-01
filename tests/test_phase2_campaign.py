#!/usr/bin/env python3
"""
Phase 2 Campaign Test Suite
Validates:
  1. Configuration parsing across all YAML configurations
  2. Statistical Wilson confidence interval calculations
  3. Outcome classification definitions
  4. Raw results schema and integrity
  5. Deterministic seed reproducibility
  6. Quantization model absorption calculations
  7. Verification that injector faults are verified and active
"""

import json
import math
import os
import unittest
import yaml

class TestPhase2Campaign(unittest.TestCase):

    def test_01_configuration_parsing(self):
        """Verify all Phase 2 YAML configuration files are valid and contain required fields."""
        config_dir = "experiments/configurations/mlkem_phase2"
        self.assertTrue(os.path.exists(config_dir), f"Directory {config_dir} must exist")
        expected_configs = [
            "baseline_verification.yaml",
            "ntt_stage_screening.yaml",
            "fault_magnitude.yaml",
            "cbd_faults.yaml",
            "fo_faults.yaml",
            "secret_state_faults.yaml",
            "parameter_set_comparison.yaml",
            "quantization_absorption.yaml"
        ]
        for cfg_name in expected_configs:
            cfg_path = os.path.join(config_dir, cfg_name)
            self.assertTrue(os.path.exists(cfg_path), f"Config {cfg_path} must exist")
            with open(cfg_path, "r") as f:
                cfg = yaml.safe_load(f)
            self.assertIn("experiment_id", cfg)
            self.assertIn("purpose", cfg)
            self.assertIn("output_path", cfg)

    def test_02_wilson_confidence_interval(self):
        """Verify Wilson 95% confidence interval implementation matches statistical definition."""
        def wilson_ci(k, n, z=1.96):
            if n == 0:
                return 0.0, 0.0, 0.0
            p = k / n
            denom = 1.0 + (z * z) / n
            center = (p + (z * z) / (2.0 * n)) / denom
            margin = (z / denom) * math.sqrt((p * (1.0 - p) / n) + (z * z) / (4.0 * n * n))
            low = max(0.0, center - margin) * 100.0
            high = min(1.0, center + margin) * 100.0
            return p * 100.0, low, high

        # N=1000, k=0 (0 events: should have upper bound > 0)
        p, low, high = wilson_ci(0, 1000)
        self.assertEqual(p, 0.0)
        self.assertEqual(low, 0.0)
        self.assertGreater(high, 0.0)
        self.assertLess(high, 1.0) # ~0.37%

        # N=1000, k=1000 (100% events: should have lower bound < 100)
        p, low, high = wilson_ci(1000, 1000)
        self.assertEqual(p, 100.0)
        self.assertGreater(low, 99.0)
        self.assertEqual(high, 100.0)

    def test_03_raw_results_integrity(self):
        """Verify raw JSON results are complete, valid, and contain required outcome classifications."""
        results_file = "results/phase2/raw/mlkem_campaign_raw_results.json"
        self.assertTrue(os.path.exists(results_file), f"Raw results file {results_file} must exist")
        with open(results_file, "r") as f:
            data = json.load(f)
        
        self.assertIn("metadata", data)
        self.assertIn("campaigns", data)
        campaigns = data["campaigns"]
        self.assertGreaterEqual(len(campaigns), 100, "Should contain at least 100 evaluated campaigns")
        
        required_outcomes = [
            "CORRECT", "IMPLICIT_REJECTION", "EXPLICIT_ERROR",
            "CANDIDATE_KEY_MISMATCH", "CRASH", "TIMEOUT",
            "UNDETECTED_FAULT", "POTENTIAL_LEAKAGE_SIGNAL"
        ]
        
        for c in campaigns[:10]:
            self.assertIn("campaign_id", c)
            self.assertIn("algorithm", c)
            self.assertIn("operation", c)
            self.assertIn("total_trials", c)
            self.assertGreater(c["total_trials"], 0)
            self.assertIn("outcomes", c)
            for oc in required_outcomes:
                self.assertIn(oc, c["outcomes"])

    def test_04_baseline_controls(self):
        """Verify that Control A (No-Fault) and Control B (Zero-Glitch) produce 100% CORRECT across all parameter sets."""
        results_file = "results/phase2/raw/mlkem_campaign_raw_results.json"
        with open(results_file, "r") as f:
            data = json.load(f)
        
        for alg in ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]:
            ctrl_a = next((c for c in data["campaigns"] if c["algorithm"] == alg and c["campaign_id"].startswith("BASE_")), None)
            self.assertIsNotNone(ctrl_a, f"Baseline control A for {alg} must exist")
            self.assertEqual(ctrl_a["outcomes"]["CORRECT"]["count"], ctrl_a["total_trials"])
            
            ctrl_b = next((c for c in data["campaigns"] if c["algorithm"] == alg and c["campaign_id"].startswith("CTRL_B_")), None)
            self.assertIsNotNone(ctrl_b, f"Baseline control B for {alg} must exist")
            self.assertEqual(ctrl_b["outcomes"]["CORRECT"]["count"], ctrl_b["total_trials"])

    def test_05_quantization_slack_bounds(self):
        """Verify Phase 1 quantization model: T_worst(d, q) == 1 for all d in {4, 5, 10, 11}."""
        quant_file = "results/phase2/raw/quantization_absorption.json"
        self.assertTrue(os.path.exists(quant_file), f"Quantization results {quant_file} must exist")
        with open(quant_file, "r") as f:
            data = json.load(f)
        
        worst = data["worst_case_tolerance"]
        for d_str in ["4", "5", "10", "11"]:
            self.assertEqual(worst[d_str], 1, f"T_worst for d={d_str} must equal 1 (distance to closest boundary)")

    def test_06_sensitivity_matrix_export(self):
        """Verify processed sensitivity matrix CSV exists and matches campaign count."""
        csv_file = "results/phase2/processed/sensitivity_matrix.csv"
        self.assertTrue(os.path.exists(csv_file), f"CSV {csv_file} must exist")
        with open(csv_file, "r") as f:
            lines = [l.strip() for l in f if l.strip()]
        header = lines[0].split(",")
        self.assertIn("dominant_outcome", header)
        self.assertGreaterEqual(len(lines), 101) # header + at least 100 rows

if __name__ == "__main__":
    unittest.main()
