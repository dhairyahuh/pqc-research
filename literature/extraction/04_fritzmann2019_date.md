# Literature Extraction: Fritzmann et al. (2019) — IEEE DATE

**Extraction Date:** 2026-10-17  
**Reviewer:** Automated Research Auditor (Anti-Hallucination Protocol)  
**Verification Level:** `[DIRECTLY OBSERVED FROM FULL TEXT PDF]`  
**Source PDF:** `literature/p1_papers/Towards_Reliable_and_Secure_Post-Quantum_Co-Processors_based_on_RISC-V.pdf`

---

## 1. Bibliographic Identity
- **Exact Title:** Towards Reliable and Secure Post-Quantum Co-Processors based on RISC-V
- **Authors:** Tim Fritzmann, Uzair Sharif, Daniel Müller-Gritschneder, Cezar Reinbrecht, Ulf Schlichtmann, Johanna Sepulveda
- **Venue:** 2019 Design, Automation & Test in Europe Conference & Exhibition (IEEE/ACM DATE 2019)
- **Publication Details:** March 2019, Florence, Italy, pp. 1148–1153
- **DOI:** `10.23919/DATE.2019.8715104`
- **Page Count:** 6 pages
- **Completeness:** Full conference paper.

---

## 2. Research Question and Problem Addressed
- **Problem:** Embedded IoT devices implementing post-quantum cryptography on RISC-V SoCs face both random physical soft errors (reliability) and deliberate fault injection attacks (security). Dedicated hardware accelerators for NTT and Keccak speed up execution, but need systematic resilience evaluation.
- **Goal:** Quantify the vulnerability of NTT routines to random soft errors and adversarial register manipulation, and evaluate software/hardware redundancy countermeasures.

---

## 3. Cryptographic Algorithm and Parameters
- **Algorithm:** NewHope (Ring-LWE key exchange).
- **Parameters:** Evaluated for $n=512$ and $n=1024$, modulus $q=12289$.

---

## 4. Fault Model and Attacker Assumptions
- **Dual Perspective:**
  1. *Reliability Model:* Random soft errors modeled as transient bit-flips occurring in CPU registers and execution pipeline during NTT execution.
  2. *Adversarial Fault Attack Model:* Targeted laser/EM/clock glitch forcing output coefficients to zero during the post-processing scaling of inverse NTT ($NTT^{-1}$).

---

## 5. Fault Location, Duration, Multiplicity, and Activation
- **Reliability:** Random bit-flips injected across processor core registers and ALU datapath during NTT routine execution.
- **Attack:** Targeted bit-flips or stuck-at faults injected into registers `R19` and `R20` during the final scaling loop of $NTT^{-1}$ where coefficients are multiplied by $n^{-1}$ (Section VI-B, p. 5).
- **Duration:** Transient single-cycle bit-flips.

---

## 6. Injection Method
- **Method:** Simulation-based fault injection using a multi-level instruction-set/RTL simulator of a 32-bit RISC-V processor (Section VI-A, p. 4).
- **Sample Size:** 10,000 fault injection experiments per NTT variant (NTT with LUT vs. arithmetic NTT).

---

## 7. Detection Mechanism and Mathematical Invariant
- **Mechanism:** **Dual Modular Redundancy (DMR).**
- **Technique:** Duplicates the execution of the NTT routine and compares the final outputs.
- **Mathematical Invariant:** None. No arithmetic or algebraic relationship within the butterfly is checked; protection is achieved via macro-level duplication and comparison.

---

## 8. Action on Error: Detection, Correction, or Recovery
- **Action:** Detection and re-execution at the routine level.
- **Recovery:** Full-routine re-execution. If the two DMR executions disagree, an error is signaled and the routine restarts or aborts. No localized or in-place rollback.

---

## 9. Granularity of Defense
- **Granularity:** Coarse algorithm / entire NTT routine level.
- **Rollback:** Whole-routine re-execution ($2\times$ execution overhead).

---

## 10. Transform Coverage (Forward vs. Inverse NTT)
- **Evaluated:** Both forward NTT and inverse NTT ($NTT^{-1}$) are implemented on the RISC-V co-processor.
- **Specific Attack Focus:** The adversarial fault attack specifically targets the inverse NTT post-processing multiplication by $n^{-1}$ to force zero coefficients.

