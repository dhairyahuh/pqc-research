# ASTRA-Sec Phase 4: Evidence-Based Candidate Comparison Matrix

## 1. Weighted Evaluation Methodology

Candidates are evaluated across 11 standardized criteria reflecting the operational and scientific needs of ASTRA-Sec. Each criterion is assigned an explicit weight summing to 100 points. Candidates are scored on a scale from 1 (unsuitable / absent) to 10 (flawless native capability).

---

## 2. Comprehensive Comparison Matrix

| # | Evaluation Criterion | Weight | CesiumJS | globe.gl | Three.js | React Three Fiber |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **C1** | **3D Globe & Geospatial Capability** | **15** | **10** (15.0) | **6** (9.0) | **4** (6.0) | **4** (6.0) |
| **C2** | **Dynamic Entities & Animation** | **15** | **10** (15.0) | **6** (9.0) | **7** (10.5) | **8** (12.0) |
| **C3** | **Satellite / Orbital Integration** | **10** | **10** (10.0) | **4** (4.0) | **4** (4.0) | **4** (4.0) |
| **C4** | **Frontend / React Integration** | **10** | **8** (8.0) | **9** (9.0) | **7** (7.0) | **10** (10.0) |
| **C5** | **Event-Driven Update Suitability** | **10** | **9** (9.0) | **7** (7.0) | **8** (8.0) | **8** (8.0) |
| **C6** | **Performance & Scalability Potential** | **10** | **9** (9.0) | **5** (5.0) | **9** (9.0) | **8** (8.0) |
| **C7** | **Extensibility & Custom Rendering** | **10** | **8** (8.0) | **5** (5.0) | **10** (10.0) | **9** (9.0) |
| **C8** | **Maintenance & Ecosystem Health** | **5** | **10** (5.0) | **7** (3.5) | **10** (5.0) | **9** (4.5) |
| **C9** | **Licensing & Dependency Safety** | **5** | **9** (4.5) | **9** (4.5) | **10** (5.0) | **10** (5.0) |
| **C10**| **Offline / Local Deployment** | **5** | **9** (4.5) | **8** (4.0) | **10** (5.0) | **10** (5.0) |
| **C11**| **Initial Integration Effort** | **5** | **7** (3.5) | **10** (5.0) | **4** (2.0) | **4** (2.0) |
| **TOTAL**| **Weighted Cumulative Score** | **100** | **91.5 / 100** | **65.0 / 100** | **70.5 / 100** | **73.5 / 100** |

---

## 3. Criterion-by-Criterion Justification and Evidence

### C1. 3D Globe & Geospatial Capability (Weight: 15)
- **CesiumJS (Score: 10/10)**: Native WGS84 oblate spheroid model, full geodetic coordinate math, terrain and tiled imagery pyramids, accurate solar ephemeris and atmospheric scattering.
- **globe.gl (Score: 6/10)**: Renders a simple sphere with a 2D texture wrapped around it. Does not model ellipsoidal flattening or elevation.
- **Three.js / R3F (Score: 4/10)**: No built-in geospatial concepts. Everything from latitude/longitude conversion to surface projection must be coded manually.

### C2. Dynamic Entities & Animation (Weight: 15)
- **CesiumJS (Score: 10/10)**: Purpose-built `SampledPositionProperty` with polynomial interpolation, velocity-oriented rotation (`VelocityOrientationProperty`), and CZML time-series packet streaming.
- **Three.js / R3F (Score: 7–8/10)**: Powerful animation mixers and particle systems, but requires manual calculation of 3D trajectory paths over an orbital sphere.
- **globe.gl (Score: 6/10)**: Animates dashes along arcs using `tween.js`, but does not support individually queryable moving packet entities with custom metadata.

