#!/usr/bin/env python3
"""
Test Suite: Phase 7H Independent Native Fault-Injection Audit and Reproducibility
Validates:
1. In-tree execution & architectural count (5,376 forward NTT butterflies executed, inverse NTT unmonitored).
2. Dual-invariant mathematical blind spots:
   - Symmetric perturbation (u'+Δ, v'+Δ) bypasses Difference check (D==0) but is detected by Sum check (S!=0).
   - Anti-symmetric perturbation (u'+Δ, v'-Δ) bypasses Sum check (S==0) but is detected by Difference check (D!=0).
3. Multiplier blind spot empirical reproducibility (Reused-T < 10% vs Recomputed-T 100%).
4. Phase 7G raw data serialization audit: zero duplicates, zero missing IDs, zero uncontained corruptions.
5. Independent Phase 7H trial dataset integrity (1,200 trials with isolated per-configuration state).
6. Calibrated timing distribution: invalid/valid CT ratio within 1.00 ± 0.05.
"""

import json
import os
import subprocess
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
AUDIT_METRICS_JSON = os.path.join(ROOT_DIR, "results/phase7h/processed/phase7h_audit_metrics.json")
TIMING_DIST_JSON = os.path.join(ROOT_DIR, "results/phase7h/processed/phase7h_timing_distribution.json")
INDEP_TRIALS_JSON = os.path.join(ROOT_DIR, "results/phase7h/raw/phase7h_independent_trials.json")
HARNESS_BIN = os.path.join(ROOT_DIR, "bin/phase7h_independent_reproducer")


