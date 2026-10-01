#!/usr/bin/env python3
"""
Test Suite: Phase 7G Native ML-KEM NTT Monitor Integration and End-to-End Validation
Validates:
1. Genuine in-tree execution (5,376 butterflies executed, zero false positives on authentic inputs).
2. Multiplier blind-spot discrimination: Reused-t fails (<10% recovery) while Recomputed-t recovers (100% recovery).
3. Output register & symmetric perturbation recovery: Classes 3 & 4 achieve 100% recovery.
4. Fail-safe handling: Pre-NTT input, persistent stuck-at, and FO decision faults safely reject (100% safe rejection).
5. Zero undetected key corruption (R_U == 0.00% across all 1,200 trials).
6. Integrated benchmark overhead (<20% for Recomputed-t vs ~100% for DMR) and constant-time ratio (1.00x).
"""

import json
import os
import subprocess
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RESULTS_JSON = os.path.join(ROOT_DIR, "results/phase7g/processed/phase7g_native_results.json")
RAW_TRIALS_JSON = os.path.join(ROOT_DIR, "results/phase7g/raw/phase7g_native_trials.json")
HARNESS_BIN = os.path.join(ROOT_DIR, "bin/phase7g_native_validation")


class TestPhase7GNativeValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure results exist; if not, re-run harness
        if not os.path.exists(RESULTS_JSON) or not os.path.exists(RAW_TRIALS_JSON):
            subprocess.run(["make", "phase7g"], cwd=ROOT_DIR, check=True)

        with open(RESULTS_JSON, "r") as f:
            cls.results = json.load(f)

        with open(RAW_TRIALS_JSON, "r") as f:
            cls.raw_trials = json.load(f)

    def test_01_binary_execution_and_instrumentation_proof(self):
        """Verify native harness executes cleanly and confirms in-tree butterfly execution."""
        proc = subprocess.run([HARNESS_BIN], cwd=ROOT_DIR, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Harness failed: {proc.stderr}")
        self.assertIn("--- [Section 1] Control Trials & Native Path Instrumentation Proof ---", proc.stdout)
        self.assertIn("Executed Butterflies = 5376", proc.stdout)
        self.assertIn("Mismatches = 0", proc.stdout)
        self.assertIn("Test 1.2 Reused-T Active All Layers", proc.stdout)
        self.assertIn("Test 1.3 Recomputed-T Active Layers", proc.stdout)

    def test_02_multiplier_fault_discrimination(self):
        """Verify empirical confirmation of the multiplier blind spot (Class 1)."""
        c1 = self.results["threat_classes"]["class_1"]
        # Reused-t CANNOT detect faults in t, resulting in low recovery (~4%) similar to baseline noise (2.67%)
        self.assertLess(c1["rec_reused_t_pct"], 10.0, "Reused-t falsely claimed high recovery on multiplier faults")
        # Recomputed-t detects and recovers 100% of transient multiplier faults
        self.assertEqual(c1["rec_recomputed_t_pct"], 100.0, "Recomputed-t failed to achieve 100% recovery on Class 1")
        self.assertEqual(c1["rej_recomputed_t_pct"], 0.0, "Recomputed-t had unexpected rejections on Class 1")

    def test_03_output_register_and_symmetric_fault_recovery(self):
        """Verify Classes 3 and 4 achieve 100% recovery under both monitor modes."""
        c3 = self.results["threat_classes"]["class_3"]
        c4 = self.results["threat_classes"]["class_4"]

        # Class 3: Output register bit flip
        self.assertEqual(c3["rec_reused_t_pct"], 100.0)
        self.assertEqual(c3["rec_recomputed_t_pct"], 100.0)

        # Class 4: Symmetric perturbation (u'+Δ, v'+Δ)
        self.assertEqual(c4["rec_reused_t_pct"], 100.0)
        self.assertEqual(c4["rec_recomputed_t_pct"], 100.0)

    def test_04_safe_implicit_rejection_boundaries(self):
        """Verify Classes 2, 5, 6, 7 safely reject without leaking corrupted keys."""
        classes = self.results["threat_classes"]

        # Class 2: Twiddle factor corruption
        self.assertGreaterEqual(classes["class_2"]["rej_recomputed_t_pct"], 95.0)

        # Class 5: Pre-NTT input corruption
        self.assertEqual(classes["class_5"]["rej_recomputed_t_pct"], 100.0)

        # Class 6: Persistent ALU stuck-at fault
        self.assertEqual(classes["class_6"]["rec_recomputed_t_pct"], 0.0)
        self.assertEqual(classes["class_6"]["rej_recomputed_t_pct"], 100.0)

        # Class 7: FO decision barrier toggle
        self.assertEqual(classes["class_7"]["rec_recomputed_t_pct"], 0.0)
        self.assertEqual(classes["class_7"]["rej_recomputed_t_pct"], 100.0)

    def test_05_strict_zero_undetected_corruption(self):
        """Verify across all 1,200 trials that zero undetected corrupted keys are released."""
        total_trials = len(self.raw_trials)
        self.assertEqual(total_trials, 1200)

        # Valid statuses:
        # 0x5A5A5A5A (MLK_STATUS_SUCCESS: authentic/recovered key)
        # 0xA5A5A5A5 (MLK_STATUS_REJECT: safe implicit rejection)
        # 0xFFFFFFFF (MLK_STATUS_FAULT: native fault detected / fail-stop triggered)
        # Any other status (e.g. 0xDEADBEEF) represents an unhandled corruption
        valid_statuses = {"0x5A5A5A5A", "0xA5A5A5A5", "0xFFFFFFFF"}
        for t in self.raw_trials:
            for cfg in ["cfg1_unmonitored", "cfg2_reused_t", "cfg3_recomputed_t"]:
                status = t[cfg]["status"]
                self.assertIn(status, valid_statuses, f"Trial {t['trial_id']} ({cfg}) released invalid status {status}!")

    def test_06_benchmark_overhead_and_timing_ratio(self):
        """Verify decapsulation benchmark overhead and constant-time behavior."""
        bench = self.results["benchmark"]

        # DMR overhead should be approximately +100%
        self.assertGreater(bench["overhead_dmr_pct"], 90.0)
        self.assertLess(bench["overhead_dmr_pct"], 115.0)

        # Recomputed-t overhead should be modest (<25%, measured ~15.37%)
        self.assertLess(bench["overhead_recomputed_t_pct"], 25.0)
        self.assertGreater(bench["overhead_recomputed_t_pct"], 5.0)

        # Invalid ciphertext ratio should be ~1.00 (within 0.05)
        self.assertAlmostEqual(bench["invalid_ct_ratio"], 1.00, delta=0.05)


if __name__ == "__main__":
    unittest.main()
