# Phase 1 — Document 05: Evaluation of Five Candidate Research Contributions

**Document ID:** `ASTRA-SEC-PH1-DOC-05`  
**Research Directorate:** Multidisciplinary Academic Evaluation Team  
**Date:** November 2026  
**Evaluation Rigor:** High (Prior art scrutinized, falsifiability required, no assumed novelty)

---

## 1. Candidate 1: Cross-Layer Fault-Aware Security State Machine (CL-FASSM)

### A. Problem Definition
When satellite nodes communicate over delay-tolerant networks while exposed to cosmic radiation, two failure domains interact simultaneously:
1. **Low-level hardware/arithmetic faults:** Cosmic single-event upsets (SEUs) corrupt intermediate post-quantum polynomial calculations (e.g., in ML-KEM decapsulation), triggering either transient rollback or permanent fail-stop implicit rejection.
2. **High-level network disruptions:** Orbital contact windows close, bundles queue in persistent spools, and key rotation epochs advance during transit.

In current architectures, these two domains operate in complete isolation. The cryptographic engine either succeeds or silently drops the bundle, leaving the DTN transport layer blind to whether a failure was caused by a cosmic SEU (recoverable locally), an active adversarial tampering attempt (requires security audit and relay blacklisting), or an expired key epoch (requires re-keying negotiation).

### B. Prior-Art Coverage
- **DTN Transport:** RFC 9171 (BPv7) and NASA/JPL ION-DTN provide custody transfer and status reporting (`ReasonCode: BlockUnintelligible` or `DepletedStorage`), but have zero awareness of internal cryptographic execution outcomes.
- **Cryptographic Fault Handling:** Ravi et al. (2020) and Primas et al. (2021) study fault detection in isolation on a single board, treating the network as non-existent.
- **Cross-Layer Networking:** Wireless sensor networks (e.g., ZigBee/6LoWPAN) coordinate PHY signal strength with MAC routing, but have never addressed post-quantum arithmetic rollback coordination with store-and-forward bundles.

### C. Unresolved Gap
No existing protocol defines a formal state machine that coordinates low-level cryptographic execution states ($\text{State}_{\text{crypto}} \in \{\text{CLEAN}, \text{ROLLBACK}_1, \text{ROLLBACK}_2, \text{FAIL\_STOP}\}$) with DTN persistence and custody states ($\text{State}_{\text{DTN}} \in \{\text{SPOOLED}, \text{FORWARDING}, \text{CUSTODY\_ACCEPTED}, \text{EXPIRED}\}$).

### D. Proposed Technical Contribution
A cross-layer protocol state machine that binds Layer 4 arithmetic recovery outcomes to Layer 5/6 DTN spool transitions:
1. **Transient SEU Escalation Rule:** If decapsulation fails on Attempt 1 ($K=1$), local snapshot rollback is executed without signaling the DTN layer (preventing unnecessary orbital retransmissions).
2. **Persistent SEU / Fail-Stop Rule:** If rollback budget is exhausted ($K > 2$), the state machine transitions to FIPS 203 implicit rejection, alerts Layer 7 FDIR telemetry, records the event in the SQLite WAL audit ledger, and instructs DTN custody transfer to suppress retransmission (preventing Denial of Service across scarce satellite bandwidth).
3. **Epoch Transition Rule:** If a bundle arrives after a key rotation epoch has advanced, the state machine triggers an authenticated re-keying challenge bundle rather than dropping the message.

### E. Mathematical and Formal Depth
Requires formal modeling of a finite state automaton $\mathcal{M} = (S, \Sigma, \delta, s_0, F)$:
- State space $S = S_{\text{crypto}} \times S_{\text{dtn}} \times S_{\text{replay}}$.
- Safety invariant: $\forall s \in S$, an unauthenticated or corrupt payload never transitions to $S_{\text{executed}}$.
- Liveness invariant: $\forall s \in S$, transient arithmetic faults recover within $t_{\text{rollback}} \le 2 \cdot t_{\text{butterfly}}$ without inducing DTN bundle drop.

### F. Experimental Validation
Tested across 20 dual-fault scenarios where SEUs are injected into ML-KEM decapsulation at the exact instant an orbital contact window terminates or a duplicate bundle arrives.

### G. Falsifiability
Disproved if an existing published DTN security framework (e.g., an unreviewed BPSec draft or ESA study) already coordinates internal KEM rollback states with bundle custody transfer, or if cross-layer signaling introduces higher latency than naive retransmission.

### H. Feasibility
**HIGH.** Both the C99 fault hooks and the Python BPv7/spool engines exist in the codebase and can be bridged via defined ctypes telemetry callbacks.

### I. Novelty Confidence: **HIGH**
Strong prior-art defense; solves an authentic, demonstrable failure mode at the intersection of space radiation and DTN store-and-forward networking.

---

## 2. Candidate 2: Crash-Consistent Cryptographic Command Acceptance Protocol (C4AP)

