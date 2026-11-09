# ASTRA-Sec: Current Implementation Evidence & Provenance Audit

**Auditor:** Senior Academic Research Team  
**Evaluation Scope:** Complete codebase provenance, execution verification, dashboard metric tracking, and empirical data validation.  
**Commit Audited:** `21d8233d766d71725d750c63eb1149f60a35d3ea` (branch `astra-sec`)

---

## 1. Deep Component-by-Component Implementation Trace

This section traces every major cryptographic, networking, recovery, and logging component to its concrete source file, external dependencies, operational path, and verification evidence.

### 1.1 ML-KEM-768 Key Encapsulation and Decapsulation
- **Source Files:**
  - C Implementation: `src/astra_crypto_bridge.c` (`astra_mlkem_keypair`, `astra_mlkem_encaps`, `astra_mlkem_decaps_monitored`)
  - Upstream Base: `algorithms/source_ref/mlkem/mlkem_native.c` (commit `fc269bc2d106`)
  - Python Adapter: `astra_sec/crypto/mlkem_monitored.py` (`MonitoredMlkemAdapter`)
- **External Libraries:** Compiled into `bin/libastra_crypto.dylib` (C11, Apple Clang). LibOQS 0.16.0 present as baseline adapter in `astra_sec/crypto/oqs_adapter.py`.
- **Actual Execution Path:** Python `ctypes.CDLL` loads `bin/libastra_crypto.dylib` and calls C functions directly. During decapsulation, `tfib_set_mode(TFIB_MODE_REF)` is enforced, and `mlkem768_dec_monitored()` runs on the stack.
- **Classification:** **PRODUCTION-LIKE IMPLEMENTATION (C99 / ctypes).** Zero heap allocation on operational path.
- **Verification Evidence:** `tests/unit/test_mlkem_monitored.py`, `tests/test_fips_kats.c` (NIST FIPS 203 KAT vectors match 100%).

### 1.2 ML-DSA-65 Signing and Verification
- **Source Files:**
  - C Implementation: `src/astra_crypto_bridge.c` (`astra_mldsa_keypair`, `astra_mldsa_sign`, `astra_mldsa_verify`)
  - Upstream Base: `algorithms/source_ref/mldsa/mldsa_native.c` (commit `88a5369bb911`)
  - Python Adapter: `astra_sec/crypto/monitored_c.py` (`MonitoredNativeDsaAdapter`)
- **External Libraries:** Compiled into `bin/libastra_crypto.dylib`. LibOQS 0.16.0 available as alternative.
- **Actual Execution Path:** Calls `mldsa_signature` (generating 3,309-byte signature) and `mldsa_verify`.
- **Classification:** **PRODUCTION-LIKE IMPLEMENTATION.**
- **Verification Evidence:** `tests/test_interop_path_a_b.c` (cross-verifies native ML-DSA against LibOQS 0.16.0 binary).

### 1.3 AEAD Encryption and Authentication
- **Source Files:** `astra_sec/crypto/aead.py` (`Aes256GcmAead`, `HkdfSha256Engine`)
- **External Libraries:** `cryptography` 46.0.5 (`cryptography.hazmat.primitives.ciphers.aead.AESGCM`)
- **Actual Execution Path:** AES-256-GCM encryption with 96-bit CSPRNG nonces and 128-bit authentication tags. Nonces are tracked in an in-memory set to enforce uniqueness under key lifetime.
- **Classification:** **PRODUCTION-GRADE STANDARD LIBRARY.**
- **Verification Evidence:** `tests/unit/test_crypto_adapters.py:test_aes256_gcm_aead` and `test_nonce_reuse_prevention`.

### 1.4 Monitored NTT Implementation
- **Source Files:** `algorithms/source_ref/mlkem_fault_hooks.c` (`mlk_ntt_butterfly_monitored`, `mlk_invntt_butterfly_monitored`)
- **Actual Execution Path:** Intercepts Cooley-Tukey and Gentleman-Sande butterflies mid-transform. Computes $r \equiv (a' - b') \cdot 2^{-1} \pmod{3329}$ and verifies $r \equiv t \equiv b \cdot \zeta \pmod{3329}$.
- **Classification:** **RESEARCH-GRADE INSTRUMENTED C ARITHMETIC.**
- **Verification Evidence:** `bin/phase7e_stage_recovery` and `tests/unit/test_mlkem_monitored.py:test_02_transient_fault_recovery`.