### C3. Satellite / Orbital Integration (Weight: 10)
- **CesiumJS (Score: 10/10)**: Natively supports Earth-Centered Inertial (ECI / `ReferenceFrame.INERTIAL`) frames where the Earth rotates underneath the orbital plane. Integrates seamlessly with SGP4 propagation from `satellite.js`.
- **globe.gl (Score: 4/10)**: Only supports Earth-fixed spherical rotation. Orbiting satellites would unrealistically rotate synchronously with Earth longitude unless custom matrices are injected.
- **Three.js / R3F (Score: 4/10)**: Requires manual matrix math to decouple rotating Earth mesh from an inertial satellite plane.

### C4. Frontend / React Integration (Weight: 10)
- **R3F (Score: 10/10)**: Native React reconciler.
- **globe.gl (Score: 9/10)**: Exists as both vanilla `globe.gl` and turnkey `react-globe.gl`.
- **CesiumJS (Score: 8/10)**: Works seamlessly in vanilla HTML5/ES6 (matching ASTRA-Sec's existing dashboard) and in React via `useRef` or `Resium`.

### C5. Event-Driven Update Suitability (Weight: 10)
- **CesiumJS (Score: 9/10)**: Direct mutation of entity properties (`label.text`, `polyline.material`) without recreating scene nodes.
- **Three.js / R3F (Score: 8/10)**: Direct updates to object transforms and buffer attributes.
- **globe.gl (Score: 7/10)**: Accessor functions require re-feeding array data for updates.

### C6. Performance & Scalability Potential (Weight: 10)
- **CesiumJS (Score: 9/10)**: Automatically batches primitives (`PolylineCollection`, `PointPrimitiveCollection`) supporting 1,000+ satellites at 60 FPS.
- **Three.js (Score: 9/10)**: Maximum raw WebGL performance potential if custom instancing is implemented.
- **globe.gl (Score: 5/10)**: Noticeable frame rate drops when scaling to large numbers of custom 3D mesh layers.

### C7. Extensibility & Custom Rendering (Weight: 10)
- **Three.js (Score: 10/10)**: Complete control over raw GLSL shaders, post-processing passes, and custom scene graph nodes.
- **CesiumJS (Score: 8/10)**: Highly extensible via custom primitives, post-processing stages, and GLTF shader overrides, though wrapped in geospatial abstractions.
- **globe.gl (Score: 5/10)**: Constrained by opinionated layer abstractions.

### C8. Maintenance & Ecosystem Health (Weight: 5)
- **CesiumJS (Score: 10/10)**: Predominant industry standard for aerospace, military, and commercial space tracking; monthly releases, backed by Cesium Inc. / Bentley.
- **Three.js (Score: 10/10)**: Premier 3D web library worldwide.
- **globe.gl (Score: 7/10)**: Maintained by individual creator (Vasco Asturiano); healthy but smaller community.

### C9. Licensing & Dependency Safety (Weight: 5)
- **Three.js / R3F (Score: 10/10)**: MIT License, zero vendor ties.
- **CesiumJS (Score: 9/10)**: Apache 2.0. Optional cloud service (Cesium ion) can be completely disabled for 100% offline compliance.
- **globe.gl (Score: 9/10)**: MIT License, requires local hosting of textures to eliminate CDN dependencies.

### C10. Offline / Local Deployment (Weight: 5)
- **Three.js (Score: 10/10)**: 100% local.
- **CesiumJS (Score: 9/10)**: 100% local using `EllipsoidTerrainProvider` and local NaturalEarthII asset.
- **globe.gl (Score: 8/10)**: Requires localizing remote texture image URLs.

### C11. Initial Integration Effort (Weight: 5)
- **globe.gl (Score: 10/10)**: Simplest drop-in library for basic arcs.
- **CesiumJS (Score: 7/10)**: Requires initial configuration to disable ion widgets and set up entity structures.
- **Three.js / R3F (Score: 4/10)**: Highest effort due to requiring from-scratch development of geospatial coordinate transforms, ellipsoids, and camera controllers.