### A. Problem Definition
Satellite flight computers reset frequently due to single-event functional interrupts (SEFIs) or watchdog resets. If a satellite resets while authenticating or executing a telecommand, inconsistent state transitions can occur:
- If anti-replay state is updated *after* command execution, a crash between execution and state commit allows command replay upon reboot.
- If anti-replay state is updated *before* cryptographic verification completes, a crash during verification permanently locks out a valid command.
- If an acknowledgement (ACK) is generated before application commit, a crash causes ground stations to believe a command succeeded when it was lost.

### B. Prior-Art Coverage
- **Database Systems:** Gray et al. (1981), ACID transaction protocols, Write-Ahead Logging (WAL).
- **Satellite Systems:** ECSS-E-ST-70-41C defines telecommand execution verification stages (Received, Accepted, Started, Completed), but assumes sequential execution on non-partitioned networks.
- **DTN:** RFC 9171 supports custody transfer, but custody signals that a bundle was *stored*, not that an application-layer command was *executed*.

### C. Unresolved Gap
No prior work formalizes a **crash-consistent cryptographic transaction protocol** for post-quantum telecommands that guarantees **at-most-once execution** across arbitrary node power-cycles and reboots.

### D. Proposed Technical Contribution
A 5-phase cryptographic transaction protocol:
$$\text{Received} \xrightarrow{\text{L2 Auth}} \text{Authenticated} \xrightarrow{\text{WAL Pre-Commit}} \text{Accepted} \xrightarrow{\text{App Exec}} \text{Committed} \xrightarrow{\text{DSA Sign}} \text{Acknowledged}$$
- The protocol enforces that an anti-replay sequence mark is committed to the SQLite WAL journal *atomically* with the verified command envelope before application dispatch.
- Ground Station Verifiers reject any ACK that does not cryptographically bind the destination's post-execution WAL transaction ID.

### E. Mathematical and Formal Depth
Formal state-machine modeling with TLA+ or Promela/SPIN proving crash consistency and anti-replay invariance under arbitrary `SIGKILL` fault schedules.

### F. Experimental Validation
Injecting power-cycle resets (`SIGKILL`) at each of the 5 transition boundaries during 1,000 rapid command dispatches, verifying zero duplicate executions and zero lost commands.

### G. Falsifiability
Disproved if standard database WAL protocols trivially solve the problem without cryptographic binding, or if existing CCSDS telecommand implementations already provide WAL-backed crash-consistent anti-replay.

### H. Feasibility: **HIGH**
The existing SQLite WAL spool in `astra_sec/network/spool.py` already supports atomic transactions.

### I. Novelty Confidence: **MEDIUM to HIGH**
Technically deep and publication-worthy in distributed systems or aerospace dependability venues, but borders on applying known database transaction principles to cryptographic telecommands.

---

## 3. Candidate 3: Fault-Aware DTN Message Lifecycle Architecture

### A. Problem Definition
When an intermediate satellite relay or destination node encounters an arithmetic cryptographic fault, DTN message lifecycle timers (bundle lifetime, custody timeout) continue ticking. If a bundle expires while an endpoint is executing localized rollbacks or waiting for a clean re-computation window, the message is discarded.

### B. Prior-Art Coverage
RFC 9171 specifies bundle lifetime and expiry. NASA ION-DTN implements custody timeouts with exponential backoff.

### C. Unresolved Gap
Existing DTN lifecycle models treat bundle lifetimes as monotonic wall-clock intervals independent of cryptographic processing health.

### D. Proposed Technical Contribution
An adaptive bundle lifecycle extension where cryptographic retry states dynamically modulate custody hold times and retransmission backoffs.

### E. Mathematical and Formal Depth
Queueing theory analysis under stochastic fault rates; proof of bounded queue occupancy under Poisson-distributed SEUs.

### F. Experimental Validation
Simulating high SEU radiation flux in orbital bundles and measuring message loss rates with and without adaptive lifecycle extensions.

### G. Falsifiability
Disproved if simple static TTL extension provides equivalent reliability without protocol modifications.

### H. Feasibility: **MEDIUM**

### I. Novelty Confidence: **MEDIUM**
While practical, reviewers may consider this an engineering heuristic rather than a fundamental scientific contribution.

---

## 4. Candidate 4: Independent Fault-Checker Resilience for ML-KEM (TFIB-Ref)

### A. Problem Definition
In high-radiation space environments, fault-tolerant execution mechanisms are themselves vulnerable to radiation. If a single-event upset flips bits in the **invariant checking table** (e.g., the twiddle factor array $\zeta$) or the **checker logic itself**, the defense fails:
- False Positive: The checker flags clean computation as corrupt, causing needless fail-stop suppression.
- False Negative: The checker accepts corrupted secret key material, causing Silent Data Corruption (SDC).

