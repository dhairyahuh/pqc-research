# End-to-End Reproducibility Guide

Follow this protocol to reproduce every major experimental claim and verify the entire research codebase from scratch.

## Prerequisites
- macOS or Linux
- Apple clang / GCC 11+
- GNU Make
- Python 3.9+ with `pytest`, `numpy`, `scipy`

## Step 1: Clean and Build Core Binaries
```bash
make clean
make all
```
Expected output:
- Compiles `bin/test_fips_kats`
- Compiles `bin/test_mlkem_harness`
- Compiles `bin/test_mldsa_harness`
- Exits with return code 0.

## Step 2: Validate NIST FIPS 203 Cryptographic Conformance
```bash
./bin/test_fips_kats
```
Expected output:
- `KAT vectors passed: 100/100` (zero cryptographic regressions).

## Step 3: Verify Countermeasure Independence (Step 2C)
```bash
./tfib_experiments/test_step2c_countermeasure_independence
```
Expected output:
- Executes 9 modular test cases validating orthogonality between TFIB, DMR, and FO rejection.
- `[PASS] 9 / 9 test assertions succeeded.`

## Step 4: Run Phase 18 Cleanroom Production Trials
```bash
./phase18_audit/production_reproducer
```
Expected output:
- Runs 400 cleanroom trials on ML-KEM-768 decapsulation with Gate A injection.
- Overwrites [`phase18_audit/raw_production_trials.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/raw_production_trials.csv) with deterministic hashes.
- Prints summary confirming 100% containment and 0 false alarms.

## Step 5: Execute Python Verification Suites
```bash
python3 -m unittest tests/test_phase4_audit.py
python3 -m unittest tests/test_phase5_cross_impl.py
python3 -m unittest tests/test_phase6_resilience.py
```
Expected output:
- All unit and audit test suites pass with code 0.

