# Phase 00: Integration Proposal & Architecture Plan
## ASTRA-Sec Development — Strategy for Integrating Monitored PQC into ASTRA-Sec

**Author:** ASTRA-Sec Development Agent  
**Date:** November 2026  
**Status:** Complete  
**Scope:** Evaluation of integration strategies between the audited PQC fault-resilience implementation and the incoming ASTRA-Sec communication architecture.

---

## 1. Context & Integration Objectives

ASTRA-Sec requires post-quantum cryptographic primitives (specifically NIST FIPS 203 ML-KEM-768 and FIPS 204 ML-DSA-65) with embedded fault resilience for high-reliability aerospace/space systems communications.

The existing research codebase in `pqc-research` provides:
1. Pure C99, zero-heap implementations of ML-KEM and ML-DSA.
2. Dual-transform algebraic invariant monitoring across 9,856 NTT butterfly operations.
3. In-place localized register rollback ($R_{max} = 2$) and persistent fail-stop containment.
4. Hardened Twiddle Factor Integrity Binding (`libtfib.a`).

The integration strategy must achieve:
- **Absolute Preservation:** The existing PQC research baseline must remain immutable and undisturbed.
- **Architectural Decoupling:** Fault-resilience mechanisms must not leak raw internal state into the outer ASTRA-Sec secure framing layer.
- **Target Portability:** Must compile seamlessly for workstation development (macOS/Linux) and embedded flight targets (ARM Cortex-M4/M7, RISC-V RV32IM, RTEMS).
- **Strict Cryptographic Boundary:** Zero heap allocation, deterministic memory consumption, and constant-time execution.

---

## 2. Comparative Evaluation of Integration Options

We evaluate four structural integration pathways:

| Evaluation Criterion | Option A: Git Submodule | Option B: Versioned Static Library (`libastra_pqc.a`) | Option C: Direct Source Import (In-Tree Vendor) | Option D: Hybrid Monitored Engine with C-ABI Header |
|---|:---:|:---:|:---:|:---:|
| **Preservation of Old Repo** | **High** (pointer only) | **High** (artifact boundary) | **Low** (source duplication risk) | **Highest** (isolated build target) |
| **Build Decoupling** | Medium (coupled sub-make) | **High** (links pre-built `.a`) | Low (monolithic compilation) | **High** (hermetic C-ABI barrier) |
| **Zero Heap / Stack Determinism** | High | **High** | Medium (compiler bleed) | **High** |
| **API Encapsulation** | Low (exposes internal hooks) | **High** (exports only public KEM) | Low (all internal headers exposed) | **Highest** (strict opaque context) |
| **Spaceborne RTOS Portability** | Medium (submodule paths) | High (cross-compiled archive) | High (source compiles into RTOS) | **Highest** (single C-ABI contract) |
| **Adversarial Auditability** | Medium | High | Low (diff pollution) | **High** |

---

## 3. Analysis of Options

### Option A: Git Submodule
- *Concept:* ASTRA-Sec repository includes `pqc-research` as a Git submodule at a pinned commit.
- *Pros:* Tracks upstream commit history directly without copying files.
- *Cons:* Submodules complicate continuous integration and flight software deployment. Internal fault-injection headers and research test harnesses bleed into production search paths. Submodule pointers can desynchronize in multi-developer environments.

### Option B: Separate Versioned Static Library (`libastra_pqc.a`)
- *Concept:* Build a standalone static archive `libastra_pqc.a` exposing standard cryptographic KEM/DSA calls, with internal fault resilience compiled in.
- *Pros:* Cleanest binary separation. ASTRA-Sec links `libastra_pqc.a` without knowing about NTT butterflies or invariant math.
- *Cons:* Debugging internal fault escalation across a binary boundary can obscure telemetry logging in aerospace testbeds.

### Option C: Carefully Audited Source Import (Vendoring)
- *Concept:* Copy audited files into an `astra_sec/crypto/vendor/` directory and compile monolithically.
- *Pros:* Simplifies single-pass cross-compilation for embedded targets (e.g., bare-metal ARM/RISC-V).
- *Cons:* High risk of code drift, file duplication, and breaking baseline reproducibility. Violates Prompt 01's constraint ("Do not copy the source yet").

### Option D: Recommended Strategy — Hybrid Hermetic Engine with Versioned C-ABI Export
- *Concept:* Maintain the existing PQC implementation in its dedicated repository root. Introduce a thin, audited C-ABI integration shim (`astra_pqc_interface.h` / `astra_pqc_engine.c`) that:
  1. Exports a strict, versioned, zero-heap cryptographic API (`astra_pqc_kem_encaps`, `astra_pqc_kem_decaps`).
  2. Encapsulates the 9,856 NTT butterfly invariant checks and TFIB reference binding internally.
  3. Maps persistent fail-stop containment directly to ASTRA-Sec fault telemetry counters (`astra_pqc_telemetry_t`) without exposing internal research hooks.
  4. Generates a standalone, hermetic static library (`libastra_pqc.a`) with formal CMake and Makefile export targets.

---

## 4. Architectural Recommendation & Rationale

**Recommendation:** **Option D (Hybrid Hermetic Engine with Versioned C-ABI Export)** is formally recommended.

### Why Option D is Safest:
1. **Zero Source Mutation:** Does not modify or duplicate any existing file in `algorithms/source_ref/` or `tfib_implementation/`.
2. **Deterministic C-ABI Contract:** Exposes only opaque, fixed-size byte buffers matching FIPS 203 parameters:
   - Public Key: 1,184 bytes
   - Ciphertext: 1,088 bytes
   - Shared Secret: 32 bytes
3. **Telemetry Integration:** Bridges the gap between research monitors and operational spacecraft FDIR (Fault Detection, Isolation, and Recovery) by mapping monitor counters to an aerospace telemetry struct:
   ```c
   typedef struct {
       uint32_t transient_recoveries;
       uint32_t persistent_fail_stops;
       uint32_t twiddle_faults_detected;
       bool sdc_prevention_engaged;
   } astra_pqc_telemetry_t;
   ```
4. **Embedded Flight Readiness:** Enables compiling for workstation simulation, NASA Core Flight System (cFS), or bare-metal RTEMS with zero code changes.

---

## 5. Phased Integration Roadmap

| Milestone | Target Deliverable | Dependencies |
|---|---|---|
| **Phase 00 (Current)** | Complete repository audit, preservation baseline, environment logging. | None |
| **Phase 01** | C-ABI Interface Definition (`astra_pqc_interface.h`) & Telemetry Contract. | Phase 00 Approval |
| **Phase 02** | Hermetic Build Target (`libastra_pqc.a`) & Static Linker Validation. | Phase 01 Interface |
| **Phase 03** | ASTRA-Sec Key Encapsulation Protocol Integration & Zero-Heap Session Handshake. | Phase 02 Library |
| **Phase 04** | End-to-End Fault-Tolerant Communication Campaign & FDIR Telemetry Validation. | Phase 03 Protocol |
