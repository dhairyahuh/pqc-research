"""ASTRA-Sec Phase 3: Unit Tests for Experiment Configuration Manager."""

import os
import tempfile
import unittest
from pydantic import ValidationError

from research.phase3_experimental_lab.harness.config import (
    BaselineType,
    ExperimentConfig,
    FaultConfig,
    ImpairmentConfig,
    WorkloadConfig,
)


class TestLabConfig(unittest.TestCase):
    def test_default_config_valid(self):
        cfg = ExperimentConfig(
            experiment_name="Unit Test Experiment",
            group="A",
            scenario_id="EXP-TEST-01",
        )
        self.assertEqual(cfg.baseline, BaselineType.TREATMENT_E_FULL_ASTRA_SEC)
        self.assertEqual(cfg.workload.payload_size_bytes, 256)
        self.assertEqual(cfg.workload.total_messages, 10)
        self.assertEqual(cfg.random_seed, 42)

    def test_config_hash_deterministic(self):
        cfg1 = ExperimentConfig(
            experiment_name="Test Hash",
            group="A",
            scenario_id="EXP-01",
            random_seed=123,
        )
        cfg2 = ExperimentConfig(
            experiment_name="Test Hash",
            group="A",
            scenario_id="EXP-01",
            random_seed=123,
        )
        self.assertEqual(cfg1.compute_config_hash(), cfg2.compute_config_hash())

    def test_invalid_payload_size_rejected(self):
        with self.assertRaises(ValidationError):
            # Payload size too small (< 16 B)
            ExperimentConfig(
                experiment_name="Invalid Payload",
                group="A",
                scenario_id="EXP-INV",
                workload=WorkloadConfig(payload_size_bytes=4),
            )

    def test_invalid_loss_rate_rejected(self):
        with self.assertRaises(ValidationError):
            # Loss rate > 1.0
            ExperimentConfig(
                experiment_name="Invalid Loss",
                group="A",
                scenario_id="EXP-INV",
                impairment=ImpairmentConfig(loss_rate=1.5),
            )

    def test_save_and_load_file(self):
        temp_dir = tempfile.mkdtemp()
        path = os.path.join(temp_dir, "test_cfg.json")
        try:
            cfg = ExperimentConfig(
                experiment_name="File Save Test",
                group="B",
                scenario_id="EXP-SAVE",
            )
            cfg.save_to_file(path)
            loaded = ExperimentConfig.load_from_file(path)
            self.assertEqual(cfg.experiment_name, loaded.experiment_name)
            self.assertEqual(cfg.compute_config_hash(), loaded.compute_config_hash())
        finally:
            if os.path.exists(path):
                os.remove(path)
            os.rmdir(temp_dir)


if __name__ == "__main__":
    unittest.main()
