# ASTRA-Sec: Research Methodology, Hypotheses & Evaluation Metrics

**Permanent Research Title:** *Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems*  
**Document Designation:** Formal Research Methodology & Experimental Framework  
**Date:** November 10, 2026  

---

## 1. Core Research Questions

ASTRA-Sec addresses three fundamental engineering research questions at the intersection of space network communications and post-quantum cybersecurity:

- **RQ1 (Fault Detectability & Containment)**: Can software-level mathematical invariant checks within the Number Theoretic Transform (NTT) of lattice-based algorithms (FIPS 203 ML-KEM-768) reliably detect ionizing radiation bit-flips mid-execution without incurring excessive computational overhead?
- **RQ2 (Transient SEU Recovery)**: Can a localized register snapshot rollback mechanism ($K \le 2$) successfully recover decapsulation fidelity from transient Single-Event Upsets without requiring end-to-end packet re-transmission across disrupted, long-delay space links?
- **RQ3 (Protocol Continuity & Zero Loss)**: How does the integration of post-quantum cryptographic wire envelopes ($5,119\ \text{B}$) with RFC 9171 Delay-Tolerant Networking (DTN) and transactional SQLite WAL queues perform during prolonged inter-satellite link outages and reordering events?

---

## 2. Formal Hypotheses

- **$H_1$ (Invariant Coverage)**: Dual-transform NTT butterfly twiddle invariant checking ($r \equiv t \cdot \zeta \pmod{3329}$) achieves $100\%$ detection of Single-Event Upsets injected into active butterfly coefficient registers and twiddle factors during the decapsulation polynomial multiplication phase.
- **$H_2$ (SDC Suppression)**: By combining localized retry ($K \le 2$) with fail-stop implicit rejection (hashing pseudo-random seed $z$), the rate of Silent Data Corruption (SDC) across $N \ge 1,000$ fault injection trials is reduced to exactly $0.00\%$ ($95\%$ Confidence Interval: $[0.00\%, 0.37\%]$).
- **$H_3$ (Delay-Tolerant Continuity)**: During link disruptions up to $86,400\ \text{seconds}$, persistent transactional custody transfer maintains $100\%$ bundle delivery fidelity without message loss, while anti-replay filters prevent duplicate acceptance of re-transmitted bundles.
- **$H_4$ (Observability Overhead Bound)**: Microsecond-resolution monotonic telemetry collection across all 7 layers introduces less than $1.0\%$ latency overhead relative to the end-to-end space link baseline.

---

## 3. Experimental Design & Independent Variables

### 3.1 Controlled Fault Injection Model
Faults are injected using deterministic C memory-mapped mutators at specific stages of ML-KEM-768 decapsulation:
1. **Target Subsystems**:
   - Stage 1–7 Cooley-Tukey NTT butterfly blocks (Layer 1, Butterfly 0 to Layer 7, Butterfly 127).
   - Invariant twiddle factor arrays ($\zeta$).
   - Base multiplication accumulation registers (`basemul_acc`).
   - Fujisaki-Okamoto (FO) transform constant-time memory comparison predicate (`ct_memcmp`).
2. **Fault Taxonomies**:
   - Single-bit flips (SEU emulation).
   - Multi-bit bursts.
   - Zero-glitch / stuck-at-zero faults.
   - Twiddle relocation table perturbations.

### 3.2 Evaluation Metrics & Definitions

| Metric | Definition | Target Threshold |
| :--- | :--- | :--- |
| **Detection Rate ($P_d$)** | $\frac{N_{\text{detected}}}{N_{\text{faulted}}}$ | $\ge 99.9\%$ |
| **SDC Rate ($P_{\text{sdc}}$)** | Probability of corrupted ciphertext producing valid plaintext | **$0.00\%$ strictly enforced** |
| **Recovery Rate ($P_{\text{rec}}$)**| Transient SEUs successfully recovered via $K=1$ rollback | $\ge 98.0\%$ |
| **Delivery Ratio ($R_{\text{del}}$)**| $\frac{\text{Bundles Delivered}}{\text{Bundles Dispatched}}$ during link disruption | **$100.0\%$ (zero packet loss)**|
| **Instrumentation Overhead**| $\frac{T_{\text{instrumented}} - T_{\text{baseline}}}{T_{\text{baseline}}}$ | **$< 1.0\%$** |
| **Wire Frame Efficiency** | Total PQC envelope size ($5,119\ \text{B}$) vs application payload | Quantified & bounded |

---

## 4. Statistical Validation Protocols

- **Confidence Intervals**: Wilson score intervals for binomial proportions (e.g., detection rates, implicit rejection rates).
- **Sample Size**: Multi-trial empirical campaigns spanning $N=38$ (core pilot matrix), $N=100$ (per-butterfly stress sweeps), and $N=1,000$ (Monte Carlo SEU campaigns).
- **Reproducibility**: All random seeds are fixed and documented in configuration manifests under `research/phase3_experimental_lab/configs/`.
