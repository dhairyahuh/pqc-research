# ASTRA-Sec: Backend API & WebSocket Reference

The ASTRA-Sec Mission Control backend is implemented in Python using FastAPI. It exposes RESTful telemetry APIs and an asynchronous WebSocket stream for live mission observability.

---

## 1. Authentication

Administrative control endpoints (`/api/dispatch`, `/api/faults/inject`, `/api/faults/reset`) require bearer token authentication.

```http
Authorization: Bearer <ASTRA_ADMIN_TOKEN>
```
Default token: `astra-mission-control-token` (configurable via environment variable `ASTRA_ADMIN_TOKEN`).

---

## 2. Core Operational REST Endpoints

### 2.1 System Health
`GET /api/health`
Returns the operational status of the ASTRA-Sec Mission Control backend and active cryptographic algorithms.

**Response (200 OK):**
```json
{
  "status": "HEALTHY",
  "system": "ASTRA-Sec Mission Control Interface",
  "version": "0.1.0",
  "timestamp_utc": "2026-11-10T01:30:00Z",
  "security_active": true,
  "post_quantum_algorithms": [
    "ML-KEM-768 (FIPS 203)",
    "ML-DSA-65 (FIPS 204)"
  ]
}
```

### 2.2 Network Topology
`GET /api/topology`
Returns the active space constellation nodes and communication link states.

**Response (200 OK):**
```json
{
  "nodes": [
    {"id": "dtn://gsa/app", "name": "Ground Station Alpha", "type": "ground_station"},
    {"id": "dtn://sat1/relay", "name": "Satellite Relay 1", "type": "satellite"},
    {"id": "dtn://sat2/relay", "name": "Satellite Relay 2", "type": "satellite"},
    {"id": "dtn://gsb/app", "name": "Ground Station Bravo", "type": "ground_station"}
  ],
  "links": [
    {"source": "dtn://gsa/app", "target": "dtn://sat1/relay", "state": "UP"},
    {"source": "dtn://sat1/relay", "target": "dtn://sat2/relay", "state": "UP"},
    {"source": "dtn://sat2/relay", "target": "dtn://gsb/app", "state": "UP"}
  ]
}
```

### 2.3 DTN Queue Status
`GET /api/queue`
Returns persistent SQLite WAL queue metrics (bundle counts and storage bytes) across all relays.

**Response (200 OK):**
```json
{
  "queues": [
    {
      "relay_eid": "dtn://sat1/relay",
      "pending_bundles": 0,
      "storage_bytes": 20480,
      "storage_kb": 20.0
    },
    {
      "relay_eid": "dtn://sat2/relay",
      "pending_bundles": 0,
      "storage_bytes": 20480,
      "storage_kb": 20.0
    }
  ]
}
```

### 2.4 Orbital Ephemeris Catalog
`GET /api/orbital/satellites?refresh_live=false`
Returns the public Two-Line Element (TLE) ephemeris catalog, node classifications, and ground station facilities.

**Response (200 OK):**
```json
{
  "source": "CELESTRAK_PUBLIC_GP_AND_ASTRA_SEC_SGP4",
  "generated_at": "2026-11-09T19:42:00Z",
  "data_freshness_status": "CACHED_OFFLINE",
  "sgp4_model": "SGP4_STANDARD_REVISED_2006",
  "air_gapped_fallback": true,
  "satellites": [
    {
      "id": "sat1",
      "norad_cat_id": 99001,
      "name": "ASTRA-LEO-1 (SAT-1 Relay)",
      "classification": "SIMULATED_TESTBED_NODE",
      "eid": "dtn://sat1/relay",
      "orbit_type": "Polar Sun-Synchronous LEO",
      "nominal_altitude_km": 550.0,
      "inclination_deg": 97.4,
      "period_minutes": 95.6,
      "line1": "1 99001U 26901A...",
      "line2": "2 99001  97.4000..."
    }
  ],
  "ground_stations": [...]
}
```

### 2.5 Real-Time SGP4 Propagation
`GET /api/orbital/propagation?timestamp=<float>`
Calculates and returns physical orbital states (latitude, longitude, altitude, velocity, and 3D ISL distance).

---

## 3. Flight Operations Command APIs

### 3.1 Dispatch Envelope
`POST /api/dispatch`
Headers: `Authorization: Bearer <token>`
Body:
```json
{
  "payload_text": "FLIGHT_TELEMETRY_PACKET_MISSION_EPOCH_2026",
  "ttl_seconds": 3600,
  "simulate_transient_fault": false,
  "scenario": "nominal"
}
```
Available Scenarios: `nominal`, `isl_outage`, `ntt_transient`, `ntt_persistent`, `replay_attack`, `tamper_sig`.

### 3.2 Fault Injection
`POST /api/faults/inject`
Headers: `Authorization: Bearer <token>`
Body:
```json
{
  "target_node": "dtn://sat1/relay",
  "fault_type": "link_outage",
  "duration_ms": 1000
}
```

---

## 4. WebSocket Telemetry Stream

`WS /ws/telemetry`
Provides bi-directional real-time telemetry events.

### Broadcast Event Types:
- `TELEMETRY_EVENT`: Granular layer event (ADU create, KEM encap, HKDF, AEAD encrypt, DSA sign, forward, decap, verify, ACK).
- `MESSAGE_TRANSMITTED`: Envelope delivery summary record.
- `FAULT_STATE_CHANGED`: Dynamic link state change (`link_outage`, `link_restore`).
