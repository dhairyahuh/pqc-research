# Paper Track 1 — Internal Fault Detection & Localized Recovery

## RESEARCH MAP

**Status:** KEEP (Primary candidate)  
**Decision:** This track has the strongest evidence base and clearest novelty positioning.

---

## Provisional Title
"Software-Level Dual-Transform NTT Invariant Monitoring with Localized Register Rollback for ML-KEM-768"

## Research Question
Can pure-software algebraic invariant monitoring across all forward Cooley-Tukey and inverse Gentleman-Sande NTT butterflies, combined with localized single-butterfly register rollback, provide complete transient fault recovery and deterministic fail-stop containment in ML-KEM-768 decapsulation at significantly lower overhead than software DMR?

## Hypotheses
- **H1:** Transient single-butterfly faults are recovered in-place with 100% success (output = K_valid).
- **H2:** Persistent faults escalate to 100% deterministic implicit rejection (K_rej) with zero SDC.

## Implementation Components
| Component | Location |
|:---|:---|
| Instrumented poly.c (CT + GS monitors) | `algorithms/source_ref/mlkem/src/poly.c` |
| TFIB core (invariant checking + rollback) | `tfib_implementation/tfib_core.c/h` |
| TFIB ref (reference countermeasure) | `tfib_implementation/tfib_ref.c/h` |
| TFIB meta (meta-countermeasure) | `tfib_implementation/tfib_meta.c/h` |
| Fault hooks | `algorithms/source_ref/mlkem_fault_hooks.c/h` |
| Campaign PRF (deterministic seeds) | `tfib_experiments/campaign_prf.h` |

## Existing Evidence
| Evidence | Location | Status |
|:---|:---|:---|
| Step 2C-A campaign (900 trials) | `tfib_experiments/phase2_step2c_trial_results.csv` | REPRODUCED |
| Benchmark raw data | `tfib_benchmark_raw.csv` | REPORTED |
| FIPS KAT pass | `tests/test_fips_kats.c` → binary | REPRODUCED (partial) |
| Oracle verification | `tfib_experiments/phase11_oracle/` | REPRODUCED |
| Gate A test vectors | `research/phase18_gate_a/` | REPORTED |
| SHAKE-256 verification | Evidence Ledger L4 | VERIFIED |

## Reported Findings (from manuscript and contribution analysis)
1. 100/100 transient fault recovery (F4), 95% CI [96.30%, 100.00%] `[REPORTED]`
2. 200/200 persistent fail-stop (F5A+F5B), 95% CI [98.14%, 100.00%] `[REPORTED]`
3. 0/300 SDC, 95% CI [0.00%, 1.26%] `[REPORTED]`
4. +16.9% overhead under -O3, +25.3% under -O2 vs +135-149% for DMR `[REPORTED]`
5. Circular verifier 98.5% false-pass (591/600) `[REPORTED]`
6. Twiddle factor blindness 0.0% local detection `[REPORTED]`

## Claims Supported by Raw Data
- Step 2C-A aggregate counts verified: 900 trials, 0 SDC, 750 fault-activated `[REPRODUCED]`
- Deterministic reproducibility: SHA-256 match of trial CSV `[REPRODUCED]`
- Symbolic injection only (no const table mutation) `[VERIFIED]`

## Claims That Remain Unverified
- Per-butterfly coverage across all 9,856 butterflies (source-level verification needed)
- Benchmark platform (M1 vs M3 Pro discrepancy)
- Circular verifier denominator and exact test configuration
- Complete constant-time compliance claim (Cohen's d, KS test)
- Formal proof of twiddle blindness theorem (location and verification needed)

## Main Limitations and Possible Confounders
1. Software fault injection only — not physical radiation testing
2. Single platform tested (Apple Silicon arm64)
3. Single-butterfly fault model — multi-bit simultaneous upsets not covered by Tier 1
4. No adversarial fault resistance (SIFA/DFA explicitly excluded)
5. Twiddle factor blindness creates a known detection gap at the local invariant level

## Relevant Prior-Work Questions
1. Does Paul et al. (ACM TECS 2026) cover inverse GS invariants or software realization?
2. Does any IEEE paper provide software-level NTT fault recovery (not just detection)?
3. Has localized single-butterfly rollback been published in any domain?
4. What overhead do existing hardware schemes report, and how does ours compare?

## What Must Be Completed Before Paper Can Be Defended
1. Literature review with verified full texts (P1 papers from shortlist)
2. Platform contradiction resolved
3. FIPS KATs rebuilt from current source and passed
4. Benchmark numbers confirmed on stated platform
5. Per-butterfly instrumentation coverage verified against source
6. Twiddle blindness proof located and independently checked

## Provisional Decision: **KEEP** — Primary research direction
