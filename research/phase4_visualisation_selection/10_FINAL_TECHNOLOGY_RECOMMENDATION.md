# ASTRA-Sec Phase 4: Final Technology Recommendation

## 1. Primary Recommendation: The Approved Visual Foundation

Based on rigorous source-code forensics, mathematical orbital requirements, licensing verification, and compatibility with the existing ASTRA-Sec architecture, the primary recommendation is:

### **Primary 3D Rendering Engine: CesiumJS**
* **Repository**: https://github.com/CesiumGS/cesium
* **License**: **Apache License 2.0**
* **Role**: Primary 3D Virtual Globe, WGS84 Geodetic Coordinate Engine, Spacecraft Entity Manager, Dynamic Link Polyline Renderer, and In-Transit Packet Animator.

### **Companion Orbital Mechanics Engine: satellite.js**
* **Repository**: https://github.com/shashwatak/satellite-js
* **License**: **MIT License**
* **Role**: Lightweight Client-Side SGP4/SDP4 Propagator converting NORAD Two-Line Element (TLE) sets into Earth-Centered Inertial (TEME/ECI) coordinates for high-accuracy constellation tracking.

---

## 2. Why CesiumJS Outperformed All Alternatives

1. **Native Aerospace Coordinate Frames**:
   CesiumJS is the only open-source web engine with built-in native support for **Earth-Centered Inertial (`ReferenceFrame.INERTIAL`)** coordinate systems. In low-Earth orbit, satellites travel in an inertial orbital plane while the Earth rotates underneath them. CesiumJS renders this astronomical reality natively without manual matrix transformations.
2. **Time-Dynamic Entity Interpolation**:
   Cesium's `SampledPositionProperty` allows packets, satellites, and acknowledgments to be animated using exact microsecond timestamps matching ASTRA-Sec's Phase 2 and Phase 3 telemetry records. It handles polynomial interpolation (Lagrange / Hermite) automatically.
3. **Timeline Scrubbing and Historical Replay**:
   CesiumJS includes built-in `Timeline` and `Animation` clock controllers (`JulianDate`, `viewer.clock`). An experimenter can pause, scrub backward, or replay historical Phase 3 experimental trials from raw JSONL files without implementing a custom playback slider.
4. **Direct Compatibility with Vanilla HTML5 Frontend**:
   CesiumJS distributes standalone pre-built UMD and ES modules that mount into a standard `<div>` in `index.html` alongside the existing FastAPI backend. It does **not** require rebuilding the application around a heavy Node.js/React framework.

---

## 3. Why the Closest Alternatives Were Not Selected

### Why Not `globe.gl`?
While `globe.gl` is visually appealing and straightforward to configure, it is fundamentally a **2.5D spherical data-graph component**, not an aerospace simulation engine:
- It models the Earth as an unflattened, perfect sphere, distorting geodetic altitudes.
- It cannot render satellites in an inertial space frame (satellites rotate rigidly with the Earth texture).
- It lacks time-sampled entity interpolation; packet bursts are anonymous dash animations along arcs, making it impossible to click an individual in-transit packet to inspect its unique `envelope_id`, ML-KEM ciphertext bytes, or ML-DSA signature status.

### Why Not Pure Three.js / React Three Fiber?
Three.js is an exceptional general-purpose 3D graphics library, but selecting it would force the research team to write:
- Custom WGS84 geodetic-to-Cartesian coordinate projection algorithms.
- Custom tiled imagery and terrain loading systems.
- Custom celestial ephemeris and inertial frame coordinate converters.
- Custom timeline and historical scrubbing machinery.
Developing these geospatial primitives from scratch would divert engineering resources away from ASTRA-Sec's core post-quantum cryptographic resilience and DTN research.

---

## 4. Native Capabilities vs. Custom Development Required

| Capability | CesiumJS Native Feature | Required Custom Implementation |
| :--- | :--- | :--- |
| **WGS84 3D Earth** | Built-in (`Ellipsoid.WGS84`) | None (Configure offline NaturalEarthII texture) |
| **Spacecraft Entities** | Built-in GLTF/GLB model loader & billboard markers | Acquire/provide simple low-poly satellite `.glb` model |
| **Dynamic Links** | Built-in `PolylineGlowMaterialProperty` | Link state color manager (Cyan = Active, Red = Outage) |
| **Packet Movement** | Built-in `SampledPositionProperty` | Ingestion mapper translating `/ws/live` events to path samples |
| **Telemetry HUD** | Built-in infoBox & ScreenSpaceEventHandler | Custom CSS HUD cards matching ASTRA-Sec dark theme |
| **SGP4 Propagation** | Handled by companion `satellite.js` | Glue script converting `satellite.propagate()` output to `Cartesian3` |
| **Timeline Replay** | Built-in `viewer.timeline` & `viewer.clock` | JSONL parser loading experiment records into timeline intervals |

---

## 5. Licensing, Governance, and Deployment Assurance

- **Zero Commercial Lock-in**: CesiumJS and satellite.js are 100% free for commercial and non-commercial research under Apache 2.0 and MIT licenses.
- **Air-Gapped Operation**: Initializing Cesium with `baseLayerPicker: false`, `geocoder: false`, and local textures ensures zero outbound network calls, fulfilling strict space-laboratory air-gap security constraints.
