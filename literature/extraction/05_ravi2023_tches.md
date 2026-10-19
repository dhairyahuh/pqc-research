# Literature Extraction: Ravi et al. (2023) — IACR TCHES

**Extraction Date:** 2026-10-17  
**Reviewer:** Automated Research Auditor (Anti-Hallucination Protocol)  
**Verification Level:** `[DIRECTLY OBSERVED FROM FULL TEXT PDF]`  
**Source PDF:** `literature/p1_papers/TCHES2023_2_16.pdf`

---

## 1. Bibliographic Identity
- **Exact Title:** Fiddling the Twiddle Constants - Fault Injection Analysis of the Number Theoretic Transform
- **Authors:** Prasanna Ravi, Bolin Yang, Shivam Bhasin, Fan Zhang, Anupam Chattopadhyay
- **Venue:** IACR Transactions on Cryptographic Hardware and Embedded Systems (TCHES)
- **Publication Details:** Vol. 2023, No. 2, pp. 447–481
- **DOI:** `10.46586/tches.v2023.i2.447-481`
- **Page Count:** 35 pages
- **Completeness:** Full journal/conference transaction paper.

---

## 2. Research Question and Problem Addressed
- **Problem:** Cryptographic implementations of lattice-based schemes (Kyber, Dilithium) rely on pre-computed twiddle factor tables stored in memory. Existing fault attacks predominantly target polynomial coefficients, control loops, or hashing routines.
- **Goal:** Investigate whether faulting the twiddle factor constants or their memory pointers during NTT execution can bypass known fault countermeasures and enable full key recovery.

---

## 3. Cryptographic Algorithm and Parameters
- **Algorithms:** NIST standardization winners:
  - Kyber (Kyber-512, Kyber-768, Kyber-1024) — IND-CCA KEM
  - Dilithium (Dilithium2, Dilithium3, Dilithium5) — Digital Signature
- **Implementation Library:** `pqm4` library optimized for ARM Cortex-M4.

---

## 4. Fault Model and Attacker Assumptions
- **Model:** Physical Electromagnetic Fault Injection (EMFI) and simulated memory corruption.
- **Target Mechanism:** Faulting the twiddle pointer $T \to T^*$ during pointer loading from Flash/RAM so that the pointer addresses an array filled with zeros (Condition 1 & 2, Section 4.2, p. 14).
- **Effect:** Zeroization of twiddle constants across NTT execution stages.

---

## 5. Fault Location, Duration, Multiplicity, and Activation
- **Location:** Pointer registers holding the base address of the twiddle factor table, or persistent memory containing twiddle constants.
- **Timing:** Injected precisely at the instruction loading the twiddle table pointer before the NTT loop.
- **Duration:** Transient fault on pointer register, leading to persistent zeroization of twiddle factors throughout the transform execution.

---

## 6. Injection Method
- **Method:** Physical EMFI using an electromagnetic probe placed over an STM32F407 ARM Cortex-M4 microcontroller (Section 7.1, p. 24).
- **Validation:** Supported by real physical EM fault injections with oscilloscope visual trigger confirmation (Fig. 6, p. 25).

---

## 7. Detection Mechanism and Countermeasures Discussed
- **Paper Nature:** **Attack and vulnerability analysis.**
- **Countermeasures Evaluated (Section 8, pp. 30–31):**
  - *Implementation-level:*
    1. Jitter / horizontal noise.
    2. On-the-fly computation of twiddle factors (avoids tables, but heavy latency penalty).
    3. Twiddle pointer integrity checks (parity, redundant loads).
  - *Algorithmic-level:*
    1. Sanity checking of twiddle array: Verifying that sampled twiddles satisfy $\omega^n \equiv 1 \pmod q$ and $\omega^{n/2} \equiv -1 \pmod q$.
    2. Output entropy check: Detecting collapse in polynomial output distribution.
- **Mathematical Invariant Checking:** Not evaluated by Ravi et al.

---

## 8. Action on Error: Detection, Correction, or Recovery
- The paper demonstrates successful attacks and bypass of countermeasures; countermeasures are proposed conceptually in Section 8 without automated recovery or rollback.

