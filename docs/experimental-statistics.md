# Experimental Statistics and Uncertainty Quantification

## 1. Scientific Objective

In empirical fault injection, binary outcomes (e.g., fault detected vs. silent data corruption) follow binomial distributions. Simply reporting an observed proportion $\hat{p} = k/n$ without confidence bounds is statistically invalid for scientific publication. This document defines the formal statistical methodology applied across all experimental campaigns.

---

## 2. Sample Size Determination

For initial pipeline validation and development:
$$N = 1,000 \quad \text{iterations per test condition}$$
For formal research campaigns and paper figures:
$$N = 10,000+ \quad \text{iterations per test condition}$$

### Margin of Error Calculation
Under a standard binomial distribution, the maximum standard error of an estimated proportion $\hat{p}$ occurs at $p = 0.5$:
$$\text{SE}_{\max} = \sqrt{\frac{0.5 \times (1 - 0.5)}{N}} = \frac{0.5}{\sqrt{N}}$$
- For $N = 1,000$: Maximum margin of error at 95% confidence is $E \approx 1.96 \times \frac{0.5}{\sqrt{1000}} \approx \pm 3.10\%$.
- For $N = 10,000$: Maximum margin of error at 95% confidence is $E \approx 1.96 \times \frac{0.5}{\sqrt{10000}} \approx \pm 0.98\%$.

---

## 3. Confidence Interval Formulation: Wilson Score Interval

Because fault rates can be near 0% (e.g., CRASH rate in memory-safe code) or near 100% (e.g., DETECTED_FAILURE under strict parity checks), the standard normal (Wald) approximation $\hat{p} \pm z \sqrt{\hat{p}(1-\hat{p})/n}$ fails catastrophically (can produce bounds outside $[0, 1]$).

We mandate the **Wilson Score Interval** with continuity correction for all reported failure and detection rates:

$$CI_{95\%} = \frac{\hat{p} + \frac{z^2}{2N} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{N} + \frac{z^2}{4N^2}}}{1 + \frac{z^2}{N}}$$
where $z = 1.95996$ for a two-sided 95% confidence level.

---

## 4. Deterministic Random Seed Strategy

Reproducibility is enforced through hierarchical, cryptographically independent PRNG seeding:
1. **Master Campaign Seed:** Fixed 64-bit integer specified in the experiment manifest YAML (e.g., `seed: 421098`).
2. **Deterministic Run Seeding:** For each iteration $i \in \{0, \dots, N-1\}$, the iteration seed is derived via a cryptographic key derivation function or non-overlapping sequence:
   $$\text{Seed}_i = \text{SHA-256}(\text{MasterSeed} \parallel i)[0..7]$$
3. **Reproducibility Guarantee:** Any specific failed or anomalous trial can be replayed in isolation by specifying `(MasterSeed, IterationID)`.

---

## 5. Performance Timing Statistics

For latency and computational overhead measurements:
- **Warmup:** Minimum 20 unmeasured iterations to warm CPU caches and instruction branch predictors.
- **Reporting Metrics:**
  - **Median ($Q_2$):** Primary measure of central tendency (robust to OS context switches).
  - **Interquartile Range (IQR = $Q_3 - Q_1$):** Primary measure of dispersion.
  - **Mean ($\mu$) and Standard Deviation ($\sigma$):** Secondary parametric reporting.
  - **99th Percentile ($P_{99}$):** Worst-case execution timing for real-time space systems.
- **Outlier Treatment:** Timing samples exceeding $\mu + 4\sigma$ (attributable to OS interrupts) are logged with diagnostic flags but isolated in the trimmed distributions.
