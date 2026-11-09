# ASTRA-Sec: Candidate Novel Research Contributions

**Auditors:** Senior Academic Research Team  
**Evaluation Standard:** Sceptical peer-review assessment of 5 distinct candidate contributions across prior art, technical depth, falsifiability, and novelty confidence.

---

## 1. Evaluation of Candidate Contributions

### CANDIDATE A: Cross-Layer Security State Machine
- **Prior Art:** Layered network security models (OSI, TCP/IP, CCSDS); standard state machines for DTN bundle processing (RFC 9171 Section 5).
- **Precise Unresolved Problem:** No existing model formalizes the coupling between low-level arithmetic fault outcomes (transient rollback, persistent implicit rejection) and higher-layer delivery, acknowledgment, and spool management states.
- **Proposed Technical Mechanism:** A formal cross-layer state machine defined across physical SEU events, L4 monitored butterfly invariants ($r \equiv t\zeta \pmod q$), L5 DTN store-and-forward statuses, and L7 forensic verification receipts.
- **What is Genuinely New:** Explicit state transitions mapping physical decapsulation recoveries directly to authenticated acknowledgment receipts, preventing unnecessary DTN retransmissions.
- **Measurable Hypotheses:** Eliminates 100% of network retransmissions caused by transient single-event upsets while incurring $<3\%$ latency overhead.
- **Implementation Difficulty:** **MEDIUM** (State machine requires formal specification and rigorous edge-case unit testing).
- **What Could Disprove It:** If state explosion leads to unresolvable deadlocks under concurrent link outages, or if state transitions leak secret key timing information.
- **Novelty Confidence:** **HIGH** (Unexplored in both PQC and DTN literature).

---

### CANDIDATE B: Fault-Aware DTN Delivery Protocol
- **Prior Art:** RFC 9171 Bundle Protocol v7, RFC 9172 BPSec, NASA/JPL ION-DTN.
- **Precise Unresolved Problem:** When an endpoint encounters an arithmetic fault, standard DTN protocols have no mechanism to signal cryptographic health back to the sender without compromising confidentiality or exposing fault injection vulnerabilities.
- **Proposed Technical Mechanism:** An extension block or structured cryptographic receipt (`MessageAcknowledgment`) that conveys verified execution telemetry (butterfly count, recovery count, fail-stop status) signed under ML-DSA-65.
- **What is Genuinely New:** Forensic ground-station verification of remote spacecraft cryptographic health across multi-hop relays without revealing plaintext or secret keys.
- **Measurable Hypotheses:** Ground stations can verify whether remote decapsulation experienced transient recovery or permanent degradation with zero key exposure.
- **Implementation Difficulty:** **MEDIUM** (Requires extending BPv7 extension blocks or application receipt formats).
- **What Could Disprove It:** If telemetry metadata increases bundle wire overhead beyond allowable TT&C bandwidth limits ($>5\%$).
- **Novelty Confidence:** **MEDIUM-HIGH**.

---

### CANDIDATE C: Crash-Consistent Cryptographic Command Acceptance
- **Prior Art:** Database Write-Ahead Logging (WAL), atomic transactional commit protocols (ACID), SQLite persistent spools.
- **Precise Unresolved Problem:** Endpoint crashes between command decryption and anti-replay state commitment allow duplicate command execution upon reboot if a command is re-sent across alternative space relays.
- **Proposed Technical Mechanism:** A strict two-phase atomic commit protocol binding the update of the persistent anti-replay filter, command payload execution, and signed acknowledgment spooling into an indivisible WAL transaction.
- **What is Genuinely New:** Provable protection against duplicate command execution and replay attacks across unannounced power failures and reboots in space systems.
- **Measurable Hypotheses:** Zero duplicate executions ($0/1000$ crash trials) and zero replay acceptance following reboot.
- **Implementation Difficulty:** **LOW-MEDIUM** (Standard transactional engineering applied to cryptographic state).
- **What Could Disprove It:** If the transactional write bottleneck severely degrades message ingestion throughput.
- **Novelty Confidence:** **MEDIUM** (Strong engineering value, but conceptually derived from database transaction literature).

---

### CANDIDATE D: Key-Transition Safety under Disruption
- **Prior Art:** CCSDS SDLS Extended Procedures (SDLS-EP), classical Double Ratchet (Signal protocol), SDLS-DR (Ledin et al., 2026).
- **Precise Unresolved Problem:** When bundles are delayed in intermediate satellite spools for hours or days, ground station key rotations or authorization revocations can invalidate queued commands or silently re-authorize stale commands upon arrival.
- **Proposed Technical Mechanism:** An epoch-bound authorization policy associating bundles with monotonic key generation epochs, evaluated against historical trust states upon delivery.
- **What is Genuinely New:** Post-quantum forward secrecy and asynchronous revocation verification for multi-hop disruption-tolerant networks.
- **Measurable Hypotheses:** Expired and revoked commands are 100% rejected even when arriving out-of-order after multi-day delays.
- **Implementation Difficulty:** **HIGH** (Complex epoch synchronization across disconnected nodes).
- **What Could Disprove It:** If clock drift between orbital nodes desynchronizes epoch boundaries.
- **Novelty Confidence:** **MEDIUM-HIGH**.

---

### CANDIDATE E: Independent Fault-Checking for PQC Endpoints
- **Prior Art:** Ravi et al. (CHES 2021), Paul et al. (IEEE TCSI 2026), REMO modular offset checks.
- **Precise Unresolved Problem:** Software PQC implementations on flight processors either have no protection or rely on full duplicate execution (DMR), doubling compute time and power consumption.
- **Proposed Technical Mechanism:** A pure C99 sub-word invariant monitor checking $r \equiv t\zeta \pmod q$ with Strategy 1 TFIB-Ref independent twiddle verification and localized snapshot rollback ($K \le 2$).
- **What is Genuinely New:** The first pure software-level, constant-time, zero-heap fault-resilient ML-KEM-768 implementation achieving 99.4% fault coverage with only $+2.29\%$ latency overhead.
- **Measurable Hypotheses:** Achieves comparable fault coverage to DMR $2\times$ while reducing latency overhead from $+101.49\%$ down to $+2.29\%$.
- **Implementation Difficulty:** **LOW** (Already implemented and validated in ASTRA-Sec Phase 7/Phase 10).
- **What Could Disprove It:** If complex instruction reordering under aggressive compiler optimizations (`-O3`) optimizes away the invariant check.
- **Novelty Confidence:** **HIGH** (Direct, measurable advance over existing PQC software implementations).

---

## 2. Synthesis & Strategic Recommendation

To ensure scientific defensibility, we recommend **NOT** attempting to claim all five candidates as separate novelties. Instead, we recommend:

### **Primary Research Contribution (The Core):**
**CANDIDATE E + CANDIDATE A (Unified):**
> **"A Software-Level Fault-Resilient Post-Quantum Cryptographic Execution Engine with Cross-Layer Disruption-Tolerant Delivery for Space Systems"**

- **Why this combination is defensible:**
  1. Low-level algorithmic novelty: Sub-word NTT invariant monitoring with localized snapshot rollback ($K \le 2$) delivers high fault coverage (+2.29% overhead vs +101% for DMR).
  2. Protocol-level novelty: Seamless cross-layer coupling that heals transient radiation upsets in-flight without triggering costly multi-hour DTN retransmissions.
