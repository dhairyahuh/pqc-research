# Rigorous Mathematical Framework: Modeling, Bounds, and Constrained Optimization
**Project:** Adaptive, Resilient, Post-Quantum Space Communication Framework  
**Phase:** Phase 5 — Mathematical Foundation  
**Date:** October 2026  
**Status:** Defensible Analytical Formulation  

---

## 1. Mathematical Taxonomy & Nature of Contribution

Before presenting mathematical derivations, the academic classification of this mathematical framework is formally established:
- **Established Theory:** Discrete-Time Markov Chains (DTMC), Gilbert-Elliott channel analysis, Reed-Solomon coding bounds (Singleton bound), and Wilson score confidence intervals are well-established classical theory.
- **Novel Mathematical Formulation:** The **Constrained Cross-Layer Optimization Problem**, which explicitly separates hard cryptographic security invariants from link performance objectives and couples endpoint arithmetic recovery probability ($R_{\text{rec}}$) with communication goodput, represents an original system-level formulation.

---

## 2. Stochastic Channel State Modeling

### 2.1 Discrete-Time Markov Chain (DTMC) Formulation
Let the channel state at discrete transmission interval $t \in \{0, 1, 2, \dots\}$ be $S_t \in \mathcal{S} = \{G, B, O\}$, where:
- $G$: Good State (nominal LEO/GEO link).
- $B$: Bad State (rain fade / ionospheric scintillation).
- $O$: Outage State (orbital occultation / antenna blockage).

The state evolution is governed by a homogeneous, irreducible, aperiodic discrete-time Markov chain with transition probability matrix $\mathbf{P} \in \mathbb{R}^{3 \times 3}$:

$$\mathbf{P} = \begin{bmatrix}
1 - (P_{GB} + P_{GO}) & P_{GB} & P_{GO} \\
P_{BG} & 1 - (P_{BG} + P_{BO}) & P_{BO} \\
P_{OG} & P_{OB} & 1 - (P_{OG} + P_{OB})
\end{bmatrix}$$

### 2.2 Stationary Distribution
Because $\mathbf{P}$ is stochastic and ergodic, a unique stationary distribution vector $\boldsymbol{\pi} = [\pi_G, \pi_B, \pi_O]^T$ exists satisfying:
$$\boldsymbol{\pi}^T \mathbf{P} = \boldsymbol{\pi}^T \quad \text{subject to} \quad \sum_{s \in \mathcal{S}} \pi_s = 1$$

Solving $\boldsymbol{\pi}^T (\mathbf{P} - \mathbf{I}) = \mathbf{0}$, the steady-state availability of the nominal channel is:
$$\pi_G = \frac{P_{BG} P_{OG} + P_{BO} P_{OG} + P_{BG} P_{OB}}{\sum_{\text{states}} \text{cofactors}}$$

### 2.3 Unconditional Channel Packet Erasure Rate
Let $\epsilon_s$ denote the conditional packet erasure probability in state $s$:
$$\epsilon_G \ll 10^{-4}, \quad \epsilon_B \in [0.10, 0.50], \quad \epsilon_O = 1.00$$
The unconditional expected packet erasure probability $\bar{\epsilon}$ is:
$$\bar{\epsilon} = \sum_{s \in \mathcal{S}} \pi_s \epsilon_s = \pi_G \epsilon_G + \pi_B \epsilon_B + \pi_O$$

---

## 3. Coding Theory & Interleaving Bounds

### 3.1 Reed-Solomon Erasure Decoding Over Packet Channels
Consider a packet-level systematic block code $(N, K)$, where $K$ information packets are encoded with $M = N - K$ parity packets. 
* **Singleton Bound for Maximum Distance Separable (MDS) Codes:**
  $$d_{\min} = N - K + 1 = M + 1$$
* **Erasure Correction Guarantee:** An MDS erasure code (such as Reed-Solomon over $GF(2^8)$ or packet parity arrays) can recover all $K$ original information packets if and only if the number of erased packets $e$ satisfies:
  $$e \le N - K$$
  Equivalently, the receiver requires any $K$ out of $N$ transmitted packets to achieve 100% reconstruction.

### 3.2 Block Interleaving Dispersion Theorem
In the Bad state ($B$), channel erasures occur in contiguous bursts of average length $\mu_B = 1 / P_{BG}$.
* Let a matrix interleaver have depth $D$ and width $N$. Contiguous channel packet erasures of length $L \le D$ are dispersed across $L$ distinct $(N, K)$ codewords such that each codeword experiences at most:
  $$e_{\text{codeword}} \le \left\lceil \frac{L}{D} \right\rceil \text{ erasures}$$
