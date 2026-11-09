# Phase 1 — Document 07: Formal Research System Model and Security Properties

**Document ID:** `ASTRA-SEC-PH1-DOC-07`  
**Research Directorate:** Multidisciplinary Academic Evaluation Team  
**Date:** November 2026  
**Formal Framework:** Rigorous Distributed System & Cryptographic Protocol Model  

---

## 1. System and Network Model

### 1.1 Structural Network Topology
The system $\mathcal{N} = (\mathcal{V}, \mathcal{E}, \mathcal{W})$ comprises a 4-node store-and-forward delay-tolerant space network:
- **Node Set:** $\mathcal{V} = \{\text{GSA}, \text{SAT}_1, \text{SAT}_2, \text{GSB}\}$
  - $\text{GSA}$ (Ground Station A): Dispatching command authority.
  - $\text{SAT}_1, \text{SAT}_2$: Intermediate LEO satellite store-and-forward relays.
  - $\text{GSB}$ (Ground Station B / Spacecraft Bus): Destination executing payload commands and emitting telemetry.
- **Link Topology:** $\mathcal{E}(t) \subseteq \mathcal{V} \times \mathcal{V}$ is a time-varying directed contact graph:
  $$\mathcal{E}(t) = \{(\text{GSA}, \text{SAT}_1), (\text{SAT}_1, \text{SAT}_2), (\text{SAT}_2, \text{GSB}), (\text{GSB}, \text{SAT}_2), (\text{SAT}_2, \text{SAT}_1), (\text{SAT}_1, \text{GSA})\}$$

### 1.2 Intermittent Contact Model ($\mathcal{W}$)
- Links exist only during designated orbital contact windows:
  $$W_{u,v} = \{[t_{\text{start}}^{(i)}, t_{\text{end}}^{(i)}] \mid i \in \mathbb{N}\}$$
- When $t \notin W_{u,v}$, link state is $\text{DISRUPTED}$; bundles are held in persistent non-volatile storage ($\mathcal{S}_v$).
- One-way transmission delay $\tau_{\text{prop}} \in [10\ \text{ms}, 180\ \text{s}]$ depending on orbital geometry.
- Bundles are subject to arbitrary reordering, multi-path duplication, and temporary packet loss.

### 1.3 Persistent Storage Model ($\mathcal{S}_v$)
- Each node $v \in \mathcal{V}$ maintains an ACID-compliant Write-Ahead Logged (WAL) persistent store $\mathcal{S}_v$ with synchronous disk barriers ($f_{\text{sync}}$).
- **Crash Recovery Invariant:** State committed to $\mathcal{S}_v$ survives unannounced process termination (`SIGKILL`, watchdog reset, power-cycling).

---

## 2. Cryptographic Execution Model

### 2.1 Post-Quantum Primitive Definitions
- **Key Encapsulation Mechanism (ML-KEM-768):**
  $$\begin{aligned}
  (pk_{\text{kem}}, sk_{\text{kem}}) &\leftarrow \text{KEM.KeyGen}(1^\lambda) && \text{Key generation in }\mathbb{Z}_q[X]/(X^{256}+1) \\
  (c, K_{\text{shared}}) &\leftarrow \text{KEM.Encaps}(pk_{\text{kem}}) && \text{Encapsulation (1,088 B ciphertext)} \\
  K_{\text{shared}} &\leftarrow \text{KEM.Decaps}(c, sk_{\text{kem}}) && \text{Monitored Decapsulation}
  \end{aligned}$$
- **Digital Signatures (ML-DSA-65):**
  $$\begin{aligned}
  (pk_{\text{dsa}}, sk_{\text{dsa}}) &\leftarrow \text{DSA.KeyGen}(1^\lambda) \\
  \sigma &\leftarrow \text{DSA.Sign}(m, sk_{\text{dsa}}) && \text{Signature generation (3,309 B)} \\
  \{0, 1\} &\leftarrow \text{DSA.Verify}(m, \sigma, pk_{\text{dsa}})
  \end{aligned}$$
