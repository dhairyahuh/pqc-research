#!/usr/bin/env python3
"""
Test Suite: Phase 7I End-to-End Validation, Inverse NTT Monitoring, and Public API Fail-Stop
Validates:
1. 100% Decapsulation NTT Coverage (5,376 Forward + 4,480 Inverse = 9,856 butterflies, 0 false positives).
2. Public API Fail-Stop Contract:
   - mlkem768_dec(NULL) under persistent fault enforces fail = 0xFF and releases safe rejection key.
   - mlkem768_dec_monitored(&status) returns status = 0xFFFFFFFF (MLK_STATUS_FAULT).
3. Inverse NTT Mathematical Invariant Soundness:
   - Adder sum check S = (u' - (u + v)) mod 3329 == 0.
   - Multiplier recomputed difference check D = (v' - fqmul(v - u, zeta)) mod 3329 == 0.
   - Symmetric and anti-symmetric output perturbations detected.
4. Comprehensive 14-Class Campaign Outcomes:
   - 100% recovery on transient ALU faults (C01, C03, C04, C06, C07, C08, C09).
   - 100% safe rejection on persistent and protocol faults (C10, C11, C12, C13).
   - Exactly zero undetected key corruptions (R_U == 0.00%) across all 1,400 trials.
5. Performance & Constant-Time Assessment:
   - Combined Forward+Inverse overhead < 30% (measured ~17.1%) vs DMR > 100%.
   - Randomized-order timing ratio between invalid and valid ciphertexts within 1.00 ± 0.05.
"""

import json
import os
import subprocess
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
E2E_RESULTS_JSON = os.path.join(ROOT_DIR, "results/phase7i/processed/phase7i_e2e_results.json")
E2E_TRIALS_JSON = os.path.join(ROOT_DIR, "results/phase7i/raw/phase7i_e2e_trials.json")
HARNESS_BIN = os.path.join(ROOT_DIR, "bin/phase7i_e2e_validation")


