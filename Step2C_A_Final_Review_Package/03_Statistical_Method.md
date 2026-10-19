# Phase 2 Step 2C-A: Statistical Methodology & Upper Bound Calculations

## 1. Zero-SDC Result & Evaluated Sample

In the Phase 2 Step 2C-A experimental campaign, decapsulation trials were evaluated across three configurations (`BASELINE`, `TFIB_REF`, and `TFIB_META`) over 18 experimental suites of 50 trials each, yielding a total campaign size of $N_{\text{total}} = 900$ trials.

### Denominator Specification
The zero Silent Data Corruption (SDC) rate is computed strictly over the **fault-activated trials**:
- **Fault-Activated Trials ($N_{\text{act}}$):** Exactly $750$ trials where a software fault was actively injected into the operational twiddle, reference twiddle, metadata tag, checker logic, or simultaneously into both operational and reference twiddles.
- **Clean Control Trials ($N_{\text{clean}}$):** Exactly $150$ unmutated baseline runs (50 per configuration) used exclusively to confirm nominal operation and verify 0% false alarms. These 150 clean trials are **excluded** from the SDC denominator.
- **Observed SDC Events ($k$):** Exactly $0$ SDC events observed among the $750$ fault-activated trials ($0 / 750 = 0.0\%$).

A separate subset evaluation is conducted on the paired-mutation suite:
- **Simultaneous Paired-Mutation Suite ($N_{\text{simul}}$):** Exactly $50$ trials where coordinated software mutations applied identical bit-flips to operational and reference twiddles.
- **Observed SDC Events ($k$):** Exactly $0$ SDC events observed among these $50$ trials ($0 / 50 = 0.0\%$).

---

## 2. Statistical Method: Exact One-Sided Clopper–Pearson Binomial Upper Bound

### Mathematical Formulation
Under the assumption of independent, identically distributed Bernoulli trials with constant error probability $p$ per trial, the cumulative probability of observing zero defects in $N$ independent trials is:
$$P(K = 0) = (1 - p)^N$$

To establish a one-sided upper confidence bound $p_{\text{upper}}$ at confidence level $\gamma = 1 - \alpha$ (with $\alpha = 0.05$ for $95\%$ confidence), we solve:
$$(1 - p_{\text{upper}})^N = \alpha = 0.05$$
$$1 - p_{\text{upper}} = \alpha^{1/N} = 0.05^{1/N}$$
$$p_{\text{upper}} = 1 - 0.05^{1/N}$$

### Numerical Calculations

#### Campaign Fault-Activated Trials ($N_{\text{act}} = 750$)
$$p_{\text{SDC}} \le 1 - 0.05^{1/750}$$
$$0.05^{1/750} \approx 0.996009827...$$
$$p_{\text{SDC}} \le 0.00399017... \approx \mathbf{0.399\%}$$

#### Paired-Mutation Suite ($N_{\text{simul}} = 50$)
$$p_{\text{SDC}} \le 1 - 0.05^{1/50}$$
$$0.05^{1/50} \approx 0.941836...$$
$$p_{\text{SDC}} \le 0.058163... \approx \mathbf{5.82\%}$$

---

## 3. Comparison of Statistical Estimators

To prevent ambiguity or conflation of methods, the table below compares the exact one-sided Clopper–Pearson upper bound with standard alternatives:

| Metric / Method | Formula ($k=0$) | $N = 750$ Bound | $N = 50$ Bound | Methodological Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Exact One-Sided Clopper–Pearson (Reported)** | $1 - 0.05^{1/N}$ | **$0.399\%$** ($0.00399$) | **$5.82\%$** ($0.05816$) | Exact finite-sample binomial upper bound at $\gamma = 0.95$. Primary metric across all documentation. |
| **Rule-of-Three Approximation** | $\frac{3}{N}$ | **$0.400\%$** ($0.00400$) | **$6.00\%$** ($0.06000$) | Classical Poisson/Taylor approximation ($-\ln(0.05) \approx 2.9957 \approx 3$). Slightly conservative. |
| **Wilson Score Interval (One-Sided Upper, $\alpha=0.05$)** | $\frac{z^2}{N + z^2}$ with $z=1.6449$ | **$0.360\%$** ($0.00359$) | **$5.13\%$** ($0.05130$) | Asymptotic score test inversion (one-sided $z_{0.95} = 1.64485$). |
| **Wilson Score Interval (Two-Sided Upper, $\alpha=0.05$)** | $\frac{z^2}{N + z^2}$ with $z=1.9600$ | **$0.490\%$** ($0.00489$) | **$7.11\%$** ($0.07114$) | Two-sided 95% confidence interval $[0.0\%, 0.49\%]$ or $[0.0\%, 7.11\%]$. Not to be confused with one-sided bound. |

### Methodological Rule
All documentation files (`phase2_step2c_report.md`, `phase2_step2c_dependency_model.md`, and `phase2_step2c_experiment_design.md`) report the **exact one-sided 95% binomial bound** ($0.399\%$ for $N=750$, $5.82\%$ for $N=50$) as the primary confidence bound. Where the Rule of Three or Wilson score interval is referenced, it is explicitly identified by name and presented solely for methodological comparison.

---

## 4. Assumptions, Conditions, and Scientific Scope

The statistical confidence bound of $p_{\text{SDC}} \le 0.399\%$ is strictly conditional upon the following experimental conditions and must **not** be interpreted as an unconditional or physical guarantee:

1. **Software-Level Model Assumption:** Faults were injected as deterministic bit-flips in C variables within host process memory on macOS ARM64. The bound reflects behavior under these tested software perturbations, not microarchitectural or physical fault mechanisms.
2. **Pseudo-Random Sampling Distribution:** Trials were generated deterministically using domain-separated SHAKE-256 PRF derivations (`campaign_prf.h`). While uniform over trial seeds, this does not represent the full combinatorial space of multi-bit faults or adversarial fault selection.
3. **Specific Configuration Mix:** The 750 fault-activated trials represent a structured mixture of 15 fault suites (operational twiddles, reference twiddles, tags, checker logic, and paired mutations) across three architectures. The aggregate bound reflects this specific experimental mix.
4. **No Physical Radiation Qualification:** This bound does **not** prove physical radiation tolerance, single-event upset (SEU) immunity, or spatial silicon independence. Physical qualification requires beam testing and hardware fault injection.
