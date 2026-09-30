# Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems

## 1. Executive Summary

This research project investigates the computational and algorithmic fault resilience of standardized Post-Quantum Cryptographic (PQC) algorithms—specifically **ML-KEM** (FIPS 203) and **ML-DSA** (FIPS 204)—under fault models representative of space-based and radiation-constrained computing environments.

Modern satellite constellations, CubeSats, and deep-space missions require post-quantum secure communications to guard against "harvest now, decrypt later" threats. However, space computing platforms are exposed to galactic cosmic rays, solar energetic particles, and trapped radiation belts that induce Single Event Effects (SEEs), such as Single Event Upsets (SEUs), transient computational glitches, and memory bit corruption. 

Because lattice-based cryptographic algorithms depend heavily on high-degree polynomial arithmetic, Number Theoretic Transforms (NTT), rejection sampling loops, and module-lattice structures, their sensitivity to computational and memory faults differs qualitatively from pre-quantum primitives (e.g., RSA, ECC).

This project integrates three research layers:
1. **Layer A — Cryptographic Mathematics:** Detailed algebraic formulation of Module Learning with Errors (M-LWE) and Module Short Integer Solution (M-SIS) problems, polynomial rings, NTT, Gaussian/binomial noise distributions, and rejection sampling.
2. **Layer B — Cryptographic Implementation:** Analysis of concrete C/C++ memory operations, cache layouts, modular reduction routines (Montgomery / Barrett), sampling loops, and serialization routines.
3. **Layer C — Fault-Resilience Experimentation:** A controlled, deterministic, repeatable fault-injection framework operating across multiple abstraction levels (input-level, memory-level, intermediate-state, and instruction/computation-level).

---

## 2. Directory Structure

```text
pqc-fault-resilience/
├── README.md                           # Project top-level documentation
├── requirements/
│   └── requirements.txt                # Python dependencies
├── docs/
│   ├── project-overview.md             # In-depth architectural & research overview
│   ├── research-questions.md           # RQs formulation and hypothesis mapping
│   ├── methodology.md                  # Experimental protocol and metrics definition
│   ├── references.md                   # Formal academic bibliography
│   ├── mathematics/
│   │   ├── ml-kem.md                   # Mathematical analysis of ML-KEM (FIPS 203)
│   │   └── ml-dsa.md                   # Mathematical analysis of ML-DSA (FIPS 204)
│   └── fault-model/
│       └── fault-model.md              # Space radiation to software fault abstraction model
├── algorithms/
│   ├── ml-kem/                         # ML-KEM baseline harness and wrapper
│   └── ml-dsa/                         # ML-DSA baseline harness and wrapper
├── fault_injection/
│   ├── injector/                       # Core deterministic fault injector engine
│   ├── fault_models/                   # SEU, multi-bit, transient, and burst fault definitions
│   ├── targets/                        # Target memory buffers, coefficients, and registers
│   └── scheduler/                      # Injection timing and trigger controllers
├── resilience/
│   ├── redundancy/                     # Redundant computation modules (selective / dual)
│   ├── integrity_checks/               # Norm, range, and checksum verification routines
│   ├── retry/                          # Exception and fault handling retry wrappers
│   └── checkpoint/                     # Intermediate state checkpointing & recovery
├── experiments/
│   ├── baseline/                       # Correctness validation and performance benchmarks
│   ├── fault_injection/                # Experimental campaign runners
│   ├── resilience/                     # Protected execution comparative evaluations
│   └── configurations/                 # YAML/JSON reproducible experiment manifests
├── results/                            # Structured CSV, JSON, and plotting outputs
├── scripts/                            # Analysis, visualization, and automation scripts
└── tests/                              # Unit, integration, and known-answer test suites
```

---

## 3. Technology Stack & Environment

- **Host Architecture:** Apple Silicon (arm64, Apple M1, 8 cores, 8 GB RAM)
- **Host OS:** macOS (Darwin 27.x)
- **Primary Toolchain:** Apple Clang (C99 / C++17), CMake 4.4+, GNU Make 3.81, Ninja
- **Cryptographic Engines:**
  - OpenSSL 3.6.4+ (Standard FIPS 203 / 204 provider)
  - `liboqs` 0.16.0+ (Open Quantum Safe C library)
- **Analysis & Instrumentation Environment:** Python 3.9+, NumPy, SciPy, Matplotlib

---

## 4. Research Scope and Constraints

- **Simulation Model:** All fault experiments are conducted via software-based fault simulation representing abstract fault classes (SEU, transient arithmetic disturbance, persistent memory cell degradation). We do not claim physical equivalence to in-situ orbital radiation testing.
- **Standards Compliance:** Cryptographic operations are bound strictly to NIST FIPS 203 (ML-KEM) and NIST FIPS 204 (ML-DSA). No proprietary or non-standard cryptographic primitives are invented.
