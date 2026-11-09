# ASTRA-Sec Phase 4: Future 3D Visualization Scene and Interaction Design

## 1. Scene Layout & Composition

The future 3D Mission Control scene will integrate into `astra_sec/dashboard/static/index.html` as the central visual operational environment, flanked by telemetry status cards and cryptographic audit logs.

```
+----------------------------------------------------------------------------------------------------+
| ASTRA-Sec Mission Control HUD — Post-Quantum Space Resilience Monitor                              |
+----------------------------------------------------------------------------------------------------+
| [Top Bar: Epoch UTC | Active Mode: TESTBED TOPOLOGY / ORBITAL SGP4 | Link State: UP | Replay: LIVE] |
+------------------------------------------------------+---------------------------------------------+
|                                                      | [HUD Telemetry Cards]                       |
|                                                      | - Cryptographic Engine: ML-KEM-768 Monitored|
|                                                      | - Digital Signatures: ML-DSA-65 (FIPS 204)  |
|                                                      | - Layer 4 Status: Invariant Guard Active    |
|                CESIUMJS 3D VIEWPORT                  | - Rollback Budget: K=2 (0 Exhaustions)      |
|                                                      |                                             |
|          [ SAT-1 ] -------- ISL -------- [ SAT-2 ]   | [Selected Entity Inspector Panel]           |
|            /                                \        | - Entity: Satellite Relay 1 (dtn://sat1)   |
|         Uplink                           Downlink    | - Altitude: 550.0 km                        |
|          /                                    \      | - SQLite WAL Queue: 5 Bundles (73.2 KB)     |
|      [ GSA ]                                [ GSB ]  | - Contact State: ACTIVE (SAT2 Peer)         |
|   (Svalbard)                              (Canberra) | - Trust Store: 4 Registered Public Keys     |
|                                                      |                                             |
|                                                      | [Cryptographic Event Stream]                |
|                                                      | [20:30:01] GSA -> Encap 1,088 B CT          |
|                                                      | [20:30:02] SAT1 -> Spooled Bundle bb0455    |
|                                                      | [20:30:03] GSB -> Decap Verified (SDC: 0)   |
+------------------------------------------------------+---------------------------------------------+
| [Timeline Controller: Play/Pause | Scrub Slider | Speed: 1x, 5x, 20x | Time: 2026-11-09T20:30:00Z]   |
+----------------------------------------------------------------------------------------------------+
```

---

## 2. Detailed Subsystem Visual Design

### 2.1. Earth and Geography
* **Visual Elements**: Interactive WGS84 ellipsoid rendered with NaturalEarthII high-resolution texture. Night-side illumination with subtle city light textures and dynamic solar terminator.
* **Ground Stations**:
  - `GSA`: Svalbard Satellite Station ($78.2297^\circ\text{ N}, 15.4078^\circ\text{ E}$). 3D parabolic antenna icon, pulsing cyan telemetry halo.
  - `GSB`: Canberra Deep Space Communication Complex ($-35.4014^\circ\text{ S}, 148.9817^\circ\text{ E}$). 3D parabolic antenna icon, green reception indicator.
* **Backend Data Source**: Static node definitions in `astra_sec.service.ground_station`. Coordinates to be formally declared in `GroundStationConfig` *(Future enhancement)*.

---

### 2.2. Satellite Constellation Network
* **Relay Nodes**:
  - `SAT1`: `dtn://sat1/relay`. 3D spacecraft model in polar orbit at 550 km altitude.
  - `SAT2`: `dtn://sat2/relay`. 3D spacecraft model in matching orbital plane offset by $45^\circ$ true anomaly.
* **Node Labels**: Dynamic billboard text hovering over satellites showing pending spool queue count and disk storage (e.g. `LEO-1 | Queue: 5 (73 KB)`).
* **Backend Data Source**: Emitted via `/api/queue` and `ForwardingEvent` telemetry.

---

### 2.3. Communication Links
* **Dynamic 3D Polylines**:
  - **Uplink**: GSA $\longrightarrow$ SAT1.
  - **Inter-Satellite Link (ISL)**: SAT1 $\longleftrightarrow$ SAT2.
  - **Downlink**: SAT2 $\longrightarrow$ GSB.
* **Material Properties & State Representation**:
  - **Active / UP**: `PolylineGlowMaterialProperty` glowing vibrant cyan (`#00e5ff`).
  - **Link Outage / OCCULTED**: Solid pulsing red line (`#ff1744`), dashed segments indicating severed RF path.
* **Backend Data Source**: `LinkState` events emitted via `/ws/live` and `/api/admin/inject-fault`.

---

### 2.4. Packet and Bundle Movement
* **Visual Entity**: A glowing yellow/gold geometric pulse moving along active links.
* **Animation Lifecycle**:
  - Created at GSA upon `MESSAGE_DISPATCHED`.
  - Interpolated along the 3D polyline using `SampledPositionProperty` matching transit duration $t_{relay}$.
  - On arrival at SAT1, the packet pauses momentarily during the `BUNDLE_SPOOLED` SQLite write, then resumes transit toward SAT2.
  - On arrival at GSB, packet emits a green confirmation ring. A smaller green packet (ML-DSA-65 signed ACK) travels in reverse back to GSA.
* **Backend Data Source**: Per-message microsecond timestamps ($t_{origin}, t_{cbor}, t_{relay}, t_{dest}, t_{ack}$) recorded in Phase 3 raw JSONL output.

---

### 2.5. Cryptographic Execution Indicators
* **ML-KEM-768 Encap / Decap**: Pulsing cyan geometric shield surrounding the node during cryptographic execution.
* **ML-DSA-65 Digital Signatures**: Brief purple flash on envelope departure and destination verification.
* **Fault Detection & Rollback**:
  - If a radiation SEU bit flip is injected, the node flashes amber (`#ffab00`).
  - If rollback recovery succeeds ($K \le 2$), an amber restoration ring expands and turns green.
  - If fail-stop is triggered (e.g. stuck persistent bit), the packet turns solid red and terminates, and the destination node displays an explicit containment indicator.
* **Security Guardrail**: **Zero secret keys, nonces, or unencrypted plaintext are ever rendered in the 3D scene or DOM.**

---

### 2.6. DTN Persistence and Buffer Visualization
* **Queue Growth**: Real-time 3D bar gauge or billboard ring above satellite relays showing SQLite WAL queue depth.
* **Link Disruption Behavior**: When ISL is severed (`LinkState.DOWN`), packets arriving at SAT1 visually divert into the satellite's persistent storage vault. Upon link restoration, spooled packets visually flush in FIFO sequence order across the restored link.
* **Backend Data Source**: `spool_disk_bytes` and `pending_bundles` from `SatelliteRelayNode.get_fdir_telemetry()`.

---

### 2.7. Historical Trial Replay Engine
* **Controls**: CesiumJS native `Timeline` and `Animation` widgets with Play, Pause, Step Forward, Step Backward, and Speed Multipliers ($1\times, 5\times, 10\times, 50\times$).
* **Replay Data Source**: Loads any selected Phase 3 manifest (`EXP-D01-FULL-ASTRA_24bd1cdf_manifest.json`) and associated raw JSONL measurement file, translating recorded timestamps into `JulianDate` clock intervals for exact deterministic reproduction.
