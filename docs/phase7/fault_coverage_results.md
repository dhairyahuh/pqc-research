# Fault Coverage and Resilience Results

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Harness Output:** `results/phase7/processed/phase7_resilience_results.json`  
**Total Injected Trials:** 1,200 trials (150 per fault class)

---

## 1. Comprehensive Fault Detection Matrix

The table below reports the empirical detection coverage across the 8 threat classes for all 5 evaluated configurations:

| Threat Fault Class | Config 1 (Baseline) | Config 2 (Unweighted Invariant) | Config 3 (Complementary NTT) | Config 4 (Duplicate DMR) | Config 5 (Layered Architecture) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Class 1 (Intermediate T)** | 0.0% (0/150) | 0.0% (0/150) | 14.0% (21/150) | 96.7% (145/150) | **96.7% (145/150)** |
| **Class 2 (Twiddle Zeta)** | 0.0% (0/150) | 0.0% (0/150) | 14.0% (21/150) | 100.0% (150/150) | **100.0% (150/150)** |
| **Class 3 (Output Add Reg)** | 0.0% (0/150) | 100.0% (150/150) | 100.0% (150/150) | 98.7% (148/150) | **100.0% (150/150)** |
| **Class 4 (Correlated Mult)** | 0.0% (0/150) | 0.0% (0/150) | 0.0% (0/150) | 100.0% (150/150) | **100.0% (150/150)** |
| **Class 5 (Pre-Invoc Input)** | 0.0% (0/150) | 0.0% (0/150) | 0.0% (0/150) | 0.0% (0/150) | **100.0% (150/150)** |
| **Class 6 (Checker Perturb)** | 0.0% (0/150) | 0.0% (0/150) | 0.0% (0/150) | 0.0% (0/150) | **100.0% (150/150)** |
| **Class 7 (Control FO Gate)** | 0.0% (0/150) | 0.0% (0/150) | 0.0% (0/150) | 0.0% (0/150) | **100.0% (150/150)** |
| **Class 8 (Persistent Stuck)** | 0.0% (0/150) | 0.0% (0/150) | 0.0% (0/150) | 0.0% (0/150) | **100.0% (150/150)** |

---

## 2. Statistical Analysis & Confidence Intervals

Using Wilson score intervals at 95% confidence ($z = 1.96$):
- **100.0% Detection (150/150 trials):** 95% CI = $[97.5\%, 100.0\%]$.
- **96.7% Detection (145/150 trials):** 95% CI = $[92.4\%, 98.6\%]$.
- **0.0% Detection (0/150 trials):** 95% CI = $[0.0\%, 2.5\%]$.

---

## 3. Key Empirical Findings

1. **Confirmation of Universal Parity Cancellation:**
   - Config 2 (Unweighted Parity Invariant) exhibits **0.0% detection** across both Class 1 (`INTERMEDIATE_T`) and Class 2 (`TWIDDLE_ZETA`).
   - Every single butterfly multiplier error in layers 1 through 7 cancels algebraically.
2. **Breakthrough of the Weighted Inverse-Zeta Invariant:**
   - Config 3 detects 100% of Layer 7 `INTERMEDIATE_T` and `TWIDDLE_ZETA` faults (overall 14.0% across all 7 layers, as Layer 7 represents 1/7 of trials).
3. **DMR Blind Spots Confirmed:**
   - Config 4 (Duplicate DMR) completely fails (0.0% detection) on Class 5 (Pre-invocation Input Corruption) and Class 8 (Persistent Stuck Faults), as both passes read the same corrupted state and agree on a faulty shared secret.
4. **Superiority of the Layered Architecture:**
   - Config 5 achieves **$\ge 96.7\%$ detection across every single evaluated fault class**, completely eliminating DMR's common-mode vulnerabilities while preventing the silent desynchronization inherent in baseline FIPS 203 implicit rejection.
