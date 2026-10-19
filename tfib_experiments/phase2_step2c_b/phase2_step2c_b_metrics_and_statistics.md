# Phase 2 Step 2C-B: Metrics, Statistical Methodology & Pilot-Contingent Power Analysis

**Document:** `phase2_step2c_b_metrics_and_statistics.md`  
**Phase:** Phase 2 Step 2C-B (Experimental Design — Revision 3)  
**Status:** Methodological Design Specification Only (No Implementation or Execution)  
**Date:** 2026-10-04  
**Target:** ML-KEM-768 with Two-Factor Invariant Butterfly (TFIB)  

---

## 1. Primary Statistical Comparison: McNemar's Paired Analysis

### 1.1 The Unit of Pairing & Trial Independence
Because all layout variants are evaluated using identical deterministic PRF seeds derived from `campaign_prf.h`, experimental trials are **strictly matched**:
- **Unit of Pairing:** A single end-to-end decapsulation execution trial $j$ evaluating identical public/private keypairs, identical ciphertext, and identical relative spatial fault parameters ($A_{\text{anchor}} = A_{\text{op}}$, $\Delta_{\text{offset}} = 0$, $L = 512$ bytes, and identical pseudo-random XOR mutation mask stream $M$).
- **Trial Independence:** Every trial $j$ initializes a fresh cryptographic context and clean process heap memory. No cryptographic or arithmetic state is preserved between consecutive trials $j$ and $j+1$.

### 1.2 Primary Binary Outcome Variable ($Y_j^{(V)}$)
For trial $j$ in variant $V \in \{A, B, C\}$, the primary outcome $Y_j^{(V)} \in \{0, 1\}$ evaluates local countermeasure integrity:

$$Y_j^{(V)} = \begin{cases} 
1 & \text{if reference table integrity is preserved, local monitor detects operational mismatch, and recovers genuinely} \\
0 & \text{if reference table is corrupted (dual-table corruption, checker blindness, or poisoned rollback)}
\end{cases}$$

### 1.3 McNemar's Paired $2 \times 2$ Contingency Table
For the primary confirmatory comparison between Variant A (Collocated) and Variant C (Page-Isolated):

```
                          Variant C (Page-Isolated)
                          Y = 1 (Preserved)    Y = 0 (Corrupted)
Variant A        Y = 1          n_11                  n_10
(Collocated)     Y = 0          n_01                  n_00
```

- $n_{11}$: Both variants preserved the reference table.
- $n_{00}$: Both variants suffered reference table corruption.
- $n_{01}$: Variant A suffered dual corruption, but Variant C preserved the reference table (discordant pair favoring Variant C).
- $n_{10}$: Variant A preserved the reference table, but Variant C suffered dual corruption (discordant pair favoring Variant A).
- Total discordant pairs: $n_{\text{disc}} = n_{01} + n_{10}$.

### 1.4 Exact vs Asymptotic Test Selection
To ensure exact statistical validity regardless of observed event counts:
1. **Exact Conditional Binomial Test (Default for $n_{\text{disc}} < 25$):**
   Under $H_0: P(n_{01}) = P(n_{10}) = 0.5$, $n_{01} \sim \text{Binomial}(n_{\text{disc}}, 0.5)$. The exact two-sided $p$-value is:
   $$p_{\text{exact}} = 2 \times \sum_{k=0}^{\min(n_{01}, n_{10})} \binom{n_{\text{disc}}}{k} 0.5^{n_{\text{disc}}}$$
2. **McNemar's Asymptotic Test with Edwards' Continuity Correction (For $n_{\text{disc}} \ge 25$):**
   $$\chi^2 = \frac{(|n_{01} - n_{10}| - 1)^2}{n_{01} + n_{10}}, \quad \text{df} = 1$$

---

## 2. Statistical Power & Pilot-Contingent Sample Sizing

### 2.1 Why Sample Size Cannot Be Fixed a Priori
In McNemar's test, statistical power depends non-linearly on two parameters:
1. The **marginal difference** $\delta = |P(Y^{(C)} = 1) - P(Y^{(A)} = 1)| = \frac{|n_{01} - n_{10}|}{N}$.
2. The **total discordant proportion** $p_{\text{disc}} = P(n_{01}) + P(n_{10}) = \frac{n_{01} + n_{10}}{N}$.

Using the standard asymptotic sample size formulation (Connor 1987, Miettinen 1968):

$$N = \frac{\left( z_{1 - \alpha/2} \sqrt{p_{\text{disc}}} + z_{1 - \beta} \sqrt{p_{\text{disc}} - \delta^2} \right)^2}{\delta^2}$$

Because $p_{\text{disc}}$ cannot be known prior to executing the spatial fault engine on the compiled binary, **claiming a guaranteed fixed sample size of $N=250$ with $>85\%$ power a priori is methodologically ungrounded**. Depending on $p_{\text{disc}}$, $N=250$ may be severely underpowered or unnecessarily excessive.

