#!/usr/bin/env python3
"""Smoke tests for the ASTRA-Sec benchmarking suite (Prompt 11)."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from benchmarks.run_comparative_benchmarks import BenchmarkSuite


class TestBenchmarkSmoke(unittest.TestCase):
    """Verifies that the benchmarking suite initializes, measures, and exports properly."""

    def test_benchmark_micro_run(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            suite = BenchmarkSuite(output_dir=tmp_dir, seed=42)
            # Run minimal iterations for fast regression verification
            suite.run_crypto_benchmarks(iterations=5, warmup=1)
            suite.run_dtn_security_benchmarks(iterations=5, warmup=1)
            suite.run_system_multihop_benchmarks(iterations=3, warmup=1)
            overheads = suite.measure_overheads()
            suite.export_results(overheads)

            json_path = Path(tmp_dir) / "benchmark_results.json"
            csv_path = Path(tmp_dir) / "raw_crypto_latencies.csv"

            self.assertTrue(json_path.exists(), "benchmark_results.json was not created.")
            self.assertTrue(csv_path.exists(), "raw_crypto_latencies.csv was not created.")

            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.assertIn("metadata", data)
            self.assertIn("benchmarks", data)
            self.assertIn("overheads", data)
            self.assertGreaterEqual(len(data["benchmarks"]), 10)


if __name__ == "__main__":
    unittest.main()
