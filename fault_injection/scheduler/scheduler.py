"""
Deterministic Fault Scheduling and Metadata Generator for PQC Experiments.
"""

import hashlib
import random
from typing import Generator, Dict, Any, List
from fault_injection.fault_models.fault_definitions import FaultDescriptor, FaultClass


class DeterministicScheduler:
    """
    Generates fully reproducible sequences of fault descriptors using
    SHA-256 derived seeds and deterministic pseudo-random parameters.
    """

    def __init__(self, master_seed: int, experiment_id: str):
        self.master_seed = master_seed
        self.experiment_id = experiment_id

    def derive_run_seed(self, iteration: int) -> int:
        """Derives a deterministic 64-bit integer seed for a specific iteration."""
        seed_str = f"{self.experiment_id}:{self.master_seed}:{iteration}"
        digest = hashlib.sha256(seed_str.encode("utf-8")).digest()
        return int.from_bytes(digest[:8], byteorder="big")

    def schedule_seu_campaign(
        self,
        algorithm: str,
        parameter_set: str,
        target_name: str,
        buffer_len: int,
        injection_stage: str,
        iterations: int
    ) -> Generator[FaultDescriptor, None, None]:
        """Schedules N single-bit flips across random byte and bit coordinates."""
        for i in range(iterations):
            run_seed = self.derive_run_seed(i)
            rng = random.Random(run_seed)

            byte_idx = rng.randint(0, buffer_len - 1)
            bit_idx = rng.randint(0, 7)

            yield FaultDescriptor(
                experiment_id=self.experiment_id,
                algorithm=algorithm,
                parameter_set=parameter_set,
                fault_class=FaultClass.SEU.value,
                fault_type="single_bit_flip",
                target=target_name,
                target_index=byte_idx,
                bit_index=bit_idx,
                injection_stage=injection_stage,
                injection_time=0.0,
                seed=run_seed,
                duration=1,
                magnitude=1
            )

    def schedule_burst_campaign(
        self,
        algorithm: str,
        parameter_set: str,
        target_name: str,
        buffer_len: int,
        burst_len: int,
        injection_stage: str,
        iterations: int
    ) -> Generator[FaultDescriptor, None, None]:
        """Schedules N burst corruptions of length burst_len."""
        for i in range(iterations):
            run_seed = self.derive_run_seed(i)
            rng = random.Random(run_seed)

            max_start = max(0, buffer_len - burst_len)
            start_byte = rng.randint(0, max_start)

            yield FaultDescriptor(
                experiment_id=self.experiment_id,
                algorithm=algorithm,
                parameter_set=parameter_set,
                fault_class=FaultClass.BURST.value,
                fault_type="burst_byte_corruption",
                target=target_name,
                target_index=start_byte,
                bit_index=0,
                injection_stage=injection_stage,
                injection_time=0.0,
                seed=run_seed,
                duration=1,
                magnitude=burst_len
            )
