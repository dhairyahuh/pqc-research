"""Integration Test Suite: Monitored ML-KEM Fault Resilience in ASTRA-Sec Messaging."""

import unittest

from astra_sec.crypto.mlkem_monitored import MonitoredMlkemAdapter
from astra_sec.schema.trust import PublicKeyTrustStore
from astra_sec.service.ground_station import (
    DecapsulationFaultError,
    GroundStationNode,
)


class TestFaultResilienceIntegration(unittest.TestCase):
    """End-to-end integration tests verifying fault resilience across Ground Station A and B."""

    def setUp(self):
        self.trust_a = PublicKeyTrustStore()
        self.trust_b = PublicKeyTrustStore()

        self.monitored_kem_b = MonitoredMlkemAdapter()
        self.monitored_kem_b.reset_faults()

        self.gsa = GroundStationNode(
            node_eid="dtn://gsa/app",
            role="ground_station",
            trust_store=self.trust_a,
        )
        self.gsb = GroundStationNode(
            node_eid="dtn://gsb/app",
            role="ground_station",
            kem_adapter=self.monitored_kem_b,
            trust_store=self.trust_b,
        )

        # Exchange trusted public keys
        self.trust_a.register_peer(self.gsb.get_public_identity())
        self.trust_b.register_peer(self.gsa.get_public_identity())

    def tearDown(self):
        self.monitored_kem_b.reset_faults()

    def test_01_clean_messaging_telemetry(self):
        """Scenario 1: Clean messaging records zero fault counters in FDIR telemetry."""
        payload = b"Telemetry: Systems nominal, battery at 98.4%."
        envelope = self.gsa.send_message("dtn://gsb/app", payload)

        decrypted, ack = self.gsb.receive_message(envelope)
        self.assertEqual(decrypted, payload)
        self.assertEqual(ack.status, "SUCCESS")

        telem = self.gsb.get_fdir_telemetry()
        self.assertEqual(telem.transient_recoveries, 0)
        self.assertEqual(telem.persistent_fail_stops, 0)
        self.assertEqual(telem.bundles_forwarded, 1)

    def test_02_transient_fault_recovery_in_flight(self):
        """Scenario 2: Single-event upset during decapsulation is recovered without packet loss."""
        # Arm transient fault in GSB's decapsulation engine: Layer 2, Butterfly 17, Bit 3
        self.monitored_kem_b.inject_op_twiddle_fault(layer=2, butterfly=17, bit=3, persistent=False)

        payload = b"Critical Flight Maneuver: Execute burn at T+04:30."
        envelope = self.gsa.send_message("dtn://gsb/app", payload)

        # Message must successfully decrypt despite transient fault
        decrypted, ack = self.gsb.receive_message(envelope)
        self.assertEqual(decrypted, payload)
        self.assertEqual(ack.status, "SUCCESS")
        self.assertTrue(self.gsa.verify_acknowledgment(ack, envelope))

        # Verify FDIR telemetry captured the transient recovery
        telem = self.gsb.get_fdir_telemetry()
        self.assertGreater(telem.transient_recoveries, 0)
        self.assertEqual(telem.persistent_fail_stops, 0)
        self.assertEqual(telem.bundles_forwarded, 1)

    def test_03_persistent_fault_fail_stop_suppression(self):
        """Scenario 3: Persistent hardware fault engages fail-stop suppression; plaintext never leaks."""
        # Arm persistent fault in GSB's decapsulation engine: Layer 3, Butterfly 25, Bit 5
        self.monitored_kem_b.inject_op_twiddle_fault(layer=3, butterfly=25, bit=5, persistent=True)

        payload = b"Top Secret Payload: Never expose if hardware corrupted."
        envelope = self.gsa.send_message("dtn://gsb/app", payload)

        # Ingestion must strictly fail with DecapsulationFaultError
        with self.assertRaises(DecapsulationFaultError):
            self.gsb.receive_message(envelope)

        # Verify FDIR telemetry captured the persistent fail-stop
        telem = self.gsb.get_fdir_telemetry()
        self.assertGreater(telem.persistent_fail_stops, 0)
        self.assertEqual(telem.bundles_rejected, 1)


if __name__ == "__main__":
    unittest.main()
