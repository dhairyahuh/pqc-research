# ASTRA-Sec: Phase 5 Professional Mission Control & Cryptographic Security Observability Implementation Report

## 1. Executive Summary & Objective

In accordance with Phase 5 requirements, the ASTRA-Sec Mission Control interface has been elevated into an aerospace-grade, technically detailed satellite communication and cybersecurity observability environment.

The system now exposes the internal cryptographic, transport, and fault-resilience mechanics of ASTRA-Sec across both a high-fidelity **3D Mission Operations Mode** and an in-depth **Technical Analysis Mode**. Observers can trace the full lifecycle of a message:

$$\text{Originator ADU} \longrightarrow \text{ML-KEM-768 Encap} \longrightarrow \text{HKDF-SHA256} \longrightarrow \text{ML-DSA-65 Sign} \longrightarrow \text{AES-256-GCM} \longrightarrow \text{BPv7 Wire Bundle} \longrightarrow \text{SQLite WAL Spool} \longrightarrow \text{3D Constellation Forwarding} \longrightarrow \text{L4 NTT Invariant Verification} \longrightarrow \text{Receiver Acceptance} \longrightarrow \text{Signed Return ACK}$$

---

## 2. Features Actually Implemented

### A. Unified NASA Open MCT & Orbit-02 Console Architecture
The dashboard follows the high-density flight operations architecture inspired by NASA Open MCT and aerospace mission control centers (Orbit-02):
1. **Top Mission Header (44px)**:
   - Aerospace mission branding with FIPS 203 & 204 verification badges.
   - Live subsystem health pills: System Health (`HEALTHY`), Crypto Suite (`ML-KEM-768 / ML-DSA-65`), DTN (`RFC 9171 BPv7`), Spool (`ACID WAL`), WebSocket connection status, and live real-time ticking UTC clock.
   - One-click navigation toggle between the primary **Flight Console** and the deep **Experiment Lab**.

2. **Main 3-Column Flight Operations Grid**:
   - **Left Panel (310px)**:
     - Constellation Network Entities (GSA Svalbard, SAT-1 Polar LEO, SAT-2 Inclined LEO, GSB Canberra) with status pills and active node selection.
     - Selected Node Astrodynamics & Subsystems Inspector:
       - Real satellite orbital parameters: Semi-Major Axis ($6,928.14\text{ km}$), Orbital Altitude ($550.00\text{ km}$), Orbital Velocity ($7.59\text{ km/s}$), Orbital Period ($95.60\text{ min}$), Inclination ($97.40^\circ$), and Queue Depth.
       - Ground station facility parameters: Facility name, Elevation, Tracking Antenna, and Cryptographic Authorization Role.
       - Synchronized two-way selection: clicking any node in the left panel updates the 3D globe camera; clicking any node on the 3D globe updates the left panel astrodynamics.
   - **Center Panel (Flexible Width)**:
     - Central interactive 3D Earth rendered via Globe.gl with local high-resolution textures (`earth-night.jpg`, `night-sky.png`).
     - Dynamic 3D communication arcs (Uplink, ISL, Downlink, Return ACK) terminating precisely at node altitudes ($0.015$ ground radome, $0.35$ satellite bus).
     - Integrated Flight Command Strip: Payload text input, 6-scenario demonstration selector, `[▶ DISPATCH ENVELOPE]`, `[⚡ TOGGLE ISL OUTAGE]`, and `[↺ RESET ALL FAULTS]`.
     - HUD overlays: Live Orbital Link Telemetry, Interactive Node Inspector, In-Flight Packet Inspector, and Camera Presets (Overview, SAT-1, SAT-2, GSA, GSB, Auto-Rotate).
     - Live dispatch feedback banner with latency, delivery, and recovery indicators.
   - **Right Panel (370px)**:
     - **L2/L3 PQC Pipeline (8 Stages)**: Compact stage cards with live status badges (`COMPLETED`, `RUNNING`, `FAILED`, `PENDING`), algorithm details, and byte sizes.
     - **L4 NTT Fault Resilience Monitor**: Mathematical invariant verification $r \equiv t \cdot \zeta \pmod{3329}$, 128 dual butterflies checked, reference checker status, snapshot rollback buffer ($K \le 2$), recovery counters, fail-stop status, and live execution progression trace.
     - **Active DTN Wire Breakdown**: Visual segmented meter and breakdown of the 5,119 B wire bundle (ML-KEM-768 CT: 1,088 B, ML-DSA-65 Sig: 3,309 B, AES-256 CT: 56 B, AEAD Nonce + Tag + BPv7 Headers: 666 B).

