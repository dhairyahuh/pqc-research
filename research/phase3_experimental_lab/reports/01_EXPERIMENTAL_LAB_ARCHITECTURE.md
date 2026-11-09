# ASTRA-Sec Phase 3: Experimental Laboratory Architecture

## 1. Executive Summary

This document describes the architectural design, implementation structure, and execution framework of the ASTRA-Sec Phase 3 Reproducible Experimental Laboratory. The laboratory is engineered to provide rigorous, automated, and mathematically verifiable measurement of the 7-layer ASTRA-Sec communication pipeline alongside classical and post-quantum cryptographic baselines.

The laboratory operates directly on the core pipeline verified in Phase 2, adhering to the principle that experimental measurements must execute against actual operational software rather than detached mock models or synthetic simulations.

---

## 2. Laboratory Architectural Model

The experimental laboratory is organized into modular subsystems decoupled through strict interfaces:

```
+-----------------------------------------------------------------------------------+
|                           CLI & Scenario Runner                                   |
|                        (scripts/run_phase3_lab.py)                                |
+-----------------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------------+
|                        Harness Experiment Orchestrator                            |
|        - Config Validator (Pydantic v2 Schema & SHA-256 Config Hash)              |
|        - Workload Dispatcher (Steady-State Rate Throttling / Concurrency)         |
|        - Telemetry & Resource Monitor (Real-time psutil CPU / RSS / Disk WAL)     |
|        - Statistical Engine (Parametric & Non-Parametric Metrics, Cohen's d)     |
+-----------------------------------------------------------------------------------+
           |                                  |                        |
           v                                  v                        v
+-----------------------+         +-----------------------+  +----------------------+
|  Experiment Adapters  |         | Impairment Controller |  |   Fault Controller   |
|  - AstraSecTreatment  | <-----> | - Injected Latency    |  | - NTT Butterfly SEU  |
|  - BaselineNonPqc     |         | - Deterministic Jitter|  | - Stuck Register     |
|  - BaselineUnmonitPqc |         | - Drop / Duplicate    |  | - Twiddle Persistent |
+-----------------------+         +-----------------------+  +----------------------+
           |
           v
+-----------------------------------------------------------------------------------+
|                         Core 4-Node Network Pipeline                              |
|           GSA (Sender) -> SAT1 (Relay) -> SAT2 (Relay) -> GSB (Receiver)          |
|                 [L2/L3 E2E Crypto, L5 DTN Spooling, L6 Recovery]                  |
+-----------------------------------------------------------------------------------+
           |
           v
+-----------------------------------------------------------------------------------+
|                       Output & Provenance Artifacts                               |
|       - Raw Measurements (JSONL per message with microsecond timestamps)          |
|       - Cryptographic Provenance Manifests (Git commit, dirty, seed, hash)        |
+-----------------------------------------------------------------------------------+
```

---

## 3. Core Subsystems

### 3.1. Experiment Adapters (`research/phase3_experimental_lab/adapters/`)
All experiments interact with communication stacks through the abstract `ExperimentAdapter` interface (`base.py`):
1. **`AstraSecTreatmentAdapter`**: Instantiates the production 4-node pipeline (`GroundStationSender`, `SatelliteRelayNode` 1 & 2, `GroundStationVerifier`). Executes full ML-KEM-768 key encapsulation, ML-DSA-65 digital signatures, AES-256-GCM AEAD encryption, canonical CBOR wire serialization, DTN bundle spooling, and reverse-path ML-DSA-65 signed acknowledgments.
2. **`BaselineNonPqcAdapter`**: Instantiates a conventional pre-quantum communication pipeline using AES-256-GCM authenticated encryption and HMAC-SHA256 signatures, isolating the exact overhead of post-quantum cryptographic primitives.
3. **`BaselineUnmonitoredPqcAdapter`**: Instantiates the 4-node pipeline using standard unmonitored LibOQS ML-KEM-768 and ML-DSA-65 primitives, isolating the computational overhead and fault-detection efficacy of ASTRA-Sec's native monitored C implementation.

### 3.2. Deterministic Workload Generator (`research/phase3_experimental_lab/workloads/`)
- Generates reproducible pseudo-random byte payloads of parameterized size (16 B to 1 MB) using seed-derived PRNGs.
- Supports precision rate throttling via high-resolution sleep timers, steady-state dispatching, and thread-pooled concurrency.

### 3.3. Deterministic Network Impairment Engine (`research/phase3_experimental_lab/impairments/`)
- Intercepts bundles across relay links without modifying application data.
- Injects deterministic Gaussian or fixed delay, millisecond jitter, uniform pseudo-random packet loss, packet duplication, out-of-order reordering, and timed contact schedule outages.

### 3.4. Cryptographic Fault Injection Engine (`research/phase3_experimental_lab/fault_campaigns/`)
- Operates at Layer 4 (C cryptographic execution layer).
- Injects bit flips into intermediate NTT butterfly calculations ($r \equiv t\zeta \pmod q$), twiddle factor ROM tables, and wire ciphertext/signature buffers.
- Tracks detection, rollback recovery, fail-stop containment, and silent data corruption (SDC) occurrences.

### 3.5. System Resource Monitor & Collector (`research/phase3_experimental_lab/harness/collector.py`)
- Continuously samples process CPU percentage, Resident Set Size (RSS), peak memory usage, and spool storage growth on disk.
- Overhead of monitoring is sub-millisecond (< 50 $\mu$s per measurement).

### 3.6. Provenance Manifest Engine (`research/phase3_experimental_lab/harness/manifest.py`)
- Generates immutable JSON manifest files for every completed trial.
- Captures environment metadata: exact Git commit SHA-1, branch, dirty tree state, Python version, OS architecture, hardware CPU core count, total RAM, SHA-256 configuration hash, and high-precision UTC timestamps.

---

## 4. Execution Pipeline & File Structure

```
research/phase3_experimental_lab/
├── configs/                     # Canonical experiment definitions (Pydantic validated)
│   ├── pilot.json
│   ├── group_a_baseline_non_pqc.json
│   ├── group_b_baseline_unmonitored_pqc.json
│   ├── group_d_full_astra_sec.json
│   ├── group_e_payload_scaling.json
│   ├── group_f_concurrency.json
│   ├── group_g_impairment.json
│   └── group_j_fault_campaign.json
├── harness/                     # Laboratory orchestration and collection
│   ├── config.py                # Schema & SHA-256 hash calculation
│   ├── collector.py             # Hardware & system telemetry sampler
│   ├── manifest.py              # Provenance manifest generator
│   └── orchestrator.py          # Campaign execution harness
├── adapters/                    # Concrete communication pipeline adapters
│   ├── base.py
│   ├── astra_adapter.py
│   ├── baseline_non_pqc.py
│   └── baseline_unmonitored_pqc.py
├── workloads/                   # Deterministic workload generators
│   └── generator.py
├── impairments/                 # Network channel impairment simulation
│   └── network.py
├── fault_campaigns/             # Cryptographic fault injection controller
│   └── controller.py
├── analysis/                    # Statistical distribution and hypothesis testing
│   └── stats.py
├── tests/                       # Laboratory self-test and verification suite
│   ├── test_lab_config.py
│   ├── test_lab_orchestrator.py
│   └── test_lab_stats.py
├── results/                     # Execution artifacts (raw measurements & manifests)
│   ├── raw/                     # Line-delimited JSONL measurements
│   └── manifests/               # Cryptographic provenance manifests
└── reports/                     # Laboratory documentation and experimental findings
```
