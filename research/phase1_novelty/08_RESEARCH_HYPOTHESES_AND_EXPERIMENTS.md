# Phase 1 — Document 08: Research Hypotheses and Experimental Methodology

**Document ID:** `ASTRA-SEC-PH1-DOC-08`  
**Research Directorate:** Multidisciplinary Academic Evaluation Team  
**Date:** November 2026  
**Standards Compliance:** Falsifiable Hypotheses, Rigorous Sample Sizing, Control Baselines  

---

## 1. Primary and Secondary Research Hypotheses

### Primary Hypothesis ($H_1$)
> **Hypothesis $H_1$:** A cross-layer fault-aware security state machine that coordinates sub-word NTT butterfly invariant monitoring with DTN persistent custody transfer reduces telecommand message loss under cosmic SEU flux by at least $40\%$ compared to uncoordinated DTN-PQC architectures, while maintaining a decapsulation latency overhead under $+3.0\%$ over unmonitored LibOQS.

### Secondary Hypotheses
- **$H_{2a}$ (Fault Containment):** Interleaving sub-word invariant checking with localized stack rollback ($K \le 2$) achieves $\ge 99.0\%$ single-bit SEU detection coverage with $0.00\%$ Silent Data Corruption (SDC).
- **$H_{2b}$ (Crash-Consistent Anti-Replay):** Persisting anti-replay sequence state synchronously to SQLite WAL before application dispatch achieves zero duplicate command executions across arbitrary process power-cycles.
- **$H_{2c}$ (Relay Opacity):** Intermediate store-and-forward satellite relays route bundles with zero exposure of application plaintext, maintaining confidentiality even when intermediate relays are actively malicious.

---

## 2. Experimental Comparison Groups (Baselines)

To ensure fair and rigorous comparative evaluation, all experiments benchmark the proposed architecture against three distinct baselines:

| Group ID | Experimental Configuration Name | Description & Architectural Components | Purpose in Evaluation |
| :--- | :--- | :--- | :--- |
| **Group A** | **Unprotected PQC + DTN Baseline** | Standard ML-KEM-768 (LibOQS) + BPv7 DTN. Zero internal fault monitoring. | Quantifies system vulnerability to SEUs and baseline latency ($35.44\ \mu\text{s}$). |
| **Group B** | **Dual Modular Redundancy (DMR) Baseline** | Standard ML-KEM-768 executed twice sequentially with output comparison. | Evaluates conventional software fault-tolerance (+101.49% overhead). |
| **Group C** | **Monitored PQC without Cross-Layer State** | ASTRA-Sec Layer 4 C monitor enabled, but operating in isolation from DTN transport. | Isolates the exact benefit of cross-layer state coordination vs siloed monitoring. |
| **Group D** | **ASTRA-Sec Proposed Architecture** | Full cross-layer state machine coordinating Layer 4 rollback with Layer 5/6 DTN custody. | Evaluates proposed integrated system performance and resilience. |

---

## 3. Sample Size Determination and Statistical Methodology

### 3.1 Why 38 Deterministic Scenarios Are Insufficient
In Phase 16, 38 deterministic unit/integration scenarios were executed to verify protocol functionality. While sufficient for functional regression testing, **38 trials do not provide statistical power for peer-reviewed academic claims**.

### 3.2 Statistical Power Sizing for Fault Injection
- To measure a fault detection coverage of $P = 99.4\%$ with a margin of error $E = 0.5\%$ at a $99\%$ confidence interval ($Z = 2.576$):
  $$N = \frac{Z^2 \cdot P(1 - P)}{E^2} = \frac{(2.576)^2 \cdot 0.994 \cdot (0.006)}{(0.005)^2} \approx \frac{6.6358 \cdot 0.005964}{0.000025} \approx 1,583\ \text{trials}$$
- Therefore, the formal experimental campaign mandates **a minimum of $3,000$ randomized fault injection trials per campaign** (totaling $\ge 15,000$ executions across Groups A–D).

---

## 4. Detailed Specification of the 20 Evaluation Scenarios

Each scenario defines independent variables, dependent variables, controls, expected outcomes, and failure criteria:

```
+----------------------------------------------------------------------------------------------------+
| SCENARIO MATRIX OVERVIEW                                                                           |
| S01-S05: Cryptographic Arithmetic & Invariant Faults (Single-bit, Persistent, Checker, Rollback)  |
| S06-S10: Network Disruption & Contact Scheduling (Outage, Disconnection, Reordering, Duplication)  |
| S11-S15: Crash Recovery & Anti-Replay Consistency (Relay Crash, Dest Crash, WAL Rollback)          |
| S16-S20: Cross-Layer & Adversarial Stress (Simultaneous Outage + SEU, Stale Epoch, Lost ACK)     |
+----------------------------------------------------------------------------------------------------+
```

### Table 1: Comprehensive Scenario Specifications

