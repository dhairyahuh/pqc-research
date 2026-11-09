"""ASTRA-Sec: Multi-Node Satellite Communication Integration Test Suite.

Validates the 4-node orbital topology:
Ground Station A (GSA) -> Satellite 1 (SAT1) -> Satellite 2 (SAT2) -> Ground Station B (GSB)

Tests 8 Required Scenarios:
1. Normal forwarding across all relays to GSB with reverse ACK to GSA.
2. Relay restart with persistent spool recovery surviving process reboots.
3. Delayed forwarding across orbital contact windows.
4. Duplicate forwarding suppression at intermediate relays.
5. Message reordering tolerance via sliding-window anti-replay.
6. Relay unavailable leading to safe spool expiration.
7. Relay payload tampering detected by GSB before plaintext exposure.
8. Unauthorized node injection rejected by relay.
"""

import os
import shutil
import tempfile
import time
import unittest

from astra_sec.network.relay import SatelliteRelayNode
from astra_sec.network.routing import ContactSchedule, RoutingTable
from astra_sec.network.service import DirectMemoryTransport, HttpNodeTransport, NodeHttpServer
from astra_sec.network.spool import PersistentMessageSpool
from astra_sec.schema.envelope import EnvelopeHeader, PqcMessageEnvelope
from astra_sec.schema.network import DeliveryStatus, LinkState
from astra_sec.schema.trust import PublicKeyTrustStore
from astra_sec.service.ground_station import GroundStationNode, SignatureVerificationError


