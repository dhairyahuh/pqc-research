# AI PPT FACT-CHECK REGISTER
## Research Programme: Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems
### Current Implementation Case Study: Software-Level Fault Resilience for ML-KEM-768 Decapsulation

**Anti-Hallucination Protocol:** Every claim in the slide deck that contains a numerical figure, a statistical bound, a pass/fail outcome, a compliance statement, or a performance metric is registered here with its evidentiary source, sample size, verification status, and technical caveats.

---

## Verification Status Definitions
- **[DIRECTLY OBSERVED]:** Directly inspected in raw repository files (CSV, JSON, source code) or verified through direct command execution during this audit.
- **[INDEPENDENTLY VERIFIED]:** Recomputed from underlying raw data files during this audit.
- **[REPORTED BY PRIOR PHASE]:** Recorded in prior phase documentation, audit ledgers, or console stdout logs where raw per-iteration data was not persisted to disk.
- **[INFERRED]:** Mathematically derived from directly verified base quantities.

---

## Section 1: Core Performance Claims & Benchmark Scopes

### Claim 1.1 — End-to-End Decapsulation Latency Overhead: +16.9% (Comparison A)

| Field | Value |
|---|---|
| **Claim as stated** | "+16.9% latency overhead on monitored architecture for full ML-KEM-768 decapsulation" |
| **Numerical values** | Baseline: 110.77 µs; Monitored: 129.51 µs; Latency Ratio: 1.169× (+16.9%) |
| **Source file** | `AYUSH.md` (Section 15) and `paper/manuscript.md` (Abstract, Table 4) |
| **Methodology** | N=2,000 warm decapsulations; Apple Silicon ARM64 (Apple M3 Pro); macOS Darwin 25.1.0; Apple Clang 17.0.0; `-O3` |
| **Verification status** | **REPORTED BY PRIOR PHASE** — Captured from stdout console summary logs. Per-iteration raw sample CSV was not persisted to disk (explicitly disclosed in manuscript Table 4, footnote 1). |
| **Known caveat** | Two historical benchmark logs recorded slightly different standard deviations (4.82 µs / 5.14 µs vs 1.42 µs / 5.61 µs). The mean (+16.9%) is cited in the manuscript. Measures end-to-end decapsulation, distinct from isolated NTT transforms. |
| **Slide usage** | Slides 01, 08 (Comparison A), 11 |

---

### Claim 1.2 — Isolated NTT Sequential DMR Overhead: +99.33% (Comparison B)

| Field | Value |
|---|---|
| **Claim as stated** | "Sequential software DMR incurs +99.33% overhead at the isolated NTT level" |
| **Numerical values** | Baseline NTT: 46.65 µs; DMR NTT: 92.98 µs; Overhead: +99.33% |
| **Source file** | `results/phase7h/processed/phase7h_timing_distribution.json` |
| **Methodology** | N=2,000 runs; Phase 7H isolated NTT-level benchmark; same hardware and compiler settings |
| **Verification status** | **DIRECTLY OBSERVED** — JSON artifact directly inspected and numerical values verified. |
| **Known caveat** | This measures isolated NTT-level DMR, not full decapsulation DMR. Conceptual full-decapsulation DMR latency (≥+100%) is an analytical extrapolation and is deliberately NOT presented as an experimentally measured end-to-end result. |
| **Slide usage** | Slides 01, 03, 08 (Comparison B), 11 |

---

### Claim 1.3 — Phase 7I Combined Dual-Transform NTT Monitoring Overhead: +17.27% (Comparison B)

| Field | Value |
|---|---|
| **Claim as stated** | "Phase 7I combined dual-transform NTT monitoring overhead: +17.27%" |
| **Numerical values** | Baseline Dual-NTT: 68.47 µs; Combined Monitored Dual-NTT: 80.30 µs; Overhead: +17.27% |
| **Source file** | `results/phase7i/processed/phase7i_e2e_results.json` |
| **Methodology** | N=2,000 runs; Phase 7I isolated forward + inverse NTT monitoring benchmark |
| **Verification status** | **DIRECTLY OBSERVED** — JSON artifact directly inspected and numerical values verified. |
| **Known caveat** | Distinct from Claim 1.1: Phase 7I measures combined NTT transforms only (80.30 µs vs 68.47 µs), whereas Claim 1.1 measures end-to-end decapsulation (129.51 µs vs 110.77 µs). Slides 08 explicitly segregates these two comparisons. |
| **Slide usage** | Slide 08 (Comparison B) |

---

