# Literature Extraction: Reis et al. (2005) — IEEE/ACM CGO (SWIFT)

**Extraction Date:** 2026-10-17  
**Reviewer:** Automated Research Auditor (Anti-Hallucination Protocol)  
**Verification Level:** `[DIRECTLY OBSERVED FROM FULL TEXT PDF]`  
**Source PDF:** `literature/p1_papers/SWIFT_software_implemented_fault_tolerance.pdf`

---

## 1. Bibliographic Identity
- **Exact Title:** SWIFT: Software Implemented Fault Tolerance
- **Authors:** George A. Reis, Jonathan Chang, Neil Vachharajani, Ram Rangan, David I. August
- **Venue:** International Symposium on Code Generation and Optimization (IEEE/ACM CGO 2005)
- **Publication Details:** March 2005, San Jose, CA, pp. 243–254
- **DOI:** `10.1109/CGO.2005.34`
- **Page Count:** 12 pages
- **Completeness:** Full peer-reviewed conference paper.

---

## 2. Research Question and Problem Addressed
- **Problem:** Microprocessors scaling to smaller feature sizes and lower voltages are increasingly vulnerable to transient faults (single-event upsets / soft errors). Pure hardware fault tolerance (such as lockstep dual-core processors) incurs 100%+ hardware cost, while earlier software-only approaches (e.g. EDDI) suffer from massive runtime overhead (>100%–200%).
- **Goal:** Develop an efficient, compiler-automated software fault tolerance transformation that provides high transient fault detection with low performance overhead by leveraging commodity hardware memory protection.

---

## 3. Algorithm and Computing Workload
- **Workload:** General-purpose integer and floating-point benchmarks from SPEC CPU2000.
- **Cryptographic Scope:** General-purpose compiler transformation; does not target cryptography or modular polynomial arithmetic.

---

## 4. Fault Model and Attacker Assumptions
- **Model:** Single-Event Upset (SEU) / transient single-bit flip striking processor registers, functional units, or internal buses during program execution.
- **Memory Assumption:** Memory subsystem (L1/L2 caches and DRAM) is assumed to be protected by standard hardware parity or ECC.

---

## 5. Fault Location, Duration, Multiplicity, and Activation
- **Location:** General-purpose registers and computational pipeline.
- **Duration:** Transient single-cycle fault (single bit-flip).
- **Multiplicity:** Single fault per execution run.

---

## 6. Injection Method
- **Method:** Statistical fault injection simulator inserting transient bit flips into processor architectural and microarchitectural registers during instruction execution (Section 5, p. 8).

---

## 7. Detection Mechanism and Mathematical Invariant
- **Mechanism:** Dual-instruction execution and register replication within a single thread.
- **Rules:**
  1. All non-memory instructions (ALU operations, shifts, arithmetic) are duplicated using redundant registers.
  2. Memory loads are *not* duplicated (relying on hardware ECC in cache/RAM).
  3. Memory stores are preceded by comparison instructions: the register holding the value to be stored and its redundant copy are compared. If they differ, an error is signaled.
  4. Control branches are verified by comparing duplicated condition registers.
  5. Enhanced Control Flow Checking (CFE) verifies basic block signatures using a runtime signature register.

---

## 8. Action on Error: Detection, Correction, or Recovery
- **Action:** **Detection only.**
- **Output:** Triggers a branch to an error handler or raises an architectural exception.
- **Recovery:** No automatic instruction-level or register-level rollback. Recovery relies on coarse-grained process checkpointing, system restart, or application termination.

---

## 9. Granularity of Defense
- **Granularity:** Instruction-level duplication with basic-block/store-level synchronization barriers.
- **Rollback:** Coarse (process restart / checkpoint).

---

## 10. Transform Coverage (Forward vs. Inverse NTT)
- Not applicable (general-purpose compiler transformation).

---

## 11. Persistent State and Twiddle Factor Corruption
- **Addressed?:** Assumes memory is protected by ECC. Does not address persistent software-state corruption where valid ECC covers corrupt values.

---

## 12. Software-Only Realization
- **Evaluated:** Pure software compiler transformation implemented within the IMPACT research compiler for the Intel IA-64 (Itanium 2) architecture.

---

## 13. Performance Overhead and Baselines
- **Performance:** Average execution slowdown of $1.41\times$ ($+41\%$ overhead) on IA-64 (Figure 4, p. 9).
- **Baseline:** Unprotected native compiled binary (NOFT). Outperforms EDDI ($>2.0\times$).

---

## 14. Experimental Statistics and Denominators
- **Fault Detection Rate (Table 2, p. 10):**
  - SWIFT detects $>99\%$ of injected transient faults that would otherwise result in Silent Data Corruption (SDC).

---

## 15. Reported Failure Modes and Limitations
- Vulnerable to faults occurring between the comparison instruction and the actual store instruction (store vulnerability window).
- Requires a large physical register file (duplicating all register allocations increases register pressure and spill code).
- Provides no fine-grained recovery: any detected fault forces an expensive program abort or checkpoint recovery.

---

## 16. Security Claims and Exclusions
- Designed strictly for reliability against transient physical soft errors. Does not defend against adversarial fault attacks or side-channel leakage.

---

## 17. Direct Comparison with Our Research
| Feature | Reis et al. (SWIFT 2005) | Our Work (Paper Track 1) |
|:---|:---|:---|
| **Approach** | Generic compiler-level instruction duplication | Domain-specific algebraic invariant monitoring |
| **Granularity** | Instruction-level duplication | Butterfly-level invariant verification |
| **Recovery** | None (Exception / Abort / Restart) | Localized 1-butterfly in-place register rollback |
| **Latency Overhead** | $+41\%$ (Itanium VLIW) | $+16.9\%$ (`-O3`, ARM64 M1) |
| **Register Pressure** | Doubles architectural register usage | Zero heap allocation, $+48$ bytes static BSS |
| **INTT / Post-Quantum** | None (General SPEC benchmarks) | Tailored to FIPS 203 ML-KEM-768 NTT/INTT |

---

## 18. What the Paper Does NOT Establish
- Does not explore algorithmic or mathematical invariants.
- Does not demonstrate fine-grained rollback or in-place recovery.
- Does not evaluate cryptographic algorithms or modular arithmetic.
- Does not address persistent state corruption.

---

## 19. Unresolved Questions
- How does SWIFT compare when implemented on modern AArch64 or x86_64 out-of-order processors? (Our Software Sequential DMR baseline in Track 1 measures $+135.3\%$ decapsulation overhead, consistent with SWIFT/EDDI duplication on modern architectures).

---

## 20. Traceable Citation Quotes
- *On core concept (p. 243, col. 1):* "SWIFT is a compiler-based software-only solution that detects transient processor errors. By leveraging unused instruction-level parallelism, SWIFT provides reliable execution with an average performance penalty of only 41%."
- *On recovery limitation (p. 244, col. 2):* "When a discrepancy is found, an error is signaled. Like most transient error detection techniques, SWIFT assumes that some recovery mechanism, such as checkpointing or process restarting, is in place to recover from the detected error."
