"""ASTRA-Sec: LibOQS Cryptographic Adapter (Reference Baseline & Cross-Verification)."""

import ctypes
import os
import platform
from pathlib import Path
from typing import Optional, Tuple

from astra_sec.core.exceptions import AstraError
from astra_sec.crypto.base import DecapsulationStatus, DsaAdapter, KemAdapter


def _find_liboqs() -> Path:
    """Discovers installed liboqs shared library."""
    env_path = os.environ.get("LIBOQS_PATH")
    if env_path and os.path.exists(env_path):
        return Path(env_path)

    system = platform.system()
    ext = "dylib" if system == "Darwin" else "so"

    search_paths = [
        Path(f"/opt/homebrew/lib/liboqs.{ext}"),
        Path(f"/usr/local/lib/liboqs.{ext}"),
        Path(f"/usr/lib/liboqs.{ext}"),
        Path(f"/usr/lib/x86_64-linux-gnu/liboqs.{ext}"),
        Path(f"/usr/lib/aarch64-linux-gnu/liboqs.{ext}"),
    ]
    for p in search_paths:
        if p.exists():
            return p

    raise AstraError(f"liboqs.{ext} not found in system paths. Install liboqs or set LIBOQS_PATH.")


class _LibOQSBridge:
    """Low-level ctypes interface for liboqs."""

    _instance: Optional["_LibOQSBridge"] = None

    def __init__(self, lib_path: Optional[Path] = None):
        target = lib_path or _find_liboqs()
        try:
            self.cdll = ctypes.CDLL(str(target))
        except Exception as e:
            raise AstraError(f"Failed to load liboqs from {target}: {e}") from e

        # KEM function prototypes
        self.cdll.OQS_KEM_new.argtypes = [ctypes.c_char_p]
        self.cdll.OQS_KEM_new.restype = ctypes.c_void_p

        self.cdll.OQS_KEM_keypair.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        self.cdll.OQS_KEM_keypair.restype = ctypes.c_int

        self.cdll.OQS_KEM_encaps.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        self.cdll.OQS_KEM_encaps.restype = ctypes.c_int

        self.cdll.OQS_KEM_decaps.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        self.cdll.OQS_KEM_decaps.restype = ctypes.c_int

        self.cdll.OQS_KEM_free.argtypes = [ctypes.c_void_p]
        self.cdll.OQS_KEM_free.restype = None

        # SIG function prototypes
        self.cdll.OQS_SIG_new.argtypes = [ctypes.c_char_p]
        self.cdll.OQS_SIG_new.restype = ctypes.c_void_p

        self.cdll.OQS_SIG_keypair.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        self.cdll.OQS_SIG_keypair.restype = ctypes.c_int

        self.cdll.OQS_SIG_sign.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
        ]
        self.cdll.OQS_SIG_sign.restype = ctypes.c_int

        self.cdll.OQS_SIG_verify.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
        ]
        self.cdll.OQS_SIG_verify.restype = ctypes.c_int

        self.cdll.OQS_SIG_free.argtypes = [ctypes.c_void_p]
        self.cdll.OQS_SIG_free.restype = None

    @classmethod
    def get_instance(cls) -> "_LibOQSBridge":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


