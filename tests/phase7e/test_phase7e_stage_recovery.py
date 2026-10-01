#!/usr/bin/env python3
"""
Unit and regression tests for Phase 7E:
Mathematical Derivation and Early-Stage NTT Fault Recovery in ML-KEM-768.

Validates:
1. Mathematical reference model butterfly invariant across all layers.
2. Dual butterfly invariant zero-kernel property.
3. Raw experimental trial dataset integrity (1,050 trials).
4. Processed recovery rates (Configs A, B, D, E) and Wilson confidence intervals.
5. Strict zero undetected corrupted key release (R_U = 0.0%).
6. Constant-time execution ratio and DMR performance overhead comparison.
"""

import json
import os
import sys
import unittest

# Ensure experiments/phase7e is importable
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, os.path.join(REPO_ROOT, "experiments", "phase7e"))

try:
    from mathematical_reference import (
        MLKEM_Q,
        MLK_ZETAS,
        fqmul,
        ntt_butterfly,
        verify_butterfly_invariants,
        run_full_ntt_reference,
    )
    MATH_REF_AVAILABLE = True
except ImportError:
    MATH_REF_AVAILABLE = False

RECOVERED_TOKEN = "0x3C3C3C3C"


class TestPhase7EMathematicalReference(unittest.TestCase):
    """Tests verifying the independent mathematical reference model."""

    def setUp(self):
        if not MATH_REF_AVAILABLE:
            self.skipTest("mathematical_reference.py not importable")

    def test_fqmul_known_values(self):
        """Verify Montgomery multiplication reference arithmetic."""
        self.assertEqual(fqmul(0, 100), 0)
        res = fqmul(1, 1)
        self.assertTrue(0 <= res < MLKEM_Q)

    def test_dual_butterfly_check_correct_state(self):
        """Dual invariant must evaluate to True for an uncorrupted butterfly."""
        u = 1234
        v = 2345
        zeta = MLK_ZETAS[1]
        u_prime, v_prime, t = ntt_butterfly(u, v, zeta)

        diff_ok, sum_ok = verify_butterfly_invariants(u, v, zeta, u_prime, v_prime)
        self.assertTrue(diff_ok)
        self.assertTrue(sum_ok)

    def test_detection_kernel_symmetric_perturbation(self):
        """
        Symmetric fault (u' + delta, v' + delta) bypasses Diff check,
        but MUST be detected by Sum check and Dual check.
        """
        u = 1500
        v = 800
        zeta = MLK_ZETAS[2]
        u_prime, v_prime, t = ntt_butterfly(u, v, zeta)

        delta = 42
        u_corrupt = (u_prime + delta) % MLKEM_Q
        v_corrupt = (v_prime + delta) % MLKEM_Q

        diff_ok, sum_ok = verify_butterfly_invariants(u, v, zeta, u_corrupt, v_corrupt)
        # Difference invariant is BLIND to symmetric perturbation
        self.assertTrue(diff_ok, "Diff check unexpectedly triggered on symmetric perturbation")
        # Sum invariant MUST catch symmetric perturbation
        self.assertFalse(sum_ok, "Sum check failed to catch symmetric perturbation")

    def test_detection_kernel_multiplier_perturbation(self):
        """
        Intermediate multiplier fault (t' = t + delta) bypasses Sum check,
        but MUST be detected by Diff check and Dual check.
        """
        u = 1500
        v = 800
        zeta = MLK_ZETAS[2]
        u_prime, v_prime, t = ntt_butterfly(u, v, zeta)
        delta = 42
        t_corrupt = (t + delta) % MLKEM_Q

        u_fault = (u + t_corrupt) % MLKEM_Q
        v_fault = (u - t_corrupt + MLKEM_Q) % MLKEM_Q

        diff_ok, sum_ok = verify_butterfly_invariants(u, v, zeta, u_fault, v_fault)
        # Sum invariant is BLIND to multiplier corruption (u' + v' = 2u mod q)
        self.assertTrue(sum_ok, "Sum check unexpectedly triggered on multiplier corruption")
        # Diff invariant MUST catch it
        self.assertFalse(diff_ok, "Diff check failed to catch multiplier corruption")

    def test_full_ntt_reference_invariant_soundness(self):
        """Run full 7-layer NTT on random polynomial and confirm all 896 invariants hold."""
        import random
        random.seed(42)
        poly = [random.randint(0, MLKEM_Q - 1) for _ in range(256)]
        _, all_diff_ok, all_sum_ok = run_full_ntt_reference(poly, check_invariants=True)
        self.assertTrue(all_diff_ok)
        self.assertTrue(all_sum_ok)


