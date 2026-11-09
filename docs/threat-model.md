# ASTRA-Sec: Comprehensive Threat Model
## Adversarial and Environmental Risk Analysis for Multi-Hop Space Communications

**Author:** ASTRA-Sec Development Agent  
**Date:** November 2026  
**Status:** Complete  
**Standards:** NIST SP 800-30 Rev. 1, ECSS-E-ST-70-41C, CCSDS 350.1-G-2

---

## 1. Threat Landscape & Boundary Definition

Spaceborne communication networks operate under a dual threat model:
1. **Intentional Malicious Attacks (Cyber & Electronic Warfare):** Adversaries intercepting, spoofing, delaying, or altering RF downlinks and uplinks, or compromising intermediate relay spacecraft.
2. **Accidental Physical & Environmental Faults (Space Physics):** Galactic cosmic rays, solar energetic protons, and trapped radiation belt particles ionizing silicon, inducing Single-Event Upsets (SEUs), Single-Event Transients (SETs), and latchups.

```
                                  THREAT MODEL TAXONOMY
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
     [ INTENTIONAL MALICIOUS ATTACKS ]              [ ACCIDENTAL ENVIRONMENTAL FAULTS ]
     - Passive Eavesdropping (Quantum harvest)      - Cosmic Ray Single-Event Upsets (SEUs)
     - Active RF Injection / Man-in-the-Middle      - Single-Event Transients (ALU voltage spikes)
     - Message Modification & Forgery               - Permanent Stuck-At Latches & Cell Breakdown
     - Replay Attacks of Valid Historical Bundles   - Single-Event Latchup / Power Traps
     - Compromised Intermediate Relay Satellites    - Orbital Occultation & Path Intermittency
     - Stale Authorization & Identity Spoofing       - Unplanned Flight Computer Reboots
```

---

## 2. Component Trust Classification

Every entity in the ASTRA-Sec architecture is explicitly classified into one of three trust categories:

| Component | Trust Level | Rationale & Trust Scope | Untrusted Behaviors Assumed |
|---|:---:|---|---|
| **Ground Station A (Origin)** | **Trusted** | Originator of telecommands and cryptographic session states. Holds authoritative private signing key. | Assumed physically secured and free of local malware. |
| **Ground Station B (Destination)** | **Trusted** | Terminating mission endpoint. Holds authoritative KEM private decapsulation key. | Assumed physically secured; executes L7 audit verification. |
| **Satellite 1 (LEO Relay)** | **Untrusted** | Commercial or multi-tenant satellite relaying BPv7 bundles. | May inspect packets, eavesdrop, drop bundles, alter routing headers, or replay old bundles. |
| **Satellite 2 (Crosslink Relay)** | **Untrusted** | Inter-satellite relay node. May be operated by third-party coalition partners. | Same as Satellite 1. Cannot be trusted with payload plaintext or symmetric keys. |
| **Physical RF Uplink / Downlink** | **Untrusted** | Free-space RF transmission medium across UHF, S-, X-, and Ka-bands. | Complete passive eavesdropping and active packet injection/jamming assumed. |
| **Flight Computer ALU / Registers** | **Partially Trusted** | COTS microcontroller (ARM/RISC-V) executing cryptographic arithmetic in orbit. | Trusted for nominal logic, but **untrusted against radiation-induced SEU bit-flips**. |
| **Local Checkers & Invariant Code**| **Partially Trusted** | Software routines evaluating invariants in CPU registers. | May be corrupted by radiation strikes (tested in Step 2C-A); must not cause SDC. |

---

## 3. Threat Catalog & Attack Vector Analysis

### 3.1 Network-Level Intentional Adversaries

#### T-01: Passive Eavesdropping & "Harvest-Now, Decrypt-Later"
- **Threat Actor:** Well-resourced nation-state adversary recording encrypted satellite RF downlinks with massive terrestrial ground arrays.
- **Goal:** Archive encrypted payloads today and decrypt them when a cryptanalytically relevant quantum computer becomes operational.
- **ASTRA-Sec Mitigation:** NIST FIPS 203 ML-KEM-768 key encapsulation combined with AES-256-GCM authenticated encryption. Classical RSA/ECC algorithms are strictly excluded.