3. **Bottom Dock (185px)**:
   - **Left Half**: End-to-End Security & Delivery Timeline with clickable milestones for audit inspection.
   - **Right Half**: Cryptographic Forensic Audit Trail with live append-only logging and category filter pills (`ALL`, `CRYPTO`, `FAULT`, `DTN`, `SECURITY`).

4. **Experiment Lab & Historical Matrix View**:
   - Accessible via the header toggle `[🔬 EXPERIMENT LAB]`.
   - Complete 38-trial empirical campaign explorer (Group A through E) querying raw records directly from `campaign_results.jsonl`.
   - Core metrics summary: Total Trials (38), Fault Detection Rate (100.0%), SDC Count (0), Latency profile ($p_{50} = 11.66\text{ ms}$).
   - Satellite SQLite WAL queue storage telemetry breakdown.

### B. Demonstration Orchestration Engine
Supports 6 interactive real-time scenarios via `/api/admin/dispatch`:
1. `nominal`: Nominal End-to-End PQC Delivery.
2. `isl_outage`: Inter-Satellite Link Outage (Packets halt and spool in SAT-1 WAL; link turns Crimson Red; flushes on restoration).
3. `ntt_transient`: NTT Butterfly SEU Bit-Flip (Invariant failure caught; localized register rollback $K=1$; retry succeeds).
4. `ntt_persistent`: Persistent Cryptographic Fault & Fail-Stop ($K > 2$ triggers fail-stop implicit rejection suppression).
5. `replay_attack`: Persistent Anti-Replay Filter Suppression (Replayed duplicate sequence number rejected at Layer 6).
6. `tamper_sig`: Digital Signature Tamper Rejection (1-bit corrupted ML-DSA-65 signature rejected before plaintext exposure).

---

## 3. Source Files Created and Modified

| File Path | Type | Role & Changes |
| :--- | :---: | :--- |
| `astra_sec/dashboard/static/index.html` | Modified | Redesigned into aerospace-grade dual-mode UI with HUD overlays, 8-stage pipeline cards, L4 NTT monitor, DTN spool meters, timeline, and audit stream. |
| `astra_sec/dashboard/static/js/mission_control_3d.js` | Modified | Upgraded 3D scene with precise altitude termination ($0.015$ / $0.35$), return ACK path, multi-hop packet transit engine with outage halting, and live telemetry synchronization. |
| `astra_sec/dashboard/app.py` | Modified | Added rich telemetry structures (`pipeline_trace`, `ntt_telemetry`, `bundle_info`, `timeline_events`), multi-scenario dispatch handler, and new REST endpoints (`/api/pipeline/latest`, `/api/bundle/latest`, `/api/timeline/latest`, `/api/experiments/trial/{trial_id}`). |
| `astra_sec/service/ground_station.py` | Modified | Added tracking for `last_decaps_telemetry` to capture native C fault telemetry directly from `decapsulate_with_telemetry`. |
| `tests/unit/test_dashboard.py` | Modified | Added 7 new test cases covering all new endpoints and fault scenarios. |
| `/tmp/test_phase5_e2e.py` | Created | Automated Playwright browser test harness verifying all 10 acceptance stages. |

---

## 4. Backend Interfaces Consumed

* `GET /api/pipeline/latest`: Fetches the latest 8-stage cryptographic pipeline and NTT telemetry.
* `GET /api/bundle/latest`: Fetches active bundle wire framing and storage metadata.
* `GET /api/timeline/latest`: Fetches discrete event milestones for the horizontal timeline.
* `GET /api/experiments/trial/{trial_id}`: Retrieves raw empirical trial parameters directly from `data/experiments/trials/campaign_results.jsonl`.
* `POST /api/admin/dispatch`: Executes real cryptographic operations and scenarios (`nominal`, `isl_outage`, `ntt_transient`, `ntt_persistent`, `replay_attack`, `tamper_sig`).
* `POST /api/admin/inject-fault`: Injects link outages, arms NTT twiddle SEUs, or resets faults.
* `WebSocket /ws/live`: Real-time streaming broadcasting `INITIAL_STATE`, `MESSAGE_TRANSMITTED`, and `FAULT_STATE_CHANGED`.