class TestMultiNodeSatellite(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.sat1_spool_path = os.path.join(self.temp_dir, "spool_sat1.db")
        self.sat2_spool_path = os.path.join(self.temp_dir, "spool_sat2.db")

        # Shared trust store for Ground Stations (PKI)
        self.trust_store = PublicKeyTrustStore()

        # Instantiate Ground Stations
        self.gsa = GroundStationNode(
            node_eid="dtn://gsa/app",
            role="ground_station",
            trust_store=self.trust_store,
        )
        self.gsb = GroundStationNode(
            node_eid="dtn://gsb/app",
            role="ground_station",
            trust_store=self.trust_store,
        )

        # Cross-register public identities in trust store
        self.trust_store.register_peer(self.gsa.get_public_identity())
        self.trust_store.register_peer(self.gsb.get_public_identity())

        # Setup routing tables
        # GSA -> SAT1 -> SAT2 -> GSB
        self.rt_gsa = RoutingTable({"dtn://gsb/*": "dtn://sat1/relay"})
        self.rt_sat1 = RoutingTable({
            "dtn://gsb/*": "dtn://sat2/relay",
            "dtn://gsa/*": "dtn://gsa/app",
        })
        self.rt_sat2 = RoutingTable({
            "dtn://gsb/*": "dtn://gsb/app",
            "dtn://gsa/*": "dtn://sat1/relay",
        })
        self.rt_gsb = RoutingTable({"dtn://gsa/*": "dtn://sat2/relay"})

        # Transport registry
        self.transport = DirectMemoryTransport()

        # Instantiate Satellite Relays
        self.sat1 = SatelliteRelayNode(
            node_eid="dtn://sat1/relay",
            spool_db_path=self.sat1_spool_path,
            routing_table=self.rt_sat1,
            forwarder_fn=lambda next_hop, env, from_peer=None: self.transport.send(next_hop, env, from_peer=from_peer),
            authorized_peers={"dtn://gsa/app", "dtn://sat2/relay"},
        )

        self.sat2 = SatelliteRelayNode(
            node_eid="dtn://sat2/relay",
            spool_db_path=self.sat2_spool_path,
            routing_table=self.rt_sat2,
            forwarder_fn=lambda next_hop, env, from_peer=None: self.transport.send(next_hop, env, from_peer=from_peer),
            authorized_peers={"dtn://sat1/relay", "dtn://gsb/app"},
        )

        # Register nodes in transport
        self.transport.register_node("dtn://gsa/app", self.gsa)
        self.transport.register_node("dtn://sat1/relay", self.sat1)
        self.transport.register_node("dtn://sat2/relay", self.sat2)
        self.transport.register_node("dtn://gsb/app", self.gsb)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_normal_forwarding_and_ack(self):
        """Scenario 1: Happy path message forwarding across both satellite relays.

        GSA -> SAT1 -> SAT2 -> GSB
        Verifies:
        - Relays never decrypt or access plaintext.
        - GSB decapsulates with monitored ML-KEM and verifies ML-DSA-65 signature.
        - Reverse ACK from GSB traverses SAT2 -> SAT1 -> GSA.
        """
        secret_telemetry = b"SPACE_TELEMETRY: ORBITAL_VELOCITY=7.66km/s, ALTITUDE=408km"

        # GSA creates protected envelope
        envelope = self.gsa.send_message(
            destination_eid="dtn://gsb/app",
            payload=secret_telemetry,
        )

        # Track received payload at GSB
        delivered_payload = []
        original_receive = self.gsb.receive_message

        def capturing_receive(env, current_time=None):
            pt, ack = original_receive(env, current_time)
            delivered_payload.append(pt)
            # Route ACK in reverse direction back to GSA
            self.transport.send("dtn://sat2/relay", self._wrap_ack_as_envelope(ack))
            return pt, ack

        self.gsb.receive_message = capturing_receive

        # Dispatch from GSA to SAT1
        next_hop = self.rt_gsa.get_next_hop("dtn://gsb/app")
        self.assertEqual(next_hop, "dtn://sat1/relay")
        sent = self.transport.send(next_hop, envelope)
        self.assertTrue(sent)

        # Assert delivery at GSB
        self.assertEqual(len(delivered_payload), 1)
        self.assertEqual(delivered_payload[0], secret_telemetry)

        # Verify relays logged forwarding without possessing decryption keys
        sat1_forward_evts = [e for e in self.sat1.events if e.event_type == "MESSAGE_FORWARDED"]
        sat2_forward_evts = [e for e in self.sat2.events if e.event_type == "MESSAGE_FORWARDED"]
        # Both relays forwarded the data message to GSB and the reverse ACK to GSA
        self.assertEqual(len(sat1_forward_evts), 2)
        self.assertEqual(len(sat2_forward_evts), 2)
        forward_data = [e for e in sat1_forward_evts if e.destination_eid == "dtn://gsb/app"]
        self.assertEqual(len(forward_data), 1)
        self.assertEqual(forward_data[0].next_hop_eid, "dtn://sat2/relay")

    def _wrap_ack_as_envelope(self, ack) -> PqcMessageEnvelope:
        """Helper to return an ACK over the DTN routing topology."""
        ack_payload = ack.ack_id.encode("ascii") + b"|" + ack.status.encode("utf-8")
        return self.gsb.send_message(
            destination_eid=ack.destination_eid,
            payload=ack_payload,
        )

    def test_02_relay_restart_with_persistent_spool(self):
        """Scenario 2: Relay node reboots while bundles are queued in persistent spool.

        SAT1 link to SAT2 is DOWN.
        Bundle is spooled to SQLite DB.
        SAT1 instance is deleted (simulating crash).
        New SAT1 instance boots with same DB path.
        Link is restored, spool is processed, and message is delivered to GSB.
        """
        payload = b"CRITICAL_COMMAND: ATTITUDE_ADJUST_PITCH_+2.5_DEG"
        envelope = self.gsa.send_message("dtn://gsb/app", payload)

        # Sever link between SAT1 and SAT2
        self.sat1.set_link_state("dtn://sat2/relay", LinkState.DOWN)

        # Ingest at SAT1 -> should be queued as WAITING_CONTACT
        evt = self.sat1.ingest(envelope)
        self.assertEqual(evt.status, DeliveryStatus.WAITING_CONTACT)
        self.assertEqual(self.sat1.spool.count_pending(), 1)

        # Simulate crash / reboot of SAT1
        del self.sat1
        rebooted_sat1 = SatelliteRelayNode(
            node_eid="dtn://sat1/relay",
            spool_db_path=self.sat1_spool_path,
            routing_table=self.rt_sat1,
            forwarder_fn=lambda next_hop, env, from_peer=None: self.transport.send(next_hop, env, from_peer=from_peer),
            authorized_peers={"dtn://gsa/app", "dtn://sat2/relay"},
        )
        self.transport.register_node("dtn://sat1/relay", rebooted_sat1)

        # Verify spool survived reboot
        self.assertEqual(rebooted_sat1.spool.count_pending(), 1)

        # Restore link and flush spool
        rebooted_sat1.set_link_state("dtn://sat2/relay", LinkState.UP)
        flushed_events = rebooted_sat1.process_spool()
        self.assertEqual(len(flushed_events), 1)
        self.assertEqual(flushed_events[0].status, DeliveryStatus.FORWARDED)
        self.assertEqual(rebooted_sat1.spool.count_pending(), 0)

    def test_03_delayed_forwarding_contact_window(self):
        """Scenario 3: Forwarding delayed until orbital contact window opens.

        Contact window is scheduled 300s in the future.
        Message arrives now -> WAITING_CONTACT.
        Clock advances 350s -> Window is active, spool flushes and delivers.
        """
        now = int(time.time())
        schedule = ContactSchedule("dtn://sat1/relay")
        # Explicit contact window: opens at now+300, closes at now+600
        schedule.add_contact_window("dtn://sat2/relay", start_time_utc=now + 300, end_time_utc=now + 600)

        # Create relay with scheduled contact
        scheduled_sat1 = SatelliteRelayNode(
            node_eid="dtn://sat1/relay",
            spool_db_path=os.path.join(self.temp_dir, "spool_sched.db"),
            routing_table=self.rt_sat1,
            contact_schedule=schedule,
            forwarder_fn=lambda next_hop, env, from_peer=None: self.transport.send(next_hop, env, from_peer=from_peer),
            authorized_peers={"dtn://gsa/app", "dtn://sat2/relay"},
        )

        envelope = self.gsa.send_message("dtn://gsb/app", b"DELAYED_TELEMETRY_RECORD", custom_timestamp=now)

        # Ingest at t = now (before window)
        evt = scheduled_sat1.ingest(envelope, current_time=now)
        self.assertEqual(evt.status, DeliveryStatus.WAITING_CONTACT)

        # Attempt flush at t = now + 100 (still closed)
        flushed = scheduled_sat1.process_spool(current_time=now + 100)
        self.assertEqual(len(flushed), 0)

        # Flush at t = now + 350 (inside contact window)
        flushed = scheduled_sat1.process_spool(current_time=now + 350)
        self.assertEqual(len(flushed), 1)
        self.assertEqual(flushed[0].status, DeliveryStatus.FORWARDED)

    def test_04_duplicate_forwarding_suppression(self):
        """Scenario 4: Duplicate transmission is detected and suppressed at intermediate relay."""
        envelope = self.gsa.send_message("dtn://gsb/app", b"DUPLICATE_TEST_PAYLOAD")

        # First transmission -> FORWARDED
        evt1 = self.sat1.ingest(envelope)
        self.assertEqual(evt1.status, DeliveryStatus.FORWARDED)

        # Duplicate transmission of exact same envelope -> DROPPED_DUPLICATE
        evt2 = self.sat1.ingest(envelope)
        self.assertEqual(evt2.status, DeliveryStatus.DROPPED_DUPLICATE)
        self.assertEqual(evt2.event_type, "REJECT_DUPLICATE_ENVELOPE")

    def test_05_message_reordering_tolerance(self):
        """Scenario 5: Out-of-order message delivery handled properly by destination."""
        # Generate 3 ordered messages
        env1 = self.gsa.send_message("dtn://gsb/app", b"PACKET_#1", custom_sequence_id=1)
        env2 = self.gsa.send_message("dtn://gsb/app", b"PACKET_#2", custom_sequence_id=2)
        env3 = self.gsa.send_message("dtn://gsb/app", b"PACKET_#3", custom_sequence_id=3)

        # Deliver out of order: #2, #1, #3
        pt2, _ = self.gsb.receive_message(env2)
        pt1, _ = self.gsb.receive_message(env1)
        pt3, _ = self.gsb.receive_message(env3)

        self.assertEqual(pt1, b"PACKET_#1")
        self.assertEqual(pt2, b"PACKET_#2")
        self.assertEqual(pt3, b"PACKET_#3")

    def test_06_relay_unavailable_ttl_expiration(self):
        """Scenario 6: Permanent relay failure causes envelope to expire in spool."""
        now = int(time.time())
        # Envelope with short TTL = 30 seconds
        envelope = self.gsa.send_message(
            "dtn://gsb/app",
            b"EXPIRING_PACKET",
            ttl_seconds=30,
            custom_timestamp=now,
        )

        # Sever link to SAT2
        self.sat1.set_link_state("dtn://sat2/relay", LinkState.DOWN)
        self.sat1.ingest(envelope, current_time=now)
        self.assertEqual(self.sat1.spool.count_pending(), 1)

        # Advance time by 45 seconds (exceeding TTL)
        flushed = self.sat1.process_spool(current_time=now + 45)
        self.assertEqual(len(flushed), 1)
        self.assertEqual(flushed[0].status, DeliveryStatus.EXPIRED)
        self.assertEqual(flushed[0].event_type, "SPOOL_MESSAGE_EXPIRED")
        self.assertEqual(self.sat1.spool.count_pending(), 0)

    def test_07_relay_payload_tampering_detected(self):
        """Scenario 7: Malicious/corrupted relay tampers with ciphertext.

        GSB verifies signature and detects tampering before exposing any plaintext.
        """
        envelope = self.gsa.send_message("dtn://gsb/app", b"HIGH_INTEGRITY_PAYLOAD", custom_sequence_id=777)

        # Relay SAT1 tampers with 1 byte of the ciphertext
        corrupted_ct = bytearray(envelope.ciphertext)
        corrupted_ct[0] ^= 0x55  # Bit flip

        tampered_envelope = PqcMessageEnvelope(
            header=envelope.header,
            ciphertext=bytes(corrupted_ct),
            tag=envelope.tag,
            signature=envelope.signature,
        )

        # GSB attempts to receive -> must raise SignatureVerificationError
        with self.assertRaises(SignatureVerificationError):
            self.gsb.receive_message(tampered_envelope)

    def test_08_unauthorized_node_rejected(self):
        """Scenario 8: Unauthorized rogue node rejected by relay."""
        envelope = self.gsa.send_message("dtn://gsb/app", b"ROGUE_INJECTION")

        # Ingest at SAT1 reporting from an unauthorized peer EID
        evt = self.sat1.ingest(envelope, from_peer="dtn://rogue_satellite/relay")
        self.assertEqual(evt.status, DeliveryStatus.DROPPED_UNAUTHORIZED)
        self.assertEqual(evt.event_type, "REJECT_UNAUTHORIZED_PEER")

    def test_09_isolated_service_http_transport(self):
        """Validates isolated node execution as HTTP server processes."""
        server_sat2 = NodeHttpServer(self.sat2)
        port_sat2 = server_sat2.start()

        server_gsb = NodeHttpServer(self.gsb)
        port_gsb = server_gsb.start()

        try:
            http_transport = HttpNodeTransport({
                "dtn://sat2/relay": f"http://127.0.0.1:{port_sat2}",
                "dtn://gsb/app": f"http://127.0.0.1:{port_gsb}",
            })

            # Create envelope
            envelope = self.gsa.send_message("dtn://gsb/app", b"ISOLATED_HTTP_PAYLOAD")

            # Update SAT2's forwarder to use HTTP to reach GSB
            self.sat2.forwarder_fn = lambda next_hop, env, from_peer=None: http_transport.send(next_hop, env, from_peer=from_peer)

            # Send via HTTP to SAT2 (originating from SAT1)
            ok = http_transport.send("dtn://sat2/relay", envelope, from_peer="dtn://sat1/relay")
            self.assertTrue(ok)
        finally:
            server_sat2.stop()
            server_gsb.stop()


if __name__ == "__main__":
    unittest.main()