* **Sufficient Condition for Zero Loss:** If the interleaving depth satisfies:
  $$D \ge \frac{L_{\max}}{N - K}$$
  then all burst erasures of length $L \le L_{\max}$ are completely corrected by the FEC decoder without invoking link retransmission.

---

## 4. Endpoint Cryptographic Resilience Formulation

### 4.1 Invariant Error Kernel Intersection
Let the input coefficients to an NTT butterfly be $u, v \in \mathbb{Z}_q$ with twiddle $\zeta \in \mathbb{Z}_q$ ($q = 3329$). Let the computed butterfly outputs be $\tilde{u}, \tilde{v}$. Under an additive fault $(\Delta u, \Delta v) \in \mathbb{Z}_q^2$:
$$\tilde{u} \equiv u' + \Delta u \pmod q, \quad \tilde{v} \equiv v' + \Delta v \pmod q$$

1. **Forward Cooley-Tukey Invariants:**
   - Sum Check: $\Delta_{\text{sum}} = (\tilde{u} + \tilde{v}) - 2u \equiv \Delta u + \Delta v \pmod q$.
   - Difference Check: $\Delta_{\text{diff}} = (\tilde{u} - \tilde{v}) - 2(v\zeta) \equiv \Delta u - \Delta v \pmod q$.
2. **Error Kernel Analysis:**
   $$\ker(\Delta_{\text{sum}}) = \{(\Delta u, \Delta v) \in \mathbb{Z}_q^2 \mid \Delta u + \Delta v \equiv 0 \pmod q\}$$
   $$\ker(\Delta_{\text{diff}}) = \{(\Delta u, \Delta v) \in \mathbb{Z}_q^2 \mid \Delta u - \Delta v \equiv 0 \pmod q\}$$
3. **Simultaneous Intersection:**
   $$\ker(\Delta_{\text{sum}}) \cap \ker(\Delta_{\text{diff}}) = \{(\Delta u, \Delta v) \in \mathbb{Z}_q^2 \mid \Delta u + \Delta v \equiv 0 \text{ and } \Delta u - \Delta v \equiv 0 \pmod q\}$$
   Adding the two congruences:
   $$2\Delta u \equiv 0 \pmod q \implies \Delta u \equiv 0 \pmod q \quad (\text{since } \gcd(2, 3329) = 1)$$
   Substituting back:
   $$\Delta v \equiv 0 \pmod q$$
   **Theorem 1 (Single-Stage Completeness):** The joint evaluation of sum and difference invariants possesses a trivial kernel:
   $$\ker(\Delta_{\text{sum}}) \cap \ker(\Delta_{\text{diff}}) = \{(0, 0)\} \subset \mathbb{Z}_q^2$$
   *Consequence:* No single-fault perturbation in butterfly output registers can escape detection.

### 4.2 Two-Tier Cryptographic Recovery Probability
Let $P_{\text{SEU}}$ denote the probability that an SEU occurs during the execution of a decapsulation operation ($9{,}856$ butterflies). The decapsulation outcome probability decomposes as:
1. **Tier 1 (Autonomous Recovery):**
   $$P_{\text{Recovered}} = P_{\text{SEU}} \cdot P(\text{transient}) \cdot R_{\text{rec}}$$
   where $R_{\text{rec}} = 1.00$ for all single-cycle transient disturbances within the covered fault domain.
2. **Tier 2 (Safe Implicit Rejection):**
   $$P_{\text{SafeReject}} = P_{\text{SEU}} \cdot [1 - P(\text{transient})] + (1 - P_{\text{SEU}}) \cdot P(\text{ciphertext corrupted})$$
   Under FIPS 203 Section 7.3, failed recovery or tampered ciphertext triggers $K_{\text{rej}} = \text{SHAKE256}(z \parallel c)$.

---

## 5. Security-Constrained Optimization Problem

### 5.1 Objective Function: Effective Authenticated Goodput
The goal of the Adaptive Resilience Controller is to maximize the **Effective Authenticated Goodput** ($\mathcal{G}$), defined as the rate of successfully authenticated, uncorrupted application payload bits delivered per second:

$$\max_{\mathbf{a} \in \mathcal{A}} \quad \mathcal{G}(\mathbf{a}) = \frac{\mathbb{E}[\text{PayloadBits Delivered and Authenticated}]}{\mathbb{E}[\text{Total Transmission Latency}]}$$

