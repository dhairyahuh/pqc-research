"""
Formal Fault Definitions, Classifications, and Metadata Schemas for PQC Fault Experiments.
Adheres strictly to the corrected research taxonomy:

Cryptographic Layer Outcomes:
- CORRECT_VALID_DECAPSULATION: Legitimate cryptographic output matches ground truth.
- EXPECTED_IMPLICIT_REJECTION: Cryptographically expected FO transform behavior on invalid input.
- EXPECTED_SIGNATURE_REJECTION: Cryptographically expected signature verification rejection on tampered input.
- EXPLICIT_ERROR: Handled error code returned by implementation (e.g. invalid modulus / deserialization check).
- UNEXPECTED_INCORRECT_OUTPUT: Undetected invalid output violating specification guarantees.
- CRASH: Uncaught exception, segmentation fault, or process abort.
- TIMEOUT: Infinite loop, hang, or watchdog expiration.

System/Protocol Layer Outcomes:
- KEY_MATCH: Spacecraft and Ground session keys identical.
- KEY_MISMATCH_DETECTED: Session key divergence detected by protocol (e.g. MAC/AEAD authentication failure).
- KEY_MISMATCH_UNDETECTED: Session key divergence unhandled, resulting in silent payload corruption.
- SESSION_ABORTED: Handled session termination.
- SESSION_RECOVERED: Session re-established via retry / handshake recovery.
"""

from enum import Enum
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


class FaultClass(str, Enum):
    SEU = "SEU"                   # Single Event Upset: 1-bit flip
    MULTI_BIT = "MULTI_BIT"       # Multiple independent bit flips
    BURST = "BURST"               # Contiguous multi-bit/byte burst corruption
    TRANSIENT = "TRANSIENT"       # Temporary arithmetic / intermediate value glitch
    PERSISTENT = "PERSISTENT"     # Persistent / stuck-at memory degradation


class CryptoOutcomeClass(str, Enum):
    CORRECT_VALID_DECAPSULATION = "CORRECT_VALID_DECAPSULATION"
    EXPECTED_IMPLICIT_REJECTION = "EXPECTED_IMPLICIT_REJECTION"
    EXPECTED_SIGNATURE_REJECTION = "EXPECTED_SIGNATURE_REJECTION"
    EXPLICIT_ERROR = "EXPLICIT_ERROR"
    UNEXPECTED_INCORRECT_OUTPUT = "UNEXPECTED_INCORRECT_OUTPUT"
    CRASH = "CRASH"
    TIMEOUT = "TIMEOUT"


class ProtocolOutcomeClass(str, Enum):
    KEY_MATCH = "KEY_MATCH"
    KEY_MISMATCH_DETECTED = "KEY_MISMATCH_DETECTED"
    KEY_MISMATCH_UNDETECTED = "KEY_MISMATCH_UNDETECTED"
    SESSION_ABORTED = "SESSION_ABORTED"
    SESSION_RECOVERED = "SESSION_RECOVERED"
    TIMEOUT = "TIMEOUT"


@dataclass
class FaultDescriptor:
    experiment_id: str
    algorithm: str
    parameter_set: str
    fault_class: str
    fault_type: str
    target: str
    target_index: int
    bit_index: int
    injection_stage: str
    injection_time: float
    seed: int
    duration: int
    magnitude: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CryptoFaultResult:
    fault: FaultDescriptor
    baseline_result: str
    faulted_result: str
    outcome_class: CryptoOutcomeClass
    fault_detected: bool
    runtime_us: float
    memory_bytes: int
    error_code: int
    details: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["outcome_class"] = self.outcome_class.value
        return d


@dataclass
class ProtocolFaultResult:
    fault: FaultDescriptor
    ground_key: str
    spacecraft_key: str
    keys_match: bool
    protocol_outcome: ProtocolOutcomeClass
    detection_latency_us: float
    details: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["protocol_outcome"] = self.protocol_outcome.value
        return d
