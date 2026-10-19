# Statistical Methods, Confidence Intervals, and Telemetry Results

**Auditor:** Skeptical Independent Cryptographic Software Verification Auditor  
**Date:** October 2026  
**Subject:** Statistical Formulation, Wilson Score Confidence Intervals, and Sample Dependence Analysis  

---

## 1. Executive Summary

This document formalizes the statistical methodology employed in Phase 15. Every reported point estimate and confidence interval is derived directly from raw trial rows using identical numerators and denominators. 

We explicitly articulate the statistical assumptions, limitations, and dependence caveats governing the sample space, including the matched-pair PRNG seed structure across production targets and the mathematical limits of zero-event empirical observations.

---

## 2. Statistical Formulation

### 2.1 Binomial Proportion Point Estimate
For any target with sample size $n$ and observed outcome count $k$:
$$\hat{p} = \frac{k}{n}$$

### 2.2 Confidence Interval: Wilson Score Interval
Standard Wald asymptotic intervals ($\hat{p} \pm z \sqrt{\hat{p}(1-\hat{p})/n}$) fail catastrophically when $k = 0$ or $k = n$, producing zero-width intervals ($[0\%, 0\%]$ or $[100\%, 100\%]$) that violate basic probability theory.

To provide mathematically sound coverage for extreme proportions, all confidence bounds are computed using the **Wilson Score Interval** at the 95% confidence level ($\alpha = 0.05$, $z = 1.959964$):
$$p_{\text{lower}}, p_{\text{upper}} = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$

### 2.3 Zero-Event Upper Bounds: Wilson Score vs. Rule of Three
For zero-event outcomes ($k = 0$), the upper bound represents the maximum true failure rate consistent with the empirical evidence:
- **For $n = 100, k = 0$:**
  - Wilson 95% Upper Bound: **$3.70\%$** ($[0.0\%, 3.7\%]$).
  - Classical Rule of Three ($3/n$): **$3.00\%$**.
  - Conservative Audit Standard: We adopt the Wilson upper bound ($3.7\%$), which is slightly more conservative.
- **For $n = 400, k = 0$:**
  - Wilson 95% Upper Bound: **$0.95\%$** ($[0.0\%, 0.95\%]$).
  - Classical Rule of Three ($3/n$): **$0.75\%$**.

---

## 3. Comprehensive Recalculated Results Matrix

Every figure below is derived dynamically from raw CSV rows (no hardcoded inputs):

### 3.1 Harness Model Targets (Phase 7 Raw CSV: `derived_corrected_trial_results.csv`)
*Evaluates internal recovery verifier behavior under simulated snapshot memory corruption.*

| Target ID | Target Description | Raw Trials ($n$) | Fault Triggered ($T=1$) | Verifier Accepted ($V=1$) | Retry Differed ($\mathbf{r}_{\text{rec}} \ne \mathbf{r}_{\text{ref}}$) | $H_1$ False Recovery ($k$) | $H_1$ Point Estimate | $H_1$ 95% Wilson CI | Safe Rejection ($V=0$) | $H_2$ SDC Count | $H_2$ 95% Wilson CI |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **F1** | Saved Operand Bitflip | 100 | 100 | 98 | 100 | **98** | **98.0%** | [93.0%, 99.4%] | 2 | **0** | [0.0%, 3.7%] |
| **F2** | Snapshot Pre-Retry Diffusion | 100 | 100 | 100 | 100 | **100** | **100.0%** | [96.3%, 100.0%] | 0 | **0** | [0.0%, 3.7%] |
| **F3** | Persistent Count Zeroing | 100 | 100 | 0 | 100 | **0** | **0.0%** | [0.0%, 3.7%] | 100 | **0** | [0.0%, 3.7%] |
| **F6** | Verifier Flag Forced Pass | 100 | 100 | 99 | 100 | **99** | **99.0%** | [94.6%, 99.8%] | 1 | **0** | [0.0%, 3.7%] |
| **F7** | Retry Arithmetic Glitch | 100 | 100 | 94 | 100 | **94** | **94.0%** | [87.5%, 97.2%] | 6 | **0** | [0.0%, 3.7%] |
| **F8** | Verifier Operand Corrupt | 100 | 100 | 0 | 0 | **0** | **0.0%** | [0.0%, 3.7%] | 100 | **0** | [0.0%, 3.7%] |
| **F9** | DSPC Multi-Bit Collision | 100 | 100 | 100 | 100 | **100** | **100.0%** | [96.3%, 100.0%] | 0 | **0** | [0.0%, 3.7%] |
| **F10**| DSPC State Bypass | 100 | 100 | 100 | 100 | **100** | **100.0%** | [96.3%, 100.0%] | 0 | **0** | [0.0%, 3.7%] |
| **F11**| DSPC Single-Bit Clean | 100 | 100 | 0 | 100 | **0** | **0.0%** | [0.0%, 3.7%] | 100 | **0** | [0.0%, 3.7%] |

