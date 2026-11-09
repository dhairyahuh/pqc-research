"""ASTRA-Sec: Core Cryptographic Interfaces and Abstractions."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Tuple


class DecapsulationStatus(Enum):
    """FIPS 203 & Monitored Decapsulation Execution Status."""

    SUCCESS = 0x5A5A5A5A
    REJECT = 0xA5A5A5A5
    FAULT = 0xDEADBEEF

    @classmethod
    def from_code(cls, code: int) -> "DecapsulationStatus":
        for member in cls:
            if member.value == code:
                return member
        return cls.FAULT

    @property
    def is_success(self) -> bool:
        return self == DecapsulationStatus.SUCCESS


class KemAdapter(ABC):
    """Abstract Base Class for Post-Quantum Key Encapsulation (ML-KEM-768)."""

    ALGORITHM_NAME = "ML-KEM-768"
    PUBLIC_KEY_BYTES = 1184
    SECRET_KEY_BYTES = 2400
    CIPHERTEXT_BYTES = 1088
    SHARED_SECRET_BYTES = 32

    @abstractmethod
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Generates (public_key, secret_key) tuple."""
        raise NotImplementedError

    @abstractmethod
    def encapsulate(self, peer_public_key: bytes) -> Tuple[bytes, bytes]:
        """Encapsulates a shared secret under peer_public_key.

        Returns: (ciphertext, shared_secret)
        """
        raise NotImplementedError

    @abstractmethod
    def decapsulate(self, ciphertext: bytes, secret_key: bytes) -> Tuple[bytes, DecapsulationStatus]:
        """Decapsulates a shared secret using secret_key with monitoring.

        Returns: (shared_secret, status)
        """
        raise NotImplementedError


class DsaAdapter(ABC):
    """Abstract Base Class for Post-Quantum Digital Signatures (ML-DSA-65)."""

    ALGORITHM_NAME = "ML-DSA-65"
    PUBLIC_KEY_BYTES = 1952
    SECRET_KEY_BYTES = 4032
    SIGNATURE_BYTES = 3309

    @abstractmethod
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Generates (public_key, secret_key) tuple."""
        raise NotImplementedError

    @abstractmethod
    def sign(self, message: bytes, secret_key: bytes) -> bytes:
        """Signs message using secret_key.

        Returns: signature bytes
        """
        raise NotImplementedError

    @abstractmethod
    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """Verifies signature over message using public_key."""
        raise NotImplementedError


class AeadEngine(ABC):
    """Standardized AEAD Scheme for Payload Encryption (AES-256-GCM)."""

    KEY_BYTES = 32
    NONCE_BYTES = 12
    TAG_BYTES = 16

    @abstractmethod
    def encrypt(self, key: bytes, nonce: bytes, plaintext: bytes, aad: bytes) -> Tuple[bytes, bytes]:
        """Encrypts plaintext with key, nonce, and authenticated additional data.

        Returns: (ciphertext, 16-byte tag)
        """
        raise NotImplementedError

    @abstractmethod
    def decrypt(self, key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes, aad: bytes) -> bytes:
        """Decrypts ciphertext with key, nonce, tag, and authenticated additional data.

        Returns: plaintext bytes
        """
        raise NotImplementedError