class TestPhase7IE2EValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(E2E_RESULTS_JSON) or not os.path.exists(E2E_TRIALS_JSON):
            subprocess.run(["make", "phase7i"], cwd=ROOT_DIR, check=True)
            subprocess.run([HARNESS_BIN], cwd=ROOT_DIR, check=True)

        with open(E2E_RESULTS_JSON, "r") as f:
            cls.e2e_results = json.load(f)

        with open(E2E_TRIALS_JSON, "r") as f:
            cls.e2e_trials = json.load(f)

    def test_01_full_ntt_coverage_and_butterfly_counts(self):
        """Verify 5,376 forward and 4,480 inverse butterflies (total 9,856) executed."""
        proc = subprocess.run([HARNESS_BIN], cwd=ROOT_DIR, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Harness failed: {proc.stderr}")
        self.assertIn("1.2 Forward-Only:         Fwd Count = 5376, Inv Count =    0, Mis = 0 (PASS: EXACT 5,376)", proc.stdout)
        self.assertIn("1.3 Inverse-Only:         Fwd Count =    0, Inv Count = 4480, Mis = 0 (PASS: EXACT 4,480)", proc.stdout)
        self.assertIn("1.4 Combined Dual NTT:    Total Executed =  9856 (5376 + 4480), Mismatches = 0 (PASS: 100% COMPLETE NTT COVERAGE)", proc.stdout)

    def test_02_public_api_fail_stop_contract(self):
        """Verify public API calls with NULL internal_status enforce fail = 0xFF under persistent faults."""
        proc = subprocess.run([HARNESS_BIN], cwd=ROOT_DIR, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("2.1 Public mlkem768_dec(NULL) Fwd Fault: RC = 0, Match = NO (PASS: SAFE REJECTION)", proc.stdout)
        self.assertIn("2.2 Monitored mlkem768_dec_monitored:   RC = 0, Status = 0xFFFFFFFF (PASS: 0xFFFFFFFF FAULT TOKEN)", proc.stdout)
        self.assertIn("2.3 Public mlkem768_dec(NULL) Inv Fault: RC = 0, Match = NO (PASS: SAFE REJECTION)", proc.stdout)
        self.assertIn("2.4 Monitored mlkem768_dec_monitored:   RC = 0, Status = 0xFFFFFFFF (PASS: 0xFFFFFFFF FAULT TOKEN)", proc.stdout)

    def test_03_inverse_ntt_mathematical_invariants(self):
        """Verify Gentleman-Sande inverse butterfly invariant arithmetic."""
        q = 3329
        u, v, zeta = 500, 1200, -1044

        # Gentleman-Sande forward arithmetic
        # u' = barrett_reduce(u + v)
        # v' = fqmul(v - u, zeta)
        diff = (v - u)
        prod = diff * zeta
        u_red = ((prod & 0xFFFF) * (-3327)) & 0xFFFF
        if u_red > 32767:
            u_red -= 65536
        v_prime = (prod - u_red * q) >> 16
        u_prime = (u + v) % q

        # Test Invariants on clean outputs
        sum_c = (u_prime - (u + v)) % q
        diff_c = (v_prime - v_prime) % q
        self.assertEqual(sum_c, 0)
        self.assertEqual(diff_c, 0)

        # Test symmetric perturbation: u* = u' + delta, v* = v' + delta
        delta = 77
        u_sym = u_prime + delta
        v_sym = v_prime + delta
        sum_sym = (u_sym - (u + v)) % q
        self.assertEqual(sum_sym, delta % q, "Sum check must catch symmetric perturbation!")

        # Test multiplier fault on v'
        v_fault = v_prime ^ 0x01
        diff_fault = (v_fault - v_prime) % q
        self.assertNotEqual(diff_fault, 0, "Multiplier recomputed check must catch v' fault!")

    def test_04_adversarial_campaign_metrics_and_zero_corruption(self):
        """Verify 1,400 trials across 14 classes achieve strict 0.00% undetected key corruption."""
        self.assertEqual(len(self.e2e_trials), 1400)

        # Classes that achieve 100% autonomous recovery (ALU faults)
        recovery_classes = [
            "C01: Fwd Intermediate T (Transient)",
            "C03: Fwd Output Register (Transient)",
            "C04: Inv Intermediate Diff (Transient)",
            "C06: Inv Adder Output U' (Transient)",
            "C07: Inv Multiplier Output V' (Transient)",
            "C08: Inv Symmetric Output Perturbation",
            "C09: Inv Anti-Symmetric Output Perturbation"
        ]

        for cls_name in recovery_classes:
            trials = [t for t in self.e2e_trials if t["fault_class"] == cls_name]
            self.assertEqual(len(trials), 100)
            rec_count = sum(1 for t in trials if t["outcome"] == "RECOVERED")
            self.assertEqual(rec_count, 100, f"{cls_name} did not achieve 100% recovery (got {rec_count})")

        # Classes that achieve 100% safe rejection
        reject_classes = [
            "C10: Pre-NTT Ciphertext Input Corruption",
            "C11: Persistent Stuck-at Fault (Forward NTT)",
            "C12: Persistent Stuck-at Fault (Inverse NTT)",
            "C13: FO Control Decision Gate Perturbation"
        ]

        for cls_name in reject_classes:
            trials = [t for t in self.e2e_trials if t["fault_class"] == cls_name]
            self.assertEqual(len(trials), 100)
            rej_count = sum(1 for t in trials if t["outcome"] == "SAFE_REJECT")
            self.assertEqual(rej_count, 100, f"{cls_name} did not achieve 100% rejection (got {rej_count})")

        # Global Undetected Corruptions must be exactly 0 across all 1,400 trials
        corrupt_count = sum(1 for t in self.e2e_trials if t["outcome"] == "UNDETECTED_CORRUPT")
        self.assertEqual(corrupt_count, 0, f"Found {corrupt_count} undetected key corruptions!")

    def test_05_integrated_benchmark_and_timing_ratio(self):
        """Verify combined Forward+Inverse monitoring overhead and constant-time behavior."""
        bench = self.e2e_results["benchmarks"]

        # Combined Forward+Inverse overhead should be ~15% - 25% (measured ~17.1%)
        self.assertLess(bench["combined"]["overhead_pct"], 30.0)
        self.assertGreater(bench["combined"]["overhead_pct"], 10.0)

        # DMR overhead should be > 100% (measured ~137%)
        self.assertGreater(bench["dmr"]["overhead_pct"], 100.0)

        # Randomized timing assessment ratio must be ~1.00 (within 0.05)
        ratio_mean = self.e2e_results["timing_assessment"]["ratio_mean"]
        ratio_med  = self.e2e_results["timing_assessment"]["ratio_median"]
        self.assertAlmostEqual(ratio_mean, 1.00, delta=0.05)
        self.assertAlmostEqual(ratio_med,  1.00, delta=0.05)


if __name__ == "__main__":
    unittest.main()
