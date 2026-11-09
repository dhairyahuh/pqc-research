# ASTRA-Sec Phase 4: Open-Source Repository Discovery and Landscape Survey

## 1. Survey Scope & Methodology

To identify the most viable open-source 3D geospatial foundation for ASTRA-Sec, a systematic survey of available open-source software was conducted on November 9, 2026. The search evaluated candidates across five distinct architectural categories:
1. **Full-Featured Geospatial Virtual Globes**: Engines natively providing WGS84 ellipsoids, digital elevation models, geospatial coordinate systems, and entity animation.
2. **General-Purpose 3D Web Rendering Frameworks**: Low-level 3D engines capable of rendering arbitrary meshes and scenes, requiring custom geospatial math.
3. **Declarative Component-Wrapped Globes**: Higher-level libraries that encapsulate 3D spheres and network graphs into turnkey web components.
4. **Orbital Propagation Companion Libraries**: Mathematical libraries calculating Keplerian and SGP4/SDP4 satellite state vectors from Two-Line Element (TLE) sets.
5. **Geospatial Big-Data & Layer Visualization Libraries**: Frameworks focusing on large-scale geospatial layers and data science over maps.

---

## 2. Investigated Candidates

### 2.1. Candidate A: CesiumJS (`CesiumGS/cesium`)
- **Repository**: https://github.com/CesiumGS/cesium
- **Category**: Geospatial 3D Virtual Globe Engine
- **Core Technology**: WebGL / WebGPU, WGS84 ellipsoid, CZML streaming, 3D Tiles, Entity API.
- **Initial Assessment**: The industry standard for aerospace, satellite tracking, defense, and GIS applications. Natively handles inertial (ECI) and fixed (ECEF) reference frames, time-dynamic sampled positions, and camera tracking.

---

### 2.2. Candidate B: satellite.js (`shashwatak/satellite-js`)
- **Repository**: https://github.com/shashwatak/satellite-js
- **Category**: Orbital Mechanics & SGP4/SDP4 Companion Library
- **Core Technology**: JavaScript port of SGP4/SDP4 orbit propagation algorithms.
- **Initial Assessment**: Not a visual rendering engine. Pure mathematical library converting Two-Line Elements (TLEs) into Cartesian coordinates (TEME/ECI/ECEF) and geodetic coordinates (lat, lon, alt). Essential companion library if physical orbital mechanics are added to visual nodes.

---

### 2.3. Candidate C: Three.js (`mrdoob/three.js`)
- **Repository**: https://github.com/mrdoob/three.js
- **Category**: General-Purpose 3D WebGL Library
- **Core Technology**: WebGL scene graph, custom shaders, camera controls, mesh loaders, particle systems.
- **Initial Assessment**: Extremely mature and ubiquitous 3D graphics library. However, it lacks native concepts of geospatial ellipsoids (WGS84), geodetic coordinates, GIS tile pyramids, or orbital frames. Building an accurate Earth with terrain, atmosphere, and coordinate projections requires substantial custom development.

---

### 2.4. Candidate D: React Three Fiber (`pmndrs/react-three-fiber`)
- **Repository**: https://github.com/pmndrs/react-three-fiber
- **Category**: React Reconciler for Three.js
- **Core Technology**: Declarative Three.js scene composition using React components and hooks.
- **Initial Assessment**: Excellent developer ergonomics for React applications, but inherits all Three.js limitations regarding geospatial coordinate conversions. Furthermore, the existing ASTRA-Sec dashboard currently uses vanilla HTML5/ES6 and FastAPI rather than a heavy React bundler.

---

### 2.5. Candidate E: globe.gl (`vasturiano/globe.gl`)
- **Repository**: https://github.com/vasturiano/globe.gl
- **Category**: WebGL 3D Globe Visualization Component
- **Core Technology**: Built on `three-globe` and Three.js. Provides turnkey layers for arcs, points, labels, and heatmaps.
- **Initial Assessment**: Extremely easy to integrate into vanilla HTML5 applications (`<script src="globe.gl">`). Excellent visual appeal for animated arcs and pulses. However, the globe is rendered as a simple sphere, lacks inertial coordinate frames (Earth cannot rotate underneath an inclined satellite orbit), and cannot natively parse CZML or time-sampled trajectory properties.

---

### 2.6. Candidate F: react-globe.gl (`vasturiano/react-globe.gl`)
- **Repository**: https://github.com/vasturiano/react-globe.gl
- **Category**: React Wrapper for `globe.gl`
- **Core Technology**: `globe.gl` + `react-kapsule`.
- **Initial Assessment**: Wrapper around `globe.gl` for React environments. Offers identical rendering capabilities and identical limitations as `globe.gl`.

---

### 2.7. Candidate G: Resium (`reearth/resium`)
- **Repository**: https://github.com/reearth/resium
- **Category**: React Component Wrapper for CesiumJS
- **Core Technology**: Declarative React components for Cesium entities, primitives, and viewer.
- **Initial Assessment**: Combines the aerospace-grade rigor of CesiumJS with React declarative ergonomics. Highly relevant if the frontend migrates to React.

---

### 2.8. Candidate H: NASA WorldWind / WebWorldWind (`NASAWorldWind/WebWorldWind`)
- **Repository**: https://github.com/NASAWorldWind/WebWorldWind
- **Category**: Virtual Globe SDK
- **Core Technology**: NASA-developed 3D virtual globe for web browsers.
- **Initial Assessment**: Highly respected NASA heritage for geospatial applications. However, project activity has substantially declined over recent years with infrequent releases, whereas CesiumJS has continuous monthly releases and widespread active maintenance.

---

### 2.9. Candidate I: deck.gl (`visgl/deck.gl`)
- **Repository**: https://github.com/visgl/deck.gl
- **Category**: Large-Scale Geospatial Data Visualization
- **Core Technology**: WebGL2 / WebGPU-powered data layer framework by Vis.gl / Uber.
- **Initial Assessment**: Outstanding for rendering millions of points and paths over 2D/2.5D map projections (Mapbox/MapLibre). GlobeView is supported, but it is not optimized for aerospace 3D orbital mechanics, satellite orientation, or space-frame animations.

---

## 3. Discovery Summary & Selected Shortlist

Based on initial architectural alignment with ASTRA-Sec's satellite communication requirements, the following top four candidates were shortlisted for rigorous source-code forensics:

1. **CesiumJS** (Primary 3D Geospatial Virtual Globe Engine)
2. **globe.gl** (Lightweight Sphere & Network Arc Alternative)
3. **Three.js** (Custom 3D Engine Baseline)
4. **satellite.js** (Essential SGP4 Companion Library)
