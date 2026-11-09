"""ASTRA-Sec: Monitored C Native Cryptographic Adapter (ML-KEM-768 & ML-DSA-65)."""

import ctypes
import os
import platform
from pathlib import Path
from typing import Optional, Tuple

from astra_sec.core.exceptions import AstraError
from astra_sec.crypto.base import DecapsulationStatus, DsaAdapter, KemAdapter


class MonitoredCLoadError(AstraError):
    """Raised when the native fault-monitored shared library fails to load."""


def _find_crypto_library() -> Path:
    """Locates the compiled libastra_crypto shared library."""
    # 1. Environment variable override
    env_path = os.environ.get("ASTRA_CRYPTO_LIB_PATH")
    if env_path and os.path.exists(env_path):
        return Path(env_path)

    # 2. Check repo root / bin
    base_dir = Path(__file__).resolve().parent.parent.parent
    system = platform.system()
    ext = "dylib" if system == "Darwin" else "so"
    candidate = base_dir / "bin" / f"libastra_crypto.{ext}"
    if candidate.exists():
        return candidate

    # 3. Check current working directory
    cwd_candidate = Path(f"bin/libastra_crypto.{ext}")
    if cwd_candidate.exists():
        return cwd_candidate.resolve()

    raise MonitoredCLoadError(
        f"Monitored C cryptographic engine library not found at {candidate}. "
        "Run 'make' to compile bin/libastra_crypto."
    )


class _NativeBridge:
    """Singleton C-FFI wrapper binding ctypes to libastra_crypto."""

    _instance: Optional["_NativeBridge"] = None

    def __init__(self, lib_path: Optional[Path] = None):
        target = lib_path or _find_crypto_library()
        try:
            self.cdll = ctypes.CDLL(str(target))
        except Exception as e:
            raise MonitoredCLoadError(f"Failed to load shared library {target}: {e}") from e

        # astra_kem768_keypair(uint8_t *pk, uint8_t *sk)
        self.cdll.astra_kem768_keypair.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        self.cdll.astra_kem768_keypair.restype = ctypes.c_int

        # astra_kem768_encaps(uint8_t *ct, uint8_t *ss, const uint8_t *pk)
        self.cdll.astra_kem768_encaps.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        self.cdll.astra_kem768_encaps.restype = ctypes.c_int

        # astra_kem768_decaps_monitored(uint8_t *ss, const uint8_t *ct, const uint8_t *sk, uint32_t *status)
        self.cdll.astra_kem768_decaps_monitored.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        self.cdll.astra_kem768_decaps_monitored.restype = ctypes.c_int

        # astra_dsa65_keypair(uint8_t *pk, uint8_t *sk)
        self.cdll.astra_dsa65_keypair.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        self.cdll.astra_dsa65_keypair.restype = ctypes.c_int

        # astra_dsa65_sign(uint8_t *sig, size_t *sig_len, const uint8_t *msg, size_t msg_len, const uint8_t *sk)
        self.cdll.astra_dsa65_sign.argtypes = [
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_char_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
        ]
        self.cdll.astra_dsa65_sign.restype = ctypes.c_int

        # astra_dsa65_verify(const uint8_t *sig, size_t sig_len, const uint8_t *msg, size_t msg_len, const uint8_t *pk)
        self.cdll.astra_dsa65_verify.argtypes = [
            ctypes.c_char_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
            ctypes.c_size_t,
            ctypes.c_char_p,
        ]
        self.cdll.astra_dsa65_verify.restype = ctypes.c_int

    @classmethod
    def get_instance(cls) -> "_NativeBridge":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


