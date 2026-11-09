# ASTRA-Sec Phase 4: Performance, Rendering Limits, and Scalability Assessment

## 1. Performance Engineering Scope

The 3D Mission Control component must maintain high visual fidelity and continuous 60 FPS animation without degrading backend responsiveness, stalling telemetry collection, or causing browser tab memory leaks.

This document analyzes the computational profile, rendering bottlenecks, and scalability characteristics of the leading candidates.

---

## 2. Rendering Pipeline & Bottleneck Analysis

### 2.1. WebGL Draw-Call and Memory Bottlenecks
In browser-based 3D applications, performance is bounded by three critical constraints:
1. **CPU-to-GPU Draw Calls**: Excessive draw calls (> 1,000 per frame) degrade frame rates on standard laptops.
   - *CesiumJS*: Automatically batches polylines and billboarding primitives via internal vertex buffers (`PolylineCollection`, `BillboardCollection`).
   - *Three.js / globe.gl*: Standard meshes create individual draw calls unless explicitly batched using `InstancedMesh`.
2. **WebGL Context Overhead**: Multiple 3D canvases or frequent context reinstantiations can exceed browser limits (typically 8–16 WebGL contexts per browser session). A single shared WebGL canvas must host the entire globe and constellation.
3. **Garbage Collection (GC) Stutters**: In high-throughput messaging (e.g. 50+ packets/sec), creating temporary JavaScript vectors and objects inside the animation loop triggers frequent V8 GC pauses. Cesium's scratch variables (`Cartesian3.clone(val, resultScratch)`) prevent heap allocations during animation frames.

---

## 3. Scalability Assessment Across Scenarios

| Operational Scenario | Number of Nodes | Moving Packets | CesiumJS Capability | globe.gl Capability | Three.js Capability |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ASTRA-Sec 4-Node Testbed** | 4 nodes (2 ground, 2 LEO) | 1–10 active | **60 FPS** (< 5% GPU load) | **60 FPS** (< 5% GPU load) | **60 FPS** (< 5% GPU load) |
| **Multi-Hop Relay Chain** | 10 satellites | 10–50 active | **60 FPS** (~8% GPU load) | **60 FPS** (~10% GPU load) | **60 FPS** (with custom code) |
| **Walker Constellation** | 66 satellites (e.g. Iridium) | 50–200 active | **60 FPS** (~15% GPU load) | **35–45 FPS** (Geometry lag) | **60 FPS** (if InstancedMesh used) |
| **Mega-Constellation (Future)** | 1,000+ satellites | 500+ active | **45–60 FPS** (`PointPrimitiveCollection`) | **< 15 FPS** (Severe UI freeze) | **30–50 FPS** (Compute shaders) |

---

## 4. Controlled Performance Benchmark Protocol (Future Implementation Phase)

To verify real-world rendering performance empirically in the next implementation phase, a standardized benchmark suite will be executed measuring:
1. **Steady-State Frame Rate (FPS)**: Under idle globe rotation vs. active packet animation.
2. **Animation Loop Execution Time**: Target: $< 16.6\text{ ms}$ total frame time (10 ms render + 6 ms JavaScript execution).
3. **Browser Memory Footprint**: Process RSS growth over a 30-minute continuous telemetry stream (target: $< 25\text{ MB}$ net heap growth).
4. **WebSocket Ingestion Latency**: Delay between `/ws/live` packet receipt and visual property update (target: $< 10\text{ ms}$).
