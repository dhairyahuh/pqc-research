# Phase 13 — Evidence Gaps: the missing bridge from software faults to physical radiation effects

To connect the present software experiments to physical radiation effects, every item below is
required and **currently absent** in this project. None of these may be invented.

1. **A specific target device/architecture.** The study runs on a developer Apple-silicon host; no
   radiation-relevant target (rad-hard/COTS part, FPGA, soft-core, SRAM/DRAM technology node) is
   chosen. Upset behavior is device- and technology-specific (Baumann2005; SRAM65_MBU). → MISSING.
2. **Device-specific radiation-effects data or a documented test setup.** No measured cross-sections,
   LET thresholds, SER, or beam/alpha test for any target device (JESD89 defines how such data is
   obtained; Normand1996/DoddMassengill2003 are general). We extracted/invented **no** numbers. → MISSING.
3. **A justified physical→software translation.** No method maps physical upsets (which structure,
   when, how many bits) to the software-visible fault distribution used in the campaigns. Whether an
   upset even becomes a visible error is workload/architecture dependent (Mukherjee2003 AVF;
   LEON3_MBU2025). → MISSING.
4. **Grounded distributions for bit multiplicity, persistence, timing, location.** The current model
   chooses these by fiat (single-bit, transient/persistent toggle, specific coefficient). No evidence
   fixes them for any device. MBU multiplicity is technology-specific (SRAM65_MBU). → MISSING.
5. **An operational/radiation environment model** (orbit, particle spectrum, shielding) if any rate
   or mission-exposure statement is made. None exists; no rate claims should be made. → MISSING.
6. **A validated fault-injection method with state-affected verification.** The Phase-11 prototype
   verifies read-back/consumption/restoration on a *model* `__DATA_CONST` table; the real `mlk_zetas`
   (in `__TEXT,__const`) was not injected, and no mapping to a physical structure exists. → PARTIAL
   (mechanism only, model) / MISSING for the real device.
7. **A clear separation of regimes.** Simulation vs software fault injection vs accelerated radiation
   testing vs deployment qualification are distinct; this project is **software fault injection
   only** and must not be described as any of the others. → must be stated (this phase does).

## Also unavailable (do not fabricate)
No laboratory/beam access, no radiation-test equipment, no device-vendor data, and no external
collaborators are available to this project. The physical bridge therefore **cannot** be built from
current resources; it would require new equipment/collaboration/data (Options C/D).