### Claim 1.4 — Phase 7H Single-Rail Recomputed Check: +19.18% (Comparison B)

| Field | Value |
|---|---|
| **Claim as stated** | "Single-rail recomputed intermediate check overhead: +19.18%" |
| **Numerical values** | Baseline: 46.65 µs; Recomputed_t: 55.59 µs; Overhead: +19.18% |
| **Source file** | `results/phase7h/processed/phase7h_timing_distribution.json` |
| **Methodology** | N=2,000 runs; Phase 7H single-rail isolated NTT benchmark |
| **Verification status** | **DIRECTLY OBSERVED** — JSON artifact verified. |
| **Slide usage** | Slide 08 (Comparison B reference) |

---

## Section 2: Fault Containment Claims

### Claim 2.1 — Transient Multiplier Upset Recovery (F4): 100/100

| Field | Value |
|---|---|
| **Claim as stated** | "100/100 transient multiplier upsets recover on retry 1" |
| **Numerical values** | 100 genuine recovery outcomes out of 100 armed transient trials |
| **Source file** | `phase18_audit/raw_production_trials.csv` |
| **Verification status** | **DIRECTLY OBSERVED & INDEPENDENTLY VERIFIED** — 400-row CSV inspected; exactly 100 rows with `target = F4_TRANSIENT_RECOVERY` exhibit `outcome = GENUINE_RECOVERY` and `matches_valid_key = 1`. |
| **Sample size** | N = 100 |
| **Confidence interval** | 95% Wilson score CI: [96.30%, 100.00%] |
| **Scope qualifier** | Across evaluated fault configurations, detected transient faults recovered locally; this does not establish universal coverage against every possible fault class. |
| **Slide usage** | Slides 01, 07, 08, 11 |

---

### Claim 2.2 — Persistent Fault Safe Fail-Stop (F5A + F5B): 200/200

| Field | Value |
|---|---|
| **Claim as stated** | "200/200 persistent fault trials safely escalate to FIPS 203 implicit rejection" |
| **Numerical values** | 200 rows with `outcome = SAFE_FAIL_STOP` (100 F5A recurring bit-flip + 100 F5B force-zero) |
| **Source file** | `phase18_audit/raw_production_trials.csv` |
| **Verification status** | **DIRECTLY OBSERVED & INDEPENDENTLY VERIFIED** — 100 F5A rows + 100 F5B rows all show `outcome = SAFE_FAIL_STOP`, `matches_rejection_key = 1`, and `matches_valid_key = 0`. |
| **Sample size** | N = 200 |
| **Confidence interval** | 95% Wilson score CI: [98.12%, 100.00%] |
| **Scope qualifier** | Evaluated persistent faults escalated to implicit rejection; does not establish coverage across every possible persistent fault model. |
| **Slide usage** | Slides 07, 08, 11 |

---

### Claim 2.3 — Zero SDC in Production Cleanroom Trials (Phase 18, N=300 active)

| Field | Value |
|---|---|
| **Claim as stated** | "0 SDC observed across 300 active production fault trials" |
| **Numerical values** | 0 Silent Data Corruption events in 300 armed trials |
| **Source file** | `phase18_audit/raw_production_trials.csv` |
| **Verification status** | **DIRECTLY OBSERVED & INDEPENDENTLY VERIFIED** — 300 rows with `armed = 1`. All 300 resolve to either `GENUINE_RECOVERY` (100) or `SAFE_FAIL_STOP` (200). Zero trials emit corrupted keys without detection. |
| **Confidence interval** | 95% Wilson score CI: [0.00%, 1.26%] (rule of three upper bound: 3/300 = 1.00%) |
| **Crucial caveat** | Represents a statistical upper bound under the evaluated fault model; not a mathematical proof of zero probability across all possible execution environments. |
| **Slide usage** | Slides 01, 06, 08, 09, 11 |

---

### Claim 2.4 — Zero SDC in Canonical Campaign (N=750 active) with Mechanism Breakdown