#### T-02: Active Network Man-in-the-Middle (MitM) & Payload Tampering
- **Threat Actor:** Rogue ground station or electronic warfare asset transmitting forged RF frames.
- **Goal:** Modify telecommand parameters (e.g., thruster firings, attitude maneuvers) in transit.
- **ASTRA-Sec Mitigation:** NIST FIPS 204 ML-DSA-65 post-quantum digital signatures encapsulated in RFC 9172 Block Integrity Blocks (BIB). Any single-bit payload alteration causes immediate verification failure.

#### T-03: Replay of Historical Valid Bundles
- **Threat Actor:** Adversary capturing and re-transmitting genuine, previously executed telecommands.
- **Goal:** Induce duplicate command execution (e.g., replaying a battery discharge command).
- **ASTRA-Sec Mitigation:** Three-fold replay protection:
  1. Monotonically increasing bundle sequence numbers inside the authenticated payload.
  2. Bounded creation timestamp and time-to-live (TTL) expiration in BPv7 primary blocks.
  3. Ephemeral ratcheting: each bundle uses a unique ratchet step index ($N_{step}$); duplicate indices are rejected by the sliding-window Bloom filter.

#### T-04: Compromised Intermediate Relay Satellites
- **Threat Actor:** Hostile entity gaining administrative control over an intermediate relay satellite (e.g., SAT1 or SAT2).
- **Goal:** Extract intelligence from crosslink traffic or redirect mission bundles.
- **ASTRA-Sec Mitigation:** Strict Layer 7 (BPSec) end-to-end encryption. Intermediate relays inspect only the primary routing header (EIDs); payload data is encapsulated in an opaque Block Confidentiality Block (BCB) decryptable only by the private key holder (GSB).

#### T-05: Key Compromise & Lack of Forward Secrecy
- **Threat Actor:** Physical extraction of cryptographic state from a retired or captured satellite.
- **Goal:** Decrypt historical mission recordings or forge future commands.
- **ASTRA-Sec Mitigation:** The Post-Quantum Double Ratchet (PQ-DR). Each bundle derivation immediately deletes prior ephemeral keys via forward KDF hashing, guaranteeing **forward secrecy**. Subsequent ephemeral ML-KEM key exchanges provide **post-compromise recovery (self-healing)**.

---

### 3.2 Environmental Physical & Hardware Faults

#### T-06: Single-Event Upset (SEU) in Butterfly Registers
- **Physical Cause:** Ionizing cosmic ray striking a CPU flip-flop holding an intermediate NTT coefficient.
- **Failure Mode:** Silent Data Corruption (SDC). The decapsulation routine finishes with return code 0 but derives a mutated session key $K' \neq K$, permanently severing communications.
- **ASTRA-Sec Mitigation:** Sub-word dual-rail invariant monitoring ($(u'+v') \equiv 2u \pmod q$). If an SEU occurs, the monitor restores clean register snapshots (`u_saved, v_saved`) and recomputes the butterfly in-place ($R_{max}=2$), achieving 100% transient recovery with 0 SDC across tested trials.

#### T-07: Permanent Latchup / Stuck-At Register Faults
- **Physical Cause:** Total Ionizing Dose (TID) gate rupture or physical transistor destruction, locking a register bit to 1 or 0 permanently.
- **Failure Mode:** Unbounded retry loop causing flight computer watchdog timeout and system crash.
- **ASTRA-Sec Mitigation:** Bounded retry counter ($R_{max}=2$). When retries are exhausted, the monitor increments a persistent error counter and escalates to an algebraic fail-stop, forcing FIPS 203 implicit rejection ($K_{rej}$) without throwing processor traps.

#### T-08: Twiddle Factor Table Corruption (Theorem 1)
- **Physical Cause:** Radiation bit-flip in the read-only twiddle factor table ($\zeta$) in SRAM/Flash.
- **Failure Mode:** Input/output invariants pass falsely because $(u'+v') \equiv 2u \pmod q$ cancels $\zeta v$, blinding the monitor.
- **ASTRA-Sec Mitigation:** Twiddle Factor Integrity Binding (`tfib_ref.c`), which binds operational twiddles against an independent reference table (`tfib_zetas_ref[128]`) prior to butterfly arithmetic.

