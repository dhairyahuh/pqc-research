# Experimental Evidence Audit & Discrepancy Register

**Audit Date:** 2026-10-17  
**Auditor:** Automated Research Auditor (Mandatory Anti-Hallucination Protocol)  
**Verification Level:** `[DIRECTLY OBSERVED & INDEPENDENTLY RECOMPUTED]`  
**Target Repository:** `/Users/dhairyajain/Desktop/pqc research`

---

## 1. Discrepancy Register

| ID | Issue Description | Location 1 (Claimed) | Location 2 (Evidence) | Root Cause | Resolution / Required Action |
|:---|:---|:---|:---|:---|:---|
| **DISC-01** | **Host CPU Platform Mismatch** | [manuscript.md:L21,50,222,302](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) claims: *"Apple M3 Pro (12 CPU cores, 36 GB RAM, Darwin 24.1.0)"* | [EVIDENCE_LEDGER.md:L18](file:///Users/dhairyajain/Desktop/pqc%20research/research/EVIDENCE_LEDGER.md), host `sysctl hw.model` / `uname -a`: **Apple M1 (MacBookAir10,1, 8 cores, Darwin 27.0.0)** | Manuscript drafter hallucinated/copy-pasted M3 Pro specs. All benchmark logs (`phase7i_e2e_results.json`, `phase18_audit/performance_reproduction.md`) ran on the local M1 host. | **CORRECT MANUSCRIPT.** Update manuscript text, tables, and methodology to explicitly state Apple M1 (8 cores, Darwin 27.0.0). |
| **DISC-02** | **Circular Verifier Rate (98.5% vs. 94%–100%)** | [authoritative_results.csv:H1_AGG](file:///Users/dhairyajain/Desktop/pqc%20research/authoritative_results.csv) reports **98.5%**; [claim_evidence_matrix.csv:CLM-06](file:///Users/dhairyajain/Desktop/pqc%20research/claim_evidence_matrix.csv) reports **94.0% to 100.0%** | `phase16_targeted_evidence_closure/h1_activation_*.csv`: Individual models $T_1=98\%, T_2=94\%, T_3=100\%, T_4=100\%, T_5=99\%, T_6=100\%$ | Different levels of aggregation from the exact same dataset. Aggregate pooled rate is $591/600 = 98.5\%$; range across individual sub-models is $94.0\%–100.0\%$. | **RECONCILED.** State both clearly in manuscript: "Individual test models exhibited 94.0% to 100.0% blindness, with a pooled aggregate of 98.5% ($591/600$ trials)." |
| **DISC-03** | **Efficiency Advantage Scope ("5.9x")** | [manuscript.md:L23](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md#L23) claims *"5.9x efficiency advantage over software DMR"* | [phase18_audit/performance_reproduction.md:L20](file:///Users/dhairyajain/Desktop/pqc%20research/phase18_audit/performance_reproduction.md#L20) | Latency overhead ratio: $+149.0\% / +25.3\% \approx 5.89\times$ under `-O2` ($+135.3\% / +16.9\% \approx 8.0\times$ under `-O3`). Valid *only* against single-thread software sequential re-execution. | **QUALIFY IN MANUSCRIPT.** Must explicitly restrict "efficiency advantage" to single-threaded software sequential DMR; explicitly disclaim superiority over hardware dual-core lockstep. |
| **DISC-04** | **Space Radiation Environment Claims** | [manuscript.md:L12,26](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md#L12) references space radiation and SEU resilience | [literature/p1_papers/Basic_mechanisms_and_modeling_of_single-event_upset_in_digital_microelectronics.pdf](file:///Users/dhairyajain/Desktop/pqc%20research/literature/p1_papers/Basic_mechanisms_and_modeling_of_single-event_upset_in_digital_microelectronics.pdf) (Dodd 2003) | Software fault injection does not model physical radiation, charge deposition, or MCUs. | **BOUND IN MANUSCRIPT.** Reframe strictly as an *architectural register single-event upset model*. Explicitly disclaim physical radiation hardness. |

---

## 2. Independent Audit of Core Empirical Campaigns

### A. Step 2C-A Canonical Campaign (900 Trials)
- **Source Artifact:** `tfib_raw_results.csv`, `authoritative_results.csv`, `research/EVIDENCE_LEDGER.md`.
- **Trial Population Breakdown `[DIRECTLY OBSERVED & INDEPENDENTLY VERIFIED]`:**
  - Total Trials: **900**
  - Baseline Control (Unfaulted): **150** (150 clean completions, 0 failures)
  - Reference Arm (Fault Injected, Check-Only / No Rollback): **400**
  - Recovery Arm (Fault Injected, Localized Rollback Active): **350**
- **Outcome Classification across 750 Activated Faults:**
  - `RECOVERED`: **250** (100% of transient computational butterfly faults in recovery arm successfully restored in-place)
  - `SAFE_FAIL_DETECTED`: **350** (Clean error exit triggered when faults exceed retry threshold $M=2$)
  - `SAFE_FAIL_FO_CONTAINED`: **147** (Persistent twiddle faults passed local check but caught by outer FO check $\to$ implicit rejection)
  - `INEFFECTIVE`: **3** (Fault injected into dead register or masked by arithmetic reduction)
  - `SILENT_DATA_CORRUPTION (SDC)`: **0** ($0/750$ active faults produced corrupt uncontained shared secret)
- **Statistical Upper Bound:**
  - Targeted production trial population: $0/300$ active butterfly faults $\to$ Clopper-Pearson 95% CI: $[0.00\%, 1.26\%]$.
  - Pooled campaign population: $0/750$ active faults $\to$ One-sided 97.5% upper bound $\le 0.49\%$ (rule of 3: $3/750 = 0.004$).

---

### B. Mathematical Butterfly Operation Count
- **Verification Target:** Reported claim of **9,856** monitored butterflies per decapsulation.
- **Independent Derivation `[INDEPENDENTLY RECOMPUTED]`:**
  - For ML-KEM-768: polynomial degree $n = 256$.
  - Number of stages per NTT: $\log_2(256) - 1 = 7$ stages.
  - Number of butterfly operations per stage: $n / 2 = 128$.
  - Butterflies per polynomial transform: $7 \times 128 = 896$ butterflies.
  - **Forward NTTs in Decapsulation:**
    - Transform secret vector $\hat{s}$ (3 polynomials): $3 \times 896 = 2,688$ CT butterflies.
    - Transform received ciphertext vector $\hat{u}$ (3 polynomials): $3 \times 896 = 2,688$ CT butterflies.
    - Total Forward Cooley-Tukey: $6 \times 896 = \mathbf{5,376}$ butterflies.
  - **Inverse NTTs in Decapsulation:**
    - Inverse transform for message decoding $w = \text{INTT}(\hat{s}^T \circ \hat{u})$ (1 polynomial): $1 \times 896 = 896$ GS butterflies.
    - Re-encryption FO matrix multiplication $\hat{A}^T \circ \hat{r}$ (4 polynomials): $4 \times 896 = 3,584$ GS butterflies.
    - Total Inverse Gentleman-Sande: $5 \times 896 = \mathbf{4,480}$ butterflies.
  - **Grand Total Monitored Butterflies:** $5,376 + 4,480 = \mathbf{9,856}$ butterflies.
- **Conclusion:** Mathematical claim is exact and verified in [poly.c:L174, L218](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem/src/poly.c#L174).

---

### C. Benchmark Latency and Memory Profiling
- **Verification Target:** Table 4 in [paper/tables/table4_performance_comparison.csv](file:///Users/dhairyajain/Desktop/pqc%20research/paper/tables/table4_performance_comparison.csv) and [manuscript.md:L302](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md#L302).
- **Benchmarking Parameters `[DIRECTLY OBSERVED]`:**
  - Measurement size: $N = 2,000$ warm-stabilized decapsulation iterations.
  - Timing primitive: `clock_gettime(CLOCK_MONOTONIC)`.
  - Toolchain: Apple Clang (`-std=c11`).
- **Results Summary:**
  - **Optimization `-O3`:**
    - Baseline Unprotected: $110.77\ \mu\text{s}$ ($\sigma = 4.82$)
    - Invariant Monitored + Rollback: $129.51\ \mu\text{s}$ ($\sigma = 5.14$) $\implies \mathbf{+16.9\%}$ latency overhead ($1.17\times T_0$).
    - Software Sequential DMR: $260.68\ \mu\text{s}$ ($\sigma = 8.92$) $\implies \mathbf{+135.3\%}$ latency overhead ($2.35\times T_0$).
  - **Optimization `-O2`:**
    - Baseline Unprotected: $124.30\ \mu\text{s}$ ($\sigma = 5.60$)
    - Invariant Monitored + Rollback: $155.75\ \mu\text{s}$ ($\sigma = 6.10$) $\implies \mathbf{+25.3\%}$ latency overhead ($1.25\times T_0$).
    - Software Sequential DMR: $309.51\ \mu\text{s}$ ($\sigma = 10.40$) $\implies \mathbf{+149.0\%}$ latency overhead ($2.49\times T_0$).
  - **Memory Footprint:**
    - Heap allocations: **0 bytes** (`malloc` count = 0).
    - Stack footprint: $1,408$ bytes monitored vs. $1,216$ bytes baseline ($+192$ bytes local frame).
    - Static state: **48 bytes** BSS.

---

### D. Audit of Deferred Paper Directions

#### 1. Paper Track 2: Cross-Layer Fault Interactions (`spacecraft_protocol_sim.py`)
- **Inspection `[DIRECTLY OBSERVED]`:** [experiments/system_model/spacecraft_protocol_sim.py](file:///Users/dhairyajain/Desktop/pqc%20research/experiments/system_model/spacecraft_protocol_sim.py), [results/spacecraft_protocol_desync_results.json](file:///Users/dhairyajain/Desktop/pqc%20research/results/spacecraft_protocol_desync_results.json).
- **Critical Finding:** The reported "cross-layer interaction" between CCSDS framing faults and cryptographic decapsulation is largely a trivial artifact of serialization ordering: when a channel fault is injected, the packet framing check rejects the corrupted frame *before* it is ever passed to the cryptographic decapsulation function.
- **Assessment:** This does not represent an independent scientific discovery or deep coupling; it is the natural consequence of protocol layer filtering.
- **Decision:** **DEFER / ARCHIVE Track 2 as an independent paper.**

#### 2. Paper Track 3: Persistent State & Twiddle Factor Faults
- **Inspection `[DIRECTLY OBSERVED]`:** Twiddle table fault pilot (147 trials).
- **Critical Finding:** When twiddle factors $\omega$ in memory are corrupted, the internal butterfly arithmetic remains algebraically consistent with the faulty constant ($E_1 = 2U$ and $E_2 = 2V'$ still hold), causing a $0.0\%$ local detection rate (100% false-pass). However, the resulting decrypted message $m^*$ fails the outer Fujisaki-Okamoto re-encryption test ($c^* \neq c$), causing decapsulation to deterministically return the implicit rejection key.
- **Assessment:** High-value failure-mode characterization. However, a standalone paper on this alone is too narrow and lacks multi-fault statistical backing.
- **Decision:** **FOLD INTO TRACK 1 (Section 4 / Discussion).** This transforms a potential weakness into a major strength of Paper 1: characterizing the defensive boundary between fine-grained arithmetic monitoring and protocol failsafes.
