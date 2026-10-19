# Literature Extraction: Sarker et al. (2023) — IEEE TCAD

**Extraction Date:** 2026-10-17  
**Reviewer:** Automated Research Auditor (Anti-Hallucination Protocol)  
**Verification Level:** `[DIRECTLY OBSERVED FROM FULL TEXT PDF]`  
**Source PDF:** `literature/p1_papers/Error_Detection_Architectures_for_Hardware_Software_Co-Design_Approaches_of_Number-Theoretic_Transform (2).pdf`

---

## 1. Bibliographic Identity
- **Exact Title:** Error Detection Architectures for Hardware/Software Co-Design Approaches of Number-Theoretic Transform
- **Authors:** Ausmita Sarker, Alvaro Cintas Canto, Mehran Mozaffari Kermani, Reza Azarderakhsh
- **Venue:** IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems (IEEE TCAD)
- **Publication Details:** Vol. 42, No. 7, July 2023, pp. 2418–2422
- **DOI:** `10.1109/TCAD.2022.3218614`
- **Page Count:** 5 pages (pp. 2418–2422)
- **Completeness:** Full peer-reviewed transaction paper.

---

## 2. Research Question and Problem Addressed
- **Problem:** NTT is computationally intensive for lattice-based cryptography (e.g., Kyber, NewHope). Hardware accelerators in HW/SW co-design platforms are vulnerable to physical fault injection attacks (clock glitches, laser, voltage drops) that induce computational errors and bypass cryptography.
- **Goal:** Develop low-overhead concurrent error detection (CED) architectures for the polynomial multiplication / NTT accelerator without doubling execution time.

---

## 3. Cryptographic Algorithm and Parameters
- **Algorithm:** Number-Theoretic Transform (NTT) for lattice-based cryptography.
- **Parameters Evaluated:** $n = 512, q = 12289, k = 3$ (Table I, p. 2421).
- **Target Cryptosystems:** Mentioned Kyber and NewHope in the abstract, but parameterization tested ($n=512, q=12289$) matches NewHope/earlier lattices, *not* standard NIST FIPS 203 ML-KEM-768 ($n=256, q=3329$).

---

## 4. Fault Model and Attacker Assumptions
- **Model:** Stuck-at fault model (stuck-at-0 and stuck-at-1).
- **Multiplicity:** Single-bit, two-bit, and multiple-bit faults injected at the inputs of the operations.
- **Adversary Capability:** Attacker injecting transient or permanent faults to cause mathematical divergence in the NTT output.

---

## 5. Fault Location, Duration, Multiplicity, and Activation
- **Location:** Accelerator input registers $A, B, C, D$ and the internal modular multiplier/adder/subtractor datapath (Section III, pp. 2419–2420).
- **Duration:** Evaluates both permanent and transient fault models in simulation.
- **Multiplicity:** 1-bit, 2-bit, multi-bit.
- **Activation:** Active during polynomial loading and modular reduction stages.

---

## 6. Injection Method
- **Method:** Simulated fault injection using VHDL testbenches in Xilinx Vivado (Section IV-A, p. 2420).
- **Physical Validation:** No physical laser, electromagnetic, or beam testing. Strictly RTL/simulation-based injection.

---

## 7. Detection Mechanism and Mathematical Invariant
- **Technique:** Recomputing with Encoded Operands (RENO) and recomputing with swapped operands.
- **Mathematical Principle:**
  - For multiplication operand $A$: Negates input $A$ modulo $q$ ($A' = -A \bmod q$), performs multiplication with twiddle factor in RAM2 ($V' = -A \cdot \omega \bmod q$), and applies modular negation to the product. Checks whether $-(-A \cdot \omega) \equiv A \cdot \omega \pmod q$ (Section III-C, p. 2420).
  - For addition/subtractor lines $C$ and $D$: During the normal cycle, $out_3 = Reg_1 - Reg_2$ and $out_4 = Reg_1 + Reg_2$. In the RENO cycle, $Reg_2$ is negated modulo $q$, producing intermediate outputs $out'_3 = Reg_1 + Reg_2$ and $out'_4 = Reg_1 - Reg_2$. Swapping $out'_3$ and $out'_4$ allows direct comparison with the normal cycle outputs via comparators (Section III-D, p. 2420, Fig. 4).
- **Invariant Type:** Recomputation with operand negation/swapping (temporal/functional redundancy). Not an algebraic linear sum invariant across butterfly ports.

---

## 8. Action on Error: Detection, Correction, or Recovery
- **Action:** **Detection only.**
- **Output:** Asserts an error flag from the output comparators.
- **Correction / Recovery:** None. The architecture does not implement register rollback, single-butterfly retry, or mathematical error correction.

---

