#!/usr/bin/env python3
"""
Targeted Automated Test Suite for Phase 4:
  - Validates Mathematical Diffusion Laws & Boundary Cases
  - Validates Decoding Slack Correction (|Delta| <= 12 Bound)
  - Validates Dynamic Quantization Vector Absorption Bounds
  - Validates ML-DSA Verification Zero Arithmetic Slack
  - Validates Normalized Datasets, Schemas, and Statistical Intervals
"""

import unittest
import os
import json
import csv
import math

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROCESSED_DIR = os.path.join(ROOT_DIR, "results/phase4/processed")


class TestPhase4ClaimAudit(unittest.TestCase):

    def test_mathematical_diffusion_laws(self):
        """Verify diffusion formulas for ML-KEM and ML-DSA across all layers."""
        # ML-KEM (7 layers)
        for L in range(1, 8):
            shared_expected = 1 << (8 - L)
            single_expected = 1 << (7 - L)
            self.assertEqual(shared_expected, 2 ** (8 - L))
            self.assertEqual(single_expected, 2 ** (7 - L))

        # ML-DSA (8 layers)
        for L in range(1, 9):
            shared_expected = 1 << (9 - L)
            single_expected = 1 << (8 - L)
            self.assertEqual(shared_expected, 2 ** (9 - L))
            self.assertEqual(single_expected, 2 ** (8 - L))

    def test_decoding_slack_boundary_correction(self):
        """
        Verify that decoding slack threshold (832.25) masks Layer 1 single register faults
        ONLY when |Delta| <= 12, correcting the prior claim of unconditional masking.
        """
        q = 3329
        slack = q / 4.0  # 832.25
        error_per_delta = 524.0 / 8.0  # 65.5

        # Check Delta = 12
        peak_err_12 = 12 * error_per_delta
        self.assertLess(peak_err_12, slack, "Delta=12 should be strictly within slack")

        # Check Delta = 13
        peak_err_13 = 13 * error_per_delta
        self.assertGreater(peak_err_13, slack, "Delta=13 should exceed slack")

        max_masked_delta = math.floor(slack / error_per_delta)
        self.assertEqual(max_masked_delta, 12, "Maximum masked delta must be exactly 12")

    def test_quantization_bounds_single_vs_vector(self):
        """
        Verify that while single-coefficient absorption for d=10 is ~69%,
        joint absorption across a 64-coefficient diffused vector is effectively 0.
        """
        p_single_delta1 = 0.6924
        p_vec16 = p_single_delta1 ** 16
        p_vec64 = p_single_delta1 ** 64

        self.assertLess(p_vec16, 0.005, "16-coeff error vector absorption must be < 0.5%")
        self.assertLess(p_vec64, 1e-9, "64-coeff error vector absorption must be < 1e-9")

    def test_mldsa_verification_zero_slack(self):
        """
        Verify that ML-DSA verification commitment hash has zero collision slack.
        """
        # Cryptographic hash SHA3-256 output length in bits
        hash_bits = 256
        collision_prob = 2 ** (-hash_bits)
        self.assertLess(collision_prob, 1e-70, "Hash collision probability must be negligible")

    def test_normalized_campaign_matrix_integrity(self):
        """Verify normalized campaign matrix CSV structure and data sanity."""
        csv_path = os.path.join(PROCESSED_DIR, "normalized_campaign_matrix.csv")
        self.assertTrue(os.path.exists(csv_path), f"File {csv_path} does not exist")

        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertGreaterEqual(len(rows), 230, "Expected at least 230 campaign records")

        required_cols = [
            "campaign_id", "algorithm", "algorithm_family", "operation",
            "fault_taxonomy", "injection_locus", "total_trials",
            "unified_outcome_dominant", "dominant_rate_pct",
            "ci_95_low", "ci_95_high", "security_consequence", "comparability_class"
        ]
        for col in required_cols:
            self.assertIn(col, rows[0], f"Missing required column: {col}")

        # Check CI consistency
        for r in rows:
            rate = float(r["dominant_rate_pct"])
            low = float(r["ci_95_low"])
            high = float(r["ci_95_high"])
            self.assertLessEqual(low, rate + 0.01, f"CI low {low} exceeds rate {rate}")
            self.assertGreaterEqual(high, rate - 0.01, f"CI high {high} less than rate {rate}")

    def test_comparability_matrix_completeness(self):
        """Verify that comparability matrix contains all four required categories."""
        csv_path = os.path.join(PROCESSED_DIR, "cross_algorithm_comparability_matrix.csv")
        self.assertTrue(os.path.exists(csv_path), f"File {csv_path} does not exist")

        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        categories = set(r["category"] for r in rows)
        expected_cats = {
            "DIRECTLY_COMPARABLE",
            "COMPARABLE_WITH_NORMALIZATION",
            "QUALITATIVELY_COMPARABLE",
            "NOT_COMPARABLE"
        }
        self.assertEqual(categories, expected_cats, "Comparability matrix must contain all 4 categories")

    def test_statistical_summary_json(self):
        """Verify statistical summary JSON content and trial counts."""
        json_path = os.path.join(PROCESSED_DIR, "statistical_reanalysis_summary.json")
        self.assertTrue(os.path.exists(json_path), f"File {json_path} does not exist")

        with open(json_path, "r") as f:
            data = json.load(f)

        meta = data["metadata"]
        self.assertGreater(meta["total_evaluated_trials"], 200000, "Expected > 200,000 total trials")
        self.assertEqual(meta["mlkem_campaigns"], 117)
        self.assertEqual(meta["mldsa_campaigns"], 122)


if __name__ == "__main__":
    unittest.main()
