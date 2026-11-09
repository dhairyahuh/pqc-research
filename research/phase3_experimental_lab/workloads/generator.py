"""ASTRA-Sec Phase 3: Workload and Traffic Generator.

Produces synthetic telecommand payloads across configurable sizes,
arrival rates, concurrency levels, and burst profiles.
"""

import hashlib
import time
from typing import Iterator, Tuple
from research.phase3_experimental_lab.harness.config import WorkloadConfig


class WorkloadGenerator:
    """Generates deterministic telecommand workloads for load testing."""

    def __init__(self, config: WorkloadConfig, random_seed: int = 42):
        self.config = config
        self.seed = random_seed
        self._pattern = self._build_deterministic_payload_template(config.payload_size_bytes)

    def _build_deterministic_payload_template(self, size_bytes: int) -> bytes:
        """Constructs a deterministic repeatable byte pattern matching size_bytes."""
        base_header = f"ASTRA-SEC-LOADTEST-SEED-{self.seed}:".encode("ascii")
        if len(base_header) >= size_bytes:
            return base_header[:size_bytes]

        padding_needed = size_bytes - len(base_header)
        # Generate pseudo-random repeatable padding using SHA256 blocks
        padding = bytearray()
        counter = 0
        while len(padding) < padding_needed:
            block = hashlib.sha256(f"{self.seed}:{counter}".encode("ascii")).digest()
            padding.extend(block)
            counter += 1
        return base_header + bytes(padding[:padding_needed])

    def generate_payload(self, message_index: int) -> bytes:
        """Returns deterministic payload for the given message index."""
        # Embed message index in first 16 bytes for identification
        idx_prefix = f"MSG-{message_index:08d}:".encode("ascii")
        return idx_prefix + self._pattern[len(idx_prefix):]

    def iter_workload(self) -> Iterator[Tuple[int, bytes, float]]:
        """Yields (message_index, payload, target_dispatch_time) adhering to rate."""
        interval_s = 1.0 / self.config.rate_msg_per_sec if not self.config.burst_mode else 0.0
        start_time = time.time()

        for idx in range(self.config.total_messages):
            target_time = start_time + (idx * interval_s)
            payload = self.generate_payload(idx)
            yield idx, payload, target_time
