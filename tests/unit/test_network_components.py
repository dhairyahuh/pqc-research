"""Unit tests for ASTRA-Sec network components (routing, spool, relay, contact schedule)."""

import os
import shutil
import tempfile
import time
import unittest

from astra_sec.network.relay import SatelliteRelayNode
from astra_sec.network.routing import ContactSchedule, RoutingTable
from astra_sec.network.service import DirectMemoryTransport
from astra_sec.network.spool import PersistentMessageSpool
from astra_sec.schema.envelope import EnvelopeHeader, PqcMessageEnvelope
from astra_sec.schema.network import DeliveryStatus, LinkState


class TestNetworkComponents(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_spool.db")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_dummy_envelope(self, env_id: str, src: str, dst: str, ttl: int = 3600) -> PqcMessageEnvelope:
        header = EnvelopeHeader(
            envelope_id=env_id,
            source_eid=src,
            destination_eid=dst,
            sequence_id=1,
            timestamp_utc=int(time.time()),
            ttl_seconds=ttl,
            kem_ciphertext=b"\x01" * 1088,
            nonce=b"\x02" * 12,
        )
        return PqcMessageEnvelope(
            header=header,
            ciphertext=b"encrypted payload",
            tag=b"\x03" * 16,
            signature=b"\x04" * 3309,
        )

    def test_routing_table(self):
        rt = RoutingTable()
        rt.add_route("dtn://gsb/app", "dtn://sat1/relay")
        rt.add_route("dtn://constellation/*", "dtn://sat2/relay")

        # Exact match
        self.assertEqual(rt.get_next_hop("dtn://gsb/app"), "dtn://sat1/relay")
        # Wildcard match
        self.assertEqual(rt.get_next_hop("dtn://constellation/sat3"), "dtn://sat2/relay")
        # Unknown route
        self.assertIsNone(rt.get_next_hop("dtn://unknown/node"))

    def test_contact_schedule_and_overrides(self):
        cs = ContactSchedule("dtn://sat1/relay")
        now = int(time.time())

        # Peer with no explicit window defaults to UP
        self.assertEqual(cs.get_link_state("dtn://sat2/relay", now), LinkState.UP)

        # Peer with explicit future window is OCCULTED now
        cs.add_contact_window("dtn://gsb/app", start_time_utc=now + 500, end_time_utc=now + 1000)
        self.assertEqual(cs.get_link_state("dtn://gsb/app", now), LinkState.OCCULTED)
        self.assertFalse(cs.is_contact_available("dtn://gsb/app", now))

        # Check inside window
        self.assertTrue(cs.is_contact_available("dtn://gsb/app", now + 600))

        # Manual link override overrides scheduled window
        cs.set_link_override("dtn://gsb/app", LinkState.UP)
        self.assertTrue(cs.is_contact_available("dtn://gsb/app", now))

        cs.set_link_override("dtn://sat2/relay", LinkState.DOWN)
        self.assertFalse(cs.is_contact_available("dtn://sat2/relay", now))

    def test_persistent_spool_survives_restart(self):
        spool1 = PersistentMessageSpool(self.db_path)
        env = self._create_dummy_envelope(
            "11111111-1111-1111-1111-111111111111",
            "dtn://gsa/app",
            "dtn://gsb/app",
        )

        spool1.enqueue(env, "dtn://sat1/relay", initial_status=DeliveryStatus.QUEUED)
        self.assertEqual(spool1.count_pending(), 1)
        self.assertEqual(spool1.count_total(), 1)

        # Simulate process crash / restart: instantiate new spool pointing to same SQLite DB
        del spool1
        spool2 = PersistentMessageSpool(self.db_path)
        self.assertEqual(spool2.count_pending(), 1)

        pending = spool2.get_pending()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].envelope_id, "11111111-1111-1111-1111-111111111111")
        self.assertEqual(pending[0].next_hop_eid, "dtn://sat1/relay")

        spool2.mark_forwarded("11111111-1111-1111-1111-111111111111")
        self.assertEqual(spool2.count_pending(), 0)
        self.assertEqual(spool2.count_total(), 1)

    def test_satellite_relay_zero_decryption(self):
        rt = RoutingTable({"dtn://gsb/app": "dtn://sat2/relay"})
        relay = SatelliteRelayNode(
            node_eid="dtn://sat1/relay",
            spool_db_path=self.db_path,
            routing_table=rt,
        )

        # Architectural invariant check: relay must NOT have crypto private keys
        self.assertFalse(hasattr(relay, "kem_keys"))
        self.assertFalse(hasattr(relay, "dsa_keys"))
        self.assertFalse(hasattr(relay, "aead"))

        env = self._create_dummy_envelope(
            "22222222-2222-2222-2222-222222222222",
            "dtn://gsa/app",
            "dtn://gsb/app",
        )
        evt = relay.ingest(env)
        self.assertEqual(evt.status, DeliveryStatus.FORWARDED)
        self.assertEqual(evt.next_hop_eid, "dtn://sat2/relay")
        self.assertEqual(len(relay.events), 1)


if __name__ == "__main__":
    unittest.main()
