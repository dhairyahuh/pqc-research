# ASTRA-Sec Phase 3: Known Limitations and Failed Experiments

## 1. Scientific Integrity Policy

In accordance with rigorous academic and scientific standards, this document records all discovered engineering limitations, execution anomalies, failed trials, and scope boundaries encountered during Phase 3 laboratory development.

---

## 2. Failed Experiments & Root-Cause Analyses

### 2.1. Group B Initial Failure: LibOQS Adapter Signature Mismatch
* **Symptom**: During initial execution of `group_b_baseline_unmonitored_pqc.json`, the orchestrator aborted immediately with:
  `KeyError: 'cdll'` and `'str' object has no attribute 'cdll'`.
* **Root Cause**: The adapter constructor in `baseline_unmonitored_pqc.py` erroneously passed strings `"ML-KEM-768"` and `"ML-DSA-65"` to `OqsKemAdapter(bridge)` and `OqsDsaAdapter(bridge)`. The parameters expected an optional `_LibOQSBridge` instance or `None`, but receiving a string assigned `self._bridge = "ML-KEM-768"`, causing subsequent calls to `self._bridge.cdll` to fail.
* **Resolution**: Updated the instantiation in `baseline_unmonitored_pqc.py` to `OqsKemAdapter()` and `OqsDsaAdapter()`, which automatically discover and load the system `_LibOQSBridge.get_instance()`. Subsequent execution succeeded with 100% delivery.

---

### 2.2. Group F Concurrency Stress: Session Interleaving & Replay Errors
* **Symptom**: Executing `EXP-F01-CONCURRENCY-4` across 4 concurrent threads resulted in only 1 successful delivery out of 12 attempts (8.33% success), with 11 messages failing due to:
  `ReplayDetectedError: Replay detected: sequence 110 from 'dtn://gsa/app' was already processed` and `CORRUPT_PAYLOAD_SDC: Decrypted plaintext does not match dispatched payload`.
* **Root Cause**:
  1. The Double Ratchet and Anti-Replay state engines (`GSA` sender and `GSB` receiver) maintain strictly sequential monotonic session counters (`sequence_number`).
  2. In the concurrent test harness, multiple threads invoked `send_and_receive()` simultaneously against a single shared session instance without thread synchronization around session step evolution.
  3. Concurrent worker threads generated duplicate sequence numbers and interleaved ratchet key derivations, triggering immediate anti-replay rejection and payload mismatch.
* **Architectural Conclusion**:
  In space DTN architectures, a single security association (Double Ratchet session) is fundamentally sequential. High-concurrency flight systems must either:
  a. Serialize transmissions over a mutex-locked session queue, or
  b. Establish distinct security associations / channel IDs for each concurrent task.

---

## 3. Laboratory Scope & Boundary Limitations

1. **Process-Level Integration vs. Flight Hardware**:
   - The current laboratory evaluates the 7-layer pipeline inside a single high-performance Darwin arm64 process space using in-memory queues and persistent SQLite WAL files. While timing, crypto algorithms, wire formats, and DTN logic are real, physical RF propagation delay and Doppler shift are modeled programmatically rather than transmitted over SDR radio links.
2. **Post-Quantum Signature Overhead**:
   - The ML-DSA-65 digital signature is 3,309 bytes, which constitutes ~65% of the total bundle size. For extreme low-bandwidth LEO constellations (e.g. 9600 bps), this overhead will require packet fragmentation or hybrid pre-shared state amortizations.
3. **C Library Dependency**:
   - Baseline B requires a native `liboqs.dylib` or `liboqs.so` compiled and accessible in system library paths. On environments lacking LibOQS, Baseline B will fail during loading.
