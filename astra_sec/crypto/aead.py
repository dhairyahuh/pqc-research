"""ASTRA-Sec: AEAD Encryption Engine (AES-256-GCM) and Key Derivation (HKDF-SHA256)."""

import os
import threading
from typing import Optional, Set, Tuple

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from astra_sec.core.exceptions import AstraError
from astra_sec.crypto.base import AeadEngine


class NonceReuseError(AstraError):
    """Raised when an AEAD nonce is reused under the same key or session."""


class AeadDecryptionError(AstraError):
    """Raised when AEAD authentication verification or decryption fails."""


class Aes256GcmAead(AeadEngine):
    """NIST SP 800-38D AES-256-GCM Authenticated Encryption Engine."""

    KEY_BYTES = 32
    NONCE_BYTES = 12
    TAG_BYTES = 16

    def __init__(self, enforce_nonce_uniqueness: bool = True):
        self._enforce_nonce = enforce_nonce_uniqueness
        self._used_nonces: Set[bytes] = set()
        self._lock = threading.Lock()

    def generate_nonce(self) -> bytes:
        """Generates a cryptographically random, unique 12-byte (96-bit) nonce."""
        with self._lock:
            for _ in range(100):
                nonce = os.urandom(self.NONCE_BYTES)
                if nonce not in self._used_nonces:
                    if self._enforce_nonce:
                        self._used_nonces.add(nonce)
                    return nonce
            raise NonceReuseError("Failed to sample unique nonce from CSPRNG.")

    def encrypt(
        self, key: bytes, nonce: bytes, plaintext: bytes, aad: bytes
    ) -> Tuple[bytes, bytes]:
        """Encrypts plaintext with key, nonce, and AAD.

        Returns: (ciphertext, 16-byte tag)
        """
        if len(key) != self.KEY_BYTES:
            raise ValueError(f"AES-256 requires 32-byte key, got {len(key)}")
        if len(nonce) != self.NONCE_BYTES:
            raise ValueError(f"AES-GCM requires 12-byte nonce, got {len(nonce)}")

        with self._lock:
            if self._enforce_nonce:
                key_nonce_binding = key[:8] + nonce
                if key_nonce_binding in self._used_nonces:
                    raise NonceReuseError("Nonce reuse detected under active key!")
                self._used_nonces.add(key_nonce_binding)

        aesgcm = AESGCM(key)
        # AESGCM.encrypt returns ciphertext + tag appended (last 16 bytes)
        raw_output = aesgcm.encrypt(nonce, plaintext, aad)
        ciphertext = raw_output[:-self.TAG_BYTES]
        tag = raw_output[-self.TAG_BYTES:]
        return ciphertext, tag

    def decrypt(
        self, key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes, aad: bytes
    ) -> bytes:
        """Decrypts ciphertext with key, nonce, tag, and AAD.

        Raises AeadDecryptionError if the authentication tag or ciphertext is tampered.
        """
        if len(key) != self.KEY_BYTES:
            raise ValueError(f"AES-256 requires 32-byte key, got {len(key)}")
        if len(nonce) != self.NONCE_BYTES:
            raise ValueError(f"AES-GCM requires 12-byte nonce, got {len(nonce)}")
        if len(tag) != self.TAG_BYTES:
            raise ValueError(f"AES-GCM requires 16-byte tag, got {len(tag)}")

        aesgcm = AESGCM(key)
        combined = ciphertext + tag
        try:
            plaintext = aesgcm.decrypt(nonce, combined, aad)
            return plaintext
        except InvalidTag as e:
            raise AeadDecryptionError(
                "AEAD authentication tag mismatch or corrupted ciphertext/AAD."
            ) from e


class HkdfSha256Engine:
    """RFC 5869 HKDF-SHA256 Key Derivation Engine."""

    DEFAULT_INFO = b"ASTRA-Sec-v1-Payload-AES-256-GCM"

    @classmethod
    def derive_payload_key(
        cls,
        shared_secret: bytes,
        salt: Optional[bytes] = None,
        info: bytes = DEFAULT_INFO,
        length: int = 32,
    ) -> bytes:
        """Derives a symmetric key of specified length from the KEM shared secret."""
        if len(shared_secret) != 32:
            raise ValueError(f"Expected 32-byte shared secret, got {len(shared_secret)}")
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            info=info,
        )
        return hkdf.derive(shared_secret)
