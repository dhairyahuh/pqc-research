# Literature Extraction: Dodd & Massengill (2003) — IEEE TNS

**Extraction Date:** 2026-10-17  
**Reviewer:** Automated Research Auditor (Anti-Hallucination Protocol)  
**Verification Level:** `[DIRECTLY OBSERVED FROM FULL TEXT PDF]`  
**Source PDF:** `literature/p1_papers/Basic_mechanisms_and_modeling_of_single-event_upset_in_digital_microelectronics.pdf`

---

## 1. Bibliographic Identity
- **Exact Title:** Basic Mechanisms and Modeling of Single-Event Upset in Digital Microelectronics
- **Authors:** Paul E. Dodd, Lloyd W. Massengill
- **Venue:** IEEE Transactions on Nuclear Science (IEEE TNS)
- **Publication Details:** Vol. 50, No. 3, June 2003, pp. 583–602
- **DOI:** `10.1109/TNS.2003.813129`
- **Page Count:** 20 pages (pp. 583–602)
- **Completeness:** Full peer-reviewed invited review paper.

---

## 2. Research Question and Problem Addressed
- **Problem:** Ionizing radiation in space environments (cosmic rays, trapped protons, solar energetic particles) and terrestrial environments (alpha particles from packaging, atmospheric neutrons) creates transient electron-hole pairs in silicon, causing non-destructive single-event effects (SEE).
- **Goal:** Provide a comprehensive review of the physical mechanisms of charge generation, transport, collection, critical charge ($Q_{\text{crit}}$) thresholds, and modeling techniques for Single-Event Upsets (SEUs) and Single-Event Transients (SETs) in CMOS digital circuits.

---

## 3. Physical Mechanisms and Device Types
- **Physical Phenomena:**
  - Direct ionization by heavy ions (Linear Energy Transfer, LET).
  - Nuclear reactions / secondary recoil ions from protons and neutrons.
  - Funneling effect (distortion of electric field expanding charge collection).
  - Diffusion of carriers from outside the depletion region.
- **Circuit Types:** SRAMs, DRAMs, CMOS combinational logic, microprocessors.

---

## 4. Fundamental Fault Models and Definitions
- **Critical Charge ($Q_{\text{crit}}$):** The minimum amount of charge that must be collected at a sensitive circuit node to flip the logic state of that node:
  $$Q_{\text{crit}} = \int_0^{\tau} I_{\text{in}}(t) \, dt$$
  As supply voltage $V_{dd}$ and node capacitance $C$ scale down, $Q_{\text{crit}} \approx C \cdot V_{dd}$ decreases dramatically, increasing vulnerability (Section III, pp. 584–586).
- **Single-Event Upset (SEU):** A radiation-induced bit-flip in a bistable storage element (SRAM cell, latch, or flip-flop).
- **Single-Event Transient (SET):** A transient voltage pulse generated in combinational logic. An SET becomes an SEU if and only if it propagates to a latch and satisfies setup/hold times during the active clock edge ("electrical, logical, and temporal masking", Section V, pp. 589–590).
- **Multi-Cell Upset (MCU):** A single ionizing strike depositing charge across adjacent nodes, simultaneously flipping multiple bits.

---

## 5. Hardware Mitigation Techniques Reviewed (Section VI, pp. 591–593)
- **Device-level:** Silicon-on-insulator (SOI), epitaxial substrates, triple-well CMOS.
- **Circuit-level:** Resistor/capacitor decoupled memory cells (e.g. HIT cell), Dual-Interlocked Cell (DICE).
- **System-level:** Error Correcting Codes (ECC), Triple Modular Redundancy (TMR), Dual Modular Redundancy (DMR).

---

## 6. Relevance to Our Post-Quantum Cryptography Research
- **Distinction Between Architectural Faults and Radiation Physics:**
  - A software-level bit-flip model (such as flipping a bit in a C variable or CPU register) abstracts the *architectural manifestation* of an SEU that has already survived electrical, logical, and temporal masking and latched into an architectural register.
  - Software fault injection does **NOT** simulate:
    - Charge deposition or collection dynamics.
    - Node cross-talk or charge sharing causing Multi-Cell Upsets (MCUs).
    - Single-event transients in clock networks or asynchronous resets.
    - Power supply rail collapse or analog metastability.
- **Scientific Integrity Requirement:** Any claim in our manuscript linking software-level invariant monitoring to "space radiation resilience" must explicitly acknowledge this boundary. We demonstrate resilience against *architectural transient single-bit register perturbations*, not physical semiconductor-level radiation hardness.

---

## 7. Direct Comparison with Our Research
| Concept | Dodd & Massengill (2003) | Our Work (Paper Track 1) |
|:---|:---|:---|
| **Level** | Physical semiconductor physics & SPICE | Software runtime / algorithm level (C99) |
| **Fault Cause** | Ionizing heavy ions, protons, neutrons | Controlled software-simulated register mutations |
| **Mitigation Target** | Hardening silicon nodes, $Q_{\text{crit}}$, DICE | Hardening cryptographic NTT arithmetic pipelines |
| **Defensive Action** | Physical charge dissipation / ECC | Dual-transform algebraic invariants + rollback |
| **Scope of Claim** | Physical radiation tolerance | Algorithmic fault detection & containment |

---

## 8. What the Paper Does NOT Establish
- Does not address cryptographic algorithms or post-quantum schemes.
- Does not propose software-level algorithmic invariants.

---

## 9. Key Manuscript Guidance Derived from This Source
1. **Never claim physical radiation hardness:** Our C99 implementation on Apple M1 has never undergone proton beam or heavy-ion testing.
2. **Proper terminology:** Refer to our fault model as an *architectural single-event upset model* or *software register bit-flip model*, explicitly citing Dodd & Massengill to ground the connection.
3. **Multi-bit limitation:** In scaled nanometer CMOS, multi-cell upsets (MCUs) from charge sharing can produce correlated multi-bit errors. Our single-butterfly rollback must be characterized with respect to single-event vs. burst/correlated fault limits.

---

## 10. Traceable Citation Quotes
- *On SEU definition (p. 583, col. 1):* "Single-event upset (SEU) is radiation-induced errors in microelectronic circuits caused when charged particles (usually from the radiation environment in space) lose energy by ionizing the medium through which they pass, creating an electron-hole pair track."
- *On SET in logic (p. 589, col. 2):* "For an SET to result in an error in digital logic, three conditions must be satisfied: (1) the transient must be generated and collected with sufficient amplitude and duration to propagate through subsequent logic gates (electrical masking); (2) there must be an open logic path from the struck node to a latch or memory element (logical masking); and (3) the transient must arrive at the latch during the clock latching window (temporal masking)."