| Scenario ID & Name | Independent Variable | Dependent Variables | Control Group | Expected Result | Falsification / Failure Condition |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **S01: Normal Clean Traversal** | Payload size (64 B to 64 KB) | E2E latency, CPU cycles | Group A | Clean delivery, latency $< 2.0\ \text{ms}$ in-memory | Any delivery failure or latency spike |
| **S02: Single-Bit Transient SEU** | Bit position $b \in [0, 15]$ in NTT coeff | Detection rate, recovery latency | Group A vs D | 99.4% detected; recovered in $\le 2$ passes | Undetected corruption (SDC) $> 0.1\%$ |
| **S03: Persistent Stuck-Bit Fault** | Stuck bit in arithmetic register | Fail-stop suppression rate | Group A vs D | 100% fail-stop escalation; zero SDC | Corrupted plaintext delivered to L1 |
| **S04: Twiddle Table Bit Flip** | Bit flip in `zetas.inc` ROM array | Invariant catch rate | Group B vs D | Invariant catches corruption immediately | Output matches faulted transform |
| **S05: Fault During Invariant Eval** | Fault injected into checking logic | False positive / negative rate | Group C vs D | Fails safe (implicit rejection); no SDC | Corrupted secret key accepted |
| **S06: Temporary Link Outage** | Link down duration (0.5s to 5s) | Spool occupancy, delivery delay | Group A vs D | Bundle spooled in WAL; delivered upon link up | Bundle lost or discarded during outage |
| **S07: Extended Disconnection** | Outage duration exceeding TTL | Purge correctness, status telemetry | Group C vs D | Bundle purged cleanly; status = `EXPIRED` | Zombie bundle forwarded post-TTL |
| **S08: Message Reordering** | Injected jitter / shuffle permutation | Anti-replay admission rate | Group A vs D | Reordered bundles within window accepted | Valid reordered bundles dropped |
| **S09: Multipath Duplicate Delivery**| Redundant bundle injection count | Deduplication drop rate | Group A vs D | Redundant copies dropped; exactly-once exec | Duplicate command executed twice |
| **S10: High-Rate Burst Traffic** | Transmission rate (10 to 500 msg/s) | Queue latency, buffer drop rate | Group C vs D | WAL throughput scales linearly up to I/O limit | Database deadlock or silent drop |
| **S11: Relay Crash During Transit** | `SIGKILL` injected mid-forwarding | Spool recovery rate upon reboot | Group C vs D | Relay reloads WAL; resumes forwarding | In-flight bundle permanently lost |
| **S12: Destination Crash Pre-Commit**| `SIGKILL` before WAL transaction | Anti-replay rollback consistency | Group A vs D | Command uncommitted; re-attempt admitted | Partial state leaves replay lock |
| **S13: Destination Crash Post-Commit**| `SIGKILL` after WAL transaction | Duplicate execution rate | Group A vs D | Command marked executed; replay rejected | Command re-executes upon reboot |
| **S14: Replay After Destination Reboot**| Re-injecting old bundle post-reboot| Replay detection rate | Group A vs D | 100% replay rejection; counter preserved | Replay accepted after power-cycle |
| **S15: Corrupted Persistent Spool** | Bit flip injected into SQLite file | DB corruption recovery behavior | Group C vs D | WAL checksum catches error; alerts FDIR | Corrupted record parsed as valid |
| **S16: Key Rotation Mid-Transit** | Epoch advance while bundle spooled | Re-key negotiation success rate | Group C vs D | Mismatch caught; triggers secure re-keying | Old key decrypts or bundle dropped |
| **S17: Authorization Revocation** | Revoking sender policy in transit | Command rejection rate at GSB | Group A vs D | Status = `REVOKED`; command rejected | Revoked ground station command runs |
| **S18: Lost Acknowledgement (ACK)** | ACK packet dropped by channel | Sender retry / duplicate behavior | Group C vs D | Sender retransmits; GSB returns cached ACK | Destination re-executes command |
| **S19: Corrupted ML-DSA-65 ACK** | Bit flip in 3,309 B signature | Ground Station Verifier response | Group A vs D | ACK rejected; raises `SignatureError` | Unauthenticated ACK accepted |
| **S20: Simultaneous SEU + Outage** | SEU in NTT + simultaneous link drop | Cross-layer state coherence | Group C vs D | Rollback succeeds in spool; delivered on link | Cryptographic state desynchronizes |

---

## 5. Randomization and Reproducibility Protocol

1. **Deterministic Random Seeds:**
   - All stochastic fault injections and channel drops derive from cryptographic PRNGs seeded by fixed master seeds:
     $$\text{Seed}_i = \text{SHA256}(\text{"ASTRA-SEC-EXP-CAMPAIGN-2026"} \parallel \text{TrialIndex})$$
2. **Raw Data Archival:**
   - Every single trial generates an immutable JSON-Lines record containing: trial UUID, timestamp, seed, injected bit mask, execution cycles, CPU memory rss, intermediate SHA-256 digests, and return code.
3. **Statistical Reporting:**
   - All latency metrics reported with Mean, Standard Deviation ($\sigma$), Median ($P_{50}$), $95^{\text{th}}$ percentile ($P_{95}$), and $99^{\text{th}}$ percentile ($P_{99}$). Confidence intervals computed at $99\%$ confidence level ($p < 0.01$).

