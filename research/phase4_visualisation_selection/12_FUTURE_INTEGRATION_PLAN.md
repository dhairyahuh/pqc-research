# ASTRA-Sec Phase 4: Phased Future Integration Plan

## 1. Minimal Proof-of-Concept Scope for Next Phase

To prevent scope creep and maintain strict software stability, the subsequent implementation phase will focus exclusively on a **Minimal Viable 3D Visualization Proof-of-Concept (PoC)**:
1. Mount a local CesiumJS viewport into a dedicated pane in `astra_sec/dashboard/static/index.html`.
2. Render an offline 3D Earth using local NaturalEarthII imagery and WGS84 ellipsoid.
3. Position the 4 operational nodes (`GSA`, `SAT1`, `SAT2`, `GSB`) and render the 3 communication links.
4. Animate a single packet traversing the 4-node pipeline when `/api/admin/dispatch` is triggered.
5. Dynamically toggle link color when the existing link outage button is clicked.

No broader frontend redesign will be attempted in the initial PoC.

---

## 2. Technical Implementation Architecture (16 Dimensions)

### 2.1. Dependency Installation Strategy
* Download pre-built standalone distribution of **CesiumJS** (v1.120+ release assets: `Cesium.js`, `Widgets.css`, `Assets/`, `Widgets/`) into `astra_sec/dashboard/static/vendor/cesium/`.
* Download standalone minified **`satellite.min.js`** into `astra_sec/dashboard/static/vendor/satellite/`.
* **Zero npm build requirement**: Serving these static vendor files directly via FastAPI's `StaticFiles(directory="static")` eliminates Node.js/bundler complexity.

### 2.2. Repository Integration Approach
* Keep visualization assets strictly partitioned within the dashboard static directory:
  ```
  astra_sec/dashboard/static/
  ├── vendor/
  │   ├── cesium/              # Pre-compiled CesiumJS library and assets
  │   └── satellite/           # Standalone satellite.js library
  ├── js/
  │   ├── astra_visual.js      # Cesium initialization and entity manager
  │   ├── astra_adapter.js     # WebSocket event translator
  │   └── astra_replay.js      # Historical JSONL experiment replayer
  ├── css/
  │   └── mission_control.css  # 3D viewport and HUD overlay styling
  └── index.html               # Main dashboard integrating the 3D viewport
  ```

### 2.3. Component Boundaries
* The 3D scene graph runs inside a dedicated canvas element (`<div id="cesiumContainer">`).
* The existing HTML metrics cards, queue counters, and audit logs remain autonomous DOM elements outside the WebGL canvas, communicating via standard JavaScript custom events.

### 2.4. Data Adapter
* Author `astra_adapter.js`: Subscribes to the existing `window.ws` WebSocket stream and maps backend JSON payloads (`MESSAGE_TRANSMITTED`, `BUNDLE_SPOOLED`, `FAULT_RECOVERED`) directly into visual entity calls.

### 2.5. Event Subscription Mechanism
* Leverages the existing `/ws/live` WebSocket connection in `index.html`. No additional backend communication channels are required.

### 2.6. Entity Lifecycle
* **Static Entities** (`GSA`, `GSB`, `SAT1`, `SAT2`): Created once during viewer initialization. Never destroyed during active session.
* **Transient Entities** (Packets, ACKs): Created upon message dispatch, animated across link polylines, and destroyed automatically upon delivery.

### 2.7. Satellite Position Update Strategy
* **Mode 1 (Testbed Topology)**: Fixed geocentric positions ($h = 550\text{ km}$) optimized for clear topological visualization.
* **Mode 2 (SGP4 Propagation)**: Client-side animation loop calling `satellite.propagate()` at 30 Hz and updating `satEntity.position` via `JulianDate`.

### 2.8. Link Rendering Strategy
* 3D polylines instantiated via `viewer.entities.add({ polyline: { positions: ... } })`.
* Color and glow bound to `CallbackProperty` referencing the live link state variable (`islState`).

### 2.9. Packet Animation Strategy
* In-flight packets use `SampledPositionProperty` populated with start position, waypoint positions (relays), and end position, bound to `JulianDate` timestamps matching measured transit delays.

### 2.10. Historical Replay Strategy
* REST endpoint `/api/trials/{id}/raw` fetches the raw Phase 3 JSONL file.
* `astra_replay.js` iterates through JSON lines, populates Cesium `TimeIntervalCollection`, and sets `viewer.clock.startTime` and `viewer.clock.stopTime`.

### 2.11. Performance Optimization
* Set `viewer.scene.requestRenderMode = true` to render frames only when scene state changes or animations are active, reducing idle laptop GPU consumption to < 2%.
* Use `Cartesian3` scratch variables to eliminate garbage collection stutters.

### 2.12. Error Handling
* Wrap WebGL initialization in feature-detection guards: if WebGL is unsupported or crashes, display a graceful fallback banner and maintain standard 2D dashboard operations.

### 2.13. Testing Strategy
* Automated browser integration tests using Playwright/Selenium verifying:
  1. CesiumJS canvas mounts with WebGL 2.0 context.
  2. Four nodes are present in `viewer.entities`.
  3. WebSocket dispatch event spawns an active packet entity.

### 2.14. Browser Compatibility
* Target modern evergreen browsers: Chrome 90+, Firefox 90+, Safari 15+, Edge 90+.

### 2.15. Deployment Strategy
* Vendor assets bundled directly with the Python package or downloaded via a simple `make download-cesium` target, ensuring self-contained offline deployment.

### 2.16. Rollback Strategy
* If CesiumJS introduces performance bottlenecks on low-spec hardware, the 3D viewport can be toggled off via a simple UI switch (`Show 3D Globe: OFF`), falling back cleanly to the existing 2D network diagram in `index.html`.

---

## 3. Files Identified for Future Modification (Read-Only Audit)

The following existing files will be modified in the future implementation phase (none are modified in Phase 4):
1. `astra_sec/dashboard/static/index.html`: Add `<div id="cesiumContainer">` container and vendor script tags.
2. `astra_sec/dashboard/app.py`: Add endpoint `/api/trials/{id}/raw` to stream raw JSONL experiment logs for historical replay.
3. `Makefile`: Add target `download-cesium` to fetch and extract verified offline Cesium assets.
