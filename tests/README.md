# Tests Directory

This directory contains cryptographic conformance tests, fault injection validation harnesses, interoperability checks, and phase regression suites.

## Key Test Suites
- [`kat_mlkem768.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tests/kat_mlkem768.c): FIPS 203 Known Answer Test driver for ML-KEM-768.
- [`kat_mldsa65.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tests/kat_mldsa65.c) & [`kat_mldsa44.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tests/kat_mldsa44.c): FIPS 204 KAT drivers.
- [`test_phase4_audit.py`](file:///Users/dhairyajain/Desktop/pqc%20research/tests/test_phase4_audit.py): Validates statistical diffusion reanalysis and spacecraft simulator metrics.
- [`test_phase5_cross_impl.py`](file:///Users/dhairyajain/Desktop/pqc%20research/tests/test_phase5_cross_impl.py): Verifies cross-implementation boundary properties and documentation.
- [`test_phase6_resilience.py`](file:///Users/dhairyajain/Desktop/pqc%20research/tests/test_phase6_resilience.py): Asserts formal falsification of circular inverse verifiers.
- `phase7*/`: Phase 7 audit and timing validation suites.

## How to Run Tests
```bash
# Known Answer Tests (KATs)
./bin/test_fips_kats

# Step 2C Countermeasure Independence Suite
./tfib_experiments/test_step2c_countermeasure_independence

# Python Test Suites
pytest tests/test_phase4_audit.py tests/test_phase5_cross_impl.py tests/test_phase6_resilience.py
```

