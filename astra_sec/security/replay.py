"""ASTRA-Sec: Persistent Sliding-Window Anti-Replay Filter (L6 / L7)."""

import logging
import threading
import time
from typing import Dict, Optional, Set

from astra_sec.core.exceptions import ReplayDetectedError, StaleMessageError
from astra_sec.security.persistent_state import PersistentSecurityState

logger = logging.getLogger("astra_sec.security.replay")


class PersistentAntiReplayFilter:
    """Combines high-performance sliding-window tracking with ACID crash-consistent persistence.

    Invariants:
    1. Node reboot does NOT reset the replay filter.
    2. Previously executed commands can never execute again.
    3. Valid delayed messages within TTL window are accepted.
    """

    def __init__(
        self,
        persistent_state: PersistentSecurityState,
        max_clock_skew_seconds: int = 120,
        window_size: int = 1000,
    ):
        self.state = persistent_state
        self._max_clock_skew = max_clock_skew_seconds
        self._window_size = window_size
        self._highest_seq: Dict[str, int] = {}
        self._lock = threading.Lock()

    def check_and_update(
        self,
        source_eid: str,
        sequence_id: int,
        timestamp_utc: int,
        ttl_seconds: int,
        envelope_id: str,
        current_time: Optional[int] = None,
    ) -> None:
        """Validates that a message is fresh and not replayed, then commits to persistent state.

        Raises:
            StaleMessageError: if the message has exceeded its TTL or is too far in future.
            ReplayDetectedError: if the sequence number has already been seen or is stale.
        """
        now = current_time if current_time is not None else int(time.time())

        # 1. Freshness checks
        if now > (timestamp_utc + ttl_seconds):
            raise StaleMessageError(
                f"Command expired: created at {timestamp_utc} with TTL={ttl_seconds}s "
                f"(current time is {now}, expired by {now - (timestamp_utc + ttl_seconds)}s)"
            )

        if timestamp_utc > (now + self._max_clock_skew):
            raise StaleMessageError(
                f"Command timestamp in future: {timestamp_utc} > {now + self._max_clock_skew} (skew exceeded)"
            )

        # 2. Anti-replay validation
        with self._lock:
            # Query persistent state first (survives restarts)
            if self.state.is_sequence_processed(source_eid, sequence_id):
                raise ReplayDetectedError(
                    f"Replay detected: sequence {sequence_id} from '{source_eid}' was already executed."
                )

            if source_eid not in self._highest_seq:
                self._highest_seq[source_eid] = self.state.get_highest_sequence(source_eid)

            highest = self._highest_seq[source_eid]

            # If sequence is behind the sliding window boundary
            if highest > self._window_size and sequence_id <= (highest - self._window_size):
                raise ReplayDetectedError(
                    f"Sequence {sequence_id} from '{source_eid}' is stale (sliding window edge is {highest - self._window_size})."
                )

            # Atomically commit to persistent database
            self.state.record_accepted_command(source_eid, sequence_id, envelope_id)

            if sequence_id > highest:
                self._highest_seq[source_eid] = sequence_id
