# Cross-Layer Space Protocol Assumption Review and Sensitivity Audit

**Auditor:** Skeptical Space Systems and Network Protocol Auditor  
**Investigation Focus:** Reassessment of the endpoint state machine, protocol assumptions, and sensitivity findings in `phase3_harness_audit/harness/cross_layer_sensitivity.py` and `cross_layer_sensitivity_results.csv`  

---

## 1. Distinction Between Model-Level Results vs. Implementation-Level Evidence

In evaluating the cross-layer space communication framework, experimental boundaries must be rigorously delineated:

| Component | Implementation Level (Empirical Reality) | Model Level (Simulation Assumption) |
| :--- | :--- | :--- |
| **ML-KEM-768 Decapsulation** | Real C/Python wrapper execution (`oqs_wrapper.MLKEM`) calling actual cryptographic routines. | Injected faults inside the Python wrapper are simulated bit flips, not physical electromagnetic upsets. |
| **Telecommand Framing & HMAC** | Real cryptographic hashing (`hashlib.sha256`) and message authentication (`hmac.new`). | Packet length (18 bytes) and command opcodes are representative model abstractions. |
| **Space Link Physical Channel** | **Simulated purely in Python**. No physical RF hardware, software-defined radio (SDR), or Doppler link was used. | Packet loss ($L$), bit error rate (BER), and propagation delay ($25\,\text{ms}$) are stochastic Bernoulli trials. |
| **Endpoint Hardware State** | **Simulated in Python objects** (`SpacecraftEndpoint` class). | Microcontroller watchdog reboot is modeled as an object re-initialization wiping memory. |

---

## 2. Re-Assessment of Protocol Properties Under Adversarial Stress

Based on the 15 sensitivity sweeps ($N = 50$ sessions per scenario, 10 telecommands per session):

### 2.1 Persistent Computational Faults (Scenario 8)
- **Observed Metric:** Handshake Success = **86.0%**, Delivery Rate = **86.0%**, Retransmissions = **4.2%**.
- **Auditor Evaluation:**
  - In Phase 2, it was assumed that retransmission trivially overcomes computational faults (`# Transient SEU passed`).
  - The Phase 3 sensitivity harness demonstrated that if a computational fault is persistent (e.g., stuck-at register or gate damage from heavy ions), repeated retransmissions of the handshake fail identically.
  - **Boundary Condition:** Transport-layer ARQ can only resolve **transient** computational SEUs. Tolerating persistent hardware faults requires architectural redundancy (dual/triple modular redundancy) or dynamic core migration.

### 2.2 Endpoint Restarts and State Desynchronization (Scenario 10)
- **Observed Metric:** Handshake Success = **100.0%**, Delivery Rate = **72.2%**, Retransmission Overhead = **84.4%**.
- **Auditor Evaluation:**
  - Radiation-induced watchdog reboots wipe volatile SRAM, returning the spacecraft endpoint to `IDLE` and destroying the ephemeral session key $K_{\text{session}}$.
  - Ground station frames encrypted under the old key fail authentication (`AUTH_FAIL`), causing catastrophic packet rejection and unbounded retransmissions.
  - **Boundary Condition:** Monotonic sequence checking and replay rejection are insufficient if the session key is lost. The protocol strictly requires an **authenticated state-resynchronization handshake** triggered upon consecutive authentication rejections.

### 2.3 Lost Acknowledgements and Replay Handling (Scenario 9)
- **Observed Metric:** Handshake Success = **100.0%**, Delivery Rate = **100.0%**, Replays Accepted = **0**, Replays Rejected = **102**.
- **Auditor Evaluation:**
  - When uplink telecommands are successfully decrypted but the downlink ACK is lost, the ground station retransmits the frame, delivering a duplicate.
  - Because the endpoint verifies $seq == S_{\text{expected}}$ and increments $S_{\text{expected}}$ upon acceptance, duplicate packets are strictly rejected (`REPLAY_REJECTED`).
  - **Boundary Condition:** Replay immunity holds provided the sequence counter is strictly monotonic and does not wrap around within a single session lifetime ($< 2^{16}$ frames).

### 2.4 Retry Budget Exhaustion (Scenarios 11 vs. 12 vs. 13)
- Under moderate space channel stress ($L=10\%$, $\text{BER}=2\%$, $\text{SEU}=5\%$):
  - $R = 1 \implies$ Delivery Rate = **91.4%** (8.6% packet loss due to early budget exhaustion).
  - $R = 3 \implies$ Delivery Rate = **99.2%**.
  - $R = 5 \implies$ Delivery Rate = **100.0%**.
- **Auditor Evaluation:**
  - Claims of "100% reliable post-quantum delivery" are strictly conditional on the retry budget $R$. In space links with severe burst noise or long round-trip times (deep space links with RTT $> 10\,\text{s}$), setting high retry budgets severely degrades link goodput.

---

## 3. Threat Model and Boundary Conditions Summary

| Claimed Property | Audit Assessment | Demonstrated Boundary Conditions |
| :--- | :--- | :--- |
| **100% Message Delivery** | **Conditional Model Artifact** | Holds only for transient errors with retry budgets $R \ge 3$. Collapses under persistent faults (86%) or unhandled reboots (72%). |
| **Replay Protection** | **Cryptographically Sound** | Monotonic sequence counters prevent replay acceptance under ACK loss. |
| **Fail-Stop Containment** | **Sound in Architecture, Vulnerable in Timing** | Aborting on error prevents leaking corrupted ciphertexts, but observable execution timing creates an external distinguishing channel. |
| **Cross-Layer Recovery** | **Partially Demonstrated** | Handshake ARQ recovers from transient decapsulation faults, but requires explicit re-handshake triggers after endpoint crash/reboot. |
