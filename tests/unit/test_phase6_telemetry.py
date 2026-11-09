"""ASTRA-Sec: Phase 6 Live Telemetry Engineering & Security Observability Tests.

Verifies all Phase 6 acceptance criteria:
1. Forensic reconciliation of Discrepancies A, B, C, D.
2. Unified Pydantic v2 telemetry event schema with nanosecond precision.
3. Thread-safe non-blocking telemetry engine with correlation indexing.
4. Cryptographic measurements for ML-KEM-768, HKDF-SHA256, ML-DSA-65, AES-256-GCM.
5. NTT invariant monitoring reflecting native C engine 9,856 butterflies.
6. Detailed DTN queue and SQLite WAL storage telemetry.
7. Per-hop physical network metrics.
8. System health multi-dimensional decomposition.
9. Zero leakage of private keys, shared secrets, or plaintexts.
10. Telemetry REST and WebSocket endpoints.
11. Telemetry instrumentation overhead benchmarking (< 1%).
"""

import json
import os
import shutil
import tempfile
import time
import unittest

from fastapi.testclient import TestClient

from astra_sec.core.telemetry_engine import TelemetryEngine
from astra_sec.dashboard.app import app
from astra_sec.network.spool import PersistentMessageSpool
from astra_sec.schema.envelope import EnvelopeHeader, PqcMessageEnvelope
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
from astra_sec.service.telemetry_benchmark import measure_instrumentation_overhead


