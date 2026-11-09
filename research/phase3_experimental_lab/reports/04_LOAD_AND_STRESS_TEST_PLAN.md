# ASTRA-Sec Phase 3: Load and Stress Testing Methodology and Results

## 1. Load Testing Objectives

The load and stress testing suite evaluates the behavior of ASTRA-Sec under varying message rates, sustained throughput, payload scaling, and multi-threaded concurrency. The primary questions addressed are:
1. Does the pipeline maintain deterministic sub-millisecond serialization and steady-state throughput under rate limits?
2. How does end-to-end latency scale with application payload sizes ($512\text{ B}$ vs $4,096\text{ B}$)?
3. What are the concurrency characteristics and architectural boundaries when multiple threads access the cryptographic and DTN state engines?

---

## 2. Experimental Scenarios and Configurations

### 2.1. Group D: Baseline Full ASTRA-Sec Treatment (`EXP-D01-FULL-ASTRA`)
* **Configuration**: 10 messages, 512 B payload, rate-throttled at 20 msg/sec, concurrency = 1.
* **Measured Outcome**:
  - Total Dispatched: 10
  - Successfully Delivered: 10 (100.0%)
  - Throughput: 21.06 msg/sec
  - End-to-End Latency:
    - Median (P50): 14,925.21 $\mu$s (14.93 ms)
    - P95: 18,915.47 $\mu$s (18.92 ms)
    - P99: 19,906.19 $\mu$s (19.91 ms)
    - Mean $\pm$ Std: 15,248.80 $\pm$ 2,282.60 $\mu$s
    - 99% Confidence Interval: [12,903.00, 17,594.61] $\mu$s
  - Mean CPU Utilization: 18.55%
  - Peak RSS Memory: 94.91 MB

---

### 2.2. Group E: Payload Scaling (`EXP-E01-PAYLOAD-4KB`)
* **Configuration**: 10 messages, 4,096 B payload (8x payload size increase), rate 20 msg/sec, concurrency = 1.
* **Measured Outcome**:
  - Total Dispatched: 10
  - Successfully Delivered: 10 (100.0%)
  - Throughput: 21.26 msg/sec
  - End-to-End Latency:
    - Median (P50): 13,308.21 $\mu$s (13.31 ms)
    - P95: 13,999.47 $\mu$s (14.00 ms)
    - P99: 14,146.59 $\mu$s (14.15 ms)
    - Mean $\pm$ Std: 12,955.03 $\pm$ 1,036.24 $\mu$s
    - 99% Confidence Interval: [11,890.09, 14,019.96] $\mu$s
  - Mean CPU Utilization: 16.37%
  - Peak RSS Memory: 94.95 MB
* **Analysis**:
  - Increasing the payload from 512 B to 4,096 B did not increase latency significantly. Because AES-256-GCM hardware acceleration processes 4 KB in < 5 $\mu$s, the dominant latency factors remain post-quantum key encapsulation ($t_{origin} \approx 1\text{--}2\text{ ms}$) and ML-DSA-65 signature generation and verification.

---

### 2.3. Group F: Concurrency Stress (`EXP-F01-CONCURRENCY-4`)
* **Configuration**: 12 messages dispatched across 4 concurrent worker threads against a single shared GSA-GSB pipeline instance.
* **Measured Outcome**:
  - Total Attempted: 12
  - Delivered: 1 (8.33%)
  - Replay / Collision Failures: 11 (91.67%)
* **Architectural Discovery**:
  - Under unsynchronized multi-threaded dispatch, concurrent threads generated identical sequence numbers and interleaved Double Ratchet state transitions, triggering `ReplayDetectedError: Replay detected: sequence 110 from 'dtn://gsa/app' was already processed`.
  - In a secure space communication channel, the Double Ratchet state is strictly sequential and monotonic per security association. Concurrent multi-threading across a single peer pair requires an origin serialization lock or multi-channel muxing.
