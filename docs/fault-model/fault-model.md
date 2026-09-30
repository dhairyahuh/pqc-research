# Space-System Radiation Environment to Software Fault Abstraction Model

## 1. Physical Phenomenon vs. Software Simulation

```
[Space Radiation Physics]
Galactic Cosmic Rays (GCR), Solar Energetic Particles (SEP), Trapped Van Allen Belt Protons
                           │
                           ▼ (Ionization & Linear Energy Transfer - LET)
[Silicon Device Interactions]
Charge collection at transistor junctions exceeding critical charge (Q_crit)
                           │
                           ▼ (Circuit Manifestation)
[Single Event Effects (SEE)]
- Single Event Upsets (SEU)
- Single Event Transients (SET)
- Single Event Functional Interrupts (SEFI)
                           │
                           ▼ (Formal Software Abstraction)
[Software Fault Injection Model]
- Deterministic Bit Inversion (0 -> 1, 1 -> 0)
- Byte / Word Arithmetic Corruption
- Loop Bound / Instruction Counter Skip
- Memory Pointer Offset Displacement
```

> **Epistemological Guardrail:** We explicitly state that our software-based fault injection simulates the *logical consequences* of radiation-induced upsets on data and computational flow; it does not simulate electron-hole plasma dynamics or physical silicon displacement damage.

---

## 2. Taxonomical Fault Classes

### Class A: Single Event Upset (SEU) — Single Bit Flip
- **Mechanism:** Inverting exactly one bit $b_i \leftarrow b_i \oplus 1$ in a target byte or word.
- **Physical Analogue:** Single memory cell flip in SRAM or register file caused by heavy ion strike.
- **Parameters:** Target buffer, byte offset, bit position (0..7).

### Class B: Multiple Cell Upset (MCU) — Burst Bit Corruption
- **Mechanism:** Inverting multiple physically adjacent bits (simulated as contiguous bits or bytes within a cache line).
- **Physical Analogue:** High-LET ion traversing adjacent storage cells.
- **Parameters:** Target buffer, start byte, length (2..8 bytes), bit mask.

### Class C: Single Event Transient (SET) — Arithmetic Glitch
- **Mechanism:** Perturbing the output of an arithmetic operation (e.g., modular addition $c = (a + b) \pmod q + \delta$).
- **Physical Analogue:** Voltage spike in combinatorial adder/multiplier logic latching into a pipeline stage.
- **Parameters:** Injection point (e.g., NTT butterfly step), perturbation magnitude $\delta \in \mathbb{Z}_q$.

### Class D: Persistent / Stuck-at Fault
- **Mechanism:** Forcing a specific memory location or coefficient to remain constant (0x00, 0xFF) across multiple read/write cycles.
- **Physical Analogue:** Hard micro-latchup or permanent displacement damage in a storage cell.

### Class E: Single Event Functional Interrupt (SEFI) — Control Flow Disruption
- **Mechanism:** Skipping an instruction, forcing a branch inversion (e.g., branch condition `if (norm > bound)` forced false), or corrupting loop indices.
- **Physical Analogue:** Control register upset or program counter glitch.