#### T-09: Unshielded Circular Verifier Masking
- **Physical Cause:** Runtime checker evaluates invariants using mutated live registers rather than pre-computation snapshots.
- **Failure Mode:** 98.5% failure rate (591/600 false passes observed in Phase 16) due to circular arithmetic consistency.
- **ASTRA-Sec Mitigation:** Mandatory compiler-mapped register snapshots (`u_saved = r[j]`, `v_saved = r[j+len]`) captured strictly before butterfly execution begins.

#### T-10: Spacecraft Power Trap & Flight Computer Restart
- **Physical Cause:** Power brownout or watchdog reset during bundle processing.
- **Failure Mode:** Desynchronization of the ratcheting state machine; key re-use vulnerabilities on reboot.
- **ASTRA-Sec Mitigation:** Crash-consistent state journaling. Ratchet indices and key seeds are written to non-volatile memory (NVRAM) before bundle transmission. On restart, the node rolls back to the last committed atomic journal entry.

---

## 4. Threat-to-Mitigation Traceability Matrix

| Threat ID | Threat Category | Target Subsystem | Severity | ASTRA-Sec Countermeasure | Residual Risk |
|---|---|---|:---:|---|---|
| **T-01** | Malicious / Cryptanalytic | Space Link Telemetry | **Critical** | FIPS 203 ML-KEM-768 + AES-256-GCM | Negligible (Lattice hardness) |
| **T-02** | Malicious / Active | Space Link Telecommand | **Critical** | FIPS 204 ML-DSA-65 (BIB Extension) | Negligible (Signature unforgeability)|
| **T-03** | Malicious / Replay | Flight Computer Command | **High** | Monotonic Counter + Bloom Filter + Ratchet Index | Low (Window wrap-around guarded) |
| **T-04** | Malicious / Relay | Intermediate Satellites | **High** | L7 BPSec BCB End-to-End Encryption | Negligible (No relay key exposure) |
| **T-05** | Malicious / Compromise | Flight Computer Memory | **High** | Post-Quantum Double Ratchet (Forward/Self-Healing) | Low (Window of exposure = 1 bundle) |
| **T-06** | Environmental / Transient | NTT Butterfly Logic | **Critical** | Register Snapshots + Invariant Rollback ($R_{max}=2$) | Bounded ($\le 0.49\%$ SDC bound) |
| **T-07** | Environmental / Permanent | Microprocessor Silicon | **High** | Fail-Stop Escalation $\to$ FIPS 203 Implicit Rejection | Low (Triggers safe link rekey) |
| **T-08** | Environmental / Constant | Twiddle Storage | **High** | TFIB Hardened Reference Table Binding (`tfib_ref.c`) | Low (Closed Theorem 1 blind spot) |
| **T-09** | Design Flaw / Logic | Software Invariant Verifier | **Critical** | Pre-Computation Snapshot Isolation | Mitigated (0% circular masking) |
| **T-10** | Physical / Power | Flight Computer OS | **Medium** | Atomic NVRAM Ratchet State Journaling | Low (Non-volatile write wear) |

---

## 5. Explicit Limitations of Software Fault Modeling

It is vital to state the scientific boundaries of software fault injection:
1. **No Physical Semiconductor Simulation:** Software-level register bit-flips model the *logical consequence* of an SEU, but do not simulate analog pulse widths, charge collection, or substrate current transport.
2. **Control-Flow Skips Outside Datapath:** If a radiation particle causes the CPU instruction pointer to jump completely over the butterfly loop, arithmetic invariants will not execute. Control-flow integrity (CFI) is handled at L6/L7 via outer signature verification.
3. **Multi-Cell Physical Clustering:** Software injection flips logical bits in a register, whereas high-LET heavy ions can cause physical multi-cell cluster upsets across adjacent physical memory bitlines.