- **Authenticated Encryption with Associated Data (AES-256-GCM):**
  $$\begin{aligned}
  (c_{\text{aead}}, \tau) &\leftarrow \text{AEAD.Encrypt}(K, N, P, AAD) \\
  P &\leftarrow \text{AEAD.Decrypt}(K, N, c_{\text{aead}}, \tau, AAD) \quad (\text{or }\bot)
  \end{aligned}$$
- **Canonical AAD Binding:**
  $$AAD = \text{SHA256}(\text{sender\_eid} \parallel \text{recipient\_eid} \parallel \text{envelope\_id} \parallel \text{epoch\_id} \parallel \text{seq\_num})$$

---

## 3. Physical & Software Fault Model

### 3.1 Radiation-Induced Single-Event Upsets (SEUs)
- **Target Subsystem:** Flight computer CPU registers, ALU accumulator, and L1 cache during ML-KEM NTT polynomial multiplication.
- **Fault Types Injected:**
  1. *Transient Single-Bit Flip:* $a[j] \leftarrow a[j] \oplus 2^b$ where $b \in [0, 15]$.
  2. *Persistent Register Fault:* $a[j] \leftarrow a[j] \lor 2^b$ (stuck bit in arithmetic register).
  3. *Twiddle Factor Corruption:* $\zeta_i \leftarrow \zeta_i \oplus 2^b$ (bit flip in twiddle lookup array).
  4. *Memory Buffer Bit Flip:* stack-allocated polynomial coefficient array corruption.
- **Explicit Boundary:** All fault evaluations in this work are conducted via **controlled in-memory bit-flip injection in C execution hooks**. Physical particle accelerator beam testing (heavy-ion or proton irradiation) is outside the scope of this software study.

### 3.2 Recovery & Containment Limits
- Localized rollback retry budget is strictly bounded: $K \le 2$.
- Upon the second failed retry ($K > 2$), the system escalates to fail-stop suppression, executing FIPS 203 Section 7.3 implicit rejection:
  $$K_{\text{shared}} \leftarrow \text{SHAKE256}(s \parallel c)$$
  wiping true shared secrets and returning a deterministic random key.

---

## 4. Adversary Threat Model

### 4.1 Adversarial Capabilities ($\mathcal{A}$)
The adversary $\mathcal{A}$ has full Dolev-Yao capabilities over the RF and DTN communication links, plus physical fault-injection capabilities over orbital relay hardware:
1. **Link Control:** $\mathcal{A}$ can eavesdrop, intercept, alter, delay, replay, or inject arbitrary packets on any link $(\text{GSA}, \text{SAT}_1)$, $(\text{SAT}_1, \text{SAT}_2)$, or $(\text{SAT}_2, \text{GSB})$.
2. **Relay Compromise:** $\mathcal{A}$ can control an intermediate satellite relay ($\text{SAT}_1$ or $\text{SAT}_2$) and attempt to read or modify transit payloads.
3. **Endpoint Power-Cycle:** $\mathcal{A}$ can induce watchdog resets or power-cycles on endpoints to exploit volatile state loss.
4. **Targeted Fault Injection:** $\mathcal{A}$ can inject bit flips during cryptographic transforms via EM fault injection or laser glitching.

### 4.2 Out-of-Scope Assumptions (Boundary Conditions)
- Cryptographic primitives (SHAKE256, AES-256, underlying Ring-LWE lattice hardness) are computationally secure against classical and quantum polynomial-time attacks.
- Endpoint master seed storage in physical secure elements is tamper-resistant.
- Jamming of physical RF spectrum (denial of PHY link) is unpreventable at the protocol layer.

---

## 5. Formal Security and Dependability Properties

We evaluate the system against eight fundamental properties, rigorously separating safety (nothing bad happens) from liveness (good things eventually happen):

