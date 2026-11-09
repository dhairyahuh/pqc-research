# ASTRA-Sec: Formal System & Threat Model

**Auditors:** Senior Academic Research Team  
**Formalism:** State Machine Specification, Inductive Invariants, and PlusCal/TLA+ Formal Model Draft.

---

## 1. System, Network & Cryptographic Models

### 1.1 System Model
The system consists of a set of logical nodes $\mathcal{N} = \mathcal{G} \cup \mathcal{S}$:
- $\mathcal{G} = \{G_A, G_B\}$: Ground stations operating in secure physical environments with high computational capabilities and reliable power.
- $\mathcal{S} = \{S_1, S_2, \dots, S_n\}$: Spaceborne satellite relays and payload computers operating in Low Earth Orbit (LEO) subject to severe SWaP (Size, Weight, Power) limits, periodic orbital occultation, and ionising radiation.

### 1.2 Network Model (Store-Carry-Forward DTN)
- Communication follows RFC 9171 (Bundle Protocol v7).
- Topologies are intermittently connected: a contact opportunity between node $u$ and node $v$ exists only during scheduled time intervals $[t_{\text{start}}, t_{\text{end}}]$ defined by an orbital contact plan $\mathcal{C}$.
- Channels exhibit high latency ($>100\ \text{ms}$ up to minutes), asymmetric bandwidth, and link blackouts during orbital occultation.
- Messages may be delayed, duplicated, or delivered out-of-order across multi-hop paths.

### 1.3 Cryptographic Model
- **Key Agreement:** NIST FIPS 203 ML-KEM-768 with public keys $pk \in \{0,1\}^{1184 \times 8}$, secret keys $sk \in \{0,1\}^{2400 \times 8}$, and ciphertexts $ct \in \{0,1\}^{1088 \times 8}$.
- **Authentication:** NIST FIPS 204 ML-DSA-65 with public keys $pk_D \in \{0,1\}^{1952 \times 8}$, secret keys $sk_D \in \{0,1\}^{4032 \times 8}$, and signatures $\sigma \in \{0,1\}^{3309 \times 8}$.
- **Symmetric Encryption:** NIST SP 800-38D AES-256-GCM.
- **Key Derivation:** RFC 5869 HKDF-SHA256 bound to canonical AAD context.

---

## 2. Fault & Adversary Models

### 2.1 Fault Model (Physical Radiation Environment)
- **Single-Event Upsets (SEUs):** High-energy cosmic rays or trapped protons induce transient bit-flips in operational arithmetic registers during Number Theoretic Transform (NTT) butterfly loops:
  $$\tilde{a} = a \oplus e, \quad e \in \{0,1\}^{16}, \quad \text{weight}(e) \ge 1$$
- **Persistent Faults:** Latch-up or permanent gate degradation causing stuck-at bit faults in register cells or operational twiddle factor tables.
- **Fault Rate:** Modeled as Poisson arrivals during South Atlantic Anomaly (SAA) passes or solar particle events.

