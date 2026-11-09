# ASTRA-Sec Phase 3: Reproducibility Protocol and Data Provenance

## 1. Principles of Scientific Reproducibility

A central mandate of Phase 3 is ensuring that every experimental claim is fully verifiable by an external auditor. To eliminate ambiguity, every trial run emits an immutable cryptographic provenance manifest alongside raw, unaggregated line-delimited JSONL measurements.

---

## 2. Cryptographic Provenance Manifest Schema

Every experiment automatically produces a manifest JSON file with the following verified structure:

```json
{
  "manifest_version": "1.0",
  "experiment_id": "24bd1cdf-a525-4601-8486-9676590419c9",
  "status": "COMPLETED",
  "start_time_utc": "2026-11-09T15:06:11.831558+00:00",
  "end_time_utc": "2026-11-09T15:06:12.306354+00:00",
  "environment": {
    "git_commit": "b0b915f0c3f2ad5fa15d1d99cc2e49329367f940",
    "git_branch": "astra-sec",
    "git_dirty": true,
    "python_version": "3.9.6",
    "os_name": "Darwin",
    "os_release": "27.0.0",
    "os_architecture": "arm64",
    "processor": "arm",
    "cpu_logical_cores": 8,
    "total_ram_bytes": 8589934592
  },
  "config_hash": "21318270a4de33d0efc16772a0889f417f7b538e12d46e9df0ba5d3abde3b01a",
  "configuration": { ... },
  "raw_output_path": ".../results/raw/EXP-D01-FULL-ASTRA_24bd1cdf.jsonl",
  "summary_statistics": { ... }
}
```

---

## 3. Configuration Integrity & Determinism

### 3.1. SHA-256 Configuration Hashing
Before execution, the orchestrator serializes the Pydantic experiment model into canonical JSON with sorted keys, computes the SHA-256 digest, and embeds it into the manifest. Any alteration to parameters (payload size, loss rate, fault injection probability) alters the hash, preventing silent parameter drift.

### 3.2. PRNG Seed Management
All random processes (payload content generation, Bernoulli loss decisions, fault bit selection) are governed by explicit integer seeds declared in the configuration file (`random_seed: 1001, 2002, 3003, ...`). Re-running an experiment with the same configuration and seed produces identical packet sequences and fault locations.

---

## 4. Independent Verification Instructions

An external reviewer can reproduce and verify the laboratory results with the following commands:

```bash
# 1. Validate all canonical JSON experiment configurations
make lab-validate

# 2. Execute the self-test test suite for laboratory harness and statistics
make lab-test

# 3. Execute the pilot experiment and inspect output manifest
make lab-pilot

# 4. Execute the full experimental campaign suite
make lab-campaign

# 5. Inspect raw data and verify manifest integrity
ls -l research/phase3_experimental_lab/results/raw/
ls -l research/phase3_experimental_lab/results/manifests/
```
