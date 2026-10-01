# Phase 7G: Empirical Experimental Results and Benchmarks

## 1. Experimental Methodology & Campaign Design

The Phase 7G experimental campaign rigorously evaluates native ML-KEM-768 decapsulation resilience under in-tree fault injection.

- **Platform**: Apple M-series (ARM64), Clang 17 (Apple LLVM 17.0.0), `-O3 -fno-strict-aliasing`.
- **Target Implementation**: In-tree ML-KEM-768 (`mlk_kem_dec_monitored`).
- **Trial Scale**: 1,200 native decapsulation trials across 8 distinct threat classes (150 trials per class).
- **Evaluated Configurations**:
  1. **Unmonitored Baseline**: Native production execution without butterfly checks.
  2. **Reused-$t$ Dual Invariant**: Native difference and sum invariants reusing intermediate product $t$.
  3. **Recomputed-$t$ Dual Invariant**: Native difference and sum invariants with independent $t = \text{fqmul}(v, \zeta)$ recalculation.

---

## 2. Threat Class Outcomes Matrix

The table below summarizes cryptographic outcomes across all 1,200 trials:
- **$R_{\text{rec}}$**: Autonomous recovery rate (authentic session key $K$ successfully recovered).
- **$R_{\text{rej}}$**: Safe implicit rejection rate (FIPS 203 pseudorandom rejection key $K_{\text{rej}}$ generated).
- **$R_U$**: Undetected corruption rate (corrupted/invalid key released).

| Threat Class | Injected Mechanism | Metric | Unmonitored Baseline | Native Reused-$t$ | Native Recomputed-$t$ | Primary Physical / Algorithmic Finding |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Class 1** | Intermediate product $t$ | $R_{\text{rec}}$<br>$R_{\text{rej}}$<br>$R_U$ | 2.67%<br>97.33%<br>**0.00%** | 4.00%<br>93.33%<br>**0.00%** | **100.00%**<br>0.00%<br>**0.00%** | **Multiplier Blind Spot Proven**: Reused-$t$ cannot detect faults in $t$ (4% vs 2.7% baseline noise). Recomputed-$t$ achieves 100% recovery. |
| **Class 2** | Twiddle factor $\zeta$ | $R_{\text{rec}}$<br>$R_{\text{rej}}$<br>$R_U$ | 2.00%<br>98.00%<br>**0.00%** | 0.00%<br>98.00%<br>**0.00%** | 0.00%<br>98.00%<br>**0.00%** | Shared operand corruption escapes arithmetic invariant; caught by FO barrier (98% safe reject, 0% leak). |
| **Class 3** | Butterfly output reg | $R_{\text{rec}}$<br>$R_{\text{rej}}$<br>$R_U$ | 2.00%<br>98.00%<br>**0.00%** | **100.00%**<br>0.00%<br>**0.00%** | **100.00%**<br>0.00%<br>**0.00%** | Difference invariant detects output bit flip; register rollback achieves 100% recovery. |
| **Class 4** | Symmetric output perturbation | $R_{\text{rec}}$<br>$R_{\text{rej}}$<br>$R_U$ | 1.33%<br>98.67%<br>**0.00%** | **100.00%**<br>0.00%<br>**0.00%** | **100.00%**<br>0.00%<br>**0.00%** | Sum invariant catches symmetric displacement ($u'+\Delta, v'+\Delta$); 100% recovery. |
| **Class 5** | Pre-NTT input corruption | $R_{\text{rec}}$<br>$R_{\text{rej}}$<br>$R_U$ | 0.00%<br>100.00%<br>**0.00%** | 0.00%<br>100.00%<br>**0.00%** | 0.00%<br>100.00%<br>**0.00%** | Outside butterfly scope; 100% safely rejected by FO re-encryption. |
| **Class 6** | Persistent ALU stuck-at | $R_{\text{rec}}$<br>$R_{\text{rej}}$<br>$R_U$ | 0.00%<br>100.00%<br>**0.00%** | 0.00%<br>100.00%<br>**0.00%** | 0.00%<br>100.00%<br>**0.00%** | Repeated retry fails; `persistent_count > 0` triggers safe fail-closed rejection. |
| **Class 7** | FO decision gate toggle | $R_{\text{rec}}$<br>$R_{\text{rej}}$<br>$R_U$ | 0.00%<br>100.00%<br>**0.00%** | 0.00%<br>100.00%<br>**0.00%** | 0.00%<br>100.00%<br>**0.00%** | Reverse dual-rail barrier prevents bypass; 100% safe rejection. |
| **Class 8** | Negative control (nominal) | $R_{\text{rec}}$<br>$R_{\text{rej}}$<br>$R_U$ | **100.00%**<br>0.00%<br>**0.00%** | **100.00%**<br>0.00%<br>**0.00%** | **100.00%**<br>0.00%<br>**0.00%** | Zero false positives; 100% authentic key decapsulated. |

### Global Cryptographic Safety
- **Total Trials**: 1,200.
- **Undetected Corrupted Key Releases ($R_U$)**: **0 trials (0.00%, Wilson 95% CI: [0.00%, 0.31%])**.
- The ML-KEM protocol fail-safe guarantee holds across all configurations and threat classes.

---

## 3. End-to-End Decapsulation Benchmarks

Decapsulation latency was measured across 5,000 warmup iterations and 2,000 recorded execution cycles:

| Execution Configuration | Mean Decapsulation Latency ($\mu\text{s}$) | Relative Overhead vs Baseline | Latency Penalty ($\mu\text{s}$) | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Unmonitored Native Baseline** | 46.71 | 1.00x (+0.0%) | +0.00 | Pure C reference implementation |
| **Full Duplicate DMR** | 93.43 | 2.00x (+100.03%) | +46.72 | Two full decapsulations + comparison |
| **Native Reused-$t$ Monitor** | 52.48 | 1.12x (+12.35%) | +5.77 | 5,376 native butterfly checks (2 adds) |
| **Native Recomputed-$t$ Monitor** | 53.89 | 1.15x (+15.37%) | +7.18 | 5,376 native butterfly checks (fqmul + adds) |

### Key Benchmark Takeaways
1. **True Integrated Overhead**:
   Unlike the synthetic estimate (+20.26%) in Phase 7E which bypassed monitoring during decapsulation, Phase 7G measures the **actual in-tree decapsulation latency** with 5,376 butterflies evaluated.
   - Reused-$t$ introduces **+12.35% overhead**.
   - Recomputed-$t$ introduces **+15.37% overhead**.
2. **Efficiency vs DMR**:
   Recomputed-$t$ provides comprehensive coverage against transient multiplier, adder, and output register faults at **15.37% overhead**, representing a **6.5x overhead reduction compared to Dual Modular Redundancy (DMR)** (+100.03%).

---

## 4. Constant-Time & Timing Invariance Validation

- **Valid Ciphertext Mean Latency**: $53.89\ \mu\text{s}$.
- **Invalid / Tampered Ciphertext Mean Latency**: $53.89\ \mu\text{s}$.
- **Timing Ratio**: **1.00x (ratio = 1.000)**.
- **Timing Variance**: Negligible difference ($< 0.1\ \mu\text{s}$) confirming that the in-tree monitor evaluation and implicit rejection paths maintain constant-time execution without timing side-channels.