class TestPhase7HAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Run reproducer and audit script if output files do not exist
        if not os.path.exists(AUDIT_METRICS_JSON) or not os.path.exists(TIMING_DIST_JSON) or not os.path.exists(INDEP_TRIALS_JSON):
            subprocess.run(["make", "phase7h"], cwd=ROOT_DIR, check=True)
            subprocess.run([HARNESS_BIN], cwd=ROOT_DIR, check=True)
            subprocess.run(["python3", "experiments/phase7h/audit_analysis.py"], cwd=ROOT_DIR, check=True)

        with open(AUDIT_METRICS_JSON, "r") as f:
            cls.audit_metrics = json.load(f)

        with open(TIMING_DIST_JSON, "r") as f:
            cls.timing_dist = json.load(f)

        with open(INDEP_TRIALS_JSON, "r") as f:
            cls.indep_trials = json.load(f)

    def test_01_architectural_execution_and_butterfly_count(self):
        """Verify 5,376 forward NTT butterflies executed and unmonitored inverse NTT."""
        proc = subprocess.run([HARNESS_BIN], cwd=ROOT_DIR, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Harness failed: {proc.stderr}")
        self.assertIn("Audit 1.1 Unmonitored Executed Count: 0", proc.stdout)
        self.assertIn("Audit 1.2 Monitored Executed Count:   5376", proc.stdout)
        self.assertIn("2 NTT vectors x 3 poly/vec x 896 butterflies/poly = 5,376", proc.stdout)
        self.assertIn("5 inverse NTT polynomials (4,480 butterflies) UNMONITORED", proc.stdout)

    def test_02_mathematical_dual_invariant_blind_spots(self):
        """Mathematically verify symmetric vs anti-symmetric invariant complementary coverage."""
        q = 3329
        u, v, zeta = 100, 200, -1044
        # Standard Montgomery multiplication reference for fqmul
        prod = (v * zeta)
        u_red = ((prod & 0xFFFF) * (-3327)) & 0xFFFF
        if u_red > 32767:
            u_red -= 65536
        t = (prod - u_red * q) >> 16

        u_prime = u + t
        v_prime = u - t
        delta = 42

        # 1. Symmetric perturbation: u* = u' + delta, v* = v' + delta
        u_sym = u_prime + delta
        v_sym = v_prime + delta
        diff_sym = (u_sym - v_sym - 2 * t) % q
        sum_sym  = (u_sym + v_sym - 2 * u) % q
        self.assertEqual(diff_sym, 0, "Difference check should have a blind spot on symmetric fault!")
        self.assertNotEqual(sum_sym, 0, "Sum check must catch symmetric fault!")

        # 2. Anti-symmetric perturbation: u* = u' + delta, v* = v' - delta
        u_asym = u_prime + delta
        v_asym = v_prime - delta
        diff_asym = (u_asym - v_asym - 2 * t) % q
        sum_asym  = (u_asym + v_asym - 2 * u) % q
        self.assertEqual(sum_asym, 0, "Sum check should have a blind spot on anti-symmetric fault!")
        self.assertNotEqual(diff_asym, 0, "Difference check must catch anti-symmetric fault!")

    def test_03_multiplier_fault_discrimination_reproducibility(self):
        """Verify empirical confirmation of the multiplier blind spot in independent run."""
        c1_trials = [t for t in self.indep_trials if "Class 1" in t["fault_class"]]
        self.assertEqual(len(c1_trials), 150)

        # Reused-T recovery must be low (< 10%)
        rec_reused = sum(1 for t in c1_trials if t["cfg2_reused_t"]["recovered"])
        self.assertLess(rec_reused / 150.0, 0.10)

        # Recomputed-T recovery must be 100%
        rec_recomputed = sum(1 for t in c1_trials if t["cfg3_recomputed_t"]["recovered"])
        self.assertEqual(rec_recomputed, 150)

    def test_04_phase7g_raw_serialization_audit(self):
        """Verify Phase 7G raw data contains 0 duplicate IDs, 0 missing IDs, and 0 uncontained faults."""
        self.assertEqual(self.audit_metrics["total_records"], 1200)
        self.assertEqual(self.audit_metrics["duplicate_ids"], 0)
        self.assertEqual(len(self.audit_metrics["missing_ids"]), 0)
        self.assertEqual(self.audit_metrics["total_uncontained_faults"], 0)
        self.assertEqual(len(self.audit_metrics["findings"]), 4)

    def test_05_independent_dataset_integrity(self):
        """Verify Phase 7H independent trial dataset schema, size, and isolated state."""
        self.assertEqual(len(self.indep_trials), 1200)
        valid_statuses = {"0x5A5A5A5A", "0xA5A5A5A5", "0xFFFFFFFF"}

        # Class 8 (negative control) must have recovered: true across all 3 configurations
        c8_trials = [t for t in self.indep_trials if "Class 8" in t["fault_class"]]
        self.assertEqual(len(c8_trials), 150)
        for t in c8_trials:
            self.assertTrue(t["cfg1_unmonitored"]["recovered"])
            self.assertTrue(t["cfg2_reused_t"]["recovered"])
            self.assertTrue(t["cfg3_recomputed_t"]["recovered"])

        for t in self.indep_trials:
            for cfg in ["cfg1_unmonitored", "cfg2_reused_t", "cfg3_recomputed_t"]:
                self.assertIn(t[cfg]["status"], valid_statuses)

    def test_06_timing_distribution_and_constant_time_assessment(self):
        """Verify timing metrics from statistical distribution."""
        bench = self.timing_dist
        self.assertEqual(bench["sample_count"], 2000)

        # DMR overhead should be ~100% (90% - 120%)
        self.assertGreater(bench["dmr"]["overhead_pct"], 90.0)
        self.assertLess(bench["dmr"]["overhead_pct"], 120.0)

        # Recomputed-T overhead should be ~15% - 22%
        self.assertGreater(bench["recomputed_t"]["overhead_pct"], 10.0)
        self.assertLess(bench["recomputed_t"]["overhead_pct"], 25.0)

        # Timing ratio between invalid and valid ciphertexts must be near 1.00
        ratio = bench["timing_assessment"]["ratio"]
        self.assertAlmostEqual(ratio, 1.00, delta=0.05)


if __name__ == "__main__":
    unittest.main()