class OqsKemAdapter(KemAdapter):
    """Reference Baseline ML-KEM-768 Adapter backed by liboqs."""

    def __init__(self, bridge: Optional[_LibOQSBridge] = None):
        self._bridge = bridge or _LibOQSBridge.get_instance()
        self._kem_ptr = self._bridge.cdll.OQS_KEM_new(b"ML-KEM-768")
        if not self._kem_ptr:
            raise AstraError("liboqs does not support or failed to initialize ML-KEM-768.")

    def __del__(self):
        if hasattr(self, "_kem_ptr") and self._kem_ptr and hasattr(self, "_bridge"):
            self._bridge.cdll.OQS_KEM_free(self._kem_ptr)
            self._kem_ptr = None

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        pk_buf = ctypes.create_string_buffer(self.PUBLIC_KEY_BYTES)
        sk_buf = ctypes.create_string_buffer(self.SECRET_KEY_BYTES)
        rc = self._bridge.cdll.OQS_KEM_keypair(self._kem_ptr, pk_buf, sk_buf)
        if rc != 0:
            raise AstraError("liboqs ML-KEM-768 keypair generation failed.")
        return bytes(pk_buf.raw), bytes(sk_buf.raw)

    def encapsulate(self, peer_public_key: bytes) -> Tuple[bytes, bytes]:
        if len(peer_public_key) != self.PUBLIC_KEY_BYTES:
            raise ValueError(f"Invalid public key length: {len(peer_public_key)}")
        ct_buf = ctypes.create_string_buffer(self.CIPHERTEXT_BYTES)
        ss_buf = ctypes.create_string_buffer(self.SHARED_SECRET_BYTES)
        rc = self._bridge.cdll.OQS_KEM_encaps(self._kem_ptr, ct_buf, ss_buf, peer_public_key)
        if rc != 0:
            raise AstraError("liboqs ML-KEM-768 encapsulation failed.")
        return bytes(ct_buf.raw), bytes(ss_buf.raw)

    def decapsulate(self, ciphertext: bytes, secret_key: bytes) -> Tuple[bytes, DecapsulationStatus]:
        if len(ciphertext) != self.CIPHERTEXT_BYTES:
            raise ValueError(f"Invalid ciphertext length: {len(ciphertext)}")
        if len(secret_key) != self.SECRET_KEY_BYTES:
            raise ValueError(f"Invalid secret key length: {len(secret_key)}")
        ss_buf = ctypes.create_string_buffer(self.SHARED_SECRET_BYTES)
        rc = self._bridge.cdll.OQS_KEM_decaps(self._kem_ptr, ss_buf, ciphertext, secret_key)
        status = DecapsulationStatus.SUCCESS if rc == 0 else DecapsulationStatus.REJECT
        return bytes(ss_buf.raw), status


class OqsDsaAdapter(DsaAdapter):
    """Reference Baseline ML-DSA-65 Adapter backed by liboqs."""

    def __init__(self, bridge: Optional[_LibOQSBridge] = None):
        self._bridge = bridge or _LibOQSBridge.get_instance()
        self._sig_ptr = self._bridge.cdll.OQS_SIG_new(b"ML-DSA-65")
        if not self._sig_ptr:
            raise AstraError("liboqs does not support or failed to initialize ML-DSA-65.")

    def __del__(self):
        if hasattr(self, "_sig_ptr") and self._sig_ptr and hasattr(self, "_bridge"):
            self._bridge.cdll.OQS_SIG_free(self._sig_ptr)
            self._sig_ptr = None

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        pk_buf = ctypes.create_string_buffer(self.PUBLIC_KEY_BYTES)
        sk_buf = ctypes.create_string_buffer(self.SECRET_KEY_BYTES)
        rc = self._bridge.cdll.OQS_SIG_keypair(self._sig_ptr, pk_buf, sk_buf)
        if rc != 0:
            raise AstraError("liboqs ML-DSA-65 keypair generation failed.")
        return bytes(pk_buf.raw), bytes(sk_buf.raw)

    def sign(self, message: bytes, secret_key: bytes) -> bytes:
        if len(secret_key) != self.SECRET_KEY_BYTES:
            raise ValueError(f"Invalid DSA secret key length: {len(secret_key)}")
        sig_buf = ctypes.create_string_buffer(self.SIGNATURE_BYTES)
        sig_len = ctypes.c_size_t(0)
        rc = self._bridge.cdll.OQS_SIG_sign(
            self._sig_ptr, sig_buf, ctypes.byref(sig_len), message, len(message), secret_key
        )
        if rc != 0:
            raise AstraError("liboqs ML-DSA-65 signing failed.")
        return bytes(sig_buf.raw)[: sig_len.value]

    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        if len(public_key) != self.PUBLIC_KEY_BYTES or len(signature) != self.SIGNATURE_BYTES:
            return False
        rc = self._bridge.cdll.OQS_SIG_verify(
            self._sig_ptr, message, len(message), signature, len(signature), public_key
        )
        return rc == 0
