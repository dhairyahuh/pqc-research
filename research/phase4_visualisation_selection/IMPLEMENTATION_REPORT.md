# ASTRA-Sec: 3D Satellite Mission Control Visualization Implementation Report

## 1. Selected Open-Source Foundation & Licensing

* **Primary 3D Geospatial Engine**: **Globe.gl** (v2.46.2) built upon **Three.js** (r160) and **Three-Globe** (v2.45).
* **Repository**: https://github.com/vasturiano/globe.gl
* **License**: **MIT License** (Fully open-source, permissive, commercially viable, zero royalties or subscription tokens).
* **Deployment Integrity**: **100% Offline Air-Gapped Operation**.
  - All core dependencies (`three.min.js`, `globe.gl.min.js`) and high-resolution Earth/space textures (`earth-night.jpg`, `earth-blue-marble.jpg`, `night-sky.png`) are hosted locally in `astra_sec/dashboard/static/`.
  - Zero external CDN or cloud API dependencies (no Cesium ion, no Mapbox, no Google Maps API keys required).

---

## 2. Dependencies Added

* **Zero New Python Packages**: Uses existing FastAPI, Uvicorn, and Starlette stack.
* **Zero npm Build Step**: Client-side libraries run natively in the browser without Webpack, Vite, or Node.js runtime compilation:
  - `astra_sec/dashboard/static/vendor/three.min.js` (654 KB, MIT)
  - `astra_sec/dashboard/static/vendor/globe.gl.min.js` (1.8 MB, MIT)
  - `astra_sec/dashboard/static/textures/earth-night.jpg` (698 KB)
  - `astra_sec/dashboard/static/textures/earth-blue-marble.jpg` (1.4 MB)
  - `astra_sec/dashboard/static/textures/night-sky.png` (883 KB)

---

## 3. Files Created and Modified

### Files Created:
1. `astra_sec/dashboard/static/js/mission_control_3d.js`: Full-featured 3D mission control module managing:
   - 3D WGS84 coordinates for GSA (Svalbard), SAT1 (LEO-1), SAT2 (LEO-2), and GSB (Canberra).
   - Custom 3D procedural spacecraft meshes (bus, dual solar panels, nadir antenna dish, beacon lights) and ground antenna radomes.
   - Dynamic 3D communication arcs (Uplink, ISL, Downlink) with animated signal pulses and state transitions.
   - Multi-hop packet animation engine (`GSA` $\rightarrow$ `SAT1` $\rightarrow$ `SAT2` $\rightarrow$ `GSB` $\rightarrow$ `ACK`).
   - Interactive node inspection HUD and camera focus presets.
2. `astra_sec/dashboard/static/vendor/three.min.js`: Local standalone Three.js build.
3. `astra_sec/dashboard/static/vendor/globe.gl.min.js`: Local standalone Globe.gl bundle.
4. `astra_sec/dashboard/static/textures/*`: High-resolution local Earth and starry sky textures.
5. `research/phase4_visualisation_selection/3d_mission_control_screenshot.png`: Full-resolution PNG screenshot of the running 3D dashboard.

### Files Modified:
1. `astra_sec/dashboard/static/index.html`:
   - Replaced flat 2D SVG/CSS diagram with responsive 560px 3D Earth Mission Control viewport.
   - Added HUD overlays: Operational Telemetry Stream, Node Inspector Panel, In-Flight Packet Tracker, and Camera Presets.
   - Linked `/api/admin/dispatch`, `/api/admin/inject-fault`, and `/ws/live` to the 3D animation engine.

---

## 4. Backend Interfaces Consumed

* `GET /api/topology`: Fetches live status of the 4 nodes and 3 communication links.
* `GET /api/queue`: Fetches real-time SQLite WAL spool queue depth (`pending_bundles`) and disk storage (`storage_kb`).
* `GET /api/nodes`: Fetches active FIPS 203 ML-KEM-768 and FIPS 204 ML-DSA-65 public key fingerprints and FDIR telemetry.
* `POST /api/admin/dispatch`: Dispatches real post-quantum encrypted and signed envelopes across the 4-node pipeline.
* `POST /api/admin/inject-fault`: Dynamically injects `link_outage` (ISL DOWN) or `link_restore` (ISL UP and spool flush).
* `WebSocket /ws/live`: Real-time event broadcast stream updating the 3D scene on `MESSAGE_TRANSMITTED` and `FAULT_STATE_CHANGED`.