---

## 11. Persistent State and Twiddle Factor Corruption
- **Addressed?:** **No.**
- **Details:** Twiddle factors are stored in BRAM. Random bit-flips are injected into processor registers during execution, not persistent table memory.

---

## 12. Software-Only Realization
- **Evaluated?:** Evaluates both software execution on RISC-V and hardware acceleration in an NTT coprocessor. The fault injection resilience study in Section VI-A focuses on software execution of the NTT on the RISC-V core.

---

## 13. Performance Overhead and Baselines
- **DMR Overhead:** Execution redundancy roughly doubles latency ($>2.0\times T_0$, $+100\%$ to $+135\%$ overhead).
- **Hardware Acceleration:** Hardware NTT accelerator achieves $84\times$ speedup over software execution on RISC-V (Table IV, p. 6).

---

## 14. Experimental Statistics and Denominators
- **Reliability Findings (10,000 trials per variant, Table II, p. 4):**
  - Unprotected Soft Error Vulnerability:
    - Micro-architecture Masking ($\mu\text{AM}$): $77.8\%$ (NTT-LUT), $78.8\%$ (NTT)
    - Application Masking (AM): $17.2\%$, $17.5\%$
    - Silent Data Corruption (SDC): $4.96\%$ (NTT-LUT), $3.66\%$ (NTT)
  - DMR Effectiveness:
    - DMR detected 168 out of 208 SDC scenarios ($80.77\%$ detection rate).
    - Residual SDC rate dropped to $0.72\%$ (NTT-LUT) and $0.80\%$ (NTT).

---

## 15. Reported Failure Modes and Limitations
- DMR does not catch common-mode faults (19.23% of SDCs bypassed DMR because faults corrupted state visible to both runs or control structures).
- Full routine re-execution introduces severe latency and energy penalties in resource-constrained IoT nodes.

---

## 16. Security Claims and Exclusions
- Identifies that zeroizing outputs in inverse NTT destroys LWE security by eliminating the error term.
- Recommends DMR as a generic defense but notes its substantial overhead.

---

## 17. Direct Comparison with Our Research
| Feature | Fritzmann et al. (2019) | Our Work (Paper Track 1) |
|:---|:---|:---|
| **Cryptosystem** | NewHope ($n=512/1024, q=12289$) | NIST FIPS 203 ML-KEM-768 ($n=256, q=3329$) |
| **Detection Method** | Dual Modular Redundancy (DMR) | Fine-grained algebraic invariant checking |
| **Recovery Mechanism** | Full-routine re-execution | Localized 1-butterfly register rollback |
| **Latency Overhead** | $>+100\%$ (DMR execution duplication) | $+16.9\%$ (`-O3`) / $+25.3\%$ (`-O2`) |
| **SDC Detection Rate** | $80.77\%$ under random soft errors | $100\%$ ($0/300$ SDCs, one-sided CI upper bound $<1.26\%$) |
| **Memory Overhead** | $2\times$ memory footprint for duplicate run | Zero dynamic heap, $+48$ bytes static BSS |

---

## 18. What the Paper Does NOT Establish
- Does not explore arithmetic or algebraic invariant checking.
- Does not demonstrate fine-grained rollback.
- Does not evaluate ML-KEM or FIPS 203 parameters.
- Does not investigate twiddle factor memory corruption or protocol-level FO containment.

---

## 19. Unresolved Questions
- Why did DMR only achieve an $80.77\%$ detection rate against soft errors? (Paper notes common registers and control dependencies remained unprotected).

---

## 20. Traceable Citation Quotes
- *On soft error classification (p. 4, col. 2):* "The DMR was able to detect 168 out of 208 SDC scenarios thus resulting in a SDC detection rate of 80.77%. The effective SDC rates for NTT-LUT and NTT drop down to 0.72% and 0.8% respectively."
- *On attack on inverse NTT (p. 5, col. 1):* "Let us assume an attacker who is able to inject faults in the post processing multiplication of the NTT^-1 operation... when the output coefficients of the NTT^-1 are forced to zero, an attacker can directly read out the secret key."
