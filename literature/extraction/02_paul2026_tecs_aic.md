# Literature Extraction: Paul et al. (2026) — ACM TECS (AIC)

**Extraction Date:** 2026-10-17  
**Reviewer:** Automated Research Auditor (Anti-Hallucination Protocol)  
**Verification Level:** `[DIRECTLY OBSERVED FROM FULL TEXT PDF]`  
**Source PDF:** `literature/p1_papers/3822512.pdf`

---

## 1. Bibliographic Identity
- **Exact Title:** Efficient Error Detection for NTT Using Algebraic Invariants (AIC) Checking for PQC and FHE on FPGA
- **Authors:** Rourab Paul, Paresh Baidya, Swagata Mandal, Krishnendu Guha
- **Venue:** ACM Transactions on Embedded Computing Systems (ACM TECS)
- **Publication Details:** Vol. 25, No. 4, Article 70, Publication date: July 2026, 20 pages
- **DOI:** `10.1145/3822512`
- **Page Count:** 20 pages (Article 70:1–70:20)
- **Completeness:** Full peer-reviewed transaction paper.

---

## 2. Research Question and Problem Addressed
- **Problem:** NTT is the primary bottleneck in PQC (Kyber, Dilithium) and FHE (BGV, CKKS). Physical and intentional fault injection attacks (clock/EM/laser glitches) corrupt NTT processing elements (PEs), causing key/message leakage or system failure. Prior countermeasures either protect only the multiplier (leaving adders/subtractors vulnerable) or incur massive hardware duplication overhead.
- **Goal:** Design concurrent, lightweight algebraic invariant checking (AIC) for the NTT PE that protects all three arithmetic blocks: multiplier, adder, and subtractor.

---

## 3. Cryptographic Algorithm and Parameters
- **Algorithms:** Evaluated across multiple PQC and FHE parameter sets (Table 2, p. 16):
  - Kyber-512 ($n=256, q=3329$)
  - Kyber-768/1024 ($n=256, q=3329$)
  - Dilithium ($n=256, q=8380417$)
  - FHE parameters ($n=1024, 2048, 4096; q \approx 2^{12}$ to $2^{54}$)

---

## 4. Fault Model and Attacker Assumptions
- **Fault Model:** Transient and permanent bit-flip faults (random $\eta$-bit flipping and burst flipping) targeting PE arithmetic components (Section 5.3, pp. 15–18).
- **Adversary Capability:** Attacker capable of injecting single or multiple bit faults into PE arithmetic operations (adder, subtractor, Barrett multiplier).

---

## 5. Fault Location, Duration, Multiplicity, and Activation
- **Target Locations:** Arithmetic components of the NTT Processing Element:
  - $\log q$-bit Barrett multiplier (`mult`)
  - $\log q$-bit modular adder (`add`)
  - $\log q$-bit modular subtractor (`sub`)
- **Duration:** Transient single-cycle faults and permanent stuck-at faults.
- **Multiplicity:** Evaluated for $\eta = 1$ to $11$ faulty bits (random and burst) (Tables 3 & 4, pp. 17–18).

---

## 6. Injection Method
- **Method:** Simulation and emulation-based fault injection on FPGA using Python-driven testbenches and Vivado hardware co-simulation (Section 5.3, p. 15).
- **Sample Size:** 1.5 million fault injection trials per configuration (Table 4 footnote, p. 18).

---

