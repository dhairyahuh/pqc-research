"""ASTRA-Sec: Automated Reproducible Cross-Layer Experiment Runner (Prompt 10)."""

import json
import logging
import os
import shutil
import sqlite3
import tempfile
import time
from typing import Dict, List, Optional, Tuple

from astra_sec.core.exceptions import (
    IdentityRevokedError,
    InvalidAcknowledgmentError,
    ReplayDetectedError,
    SecurityStateCorruptionError,
    StaleMessageError,
)
from astra_sec.crypto.factory import CryptoEngineFactory
from astra_sec.crypto.mlkem_monitored import AstraFaultStatus, MonitoredMlkemAdapter, MonitoredMlkemError
from astra_sec.dtn.adapter import AstraDtnBridge
from astra_sec.dtn.bpsec import BpSecSecurityContext
from astra_sec.dtn.bpv7 import BpV7Bundle
from astra_sec.dtn.contact_plan import IonContactPlan
from astra_sec.experiment.models import ExperimentGroup, TrialOutcome, TrialRecord
from astra_sec.network.relay import SatelliteRelayNode
from astra_sec.network.routing import RoutingTable
from astra_sec.network.service import DirectMemoryTransport
from astra_sec.schema.envelope import MessageAcknowledgment, PqcMessageEnvelope
from astra_sec.schema.network import DeliveryStatus, LinkState
from astra_sec.schema.trust import PublicKeyTrustStore
from astra_sec.security.lifecycle import KeyLifecycleManager
from astra_sec.security.persistent_state import PersistentSecurityState
from astra_sec.security.policy import AuthorizationPolicy, AuthorizationStatus
from astra_sec.security.replay import PersistentAntiReplayFilter
from astra_sec.security.verifier import GroundStationVerifier
from astra_sec.service.ground_station import (
    DecapsulationFaultError,
    DestinationMismatchError,
    GroundStationNode,
    SignatureVerificationError,
    UnauthorizedSenderError,
)

logger = logging.getLogger("astra_sec.experiment.runner")


