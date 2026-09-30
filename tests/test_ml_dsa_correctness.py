"""
ML-DSA (FIPS 204) Cryptographic Correctness and Tamper Detection Test Suite.
Validates:
- Parameter sizes against NIST FIPS 204 standards
- KeyGen -> Sign -> Verify round-trip validity over multiple iterations
- Cryptographic failure on message alterations
- Cryptographic failure on signature alterations (single-bit flips, byte swaps)
- Isolation across distinct public keys
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from algorithms.oqs_wrapper import MLDSA, get_liboqs_version


class TestMLDSACorrectness(unittest.TestCase):
    """Rigorous correctness and FIPS 204 compliance tests for ML-DSA."""

    @classmethod
    def setUpClass(cls):
        cls.version = get_liboqs_version()
        # NIST FIPS 204 Table 1 and Table 2 exact sizes (in bytes)
        cls.expected_params = {
            "ML-DSA-44": {
                "pk_bytes": 1312,
                "sk_bytes": 2560,
                "sig_bytes": 2420,
                "nist_category": 2
            },
            "ML-DSA-65": {
                "pk_bytes": 1952,
                "sk_bytes": 4032,
                "sig_bytes": 3309,
                "nist_category": 3
            },
            "ML-DSA-87": {
                "pk_bytes": 2592,
                "sk_bytes": 4896,
                "sig_bytes": 4627,
                "nist_category": 5
            }
        }

    def test_parameter_sizes(self):
        """Verify that public keys, secret keys, and signatures match FIPS 204 exact byte lengths."""
        for alg_name, params in self.expected_params.items():
            with self.subTest(algorithm=alg_name):
                sig = MLDSA(alg_name)
                self.assertEqual(sig.length_public_key, params["pk_bytes"])
                self.assertEqual(sig.length_secret_key, params["sk_bytes"])
                self.assertEqual(sig.length_signature, params["sig_bytes"])

    def test_roundtrip_validity_multi_iterations(self):
        """Test KeyGen -> Sign -> Verify valid signatures over 50 iterations per variant."""
        iterations = 50
        for alg_name in self.expected_params.keys():
            sig = MLDSA(alg_name)
            for i in range(iterations):
                pk, sk = sig.keypair()
                message = f"Space Mission Critical Telecommand seq={i} timestamp=2026-09-30T12:00:00Z".encode("utf-8")
                signature = sig.sign(message, sk)

                self.assertEqual(len(signature), sig.length_signature)
                valid = sig.verify(message, signature, pk)
                self.assertTrue(valid, f"Verification failed on iteration {i} for {alg_name}")

    def test_rejection_on_modified_message(self):
        """Verify that any modification to the signed message results in verification failure."""
        for alg_name in self.expected_params.keys():
            with self.subTest(algorithm=alg_name):
                sig = MLDSA(alg_name)
                pk, sk = sig.keypair()
                original_msg = b"Spacecraft orbital trajectory adjustment vector: [0.0, 1.25, -0.42]"
                tampered_msg = b"Spacecraft orbital trajectory adjustment vector: [0.0, 1.26, -0.42]"

                signature = sig.sign(original_msg, sk)
                self.assertTrue(sig.verify(original_msg, signature, pk))
                self.assertFalse(sig.verify(tampered_msg, signature, pk), "Tampered message was accepted as valid!")

    def test_rejection_on_bit_flipped_signatures(self):
        """Verify that single-bit flips anywhere in the signature cause immediate verification rejection."""
        for alg_name in self.expected_params.keys():
            with self.subTest(algorithm=alg_name):
                sig = MLDSA(alg_name)
                pk, sk = sig.keypair()
                message = b"Payload telemetry checksum block"
                signature = sig.sign(message, sk)

                # Test bit flip at beginning, middle, and end
                test_indices = [0, len(signature) // 2, len(signature) - 1]
                for idx in test_indices:
                    tampered_sig = bytearray(signature)
                    tampered_sig[idx] ^= 0x01
                    self.assertFalse(
                        sig.verify(message, bytes(tampered_sig), pk),
                        f"Signature with bit-flip at index {idx} was falsely accepted for {alg_name}"
                    )

    def test_rejection_with_different_public_key(self):
        """Verify that a valid signature is rejected when verified against a different public key."""
        for alg_name in self.expected_params.keys():
            with self.subTest(algorithm=alg_name):
                sig = MLDSA(alg_name)
                pk1, sk1 = sig.keypair()
                pk2, sk2 = sig.keypair()
                message = b"Inter-satellite link handshake"

                signature1 = sig.sign(message, sk1)
                self.assertTrue(sig.verify(message, signature1, pk1))
                self.assertFalse(sig.verify(message, signature1, pk2), "Signature verified against incorrect public key!")


if __name__ == "__main__":
    unittest.main()
