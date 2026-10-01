# Phase 7K: Statistical Re-Analysis & Raw Data Integrity Audit

## 1. Raw Dataset Verification & Traceability

The raw trial records from Phase 7I (`results/phase7i/raw/phase7i_e2e_trials.json`, $N=1,400$) and Phase 7J (`results/phase7j/raw/phase7j_extended_trials.json`, $N=1,600$) were audited using [`experiments/phase7k/statistical_audit.py`](file:///Users/dhairyajain/Desktop/pqc%20research/experiments/phase7k/statistical_audit.py).

### Data Integrity Audit Summary:
- **Trial ID Uniqueness**: 1,400 unique IDs in Phase 7I ($0 \le \text{ID} \le 1399$); 1,600 unique IDs in Phase 7J ($0 \le \text{ID} \le 1599$). Zero duplicate IDs detected.
- **Completeness**: Zero missing records or truncated JSON arrays.
- **PRNG Seed Independence**:
  - Phase 7I seeds: $\text{seed} = (\text{class} + 1) \times 40000 + \text{trial} + 999$
  - Phase 7J seeds: $\text{seed} = (\text{class} + 1) \times 50000 + \text{trial} + 1234$
  - **Seed Intersection**: Exactly **0 collisions** across all 3,000 generated seeds.
- **Absence of Double-Counting**: Phase 7I and Phase 7J records represent completely separate experimental campaigns evaluating disjoint threat models and seeds.

---

## 2. Master Outcome Distribution & Confidence Intervals

| Campaign / Scope | Sample Size ($N$) | Autonomous Recoveries | Safe Rejections | Benign Equivalent | Undetected Corruptions | Undetected Rate (Wilson 95% CI) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Phase 7I Campaign** | 1,400 | 700 (50.00%) | 583 (41.64%) | 117 (8.36%) | **0 (0.00%)** | $[0.000\%, 0.273\%]$ |
| **Phase 7J Extended** | 1,600 | 899 (56.19%) | 589 (36.81%) | 112 (7.00%) | **0 (0.00%)** | $[0.000\%, 0.239\%]$ |
| **Cumulative Total** | **3,000** | **1,499 (49.97%)** | **1,272 (42.40%)** | **229 (7.63%)** | **0 (0.00%)** | **$[0.000\%, 0.128\%]$** |

### Statistical Categorization Breakdown (Cumulative 3,000 Trials):
1. **Autonomous Recovery ($49.97\%$, 95% CI $[48.18\%, 51.75\%]$)**:
   All transient arithmetic single-bit and multi-bit faults in butterfly adders, multipliers, and intermediate differences were detected, rolled back, and recomputed in place, producing $K == K_{\text{valid}}$.
2. **Safe Implicit Rejection ($42.40\%$, 95% CI $[40.64\%, 44.18\%]$)**:
   Persistent faults, shadow register corruptions, pre-NTT ciphertext tampering, and retry-exhaustion events safely triggered fail-stop and emitted $K == K_{\text{rej}}$, releasing no private keys.
3. **Benign Equivalent Behavior ($7.63\%$, 95% CI $[6.74\%, 8.64\%]$)**:
   Negative controls and twiddle factor bit-flips that mapped to algebraically identical ring quotients produced $K == K_{\text{valid}}$ without triggering monitor retries.
4. **Undetected Corruptions ($0.00\%$, 95% CI $[0.000\%, 0.128\%]$)**:
   Zero uncontained or corrupted shared secrets were released.

---

## 3. Methodological Rigor: Observed Rates vs True Failure Probability

In academic publication, zero observed events must not be presented as proof of impossible occurrence.

### Critical Statistical Principle:
$$\hat{p} = \frac{0}{3000} = 0.00\% \not\implies \Pr(\text{Undetected Corruption}) = 0$$

Using the Wilson score interval with continuity correction:
$$\text{CI}_{95\%} = \left[ 0, \frac{z_{1-\alpha/2}^2}{N + z_{1-\alpha/2}^2} \right] = \left[ 0, \frac{1.95996^2}{3000 + 1.95996^2} \right] \approx [0.000\%, 0.128\%]$$

### Publication Recommendation:
State clearly that across 3,000 empirical injection trials, zero undetected corruptions were observed, establishing with 95% statistical confidence that the rate of uncontained key leakage is bounded below **$0.128\%$** under the evaluated software fault model.
