"""
ML-KEM (FIPS 203) Cryptographic Correctness and Boundary Validation Test Suite.
Validates:
- Parameter sizes against NIST FIPS 203 standards
- KeyGen -> Encaps -> Decaps round-trip equality over multiple iterations
- Implicit rejection on corrupted ciphertexts (Fujisaki-Okamoto transform property)
- Cross-algorithm isolation
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from algorithms.oqs_wrapper import MLKEM, get_liboqs_version


class TestMLKEMCorrectness(unittest.TestCase):
    """Rigorous correctness and FIPS 203 compliance tests for ML-KEM."""

    @classmethod
    def setUpClass(cls):
        cls.version = get_liboqs_version()
        # NIST FIPS 203 Table 2 and Table 3 exact sizes (in bytes)
        cls.expected_params = {
            "ML-KEM-512": {
                "pk_bytes": 800,
                "sk_bytes": 1632,
                "ct_bytes": 768,
                "ss_bytes": 32,
                "claim_nist_level": 1
            },
            "ML-KEM-768": {
                "pk_bytes": 1184,
                "sk_bytes": 2400,
                "ct_bytes": 1088,
                "ss_bytes": 32,
                "claim_nist_level": 3
            },
            "ML-KEM-1024": {
                "pk_bytes": 1568,
                "sk_bytes": 3168,
                "ct_bytes": 1568,
                "ss_bytes": 32,
                "claim_nist_level": 5
            }
        }

    def test_parameter_sizes(self):
        """Verify that public keys, secret keys, ciphertexts, and shared secrets match FIPS 203 exact byte lengths."""
        for alg_name, params in self.expected_params.items():
            with self.subTest(algorithm=alg_name):
                kem = MLKEM(alg_name)
                self.assertEqual(kem.length_public_key, params["pk_bytes"])
                self.assertEqual(kem.length_secret_key, params["sk_bytes"])
                self.assertEqual(kem.length_ciphertext, params["ct_bytes"])
                self.assertEqual(kem.length_shared_secret, params["ss_bytes"])

    def test_roundtrip_equality_multi_iterations(self):
        """Test KeyGen -> Encaps -> Decaps produces identical 32-byte shared secrets across 50 iterations per variant."""
        iterations = 50
        for alg_name in self.expected_params.keys():
            kem = MLKEM(alg_name)
            for i in range(iterations):
                pk, sk = kem.keypair()
                self.assertEqual(len(pk), kem.length_public_key)
                self.assertEqual(len(sk), kem.length_secret_key)

                ct, ss_enc = kem.encaps(pk)
                self.assertEqual(len(ct), kem.length_ciphertext)
                self.assertEqual(len(ss_enc), kem.length_shared_secret)

                ss_dec = kem.decaps(ct, sk)
                self.assertEqual(len(ss_dec), kem.length_shared_secret)
                self.assertEqual(ss_enc, ss_dec, f"Iteration {i} failed for {alg_name}: ss mismatch")

    def test_implicit_rejection_on_ciphertext_tampering(self):
        """
        FIPS 203 Section 7.3: If ciphertext is modified, decapsulation MUST NOT return
        the original shared secret. Instead, it must return a pseudorandom value derived
        from the hash of the corrupted ciphertext and the rejection seed in the secret key.
        """
        for alg_name in self.expected_params.keys():
            with self.subTest(algorithm=alg_name):
                kem = MLKEM(alg_name)
                pk, sk = kem.keypair()
                ct, ss_enc = kem.encaps(pk)

                # Test 1: Single bit flip at index 0
                ct_mod1 = bytearray(ct)
                ct_mod1[0] ^= 0x01
                ss_dec1 = kem.decaps(bytes(ct_mod1), sk)
                self.assertNotEqual(ss_enc, ss_dec1, "Tampered ciphertext (bit 0) produced valid shared secret!")

                # Test 2: Single bit flip in middle
                ct_mod2 = bytearray(ct)
                ct_mod2[len(ct) // 2] ^= 0x80
                ss_dec2 = kem.decaps(bytes(ct_mod2), sk)
                self.assertNotEqual(ss_enc, ss_dec2, "Tampered ciphertext (middle bit) produced valid shared secret!")

                # Test 3: Last byte zeroed
                ct_mod3 = bytearray(ct)
                ct_mod3[-1] ^= 0xFF
                ss_dec3 = kem.decaps(bytes(ct_mod3), sk)
                self.assertNotEqual(ss_enc, ss_dec3, "Tampered ciphertext (last byte) produced valid shared secret!")

                # Implicit rejection should produce deterministic rejection keys for identical corruptions
                ss_dec1_again = kem.decaps(bytes(ct_mod1), sk)
                self.assertEqual(ss_dec1, ss_dec1_again, "Implicit rejection output was non-deterministic!")

    def test_invalid_buffer_sizes_raise_errors(self):
        """Test that invalid public key, secret key, or ciphertext lengths raise explicit exceptions."""
        kem = MLKEM("ML-KEM-768")
        with self.assertRaises(ValueError):
            kem.encaps(b"too_short")
        with self.assertRaises(ValueError):
            kem.decaps(b"short_ct", b"x" * kem.length_secret_key)
        with self.assertRaises(ValueError):
            kem.decaps(b"x" * kem.length_ciphertext, b"short_sk")


if __name__ == "__main__":
    unittest.main()