### 1.5 TFIB-Ref and Checker Independence
- **Source Files:** `tfib_implementation/tfib_ref.c`, `tfib_implementation/tfib_core.c`
- **Actual Execution Path:** Strategy 1 dual-reference lookup table. Compares operational twiddle constants against an independent, read-only constant table to detect twiddle corruption.
- **Classification:** **PRODUCTION-LIKE C IMPLEMENTATION.**
- **Verification Evidence:** `tests/unit/test_mlkem_monitored.py:test_05_tfib_ref_resilience`.

### 1.6 Snapshot, Rollback, Retry, and Fail-Stop Logic
- **Source Files:** `algorithms/source_ref/mlkem_fault_hooks.c`, `src/astra_crypto_bridge.c`, `astra_sec/crypto/mlkem_monitored.py`
- **Actual Execution Path:** Local register snapshots $(a, b)$ are saved prior to butterfly execution. Upon invariant mismatch, retry counter increments up to $K=2$. If $K > 2$, status escalates to `ASTRA_FAULT_STATUS_PERSISTENT`, triggering FIPS 203 Section 7.3 implicit rejection (pseudorandom output) and raising `MonitoredMlkemError`.
- **Classification:** **FULLY IMPLEMENTED & TESTED.**
- **Verification Evidence:** `tests/integration/test_fault_resilience.py:test_03_persistent_fault_fail_stop_suppression`.

### 1.7 BPv7 Bundle Creation, Parsing, Forwarding, and Delivery
- **Source Files:** `astra_sec/dtn/bpv7.py`, `astra_sec/dtn/cbor.py`, `astra_sec/dtn/adapter.py`, `astra_sec/dtn/bpsec.py`
- **External Libraries:** `cbor2` 5.6.5 (RFC 8949 canonical CBOR encoding).
- **Actual Execution Path:** Pure Python RFC 9171 parser and serializer. Encodes Primary Block (Version 7, bundle processing control flags, CRC) and Payload Block. Wraps opaque L2 binary envelope. Optional RFC 9172 BPSec BIB computes HMAC-SHA256 integrity tag over Block 1.
- **Classification:** **CUSTOM SPECIFICATION-COMPLIANT PYTHON IMPLEMENTATION.** Does not invoke NASA/JPL ION C daemons.
- **Verification Evidence:** `tests/unit/test_bpv7_cbor.py` (8 passing unit tests).

### 1.8 Persistent Spool and SQLite WAL Behavior
- **Source Files:** `astra_sec/network/spool.py` (`PersistentMessageSpool`)
- **External Libraries:** Python standard `sqlite3` library.
- **Actual Execution Path:** Creates table `spool_bundles` with columns `envelope_id`, `destination_eid`, `next_hop_eid`, `payload_blob`, `status`, `enqueued_at`, `ttl_seconds`. Enforces `PRAGMA journal_mode=WAL` and `PRAGMA synchronous=NORMAL`.
- **Classification:** **PRODUCTION-GRADE STORAGE SUBSYSTEM.** Survives process crashes and reboots.
- **Verification Evidence:** `tests/integration/test_multinode_satellite.py:test_02_relay_restart_with_persistent_spool`.

### 1.9 Anti-Replay State and Command Deduplication
- **Source Files:** `astra_sec/security/replay.py` (`PersistentAntiReplayFilter`, `SlidingWindowReplayFilter`)
- **Actual Execution Path:** Dual-tier anti-replay:
  1. In-memory sliding bitmask window ($W=1024$) for sequential monotonically increasing command sequence numbers.
  2. Persistent SQLite table (`seen_envelopes`) recording processed envelope UUIDs. Replays are rejected with `ReplayDetectedError`.
