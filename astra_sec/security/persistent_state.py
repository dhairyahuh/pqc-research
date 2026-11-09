"""ASTRA-Sec: Cryptographically Protected Persistent Security State (L6 / L7)."""

import hashlib
import hmac
import logging
import os
import sqlite3
import threading
import time
from typing import Dict, List, Optional, Set, Tuple

from astra_sec.core.exceptions import (
    ReplayDetectedError,
    SecurityStateCorruptionError,
)

logger = logging.getLogger("astra_sec.security.persistent_state")


class PersistentSecurityState:
    """Non-volatile ACID persistent security state with cryptographic integrity protection.

    Enforces:
    1. Replay state persists across node restarts.
    2. Revocations persist across node restarts.
    3. State corruption triggers explicit fail-stop locking; NEVER silently resets to blank slate.
    """

    def __init__(self, db_path: str, integrity_key: bytes):
        self.db_path = os.path.abspath(db_path)
        self.integrity_key = integrity_key
        self._lock = threading.Lock()
        self.is_locked_fail_stop = False

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        self._verify_and_update_integrity()

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
                    CREATE TABLE IF NOT EXISTS seen_sequences (
                        source_eid TEXT NOT NULL,
                        sequence_id INTEGER NOT NULL,
                        envelope_id TEXT NOT NULL,
                        accepted_at_utc INTEGER NOT NULL,
                        PRIMARY KEY (source_eid, sequence_id)
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS revoked_identities (
                        eid TEXT PRIMARY KEY,
                        revoked_at_utc INTEGER NOT NULL,
                        reason TEXT NOT NULL
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS state_manifest (
                        manifest_id INTEGER PRIMARY KEY CHECK (manifest_id = 1),
                        state_hmac BLOB NOT NULL,
                        updated_at_utc INTEGER NOT NULL
                    )
                    """
                )

    def _compute_state_hmac(self, conn: sqlite3.Connection) -> bytes:
        """Computes HMAC-SHA256 over all rows in seen_sequences and revoked_identities."""
        hasher = hmac.new(self.integrity_key, b"ASTRA_STATE_V1", hashlib.sha256)

        cursor = conn.execute(
            "SELECT source_eid, sequence_id, envelope_id FROM seen_sequences ORDER BY source_eid, sequence_id"
        )
        for row in cursor.fetchall():
            entry = f"{row['source_eid']}|{row['sequence_id']}|{row['envelope_id']}".encode("utf-8")
            hasher.update(entry)

        cursor = conn.execute(
            "SELECT eid, revoked_at_utc, reason FROM revoked_identities ORDER BY eid"
        )
        for row in cursor.fetchall():
            entry = f"{row['eid']}|{row['revoked_at_utc']}|{row['reason']}".encode("utf-8")
            hasher.update(entry)

        return hasher.digest()

    def _verify_and_update_integrity(self) -> None:
        """Verifies existing state HMAC on startup. Locks system if corrupted."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT state_hmac FROM state_manifest WHERE manifest_id = 1")
                row = cursor.fetchone()
                computed = self._compute_state_hmac(conn)

                if row is not None:
                    stored_hmac = row["state_hmac"]
                    if not hmac.compare_digest(stored_hmac, computed):
                        self.is_locked_fail_stop = True
                        logger.critical("PERSISTENT SECURITY STATE CORRUPTED! Lockout engaged.")
                        raise SecurityStateCorruptionError(
                            "Persistent security state checksum mismatch. System fail-stop locked."
                        )
                else:
                    # Initial boot: record baseline HMAC
                    conn.execute(
                        "INSERT OR REPLACE INTO state_manifest (manifest_id, state_hmac, updated_at_utc) VALUES (1, ?, ?)",
                        (computed, int(time.time())),
                    )

    def _assert_not_locked(self) -> None:
        if self.is_locked_fail_stop:
            raise SecurityStateCorruptionError(
                "Persistent security state is corrupted. Safe-mode fail-stop is engaged."
            )

    def is_sequence_processed(self, source_eid: str, sequence_id: int) -> bool:
        """Checks if a sequence ID was previously accepted."""
        self._assert_not_locked()
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM seen_sequences WHERE source_eid = ? AND sequence_id = ?",
                    (source_eid, sequence_id),
                )
                return cursor.fetchone() is not None

    def record_accepted_command(self, source_eid: str, sequence_id: int, envelope_id: str) -> None:
        """Atomically records an accepted command sequence and commits updated HMAC."""
        self._assert_not_locked()
        now = int(time.time())
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM seen_sequences WHERE source_eid = ? AND sequence_id = ?",
                    (source_eid, sequence_id),
                )
                if cursor.fetchone() is not None:
                    raise ReplayDetectedError(
                        f"Replay detected in persistent state: sequence {sequence_id} from '{source_eid}' was already executed."
                    )

                conn.execute(
                    """
                    INSERT INTO seen_sequences (source_eid, sequence_id, envelope_id, accepted_at_utc)
                    VALUES (?, ?, ?, ?)
                    """,
                    (source_eid, sequence_id, envelope_id, now),
                )
                # Recompute and commit state HMAC atomically
                new_hmac = self._compute_state_hmac(conn)
                conn.execute(
                    "UPDATE state_manifest SET state_hmac = ?, updated_at_utc = ? WHERE manifest_id = 1",
                    (new_hmac, now),
                )

    def get_highest_sequence(self, source_eid: str) -> int:
        """Retrieves highest accepted sequence number for a peer."""
        self._assert_not_locked()
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT MAX(sequence_id) as max_seq FROM seen_sequences WHERE source_eid = ?",
                    (source_eid, ),
                )
                row = cursor.fetchone()
                return row["max_seq"] or 0

    def record_revocation(self, eid: str, reason: str) -> None:
        """Atomically persists a revoked identity."""
        self._assert_not_locked()
        now = int(time.time())
        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO revoked_identities (eid, revoked_at_utc, reason) VALUES (?, ?, ?)",
                    (eid, now, reason),
                )
                new_hmac = self._compute_state_hmac(conn)
                conn.execute(
                    "UPDATE state_manifest SET state_hmac = ?, updated_at_utc = ? WHERE manifest_id = 1",
                    (new_hmac, now),
                )

    def is_identity_revoked(self, eid: str) -> bool:
        """Checks if an identity is revoked in persistent storage."""
        self._assert_not_locked()
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT 1 FROM revoked_identities WHERE eid = ?", (eid, ))
                return cursor.fetchone() is not None
