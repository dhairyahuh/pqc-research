# Cross-Layer Space Communication Protocol Simulation Results

**Auditor:** Skeptical Cryptographic Security Researcher & Space Systems Fault-Tolerance Engineer  
**Simulation Framework:** [`phase2_independent_validation/harness/cross_layer_system_sim.py`](file:///Users/dhairyajain/Desktop/pqc%20research/phase2_independent_validation/harness/cross_layer_system_sim.py)  
**Telemetry Dataset:** [`phase2_independent_validation/cross_layer_simulation_metrics.json`](file:///Users/dhairyajain/Desktop/pqc%20research/phase2_independent_validation/cross_layer_simulation_metrics.json) (2,000 evaluated sessions, 20,000 telecommands)  
**Date:** 2026-10-02  

---

## 1. System Model Specification

```
+---------------------------------------------------------------------------------------+
| GROUND STATION                                                    SPACECRAFT          |
|                                                                                       |
|  [Generate Telecommand]                                           [Public Key pk]     |
|         |                                                                |            |
|  [ML-KEM Encaps(pk)] -----(Uplink Ciphertext ct)-------------> [ML-KEM Decaps(sk)]   |
|         |                                                             |               |
|  (Session Key K_ground)                                       [Fail-Stop Monitor]     |
|         |                                                             |               |
|  [Encrypt Payload]                                            [Valid / Quench K_rej]  |
|  [HMAC-SHA256 Tag] ----(Authenticated Telecommand Packet)-----> [MAC Verification]    |
|         ^                                                             |               |
|         |                                                       [Command Execution]   |
|         +------------------(ARQ Retransmit ACK/NACK)------------------+               |
+---------------------------------------------------------------------------------------+
```

### 1.1 Protocol Pipeline
1. **Cryptographic Key Establishment:** ML-KEM-768 keypair generated on the spacecraft; Ground Station executes encapsulation to derive shared secret $K_{\text{ground}}$ and ciphertext $c$.
2. **Authenticated Transport Framing:** Telecommands are formatted as 18-byte structured frames containing:
   - $4\,\text{B}$ Magic Synchronization Word (`0x53504143` = `SPAC`)
   - $2\,\text{B}$ Monotonic Packet Sequence Counter
   - $1\,\text{B}$ Subsystem Identifier (ADCS, EPS, COMM)
   - $1\,\text{B}$ Command Opcode
   - $8\,\text{B}$ Telecommand Parameters
   - $2\,\text{B}$ CRC-16-CCITT Integrity Checksum
3. **Symmetric Payload Protection:** Keystream derived via $\text{SHA-256}(K \parallel \text{seq})$ with an appended $\text{HMAC-SHA-256}(K, \text{ciphertext} \parallel \text{seq})$ tag.
4. **Endpoint Decapsulation Mode:** Fail-Stop (Variant D). Any computational fault immediately quenches candidate key release and outputs deterministic rejection key $K_{\text{rej}}$.
5. **Transport Recovery:** Stop-and-Wait Automatic Repeat reQuest (ARQ) with bounded retries ($N_{\text{retry}} \le 3$).

### 1.2 Separation of Recovery Responsibilities
- **Recoverable via Transport ARQ:** Transient uplink packet drops, RF channel bit flips (BER), and transient computational SEUs during decapsulation.
- **Requires Cryptographic Session Re-establishment:** Persistent stuck-at memory faults, exhausted ARQ retries, or corruptions in long-term secret key storage ($sk$).

---

## 2. Security and Operational Analysis

### 2.1 Retransmission Safety & Prevention of State Reuse
- **Risk Analyzed:** Does retransmitting after decapsulation failure risk repeating an unsafe cryptographic state transition?
- **Protocol Defense:** Upon detecting an implicit rejection or MAC failure, the ground station generates a **fresh random ephemeral seed** $m_{\text{new}}$ and calls `mlkem_enc` again to produce an independent ciphertext $c_{\text{new}}$ and fresh session key $K_{\text{new}}$. No faulted ciphertext or stale session state is ever reused ($0$ unsafe key reuses observed).

### 2.2 Sequence Windowing, Replay, and Reordering Protection
- The spacecraft receiver enforces a strictly monotonic sequence counter window $[w_{\min}, w_{\max}]$ around the expected sequence counter:
  - Packets with $\text{seq} < w_{\min}$ are rejected as stale replays.
  - Packets with $\text{seq} > w_{\max}$ are rejected as desynchronized framing errors.
  - The HMAC tag authenticates the sequence counter directly, preventing spoofing or reordering.

### 2.3 Long-Interval Link Loss Behavior
- If communication is lost exceeding the maximum retry window, the spacecraft receiver transitions into **Safe Mode**:
  - The unauthenticated session key is wiped from volatile memory.
  - Telecommand execution is locked until a fresh cryptographic handshake is established over the next ground pass.

---

## 3. Empirical Simulation Results ($N = 500$ Sessions per Configuration)

| Metric | Config 1: Clean Baseline | Config 2: Fail-Stop without Transport Recovery | Config 3: Fail-Stop with Transport ARQ | Config 4: Joint Space Radiation SEUs + Channel Errors |
| :--- | :---: | :---: | :---: | :---: |
| **Channel Loss Rate** | $0.0\%$ | $0.0\%$ | $0.0\%$ | **$5.0\%$** |
| **Channel Bit Error Rate (BER)** | $0.0\%$ | $0.0\%$ | $0.0\%$ | **$1.0\%$** |
| **Computational SEU Rate** | $0.0\%$ | **$5.0\%$** | **$5.0\%$** | **$5.0\%$** |
| **Authenticated Message Delivery** | **$100.0\%$** | $94.6\%$ | **$100.0\%$** | **$100.0\%$** |
| **Session Establishment Success** | **$100.0\%$** | $94.6\%$ | **$100.0\%$** | **$100.0\%$** |
| **Resynchronization Recoveries** | $0.0\%$ (N/A) | $0.0\%$ | **$4.6\%$** | **$2.8\%$** |
| **Unsafe Key/State Reuses** | **0** | **0** | **0** | **0** |
| **Incorrect Accepted Messages (SDC)** | **0 (0.0%)** | **0 (0.0%)** | **0 (0.0%)** | **0 (0.0%)** |
| **Safe Failures Quenched** | 0 | 27 | 0 (Recovered via ARQ) | 0 (Recovered via ARQ) |
| **Retransmissions Incurred** | 0 | 0 | 23 | 344 |
| **Goodput Efficiency Ratio** | **$100.0\%$** | $100.0\%$ | **$100.0\%$** | **$93.81\%$** |
| **Mean End-to-End Packet Latency** | $187.50\,\text{ms}$ | $187.50\,\text{ms}$ | $189.80\,\text{ms}$ ($+1.2\%$) | $197.87\,\text{ms}$ ($+5.5\%$) |

---

## 4. Key Comparative Findings

1. **Failure of Isolated Endpoint Recovery (Config 2):**
   When ML-KEM decapsulation operates as fail-stop without transport coordination, every computational SEU terminates the session permanently, dropping packet delivery from $100\%$ down to **$94.6\%$** ($27$ aborted sessions).
2. **Restoration of Availability via Transport ARQ (Config 3):**
   Coordinating the fail-stop quench with transport-level retransmission restores authenticated packet delivery to **$100.0\%$** at an overhead of only $+2.3\,\text{ms}$ ($+1.2\%$) in latency.
3. **Resilience Under Joint Stress (Config 4):**
   Under joint channel degradation (5% packet loss, 1% BER) and space radiation SEUs (5%), the cross-layer architecture achieved **$100.0\%$ message delivery** with **$0.0\%$ Silent Data Corruption**, maintaining **$93.81\%$ goodput efficiency**.
