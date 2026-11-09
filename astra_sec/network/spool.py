"""ASTRA-Sec: Non-Volatile Persistent Message Spool (L6 Disruption Recovery)."""

import logging
import os
import sqlite3
import threading
import time
from typing import List, Optional

from astra_sec.schema.envelope import PqcMessageEnvelope
from astra_sec.schema.network import DeliveryStatus, SpoolItem

logger = logging.getLogger("astra_sec.network.spool")


class PersistentMessageSpool:
    """ACID-compliant SQLite-backed persistent message queue surviving node restarts.

    Implements L6 persistent non-volatile spooling with atomic Write-Ahead Logging (WAL).
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._lock = threading.Lock()

        # Ensure parent directory exists
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS message_spool (
                        envelope_id TEXT PRIMARY KEY,
                        source_eid TEXT NOT NULL,
                        destination_eid TEXT NOT NULL,
                        next_hop_eid TEXT NOT NULL,
                        status TEXT NOT NULL,
                        envelope_blob BLOB NOT NULL,
                        created_at_utc INTEGER NOT NULL,
                        updated_at_utc INTEGER NOT NULL,
                        attempts INTEGER NOT NULL DEFAULT 0
                    )
                    """
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_spool_status ON message_spool(status)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_spool_next_hop ON message_spool(next_hop_eid, status)"
                )

    def enqueue(
        self,
        envelope: PqcMessageEnvelope,
        next_hop_eid: str,
        initial_status: DeliveryStatus = DeliveryStatus.QUEUED,
    ) -> SpoolItem:
        """Atomically persists a new envelope to the non-volatile spool."""
        now = int(time.time())
        env_bytes = envelope.to_binary()
        item = SpoolItem(
            envelope_id=envelope.header.envelope_id,
            source_eid=envelope.header.source_eid,
            destination_eid=envelope.header.destination_eid,
            next_hop_eid=next_hop_eid,
            status=initial_status,
            envelope=envelope,
            created_at_utc=now,
            attempts=0,
        )

        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO message_spool (
                        envelope_id, source_eid, destination_eid, next_hop_eid,
                        status, envelope_blob, created_at_utc, updated_at_utc, attempts
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(envelope_id) DO UPDATE SET
                        status = excluded.status,
                        next_hop_eid = excluded.next_hop_eid,
                        updated_at_utc = excluded.updated_at_utc
                    """,
                    (
                        item.envelope_id,
                        item.source_eid,
                        item.destination_eid,
                        item.next_hop_eid,
                        item.status.value,
                        env_bytes,
                        now,
                        now,
                        0,
                    ),
                )
        logger.debug("Spooled envelope %s to %s", item.envelope_id, self.db_path)
        return item

    def get_pending(self, next_hop_eid: Optional[str] = None, limit: int = 100) -> List[SpoolItem]:
        """Retrieves pending (QUEUED or WAITING_CONTACT) envelopes for forwarding."""
        query = (
            "SELECT * FROM message_spool WHERE status IN (?, ?) "
        )
        params: list = [DeliveryStatus.QUEUED.value, DeliveryStatus.WAITING_CONTACT.value]

        if next_hop_eid:
            query += "AND next_hop_eid = ? "
            params.append(next_hop_eid)

        query += "ORDER BY created_at_utc ASC LIMIT ?"
        params.append(limit)

        items: List[SpoolItem] = []
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(query, params)
                for row in cursor.fetchall():
                    envelope = PqcMessageEnvelope.from_binary(row["envelope_blob"])
                    items.append(
                        SpoolItem(
                            envelope_id=row["envelope_id"],
                            source_eid=row["source_eid"],
                            destination_eid=row["destination_eid"],
                            next_hop_eid=row["next_hop_eid"],
                            status=DeliveryStatus(row["status"]),
                            envelope=envelope,
                            created_at_utc=row["created_at_utc"],
                            attempts=row["attempts"],
                        )
                    )
        return items

    def update_status(
        self,
        envelope_id: str,
        status: DeliveryStatus,
        increment_attempts: bool = False,
    ) -> None:
        """Atomically updates envelope delivery state."""
        now = int(time.time())
        attempts_expr = "attempts + 1" if increment_attempts else "attempts"
        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    f"""
                    UPDATE message_spool
                    SET status = ?, updated_at_utc = ?, attempts = {attempts_expr}
                    WHERE envelope_id = ?
                    """,
                    (status.value, now, envelope_id),
                )

    def mark_forwarded(self, envelope_id: str) -> None:
        """Marks spooled item as successfully forwarded to the next hop."""
        self.update_status(envelope_id, DeliveryStatus.FORWARDED, increment_attempts=True)

    def mark_delivered(self, envelope_id: str) -> None:
        """Marks spooled item as delivered to terminating destination."""
        self.update_status(envelope_id, DeliveryStatus.DELIVERED, increment_attempts=True)

    def mark_expired(self, envelope_id: str) -> None:
        """Marks spooled item as expired due to TTL."""
        self.update_status(envelope_id, DeliveryStatus.EXPIRED)

    def count_pending(self) -> int:
        """Counts envelopes awaiting forwarding."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) as cnt FROM message_spool WHERE status IN (?, ?)",
                    (DeliveryStatus.QUEUED.value, DeliveryStatus.WAITING_CONTACT.value),
                )
                return cursor.fetchone()["cnt"]

    def count_total(self) -> int:
        """Counts all spooled envelopes regardless of state."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) as cnt FROM message_spool")
                return cursor.fetchone()["cnt"]

    def get_detailed_stats(self) -> dict:
        """Returns physical and logical storage telemetry for this spool."""
        db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        wal_path = f"{self.db_path}-wal"
        wal_size = os.path.getsize(wal_path) if os.path.exists(wal_path) else 0

        with self._lock:
            with self._get_connection() as conn:
                pending_cnt = conn.execute(
                    "SELECT COUNT(*) as cnt FROM message_spool WHERE status IN (?, ?)",
                    (DeliveryStatus.QUEUED.value, DeliveryStatus.WAITING_CONTACT.value),
                ).fetchone()["cnt"]

                persisted_cnt = conn.execute(
                    "SELECT COUNT(*) as cnt FROM message_spool"
                ).fetchone()["cnt"]

                last_ins = conn.execute(
                    "SELECT MAX(created_at_utc) as ts FROM message_spool"
                ).fetchone()["ts"]

                last_fwd = conn.execute(
                    "SELECT MAX(updated_at_utc) as ts FROM message_spool WHERE status = ?",
                    (DeliveryStatus.FORWARDED.value,),
                ).fetchone()["ts"]

                expired_cnt = conn.execute(
                    "SELECT COUNT(*) as cnt FROM message_spool WHERE status = ?",
                    (DeliveryStatus.EXPIRED.value,),
                ).fetchone()["cnt"]

                row = conn.execute("PRAGMA journal_mode").fetchone()
                journal_mode = row[0].upper() if row else "UNKNOWN"

        return {
            "pending_bundles": pending_cnt,
            "persisted_bundles": persisted_cnt,
            "expired_bundles": expired_cnt,
            "database_bytes": db_size,
            "database_kb": round(db_size / 1024.0, 2),
            "wal_bytes": wal_size,
            "wal_kb": round(wal_size / 1024.0, 2),
            "wal_mode": journal_mode == "WAL",
            "last_insertion_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(last_ins)) if last_ins else None,
            "last_forwarding_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(last_fwd)) if last_fwd else None,
            "last_inserted_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(last_ins)) if last_ins else None,
            "last_forwarded_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(last_fwd)) if last_fwd else None,
        }

    def purge(self) -> None:
        """Clears all records in spool."""
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM message_spool")
