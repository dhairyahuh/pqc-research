# FAULT RESILIENCE ANALYSIS OF POST-QUANTUM CRYPTOGRAPHIC IMPLEMENTATIONS FOR SPACE SYSTEMS
## Initial Case Study: Software-Level Fault Resilience for ML-KEM-768 Decapsulation

[![Build & KATs](https://img.shields.io/badge/FIPS%20203%2F204%20KATs-18%2F18%20Pass-brightgreen.svg)]()
[![Step 2C Independence](https://img.shields.io/badge/Step%202C%20Independence-9%2F9%20Pass-blue.svg)]()
[![Overhead](https://img.shields.io/badge/Decapsulation%20Overhead-%2B16.9%25-success.svg)]()
[![SDC Rate](https://img.shields.io/badge/Observed%20SDC-0%2F300%20(Production)-brightgreen.svg)]()
[![Standards](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-orange.svg)]()

---

## 1. Research Identity & Three-Level Architecture

> **Authoritative Research Framing:**  
> "The research, titled 'Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems', investigates the reliability and fault resilience of post-quantum cryptographic implementations in space-system environments.
> 
> As part of the initial implementation and experimental evaluation, the project has focused on ML-KEM-768, a standardized post-quantum key-encapsulation mechanism under NIST FIPS 203.
> 
> This implementation-level study investigates NTT arithmetic fault detection through dual-transform algebraic invariant monitoring, localized rollback and retry, and fail-stop containment using the Fujisaki–Okamoto implicit rejection mechanism.
> 
> The experimental results obtained so far provide an initial technical foundation for the broader research. However, the overall research objective extends beyond this implementation and includes additional cryptographic implementations, embedded processor evaluation, representative space-relevant fault models, hardware/software co-design, physical fault testing, and eventual spacecraft-level integration and validation."

### The Three-Level Research Structure

```text
+---------------------------------------------------------------------------------------------------------+
| LEVEL A — OVERALL RESEARCH PROGRAMME (PERMANENT TITLE)                                                  |
| "Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems"             |
| The complete research agenda: evaluating and improving PQC reliability under space radiation, SEUs,    |
| hardware resource constraints, and orbital operational environments.                                    |
+---------------------------------------------------------------------------------------------------------+
                                                     │
                                                     ▼
+---------------------------------------------------------------------------------------------------------+
| LEVEL B — WORK COMPLETED SO FAR (INITIAL IMPLEMENTATION CASE STUDY)                                     |
| "Software-Level Fault Resilience for ML-KEM-768"                                                        |
| • Standardized primitive: NIST FIPS 203 ML-KEM-768 (Kyber)                                              |
| • Micro-level invariant monitoring across all 9,856 NTT butterflies (5,376 CT + 4,480 GS)                |
| • Localized single-butterfly register rollback (~0.0101% operation-count retry ratio, 100/100 recovered)|
| • Deterministic fail-stop containment via FIPS 203 Section 7.3 implicit rejection (200/200 safe stops) |
| • Cleanroom & canonical validation: 0 SDC across 300 production trials & 750 campaign trials            |
| • Apple Silicon ARM64 benchmark: +16.9% decapsulation latency overhead under -O3; 0 dynamic heap bytes  |
| • Disclosed limitation: Theorem 1 twiddle-factor blindness of local monitors                           |
+---------------------------------------------------------------------------------------------------------+
                                                     │
                                                     ▼
+---------------------------------------------------------------------------------------------------------+
| LEVEL C — REMAINING RESEARCH & FUTURE WORK (SEVEN BROAD WORK PACKAGES)                                  |
| • WP1: Broader Cryptographic Evaluation (ML-DSA, SLH-DSA, stateful hash signatures, cross-algorithm)     |
| • WP2: Embedded & Space-Oriented Computing (ARM Cortex-M4, RISC-V RV32IM, memory/stack/cycles)          |
| • WP3: Space-Relevant Fault Modelling (SEUs, SETs, multi-bit bursts, memory, control flow)              |
| • WP4: Hardware/Software Fault Resilience (hardware ECC, memory protection, twiddle CRC32 binding)     |
| • WP5: Physical Validation (laboratory EMFI, voltage/clock glitching, cyclotron beam irradiation)       |
| • WP6: Space-System Integration (spacecraft OBC, NASA cFS, RTEMS, CCSDS SDLS, FDIR safe-mode)          |
| • WP7: System-Level Validation (hardware-in-the-loop testbed, mission availability & link reliability) |
+---------------------------------------------------------------------------------------------------------+
```

See [`docs/architecture/RESEARCH_EVOLUTION.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/architecture/RESEARCH_EVOLUTION.md) for the complete multi-layer architecture and evolution mapping.

---

## 2. Current Implementation and Experimental Progress: ML-KEM-768

### The Problem in Parameter Set 768
In post-quantum cryptography under NIST FIPS 203 (**ML-KEM-768**), key decapsulation executes **9,856 Number Theoretic Transform (NTT) butterfly operations** across 11 polynomial transforms. If an unmitigated bit-flip strikes an intermediate arithmetic operand:
- **Silent Data Corruption (SDC):** The decapsulation routine emits an undetected incorrect shared key, exposing downstream communications to cryptanalytic compromise.
- **Unavailability:** Uncontained aborts or sequential Dual Modular Redundancy (DMR)—which incurs **$+99.33\%$** latency overhead at the NTT level—drain tight power budgets and cause link renegotiation storms.
- **Circular Verifier Blindness:** Naive sanity verifiers that re-read live corrupted registers fail due to common-mode blindness, exhibiting a **98.5% false-pass rate** ($591/600$ trials across 6 H1-relevant targets).

### Our Implemented Solution: Dual Invariants + Local Rollback
We design, implement, and empirically validate an end-to-end software fault-resilience architecture:
- **Micro-Level Monitoring:** Intercepts all 9,856 butterflies (5,376 Forward Cooley-Tukey + 4,480 Inverse Gentleman-Sande) using decoupled algebraic invariants with zero modular division overhead.
- **Localized Register Rollback:** Restores operands from software-managed snapshot variables, recovering transient faults on retry 1 with only a single-butterfly recomputation (~$0.0101\%$ operation ratio; distinct from wall-clock overhead).
- **Deterministic Containment:** Escalate persistent faults to FIPS 203 Section 7.3 implicit rejection ($K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$).
- **Empirical Results:** $100\%$ transient recovery (100/100, Wilson CI: $[96.3\%, 100\%]$), $100\%$ safe fail-stop (200/200, Wilson CI: $[98.1\%, 100\%]$), **0 SDC observed across 300 active production trials** (Wilson CI: $[0.00\%, 1.26\%]$) and **0 SDC across 750 active campaign trials** (Clopper-Pearson bound: $0.49\%$), with **$+16.9\%$** decapsulation overhead under `-O3`. Zero dynamic heap allocations in monitoring paths.

---

## 2. Fast Navigation & Presentation Preparation

For tomorrow's academic progress defense, all essential materials are centralized in [`docs/presentation/`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/):
- **Master Progress Report:** [`docs/presentation/RESEARCH_PROGRESS_MASTER.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/RESEARCH_PROGRESS_MASTER.md) (Comprehensive 16-section technical foundation)
- **14-Slide Presentation Deck:** [`docs/presentation/PROGRESS_PRESENTATION_OUTLINE.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/PROGRESS_PRESENTATION_OUTLINE.md) (Slide-by-slide scripts & talking points)
- **Defense Question Bank:** [`docs/presentation/DEFENSE_QUESTION_BANK.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/DEFENSE_QUESTION_BANK.md) (22 anticipated defense Q&As)
- **Live Code Demo Guide:** [`docs/presentation/LIVE_CODE_DEMO_GUIDE.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/presentation/LIVE_CODE_DEMO_GUIDE.md) (3–5 min terminal script with line references)
- **Codebase Architecture Map:** [`docs/architecture/CODEBASE_MAP.md`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/architecture/CODEBASE_MAP.md) (Direct answers to 10 codebase questions)

---

## 3. Repository Architecture

```text
pqc-research/
│
├── README.md                           <- Master front-door guide (This file)
├── PROJECT_OVERVIEW.md                 <- High-level project summary
├── CONTRIBUTING.md                     <- Safety & non-destructive research protocol
├── research-roadmap.md                 <- Long-term research milestones
│
├── docs/                               <- Centralized documentation hub
│   ├── README.md                       <- Documentation overview
│   ├── presentation/                   <- Progress defense deliverables & question bank
│   ├── project/                        <- Mission, objectives, scope, tech stack, glossary
│   ├── architecture/                   <- System diagrams, execution flow, codebase map
│   ├── phases/                         <- Chronological phase archive (Phase 00 - Phase 18, TFIB)
│   ├── experiments/                    <- Fault injection, benchmarks, testing, reproducibility
│   ├── audits/                         <- Evidence audits, gap closure, prior art comparisons
│   └── references/                     <- Literature database and bibtex records
│
├── algorithms/                         <- Core PQC cryptographic source trees
│   ├── README.md
│   ├── ml-kem/                         <- ML-KEM-768 production wrappers & harnesses
│   ├── ml-dsa/                         <- ML-DSA digital signature harnesses
│   └── source_ref/                     <- Standalone C99 FIPS 203/204 reference trees & fault hooks
│
├── tfib_implementation/                <- TFIB v2 source code and precompiled static library
│   ├── README.md
│   ├── tfib_ref.h & tfib_ref.c         <- Canonical ROM assertion and self-healing engine
│   └── libtfib.a                       <- Static library for linking
│
├── tfib_experiments/                  <- Step 2C countermeasure independence test suite
│   └── test_step2c_countermeasure_independence.c
│
├── phase18_audit/                      <- Cleanroom trial reproducer (N=400 Gate A trials)
│   ├── production_reproducer.c
│   └── raw_production_trials.csv
│
├── phase11_conformance_audit/          <- FIPS 203 Section 7.3 implicit rejection oracle audit (N=100)
├── phase16_targeted_evidence_closure/  <- Hypothesis 1 circular verifier study (N=600)
│
├── data/                               <- Experimental datasets & cryptographic digests
│   ├── README.md
│   └── manifests/                      <- dataset_provenance_manifest.csv (SHA-256 fingerprints)
│
├── tests/                              <- Conformance and regression test suites
│   ├── README.md
│   ├── kat_mlkem768.c & kat_mldsa65.c  <- NIST FIPS Known Answer Tests
│   └── test_phase*.py                  <- Python audit and diffusion test suites
│
├── results/                            <- Historical logs, distributions, and plot figures
├── benchmarks/                         <- Hardware performance profiles (Apple M3 Pro)
├── paper/                              <- Academic manuscript (manuscript.md), references, versions
└── scripts/                            <- Utility plotting and verification scripts
```

---

## 4. Quickstart: Build & Verification

### Step 1: Compile All Targets
```bash
make clean
make all
```

### Step 2: Validate Cryptographic Conformance (FIPS 203 KATs)
```bash
./bin/test_fips_kats
```
*Expected: 100/100 KAT vectors passing with zero regressions.*

### Step 3: Run Step 2C Countermeasure Independence Suite
```bash
./tfib_experiments/test_step2c_countermeasure_independence
```
*Expected: 9/9 assertions pass, confirming TFIB operates orthogonally to DMR and FO rejection.*

### Step 4: Run Phase 18 Cleanroom Trials
```bash
./phase18_audit/production_reproducer
```
*Expected: 400 cleanroom trials executed with 100% containment and zero false alarms.*

### Step 5: Run Python Verification Suites
```bash
python3 -m unittest tests/test_phase4_audit.py
python3 -m unittest tests/test_phase5_cross_impl.py
python3 -m unittest tests/test_phase6_resilience.py
```
*Expected: All test suites exit with code 0.*

---

## 5. ASTRA-Sec: Space Network Cryptographic Architecture

Building upon the low-level ML-KEM-768 fault resilience foundations, **ASTRA-Sec** establishes an end-to-end post-quantum secure messaging protocol designed for high-latency, intermittently-connected space networks (RFC 9171 DTN Bundle Protocol v7, RFC 9172 BPSec).

### 7-Layer Protocol Architecture

```text
+-----------------------------------------------------------------------------------+
| L1: Application & Telemetry     | Validated ADU creation, telemetry command opcode |
+-----------------------------------------------------------------------------------+
| L2: End-to-End Secure Messaging | AES-256-GCM envelope, 162-byte canonical AAD    |
+-----------------------------------------------------------------------------------+
| L3: Post-Quantum Crypto Services| ML-KEM-768 key encapsulation, ML-DSA-65 verify   |
+-----------------------------------------------------------------------------------+
| L4: Fault-Resilient Execution   | NTT invariant checks, K<=2 rollback, fail-stop   |
+-----------------------------------------------------------------------------------+
| L5: Delay-Tolerant Transport    | RFC 9171 BPv7 bundles, RFC 9172 hop integrity    |
+-----------------------------------------------------------------------------------+
| L6: Disruption Management       | Persistent spooling, out-of-order reassembly     |
+-----------------------------------------------------------------------------------+
| L7: FDIR & Ground Audit         | Spacecraft telemetry, SDC suppression audit      |
+-----------------------------------------------------------------------------------+
```

### Reference Scenario: 4-Node Space Relay Topology
$$\text{Ground Station A (GSA)} \longrightarrow \text{Satellite Relay 1 (SAT1)} \longrightarrow \text{Satellite Relay 2 (SAT2)} \longrightarrow \text{Ground Station B (GSB)}$$

---

## 6. ASTRA-Sec Quickstart & Unified Testing

### Step 1: Install Development Environment
```bash
make setup-dev
```

### Step 2: Run Unified Verification (C Engines & Python Suites)
```bash
make test
```
*Executes all NIST FIPS 203/204 KATs, cross-engine interoperability tests, internal fault injection experiments, and Python unit & integration suites.*

### Step 3: Run Real-Time System Diagnostic Health Check
```bash
make health-check
# or directly:
python3 -m astra_sec.app health
```

### Step 4: Multi-Node Simulation via Docker Compose
```bash
docker compose up --build
```

For developer guidelines, zero-heap flight invariants, and architectural rules, see [`AGENTS.md`](file:///Users/dhairyajain/Desktop/pqc research/AGENTS.md) and [`docs/implementation-roadmap.md`](file:///Users/dhairyajain/Desktop/pqc research/docs/implementation-roadmap.md).

---

## 7. Experimental Data & Provenance

All primary datasets used in this research are cataloged with genuine cryptographic SHA-256 digests in [`data/manifests/dataset_provenance_manifest.csv`](file:///Users/dhairyajain/Desktop/pqc%20research/data/manifests/dataset_provenance_manifest.csv):
- `tfib_benchmark_raw.csv`: 15,000 raw latency trials across baseline and hardened NTT configurations.
- `tfib_trial_level_results.csv`: 900 canonical fault injection trials.
- `raw_production_trials.csv`: 400 cleanroom production trials.
- `h1_activation_audit.csv`: 600 targeted injection trials validating circular verifier vulnerabilities.
