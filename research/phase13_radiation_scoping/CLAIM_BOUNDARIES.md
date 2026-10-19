# Phase 13 — Claim Boundaries

## 1. Claims the current SOFTWARE study CAN support
- Under the specified software fault models and distribution F, the measured outcome counts and rates
  (Phase 2 memory, Phase 3 channel, Phase 4 combined) as recomputed from raw.
- A model-conditional, **largely structural** cross-layer interaction (Δ̂ conditional on F) and a
  **channel-masking** observation, framed as an instance of established fault masking/derating
  (Avizienis 2004; Mukherjee 2003), explicitly not recovery.
- No silent data corruption observed in the sampled memory model (with the one-sided bound stated as
  finite-sample, not zero risk).
- A reproducible fault-contract/oracle methodology, taxonomy, matched-seed design, and internal audit.

## 2. Claims the LITERATURE can support (about the systems THOSE SOURCES studied — not ours)
- Radiation-induced single-event effects (SEU/MBU/MCU/SEFI) occur in semiconductor memories/logic
  (Baumann2005; DoddMassengill2003), including at ground level from cosmic-ray neutrons (Normand1996).
- Soft-error rates and upset characteristics are **device-, technology-, and environment-specific**
  and are measured by standardized methods (JESD89); MBU multiplicity depends on technology node
  (SRAM65_MBU).
- Whether a physical upset becomes a software-visible error is **workload- and architecture-dependent**
  (AVF/derating — Mukherjee2003; LEON3_MBU2025).
These statements apply to the devices/tests in those papers, **not** to this project's host or build.

## 3. Claims that remain UNSUPPORTED for this project
- Any radiation resilience/hardness, SEU/MBU/SEFI tolerance, space qualification, or flight readiness.
- Any equivalence between this project's XOR/logical-value faults and a physical SEU.
- Any mapping of the software fault distribution to a specific upset rate, cross-section, particle
  fluence, device sensitivity, or orbital/radiation environment.
- Any cross-device or cross-technology extrapolation.
- That the persistent-storage arm has been demonstrated on the real SUT (it has not; Phase-11 model only).
- "Systematic review" of either the PQC-fault or radiation-effects literature (searches were targeted).
