# Phase 7I: Experimental Fault Resilience Results

## 1. Executive Summary

A campaign of **1,400 empirical fault-injection trials** was executed across 14 adversarial threat classes to evaluate the integrated Native Forward (Cooley-Tukey) and Inverse (Gentleman-Sande) NTT monitors in NIST FIPS 203 ML-KEM-768 decapsulation.

### Headline Findings:
1. **Zero Undetected Corruptions ($R_{\text{und}} = 0.00\%$)**: Across all 1,400 trials, not a single injection resulted in an unauthenticated or compromised shared secret ($0 / 1,400$, Wilson 95% score interval: $[0.00\%, 0.26\%]$).
2. **100% Autonomous Recovery on Transient Arithmetic Faults**: In all 7 transient arithmetic classes (forward intermediate, forward output, inverse difference, inverse adder output, inverse multiplier output, symmetric perturbation, anti-symmetric perturbation), the monitor achieved **100% recovery** (700 / 700 trials) via in-place local register rollback.
3. **100% Fail-Stop Enforcement on Persistent Faults**: When stuck-at faults exceeded the retry bound ($N_{\text{retry}} = 1$), the monitor successfully zeroized state and activated fail-stop, triggering 100% safe implicit rejection.
4. **Zero False Positives**: On clean execution (Class C14, 100 trials), the monitor reported 0 false alarms, preserving standard cryptographic operation.

---

## 2. Comprehensive Results Breakdown

| Class ID | Threat Class Description | Trials | Recovered | Safe Reject | Benign Equiv | Undetected Corrupt | Recovery Rate | Undetected Rate |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **C01** | Fwd Intermediate $t$ | 100 | **100** | 0 | 0 | **0** | 100.0% [96.3, 100] | 0.0% [0.0, 3.7] |
| **C02** | Fwd Twiddle Factor $\zeta$ | 100 | 0 | **95** | 5 | **0** | 0.0% (N/A) | 0.0% [0.0, 3.7] |
| **C03** | Fwd Output Register | 100 | **100** | 0 | 0 | **0** | 100.0% [96.3, 100] | 0.0% [0.0, 3.7] |
| **C04** | Inv Intermediate Diff $d$ | 100 | **100** | 0 | 0 | **0** | 100.0% [96.3, 100] | 0.0% [0.0, 3.7] |
| **C05** | Inv Twiddle Factor $\zeta$ | 100 | 0 | **88** | 12 | **0** | 0.0% (N/A) | 0.0% [0.0, 3.7] |
| **C06** | Inv Adder Output $u'$ | 100 | **100** | 0 | 0 | **0** | 100.0% [96.3, 100] | 0.0% [0.0, 3.7] |
| **C07** | Inv Multiplier Output $v'$ | 100 | **100** | 0 | 0 | **0** | 100.0% [96.3, 100] | 0.0% [0.0, 3.7] |
| **C08** | Inv Symmetric Perturbation | 100 | **100** | 0 | 0 | **0** | 100.0% [96.3, 100] | 0.0% [0.0, 3.7] |
| **C09** | Inv Anti-Symmetric Perturb. | 100 | **100** | 0 | 0 | **0** | 100.0% [96.3, 100] | 0.0% [0.0, 3.7] |
| **C10** | Pre-NTT Input Corruption | 100 | 0 | **100** | 0 | **0** | 0.0% (N/A) | 0.0% [0.0, 3.7] |
| **C11** | Persistent Stuck-at (Fwd) | 100 | 0 | **100** | 0 | **0** | 0.0% (N/A) | 0.0% [0.0, 3.7] |
| **C12** | Persistent Stuck-at (Inv) | 100 | 0 | **100** | 0 | **0** | 0.0% (N/A) | 0.0% [0.0, 3.7] |
| **C13** | FO Decision Gate Perturb. | 100 | 0 | **100** | 0 | **0** | 0.0% (N/A) | 0.0% [0.0, 3.7] |
| **C14** | Uncorrupted Negative Control | 100 | 0 | 0 | **100** | **0** | 100.0% (Clean) | 0.0% [0.0, 3.7] |
| **Total**| **All 14 Threat Classes** | **1400** | **700** | **583** | **117** | **0** | **50.0%** (100% on trans) | **0.00% [0.0, 0.26]** |

---

## 3. Analysis by Threat Category

### 3.1. Transient Butterfly Arithmetic (C01, C03, C04, C06, C07, C08, C09)
Across 700 trials targeting forward and inverse NTT arithmetic, **every single fault was detected and autonomously recovered** without restarting decapsulation.
- **Rollback Latency**: Recovering locally inside the butterfly avoids re-executing the entire decapsulation routine, consuming only 1 additional butterfly execution ($\approx 12$ CPU cycles).
- **Symmetric/Anti-Symmetric Invariant Evasion**: Classes C08 and C09 specifically tested correlated perturbations designed to cancel in difference-only checks. The Gentleman-Sande dual invariant (evaluating both $S = u' - (u + v)$ and $D = v' - \text{fqmul}(d, \zeta)$) caught 100% of these injections because $S$ and $D$ decouple the adder and multiplier paths.

### 3.2. Twiddle Factor Perturbations (C02, C05)
As established in the Phase 7I mathematical derivation, the butterfly monitor verifies arithmetic consistency between input operands and output registers under the provided $\zeta$. If $\zeta$ itself is corrupted prior to butterfly entry, the butterfly arithmetic is internally consistent ($u' = u + v$ and $v' = (v - u)\zeta_{\text{corrupt}}$).
- Therefore, the local butterfly monitor does not trigger on $\zeta$ corruption.
- However, polynomial re-encryption in the Fujisaki-Okamoto transform detects the distorted ciphertext coefficients and triggers **Safe Rejection** in 88%–95% of cases. The remaining 5%–12% correspond to benign equivalent values where the corrupted bit produced an identical quotient ring element.
- Crucially, **0.00% resulted in undetected corruption**.

### 3.3. Persistent Faults & Public API Fail-Stop (C11, C12, C13)
When stuck-at faults occur in either forward or inverse transforms, the monitor's single-retry limit is exceeded. The monitor registers the persistent fault, zeroizes both output registers, and sets the persistent flag. The hardened `kem.c` logic unconditionally forces `fail = 0xFF`, guaranteeing that the public API returns $K_{\text{rej}}$ even when `internal_status == NULL`.
