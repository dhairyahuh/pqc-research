"""ASTRA-Sec: Cryptographic Key Lifecycle Management (NIST SP 800-57 & CCSDS SDLS-EP Alignment)."""

from enum import Enum
import logging
import time
import uuid
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from astra_sec.core.exceptions import KeyLifecycleError

logger = logging.getLogger("astra_sec.security.lifecycle")


class KeyLifecycleState(str, Enum):
    """NIST SP 800-57 Part 1 Key States."""

    GENERATED = "GENERATED"
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"
    REVOKED = "REVOKED"
    COMPROMISED = "COMPROMISED"


class KeyRecord(BaseModel):
    """Metadata record for a cryptographic key tracking operational lifecycle."""

    key_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    algorithm: str
    public_key: bytes
    state: KeyLifecycleState = KeyLifecycleState.ACTIVE
    version: int = 1
    created_at_utc: int = Field(default_factory=lambda: int(time.time()))
    activated_at_utc: Optional[int] = None
    retired_at_utc: Optional[int] = None
    revoked_at_utc: Optional[int] = None

    def can_encrypt_or_sign(self) -> bool:
        """Only ACTIVE keys can originate new cryptographic operations."""
        return self.state == KeyLifecycleState.ACTIVE

    def can_decrypt_or_verify(self, grace_period_seconds: int = 86400) -> bool:
        """ACTIVE keys and recently RETIRED keys (for delayed in-flight messages) can verify/decrypt."""
        if self.state == KeyLifecycleState.ACTIVE:
            return True
        if self.state == KeyLifecycleState.RETIRED:
            if self.retired_at_utc is not None:
                now = int(time.time())
                return (now - self.retired_at_utc) <= grace_period_seconds
            return True
        return False


class KeyLifecycleManager:
    """Manages key generation, rotation, retirement, and revocation."""

    def __init__(self, node_eid: str):
        self.node_eid = node_eid
        self._keys: Dict[str, KeyRecord] = {}  # key_id -> KeyRecord
        self._active_key_id: Optional[str] = None

    def register_key(self, algorithm: str, public_key: bytes, make_active: bool = True) -> KeyRecord:
        """Registers a new cryptographic key."""
        now = int(time.time())
        record = KeyRecord(
            algorithm=algorithm,
            public_key=public_key,
            state=KeyLifecycleState.ACTIVE if make_active else KeyLifecycleState.GENERATED,
            activated_at_utc=now if make_active else None,
            version=len(self._keys) + 1,
        )
        self._keys[record.key_id] = record
        if make_active:
            if self._active_key_id and self._active_key_id in self._keys:
                # Transition previous active key to RETIRED
                old = self._keys[self._active_key_id]
                old.state = KeyLifecycleState.RETIRED
                old.retired_at_utc = now
            self._active_key_id = record.key_id
            logger.info("Node %s activated key %s (v%d)", self.node_eid, record.key_id, record.version)
        return record

    def rotate_key(self, algorithm: str, new_public_key: bytes) -> Tuple[KeyRecord, Optional[KeyRecord]]:
        """Rotates current active key to RETIRED and activates new key.

        Returns (new_active_key, retired_key).
        """
        now = int(time.time())
        old_record = None
        if self._active_key_id and self._active_key_id in self._keys:
            old_record = self._keys[self._active_key_id]
            old_record.state = KeyLifecycleState.RETIRED
            old_record.retired_at_utc = now
            logger.info("Node %s retired key %s", self.node_eid, old_record.key_id)

        new_record = KeyRecord(
            algorithm=algorithm,
            public_key=new_public_key,
            state=KeyLifecycleState.ACTIVE,
            activated_at_utc=now,
            version=(old_record.version + 1) if old_record else 1,
        )
        self._keys[new_record.key_id] = new_record
        self._active_key_id = new_record.key_id
        logger.info("Node %s rotated to active key %s (v%d)", self.node_eid, new_record.key_id, new_record.version)
        return new_record, old_record

    def revoke_key(self, key_id: str) -> KeyRecord:
        """Immediately revokes a key due to compromise or policy termination."""
        if key_id not in self._keys:
            raise KeyLifecycleError(f"Key ID '{key_id}' not found.")
        rec = self._keys[key_id]
        rec.state = KeyLifecycleState.REVOKED
        rec.revoked_at_utc = int(time.time())
        if self._active_key_id == key_id:
            self._active_key_id = None
        logger.warning("Node %s REVOKED key %s", self.node_eid, key_id)
        return rec

    def get_active_key(self) -> Optional[KeyRecord]:
        if self._active_key_id:
            return self._keys.get(self._active_key_id)
        return None

    def get_key(self, key_id: str) -> Optional[KeyRecord]:
        return self._keys.get(key_id)
