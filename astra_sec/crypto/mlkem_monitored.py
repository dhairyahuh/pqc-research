"""ASTRA-Sec: Monitored ML-KEM-768 Native Cryptographic Adapter with TFIB-Ref & Invariant Telemetry."""

import ctypes
import os
import platform
from enum import IntEnum
from pathlib import Path
from typing import Optional, Tuple

from pydantic import BaseModel, Field

from astra_sec.core.exceptions import AstraError
from astra_sec.crypto.base import DecapsulationStatus, KemAdapter


class AstraFaultStatus(IntEnum):
    """Categorized Fault Resilience Status Codes."""

    SUCCESS = 0
    RECOVERED = 1
    PERSISTENT = 2
    UNRECOVERABLE = 3
    INVALID_INPUT = 4
    CHECKER_FAILURE = 5


class MlkemTelemetry(BaseModel):
    """Execution telemetry captured during fault-resilient ML-KEM decapsulation."""

    status: AstraFaultStatus = Field(..., description="Categorized resilience outcome")
    raw_internal_code: int = Field(..., description="FIPS 203 status word (0x5A5A5A5A, 0xFFFFFFFF, etc.)")
    butterflies_executed: int = Field(default=0, description="Total butterflies monitored (5376 CT + 4480 GS)")
    mismatch_count: int = Field(default=0, description="Invariant violations detected")
    retry_count: int = Field(default=0, description="In-place rollback attempts performed")
    recovered_count: int = Field(default=0, description="Successful transient recoveries")
    persistent_count: int = Field(default=0, description="Persistent faults detected")
    twiddle_faults_detected: int = Field(default=0, description="Twiddle table mismatches caught via TFIB-Ref")
    last_failed_layer: int = Field(default=-1, description="Layer index where last fault was caught")
    last_failed_butterfly: int = Field(default=-1, description="Butterfly index where last fault was caught")
    fail_stop_engaged: bool = Field(default=False, description="True if implicit rejection suppression occurred")

    @property
    def is_clean(self) -> bool:
        return self.status == AstraFaultStatus.SUCCESS and self.mismatch_count == 0

    @property
    def is_recovered(self) -> bool:
        return self.status == AstraFaultStatus.RECOVERED and self.recovered_count > 0

    @property
    def is_fail_stop(self) -> bool:
        return self.fail_stop_engaged or self.status in (
            AstraFaultStatus.PERSISTENT,
            AstraFaultStatus.UNRECOVERABLE,
            AstraFaultStatus.CHECKER_FAILURE,
        )


class _CTelemetryStruct(ctypes.Structure):
    _fields_ = [
        ("status", ctypes.c_int),
        ("raw_internal_code", ctypes.c_uint32),
        ("butterflies_executed", ctypes.c_uint32),
        ("mismatch_count", ctypes.c_uint32),
        ("retry_count", ctypes.c_uint32),
        ("recovered_count", ctypes.c_uint32),
        ("persistent_count", ctypes.c_uint32),
        ("twiddle_faults_detected", ctypes.c_uint32),
        ("last_failed_layer", ctypes.c_int),
        ("last_failed_butterfly", ctypes.c_int),
        ("fail_stop_engaged", ctypes.c_bool),
    ]


class MonitoredMlkemError(AstraError):
    """Raised when monitored ML-KEM decapsulation fails or detects unrecoverable faults."""

    def __init__(self, message: str, telemetry: Optional[MlkemTelemetry] = None):
        super().__init__(message)
        self.telemetry = telemetry


def _locate_crypto_library() -> Path:
    """Locates the compiled libastra_crypto shared library."""
    env_path = os.environ.get("ASTRA_CRYPTO_LIB_PATH")
    if env_path and os.path.exists(env_path):
        return Path(env_path)

    base_dir = Path(__file__).resolve().parent.parent.parent
    system = platform.system()
    ext = "dylib" if system == "Darwin" else "so"
    candidate = base_dir / "bin" / f"libastra_crypto.{ext}"
    if candidate.exists():
        return candidate

    cwd_candidate = Path(f"bin/libastra_crypto.{ext}")
    if cwd_candidate.exists():
        return cwd_candidate.resolve()

    raise MonitoredMlkemError(
        f"Native cryptographic shared library not found at {candidate}. "
        "Run 'make' to build bin/libastra_crypto."
    )


