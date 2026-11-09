# ASTRA-Sec Phase 4: Visualization Requirements Specification

## 1. Executive Summary

This document establishes the formal visualization requirements for the future 3D Mission Control component of ASTRA-Sec. Rather than deriving requirements from visual aesthetics, this specification is strictly derived from the operational characteristics, node topology, telemetry schemas, and event flows verified in Phase 2 (`research/phase2_core_pipeline/`) and Phase 3 (`research/phase3_experimental_lab/`).

---

## 2. Operational Topology vs. Visual Simulation

Before defining rendering requirements, the distinction between operational software entities and geospatial representations must be formally documented:

| Entity | ASTRA-Sec Implementation Reality | Current Geospatial Status | Future 3D Representation |
| :--- | :--- | :--- | :--- |
| **Ground Station A (`GSA`)** | `GroundStationNode` (`dtn://gsa/app`). Full cryptographic originator (ML-KEM encap, ML-DSA signing, AEAD encryption). | Static logical node. Coordinates not yet in core schema (conceptually Svalbard or Canberra). | Fixed WGS84 surface marker, ground antenna icon, TX/RX status halo. |
| **Satellite Relay 1 (`SAT1`)** | `SatelliteRelayNode` (`dtn://sat1/relay`). Transactional SQLite WAL bundle spooling, routing table, forwarder. | Logical DTN router. No orbital state vectors in core schema. | Low-Earth Orbit (LEO-1 ~550 km altitude) node, 3D spacecraft model. |
| **Satellite Relay 2 (`SAT2`)** | `SatelliteRelayNode` (`dtn://sat2/relay`). Transactional SQLite WAL bundle spooling, routing table, forwarder. | Logical DTN router. No orbital state vectors in core schema. | Low-Earth Orbit (LEO-2 ~550 km altitude) node, 3D spacecraft model. |
| **Ground Station B (`GSB`)** | `GroundStationVerifier` (`dtn://gsb/app`). Decapsulation, signature verification, anti-replay, ACK generation. | Static logical node. Coordinates not yet in core schema (conceptually White Sands or Darmstadt). | Fixed WGS84 surface marker, reception telemetry indicator. |
| **ISL Link (`SAT1 <-> SAT2`)** | `ContactSchedule` / `LinkState` (UP, DOWN, OCCULTED). | Logical link state with simulated outage & restoration. | 3D dynamic vector line; color indicates link health (Cyan = Active, Red = Outage). |
| **Uplink / Downlink** | Ingestion & delivery callback loops with measurable latency. | Logical transport hops. | Line-of-sight visual cones/beams between ground stations and relays. |
| **In-Flight Bundles** | `PqcMessageEnvelope` (5,119 B wire payload). | Abstract byte arrays in memory / SQLite tables. | Animated packet entity traversing path with unique bundle ID tag. |

> [!IMPORTANT]
> ASTRA-Sec's four operational nodes currently operate as logical software endpoints. The backend does not yet propagate Keplerian orbital elements or SGP4 state vectors. A primary requirement for future visualization is bridging this gap without compromising backend authority.

---

## 3. Requirements Classification Matrix

Requirements are categorized into **Mandatory** (required for baseline 3D Mission Control), **Desirable** (essential for high-impact research presentation), and **Optional Future Capability** (advanced astronomical or constellation scaling).

| Requirement Category | Specific Capability | Classification | Current Backend Availability | Implementation Dependency |
| :--- | :--- | :--- | :--- | :--- |
| **R01: Earth Rendering** | Interactive 3D WGS84 globe with smooth zooming, panning, rotation, and terminator day/night illumination. | **Mandatory** | External to backend | 3D Globe Engine (WebGL/WebGPU) |
| **R02: Ground Stations** | Geospatial positioning of GSA and GSB using latitude, longitude, and altitude above ellipsoid. | **Mandatory** | Lat/Lon coordinates must be assigned in config | Geospatial Entity API |
| **R03: Satellite Nodes** | Dynamic 3D spacecraft entities representing SAT1 and SAT2 in space. | **Mandatory** | Logical node IDs exist (`dtn://sat1/relay`) | 3D Model Loading (GLTF/GLB) or billboard primitives |
| **R04: Dynamic Movement** | Time-dependent position updates along orbital paths. | **Desirable** | Not in core (requires SGP4/TLE companion) | Orbital propagation or interpolated trajectory |
| **R05: Communication Links** | Dynamic 3D lines representing Uplink, Inter-Satellite Link (ISL), and Downlink. | **Mandatory** | Link states (`LinkState.UP/DOWN`) available | Dynamic Polyline / Glow Material |
| **R06: In-Transit Bundles** | Animated packet entities moving along active links between nodes during message transit. | **Mandatory** | Timestamps ($t_{origin}, t_{relay}, t_{dest}$) verified in Phase 3 | Time-sampled entity interpolation |
| **R07: DTN Queue State** | Visual queue indicators showing pending bundle count and SQLite WAL disk size per relay. | **Mandatory** | Exposed via `/api/queue` and Phase 3 telemetry | UI Data Badges / 3D billboard labels |
| **R08: Crypto Indicators** | Visual indicators for ML-KEM encapsulation, ML-DSA verification, and AEAD decryption. | **Mandatory** | Emitted in Phase 2/3 events and `/ws/live` | Event-driven status glow / HUD cards |
| **R09: Fault & Rollback** | Visual state change when SEU occurs, rollback ($K \le 2$) executes, or fail-stop engages. | **Mandatory** | Emitted in Phase 3 JSONL (`transient_recovery_occurred`) | Event-driven alert animations / node recoloring |
| **R10: Replay Engine** | Deterministic playback of historical experiment trials from Phase 3 raw JSONL manifests. | **Desirable** | Raw JSONL records and manifests exist | Timeline scrubbing / clock synchronization |
| **R11: Live Telemetry** | Sub-100 ms updates from live WebSocket `/ws/live` stream without UI stutter. | **Mandatory** | WebSocket endpoint operational | Reactive state adapter (no full scene redraws) |
| **R12: Node Inspection** | Clickable ground stations and satellites opening detailed inspection panels (trust store, queue, keys). | **Mandatory** | Node identities and policy models fully inspectable | Raycasting / Entity picking API |
| **R13: Local / Offline** | Complete standalone execution without requiring internet access or third-party commercial API keys. | **Mandatory** | Requirement for secure lab & flight testbeds | Local tile assets & local terrain ellipsoid |
| **R14: Constellation Scale**| Scaling from 2 relays to 100+ constellation nodes (e.g. Walker delta constellation). | **Optional Future** | Routing table supports regex routing | Instanced rendering / PointPrimitiveCollection |

---

## 4. Key Takeaways for Technology Selection

1. The selected rendering engine must support **true geospatial coordinates** (WGS84 ellipsoidal geometry) rather than an arbitrary 3D sphere, because space ground tracks and orbital mechanics require geodetic reference frames.
2. The engine must support **time-dynamic entities** (positions defined as functions of time or sampled timestamps) to enable both smooth real-time animation and historical trial scrubbing.
3. The engine must support **event-driven updates** without tearing down and rebuilding the 3D scene graph upon each WebSocket packet arrival.
4. The solution must run **100% offline** without commercial license tokens, mandatory cloud accounts, or remote tile-server calls.
