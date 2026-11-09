# Technology Stack

## 1. Programming Languages & Compilers
- **C (C99 Standard):** Core cryptographic primitives, NTT engines, TFIB integrity verification, fault injection harnesses, and cleanroom reproducers.
  - Compilers: `clang` / Apple clang version 17+, `gcc` (GCC 11+ compatible).
  - Optimization Flags: `-O3`, `-Wall`, `-Wextra`, `-Wpedantic`.
- **Python (3.9+):** Statistical modeling, test automation suites, dataset generation, and verification scripts (`pytest`, `numpy`, `scipy`).
- **POSIX Shell (zsh/bash):** Automated build orchestration, benchmark runs, and test harnesses.

## 2. Cryptographic Codebases & Standards
- **NIST FIPS 203:** Module-Lattice-Based Key-Encapsulation Mechanism Standard (ML-KEM-768 parameter set: $k=3, q=3329, n=256, \eta_1=2, \eta_2=2$).
- **NIST FIPS 204:** Module-Lattice-Based Digital Signature Standard (ML-DSA reference trees).
- **PQClean / Reference Implementations:** Standard standalone C99 reference code for Kyber and Dilithium.

## 3. Hardware Benchmarking Platform
- **Processor:** Apple M3 Pro (12-core CPU, 18-core GPU).
- **Memory Architecture:** Unified LPDDR5 Memory (High-bandwidth, low-latency access).
- **Measurement Instrumentation:** High-precision monotonic nanosecond timers (`clock_gettime(CLOCK_MONOTONIC)` and Apple mach timebase).

