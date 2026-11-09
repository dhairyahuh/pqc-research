"""ASTRA-Sec: Ground-Station Verification & Forensic Audit Module (L7)."""

import logging
import time
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from astra_sec.core.exceptions import InvalidAcknowledgmentError
from astra_sec.crypto.base import DsaAdapter
from astra_sec.crypto.factory import CryptoEngineFactory
from astra_sec.schema.envelope import MessageAcknowledgment, PqcMessageEnvelope
from astra_sec.schema.trust import PublicKeyTrustStore, TrustError

logger = logging.getLogger("astra_sec.security.verifier")


class VerificationRecord(BaseModel):
    """Forensic verification entry in the ground-station audit ledger."""

    record_id: str
    original_envelope_id: str
    acknowledging_eid: str
    status: str
    signature_valid: bool
    verified_at_utc: int = Field(default_factory=lambda: int(time.time()))


class GroundStationVerifier:
    """Ground station verification service providing receipt audit and cryptographic correlation."""

    def __init__(
        self,
        node_eid: str,
        trust_store: PublicKeyTrustStore,
        dsa_adapter: Optional[DsaAdapter] = None,
    ):
        self.node_eid = node_eid
        self.trust_store = trust_store
        self.dsa = dsa_adapter or CryptoEngineFactory.get_dsa_adapter()

        # Outstanding sent commands awaiting acknowledgement: envelope_id -> PqcMessageEnvelope
        self._pending_commands: Dict[str, PqcMessageEnvelope] = {}
        # Append-only verification ledger
        self.ledger: List[VerificationRecord] = []

    def record_dispatched_command(self, envelope: PqcMessageEnvelope) -> None:
        """Records an outgoing command to track expected cryptographic acknowledgement."""
        self._pending_commands[envelope.header.envelope_id] = envelope

    def verify_acknowledgment(
        self,
        ack: MessageAcknowledgment,
        expected_envelope: Optional[PqcMessageEnvelope] = None,
    ) -> VerificationRecord:
        """Cryptographically verifies a returned MessageAcknowledgment.

        Enforces:
        1. Envelope ID must match an expected dispatched command.
        2. Acknowledging node must match original command destination.
        3. Recipient in ACK must match this ground station.
        4. ML-DSA-65 signature must verify against acknowledging node's public key.

        Raises:
            InvalidAcknowledgmentError: if any check fails.
        """
        env_id = ack.original_envelope_id
        original = expected_envelope or self._pending_commands.get(env_id)

        if not original:
            raise InvalidAcknowledgmentError(
                f"Uncorrelated acknowledgement: envelope ID '{env_id}' was not dispatched by this node."
            )

        if ack.source_eid != original.header.destination_eid:
            raise InvalidAcknowledgmentError(
                f"ACK originator mismatch: expected '{original.header.destination_eid}', got '{ack.source_eid}'."
            )

        if ack.destination_eid != self.node_eid:
            raise InvalidAcknowledgmentError(
                f"ACK destination mismatch: expected '{self.node_eid}', got '{ack.destination_eid}'."
            )

        try:
            peer_dsa_pk = self.trust_store.get_dsa_public_key(ack.source_eid)
        except TrustError as e:
            raise InvalidAcknowledgmentError(f"Cannot verify ACK signature: {e}") from e

        signable_bytes = ack.to_signable_bytes()
        sig_valid = self.dsa.verify(signable_bytes, ack.signature, peer_dsa_pk)
        if not sig_valid:
            raise InvalidAcknowledgmentError(
                f"Cryptographic signature on ACK '{ack.ack_id}' failed verification."
            )

        # Correlation and verification succeeded: remove from pending
        if env_id in self._pending_commands:
            del self._pending_commands[env_id]

        record = VerificationRecord(
            record_id=ack.ack_id,
            original_envelope_id=env_id,
            acknowledging_eid=ack.source_eid,
            status=ack.status,
            signature_valid=True,
        )
        self.ledger.append(record)
        logger.info(
            "VERIFIED ACK [%s] from %s for envelope %s (Status: %s)",
            ack.ack_id[:8],
            ack.source_eid,
            env_id[:8],
            ack.status,
        )
        return record
