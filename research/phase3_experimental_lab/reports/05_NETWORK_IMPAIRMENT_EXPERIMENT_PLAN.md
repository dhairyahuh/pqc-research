# ASTRA-Sec Phase 3: Network Impairment Experimentation and Disruption Tolerance

## 1. Space Channel Characteristics & Rationale

Space communication networks encounter extreme propagation delays, high channel noise, orbital occultation, and frequent physical link outages. To evaluate ASTRA-Sec's resilience, the experimental laboratory incorporates a deterministic network impairment engine that intercepts and perturbs bundles in transit across relay nodes.

---

## 2. Impairment Models Implemented

1. **Propagation Delay**: Fixed latency injection simulating satellite link distance ($\tau_d = 50\text{ ms}$, representing medium-Earth orbit relay hops).
2. **Deterministic Jitter**: Normal distribution timing variation ($\sigma_\tau = 5\text{ ms}$) around mean propagation delay.
3. **Random Bundle Loss**: Bernoulli packet loss probability ($P_{loss} = 0.10$), simulating atmospheric attenuation or line-of-sight occultation.
4. **Bundle Duplication**: Duplicate packet injection ($P_{dup} = 0.05$), testing anti-replay suppression.
5. **Out-of-Order Delivery**: Random reordering of queued bundles, verifying sequence window reassembly.
6. **Link Outage**: Complete contact schedule teardown ($T_{out} > 0$), forcing relay spooling into persistent SQLite WAL storage.

---

## 3. Experimental Evaluation: Group G (`EXP-G01-IMPAIRMENT`)

### 3.1. Parameter Configuration
- **Payload Size**: 512 B
- **Total Messages**: 10
- **Base Rate**: 20 msg/sec
- **Injected Delay**: 50.0 ms
- **Injected Jitter**: 5.0 ms
- **Injected Loss Rate**: 10.0% (0.10)
- **Random Seed**: 7007 (fully deterministic)

---

### 3.2. Empirical Results
* **Total Dispatched**: 10
* **Delivered Count**: 9 (90.0%)
* **Dropped in Transit**: 1 (10.0%) — exactly matching the configured Bernoulli loss rate ($P_{loss} = 0.10$).
* **Measured End-to-End Latency**:
  - Median (P50): 67,546.08 $\mu$s (67.55 ms)
  - P95: 77,122.09 $\mu$s (77.12 ms)
  - P99: 78,669.05 $\mu$s (78.67 ms)
  - Mean $\pm$ Std: 68,630.88 $\pm$ 6,935.39 $\mu$s
  - 99% Confidence Interval: [60,873.91, 76,387.85] $\mu$s
* **Resource Utilization**:
  - Mean CPU Utilization: 27.90%
  - Peak RSS Memory: 94.83 MB

---

### 3.3. Scientific Analysis
1. **Latency Decomposition**:
   - Baseline clean latency (Group D) Mean: 15.25 ms.
   - Injected channel delay: 50.0 ms + jitter.
   - Impaired latency (Group G) Mean: 68.63 ms.
   - Theoretical expectation: $15.25\text{ ms} + 50.00\text{ ms} = 65.25\text{ ms}$.
   - Observed difference: $+3.38\text{ ms}$, corresponding closely to the positive jitter component and extra relay buffer queue time.
2. **Channel Integrity**:
   - All 9 delivered messages arrived with intact cryptographic integrity, verified ML-DSA-65 signatures, and zero replay errors.
   - The single dropped bundle was safely dropped by the channel without corrupting subsequent session state or causing deadlock.
