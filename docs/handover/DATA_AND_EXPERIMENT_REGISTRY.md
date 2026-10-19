# Data and Experiment Registry

**Repository:** `pqc-research`  
**Active Branch:** `space-resilience-framework`  
**Author:** Dhairya Jain  
**Handover Recipient:** Ayush  
**Date:** October 2026  

This registry provides an authoritative, evidence-backed inventory of all experimental datasets, raw trial CSVs, processed benchmark distributions, and test logs across the repository.

---

## 1. Primary Raw Experimental Datasets

### 1.1 Production Fault Campaign (`phase18_audit/raw_production_trials.csv`)
- **Category:** Primary Raw Data (`[DIRECTLY OBSERVED]`)
- **File Size:** 38,720 bytes (401 lines, 400 data rows)
- **SHA-256:** `9d5ca2dfc03dc0c88a70426b4c70cd567b93666f0e6d095dc39e43b2952b36d4`
- **Generating Command / Harness:**
  ```bash
  clang -O3 -Wall -Wextra -std=c11 -I. -Ialgorithms/source_ref/mlkem \
    phase18_audit/production_reproducer.c bin/obj/mlkem768_inst.o bin/obj/mlkem_fault_hooks.o \
    -o phase18_audit/production_reproducer && ./phase18_audit/production_reproducer
  ```
- **Population & Denominators ($N=400$):**
  - `F12_CLEAN_BASELINE` ($N=100$): 100 clean-baseline controls. Validates $0$ false-alarm aborts and $100.0\%$ clean-success rate.
  - `F4_TRANSIENT_RECOVERY` ($N=100$): 100 active transient multiplier bitflip trials. Validates $100.0\%$ in-place recovery on retry 1 (`matches_valid_key==1`).
  - `F5A_RECURRING_BITFLIP` ($N=100$): 100 active persistent multiplier faults. Validates $100.0\%$ safe fail-stop escalation (`matches_rejection_key==1`).
  - `F5B_FORCE_VALUE_ZERO` ($N=100$): 100 active software force-zeroing faults. Validates $100.0\%$ safe fail-stop escalation (`matches_rejection_key==1`).
- **SDC Accounting:** Zero SDC observed across all 300 active trials ($SDC = 0/300$, $95\%$ Wilson CI: $[0.00\%, 1.26\%]$).
- **Manuscript Mapping:** Supported rows F12, F4, F5A, F5B, and analytical aggregate row H2 in Table 2.

---

### 1.2 Invalid-Ciphertext KAT Conformance (`phase11_conformance_audit/invalid_ciphertext_trials.csv`)
- **Category:** Primary Raw Data (`[DIRECTLY OBSERVED]`)
- **File Size:** 18,349 bytes (101 lines, 100 data rows)
- **SHA-256:** `ed73e599859bf44bdedd010acc2d64bdb82094e5631432f0a304b2b5d077a4e8`
- **Generating Harness:** `phase11_conformance_audit/run_conformance_audit.c`
- **Population & Denominators ($N=100$):**
  - 100 deterministic single-bit mutations across the 1,088-byte ciphertext space.
  - $100/100$ ($100.0\%$) trials deterministically produced implicit rejection matching the independent Keccak-f[1600] SHAKE-256 oracle.
- **Manuscript Mapping:** Supported row KAT in Table 2.

---

### 1.3 Circular-Verifier Vulnerability Campaign (`phase16_targeted_evidence_closure/h1_activation_audit.csv`)
- **Category:** Primary Raw Data (`[DIRECTLY OBSERVED]`)
- **File Size:** 241,120 bytes (1,201 lines, 1,200 data rows)
- **SHA-256:** `8684ed492178a0677edee99eacdc66224e6afbc597d685b7302b444152cd7a56`
- **Audited Population ($N=600$ across 6 vulnerable targets):**
  - Evaluates circular checkers that read live faulted registers rather than snapshot inputs.
  - T1 (CT Multiplier): 98 false passes / 100 trials ($98.0\%$, $[93.0\%, 99.5\%]$)
  - T2 (CT Subtractor): 94 false passes / 100 trials ($94.0\%$, $[87.5\%, 97.2\%]$)
  - T3 (GS Adder): 100 false passes / 100 trials ($100.0\%$, $[96.3\%, 100.0\%]$)
  - T4 (GS Multiplier): 100 false passes / 100 trials ($100.0\%$, $[96.3\%, 100.0\%]$)
  - T5 (Twiddle Scale): 99 false passes / 100 trials ($99.0\%$, $[94.6\%, 99.8\%]$)
  - T6 (In-Place Array): 100 false passes / 100 trials ($100.0\%$, $[96.3\%, 100.0\%]$)
  - **Aggregate Total:** **591 false passes / 600 trials** ($98.5\%$, $95\%$ Wilson score CI: $[97.2\%, 99.2\%]$).
- **Manuscript Mapping:** Supported Table 3 and Section 6.2.

---

