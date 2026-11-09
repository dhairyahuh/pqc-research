# ASTRA-Sec: Research Hypotheses & Falsifiability Criteria

**Auditors:** Senior Academic Research Team  
**Scientific Standard:** Falsifiable, Quantifiable Hypotheses with Statistical Significance Criteria ($p < 0.01$).

---

## 1. Primary Research Hypotheses

### Hypothesis 1: Computational Overhead of Invariant Monitoring vs. DMR
- **Statement:** Mid-transform NTT butterfly invariant monitoring with localized snapshot rollback ($K \le 2$) achieves fault detection coverage statistically indistinguishable from Dual Modular Redundancy (DMR $2\times$) ($>99\%$), while reducing execution latency overhead from $>100\%$ down to $<5\%$ over unprotected reference ML-KEM-768.
- **Null Hypothesis ($H_{0,1}$):** Invariant monitoring incurs latency overhead $\ge 20\%$ or achieves fault coverage $\le 95\%$.
- **Alternative Hypothesis ($H_{1,1}$):** Invariant monitoring incurs latency overhead $< 5\%$ with fault detection coverage $\ge 99.0\%$.
- **Independent Variable:** Protection architecture (Unprotected LibOQS, Monitored Invariant + Rollback, DMR $2\times$).
- **Dependent Variables:** Decapsulation latency ($\mu\text{s}$), CPU cycle count, fault detection coverage (%).
- **Falsification Threshold:** If measured latency overhead exceeds $5.0\%$ or fault coverage drops below $99.0\%$, $H_{1,1}$ is rejected.

---

### Hypothesis 2: Space Network Retransmission Suppression
- **Statement:** Under single-event transient radiation upsets (SEUs) during ML-KEM decapsulation in an intermittently connected space network, localized register rollback ($K=1$) eliminates $100\%$ of network-level bundle retransmissions that would otherwise occur in unmonitored systems.
- **Null Hypothesis ($H_{0,2}$):** In-flight transient faults cause $\ge 1\%$ of bundles to be dropped or retransmitted.
- **Alternative Hypothesis ($H_{1,2}$):** In-flight transient faults cause $0.0\%$ bundle loss and zero uplink retransmission requests across evaluated single-event upset trials.
- **Independent Variable:** Transient bit-flip injection rate (upsets per 1,000 decapsulations).
- **Dependent Variables:** Retransmission request count, bundle delivery success rate (%), end-to-end delivery completion time (s).
- **Falsification Threshold:** If any transient SEU causes a bundle to fail delivery or require retransmission, $H_{1,2}$ is falsified.

---

### Hypothesis 3: Silent Data Corruption (SDC) Suppression Rate
- **Statement:** When subjected to persistent hardware faults (stuck-at bits in operational registers or mutated twiddle factors), fail-stop implicit rejection suppression guarantees that zero uncontained, corrupted shared secrets are ever output to higher protocol layers.
- **Null Hypothesis ($H_{0,3}$):** Persistent hardware faults lead to SDC rate $> 0.001\%$.
- **Alternative Hypothesis ($H_{1,3}$):** Persistent hardware faults achieve an observed SDC rate of $0.000\%$ ($0$ corrupted plaintexts or keys accepted across evaluated campaigns).
- **Independent Variable:** Injected persistent fault location (twiddle table, CT butterfly add/sub registers, accumulator).
- **Dependent Variables:** SDC occurrence count, fail-stop escalation count, AEAD decryption rejection rate.
- **Falsification Threshold:** If a faulted decapsulation returns a key that decrypts ciphertext into corrupted plaintext without raising an error, $H_{1,3}$ is decisively falsified.

---

### Hypothesis 4: BPSec Transport Layer Overhead Bound
- **Statement:** Nesting an end-to-end post-quantum cryptographic envelope (ML-KEM-768 + AES-256-GCM + ML-DSA-65) inside an RFC 9171 BPv7 bundle with RFC 9172 BPSec BIB integrity adds $<5\%$ latency overhead compared to unauthenticated BPv7 transport over multi-hop space links.
- **Null Hypothesis ($H_{0,4}$):** L2 + L5 security layering adds $\ge 15\%$ transmission latency overhead.
- **Alternative Hypothesis ($H_{1,4}$):** L2 + L5 security layering adds $< 5\%$ latency overhead over multi-hop forwarding paths.
- **Independent Variable:** Security configuration (Plain BPv7 vs. BPv7 + L2 Envelope + BPSec BIB).
- **Dependent Variables:** Multi-hop transit latency (ms), bundle wire size (bytes).
- **Falsification Threshold:** Measured multi-hop transit latency overhead $\ge 5.0\%$.

---

### Hypothesis 5: Crash-Consistent Replay Immunity
- **Statement:** Atomic transactional persistence binding the anti-replay ledger to command execution ensures that zero replayed commands are accepted following unexpected node crashes or reboots.
- **Null Hypothesis ($H_{0,5}$):** Replaying previously executed commands following a power-loss crash results in $>0\%$ duplicate execution.
- **Alternative Hypothesis ($H_{1,5}$):** Replaying previously executed commands following a power-loss crash results in exactly $0\%$ duplicate execution ($100\%$ replay rejection).
- **Independent Variable:** Node reboot / crash timing relative to command arrival.
- **Dependent Variables:** Duplicate execution count, replay detection rate (%).
- **Falsification Threshold:** Any successful execution of a duplicate command.
