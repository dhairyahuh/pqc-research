"""ASTRA-Sec: Anti-Replay Filter & Message Freshness Validator."""

import threading
import time
from typing import Dict, Optional, Set

from astra_sec.core.exceptions import ReplayDetectedError, StaleMessageError


class AntiReplayFilter:
    """Sliding-window Anti-Replay and Freshness Tracker per peer EID."""

    def __init__(self, max_clock_skew_seconds: int = 120, window_size: int = 1000):
        self._max_clock_skew = max_clock_skew_seconds
        self._window_size = window_size
        self._highest_seq: Dict[str, int] = {}
        self._seen_seqs: Dict[str, Set[int]] = {}
        self._lock = threading.Lock()

    def check_and_update(
        self,
        source_eid: str,
        sequence_id: int,
        timestamp_utc: int,
        ttl_seconds: int,
        current_time: Optional[int] = None,
    ) -> None:
        """Validates that a message is fresh and not replayed, then updates state.

        Raises:
            StaleMessageError: if the message has exceeded its TTL or is too far in future.
            ReplayDetectedError: if the sequence number has already been seen or is stale.
        """
        now = current_time if current_time is not None else int(time.time())

        # 1. Freshness checks
        if now > (timestamp_utc + ttl_seconds):
            raise StaleMessageError(
                f"Message expired: timestamp {timestamp_utc} + TTL {ttl_seconds}s "
                f"< current time {now} (expired by {now - (timestamp_utc + ttl_seconds)}s)"
            )

        if timestamp_utc > (now + self._max_clock_skew):
            raise StaleMessageError(
                f"Message timestamp in future: {timestamp_utc} > {now + self._max_clock_skew} (skew exceeded)"
            )

        # 2. Anti-replay checks
        with self._lock:
            if source_eid not in self._seen_seqs:
                self._seen_seqs[source_eid] = set()
                self._highest_seq[source_eid] = 0

            seen = self._seen_seqs[source_eid]
            highest = self._highest_seq[source_eid]

            if sequence_id in seen:
                raise ReplayDetectedError(
                    f"Replay detected: sequence {sequence_id} from '{source_eid}' was already processed."
                )

            # If sequence is older than lowest retained window edge
            if sequence_id <= (highest - self._window_size):
                raise ReplayDetectedError(
                    f"Sequence {sequence_id} is too old (window edge is {highest - self._window_size})."
                )

            # Record sequence
            seen.add(sequence_id)
            if sequence_id > highest:
                self._highest_seq[source_eid] = sequence_id

            # Trim seen set to bound memory footprint
            if len(seen) > self._window_size * 2:
                min_retained = self._highest_seq[source_eid] - self._window_size
                self._seen_seqs[source_eid] = {s for s in seen if s >= min_retained}