| Field | Value |
|---|---|
| **Claim as stated** | "0 SDC across 750 active canonical campaign trials (Clopper-Pearson bound: 0.49%)" |
| **Numerical values** | N_total = 900; N_clean = 150; N_active = 750; SDC = 0 |
| **Outcome breakdown** | • `GENUINE_RECOVERY`: 250 (local invariant detected → rollback recovered)<br>• `SAFE_FAIL_STOP`: 350 (local invariant detected → retry exhausted → K_rej)<br>• `LOCAL_BLIND_FO_CONTAINED`: 147 (local invariant blind to twiddle fault → outer FO re-encryption caught polynomial error → K_rej emitted; NOT SDC)<br>• `INEFFECTIVE_FAULT_VALID`: 3 (injected fault did not propagate to output → valid key correctly returned; NOT SDC) |
| **Source file** | `tfib_trial_level_results.csv` |
| **Verification status** | **DIRECTLY OBSERVED & INDEPENDENTLY VERIFIED** — Recomputed column distributions for `oracle_classification` across all 900 rows. Exactly 750 active rows confirmed. |
| **Confidence bound** | One-sided 97.5% Clopper-Pearson upper bound: 0.49% (k=0, n=750) |
| **Important distinction** | 147 trials were invisible to the local invariant monitor (Theorem 1 twiddle blindness) and were contained exclusively by the outer FO mechanism. Slides explicitly disclose this mechanism split. |
| **Slide usage** | Slides 08, 09, 11 |

---

## Section 3: Experimental Validation Claims

### Claim 3.1 — Circular Verifier Blindness: 591/600 (98.5%)

| Field | Value |
|---|---|
| **Claim as stated** | "98.5% false-pass rate for circular verifiers reading live faulted registers" |
| **Numerical values** | 591 blind passes out of 600 H1-relevant trials across 6 target configurations |
| **Source file** | `phase16_targeted_evidence_closure/h1_activation_audit.csv` |
| **Verification status** | **DIRECTLY OBSERVED & INDEPENDENTLY VERIFIED** — CSV contains 1200 rows across 12 target names (100 trials each). Exactly 591 rows have `audit_classification_status = H1_BLIND_PASS_OBSERVED`.<br>Per-target breakdown across the 6 H1-relevant targets:<br>• F1_SAVED_OPERAND_BITFLIP: 98/100<br>• F2_SNAPSHOT_PRE_RETRY_DIFFUSION: 100/100<br>• F6_VERIFIER_RESULT_FORCE_PASS: 99/100<br>• F7_RETRY_ARITHMETIC_GLITCH: 94/100<br>• F9_DSPC_COLLISION_MULTI_BIT: 100/100<br>• F10_DSPC_STATE_BYPASS: 100/100<br>Sum: 98 + 100 + 99 + 94 + 100 + 100 = 591 / 600 = 98.5%. |
| **Confidence interval** | 95% Wilson score CI: [97.20%, 99.20%] |
| **Scope qualification** | Snapshot isolation addresses the common-mode failure observed in the evaluated verifier configurations. |
| **Slide usage** | Slides 03, 08 |

---

### Claim 3.2 — FIPS 203 Section 7.3 Conformance (Phase 11): N=200

| Field | Value |
|---|---|
| **Claim as stated** | "100% implicit rejection conformance with FIPS 203 Section 7.3" |
| **Numerical values** | 200 trials (100 valid ciphertexts + 100 invalid ciphertexts) |
| **Source files** | `phase11_conformance_audit/valid_ciphertext_trials.csv`, `phase11_conformance_audit/invalid_ciphertext_trials.csv` |
| **Verification status** | **REPORTED BY PRIOR PHASE** — Datasets SHA-256 registered in provenance manifest (`bfce13a8...`, `ed73e599...`). |
| **Slide usage** | Slide 08 |

---

### Claim 3.3 — NIST Known Answer Test Conformance: 18/18 Vectors Pass

| Field | Value |
|---|---|
| **Claim as stated** | "18/18 NIST KAT vectors pass across all ML-KEM and ML-DSA parameter sets" |
| **Numerical values** | 18 passed tests (0 failed) |
| **Parameter coverage** | • ML-KEM-512, ML-KEM-768, ML-KEM-1024 (Keygen, Encaps, Decaps = 9 tests)<br>• ML-DSA-44, ML-DSA-65, ML-DSA-87 (Sign, Verify, Tamper-Reject = 9 tests) |
| **Source binary** | `bin/test_fips_kats` |
| **Verification status** | **DIRECTLY OBSERVED** — Binary executed during audit. Console output: "ALL NIST FIPS 203 & 204 TEST VECTORS VERIFIED SUCCESSFULLY (PASS)". |
| **Important distinction** | Passing KAT vectors validates functional correctness and standard algorithm conformance; it does NOT constitute formal FIPS certification or CMVP validation. |
| **Slide usage** | Slides 06, 08, 11 |

---

### Claim 3.4 — Step 2C Countermeasure Independence: 9/9 Pass