class TestPhase6Telemetry(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_log_file = os.path.join(self.temp_dir, "test_events.jsonl")
        self.client = TestClient(app)
        self.admin_headers = {"x-admin-token": "astra-mission-control-token"}

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_telemetry_event_schema_validation(self):
        """Acceptance Test 1: TelemetryEvent schema validates nanosecond timing & DTN EIDs."""
        event = TelemetryEvent(
            event_type=EventType.CRYPTO_OPERATION,
            timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            monotonic_timestamp_ns=time.perf_counter_ns(),
            component=ComponentLayer.L3_KEM,
            source_node="dtn://gsa/app",
            destination_node="dtn://gsb/app",
            operation="KEM_ENCAPSULATE",
            status="SUCCESS",
            duration_ns=32100,
            correlation_id="test-corr-001",
            metadata={"ciphertext_bytes": 1088},
        )
        self.assertEqual(event.component, ComponentLayer.L3_KEM)
        self.assertEqual(event.duration_ns, 32100)
        self.assertEqual(event.source_node, "dtn://gsa/app")
        self.assertTrue(event.monotonic_timestamp_ns > 0)

    def test_02_measurement_schemas(self):
        """Acceptance Test 2: Fine-grained measurement models validate properly."""
        crypto_meas = CryptographicMeasurement(
            algorithm="ML-KEM-768",
            operation="ENCAPSULATE",
            duration_ns=32150,
            input_bytes_len=1184,
            output_bytes_len=1088,
            status="SUCCESS",
            verified=True,
        )
        self.assertEqual(crypto_meas.duration_ns, 32150)

        ntt_meas = NttInvariantMeasurement(
            butterflies_executed=9856,
            layer_width=128,
            transforms_monitored=11,
            invariant_status="NOMINAL_VERIFIED",
        )
        self.assertEqual(ntt_meas.butterflies_executed, 9856)
        self.assertEqual(ntt_meas.layer_width, 128)
        self.assertEqual(ntt_meas.transforms_monitored, 11)

        dtn_meas = DtnQueueMeasurement(
            relay_eid="dtn://sat1/relay",
            pending_bundles=2,
            persisted_bundles=5,
            database_bytes=24576,
            wal_bytes=8192,
            wal_mode=True,
        )
        self.assertEqual(dtn_meas.database_bytes, 24576)
        self.assertTrue(dtn_meas.wal_mode)

        hop_meas = HopNetworkMeasurement(
            hop_id="HOP_1_UPLINK",
            source_eid="dtn://gsa/app",
            target_eid="dtn://sat1/relay",
            link_state="UP",
            total_transmissions=10,
            failed_transmissions=0,
            last_duration_ms=1.20,
        )
        self.assertEqual(hop_meas.link_state, "UP")

    def test_03_telemetry_engine_ring_buffer_and_correlation(self):
        """Acceptance Test 3: Thread-safe ring buffer and correlation index."""
        engine = TelemetryEngine(max_events=100, log_file=self.test_log_file)
        received_events = []
        engine.add_listener(lambda ev: received_events.append(ev))

        corr_id = "test-corr-alpha"
        e1 = engine.emit_event(
            event_type=EventType.CRYPTO_OPERATION,
            component=ComponentLayer.L3_DSA,
            source_node="dtn://gsa/app",
            operation="DSA_SIGN",
            status="SUCCESS",
            correlation_id=corr_id,
            duration_ns=105000,
        )
        e2 = engine.emit_event(
            event_type=EventType.DTN_STORE_FORWARD,
            component=ComponentLayer.L5_BPV7,
            source_node="dtn://sat1/relay",
            operation="MESSAGE_FORWARDED",
            status="FORWARDED",
            correlation_id=corr_id,
        )

        lifecycle = engine.get_lifecycle_events(corr_id)
        self.assertEqual(len(lifecycle), 2)
        self.assertEqual(lifecycle[0].operation, "DSA_SIGN")
        self.assertEqual(lifecycle[1].operation, "MESSAGE_FORWARDED")
        self.assertEqual(len(received_events), 2)

    def test_04_telemetry_engine_jsonl_logging(self):
        """Acceptance Test 4: Structured non-blocking JSONL logging to disk."""
        engine = TelemetryEngine(max_events=50, log_file=self.test_log_file)
        engine.emit_event(
            event_type=EventType.FAULT_INSPECTION,
            component=ComponentLayer.L4_NTT,
            source_node="dtn://gsb/app",
            operation="NTT_CHECK",
            status="NOMINAL",
            correlation_id="disk-log-test",
            metadata={"butterflies": 9856},
        )
        self.assertTrue(os.path.exists(self.test_log_file))
        with open(self.test_log_file, "r", encoding="utf-8") as f:
            lines = [json.loads(line) for line in f if line.strip()]
        self.assertGreaterEqual(len(lines), 1)
        self.assertEqual(lines[-1]["operation"], "NTT_CHECK")
        self.assertEqual(lines[-1]["metadata"]["butterflies"], 9856)

    def test_05_discrepancy_a_signing_vs_verification(self):
        """Acceptance Test 5: Discrepancy A resolved - signing succeeds 100%, tamper rejects at receiver."""
        # Scenario 1: Nominal dispatch -> Stage 4 COMPLETED, Stage 7 COMPLETED
        res_nom = self.client.post(
            "/api/admin/dispatch",
            json={"payload_text": "NOMINAL_DISCREPANCY_TEST", "scenario": "nominal"},
            headers=self.admin_headers,
        )
        self.assertEqual(res_nom.status_code, 200)
        pipe_nom = res_nom.json()["pipeline"]
        self.assertEqual(pipe_nom["stage4_dsa_signature"]["status"], "COMPLETED")
        self.assertEqual(pipe_nom["stage7_receiver_verification"]["status"], "COMPLETED")

        # Scenario 2: Tamper signature in transit -> Stage 4 COMPLETED (originator cleanly signed!),
        # but Stage 7 REJECTED_SIGNATURE (receiver rejected tampered bytes!)
        res_tamper = self.client.post(
            "/api/admin/dispatch",
            json={"payload_text": "TAMPER_SIG_DISCREPANCY_TEST", "scenario": "tamper_sig"},
            headers=self.admin_headers,
        )
        self.assertEqual(res_tamper.status_code, 200)
        self.assertEqual(res_tamper.json()["status"], "SIGNATURE_TAMPER_REJECTED")
        pipe_tamper = res_tamper.json()["pipeline"]
        self.assertEqual(pipe_tamper["stage4_dsa_signature"]["status"], "COMPLETED")
        self.assertEqual(pipe_tamper["stage7_receiver_verification"]["status"], "REJECTED_SIGNATURE")
        self.assertEqual(pipe_tamper["stage7_receiver_verification"]["signature_verification"], "REJECTED_INVALID_SIG")

    def test_06_discrepancy_b_fips_kat_vs_message_auth(self):
        """Acceptance Test 6: Discrepancy B resolved - KAT conformance is distinct from message authentication."""
        health = self.client.get("/api/telemetry/health").json()
        self.assertEqual(health["fips_conformance_status"], "KAT_VERIFIED")
        self.assertIn("active_envelope_authenticated", health)

        # After a tampered signature message, KAT status remains verified while envelope authentication is False
        self.client.post(
            "/api/admin/dispatch",
            json={"payload_text": "TAMPER_AUTH_CHECK", "scenario": "tamper_sig"},
            headers=self.admin_headers,
        )
        health_after = self.client.get("/api/telemetry/health").json()
        self.assertEqual(health_after["fips_conformance_status"], "KAT_VERIFIED")
        self.assertFalse(health_after["active_envelope_authenticated"])
        self.assertEqual(health_after["last_message_status"], "REJECTED_SIGNATURE")

    def test_07_discrepancy_c_system_health_decomposition(self):
        """Acceptance Test 7: Discrepancy C resolved - multi-dimensional health model."""
        res = self.client.get("/api/telemetry/health")
        self.assertEqual(res.status_code, 200)
        h = res.json()
        self.assertIn("overall_status", h)
        self.assertIn("process_health", h)
        self.assertIn("crypto_subsystem", h)
        self.assertIn("dtn_subsystem", h)
        self.assertIn("link_health", h)
        self.assertIn("last_message_status", h)
        self.assertEqual(h["process_health"], "ONLINE")
        self.assertEqual(h["dtn_subsystem"], "OPERATIONAL")

    def test_08_discrepancy_d_ntt_butterfly_counting(self):
        """Acceptance Test 8: Discrepancy D resolved - genuine 9,856 butterflies executed across 11 transforms."""
        res = self.client.post(
            "/api/admin/dispatch",
            json={"payload_text": "NTT_COUNT_CHECK", "scenario": "nominal"},
            headers=self.admin_headers,
        )
        self.assertEqual(res.status_code, 200)
        ntt = res.json()["ntt"]
        self.assertEqual(ntt["butterflies_executed"], 9856)
        self.assertEqual(ntt["layer_width"], 128)
        self.assertEqual(ntt["transforms_monitored"], 11)
        self.assertEqual(ntt["modulus_q"], 3329)

    def test_09_dtn_sqlite_wal_storage_telemetry(self):
        """Acceptance Test 9: DTN SQLite WAL inspection returns true disk stats."""
        spool_db = os.path.join(self.temp_dir, "test_spool.db")
        spool = PersistentMessageSpool(db_path=spool_db)
        stats = spool.get_detailed_stats()

        self.assertEqual(stats["pending_bundles"], 0)
        self.assertEqual(stats["persisted_bundles"], 0)
        self.assertGreater(stats["database_bytes"], 0)
        self.assertTrue(stats["wal_mode"])

        env = PqcMessageEnvelope(
            header=EnvelopeHeader(
                envelope_id="test-env-001",
                source_eid="dtn://gsa/app",
                destination_eid="dtn://gsb/app",
                sequence_id=1,
                timestamp_utc=int(time.time()),
                ttl_seconds=3600,
                kem_ciphertext=b"\x00" * 1088,
                nonce=b"\x01" * 12,
            ),
            ciphertext=b"CIPHERTEXT",
            tag=b"\x02" * 16,
            signature=b"\x03" * 3309,
        )
        spool.enqueue(env, next_hop_eid="dtn://sat2/relay")
        stats_updated = spool.get_detailed_stats()
        self.assertEqual(stats_updated["pending_bundles"], 1)
        self.assertEqual(stats_updated["persisted_bundles"], 1)
        self.assertIsNotNone(stats_updated["last_inserted_utc"])

    def test_10_rest_dtn_spools_endpoint(self):
        """Acceptance Test 10: GET /api/dtn/spools returns array of detailed queue telemetry."""
        res = self.client.get("/api/dtn/spools")
        self.assertEqual(res.status_code, 200)
        spools = res.json()
        self.assertEqual(len(spools), 2)
        self.assertEqual(spools[0]["relay_eid"], "dtn://sat1/relay")
        self.assertEqual(spools[1]["relay_eid"], "dtn://sat2/relay")
        self.assertTrue(spools[0]["wal_mode"])

    def test_11_rest_telemetry_hops_endpoint(self):
        """Acceptance Test 11: GET /api/telemetry/hops returns 3 hop telemetry records."""
        res = self.client.get("/api/telemetry/hops")
        self.assertEqual(res.status_code, 200)
        hops = res.json()
        self.assertEqual(len(hops), 3)
        self.assertEqual(hops[0]["hop_id"], "HOP_1_UPLINK")
        self.assertEqual(hops[1]["hop_id"], "HOP_2_ISL")
        self.assertEqual(hops[2]["hop_id"], "HOP_3_DOWNLINK")

    def test_12_rest_telemetry_events_query(self):
        """Acceptance Test 12: GET /api/telemetry/events supports filtering."""
        res = self.client.get("/api/telemetry/events?limit=25")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total", data)
        self.assertIn("events", data)

    def test_13_rest_telemetry_lifecycle_trace(self):
        """Acceptance Test 13: GET /api/telemetry/lifecycle/{correlation_id} returns correlated sequence."""
        # Dispatch a message to generate correlated events
        res = self.client.post(
            "/api/admin/dispatch",
            json={"payload_text": "CORRELATION_TEST", "scenario": "nominal"},
            headers=self.admin_headers,
        )
        env_id = res.json()["envelope_id"]

        res_life = self.client.get(f"/api/telemetry/lifecycle/{env_id}")
        self.assertEqual(res_life.status_code, 200)
        life = res_life.json()
        self.assertEqual(life["correlation_id"], env_id)
        self.assertGreaterEqual(life["event_count"], 8)
        self.assertGreater(life["total_measured_latency_us"], 0.0)

        ops = [e["operation"] for e in life["events"]]
        self.assertIn("ADU_CREATE", ops)
        self.assertIn("KEM_ENCAPSULATE", ops)
        self.assertIn("DSA_SIGN", ops)
        self.assertIn("DSA_VERIFY", ops)

    def test_14_rest_experiments_provenance(self):
        """Acceptance Test 14: GET /api/experiments/provenance returns verified manifest records."""
        res = self.client.get("/api/experiments/provenance")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("provenance_records", data)
        self.assertGreaterEqual(len(data["provenance_records"]), 5)
        self.assertEqual(data["fips_compliance"], "FIPS 203 (ML-KEM) & FIPS 204 (ML-DSA) NIST Approved KATs")

    def test_15_instrumentation_overhead_benchmark(self):
        """Acceptance Test 15: Telemetry instrumentation overhead benchmark < 1%."""
        result = measure_instrumentation_overhead(iterations=50)
        self.assertEqual(result["status"], "PASS")
        self.assertIn("mean_baseline_latency_us", result)
        self.assertIn("mean_instrumented_latency_us", result)
        self.assertIn("overhead_pct", result)

    def test_16_zero_secret_leakage(self):
        """Acceptance Test 16: Zero private keys, shared secrets, or plaintexts in telemetry."""
        # Dispatch with distinctive canary string
        canary = "CANARY_SECRET_PAYLOAD_TOP_CONFIDENTIAL_12345"
        res = self.client.post(
            "/api/admin/dispatch",
            json={"payload_text": canary, "scenario": "nominal"},
            headers=self.admin_headers,
        )
        self.assertEqual(res.status_code, 200)
        env_id = res.json()["envelope_id"]

        # Inspect lifecycle events
        life = self.client.get(f"/api/telemetry/lifecycle/{env_id}").json()
        serialized = json.dumps(life)
        # Canary payload must NOT be exposed in metadata
        self.assertNotIn(canary, serialized)
        # Check that no private key fields exist
        self.assertNotIn("secret_key", serialized)
        self.assertNotIn("private_key", serialized)
        self.assertNotIn("shared_secret_bytes", serialized)

    def test_17_ntt_transient_fault_recovery_telemetry(self):
        """Acceptance Test 17: NTT transient fault triggers K=1 rollback and reports RECOVERED."""
        res = self.client.post(
            "/api/admin/dispatch",
            json={"payload_text": "TRANSIENT_FAULT_TEST", "scenario": "ntt_transient"},
            headers=self.admin_headers,
        )
        self.assertEqual(res.status_code, 200)
        ntt = res.json()["ntt"]
        self.assertEqual(ntt["invariant_status"], "ANOMALY_RECOVERED")
        self.assertEqual(ntt["fault_type_injected"], "TRANSIENT_TWIDDLE_BIT_FLIP")
        self.assertEqual(ntt["fault_layer"], 2)
        self.assertEqual(ntt["fault_butterfly"], 10)
        self.assertEqual(ntt["recovered_count"], 1)
        self.assertFalse(ntt["fail_stop_engaged"])

    def test_18_ntt_persistent_fault_fail_stop_telemetry(self):
        """Acceptance Test 18: NTT persistent fault triggers K>2 rollback exhaustion and fail-stop."""
        res = self.client.post(
            "/api/admin/dispatch",
            json={"payload_text": "PERSISTENT_FAULT_TEST", "scenario": "ntt_persistent"},
            headers=self.admin_headers,
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "FAIL_STOP_SUPPRESSED")
        ntt = res.json()["ntt"]
        self.assertEqual(ntt["invariant_status"], "VIOLATION_FAIL_STOP")
        self.assertTrue(ntt["fail_stop_engaged"])
        self.assertEqual(ntt["fail_stop_action"], "IMPLICIT_REJECTION_PSEUDORANDOM_SEED")

    def test_19_replay_suppression_telemetry(self):
        """Acceptance Test 19: Replay attack is detected and suppressed with audit log."""
        # 1. Send first message
        res1 = self.client.post(
            "/api/admin/dispatch",
            json={"payload_text": "REPLAY_ORIGINAL", "scenario": "nominal"},
            headers=self.admin_headers,
        )
        self.assertEqual(res1.status_code, 200)

        # 2. Resend as replay attack
        res2 = self.client.post(
            "/api/admin/dispatch",
            json={"payload_text": "REPLAY_ORIGINAL", "scenario": "replay_attack"},
            headers=self.admin_headers,
        )
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["status"], "REPLAY_BLOCKED")
        self.assertFalse(res2.json()["delivered_to_destination"])
        pipe = res2.json()["pipeline"]
        self.assertEqual(pipe["stage7_receiver_verification"]["status"], "REJECTED_REPLAY")

    def test_20_isl_outage_spooling_telemetry(self):
        """Acceptance Test 20: ISL outage engages DTN spooling and updates link telemetry."""
        res = self.client.post(
            "/api/admin/dispatch",
            json={"payload_text": "ISL_OUTAGE_TEST", "scenario": "isl_outage"},
            headers=self.admin_headers,
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "SPOOLED_IN_FLIGHT")
        self.assertFalse(res.json()["delivered_to_destination"])
        self.assertGreaterEqual(res.json()["sat1_queue_depth"], 1)

        # Check Hop 2 ISL is marked DOWN
        hops = self.client.get("/api/telemetry/hops").json()
        isl_hop = next(h for h in hops if h["hop_id"] == "HOP_2_ISL")
        self.assertEqual(isl_hop["link_state"], "DOWN")
        self.assertTrue(isl_hop["outage_active"])


if __name__ == "__main__":
    unittest.main()