### B. Prior-Art Coverage
- Paul et al. (2023) introduce DSP slice invariant checking, but assume the FPGA DSP blocks and twiddle ROM are immutable and immune to radiation.
- Ravi et al. (2020) evaluate DMR, which is equally vulnerable if both compute paths share common memory or if the comparator itself is faulted.

### C. Unresolved Gap
Zero published literature evaluates software-level self-checking resilience where the **reference twiddle table (TFIB-Ref)** and the **rollback snapshot buffers** are subjected to simultaneous adversarial fault injection.

### D. Proposed Technical Contribution
A self-verifying, constant-time dual-transform architecture in pure C99:
1. Reference twiddle table verification using compile-time ROM checksums.
2. Independent forward/inverse algebraic cross-invariants ($r \cdot r^{-1} \equiv 1 \pmod q$).
3. Bounded stack snapshot protection preventing rollback corruption.

### E. Mathematical and Formal Depth
Modular polynomial arithmetic proofs, algebraic invariant derivations in $\mathbb{Z}_{3329}$, and exhaustive fault injection modeling across all 256 coefficients and 128 twiddle factors.

### F. Experimental Validation
Injecting 10,000 physical bit flips targeting the twiddle arrays and checking logic directly, measuring fault detection coverage, recovery success, and SDC rate.

### G. Falsifiability
Disproved if twiddle table corruption cannot be detected without full duplicate execution (+100% overhead).

### H. Feasibility: **VERY HIGH**
The native C99 implementation in `algorithms/source_ref/` already contains these hooks and has been benchmarked.

### I. Novelty Confidence: **HIGH (in Cryptographic Hardware/Embedded Systems)**
Extremely strong as an embedded cryptography / CHES paper, but narrower than the full space network architecture.

---

## 5. Candidate 5: Key-Transition Safety During Disruption-Tolerant Disconnection

### A. Problem Definition
In deep-space or sparse LEO constellations, bundles may remain queued in persistent storage for days or weeks. During this transit interval, a ground station may execute a scheduled or emergency post-quantum key rotation (e.g., advancing the Double Ratchet epoch or revoking a compromised satellite public key). When the queued bundle finally arrives at the destination:
- If the destination uses its updated key state, it cannot decapsulate the bundle.
- If the destination retains old private keys indefinitely, it violates forward secrecy.

### B. Prior-Art Coverage
Signal Protocol / Double Ratchet manages out-of-order messages in connected networks, but drops messages older than a small sliding window (e.g., 2,000 skipped keys). BPSec delegates key management to external authorities.

### C. Unresolved Gap
No protocol specifies a formal policy-driven mechanism for safely resolving queued authenticated post-quantum messages spanning key rotation epochs across disruption-tolerant disconnections.

### D. Proposed Technical Contribution
A key-epoch envelope structure that binds epoch validity intervals with cryptographic proof-of-dispatch, allowing secure asynchronous re-keying negotiation without exposing past traffic to key compromise.

### E. Mathematical and Formal Depth
Cryptographic game-based security proofs for forward secrecy and post-compromise security under asynchronous network partitions.

### F. Experimental Validation
Simulating 72-hour orbital disconnections with mid-transit key revocations and validating clean re-keying and packet handling.

### G. Falsifiability
Disproved if existing asynchronous messaging protocols (e.g., MLS — Messaging Layer Security, RFC 9420) already accommodate long-delay DTN key transitions.

### H. Feasibility: **MEDIUM**

### I. Novelty Confidence: **MEDIUM**
Strong, but MLS is increasingly exploring asynchronous group key transitions, increasing the risk of prior-art preemption.

---

## 6. Synthesis and Comparative Summary

| Candidate | Technical Domain | Primary Strength | Primary Vulnerability / Counter-Evidence | Novelty Confidence |
| :--- | :--- | :--- | :--- | :--- |
| **Candidate 1: Cross-Layer State Machine** | Protocol & Systems | Solves the genuine gap between crypto rollback and DTN custody. | Must prove that cross-layer signaling does not violate layering abstraction. | **HIGH** |
| **Candidate 2: Crash-Consistent Acceptance** | Distributed Systems | Solves critical satellite restart-replay vulnerability. | Similar to database transaction processing principles. | **MEDIUM-HIGH** |
| **Candidate 3: Fault-Aware Lifecycle** | DTN Transport | Practical queue optimization under high SEU rates. | Reviewers may view as an engineering heuristic. | **MEDIUM** |
| **Candidate 4: TFIB-Ref Fault Checker** | Embedded Cryptography | Deep algorithmic novelty in C99; $+2.29\%$ vs $+101.49\%$ DMR. | Narrower algorithmic focus; ignores wider DTN space network. | **HIGH (CHES scope)** |
| **Candidate 5: Key-Transition Safety** | Cryptographic Protocols | Critical for multi-day interplanetary disconnections. | Overlaps partially with ongoing IETF MLS asynchronous extensions. | **MEDIUM** |
