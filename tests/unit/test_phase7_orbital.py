"""Phase 7 Unit & Integration Verification: Real Orbital Data, Physical Astrodynamics,
SGP4 Ephemeris Management, and Offline Air-Gapped Resilience.
"""

import json
import math
import os
import time
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

from astra_sec.dashboard.app import create_app
from astra_sec.schema.orbital import (
    GroundStationRecord,
    OrbitalCatalogPayload,
    PropagatedSatelliteState,
    SatelliteClassification,
    SatelliteOrbitalRecord,
)
from astra_sec.service.orbital_service import OrbitalService

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
CACHE_FILE = ROOT_DIR / "data" / "orbital" / "cached_tle.json"


def calc_tle_checksum(line: str) -> int:
    """Computes standard Two-Line Element (TLE) checksum (modulo 10)."""
    s = 0
    for c in line[:68]:
        if c.isdigit():
            s += int(c)
        elif c == "-":
            s += 1
    return s % 10


class TestPhase7OrbitalRealism(unittest.TestCase):
    """Verifies Phase 7 astrodynamics, public orbital data, and 3D network models."""

    def test_01_orbital_cache_file_exists_and_schema_valid(self):
        """Verifies cached TLE data exists and conforms to Pydantic v2 schema."""
        self.assertTrue(CACHE_FILE.exists(), f"Orbital cache file not found at {CACHE_FILE}")
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        payload = OrbitalCatalogPayload(
            source=data["source"],
            generated_at=data["generated_at"],
            data_freshness_status="CACHED_OFFLINE",
            sgp4_model=data["sgp4_model"],
            air_gapped_fallback=data["air_gapped_fallback"],
            satellites=[SatelliteOrbitalRecord(**s) for s in data["satellites"]],
            ground_stations=[GroundStationRecord(**g) for g in data["ground_stations"]],
        )
        self.assertGreaterEqual(len(payload.satellites), 4)
        self.assertEqual(len(payload.ground_stations), 2)
        self.assertTrue(payload.air_gapped_fallback)

    def test_02_strict_satellite_classification(self):
        """Verifies strict separation between simulated testbed nodes and real reference space assets."""
        svc = OrbitalService(cache_file=CACHE_FILE)
        catalog = svc.get_catalog(refresh_live=False)

        sat1 = next(s for s in catalog.satellites if s.id == "sat1")
        sat2 = next(s for s in catalog.satellites if s.id == "sat2")
        iss = next(s for s in catalog.satellites if s.id == "iss")
        noaa19 = next(s for s in catalog.satellites if s.id == "noaa19")

        # Invariant: SAT-1 and SAT-2 must be classified as simulated testbed nodes
        self.assertEqual(sat1.classification, SatelliteClassification.SIMULATED_TESTBED_NODE)
        self.assertEqual(sat2.classification, SatelliteClassification.SIMULATED_TESTBED_NODE)
        self.assertEqual(sat1.eid, "dtn://sat1/relay")
        self.assertEqual(sat2.eid, "dtn://sat2/relay")

        # Invariant: Reference objects must be classified as real reference orbits
        self.assertEqual(iss.classification, SatelliteClassification.REAL_REFERENCE_ORBIT)
        self.assertEqual(noaa19.classification, SatelliteClassification.REAL_REFERENCE_ORBIT)
        self.assertIsNone(iss.eid)
        self.assertIsNone(noaa19.eid)

    def test_03_tle_formatting_and_checksum_integrity(self):
        """Verifies all TLE ephemerides adhere to standard 69-character lines and checksums."""
        svc = OrbitalService(cache_file=CACHE_FILE)
        catalog = svc.get_catalog(refresh_live=False)

        for sat in catalog.satellites:
            l1 = sat.line1
            l2 = sat.line2

            self.assertEqual(len(l1), 69, f"Satellite {sat.name} Line 1 length {len(l1)} != 69")
            self.assertEqual(len(l2), 69, f"Satellite {sat.name} Line 2 length {len(l2)} != 69")
            self.assertTrue(l1.startswith("1 "), f"Satellite {sat.name} Line 1 must start with '1 '")
            self.assertTrue(l2.startswith("2 "), f"Satellite {sat.name} Line 2 must start with '2 '")

            # Checksum calculation
            expected_ck1 = int(l1[68])
            calc_ck1 = calc_tle_checksum(l1)
            self.assertEqual(calc_ck1, expected_ck1, f"Line 1 checksum mismatch for {sat.name}: calc {calc_ck1} != exp {expected_ck1}")

            expected_ck2 = int(l2[68])
            calc_ck2 = calc_tle_checksum(l2)
            self.assertEqual(calc_ck2, expected_ck2, f"Line 2 checksum mismatch for {sat.name}: calc {calc_ck2} != exp {expected_ck2}")

    def test_04_sgp4_ephemeris_propagation_physics(self):
        """Verifies analytical orbital propagation obeys Keplerian mechanics and geodetic bounds."""
        svc = OrbitalService(cache_file=CACHE_FILE)
        states = svc.propagate_all(timestamp=1762718400.0)

        self.assertGreaterEqual(len(states), 4)
        for st in states:
            self.assertTrue(-90.0 <= st.lat <= 90.0, f"Latitude {st.lat} out of bounds for {st.name}")
            self.assertTrue(-180.0 <= st.lng <= 180.0, f"Longitude {st.lng} out of bounds for {st.name}")
            self.assertTrue(300.0 <= st.altitude_km <= 1200.0, f"Altitude {st.altitude_km} out of LEO bounds for {st.name}")
            # Orbital velocity in LEO: ~7.2 to ~7.9 km/s (Mach 21 - 23)
            self.assertTrue(7.2 <= st.velocity_kms <= 7.9, f"Velocity {st.velocity_kms} km/s out of physical bounds for {st.name}")
            self.assertTrue(88.0 <= st.orbital_period_min <= 110.0, f"Period {st.orbital_period_min} min out of bounds for {st.name}")

    def test_05_ground_stations_geodetic_coordinates(self):
        """Verifies ground station placement, elevations, and facility specifications."""
        svc = OrbitalService(cache_file=CACHE_FILE)
        catalog = svc.get_catalog(refresh_live=False)

        gsa = next(g for g in catalog.ground_stations if g.id == "gsa")
        gsb = next(g for g in catalog.ground_stations if g.id == "gsb")

        # Svalbard SvalSat polar ground station
        self.assertEqual(gsa.name, "Ground Station Alpha (GSA)")
        self.assertAlmostEqual(gsa.lat, 78.23, places=1)
        self.assertAlmostEqual(gsa.lng, 15.41, places=1)
        self.assertEqual(gsa.altitude_km, 0.45)
        self.assertEqual(gsa.eid, "dtn://gsa/app")

        # Canberra CDSCC deep space ground station
        self.assertEqual(gsb.name, "Ground Station Bravo (GSB)")
        self.assertAlmostEqual(gsb.lat, -35.40, places=1)
        self.assertAlmostEqual(gsb.lng, 148.98, places=1)
        self.assertEqual(gsb.altitude_km, 0.65)
        self.assertEqual(gsb.eid, "dtn://gsb/app")

    def test_06_isl_crosslink_range_calculation(self):
        """Verifies 3D Euclidean inter-satellite range computation between SAT-1 and SAT-2."""
        svc = OrbitalService(cache_file=CACHE_FILE)
        states = svc.propagate_all(timestamp=1762718400.0)

        sat1 = next(s for s in states if s.id == "sat1")
        sat2 = next(s for s in states if s.id == "sat2")

        self.assertIsNotNone(sat1.active_isl_range_km)
        self.assertIsNotNone(sat2.active_isl_range_km)
        self.assertEqual(sat1.active_isl_range_km, sat2.active_isl_range_km)
        # Realistic line-of-sight range between two LEO satellites on separate orbital planes: 1,000 to 12,500 km
        self.assertTrue(1000.0 <= sat1.active_isl_range_km <= 12500.0)

    def test_07_offline_air_gapped_fallback(self):
        """Verifies that offline air-gapped environments gracefully serve cached TLEs without crashing."""
        svc = OrbitalService(cache_file=CACHE_FILE)
        
        # Requesting catalog without network must succeed instantly
        cat_offline = svc.get_catalog(refresh_live=False)
        self.assertEqual(cat_offline.data_freshness_status, "CACHED_OFFLINE")
        self.assertTrue(cat_offline.air_gapped_fallback)

        # When refresh_live is requested but network times out / fails, fallback is seamless
        cat_fallback = svc.get_catalog(refresh_live=True)
        self.assertEqual(len(cat_fallback.satellites), len(cat_offline.satellites))

    def test_08_fastapi_orbital_endpoints(self):
        """Verifies REST endpoints /api/orbital/satellites and /api/orbital/propagation."""
        app = create_app()
        client = TestClient(app)

        # 1. GET /api/orbital/satellites
        res_sat = client.get("/api/orbital/satellites")
        self.assertEqual(res_sat.status_code, 200)
        data_sat = res_sat.json()
        self.assertIn("satellites", data_sat)
        self.assertGreaterEqual(len(data_sat["satellites"]), 4)
        self.assertIn("ground_stations", data_sat)
        self.assertEqual(len(data_sat["ground_stations"]), 2)

        # 2. GET /api/orbital/propagation
        res_prop = client.get("/api/orbital/propagation")
        self.assertEqual(res_prop.status_code, 200)
        data_prop = res_prop.json()
        self.assertIn("timestamp_utc", data_prop)
        self.assertIn("satellites", data_prop)
        sat_list = data_prop["satellites"]
        sat1_prop = next(s for s in sat_list if s["id"] == "sat1")
        self.assertIn("lat", sat1_prop)
        self.assertIn("lng", sat1_prop)
        self.assertIn("velocity_kms", sat1_prop)
        self.assertIn("active_isl_range_km", sat1_prop)

    def test_09_frontend_vendor_assets_integrity(self):
        """Verifies 100% offline air-gapped vendor scripts are present and intact."""
        vendor_dir = ROOT_DIR / "astra_sec" / "dashboard" / "static" / "vendor"
        self.assertTrue((vendor_dir / "globe.gl.min.js").exists())
        self.assertGreater((vendor_dir / "globe.gl.min.js").stat().st_size, 500000)
        self.assertTrue((vendor_dir / "three.min.js").exists())
        self.assertGreater((vendor_dir / "three.min.js").stat().st_size, 100000)
        self.assertTrue((vendor_dir / "satellite.min.js").exists())
        self.assertGreater((vendor_dir / "satellite.min.js").stat().st_size, 20000)


if __name__ == "__main__":
    unittest.main()
