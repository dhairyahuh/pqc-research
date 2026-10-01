#!/usr/bin/env python3
"""
Targeted Automated Test Suite for Phase 6B:
  - Validates Independent Audit Result Schema and Values
  - Validates Universal Parity Cancellation Theorem (0% detection for intermediate t)
  - Validates DMR Common-Mode Failure Modes (0% detection for persistent/input faults)
  - Validates Completeness of Phase 6B Documentation Deliverables
"""

import unittest
import os
import sys
import json
import random

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from experiments.mathematics.test_ntt_butterfly_math import forward_ntt, Q, ZETAS, N

RESULTS_FILE = os.path.join(ROOT_DIR, "results/phase6b/processed/phase6b_audit_results.json")
DOCS_DIR = os.path.join(ROOT_DIR, "docs/phase6b")


def forward_ntt_with_t_fault(poly, target_layer, target_pair, delta):
    r = list(poly)
    k = 1
    length = 128
    layer = 1
    while length >= 2:
        for start in range(0, N, 2 * length):
            zeta = ZETAS[k]
            k += 1
            for j in range(start, start + length):
                t = (zeta * r[j + length]) % Q
                if layer == target_layer and j == target_pair:
                    t = (t + delta) % Q
                r[j + length] = (r[j] - t) % Q
                r[j] = (r[j] + t) % Q
        layer += 1
        length //= 2
    return r


class TestPhase6BAudit(unittest.TestCase):

    def setUp(self):
        self.assertTrue(os.path.exists(RESULTS_FILE), "Phase 6B audit results JSON must exist")
        with open(RESULTS_FILE, "r") as f:
            self.results = json.load(f)

    def test_audit_results_schema_and_critical_findings(self):
        """Validate that audit accurately records the blind spots and common-mode failures."""
        self.assertEqual(self.results.get("phase"), "6B")
        
        # NTT Invariant Audit
        ntt = self.results.get("ntt_invariant_audit", {})
        self.assertEqual(ntt.get("output_add_detection_pct"), 100.0)
        self.assertEqual(ntt.get("interm_t_detection_pct"), 0.0)
        self.assertEqual(ntt.get("twiddle_zeta_detection_pct"), 0.0)
        self.assertTrue(ntt.get("universal_parity_cancellation_confirmed"))

        # Duplicate Execution Audit
        dmr = self.results.get("duplicate_execution_audit", {})
        self.assertEqual(dmr.get("transient_detection_pct"), 100.0)
        self.assertEqual(dmr.get("persistent_detection_pct"), 0.0)
        self.assertEqual(dmr.get("input_corruption_detection_pct"), 0.0)
        self.assertTrue(dmr.get("common_mode_blind_spot_confirmed"))

    def test_universal_parity_cancellation_across_all_layers(self):
        """
        Formally verify that an intermediate multiplier fault t -> t + delta
        cancels identically in both even and odd projection sums across all 7 layers.
        """
        random.seed(1337)
        poly = [random.randint(0, Q - 1) for _ in range(256)]
        exp_even = (128 * poly[0]) % Q
        exp_odd  = (128 * poly[1]) % Q

        for layer in range(1, 8):
            for delta in [1, 10, 100, 500, 3328]:
                fault_ntt = forward_ntt_with_t_fault(poly, layer, 0, delta)
                sum_even = sum(fault_ntt[2 * i] for i in range(128)) % Q
                sum_odd  = sum(fault_ntt[2 * i + 1] for i in range(128)) % Q

                self.assertEqual(sum_even, exp_even, f"Layer {layer} even sum failed to cancel")
                self.assertEqual(sum_odd, exp_odd, f"Layer {layer} odd sum failed to cancel")

    def test_documentation_deliverables_completeness(self):
        """Verify that all required Phase 6B documentation deliverables exist and are populated."""
        required_docs = [
            "independent_audit.md",
            "ntt_invariant_coverage.md",
            "duplicate_execution_robustness.md",
            "multi_rail_robustness.md",
            "statistical_reanalysis.md",
            "spacecraft_model_sensitivity.md",
            "mldsa_claim_audit.md",
            "novelty_reassessment.md",
            "phase6b_final_report.md"
        ]
        for doc in required_docs:
            doc_path = os.path.join(DOCS_DIR, doc)
            self.assertTrue(os.path.exists(doc_path), f"Missing Phase 6B deliverable: {doc}")
            self.assertGreater(os.path.getsize(doc_path), 500, f"Deliverable too short: {doc}")


if __name__ == "__main__":
    unittest.main()
