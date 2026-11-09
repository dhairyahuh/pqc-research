# ASTRA-Sec Phase 4: Technical Compatibility with the Existing System Stack

## 1. Existing System Stack Forensics

Before evaluating integration ergonomics, the existing implementation stack of ASTRA-Sec was inspected:

### 1.1. Backend Architecture
* **Framework**: FastAPI (Python 3.9+) with Uvicorn ASGI server (`astra_sec/dashboard/app.py`).
* **Transport Protocols**:
  - HTTP REST endpoints (`/api/trials`, `/api/summary`, `/api/queue`, `/api/admin/dispatch`, `/api/admin/inject-fault`).
  - WebSocket full-duplex stream (`/ws/live`) powered by Starlette `WebSocketManager`.
* **Data Payloads**: Strict JSON models validated via Pydantic v2 schemas (`PqcMessageEnvelope`, `VerificationRecord`, `ForwardingEvent`).
* **Storage Engines**: Persistent SQLite 3 with Write-Ahead Logging (`spool_sat1.db`, `spool_sat2.db`).

### 1.2. Frontend Architecture
* **Location**: `astra_sec/dashboard/static/index.html` (661 lines).
* **Framework**: **Vanilla HTML5, CSS3, and ES6+ JavaScript**.
* **Bundler / Build System**: **Zero frontend bundler** (No Webpack, Vite, or npm build step required to run the dashboard).
* **Styling**: Pure CSS custom properties (dark mission-control theme `#0a0d14`, JetBrains Mono & Inter typography, flexbox/grid layout).
* **Networking**: Native browser `fetch()` for REST and native `WebSocket` for live event telemetry.

---

## 2. Answers to the 12 Required Technical Questions

| # | Technical Question | CesiumJS Assessment | globe.gl Assessment |
| :--- | :--- | :--- | :--- |
| **Q1** | Can it render inside the existing application without replacing the frontend? | **YES**. Can be mounted into a dedicated `<div id="cesiumContainer">` in `index.html` via a standalone script tag or module. | **YES**. Mounts into `<div id="globeViz">` in `index.html`. |
| **Q2** | Can it support a continuously updating 4-node topology? | **YES**. `EntityCollection` updates node positions, link vectors, and status colors dynamically. | **YES**. Re-evaluates accessor functions on data arrays. |
| **Q3** | Can entities move smoothly along communication paths? | **YES**. `SampledPositionProperty` provides sub-millisecond polynomial interpolation along 3D polylines. | **PARTIAL**. Animates dashes along arcs, but lacks individual entity tracking with custom metadata. |
| **Q4** | Can a packet be tied to a unique message or bundle ID? | **YES**. Each bundle is instantiated as a distinct Cesium `Entity` tagged with `envelope_id`, payload size, and timestamps. | **NO**. Packets in `globe.gl` are anonymous dash intervals along an arc. |
| **Q5** | Can multiple packets be animated simultaneously? | **YES**. `viewer.entities` handles hundreds of concurrent time-stamped moving entities. | **YES**. Multiple arcs can animate dashes simultaneously. |
| **Q6** | Can links change appearance according to actual link state? | **YES**. Link polylines bind dynamic `MaterialProperty` (e.g. Glowing Cyan for Active, Pulsing Red for Outage). | **YES**. Link color accessor updates based on node state. |
| **Q7** | Can a node expose a detailed inspection panel when selected? | **YES**. Native `ScreenSpaceEventHandler` supports clicking entities to populate HUD panels with node keys, queues, and policies. | **YES**. `onPointClick` and `onCustomLayerClick` callbacks supported. |
| **Q8** | Can the scene display timestamps and replay historical events? | **YES**. Native Cesium `Timeline` and `Clock` widgets scrub historical time windows with deterministic synchronization. | **NO**. No native timeline or clock widget. Requires writing custom scrubbing UI and state machinery. |
| **Q9** | Can it handle updates without recreating the entire scene? | **YES**. Updates modify existing `Entity` properties in place without destroying the scene graph. | **PARTIAL**. Changing data arrays triggers internal Three.js geometry updates. |
| **Q10**| Can it run locally without requiring commercial external APIs? | **YES**. Initialized with `EllipsoidTerrainProvider` and local NaturalEarthII texture. | **YES**. Works with local texture maps. |
| **Q11**| Can it run on target hardware and modern browsers? | **YES**. Standard WebGL 1.0 / 2.0; runs smoothly on macOS, Linux, and Windows (Chrome, Safari, Firefox, Edge). | **YES**. Standard WebGL via Three.js. |
| **Q12**| Can it support eventual addition of 100+ satellites? | **YES**. `PointPrimitiveCollection` and instanced GLTF rendering support large constellations (thousands of satellites). | **LIMITED**. Frame rate degrades above several dozen custom 3D mesh objects. |

---

## 3. Frontend Architecture Impact Analysis

Because the existing dashboard is built with vanilla HTML5/ES6 and served directly by FastAPI's `StaticFiles`, integrating a library that requires a heavy React or TypeScript bundler (such as React Three Fiber or Resium) would impose a disruptive refactoring burden on the project.

In contrast:
1. **CesiumJS** distributes pre-compiled, optimized UMD/ESM builds (`Cesium.js` and `Widgets.css`) that can be hosted directly in `astra_sec/dashboard/static/cesium/`.
2. This allows the 3D globe to mount directly inside `index.html` as a peer component to the existing metrics cards and audit log, maintaining 100% backward compatibility with the existing FastAPI backend and WebSocket infrastructure.
3. If the team later chooses to migrate the frontend to React, CesiumJS code is easily encapsulated within a React `useRef` hook or migrated to Resium without rewriting the underlying entity models.
