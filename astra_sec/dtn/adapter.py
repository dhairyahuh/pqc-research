"""ASTRA-Sec: DTN Transport Adapter & BPv7 Store-Carry-Forward Router."""

import logging
import os
import sqlite3
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from astra_sec.core.exceptions import AstraError
from astra_sec.dtn.bpsec import BpSecError, BpSecSecurityContext
from astra_sec.dtn.bpv7 import (
    BLOCK_TYPE_BIB,
    BpV7Bundle,
    PrimaryBlock,
    unix_to_dtn_epoch,
)
from astra_sec.dtn.contact_plan import IonContactPlan
from astra_sec.schema.envelope import PqcMessageEnvelope
from astra_sec.schema.network import DeliveryStatus, ForwardingEvent

logger = logging.getLogger("astra_sec.dtn.adapter")


class DtnProtocolError(AstraError):
    """Raised when DTN bundle processing fails."""


class BpV7ExpiredError(DtnProtocolError):
    """Raised when an ingested BPv7 bundle has exceeded its lifetime."""


class BpSecVerificationError(DtnProtocolError):
    """Raised when RFC 9172 BPSec verification fails."""


class AstraDtnBridge:
    """Bridges ASTRA-Sec L2 End-to-End Envelopes with RFC 9171 / RFC 9172 DTN Bundles.

    Architectural Invariant:
    Application-level end-to-end encryption (ML-KEM-768 + AES-256-GCM + ML-DSA-65) is preserved
    within the opaque BPv7 Payload Block.
    BPSec operates optionally at L5 without altering the application payload.
    """

    @staticmethod
    def envelope_to_bundle(
        envelope: PqcMessageEnvelope,
        lifetime_seconds: int = 3600,
        bib_key: Optional[bytes] = None,
        sequence_number: int = 1,
    ) -> BpV7Bundle:
        """Encapsulates an ASTRA-Sec cryptographic envelope into an RFC 9171 BPv7 bundle."""
        header = envelope.header
        primary = PrimaryBlock(
            destination_eid=header.destination_eid,
            source_eid=header.source_eid,
            report_to_eid="dtn:none",
            creation_time_dtn=unix_to_dtn_epoch(header.timestamp_utc),
            sequence_number=sequence_number,
            lifetime_ms=lifetime_seconds * 1000,
        )

        payload_bytes = envelope.to_binary()
        extension_blocks = []

        # Optional RFC 9172 BPSec Block Integrity Block (BIB)
        if bib_key is not None:
            bib = BpSecSecurityContext.create_bib(
                target_block_number=1,
                target_data=payload_bytes,
                shared_key=bib_key,
            )
            extension_blocks.append(bib)

        return BpV7Bundle(
            primary_block=primary,
            payload_data=payload_bytes,
            extension_blocks=extension_blocks,
        )

    @staticmethod
    def bundle_to_envelope(
        bundle: BpV7Bundle,
        bib_key: Optional[bytes] = None,
        current_time_unix: Optional[int] = None,
    ) -> PqcMessageEnvelope:
        """Extracts and verifies an ASTRA-Sec envelope from an RFC 9171 BPv7 bundle."""
        # 1. Check bundle lifetime expiration
        if bundle.is_expired(current_time_unix):
            raise BpV7ExpiredError(
                f"BPv7 bundle '{bundle.bundle_id}' lifetime expired."
            )

        # 2. Check BPSec BIB if key provided or BIB block present
        bib_blocks = [b for b in bundle.extension_blocks if b.block_type_code == BLOCK_TYPE_BIB]
        if bib_blocks and bib_key is not None:
            try:
                BpSecSecurityContext.verify_bib(bib_blocks[0], bundle.get_payload(), bib_key)
            except BpSecError as e:
                raise BpSecVerificationError(f"BPSec integrity verification failed: {e}") from e
        elif bib_blocks and bib_key is None:
            raise BpSecVerificationError("Bundle contains BPSec BIB but no verification key provided.")

        # 3. Parse L2 envelope from binary payload
        try:
            envelope = PqcMessageEnvelope.from_binary(bundle.get_payload())
            return envelope
        except Exception as e:
            raise DtnProtocolError(f"Failed to unwrap ASTRA-Sec envelope from payload: {e}") from e


