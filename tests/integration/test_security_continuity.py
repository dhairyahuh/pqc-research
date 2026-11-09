"""ASTRA-Sec: Security Continuity & Ground-Station Verification Integration Test Suite (Prompt 09).

Validates:
1. Replay of accepted command is rejected.
2. Duplicate bundle is suppressed at relay.
3. Delayed valid message within TTL window is accepted.
4. Expired command is rejected.
5. Revoked sender is rejected.
6. Key rotation operates cleanly.
7. Restart during queued delivery preserves bundle and security state.
8. Restart after command acceptance preserves anti-replay; replay after boot is rejected.
9. Corrupted persistent security state triggers fail-stop lockout.
10. Invalid acknowledgement is rejected by GroundStationVerifier.
"""

import os
import shutil
import sqlite3
import tempfile
import time
import unittest

from astra_sec.core.exceptions import (
    IdentityRevokedError,
    InvalidAcknowledgmentError,
    ReplayDetectedError,
    SecurityStateCorruptionError,
    StaleMessageError,
)
from astra_sec.network.relay import SatelliteRelayNode
from astra_sec.network.routing import RoutingTable
from astra_sec.network.service import DirectMemoryTransport
from astra_sec.schema.envelope import MessageAcknowledgment, PqcMessageEnvelope
from astra_sec.schema.network import DeliveryStatus, LinkState
from astra_sec.schema.trust import PublicKeyTrustStore
from astra_sec.security.lifecycle import KeyLifecycleManager
from astra_sec.security.persistent_state import PersistentSecurityState
from astra_sec.security.policy import AuthorizationPolicy, AuthorizationStatus
from astra_sec.security.replay import PersistentAntiReplayFilter
from astra_sec.security.verifier import GroundStationVerifier
from astra_sec.service.ground_station import GroundStationNode, SignatureVerificationError


