# ASTRA-Sec Phase 4: Licensing, Dependency, and Supply-Chain Risk Analysis

## 1. Compliance & Security Scope

Because ASTRA-Sec is developed as a rigorous, open scientific research project intended for academic publication, open-source release, and live demonstrations, the visualization foundation must satisfy strict licensing and operational requirements:
1. **Permissive Open-Source Licensing**: Free from copyleft viral clauses (e.g., GPL/AGPL).
2. **Commercial & Non-Commercial Freedom**: Suitable for research, defense, and aerospace testbeds.
3. **Zero Mandatory Paid Subscriptions**: Must not require commercial SaaS accounts, paid API keys, or credit cards.
4. **100% Offline Capability**: Must operate completely air-gapped on isolated testbed networks without phoning home to external servers.

---

## 2. Licensing Forensics Across Candidates

### 2.1. CesiumJS (`CesiumGS/cesium`)
* **Primary License**: **Apache License 2.0**
  - Permits commercial and non-commercial use, modification, distribution, and patent grant.
  - Requires preservation of copyright notices and license text.
  - No copyleft restrictions on proprietary code integrating with it.
* **Cesium ion Risk Analysis**:
  - *Perception*: Many developers erroneously believe CesiumJS requires a paid "Cesium ion" subscription.
  - *Reality*: The CesiumJS software engine is 100% open source under Apache 2.0. "Cesium ion" is merely an optional commercial cloud asset hosting service (providing Cesium World Terrain, Bing Maps imagery, and 3D building tiles).
  - *Offline Mitigation*: By explicitly initializing `Cesium.Viewer` with:
    ```javascript
    const viewer = new Cesium.Viewer("cesiumContainer", {
      baseLayer: Cesium.ImageryLayer.fromProviderAsync(
        Cesium.TileMapServiceImageryProvider.fromUrl(
          Cesium.buildModuleUrl("Assets/Textures/NaturalEarthII") // Built-in offline asset
        )
      ),
      terrainProvider: new Cesium.EllipsoidTerrainProvider(), // Offline WGS84 smooth ellipsoid
      baseLayerPicker: false,
      geocoder: false,
      animation: true,
      timeline: true
    });
    ```
    CesiumJS never makes an outbound network request, never prompts for an API key, and runs completely offline.
* **Risk Level**: **LOW (Mitigated by configuration)**.

---

### 2.2. satellite.js (`shashwatak/satellite-js`)
* **Primary License**: **MIT License**
  - Extremely permissive.
  - No dependency on external web APIs, cloud services, or external assets.
  - Pure in-memory mathematical computation.
* **Risk Level**: **ZERO RISK**.

---

### 2.3. Three.js (`mrdoob/three.js`)
* **Primary License**: **MIT License**
  - Permissive open-source license.
  - Offline capability is 100% native (developers supply their own textures/geometry).
* **Risk Level**: **ZERO RISK**.

---

### 2.4. globe.gl (`vasturiano/globe.gl`)
* **Primary License**: **MIT License**
  - Permissive open-source license.
  - Default examples fetch Earth surface imagery from Unpkg or GitHub raw URLs (`//unpkg.com/three-globe/example/img/earth-night.jpg`).
  - *Offline Requirement*: Local assets (texture PNGs) must be hosted on the local static server to prevent remote CDN dependencies.
* **Risk Level**: **LOW (Mitigated by local asset hosting)**.

---

## 3. Dependency Risk & Supply-Chain Matrix

| Candidate | Primary License | Direct Runtime Deps | External Cloud Services | Air-Gapped / Offline Feasibility | Overall Risk Rating |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CesiumJS** | Apache 2.0 | 5 (`@cesium/engine`, `@cesium/widgets`, `@cesium/core`, `@cesium/gltf`, `protobufjs`) | Optional (Cesium ion) — Can be completely disabled | **100% Offline** with built-in NaturalEarthII texture and ellipsoid | **LOW** |
| **satellite.js** | MIT | 0 (Zero dependencies) | None | **100% Offline** (Pure in-memory math) | **NEGLIGIBLE** |
| **Three.js** | MIT | 0 (Zero dependencies) | None | **100% Offline** (Manual asset loading) | **NEGLIGIBLE** |
| **globe.gl** | MIT | 5 (`three`, `three-globe`, `three-render-objects`, `@tweenjs/tween.js`, `kapsule`) | None (Uses CDN textures by default) | **100% Offline** if textures downloaded locally | **LOW** |

---

## 4. Policy Conclusion

Both **CesiumJS** (Apache 2.0) and **satellite.js** (MIT) satisfy all licensing, intellectual property, and air-gapped security policies. By explicitly configuring CesiumJS to use local imagery textures and the standard WGS84 ellipsoid without Cesium ion tokens, the solution maintains total independence from commercial external services.
