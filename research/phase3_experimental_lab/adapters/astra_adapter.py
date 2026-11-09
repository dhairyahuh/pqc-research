"""ASTRA-Sec Phase 3: Full ASTRA-Sec Treatment Adapter (Treatment E).

Invokes the genuine 4-node ASTRA-Sec pipeline:
GSA -> SAT1 (spool) -> SAT2 (spool) -> GSB -> Return ACK to GSA.
Instruments each layer using high-resolution monotonic timers.
"""

import os
import time
from typing import Any, Dict, List, Optional

from astra_sec.crypto.factory import CryptoEngineFactory
from astra_sec.dtn.adapter import AstraDtnBridge
from astra_sec.dtn.bpv7 import BpV7Bundle
from astra_sec.network.relay import SatelliteRelayNode
from astra_sec.network.routing import ContactSchedule, RoutingTable
from astra_sec.schema.envelope import PqcMessageEnvelope
from astra_sec.schema.network import DeliveryStatus, LinkState
from astra_sec.schema.trust import PublicKeyTrustStore
from astra_sec.security.policy import AuthorizationPolicy, AuthorizationStatus
from astra_sec.security.verifier import GroundStationVerifier
from astra_sec.service.ground_station import GroundStationNode
from research.phase3_experimental_lab.adapters.base import ExperimentAdapter


