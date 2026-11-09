# ASTRA-Sec: Recommended Academic Research Direction

**Authors:** Senior Academic Research Team  
**Publication Strategy:** Targeted for IEEE Transactions on Aerospace and Electronic Systems (T-AES) or ACM Conference on Computer and Communications Security (CCS) Space Security Workshop.

---

## 1. Selected Research Contribution Portfolio

### Primary Contribution:
**Software-Level Fault-Resilient ML-KEM-768 with Sub-Word Invariant Monitoring and Localized Register Rollback for Space Flight Processors**

### Supporting Contribution 1:
**Cross-Layer Disruption-Tolerant Cryptographic State Machine Coupling Arithmetic Fault Recovery with RFC 9171 BPv7 Delivery**

### Supporting Contribution 2:
**Crash-Consistent Non-Volatile Anti-Replay Ledger for Asynchronous Disconnected Space Networks**

---

## 2. Research Formulation Blueprint

### 2.1 Recommended Research Title
> **"ASTRA-Sec: A Fault-Resilient Post-Quantum Cryptographic Framework with Disruption-Tolerant Delivery for Space Systems"**

### 2.2 Precise Research Problem
Standard post-quantum cryptographic implementations (NIST FIPS 203 ML-KEM) running on spacecraft commercial flight computers are susceptible to radiation single-event upsets (SEUs) during Number Theoretic Transform (NTT) polynomial multiplication. Existing defenses rely on full duplicate execution (DMR $2\times$), which doubles computational latency (+101%) and energy consumption. Furthermore, in store-and-forward space networks (RFC 9171 DTN), transient execution errors trigger costly multi-hour round-trip retransmissions across disconnected orbital relays.

### 2.3 The Identified Research Gap
Prior research either hardens FPGA butterfly units in hardware (Paul et al., 2026) or studies DTN routing protocols without cryptographic fault awareness (NASA ION). No existing work provides a **pure software-level, constant-time, zero-heap fault-resilient ML-KEM engine that heals transient SEUs in-flight via localized rollback ($K \le 2$) and couples arithmetic health directly to disruption-tolerant delivery states**.

### 2.4 Research Questions
- **RQ1 (Algorithmic Overhead):** Can software-level sub-word NTT butterfly invariant monitoring ($r \equiv t\zeta \pmod q$) achieve $\ge 99\%$ single-event fault coverage with $<5\%$ latency overhead compared to unprotected LibOQS?
- **RQ2 (Disruption Resilience):** Does localized in-place rollback ($K \le 2$) eliminate network-level retransmissions caused by transient decapsulation faults in multi-hop store-and-forward satellite networks?
- **RQ3 (SDC & Side-Channel Containment):** Does the integrated TFIB-Ref dual-reference verification and fail-stop implicit rejection suppression guarantee zero Silent Data Corruption (SDC) without introducing timing side-channels?

### 2.5 Testable Hypotheses
1. *Hypothesis 1:* ASTRA-Sec decapsulation latency overhead is $\le 3.0\%$ over unprotected baseline ($36.25\ \mu\text{s}$ vs $35.44\ \mu\text{s}$), whereas DMR $2\times$ incurs $\ge 100\%$ overhead ($73.04\ \mu\text{s}$).
2. *Hypothesis 2:* Localized rollback recovers $100\%$ of single-event upsets injected into operational twiddle factors and butterfly registers, reducing packet drop to $0.0\%$.
3. *Hypothesis 3:* Persistent twiddle table corruption triggers fail-stop implicit rejection suppression in $100\%$ of trials ($0/500$ SDC events).

### 2.6 Proposed Technical Mechanism
- **Layer 4 (Arithmetic):** C99 inline butterfly monitor computes $r \equiv (a' - b') \cdot 2^{-1} \pmod{3329}$ and verifies against $t \equiv b \cdot \zeta \pmod{3329}$. If mismatched, it restores $(a, b)$ from register snapshot up to $K=2$ times. Strategy 1 TFIB-Ref verifies operational twiddle tables against independent static memory.
- **Layer 2 (Security):** AES-256-GCM AEAD binds canonical AAD (EIDs, sequence numbers, TTL, KEM ciphertext, nonce).
- **Layer 5/6 (DTN & Persistence):** RFC 9171 BPv7 engine with canonical CBOR encoding, RFC 9172 BIB HMAC-SHA256, and SQLite WAL spooling surviving process crashes.

### 2.7 Formal Safety Properties
- $\text{Safety}_1$: Zero unauthenticated command acceptance.
- $\text{Safety}_2$: Zero command acceptance after corrupted decapsulation.
- $\text{Safety}_3$: Zero command replay after endpoint crash or reboot.
- $\text{Safety}_4$: Zero plaintext exposure at intermediate satellite relays.

### 2.8 Experimental Baselines
1. Unprotected ML-KEM-768 (LibOQS 0.16.0 C reference).
2. Dual Modular Redundancy (DMR $2\times$ duplicate execution).
3. Plain BPv7 without cross-layer fault awareness.
4. ASTRA-Sec complete stack.

---

## 3. Anticipated Academic Impact & Venue Target

- **Primary Target:** *IEEE Transactions on Aerospace and Electronic Systems (T-AES)* or *IEEE Transactions on Information Forensics and Security (T-IFS)*.
- **Alternative Target:** *ACM Conference on Computer and Communications Security (CCS) — SpaceSec Workshop*.
- **Core Value Proposition to Reviewers:** A grounded, reproducible, cross-disciplinary paper that solves a real engineering contradiction in aerospace computing: achieving post-quantum security and radiation fault tolerance within real satellite flight computing budgets.
