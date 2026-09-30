"""
Post-Quantum Cryptography Reference Wrapper for ML-KEM (FIPS 203) and ML-DSA (FIPS 204).
Interfaces directly with liboqs (Open Quantum Safe) dynamic library via ctypes.
Provides high-performance, standards-compliant baseline operations with raw memory buffer access.
"""

import ctypes
import os
from typing import Tuple, Optional

# Locate liboqs dynamic library
POSSIBLE_LIB_PATHS = [
    "/opt/homebrew/lib/liboqs.dylib",
    "/usr/local/lib/liboqs.dylib",
    "/usr/lib/liboqs.dylib",
    os.path.expanduser("~/.local/lib/liboqs.dylib")
]

_oqs_lib_path = None
for path in POSSIBLE_LIB_PATHS:
    if os.path.exists(path):
        _oqs_lib_path = path
        break

if not _oqs_lib_path:
    raise RuntimeError("Could not find liboqs.dylib in standard search paths.")

liboqs = ctypes.CDLL(_oqs_lib_path)

# Status codes
OQS_STATUS_SUCCESS = 0
OQS_STATUS_ERROR = -1

# Initialize liboqs
liboqs.OQS_init()
liboqs.OQS_version.restype = ctypes.c_char_p


class OQS_KEM_STRUCT(ctypes.Structure):
    _fields_ = [
        ("method_name", ctypes.c_char_p),
        ("alg_version", ctypes.c_char_p),
        ("claimed_nist_level", ctypes.c_uint8),
        ("ind_cca", ctypes.c_bool),
        ("length_public_key", ctypes.c_size_t),
        ("length_secret_key", ctypes.c_size_t),
        ("length_ciphertext", ctypes.c_size_t),
        ("length_shared_secret", ctypes.c_size_t),
        # Function pointers follow, not needed for direct wrapper invocation
    ]


class OQS_SIG_STRUCT(ctypes.Structure):
    _fields_ = [
        ("method_name", ctypes.c_char_p),
        ("alg_version", ctypes.c_char_p),
        ("claimed_nist_level", ctypes.c_uint8),
        ("euf_cma", ctypes.c_bool),
        ("suf_cma", ctypes.c_bool),
        ("sig_with_ctx_support", ctypes.c_bool),
        ("length_public_key", ctypes.c_size_t),
        ("length_secret_key", ctypes.c_size_t),
        ("length_signature", ctypes.c_size_t),
    ]


# Function prototypes
liboqs.OQS_KEM_new.argtypes = [ctypes.c_char_p]
liboqs.OQS_KEM_new.restype = ctypes.POINTER(OQS_KEM_STRUCT)

liboqs.OQS_KEM_free.argtypes = [ctypes.POINTER(OQS_KEM_STRUCT)]
liboqs.OQS_KEM_free.restype = None

liboqs.OQS_KEM_keypair.argtypes = [
    ctypes.POINTER(OQS_KEM_STRUCT),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.POINTER(ctypes.c_uint8)
]
liboqs.OQS_KEM_keypair.restype = ctypes.c_int

liboqs.OQS_KEM_encaps.argtypes = [
    ctypes.POINTER(OQS_KEM_STRUCT),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.POINTER(ctypes.c_uint8)
]
liboqs.OQS_KEM_encaps.restype = ctypes.c_int

liboqs.OQS_KEM_decaps.argtypes = [
    ctypes.POINTER(OQS_KEM_STRUCT),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.POINTER(ctypes.c_uint8)
]
liboqs.OQS_KEM_decaps.restype = ctypes.c_int

liboqs.OQS_SIG_new.argtypes = [ctypes.c_char_p]
liboqs.OQS_SIG_new.restype = ctypes.POINTER(OQS_SIG_STRUCT)

liboqs.OQS_SIG_free.argtypes = [ctypes.POINTER(OQS_SIG_STRUCT)]
liboqs.OQS_SIG_free.restype = None

liboqs.OQS_SIG_keypair.argtypes = [
    ctypes.POINTER(OQS_SIG_STRUCT),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.POINTER(ctypes.c_uint8)
]
liboqs.OQS_SIG_keypair.restype = ctypes.c_int