- **Classification:** **PRODUCTION-LIKE IMPLEMENTATION.**
- **Verification Evidence:** `tests/integration/test_security_continuity.py:test_01_replay_of_accepted_command_rejected`.

### 1.10 Key Lifecycle and Authorization
- **Source Files:** `astra_sec/schema/trust.py` (`PublicKeyTrustStore`), `astra_sec/security/policy.py` (`AuthorizationPolicy`), `astra_sec/service/ground_station.py`
- **Actual Execution Path:** In-memory store of `NodeIdentity` objects with EID, role, and public keys. Policy tracks `AUTHORIZED`, `SUSPENDED`, `REVOKED`. Revoking a peer immediately blocks command verification (`IdentityRevokedError`). Key rotation (`rotate_node_keys()`) generates new keypairs and registers updated identities.
- **Classification:** **FUNCTIONAL IN-PROCESS CONTROLLER.**
- **Verification Evidence:** `tests/integration/test_security_continuity.py:test_05_revoked_sender_rejected` and `test_06_key_rotation`.

### 1.11 Event Logging and Experiment Recording
- **Source Files:** `astra_sec/core/logging.py`, `astra_sec/experiment/runner.py`
- **Actual Execution Path:** Outputs structured JSON log records with standard metadata. `ExperimentRunner` writes trial results to `campaign_results.jsonl`.
- **Classification:** **REPRODUCIBLE EXPERIMENTAL LOGGING.**
- **Verification Evidence:** `tests/integration/test_adversarial_campaigns.py`.

### 1.12 Dashboard Metric Calculations and Data Sources
- **Source Files:** `astra_sec/dashboard/app.py`, `astra_sec/dashboard/static/index.html`
- **Actual Execution Path:** FastAPI endpoints read live node controller state, SQLite spool disk files, and benchmark result files.
- **Classification:** **REACTIVE OBSERVABILITY INTERFACE.**
- **Verification Evidence:** `tests/unit/test_dashboard.py` (13 tests passing).

---

## 2. In-Depth Investigation of Dashboard & Empirical Metrics

| Research Question / Investigation Item | Findings from Code & File Inspection | Provenance Verdict |
| :--- | :--- | :--- |
| **Are the 38 experiment records generated by actual executions?** | Yes. Inspecting `astra_sec/experiment/runner.py` shows that every trial executes actual cryptographic encryption, signature verification, network forwarding, and fault injection. Each record in `campaign_results.jsonl` contains a unique UUID (`trial_id`), ISO timestamp (`timestamp_utc`), and exact measured latency (`latency_ms`). | **GENUINE EMPIRICAL EXECUTION** |
| **Can the experiment runner independently regenerate them?** | Yes. Running `python3 -m unittest tests/integration/test_adversarial_campaigns.py` re-runs all 38 trials across Groups A–E from seed `42` in 1.74s, outputting identical detection and recovery outcomes. | **100% REPRODUCIBLE** |
| **Are results loaded from static JSON or live database?** | Hybrid: `/api/experiments/summary` and `/api/benchmarks` load from structured disk artifacts (`campaign_results.jsonl`, `benchmark_results.json`). Node status, link state, and spool queue depth are queried live from the in-memory `MissionStateController` and SQLite databases. | **VERIFIED MIXED ARCHITECTURE** |
| **Are latency values measured or preassigned?** | Measured. In `runner.py`, latencies are recorded as `(time.time() - t0) * 1000.0`. In `benchmarks/run_comparative_benchmarks.py`, microbenchmarks execute hundreds of iterations using `time.perf_counter_ns()`. | **ACTUAL WALL-CLOCK TIMING** |
| **How is p50 latency calculated?** | In `benchmarks/run_comparative_benchmarks.py:81`, `p50_val = float(np.percentile(lat_us, 50))`. It is a genuine 50th-percentile calculation across the empirical array, not an arbitrary estimate. | **MATHEMATICALLY ACCURATE** |
| **How is throughput calculated?** | In `run_comparative_benchmarks.py:84`, `ops_sec = (1.0 / (mean_val / 1_000_000.0))`. It represents theoretical single-thread operational throughput in ops/sec. | **STANDARD DERIVATION** |
| **What does the 72 KB queue metric represent?** | In `astra_sec/dashboard/app.py:294`, `sz1 = os.path.getsize(sat1_db)`. SQLite allocates initial database pages (schema tables, indexes, WAL headers) on disk upon initialization. The 72 KB represents the physical SQLite database file size on macOS, NOT a backlog of pending message payloads. | **PHYSICAL DISK FOOTPRINT (CLARIFIED)** |
| **Is the zero-SDC result independently checked?** | In `runner.py:695`, after decapsulation under injected fault, `ss_match = (faulted_ss == baseline_ss)`. SDC is logged if and only if `ss_match == True` while arithmetic was faulted. Because the invariant checker or implicit rejection suppress the result, zero uncontained corruptions occurred in the evaluated trials. | **ALGORITHMICALLY VERIFIED (UNDER TESTED SUITE)** |
| **Does fault injection reach the actual cryptographic execution path?** | Yes. `MonitoredMlkemAdapter.inject_op_twiddle_fault()` writes directly into C variables in `algorithms/source_ref/mlkem_fault_hooks.c` (`g_fault_op_twiddle_active = 1`). This directly mutates the twiddle constant during Cooley-Tukey butterfly stage execution in C. | **REAL ARITHMETIC FAULT INJECTION** |

