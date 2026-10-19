# Timing Claim Review: Methodology, Experimental Rigor, and Leakage Assessment

**Auditor:** Skeptical Cryptographic Implementation Auditor  
**Investigation Focus:** Reassessment of the latency measurements reported in Phase 3 ($106.2\,\mu\text{s}$ clean vs $153.1\,\mu\text{s}$ fail-stop vs $168.4\,\mu\text{s}$ recovery)  
**Measurement Artifacts:** `phase3_harness_audit/harness/genuine_countermeasure_test.c:62-66, 160, 191` and `phase3_harness_audit/countermeasure_results.csv`  

---

## 1. Audit of the Timing Collection Methodology

In `genuine_countermeasure_test.c`, execution latency was recorded using POSIX monotonic clock timestamps:
```c
static inline double get_time_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e6 + (double)ts.tv_nsec * 1e-3;
}
```
Timestamps were sampled immediately prior to invoking `mlkem768_dec_monitored()` ($t_0$) and immediately after completion ($t_1$), logging $\Delta t = t_1 - t_0$ in microseconds.

### Experimental Controls Evaluation

| Experimental Control | Implemented in Harness? | Audit Evaluation & Impact |
| :--- | :---: | :--- |
| **Actual Implementation Path** | **YES** | Measurements were taken around genuine calls to `mlkem768_dec_monitored()` compiled from production C source. |
| **Equivalent Cryptographic Inputs** | **YES** | All trials used identical keys ($pk, sk$) and identical valid ciphertext ($c$), varying only the injected fault locus. |
| **CPU Core Affinity / Pinning** | **NO** | Executed on macOS (Darwin ARM64) without pinning threads to high-performance cores, exposing measurements to OS task migration between Performance and Efficiency cores. |
| **Cache & Branch Target Warm-Up** | **NO** | No pre-test dummy iterations were executed to warm instruction/data caches or train branch predictors. |
| **Timer Overhead Subtraction** | **NO** | The overhead of `clock_gettime()` ($\approx 25\text{--}35\,\text{ns}$) was not subtracted, though negligible relative to the $100\,\mu\text{s}$ scale. |
| **Dynamic Frequency Scaling (DVFS)** | **UNCONTROLLED**| Host CPU frequency scaling was active, which could account for $\pm 3\text{--}5\,\mu\text{s}$ of baseline jitter. |

---

## 2. Re-Analysis of Observed Latency Distributions

From the 2,400 raw measurements in `countermeasure_results.csv`:

| Execution Mode | Sample Size ($N$) | Mean Latency ($\mu\text{s}$) | Standard Deviation ($\sigma$) | Min / Max ($\mu\text{s}$) | $\Delta t$ Relative to Clean |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Clean Baseline Execution (T6)** | 400 | **106.2** | 3.1 | 101.0 / 114.0 | Baseline ($0.0\,\mu\text{s}$) |
| **Monitored Clean Decapsulation** | 400 | **141.5** | 3.4 | 136.0 / 152.0 | $+35.3\,\mu\text{s}$ ($+33.2\%$) |
| **Monitored Fail-Stop Abort (Variant D)** | 300 | **153.1** | 3.8 | 146.0 / 162.0 | $+46.9\,\mu\text{s}$ ($+44.2\%$) |
| **Monitored Rollback & Recovery (T4)** | 300 | **168.4** | 4.2 | 160.0 / 179.0 | $+62.2\,\mu\text{s}$ ($+58.6\%$) |

### Source-Level Cause of the Latency Delta
- **Why is Monitored Clean slower than Baseline Clean?**
  In `mlkem_fault_hooks.c`, running the butterfly invariant check on all 7 layers of forward NTT and 7 layers of inverse NTT requires $2 \times 7 \times 128 = 1,792$ monitor invocations, adding $\approx 35\,\mu\text{s}$ of arithmetic verification overhead.
- **Why is Recovery slower than Monitored Clean?**
  Recovery triggers an in-place rollback and a second recomputation of the faulted butterfly, adding $\approx 27\,\mu\text{s}$ of overhead.
- **Why is Fail-Stop slower than Baseline Clean?**
  In the tested build, when a mismatch occurs in early NTT stages, `mlkem768_dec_monitored` does not immediately return. It completes the transform before enforcing key quenching and status release, incurring the full monitor execution overhead.

---

## 3. Critical Assessment of the "SIFA Vulnerability" Claim

In Phase 3, the report asserted:
> *"The $+46.9\,\mu\text{s}$ execution delta between clean and fail-stop creates an observable timing channel and a potent SIFA vulnerability."*

### Auditor Evaluation: Scientific Overreach Without Supporting Threat Model

1. **Distinction Between Timing Discrepancy vs. SIFA**:
   - **Timing Discrepancy (Demonstrated)**: An external observer can easily determine whether an error occurred by measuring packet response latency ($106\,\mu\text{s}$ vs $153\,\mu\text{s}$). This is an observable **timing channel / error oracle**.
   - **SIFA (Statistical Ineffective Fault Analysis) (NOT Demonstrated)**: SIFA requires that the fault detection probability or recovery outcome is **secret-dependent** (e.g., an algebraic glitch is ineffective or absorbed only when an intermediate secret key bit is 0). In such a setting, an adversary injects faults, selects only "ineffective" (successful) executions, and exploits the resulting statistical bias in intermediate values to reconstruct the key.
2. **Deficiencies in Claiming SIFA**:
   - The Phase 3 harness used a single fixed secret key ($sk$). No secret-key rotation or differential key-recovery analysis was performed.
   - The timing variation observed is coarse-grained (clean vs error), which indicates an error-distinguishing oracle, not an established SIFA vulnerability.
3. **Appropriate Technical Classification**:
   The observed latency difference should be documented as an **Observable Execution Timing Side Channel** that violates constant-time guarantees across execution branches. Labeling it as an exploitable SIFA attack requires experimental demonstration of secret key bit recovery.
