# ASTRA-Sec: Phase 7 Implementation & Verification Report
## Real Orbital Data, Physical Astrodynamics, 3D Spacecraft Models & Physically Grounded Network Visualisation

**Permanent Research Title:** *Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems*  
**Mission Protocol:** *ASTRA-Sec: Post-Quantum End-to-End Secure Messaging and Delay-Tolerant Cryptographic Resilience for Space Networks*  
**Phase:** 7 — Real Orbital Data, Professional Spacecraft Models & Physically Grounded 3D Network Visualisation  
**Author:** Antigravity Autonomous Systems Architect & Post-Quantum Aerospace Engineer  
**Date:** November 10, 2026  
**Status:** COMPLETE & VERIFIED  

---

## 1. Executive Summary & Mission Scope

Phase 7 upgrades the ASTRA-Sec Mission Control 3D geospatial environment from an illustrative 3D visualization into an aerospace-grade, physically grounded space network observatory. 

Prior to Phase 7, space nodes were positioned at static coordinates with simplified point spheres. In Phase 7, the environment has been fully modernized with:
1. **Real Public Orbital Data (CelesTrak / TLE)**: Integrated Two-Line Element (TLE) ephemeris ingestion with sub-second timeout, strict modulo-10 checksum verification, and 100% offline air-gapped cache fallback.
2. **SGP4 Astrodynamics Engine (`satellite.js`)**: Real-time analytical propagation of satellite state vectors, orbital velocity ($v = \sqrt{\mu / r} \approx 7.59\ \text{km/s}$), geodetic coordinates ($\text{lat}, \text{lng}, \text{alt}$), and dynamic inter-satellite crosslink range ($d_{\text{ISL}}$).
3. **3D Orbital Trajectory Paths & Ground Tracks**: 72-segment closed Keplerian orbit curves wrapping the 3D Earth at physical orbital altitudes, color-coded by constellation plane.
4. **Professional 3D Spacecraft Models**: Modular Three.js procedural assets featuring metallic multi-layer insulation (gold foil MLI), articulated multi-panel photovoltaic solar arrays with high-efficiency blue cell textures, steerable high-gain parabolic reflector dishes, feed horns, optical laser crosslink terminals, and aft attitude propulsion nozzles.
5. **Professional Ground Station Terminal Models**: High-polygon faceted geodesic tracking radome at Svalbard (GSA) and 34-meter beam waveguide parabolic tracking dish on a dual-axis azimuth/elevation gimbal fork at Canberra (GSB).
6. **Physically Grounded Communication Arcs**: Dynamically bound link geometries that track moving spacecraft across orbits, reflecting nominal links, ISL outages, and in-flight cryptographic bundle transit.
7. **Strict Research Integrity & Entity Classification**: Formal and UI-level separation distinguishing real reference space assets (e.g., ISS ZARYA NORAD 25544, NOAA-19 NORAD 33591, IRIDIUM-106 NORAD 43075) from simulated ASTRA-Sec testbed nodes (`dtn://sat1/relay`, `dtn://sat2/relay`).

---

## 2. Orbital Data Architecture & Classification Invariants

### 2.1 Two-Line Element (TLE) Ingestion & Air-Gapped Cache
Public TLE ephemerides are managed via `astra_sec.service.orbital_service.OrbitalService` backed by `data/orbital/cached_tle.json`. The service implements dual-mode operation:
- **Online Refresh Mode**: Connects to CelesTrak (`https://celestrak.org/NORAD/elements/gp.php?CATNR=...`) with a 2.0-second timeout to retrieve updated Keplerian elements.
- **Guaranteed Air-Gapped Fallback**: If internet connectivity is absent or times out, the system operates completely offline without degradation, serving verified cached ephemerides with explicit data freshness indicators (`CACHED_OFFLINE`).

### 2.2 Strict Node Classification Hierarchy

