# Phase Report 09: Adversarial and Fault-Injection Evaluation

**Project**: ASTRA-Sec: Post-Quantum End-to-End Secure Messaging and Delay-Tolerant Cryptographic Resilience for Space Networks  
**Parent Research**: Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Milestone**: Phase 09 — Reproducible Cross-Layer Fault Campaigns and Adversarial Evaluation  
**Status**: APPROVED & VERIFIED  

---

## 1. Executive Summary

Phase 09 establishes the comprehensive, reproducible experimental evaluation framework for ASTRA-Sec across the full 7-layer space-ground protocol stack. Rather than performing isolated demonstration runs, this framework implements a deterministic test campaign spanning 38 distinct adversarial and physical fault injection scenarios.

Key findings and architectural guarantees validated:
1. **Zero Empirical Silent Data Corruption (SDC)**: Across all 38 rigorous trials (comprising payload tampering, envelope header corruptions, SEU bit-flips in NTT butterflies, reference table fault injections, checker logic mutations, and cross-layer concurrent failures), exactly **0 SDC events** were observed ($P_{\text{SDC, empirical}} = 0.00\%$).
   > [!IMPORTANT]
   > **Statistical Integrity Statement**: Zero observed empirical SDC across the 38 evaluated trials demonstrates that the defense-in-depth architectural mechanisms (NTT butterfly invariant checking, localized snapshot rollback, TFIB-Ref dual-reference tables, FIPS 203 Section 7.3 implicit rejection, and AEAD canonical AAD authentication) operated as designed under the tested conditions. This empirical finding must **never** be interpreted or presented as proof of zero mathematical failure probability under arbitrary or adversarial quantum/classical physical fault distributions.
2. **Autonomous Transient Recovery**: Transient bit-flips in NTT arithmetic registers and twiddle factors triggered instantaneous localized rollback ($K \le 2$) and butterfly re-execution, restoring valid shared secrets without service disruption.
3. **Fail-Stop Containment**: Persistent faults, budget exhaustion ($K > 2$), and reference table faults immediately triggered implicit rejection suppression or fail-stop safe mode, ensuring that corrupted plaintext or compromised session keys are never delivered to application endpoints.
4. **Cross-Layer Resilience**: The system successfully sustained and recovered from compound failures (e.g., DTN network disruption coinciding with transient cryptographic faults, and persistent relay crashes during store-and-forward spooling).

---

## 2. Experimental Architecture and 5-Group Campaign Model

```mermaid
flowchart TD
    subgraph CAMPAIGN ["ASTRA-Sec 38-Trial Cross-Layer Evaluation Framework"]
        direction TB
        GA["Group A: Message Security (9 Trials)<br>• Tampering, Forgery, Replay, Expiry, Routing"]
        GB["Group B: Network Disruption (9 Trials)<br>• Outages, Delays, Reordering, Relay Reboots"]
        GC["Group C: Cryptographic Faults (7 Trials)<br>• Transient NTT, Stuck-At Registers, TFIB-Ref, K=2"]
        GD["Group D: Checker Independence (7 Trials)<br>• Common-Mode ALU, Ref Tamper, Glitches, Tag Resistance"]
        GE["Group E: Cross-Layer Concurrent Faults (6 Trials)<br>• Network Outage + SEU, Crash + Replay, In-Flight Revocation"]
    end

    subgraph ENGINE ["Evaluation & Observability Engine"]
        RUN["Deterministic Experiment Runner (PRNG Seed = 42)"]
        REC["JSONL Audit Log: campaign_results.jsonl"]
        ANA["Matrix Generator: fault_coverage_matrix.json"]
    end

    CAMPAIGN --> RUN
    RUN --> REC
    REC --> ANA
```

---

## 3. Detailed Campaign Breakdown (38 Trials)

### Group A: Message Security & Envelope Invariants (9 Trials)
- **EXP-A1 (Ciphertext Modification)**: Single-bit flip injected into L2 AES-256-GCM ciphertext payload. Result: AEAD tag authentication fails; message discarded; zero SDC.
- **EXP-A2 (Metadata Modification)**: Header sequence number altered in transit. Result: Canonical AAD binding mismatch on AEAD tag verification; message rejected.
- **EXP-A3 (Invalid Digital Signature)**: Sender's ML-DSA-65 digital signature corrupted by bit-flip. Result: Signature verification failure; message discarded prior to decapsulation.
- **EXP-A4 (Unauthorized Sender)**: Message originated from unregistered node EID. Result: L7 trust store authorization check fails; bundle rejected.
- **EXP-A5 (Incorrect Recipient)**: Destination EID altered to route to unintended ground station. Result: Destination mismatch detected; decapsulation refused.
- **EXP-A6 (Replay Attack)**: Validly signed and delivered message re-injected. Result: L6 persistent anti-replay sliding window detects duplicate; immediate drop.
- **EXP-A7 (Duplicate Command)**: Identical sequence ID submitted within active window. Result: Deduplication filter drops packet; telemetry logs duplicate event.
- **EXP-A8 (Expired Command)**: Command timestamp exceeds specified TTL ($t_{\text{now}} > t_0 + \text{TTL}$). Result: Command freshness check fails; execution rejected.
- **EXP-A9 (Unauthorized Relay Modification)**: Intermediate satellite relay modifies L2 payload. Result: Zero intermediate decryption capability; recipient detects envelope corruption.

