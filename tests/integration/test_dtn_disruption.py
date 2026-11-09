"""ASTRA-Sec: DTN & Store-and-Forward Integration Test Suite (Prompt 08).

Validates RFC 9171 (BPv7), RFC 9172 (BPSec), and Store-and-Forward Disruption Resilience:
1. Network available (happy path store-and-forward across 4 nodes)
2. Network unavailable (held in persistent spool)
3. Delayed contact (contact window opens later)
4. Message queue (multiple bundles queued and drained sequentially)
5. Satellite relay restart (spool survives reboot)
6. Bundle duplication (duplicate primary block suppressed)
7. Expired bundle (lifetime expired bundle pruned)
8. Invalid bundle security (BPSec BIB tampering rejected)
9. Valid message delivered after reconnection (end-to-end cryptographic integrity intact)
"""

import os
import shutil
import tempfile
import time
import unittest

from astra_sec.dtn.adapter import (
    AstraDtnBridge,
    BpSecVerificationError,
    BpV7ExpiredError,
    DtnSpoolRouter,
)
from astra_sec.dtn.bpsec import BpSecSecurityContext
from astra_sec.dtn.bpv7 import BpV7Bundle, CanonicalBlock, PrimaryBlock
from astra_sec.dtn.contact_plan import IonContactPlan
from astra_sec.schema.network import DeliveryStatus
from astra_sec.schema.trust import PublicKeyTrustStore
from astra_sec.service.ground_station import GroundStationNode


