"""ASTRA-Sec Phase 3: Baseline A — Conventional Non-PQC Transport Adapter.

Uses standard classical cryptography:
- Pre-shared 256-bit symmetric key for AES-256-GCM encryption.
- HMAC-SHA256 (32 B) for message authentication instead of ML-DSA-65 (3,309 B).
- Same 4-node store-and-forward routing topology and SQLite spooling.
Provides the reference baseline isolating the exact cost of post-quantum operations.
"""

import hashlib
import hmac
import os
import time
from typing import Any, Dict, List, Optional

from astra_sec.crypto.aead import Aes256GcmAead
from astra_sec.network.relay import SatelliteRelayNode
from astra_sec.network.routing import ContactSchedule, RoutingTable
from astra_sec.schema.envelope import EnvelopeHeader, MessageAcknowledgment, PqcMessageEnvelope
from astra_sec.schema.network import DeliveryStatus, LinkState
from research.phase3_experimental_lab.adapters.base import ExperimentAdapter


class BaselineNonPqcAdapter(ExperimentAdapter):
    """Executes the 4-node pipeline with classical AES-GCM + HMAC-SHA256."""

    def __init__(self, use_in_memory_spool: bool = False):
        self.use_in_memory_spool = use_in_memory_spool
        self.aead = Aes256GcmAead()
        self.psk = hashlib.sha256(b"ASTRA_SEC_BASELINE_A_PRE_SHARED_KEY").digest()
        self.delivered_envelopes: List[PqcMessageEnvelope] = []
        self.sat1: Optional[SatelliteRelayNode] = None
        self.sat2: Optional[SatelliteRelayNode] = None
        self.seq_id = 1

    def setup(self, temp_dir: str, impairment_controller: Optional[Any] = None, fault_controller: Optional[Any] = None) -> None:
        self.delivered_envelopes.clear()
        if self.use_in_memory_spool:
            spool_sat1 = ":memory:"
            spool_sat2 = ":memory:"
        else:
            spool_sat1 = os.path.join(temp_dir, "spool_b_sat1.db")
            spool_sat2 = os.path.join(temp_dir, "spool_b_sat2.db")

        sched1 = ContactSchedule("dtn://sat1/relay")
        sched1.set_link_override("dtn://sat2/relay", LinkState.UP)
        sched2 = ContactSchedule("dtn://sat2/relay")
        sched2.set_link_override("dtn://gsb/app", LinkState.UP)

        rt1 = RoutingTable({"dtn://gsb/*": "dtn://sat2/relay"})
        rt2 = RoutingTable({"dtn://gsb/*": "dtn://gsb/app"})

        self.sat1 = SatelliteRelayNode("dtn://sat1/relay", spool_db_path=spool_sat1, routing_table=rt1, contact_schedule=sched1)
        self.sat2 = SatelliteRelayNode("dtn://sat2/relay", spool_db_path=spool_sat2, routing_table=rt2, contact_schedule=sched2)

        def forward_sat1(target_eid, env, from_peer=None):
            return self.sat2.ingest(env, from_peer="dtn://sat1/relay").status == DeliveryStatus.FORWARDED

        def forward_sat2(target_eid, env, from_peer=None):
            self.delivered_envelopes.append(env)
            return True

        self.sat1.forwarder_fn = forward_sat1
        self.sat2.forwarder_fn = forward_sat2

    def send_and_receive(
        self,
        payload: bytes,
        ttl_seconds: int = 300,
        custom_sequence_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        self.delivered_envelopes.clear()
        metrics = {
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
            t0 = time.perf_counter_ns()
            seq = custom_sequence_id or self.seq_id
            self.seq_id += 1
            nonce = self.aead.generate_nonce()
            # Non-PQC dummy KEM ciphertext padded to schema envelope standard 1,088 B
            dummy_kem = b"\x00" * 1088
            header = EnvelopeHeader(
                version=1,
                envelope_id=f"nonpqc-{seq}",
                source_eid="dtn://gsa/app",
                destination_eid="dtn://gsb/app",
                sequence_id=seq,
                timestamp_utc=int(time.time()),
                ttl_seconds=ttl_seconds,
                kem_ciphertext=dummy_kem,
                nonce=nonce,
            )
            aad = header.to_canonical_aad()
            ciphertext, tag = self.aead.encrypt(self.psk, nonce, payload, aad)
            # Classical HMAC-SHA256 signature (32 bytes) padded to schema envelope standard 3,309 B
            mac = hmac.new(self.psk, aad + ciphertext + tag, hashlib.sha256).digest()
            padded_mac = mac.ljust(3309, b"\x00")
            env = PqcMessageEnvelope(
                header=header,
                ciphertext=ciphertext,
                tag=tag,
                signature=padded_mac,
            )
            t1 = time.perf_counter_ns()
            metrics["t_origin_us"] = (t1 - t0) / 1000.0
            metrics["wire_bytes"] = len(ciphertext) + len(tag) + len(padded_mac) + len(aad)

            # Relay Transit
            t_r0 = time.perf_counter_ns()
            self.sat1.ingest(env, from_peer="dtn://gsa/app")
            t_r1 = time.perf_counter_ns()
            metrics["t_relay_transit_us"] = (t_r1 - t_r0) / 1000.0

            # Destination Ingest & Decrypt
            t_d0 = time.perf_counter_ns()
            delivered = self.delivered_envelopes[0]
            # Verify HMAC
            expected_mac = hmac.new(self.psk, delivered.header.to_canonical_aad() + delivered.ciphertext + delivered.tag, hashlib.sha256).digest()
            if not hmac.compare_digest(expected_mac, delivered.signature[:32]):
                metrics["status"] = "HMAC_VERIFICATION_FAILED"
                return metrics
            pt = self.aead.decrypt(self.psk, delivered.header.nonce, delivered.ciphertext, delivered.tag, delivered.header.to_canonical_aad())
            t_d1 = time.perf_counter_ns()
            metrics["t_dest_verify_us"] = (t_d1 - t_d0) / 1000.0

            if pt != payload:
                metrics["status"] = "CORRUPT_PAYLOAD"
                return metrics

            metrics["delivered"] = True
            metrics["status"] = "SUCCESS"
            metrics["e2e_latency_us"] = (time.perf_counter_ns() - t_start) / 1000.0
            return metrics
        except Exception as e:
            metrics["status"] = type(e).__name__
            metrics["error"] = str(e)
            metrics["e2e_latency_us"] = (time.perf_counter_ns() - t_start) / 1000.0
            return metrics

    def teardown(self) -> None:
        self.sat1 = None
        self.sat2 = None

    def get_system_telemetry(self) -> Dict[str, Any]:
        return {"baseline": "NON_PQC", "messages_delivered": self.seq_id - 1}