---

## 5. Missing Telemetry Identified & Handled

* The backend currently tracks logical node EIDs (`dtn://gsa/app`, `dtn://sat1/relay`, `dtn://sat2/relay`, `dtn://gsb/app`).
* To ground the visualization in realistic space geography without inventing false orbital claims, geodetic coordinates were explicitly configured in `mission_control_3d.js` and clearly documented:
  - **GSA**: $78.2297^\circ\text{ N}, 15.4078^\circ\text{ E}$ (Svalbard Satellite Station, Norway, Alt: 0.01)
  - **SAT1**: $52.00^\circ\text{ N}, 38.00^\circ\text{ E}$ (LEO Sun-Synchronous, Alt: 0.36, ~550 km)
  - **SAT2**: $-8.00^\circ\text{ S}, 92.00^\circ\text{ E}$ (LEO Relay, Alt: 0.36, ~550 km)
  - **GSB**: $-35.4014^\circ\text{ S}, 148.9817^\circ\text{ E}$ (Canberra Deep Space Complex, Australia, Alt: 0.01)

---

## 6. How to Run the Implemented Dashboard

```bash
# 1. Start the ASTRA-Sec Mission Control server
make dashboard
# Or directly:
python3 -m uvicorn astra_sec.dashboard.app:app --host 0.0.0.0 --port 8000

# 2. Open in any modern web browser:
open http://localhost:8000
```

---

## 7. Automated and Manual Test Results

| Test # | Acceptance Test Case | Execution Verification | Outcome |
| :---: | :--- | :--- | :---: |
| **1** | Dashboard starts successfully | Uvicorn running on port 8000; HTTP GET `/` returns status 200 | **PASS** |
| **2** | Existing dashboard API operational | `/api/summary`, `/api/queue`, `/api/nodes`, `/api/trials` return valid JSON | **PASS** |
| **3** | Real 3D Earth renders | WebGL canvas rendered with continents, atmosphere, and starfield | **PASS** |
| **4** | All 4 network nodes appear | GSA, SAT1, SAT2, GSB rendered with 3D models and geodetic coordinates | **PASS** |
| **5** | 3 communication paths render | Uplink (GSA $\rightarrow$ SAT1), ISL (SAT1 $\rightarrow$ SAT2), Downlink (SAT2 $\rightarrow$ GSB) | **PASS** |
| **6** | Camera rotation & controls | OrbitControls active (left drag rotates, scroll zooms, right drag pans) | **PASS** |
| **7** | Camera preset buttons | Overview, Focus SAT-1, Focus SAT-2, Focus GSA, Focus GSB functional | **PASS** |
| **8** | Node selection & inspection | Clicking any node opens Node Inspector HUD with live keys & queue state | **PASS** |
| **9** | Real dispatch integration | `POST /api/admin/dispatch` executes ML-KEM-768 encap & ML-DSA-65 signing | **PASS** |
| **10**| 3D packet hop animation | Golden packet travels along 3D arcs across all hops to destination | **PASS** |
| **11**| Link outage visual state | ISL turns pulsing Crimson Red (`#ff1744`); packets spool safely at SAT1 | **PASS** |
| **12**| Link recovery & queue flush | Restoring link flushes spooled packets to GSB; ISL returns to Cyan | **PASS** |
| **13**| NTT SEU fault alert | Destination shows amber rollback recovery alert ($K=1$), then confirms delivery | **PASS** |
| **14**| Zero console errors | Verified clean script execution under modern browser standards | **PASS** |
| **15**| Offline verification | 100% of vendor scripts and textures loaded from `/static/` | **PASS** |

---

## 8. Captured Screenshot Proof

Actual screenshot captured from the running application:  
`research/phase4_visualisation_selection/3d_mission_control_screenshot.png` (1440 $\times$ 1100 resolution, 349 KB PNG).

---

## 9. Known Limitations

1. **Constellation Size**: Currently configured for the verified 4-node pipeline. Adding 100+ Walker constellation satellites is supported by the data model but will require multi-path routing telemetry from Layer 5.
2. **Simplified Orbital Drift**: Satellites currently follow deterministic orbital tracks. Full SGP4/TLE continuous physical propagation can be enabled via `satellite.js` in a future phase.
