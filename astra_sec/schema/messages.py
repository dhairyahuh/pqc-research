"""ASTRA-Sec Validated Message Schema Foundations."""

import time
import uuid
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from astra_sec.schema.validators import validate_dtn_eid


class ApplicationDataUnit(BaseModel):
    """L1 Application Data Unit (ADU) originating from ground control or onboard payload."""

    adu_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_eid: str = Field(default="dtn://gsa/app", description="Originating node URI")
    destination_eid: str = Field(default="dtn://gsb/app", description="Target destination URI")
    timestamp_utc: float = Field(default_factory=time.time, description="Creation UTC epoch timestamp")
    command_code: int = Field(default=0x0001, ge=0, le=0xFFFF, description="Mission command / telemetry opcode")
    payload_bytes: bytes = Field(default=b"", description="Raw application payload data")
    priority: int = Field(default=1, ge=0, le=3, description="DTN bundle delivery priority: 0=Bulk, 1=Normal, 2=Expedited")

    @field_validator("source_eid", "destination_eid")
    @classmethod
    def check_eid(cls, v: str) -> str:
        return validate_dtn_eid(v)


class CryptoEnvelopeHeader(BaseModel):
    """L2 Authenticated Header covering the cryptographic envelope (AAD)."""

    magic: str = Field(default="ASTR", max_length=4)
    version: int = Field(default=1, ge=1, le=65535)
    sequence_id: int = Field(default=1, ge=1, description="Strictly monotonic bundle counter")
    ratchet_step: int = Field(default=0, ge=0, description="Post-Quantum Double Ratchet epoch index")
    timestamp_utc: int = Field(default_factory=lambda: int(time.time()))
    ttl_seconds: int = Field(default=86400, ge=60, description="Time-To-Live in seconds")
    source_eid: str = Field(default="dtn://gsa/app")
    destination_eid: str = Field(default="dtn://gsb/app")

    @field_validator("source_eid", "destination_eid")
    @classmethod
    def check_eid(cls, v: str) -> str:
        return validate_dtn_eid(v)

    def to_aad_bytes(self) -> bytes:
        """Serializes the envelope header into canonical bytes for AES-256-GCM AAD binding."""
        src_padded = self.source_eid.encode("utf-8").ljust(64, b"\x00")[:64]
        dst_padded = self.destination_eid.encode("utf-8").ljust(64, b"\x00")[:64]
        return (
            self.magic.encode("ascii")
            + self.version.to_bytes(2, "big")
            + self.sequence_id.to_bytes(8, "big")
            + self.ratchet_step.to_bytes(8, "big")
            + self.timestamp_utc.to_bytes(8, "big")
            + self.ttl_seconds.to_bytes(4, "big")
            + src_padded
            + dst_padded
        )


class FdirTelemetryReport(BaseModel):
    """L7 Spacecraft Fault Detection, Isolation, and Recovery (FDIR) telemetry status report."""

    node_eid: str = Field(default="dtn://sat1/relay")
    uptime_seconds: float = Field(default=0.0, ge=0.0)
    transient_recoveries: int = Field(default=0, ge=0, description="NTT butterflies recovered locally via snapshot")
    persistent_fail_stops: int = Field(default=0, ge=0, description="Persistent faults escalated to implicit rejection")
    twiddle_faults_detected: int = Field(default=0, ge=0, description="Twiddle table mutations caught via TFIB-Ref")
    sdc_prevention_engaged: bool = Field(default=True, description="Whether fail-stop suppression is active")
    bundles_forwarded: int = Field(default=0, ge=0)
    bundles_rejected: int = Field(default=0, ge=0)

    @field_validator("node_eid")
    @classmethod
    def check_eid(cls, v: str) -> str:
        return validate_dtn_eid(v)


class BundleVerificationResult(BaseModel):
    """L2/L7 Verification output generated upon bundle ingestion."""

    bundle_id: str
    is_valid: bool
    sender_verified: bool = False
    payload_decrypted: bool = False
    fault_recovered: bool = False
    error_message: Optional[str] = None
