"""ASTRA-Sec Phase 3: Cryptographic Fault Campaign Controller.

Coordinates fault injection against ML-KEM-768 execution:
- Transient Single-Event Upsets (SEU)
- Persistent stuck-bit register faults
- Twiddle table corruptions
- Multi-bit / ciphertext mutations
Tracks activation, detection, rollback recovery, fail-stop, and SDC.
"""

import random
from typing import Any, Dict
from astra_sec.schema.envelope import PqcMessageEnvelope
from research.phase3_experimental_lab.harness.config import FaultConfig


class FaultInjectionController:
    """Controls and monitors fault activations during experimental runs."""

    def __init__(self, config: FaultConfig, random_seed: int = 42):
        self.config = config
        self.rng = random.Random(random_seed)
        self.total_injected = 0
        self.total_activated = 0
        self.detected_count = 0
        self.recovered_count = 0
        self.fail_stop_count = 0
        self.sdc_count = 0

    def apply_fault(self, envelope: PqcMessageEnvelope) -> None:
        """Injects configured fault into the transit envelope."""
        if not self.config.enabled:
            return

        if self.rng.random() > self.config.injection_probability:
            return

        self.total_injected += 1

        if self.config.fault_type == "transient_seu":
            # Mutate 1 bit in ciphertext (simulating NTT intermediate corruption)
            ct = bytearray(envelope.header.kem_ciphertext)
            byte_idx = (self.config.target_layer * 32) % len(ct)
            ct[byte_idx] ^= (1 << self.config.bit_position)
            envelope.header.kem_ciphertext = bytes(ct)
            self.total_activated += 1

        elif self.config.fault_type == "persistent_stuck_bit":
            # Multi-byte stuck-bit mutation causing unrecoverable failure
            ct = bytearray(envelope.header.kem_ciphertext)
            for i in range(4):
                ct[i * 16] |= 0xFF
            envelope.header.kem_ciphertext = bytes(ct)
            self.total_activated += 1

        elif self.config.fault_type == "twiddle_corrupt":
            ct = bytearray(envelope.header.kem_ciphertext)
            ct[0] ^= 0x55
            envelope.header.kem_ciphertext = bytes(ct)
            self.total_activated += 1

    def record_outcome(self, result_status: str, has_sdc: bool) -> None:
        if has_sdc:
            self.sdc_count += 1
        if "RECOVERED" in result_status or result_status == "SUCCESS":
            self.recovered_count += 1
            self.detected_count += 1
        elif "FAIL_STOP" in result_status or "DecapsulationFaultError" in result_status or "DecryptionError" in result_status:
            self.fail_stop_count += 1
            self.detected_count += 1

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_injected": self.total_injected,
            "total_activated": self.total_activated,
            "detected_count": self.detected_count,
            "recovered_count": self.recovered_count,
            "fail_stop_count": self.fail_stop_count,
            "sdc_count": self.sdc_count,
            "detection_coverage_pct": (
                (self.detected_count / max(1, self.total_activated)) * 100.0
            ),
        }
