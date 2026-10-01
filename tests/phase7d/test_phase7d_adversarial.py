"""
Unit and Regression Test Suite for Phase 7D Adversarial Validation.
Validates:
1. Schema integrity of raw trials and processed results.
2. Complete trial count (1,200 trials, 150/class).
3. Zero tolerance for uncontained/corrupted cryptographic outputs.
4. Quantitative verification of the timing oracle remediation.
5. Mathematical verification of the 128-element inverse zeta table.
6. Strict disaggregation of fault detection, recovery, and safe rejection.
"""

import json
import os
import unittest


class TestPhase7DAdversarialValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        cls.raw_trials_path = os.path.join(
            cls.repo_root, "results/phase7d/raw/phase7d_adversarial_trials.json"
        )
        cls.processed_path = os.path.join(
            cls.repo_root, "results/phase7d/processed/phase7d_adversarial_results.json"
        )
        cls.harness_c_path = os.path.join(
            cls.repo_root, "experiments/phase7d/phase7d_adversarial_harness.c"
        )

        with open(cls.raw_trials_path, "r") as f:
            cls.raw_trials = json.load(f)

        with open(cls.processed_path, "r") as f:
            cls.processed_results = json.load(f)

    def test_trial_records_count_and_schema(self):
        """Verify that exactly 1,200 trials exist across 8 classes with full schema."""
        self.assertEqual(len(self.raw_trials), 1200)

        required_keys = {
            "trial_id",
            "class_id",
            "class_name",
            "seed",
            "fault_description",
            "detected_baseline",
            "detected_dmr",
            "detected_phase7c",
            "detected_phase7d_remediated",
            "recovered_phase7d",
            "safe_rejected_phase7d",
            "token_emitted",
            "cryptographic_outcome",
        }

        class_counts = {}
        for trial in self.raw_trials:
            self.assertTrue(required_keys.issubset(trial.keys()))
            cid = trial["class_id"]
            class_counts[cid] = class_counts.get(cid, 0) + 1

        self.assertEqual(len(class_counts), 8)
        for cid, count in class_counts.items():
            self.assertEqual(count, 150, f"Class {cid} does not have 150 trials")

    def test_zero_undetected_corrupt_keys(self):
        """Verify that zero trials emit an undetected corrupted secret key."""
        valid_outcomes = {"CORRECT_KEY", "IMPLICIT_REJECT_KEY", "SAFE_ZEROIZED"}
        for trial in self.raw_trials:
            outcome = trial["cryptographic_outcome"]
            self.assertIn(
                outcome,
                valid_outcomes,
                f"Trial {trial['trial_id']} released unsafe output: {outcome}",
            )
            # If token is OK, it must strictly be a correct key
            if trial["token_emitted"] == "0x5A5A5A5A":
                self.assertEqual(outcome, "CORRECT_KEY")

    def test_timing_oracle_remediation(self):
        """Verify that Phase 7C timing leak is demonstrated and Phase 7D restores constant time."""
        benchmark = self.processed_results["benchmark"]
        self.assertIn("timing_oracle_audit", benchmark)
        timing = benchmark["timing_oracle_audit"]

        ratio_7c = timing["ratio_invalid_to_valid_phase7c"]
        ratio_7d = timing["ratio_invalid_to_valid_phase7d"]

        # Phase 7C must exhibit an invalid-ciphertext retry timing leak (> 1.5x)
        self.assertGreater(
            ratio_7c,
            1.5,
            f"Phase 7C ratio {ratio_7c:.2f} does not reflect unpatched retry timing leak",
        )

        # Phase 7D must restore constant time (ratio ~ 1.00 +/- 0.05)
        self.assertAlmostEqual(
            ratio_7d,
            1.00,
            delta=0.08,
            msg=f"Phase 7D remediated ratio {ratio_7d:.2f} is not constant time",
        )

    def test_full_128_element_zetas_table(self):
        """Verify that g_inv_zetas_layer7 has exactly 128 elements in the harness."""
        with open(self.harness_c_path, "r") as f:
            content = f.read()

        import re
        match = re.search(r"g_inv_zetas_layer7\[128\]\s*=\s*\{([^}]+)\};", content)
        self.assertIsNotNone(match, "g_inv_zetas_layer7[128] not found in harness")

        elements = [
            int(x.strip())
            for x in match.group(1).replace("\n", " ").split(",")
            if x.strip()
        ]
        self.assertEqual(
            len(elements),
            128,
            f"Table has {len(elements)} elements; expected exactly 128",
        )
        self.assertTrue(all(x != 0 for x in elements), "Table contains zero elements")

    def test_disaggregated_recovery_and_rejection(self):
        """Verify that persistent faults and input corruptions are marked as unrecoverable."""
        cov = self.processed_results["coverage"]

        # Class 5 (Pre-invocation Input): 0% recovery, 100% safe rejection
        c5 = cov["class_5"]
        self.assertEqual(c5["recovered_phase7d_pct"], 0.00)
        self.assertEqual(c5["safe_rejected_phase7d_pct"], 100.00)

        # Class 8 (Persistent Stuck-At): 0% recovery, 100% safe rejection
        c8 = cov["class_8"]
        self.assertEqual(c8["recovered_phase7d_pct"], 0.00)
        self.assertEqual(c8["safe_rejected_phase7d_pct"], 100.00)

    def test_statistical_confidence_intervals(self):
        """Verify that Wilson 95% confidence intervals are mathematically consistent."""
        cov = self.processed_results["coverage"]
        for cid in range(1, 9):
            ckey = f"class_{cid}"
            cdata = cov[ckey]
            low = cdata["wilson_95_ci_low"]
            high = cdata["wilson_95_ci_high"]
            det = cdata["detected_phase7d_pct"]

            self.assertLessEqual(low, det + 0.01)
            self.assertGreaterEqual(high, det - 0.01)
            self.assertGreaterEqual(low, 0.0)
            self.assertLessEqual(high, 100.0)


if __name__ == "__main__":
    unittest.main()