### 1.4 Canonical 900-Trial TFIB Campaign (`tfib_trial_level_results.csv`)
- **Category:** Primary Raw Data (`[DIRECTLY OBSERVED]`)
- **File Size:** 79,936 bytes (901 lines, 900 data rows)
- **SHA-256:** `cff3514984a2042c2de3dbd53202abc8835faf9ebe3788eea494ce878c8a44f1`
- **Population & Denominators ($N=900$):**
  - Clean Controls: Exactly 150 trials (`CLEAN_CONTROL`).
  - Active Fault Injections: Exactly 750 trials across 9 fault suites:
    - `OP_TWIDDLE_TRANSIENT` ($N=150$), `OP_TWIDDLE_PERSISTENT` ($N=150$)
    - `REF_TWIDDLE_TRANSIENT` ($N=50$), `REF_TWIDDLE_PERSISTENT` ($N=50$)
    - `SIMULTANEOUS_COMMON_MODE` ($N=50$)
    - `CHECKER_LOGIC_TRANSIENT` ($N=100$), `CHECKER_LOGIC_PERSISTENT` ($N=100$)
    - `META_TAG_TRANSIENT` ($N=50$), `META_TAG_PERSISTENT` ($N=50$)
- **Outcome Classifications ($N=750$ Active):**
  - Genuine Recovery: 250 trials
  - Safe Fail-Stop: 350 trials
  - Local Blind FO-Contained: 147 trials
  - Ineffective Fault (Clean Valid): 3 trials
  - Silent Data Corruption: **0 trials** ($0/750$, one-sided $97.5\%$ Clopper-Pearson upper bound: **0.49%**).
- **Manuscript Mapping:** Supported Abstract (Line 18), Introduction (Line 50), and Section 6.1 (Line 306).

---

### 1.5 Twiddle Factor Memory Corruption Pilot (`results/phase15q/trial_ledger.csv`)
- **Category:** Primary Raw Data (`[DIRECTLY OBSERVED]`)
- **File Size:** 3,299 bytes (17 lines, 16 data rows)
- **SHA-256:** `5cf48fb9ab869cff6345eb1b8d03785ec65d3ab1c2ee76cab29d4ea6bde45d2c`
- **Population & Denominators ($N=16$ on reference vector):**
  - 11 active mutations directly altering consumed twiddle factors (`zetas[1, 2, 32, 63, 64, 95, 127]`).
  - All 11 active consumed mutations bypassed local butterfly checks but deterministically triggered FO re-encryption rejection (`crypto_endpoint == REJECTION`).
  - 5 controls (2 golden baselines, 1 unused root factor, 2 sham zero masks) behaved as expected.
- **Manuscript Mapping:** Supported Section 3.3 and Section 7 Item 2.

---

## 2. Processed Performance and Timing Records

### 2.1 Phase 7H Isolated Timing Distribution (`results/phase7h/processed/phase7h_timing_distribution.json`)
- **Category:** Processed Benchmark Data (`[DIRECTLY OBSERVED]`)
- **SHA-256:** `08fccaea31dde745e617e109e3d668c73f0f69685a1efe44fd755b5bf531a5be`
- **Metrics ($N=2{,}000$ iterations):**
  - Baseline Mean: $46.65\,\mu\text{s}$ ($\sigma = 14.32\,\mu\text{s}$, median $46.00\,\mu\text{s}$, p95 $47.00\,\mu\text{s}$)
  - DMR Mean: $92.98\,\mu\text{s}$ ($\sigma = 12.97\,\mu\text{s}$, median $92.00\,\mu\text{s}$, p95 $95.00\,\mu\text{s}$)
  - Logged Overhead Metric: $+99.33\%$ (ratio of displayed rounded means: $+99.31\%$)
- **Significance:** Empirical proof that software sequential duplicate decapsulation requires $\approx +100\%$ overhead.

### 2.2 Phase 7I End-to-End Latency & Butterfly Counts (`results/phase7i/processed/phase7i_e2e_results.json`)
- **Category:** Processed Benchmark Data (`[DIRECTLY OBSERVED]`)
- **SHA-256:** `5e294c5634002f37fc8ec723077c84f0442587812d701b2a4add54d290a8a9dd`
- **Metrics ($N=2{,}000$ warm-stabilized decapsulations on Apple M3 Pro, `-O3`):**
  - Total Butterflies: **9,856** (5,376 Forward CT, 4,480 Inverse GS)
  - Baseline Latency: $110.77\,\mu\text{s}$ ($\sigma = 4.82\,\mu\text{s}$)
  - Monitored Invariant + Rollback: $129.51\,\mu\text{s}$ ($\sigma = 5.14\,\mu\text{s}$)
  - Overhead: **+16.9%** ($1.17\times$ slowdown)
- **Disclosure Note:** Table 4 footnote 1 notes an alternate summary run logging $\sigma = 1.42\,\mu\text{s}$ and $5.61\,\mu\text{s}$; raw per-iteration sample records were not persisted to disk.

---

## 3. Data Integrity & Traceability Rules for Ayush

1. **Never Overwrite Raw CSVs:** Raw trial logs must remain immutable. Any new recomputation should output to a new script or derived summary file.
2. **Never Pool Populations:** Do not aggregate the 400 production records with the 900 campaign records or the 100 conformance records; they evaluate distinct harnesses and fault models.
3. **Always Check Hashes:** Before citing or analyzing any dataset, verify that its SHA-256 matches the manifest in [`reproducibility_manifest.json`](file:///Users/dhairyajain/Desktop/pqc%20research/docs/handover/reproducibility_manifest.json).