### 2.2 Adversary Model (Dolev-Yao + Cryptographic Bound)
- The network adversary $\mathcal{A}_{\text{net}}$ controls all intermediate communication channels (can eavesdrop, delay, reorder, alter, inject, or replay arbitrary packets).
- $\mathcal{A}_{\text{net}}$ can compromise or seize intermediate satellite relays $S_i$.
- $\mathcal{A}_{\text{net}}$ is computationally bounded against modern cryptography but possesses a Cryptographically Relevant Quantum Computer (CRQC) capable of breaking classical discrete logarithm and factoring problems (Shor's algorithm).
- Physical ground stations $G_A, G_B$ are trusted; their master private keys remain uncompromised.

---

## 3. Node State Machine & Formal Lifecycle

Every destination node maintains a persistent state tuple:
$$\Sigma = \langle \mathcal{T}, \mathcal{R}, \mathcal{P}, \mathcal{K}, \mathcal{E} \rangle$$
- $\mathcal{T}$: Monotonic system clock (seconds UTC).
- $\mathcal{R}$: Persistent anti-replay filter tracking processed envelope IDs and sequence window.
- $\mathcal{P}$: Authorized peer registry mapping EIDs to valid public key identities.
- $\mathcal{K}$: Local post-quantum keypairs.
- $\mathcal{E}$: FDIR execution telemetry counters.

---

## 4. Formal Safety Properties

We define eight mandatory safety properties that must hold across all execution paths:

### Property 1: No Unauthenticated Command Acceptance
$$\forall m, \quad \text{Accept}(m) \implies \text{Verify}_{\text{DSA}}(pk_{\text{src}}, \text{AAD}(m), \sigma_m) = \text{VALID} \land \text{IsAuthorized}(pk_{\text{src}})$$
*Guarantee:* A command is never executed unless its originator is authenticated under a valid ML-DSA-65 public key.

### Property 2: No Acceptance after Failed or Uncertain Decapsulation
$$\forall m, \quad \text{Accept}(m) \implies \text{Decaps}(ct_m, sk) = (ss, \text{SUCCESS}) \land \text{AEAD-Auth}(k, m) = \text{VALID}$$
*Guarantee:* If decapsulation fails or produces a corrupted key, the message payload is suppressed with zero plaintext release.

### Property 3: No Replay Acceptance after Endpoint Restart
$$\forall m, \forall \text{Crash}, \quad \text{Processed}(m) \implies \Box (\text{PostCrash} \implies \neg \text{Accept}(m))$$
*Guarantee:* Replaying an accepted command after node reboot is strictly rejected.

### Property 4: No Duplicate Command Execution
$$\forall m, \quad \text{Count}(\text{Execute}(m)) \le 1$$
*Guarantee:* No command can ever be executed more than once, even across reordered multi-path relays.

### Property 5: No Acknowledgment Before Atomic Commit
$$\forall m, \quad \text{EmitACK}(m) \implies \text{Committed}_{\text{WAL}}(\text{ReplayFilter}, m) = \text{TRUE}$$
*Guarantee:* A signed receipt acknowledgment is never dispatched before the anti-replay record is safely committed to non-volatile disk.

### Property 6: No Silent Authorization Across Key Invalidation
$$\forall m, \quad \text{Time}(m) > \text{Expiry}(pk_{\text{src}}) \lor \text{Revoked}(pk_{\text{src}}) \implies \neg \text{Accept}(m)$$
*Guarantee:* Stale or revoked keys cannot authorize queued commands.

### Property 7: Zero Silent Data Corruption (SDC Suppression)
$$\forall \text{Fault } f, \quad \text{DecapsStatus} = \text{FAULT} \implies \text{OutputKey} = \text{RANDOM\_SEED} \land \text{Plaintext} = \emptyset$$
*Guarantee:* Persistent hardware faults escalate to implicit rejection, preventing corrupted secret keys from leaking.

### Property 8: Zero Intermediate Plaintext Exposure
$$\forall S_i \in \mathcal{S}, \quad \text{State}(S_i) \cap \text{Plaintext}(m) = \emptyset$$
*Guarantee:* Intermediate relays inspect routing only; ciphertext remains end-to-end encrypted under AES-256-GCM.

---

## 5. PlusCal / TLA+ Model Draft

```tla
--------------------------- MODULE AstraSecModel ---------------------------
EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS MaxRollback, MaxSeq

VARIABLES 
    node_state,        \* [status: {IDLE, COMPUTING, RECOVERING, FAIL_STOP}]
    rollback_count,    \* 0..MaxRollback
    replay_filter,     \* Set of accepted sequence numbers
    decaps_key_valid,  \* BOOLEAN
    command_accepted   \* BOOLEAN

TypeInvariant ==
    /\ node_state \in {"IDLE", "COMPUTING", "RECOVERING", "FAIL_STOP"}
    /\ rollback_count \in 0..MaxRollback
    /\ replay_filter \subseteq 1..MaxSeq
    /\ decaps_key_valid \in BOOLEAN
    /\ command_accepted \in BOOLEAN

Safety_NoSDCAfterFailure ==
    (node_state = "FAIL_STOP") => (~command_accepted /\ ~decaps_key_valid)

Safety_NoReplayExecution ==
    \A seq \in replay_filter : ~(node_state = "COMPUTING" /\ seq \in replay_filter /\ command_accepted)
=============================================================================
```
