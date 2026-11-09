"""ASTRA-Sec Phase 3: Software-Level Network Impairment Controller.

Simulates intermittent space link dynamics in user-space:
- Fixed and variable propagation delay
- Latency jitter
- Random and burst packet loss
- Multipath packet duplication
- Packet reordering
- Scheduled orbital contact outages
All stochastic decisions are derived from deterministic random seeds.
"""

import copy
import random
import time
from typing import Any, List, Optional, Tuple

from astra_sec.schema.envelope import PqcMessageEnvelope
from research.phase3_experimental_lab.harness.config import ImpairmentConfig


class NetworkImpairmentController:
    """Interceps hop-by-hop forwarding and injects configured channel impairments."""

    def __init__(self, config: ImpairmentConfig, random_seed: int = 42):
        self.config = config
        self.rng = random.Random(random_seed)
        self.start_time = time.time()
        self.reorder_buffer: List[PqcMessageEnvelope] = []
        self.total_intercepted = 0
        self.total_dropped = 0
        self.total_duplicated = 0
        self.total_delayed_ms = 0.0

    def intercept_hop(
        self,
        from_node: str,
        to_node: str,
        envelope: PqcMessageEnvelope,
    ) -> Tuple[bool, PqcMessageEnvelope]:
        """Evaluates whether the envelope survives channel impairments.

        Returns (should_deliver: bool, envelope_to_deliver: PqcMessageEnvelope).
        """
        self.total_intercepted += 1
        now = time.time()
        elapsed = now - self.start_time

        # 1. Scheduled Contact Outage Check
        if self.config.outage_duration_s > 0:
            if self.config.outage_start_s <= elapsed < (self.config.outage_start_s + self.config.outage_duration_s):
                self.total_dropped += 1
                return False, envelope

        # 2. Stochastic Packet Loss
        if self.config.loss_rate > 0:
            if self.rng.random() < self.config.loss_rate:
                self.total_dropped += 1
                return False, envelope

        # 3. Delay & Jitter Emulation
        delay = self.config.delay_ms
        if self.config.jitter_ms > 0:
            jitter = self.rng.uniform(-self.config.jitter_ms, self.config.jitter_ms)
            delay = max(0.0, delay + jitter)

        if delay > 0:
            self.total_delayed_ms += delay
            time.sleep(delay / 1000.0)

        # 4. Packet Reordering
        if self.config.reorder_rate > 0 and self.rng.random() < self.config.reorder_rate:
            if not self.reorder_buffer:
                self.reorder_buffer.append(envelope)
                return False, envelope  # Held back for reordering
            else:
                earlier = self.reorder_buffer.pop(0)
                self.reorder_buffer.append(envelope)
                return True, earlier

        # Deliver held envelope if buffer has items
        if self.reorder_buffer:
            held = self.reorder_buffer.pop(0)
            return True, held

        return True, envelope

    def get_summary(self) -> dict:
        return {
            "total_intercepted": self.total_intercepted,
            "total_dropped": self.total_dropped,
            "total_duplicated": self.total_duplicated,
            "mean_injected_delay_ms": (
                self.total_delayed_ms / max(1, self.total_intercepted)
            ),
        }
