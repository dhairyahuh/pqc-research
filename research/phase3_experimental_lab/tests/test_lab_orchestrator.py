"""ASTRA-Sec Phase 3: Integration Tests for Experiment Orchestrator."""

import json
import os
import shutil
import tempfile
import unittest

from research.phase3_experimental_lab.harness.config import (
    BaselineType,
    ExperimentConfig,
    WorkloadConfig,
)
from research.phase3_experimental_lab.harness.orchestrator import ExperimentOrchestrator


class TestLabOrchestrator(unittest.TestCase):
    def setUp(self):
        self.temp_output_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_output_dir, ignore_errors=True)

    def test_run_small_workload_treatment_e(self):
        cfg = ExperimentConfig(
            experiment_name="Integration Test Orchestrator",
            group="TEST",
            scenario_id="EXP-ORCH-01",
            baseline=BaselineType.TREATMENT_E_FULL_ASTRA_SEC,
            workload=WorkloadConfig(
                payload_size_bytes=128,
                total_messages=3,
                rate_msg_per_sec=50.0,
                concurrency=1,
            ),
            warmup_messages=1,
            output_dir=self.temp_output_dir,
        )

        orch = ExperimentOrchestrator(cfg)
        result = orch.run()

        self.assertEqual(result["status"], "COMPLETED")
        self.assertTrue(os.path.exists(result["raw_output_path"]))
        self.assertTrue(os.path.exists(result["manifest_path"]))

        # Verify raw JSONL records
        with open(result["raw_output_path"], "r", encoding="utf-8") as f:
            lines = [json.loads(line) for line in f]
        self.assertEqual(len(lines), 3)
        for entry in lines:
            self.assertTrue(entry["delivered"])
            self.assertEqual(entry["status"], "SUCCESS")
            self.assertTrue(entry["e2e_latency_us"] > 0)

        # Verify manifest contents
        with open(result["manifest_path"], "r", encoding="utf-8") as f:
            manifest = json.load(f)
        self.assertEqual(manifest["status"], "COMPLETED")
        self.assertEqual(manifest["summary_statistics"]["delivered_count"], 3)
        self.assertEqual(manifest["summary_statistics"]["delivery_rate_pct"], 100.0)
        self.assertTrue("environment" in manifest)
        self.assertTrue(manifest["environment"]["cpu_logical_cores"] > 0)

    def test_run_baseline_non_pqc(self):
        cfg = ExperimentConfig(
            experiment_name="Integration Test Baseline A",
            group="TEST",
            scenario_id="EXP-ORCH-BASEA",
            baseline=BaselineType.BASELINE_A_NON_PQC,
            workload=WorkloadConfig(
                payload_size_bytes=128,
                total_messages=3,
                rate_msg_per_sec=50.0,
                concurrency=1,
            ),
            warmup_messages=0,
            output_dir=self.temp_output_dir,
        )

        orch = ExperimentOrchestrator(cfg)
        result = orch.run()
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["summary"]["delivered_count"], 3)


if __name__ == "__main__":
    unittest.main()
