# Phase 4 — Space-System Implications & Protocol Mapping

**Project Title:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Standards:** NIST FIPS 203 (ML-KEM), NIST FIPS 204 (ML-DSA), CCSDS 355.0-B-1 (SDLS)  
**Document Version:** 1.0.0-SPACE-SYSTEMS  
**Date:** October 1, 2026  
**Status:** COMPLETE & INDEPENDENTLY AUDITED  

---

## 1. Strict Scope Boundary & Disclaimer

> [!CAUTION]
> **RESEARCH SIMULATION DISCLAIMER:**  
> The findings in this report derive from **simulated computational fault injection** into software implementations running on general-purpose host microprocessors.  
> - These results do **NOT** constitute physical radiation testing, particle accelerator beam validation, or flight-hardware qualification.  
> - No claims are made regarding Total Ionizing Dose (TID), Single-Event Latchup (SEL), or physical space qualification under NASA, ESA, or ECSS standards.  
> - Spacecraft telemetry and telecommand evaluations are conducted using an **abstract communication protocol model** intended solely for software resilience analysis.

---

## 2. Cryptographic-to-Protocol Failure Mapping

To translate implementation-level cryptographic fault outcomes into operational space mission consequences, we map each validated cryptographic state to the standard pipeline of an abstract spacecraft command and telemetry receiver:

$$\text{RF Uplink Frame} \longrightarrow \text{Crypto Decaps / Verify} \longrightarrow \text{Plaintext Framing Check} \longrightarrow \text{Opcode & Semantic Check} \longrightarrow \text{Execution}$$

| Validated Cryptographic Outcome | Protocol Layer Impact | Spacecraft Operational Consequence | Mission Risk Classification | Autonomous Recovery Mechanism |
|:---|:---|:---|:---:|:---|
| **`CORRECT_OUTPUT`** (Masked arithmetic fault in decapsulation) | Seamless pass-through | Telecommand decrypted and verified cleanly; nominal execution. | **NO IMPACT** | None required; error naturally absorbed by $\lfloor q/4 \rfloor$ decoding slack. |
| **`IMPLICIT_REJECTION`** (ML-KEM decapsulation fault exceeds slack) | Cryptographic session desynchronization | Receiver produces incorrect session key $K_{\text{rej}} \neq K_{\text{ground}}$. Subsequent AEAD or framing checks fail; telecommand rejected. | **AVAILABILITY IMPACT (MODERATE)** | Protocol-level handshake retry; request key renegotiation from ground station. |
| **`EXPLICIT_REJECTION`** (ML-DSA verification failure on corrupted signature) | Authentication failure | Command discarded prior to framing or execution; explicit error logged in spacecraft telemetry. | **AVAILABILITY IMPACT (LOW/TRANSIENT)** | Telecommand retransmission from ground station over subsequent contact window. |
| **`ATTEMPT_EXHAUSTION_DOS`** (ML-DSA signing loop exhausted by persistent fault) | Telemetry authentication blackout | Spacecraft cannot sign downlink telemetry or command acknowledgments. Ground station cannot authenticate spacecraft status. | **AVAILABILITY IMPACT (HIGH)** | Watchdog reset of cryptographic signing sub-system; fallback to secondary flight computer. |
| **`DECISION_OVERRIDE`** (Simulated Boolean gate bypass on invalid signature) | Authentication bypass | Unauthenticated command packet accepted by crypto layer. | **POTENTIAL INTEGRITY IMPACT (CRITICAL)** | Downstream multi-layer defense: framing magic bytes, strict sequence counter windows, command semantic checks. |
| **`GARBLED_PAYLOAD_MISMATCH`** (ML-KEM candidate key selected on corrupted CT) | Silent session desynchronization | Both parties hold completely different, uncorrelated keys. Uplink stream cannot be decrypted. | **AVAILABILITY IMPACT (MODERATE)** | Autonomous session timeout; ground-commanded handshake re-initialization. |

---

## 3. Abstract Protocol Layer Analysis

### 3.1 Unauthenticated vs. Authenticated Framing Under SEUs
In [`experiments/system_model/spacecraft_protocol_sim.py`](file:///Users/dhairyajain/Desktop/pqc%20research/experiments/system_model/spacecraft_protocol_sim.py), the abstract spacecraft communication model demonstrated the vital distinction between unauthenticated raw streams and authenticated framing:

1. **Unauthenticated Stream Scenario (Raw Decryption):**
   - When an SEU causes ML-KEM implicit rejection, the spacecraft decapsulates $K_{\text{rej}}$ instead of $K_{\text{ground}}$.
   - If the uplink uses raw stream decryption without framing authentication:
     - The corrupted session key decrypts incoming bytes into pseudorandom noise.
     - In the updated receiver model, the explicit multi-stage receiver intercepts this noise at the **Magic Sync Header** check (100.0% rejected with $0.0\%$ accepted).
     - *Finding:* Even without cryptographic MACs, a rigorous format/CRC parser prevents execution of garbled commands, transforming a potential integrity hazard into an explicit format rejection.
2. **Authenticated Protocol Scenario (HMAC-SHA256 / AEAD):**
   - The spacecraft validates the cryptographic authentication tag before attempting command parsing.
   - When an SEU induces implicit rejection ($K_{\text{sc}} \neq K_{\text{ground}}$), the MAC verification fails deterministically.
   - The payload is dropped immediately, and the autonomous recovery state machine initiates handshake retransmissions.
   - In 1,000 simulated iterations, **100.0% of sessions recovered on Retry 1** within an average latency of $73.5\,\mu\text{s}$.

---

## 4. Architectural Resilience Recommendations for Space Flight Software

Based on the Phase 4 audit, the following software architectural principles are recommended for flight software incorporating post-quantum cryptography:

1. **Explicit Telemetry for Cryptographic Mismatches:**
   - Because ML-KEM decapsulation fails closed to pseudorandom keys without raising an exception, downstream protocol layers must flag framing/MAC authentication failures as potential **cryptographic desynchronizations** rather than generic RF channel noise.
2. **Double-Checked Verification Decision Gates:**
   - To mitigate single-point decision gate overrides (`cmp: 1 -> 0`), flight software should implement dual-variable verification logic:
     ```c
     volatile int verify_status_1 = mld_sign_verify(...);
     volatile int verify_status_2 = mld_sign_verify_independent(...);
     if (verify_status_1 == SUCCESS && verify_status_2 == SUCCESS) {
         execute_command();
     } else {
         log_telemetry_fault();
     }
     ```
3. **Rejection Loop Watchdogs:**
   - In ML-DSA signing, the rejection loop must be bounded by strict execution timeout watchdogs to prevent space computer thread starvation during heavy-ion bursts.
4. **Multi-Stage Defense-in-Depth:**
   - No flight system should rely solely on the cryptographic verification return code. Downstream command interpreters must enforce independent sequence counters, valid command opcode dictionaries, and hardware authorization interlocks.
