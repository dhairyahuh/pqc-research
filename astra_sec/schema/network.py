"""ASTRA-Sec: Multi-Node Satellite Network and Relay Schemas."""

from enum import Enum
import time
import uuid
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator

from astra_sec.schema.envelope import PqcMessageEnvelope
from astra_sec.schema.validators import validate_dtn_eid


class DeliveryStatus(str, Enum):
    """Lifecycle delivery states for space network message envelopes."""

    QUEUED = "QUEUED"
    IN_FLIGHT = "IN_FLIGHT"
    FORWARDED = "FORWARDED"
    DELIVERED = "DELIVERED"
    WAITING_CONTACT = "WAITING_CONTACT"
    EXPIRED = "EXPIRED"
    DROPPED_DUPLICATE = "DROPPED_DUPLICATE"
    DROPPED_UNAUTHORIZED = "DROPPED_UNAUTHORIZED"
    DROPPED_TAMPERED = "DROPPED_TAMPERED"


class LinkState(str, Enum):
    """Orbital link physical connection state."""

    UP = "UP"
    DOWN = "DOWN"
    OCCULTED = "OCCULTED"


class ContactWindow(BaseModel):
    """Scheduled orbital line-of-sight contact window between two nodes."""

    source_eid: str = Field(..., description="Local node RFC 9171 EID")
    peer_eid: str = Field(..., description="Target node RFC 9171 EID")
    start_time_utc: int = Field(..., description="Contact window start timestamp")
    end_time_utc: int = Field(..., description="Contact window end timestamp")
    is_active: bool = Field(default=True, description="Whether contact link is physically operational")

    @field_validator("source_eid", "peer_eid")
    @classmethod
    def check_eid(cls, v: str) -> str:
        return validate_dtn_eid(v)

    def is_in_contact(self, timestamp: Optional[int] = None) -> bool:
        """Determines if the contact window is valid at the given timestamp."""
        if not self.is_active:
            return False
        now = timestamp if timestamp is not None else int(time.time())
        return self.start_time_utc <= now <= self.end_time_utc


class ForwardingEvent(BaseModel):
    """Structured audit log entry for multi-hop store-carry-forward events."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_utc: int = Field(default_factory=lambda: int(time.time()))
    node_eid: str = Field(..., description="Relay or endpoint node recording event")
    event_type: str = Field(..., description="Event action descriptor")
    envelope_id: str = Field(..., description="Message envelope UUID")
    source_eid: str = Field(..., description="Original sender EID")
    destination_eid: str = Field(..., description="Final destination EID")
    next_hop_eid: Optional[str] = Field(default=None, description="Next hop relay/endpoint EID")
    status: DeliveryStatus = Field(..., description="Current bundle delivery status")
    details: Dict[str, Any] = Field(default_factory=dict, description="Metadata and reason codes")

    @field_validator("node_eid", "source_eid", "destination_eid")
    @classmethod
    def check_eid(cls, v: str) -> str:
        return validate_dtn_eid(v)

    @field_validator("next_hop_eid")
    @classmethod
    def check_optional_eid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return validate_dtn_eid(v)
        return v


class SpoolItem(BaseModel):
    """Model for non-volatile persistently spooled envelopes."""

    envelope_id: str = Field(...)
    source_eid: str = Field(...)
    destination_eid: str = Field(...)
    next_hop_eid: str = Field(...)
    status: DeliveryStatus = Field(default=DeliveryStatus.QUEUED)
    envelope: PqcMessageEnvelope = Field(...)
    created_at_utc: int = Field(default_factory=lambda: int(time.time()))
    attempts: int = Field(default=0)
