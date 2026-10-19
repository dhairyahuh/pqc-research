# External Audit Package: TFIB Verification Data

This directory contains the primary empirical datasets, raw timing samples, and source code of the experimental runners for external auditing of the Twiddle Factor Integrity Binding (TFIB) research extension for ML-KEM-768.

---

## 1. Directory Contents

| File | Size | Description |
| :--- | :--- | :--- |
| [`tfib_trial_level_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/chatgpt/tfib_trial_level_results.csv) | 78 KB (901 lines) | Individual trial-by-trial empirical records across 18 test suites (900 total trials). Tracks exact trigger counts, monitor mismatch flags, recovery flags, oracle key comparison, and final classification. |
| [`tfib_benchmark_raw.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/chatgpt/tfib_benchmark_raw.csv) | 1.3 MB (40,001 lines) | Full sample-level timing dataset containing 40,000 individual decapsulation execution latencies (in microseconds) across Baseline, TFIB-Ref, TFIB-Meta, and Active Recovery. |
| [`tfib_validity_audit_runner.c`](file:///Users/dhairyajain/Desktop/pqc%20research/chatgpt/tfib_validity_audit_runner.c) | 9.6 KB | Complete C source code of the test harness executing all 18 targeted fault-injection test suites with independent oracle evaluation. |
| [`tfib_benchmark_audit.c`](file:///Users/dhairyajain/Desktop/pqc%20research/chatgpt/tfib_benchmark_audit.c) | 8.2 KB | Complete C source code of the high-precision 40,000-iteration benchmark harness capturing sample latencies via `mach_absolute_time`. |
| [`tfib_reproduced_results.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/chatgpt/tfib_reproduced_results.csv) | 1.4 KB (19 lines) | Aggregated summary table reporting per-suite activation counts, total triggers, detection rates, recoveries, safe fail-stops, FO catches, and SDC rates. |

---

## 2. CSV Schemas

### `tfib_trial_level_results.csv`
- `trial_id`: Sequential integer (0 to 899).
- `config`: Configuration under test (`BASELINE`, `TFIB_REF`, `TFIB_META`).
- `fault_suite`: Test suite name (e.g. `OP_TWIDDLE_TRANSIENT`, `SIMULTANEOUS_COMMON_MODE`, etc.).
- `stage`: NTT layer targeted (1 to 7).
- `butterfly`: Butterfly index targeted (0 to 127).
- `bit`: Bit flip position (1 to 15).
- `persistent`: Boolean (0 = transient, 1 = persistent).
- `trigger_count`: Number of times the fault hook fired during decapsulation.
- `fault_activated`: Boolean flag (`trigger_count > 0`).
- `mismatch_count`: Number of mismatches flagged locally by the butterfly monitor.
- `monitor_detected`: Boolean flag (`mismatch_count > 0`).
- `recovery_count`: Number of in-place butterfly recoveries performed.
- `recovered_success`: Boolean flag (`recovery_count > 0`).
- `oracle_valid_match`: Independent comparison against true secret key ($K_{\text{out}} == K_{\text{valid}}$).
- `oracle_rejection_match`: Independent comparison against FIPS 203 canonical rejection key ($K_{\text{out}} == K_{\text{rejection}}$).
- `final_status`: Internal status code returned by `mlkem768_dec_monitored` (`0x5A5A5A5A` = Success, `0xA5A5A5A5` = Rejection, `0xFFFFFFFF` = Fault).
- `oracle_classification`: Independent verdict (`CLEAN_SUCCESS`, `GENUINE_RECOVERY`, `SAFE_FAIL_STOP`, `LOCAL_BLIND_FO_CONTAINED`, `INEFFECTIVE_FAULT_VALID`, `SILENT_DATA_CORRUPTION`).

### `tfib_benchmark_raw.csv`
- `config`: `BASELINE`, `TFIB_REF`, `TFIB_META`.
- `condition`: `FAULT_FREE`, `ACTIVE_RECOVERY`.
- `iteration`: Integer (0 to 9,999).
- `latency_us`: Monotonic elapsed time in microseconds for the decapsulation operation.
