# Algorithms Directory

This directory contains the core post-quantum cryptographic implementations and research instrumentation hooks.

## Directory Structure
- [`ml-kem/`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/ml-kem/): Production-grade ML-KEM-768 test harness and integration wrappers.
- [`ml-dsa/`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/ml-dsa/): ML-DSA-65 and ML-DSA-44 signature harnesses.
- [`source_ref/`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/): Standalone C reference trees derived from NIST FIPS 203/204 standard implementations:
  - [`source_ref/mlkem/`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/): Complete ML-KEM C99 source code (KEM logic, NTT Cooley-Tukey butterfly network, Fujisaki-Okamoto verification).
  - [`source_ref/mldsa/`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mldsa/): Complete ML-DSA C99 source code.
  - [`source_ref/mlkem_fault_hooks.h`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.h) & [`mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c): Fine-grained mid-operation fault injection hooks.
- [`oqs_wrapper.py`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/oqs_wrapper.py): Python wrapper interfacing with liboqs for cross-implementation comparisons.

## Memory & Conformance Properties
- **Zero Dynamic Allocation:** Uses static or stack buffers (`MLK_ALLOC`) compliant with flight standards.
- **Constant-Time Operations:** Side-channel hardened NTT butterfly operations and Montgomery reductions.
- **Conformance:** 100% compliant with NIST Known Answer Tests (KATs).

