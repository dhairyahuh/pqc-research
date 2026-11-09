# Phase 00: Environment Audit Report
## ASTRA-Sec Development — Existing Platform & Toolchain Inspection

**Author:** ASTRA-Sec Development Agent  
**Date:** November 2026  
**Status:** Complete  
**Scope:** Host system hardware, operating system, compilers, interpreters, package managers, development utilities, containerization, and workspace layout.

---

## 1. System Hardware & Operating System

The baseline development environment has been inspected on the host system:

| Parameter | Observed System Value | Verification Command | Notes |
|---|---|---|---|
| **Operating System** | macOS 27.0.1 (Build 26A434) | `sw_vers` | Modern Darwin release |
| **Darwin Kernel Version** | 27.0.0 (Tue Aug 11 21:05:27 PDT 2026; root:xnu-13432.1.9~1/RELEASE_ARM64_T8103) | `uname -a` | ARM64 Darwin Kernel |
| **CPU Architecture** | arm64 (Apple Silicon) | `uname -m` | 64-bit ARM architecture |
| **Processor Model** | Apple M1 | `sysctl -n machdep.cpu.brand_string` | 8-core SoC |
| **CPU Core Count** | 8 logical cores (4 Performance + 4 Efficiency) | `sysctl -n hw.ncpu` | Supports parallel test runners |
| **Byte Ordering** | Little-Endian | Architecture default | Standard for ARM64 and x86_64 |

---

## 2. Compilers & Toolchains

The C toolchain and cross-compilation infrastructure were audited:

| Tool | Executable Path | Version String | Capabilities & Notes |
|---|---|---|---|
| **C Compiler (Clang)** | `/usr/bin/clang` | `Apple clang version 21.0.0 (clang-2100.1.1.101)` | Target: `arm64-apple-darwin27.0.0`. Full support for C99, C11, C17, GNU extensions, SIMD NEON intrinsics. |
| **C Compiler (GCC alias)** | `/usr/bin/gcc` | `Apple clang version 21.0.0 (clang-2100.1.1.101)` | Alias symlinked to Apple Clang on macOS. |
| **Linker** | `/usr/bin/ld` | Apple cctools-1010.6 (Xcode CLI tools) | Standard Mach-O 64-bit dynamic and static linker. |
| **Archiver** | `/usr/bin/ar` | BSD ar (cctools-1010.6) | Generates static `.a` archive libraries (`libtfib.a`). |
| **Symbol Table Tool** | `/usr/bin/ranlib` | BSD ranlib | Indexes static libraries. |

### C Compiler Diagnostics & Optimization Flags
Existing Makefiles use standard `-O3 -Wall -Wextra -std=c99` (for `mlkem-native`) and `-std=c11` (for harnesses). Apple Clang 21 produces strict diagnostics.

---

## 3. Interpreters & Scripting Runtimes

| Runtime | Path | Version | Usage in Repository |
|---|---|---|---|
| **Python 3** | `/usr/bin/python3` | `Python 3.9.6` | Benchmark statistical processing, JSON parsing, automated campaign analysis (`tests/*.py`, `results/`). |
| **Shell** | `/bin/zsh` (default), `/bin/bash` | zsh 5.9, GNU bash 3.2.57(1)-release | Test harness automation and shell-level experiment orchestrators (`experiments/*.sh`). |

---

## 4. Build Systems & Package Managers

| Utility | Path | Version | Purpose in Repository |
|---|---|---|---|
| **GNU Make** | `/usr/bin/make` | `GNU Make 3.81` (built for i386-apple-darwin11.3.0) | Primary build orchestrator for all C libraries, objects, KAT runners, and experiment binaries. |
| **CMake** | `/opt/homebrew/bin/cmake` | `cmake version 4.4.3` | Path A baseline build configuration (`CMakeLists.txt`). |
| **Homebrew** | `/opt/homebrew/bin/brew` | `Homebrew 7.0.7` | Primary package manager on macOS ARM64. |

---

## 5. External Libraries & Dependencies

| Library | Header Location | Library Binary Location | Version / Provider | Role |
|---|---|---|---|---|
| **liboqs** | `/opt/homebrew/include/oqs/oqs.h` | `/opt/homebrew/lib/liboqs.dylib` | Open Quantum Safe (via Homebrew) | Used strictly for Path A baseline cross-validation in `test_interop`. Monitored Path B (`mlkem-native`) has **zero** dependency on `liboqs`. |
| **POSIX Standard Libs** | `/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/include` | System Dynamic Linker | macOS SDK | Provides `<stdint.h>`, `<stddef.h>`, `<string.h>`, `<stdbool.h>`, `<time.h>`. |

---

## 6. Containerization & Isolation

| Utility | Path | Version | Daemon Status | Notes |
|---|---|---|---|---|
| **Docker CLI** | `/usr/local/bin/docker` | `Docker version 29.2.1, build a5c7197` | **Inactive** (Daemon socket `unix:///Users/dhairyajain/.docker/run/docker.sock` not connected) | Docker CLI is installed. Docker Desktop engine is not running in background. Host-native compilation is active. |

---

## 7. Storage & Disk Allocation

| Filesystem | Total Capacity | Used Space | Available Space | Utilization % | Mount Point |
|---|---|---|---|---|---|
| `/dev/disk3s1` (APFS) | 228 GiB | 168 GiB | **33 GiB** | 84% | `/System/Volumes/Data` |

There is 33 GiB of available storage on the root data volume, which is sufficient for C compilation, artifact generation, and local dataset logging.

---

## 8. Existing Project Directory Layout

The workspace root (`/Users/dhairyajain/Desktop/pqc research`) contains the following key directories:

```
pqc-research/
├── algorithms/                 # Cryptographic implementations (mlkem-native, mldsa-native, hooks)
│   ├── ml-kem/                 # Path A liboqs ML-KEM harness
│   ├── ml-dsa/                 # Path A liboqs ML-DSA harness
│   └── source_ref/             # Path B production reference implementations & fault hooks
├── benchmarks/                 # Nanosecond-precision timing harnesses (DMR, e2e, monitored)
├── bin/                        # Compiled executable binaries (test_fips_kats, harnesses)
├── chatgpt/                    # Independent reproducibility audit scripts and datasets
├── data/                       # Experimental CSV datasets and logs
├── deploy_perf_bundle/         # Deployment performance benchmarks and audit papers
├── docs/                       # Research documentation, architecture specs, handover guides
├── experiments/                # Campaign runners and fault injection drivers
├── fault_injection/            # Legacy fault injection utilities
├── literature/                 # Academic references, survey papers, DOIs
├── paper/                      # IEEE-format research manuscript, BibTeX, backup milestones
├── phase18_audit/              # Cleanroom production reproducer and 400 audited trial records
├── presentation/               # Master Research Presentation Handbook
├── results/                    # Processed JSON and CSV benchmark logs
├── tests/                      # Automated unit tests, KAT runners, interop tests
├── tfib_experiments/           # Canonical 900-trial experimental runner and independence tests
└── tfib_implementation/        # Hardened v2 Twiddle Factor Integrity Binding (TFIB) source
```

---

## 9. Conclusion of Environment Audit

The host system is fully equipped with modern C99/C11 compilers (Apple Clang 21), build tools (Make, CMake), and sufficient storage (33 GiB free). Host-native compilation of the existing PQC codebase functions with zero missing dependencies.