| Node ID | EID / Catalog | Name | Orbit Regime | Classification | Cryptographic & Spacecraft Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`sat1`** | `dtn://sat1/relay`<br>*(NORAD 99001)* | ASTRA-LEO-1 | Polar Sun-Sync LEO<br>(Alt: 550 km, Inc: 97.4°) | `SIMULATED_TESTBED_NODE` | Store-and-Forward Router; SQLite WAL persistent spool; Gold foil MLI bus, dual 3-panel solar wings, high-gain parabolic reflector dish. |
| **`sat2`** | `dtn://sat2/relay`<br>*(NORAD 99002)* | ASTRA-LEO-2 | Inclined Relay LEO<br>(Alt: 550 km, Inc: 45.0°) | `SIMULATED_TESTBED_NODE` | Store-and-Forward Router; SQLite WAL persistent spool; Titanium octagonal bus, dual 2-panel solar wings, dual feed horns + cross-dipole. |
| **`iss`** | `norad://25544` | ISS (ZARYA) | LEO Station Orbit<br>(Alt: 420 km, Inc: 51.63°) | `REAL_REFERENCE_ORBIT` | Real-world Keplerian ground truth benchmark; Integrated truss, pressurized cross modules, 4 bronze solar wings. |
| **`noaa19`**| `norad://33591` | NOAA 19 | Polar Sun-Sync LEO<br>(Alt: 850 km, Inc: 98.94°) | `REAL_REFERENCE_ORBIT` | Real-world polar meteorological reference; asymmetric single-wing solar array. |
| **`iridium`**| `norad://43075` | IRIDIUM 134 | Polar LEO Crosslink<br>(Alt: 780 km, Inc: 86.39°) | `REAL_REFERENCE_ORBIT` | Commercial inter-satellite link reference; triangular prism bus, phased array antennas. |
| **`gsa`** | `dtn://gsa/app` | Ground Station Alpha | Svalbard, Norway<br>(78.23° N, 15.41° E, 450 m) | `GROUND_STATION_TERMINAL`| Cryptographic Originator; ML-KEM-768 Encap, ML-DSA-65 Signer, L2 AEAD; 11m Geodesic tracking radome. |
| **`gsb`** | `dtn://gsb/app` | Ground Station Bravo | Canberra, Australia<br>(-35.40° S, 148.98° E, 650 m)| `GROUND_STATION_TERMINAL`| Destination Verifier; Monitored ML-KEM-768 Decaps, ML-DSA-65 Verify, Return ACK; 34m Beam Waveguide Parabolic Dish. |

> [!IMPORTANT]
> The ASTRA-Sec Mission Control dashboard strictly adheres to Section 1 of the permanent engineering guidelines. Testbed relay nodes are explicitly labeled as `SIMULATED_TESTBED_NODE` in all UI telemetry cards, schemas, and API responses, while CelesTrak assets are designated as `REAL_REFERENCE_ORBIT`.

---

## 3. Astrodynamics & SGP4 Orbital Propagation

### 3.1 Mathematical Foundation
Orbital state propagation is evaluated in real time both client-side (`satellite.min.js` v5.0.0) and server-side (`astra_sec/service/orbital_service.py`).
1. **Keplerian Orbital Velocity**:
   $$v = \sqrt{\frac{\mu_{\oplus}}{R_{\oplus} + h}}$$
   Where $\mu_{\oplus} = 398,600.4418\ \text{km}^3/\text{s}^2$, $R_{\oplus} = 6,378.137\ \text{km}$, and $h = 550.0\ \text{km}$.
   Calculated velocity: $v \approx 7.585\ \text{km/s}$ ($\text{Mach } 22.3$).
2. **ECI to Geodetic Coordinate Conversion**:
   $$\text{GMST} = \theta_{\text{UT1}} = \text{gstime}(\text{Date})$$
   $$\text{lat} = \arcsin\left(\frac{Z}{\|\vec{R}\|}\right), \quad \text{lng} = \text{atan2}(Y, X) - \theta_{\text{GMST}}$$
3. **Dynamic Inter-Satellite Crosslink (ISL) Range**:
   $$\vec{P} = \left[ (R_{\oplus} + h)\cos(\text{lat})\cos(\text{lng}),\ (R_{\oplus} + h)\cos(\text{lat})\sin(\text{lng}),\ (R_{\oplus} + h)\sin(\text{lat}) \right]$$
   $$d_{\text{ISL}} = \|\vec{P}_{\text{sat1}} - \vec{P}_{\text{sat2}}\|$$
   Continuously measured and displayed in the Top-Left HUD (typically oscillating between $4,500\ \text{km}$ and $9,800\ \text{km}$ across orbital passes).

### 3.2 3D Orbital Trajectory Paths
Using Globe.gl's `.pathsData()`, closed 3D Keplerian orbits are generated by propagating 72 orbital time steps across the period $T = 95.6\ \text{min}$ ($1440 / n$):
- **SAT-1 Trajectory**: Polar Sun-Synchronous ellipse inclined at $97.4^\circ$, rendered with gold stroke (`#ffd700`).
- **SAT-2 Trajectory**: Inclined relay orbit inclined at $45.0^\circ$, rendered with orange stroke (`#ff9100`).
- **ISS Trajectory**: Reference LEO orbit inclined at $51.64^\circ$, rendered with dashed cyan stroke (`#00e5ff`).

---

## 4. Spacecraft & Ground Terminal 3D Architecture

All 3D assets are constructed using modular procedural Three.js geometries, ensuring sub-millisecond offline load times, zero external network requests, and precise control over materials:

```
+-----------------------------------------------------------------------------------+
|                           ASTRA-Sec 3D SPACECRAFT ASSETS                          |
+-----------------------------------------------------------------------------------+
|  SAT-1 (ASTRA-LEO-1 Polar Relay)          |  SAT-2 (ASTRA-LEO-2 Inclined Relay)   |
|  - Gold Foil MLI Bus (Box 2.4x1.6x1.6)    |  - Titanium Octagonal Bus (Cyl r=1.15)|
|  - Dual 3-Panel Photovoltaic Wings        |  - Dual 2-Panel Photovoltaic Wings    |
|  - Steerable High-Gain Parabolic Dish     |  - Dual Feed Horns + Cross-Dipole     |
|  - Laser ISL Transceiver Terminal         |  - Dual Aft Chemical Thruster Bells   |
|  - Zenith Omni Tracking Beacon (Gold)     |  - Optical Crosslink Head (Orange)    |
+-----------------------------------------------------------------------------------+
|  GROUND STATION ALPHA (SvalSat, Norway)   |  GROUND STATION BRAVO (CDSCC, Aus)    |
|  - Geodesic Radome (Icosahedron r=1.6)    |  - 34m Beam Waveguide Dish (Sphere r)  |
|  - Concrete Base Pedestal Tower           |  - Dual-Axis Az/El Gimbal Fork Yoke   |
|  - Calibration Whip Mast & Cyan Beacon    |  - Concrete Ops Building Pedestal     |
+-----------------------------------------------------------------------------------+
```

---

## 5. Physical Network Links & Trajectory-Aware Dispatch

1. **Dynamic Link Tracking**: Communication arcs (Uplink GSA $\rightarrow$ SAT-1, ISL SAT-1 $\rightarrow$ SAT-2, Downlink SAT-2 $\rightarrow$ GSB) dynamically bind to the current instantaneous coordinates of the 3D spacecraft. As the satellites travel along their orbits, the communication vectors sweep across space in real time.
2. **Disruption Visibility**: When the ISL is severed via flight control (`TOGGLE ISL OUTAGE`), the crosslink arc switches from cyan/green to flashing red dashed strokes. Telemetry updates indicate store-and-forward spooling into SAT-1's SQLite WAL database.
3. **Trajectory-Aware Packet Animation**: Dispatched PQC envelopes travel sequentially through the 3D space scene:
   - **Hop 1 (Uplink)**: GSA SvalSat $\rightarrow$ SAT-1 ($5,119\ \text{B}$ wire bundle containing FIPS 203 encapsulation and FIPS 204 signature).
   - **Hop 2 (ISL Crosslink)**: SAT-1 $\rightarrow$ SAT-2 across the inter-satellite arc (halts with amber warning if ISL is down).
   - **Hop 3 (Downlink)**: SAT-2 $\rightarrow$ GSB Canberra.
   - **Destination Verifier & FDIR**: Destination checks ML-DSA signature and decapsulates ML-KEM secret under dual-transform NTT invariant monitoring ($r \equiv t\zeta \pmod{3329}$).
   - **Return ACK**: A high-altitude reverse verification arc flashes green across the globe confirming delivered authentication.

---

## 6. Verification Evidence & Test Artifacts

### 6.1 Unit & Integration Test Suite (`tests/unit/test_phase7_orbital.py`)
All 9 unit tests passed:
- `test_01_orbital_cache_file_exists_and_schema_valid`: PASSED
- `test_02_strict_satellite_classification`: PASSED
- `test_03_tle_formatting_and_checksum_integrity`: PASSED
- `test_04_sgp4_ephemeris_propagation_physics`: PASSED
- `test_05_ground_stations_geodetic_coordinates`: PASSED
- `test_06_isl_crosslink_range_calculation`: PASSED
- `test_07_offline_air_gapped_fallback`: PASSED
- `test_08_fastapi_orbital_endpoints`: PASSED
- `test_09_frontend_vendor_assets_integrity`: PASSED

### 6.2 Full Verification Suite
```bash
make test-python   # 45 integration + 14 unit test suites: PASS
make test-c        # All KATs + 38-trial fault injection campaigns: PASS
make health-check  # System diagnostic report: OK
make lint          # Python syntax compilation: OK
```

### 6.3 Photographic & UI Artifacts Captured
The following high-resolution 1080p verification screenshots were captured via headless Playwright automation and saved to `docs/phases/`:

1. `docs/phases/phase7_constellation_global.png` — Global Earth view displaying orbital trajectory curves, ground stations, and live satellite positions.
2. `docs/phases/phase7_spacecraft_model_sat1.png` — High-resolution close-up of SAT-1 showing gold MLI bus, 3-panel solar array wings, high-gain parabolic reflector dish, and nadir-pointing boom.
3. `docs/phases/phase7_spacecraft_model_sat2.png` — High-resolution close-up of SAT-2 showing octagonal titanium bus, dual-panel wings, dual horn antennas, and cross-dipole array.
4. `docs/phases/phase7_ground_station_dish.png` — Ground view of Ground Station Bravo showing the 34-meter parabolic dish antenna on its dual-axis gimbal fork at Canberra.
5. `docs/phases/phase7_orbital_tracks.png` — Constellation orbital trajectory paths and real-time SGP4 link geometry.
6. `docs/phases/phase7_packet_transmission.png` — Live PQC bundle dispatch with in-flight packet status HUD and active communication vectors.

---

## 7. Conclusion

Phase 7 successfully transforms ASTRA-Sec into an aerospace-grade 3D satellite mission control and cryptographic observatory. The system combines genuine public orbital data with real-time SGP4 propagation, realistic 3D spacecraft and ground terminal models, dynamic communication vector tracking, and strict research classification integrity, operating with 100% offline air-gapped capability.
