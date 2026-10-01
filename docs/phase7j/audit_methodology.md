# Phase 7J: Audit Methodology & Evidence Integrity

## 1. Audit Charter & Independence Protocol

Phase 7J serves as an **independent verification and audit phase** of the claims, source modifications, and experimental datasets produced in Phase 7I regarding combined Forward (Cooley–Tukey) and Inverse (Gentleman–Sande) Number Theoretic Transform (NTT) fault monitoring in NIST FIPS 203 ML-KEM-768 decapsulation.

### Principles of Independent Validation:
1. **Adversarial Scrutiny**: Prior claims are treated as assertions to be tested rather than established facts.
2. **Execution-Path Proof**: Source presence alone is insufficient; instrumentation and runtime counters must verify that claimed monitor code actually executes during production calls.
3. **Data Integrity & Traceability**: Raw trial-level JSON datasets must be independently analyzed for structural integrity, missing records, duplicate IDs, and counter cross-talk.
4. **Reproducibility with Broader Scope**: Experiments must be reproduced with broader parameter variation (multi-layer, multi-bit, retry-path, shadow-register, and checker-perturbation faults).
5. **Separation of Concerns**: We strictly distinguish transient arithmetic fault recovery ($K == K_{\text{valid}}$), safe implicit rejection ($K == K_{\text{rej}}$), benign algebraic equivalence, and uncontained corruption ($K \neq K_{\text{valid}} \wedge K \neq K_{\text{rej}}$).

---

## 2. Repository & Baseline Integrity Inspection

At the start of Phase 7J, the repository state was recorded:
- **Baseline Git Commit**: [`8bfc4fec9d5a4e9efac139fd429e5f37d33bcdab`](https://github.com/dhairyahuh/pqc-research/commit/8bfc4fec9d5a4e9efac139fd429e5f37d33bcdab) (`research(phase-7i): evaluate inverse NTT fault monitoring`).
- **Branch**: `main` (synced with `origin/main`).
- **Pre-Existing Uncommitted Files**:
  - `README.md`
  - `experiments/fault_injection/mlkem768_internal_fault_experiment.c`
  - `experiments/system_model/spacecraft_protocol_sim.py`
  - `fault_injection/fault_models/fault_definitions.py`
  - `results/spacecraft_protocol_desync_results.json`
  - `tests/test_fips_kats.c`
  These files were carefully preserved without modification or staging.

---

## 3. Independent Audit Workflow

The audit was conducted across five independent modules:
1. **Source & Execution Trace Audit**:
   - Traced the call path from public API `mlkem768_dec` through `indcpa.c` and `poly.c` to establish the exact polynomial transform call counts and butterfly numbers.
2. **Mathematical Re-Derivation**:
   - Replaced informal derivative arguments over finite fields with a formal polynomial identity and algebraic proof over the field $\mathbb{F}_q$ ($q=3329$).
3. **Phase 7I Dataset Recomputation**:
   - Developed `experiments/phase7j/audit_phase7i_analysis.py` to ingest `results/phase7i/raw/phase7i_e2e_trials.json` (1,400 trials) and recompute per-class counts, Wilson 95% confidence intervals, and discrepancy checks.
4. **Extended Adversarial Campaign (1,600 Trials)**:
   - Designed and compiled `experiments/phase7j/phase7j_independent_validator.c` executing 16 threat classes covering multi-layer, multi-bit, shadow register, and retry-path injections.
5. **Multi-Run Performance & Timing Audit**:
   - Executed 3 repeated benchmark runs ($N=6,000$ decapsulations per configuration) and 1,000 randomized valid/invalid ciphertext timing pairs to evaluate run-to-run drift, effect size, and Welch's $t$-test significance.
