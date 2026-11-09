"""ASTRA-Sec Phase 3: Unit Tests for Statistical Analysis Module."""

import unittest
from research.phase3_experimental_lab.analysis.stats import (
    compute_cohens_d,
    compute_distribution_metrics,
)


class TestLabStats(unittest.TestCase):
    def test_empty_list(self):
        m = compute_distribution_metrics([])
        self.assertEqual(m["count"], 0)
        self.assertEqual(m["mean"], 0.0)

    def test_known_distribution(self):
        # Array of numbers 1 to 10
        data = [float(x) for x in range(1, 11)]
        m = compute_distribution_metrics(data, confidence=0.99)
        self.assertEqual(m["count"], 10)
        self.assertAlmostEqual(m["mean"], 5.5, places=1)
        self.assertAlmostEqual(m["median"], 5.5, places=1)
        self.assertEqual(m["min"], 1.0)
        self.assertEqual(m["max"], 10.0)
        self.assertTrue(m["ci_lower"] < m["mean"] < m["ci_upper"])

    def test_cohens_d(self):
        g1 = [10.0, 11.0, 12.0, 10.5, 11.5]
        g2 = [20.0, 21.0, 22.0, 20.5, 21.5]
        d = compute_cohens_d(g1, g2)
        # Large negative effect size since g1 is much lower than g2
        self.assertTrue(d < -5.0)


if __name__ == "__main__":
    unittest.main()