---

## 5. Automated Verification & Acceptance Test Results

Automated headless browser testing via Playwright confirmed zero uncaught console errors and full system interactivity across all 10 stages:

| Stage # | Verification Scope | Observed Behavior | Status |
| :---: | :--- | :--- | :---: |
| **1** | WebGL Dashboard Mount | Loaded cleanly; 0 uncaught page errors, 0 console errors | **PASS** |
| **2** | 3D Constellation & Orbit Controls | SAT-1 focused; Node Inspector opened with live queue depth | **PASS** |
| **3** | Nominal Dispatch (Scenario 1) | Envelope dispatched; golden packet animated; status `SUCCESS` in 22.04 ms; ACK verified | **PASS** |
| **4** | ISL Outage & Spooling (Scenario 2) | Link turned Crimson Red; packet halted at SAT-1; queue spooled; restored link flushed queue | **PASS** |
| **5** | Technical Analysis Mode | Switched tabs instantly; rendered 8 pipeline cards, NTT monitor, DTN spools, and wire inspector | **PASS** |
| **6** | NTT Transient SEU (Scenario 3) | Twiddle bit-flip injected; detected via $r \equiv t\zeta \pmod{3329}$; rollback $K=1$; recovered | **PASS** |
| **7** | Persistent Fault & Fail-Stop (Scenario 4) | Persistent fault armed; retry budget exceeded ($K > 2$); fail-stop implicit rejection engaged | **PASS** |
| **8** | Anti-Replay Attack (Scenario 5) | Duplicate sequence number re-injected; rejected at L6; command execution prevented | **PASS** |
| **9** | Browser Error Log Audit | Zero page errors and zero console warnings logged throughout all test runs | **PASS** |
| **10**| Image Forensics Audit | All 6 captured screenshots verified as non-black, high-resolution renders | **PASS** |

### Screenshot Image Forensics:
- `research/phase5_mission_control/phase5_ops_nominal.png`: $1440 \times 1100$, **35,131 distinct colors** (Nominal 3D Earth & Constellation View).
- `research/phase5_mission_control/phase5_ops_outage.png`: $1440 \times 1100$, **38,284 distinct colors** (Active ISL Outage with Halting at SAT-1).
- `research/phase5_mission_control/phase5_technical_analysis.png`: $1440 \times 1100$, **3,992 distinct colors** (8-Stage Cryptographic Pipeline & NTT Monitor).
- `research/phase5_mission_control/phase5_ntt_recovery.png`: $1440 \times 1100$, **3,738 distinct colors** (L4 NTT Invariant Violation & Rollback $K=1$).
- `research/phase5_mission_control/phase5_fail_stop.png`: $1440 \times 1100$, **3,696 distinct colors** (Fail-Stop Implicit Rejection Suppression).
- `research/phase5_mission_control/phase5_replay_suppressed.png`: $1440 \times 1100$, **38,590 distinct colors** (Anti-Replay Attack Suppression).

---

## 6. How to Run the Implemented Dashboard

```bash
# 1. Start the ASTRA-Sec Mission Control server:
python3 -m uvicorn astra_sec.dashboard.app:app --host 0.0.0.0 --port 8000

# 2. Open in your web browser:
open http://localhost:8000
```

---

## 7. Known Limitations & Next Steps

1. **Constellation Scaling**: The 3D scene is currently optimized for the 4-node space network (GSA, SAT1, SAT2, GSB). A Walker constellation of 100+ nodes will require dynamic Level-of-Detail (LOD) point instancing.
2. **Physical Orbital Propagation**: Satellites currently follow deterministic sun-synchronous/inclined coordinates. Continuous physical orbital drift propagation via SGP4/TLE and `satellite.js` can be added in a future phase.