## 9. Granularity of Defense
- **Granularity:** Hardware accelerator register / processing line level (Registers A, B, C, D).
- **Rollback Capability:** Zero. When an error flag is asserted, the system must abort or re-run at the higher system/software level.

---

## 10. Transform Coverage (Forward vs. Inverse NTT)
- **Forward NTT:** Explicitly analyzed for forward NTT hardware accelerator pipeline.
- **Inverse NTT (INTT):** Mentioned in preliminary equations (Section II, p. 2419), but INTT-specific butterfly structures (such as Gentleman-Sande DIF) and scaling by $n^{-1}$ are *not* separately evaluated or protected in the hardware results.

---

## 11. Persistent State and Twiddle Factor Corruption
- **Addressed?:** **No.**
- **Analysis:** Twiddle factors are assumed to reside securely in on-chip RAM (`RAM2`, Section III-B, p. 2419). Faults are injected into operand registers ($A, B, C, D$), not into the twiddle factor tables or pointers. Twiddle blindness is not analyzed.

---

## 12. Software-Only Realization
- **Evaluated?:** **No.**
- **Note:** Despite "Hardware/Software Co-Design" in the paper title, the detection mechanism itself is 100% hardware logic (VHDL RTL: multiplexers, modular negators, pipeline registers, and comparators). The "co-design" refers to the host-accelerator partitioning, not software-level fault checking.

---

## 13. Performance Overhead and Baselines
- **FPGA Platforms:** Xilinx Zynq UltraScale+ (`XCZU4EG-FBVB900-1LV-I`) and Spartan-7 (`XC7S100FGGA676-1IL`) (Table I, p. 2421).
- **Reported Overhead:**
  - Area overhead: 12.74% (LUTs/FFs) for best-case RENO on B and A.
  - Delay overhead: 8.46%.
  - Power overhead: 7.62%.
- **Throughput Compensation:** Authors insert sub-pipelining registers to mitigate the $2\times$ latency penalty of recomputing cycles.

---

## 14. Experimental Statistics and Denominators
- **Trial Count:** 110,601 total injected faults (36,867 faults per scheme) across three architectures (Section IV-A, p. 2420).
- **Reported Error Coverage:**
  - Scheme III-B (RENO on D): 99.51%
  - Scheme III-C (RENO on B and A): 99.67%
  - Scheme III-D (Recomputing on C and D): 99.41%

---

## 15. Reported Failure Modes and Limitations
- Acknowledges that recomputing without pipelining doubles execution time ($2n$ cycles, p. 2421).
- Sub-pipelining increases area overhead.
- Does not address fault attacks targeting control logic, state machines, or memory address decoders.

---

## 16. Security Claims and Exclusions
- Protects against stuck-at faults and single/multi-bit transient disturbances during butterfly execution.
- Excludes side-channel leakage (power/EM analysis) and architectural manipulation of the host CPU.

---

## 17. Direct Comparison with Our Research
| Feature | Sarker et al. (2023) | Our Work (Paper Track 1) |
|:---|:---|:---|
| **Domain** | Hardware FPGA/ASIC (VHDL) | Pure Software C99 (AArch64/x86_64) |
| **Algorithm** | Generic NTT ($n=512, q=12289$) | NIST FIPS 203 ML-KEM-768 ($n=256, q=3329$) |
| **Detection Technique** | Recomputing with Negated Operands (RENO) | Algebraic invariant checking ($u+v, u-v$) |
| **Recovery** | None (Error flag assertion) | In-place single-butterfly register rollback |
| **INTT Coverage** | Unspecified / General | Explicit Gentleman-Sande (GS) invariant |
| **Twiddle Integrity** | Assumed uncorrupted | Characterized (Twiddle blindness & FO containment) |
| **Overhead** | +12.7% area, +8.5% delay (FPGA) | +16.9% decapsulation latency (`-O3`, M1) |

---

## 18. What the Paper Does NOT Establish
- Does not demonstrate software-level invariant monitoring.
- Does not demonstrate error recovery or rollback.
- Does not formulate invariants for Gentleman-Sande butterflies.
- Does not evaluate NIST FIPS 203 parameters.
- Does not investigate persistent twiddle factor corruption.

---

## 19. Unresolved Questions
- How would RENO perform if implemented in software (instruction overhead)?
- Would negation-based recomputation in software double the register pressure and memory spills?

---

## 20. Traceable Citation Quotes
- *On recomputation approach (p. 2419, col. 2):* "Our framework is based on constructing recomputing schemes, which incur low overhead and high error detection rate. We aim at detecting the presence of faults, both permanent and transient, on the most computationally exhaustive mathematical operations of the NTT accelerator architecture, i.e., the multiplication."
- *On recovery absence (p. 2421, col. 2):* "In this article, we present error detection schemes for the NTT found on HW/SW co-design constructions... Our schemes provide high error coverage and detect deviations due to fault injection."
