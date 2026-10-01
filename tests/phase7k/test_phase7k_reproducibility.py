#!/usr/bin/env python3
"""
Phase 7K: Clean-Room Reproducibility & Publication Verification Tests
====================================================================
Audits:
1. Complete deliverable documentation presence (all 9 docs).
2. Symbolic and small-domain mathematical verification.
3. Cumulative 3,000-trial statistical integrity and seed isolation.
4. Native execution path coverage (5,376 fwd + 4,480 inv = 9,856 bflies).
5. Performance overhead bounds and DMR reduction factor.
6. Constant-time randomized timing distributions.
"""

import json
import subprocess
import unittest
from pathlib import Path

class TestPhase7KReproducibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent.parent.parent
        cls.docs_dir = cls.root / "docs" / "phase7k"
        cls.audit_metrics_path = cls.root / "results" / "phase7k" / "statistical_audit_metrics.json"
        cls.val_results_path = cls.root / "results" / "phase7j" / "processed" / "phase7j_validation_results.json"
        cls.math_script = cls.root / "experiments" / "phase7k" / "symbolic_math_verification.py"

        with open(cls.audit_metrics_path, "r") as f:
            cls.audit_data = json.load(f)

        with open(cls.val_results_path, "r") as f:
            cls.val_results = json.load(f)

    def test_01_all_required_docs_exist(self):
        """Verify all 9 Phase 7K documentation deliverables exist and are non-empty."""
        expected_docs = [
            "reproducibility_protocol.md",
            "environment_and_build_audit.md",
            "fault_injection_audit.md",
            "mathematical_verification.md",
            "statistical_reanalysis.md",
            "performance_reproduction.md",
            "constant_time_evidence_review.md",
            "claim_to_evidence_matrix.md",
            "publication_readiness_verdict.md"
        ]
        for doc in expected_docs:
            doc_file = self.docs_dir / doc
            self.assertTrue(doc_file.exists(), f"Missing required deliverable: {doc}")
            self.assertGreater(doc_file.stat().st_size, 200, f"Deliverable {doc} is unexpectedly small")

    def test_02_symbolic_math_verification(self):
        """Verify symbolic and small-domain mathematical tests pass cleanly."""
        res = subprocess.run(["python3", str(self.math_script)], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Math verification failed:\n{res.stderr}\n{res.stdout}")
        self.assertIn("All mathematical properties verified successfully", res.stdout)

    def test_03_statistical_audit_3000_trials(self):
        """Verify cumulative 3,000-trial audit metrics and seed isolation."""
        data = self.audit_data
        cum = data["cumulative_3000_trials"]
        self.assertEqual(cum["total_trials"], 3000)
        self.assertEqual(cum["undetected_corrupt"], 0)
        self.assertEqual(cum["undetected_corrupt_pct"], 0.0)
        self.assertLess(cum["undetected_ci95"][1], 0.15) # Wilson CI upper bound < 0.15%
        self.assertEqual(data["seed_collisions"], 0)
        self.assertEqual(data["phase_7i"]["duplicate_ids"], 0)
        self.assertEqual(data["phase_7j"]["duplicate_ids"], 0)

    def test_04_native_execution_path_proof(self):
        """Verify 5,376 forward and 4,480 inverse butterflies (total 9,856)."""
        val = self.val_results
        self.assertEqual(val["forward_butterflies"], 5376)
        self.assertEqual(val["inverse_butterflies"], 4480)
        self.assertEqual(val["total_butterflies"], 9856)

    def test_05_overhead_bounds_and_dmr_ratio(self):
        """Verify benchmark overhead bounds and DMR reduction factor."""
        bench = self.val_results["benchmarks"]
        comb_overhead = bench["combined"]["overhead_pct"]
        dmr_overhead = bench["dmr"]["overhead_pct"]

        # Combined monitor overhead is tightly bounded
        self.assertGreater(comb_overhead, 10.0)
        self.assertLess(comb_overhead, 35.0)

        # DMR overhead exceeds 110%
        self.assertGreater(dmr_overhead, 110.0)

        # Overhead advantage ratio: DMR overhead / Combined overhead >= 4.0x
        ratio = dmr_overhead / comb_overhead
        self.assertGreaterEqual(ratio, 4.0, f"DMR overhead advantage {ratio:.2f}x is below expected 4.0x")

    def test_06_randomized_timing_metric(self):
        """Verify randomized timing ratio and negligible effect size."""
        timing = self.val_results["timing_assessment"]
        self.assertAlmostEqual(timing["ratio_mean"], 1.0000, delta=0.05)
        self.assertAlmostEqual(timing["ratio_median"], 1.0000, delta=0.05)
        self.assertLess(timing["cohens_d"], 0.20)

if __name__ == "__main__":
    unittest.main()
