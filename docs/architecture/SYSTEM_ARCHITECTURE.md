# System Architecture

## 1. High-Level System Architecture

The space-resilience post-quantum cryptographic framework integrates four major subsystems:

```mermaid
flowchart TD
    subgraph Spaceborne Flight Computer
        ROM[("Immutable Rad-Hard ROM\n(Golden Twiddle Tables & Hashes)")]
        SRAM[("Volatile Flight SRAM / Registers\n(Active Twiddle Tables & State)")]
        
        subgraph TFIB Integrity Subsystem
            Digest["Digest Calculator / Assertion Check"]
            Heal["Microsecond Self-Healing Engine"]
        end
        
        subgraph PQC Cryptographic Engine
            NTT["NTT Butterfly Network\n(Cooley-Tukey / Montgomery Multiplier)"]
            KEM["ML-KEM-768 Core\n(KeyGen / Encaps / Decaps)"]
            FO["Fujisaki-Okamoto Transform\n& Re-encryption Check"]
        end
    end
    
    ROM -.->|1. Initial Boot / Restore Path| SRAM
    SRAM -->|2. Table Fetch| Digest
    ROM -->|3. Golden Digest Compare| Digest
    
    Digest -->|Integrity Verified (0.015 us)| NTT
    Digest -->|Anomaly Detected!| Heal
    Heal -->|4. Copy Gold Table from ROM| SRAM
    Heal -->|5. Log SEU Telemetry Event| FlightLog["Radiation Telemetry"]
    
    NTT --> KEM
    KEM --> FO
    FO --> SharedSecret["Established Shared Secret (K)"]
```

## 2. Memory Architecture & Trust Boundaries
- **Volatile Execution Space (SRAM / CPU Registers):** Contains the active working copy of the NTT twiddle factor tables (`zetas`), message polynomials, and intermediate secret values. Subject to single-event upsets (SEUs) from space radiation.
- **Protected Immutable Space (ROM / MRAM / Rad-Hard EEPROM):** Houses the precomputed golden reference twiddle factors and the cryptographic integrity digest. This memory boundary is write-protected and decoupled from volatile scratchpads.
- **Trust Boundary Axiom:** Detection logic must *never* rely on state stored in the unverified, mutable working space. All integrity assertions evaluate against the immutable ROM boundary.

## 3. Flight Software Compliance (NASA/ESA Guidelines)
- **Zero Dynamic Allocation:** `malloc()`, `calloc()`, and `free()` are strictly forbidden in flight code paths. All arrays and buffers are statically sized or stack-allocated with fixed, bounded recursion depths ($0$).
- **Deterministic Bounded Execution:** All loops operate with fixed upper bounds ($n=256$, $128$ butterflies per layer). Execution time is invariant with respect to secret key data.
- **Fail-Safe Containment:** If an uncorrectable corruption event occurs, the system emits an explicit radiation alert event to ground telemetry rather than silently entering indefinite key-renegotiation cycles.

