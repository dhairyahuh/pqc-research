# Testing Architecture & Verification Protocols

## 1. Test Suite Matrix

The repository implements a tiered verification harness ensuring cryptographic correctness, fault containment, countermeasure independence, and non-regression.

| Tier | Test Suite | File Path | Language | Verification Target |
|---|---|---|---|---|
| **Tier 1** | Known Answer Tests | [`bin/test_fips_kats`](file:///Users/dhairyajain/Desktop/pqc%20research/bin/test_fips_kats) | C | NIST FIPS 203 cryptographic KAT conformance |
| **Tier 2** | Step 2C Independence | [`tfib_experiments/test_step2c_countermeasure_independence.c`](file:///Users/dhairyajain/Desktop/pqc%20research/tfib_experiments/test_step2c_countermeasure_independence.c) | C | 9/9 countermeasure independence assertions |
| **Tier 3** | Cleanroom Reproducer | [`phase18_audit/production_reproducer.c`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/production_reproducer.c) | C | 400 cleanroom trials evaluating Gate A fault containment |
| **Tier 4** | Statistical Reanalysis | [`tests/test_phase4_audit.py`](file:///Users/dhairyajain/Desktop/pqc%20research/tests/test_phase4_audit.py) | Python | Statistical diffusion laws and simulator validation |
| **Tier 5** | Cross-Implementation | [`tests/test_phase5_cross_impl.py`](file:///Users/dhairyajain/Desktop/pqc%20research/tests/test_phase5_cross_impl.py) | Python | Documentation cross-implementation checks |
| **Tier 6** | Circular Dependency Audit | [`tests/test_phase6_resilience.py`](file:///Users/dhairyajain/Desktop/pqc%20research/tests/test_phase6_resilience.py) | Python | Verification of circular masking falsification |
| **Tier 7** | Decapsulation Reproducibility | [`tests/phase7k/test_phase7k_reproducibility.py`](file:///Users/dhairyajain/Desktop/pqc%20research/tests/phase7k/test_phase7k_reproducibility.py) | Python | End-to-end decapsulation pipeline reproducibility |

## 2. Test Execution Commands

```bash
# Build all C targets
make all

# Run cryptographic KAT conformance
./bin/test_fips_kats

# Run Step 2C countermeasure independence
./tfib_experiments/test_step2c_countermeasure_independence

# Run Phase 18 cleanroom trial suite
./phase18_audit/production_reproducer

# Run Python audit test suites
pytest tests/test_phase4_audit.py tests/test_phase5_cross_impl.py tests/test_phase6_resilience.py
```