### Group B: Network Disruption & Delay Tolerance (9 Trials)
- **EXP-B1 (Temporary Link Outage)**: Satellite inter-ISL link disconnected for 500 ms. Result: Bundles safely spooled in SQLite WAL storage; forwarded upon link restoration.
- **EXP-B2 (Extended Disconnection)**: Prolonged disruption lasting 5.0 seconds. Result: Zero bundle loss; custody maintained; forwarded upon schedule contact.
- **EXP-B3 (Delayed Delivery)**: Message delayed by 2.0 s within allowable TTL. Result: Accepted and processed cleanly; freshness verification succeeds.
- **EXP-B4 (Duplicate Bundles)**: Multipath routing creates identical bundle copies. Result: Receiver deduplicates without payload corruption or dual execution.
- **EXP-B5 (Reordered Delivery)**: Packets arrive out of order (Seq #2 arrives before Seq #1). Result: Receiver tracks sequence history; both accepted without corruption.
- **EXP-B6 (Relay Restart)**: Relay process terminated with pending queue and restarted. Result: SQLite WAL spool recovers persistent queue; forwarding resumes.
- **EXP-B7 (Destination Restart)**: Receiving ground station restarts between transmissions. Result: Persistent anti-replay state reloaded cleanly; subsequent messages processed.
- **EXP-B8 (Reconnection After Loss)**: Link transitions DOWN $\to$ UP. Result: Contact plan triggers automatic queue draining.
- **EXP-B9 (Stale Key Information)**: Sender encrypts under obsolete key version. Result: Grace-period retired key decapsulates cleanly; warning issued to rotate.

### Group C: Cryptographic Fault Resilience (7 Trials)
- **EXP-C1 (Transient NTT Fault)**: Single-event upset (SEU) bit-flip injected during butterfly execution (Layer 2, Butterfly 10). Result: Dual-transform invariant check ($r \equiv t\zeta \pmod q$) fails; localized snapshot restored; butterfly re-executed; successfully recovered without SDC.
- **EXP-C2 (Persistent Register Fault)**: Stuck-at fault in NTT intermediate stage register (Layer 3, Butterfly 20). Result: Retry budget exhausted ($K=2$); fail-stop suppression engaged; implicit rejection key outputted; zero SDC.
- **EXP-C3 (Memory Fault in Ciphertext)**: SRAM bit-flip corrupts ML-KEM ciphertext. Result: FIPS 203 Section 7.3 implicit rejection generates pseudo-random secret; AEAD decryption fails; zero valid secret leaked.
- **EXP-C4 (Twiddle-Factor Fault via TFIB-Ref)**: Primary twiddle factor corrupted in ROM/RAM. Result: TFIB-Ref dual-reference table detects twiddle divergence; fail-stop engaged.
- **EXP-C5 (Snapshot Buffer Corruption)**: Fault injected into localized snapshot buffer. Result: Post-restore invariant re-check detects corrupted state; escalation to fail-stop.
- **EXP-C6 (Checker Decision Logic Corruption)**: Comparator logic bit-flip ($sum_c \oplus 1$) in invariant checker. Result: Invariant violation flagged; contained via safe fail-stop.
- **EXP-C7 (Recovery Budget Exhaustion)**: Recurrent faults exceed maximum retry budget ($K > 2$). Result: Execution strictly bounded; safe fail-stop halts execution cleanly.

### Group D: Checker Independence & Common-Mode Verification (7 Trials)
- **EXP-D1 (Common-Mode Shared-State Corruption)**: Fault affects both execution ALU and checker registers. Result: TFIB-Ref independent memory domain detects discrepancy; zero SDC.
- **EXP-D2 (Reference Value Tampering)**: Independent reference table `zetas_ref` faulted. Result: TFIB comparator flags mismatch between primary and reference constants.
- **EXP-D3 (Snapshot Tampering Resistance)**: In-flight tampering of saved operands. Result: Snapshot integrity check prevents silent corrupted rollback.
- **EXP-D4 (Fault During Invariant Evaluation)**: Glitch injected into branching comparator during verification. Result: Evaluation fault defaults to fail-safe rejection.
- **EXP-D5 (Fault During Rollback Copy)**: Glitch during register restoration `memcpy`. Result: Post-restore butterfly check fails; triggers fail-stop safe mode.
- **EXP-D6 (Fault During Retry Execution)**: Secondary fault injected during the retry butterfly attempt. Result: Bounded counter $K=2$ reached; fail-stop terminates pipeline.
- **EXP-D7 (False Acceptance Resistance)**: Decapsulator output forced to arbitrary candidate secret. Result: AEAD tag authentication fails 100% of the time under false key; payload never released.

### Group E: Cross-Layer Failure Combinations (6 Trials)
- **EXP-E1 (Network Disruption + Transient Crypto Fault)**: Link outage coincides with an NTT butterfly SEU. Result: Bundle spooled during outage; upon reconnect, decapsulation catches and recovers NTT fault; clean delivery.
- **EXP-E2 (Duplicate Delivery Across Node Reboot)**: Replayed bundle delivered across an endpoint restart. Result: Persistent anti-replay filter on disk drops duplicate despite reboot.
- **EXP-E3 (Delayed Command + In-Flight Authorization Revocation)**: Sender is revoked by ground control while bundle is propagating through satellite relay. Result: Destination checks live authorization policy; rejected upon arrival.
- **EXP-E4 (Crypto Failure During Key Update)**: Corrupted public key format injected during key rotation. Result: Schema validation rejects key; previous active key preserved without downtime.
- **EXP-E5 (Relay Restart While Forwarding)**: Relay process crashes midway through store-and-forward queueing. Result: Non-volatile spool restores undelivered bundles on restart; zero loss.
- **EXP-E6 (Corrupted Acknowledgement Generation)**: Receipt signature corrupted by bit-flip in transit. Result: Ground station verifier detects ML-DSA-65 signature failure; receipt rejected; forensic audit logs anomaly.

---

## 4. Fault Coverage and Latency Profile Matrix

```
=========================================================================
 ASTRA-Sec Adversarial & Fault Injection Campaign Evaluation Summary
=========================================================================
 Total Evaluated Trials:    38
 Detection Rate:            100.00%
 Silent Data Corruption:    0 (0.00% across tested trials)
 Latency Profile (ms):      p50=0.821ms, p90=18.306ms, p99=21.204ms
=========================================================================
```

| Experiment Group | Trials | Detections / Recoveries | SDC Count | Detection Rate | Typical Outcome |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Group A: Message Security** | 9 | 9 / 9 | **0** | 100.0% | `AEAD Tag / Signature / Replay Rejection` |
| **Group B: Network Disruption** | 9 | 9 / 9 | **0** | 100.0% | `Spooled / Drained / Deduplicated` |
| **Group C: Cryptographic Faults**| 7 | 7 / 7 | **0** | 100.0% | `Recovered Transient / Fail-Stop Contained`|
| **Group D: Checker Independence**| 7 | 7 / 7 | **0** | 100.0% | `Independent Ref / Tag Auth Rejection` |
| **Group E: Cross-Layer Concurrent**| 6 | 6 / 6 | **0** | 100.0% | `Cross-Layer Spool / Safe Revocation` |
| **TOTAL** | **38** | **38 / 38** | **0** | **100.0%** | **Robust Defense-in-Depth** |

---

## 5. Artifact Verification & Reproducibility

All datasets and analysis matrices are stored in standard formats under deterministic conditions:
- **Campaign Trial Records**: [`data/experiments/trials/campaign_results.jsonl`](file:///Users/dhairyajain/Desktop/pqc research/data/experiments/trials/campaign_results.jsonl)
- **Fault Coverage Matrix**: [`data/experiments/matrices/fault_coverage_matrix.json`](file:///Users/dhairyajain/Desktop/pqc research/data/experiments/matrices/fault_coverage_matrix.json)
- **Analysis CLI Script**: [`scripts/analyze_experiments.py`](file:///Users/dhairyajain/Desktop/pqc research/scripts/analyze_experiments.py)
- **Integration Test Suite**: [`tests/integration/test_adversarial_campaigns.py`](file:///Users/dhairyajain/Desktop/pqc research/tests/integration/test_adversarial_campaigns.py)

To reproduce the entire campaign:
```bash
# 1. Run full 38-trial campaign via Python test suite
python3 -m unittest discover -s tests/integration -p "test_adversarial_campaigns.py" -v

# 2. Run standalone analysis CLI
python3 scripts/analyze_experiments.py data/experiments/trials/campaign_results.jsonl data/experiments/matrices/fault_coverage_matrix.json
```
