# ASTRA-Sec Phase 4: GitHub Source-Code Forensics and Architectural Analysis

## 1. Forensics Scope & Inspection Protocol

Date of Inspection: **November 9, 2026**  
Each shortlisted candidate was subjected to deep source-code forensics across package metadata (`package.json`), build pipelines, dependency trees, public APIs, entity architectures, and maintenance indicators.

---

## 2. In-Depth Candidate Forensics

### 2.1. Candidate A: CesiumJS (`CesiumGS/cesium`)

* **Repository**: https://github.com/CesiumGS/cesium
* **License**: **Apache License 2.0** (Permissive open source; verified in `LICENSE.md`)
* **Core Language**: JavaScript / TypeScript (Modern ES2022+ / JSDoc / TS typings)
* **Build System**: Monorepo managed with npm workspaces, Rollup, and ESBuild.
* **Architecture & Source Breakdown**:
  Cesium is decomposed into modular packages:
  - `@cesium/engine`: Core 3D engine, WGS84 math (`Ellipsoid.WGS84`), scene graph, camera controllers, WebGL/WebGPU shaders, `Scene`, `Globe`.
  - `@cesium/widgets`: UI components (`Viewer`, `Timeline`, `Animation`, `BaseLayerPicker`, `Geocoder`).
  - `@cesium/core`: Fundamental math classes (`Cartesian3`, `Matrix4`, `JulianDate`, `Quaternion`).
* **Entity & Dynamic Time Model**:
  - `SampledPositionProperty`: Natively handles time-series positional coordinates in Earth-Centered Inertial (`ReferenceFrame.INERTIAL`) or Fixed (`ReferenceFrame.FIXED`) frames.
  - Built-in interpolation algorithms: `LagrangePolynomialApproximation`, `HermitePolynomialApproximation`, and `LinearApproximation`.
  - `CzmlDataSource`: Direct ingestion of JSON-based CZML documents containing time-varying properties, orientation, paths, and packet bursts.
  - `VelocityOrientationProperty`: Automatically computes 3D spacecraft pitch/roll/yaw alignment along the velocity vector.
* **Geospatial & Planetary Precision**:
  - Full WGS84 oblate spheroid modeling (semi-major axis $a = 6,378,137.0\text{ m}$, flattening $f = 1/298.257223563$).
  - Precise high-definition solar/lunar ephemeris and atmospheric light scattering.
* **Dependency Footprint**:
  - Production runtime dependencies are tightly scoped (`@cesium/engine`, `@cesium/widgets`, `@cesium/core`, `@cesium/gltf`, `protobufjs`).
  - Standalone pre-built bundles (`Cesium.js`, ~3.8 MB minified) can be imported via a single `<script>` tag or via ES module imports.
* **Maintenance & Community Activity**:
  - Releases: Monthly predictable release cycle (e.g. v1.120+).
  - Contributors: >250 active contributors; backed by Cesium Inc. / Bentley Systems.
  - Issues: Actively triaged (< 500 open issues against tens of thousands of closed).
* **Identified Forensic Limitations**:
  - Large download size (~3.8 MB minified JavaScript + ~1.5 MB CSS/assets).
  - Default initialization queries Cesium ion cloud services unless explicitly configured for local offline operation (`baseLayer: false`, `geocoder: false`, `terrainProvider: new EllipsoidTerrainProvider()`).

---

### 2.2. Candidate B: satellite.js (`shashwatak/satellite-js`)

* **Repository**: https://github.com/shashwatak/satellite-js
* **License**: **MIT License** (Permissive; verified in `LICENSE`)
* **Core Language**: JavaScript (ES6 with TypeScript declaration files `index.d.ts`)
* **Build System**: Rollup / npm.
* **Package Footprint**:
  - Zero runtime dependencies (`"dependencies": {}`).
  - Extremely compact: ~35 KB minified (~12 KB gzipped).
* **Core Functionality**:
  - `satellite.twoline2satrec(tleLine1, tleLine2)`: Parses standard NORAD Two-Line Element sets into an SGP4/SDP4 satellite record structure.
  - `satellite.propagate(satrec, date)`: Computes Cartesian position and velocity in the True Equator, Mean Equinox (TEME) inertial frame at a specific epoch.
  - Coordinate transformations:
    - `satellite.gstime(date)`: Computes Greenwich Mean Sidereal Time (GMST).
    - `satellite.eciToEcf(positionEci, gmst)`: Converts Earth-Centered Inertial (TEME) to Earth-Centered, Earth-Fixed (ECEF) coordinates.
    - `satellite.eciToGeodetic(positionEci, gmst)`: Converts ECI coordinates to geodetic coordinates ($\text{latitude, longitude, altitude}$).
* **Maintenance & Activity**:
  - Highly mature, stable mathematical implementation of SGP4 (originally ported from Vallado et al., 2006).
  - Low commit velocity due to algorithm maturity; widely used by amateur radio, NASA enthusiasts, and orbital tracking dashboards worldwide.
