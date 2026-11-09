"""Unit tests for ASTRA-Sec Post-Quantum Cryptographic Adapters."""

import unittest

from astra_sec.crypto.aead import (
    AeadDecryptionError,
    Aes256GcmAead,
    HkdfSha256Engine,
    NonceReuseError,
)
from astra_sec.crypto.base import DecapsulationStatus
from astra_sec.crypto.factory import CryptoEngineFactory
from astra_sec.crypto.monitored_c import (
    MonitoredNativeDsaAdapter,
    MonitoredNativeKemAdapter,
)
from astra_sec.crypto.oqs_adapter import OqsDsaAdapter, OqsKemAdapter


class TestCryptoAdapters(unittest.TestCase):
    """Verifies functional correctness and tamper resistance of PQC adapters."""

    def test_monitored_native_kem_roundtrip(self):
        """Verifies native monitored ML-KEM-768 keypair, encaps, and decaps."""
        kem = MonitoredNativeKemAdapter()
        pk, sk = kem.generate_keypair()
        self.assertEqual(len(pk), 1184)
        self.assertEqual(len(sk), 2400)

        ct, ss_enc = kem.encapsulate(pk)
        self.assertEqual(len(ct), 1088)
        self.assertEqual(len(ss_enc), 32)

        ss_dec, status = kem.decapsulate(ct, sk)
        self.assertEqual(len(ss_dec), 32)
        self.assertEqual(ss_enc, ss_dec)
        self.assertEqual(status, DecapsulationStatus.SUCCESS)

    def test_monitored_native_kem_corrupted_ct(self):
        """Verifies that 1-byte corrupted KEM ciphertext triggers implicit rejection."""
        kem = MonitoredNativeKemAdapter()
        pk, sk = kem.generate_keypair()
        ct, ss_enc = kem.encapsulate(pk)

        # Corrupt the ciphertext
        corrupted_ct = bytearray(ct)
        corrupted_ct[0] ^= 0xFF
        ss_dec, status = kem.decapsulate(bytes(corrupted_ct), sk)

        # Under FIPS 203 Section 7.3 implicit rejection, decapsulation outputs a pseudorandom key != ss_enc
        self.assertNotEqual(ss_enc, ss_dec)

    def test_monitored_native_dsa_roundtrip(self):
        """Verifies native ML-DSA-65 keypair, signature generation, and verification."""
        dsa = MonitoredNativeDsaAdapter()
        pk, sk = dsa.generate_keypair()
        self.assertEqual(len(pk), 1952)
        self.assertEqual(len(sk), 4032)

        msg = b"ASTRA-Sec Ground Control Telecommand: Deploy Solar Arrays"
        signature = dsa.sign(msg, sk)
        self.assertEqual(len(signature), 3309)

        # Verify Genuine
        self.assertTrue(dsa.verify(msg, signature, pk))

        # Verify Tampered Message
        self.assertFalse(dsa.verify(b"Corrupted message payload", signature, pk))

        # Verify Tampered Signature
        corrupted_sig = bytearray(signature)
        corrupted_sig[10] ^= 0x01
        self.assertFalse(dsa.verify(msg, bytes(corrupted_sig), pk))

    def test_liboqs_baseline_interoperability(self):
        """Verifies cross-engine interoperability: Native C generates, LibOQS decapsulates."""
        native_kem = MonitoredNativeKemAdapter()
        oqs_kem = OqsKemAdapter()

        # Native generates keypair
        pk_native, sk_native = native_kem.generate_keypair()

        # LibOQS encapsulates
        ct_oqs, ss_oqs = oqs_kem.encapsulate(pk_native)

        # Native decapsulates
        ss_dec, status = native_kem.decapsulate(ct_oqs, sk_native)
        self.assertEqual(status, DecapsulationStatus.SUCCESS)
        self.assertEqual(ss_oqs, ss_dec)

    def test_aes256_gcm_aead(self):
        """Verifies AES-256-GCM encryption, decryption, and authentication tag enforcement."""
        aead = Aes256GcmAead(enforce_nonce_uniqueness=True)
        key = b"\x42" * 32
        nonce = aead.generate_nonce()
        plaintext = b"Mission Critical Telemetry Payload: Gyroscope OK, Thermal 21.4C"
        aad = b"Canonical-Header-Bytes"

        ciphertext, tag = aead.encrypt(key, nonce, plaintext, aad)
        self.assertEqual(len(tag), 16)

        # Decrypt genuine
        decrypted = aead.decrypt(key, nonce, ciphertext, tag, aad)
        self.assertEqual(decrypted, plaintext)

        # Tampered ciphertext rejection
        corrupted_ct = bytearray(ciphertext)
        corrupted_ct[0] ^= 0x01
        with self.assertRaises(AeadDecryptionError):
            aead.decrypt(key, nonce, bytes(corrupted_ct), tag, aad)

        # Tampered AAD rejection
        with self.assertRaises(AeadDecryptionError):
            aead.decrypt(key, nonce, ciphertext, tag, b"Altered-Header-Bytes")

    def test_nonce_reuse_prevention(self):
        """Verifies that encrypting with an already used nonce under the same key is strictly prohibited."""
        aead = Aes256GcmAead(enforce_nonce_uniqueness=True)
        key = b"\x99" * 32
        nonce = b"\x01" * 12
        plaintext = b"Payload 1"
        aad = b"AAD"

        aead.encrypt(key, nonce, plaintext, aad)

        # Second attempt with identical nonce under same key must raise NonceReuseError
        with self.assertRaises(NonceReuseError):
            aead.encrypt(key, nonce, b"Payload 2", aad)

    def test_hkdf_sha256_derivation(self):
        """Verifies HKDF-SHA256 generates consistent 32-byte symmetric keys."""
        ss = b"\xAA" * 32
        key1 = HkdfSha256Engine.derive_payload_key(ss)
        key2 = HkdfSha256Engine.derive_payload_key(ss)
        self.assertEqual(len(key1), 32)
        self.assertEqual(key1, key2)

        # Different shared secret yields completely different key
        key3 = HkdfSha256Engine.derive_payload_key(b"\xBB" * 32)
        self.assertNotEqual(key1, key3)


if __name__ == "__main__":
    unittest.main()