class MonitoredNativeKemAdapter(KemAdapter):
    """Monitored ML-KEM-768 Native C Implementation (Primary Intended Research Path)."""

    def __init__(self, bridge: Optional[_NativeBridge] = None):
        self._bridge = bridge or _NativeBridge.get_instance()

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        pk_buf = ctypes.create_string_buffer(self.PUBLIC_KEY_BYTES)
        sk_buf = ctypes.create_string_buffer(self.SECRET_KEY_BYTES)
        rc = self._bridge.cdll.astra_kem768_keypair(pk_buf, sk_buf)
        if rc != 0:
            raise AstraError("Native ML-KEM-768 keypair generation failed.")
        return bytes(pk_buf.raw), bytes(sk_buf.raw)

    def encapsulate(self, peer_public_key: bytes) -> Tuple[bytes, bytes]:
        if len(peer_public_key) != self.PUBLIC_KEY_BYTES:
            raise ValueError(
                f"Invalid peer public key size: expected {self.PUBLIC_KEY_BYTES}, got {len(peer_public_key)}"
            )
        ct_buf = ctypes.create_string_buffer(self.CIPHERTEXT_BYTES)
        ss_buf = ctypes.create_string_buffer(self.SHARED_SECRET_BYTES)
        rc = self._bridge.cdll.astra_kem768_encaps(ct_buf, ss_buf, peer_public_key)
        if rc != 0:
            raise AstraError("Native ML-KEM-768 encapsulation failed.")
        return bytes(ct_buf.raw), bytes(ss_buf.raw)

    def decapsulate(self, ciphertext: bytes, secret_key: bytes) -> Tuple[bytes, DecapsulationStatus]:
        if len(ciphertext) != self.CIPHERTEXT_BYTES:
            raise ValueError(
                f"Invalid ciphertext size: expected {self.CIPHERTEXT_BYTES}, got {len(ciphertext)}"
            )
        if len(secret_key) != self.SECRET_KEY_BYTES:
            raise ValueError(
                f"Invalid secret key size: expected {self.SECRET_KEY_BYTES}, got {len(secret_key)}"
            )
        ss_buf = ctypes.create_string_buffer(self.SHARED_SECRET_BYTES)
        raw_status = ctypes.c_uint32(0)
        rc = self._bridge.cdll.astra_kem768_decaps_monitored(
            ss_buf, ciphertext, secret_key, ctypes.byref(raw_status)
        )
        if rc != 0:
            raise AstraError(f"Native ML-KEM-768 decapsulation invocation returned error code {rc}.")
        status = DecapsulationStatus.from_code(raw_status.value)
        return bytes(ss_buf.raw), status


class MonitoredNativeDsaAdapter(DsaAdapter):
    """Monitored ML-DSA-65 Native C Implementation (Primary Intended Research Path)."""

    def __init__(self, bridge: Optional[_NativeBridge] = None):
        self._bridge = bridge or _NativeBridge.get_instance()

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        pk_buf = ctypes.create_string_buffer(self.PUBLIC_KEY_BYTES)
        sk_buf = ctypes.create_string_buffer(self.SECRET_KEY_BYTES)
        rc = self._bridge.cdll.astra_dsa65_keypair(pk_buf, sk_buf)
        if rc != 0:
            raise AstraError("Native ML-DSA-65 keypair generation failed.")
        return bytes(pk_buf.raw), bytes(sk_buf.raw)

    def sign(self, message: bytes, secret_key: bytes) -> bytes:
        if len(secret_key) != self.SECRET_KEY_BYTES:
            raise ValueError(
                f"Invalid DSA secret key length: expected {self.SECRET_KEY_BYTES}, got {len(secret_key)}"
            )
        sig_buf = ctypes.create_string_buffer(self.SIGNATURE_BYTES)
        sig_len = ctypes.c_size_t(0)
        rc = self._bridge.cdll.astra_dsa65_sign(
            sig_buf, ctypes.byref(sig_len), message, len(message), secret_key
        )
        if rc != 0 or sig_len.value != self.SIGNATURE_BYTES:
            raise AstraError("Native ML-DSA-65 signature generation failed.")
        return bytes(sig_buf.raw)

    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        if len(public_key) != self.PUBLIC_KEY_BYTES or len(signature) != self.SIGNATURE_BYTES:
            return False
        rc = self._bridge.cdll.astra_dsa65_verify(
            signature, len(signature), message, len(message), public_key
        )
        return rc == 0