class TestSecurityContinuity(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.gsa_sec_db = os.path.join(self.temp_dir, "gsa_sec.db")
        self.gsb_sec_db = os.path.join(self.temp_dir, "gsb_sec.db")
        self.sat_spool_db = os.path.join(self.temp_dir, "sat_spool.db")
        self.integrity_key = b"ASTRA_SEC_MASTER_HMAC_KEY_32B__"

        # Trust store & Policy
        self.trust_store = PublicKeyTrustStore()
        self.policy = AuthorizationPolicy(max_command_ttl_seconds=3600)

        # Persistent security state and anti-replay for GSB
        self.gsb_state = PersistentSecurityState(self.gsb_sec_db, self.integrity_key)
        self.gsb_replay_filter = PersistentAntiReplayFilter(self.gsb_state)

        # Ground Stations
        self.gsa = GroundStationNode(
            node_eid="dtn://gsa/app",
            trust_store=self.trust_store,
            policy=self.policy,
        )
        self.gsb = GroundStationNode(
            node_eid="dtn://gsb/app",
            trust_store=self.trust_store,
            policy=self.policy,
            replay_filter=self.gsb_replay_filter,
        )

        self.trust_store.register_peer(self.gsa.get_public_identity())
        self.trust_store.register_peer(self.gsb.get_public_identity())
        self.policy.set_authorization("dtn://gsa/app", "ground_station", AuthorizationStatus.AUTHORIZED)
        self.policy.set_authorization("dtn://gsb/app", "ground_station", AuthorizationStatus.AUTHORIZED)

        # Verifier for GSA
        self.verifier = GroundStationVerifier("dtn://gsa/app", trust_store=self.trust_store)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_replay_of_accepted_command_rejected(self):
        """Scenario 1: Command accepted; immediate replay attempt must be rejected."""
        envelope = self.gsa.send_message("dtn://gsb/app", b"THRUSTER_FIRE_COMMAND", custom_sequence_id=101)
        # First execution succeeds
        pt, ack = self.gsb.receive_message(envelope)
        self.assertEqual(pt, b"THRUSTER_FIRE_COMMAND")

        # Replay attempt must raise ReplayDetectedError
        with self.assertRaises(ReplayDetectedError):
            self.gsb.receive_message(envelope)

    def test_02_duplicate_bundle_suppressed_at_relay(self):
        """Scenario 2: Duplicate bundle arriving at space relay is suppressed."""
        rt = RoutingTable({"dtn://gsb/*": "dtn://gsb/app"})
        delivered = []
        relay = SatelliteRelayNode(
            node_eid="dtn://sat1/relay",
            spool_db_path=self.sat_spool_db,
            routing_table=rt,
            forwarder_fn=lambda t, env, from_peer=None: delivered.append(env) or True,
        )

        envelope = self.gsa.send_message("dtn://gsb/app", b"RELAY_TEST_PAYLOAD", custom_sequence_id=102)

        evt1 = relay.ingest(envelope)
        self.assertEqual(evt1.status, DeliveryStatus.FORWARDED)
        self.assertEqual(len(delivered), 1)

        # Re-send duplicate envelope
        evt2 = relay.ingest(envelope)
        self.assertEqual(evt2.status, DeliveryStatus.DROPPED_DUPLICATE)
        self.assertEqual(len(delivered), 1)

    def test_03_delayed_valid_message_accepted(self):
        """Scenario 3: Delayed message within TTL window is NOT automatically invalid."""
        now = int(time.time())
        # Message created 300 seconds ago with 3600s TTL (delayed in DTN network)
        envelope = self.gsa.send_message(
            "dtn://gsb/app",
            b"DELAYED_TELEMETRY",
            ttl_seconds=3600,
            custom_timestamp=now - 300,
            custom_sequence_id=103,
        )

        pt, ack = self.gsb.receive_message(envelope, current_time=now)
        self.assertEqual(pt, b"DELAYED_TELEMETRY")
        self.assertEqual(ack.status, "SUCCESS")

    def test_04_expired_command_rejected(self):
        """Scenario 4: Expired command exceeding TTL must be rejected."""
        now = int(time.time())
        # Created 200s ago with 60s TTL -> expired by 140s
        envelope = self.gsa.send_message(
            "dtn://gsb/app",
            b"STALE_COMMAND",
            ttl_seconds=60,
            custom_timestamp=now - 200,
            custom_sequence_id=104,
        )

        with self.assertRaises(StaleMessageError):
            self.gsb.receive_message(envelope, current_time=now)

    def test_05_revoked_sender_rejected(self):
        """Scenario 5: Revoked sender identity is strictly rejected."""
        # Revoke GSA in GSB's authorization policy
        self.gsb.revoke_peer("dtn://gsa/app", reason="Cryptographic key compromised")

        envelope = self.gsa.send_message("dtn://gsb/app", b"REVOKED_ATTEMPT", custom_sequence_id=105)

        with self.assertRaises(IdentityRevokedError):
            self.gsb.receive_message(envelope)

    def test_06_key_rotation(self):
        """Scenario 6: Destination node rotates keys; sender uses new public key seamlessly."""
        # GSB rotates its ML-KEM-768 and ML-DSA-65 keys
        new_kem, new_dsa = self.gsb.rotate_node_keys()

        # GSA updates trust store with GSB's new public key
        self.gsa.trust_store.register_peer(self.gsb.get_public_identity())

        envelope = self.gsa.send_message("dtn://gsb/app", b"ROTATED_KEY_DATA", custom_sequence_id=106)
        pt, ack = self.gsb.receive_message(envelope)
        self.assertEqual(pt, b"ROTATED_KEY_DATA")

    def test_07_restart_during_queued_delivery(self):
        """Scenario 7: Relay process reboot during queueing preserves persistent spool."""
        rt = RoutingTable({"dtn://gsb/*": "dtn://gsb/app"})
        relay = SatelliteRelayNode(
            node_eid="dtn://sat1/relay",
            spool_db_path=self.sat_spool_db,
            routing_table=rt,
        )
        relay.set_link_state("dtn://gsb/app", LinkState.DOWN)

        envelope = self.gsa.send_message("dtn://gsb/app", b"QUEUED_ACROSS_REBOOT", custom_sequence_id=107)
        evt = relay.ingest(envelope)
        self.assertEqual(evt.status, DeliveryStatus.WAITING_CONTACT)
        self.assertEqual(relay.spool.count_pending(), 1)

        # Reboot relay: instantiate fresh relay pointing to same DB
        del relay
        delivered = []
        relay_reboot = SatelliteRelayNode(
            node_eid="dtn://sat1/relay",
            spool_db_path=self.sat_spool_db,
            routing_table=rt,
            forwarder_fn=lambda t, env, from_peer=None: delivered.append(env) or True,
        )
        self.assertEqual(relay_reboot.spool.count_pending(), 1)

        # Restore link and flush
        relay_reboot.set_link_state("dtn://gsb/app", LinkState.UP)
        flushed = relay_reboot.process_spool()
        self.assertEqual(len(flushed), 1)
        self.assertEqual(len(delivered), 1)

        pt, _ = self.gsb.receive_message(delivered[0])
        self.assertEqual(pt, b"QUEUED_ACROSS_REBOOT")

    def test_08_restart_after_command_acceptance(self):
        """Scenario 8: Reboot after acceptance preserves anti-replay state; replay after boot is rejected."""
        envelope = self.gsa.send_message("dtn://gsb/app", b"PERSISTENT_REPLAY_TEST", custom_sequence_id=108)
        pt, _ = self.gsb.receive_message(envelope)
        self.assertEqual(pt, b"PERSISTENT_REPLAY_TEST")

        # Simulate full process reboot of GSB
        del self.gsb
        del self.gsb_replay_filter
        del self.gsb_state

        rebooted_state = PersistentSecurityState(self.gsb_sec_db, self.integrity_key)
        rebooted_filter = PersistentAntiReplayFilter(rebooted_state)
        rebooted_gsb = GroundStationNode(
            node_eid="dtn://gsb/app",
            trust_store=self.trust_store,
            policy=self.policy,
            replay_filter=rebooted_filter,
        )

        # Attacker attempts replay against rebooted node
        with self.assertRaises(ReplayDetectedError):
            rebooted_gsb.receive_message(envelope)

    def test_09_corrupted_persistent_security_state_fail_stop(self):
        """Scenario 9: Tampered or corrupted security state triggers fail-stop lockout; never resets silently."""
        envelope = self.gsa.send_message("dtn://gsb/app", b"INTEGRITY_TEST", custom_sequence_id=109)
        self.gsb.receive_message(envelope)

        del self.gsb
        del self.gsb_replay_filter
        del self.gsb_state

        # Cosmic ray bit-flip / tampering directly into SQLite database
        conn = sqlite3.connect(self.gsb_sec_db)
        conn.execute("INSERT INTO seen_sequences VALUES ('dtn://gsa/app', 9999, 'malicious-uuid', 1000)")
        conn.commit()
        conn.close()

        # Reboot must detect state checksum mismatch and lock down
        with self.assertRaises(SecurityStateCorruptionError):
            PersistentSecurityState(self.gsb_sec_db, self.integrity_key)

    def test_10_invalid_acknowledgement_rejected(self):
        """Scenario 10: Corrupted ACK signature or forged ACK rejected by verifier."""
        envelope = self.gsa.send_message("dtn://gsb/app", b"AUDITED_COMMAND", custom_sequence_id=110)
        self.verifier.record_dispatched_command(envelope)

        _, valid_ack = self.gsb.receive_message(envelope)

        # Tamper with 1 byte of the ML-DSA-65 signature on the ACK
        corrupted_sig = bytearray(valid_ack.signature)
        corrupted_sig[0] ^= 0xAA
        tampered_ack = MessageAcknowledgment(
            ack_id=valid_ack.ack_id,
            original_envelope_id=valid_ack.original_envelope_id,
            source_eid=valid_ack.source_eid,
            destination_eid=valid_ack.destination_eid,
            timestamp_utc=valid_ack.timestamp_utc,
            status=valid_ack.status,
            signature=bytes(corrupted_sig),
        )

        # Verifier must reject tampered ACK
        with self.assertRaises(InvalidAcknowledgmentError):
            self.verifier.verify_acknowledgment(tampered_ack)


if __name__ == "__main__":
    unittest.main()
