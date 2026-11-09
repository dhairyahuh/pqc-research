"""Unit tests for ASTRA-Sec Diagnostic Health Service."""

import unittest
from astra_sec.core.config import AstraNodeConfig
from astra_sec.service.health import HealthService


class TestHealthService(unittest.TestCase):
    """Verifies diagnostic health evaluation and component status reporting."""

    def setUp(self) -> None:
        self.config = AstraNodeConfig(node_eid="dtn://gsa/app", role="originator")
        self.service = HealthService(self.config)

    def test_health_check_passes(self) -> None:
        """Verifies that health service reports OK status under valid environment."""
        status = self.service.get_health_status()
        self.assertIn(status["status"], ("OK", "PASS", "DEGRADED"))
        self.assertEqual(status["node_eid"], "dtn://gsa/app")
        self.assertEqual(status["role"], "originator")
        self.assertIn("components", status)
        self.assertEqual(status["components"]["configuration"]["status"], "PASS")
        self.assertEqual(status["components"]["storage"]["status"], "PASS")

    def test_health_check_keys(self) -> None:
        """Verifies dictionary keys in the health response."""
        status = self.service.get_health_status()
        expected_keys = {"status", "system", "version", "node_eid", "role", "uptime_seconds", "components"}
        self.assertTrue(expected_keys.issubset(status.keys()))


if __name__ == "__main__":
    unittest.main()
