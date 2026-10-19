# Phase 13 — Fault-Model Mapping (software models ↔ physical radiation effects)

Classes: **DIRECTLY SUPPORTED** · **PLAUSIBLE BUT UNVALIDATED** · **NOT EQUIVALENT** ·
**INSUFFICIENT EVIDENCE**. Evidence keys from `SOURCE_REGISTER.csv`. Overriding principle: a software
XOR is not an SEU just because both flip a bit — relating a physical event to a software-visible
fault requires device-specific upset characteristics, affected structure, spatial/temporal pattern,
architectural propagation, derating/observability, and workload dependence (Baumann2005;
DoddMassengill2003; Mukherjee2003; LEON3_MBU2025).

| Current/proposed software model | Closest physical effect | Classification | Why |
|---|---|---|---|
| Logical-value XOR of a **local/temporary** NTT value (Phase 2) | SEU in a register/operand being used | **NOT EQUIVALENT** | it mutates a transient C value, not a physical storage cell; no device, cross-section, structure, or persistence; nothing ties it to an SEU beyond "a bit changed" |
| **Persistent** corruption of the operational table backing store (proposed; Phase 11 model only) | SEU/MCU in the memory holding constants (SRAM/cache/DRAM, depending on runtime residency) | **PLAUSIBLE BUT UNVALIDATED** | corrupting real backing storage is a closer analogue, but which physical structure holds `mlk_zetas` at runtime, its cross-section, and upset multiplicity are unknown and device-specific (Baumann2005; SRAM65_MBU) |
| Single-bit corruption | SEU | **PLAUSIBLE BUT UNVALIDATED** | single-bit upsets are real (DoddMassengill2003) but their rate/location are device/environment specific (Normand1996; JESD89) — not represented here |
| Paired/"simultaneous" or multi-bit corruption (Phase 2 SIMULTANEOUS; future MBU) | MBU/MCU | **INSUFFICIENT EVIDENCE** | MBU multiplicity and spatial pattern depend strongly on technology node/layout (SRAM65_MBU; LEON3_MBU2025); no basis to choose a multiplicity/pattern without device data |
| Transient fault (clears on retry) | SEU correctable by re-read/re-write (soft error) | **PLAUSIBLE BUT UNVALIDATED** | JESD89 frames SEUs as typically correctable by rewrite, loosely matching "transient"; but our "transient" is a model toggle, not a scrub-interval-grounded process |
| Persistent fault (recurs every op) | stuck/un-scrubbed cell or hard error | **PLAUSIBLE BUT UNVALIDATED** | plausible analogue to an un-scrubbed upset/hard error; persistence timing not grounded in any scrub model |
| Execution-altering fault (wrong result) vs our hooks | SEU changing computed data | **PLAUSIBLE BUT UNVALIDATED** | whether a cell upset becomes a wrong *result* is governed by AVF/derating + workload (Mukherjee2003; LEON3_MBU2025) — not modeled here |
| (absent) execution interrupt/reset | **SEFI** | **INSUFFICIENT EVIDENCE / not modeled** | SEFIs (functional interrupt/reset) are a distinct, documented class with no analogue in the current experiments |
| Channel: corruption/loss/delay/dup/reorder/interruption (Phase 3) | — | **NOT EQUIVALENT** | these are transport/protocol phenomena, a different physical domain; not radiation-induced device upsets and not calibrated to any RF/channel physics |

## What the "most defensible" mapping would be
The **persistent-storage single-bit corruption of the operational table** is the only model with a
*plausible* (still unvalidated) physical analogue (an SEU/MCU in the memory holding the table). Even
it requires, to be validated: identifying the physical structure that actually holds `mlk_zetas`
during decapsulation on a named target device, that device's measured upset behavior, a derating/AVF
analysis for the ML-KEM workload, and a scrub/persistence model. None exist here.
