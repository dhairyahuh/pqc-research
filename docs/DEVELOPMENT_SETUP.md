# ASTRA-Sec: Development Environment Setup Guide

This guide provides verified, step-by-step instructions for establishing a clean development and research environment for ASTRA-Sec on macOS and Linux systems.

---

## 1. System Requirements & Toolchains

### Operating Systems Tested
- **macOS**: macOS 14.x (Sonoma) / 15.x (Sequoia) on Apple Silicon (M1/M2/M3/M4) or Intel x86_64.
- **Linux**: Ubuntu 22.04 LTS / 24.04 LTS, Debian 12, Fedora 39, RHEL 9.

### Required Software
- **Python**: Version 3.9, 3.10, 3.11, or 3.12 (must include `python3-dev` / `python3-pip`).
- **C Compiler**: Clang (LLVM 14+) or GCC (version 10+) supporting C99/C11 standards.
- **Build Tools**: GNU Make 3.81+, Git 2.30+.
- **Database**: SQLite 3.35+ (standard with Python 3.9+).
- **Web Browser**: Chrome, Edge, Safari, or Firefox with WebGL enabled (for 3D Mission Control).

---

## 2. Step-by-Step Installation

### Step 1: Clone the Repository
Clone the repository directly on the `astra-sec` development branch:
```bash
git clone --branch astra-sec --single-branch https://github.com/dhairyajain/pqc-research.git
cd pqc-research
```

### Step 2: Establish Python Virtual Environment
Always install dependencies within an isolated virtual environment:
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip to latest version
pip install --upgrade pip
```

### Step 3: Install Dependencies
Install development packages and install ASTRA-Sec in editable mode:
```bash
pip install -r requirements/dev.txt
pip install -e .
```

Verify Python package versions:
```bash
python3 -c "import fastapi, pydantic, uvicorn; print('FastAPI:', fastapi.__version__, '| Pydantic:', pydantic.__version__)"
```

### Step 4: Configure Local Environment
Copy the `.env.example` template to `.env`:
```bash
cp .env.example .env
```
Default parameters are pre-configured for local 4-node simulation. No modifications are necessary for development or testing.

### Step 5: Compile Native C Cryptographic Components
Build the C Known Answer Test (KAT) runners, fault injection harnesses, and the shared C library (`libastra_crypto`):
```bash
make build
```
On macOS, this produces:
- `bin/libastra_crypto.dylib`
- `bin/test_fips_kats`
- `bin/test_interop`
- `bin/ml_kem_harness`
- `bin/ml_dsa_harness`
- `bin/mlkem768_internal_fault_experiment`

On Linux, `bin/libastra_crypto.so` is built automatically with `-shared -fPIC`.

---

## 3. Verifying Installation Health

Run the system diagnostic health check to confirm that configuration, storage directories, and native C bridges are functional:
```bash
make health-check
```

Expected diagnostic output:
```text
=========================================================================
 ASTRA-Sec System Diagnostic Health Report — Version 0.1.0
=========================================================================
 Node EID:        dtn://gsa/app
 Node Role:       originator
 Overall Status:  OK
 Uptime (sec):    0.002
 Component Breakdown:
   [PASS] configuration      : PASS
   [PASS] storage            : PASS
   [PASS] c_crypto_engine    : PASS
=========================================================================
```

---

## 4. Running the Test Suites

Execute the comprehensive test pipeline:
```bash
# Run all Python unit and integration tests (59 test cases)
make test-python

# Run C Known Answer Tests and fault injection campaigns
make test-c

# Run Python static syntax check
make lint
```

---

## 5. Starting the Flight Operations Dashboard

Launch the FastAPI backend and 3D geospatial mission control:
```bash
make dashboard
```
Open **`http://127.0.0.1:8000`** in your browser to verify the interactive 3D Earth, spacecraft models, and cryptographic pipeline console.