| Field | Value |
|---|---|
| **Claim as stated** | "9/9 Step 2C countermeasure independence assertions pass" |
| **Numerical values** | 9 assertions evaluated, 9 passed, 0 failed |
| **Source binary** | `tfib_experiments/test_step2c_countermeasure_independence` |
| **Verification status** | **DIRECTLY OBSERVED** — Binary executed during audit. Confirmed: "RESULTS: 9 passed, 0 failed". |
| **Technical meaning** | Confirms that localized invariant monitoring operates orthogonally to outer Fujisaki-Okamoto rejection and redundant computation paths. |
| **Slide usage** | Slide 08 |

---

### Claim 3.5 — Phase 15Q Twiddle Factor Corruption Pilot Study

| Field | Value |
|---|---|
| **Claim as stated** | "Twiddle factor corruption pilot study evaluated on reference vector" |
| **Numerical values** | 16 total rows in `trial_ledger.csv`; 11 active mutations reported in manuscript |
| **Source file** | `results/phase15q/trial_ledger.csv` |
| **Verification status** | **REPORTED BY PRIOR PHASE** — CSV confirmed on disk (16 rows). 11 active mutations reported in manuscript; evaluated on a single reference vector. |
| **Mandatory statement** | Local invariants cannot independently detect corruption of a shared twiddle-factor value. Downstream FO validation returned implicit rejection for the evaluated reference vector in the Phase 15Q pilot (N=16); broader validation remains future work. |
| **Slide usage** | Slides 07, 09 |

---

## Section 4: Implementation & Terminology Claims

### Claim 4.1 — Zero Dynamic Heap Allocation in Monitor Paths

| Field | Value |
|---|---|
| **Claim as stated** | "Zero dynamic heap allocation in monitoring and rollback code paths" |
| **Source code** | `algorithms/source_ref/mlkem_fault_hooks.c`, `algorithms/source_ref/mlkem/src/kem.c` (lines 412–415) |
| **Verification status** | **INFERRED (SOURCE-LEVEL ONLY)** — Direct source code inspection confirms `malloc`, `calloc`, and `free` are absent from monitoring, snapshot, and rollback execution paths. |
| **Scope boundary** | Not verified by a runtime heap profiler (e.g. Valgrind massif) during execution. Does not constitute an absolute whole-program guarantee. |
| **Slide usage** | Slides 01, 06, 08, 11 |

---

### Claim 4.2 — Software-Managed State Snapshot Variables & Register Terminology

| Field | Value |
|---|---|
| **Claim as stated** | "Snapshots input operands in software-managed variables representing the butterfly's arithmetic state" |
| **Source code** | `algorithms/source_ref/mlkem_fault_hooks.c` (`u_saved`, `v_saved` variables) |
| **Verification status** | **DIRECTLY OBSERVED** — Source code defines C variables `u_saved` and `v_saved`. Unless compiled assembly evidence confirms physical register pinning, these are described strictly as software-managed variables. |
| **Fault injection model** | Described as software-injected bit-flips into register-modeled arithmetic operands via targeted enums — explicitly not physical beam testing. |
| **Slide usage** | Slides 06, 07, 09 |

---

### Claim 4.3 — 9,856 Total Butterfly Operations Monitored

| Field | Value |
|---|---|
| **Claim as stated** | "9,856 butterfly arithmetic operations monitored per decapsulation" |
| **Derivation** | • Forward NTT: 6 calls × (128 butterflies/stage × 7 stages) = 6 × 896 = 5,376 Forward CT operations<br>• Inverse NTT: 5 calls × (128 butterflies/stage × 7 stages) = 5 × 896 = 4,480 Inverse GS operations<br>• Total: 5,376 + 4,480 = 9,856 operations |
| **Source file** | `results/phase7i/processed/phase7i_e2e_results.json` |
| **Verification status** | **DIRECTLY OBSERVED & INDEPENDENTLY VERIFIED** — JSON fields `total_butterflies: 9856`, `forward_butterflies: 5376`, `inverse_butterflies: 4480` verified. |
| **Slide usage** | Slides 01, 06, 07, 08, 11 |

---

### Claim 4.4 — Localized Recomputation Ratio: ~0.0101%

| Field | Value |
|---|---|
| **Claim as stated** | "~0.0101% operation-count ratio for single-butterfly retry" |
| **Mathematical derivation** | 1 retried butterfly operation / 9,856 total operations = 1 / 9,856 = 0.00010146 = 0.010146% |
| **Verification status** | **INFERRED** — Mathematically exact from the verified 9,856 total operations. |
| **CRITICAL CAVEAT** | This is an operation-count ratio, NOT wall-clock latency overhead. Wall-clock decapsulation overhead is +16.9%. Slides clearly distinguish these metrics. |
| **Slide usage** | Slides 06, 07, 08, 11 |

