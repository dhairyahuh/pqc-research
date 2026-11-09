"""Unit tests for ASTRA-Sec Configuration Management."""

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from astra_sec.core.config import AstraNodeConfig, load_node_config
from astra_sec.core.exceptions import ConfigurationError


class TestAstraConfig(unittest.TestCase):
    """Verifies configuration loading, schema validation, and error handling."""

    def test_default_config_validity(self) -> None:
        """Verifies that default configuration initializes with valid parameters."""
        config = AstraNodeConfig()
        self.assertEqual(config.node_eid, "dtn://gsa/app")
        self.assertEqual(config.role, "originator")
        self.assertEqual(config.listen_port, 4556)
        self.assertEqual(config.health_port, 8080)
        self.assertEqual(config.ratchet_interval_bundles, 100)
        self.assertEqual(config.bundle_ttl_seconds, 86400)

    def test_invalid_node_eid_rejected(self) -> None:
        """Verifies that non-DTN URIs raise ValueError."""
        with self.assertRaises(ValueError):
            AstraNodeConfig(node_eid="http://invalid.com/app")

    def test_invalid_role_rejected(self) -> None:
        """Verifies that unknown roles raise ValueError."""
        with self.assertRaises(ValueError):
            AstraNodeConfig(role="unauthorized_role")

    def test_env_file_loading(self) -> None:
        """Verifies that settings are correctly parsed from an environment file."""
        with TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env.test"
            env_file.write_text(
                "ASTRA_NODE_EID=dtn://sat1/relay\n"
                "ASTRA_NODE_ROLE=relay\n"
                "ASTRA_LISTEN_PORT=4558\n"
                "ASTRA_LOG_LEVEL=DEBUG\n",
                encoding="utf-8",
            )
            # Temporarily clear os.environ overrides
            for k in ["ASTRA_NODE_EID", "ASTRA_NODE_ROLE", "ASTRA_LISTEN_PORT", "ASTRA_LOG_LEVEL"]:
                os.environ.pop(k, None)

            config = load_node_config(env_file)
            self.assertEqual(config.node_eid, "dtn://sat1/relay")
            self.assertEqual(config.role, "relay")
            self.assertEqual(config.listen_port, 4558)
            self.assertEqual(config.log_level, "DEBUG")


if __name__ == "__main__":
    unittest.main()
