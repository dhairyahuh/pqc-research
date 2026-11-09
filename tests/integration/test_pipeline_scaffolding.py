"""Integration test validating end-to-end scaffolding and service lifecycle."""

import subprocess
import sys
import unittest
from astra_sec.core.config import AstraNodeConfig
from astra_sec.schema.messages import ApplicationDataUnit, CryptoEnvelopeHeader
from astra_sec.service.health import HealthService


class TestPipelineScaffolding(unittest.TestCase):
    """Verifies that the initial ASTRA-Sec scaffolding components interact correctly."""

    def test_end_to_end_scaffolding_flow(self) -> None:
        """Simulates message creation, header binding, and destination health validation."""
        # 1. Originator Node Config
        origin_config = AstraNodeConfig(node_eid="dtn://gsa/app", role="originator")
        dest_config = AstraNodeConfig(node_eid="dtn://gsb/app", role="destination")

        # 2. Originator creates application message (L1)
        adu = ApplicationDataUnit(
            source_eid=origin_config.node_eid,
            destination_eid=dest_config.node_eid,
            command_code=0x00FF,
            payload_bytes=b"PING_MISSION_PAYLOAD",
            priority=2,
        )

        # 3. Originator formats cryptographic envelope header (L2)
        header = CryptoEnvelopeHeader(
            sequence_id=1,
            ratchet_step=0,
            source_eid=adu.source_eid,
            destination_eid=adu.destination_eid,
            ttl_seconds=3600,
        )
        aad = header.to_aad_bytes()

        self.assertGreater(len(aad), 100)
        self.assertEqual(header.source_eid, "dtn://gsa/app")
        self.assertEqual(header.destination_eid, "dtn://gsb/app")

        # 4. Destination runs diagnostic check
        dest_health = HealthService(dest_config).get_health_status()
        self.assertIn(dest_health["status"], ("OK", "PASS", "DEGRADED"))

    def test_cli_health_execution(self) -> None:
        """Verifies CLI execution via subprocess."""
        result = subprocess.run(
            [sys.executable, "-m", "astra_sec.app", "health", "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn('"status": "OK"', result.stdout)


if __name__ == "__main__":
    unittest.main()