---

## Section 5: Literature, Novelty & Audit Status Claims

### Claim 5.1 — Prior Art Comparative Calibration

| Field | Value |
|---|---|
| **Claim as stated** | "Prior art surveyed and novelty calibrated against 9 comparative schemes" |
| **Source file** | `phase17b_corrected/revision_summary.md` (Section 2.1), `closest_prior_art_comparison.csv` |
| **Key reference** | Paul et al. (ACM TECS 2026) introduced CT invariant checking for forward NTT on FPGA accelerators; our work investigates pure-software dual-transform (CT + decoupled GS) monitoring with register-modeled rollback on COTS CPUs. |
| **Verification status** | **REPORTED BY PRIOR PHASE** — Survey documentation and comparative matrices confirmed on disk. |
| **Slide usage** | Slide 06 |

---

### Claim 5.2 — Manuscript Audit Verdict

| Field | Value |
|---|---|
| **Claim as stated** | "Manuscript reviewed through an internal research audit (Phase 2S Final Audit — READY WITH EXPLICIT LIMITATIONS)" |
| **Source files** | `AYUSH.md` (Header, Section 16), `phase17b_corrected/revision_summary.md` (Section 4) |
| **Verification status** | **DIRECTLY OBSERVED** — Header of `AYUSH.md` and Phase 2S review summary directly verified. |
| **Slide usage** | Slide 11 |

---

## Section 6: Claims Deliberately Omitted or Qualified

| Potential Claim | Why It Was Omitted or Qualified | Slide Action Taken |
|---|---|---|
| "+25.3% latency under -O2" | Theoretical projection, not empirically supported by persistent data. | Excluded entirely. Only `-O3` (+16.9%) is cited. |
| "Physical radiation hardness" | No cyclotron, proton, or neutron beam testing was performed. | Explicitly disclosed as software-injected bit-flips into register-modeled operands. |
| "Hardware ECC unavailable on COTS" | Hardware ECC exists on select automotive/aerospace microcontrollers. | Qualified to: "Hardware ECC availability varies across COTS embedded platforms." |
| "Catastrophic cryptographic breakdown" | Sensationalist terminology. | Replaced with: "Potentially incorrect shared-secret output." |
| "Snapshot isolation mathematically necessary" | Overstated scope of informal proof. | Replaced with: "Snapshot isolation addresses the common-mode failure observed in evaluated verifiers." |
| "Four independent empirical datasets" | Implies four unrelated external data corpuses. | Replaced with: "Four experimental evaluations." |
| "Certified constant-time execution" | Conditional branches in fault recovery path; no TVLA or dudect testing performed. | Excluded. Listed as an explicit limitation and future work. |
| "Universal fault coverage / SDC = 0" | Mathematical proof across all inputs is impossible without exhaustive formal verification. | Rephrased as statistical upper bounds (1.26% and 0.49%) and explicitly noted that results do not establish coverage against every possible fault class. |
| "Space qualified / flight ready" | Desktop ARM64 benchmarking only; no radiation or embedded core testing. | Excluded. Embedded microcontroller profiling listed as future work. |
| "100% twiddle corruption protection" | Theorem 1 algebraically proves that local invariants are blind to twiddle corruption. | Explicit mandatory limitation stated on Slides 07, 09, and 10. |
| "SIFA-resistant implementation" | Statistical Ineffective Fault Attacks exploit retry behavior to recover secret keys. | Explicitly declared outside scope; fail-stop mode required under adversarial fault models. |
| "Phase 7I DMR +140.95% overhead" | Measurement artifact where monitors were enabled during DMR execution. | Excluded. Only Phase 7H isolated DMR (+99.33%) is cited. |
| "Zero secret information leakage" | No side-channel leakage assessment performed. FIPS implicit rejection prevents direct key recovery from ciphertext, but timing channels remain unmeasured. | Claim removed from Slide 07. Timing leakage declared as limitation on Slide 09. |
| "Full FIPS 203 certification / CMVP" | Passing KAT test vectors validates functional correctness, not formal certification. | Qualified as "18/18 NIST KAT vectors pass (functional correctness validation; not formal certification)." |
| "Conceptual full-decapsulation DMR latency" | Combining different benchmark configurations into one chart creates false comparisons. | Separated into Comparison A (end-to-end) and Comparison B (isolated NTT) on Slide 08. |

---

*End of AI PPT Fact-Check Register*
