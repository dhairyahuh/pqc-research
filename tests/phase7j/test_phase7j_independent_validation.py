#!/usr/bin/env python3
"""
Phase 7J: Independent Validation of Combined NTT Fault Monitoring
================================================================
Audits and verifies:
1. Integrity of Phase 7I raw data (1,400 trials, 0 duplicates, 0 missing).
2. Native execution path coverage (5,376 fwd + 4,480 inv = 9,856 butterflies).
3. Public API fail-stop contract enforcement without internal status pointer.
4. Extended 16-class adversarial fault campaign (1,600 trials, strictly 0.00% undetected corruption).
5. Multi-run benchmark stability and bounded overhead.
6. Randomized-order constant-time timing distribution metrics.
"""

import json
import unittest
from pathlib import Path

class TestPhase7JIndependentValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent.parent.parent
        cls.audit_metrics_path = cls.root / "results" / "phase7j" / "processed" / "phase7j_audit_metrics.json"
        cls.extended_trials_path = cls.root / "results" / "phase7j" / "raw" / "phase7j_extended_trials.json"
        cls.validation_results_path = cls.root / "results" / "phase7j" / "processed" / "phase7j_validation_results.json"

        with open(cls.audit_metrics_path, "r") as f:
            cls.audit_data = json.load(f)

        with open(cls.extended_trials_path, "r") as f:
            cls.extended_trials = json.load(f)

        with open(cls.validation_results_path, "r") as f:
            cls.val_results = json.load(f)

    def test_01_phase7i_dataset_integrity_audit(self):
        """Verify Phase 7I raw trial records pass all integrity audits."""
        data = self.audit_data
        self.assertEqual(data["total_trials"], 1400)
        self.assertEqual(data["duplicate_ids"], 0)
        self.assertEqual(data["missing_ids"], 0)
        self.assertEqual(data["aggregate_outcomes"]["undetected_corrupt"], 0)
        self.assertAlmostEqual(data["transient_recovery"]["rate_pct"], 100.0, places=1)
        self.assertTrue(data["processed_file_verified"])

    def test_02_native_butterfly_count_and_full_coverage(self):
        """Verify 5,376 forward and 4,480 inverse butterflies (total 9,856) executed."""
        val = self.val_results
        self.assertEqual(val["forward_butterflies"], 5376)
        self.assertEqual(val["inverse_butterflies"], 4480)
        self.assertEqual(val["total_butterflies"], 9856)

    def test_03_extended_campaign_zero_undetected_corruption(self):
        """Verify 1,600 trials across 16 extended threat classes achieve 0.00% undetected corruption."""
        trials = self.extended_trials
        self.assertEqual(len(trials), 1600)

        outcomes = {}
        for t in trials:
            c = t["fault_class"]
            o = t["outcome"]
            if c not in outcomes:
                outcomes[c] = {"RECOVERED": 0, "SAFE_REJECT": 0, "BENIGN_EQUIV": 0, "UNDETECTED_CORRUPT": 0}
            outcomes[c][o] += 1

        self.assertEqual(len(outcomes), 16)
        total_und = sum(counts["UNDETECTED_CORRUPT"] for counts in outcomes.values())
        self.assertEqual(total_und, 0, f"Detected {total_und} uncontained corruptions!")

        # Verify specific classes
        self.assertEqual(outcomes["J01: Multi-Layer Forward Transient (L1-7)"]["RECOVERED"], 100)
        self.assertEqual(outcomes["J02: Multi-Layer Inverse Transient (L1-7)"]["RECOVERED"], 100)
        self.assertEqual(outcomes["J03: Multi-Bit Forward Arithmetic Perturbation"]["RECOVERED"], 100)
        self.assertEqual(outcomes["J04: Multi-Bit Inverse Arithmetic Perturbation"]["RECOVERED"], 100)
        self.assertEqual(outcomes["J05: Saved-Operand Shadow Register Corruption"]["SAFE_REJECT"], 100)
        self.assertEqual(outcomes["J09: Rollback-State / Retry-Path Fault"]["SAFE_REJECT"], 100)
        self.assertEqual(outcomes["J11: Combined Concurrent Forward + Inverse Fault"]["RECOVERED"], 100)
        self.assertEqual(outcomes["J12: Persistent Stuck-at Fault (Early Layer 1 Fwd)"]["SAFE_REJECT"], 100)
        self.assertEqual(outcomes["J13: Persistent Stuck-at Fault (Late Layer 7 Inv)"]["SAFE_REJECT"], 100)
        self.assertEqual(outcomes["J14: Public API Decapsulation NULL Status"]["SAFE_REJECT"], 100)
        self.assertEqual(outcomes["J16: Clean Execution Negative Control"]["BENIGN_EQUIV"], 100)

    def test_04_public_api_fail_stop_contract(self):
        """Verify public API calls with NULL status enforce safe rejection on persistent faults."""
        # Class J14 specifically runs mlkem768_dec(NULL) under persistent fault
        j14_trials = [t for t in self.extended_trials if "J14" in t["fault_class"]]
        self.assertEqual(len(j14_trials), 100)
        for t in j14_trials:
            self.assertEqual(t["outcome"], "SAFE_REJECT")

    def test_05_multi_run_benchmark_stability_and_overhead(self):
        """Verify multi-run benchmark latencies and overhead relative to baseline and DMR."""
        bench = self.val_results["benchmarks"]
        self.assertGreater(bench["baseline"]["mean_us"], 50.0)
        self.assertLess(bench["baseline"]["mean_us"], 90.0)

        # Combined overhead should be bounded well below DMR (typically 12% - 30%)
        comb_overhead = bench["combined"]["overhead_pct"]
        dmr_overhead = bench["dmr"]["overhead_pct"]
        self.assertGreater(comb_overhead, 10.0)
        self.assertLess(comb_overhead, 35.0)

        # DMR overhead should be > 100%
        self.assertGreater(dmr_overhead, 110.0)

    def test_06_randomized_timing_constant_time(self):
        """Verify randomized valid vs invalid ciphertext timing distribution."""
        timing = self.val_results["timing_assessment"]
        # Timing ratios should be within 5% of 1.0000x under system timer jitter
        self.assertAlmostEqual(timing["ratio_mean"], 1.0000, delta=0.05)
        self.assertAlmostEqual(timing["ratio_median"], 1.0000, delta=0.05)
        # Cohen's d must be negligible (< 0.20)
        self.assertLess(timing["cohens_d"], 0.20)

if __name__ == "__main__":
    unittest.main()