---

## 9. Granularity of Defense
- Algorithmic sanity checking (pre-transform table validation) or transform output entropy testing.

---

## 10. Transform Coverage (Forward vs. Inverse NTT)
- Evaluates twiddle corruption on both forward NTT (in Kyber keygen, enc, dec; Dilithium sign) and inverse NTT (INTT).

---

## 11. Persistent State and Twiddle Factor Corruption
- **Central Focus:** This paper is the definitive reference establishing the severity of twiddle factor corruption.
- **Key Finding:** Zeroizing twiddle constants makes the NTT collapse into a repeated constant output, enabling 100% secret key recovery on Kyber-768 with a single faulty cipher/public key exchange.

---

## 12. Software-Only Realization
- **Evaluated:** Evaluated on pure software running on ARM Cortex-M4 (`pqm4` reference and optimized assembly).

---

## 13. Performance Overhead and Baselines
- Ravi et al. note that on-the-fly calculation of twiddle factors imposes an unacceptable latency overhead on embedded processors. Sanity checks on pointers are recommended as low-cost alternatives.

---

## 14. Experimental Statistics and Denominators
- **Attack Success Rate:** $100\%$ key recovery on Kyber-768 and Dilithium under physical EMFI (Section 7.3, pp. 25–28).
- **Countermeasure Bypass:** Proves that twiddle corruption completely bypasses:
  - `Verify_After_Sign`
  - `Verify_Loop_Abort`
  - `Verify_Add`
  - Shuffling countermeasures (Table 2 & 3, p. 29).

---

## 15. Reported Failure Modes and Limitations
- The attack requires the attacker to successfully redirect the twiddle pointer to an all-zero memory block or flip bits in the twiddle array.

---

## 16. Security Claims and Exclusions
- Highlights that high-level algorithm-level checks (like verifying signatures after signing) fail when the transform itself is distorted in a manner that produces validly signed but key-leaking output.

---

## 17. Direct Comparison with Our Research
| Feature | Ravi et al. (2023) | Our Work (Paper Track 1 / Track 3) |
|:---|:---|:---|
| **Focus** | Fault Injection Attack (EMFI) | Software Detection & Localized Rollback |
| **Twiddle Corruption** | Demonstrated full key recovery | Analyzed defense boundary & invariant blindness |
| **Local Invariant Response** | Not tested | Proved: Local CT/GS invariants exhibit **0.0% detection** (Blindness) |
| **Cryptographic Containment** | Concludes attack succeeds | Discovered: Outer Fujisaki-Okamoto (FO) check detects corruption $\to$ **Implicit Rejection (0 SDC)** |
| **Target Architecture** | ARM Cortex-M4 (32-bit) | ARM64 (Apple M1) / x86_64 C99 |

---

## 18. What the Paper Does NOT Establish
- Does not analyze whether butterfly-level algebraic invariants can detect twiddle table corruption.
- Does not investigate whether Fujisaki-Okamoto decapsulation suppresses SDC under persistent twiddle corruption.
- Does not provide an in-place software recovery mechanism.

---

## 19. Unresolved Questions
- If twiddle factors are corrupted in RAM/Flash rather than via pointer redirection, does the outer FO check in ML-KEM always prevent key recovery? (Our experimental data in Track 3 demonstrates that FO implicit rejection completely catches corrupted twiddle factors, preventing plaintext/key leakage).

---

## 20. Traceable Citation Quotes
- *On twiddle vulnerability (p. 448, col. 1):* "In this work, we demonstrate the criticality of twiddle constants used in the computation of the Number Theoretic Transform (NTT), a core arithmetic operation used in several post-quantum cryptographic schemes."
- *On countermeasure bypass (p. 475, col. 2):* "Thus, we can see that all existing fault countermeasures for the signing procedure are orthogonal to our attack, and can thus be easily bypassed with our Sign_Fault_NTT_Y attack."
- *On sanity checking (p. 476, col. 2):* "To check whether $\omega^n = 1$, one can pick $t$ twiddle factors at random such that their product is expected to be $\omega^n = 1$. If the comparison passes successfully, only then do we proceed with the NTT operation."
