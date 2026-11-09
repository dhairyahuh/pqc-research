# Fault Injection Methodology & Taxonomy

## 1. Threat Model
In low Earth orbit (LEO) and deep-space missions, galactic cosmic rays and trapped protons deposit ionizing charges into semiconductor junctions, causing single-event upsets (SEUs).

Our study models single-bit and double-bit flips in the volatile memory structures supporting post-quantum cryptographic primitives:
1. **Twiddle Factor Tables (`zetas`):** Read-only constant lookup tables loaded into volatile SRAM during initialization.
2. **Intermediate Butterfly Operands:** Dynamic arithmetic registers during layer-by-layer Cooley-Tukey transformations.
3. **Decapsulation Predicate Registers:** Control flow flags governing the Fujisaki-Okamoto re-encryption comparison.

## 2. Injection Taxonomy & Hook Architecture
Software fault injection is implemented via hook functions in [`algorithms/source_ref/mlkem_fault_hooks.c`](file:///Users/dhairyajain/Desktop/pqc%20research/algorithms/source_ref/mlkem_fault_hooks.c):
- **Gate A (Pre-computation / Constant Corruption):** Targets the 128 active coefficients of `zetas`. Emulates an SEU in constant memory before execution.
- **Gate B (Transient Computation Glitch):** Targets butterfly accumulator variables mid-NTT loop.
- **Gate C (Control Flow / Predicate Bypass):** Inverts comparison predicates in Fujisaki-Okamoto verification.

## 3. Mandatory Research Protocol Rules
- Software-injected faults are explicitly distinguished from physical accelerator beam tests.
- Zero silent faults: all injection runs log exact injected bit indices, pre-fault values, post-fault values, and cryptographic outcomes to structured CSV trial ledgers.

