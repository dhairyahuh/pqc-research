# ASTRA-Sec: Research Gap Analysis & Problem Formulation

**Auditors:** Senior Academic Research Team  
**Investigated Research Gap:** *"Cross-layer fault-aware security continuity for post-quantum command delivery over disruption-tolerant satellite networks."*  
**Evaluation Standard:** Independent, sceptical critique of novelty vs. mere technological aggregation.

---

## 1. The Core Scientific Question

Does the integration of Post-Quantum Cryptography (PQC), Delay-Tolerant Networking (DTN), and arithmetic fault resilience constitute a **genuine, defensible research contribution**, or is it simply an engineering assembly of pre-existing standards?

### Sceptical Baseline Assessment:
- Integrating ML-KEM-768 with AES-256-GCM is standard envelope encryption (e.g., NIST SP 800-56C / RFC 9180 HPKE).
- Placing an encrypted envelope inside a BPv7 bundle payload block is standard protocol layering.
- Checking $r \equiv t\zeta \pmod q$ during an NTT butterfly is an established algebraic relation (Cooley-Tukey property).
- Storing bundles in an SQLite database with WAL mode is standard software engineering.

**Therefore, merely combining these four off-the-shelf concepts does NOT constitute a publishable scientific novelty.**

---

## 2. Where the True Research Gap Lies: The Unresolved Cross-Layer Boundary

The genuine, unaddressed research gap emerges when examining the **state-machine interdependencies and failure cascades across physical, cryptographic, and network boundaries**:

```
 [Physical Layer]           [Cryptographic Layer]              [Network / Transport Layer]
 Cosmic Ray / SEU   ───>   NTT Invariant Failure (L4)  ───>  DTN Store-Carry-Forward (L5)
                             │                                 │
                             ├── Transient: Rollback (K<=2)    ├── WAITING_CONTACT (Link Down)
                             │                              │
                             └── Persistent: Fail-Stop (L4)  ──┴──> Crash / Reboot Recovery (L6)
                                       │                                 │
                                       ▼                                 ▼
                              Implicit Rejection           Persistent Anti-Replay Filter
                                       │                                 │
                                       └───────────────┬─────────────────┘
                                                       │
                                                       ▼
                                      Command Acceptance or Rejection?
                                                       │
                                                       ▼
                                          Cryptographic ACK to Ground?
```

### The 5 Cross-Layer Failure Dilemmas Unaddressed in Prior Art:

#### Dilemma 1: Cryptographic Fault vs. Network Retransmission in High-Delay Topologies
- **In Terrestrial TCP/IP:** If an endpoint experiences a decapsulation error or silent corruption, the TCP connection drops, and the client retransmits within milliseconds.
- **In Space DTN Networks:** The round-trip light time (RTT) between ground stations and deep-space or occulted LEO satellites spans minutes to hours. If a single transient SEU causes decapsulation failure, naively rejecting the bundle forces a multi-hour retransmission request over constrained uplink channels.
- **The Research Void:** How can a spacecraft flight computer distinguish a **transient hardware upset** (which can be safely healed locally via in-place register rollback) from a **persistent silicon failure or an active adversarial tampering attempt**, without exposing the host to Silent Data Corruption (SDC) or timing side-channels?

#### Dilemma 2: The Replay Dilemma across Endpoint Crashes in Disrupted Networks
- When an authenticated command is received, decapsulated, and executed, an acknowledgment (ACK) must be returned over the DTN return path.
- If the spacecraft reboots immediately following command acceptance (e.g., due to a power brownout or latch-up recovery), what happens if the return contact window was closed and the ACK was never transmitted?
- If the ground station times out and re-sends the command across an alternate relay, the spacecraft receives the identical command upon reboot.
- **The Research Void:** Traditional DTN protocols rely on ephemeral memory caches for duplicate detection. In the absence of a crash-consistent, non-volatile anti-replay state machine bound atomically to command execution, a reboot either allows duplicate command execution (potentially catastrophic for spacecraft thruster firings) or permanently deadlocks command queues.

#### Dilemma 3: In-Flight Key Transition and Authorization Expiry
- A command bundle may be queued in an intermediate satellite relay for 12 hours waiting for an orbital contact window to open.
- During transit, the ground station may rotate its signing keys, or the satellite's trust store may receive a revocation update.
- **The Research Void:** Standard PKI assumes instant online revocation (OCSP/CRL). SDLS assumes synchronous link updates. How does an endpoint evaluate a bundle that was cryptographically valid when dispatched into the DTN queue, but whose sender key expired or was revoked while the bundle was stored in an intermediate satellite spool?

#### Dilemma 4: Bounded Rollback vs. Side-Channel Invariance
- If an implementation retries an NTT butterfly upon detecting a fault, does the variable execution latency create a timing side-channel that leaks secret key Hamming weights?
- **The Research Void:** Proving that localized snapshot rollback with a fixed upper bound ($K \le 2$) preserves constant-time properties while achieving complete SDC containment under flight constraints.

---

## 3. Precise Research Problem Formulation

> **Problem Statement:**  
> In disruption-tolerant satellite networks, radiation-induced physical execution faults during post-quantum key decapsulation and endpoint crashes across multi-hour contact disruptions lead to a severe operational dilemma: either high-overhead end-to-end retransmissions and command loss, or catastrophic Silent Data Corruption (SDC) and replay vulnerabilities. Existing PQC implementations assume fault-free processors, while existing space DTN transports assume error-free cryptographic endpoints.

### Conclusion of Gap Analysis:
The intersection of **fault-resilient post-quantum cryptographic execution (L4) and crash-consistent disruption-tolerant store-and-forward transport (L5/L6)** is a **genuine, defensible, and high-impact scientific research gap**.