liboqs.OQS_SIG_sign.argtypes = [
    ctypes.POINTER(OQS_SIG_STRUCT),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.POINTER(ctypes.c_size_t),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_uint8)
]
liboqs.OQS_SIG_sign.restype = ctypes.c_int

liboqs.OQS_SIG_verify.argtypes = [
    ctypes.POINTER(OQS_SIG_STRUCT),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_uint8)
]
liboqs.OQS_SIG_verify.restype = ctypes.c_int


def get_liboqs_version() -> str:
    """Returns the installed liboqs version string."""
    return liboqs.OQS_version().decode("utf-8")


class MLKEM:
    """
    Python wrapper for ML-KEM (FIPS 203) instances:
    - ML-KEM-512
    - ML-KEM-768
    - ML-KEM-1024
    """

    ALLOWED_ALGORITHMS = {
        "ML-KEM-512": b"ML-KEM-512",
        "ML-KEM-768": b"ML-KEM-768",
        "ML-KEM-1024": b"ML-KEM-1024"
    }

    def __init__(self, alg_name: str = "ML-KEM-768"):
        if alg_name not in self.ALLOWED_ALGORITHMS:
            raise ValueError(f"Unknown algorithm: {alg_name}. Must be one of {list(self.ALLOWED_ALGORITHMS.keys())}")
        self.alg_name = alg_name
        self._c_alg_name = self.ALLOWED_ALGORITHMS[alg_name]
        self._kem = liboqs.OQS_KEM_new(self._c_alg_name)
        if not self._kem:
            raise RuntimeError(f"Failed to instantiate KEM: {alg_name}")

        self.length_public_key = self._kem.contents.length_public_key
        self.length_secret_key = self._kem.contents.length_secret_key
        self.length_ciphertext = self._kem.contents.length_ciphertext
        self.length_shared_secret = self._kem.contents.length_shared_secret

    def keypair(self) -> Tuple[bytes, bytes]:
        """
        Generates (public_key, secret_key).
        Returns raw byte arrays.
        """
        pk = (ctypes.c_uint8 * self.length_public_key)()
        sk = (ctypes.c_uint8 * self.length_secret_key)()
        rc = liboqs.OQS_KEM_keypair(self._kem, pk, sk)
        if rc != OQS_STATUS_SUCCESS:
            raise RuntimeError(f"ML-KEM keypair generation failed with status {rc}")
        return bytes(pk), bytes(sk)

    def encaps(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """
        Encapsulates a shared secret under the given public key.
        Returns (ciphertext, shared_secret).
        """
        if len(public_key) != self.length_public_key:
            raise ValueError(f"Invalid public key length {len(public_key)}, expected {self.length_public_key}")

        pk_buf = (ctypes.c_uint8 * self.length_public_key).from_buffer_copy(public_key)
        ct_buf = (ctypes.c_uint8 * self.length_ciphertext)()
        ss_buf = (ctypes.c_uint8 * self.length_shared_secret)()

        rc = liboqs.OQS_KEM_encaps(self._kem, ct_buf, ss_buf, pk_buf)
        if rc != OQS_STATUS_SUCCESS:
            raise RuntimeError(f"ML-KEM encapsulation failed with status {rc}")
        return bytes(ct_buf), bytes(ss_buf)

    def decaps(self, ciphertext: bytes, secret_key: bytes) -> bytes:
        """
        Decapsulates the ciphertext using the given secret key.
        Returns shared_secret (or pseudorandom value if ciphertext is invalid - implicit rejection).
        """
        if len(ciphertext) != self.length_ciphertext:
            raise ValueError(f"Invalid ciphertext length {len(ciphertext)}, expected {self.length_ciphertext}")
        if len(secret_key) != self.length_secret_key:
            raise ValueError(f"Invalid secret key length {len(secret_key)}, expected {self.length_secret_key}")

        ct_buf = (ctypes.c_uint8 * self.length_ciphertext).from_buffer_copy(ciphertext)
        sk_buf = (ctypes.c_uint8 * self.length_secret_key).from_buffer_copy(secret_key)
        ss_buf = (ctypes.c_uint8 * self.length_shared_secret)()

        rc = liboqs.OQS_KEM_decaps(self._kem, ss_buf, ct_buf, sk_buf)
        if rc != OQS_STATUS_SUCCESS:
            raise RuntimeError(f"ML-KEM decapsulation failed with status {rc}")
        return bytes(ss_buf)

    def __del__(self):
        if hasattr(self, "_kem") and self._kem:
            liboqs.OQS_KEM_free(self._kem)
            self._kem = None


class MLDSA:
    """
    Python wrapper for ML-DSA (FIPS 204) instances:
    - ML-DSA-44
    - ML-DSA-65
    - ML-DSA-87
    """

    ALLOWED_ALGORITHMS = {
        "ML-DSA-44": b"ML-DSA-44",
        "ML-DSA-65": b"ML-DSA-65",
        "ML-DSA-87": b"ML-DSA-87"
    }

    def __init__(self, alg_name: str = "ML-DSA-65"):
        if alg_name not in self.ALLOWED_ALGORITHMS:
            raise ValueError(f"Unknown algorithm: {alg_name}. Must be one of {list(self.ALLOWED_ALGORITHMS.keys())}")
        self.alg_name = alg_name
        self._c_alg_name = self.ALLOWED_ALGORITHMS[alg_name]
        self._sig = liboqs.OQS_SIG_new(self._c_alg_name)
        if not self._sig:
            raise RuntimeError(f"Failed to instantiate SIG: {alg_name}")

        self.length_public_key = self._sig.contents.length_public_key
        self.length_secret_key = self._sig.contents.length_secret_key
        self.length_signature = self._sig.contents.length_signature

    def keypair(self) -> Tuple[bytes, bytes]:
        """
        Generates (public_key, secret_key).
        Returns raw byte arrays.
        """
        pk = (ctypes.c_uint8 * self.length_public_key)()
        sk = (ctypes.c_uint8 * self.length_secret_key)()
        rc = liboqs.OQS_SIG_keypair(self._sig, pk, sk)
        if rc != OQS_STATUS_SUCCESS:
            raise RuntimeError(f"ML-DSA keypair generation failed with status {rc}")
        return bytes(pk), bytes(sk)

    def sign(self, message: bytes, secret_key: bytes) -> bytes:
        """
        Signs the message using secret_key.
        Returns the generated signature.
        """
        if len(secret_key) != self.length_secret_key:
            raise ValueError(f"Invalid secret key length {len(secret_key)}, expected {self.length_secret_key}")

        msg_buf = (ctypes.c_uint8 * len(message)).from_buffer_copy(message)
        sk_buf = (ctypes.c_uint8 * self.length_secret_key).from_buffer_copy(secret_key)
        sig_buf = (ctypes.c_uint8 * self.length_signature)()
        sig_len = ctypes.c_size_t(0)

        rc = liboqs.OQS_SIG_sign(self._sig, sig_buf, ctypes.byref(sig_len), msg_buf, len(message), sk_buf)
        if rc != OQS_STATUS_SUCCESS:
            raise RuntimeError(f"ML-DSA sign failed with status {rc}")
        return bytes(sig_buf[:sig_len.value])

    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """
        Verifies the signature on message with public_key.
        Returns True if valid, False if rejected or corrupted.
        """
        if len(public_key) != self.length_public_key:
            raise ValueError(f"Invalid public key length {len(public_key)}, expected {self.length_public_key}")

        msg_buf = (ctypes.c_uint8 * len(message)).from_buffer_copy(message)
        sig_buf = (ctypes.c_uint8 * len(signature)).from_buffer_copy(signature)
        pk_buf = (ctypes.c_uint8 * self.length_public_key).from_buffer_copy(public_key)

        rc = liboqs.OQS_SIG_verify(self._sig, msg_buf, len(message), sig_buf, len(signature), pk_buf)
        return rc == OQS_STATUS_SUCCESS

    def __del__(self):
        if hasattr(self, "_sig") and self._sig:
            liboqs.OQS_SIG_free(self._sig)
            self._sig = None
