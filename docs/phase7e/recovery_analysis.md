# Recovery Analysis: Early-Stage NTT Fault Containment and Restoration

## 1. Disaggregating Recovery from Safe Rejection

In Phase 7D, we identified that reporting "100% resilience" masked a fundamental limitation: transient arithmetic faults injected into NTT Layers 1 through 6 were **safely rejected** ($K_{\text{rej}}$ emitted via implicit rejection) but **never recovered** to the authentic shared secret $K$. Recovery was restricted strictly to Layer 7 ($14.0\%$ across all transform stages).

### Mathematical Definition of Operational Outcomes:
1. **Successful Recovery ($R_R$):** The system detects the physical disturbance, triggers autonomous re-execution, and successfully restores the authentic cryptographic shared secret $K$.
   $$\text{Output} = K, \quad \text{Token} = \text{RESILIENCE\_RETRY\_TOKEN}$$
2. **Safe Rejection ($R_S$):** The system cannot recover the authentic state (or recognizes an unrecoverable fault/bad input), blocks candidate key leakage, and safely outputs the pseudorandom rejection key $K_{\text{rej}}$ or zeroized buffer.
   $$\text{Output} \in \{K_{\text{rej}}, \mathbf{0}^{32}\}, \quad \text{Token} \in \{\text{RESILIENCE\_REJECT\_TOKEN}, \text{RESILIENCE\_FAULT\_TOKEN}\}$$
3. **Undetected Cryptographic Corruption ($R_U$):** The system fails to detect the anomaly and releases a corrupted or mutated candidate key $K_{\text{mutated}}$.
   $$\text{Output} = K_{\text{mutated}} \neq K, \quad \text{Token} = \text{RESILIENCE\_OK\_TOKEN} \quad \mathbf{[UNACCEPTABLE]}$$

---

## 2. Predicted vs Observed Recovery Across Architectures

We evaluate transient fault recovery rates across all 7 NTT layers ($N=150$ trials per layer):

| NTT Injection Layer | Phase 7D Baseline | Config B (Layer 1) | Config C (Layer 4) | Config D (L1+L4+L7) | Config E (All Layers 1..7) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Layer 1 ($len=128$)** | 0.0% (Safe Rej) | **100.0% (Recovered)** | 0.0% (Safe Rej) | **100.0% (Recovered)** | **100.0% (Recovered)** |
| **Layer 2 ($len=64$)**  | 0.0% (Safe Rej) | 0.0% (Safe Rej) | 0.0% (Safe Rej) | 0.0% (Safe Rej) | **100.0% (Recovered)** |
| **Layer 3 ($len=32$)**  | 0.0% (Safe Rej) | 0.0% (Safe Rej) | 0.0% (Safe Rej) | 0.0% (Safe Rej) | **100.0% (Recovered)** |
| **Layer 4 ($len=16$)**  | 0.0% (Safe Rej) | 0.0% (Safe Rej) | **100.0% (Recovered)** | **100.0% (Recovered)** | **100.0% (Recovered)** |
| **Layer 5 ($len=8$)**   | 0.0% (Safe Rej) | 0.0% (Safe Rej) | 0.0% (Safe Rej) | 0.0% (Safe Rej) | **100.0% (Recovered)** |
| **Layer 6 ($len=4$)**   | 0.0% (Safe Rej) | 0.0% (Safe Rej) | 0.0% (Safe Rej) | 0.0% (Safe Rej) | **100.0% (Recovered)** |
| **Layer 7 ($len=2$)**   | **100.0% (Recovered)** | **100.0% (Recovered)** | **100.0% (Recovered)** | **100.0% (Recovered)** | **100.0% (Recovered)** |
| **Overall NTT Recovery**| **14.0%** | **28.6%** | **28.6%** | **42.9%** | **100.0%** |
| **Safe Rejection Rate** | **86.0%** | **71.4%** | **71.4%** | **57.1%** | **0.0% (Transient)** |
| **Undetected Corrupt**  | **0.0%** | **0.0%** | **0.0%** | **0.0%** | **0.0%** |

### Critical Recovery Insights:
1. **Stepwise Recovery Elevation:** Each monitored layer increases transient recovery by exactly $\frac{1}{7} \approx 14.3\%$.
2. **Config E Achieves 100% Transient Recovery:** When all 7 layers are protected via the intra-butterfly invariant, **100.0% of transient arithmetic faults across all layers are detected as physical faults and autonomously recovered**.
3. **Zero Compromise on Containment:** In all configurations, undetected corrupted key release remains strictly **0.0%**. Even unmonitored layers fall back gracefully to safe implicit rejection via the FO check.
4. **Persistent Faults Remain Non-Recoverable:** For persistent stuck-at faults (Class 8), retry fails 100% of the time, and the system correctly safe-aborts ($R_R = 0.0\%, R_S = 100.0\%$).
