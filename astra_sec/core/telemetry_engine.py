"""ASTRA-Sec: Real-Time Telemetry Engine and Event Correlation Bus.

Provides a thread-safe, non-blocking, bounded event ring buffer with
structured JSONL persistence and end-to-end message correlation.
"""

from collections import deque
import json
import os
from pathlib import Path
import threading
import time
from typing import Any, Callable, Dict, List, Optional

from astra_sec.schema.telemetry import (
    ComponentLayer,
    CryptographicMeasurement,
    DtnQueueMeasurement,
    EventType,
    HopNetworkMeasurement,
    NttInvariantMeasurement,
    SystemHealthReport,
    TelemetryEvent,
)


class TelemetryEngine:
    """Thread-safe, bounded telemetry recorder and lifecycle correlation engine."""

    _instance: Optional["TelemetryEngine"] = None
    _lock = threading.Lock()

    def __init__(self, max_events: int = 1000, log_file: Optional[Path] = None):
        self._max_events = max_events
        self._events: deque[TelemetryEvent] = deque(maxlen=max_events)
        self._correlation_index: Dict[str, List[TelemetryEvent]] = {}
        self._listeners: List[Callable[[TelemetryEvent], None]] = []
        self._lock = threading.RLock()

        # Log directory & file
        if log_file:
            self._log_file = log_file
        else:
            base_dir = Path(__file__).resolve().parent.parent.parent
            telemetry_dir = base_dir / "data" / "telemetry"
            telemetry_dir.mkdir(parents=True, exist_ok=True)
            self._log_file = telemetry_dir / "live_events.jsonl"

        try:
            self._log_fd = open(self._log_file, "a", buffering=1, encoding="utf-8")
        except Exception:
            self._log_fd = None

    @classmethod
    def get_instance(cls, max_events: int = 1000) -> "TelemetryEngine":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(max_events=max_events)
            return cls._instance

    def add_listener(self, listener: Callable[[TelemetryEvent], None]) -> None:
        """Subscribes an event listener (e.g. WebSocket broadcaster)."""
        with self._lock:
            if listener not in self._listeners:
                self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[TelemetryEvent], None]) -> None:
        with self._lock:
            if listener in self._listeners:
                self._listeners.remove(listener)

    def emit_event(
        self,
        event_type: EventType,
        component: ComponentLayer,
        source_node: str,
        operation: str,
        status: str,
        correlation_id: str,
        destination_node: Optional[str] = None,
        message_id: Optional[str] = None,
        bundle_id: Optional[str] = None,
        duration_ns: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TelemetryEvent:
        """Creates, indexes, persists, and broadcasts a validated TelemetryEvent."""
        event = TelemetryEvent(
            event_type=event_type,
            timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            monotonic_timestamp_ns=time.perf_counter_ns(),
            component=component,
            source_node=source_node,
            destination_node=destination_node,
            message_id=message_id,
            bundle_id=bundle_id,
            operation=operation,
            status=status,
            duration_ns=duration_ns,
            correlation_id=correlation_id,
            metadata=metadata or {},
        )

        with self._lock:
            self._events.append(event)

            # Update correlation index
            if correlation_id not in self._correlation_index:
                self._correlation_index[correlation_id] = []
            self._correlation_index[correlation_id].append(event)
            if len(self._correlation_index[correlation_id]) > 100:
                self._correlation_index[correlation_id].pop(0)

            # Prune correlation index keys if too many
            if len(self._correlation_index) > 500:
                oldest_key = next(iter(self._correlation_index))
                del self._correlation_index[oldest_key]

            # Fast buffered write to structured JSONL audit stream
            if self._log_fd is not None:
                try:
                    self._log_fd.write(event.model_dump_json() + "\n")
                except Exception:
                    pass

        # Dispatch to active listeners
        for listener in list(self._listeners):
            try:
                listener(event)
            except Exception:
                pass

        return event

    def get_recent_events(
        self,
        limit: int = 50,
        component: Optional[str] = None,
        event_type: Optional[str] = None,
    ) -> List[TelemetryEvent]:
        """Returns the most recent events in reverse chronological order."""
        return self.query_events(limit=limit, component=component, event_type=event_type)

    def query_events(
        self,
        limit: int = 50,
        component: Optional[Any] = None,
        event_type: Optional[Any] = None,
        correlation_id: Optional[str] = None,
    ) -> List[TelemetryEvent]:
        """Queries telemetry events with optional filters."""
        with self._lock:
            matched = []
            for ev in reversed(self._events):
                if correlation_id and ev.correlation_id != correlation_id:
                    continue
                if component and ev.component != component:
                    continue
                if event_type and ev.event_type != event_type:
                    continue
                matched.append(ev)
                if len(matched) >= limit:
                    break
            return matched

    def get_lifecycle_events(self, correlation_id: str) -> List[TelemetryEvent]:
        """Returns all correlated events for a single message in chronological order."""
        with self._lock:
            events = self._correlation_index.get(correlation_id, [])
            return list(events)

    def clear(self) -> None:
        """Clears in-memory event buffers (used for test isolation)."""
        with self._lock:
            self._events.clear()
            self._correlation_index.clear()

    def close(self) -> None:
        """Flushes and closes the persistence file descriptor."""
        with self._lock:
            if self._log_fd is not None and not self._log_fd.closed:
                try:
                    self._log_fd.flush()
                    self._log_fd.close()
                except Exception:
                    pass
                self._log_fd = None

    def __del__(self) -> None:
        self.close()