## 7. Detection Mechanism and Mathematical Invariant
- **Schemes:** Full Recomputation AIC (FR-AIC) and Partial Recomputation AIC (PR-AIC).
- **Mathematical Invariant Formulation (Section 3.1, pp. 9–10):**
  - Considers the Cooley-Tukey (CT) butterfly outputs:
    $$\alpha[k] = (U + V) \bmod q$$
    $$\alpha[k+m] = (U - V') \bmod q$$
    where $U = \alpha[k]$, $V = \alpha[k+m] \cdot \omega \bmod q$, and $V'$ is computed via a duplicate/backup multiplier (`mult_AIC`).
  - Defines invariants:
    $$E_1 = (U + V) + (U - V') \equiv 2U \equiv 2\alpha[k] \pmod q$$
    $$E_2 = (U + V) - (U - V') \equiv 2V \equiv 2(\alpha[k+m] \cdot \omega) \pmod q$$
  - Verification: Since dividing by 2 in $\mathbb{Z}_q$ requires modular division, the hardware simply inspects bits $E_1[\log q : 1] == \alpha[k]$ (or $E_2[\log q : 1] == \alpha[k+m] \cdot \omega$) by discarding the least significant bit (taking advantage of bit-shift division when unreduced sum is preserved in $\log q + 1$ bits, Algorithm 2, p. 10).
  - Memory Alternation: Checks $E_1$ when memory index $k$ has $k[0]=1$ (odd), and checks $E_2$ when $k[0]=0$ (even), sharing a single checker unit across cycles.

---

## 8. Action on Error: Detection, Correction, or Recovery
- **Action:** **Detection only.**
- **Output:** Asserts `Fault = 1` signal (Algorithm 2, lines 18 & 22, p. 10).
- **Correction / Recovery:** **Explicitly NOT supported.**
  - Quoting Section 6 (p. 18): *"The present AIC model focuses on fault detection and does not perform fault correction. In future work, we plan to incorporate fault correction mechanisms, such as error correction algorithms and dynamic FPGA reconfiguration."*

---

## 9. Granularity of Defense
- **Granularity:** Processing Element (PE) butterfly hardware level.
- **Rollback:** None. No register saving, no butterfly recomputation, no in-place recovery. System must trigger global abort or external reconfiguration.

---

## 10. Transform Coverage (Forward vs. Inverse NTT)
- **Forward NTT (DIT / Cooley-Tukey):** Fully formulated, implemented, and analyzed (Algorithm 1 & 2).
- **Inverse NTT (DIF / Gentleman-Sande):** **NOT covered.**
  - INTT is mentioned only in passing on p. 8 as mathematical definition ($\alpha_j = \text{INTT}(\alpha)_j$).
  - Decimation-in-frequency (Gentleman-Sande) butterfly equations—where addition/subtraction precedes multiplication—are **never formulated, evaluated, or checked**.

---

## 11. Persistent State and Twiddle Factor Corruption
- **Addressed?:** **No.**
- **Analysis:** Twiddle factors are assumed to be stored in ROM/memory and fetched correctly. While zeroization fault attacks on twiddle factors are cited in the introduction, the AIC checks only verify that $(U+V) \pm (U-V')$ is algebraically consistent with the inputs supplied to the PE.
- **Blindness:** If twiddle factor $\omega$ is corrupted in memory, $V = \alpha[k+m] \cdot \omega^*$ and $V' = \alpha[k+m] \cdot \omega^*$. Both multipliers produce the same faulty value $V=V'$, so $E_1 = 2U$ and $E_2 = 2V'$ hold exactly. Thus, **Paul's AIC is mathematically blind to twiddle corruption**, though this limitation is not analyzed in their text.

---

## 12. Software-Only Realization
- **Evaluated?:** **No.**
- **Implementation:** Pure hardware on Xilinx Artix-7 FPGA (`xc7a100tcsg324-3`). Hardware structures include dedicated multipliers (`mult_AIC`), split multipliers (`mult_PAIC`), adder/subtractor checking blocks, and control logic.

---

## 13. Performance Overhead and Baselines
- **FPGA Overhead on Artix-7 (Table 2, p. 16):**
  - Area overhead: $\sim 28\%$ for FR-AIC, $\sim 15\%$ for PR-AIC.
  - Energy overhead: $\sim 4\%$.
  - Delay overhead: $0\%$ (no critical path clock frequency penalty due to pipelined checks).

---

## 14. Experimental Statistics and Denominators
- **Sample Size:** 1.5 million injected faults (Table 4, p. 18).
- **Detection Efficiency (Table 3 & 4):**
  - FR-AIC: $\approx 99.99\%$ detection across adder, subtractor, and multiplier.
  - PR-AIC: $96.15\%$ (1-bit adder), $97.91\%$ (1-bit sub), but only $23.18\%$ (1-bit mult) to $97.23\%$ (11-bit mult).

---

## 15. Reported Failure Modes and Limitations
- PR-AIC has significantly degraded detection rate for single-bit multiplier faults ($23.18\%$).
- Single-value differences in unreduced registers cannot be detected if they alias.
- Does not protect memory units, buses, or twiddle ROMs (reserved for future work, Section 6, p. 18).

---

## 16. Security Claims and Exclusions
- Protects PE arithmetic against transient and permanent faults.
- Excludes side-channel countermeasures and does not defend memory buses.

---

## 17. Direct Comparison with Our Research
| Feature | Paul et al. (2026) | Our Work (Paper Track 1) |
|:---|:---|:---|
| **Domain** | Hardware FPGA (Artix-7) | Software C99 (General Purpose CPU) |
| **Butterfly Coverage** | Forward Cooley-Tukey (CT) ONLY | Dual: Forward CT + Inverse Gentleman-Sande (GS) |
| **Recovery Mechanism** | None (Abort / Reconfigure) | Localized 1-butterfly register rollback |
| **Twiddle Corruption** | Blind (Unaddressed) | Evaluated (Twiddle blindness & FO containment) |
| **INTT Butterfly** | Not formulated | Explicit GS Invariant: $(A-B)\cdot \zeta \equiv \dots$ |
| **Overhead** | +28% LUTs / 0% clock delay (FPGA) | +16.9% decapsulation latency (`-O3`, M1) |

---

## 18. What the Paper Does NOT Establish
- Does not demonstrate software implementation or software overhead.
- Does not provide error recovery or rollback mechanisms.
- Does not formulate or test inverse NTT (Gentleman-Sande) invariants.
- Does not evaluate twiddle factor corruption or cryptographic protocol containment.

---

## 19. Unresolved Questions
- If Paul's AIC equations were ported directly to C software, what would the overhead be? (Recomputing $V'$ in software requires a second full Barrett multiplication per butterfly, substantially increasing register spills).
- How would their 1-bit shift test translate to software without hardware bit-slice slicing?

---

## 20. Traceable Citation Quotes
- *On invariant equations (p. 9, col. 2, Eq. 5–6):*
  $$E_1 = (U + V) + (U - V') \pmod q$$
  $$E_2 = (U + V) - (U - V') \pmod q$$
- *On lack of recovery (p. 18, col. 2, Sec. 6):*
  "The present AIC model focuses on fault detection and does not perform fault correction. In future work, we plan to incorporate fault correction mechanisms, such as error correction algorithms and dynamic FPGA reconfiguration."
- *On hardware scope (p. 18, col. 2, Sec. 6):*
  "Additionally, the current AIC approach exclusively targets PE operations. In future work, we will aim at covering other critical components, including memory and interconnect buses..."
