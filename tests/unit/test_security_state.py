"""Unit tests for ASTRA-Sec Security State, Key Lifecycle, and Replay Protection."""

import os
import shutil
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
from astra_sec.schema.envelope import EnvelopeHeader, MessageAcknowledgment, PqcMessageEnvelope
from astra_sec.schema.trust import PublicKeyTrustStore
from astra_sec.security.lifecycle import KeyLifecycleManager, KeyLifecycleState
from astra_sec.security.persistent_state import PersistentSecurityState
from astra_sec.security.policy import AuthorizationPolicy, AuthorizationStatus
from astra_sec.security.replay import PersistentAntiReplayFilter
from astra_sec.security.verifier import GroundStationVerifier
from astra_sec.service.ground_station import GroundStationNode


class TestSecurityState(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "sec_state.db")
        self.integrity_key = b"INTEGRITY_SECRET_KEY_32_BYTES__"

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_key_lifecycle_rotation_and_revocation(self):
        mgr = KeyLifecycleManager("dtn://gsa/app")
        # 1. Register active key
        k1 = mgr.register_key("ML-KEM-768", b"PUB_KEY_V1" * 37)
        self.assertEqual(k1.version, 1)
        self.assertEqual(k1.state, KeyLifecycleState.ACTIVE)
        self.assertTrue(k1.can_encrypt_or_sign())

        # 2. Rotate to v2
        k2, old_k = mgr.rotate_key("ML-KEM-768", b"PUB_KEY_V2" * 37)
        self.assertEqual(k2.version, 2)
        self.assertEqual(k2.state, KeyLifecycleState.ACTIVE)
        self.assertEqual(old_k.state, KeyLifecycleState.RETIRED)
        self.assertFalse(old_k.can_encrypt_or_sign())
        self.assertTrue(old_k.can_decrypt_or_verify())

        # 3. Revoke v2
        mgr.revoke_key(k2.key_id)
        self.assertEqual(k2.state, KeyLifecycleState.REVOKED)
        self.assertFalse(k2.can_encrypt_or_sign())
        self.assertFalse(k2.can_decrypt_or_verify())

    def test_authorization_policy_and_revocation(self):
        policy = AuthorizationPolicy(max_command_ttl_seconds=3600)
        policy.set_authorization("dtn://gsa/app", "ground_station", AuthorizationStatus.AUTHORIZED)

        # Authorized sender succeeds
        policy.validate_sender("dtn://gsa/app")

        # Unknown sender raises
        with self.assertRaises(IdentityRevokedError):
            policy.validate_sender("dtn://unknown/node")

        # Revoking identity raises
        policy.revoke_identity("dtn://gsa/app", reason="Key compromised")
        with self.assertRaises(IdentityRevokedError):
            policy.validate_sender("dtn://gsa/app")

        # Delayed command freshness
        now = int(time.time())
        # Valid delayed message within TTL
        policy.validate_command_freshness(timestamp_utc=now - 500, ttl_seconds=1000, current_time_utc=now)
        # Expired message
        with self.assertRaises(StaleMessageError):
            policy.validate_command_freshness(timestamp_utc=now - 1500, ttl_seconds=1000, current_time_utc=now)

    def test_persistent_security_state_integrity_and_corruption_lockout(self):
        # Initial state setup
        state = PersistentSecurityState(self.db_path, self.integrity_key)
        state.record_accepted_command("dtn://gsa/app", 1, "env-001")
        self.assertTrue(state.is_sequence_processed("dtn://gsa/app", 1))
        self.assertFalse(state.is_sequence_processed("dtn://gsa/app", 2))
        del state

        # Reboot 1: Valid reboot succeeds
        state2 = PersistentSecurityState(self.db_path, self.integrity_key)
        self.assertTrue(state2.is_sequence_processed("dtn://gsa/app", 1))
        del state2

        # Tampering attack: Modify the SQLite file directly behind the engine's back
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.execute("INSERT INTO seen_sequences VALUES ('dtn://rogue/node', 999, 'forged-env', 12345)")
        conn.commit()
        conn.close()

        # Reboot 2: Checksum mismatch must trigger SecurityStateCorruptionError and LOCKOUT
        with self.assertRaises(SecurityStateCorruptionError):
            PersistentSecurityState(self.db_path, self.integrity_key)

    def test_persistent_anti_replay_filter(self):
        state = PersistentSecurityState(self.db_path, self.integrity_key)
        rf = PersistentAntiReplayFilter(state)
        now = int(time.time())

        # First acceptance
        rf.check_and_update("dtn://gsa/app", 1, now, 3600, "env-001")

        # Replay attempt
        with self.assertRaises(ReplayDetectedError):
            rf.check_and_update("dtn://gsa/app", 1, now, 3600, "env-001-replay")

        # Simulate reboot: new filter with same DB
        del rf
        del state
        state_reboot = PersistentSecurityState(self.db_path, self.integrity_key)
        rf_reboot = PersistentAntiReplayFilter(state_reboot)

        # Attempt replay after reboot must still be rejected
        with self.assertRaises(ReplayDetectedError):
            rf_reboot.check_and_update("dtn://gsa/app", 1, now, 3600, "env-001-replay-after-boot")

    def test_ground_station_verifier(self):
        trust_store = PublicKeyTrustStore()
        gsa = GroundStationNode("dtn://gsa/app", trust_store=trust_store)
        gsb = GroundStationNode("dtn://gsb/app", trust_store=trust_store)
        trust_store.register_peer(gsa.get_public_identity())
        trust_store.register_peer(gsb.get_public_identity())

        verifier = GroundStationVerifier("dtn://gsa/app", trust_store=trust_store)

        # GSA sends message to GSB
        envelope = gsa.send_message("dtn://gsb/app", b"COMMAND_FOR_VERIFICATION")
        verifier.record_dispatched_command(envelope)

        # GSB executes and returns ACK
        _, ack = gsb.receive_message(envelope)

        # Verifier checks ACK
        rec = verifier.verify_acknowledgment(ack)
        self.assertTrue(rec.signature_valid)
        self.assertEqual(len(verifier.ledger), 1)

        # Uncorrelated ACK raises
        fake_ack = MessageAcknowledgment(
            original_envelope_id="00000000-0000-0000-0000-000000000000",
            source_eid="dtn://gsb/app",
            destination_eid="dtn://gsa/app",
            signature=ack.signature,
        )
        with self.assertRaises(InvalidAcknowledgmentError):
            verifier.verify_acknowledgment(fake_ack)


if __name__ == "__main__":
    unittest.main()
