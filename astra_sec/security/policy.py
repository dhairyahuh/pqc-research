"""ASTRA-Sec: Authorization Policy & Access Control Engine."""

from enum import Enum
import logging
import time
from typing import Dict, List, Optional, Set

from pydantic import BaseModel, Field

from astra_sec.core.exceptions import IdentityRevokedError, StaleMessageError
from astra_sec.schema.validators import validate_dtn_eid

logger = logging.getLogger("astra_sec.security.policy")


class AuthorizationStatus(str, Enum):
    AUTHORIZED = "AUTHORIZED"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"
    UNKNOWN = "UNKNOWN"


class NodeAuthorizationRecord(BaseModel):
    """Access control entry for a network node."""

    eid: str
    role: str = "ground_station"
    status: AuthorizationStatus = AuthorizationStatus.AUTHORIZED
    allowed_operations: List[str] = Field(default_factory=lambda: ["SEND", "RECEIVE", "FORWARD"])
    revocation_reason: Optional[str] = None
    updated_at_utc: int = Field(default_factory=lambda: int(time.time()))


class AuthorizationPolicy:
    """Evaluates access control rules, revocations, and operational validity."""

    def __init__(self, max_command_ttl_seconds: int = 7200):
        self.max_command_ttl_seconds = max_command_ttl_seconds
        self._records: Dict[str, NodeAuthorizationRecord] = {}
        self._revoked_eids: Set[str] = set()

    def set_authorization(
        self,
        eid: str,
        role: str,
        status: AuthorizationStatus = AuthorizationStatus.AUTHORIZED,
        allowed_operations: Optional[List[str]] = None,
    ) -> NodeAuthorizationRecord:
        """Sets authorization status for an EID."""
        valid_eid = validate_dtn_eid(eid)
        now = int(time.time())
        record = NodeAuthorizationRecord(
            eid=valid_eid,
            role=role,
            status=status,
            allowed_operations=allowed_operations or ["SEND", "RECEIVE", "FORWARD"],
            updated_at_utc=now,
        )
        self._records[valid_eid] = record
        if status == AuthorizationStatus.REVOKED:
            self._revoked_eids.add(valid_eid)
        elif valid_eid in self._revoked_eids and status == AuthorizationStatus.AUTHORIZED:
            self._revoked_eids.remove(valid_eid)
        return record

    def revoke_identity(self, eid: str, reason: str = "Policy revocation") -> None:
        """Explicitly and permanently revokes authorization for a node."""
        valid_eid = validate_dtn_eid(eid)
        now = int(time.time())
        if valid_eid in self._records:
            rec = self._records[valid_eid]
            rec.status = AuthorizationStatus.REVOKED
            rec.revocation_reason = reason
            rec.updated_at_utc = now
        else:
            self._records[valid_eid] = NodeAuthorizationRecord(
                eid=valid_eid,
                status=AuthorizationStatus.REVOKED,
                revocation_reason=reason,
                updated_at_utc=now,
            )
        self._revoked_eids.add(valid_eid)
        logger.warning("POLICY: Revoked authorization for '%s': %s", valid_eid, reason)

    def is_authorized(self, eid: str, operation: str = "SEND") -> bool:
        """Determines if an EID is authorized for a given operation."""
        if eid in self._revoked_eids:
            return False
        rec = self._records.get(eid)
        if not rec:
            return False
        if rec.status != AuthorizationStatus.AUTHORIZED:
            return False
        return operation in rec.allowed_operations

    def validate_sender(self, sender_eid: str) -> None:
        """Validates that a sender is authorized. Raises IdentityRevokedError if not."""
        if sender_eid in self._revoked_eids:
            raise IdentityRevokedError(f"Sender '{sender_eid}' has been REVOKED.")
        if not self.is_authorized(sender_eid, "SEND"):
            raise IdentityRevokedError(f"Sender '{sender_eid}' is not authorized to transmit.")

    def validate_command_freshness(
        self,
        timestamp_utc: int,
        ttl_seconds: int,
        current_time_utc: Optional[int] = None,
    ) -> None:
        """Validates message freshness against expiration policy.

        Delayed messages are NOT automatically invalid:
        A message is valid if: current_time <= timestamp + ttl AND ttl <= max_command_ttl.
        """
        now = current_time_utc if current_time_utc is not None else int(time.time())
        effective_ttl = min(ttl_seconds, self.max_command_ttl_seconds)

        if now > (timestamp_utc + effective_ttl):
            raise StaleMessageError(
                f"Command expired: created at {timestamp_utc}, TTL={effective_ttl}s, current={now} "
                f"(expired by {now - (timestamp_utc + effective_ttl)}s)"
            )