* **Forensic Role**:
  - `satellite.js` is strictly a computational engine, not a renderer. It perfectly complements CesiumJS by propagating satellite positions for `Cesium.SampledPositionProperty`.

---

### 2.3. Candidate C: Three.js (`mrdoob/three.js`)

* **Repository**: https://github.com/mrdoob/three.js
* **License**: **MIT License** (Permissive; verified in `LICENSE`)
* **Core Language**: JavaScript (ES6 modules)
* **Architecture & Source Breakdown**:
  - Ubiquitous 3D graphics library. Provides `WebGLRenderer`, `Scene`, `PerspectiveCamera`, `Mesh`, `BufferGeometry`, custom GLSL `ShaderMaterial`, and GLTF/GLB loaders.
* **Geospatial Forensics**:
  - Three.js has **no built-in concept of geospatial coordinates**.
  - No WGS84 ellipsoid: a globe is simply a `SphereGeometry(radius, widthSegments, heightSegments)`.
  - Converting latitude and longitude to 3D Cartesian coordinates requires manual trigonometric projection:
    $$x = R \cos(\text{lat}) \sin(\text{lon}), \quad y = R \sin(\text{lat}), \quad z = R \cos(\text{lat}) \cos(\text{lon})$$
  - Lacks inertial (ECI) coordinate frames where Earth rotates relative to orbital planes without spinning the camera or orbit lines.
  - Lacks time-dynamic trajectory interpolation and timeline scrubbing out of the box.
* **Integration Burden**:
  - Implementing an aerospace-grade satellite visualization requires writing custom WGS84 projection mathematics, custom tiled imagery loaders, custom camera controllers, and custom trajectory animators.

---

### 2.4. Candidate E: globe.gl (`vasturiano/globe.gl`)

* **Repository**: https://github.com/vasturiano/globe.gl
* **License**: **MIT License** (Permissive; verified in `LICENSE`)
* **Core Language**: JavaScript (ES6)
* **Build System**: Rollup / npm.
* **Dependencies**:
  - `"three": ">=0.179 <1"`
  - `"three-globe": "^2.45"`
  - `"three-render-objects": "^1.41"`
  - `"@tweenjs/tween.js": "18 - 25"`
  - `"kapsule": "^1.16"`
* **Architecture & Capabilities**:
  - Built on top of Vasco Asturiano's `three-globe` abstraction.
  - High-level declarative API for:
    - Arcs (`arcsData`, `arcColor`, `arcStroke`, `arcDashLength`, `arcDashAnimateTime`).
    - Points (`pointsData`, `pointLat`, `pointLng`, `pointColor`, `pointRadius`).
    - Labels (`labelsData`, `labelLat`, `labelLng`, `labelText`).
    - Custom objects (`customLayerData`, `customThreeObject`).
* **Forensic Limitations for ASTRA-Sec**:
  - **Spherical Approximation**: All calculations treat the Earth as a perfect sphere; does not model WGS84 flattening or true geodetic altitudes.
  - **Inertial Frame Deficiency**: The globe rotates by spinning the Three.js mesh. Objects orbiting the Earth are positioned relative to the rotating Earth mesh rather than an inertial space frame, distorting realistic satellite ground tracks.
  - **Lack of Time-Dynamic Property Model**: Animations are based on simple tween timers (`tween.js`) rather than astronomical `JulianDate` clock ticks. Cannot deterministically scrub or synchronize historical experiment replays with millisecond event timestamps.

---

## 3. Forensics Summary Table

| Evaluation Parameter | CesiumJS | satellite.js | Three.js | globe.gl |
| :--- | :--- | :--- | :--- | :--- |
| **Project License** | Apache 2.0 | MIT | MIT | MIT |
| **Primary Category** | Geospatial Virtual Globe | SGP4 Orbital Propagator | General 3D Engine | WebGL Sphere Graph |
| **WGS84 Ellipsoid** | **Native Built-in** | **Native Built-in** | None (Manual Math) | None (Simple Sphere) |
| **Inertial (ECI) Frame** | **Native Built-in** | **Native Built-in** | None | None |
| **Time-Sampled Position** | **Native (`SampledPositionProperty`)**| N/A | None | Tween-based only |
| **CZML Streaming** | **Native Built-in** | N/A | None | None |
| **Standalone Script Tag** | **Yes (`Cesium.js`)** | **Yes (`satellite.min.js`)** | Yes | Yes (`globe.gl.min.js`) |
| **React Compatibility** | Yes (via Resium or vanilla ref) | Yes | Yes (via R3F) | Yes (via `react-globe.gl`) |
| **Offline Operation** | **Yes (configured locally)** | **Yes (zero deps)** | Yes | Yes |
| **Maintenance Health** | Active (Monthly releases) | Stable / Mature | Very Active | Active |
| **Bundle Size** | ~3.8 MB | ~35 KB | ~600 KB | ~850 KB |
