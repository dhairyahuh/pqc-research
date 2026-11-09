"""Integration test executing the full ASTRA-Sec 38-trial adversarial campaign suite."""

import os
import shutil
import tempfile
import unittest

from astra_sec.experiment.models import ExperimentGroup
from astra_sec.experiment.runner import ExperimentRunner


class TestAdversarialCampaigns(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_38_trial_adversarial_campaign_execution(self):
        """Executes all 38 trials across Groups A, B, C, D, E.

        Asserts:
        1. All 38 trials execute and complete.
        2. Detection rate is 100% across all injected faults/attacks.
        3. Zero Silent Data Corruption (SDC) observed across all trials.
        4. Group breakdown matches formal specification:
           - Group A (Message Security): 9 trials
           - Group B (Network Disruption): 9 trials
           - Group C (Cryptographic Faults): 7 trials
           - Group D (Checker Independence): 7 trials
           - Group E (Cross-Layer Failure): 6 trials
        """
        runner = ExperimentRunner(self.temp_dir, seed=42)
        records = runner.run_all_campaigns()

        self.assertEqual(len(records), 38)

        # Group count verification
        grp_a = [r for r in records if r.group == ExperimentGroup.GROUP_A]
        grp_b = [r for r in records if r.group == ExperimentGroup.GROUP_B]
        grp_c = [r for r in records if r.group == ExperimentGroup.GROUP_C]
        grp_d = [r for r in records if r.group == ExperimentGroup.GROUP_D]
        grp_e = [r for r in records if r.group == ExperimentGroup.GROUP_E]

        self.assertEqual(len(grp_a), 9)
        self.assertEqual(len(grp_b), 9)
        self.assertEqual(len(grp_c), 7)
        self.assertEqual(len(grp_d), 7)
        self.assertEqual(len(grp_e), 6)

        # Zero SDC invariant
        for r in records:
            self.assertFalse(
                r.sdc_outcome,
                f"CRITICAL SDC INVARIANT VIOLATION in {r.experiment_id} ({r.test_name})",
            )
            self.assertTrue(
                r.detection_result,
                f"Detection failure in {r.experiment_id} ({r.test_name})",
            )

        # Verify JSONL log was written
        self.assertTrue(os.path.exists(runner.trials_file))
        with open(runner.trials_file, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        self.assertEqual(len(lines), 38)


if __name__ == "__main__":
    unittest.main()
