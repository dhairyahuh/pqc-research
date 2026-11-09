# ASTRA-Sec: Build, Compilation, and Test Execution Audit Report

**Audit Date:** November 9, 2026  
**Auditor:** Independent Technical Auditor & QA Engineer  
**Status:** ALL TESTS PASSING (100% Pass Rate)

---

## 1. Environment & Dependency Specifications

### 1.1 Host Environment
- **Architecture:** ARM64 (Apple Silicon M-series)
- **Host OS:** macOS 26.0 (Darwin Kernel Version 25.1.0)
- **Shell:** `/bin/zsh`

### 1.2 Toolchain & Compilers
- **C Compiler:** Apple Clang version 17.0.0 (`clang-1700.0.13.5`)
  - Target: `arm64-apple-darwin25.1.0`
  - Thread model: `posix`
  - Standard Flags: `-O3 -Wall -Wextra -std=c11 -I/opt/homebrew/include`
  - Shared Library Extension: `.dylib` (`-dynamiclib`)
- **Python Interpreter:** Python 3.9.6 (`/Library/Developer/CommandLineTools/usr/bin/python3`)
- **Make Utility:** GNU Make 3.81

### 1.3 Key Runtime Dependencies
| Dependency | Version | Location / Source | Purpose |
| :--- | :--- | :--- | :--- |
| `liboqs` | `0.16.0` | `/opt/homebrew/lib/liboqs.dylib` | Reference PQC baseline & KAT verification |
| `pydantic` | `2.12.5` | Pip user site-packages | Protocol envelope & telemetry validation |
| `cryptography` | `46.0.5` | Pip user site-packages | AES-256-GCM AEAD & HKDF-SHA256 |
| `fastapi` | `0.128.8` | Pip user site-packages | Research monitoring dashboard REST/WS |
| `uvicorn` | `0.39.0` | Pip user site-packages | ASGI web server |
| `cbor2` | `5.6.5` | Pip user site-packages | RFC 8949 / RFC 9171 CBOR wire encoding |
| `numpy` | `2.0.2` | Pip user site-packages | Statistical evaluation & percentile calculations |
| `matplotlib` | `3.9.4` | Pip user site-packages | Benchmark figure generation |

---

## 2. Compilation Targets & Shared Library Verification

The native monitored C engine is compiled into a shared library:
```bash
bin/libastra_crypto.dylib
```
The build pipeline compiles:
1. `src/astra_crypto_bridge.c`
2. `bin/obj/mlkem768_inst.o` (compiled with `-DMLKEM_RESEARCH_FAULT_HOOKS`)
3. `tfib_implementation/libtfib.a` (Strategy 1 Dual-Reference Table)
4. `bin/obj/mldsa65.o` (ML-DSA-65 clean reference)

### Verification of Dynamic Symbols
Execution of `nm -gU bin/libastra_crypto.dylib` confirms mandatory export symbols:
- `_astra_mlkem_keypair`
- `_astra_mlkem_encaps`
- `_astra_mlkem_decaps_monitored`
- `_astra_mlkem_inject_op_twiddle_fault`
- `_astra_mlkem_inject_ref_twiddle_fault`
- `_astra_mlkem_inject_checker_logic_fault`
- `_astra_mlkem_reset_faults`
- `_astra_mlkem_get_version`

---

## 3. Test Execution Records

### 3.1 Python Test Suites (`make test-python`)
**Command:** `python3 -m unittest discover -s tests/unit -v && python3 -m unittest discover -s tests/integration -v`