where the action vector $\mathbf{a} = [R, D, \alpha] \in \mathcal{A}$ selects:
- Code rate $R = K/N \in \{0.50, 0.75, 0.90\}$.
- Interleaving depth $D \in \{1, 4, 16, 32\}$.
- Retransmission policy $\alpha \in \{\text{Immediate SNACK}, \text{Deferred Batch}\}$.

### 5.2 Strict Separation of Hard Security Constraints
To prevent performance optimizations from ever compromising system security, security criteria are formulated as **inviolable mathematical constraints**, strictly excluded from the objective function:

$$\begin{aligned}
\max_{\mathbf{a} \in \mathcal{A}} \quad & \mathcal{G}(\mathbf{a}) \\
\text{subject to:} \quad & \mathbf{C_1}: \quad P_{\text{SDC}}(\mathbf{a}) = 0 \quad \text{(Zero Silent Data Corruption)} \\
& \mathbf{C_2}: \quad P_{\text{Leakage}}(\mathbf{a}) = 0 \quad \text{(Zero Unauthenticated Plaintext Leakage)} \\
& \mathbf{C_3}: \quad \text{SecParam}(\mathbf{a}) \ge 128 \text{ bits post-quantum} \quad (\text{ML-KEM-768 invariant}) \\
& \mathbf{C_4}: \quad \mathcal{L}_{\text{p99}}(\mathbf{a}) \le \mathcal{L}_{\max} \quad \text{(Tail Latency Constraint)} \\
& \mathbf{C_5}: \quad \mathcal{B}_{\text{buffer}}(\mathbf{a}) \le \mathcal{B}_{\max} \quad \text{(Memory Buffer Capacity Constraint)}
\end{aligned}$$

*Mathematical Principle:* If any action $\mathbf{a}$ violates $\mathbf{C_1}, \mathbf{C_2}$, or $\mathbf{C_3}$, its feasible set is empty ($\mathcal{A}_{\text{feasible}} = \emptyset$), regardless of how much goodput $\mathcal{G}(\mathbf{a})$ it would produce.

---

## 6. Formal Metrics & Statistical Evaluation Framework

### 6.1 Four-Tier Outcome Metric Taxonomy

Every trial $i \in \{1, \dots, N_{\text{trials}}\}$ produces an indicator vector $\mathbf{Y}_i = [Y_{i,1}, Y_{i,2}, Y_{i,3}, Y_{i,4}]$ with $\sum_{k=1}^4 Y_{i,k} = 1$:

1. **Authenticated Delivery ($P_{\text{auth}}$):**
   $$P_{\text{auth}} = \frac{1}{N_{\text{trials}}} \sum_{i=1}^{N_{\text{trials}}} \mathbb{I}(\text{Payload Decrypted} \land \text{AEAD Valid} \land \text{Seq Valid})$$
2. **Safe Rejection ($P_{\text{safe}}$):**
   $$P_{\text{safe}} = \frac{1}{N_{\text{trials}}} \sum_{i=1}^{N_{\text{trials}}} \mathbb{I}(\text{Corrupted/Replayed} \land \text{Payload Discarded} \land K == K_{\text{rej}})$$
3. **Silent Data Corruption ($P_{\text{SDC}}$):**
   $$P_{\text{SDC}} = \frac{1}{N_{\text{trials}}} \sum_{i=1}^{N_{\text{trials}}} \mathbb{I}(\text{Corrupted Payload Accepted} \lor \text{AEAD Tag Falsely Verified})$$
4. **Cryptographic Security Failure ($P_{\text{sec}}$):**
   $$P_{\text{sec}} = \frac{1}{N_{\text{trials}}} \sum_{i=1}^{N_{\text{trials}}} \mathbb{I}(\text{Plaintext Leaked Without Tag} \lor \text{Private Key Compromised})$$

### 6.2 Statistical Confidence Intervals
For small or zero empirical event counts (e.g., $P_{\text{SDC}} = 0$), standard normal approximations fail. The framework utilizes **Clopper-Pearson exact binomial confidence intervals** and **Wilson score intervals**:
$$\hat{p} \pm z_{1-\alpha/2} \sqrt{\frac{\hat{p}(1-\hat{p})}{N} + \frac{z_{1-\alpha/2}^2}{4N^2}}$$
For $N = 1,400$ trials with $k = 0$ observed events, the 95% one-sided upper confidence bound is:
$$p_{\text{upper}} = 1 - (1 - 0.95)^{1/1400} \approx 0.00213 \quad (0.21\%)$$
proving with 95% mathematical confidence that the true SDC rate is bounded below $0.22\%$.
