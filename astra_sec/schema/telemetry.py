"""ASTRA-Sec: Telemetry Event and Real-Time Measurement Schemas."""

from enum import Enum
import time
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator
from astra_sec.schema.validators import validate_dtn_eid


class EventType(str, Enum):
    """Categorized telemetry event classification."""

    CRYPTO_OPERATION = "CRYPTO_OPERATION"
    DTN_STORE_FORWARD = "DTN_STORE_FORWARD"
    FAULT_INSPECTION = "FAULT_INSPECTION"
    NETWORK_LINK = "NETWORK_LINK"
    SYSTEM_HEALTH = "SYSTEM_HEALTH"
    SECURITY_AUDIT = "SECURITY_AUDIT"


class ComponentLayer(str, Enum):
    """7-Layer architectural component classification."""

    L1_APPLICATION = "L1_APPLICATION"
    L2_AEAD = "L2_AEAD"
    L3_KEM = "L3_KEM"
    L3_DSA = "L3_DSA"
    L4_NTT = "L4_NTT"
    L5_BPV7 = "L5_BPV7"
    L6_SPOOL = "L6_SPOOL"
    L7_FDIR = "L7_FDIR"


class TelemetryEvent(BaseModel):
    """Unified telemetry event record with strict correlation and timing bounds."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Globally unique event UUID")
    event_type: EventType = Field(..., description="High-level event category")
    timestamp_utc: str = Field(..., description="ISO 8601 UTC timestamp")
    monotonic_timestamp_ns: int = Field(default_factory=time.perf_counter_ns, description="Monotonic nanosecond timestamp")
    component: ComponentLayer = Field(..., description="Producing architectural component layer")
    source_node: str = Field(..., description="Producing node RFC 9171 EID")
    destination_node: Optional[str] = Field(default=None, description="Target peer RFC 9171 EID if applicable")
    message_id: Optional[str] = Field(default=None, description="Unique Application Data Unit (ADU) identifier")
    bundle_id: Optional[str] = Field(default=None, description="RFC 9171 BPv7 bundle identifier")
    experiment_id: Optional[str] = Field(default=None, description="Associated empirical trial or campaign ID")
    operation: str = Field(..., description="Exact operational action executed")
    status: str = Field(..., description="Execution outcome (SUCCESS, FAILED, RECOVERED, REJECTED, SUPPRESSED, PENDING)")
    duration_ns: Optional[int] = Field(default=None, description="Measured duration in nanoseconds")
    correlation_id: str = Field(..., description="Correlation ID tying complete message lifecycle together")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Structured non-sensitive operational metadata")

    @field_validator("source_node")
    @classmethod
    def validate_source(cls, v: str) -> str:
        return validate_dtn_eid(v)


class CryptographicMeasurement(BaseModel):
    """Fine-grained cryptographic operation measurement."""

    algorithm: str = Field(..., description="Cryptographic primitive (e.g. ML-KEM-768, ML-DSA-65, AES-256-GCM)")
    operation: str = Field(..., description="Action: KEYGEN, ENCAPSULATE, DECAPSULATE, SIGN, VERIFY, DERIVE, ENCRYPT, DECRYPT")
    duration_ns: int = Field(..., description="Wall-clock execution latency in nanoseconds")
    input_bytes_len: int = Field(..., description="Byte length of input data")
    output_bytes_len: int = Field(..., description="Byte length of generated cryptographic artifact")
    status: str = Field(..., description="Operation status (SUCCESS, FAILED, REJECTED)")
    verified: Optional[bool] = Field(default=None, description="Independent verification status for signatures / tags")


class NttInvariantMeasurement(BaseModel):
    """Monitored ML-KEM execution telemetry directly from libastra_crypto C bridge."""

    monitored_algorithm: str = Field(default="ML-KEM-768 Decapsulation (C-Native)")
    invariant_formula: str = Field(default="r ≡ t · ζ (mod 3329)")
    modulus_q: int = Field(default=3329)
    butterflies_executed: int = Field(..., description="Total butterflies monitored (9856 per full decapsulation)")
    layer_width: int = Field(default=128, description="Butterflies per single NTT layer (N/2 = 128)")
    transforms_monitored: int = Field(default=11, description="Polynomial transforms (6 Forward CT + 5 Inverse GS)")
    reference_checker: str = Field(default="ACTIVE (TFIB-Ref Dual-Table)")
    operand_snapshot_buffer: str = Field(default="ARMED (K <= 2)")
    invariant_status: str = Field(..., description="NOMINAL_VERIFIED, ANOMALY_RECOVERED, or VIOLATION_FAIL_STOP")
    fault_type_injected: str = Field(default="NONE")
    fault_layer: Optional[int] = None
    fault_butterfly: Optional[int] = None
    mismatch_count: int = Field(default=0)
    retry_count: int = Field(default=0)
    recovered_count: int = Field(default=0)
    persistent_count: int = Field(default=0)
    twiddle_faults_detected: int = Field(default=0)
    fail_stop_engaged: bool = Field(default=False)
    fail_stop_action: str = Field(default="NONE")


class DtnQueueMeasurement(BaseModel):
    """Physical database and queue storage measurement for a relay node."""

    relay_eid: str = Field(..., description="Satellite relay node EID")
    pending_bundles: int = Field(..., description="Number of bundles awaiting transmission in WAL")
    persisted_bundles: int = Field(..., description="Total cumulative bundles stored in database")
    queue_capacity: int = Field(default=1000, description="Configured spool capacity")
    database_bytes: int = Field(..., description="Primary SQLite .db file size on disk")
    wal_bytes: int = Field(..., description="Active SQLite .db-wal write-ahead-log size on disk")
    wal_mode: bool = Field(default=True, description="True if PRAGMA journal_mode=WAL is confirmed")
    last_inserted_utc: Optional[str] = None
    last_forwarded_utc: Optional[str] = None
    replay_rejections: int = Field(default=0, description="Total replay attempts suppressed by this node")


class HopNetworkMeasurement(BaseModel):
    """Physical and link layer transmission measurement between two adjacent nodes."""

    hop_id: str = Field(..., description="Unique hop identifier (e.g. HOP_1_UPLINK, HOP_2_ISL, HOP_3_DOWNLINK)")
    source_eid: str = Field(..., description="Transmitting node EID")
    target_eid: str = Field(..., description="Receiving node EID")
    link_state: str = Field(..., description="UP or DOWN")
    total_transmissions: int = Field(default=0)
    failed_transmissions: int = Field(default=0)
    last_duration_ms: float = Field(default=0.0)
    outage_active: bool = Field(default=False)
    is_simulated_impairment: bool = Field(default=False, description="True if delay or outage is simulated")


class SystemHealthReport(BaseModel):
    """Comprehensive composite system and security health report."""

    overall_status: str = Field(..., description="HEALTHY, DEGRADED, FAIL_STOP_ENGAGED, or CORRUPTED")
    process_health: str = Field(default="ONLINE")
    crypto_subsystem: str = Field(default="HEALTHY")
    dtn_subsystem: str = Field(default="OPERATIONAL")
    link_health: str = Field(default="OPTIMAL")
    last_message_status: str = Field(default="NONE")
    fips_conformance_status: str = Field(default="KAT_VERIFIED")
    active_envelope_authenticated: bool = Field(default=True)
    active_envelope_id: Optional[str] = None
    timestamp_utc: str = Field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

