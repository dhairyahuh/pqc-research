"""ASTRA-Sec Phase 3: Experiment Configuration Schema and Manager.

Provides typed Pydantic v2 models for configuring reproducible experiments,
workloads, network impairments, fault injections, and baseline comparisons.
"""

import hashlib
import json
import os
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class BaselineType(str, Enum):
    BASELINE_A_NON_PQC = "BASELINE_A_NON_PQC"
    BASELINE_B_UNMONITORED_PQC = "BASELINE_B_UNMONITORED_PQC"
    BASELINE_C_MONITORED_PQC = "BASELINE_C_MONITORED_PQC"
    BASELINE_D_DTN_UNCOORDINATED = "BASELINE_D_DTN_UNCOORDINATED"
    TREATMENT_E_FULL_ASTRA_SEC = "TREATMENT_E_FULL_ASTRA_SEC"


class ImpairmentConfig(BaseModel):
    delay_ms: float = Field(0.0, ge=0.0, description="Fixed delay added per hop in ms")
    jitter_ms: float = Field(0.0, ge=0.0, description="Uniform random jitter added in ms")
    loss_rate: float = Field(0.0, ge=0.0, le=1.0, description="Packet loss probability [0.0, 1.0]")
    duplication_rate: float = Field(0.0, ge=0.0, le=1.0, description="Packet duplication probability")
    reorder_rate: float = Field(0.0, ge=0.0, le=1.0, description="Packet reordering probability")
    bandwidth_kbps: Optional[float] = Field(None, gt=0.0, description="Bandwidth throttling limit in kbps")
    outage_duration_s: float = Field(0.0, ge=0.0, description="Duration of initial link outage in seconds")
    outage_start_s: float = Field(0.0, ge=0.0, description="Offset when link outage triggers")


class FaultConfig(BaseModel):
    enabled: bool = Field(False, description="Whether cryptographic fault injection is active")
    fault_type: str = Field("none", description="Fault type: transient_seu, persistent_stuck_bit, twiddle_corrupt, multi_bit")
    target_layer: int = Field(0, ge=0, le=7, description="NTT stage layer target [0-7]")
    bit_position: int = Field(0, ge=0, le=15, description="Bit position flipped [0-15]")
    injection_probability: float = Field(1.0, ge=0.0, le=1.0, description="Probability of fault activation")
    retry_budget_exhaustion: bool = Field(False, description="Forces persistent corruption to exhaust K=2")


class WorkloadConfig(BaseModel):
    payload_size_bytes: int = Field(256, ge=16, le=1048576, description="Payload size in bytes (16 B - 1 MB)")
    total_messages: int = Field(10, ge=1, le=100000, description="Total number of messages to transmit")
    rate_msg_per_sec: float = Field(10.0, gt=0.0, description="Message dispatch rate in msgs/sec")
    concurrency: int = Field(1, ge=1, le=64, description="Number of concurrent sender threads")
    burst_mode: bool = Field(False, description="If True, dispatch all messages in immediate burst")


class ExperimentConfig(BaseModel):
    experiment_name: str = Field(..., min_length=3, description="Descriptive experiment identifier")
    group: str = Field(..., description="Experiment Group: A, B, C, D, E, F, G, H, I, J, K, L")
    scenario_id: str = Field(..., description="Unique scenario identifier, e.g., EXP-A01")
    description: str = Field("", description="Detailed research objective and hypothesis")
    baseline: BaselineType = Field(BaselineType.TREATMENT_E_FULL_ASTRA_SEC, description="Architecture baseline under test")
    workload: WorkloadConfig = Field(default_factory=WorkloadConfig)
    impairment: ImpairmentConfig = Field(default_factory=ImpairmentConfig)
    fault: FaultConfig = Field(default_factory=FaultConfig)
    random_seed: int = Field(42, description="Master deterministic random seed")
    warmup_messages: int = Field(2, ge=0, description="Warm-up messages prior to measurement window")
    repetitions: int = Field(1, ge=1, le=100, description="Independent repetition trials")
    timeout_seconds: float = Field(60.0, gt=0.0, description="Maximum execution timeout")
    output_dir: str = Field("research/phase3_experimental_lab/results/raw", description="Destination directory for raw JSONL")

    def compute_config_hash(self) -> str:
        """Computes deterministic SHA-256 hash of the normalized configuration."""
        dumped = json.dumps(self.model_dump(mode="json"), sort_keys=True)
        return hashlib.sha256(dumped.encode("utf-8")).hexdigest()

    @classmethod
    def load_from_file(cls, filepath: str) -> "ExperimentConfig":
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)

    def save_to_file(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.model_dump(mode="json"), f, indent=2)
