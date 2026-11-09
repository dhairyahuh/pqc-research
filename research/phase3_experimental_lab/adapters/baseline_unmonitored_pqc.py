"""ASTRA-Sec Phase 3: Baseline B — PQC Without Monitored Fault Resilience.

Executes standard ML-KEM-768 and ML-DSA-65 using LibOQS baseline
without internal sub-word NTT butterfly invariant monitoring.
Provides the reference baseline isolating the exact cost and fault behavior
of the monitored native C implementation.
"""

from astra_sec.crypto.oqs_adapter import OqsDsaAdapter, OqsKemAdapter
from research.phase3_experimental_lab.adapters.astra_adapter import AstraSecTreatmentAdapter


class BaselineUnmonitoredPqcAdapter(AstraSecTreatmentAdapter):
    """Executes the 4-node pipeline using standard unmonitored LibOQS adapters."""

    def setup(self, temp_dir: str, impairment_controller=None, fault_controller=None) -> None:
        super().setup(temp_dir, impairment_controller, fault_controller)
        # Substitute unmonitored LibOQS adapters into GSA and GSB
        unmonitored_kem = OqsKemAdapter()
        unmonitored_dsa = OqsDsaAdapter()
        if self.gsa:
            self.gsa.kem = unmonitored_kem
            self.gsa.dsa = unmonitored_dsa
        if self.gsb:
            self.gsb.kem = unmonitored_kem
            self.gsb.dsa = unmonitored_dsa
