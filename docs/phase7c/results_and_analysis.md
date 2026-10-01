# Phase 7C: Experimental Results & Detailed Analysis

## 1. Systematic Fault Detection Rates Across All 8 Threat Classes
The table below presents detection rates for 1,200 trials (150 trials per threat class) independently reproduced with matched seeds and logged in [`results/phase7c/raw/phase7c_raw_trials.json`](file:///Users/dhairyajain/Desktop/pqc%20research/results/phase7c/raw/phase7c_raw_trials.json):

| Threat Fault Class | Config 1 (Baseline) | Config 2 (Unw. NTT) | Config 3 (Compl. NTT) | Config 4 (DMR) | Config 5 (Phase 7 Oracle) | Config 6 (Phase 7C Native) | 95% Wilson CI (Config 6) |
|---|---|---|---|---|---|---|---|
| **Class 1 (Intermediate T)** | 0.0% | 0.0% | 100.0% | 100.0% | 100.0% | **100.0%** | [97.5%, 100.0%] |
| **Class 2 (Twiddle Zeta)** | 0.0% | 0.0% | 100.0% | 85.3% | 100.0% | **100.0%** | [97.5%, 100.0%] |
| **Class 3 (Output Add Reg)** | 0.0% | 100.0% | 100.0% | 98.7% | 100.0% | **100.0%** | [97.5%, 100.0%] |
| **Class 4 (Correlated Mult)** | 0.0% | 0.0% | 0.0% | 100.0% | 100.0% | **100.0%** | [97.5%, 100.0%] |
| **Class 5 (Pre-Invoc Input)** | 0.0% | 0.0% | 0.0% | **0.0%** | 100.0% | **100.0%** | [97.5%, 100.0%] |
| **Class 6 (Checker Perturb)** | 0.0% | 0.0% | 0.0% | **0.0%** | 100.0% | **100.0%** | [97.5%, 100.0%] |
| **Class 7 (Control FO Gate)** | 0.0% | 0.0% | 0.0% | **0.0%** | 100.0% | **100.0%** | [97.5%, 100.0%] |
| **Class 8 (Persistent Stuck)**| 0.0% | 0.0% | 0.0% | 100.0% | 100.0% | **100.0%** | [97.5%, 100.0%] |

---

## 2. Functional Sanity Checks Analysis
1. **Valid Ciphertext, No Fault:**
   - Evaluated Token: `0x5A5A5A5A` (`RESILIENCE_OK_TOKEN`).
   - Shared secret: Byte-for-byte exact match with ground-truth encaps key $K'$.
   - Finding: Confirms zero false-positive rate on valid incoming traffic.
2. **Invalid Ciphertext, No Fault:**
   - Evaluated Token: `0xC3C3C3C3` (`RESILIENCE_REJECT_TOKEN`).
   - Shared secret: Byte-for-byte exact match with ground-truth FIPS 203 implicit rejection key $K_{\text{rej}} = J(z \,||\, ct)$.
   - Finding: Confirms autonomous preservation of FIPS 203 implicit rejection semantics without crashes, errors, or reliance on external oracles.
3. **Control-Flow FO Predicate Override ($0 \to 1$ on Valid CT):**
   - Evaluated Token: `0xA5A5A5A5` (`RESILIENCE_FAULT_TOKEN`).
   - Caught by: Dual-rail constant-time reverse comparison (`fail != fail_chk`).
4. **Control-Flow FO Predicate Override ($1 \to 0$ on Invalid CT):**
   - Evaluated Token: `0xA5A5A5A5` (`RESILIENCE_FAULT_TOKEN`).
   - Security Behavior: `fail` immediately forced to `0xFF`, guaranteeing that candidate plaintext $m'$ and key $K_{\text{cand}}$ are **NEVER leaked**.

---

## 3. Performance & Overhead Benchmarks (2,000 Iterations)
Benchmarks executed under consistent CPU thermal and scheduling conditions:

| Architecture Configuration | Measured Mean Latency | Overhead vs Baseline |
|---|---|---|
| **Config 1: Unprotected Baseline ML-KEM-768** | 42.13 µs | reference (0.0%) |
| **Config 4: Full Duplicate Decapsulation (DMR)** | 85.50 µs | **+102.9%** |
| **Config 5: Phase 7 Layered Architecture (with Oracle)** | 51.58 µs | **+22.4%** |
| **Config 6: Phase 7C Oracle-Free Native Layered** | 51.34 µs | **+21.9%** |

### Key Performance Takeaways
1. **Zero Degradation from Oracle Removal:** The oracle-free native monitor is slightly faster than the Phase 7 oracle harness (51.34 µs vs 51.58 µs) because status extraction occurs directly from the internal comparison register rather than performing an external 32-byte memory comparison.
2. **Superior Cost-Resilience Tradeoff:** Phase 7C provides 100% coverage across all 8 classes at **+21.9% overhead**, compared to DMR at **+102.9% overhead** which completely fails (0.0% coverage) on pre-invocation corruption, checker perturbations, and control-flow overrides.

---

## 4. Machine Code & Assembly Inspection
Inspection of the disassembled AArch64 binary (`bin/phase7c_oracle_free`) confirmed:
1. **Constant-Time Status Computation:** The status derivation uses arithmetic shifts and masks (`lsr`, `sub`, `and`) without conditional branching.
2. **Conditional Move Integrity:** Output key selection employs branch-free Neon/ALU bitwise logic (`bic`, `and`, `orr`, `strb`).
3. **Stack Zeroization:** Intermediate stack buffers (`tmp`, `buf`, `kr`) are zeroized prior to function return.
4. **Limitations of Inspection:** Assembly verification confirms the absence of compiler-induced branches, but cannot guarantee immunity to physical microarchitectural side channels or laser fault attacks on physical flip-flops.
