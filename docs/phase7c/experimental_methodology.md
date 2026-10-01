# Phase 7C: Experimental Methodology & Validation Framework

## 1. Experimental Setup & Target Definition
* **Target Algorithm:** NIST FIPS 203 ML-KEM-768 (scalar C reference implementation)
* **Compiler:** Apple Clang version 17.0.0 (clang-1700.0.13.5), target `arm64-apple-darwin26.5.0`
* **Optimization Flag:** `-O3 -Wall -Wextra -std=c11`
* **Benchmarking Hardware:** Apple Silicon AArch64 (hardware monotonic clock `CLOCK_MONOTONIC`)
* **Iteration Counts:** 
  - Systematic Fault Evaluation: 1,200 trials (150 trials/class across 8 threat classes)
  - Latency & Overhead Benchmarks: 2,000 iterations per configuration

---

## 2. Tested Configurations
1. **Config 1 (Baseline):** Standard unmodified `mlkem768_dec()` reference implementation.
2. **Config 2 (Unweighted Parity NTT Invariant):** Projects even and odd coefficients into parity sums.
3. **Config 3 (Complementary Weighted NTT Invariant):** Dual parity projection with inverse-root weighting ($\zeta_{2i+1}^{-1}$).
4. **Config 4 (Full Duplicate Decapsulation - DMR):** Two independent serial decapsulations with output `memcmp`.
5. **Config 5 (Phase 7 Layered with Oracle):** Original layered architecture utilizing external `expected_ss` test-harness oracle.
6. **Config 6 (Phase 7C Oracle-Free Native Layered):** Refactored layered architecture with in-tree native monitoring via `mlkem768_dec_monitored()` (**ZERO `expected_ss` oracle**).

---

## 3. Strict Separation of Mechanism from Test Evaluation
In Phase 7, the test oracle `expected_ss` was passed into the runtime decapsulation function `decaps_layered()`. 
In Phase 7C:
* `expected_ss` is **never** provided to `decaps_layered_native()` or `mlkem768_dec_monitored()`.
* The decapsulation function derives its internal execution status purely from:
  1. Link-layer frame CRC32.
  2. Polynomial NTT invariant (when evaluating transform stages).
  3. Constant-time in-tree re-encryption comparison status (`fail` vs `fail_chk`).
  4. Multi-rail complementary register checking.
* The expected secret is used **strictly offline after execution** by the test harness solely to label the final cryptographic outcome (`CORRECT_KEY` vs `MUTATED_OR_REJECTED`) in the raw JSON logs.

---

## 4. Evaluated Threat Classes (150 Trials Each)
* **Class 1 (Intermediate T):** Single-bit flips in intermediate multiplier products across NTT layers 1 to 7.
* **Class 2 (Twiddle Zeta):** Single-bit flips in twiddle table values $\zeta$ during NTT butterflies.
* **Class 3 (Output Add Reg):** Asymmetric additive glitches on individual output coefficients.
* **Class 4 (Correlated Multiplier):** Mid-operation accumulator corruption in polynomial dot products.
* **Class 5 (Pre-Invocation Input):** Single-bit corruption in ciphertext buffer payload prior to invocation.
* **Class 6 (Checker State Perturbation):** Bit flips injected into monitor token registers.
* **Class 7 (Control FO Gate Flip):** Predicate overrides in Fujisaki-Okamoto re-encryption comparison ($0 \to 1$ and $1 \to 0$).
* **Class 8 (Persistent Stuck-At):** Hardware multiplier stuck-at-zero faults persisting across all redundant calls.
