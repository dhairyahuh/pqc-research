#!/usr/bin/env python3
"""
Unit and regression test suite for Phase 7C: Oracle-Free Native Decapsulation Monitoring.
"""

import os
import json
import unittest
import subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

class TestPhase7COracleFreeValidation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.chdir(REPO_ROOT)

    def test_01_raw_trials_integrity(self):
        raw_path = os.path.join(REPO_ROOT, "results/phase7c/raw/phase7c_raw_trials.json")
        self.assertTrue(os.path.exists(raw_path), "Raw trials JSON file missing")
        with open(raw_path, "r") as f:
            trials = json.load(f)

        self.assertEqual(len(trials), 1200, "Expected exactly 1,200 trial records")

        classes = {}
        for tr in trials:
            self.assertIn("trial_id", tr)
            self.assertIn("class_name", tr)
            self.assertIn("detected_c6_layer_native", tr)
            self.assertIn("token_c6", tr)
            c = tr["class_name"]
            classes[c] = classes.get(c, 0) + 1

        self.assertEqual(len(classes), 8, "Expected 8 threat classes")
        for c_name, count in classes.items():
            self.assertEqual(count, 150, f"Class {c_name} should have 150 trials, found {count}")

    def test_02_processed_results_agreement(self):
        proc_path = os.path.join(REPO_ROOT, "results/phase7c/processed/phase7c_resilience_results.json")
        self.assertTrue(os.path.exists(proc_path), "Processed results JSON file missing")
        with open(proc_path, "r") as f:
            proc = json.load(f)

        self.assertEqual(proc.get("phase"), "7C")
        self.assertIn("benchmark", proc)
        self.assertIn("coverage", proc)
        self.assertGreater(proc["benchmark"]["mean_baseline_us"], 0.0)
        self.assertGreater(proc["benchmark"]["mean_layered_native_us"], 0.0)

    def test_03_oracle_free_dependency(self):
        harness_path = os.path.join(REPO_ROOT, "experiments/phase7c/phase7c_oracle_free_harness.c")
        with open(harness_path, "r") as f:
            content = f.read()

        # Verify that decaps_layered_native does NOT accept expected_ss as an argument
        self.assertIn("uint32_t decaps_layered_native(", content)
        native_decl = content[content.find("uint32_t decaps_layered_native("):content.find("/* Layer 1:")]
        self.assertNotIn("expected_ss", native_decl, "decaps_layered_native must not have expected_ss argument")

    def test_04_native_header_declarations(self):
        kem_h = os.path.join(REPO_ROOT, "algorithms/source_ref/mlkem/src/kem.h")
        with open(kem_h, "r") as f:
            content = f.read()

        self.assertIn("mlk_kem_dec_monitored", content)
        self.assertIn("MLK_DECAPS_STATUS_SUCCESS", content)
        self.assertIn("MLK_DECAPS_STATUS_REJECT", content)
        self.assertIn("MLK_DECAPS_STATUS_FAULT", content)

    def test_05_fips_kat_regression(self):
        res = subprocess.run([os.path.join(REPO_ROOT, "bin/test_fips_kats")],
                             capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"FIPS KAT verification failed:\n{res.stderr}")
        self.assertIn("ALL NIST FIPS 203 & 204 TEST VECTORS VERIFIED SUCCESSFULLY (PASS)", res.stdout)

    def test_06_functional_sanity_checks(self):
        bin_path = os.path.join(REPO_ROOT, "bin/phase7c_oracle_free")
        self.assertTrue(os.path.exists(bin_path), "Phase 7C binary must exist")
        res = subprocess.run([bin_path], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Test 1.1 Valid CT:   Token = 0x5A5A5A5A (OK: YES), KeyMatch: MATCH", res.stdout)
        self.assertIn("Test 1.2 Invalid CT: Token = 0xC3C3C3C3 (REJECT: YES), KrejMatch: MATCH", res.stdout)
        self.assertIn("Test 1.3 FO Flip (0->1): Token = 0xA5A5A5A5 (FAULT: YES, Dual-Rail caught: YES)", res.stdout)
        self.assertIn("Test 1.4 FO Flip (1->0): Token = 0xA5A5A5A5 (FAULT: YES, Candidate key blocked: YES)", res.stdout)

if __name__ == "__main__":
    unittest.main()