### 2.2 Stage 1: Exploratory Pilot Campaign ($N_{\text{pilot}} = 50$ paired trials)
- **Role:** An exploratory calibration phase to measure empirical discordance $\hat{p}_{\text{disc}} = (n_{01} + n_{10}) / 50$ and verify that the spatial injector functions without operating system traps.
- **Pilot Decision Rule for Confirmatory Phase:**
  - **Case 1: Zero Discordance ($\hat{p}_{\text{disc}} = 0$):**
    If all 50 trials yield $n_{01} = n_{10} = 0$, the fault model affects both layouts identically (e.g. blast does not reach reference table in either, or reaches both). The experiment pauses for geometric review; increasing $N$ without changing $L$ is statistically futile.
  - **Case 2: Positive Discordance ($\hat{p}_{\text{disc}} > 0$):**
    Calculate the confirmatory sample size $N_{\text{conf}}$ using Connor's formula for target power $1 - \beta = 0.90$, two-sided $\alpha = 0.01$ (with Holm-Bonferroni correction, $\alpha_1 = 0.005 \implies z_{1 - 0.005/2} = 2.807$), and minimum meaningful effect $\delta = 0.10$.

### 2.3 Sample Size Requirements Across Discordance Scenarios ($\delta = 0.10$, Power $= 90\%$, $\alpha = 0.005$)

```
+---------------------------------------------------------------------------------------------------+
|                        CONNOR (1987) SAMPLE SIZE PLANNING MATRIX (delta = 0.10)                   |
+--------------------------+------------------------------+--------------------+--------------------+
| Discordant Proportion    | Estimated Concordance        | Required N (alpha= | Feasibility        |
| p_disc = (n01 + n10) / N | (n11 + n00) / N              | 0.005, power=0.90) | Assessment         |
+--------------------------+------------------------------+--------------------+--------------------+
| p_disc = 0.10 (Minimal)  | 0.90                         | N = 162 trials     | Readily Executable |
| p_disc = 0.15 (Moderate) | 0.85                         | N = 246 trials     | Target Plan (~250) |
| p_disc = 0.20 (Standard) | 0.80                         | N = 329 trials     | Readily Executable |
| p_disc = 0.30 (High)     | 0.70                         | N = 496 trials     | Upper Limit (N=500)|
| p_disc > 0.35 (Extreme)  | < 0.65                       | N > 600 trials     | Diminishing Return |
+--------------------------+------------------------------+--------------------+--------------------+
```

**Pre-Registered Confirmatory Protocol:**
- The confirmatory campaign will execute $N_{\text{conf}} = \max(200, \min(500, \lceil N_{\text{calc}} \rceil))$ paired trials.
- If the pilot indicates $N_{\text{calc}} > 500$, the campaign caps at $N=500$ and reports the observed statistical power alongside the effect size.

---

## 3. Multiple Comparisons Control

The primary confirmatory phase evaluates two planned pairwise comparisons against Variant A:
1. **Hypothesis Test 1:** Variant A (Collocated) vs Variant B (Section-Isolated)
2. **Hypothesis Test 2:** Variant A (Collocated) vs Variant C (Page-Isolated)

To strictly enforce a Family-Wise Error Rate (FWER) of $\alpha_{\text{family}} \le 0.01$:
- **Holm–Bonferroni Step-Down Procedure:**
  1. Rank order the two $p$-values: $p_{(1)} \le p_{(2)}$.
  2. Test $p_{(1)}$ against $\alpha_1 = \frac{0.01}{2} = 0.005$. If $p_{(1)} \ge 0.005$, **neither null hypothesis is rejected**; testing halts.
  3. If $p_{(1)} < 0.005$, reject $H_{0,(1)}$ and test $p_{(2)}$ against $\alpha_2 = 0.01$. If $p_{(2)} < 0.01$, reject $H_{0,(2)}$.

---

## 4. Effect Size, Confidence Intervals & Trial Accounting

### 4.1 Effect Size & Confidence Interval
- **Effect Size Metric:** The marginal proportion difference $\widehat{\Delta p} = \frac{n_{01} - n_{10}}{N}$.
- **Confidence Interval:** Computed via the **Agresti–Min method** with Wilson score bounds at the 99% confidence level (matching the FWER $\alpha = 0.01$).
- **Minimum Meaningful Effect Threshold:** Pre-registered at $\Delta p \ge 10.0\%$. If $\Delta p < 0.10$ even with $p < 0.005$, the effect is classified as statistically detectable but practically negligible.

### 4.2 Handling Invalid, Ineffective, and Infrastructure Failure Trials
All experimental trials must be rigorously accounted for in the raw output data:
1. **Effective Trials:** The spatial mutation interval successfully corrupts at least one operational twiddle coefficient read during decapsulation. Included in primary McNemar analysis.
2. **Ineffective Padding Trials:** The mutation interval falls entirely within alignment padding or unused table trailing bytes, leaving active twiddle coefficients uncorrupted. Decapsulation completes cleanly. These trials are recorded in the trial log but **flagged as ineffective and excluded from the discordant pairs analysis**.
3. **Infrastructure Failures:** An operating system permission fault (`SIGSEGV`, `vm_protect` error) or invalid memory trap occurs.
   - Infrastructure failures **cannot be silently dropped**.
   - If an infrastructure failure occurs, the trial is flagged as an `INFRASTRUCTURE_ABORT`.
   - **Fail-Closed Threshold:** If infrastructure failures exceed **1.0% of total trials** ($>2$ in pilot, $>5$ in confirmatory), the entire campaign is declared invalid and aborted for harness remediation.
