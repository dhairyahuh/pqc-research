#!/usr/bin/env python3
"""
Unit and regression tests for Phase 7F:
Independent Validation and Publication-Readiness Audit.

Validates:
1. Mathematical verification of the intermediate product (t) reuse blind spot.
2. Verification of recomputed trial metrics (1,050 trials, R_U = 0.0%).
3. Active NTT microbenchmark analysis.
4. Completeness and integrity of Phase 7F audit deliverables.
"""

import json
import os
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments", "phase7f"))

from reproduce_audit import Q, fqmul, mod_q, audit_mathematical_t_reuse, wilson_score_interval


class TestPhase7FMathematicalAudit(unittest.TestCase):
    """Tests verifying the mathematical audit findings."""

    def test_t_reuse_blind_spot_demonstration(self):
        """
        Prove that reusing intermediate product t in the butterfly difference
        invariant causes the check to evaluate to 0 under multiplier corruption,
        whereas recomputing t catches the corruption.
        """
        audit_res = audit_mathematical_t_reuse()
        # Reusing t MUST fail to detect the fault (diff eval = 0)
        self.assertEqual(audit_res["reused_t_diff_eval"], 0)
        self.assertEqual(audit_res["reused_t_sum_eval"], 0)
        self.assertFalse(audit_res["reused_t_detected"])

        # Recomputing t MUST detect the fault (diff eval != 0)
        self.assertNotEqual(audit_res["recomputed_t_diff_eval"], 0)
        self.assertTrue(audit_res["recomputed_t_detected"])

    def test_output_register_perturbation_detected(self):
        """
        Dual invariant catches output register perturbations even with reused t,
        demonstrating that the invariant is an output check, not an ALU check.
        """
        u = 1200
        v = 400
        zeta = 500
        t = fqmul(v, zeta)
        u_out = mod_q(u + t)
        v_out = mod_q(u - t)

        # Output register glitch on u_out
        delta = 33
        u_glitched = mod_q(u_out + delta)

        diff = mod_q(u_glitched - v_out - 2 * t)
        sum_val = mod_q(u_glitched + v_out - 2 * u)
        self.assertTrue(diff != 0 or sum_val != 0, "Failed to detect output register flip")

    def test_wilson_ci_bounds(self):
        """Verify Wilson score confidence interval computation."""
        low, high = wilson_score_interval(150, 150)
        self.assertGreaterEqual(low, 0.97)
        self.assertAlmostEqual(high, 1.0, places=4)


class TestPhase7FRecomputedMetrics(unittest.TestCase):
    """Tests verifying the recomputed metrics and dataset integrity."""

    @classmethod
    def setUpClass(cls):
        cls.metrics_path = os.path.join(
            REPO_ROOT, "results", "phase7f", "processed", "recomputed_metrics.json"
        )
        with open(cls.metrics_path, "r", encoding="utf-8") as f:
            cls.metrics = json.load(f)

    def test_recomputed_trials_totals(self):
        """Verify 1,050 trials recomputed across 7 layers."""
        trials = self.metrics["trial_reproduction"]
        self.assertEqual(trials["total_trials"], 1050)
        for l in range(1, 8):
            key = f"layer_{l}"
            self.assertIn(key, trials["layers"])
            self.assertEqual(trials["layers"][key]["n"], 150)

    def test_recomputed_rates(self):
        """Verify recomputed recovery and safety rates."""
        ov = self.metrics["trial_reproduction"]["overall"]
        self.assertAlmostEqual(ov["rec_a_rate"], 150 / 1050, delta=1e-3)
        self.assertAlmostEqual(ov["rec_e_rate"], 1.0, delta=1e-3)
        self.assertEqual(ov["undetected_corrupt_rate_e"], 0.0)

    def test_microbenchmark_presence(self):
        """Verify NTT microbenchmark data exists and shows non-zero overhead."""
        bench = self.metrics["ntt_microbenchmark_ns"]
        self.assertIn("unmonitored_poly_ntt_ns", bench)
        self.assertIn("monitored_all_reused_t_ns", bench)
        # Active monitoring must take longer than unmonitored
        self.assertGreater(bench["monitored_all_reused_t_ns"], bench["unmonitored_poly_ntt_ns"])


class TestPhase7FDeliverablesIntegrity(unittest.TestCase):
    """Tests confirming all required documentation deliverables exist."""

    def test_required_docs_exist(self):
        docs = [
            "docs/phase7f/independent_validation_report.md",
            "docs/phase7f/claim_reconciliation.md",
            "docs/phase7f/threats_to_validity.md",
            "results/phase7f/processed/recomputed_metrics.json",
            "experiments/phase7f/reproduce_audit.py",
        ]
        for rel_path in docs:
            full_path = os.path.join(REPO_ROOT, rel_path)
            self.assertTrue(os.path.exists(full_path), f"Missing deliverable: {rel_path}")


if __name__ == "__main__":
    unittest.main()