### Property 1: No Unauthenticated Command Acceptance (Safety)
$$\forall m, \text{ if } \text{Accept}(\text{GSB}, m) = \text{TRUE} \implies \text{DSA.Verify}(m, \sigma, pk_{\text{GSA}}) = 1 \land \text{Status}(pk_{\text{GSA}}) = \text{AUTHORIZED}$$
*Proof Mechanism:* ML-DSA-65 digital signature bound inside envelope header; invalid signature drops bundle before application dispatch.

### Property 2: No Command Acceptance After Uncertain Cryptographic Verification (Safety)
$$\text{If } \text{DecapsStatus} \in \{\text{ROLLBACK\_EXHAUSTED}, \text{FAIL\_STOP}\} \implies \text{Accept}(\text{GSB}, m) = \bot$$
*Proof Mechanism:* Fail-stop implicit rejection yields pseudo-random shared secret; AEAD decryption fails with `InvalidTag`, preventing corrupt plaintext release.

### Property 3: No Replay Acceptance After Node Restart (Safety)
$$\forall m, \text{ if } \text{Accept}(\text{GSB}, m) \text{ at time } t_1 \implies \forall t_2 > t_1 \text{ (including across crash/reboot)}, \text{Accept}(\text{GSB}, m) = \text{REJECT}$$
*Proof Mechanism:* Anti-replay sliding-window sequence tracking is persisted synchronously to SQLite WAL on disk before command execution.

### Property 4: No Duplicate Command Execution (Safety)
$$\text{ExecutionCount}(m_{\text{cmd}}) \le 1$$
*Proof Mechanism:* At-most-once execution semantics enforced by atomic WAL state transition: $\text{Accepted} \to \text{Committed} \to \text{Executed}$.

### Property 5: No Acknowledgement Before Commit Point (Safety)
$$\forall \text{ACK}(m), \text{Emit}(\text{ACK}(m)) \implies \text{State}(m) \equiv \text{COMMITTED\_IN\_WAL}$$
*Proof Mechanism:* Ground Station B generates the ML-DSA-65 signed ACK only after the SQLite transaction commits to non-volatile storage.

### Property 6: No Acceptance After Authorization Expiry or Revocation (Safety)
$$\text{If } t_{\text{arrival}} > t_{\text{creation}} + \text{TTL} \lor \text{Policy}(\text{sender}) = \text{REVOKED} \implies \text{Accept}(\text{GSB}, m) = \bot$$
*Proof Mechanism:* Explicit TTL validation against UTC synchronized hardware clocks and instant trust store policy revocation.

### Property 7: No Conversion of Fail-Stop into Successful Delivery (Safety)
$$\text{If } \text{MonitorFlag} = \text{FAIL\_STOP} \centernot\implies \text{Status} = \text{DELIVERED}$$
*Proof Mechanism:* Telemetry state machine enforces that a fail-stop suppression transition is terminal and cannot transition to `DELIVERED`.

### Property 8: Relay Plaintext Opacity (Confidentiality)
$$\forall \text{Relay } r \in \{\text{SAT}_1, \text{SAT}_2\}, \quad \mathcal{I}(P; \text{State}_r) = 0$$
*Proof Mechanism:* Mutual information between plaintext $P$ and relay state $\text{State}_r$ is zero. Relays process only Layer 5 BPv7 headers and opaque Layer 2 AES-GCM ciphertexts without access to $sk_{\text{kem}}$.

### Property 9: Bounded Transient Fault Recovery (Liveness)
$$\forall \text{Single-Bit SEU}, \quad t_{\text{recovery}} \le 2 \cdot t_{\text{butterfly}} \implies \text{DecapsStatus} = \text{SUCCESS}$$
*Proof Mechanism:* Localized stack snapshot rollback restores valid coefficients within $K \le 2$ iterations, preventing unnecessary DTN custody drops.