class AstraSecTreatmentAdapter(ExperimentAdapter):
    """Executes the complete production-path ASTRA-Sec 4-node pipeline."""

    def __init__(self, use_in_memory_spool: bool = False):
        self.use_in_memory_spool = use_in_memory_spool
        self.gsa: Optional[GroundStationNode] = None
        self.gsb: Optional[GroundStationNode] = None
        self.sat1: Optional[SatelliteRelayNode] = None
        self.sat2: Optional[SatelliteRelayNode] = None
        self.verifier: Optional[GroundStationVerifier] = None
        self.trust_store: Optional[PublicKeyTrustStore] = None
        self.policy: Optional[AuthorizationPolicy] = None
        self.impairment_controller: Optional[Any] = None
        self.fault_controller: Optional[Any] = None
        self.delivered_envelopes: List[PqcMessageEnvelope] = []
        self._temp_dir: Optional[str] = None

    def setup(
        self,
        temp_dir: str,
        impairment_controller: Optional[Any] = None,
        fault_controller: Optional[Any] = None,
    ) -> None:
        self._temp_dir = temp_dir
        self.impairment_controller = impairment_controller
        self.fault_controller = fault_controller
        self.delivered_envelopes.clear()

        # Database paths for spools
        if self.use_in_memory_spool:
            spool_sat1 = ":memory:"
            spool_sat2 = ":memory:"
        else:
            spool_sat1 = os.path.join(temp_dir, "spool_sat1.db")
            spool_sat2 = os.path.join(temp_dir, "spool_sat2.db")

        self.trust_store = PublicKeyTrustStore()
        self.policy = AuthorizationPolicy()

        self.gsa = GroundStationNode(
            node_eid="dtn://gsa/app",
            role="ground_station",
            trust_store=self.trust_store,
            policy=self.policy,
        )
        self.gsb = GroundStationNode(
            node_eid="dtn://gsb/app",
            role="ground_station",
            trust_store=self.trust_store,
            policy=self.policy,
        )

        # Register peer public keys
        self.trust_store.register_peer(self.gsa.get_public_identity())
        self.trust_store.register_peer(self.gsb.get_public_identity())
        self.policy.set_authorization("dtn://gsa/app", "ground_station", AuthorizationStatus.AUTHORIZED)
        self.policy.set_authorization("dtn://gsb/app", "ground_station", AuthorizationStatus.AUTHORIZED)

        # Relay 1 & Relay 2 configuration
        sched1 = ContactSchedule("dtn://sat1/relay")
        sched1.set_link_override("dtn://sat2/relay", LinkState.UP)
        sched2 = ContactSchedule("dtn://sat2/relay")
        sched2.set_link_override("dtn://gsb/app", LinkState.UP)
        sched2.set_link_override("dtn://sat1/relay", LinkState.UP)

        rt1 = RoutingTable({"dtn://gsb/*": "dtn://sat2/relay", "dtn://gsa/*": "dtn://gsa/app"})
        rt2 = RoutingTable({"dtn://gsb/*": "dtn://gsb/app", "dtn://gsa/*": "dtn://sat1/relay"})

        self.sat1 = SatelliteRelayNode("dtn://sat1/relay", spool_db_path=spool_sat1, routing_table=rt1, contact_schedule=sched1)
        self.sat2 = SatelliteRelayNode("dtn://sat2/relay", spool_db_path=spool_sat2, routing_table=rt2, contact_schedule=sched2)

        # Connect relays with impairment controller interception
        def forward_sat1_to_sat2(target_eid: str, env: PqcMessageEnvelope, from_peer: str = None) -> bool:
            if self.impairment_controller:
                should_deliver, delayed_env = self.impairment_controller.intercept_hop("dtn://sat1/relay", target_eid, env)
                if not should_deliver:
                    return False
                env = delayed_env
            evt = self.sat2.ingest(env, from_peer="dtn://sat1/relay")
            return evt.status == DeliveryStatus.FORWARDED

        def forward_sat2_to_gsb(target_eid: str, env: PqcMessageEnvelope, from_peer: str = None) -> bool:
            if self.impairment_controller:
                should_deliver, delayed_env = self.impairment_controller.intercept_hop("dtn://sat2/relay", target_eid, env)
                if not should_deliver:
                    return False
                env = delayed_env
            self.delivered_envelopes.append(env)
            return True

        self.sat1.forwarder_fn = forward_sat1_to_sat2
        self.sat2.forwarder_fn = forward_sat2_to_gsb

        self.verifier = GroundStationVerifier("dtn://gsa/app", trust_store=self.trust_store)

    def send_and_receive(
        self,
        payload: bytes,
        ttl_seconds: int = 300,
        custom_sequence_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        assert self.gsa is not None and self.gsb is not None
        self.delivered_envelopes.clear()

        metrics: Dict[str, Any] = {
            "delivered": False,
            "status": "UNKNOWN",
            "error": None,
            "payload_bytes": len(payload),
            "wire_bytes": 0,
            "e2e_latency_us": 0.0,
            "t_origin_us": 0.0,
            "t_cbor_ser_us": 0.0,
            "t_relay_transit_us": 0.0,
            "t_dest_verify_us": 0.0,
            "t_ack_roundtrip_us": 0.0,
        }

        t_start = time.perf_counter_ns()

        try:
            # 1. GSA Originates, encapsulates, encrypts, and signs envelope
            t0 = time.perf_counter_ns()
            env = self.gsa.send_message(
                destination_eid="dtn://gsb/app",
                payload=payload,
                ttl_seconds=ttl_seconds,
                custom_sequence_id=custom_sequence_id,
            )
            self.verifier.record_dispatched_command(env)
            t1 = time.perf_counter_ns()
            metrics["t_origin_us"] = (t1 - t0) / 1000.0

            # 2. Serialize into BPv7 Bundle
            bundle = AstraDtnBridge.envelope_to_bundle(env)
            wire_bytes = bundle.to_cbor_bytes()
            metrics["wire_bytes"] = len(wire_bytes)
            t2 = time.perf_counter_ns()
            metrics["t_cbor_ser_us"] = (t2 - t1) / 1000.0

            # Apply fault controller if configured
            if self.fault_controller:
                self.fault_controller.apply_fault(env)

            # 3. Transmit through Relays (SAT1 -> SAT2 -> GSB)
            t_relay_start = time.perf_counter_ns()
            evt_sat1 = self.sat1.ingest(env, from_peer="dtn://gsa/app")
            t_relay_end = time.perf_counter_ns()
            metrics["t_relay_transit_us"] = (t_relay_end - t_relay_start) / 1000.0

            if not self.delivered_envelopes:
                metrics["status"] = evt_sat1.status.name
                metrics["error"] = f"Relay ingestion result: {evt_sat1.status.name}"
                return metrics

            # 4. GSB Receives, decapsulates, verifies, and decrypts
            delivered_env = self.delivered_envelopes[0]
            t_dest_start = time.perf_counter_ns()
            pt, ack = self.gsb.receive_message(delivered_env)
            t_dest_end = time.perf_counter_ns()
            metrics["t_dest_verify_us"] = (t_dest_end - t_dest_start) / 1000.0

            if pt != payload:
                metrics["status"] = "CORRUPT_PAYLOAD_SDC"
                metrics["error"] = "Decrypted plaintext does not match dispatched payload"
                return metrics

            # 5. Return ACK verified at GSA Verifier
            t_ack_start = time.perf_counter_ns()
            rec = self.verifier.verify_acknowledgment(ack)
            t_ack_end = time.perf_counter_ns()
            metrics["t_ack_roundtrip_us"] = (t_ack_end - t_ack_start) / 1000.0

            metrics["delivered"] = True
            metrics["status"] = "SUCCESS"
            metrics["e2e_latency_us"] = (time.perf_counter_ns() - t_start) / 1000.0
            return metrics

        except Exception as e:
            metrics["delivered"] = False
            metrics["status"] = type(e).__name__
            metrics["error"] = str(e)
            metrics["e2e_latency_us"] = (time.perf_counter_ns() - t_start) / 1000.0
            return metrics

    def teardown(self) -> None:
        self.gsa = None
        self.gsb = None
        self.sat1 = None
        self.sat2 = None
        self.verifier = None

    def get_system_telemetry(self) -> Dict[str, Any]:
        fdir = self.gsb.get_fdir_telemetry() if self.gsb else None
        return {
            "transient_recoveries": fdir.transient_recoveries if fdir else 0,
            "persistent_fail_stops": fdir.persistent_fail_stops if fdir else 0,
            "twiddle_faults_detected": fdir.twiddle_faults_detected if fdir else 0,
            "bundles_forwarded": fdir.bundles_forwarded if fdir else 0,
            "bundles_rejected": fdir.bundles_rejected if fdir else 0,
        }
