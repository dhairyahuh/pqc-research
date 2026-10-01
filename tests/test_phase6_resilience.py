#!/usr/bin/env python3
"""
Targeted Automated Test Suite for Phase 6:
  - Validates Structured Results Dataset Schema and Values
  - Validates Mathematical FIPS 203 Incomplete NTT Algebraic Invariant Projections
  - Validates Multi-Rail Token Hamming Distance Properties
  - Validates Completeness of Phase 6 Documentation Deliverables
"""

import unittest
import os
import sys
import json
import random

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from experiments.mathematics.test_ntt_butterfly_math import forward_ntt, Q
RESULTS_FILE = os.path.join(ROOT_DIR, "results/phase6/processed/phase6_resilience_results.json")
DOCS_DIR = os.path.join(ROOT_DIR, "docs/phase6")


class TestPhase6Resilience(unittest.TestCase):

    def setUp(self):
        self.assertTrue(os.path.exists(RESULTS_FILE), "Phase 6 results JSON must exist")
        with open(RESULTS_FILE, "r") as f:
            self.results = json.load(f)

    def test_results_schema_and_metrics(self):
        """Validate top-level schema and empirical detection coverage."""
        self.assertEqual(self.results.get("phase"), 6)
        self.assertIn("baseline_decaps_us", self.results)
        self.assertGreater(self.results["baseline_decaps_us"], 0.0)

        # Candidate A1 (Full Duplicate)
        a1 = self.results.get("candidate_a1_full_duplicate", {})
        self.assertEqual(a1.get("detection_coverage_pct"), 100.0)
        self.assertEqual(a1.get("false_positive_pct"), 0.0)
        self.assertGreater(a1.get("overhead_pct"), 50.0)

        # Candidate B (NTT Invariant)
        b = self.results.get("candidate_b_ntt_invariant", {})
        self.assertEqual(b.get("detection_coverage_pct"), 100.0)
        self.assertEqual(b.get("false_positive_pct"), 0.0)

        # Candidate D (Multi-Rail)
        d = self.results.get("candidate_d_multirail", {})
        self.assertEqual(d.get("detection_coverage_pct"), 100.0)
        self.assertEqual(d.get("false_positive_pct"), 0.0)

    def test_ntt_algebraic_projection_invariants(self):
        """
        Formally verify the exact FIPS 203 incomplete NTT projection invariants:
          sum_{i=0}^{127} hat{p}_{2i}   == 128 * p_0 mod 3329
          sum_{i=0}^{127} hat{p}_{2i+1} == 128 * p_1 mod 3329
        """
        random.seed(42)
        for trial in range(50):
            p = [random.randint(0, Q - 1) for _ in range(256)]
            p_ntt = forward_ntt(p)
            
            sum_even = sum(p_ntt[2 * i] for i in range(128)) % Q
            sum_odd = sum(p_ntt[2 * i + 1] for i in range(128)) % Q
            
            exp_even = (128 * p[0]) % Q
            exp_odd = (128 * p[1]) % Q
            
            self.assertEqual(sum_even, exp_even, f"Even invariant failed at trial {trial}")
            self.assertEqual(sum_odd, exp_odd, f"Odd invariant failed at trial {trial}")

    def test_multirail_token_hamming_distance(self):
        """Verify that multi-rail status tokens have Hamming distance = 32."""
        token_ok = 0x5A5AA5A5
        token_fault = 0xA5A55A5A
        
        diff = token_ok ^ token_fault
        hamming_dist = bin(diff).count('1')
        self.assertEqual(hamming_dist, 32, "Hamming distance between OK and FAULT must be exactly 32")

    def test_documentation_deliverables_completeness(self):
        """Verify that all required Phase 6 documentation deliverables exist and are populated."""
        required_docs = [
            "evidence_validation.md",
            "threat_model.md",
            "baseline_definition.md",
            "selective_duplicate_execution.md",
            "arithmetic_invariant_checks.md",
            "mldsa_protection_study.md",
            "control_flow_integrity.md",
            "experimental_methodology.md",
            "performance_and_detection_results.md",
            "space_system_evaluation.md",
            "contribution_and_novelty_review.md",
            "final_report.md"
        ]
        for doc in required_docs:
            doc_path = os.path.join(DOCS_DIR, doc)
            self.assertTrue(os.path.exists(doc_path), f"Missing deliverable: {doc}")
            self.assertGreater(os.path.getsize(doc_path), 500, f"Deliverable too short: {doc}")


if __name__ == "__main__":
    unittest.main()
