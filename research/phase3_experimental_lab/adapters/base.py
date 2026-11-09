"""ASTRA-Sec Phase 3: Abstract Experiment Adapter Interface.

Defines the contract for executing message round-trips across
various cryptographic and transport baselines.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple


class ExperimentAdapter(ABC):
    """Abstract interface implemented by all baseline and treatment pipelines."""

    @abstractmethod
    def setup(self, temp_dir: str, impairment_controller: Optional[Any] = None, fault_controller: Optional[Any] = None) -> None:
        """Initializes nodes, keys, routing, spools, and controllers."""
        pass

    @abstractmethod
    def send_and_receive(
        self,
        payload: bytes,
        ttl_seconds: int = 300,
        custom_sequence_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Dispatches payload through the pipeline and verifies receipt and ACK.

        Returns structured measurement dictionary with timing, outcomes, and sizes.
        """
        pass

    @abstractmethod
    def teardown(self) -> None:
        """Releases sockets, databases, and temporary resources."""
        pass

    @abstractmethod
    def get_system_telemetry(self) -> Dict[str, Any]:
        """Returns node and FDIR telemetry counts."""
        pass