class MonitoredMlkemAdapter(KemAdapter):
    """Full Monitored ML-KEM-768 Native C Implementation with Invariant Telemetry & TFIB-Ref."""

    _instance: Optional["MonitoredMlkemAdapter"] = None

    def __init__(self, lib_path: Optional[Path] = None):
        target = lib_path or _locate_crypto_library()
        try:
            self._cdll = ctypes.CDLL(str(target))
        except Exception as e:
            raise MonitoredMlkemError(f"Failed to load shared library {target}: {e}") from e

        # Function signatures
        self._cdll.astra_mlkem_get_version.restype = ctypes.c_uint32
        self._cdll.astra_mlkem_keypair.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self._cdll.astra_mlkem_keypair.restype = ctypes.c_int

        self._cdll.astra_mlkem_encaps.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        self._cdll.astra_mlkem_encaps.restype = ctypes.c_int

        self._cdll.astra_mlkem_decaps_monitored.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(_CTelemetryStruct),
        ]
        self._cdll.astra_mlkem_decaps_monitored.restype = ctypes.c_int

        # Fault injection controls
        self._cdll.astra_mlkem_inject_op_twiddle_fault.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint8,
            ctypes.c_bool,
        ]
        self._cdll.astra_mlkem_inject_op_twiddle_fault.restype = ctypes.c_int

        self._cdll.astra_mlkem_inject_ref_twiddle_fault.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint8,
            ctypes.c_bool,
        ]
        self._cdll.astra_mlkem_inject_ref_twiddle_fault.restype = ctypes.c_int

        self._cdll.astra_mlkem_inject_checker_logic_fault.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_bool,
        ]
        self._cdll.astra_mlkem_inject_checker_logic_fault.restype = ctypes.c_int

        self._cdll.astra_mlkem_reset_faults.restype = ctypes.c_int

    @property
    def api_version(self) -> int:
        return self._cdll.astra_mlkem_get_version()

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        pk_buf = ctypes.create_string_buffer(self.PUBLIC_KEY_BYTES)
        sk_buf = ctypes.create_string_buffer(self.SECRET_KEY_BYTES)
        rc = self._cdll.astra_mlkem_keypair(pk_buf, sk_buf)
        if rc != 0:
            raise MonitoredMlkemError("Failed to generate ML-KEM-768 keypair.")
        return bytes(pk_buf.raw), bytes(sk_buf.raw)

    def encapsulate(self, peer_public_key: bytes) -> Tuple[bytes, bytes]:
        if len(peer_public_key) != self.PUBLIC_KEY_BYTES:
            raise ValueError(f"Invalid peer public key length: expected {self.PUBLIC_KEY_BYTES}")
        ct_buf = ctypes.create_string_buffer(self.CIPHERTEXT_BYTES)
        ss_buf = ctypes.create_string_buffer(self.SHARED_SECRET_BYTES)
        rc = self._cdll.astra_mlkem_encaps(ct_buf, ss_buf, peer_public_key)
        if rc != 0:
            raise MonitoredMlkemError("Failed to encapsulate shared secret.")
        return bytes(ct_buf.raw), bytes(ss_buf.raw)

    def decapsulate_with_telemetry(
        self, ciphertext: bytes, secret_key: bytes
    ) -> Tuple[bytes, MlkemTelemetry]:
        """Decapsulates shared secret and returns comprehensive fault telemetry."""
        if len(ciphertext) != self.CIPHERTEXT_BYTES:
            raise ValueError(f"Invalid ciphertext length: expected {self.CIPHERTEXT_BYTES}")
        if len(secret_key) != self.SECRET_KEY_BYTES:
            raise ValueError(f"Invalid secret key length: expected {self.SECRET_KEY_BYTES}")

        ss_buf = ctypes.create_string_buffer(self.SHARED_SECRET_BYTES)
        c_telem = _CTelemetryStruct()

        rc = self._cdll.astra_mlkem_decaps_monitored(
            ss_buf, ciphertext, secret_key, ctypes.byref(c_telem)
        )

        telemetry = MlkemTelemetry(
            status=AstraFaultStatus(c_telem.status),
            raw_internal_code=c_telem.raw_internal_code,
            butterflies_executed=c_telem.butterflies_executed,
            mismatch_count=c_telem.mismatch_count,
            retry_count=c_telem.retry_count,
            recovered_count=c_telem.recovered_count,
            persistent_count=c_telem.persistent_count,
            twiddle_faults_detected=c_telem.twiddle_faults_detected,
            last_failed_layer=c_telem.last_failed_layer,
            last_failed_butterfly=c_telem.last_failed_butterfly,
            fail_stop_engaged=c_telem.fail_stop_engaged,
        )

        # Invariant: Corrupted shared secret must never be accepted as valid
        if rc != 0 or telemetry.is_fail_stop:
            raise MonitoredMlkemError(
                f"Decapsulation fault suppression engaged: {telemetry.status.name} "
                f"(persistent={telemetry.persistent_count}, raw=0x{telemetry.raw_internal_code:08X})",
                telemetry=telemetry,
            )

        return bytes(ss_buf.raw), telemetry

    def decapsulate(self, ciphertext: bytes, secret_key: bytes) -> Tuple[bytes, DecapsulationStatus]:
        """Implements the standard KemAdapter interface with DecapsulationStatus."""
        try:
            ss, telemetry = self.decapsulate_with_telemetry(ciphertext, secret_key)
            return ss, DecapsulationStatus.SUCCESS
        except MonitoredMlkemError as e:
            if e.telemetry:
                if e.telemetry.status == AstraFaultStatus.PERSISTENT:
                    return b"\x00" * 32, DecapsulationStatus.FAULT
                elif e.telemetry.status == AstraFaultStatus.UNRECOVERABLE:
                    return b"\x00" * 32, DecapsulationStatus.FAULT
            return b"\x00" * 32, DecapsulationStatus.REJECT

    # Fault injection controls for experimentation & verification
    def inject_op_twiddle_fault(self, layer: int = 2, butterfly: int = 17, bit: int = 3, persistent: bool = False):
        self._cdll.astra_mlkem_inject_op_twiddle_fault(layer, butterfly, bit, persistent)

    def inject_ref_twiddle_fault(self, layer: int = 4, butterfly: int = 12, bit: int = 7, persistent: bool = False):
        self._cdll.astra_mlkem_inject_ref_twiddle_fault(layer, butterfly, bit, persistent)

    def inject_checker_logic_fault(self, layer: int = 3, butterfly: int = 10, persistent: bool = False):
        self._cdll.astra_mlkem_inject_checker_logic_fault(layer, butterfly, persistent)

    def reset_faults(self):
        self._cdll.astra_mlkem_reset_faults()