class TestDtnDisruption(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.sat1_spool = os.path.join(self.temp_dir, "spool_dtn_sat1.db")
        self.sat2_spool = os.path.join(self.temp_dir, "spool_dtn_sat2.db")

        # Trust store & Ground Stations
        self.trust_store = PublicKeyTrustStore()
        self.gsa = GroundStationNode("dtn://gsa/app", trust_store=self.trust_store)
        self.gsb = GroundStationNode("dtn://gsb/app", trust_store=self.trust_store)
        self.trust_store.register_peer(self.gsa.get_public_identity())
        self.trust_store.register_peer(self.gsb.get_public_identity())

        # Contact plan
        self.contact_plan = IonContactPlan()
        now = int(time.time())
        # Default continuous contacts: 1 (GSA) <-> 2 (SAT1) <-> 3 (SAT2) <-> 4 (GSB)
        self.contact_plan.add_contact(1, 2, now - 100, now + 10000)
        self.contact_plan.add_contact(2, 3, now - 100, now + 10000)
        self.contact_plan.add_contact(3, 4, now - 100, now + 10000)
        self.contact_plan.add_contact(4, 3, now - 100, now + 10000)
        self.contact_plan.add_contact(3, 2, now - 100, now + 10000)
        self.contact_plan.add_contact(2, 1, now - 100, now + 10000)

        # In-memory routing dispatch
        self.delivered_bundles = []

        def forward_sat2_to_gsb(target_eid, bundle):
            self.delivered_bundles.append(bundle)
            return True

        self.sat2_router = DtnSpoolRouter(
            node_eid="dtn://sat2/relay",
            node_number=3,
            spool_db_path=self.sat2_spool,
            contact_plan=self.contact_plan,
            forwarder_fn=forward_sat2_to_gsb,
        )

        def forward_sat1_to_sat2(target_eid, bundle):
            evt = self.sat2_router.ingest_bundle(bundle, next_hop_eid="dtn://gsb/app", next_hop_node=4)
            return evt.status in (DeliveryStatus.FORWARDED, DeliveryStatus.WAITING_CONTACT)

        self.sat1_router = DtnSpoolRouter(
            node_eid="dtn://sat1/relay",
            node_number=2,
            spool_db_path=self.sat1_spool,
            contact_plan=self.contact_plan,
            forwarder_fn=forward_sat1_to_sat2,
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_network_available_store_and_forward(self):
        """Scenario 1: Happy path BPv7 bundle transmission across multi-hop space network."""
        payload = b"MISSION_DATA: RADIATION_MONITOR_LEVEL_NOMINAL"
        envelope = self.gsa.send_message("dtn://gsb/app", payload)
        bundle = AstraDtnBridge.envelope_to_bundle(envelope)

        # Ingest at SAT1 -> forwards to SAT2 -> delivers to GSB
        evt = self.sat1_router.ingest_bundle(bundle, next_hop_eid="dtn://sat2/relay", next_hop_node=3)
        self.assertEqual(evt.status, DeliveryStatus.FORWARDED)
        self.assertEqual(len(self.delivered_bundles), 1)

        # GSB unwraps bundle and decrypts
        delivered_bundle = self.delivered_bundles[0]
        unwrapped_envelope = AstraDtnBridge.bundle_to_envelope(delivered_bundle)
        plaintext, ack = self.gsb.receive_message(unwrapped_envelope)

        self.assertEqual(plaintext, payload)
        self.assertEqual(ack.status, "SUCCESS")

    def test_02_network_unavailable_spooled(self):
        """Scenario 2: Inter-satellite crosslink unavailable; bundle held in persistent spool."""
        # Create plan with no contact between SAT1 (node 2) and SAT2 (node 3)
        isolated_plan = IonContactPlan()
        isolated_sat1 = DtnSpoolRouter(
            node_eid="dtn://sat1/relay",
            node_number=2,
            spool_db_path=os.path.join(self.temp_dir, "spool_iso.db"),
            contact_plan=isolated_plan,
        )

        envelope = self.gsa.send_message("dtn://gsb/app", b"HOLD_IN_SPOOL")
        bundle = AstraDtnBridge.envelope_to_bundle(envelope)

        evt = isolated_sat1.ingest_bundle(bundle, next_hop_eid="dtn://sat2/relay", next_hop_node=3)
        self.assertEqual(evt.status, DeliveryStatus.WAITING_CONTACT)
        self.assertEqual(isolated_sat1.count_pending(), 1)

    def test_03_delayed_contact_window(self):
        """Scenario 3: Contact window scheduled 300 seconds in the future."""
        now = int(time.time())
        sched_plan = IonContactPlan()
        sched_plan.add_contact(2, 3, start_time=now + 300, stop_time=now + 600)

        received_at_sat2 = []
        sched_sat1 = DtnSpoolRouter(
            node_eid="dtn://sat1/relay",
            node_number=2,
            spool_db_path=os.path.join(self.temp_dir, "spool_delayed.db"),
            contact_plan=sched_plan,
            forwarder_fn=lambda target, b: received_at_sat2.append(b) or True,
        )

        envelope = self.gsa.send_message("dtn://gsb/app", b"DELAYED_CONTACT_DATA")
        bundle = AstraDtnBridge.envelope_to_bundle(envelope)

        # Ingest at now -> held in spool
        evt = sched_sat1.ingest_bundle(bundle, next_hop_eid="dtn://sat2/relay", next_hop_node=3, current_time_unix=now)
        self.assertEqual(evt.status, DeliveryStatus.WAITING_CONTACT)
        self.assertEqual(len(received_at_sat2), 0)

        # Flush at now + 350 -> inside window
        flushed = sched_sat1.process_spool(current_time_unix=now + 350)
        self.assertEqual(len(flushed), 1)
        self.assertEqual(flushed[0].status, DeliveryStatus.FORWARDED)
        self.assertEqual(len(received_at_sat2), 1)

    def test_04_message_queue_drain(self):
        """Scenario 4: Multiple bundles queued while link is down, then drained in FIFO order."""
        plan = IonContactPlan()  # Link closed initially
        queued_bundles = []
        router = DtnSpoolRouter(
            node_eid="dtn://sat1/relay",
            node_number=2,
            spool_db_path=os.path.join(self.temp_dir, "spool_queue.db"),
            contact_plan=plan,
            forwarder_fn=lambda t, b: queued_bundles.append(b) or True,
        )

        # Enqueue 5 bundles
        for i in range(5):
            env = self.gsa.send_message("dtn://gsb/app", f"BUNDLE_RECORD_{i}".encode("utf-8"))
            b = AstraDtnBridge.envelope_to_bundle(env, sequence_number=i + 1)
            router.ingest_bundle(b, next_hop_eid="dtn://sat2/relay", next_hop_node=3)

        self.assertEqual(router.count_pending(), 5)

        # Open link
        now = int(time.time())
        plan.add_contact(2, 3, now - 10, now + 1000)

        # Drain queue
        flushed = router.process_spool(now)
        self.assertEqual(len(flushed), 5)
        self.assertEqual(len(queued_bundles), 5)
        self.assertEqual(router.count_pending(), 0)

    def test_05_satellite_relay_restart_survives(self):
        """Scenario 5: Satellite router restarts while bundles are in persistent non-volatile spool."""
        plan = IonContactPlan()  # No contact initially
        reboot_db = os.path.join(self.temp_dir, "spool_reboot.db")
        r1 = DtnSpoolRouter(
            node_eid="dtn://sat1/relay",
            node_number=2,
            spool_db_path=reboot_db,
            contact_plan=plan,
        )

        env = self.gsa.send_message("dtn://gsb/app", b"SURVIVE_REBOOT")
        b = AstraDtnBridge.envelope_to_bundle(env)
        r1.ingest_bundle(b, next_hop_eid="dtn://sat2/relay", next_hop_node=3)
        self.assertEqual(r1.count_pending(), 1)

        # Simulate crash / reboot: delete r1 and create r2 pointing to same DB
        del r1
        forwarded = []
        now = int(time.time())
        plan.add_contact(2, 3, now - 10, now + 1000)  # Link restored

        r2 = DtnSpoolRouter(
            node_eid="dtn://sat1/relay",
            node_number=2,
            spool_db_path=reboot_db,
            contact_plan=plan,
            forwarder_fn=lambda t, b: forwarded.append(b) or True,
        )
        self.assertEqual(r2.count_pending(), 1)

        # Process spool after restart
        flushed = r2.process_spool(now)
        self.assertEqual(len(flushed), 1)
        self.assertEqual(len(forwarded), 1)
        self.assertEqual(r2.count_pending(), 0)

    def test_06_bundle_duplication_suppressed(self):
        """Scenario 6: Duplicate BPv7 bundle suppressed at relay."""
        env = self.gsa.send_message("dtn://gsb/app", b"DUP_BUNDLE_TEST")
        bundle = AstraDtnBridge.envelope_to_bundle(env)

        evt1 = self.sat1_router.ingest_bundle(bundle, next_hop_eid="dtn://sat2/relay", next_hop_node=3)
        self.assertEqual(evt1.status, DeliveryStatus.FORWARDED)

        # Ingest identical bundle
        evt2 = self.sat1_router.ingest_bundle(bundle, next_hop_eid="dtn://sat2/relay", next_hop_node=3)
        self.assertEqual(evt2.status, DeliveryStatus.DROPPED_DUPLICATE)

    def test_07_expired_bundle_pruned(self):
        """Scenario 7: Bundle expires in spool while waiting for contact."""
        now = int(time.time())
        plan = IonContactPlan()  # Link down
        router = DtnSpoolRouter(
            node_eid="dtn://sat1/relay",
            node_number=2,
            spool_db_path=os.path.join(self.temp_dir, "spool_exp.db"),
            contact_plan=plan,
        )

        env = self.gsa.send_message("dtn://gsb/app", b"EXPIRE_ME")
        # Lifetime = 10 seconds
        bundle = AstraDtnBridge.envelope_to_bundle(env, lifetime_seconds=10)

        router.ingest_bundle(bundle, next_hop_eid="dtn://sat2/relay", next_hop_node=3, current_time_unix=now)
        self.assertEqual(router.count_pending(), 1)

        # Advance time by 20 seconds
        flushed = router.process_spool(current_time_unix=now + 20)
        self.assertEqual(len(flushed), 1)
        self.assertEqual(flushed[0].status, DeliveryStatus.EXPIRED)
        self.assertEqual(router.count_pending(), 0)

    def test_08_invalid_bpsec_security_rejected(self):
        """Scenario 8: Invalid or tampered RFC 9172 BPSec BIB rejected before application layer."""
        env = self.gsa.send_message("dtn://gsb/app", b"BPSEC_INTEGRITY_CHECK")
        bib_key = b"A" * 32
        bundle = AstraDtnBridge.envelope_to_bundle(env, bib_key=bib_key)

        # Verify valid unwrapping
        unwrapped = AstraDtnBridge.bundle_to_envelope(bundle, bib_key=bib_key)
        self.assertIsNotNone(unwrapped)

        # Corrupt the payload bytes
        corrupted_payload = bytearray(bundle.get_payload())
        corrupted_payload[0] ^= 0xFF
        corrupted_bundle = BpV7Bundle(
            primary_block=bundle.primary,
            payload_data=bytes(corrupted_payload),
            extension_blocks=bundle.extension_blocks,
        )

        # Attempting to unwrap must fail with BpSecVerificationError
        with self.assertRaises(BpSecVerificationError):
            AstraDtnBridge.bundle_to_envelope(corrupted_bundle, bib_key=bib_key)

    def test_09_valid_message_delivered_after_reconnection(self):
        """Scenario 9: Complete mission recovery cycle across network outage."""
        secret_command = b"FLIGHT_CRITICAL: EXECUTE_THRUST_VECTOR_ALIGNMENT_MANEUVER"
        envelope = self.gsa.send_message("dtn://gsb/app", secret_command)
        bundle = AstraDtnBridge.envelope_to_bundle(envelope)

        # Link is down
        plan = IonContactPlan()
        delivered = []
        router = DtnSpoolRouter(
            node_eid="dtn://sat1/relay",
            node_number=2,
            spool_db_path=os.path.join(self.temp_dir, "spool_recovery.db"),
            contact_plan=plan,
            forwarder_fn=lambda t, b: delivered.append(b) or True,
        )

        now = int(time.time())
        # Ingest during outage
        router.ingest_bundle(bundle, next_hop_eid="dtn://sat2/relay", next_hop_node=3, current_time_unix=now)
        self.assertEqual(router.count_pending(), 1)
        self.assertEqual(len(delivered), 0)

        # Link restores at now + 120s
        plan.add_contact(2, 3, now + 100, now + 500)
        flushed = router.process_spool(current_time_unix=now + 120)
        self.assertEqual(len(flushed), 1)
        self.assertEqual(len(delivered), 1)

        # Delivered to GSB: unwrap and verify end-to-end
        unwrapped = AstraDtnBridge.bundle_to_envelope(delivered[0])
        plaintext, ack = self.gsb.receive_message(unwrapped)

        self.assertEqual(plaintext, secret_command)
        self.assertTrue(self.gsa.verify_acknowledgment(ack, envelope))


if __name__ == "__main__":
    unittest.main()