class DtnSpoolRouter:
    """Store-carry-forward router managing BPv7 bundles with non-volatile persistence and contact plans."""

    def __init__(
        self,
        node_eid: str,
        node_number: int,
        spool_db_path: str,
        contact_plan: Optional[IonContactPlan] = None,
        forwarder_fn: Optional[Callable[[str, BpV7Bundle], bool]] = None,
        bib_key: Optional[bytes] = None,
    ):
        self.node_eid = node_eid
        self.node_number = node_number
        self.spool_db_path = spool_db_path
        self.contact_plan = contact_plan or IonContactPlan()
        self.forwarder_fn = forwarder_fn
        self.bib_key = bib_key

        self._seen_bundle_ids: Set[str] = set()
        self.events: List[ForwardingEvent] = []
        self._lock = threading.Lock()

        os.makedirs(os.path.dirname(os.path.abspath(spool_db_path)), exist_ok=True)
        self._init_spool_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.spool_db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_spool_db(self) -> None:
        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS dtn_bundle_spool (
                        bundle_id TEXT PRIMARY KEY,
                        source_eid TEXT NOT NULL,
                        destination_eid TEXT NOT NULL,
                        next_hop_node INT NOT NULL,
                        status TEXT NOT NULL,
                        bundle_cbor BLOB NOT NULL,
                        created_at_utc INTEGER NOT NULL,
                        updated_at_utc INTEGER NOT NULL,
                        attempts INTEGER NOT NULL DEFAULT 0
                    )
                    """
                )

    def log_event(
        self,
        event_type: str,
        bundle_id: str,
        source_eid: str,
        destination_eid: str,
        next_hop_eid: Optional[str],
        status: DeliveryStatus,
        details: Optional[Dict[str, Any]] = None,
    ) -> ForwardingEvent:
        event = ForwardingEvent(
            node_eid=self.node_eid,
            event_type=event_type,
            envelope_id=bundle_id.replace("::", "_"),
            source_eid=source_eid,
            destination_eid=destination_eid,
            next_hop_eid=next_hop_eid,
            status=status,
            details=details or {},
        )
        self.events.append(event)
        return event

    def ingest_bundle(
        self,
        bundle: BpV7Bundle,
        next_hop_eid: str,
        next_hop_node: int,
        current_time_unix: Optional[int] = None,
    ) -> ForwardingEvent:
        """Ingests a BPv7 bundle, evaluates duplicates/expiry, spools, and forwards if contact open."""
        now = current_time_unix if current_time_unix is not None else int(time.time())
        b_id = bundle.bundle_id

        # 1. Duplicate check
        if b_id in self._seen_bundle_ids:
            return self.log_event(
                event_type="REJECT_DUPLICATE_BUNDLE",
                bundle_id=b_id,
                source_eid=bundle.primary.source_eid,
                destination_eid=bundle.primary.destination_eid,
                next_hop_eid=next_hop_eid,
                status=DeliveryStatus.DROPPED_DUPLICATE,
            )
        self._seen_bundle_ids.add(b_id)

        # 2. Lifetime expiration check
        if bundle.is_expired(now):
            return self.log_event(
                event_type="REJECT_EXPIRED_BUNDLE",
                bundle_id=b_id,
                source_eid=bundle.primary.source_eid,
                destination_eid=bundle.primary.destination_eid,
                next_hop_eid=next_hop_eid,
                status=DeliveryStatus.EXPIRED,
            )

        # 3. Persistent Spooling
        bundle_bytes = bundle.to_cbor_bytes()
        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO dtn_bundle_spool (
                        bundle_id, source_eid, destination_eid, next_hop_node,
                        status, bundle_cbor, created_at_utc, updated_at_utc, attempts
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(bundle_id) DO UPDATE SET
                        status = excluded.status,
                        updated_at_utc = excluded.updated_at_utc
                    """,
                    (
                        b_id,
                        bundle.primary.source_eid,
                        bundle.primary.destination_eid,
                        next_hop_node,
                        DeliveryStatus.QUEUED.value,
                        bundle_bytes,
                        now,
                        now,
                        0,
                    ),
                )

        # 4. Check contact availability
        if not self.contact_plan.is_contact_open(self.node_number, next_hop_node, now):
            self._update_status(b_id, DeliveryStatus.WAITING_CONTACT)
            return self.log_event(
                event_type="BUNDLE_SPOOLED_WAITING_CONTACT",
                bundle_id=b_id,
                source_eid=bundle.primary.source_eid,
                destination_eid=bundle.primary.destination_eid,
                next_hop_eid=next_hop_eid,
                status=DeliveryStatus.WAITING_CONTACT,
            )

        # 5. Immediate forwarding attempt
        forward_ok = False
        if self.forwarder_fn:
            try:
                forward_ok = self.forwarder_fn(next_hop_eid, bundle)
            except Exception as e:
                logger.warning("Bundle forward to %s failed: %s", next_hop_eid, e)
                forward_ok = False
        else:
            forward_ok = True

        if forward_ok:
            self._update_status(b_id, DeliveryStatus.FORWARDED, increment_attempts=True)
            return self.log_event(
                event_type="BUNDLE_FORWARDED",
                bundle_id=b_id,
                source_eid=bundle.primary.source_eid,
                destination_eid=bundle.primary.destination_eid,
                next_hop_eid=next_hop_eid,
                status=DeliveryStatus.FORWARDED,
            )
        else:
            self._update_status(b_id, DeliveryStatus.WAITING_CONTACT)
            return self.log_event(
                event_type="BUNDLE_FORWARD_DEFERRED",
                bundle_id=b_id,
                source_eid=bundle.primary.source_eid,
                destination_eid=bundle.primary.destination_eid,
                next_hop_eid=next_hop_eid,
                status=DeliveryStatus.WAITING_CONTACT,
            )

    def process_spool(self, current_time_unix: Optional[int] = None) -> List[ForwardingEvent]:
        """Flushes spooled bundles when contact windows open."""
        now = current_time_unix if current_time_unix is not None else int(time.time())
        flushed: List[ForwardingEvent] = []

        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM dtn_bundle_spool WHERE status IN (?, ?)",
                    (DeliveryStatus.QUEUED.value, DeliveryStatus.WAITING_CONTACT.value),
                )
                rows = cursor.fetchall()

        for row in rows:
            bundle = BpV7Bundle.from_cbor_bytes(row["bundle_cbor"])
            b_id = row["bundle_id"]
            next_node = row["next_hop_node"]

            # Expiration in spool
            if bundle.is_expired(now):
                self._update_status(b_id, DeliveryStatus.EXPIRED)
                flushed.append(
                    self.log_event(
                        event_type="SPOOL_BUNDLE_EXPIRED",
                        bundle_id=b_id,
                        source_eid=bundle.primary.source_eid,
                        destination_eid=bundle.primary.destination_eid,
                        next_hop_eid=None,
                        status=DeliveryStatus.EXPIRED,
                    )
                )
                continue

            # Contact open
            if self.contact_plan.is_contact_open(self.node_number, next_node, now):
                forward_ok = False
                if self.forwarder_fn:
                    try:
                        forward_ok = self.forwarder_fn(bundle.primary.destination_eid, bundle)
                    except Exception as e:
                        logger.warning("Spool flush failed: %s", e)
                        forward_ok = False
                else:
                    forward_ok = True

                if forward_ok:
                    self._update_status(b_id, DeliveryStatus.FORWARDED, increment_attempts=True)
                    flushed.append(
                        self.log_event(
                            event_type="SPOOL_BUNDLE_FORWARDED",
                            bundle_id=b_id,
                            source_eid=bundle.primary.source_eid,
                            destination_eid=bundle.primary.destination_eid,
                            next_hop_eid=bundle.primary.destination_eid,
                            status=DeliveryStatus.FORWARDED,
                        )
                    )

        return flushed

    def _update_status(self, bundle_id: str, status: DeliveryStatus, increment_attempts: bool = False):
        now = int(time.time())
        attempts_expr = "attempts + 1" if increment_attempts else "attempts"
        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    f"UPDATE dtn_bundle_spool SET status = ?, updated_at_utc = ?, attempts = {attempts_expr} WHERE bundle_id = ?",
                    (status.value, now, bundle_id),
                )

    def count_pending(self) -> int:
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) as cnt FROM dtn_bundle_spool WHERE status IN (?, ?)",
                    (DeliveryStatus.QUEUED.value, DeliveryStatus.WAITING_CONTACT.value),
                )
                return cursor.fetchone()["cnt"]
