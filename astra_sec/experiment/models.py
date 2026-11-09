"""ASTRA-Sec: Experimental Trial Data Models & Taxonomy (Prompt 10)."""

from enum import Enum
import time
import uuid
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ExperimentGroup(str, Enum):
    GROUP_A = "GROUP_A_MESSAGE_SECURITY"
    GROUP_B = "GROUP_B_NETWORK_DISRUPTION"
    GROUP_C = "GROUP_C_CRYPTOGRAPHIC_FAULTS"
    GROUP_D = "GROUP_D_CHECKER_INDEPENDENCE"
    GROUP_E = "GROUP_E_CROSS_LAYER_FAILURE"


class TrialOutcome(str, Enum):
    PASS_CLEAN = "PASS_CLEAN"
    DETECTED_AND_RECOVERED = "DETECTED_AND_RECOVERED"
    DETECTED_AND_REJECTED = "DETECTED_AND_REJECTED"
    DETECTED_AND_FAIL_STOP = "DETECTED_AND_FAIL_STOP"
    SUPPRESSED_SILENT_CORRUPTION = "SUPPRESSED_SILENT_CORRUPTION"
    FAILED_SILENT_DATA_CORRUPTION = "FAILED_SILENT_DATA_CORRUPTION"  # SDC (Must NEVER happen)


class TrialRecord(BaseModel):
    """Rigorous audit record for an individual fault injection or adversarial experiment trial."""

    trial_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    experiment_id: str
    group: ExperimentGroup
    test_name: str
    timestamp_utc: int = Field(default_factory=lambda: int(time.time()))
    build_version: str = "0.1.0"
    commit_hash: str = "2cac90f"
    algorithm: str = "ML-KEM-768 + ML-DSA-65 + AES-256-GCM"
    parameter_set: str = "NIST-FIPS-203-768 / NIST-FIPS-204-65"
    node: str
    operation: str
    fault_type: str
    fault_location: str
    fault_timing: str
    configuration: Dict[str, Any] = Field(default_factory=dict)
    random_seed: int = 42
    detection_result: bool
    recovery_result: str
    final_message_correctness: bool
    sdc_outcome: bool = Field(default=False, description="True if Silent Data Corruption occurred (FAILURE)")
    latency_ms: float = 0.0
    error_classification: str
    details: Dict[str, Any] = Field(default_factory=dict)
