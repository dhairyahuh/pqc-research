"""Unit tests for ASTRA-Sec Envelope and Trust Schema Models."""

import unittest
import uuid

from astra_sec.schema.envelope import (
    EnvelopeHeader,
    MessageAcknowledgment,
    PqcMessageEnvelope,
)
from astra_sec.schema.trust import KeyPair, NodeIdentity, PublicKeyTrustStore, TrustError


class TestEnvelopeSchemas(unittest.TestCase):
    """Verifies schema validation and canonical serialization."""

    def setUp(self):
        self.kem_pk = b"\x01" * 1184
        self.dsa_pk = b"\x02" * 1952
        self.kem_ct = b"\x03" * 1088
        self.nonce = b"\x04" * 12
        self.tag = b"\x05" * 16
        self.sig = b"\x06" * 3309

    def test_envelope_header_canonical_aad_stability(self):
        """Verifies deterministic canonical AAD serialization."""
        header1 = EnvelopeHeader(
            envelope_id="00000000-0000-0000-0000-000000000001",
            source_eid="dtn://gsa/app",
            destination_eid="dtn://gsb/app",
            sequence_id=42,
            timestamp_utc=1700000000,
            ttl_seconds=3600,
            kem_ciphertext=self.kem_ct,
            nonce=self.nonce,
        )
        aad1 = header1.to_canonical_aad()

        header2 = EnvelopeHeader(
            envelope_id="00000000-0000-0000-0000-000000000001",
            source_eid="dtn://gsa/app",
            destination_eid="dtn://gsb/app",
            sequence_id=42,
            timestamp_utc=1700000000,
            ttl_seconds=3600,
            kem_ciphertext=self.kem_ct,
            nonce=self.nonce,
        )
        aad2 = header2.to_canonical_aad()

        self.assertEqual(aad1, aad2)
        self.assertTrue(aad1.startswith(b"ASTR-AEAD-V1"))

    def test_pqc_message_envelope_binary_framing(self):
        """Verifies binary encoding of complete envelope."""
        header = EnvelopeHeader(
            source_eid="dtn://gsa/app",
            destination_eid="dtn://gsb/app",
            kem_ciphertext=self.kem_ct,
            nonce=self.nonce,
        )
        envelope = PqcMessageEnvelope(
            header=header,
            ciphertext=b"EncryptedPayloadBytes",
            tag=self.tag,
            signature=self.sig,
        )
        binary = envelope.to_binary()
        self.assertTrue(binary.startswith(b"ASTRA_MSG_V1"))
        self.assertIn(b"EncryptedPayloadBytes", binary)

    def test_public_key_trust_store(self):
        """Verifies registration, lookup, and authorization in trust store."""
        store = PublicKeyTrustStore()
        peer_a = NodeIdentity(
            eid="dtn://gsa/app",
            role="ground_station",
            kem_public_key=self.kem_pk,
            dsa_public_key=self.dsa_pk,
            is_authorized=True,
        )
        store.register_peer(peer_a)

        self.assertTrue(store.is_authorized("dtn://gsa/app"))
        self.assertEqual(store.get_kem_public_key("dtn://gsa/app"), self.kem_pk)
        self.assertEqual(store.get_dsa_public_key("dtn://gsa/app"), self.dsa_pk)

        # Unregistered peer raises TrustError
        with self.assertRaises(TrustError):
            store.get_kem_public_key("dtn://unknown/node")

    def test_keypair_protection_against_logging(self):
        """Verifies secret key is redacted in KeyPair __repr__ and __str__."""
        kp = KeyPair(algorithm="ML-KEM-768", public_key=self.kem_pk, secret_key=b"SECRET_KEY_BYTES")
        repr_str = repr(kp)
        str_str = str(kp)
        self.assertNotIn("SECRET_KEY_BYTES", repr_str)
        self.assertNotIn("SECRET_KEY_BYTES", str_str)
        self.assertIn("REDACTED", repr_str)


if __name__ == "__main__":
    unittest.main()