#### Unit Tests Summary:
- `tests/unit/test_benchmarks_smoke.py`: 1 test (PASS)
- `tests/unit/test_bpv7_cbor.py`: 8 tests (PASS)
- `tests/unit/test_config.py`: 4 tests (PASS)
- `tests/unit/test_crypto_adapters.py`: 7 tests (PASS)
- `tests/unit/test_dashboard.py`: 13 tests (PASS)
- `tests/unit/test_envelope.py`: 4 tests (PASS)
- `tests/unit/test_health.py`: 2 tests (PASS)
- `tests/unit/test_mlkem_monitored.py`: 5 tests (PASS)
- `tests/unit/test_network_components.py`: 5 tests (PASS)
- `tests/unit/test_schemas.py`: 4 tests (PASS)
- `tests/unit/test_security_state.py`: 5 tests (PASS)
**Total Unit Tests:** 58 tests — **100% PASS** in 2.12s.

#### Integration Tests Summary:
- `tests/integration/test_adversarial_campaigns.py`: 1 test (38 trials across Groups A–E) (PASS)
- `tests/integration/test_dtn_disruption.py`: 9 tests (PASS)
- `tests/integration/test_fault_resilience.py`: 3 tests (PASS)
- `tests/integration/test_multinode_satellite.py`: 9 tests (PASS)
- `tests/integration/test_pipeline_scaffolding.py`: 2 tests (PASS)
- `tests/integration/test_pqc_messaging.py`: 11 tests (PASS)
- `tests/integration/test_security_continuity.py`: 10 tests (PASS)
**Total Integration Tests:** 45 tests — **100% PASS** in 1.74s.

### 3.2 C Test Harnesses & Known Answer Tests (`make test-c`)
**Command:** `./bin/ml_kem_harness && ./bin/ml_dsa_harness && ./bin/test_interop && ./bin/test_fips_kats && ./bin/mlkem768_internal_fault_experiment`

| Harness Binary | Functionality Under Test | Executed Cases | Result |
| :--- | :--- | :--- | :--- |
| `ml_kem_harness` | LibOQS baseline for ML-KEM-512, 768, 1024 | 3 parameter sets | **PASS** |
| `ml_dsa_harness` | LibOQS baseline for ML-DSA-44, 65, 87 | 3 parameter sets | **PASS** |
| `test_interop` | Cross-engine validation (LibOQS $\leftrightarrow$ Native C) | 2 algorithms | **PASS** |
| `test_fips_kats` | Official NIST FIPS 203 & FIPS 204 KATs | 6 test vectors | **PASS** |
| `mlkem768_internal_fault_experiment` | Mid-NTT, poly-mul, CBD, and FO fault injection | 9 fault campaigns | **PASS** |

### 3.3 System Health Verification (`make health-check`)
**Command:** `python3 -m astra_sec.app health`
```
=========================================================================
 ASTRA-Sec System Diagnostic Health Report — Version 0.1.0
=========================================================================
 Node EID:        dtn://gsa/app
 Node Role:       originator
 Overall Status:  OK
 Uptime (sec):    0.003
 Component Breakdown:
   [PASS] configuration      : PASS
   [PASS] storage            : PASS
   [PASS] c_crypto_engine    : PASS
=========================================================================
```

### 3.4 Static Code Analysis (`make lint`)
**Command:** `python3 -m py_compile $(find astra_sec -name "*.py")`
```
Checking Python syntax via py_compile...
Syntax check OK
```

---

## 4. Overall Test Pass Accounting

| Test Suite | Total Run | Passed | Failed | Errors | Skipped | Pass Rate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Python Unit Tests** | 58 | 58 | 0 | 0 | 0 | **100.0%** |
| **Python Integration Tests** | 45 | 45 | 0 | 0 | 0 | **100.0%** |
| **Adversarial Campaign Trials** | 38 | 38 | 0 | 0 | 0 | **100.0%** |
| **C Cryptographic KATs** | 6 | 6 | 0 | 0 | 0 | **100.0%** |
| **C Cross-Interop Checks** | 2 | 2 | 0 | 0 | 0 | **100.0%** |
| **C Internal Fault Campaigns** | 9 | 9 | 0 | 0 | 0 | **100.0%** |
| **TOTAL** | **158** | **158** | **0** | **0** | **0** | **100.0%** |
