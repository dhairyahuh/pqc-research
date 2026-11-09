#!/usr/bin/env python3
"""Unit and integration test suite for the ASTRA-Sec Research Monitoring Dashboard."""

import unittest
from fastapi.testclient import TestClient

from astra_sec.dashboard.app import create_app, ADMIN_TOKEN


class TestDashboardApi(unittest.TestCase):
    """Verifies all dashboard REST endpoints, authentication, and live data binding."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = TestClient(cls.app)
        cls.auth_headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}

    def test_health_endpoint(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertIn("ML-KEM-768", data["post_quantum_algorithms"][0])

    def test_topology_endpoint(self):
        res = self.client.get("/api/topology")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["nodes"]), 4)
        eids = [n["eid"] for n in data["nodes"]]
        self.assertIn("dtn://gsa/app", eids)
        self.assertIn("dtn://sat1/relay", eids)
        self.assertIn("dtn://sat2/relay", eids)
        self.assertIn("dtn://gsb/app", eids)
        self.assertEqual(len(data["links"]), 3)

    def test_nodes_endpoint_no_secrets_exposed(self):
        res = self.client.get("/api/nodes")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("ground_stations", data)
        self.assertIn("satellite_relays", data)

        # Invariant: NEVER leak private key material
        raw_dump = res.text.lower()
        self.assertNotIn("secret_key", raw_dump)
        self.assertNotIn("private_key", raw_dump)

    def test_queue_endpoint(self):
        res = self.client.get("/api/queue")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("queues", data)
        self.assertEqual(len(data["queues"]), 2)

    def test_experiments_summary_endpoint(self):
        res = self.client.get("/api/experiments/summary")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_trials"], 38)
        self.assertEqual(data["detections"], 38)
        self.assertEqual(data["detection_rate_pct"], 100.0)
        self.assertEqual(data["sdc_count"], 0)
        self.assertIn("statistical_disclaimer", data)

    def test_experiments_trials_endpoint(self):
        res = self.client.get("/api/experiments/trials?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["total"], 38)
        self.assertLessEqual(len(data["trials"]), 10)

    def test_benchmarks_endpoint(self):
        res = self.client.get("/api/benchmarks")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("benchmarks", data)
        self.assertIn("overheads", data)

    def test_fdir_telemetry_endpoint(self):
        res = self.client.get("/api/fdir/telemetry")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("gsa", data)
        self.assertIn("gsb", data)

    def test_admin_dispatch_unauthorized_blocked(self):
        res = self.client.post("/api/admin/dispatch", json={"payload_text": "UNAUTHORIZED_PAYLOAD"})
        self.assertEqual(res.status_code, 401)

    def test_admin_dispatch_authorized_success(self):
        res = self.client.post(
            "/api/admin/dispatch",
            json={"payload_text": "TELEMETRY_SAMPLE_TEST", "simulate_transient_fault": False},
            headers=self.auth_headers,
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertTrue(data["delivered_to_destination"])
        self.assertTrue(data["receipt_verified"])

    def test_admin_dispatch_with_transient_recovery(self):
        res = self.client.post(
            "/api/admin/dispatch",
            json={"payload_text": "TELEMETRY_RECOVERED_SEU", "simulate_transient_fault": True},
            headers=self.auth_headers,
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertTrue(data["transient_recovery_occurred"])

    def test_admin_fault_injection_and_recovery(self):
        # 1. Inject link outage
        res = self.client.post(
            "/api/admin/inject-fault",
            json={"target_node": "dtn://sat1/relay", "fault_type": "link_outage"},
            headers=self.auth_headers,
        )
        self.assertEqual(res.status_code, 200)

        # Verify link is DOWN in topology
        topo = self.client.get("/api/topology").json()
        isl_link = [l for l in topo["links"] if l["source"] == "dtn://sat1/relay"][0]
        self.assertEqual(isl_link["state"], "DOWN")

        # 2. Restore link
        res2 = self.client.post(
            "/api/admin/inject-fault",
            json={"target_node": "dtn://sat1/relay", "fault_type": "link_restore"},
            headers=self.auth_headers,
        )
        self.assertEqual(res2.status_code, 200)

        topo2 = self.client.get("/api/topology").json()
        isl_link2 = [l for l in topo2["links"] if l["source"] == "dtn://sat1/relay"][0]
        self.assertEqual(isl_link2["state"], "UP")

    def test_dashboard_html_served(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("ASTRA-Sec", res.text)
        self.assertIn("MISSION CONTROL OBSERVABILITY", res.text)


if __name__ == "__main__":
    unittest.main()
