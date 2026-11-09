# ASTRA-Sec Phase 4: Event-Driven Visualization Architecture

## 1. Architectural Philosophy

A critical requirement of Phase 4 is ensuring that the 3D visualization is an **unidirectional consumer** of authoritative system telemetry. Under no circumstances may the visualization engine simulate or invent delivery success, cryptographic status, or queue state.

The system enforces a 5-layer decoupled pipeline:

```
+-----------------------------------------------------------------------------------+
| [1] ASTRA-Sec Production Backend & Testbed                                         |
|     - ML-KEM-768 Monitored C Engine | ML-DSA-65 Signer | DTN SQLite WAL Spool    |
+-----------------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------------+
| [2] Telemetry & Event Streaming Interface                                         |
|     - REST APIs: /api/trials, /api/queue, /api/summary                            |
|     - WebSocket Stream: /ws/live (Full-duplex real-time event broadcaster)        |
+-----------------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------------+
| [3] Client-Side Telemetry Adapter (`AstraVisualAdapter`)                          |
|     - Event Ingestion & Schema Validation (Pydantic / TS models)                  |
|     - Packet Lifecycle Tracker (maps envelope_id -> active visual entity)         |
|     - State Aggregator (node queues, link health, crypto event logs)              |
+-----------------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------------+
| [4] 3D Geospatial Rendering Engine (CesiumJS)                                     |
|     - Earth WGS84 Ellipsoid | Spacecraft Models | Dynamic Polylines               |
|     - Time-Dynamic SampledPositionProperty Packet Interpolation                  |
|     - Status Halos & HUD Billboard Markers                                        |
+-----------------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------------+
| [5] User Interaction & Inspection HUD                                             |
|     - Clickable Entity Raycasting -> Node Inspection Panels (Trust, Policy, Keys) |
|     - Replay Controller (Play, Pause, Timeline Scrubbing from Raw JSONL)          |
+-----------------------------------------------------------------------------------+
```

---

## 2. Event Schema Mapping Matrix

The table below maps verified Phase 2/3 backend events into specific visual state transformations:

| Backend Event Type | Emitted By | Data Fields Available in Backend | Visual Action in 3D Scene |
| :--- | :--- | :--- | :--- |
| `MESSAGE_DISPATCHED` | GSA (`dtn://gsa/app`) | `envelope_id`, `destination_eid`, `payload_bytes`, `timestamp`, `wire_bytes` | Spawn packet entity at GSA marker; initiate uplink animation toward SAT1. |
| `CRYPTO_ENCAP_COMPLETED`| GSA | `kem_algorithm` (ML-KEM-768), `cipher_text_bytes` (1088), `duration_us` | Display cyan cryptographic shield halo around GSA; log event in Crypto HUD. |
| `SIGNATURE_VERIFIED` | SAT / GSB | `signer_eid`, `algorithm` (ML-DSA-65), `valid` (true/false) | Flash node green (if valid) or red (if invalid signature); update verification counter. |
| `BUNDLE_SPOOLED` | SAT1 / SAT2 | `bundle_id`, `spool_db`, `pending_bundles`, `storage_kb` | Update satellite queue billboard badge (e.g. `LEO-1 | Queue: 5 (73 KB)`). |
| `BUNDLE_FORWARDED` | SAT1 / SAT2 | `bundle_id`, `from_peer`, `to_peer`, `timestamp` | Animate packet entity along Inter-Satellite Link (ISL) or Downlink path. |
| `LINK_STATE_CHANGED` | Network Controller | `target_node`, `link_state` (`UP`, `DOWN`, `OCCULTED`) | Change link polyline color: Active = Cyan (`#00e5ff`), Outage = Glowing Red (`#ff1744`). |
| `FAULT_DETECTED_SEU` | Layer 4 C Engine | `fault_type`, `layer`, `bit_position`, `rollback_attempt` | Pulse receiving satellite/station with amber warning ring; increment telemetry fault counter. |
| `FAIL_STOP_ENGAGED` | Layer 4 / Verifier | `envelope_id`, `reason`, `suppression_active` | Packet turns solid red and disintegrates/fades; destination emits containment indicator. |
| `ACK_DELIVERED` | GSA Verifier | `envelope_id`, `e2e_latency_ms`, `receipt_verified` | Reverse green ACK packet completes circuit back to GSA; success banner increments. |

---

## 3. Event Handling Without Scene Regeneration

A fundamental flaw of naive WebGL implementations is re-creating the scene or re-instantiating 3D meshes on every incoming event. 

In the designed CesiumJS adapter:
1. **Persistent Nodes**: `GSA`, `SAT1`, `SAT2`, and `GSB` are created **once** upon initialization and added to `viewer.entities`.
2. **Property Mutation**: When `/ws/live` emits an event, the adapter mutates properties in place:
   ```javascript
   // Update queue badge without recreating entity
   sat1Entity.label.text = `LEO-1 | Queue: ${event.pending_bundles} (${event.storage_kb} KB)`;
   ```
3. **Transient Packet Lifecycles**:
   - On `MESSAGE_DISPATCHED`, an entity is added with a `SampledPositionProperty` that interpolates its 3D position from GSA to SAT1 over the measured transit duration $t_{relay}$.
   - Upon arrival at GSB, the entity's lifetime interval ends, and Cesium automatically garbage-collects it from the active render pass.