---

### 3.2 Production Binary Targets (Phase 13 Raw CSV: `production_trial_recalculation.csv`)
*Evaluates compiled C production objects (`mlkem768_inst.o` + `mlkem_fault_hooks.o`).*

| Target ID | Experimental Condition | Raw Trials ($n$) | Fault Triggered | Observed Behavior | Intermediate $H_1$ Measurability | $H_2$ Accepted Invalid Key ($k$) | $H_2$ Point Estimate | $H_2$ 95% Wilson CI |
| :---: | :--- | :---: | :---: | :--- | :---: | :---: | :---: | :---: |
| **F12** | Clean Baseline Control | 100 | 0 | 100/100 Clean Success | N/A (Baseline) | **0** | **0.0%** | [0.0%, 3.7%] |
| **F4** | Transient Butterfly Bitflip | 100 | 100 | 100/100 Genuine Recovery | Inferred 0 (End-to-End Key Valid) | **0** | **0.0%** | [0.0%, 3.7%] |
| **F5A** | Recurring Bit-Inversion | 100 | 100 | 100/100 Safe Fail-Stop | 0 (Verifier Rejected, $V=0$) | **0** | **0.0%** | [0.0%, 3.7%] |
| **F5B** | Software Force-Value Zero | 100 | 100 | 100/100 Safe Fail-Stop | 0 (Verifier Rejected, $V=0$) | **0** | **0.0%** | [0.0%, 3.7%] |
| **Total**| **Production Tier Execution** | **400** | **300** | **Clean, Recovered, or Aborted** | **Separated by Condition** | **0** | **0.0%** | **[0.0%, 0.95%]** |

---

## 4. Methodological Assumptions and Limitations

1. **Finite Sample Size Boundary:**
   Zero observed SDC events across 400 production trials does **not** prove mathematical impossibility of Silent Data Corruption. It establishes an empirical upper bound of $0.95\%$ at 95% confidence.
2. **Matched-Pair PRNG Seed Structure:**
   Production trials 0–99 across F12, F4, F5A, and F5B evaluated identical cryptographic instances ($pk, sk, ct$). Therefore, the 400 trials represent 100 paired blocks. Treating the 400 trials as independent cryptographic keys is an overstatement of key diversity; however, the treatment conditions are independent.
3. **Execution Tier Incomparability:**
   Harness models (Phase 7) simulate memory corruption inside standalone stack buffers, whereas production binaries (Phases 9–13) execute compiled native code. Combining their numerators and denominators into a "repository-wide pooled rate" is statistically and scientifically invalid.
4. **Software Fault Model Boundary:**
   All trials evaluated software debug hooks modifying local variables in C memory. No analog silicon latch-up, optical laser fault injection, electromagnetic pulse, or clock glitching was executed. Claims of physical hardware resilience are completely unsupported.
