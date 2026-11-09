"""Integration Test Suite: Post-Quantum End-to-End Secure Messaging (GSA -> GSB)."""

import time
import unittest
from typing import Tuple

from pydantic import ValidationError

from astra_sec.core.exceptions import ReplayDetectedError, StaleMessageError
from astra_sec.crypto.aead import AeadDecryptionError
from astra_sec.schema.envelope import EnvelopeHeader, PqcMessageEnvelope
from astra_sec.schema.trust import NodeIdentity, PublicKeyTrustStore
from astra_sec.service.ground_station import (
    DecapsulationFaultError,
    DestinationMismatchError,
    GroundStationNode,
    SignatureVerificationError,
    UnauthorizedSenderError,
)


class TestPqcMessaging(unittest.TestCase):
    """Rigorous end-to-end integration tests for ASTRA-Sec direct communications."""

    def setUp(self):
        # 1. Establish distinct trust stores for GSA and GSB
        self.trust_a = PublicKeyTrustStore()
        self.trust_b = PublicKeyTrustStore()

        # 2. Instantiate Ground Station A and Ground Station B
        self.gsa = GroundStationNode(
            node_eid="dtn://gsa/app",
            role="ground_station",
            trust_store=self.trust_a,
        )
        self.gsb = GroundStationNode(
            node_eid="dtn://gsb/app",
            role="ground_station",
            trust_store=self.trust_b,
        )

        # 3. Mutual Trust Configuration Exchange
        id_a = self.gsa.get_public_identity()
        id_b = self.gsb.get_public_identity()

        self.trust_a.register_peer(id_b)
        self.trust_b.register_peer(id_a)

    def test_01_successful_communication_and_ack(self):
        """Scenario 1: Happy path end-to-end encryption, signature, decapsulation, and ACK verification."""
        telemetry_payload = b"Deep Space Telecommand: Thruster Firing Pulse Delta-V=12.5m/s"

        # GSA transmits to GSB
        envelope = self.gsa.send_message(
            destination_eid="dtn://gsb/app",
            payload=telemetry_payload,
        )
        self.assertEqual(envelope.header.source_eid, "dtn://gsa/app")
        self.assertEqual(envelope.header.destination_eid, "dtn://gsb/app")

        # GSB ingests, verifies, decapsulates, and decrypts
        decrypted_payload, ack = self.gsb.receive_message(envelope)
        self.assertEqual(decrypted_payload, telemetry_payload)
        self.assertEqual(ack.status, "SUCCESS")
        self.assertEqual(ack.original_envelope_id, envelope.header.envelope_id)

        # GSA verifies GSB's signed receipt
        self.assertTrue(self.gsa.verify_acknowledgment(ack, envelope))

    def test_02_modified_ciphertext(self):
        """Scenario 2: Tampered ciphertext must be rejected before plaintext exposure."""
        payload = b"Top Secret Science Data"
        envelope = self.gsa.send_message("dtn://gsb/app", payload)

        # Corrupt 1 byte in ciphertext
        tampered_ct = bytearray(envelope.ciphertext)
        tampered_ct[5] ^= 0x55

        tampered_envelope = PqcMessageEnvelope(
            header=envelope.header,
            ciphertext=bytes(tampered_ct),
            tag=envelope.tag,
            signature=envelope.signature,
        )

        # Signature binds SHA-256(ciphertext), so signature verification fails immediately!
        with self.assertRaises(SignatureVerificationError):
            self.gsb.receive_message(tampered_envelope)

    def test_03_modified_metadata(self):
        """Scenario 3: Tampered metadata (sequence_id, timestamp) must be rejected."""
        payload = b"Operational Message"
        envelope = self.gsa.send_message("dtn://gsb/app", payload)

        # Tamper sequence_id in header
        tampered_header = envelope.header.model_copy(update={"sequence_id": 999})
        tampered_envelope = PqcMessageEnvelope(
            header=tampered_header,
            ciphertext=envelope.ciphertext,
            tag=envelope.tag,
            signature=envelope.signature,
        )

        with self.assertRaises(SignatureVerificationError):
            self.gsb.receive_message(tampered_envelope)

    def test_04_invalid_signature(self):
        """Scenario 4: 1-bit corrupted ML-DSA-65 signature must be rejected."""
        payload = b"Command to Execute"
        envelope = self.gsa.send_message("dtn://gsb/app", payload)

        # Corrupt 1 byte in signature
        corrupted_sig = bytearray(envelope.signature)
        corrupted_sig[42] ^= 0x01

        tampered_envelope = PqcMessageEnvelope(
            header=envelope.header,
            ciphertext=envelope.ciphertext,
            tag=envelope.tag,
            signature=bytes(corrupted_sig),
        )

        with self.assertRaises(SignatureVerificationError):
            self.gsb.receive_message(tampered_envelope)

    def test_05_unknown_sender(self):
        """Scenario 5: Originator not present in recipient's trust store must be rejected."""
        rogue_node = GroundStationNode(node_eid="dtn://rogue/attacker")
        # Rogue node knows GSB's public key
        rogue_node.trust_store.register_peer(self.gsb.get_public_identity())

        envelope = rogue_node.send_message("dtn://gsb/app", b"Malicious Command")

        with self.assertRaises(UnauthorizedSenderError):
            self.gsb.receive_message(envelope)

    def test_06_incorrect_recipient(self):
        """Scenario 6: Envelope addressed to a different destination EID must be rejected."""
        # GSA addresses envelope to SAT1 instead of GSB
        self.trust_a.register_peer(
            NodeIdentity(
                eid="dtn://sat1/relay",
                role="satellite_relay",
                kem_public_key=self.gsb.identity.kem_public_key,
                dsa_public_key=self.gsb.identity.dsa_public_key,
                is_authorized=True,
            )
        )
        envelope = self.gsa.send_message("dtn://sat1/relay", b"Telemetry for SAT1")

        with self.assertRaises(DestinationMismatchError):
            self.gsb.receive_message(envelope)

    def test_07_invalid_encapsulation(self):
        """Scenario 7: Corrupted KEM ciphertext leads to decapsulation key mismatch and tag failure."""
        payload = b"Flight Software Patch Binary"
        envelope = self.gsa.send_message("dtn://gsb/app", payload)

        # Tamper KEM ciphertext
        corrupted_kem_ct = bytearray(envelope.header.kem_ciphertext)
        corrupted_kem_ct[10] ^= 0xFF

        tampered_header = envelope.header.model_copy(update={"kem_ciphertext": bytes(corrupted_kem_ct)})
        tampered_envelope = PqcMessageEnvelope(
            header=tampered_header,
            ciphertext=envelope.ciphertext,
            tag=envelope.tag,
            signature=envelope.signature,
        )

        # Canonical signature binds KEM ciphertext, so signature check fails first
        with self.assertRaises(SignatureVerificationError):
            self.gsb.receive_message(tampered_envelope)

    def test_08_invalid_decapsulation_status(self):
        """Scenario 8: If signature was somehow valid but decapsulation faulted, DecapsulationFaultError is raised."""
        from astra_sec.crypto.base import DecapsulationStatus

        # Mock KEM adapter that simulates an internal monitor fault
        class FaultyKemAdapter:
            ALGORITHM_NAME = "ML-KEM-768"
            PUBLIC_KEY_BYTES = 1184
            SECRET_KEY_BYTES = 2400
            CIPHERTEXT_BYTES = 1088
            SHARED_SECRET_BYTES = 32

            def __init__(self, real_kem):
                self._real = real_kem

            def generate_keypair(self):
                return self._real.generate_keypair()

            def encapsulate(self, pk):
                return self._real.encapsulate(pk)

            def decapsulate(self, ct, sk):
                # Returns FAULT status
                return b"\x00" * 32, DecapsulationStatus.FAULT

        gsb_faulty = GroundStationNode(
            node_eid="dtn://gsb/app",
            kem_adapter=FaultyKemAdapter(self.gsa.kem),
            dsa_adapter=self.gsb.dsa,
            trust_store=self.trust_b,
        )
        # Re-register GSB's key with GSA
        self.trust_a.register_peer(gsb_faulty.get_public_identity())

        envelope = self.gsa.send_message("dtn://gsb/app", b"Valid Message")

        with self.assertRaises(DecapsulationFaultError):
            gsb_faulty.receive_message(envelope)

    def test_09_expired_message(self):
        """Scenario 9: Envelope with timestamp older than TTL must be rejected for staleness."""
        current_epoch = int(time.time())
        old_timestamp = current_epoch - 7200  # 2 hours in the past
        ttl = 3600  # 1 hour TTL

        envelope = self.gsa.send_message(
            destination_eid="dtn://gsb/app",
            payload=b"Stale Telecommand",
            ttl_seconds=ttl,
            custom_timestamp=old_timestamp,
        )

        with self.assertRaises(StaleMessageError):
            self.gsb.receive_message(envelope, current_time=current_epoch)

    def test_10_duplicate_message_replay(self):
        """Scenario 10: Replayed message with already processed sequence ID must be rejected."""
        payload = b"Financial Credit / Battery Charge Command"
        envelope = self.gsa.send_message("dtn://gsb/app", payload)

        # First delivery: succeeds
        decrypted, ack = self.gsb.receive_message(envelope)
        self.assertEqual(decrypted, payload)

        # Second delivery (identical replay): must raise ReplayDetectedError
        with self.assertRaises(ReplayDetectedError):
            self.gsb.receive_message(envelope)

    def test_11_invalid_key_configuration(self):
        """Scenario 11: Malformed public keys (truncated bytes) rejected during NodeIdentity creation."""
        from astra_sec.core.exceptions import SchemaValidationError

        with self.assertRaises((ValidationError, SchemaValidationError, ValueError)):
            NodeIdentity(
                eid="dtn://invalid/node",
                role="ground_station",
                kem_public_key=b"\x00" * 100,  # Invalid size (needs 1184)
                dsa_public_key=b"\x00" * 1952,
                is_authorized=True,
            )

        with self.assertRaises((ValidationError, SchemaValidationError, ValueError)):
            NodeIdentity(
                eid="dtn://invalid/node",
                role="ground_station",
                kem_public_key=b"\x00" * 1184,
                dsa_public_key=b"\x00" * 50,  # Invalid size (needs 1952)
                is_authorized=True,
            )


if __name__ == "__main__":
    unittest.main()
