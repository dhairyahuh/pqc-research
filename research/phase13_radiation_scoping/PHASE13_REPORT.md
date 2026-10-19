# Phase 13 — Report (WP3 radiation-effects scoping)

## Verdict
**A defensible physical-radiation → software-fault connection does NOT currently exist for this
project, and cannot be built from current resources.** The literature firmly establishes that
radiation single-event effects are real but **device-, technology-, environment-, and
workload-specific**; the current software models are not grounded in any of that. This phase is a
scoping/mapping exercise and makes **no** radiation claim.

## Findings (confidence)
- **High confidence:** the logical-value XOR fault is **NOT EQUIVALENT** to an SEU; the channel-fault
  models are a different (transport) domain, **NOT EQUIVALENT** to radiation effects. (Baumann2005;
  DoddMassengill2003; Normand1996; JESD89 — all metadata/abstract only.)
- **Medium confidence:** a **persistent-storage single-bit corruption** of the operational table is
  the only model with a *plausible but unvalidated* physical analogue (an SEU/MCU in the memory that
  holds the table); multi-bit/MBU and SEFI are **insufficiently evidenced** to model without a target
  device (SRAM65_MBU; LEON3_MBU2025).
- **High confidence:** whether any physical upset becomes a software-visible error is governed by
  AVF/derating and workload (Mukherjee2003; LEON3_MBU2025) — a dependency this project has not
  characterized for any device.
- **No credible radiation↔ML-KEM-software mapping was found** in the targeted search; the nearest
  PQC items are hardware error-detection / FPGA fault-tolerance (application-level), not a physical→
  software fault model.

## Does the literature motivate a specific NEXT software experiment?
**Yes, modestly:** it supports making the memory fault act on **genuine backing storage** rather than
a temporary value (Option B) — the persistent-storage arm — because real-cell corruption is the only
model with a plausible physical analogue. The literature does **not** justify choosing a radiation
rate, environment, or multiplicity, so B must remain a **software** experiment, not a radiation one.

## Recommended next step + prerequisites
**Stage E now, then B.** Keep the paper software-only and attach this scoping as future work; then,
with approval, run the persistent-storage arm (Option B). Prerequisites for B: approved research-only
relocation of `mlk_zetas` to a writable-after-`vm_protect` section + disassembly verification that the
NTT reads the relocated symbol (Phase-11 DESIGN). Prerequisites for any later radiation work (C/D):
a named target device, its measured upset data, an AVF/derating mapping for the ML-KEM workload, and
beam/alpha access or collaborators — none currently available.

## Reconciliation of search counts
Interfaces queried: a general web search engine, the **Crossref API**, and publisher/standards pages
(incl. **jedec.org**). **Not** queried as databases: IEEE Xplore, NASA NTRS, ACM DL, SpringerLink,
DBLP, Scholar. Retrieval actions this phase: **5** (3 Crossref metadata lookups + 2 web searches).
Links surfaced across the two web searches: ~20; **screened** against the criteria; **retained 9** in
`SOURCE_REGISTER.csv` (3 Crossref-verified radiation refs: Baumann/Dodd&Massengill/Normand; the JESD89
standard; 2 MBU items; Mukherjee carried from Phase 9; 2 PQC-application items). **Full texts read: 0**
(all metadata/abstract only). Device-specific numeric radiation parameters extracted/invented: **0**.

## Unresolved
- No systematic coverage (IEEE Xplore/NTRS/Scholar not searched) → recall incomplete.
- Which physical structure holds `mlk_zetas` at runtime on any target device is unknown.
- Whether a validated AVF/derating mapping for the ML-KEM workload is achievable without beam access.