class TestPhase7ETrialDataset(unittest.TestCase):
    """Tests verifying the raw trial dataset schema and contents."""

    @classmethod
    def setUpClass(cls):
        cls.raw_path = os.path.join(
            REPO_ROOT, "results", "phase7e", "raw", "phase7e_stage_recovery_trials.json"
        )
        with open(cls.raw_path, "r", encoding="utf-8") as f:
            cls.trials = json.load(f)

    def test_trial_count_and_layer_distribution(self):
        """1,050 total trials, exactly 150 per layer across layers 1 through 7."""
        self.assertEqual(len(self.trials), 1050)
        layer_counts = {}
        for trial in self.trials:
            layer = trial["stage_layer"]
            layer_counts[layer] = layer_counts.get(layer, 0) + 1

        for layer in range(1, 8):
            self.assertEqual(
                layer_counts.get(layer, 0),
                150,
                f"Layer {layer} does not have exactly 150 trials",
            )

    def test_trial_schema(self):
        """Verify each trial record contains required metadata and outcome fields."""
        required_fields = {
            "trial_id",
            "stage_layer",
            "seed",
            "token_cfg_a",
            "token_cfg_b",
            "token_cfg_c",
            "token_cfg_d",
            "token_cfg_e",
            "recovered_cfg_e",
            "cryptographic_outcome_e",
        }
        for trial in self.trials:
            self.assertTrue(required_fields.issubset(trial.keys()))

    def test_zero_undetected_corruptions(self):
        """Across all 1,050 trials, Config E must always recover the correct key."""
        for trial in self.trials:
            self.assertEqual(
                trial["cryptographic_outcome_e"],
                "CORRECT_KEY",
                f"Trial {trial['trial_id']} released an incorrect key!",
            )
            self.assertTrue(trial["recovered_cfg_e"])
            self.assertEqual(trial["token_cfg_e"], RECOVERED_TOKEN)


class TestPhase7EProcessedResults(unittest.TestCase):
    """Tests verifying processed recovery rates, confidence intervals, and benchmark."""

    @classmethod
    def setUpClass(cls):
        cls.proc_path = os.path.join(
            REPO_ROOT,
            "results",
            "phase7e",
            "processed",
            "phase7e_stage_recovery_results.json",
        )
        with open(cls.proc_path, "r", encoding="utf-8") as f:
            cls.results = json.load(f)

    def test_recovery_hierarchy(self):
        """
        Verify the mathematical hierarchy of stage recovery:
        - Config A recovers only Layer 7 (0% on L1-6, 100% on L7)
        - Config B recovers Layer 1 and 7 (100% on L1 & L7, 0% on others)
        - Config D recovers Layers 1, 4, 7 (100% on L1, L4, L7, 0% on others)
        - Config E recovers ALL Layers 1 through 7 (100% on L1-7)
        """
        layers = self.results["layer_recovery_rates"]
        for l in range(1, 8):
            key = f"layer_{l}"
            self.assertIn(key, layers)
            l_data = layers[key]

            # Config E is always 100%
            self.assertEqual(l_data["recovery_cfg_e_pct"], 100.0)

            # Config A is 100% only on layer 7
            if l == 7:
                self.assertEqual(l_data["recovery_cfg_a_pct"], 100.0)
            else:
                self.assertEqual(l_data["recovery_cfg_a_pct"], 0.0)

            # Config B is 100% on layers 1 and 7
            if l in (1, 7):
                self.assertEqual(l_data["recovery_cfg_b_pct"], 100.0)
            else:
                self.assertEqual(l_data["recovery_cfg_b_pct"], 0.0)

            # Config D is 100% on layers 1, 4, 7
            if l in (1, 4, 7):
                self.assertEqual(l_data["recovery_cfg_d_pct"], 100.0)
            else:
                self.assertEqual(l_data["recovery_cfg_d_pct"], 0.0)

            # Wilson CI lower bound >= 97.5% for fully recovered layers
            self.assertGreaterEqual(l_data["wilson_95_ci_low"], 97.5)

    def test_benchmark_metrics(self):
        """Verify latency overhead and constant-time ratio properties."""
        b = self.results["benchmark"]
        # Baseline ~42 us, DMR ~85 us (+100%)
        self.assertAlmostEqual(b["overhead_dmr_pct"], 100.12, delta=5.0)

        # Config E overhead ~20.26%
        self.assertLess(b["overhead_config_e_pct"], 25.0)
        self.assertGreater(b["overhead_config_e_pct"], 15.0)

        # Config E overhead must be substantially lower than DMR (at least 3.5x lower)
        self.assertLess(b["overhead_config_e_pct"] * 3.5, b["overhead_dmr_pct"])

        # Invalid CT ratio must be strictly 1.00 +/- 0.02
        self.assertAlmostEqual(b["invalid_ct_ratio_config_e"], 1.00, delta=0.02)


if __name__ == "__main__":
    unittest.main()
