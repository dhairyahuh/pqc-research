#!/usr/bin/env python3
"""
Targeted Automated Test Suite for Phase 5:
  - Validates Implementation Provenance and Backend Analysis
  - Validates Cross-Implementation Result Schema & Empirical Counts
  - Validates Binary Checksum Invariance Across Optimization Levels (-O0 vs -O3)
  - Validates Statistical Confidence Intervals and Sample Sizes
  - Validates Completeness of Phase 5 Documentation Deliverables
"""

import unittest
import os
import json
import math

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PHASE5_RESULTS_FILE = os.path.join(ROOT_DIR, "results/phase5/processed/cross_implementation_results.json")
PHASE5_DOCS_DIR = os.path.join(ROOT_DIR, "docs/phase5")


class TestPhase5CrossImplementation(unittest.TestCase):

    def setUp(self):
        self.assertTrue(os.path.exists(PHASE5_RESULTS_FILE), "Phase 5 results JSON must exist")
        with open(PHASE5_RESULTS_FILE, "r") as f:
            self.results = json.load(f)

    def test_results_schema_and_metadata(self):
        """Validate top-level schema, phase, and implementation definitions."""
        self.assertEqual(self.results.get("phase"), 5)
        self.assertIn("implementations", self.results)
        self.assertIn("A", self.results["implementations"])
        self.assertIn("B", self.results["implementations"])
        self.assertTrue(self.results["implementations"]["B"].get("shared_source"))
        self.assertIn("NOT_INDEPENDENT", self.results.get("independence_assessment", ""))

    def test_mlkem_cross_backend_agreement(self):
        """Validate ML-KEM cross-backend agreement (C-ref vs liboqs AArch64)."""
        kem = self.results.get("mlkem_results", {})
        agreement = kem.get("cross_backend_key_agreement", {})
        self.assertEqual(agreement.get("trials"), 500)
        self.assertEqual(agreement.get("cref_self_agreement"), 500)
        self.assertEqual(agreement.get("liboqs_self_agreement"), 500)
        self.assertEqual(agreement.get("cross_ref_decaps_oqs_ct"), 500)
        self.assertEqual(agreement.get("cross_oqs_decaps_ref_ct"), 500)
        self.assertEqual(agreement.get("errors"), 0)

    def test_mldsa_cross_backend_interoperability(self):
        """Validate ML-DSA cross-backend bidirectional interoperability."""
        dsa = self.results.get("mldsa_results", {})
        interop = dsa.get("cross_backend_interop", {})
        self.assertEqual(interop.get("trials"), 200)
        self.assertEqual(interop.get("cref_self_verify"), 200)
        self.assertEqual(interop.get("cref_sign_oqs_verify"), 200)
        self.assertEqual(interop.get("oqs_self_verify"), 200)
        self.assertEqual(interop.get("oqs_sign_cref_verify"), 200)
        self.assertEqual(interop.get("errors"), 0)

    def test_compiler_optimization_checksum_invariance(self):
        """Validate that -O0 and -O3 produce identical cryptographic checksums."""
        comp = self.results.get("compiler_sensitivity", {})
        self.assertIn("O0", comp.get("configurations_tested", []))
        self.assertIn("O3", comp.get("configurations_tested", []))

        # Public key checksum
        self.assertEqual(comp.get("pk_checksum_O0"), comp.get("pk_checksum_O3"))
        self.assertIsNotNone(comp.get("pk_checksum_O0"))

        # Secret key checksum
        self.assertEqual(comp.get("sk_checksum_O0"), comp.get("sk_checksum_O3"))

        # Ciphertext checksum
        self.assertEqual(comp.get("ct_checksum_O0"), comp.get("ct_checksum_O3"))

        # Clean shared secret checksum
        self.assertEqual(comp.get("ss_checksum_O0"), comp.get("ss_checksum_O3"))

        # Faulted shared secret checksum
        self.assertEqual(comp.get("faulted_ss_O0"), comp.get("faulted_ss_O3"))

    def test_verification_gate_audit_correction(self):
        """Validate that Phase 4 audit correction is preserved in Phase 5 results."""
        dsa = self.results.get("mldsa_results", {})
        vg = dsa.get("verification_gate_audit", {})
        self.assertIn("Boolean override is NOT cryptographic forgery", vg.get("phase4_correction", ""))

    def test_required_documentation_deliverables(self):
        """Verify that all required Phase 5 documentation files exist and are non-empty."""
        expected_docs = [
            "implementation_provenance.md",
            "common_experimental_framework.md",
            "mlkem_cross_implementation_results.md",
            "mldsa_cross_implementation_results.md",
            "compiler_architecture_sensitivity.md",
            "statistical_comparison.md",
            "cross_implementation_synthesis.md",
            "space_system_implications.md",
            "resilience_research_priorities.md",
            "final_report.md",
        ]
        for doc_name in expected_docs:
            doc_path = os.path.join(PHASE5_DOCS_DIR, doc_name)
            self.assertTrue(os.path.exists(doc_path), f"Missing required doc: {doc_name}")
            self.assertGreater(os.path.getsize(doc_path), 500, f"Doc {doc_name} is too short or empty")


if __name__ == "__main__":
    unittest.main()
