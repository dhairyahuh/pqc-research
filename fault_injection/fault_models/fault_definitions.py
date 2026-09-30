"""
Formal Fault Definitions, Classifications, and Metadata Schemas for PQC Fault Experiments.
Adheres strictly to the research taxonomy:
- Fault Classes: SEU, MULTI_BIT, BURST, TRANSIENT, PERSISTENT
- Outcome Classes: CORRECT, EXPECTED_REJECTION, DETECTED_FAILURE, RECOVERED,
                   INCORRECT_OUTPUT, SILENT_DATA_CORRUPTION, CRASH, TIMEOUT
"""

from enum import Enum
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


class FaultClass(str, Enum):
    SEU = "SEU"                   # Single Event Upset: 1-bit flip
    MULTI_BIT = "MULTI_BIT"       # Multiple independent bit flips
    BURST = "BURST"               # Contiguous multi-bit/byte burst corruption
    TRANSIENT = "TRANSIENT"       # Temporary value glitch
    PERSISTENT = "PERSISTENT"     # Persistent / stuck-at degradation


class OutcomeClass(str, Enum):
    CORRECT = "CORRECT"
    EXPECTED_REJECTION = "EXPECTED_REJECTION"
    DETECTED_FAILURE = "DETECTED_FAILURE"
    RECOVERED = "RECOVERED"
    INCORRECT_OUTPUT = "INCORRECT_OUTPUT"
    SILENT_DATA_CORRUPTION = "SILENT_DATA_CORRUPTION"
    CRASH = "CRASH"
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
class FaultResult:
    fault: FaultDescriptor
    baseline_result: str
    faulted_result: str
    outcome_class: OutcomeClass
    fault_detected: bool
    recovered: bool
    runtime_us: float
    memory_bytes: int
    error_code: int
    details: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["outcome_class"] = self.outcome_class.value
        return d