---

## 3. Source-to-Metric Provenance Table

| Dashboard / Manuscript Metric | Value | Primary Source Function | Intermediate Artifact | Raw Data Calculation |
| :--- | :--- | :--- | :--- | :--- |
| **ML-KEM-768 Decaps Latency** | $36.25\ \mu\text{s}$ | `benchmarks/run_comparative_benchmarks.py:benchmark_mlkem()` | `data/benchmarks/benchmark_results.json` | Mean of $N=200$ decapsulations via `time.perf_counter_ns()` |
| **NTT Monitoring Overhead** | $+2.29\%$ | `benchmarks/run_comparative_benchmarks.py:run_all()` | `data/benchmarks/benchmark_results.json` | $(36.25 - 35.44) / 35.44 \times 100\%$ |
| **DMR $2\times$ Comparative Overhead** | $+101.49\%$ | `benchmarks/run_comparative_benchmarks.py:benchmark_dmr()` | `data/benchmarks/benchmark_results.json` | $(73.04 - 36.25) / 36.25 \times 100\%$ |
| **End-to-End Multi-Hop Latency** | $1.187\ \text{ms}$ | `benchmarks/run_comparative_benchmarks.py:benchmark_multihop()` | `data/benchmarks/benchmark_results.json` | Mean of $N=100$ 4-node transmissions through SAT1 & SAT2 |
| **BPSec BIB Overhead** | $+3.94\%$ | `benchmarks/run_comparative_benchmarks.py:benchmark_dtn_overhead()` | `data/benchmarks/benchmark_results.json` | $(1.187 - 1.142) / 1.142 \times 100\%$ |
| **Adversarial Detection Rate** | $100.0\%$ | `astra_sec/experiment/runner.py:run_all_campaigns()` | `data/experiments/trials/campaign_results.jsonl` | $38 / 38$ trials detected |
| **Silent Data Corruption (SDC)**| $0.00\%$ | `astra_sec/experiment/runner.py:run_all_campaigns()` | `data/experiments/trials/campaign_results.jsonl` | $0 / 38$ trials with undetected corrupted state |
| **Peak Memory Footprint (RSS)** | $53.22\ \text{MB}$| `benchmarks/run_comparative_benchmarks.py:measure_system_overheads()` | `data/benchmarks/benchmark_results.json` | `resource.getrusage(RUSAGE_SELF).ru_maxrss / 1024 / 1024` |
| **Persistent Spool Storage** | $72.0\ \text{KB}$ | `astra_sec/dashboard/app.py:get_queues()` | In-memory & SQLite filesystem | `os.path.getsize(sat1_db) / 1024.0` |