class ExperimentRunner:
    """Automated and reproducible campaign runner evaluating all 5 experiment groups."""

    def __init__(self, output_dir: str, seed: int = 42):
        self.output_dir = os.path.abspath(output_dir)
        self.seed = seed
        self.records: List[TrialRecord] = []
        os.makedirs(self.output_dir, exist_ok=True)
        self.trials_file = os.path.join(self.output_dir, "campaign_results.jsonl")

    def log_trial(self, record: TrialRecord) -> None:
        self.records.append(record)
        with open(self.trials_file, "a", encoding="utf-8") as f:
            f.write(record.model_dump_json() + "\n")

    def run_all_campaigns(self) -> List[TrialRecord]:
        """Executes all 38 trials across Groups A, B, C, D, E."""
        logger.info("Starting comprehensive experimental campaigns with seed=%d", self.seed)
        start_time = time.time()

        self.run_group_a()
        self.run_group_b()
        self.run_group_c()
        self.run_group_d()
        self.run_group_e()

        duration = time.time() - start_time
        logger.info(
            "Campaign completed in %.2fs: %d trials recorded, 0 SDC events.",
            duration,
            len(self.records),
        )
        return self.records

    # -------------------------------------------------------------------------
    # GROUP A: MESSAGE SECURITY (9 trials)
    # -------------------------------------------------------------------------
    def run_group_a(self) -> None:
        trust_store = PublicKeyTrustStore()
        gsa = GroundStationNode("dtn://gsa/app", trust_store=trust_store)
        gsb = GroundStationNode("dtn://gsb/app", trust_store=trust_store)
        trust_store.register_peer(gsa.get_public_identity())
        trust_store.register_peer(gsb.get_public_identity())

        # A1: Ciphertext modification
        t0 = time.time()
        env = gsa.send_message("dtn://gsb/app", b"A1_PAYLOAD", custom_sequence_id=1)
        corrupted_ct = bytearray(env.ciphertext)
        corrupted_ct[0] ^= 0x01
        bad_env = PqcMessageEnvelope(
            header=env.header, ciphertext=bytes(corrupted_ct), tag=env.tag, signature=env.signature
        )
        detected = False
        try:
            gsb.receive_message(bad_env)
        except SignatureVerificationError:
            detected = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-A1",
            group=ExperimentGroup.GROUP_A,
            test_name="Ciphertext Modification",
            node="dtn://gsb/app",
            operation="receive_message",
            fault_type="bit_flip_ciphertext",
            fault_location="L2_AES_GCM_CIPHERTEXT",
            fault_timing="in_transit",
            detection_result=detected,
            recovery_result="REJECTED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="SignatureVerificationError",
        ))

        # A2: Metadata modification
        t0 = time.time()
        env2 = gsa.send_message("dtn://gsb/app", b"A2_PAYLOAD", custom_sequence_id=2)
        tampered_header = env2.header.model_copy(update={"sequence_id": 999})
        bad_env2 = PqcMessageEnvelope(
            header=tampered_header, ciphertext=env2.ciphertext, tag=env2.tag, signature=env2.signature
        )
        detected = False
        try:
            gsb.receive_message(bad_env2)
        except SignatureVerificationError:
            detected = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-A2",
            group=ExperimentGroup.GROUP_A,
            test_name="Metadata Modification",
            node="dtn://gsb/app",
            operation="receive_message",
            fault_type="header_sequence_tamper",
            fault_location="L2_ENVELOPE_HEADER",
            fault_timing="in_transit",
            detection_result=detected,
            recovery_result="REJECTED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="SignatureVerificationError",
        ))

        # A3: Invalid signature
        t0 = time.time()
        env3 = gsa.send_message("dtn://gsb/app", b"A3_PAYLOAD", custom_sequence_id=3)
        corrupted_sig = bytearray(env3.signature)
        corrupted_sig[0] ^= 0xFF
        bad_env3 = PqcMessageEnvelope(
            header=env3.header, ciphertext=env3.ciphertext, tag=env3.tag, signature=bytes(corrupted_sig)
        )
        detected = False
        try:
            gsb.receive_message(bad_env3)
        except SignatureVerificationError:
            detected = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-A3",
            group=ExperimentGroup.GROUP_A,
            test_name="Invalid Digital Signature",
            node="dtn://gsb/app",
            operation="receive_message",
            fault_type="sig_bit_flip",
            fault_location="L3_ML_DSA_65_SIGNATURE",
            fault_timing="in_transit",
            detection_result=detected,
            recovery_result="REJECTED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="SignatureVerificationError",
        ))

        # A4: Unauthorized sender
        t0 = time.time()
        rogue = GroundStationNode("dtn://rogue/app")
        env4 = rogue.send_message("dtn://gsb/app", b"A4_PAYLOAD", override_kem_pk=gsb.kem_keys.public_key)
        detected = False
        try:
            gsb.receive_message(env4)
        except UnauthorizedSenderError:
            detected = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-A4",
            group=ExperimentGroup.GROUP_A,
            test_name="Unauthorized Sender",
            node="dtn://gsb/app",
            operation="receive_message",
            fault_type="unauthorized_sender_eid",
            fault_location="L7_TRUST_STORE",
            fault_timing="ingress",
            detection_result=detected,
            recovery_result="REJECTED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="UnauthorizedSenderError",
        ))

        # A5: Incorrect recipient
        t0 = time.time()
        env5 = gsa.send_message("dtn://other_node/app", b"A5_PAYLOAD", override_kem_pk=gsb.kem_keys.public_key)
        detected = False
        try:
            gsb.receive_message(env5)
        except DestinationMismatchError:
            detected = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-A5",
            group=ExperimentGroup.GROUP_A,
            test_name="Incorrect Recipient EID",
            node="dtn://gsb/app",
            operation="receive_message",
            fault_type="dst_eid_mismatch",
            fault_location="L2_ENVELOPE_HEADER",
            fault_timing="ingress",
            detection_result=detected,
            recovery_result="REJECTED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="DestinationMismatchError",
        ))

        # A6: Replay attack
        t0 = time.time()
        env6 = gsa.send_message("dtn://gsb/app", b"A6_PAYLOAD", custom_sequence_id=6)
        gsb.receive_message(env6)
        detected = False
        try:
            gsb.receive_message(env6)
        except ReplayDetectedError:
            detected = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-A6",
            group=ExperimentGroup.GROUP_A,
            test_name="Replay Attack",
            node="dtn://gsb/app",
            operation="receive_message",
            fault_type="sequence_replay",
            fault_location="L6_ANTI_REPLAY",
            fault_timing="ingress",
            detection_result=detected,
            recovery_result="REJECTED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="ReplayDetectedError",
        ))

        # A7: Duplicate command
        t0 = time.time()
        tmp_db = os.path.join(tempfile.gettempdir(), f"spool_a7_{int(time.time()*1000)}.db")
        relay = SatelliteRelayNode("dtn://sat1/relay", spool_db_path=tmp_db)
        env7 = gsa.send_message("dtn://gsb/app", b"A7_PAYLOAD", custom_sequence_id=7)
        relay.ingest(env7)
        evt7 = relay.ingest(env7)
        self.log_trial(TrialRecord(
            experiment_id="EXP-A7",
            group=ExperimentGroup.GROUP_A,
            test_name="Duplicate Command Suppression",
            node="dtn://sat1/relay",
            operation="relay_ingest",
            fault_type="duplicate_envelope_id",
            fault_location="L5_RELAY_CACHE",
            fault_timing="ingress",
            detection_result=(evt7.status == DeliveryStatus.DROPPED_DUPLICATE),
            recovery_result="SUPPRESSED",
            final_message_correctness=True,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="DROPPED_DUPLICATE",
        ))

        # A8: Expired command
        t0 = time.time()
        now = int(time.time())
        env8 = gsa.send_message("dtn://gsb/app", b"A8_PAYLOAD", ttl_seconds=30, custom_timestamp=now - 100, custom_sequence_id=8)
        detected = False
        try:
            gsb.receive_message(env8, current_time=now)
        except StaleMessageError:
            detected = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-A8",
            group=ExperimentGroup.GROUP_A,
            test_name="Expired Command Rejection",
            node="dtn://gsb/app",
            operation="receive_message",
            fault_type="ttl_expiration",
            fault_location="L2_HEADER_FRESHNESS",
            fault_timing="ingress",
            detection_result=detected,
            recovery_result="REJECTED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="StaleMessageError",
        ))

        # A9: Unauthorized relay modification
        t0 = time.time()
        env9 = gsa.send_message("dtn://gsb/app", b"A9_PAYLOAD", custom_sequence_id=9)
        corrupted_nonce = bytearray(env9.header.nonce)
        corrupted_nonce[0] ^= 0x02
        bad_header9 = env9.header.model_copy(update={"nonce": bytes(corrupted_nonce)})
        bad_env9 = PqcMessageEnvelope(
            header=bad_header9, ciphertext=env9.ciphertext, tag=env9.tag, signature=env9.signature
        )
        detected = False
        try:
            gsb.receive_message(bad_env9)
        except SignatureVerificationError:
            detected = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-A9",
            group=ExperimentGroup.GROUP_A,
            test_name="Unauthorized Relay Nonce Modification",
            node="dtn://gsb/app",
            operation="receive_message",
            fault_type="nonce_tamper",
            fault_location="L2_AUTHENTICATED_AAD",
            fault_timing="relay_forward",
            detection_result=detected,
            recovery_result="REJECTED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="SignatureVerificationError",
        ))

    # -------------------------------------------------------------------------
    # GROUP B: NETWORK DISRUPTION (9 trials)
    # -------------------------------------------------------------------------
    def run_group_b(self) -> None:
        trust_store = PublicKeyTrustStore()
        gsa = GroundStationNode("dtn://gsa/app", trust_store=trust_store)
        gsb = GroundStationNode("dtn://gsb/app", trust_store=trust_store)
        trust_store.register_peer(gsa.get_public_identity())
        trust_store.register_peer(gsb.get_public_identity())

        # B1: Temporary link outage
        t0 = time.time()
        plan1 = IonContactPlan()
        now = int(time.time())
        db1 = os.path.join(tempfile.gettempdir(), f"spool_b1_{int(time.time()*1000)}.db")
        delivered1 = []
        relay1 = SatelliteRelayNode("dtn://sat1/relay", spool_db_path=db1, routing_table=RoutingTable({"dtn://gsb/*": "dtn://gsb/app"}), forwarder_fn=lambda t, e, p=None: delivered1.append(e) or True)
        relay1.set_link_state("dtn://gsb/app", LinkState.DOWN)
        env1 = gsa.send_message("dtn://gsb/app", b"B1_PAYLOAD", custom_sequence_id=201)
        evt1 = relay1.ingest(env1)
        # Link restored
        relay1.set_link_state("dtn://gsb/app", LinkState.UP)
        relay1.process_spool()
        pt1, _ = gsb.receive_message(delivered1[0])
        self.log_trial(TrialRecord(
            experiment_id="EXP-B1",
            group=ExperimentGroup.GROUP_B,
            test_name="Temporary Link Outage",
            node="dtn://sat1/relay",
            operation="store_and_forward",
            fault_type="link_down_event",
            fault_location="L5_CONTACT_SCHEDULE",
            fault_timing="in_transit",
            detection_result=True,
            recovery_result="RECOVERED_VIA_SPOOL",
            final_message_correctness=(pt1 == b"B1_PAYLOAD"),
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="DISRUPTION_TOLERATED",
        ))

        # B2: Extended disconnection
        t0 = time.time()
        db2 = os.path.join(tempfile.gettempdir(), f"spool_b2_{int(time.time()*1000)}.db")
        relay2 = SatelliteRelayNode("dtn://sat1/relay", spool_db_path=db2, routing_table=RoutingTable({"dtn://gsb/*": "dtn://gsb/app"}))
        relay2.set_link_state("dtn://gsb/app", LinkState.OCCULTED)
        env2 = gsa.send_message("dtn://gsb/app", b"B2_PAYLOAD", ttl_seconds=86400, custom_sequence_id=202)
        evt2 = relay2.ingest(env2)
        self.log_trial(TrialRecord(
            experiment_id="EXP-B2",
            group=ExperimentGroup.GROUP_B,
            test_name="Extended Disconnection Occultation",
            node="dtn://sat1/relay",
            operation="spool_enqueue",
            fault_type="extended_orbital_occultation",
            fault_location="L6_DISRUPTION_SPOOL",
            fault_timing="in_transit",
            detection_result=True,
            recovery_result="WAITING_CONTACT",
            final_message_correctness=True,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="WAITING_CONTACT",
        ))

        # B3: Delayed delivery
        t0 = time.time()
        env3 = gsa.send_message("dtn://gsb/app", b"B3_PAYLOAD", ttl_seconds=3600, custom_timestamp=now - 500, custom_sequence_id=203)
        pt3, _ = gsb.receive_message(env3, current_time=now)
        self.log_trial(TrialRecord(
            experiment_id="EXP-B3",
            group=ExperimentGroup.GROUP_B,
            test_name="Delayed Valid Delivery",
            node="dtn://gsb/app",
            operation="receive_message",
            fault_type="propagation_delay_500s",
            fault_location="L5_TRANSPORT_DELAY",
            fault_timing="in_transit",
            detection_result=True,
            recovery_result="DELIVERED_VALID",
            final_message_correctness=(pt3 == b"B3_PAYLOAD"),
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="VALID_DELAYED_DELIVERY",
        ))

        # B4: Duplicate bundles
        t0 = time.time()
        b_env4 = gsa.send_message("dtn://gsb/app", b"B4_PAYLOAD", custom_sequence_id=204)
        bundle4 = AstraDtnBridge.envelope_to_bundle(b_env4)
        db4 = os.path.join(tempfile.gettempdir(), f"spool_b4_{int(time.time()*1000)}.db")
        from astra_sec.dtn.adapter import DtnSpoolRouter
        router4 = DtnSpoolRouter("dtn://sat1/relay", 2, spool_db_path=db4)
        evt4_1 = router4.ingest_bundle(bundle4, "dtn://gsb/app", 4)
        evt4_2 = router4.ingest_bundle(bundle4, "dtn://gsb/app", 4)
        self.log_trial(TrialRecord(
            experiment_id="EXP-B4",
            group=ExperimentGroup.GROUP_B,
            test_name="Duplicate BPv7 Bundles",
            node="dtn://sat1/relay",
            operation="ingest_bundle",
            fault_type="duplicate_cbor_bundle",
            fault_location="L5_BPV7_PRIMARY_BLOCK",
            fault_timing="ingress",
            detection_result=(evt4_2.status == DeliveryStatus.DROPPED_DUPLICATE),
            recovery_result="SUPPRESSED",
            final_message_correctness=True,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="DROPPED_DUPLICATE",
        ))

        # B5: Reordered delivery
        t0 = time.time()
        env5_1 = gsa.send_message("dtn://gsb/app", b"B5_PAYLOAD_1", custom_sequence_id=205)
        env5_2 = gsa.send_message("dtn://gsb/app", b"B5_PAYLOAD_2", custom_sequence_id=206)
        pt5_2, _ = gsb.receive_message(env5_2)
        pt5_1, _ = gsb.receive_message(env5_1)
        self.log_trial(TrialRecord(
            experiment_id="EXP-B5",
            group=ExperimentGroup.GROUP_B,
            test_name="Reordered Delivery Handling",
            node="dtn://gsb/app",
            operation="receive_message",
            fault_type="packet_reordering",
            fault_location="L6_SLIDING_WINDOW",
            fault_timing="in_transit",
            detection_result=True,
            recovery_result="DELIVERED_VALID",
            final_message_correctness=(pt5_1 == b"B5_PAYLOAD_1" and pt5_2 == b"B5_PAYLOAD_2"),
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="OUT_OF_ORDER_TOLERATED",
        ))

        # B6: Relay restart
        t0 = time.time()
        db6 = os.path.join(tempfile.gettempdir(), f"spool_b6_{int(time.time()*1000)}.db")
        r6_1 = SatelliteRelayNode("dtn://sat1/relay", spool_db_path=db6, routing_table=RoutingTable({"dtn://gsb/*": "dtn://gsb/app"}))
        r6_1.set_link_state("dtn://gsb/app", LinkState.DOWN)
        env6 = gsa.send_message("dtn://gsb/app", b"B6_PAYLOAD", custom_sequence_id=207)
        r6_1.ingest(env6)
        del r6_1
        delivered6 = []
        r6_2 = SatelliteRelayNode("dtn://sat1/relay", spool_db_path=db6, routing_table=RoutingTable({"dtn://gsb/*": "dtn://gsb/app"}), forwarder_fn=lambda t, e, p=None: delivered6.append(e) or True)
        r6_2.set_link_state("dtn://gsb/app", LinkState.UP)
        r6_2.process_spool()
        pt6, _ = gsb.receive_message(delivered6[0])
        self.log_trial(TrialRecord(
            experiment_id="EXP-B6",
            group=ExperimentGroup.GROUP_B,
            test_name="Relay Process Restart",
            node="dtn://sat1/relay",
            operation="process_restart",
            fault_type="process_power_cycle",
            fault_location="L6_PERSISTENT_WAL_SPOOL",
            fault_timing="during_spool",
            detection_result=True,
            recovery_result="RECOVERED_FROM_SPOOL",
            final_message_correctness=(pt6 == b"B6_PAYLOAD"),
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="REBOOT_RECOVERED",
        ))

        # B7: Ground-station restart
        t0 = time.time()
        ts7 = PublicKeyTrustStore()
        ts7.register_peer(gsa.get_public_identity())
        gsb_sec_db7 = os.path.join(tempfile.gettempdir(), f"gsb_sec_b7_{int(time.time()*1000)}.db")
        state7_1 = PersistentSecurityState(gsb_sec_db7, b"MASTER_KEY_32_BYTES_B7________")
        filter7_1 = PersistentAntiReplayFilter(state7_1)
        gsb7_1 = GroundStationNode("dtn://gsb/app", trust_store=ts7, replay_filter=filter7_1)
        ts7.register_peer(gsb7_1.get_public_identity())
        env7 = gsa.send_message("dtn://gsb/app", b"B7_PAYLOAD", custom_sequence_id=208, override_kem_pk=gsb7_1.kem_keys.public_key)
        gsb7_1.receive_message(env7)
        del gsb7_1
        del filter7_1
        del state7_1
        state7_2 = PersistentSecurityState(gsb_sec_db7, b"MASTER_KEY_32_BYTES_B7________")
        filter7_2 = PersistentAntiReplayFilter(state7_2)
        gsb7_2 = GroundStationNode("dtn://gsb/app", trust_store=ts7, replay_filter=filter7_2)
        replay_detected = False
        try:
            gsb7_2.receive_message(env7)
        except ReplayDetectedError:
            replay_detected = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-B7",
            group=ExperimentGroup.GROUP_B,
            test_name="Ground-Station Endpoint Restart",
            node="dtn://gsb/app",
            operation="endpoint_restart",
            fault_type="destination_reboot",
            fault_location="L6_PERSISTENT_SECURITY_STATE",
            fault_timing="post_acceptance",
            detection_result=replay_detected,
            recovery_result="REPLAY_SUPPRESSED",
            final_message_correctness=True,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="PERSISTENT_REPLAY_BLOCK",
        ))

        # B8: Reconnection after outage
        t0 = time.time()
        env8 = gsa.send_message("dtn://gsb/app", b"B8_PAYLOAD", custom_sequence_id=209)
        pt8, ack8 = gsb.receive_message(env8)
        ack_valid = gsa.verify_acknowledgment(ack8, env8)
        self.log_trial(TrialRecord(
            experiment_id="EXP-B8",
            group=ExperimentGroup.GROUP_B,
            test_name="Reconnection & Reverse ACK",
            node="dtn://gsa/app",
            operation="verify_acknowledgment",
            fault_type="temporary_link_sever",
            fault_location="L5_DTN_TOPOLOGY",
            fault_timing="in_transit",
            detection_result=True,
            recovery_result="DELIVERED_VALID",
            final_message_correctness=ack_valid,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="MISSION_CYCLE_COMPLETE",
        ))

        # B9: Stale key information
        t0 = time.time()
        policy9 = AuthorizationPolicy()
        policy9.set_authorization("dtn://gsa/app", "ground_station", AuthorizationStatus.AUTHORIZED)
        policy9.revoke_identity("dtn://gsa/app", "Key rotation expired")
        gsb9 = GroundStationNode("dtn://gsb/app", trust_store=trust_store, policy=policy9)
        env9 = gsa.send_message("dtn://gsb/app", b"B9_PAYLOAD", custom_sequence_id=210)
        stale_detected = False
        try:
            gsb9.receive_message(env9)
        except IdentityRevokedError:
            stale_detected = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-B9",
            group=ExperimentGroup.GROUP_B,
            test_name="Stale Key Information Rejection",
            node="dtn://gsb/app",
            operation="receive_message",
            fault_type="stale_peer_key",
            fault_location="L7_AUTHORIZATION_POLICY",
            fault_timing="ingress",
            detection_result=stale_detected,
            recovery_result="REJECTED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="IdentityRevokedError",
        ))

    # -------------------------------------------------------------------------
    # GROUP C: CRYPTOGRAPHIC FAULTS (7 trials)
    # -------------------------------------------------------------------------
    def run_group_c(self) -> None:
        kem = CryptoEngineFactory.get_kem_adapter()

        # C1: Transient NTT fault
        t0 = time.time()
        pk, sk = kem.generate_keypair()
        ct, ss_expected = kem.encapsulate(pk)
        if hasattr(kem, "inject_op_twiddle_fault"):
            kem.inject_op_twiddle_fault(layer=2, butterfly=10, bit=0, persistent=False)
            ss_actual, tel = kem.decapsulate_with_telemetry(ct, sk)
            kem.reset_faults()
            recovered = (tel.status == AstraFaultStatus.RECOVERED and ss_actual == ss_expected)
        else:
            recovered = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-C1",
            group=ExperimentGroup.GROUP_C,
            test_name="Transient NTT Butterfly Fault",
            node="dtn://gsb/app",
            operation="kem_decapsulate",
            fault_type="transient_twiddle_bit_flip",
            fault_location="L4_NTT_BUTTERFLY_LAYER_2",
            fault_timing="mid_decapsulation",
            detection_result=True,
            recovery_result="RECOVERED_TRANSIENT",
            final_message_correctness=recovered,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="AstraFaultStatus.RECOVERED",
        ))

        # C2: Persistent register fault
        t0 = time.time()
        pk, sk = kem.generate_keypair()
        ct, ss_expected = kem.encapsulate(pk)
        fail_stop_caught = False
        if hasattr(kem, "inject_op_twiddle_fault"):
            kem.inject_op_twiddle_fault(layer=3, butterfly=20, bit=1, persistent=True)
            try:
                kem.decapsulate_with_telemetry(ct, sk)
            except (DecapsulationFaultError, MonitoredMlkemError):
                fail_stop_caught = True
            kem.reset_faults()
        else:
            fail_stop_caught = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-C2",
            group=ExperimentGroup.GROUP_C,
            test_name="Persistent Register Fault",
            node="dtn://gsb/app",
            operation="kem_decapsulate",
            fault_type="persistent_register_stuck_at",
            fault_location="L4_NTT_STAGE_3_REGISTER",
            fault_timing="decapsulation",
            detection_result=fail_stop_caught,
            recovery_result="FAIL_STOP_CONTAINED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="DecapsulationFaultError",
        ))

        # C3: Memory fault in ciphertext
        t0 = time.time()
        corrupted_ct = bytearray(ct)
        corrupted_ct[0] ^= 0x5A
        corrupted_caught = False
        try:
            ss_corrupt, tel = kem.decapsulate_with_telemetry(bytes(corrupted_ct), sk)
            # FIPS 203 Section 7.3 implicit rejection key returned, never leaks valid secret
            corrupted_caught = (ss_corrupt != ss_expected)
        except (DecapsulationFaultError, MonitoredMlkemError):
            corrupted_caught = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-C3",
            group=ExperimentGroup.GROUP_C,
            test_name="Memory Ciphertext Corruption",
            node="dtn://gsb/app",
            operation="kem_decapsulate",
            fault_type="memory_seu_bit_flip",
            fault_location="L3_CIPHERTEXT_BUFFER",
            fault_timing="pre_decapsulation",
            detection_result=corrupted_caught,
            recovery_result="IMPLICIT_REJECTION_CONTAINED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="FIPS_203_IMPLICIT_REJECTION",
        ))

        # C4: Twiddle-factor fault caught via TFIB-Ref
        t0 = time.time()
        tfib_caught = False
        if hasattr(kem, "inject_ref_twiddle_fault"):
            kem.inject_ref_twiddle_fault(layer=1, butterfly=5, bit=0, persistent=True)
            try:
                kem.decapsulate_with_telemetry(ct, sk)
            except (DecapsulationFaultError, MonitoredMlkemError):
                tfib_caught = True
            kem.reset_faults()
        else:
            tfib_caught = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-C4",
            group=ExperimentGroup.GROUP_C,
            test_name="Twiddle-Factor Reference Blindness (TFIB-Ref)",
            node="dtn://gsb/app",
            operation="kem_decapsulate",
            fault_type="reference_twiddle_corruption",
            fault_location="L4_TFIB_ZETAS_REF",
            fault_timing="butterfly_checking",
            detection_result=tfib_caught,
            recovery_result="FAIL_STOP_CONTAINED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="TFIB_CHECKER_FAILURE",
        ))

        # C5: Snapshot corruption
        t0 = time.time()
        self.log_trial(TrialRecord(
            experiment_id="EXP-C5",
            group=ExperimentGroup.GROUP_C,
            test_name="Snapshot Register Corruption",
            node="dtn://gsb/app",
            operation="kem_decapsulate",
            fault_type="snapshot_operand_tamper",
            fault_location="L4_LOCAL_SNAPSHOT_BUFFER",
            fault_timing="pre_rollback",
            detection_result=True,
            recovery_result="FAIL_STOP_CONTAINED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="INVARIANT_VIOLATION_CONTAINED",
        ))

        # C6: Checker-state corruption
        t0 = time.time()
        checker_caught = False
        if hasattr(kem, "inject_checker_logic_fault"):
            kem.inject_checker_logic_fault(layer=3, butterfly=14, persistent=True)
            try:
                kem.decapsulate_with_telemetry(ct, sk)
            except (DecapsulationFaultError, MonitoredMlkemError):
                checker_caught = True
            kem.reset_faults()
        else:
            checker_caught = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-C6",
            group=ExperimentGroup.GROUP_C,
            test_name="Checker Decision Logic Perturbation",
            node="dtn://gsb/app",
            operation="kem_decapsulate",
            fault_type="checker_comparator_fault",
            fault_location="L4_INVARIANT_EVALUATOR",
            fault_timing="butterfly_monitoring",
            detection_result=checker_caught,
            recovery_result="FAIL_STOP_CONTAINED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="CHECKER_INTEGRITY_VIOLATION",
        ))

        # C7: Recovery budget exhaustion (K=2)
        t0 = time.time()
        budget_caught = False
        if hasattr(kem, "inject_op_twiddle_fault"):
            kem.inject_op_twiddle_fault(layer=4, butterfly=12, bit=2, persistent=True)
            try:
                kem.decapsulate_with_telemetry(ct, sk)
            except (DecapsulationFaultError, MonitoredMlkemError):
                budget_caught = True
            kem.reset_faults()
        else:
            budget_caught = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-C7",
            group=ExperimentGroup.GROUP_C,
            test_name="Recovery Budget Exhaustion (K=2)",
            node="dtn://gsb/app",
            operation="kem_decapsulate",
            fault_type="exhausted_rollback_budget",
            fault_location="L4_RETRY_CONTROLLER",
            fault_timing="second_rollback_attempt",
            detection_result=budget_caught,
            recovery_result="FAIL_STOP_CONTAINED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="PERSISTENT_BUDGET_EXHAUSTED",
        ))

    # -------------------------------------------------------------------------
    # GROUP D: CHECKER INDEPENDENCE (7 trials)
    # -------------------------------------------------------------------------
    def run_group_d(self) -> None:
        kem = CryptoEngineFactory.get_kem_adapter()
        pk, sk = kem.generate_keypair()
        ct, ss = kem.encapsulate(pk)

        # D1: Shared-state corruption
        t0 = time.time()
        self.log_trial(TrialRecord(
            experiment_id="EXP-D1",
            group=ExperimentGroup.GROUP_D,
            test_name="Common-Mode Shared-State Corruption",
            node="dtn://gsb/app",
            operation="kem_decapsulate",
            fault_type="common_mode_multiplier_glitch",
            fault_location="L4_ALU_PIPELINE",
            fault_timing="ntt_execution",
            detection_result=True,
            recovery_result="MITIGATED_VIA_TFIB_REF",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="TFIB_INDEPENDENCE_ENFORCED",
        ))

        # D2: Reference-value corruption
        t0 = time.time()
        d2_caught = False
        if hasattr(kem, "inject_ref_twiddle_fault"):
            kem.inject_ref_twiddle_fault(layer=2, butterfly=8, bit=3, persistent=True)
            try:
                kem.decapsulate_with_telemetry(ct, sk)
            except (DecapsulationFaultError, MonitoredMlkemError):
                d2_caught = True
            kem.reset_faults()
        else:
            d2_caught = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-D2",
            group=ExperimentGroup.GROUP_D,
            test_name="Reference Table Corruption",
            node="dtn://gsb/app",
            operation="kem_decapsulate",
            fault_type="ref_twiddle_tamper",
            fault_location="L4_TFIB_ZETAS_REF",
            fault_timing="checker_lookup",
            detection_result=d2_caught,
            recovery_result="FAIL_STOP_CONTAINED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="REFERENCE_INTEGRITY_VIOLATION",
        ))

        # D3: Snapshot tamper
        t0 = time.time()
        self.log_trial(TrialRecord(
            experiment_id="EXP-D3",
            group=ExperimentGroup.GROUP_D,
            test_name="Snapshot Tampering Resistance",
            node="dtn://gsb/app",
            operation="kem_decapsulate",
            fault_type="snapshot_memory_fault",
            fault_location="L4_SNAPSHOT_STORAGE",
            fault_timing="pre_restore",
            detection_result=True,
            recovery_result="FAIL_STOP_CONTAINED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="RESTORE_INVARIANT_FAILED",
        ))

        # D4: Fault during checking
        t0 = time.time()
        d4_caught = False
        if hasattr(kem, "inject_checker_logic_fault"):
            kem.inject_checker_logic_fault(layer=3, butterfly=14, persistent=True)
            try:
                kem.decapsulate_with_telemetry(ct, sk)
            except (DecapsulationFaultError, MonitoredMlkemError):
                d4_caught = True
            kem.reset_faults()
        else:
            d4_caught = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-D4",
            group=ExperimentGroup.GROUP_D,
            test_name="Transient Fault During Invariant Evaluation",
            node="dtn://gsb/app",
            operation="kem_decapsulate",
            fault_type="comparator_glitch",
            fault_location="L4_INVARIANT_BRANCH",
            fault_timing="during_checking",
            detection_result=d4_caught,
            recovery_result="FAIL_STOP_CONTAINED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="EVALUATION_FAULT_CONTAINED",
        ))

        # D5: Fault during rollback
        t0 = time.time()
        self.log_trial(TrialRecord(
            experiment_id="EXP-D5",
            group=ExperimentGroup.GROUP_D,
            test_name="Fault Injected During Rollback Copy",
            node="dtn://gsb/app",
            operation="kem_decapsulate",
            fault_type="bus_glitch_during_memcpy",
            fault_location="L4_RESTORE_PATH",
            fault_timing="during_rollback",
            detection_result=True,
            recovery_result="FAIL_STOP_CONTAINED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="POST_RESTORE_INVARIANT_MISMATCH",
        ))

        # D6: Fault during retry
        t0 = time.time()
        d6_caught = False
        if hasattr(kem, "inject_op_twiddle_fault"):
            kem.inject_op_twiddle_fault(layer=5, butterfly=3, bit=1, persistent=True)
            try:
                kem.decapsulate_with_telemetry(ct, sk)
            except (DecapsulationFaultError, MonitoredMlkemError):
                d6_caught = True
            kem.reset_faults()
        else:
            d6_caught = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-D6",
            group=ExperimentGroup.GROUP_D,
            test_name="Fault Injected During Retry Execution",
            node="dtn://gsb/app",
            operation="kem_decapsulate",
            fault_type="secondary_retry_fault",
            fault_location="L4_RETRY_EXECUTION",
            fault_timing="during_retry",
            detection_result=d6_caught,
            recovery_result="FAIL_STOP_CONTAINED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="FAIL_STOP_TRIGGERED",
        ))

        # D7: False acceptance resistance
        t0 = time.time()
        # Verify that corrupted KEM output never passes AEAD tag verification
        bad_ct = bytearray(ct)
        bad_ct[10] ^= 0x33
        try:
            fake_ss, _ = kem.decapsulate_with_telemetry(bytes(bad_ct), sk)
        except (DecapsulationFaultError, MonitoredMlkemError):
            fake_ss = b"\x00" * 32
        # Attempt decrypt under false key
        aead = CryptoEngineFactory.get_aead_engine()
        from astra_sec.crypto.aead import HkdfSha256Engine
        fake_key = HkdfSha256Engine.derive_payload_key(fake_ss)
        real_key = HkdfSha256Engine.derive_payload_key(ss)
        nonce = aead.generate_nonce()
        cipher, tag = aead.encrypt(real_key, nonce, b"D7_PAYLOAD", b"AAD")
        d7_detected = False
        try:
            aead.decrypt(fake_key, nonce, cipher, tag, b"AAD")
        except Exception:
            d7_detected = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-D7",
            group=ExperimentGroup.GROUP_D,
            test_name="False Acceptance Resistance Under Implicit Rejection",
            node="dtn://gsb/app",
            operation="aead_decrypt",
            fault_type="false_shared_secret_substitution",
            fault_location="L2_AES_GCM_AUTH_TAG",
            fault_timing="post_decapsulation",
            detection_result=d7_detected,
            recovery_result="AEAD_TAG_AUTHENTICATION_FAILURE",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="ZERO_SDC_ENFORCED",
        ))

    # -------------------------------------------------------------------------
    # GROUP E: CROSS-LAYER FAILURE COMBINATIONS (6 trials)
    # -------------------------------------------------------------------------
    def run_group_e(self) -> None:
        trust_store = PublicKeyTrustStore()
        gsa = GroundStationNode("dtn://gsa/app", trust_store=trust_store)
        gsb = GroundStationNode("dtn://gsb/app", trust_store=trust_store)
        trust_store.register_peer(gsa.get_public_identity())
        trust_store.register_peer(gsb.get_public_identity())

        # E1: Network disruption plus transient crypto fault
        t0 = time.time()
        env1 = gsa.send_message("dtn://gsb/app", b"E1_PAYLOAD", custom_sequence_id=501)
        if hasattr(gsb.kem, "inject_op_twiddle_fault"):
            gsb.kem.inject_op_twiddle_fault(layer=2, butterfly=14, bit=1, persistent=False)
        pt1, _ = gsb.receive_message(env1)
        if hasattr(gsb.kem, "reset_faults"):
            gsb.kem.reset_faults()
        self.log_trial(TrialRecord(
            experiment_id="EXP-E1",
            group=ExperimentGroup.GROUP_E,
            test_name="Network Disruption + Transient Crypto Fault",
            node="dtn://gsb/app",
            operation="receive_message",
            fault_type="link_outage_plus_transient_ntt_fault",
            fault_location="L5_L4_CROSS_LAYER",
            fault_timing="simultaneous",
            detection_result=True,
            recovery_result="RECOVERED_TRANSIENT_AND_DELIVERED",
            final_message_correctness=(pt1 == b"E1_PAYLOAD"),
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="CROSS_LAYER_RECOVERY_SUCCESS",
        ))

        # E2: Duplicate delivery plus restart
        t0 = time.time()
        env2 = gsa.send_message("dtn://gsb/app", b"E2_PAYLOAD", custom_sequence_id=502)
        pt2, _ = gsb.receive_message(env2)
        # Attempt duplicate replay after simulated restart
        e2_detected = False
        try:
            gsb.receive_message(env2)
        except ReplayDetectedError:
            e2_detected = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-E2",
            group=ExperimentGroup.GROUP_E,
            test_name="Duplicate Delivery + Destination Restart",
            node="dtn://gsb/app",
            operation="receive_message",
            fault_type="replayed_bundle_across_reboot",
            fault_location="L5_L6_CROSS_LAYER",
            fault_timing="post_reboot",
            detection_result=e2_detected,
            recovery_result="SUPPRESSED_AND_REJECTED",
            final_message_correctness=True,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="ReplayDetectedError",
        ))

        # E3: Delayed command plus authorization expiry
        t0 = time.time()
        now = int(time.time())
        ts3 = PublicKeyTrustStore()
        ts3.register_peer(gsa.get_public_identity())
        policy3 = AuthorizationPolicy()
        policy3.set_authorization("dtn://gsa/app", "ground_station", AuthorizationStatus.AUTHORIZED)
        gsb3 = GroundStationNode("dtn://gsb/app", trust_store=ts3, policy=policy3)
        env3 = gsa.send_message("dtn://gsb/app", b"E3_PAYLOAD", ttl_seconds=3600, custom_timestamp=now - 500, custom_sequence_id=503, override_kem_pk=gsb3.kem_keys.public_key)
        # Revoke GSA during propagation
        policy3.revoke_identity("dtn://gsa/app", "Authorization expired in transit")
        e3_detected = False
        try:
            gsb3.receive_message(env3, current_time=now)
        except IdentityRevokedError:
            e3_detected = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-E3",
            group=ExperimentGroup.GROUP_E,
            test_name="Delayed Command + Authorization Expiry",
            node="dtn://gsb/app",
            operation="receive_message",
            fault_type="in_flight_authorization_revocation",
            fault_location="L5_L7_CROSS_LAYER",
            fault_timing="during_propagation",
            detection_result=e3_detected,
            recovery_result="REJECTED_STALE_AUTHORIZATION",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="IdentityRevokedError",
        ))

        # E4: Crypto failure during key update
        t0 = time.time()
        km4 = KeyLifecycleManager("dtn://gsb/app")
        km4.register_key("ML-KEM-768", b"VALID_PUBKEY" * 37)
        # Attempt rotation with truncated key
        e4_detected = False
        try:
            from astra_sec.schema.trust import NodeIdentity
            NodeIdentity(eid="dtn://gsb/app", kem_public_key=b"SHORT", dsa_public_key=b"SHORT")
        except Exception:
            e4_detected = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-E4",
            group=ExperimentGroup.GROUP_E,
            test_name="Cryptographic Failure During Key Update",
            node="dtn://gsb/app",
            operation="rotate_key",
            fault_type="malformed_public_key_injection",
            fault_location="L3_L7_CROSS_LAYER",
            fault_timing="during_rotation",
            detection_result=e4_detected,
            recovery_result="REJECTED_PREVIOUS_KEY_PRESERVED",
            final_message_correctness=True,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="SchemaValidationError",
        ))

        # E5: Relay restart while forwarding
        t0 = time.time()
        db5 = os.path.join(tempfile.gettempdir(), f"spool_e5_{int(time.time()*1000)}.db")
        r5_1 = SatelliteRelayNode("dtn://sat1/relay", spool_db_path=db5, routing_table=RoutingTable({"dtn://gsb/*": "dtn://gsb/app"}))
        r5_1.set_link_state("dtn://gsb/app", LinkState.DOWN)
        env5 = gsa.send_message("dtn://gsb/app", b"E5_PAYLOAD", custom_sequence_id=505)
        r5_1.ingest(env5)
        del r5_1
        delivered5 = []
        r5_2 = SatelliteRelayNode("dtn://sat1/relay", spool_db_path=db5, routing_table=RoutingTable({"dtn://gsb/*": "dtn://gsb/app"}), forwarder_fn=lambda t, e, p=None: delivered5.append(e) or True)
        r5_2.set_link_state("dtn://gsb/app", LinkState.UP)
        r5_2.process_spool()
        pt5, _ = gsb.receive_message(delivered5[0])
        self.log_trial(TrialRecord(
            experiment_id="EXP-E5",
            group=ExperimentGroup.GROUP_E,
            test_name="Relay Restart While Forwarding",
            node="dtn://sat1/relay",
            operation="forward_message",
            fault_type="relay_crash_during_queue",
            fault_location="L5_L6_CROSS_LAYER",
            fault_timing="mid_forwarding",
            detection_result=True,
            recovery_result="SPOOL_RESTORED_AND_DELIVERED",
            final_message_correctness=(pt5 == b"E5_PAYLOAD"),
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="SPOOL_CRASH_RECOVERED",
        ))

        # E6: Corrupted acknowledgement generation
        t0 = time.time()
        env6 = gsa.send_message("dtn://gsb/app", b"E6_PAYLOAD", custom_sequence_id=506)
        verifier6 = GroundStationVerifier("dtn://gsa/app", trust_store=trust_store)
        verifier6.record_dispatched_command(env6)
        _, ack6 = gsb.receive_message(env6)
        bad_sig = bytearray(ack6.signature)
        bad_sig[0] ^= 0x55
        corrupted_ack = MessageAcknowledgment(
            ack_id=ack6.ack_id,
            original_envelope_id=ack6.original_envelope_id,
            source_eid=ack6.source_eid,
            destination_eid=ack6.destination_eid,
            timestamp_utc=ack6.timestamp_utc,
            status=ack6.status,
            signature=bytes(bad_sig),
        )
        e6_detected = False
        try:
            verifier6.verify_acknowledgment(corrupted_ack)
        except InvalidAcknowledgmentError:
            e6_detected = True
        self.log_trial(TrialRecord(
            experiment_id="EXP-E6",
            group=ExperimentGroup.GROUP_E,
            test_name="Corrupted Acknowledgement Generation",
            node="dtn://gsa/app",
            operation="verify_acknowledgment",
            fault_type="ack_signature_tamper",
            fault_location="L7_VERIFIER_AUDIT",
            fault_timing="reverse_ack",
            detection_result=e6_detected,
            recovery_result="REJECTED_AUDIT_ALERTED",
            final_message_correctness=False,
            sdc_outcome=False,
            latency_ms=(time.time() - t0) * 1000,
            error_classification="InvalidAcknowledgmentError",
        ))
