# Literature Extraction: Paul et al. (2025) — arXiv:2508.03062v1 (REMO)

**Extraction Date:** 2026-10-17  
**Reviewer:** Automated Research Auditor (Anti-Hallucination Protocol)  
**Verification Level:** `[DIRECTLY OBSERVED FROM FULL TEXT PDF]`  
**Source PDF:** `literature/p1_papers/2508.03062v1.pdf`

---

## 1. Bibliographic Identity
- **Exact Title:** Lightweight Fault Detection Architecture for NTT on FPGA
- **Authors:** Rourab Paul, Paresh Baidya, Krishnendu Guha
- **Venue:** arXiv preprint (`arXiv:2508.03062v1 [cs.CR]`), under production/review
- **Publication Date:** August 2025 (CreationDate: 2025-08-06)
- **DOI:** `xxx/xxxx` (Not yet assigned / preprint)
- **Page Count:** 15 pages
- **Completeness:** Full manuscript preprint.

---

## 2. Research Question and Problem Addressed
- **Problem:** Cryptographic hardware accelerators performing NTT for Kyber are susceptible to fault injection attacks during Montgomery modular reduction and memory lookups. Existing recomputation methods require decoding stages or excessive hardware area.
- **Goal:** Design a lightweight recomputation-based fault detection module using modular offset encoding (REMO) combined with memory address checking (i-k and i-j redundancy checks) on FPGA.

---

## 3. Cryptographic Algorithm and Parameters
- **Algorithm:** NTT for Kyber (Kyber-512, Kyber-768, Kyber-1024), parameterized per FIPS 203 ($n=256, q=3329$).
- **Polynomial sizes and word widths:** $n=256$, modulus $q=3329$, word-wise reduction width $w=4$ or $8$ bits.

---

## 4. Fault Model and Attacker Assumptions
- **Fault Model:** Transient and permanent bit flips, skipping faults, and random modification of polynomial coefficients and twiddle factors in memory and datapath.
- **Adversary Assumptions:** Attacker able to inject faults into Montgomery reduction arithmetic or manipulate memory addressing lines during coefficient/twiddle retrieval.

---

## 5. Fault Location, Duration, Multiplicity, and Activation
- **Locations:**
  1. Montgomery reduction arithmetic logic in the Cooley-Tukey Butterfly Unit (CT-BU).
  2. Memory addressing lines for RAM (coefficient storage) and ROM (twiddle constant storage).
- **Duration:** Transient single-event upsets and permanent stuck-at faults.
- **Multiplicity:** Single and multi-bit faults ($\eta = 1$ to 8 bits).

---

## 6. Injection Method
- **Method:** Simulated fault injection via FPGA testbenches on Xilinx Artix-7 and Spartan-7 platforms.
- **Physical Validation:** Strictly simulated/emulated RTL injection; no physical laser or EM beam validation.

---

## 7. Detection Mechanism and Mathematical Invariant
- **Arithmetic Protection (REMO / MMRFD):**
  - Uses Modified Montgomery Reduction for Fault Detection (MMRFD, Algorithm 2, p. 6).
  - Divides $l$-bit operand $\alpha'$ into $w$-bit words: $aw_i = (\alpha'_{iw+w-1} \dots \alpha'_{iw})$.
  - Encodes operand with a modular offset: $aw_i^f = aw_i + K \cdot q$.
  - Montgomery reduction computes intermediate values $\gamma_i$ and $\gamma_i^f$.
  - By Lemma 1 (p. 5), the modular offset $K \cdot q$ cancels out upon Montgomery reduction modulo $q$:
    $$\gamma_i^f = \gamma_i + q \cdot t \implies \gamma_i^f \cdot R \bmod q = \gamma_i \cdot R \bmod q$$
  - A hardware comparator checks $\gamma_i == \gamma_i^f$. If unequal, asserts `mmrfd_fault = 1`.
- **Memory Protection (Section 3, pp. 8–10):**
  - RAM protection: $i-k$ Redundancy Checking (RC) verifies address sequence parity and valid bounds during coefficient access.
  - ROM protection: $i-j$ RC verifies address pointer integrity when loading twiddle factors from ROM.

---

## 8. Action on Error: Detection, Correction, or Recovery
- **Action:** **Detection only.**
- **Output:** Asserts `mmrfd_fault` or memory address error signals.
- **Correction / Recovery:** None. No rollback, instruction retry, or arithmetic repair is provided.

---

## 9. Granularity of Defense
- **Granularity:** Word-wise Montgomery reduction slice within the CT-BU, plus memory address decoders.
- **Rollback:** Zero. No local state restoration.

---

## 10. Transform Coverage (Forward vs. Inverse NTT)
- **Forward NTT:** Explicitly analyzed for Kyber forward NTT CT-BU.
- **Inverse NTT (INTT):** Mentioned in Section 3.1 regarding memory usage during decryption, but no specialized inverse butterfly invariant (Gentleman-Sande) is formulated for the arithmetic unit.

---

## 11. Persistent State and Twiddle Factor Corruption
- **Addressed?:** **Partially (Memory address level).**
- **Analysis:** Protects the *ROM addressing logic* (via $i-j$ RC, Section 3.2). Verifies that the pointer to the twiddle factor table is generated correctly.
- **Limitation:** Does *not* detect corruption *inside* the ROM cells themselves (e.g. if the stored twiddle constant itself is flipped in non-volatile memory or RAM). In that case, REMO still computes $aw_i \cdot \omega^*$ and $aw_i^f \cdot \omega^*$, which agree with each other, resulting in undetected twiddle corruption.

---

## 12. Software-Only Realization
- **Evaluated?:** **No.**
- **Implementation:** Pure FPGA hardware (Artix-7 / Spartan-7 RTL).

---

## 13. Performance Overhead and Baselines
- **FPGA Overhead:**
  - Area overhead: $\sim 14.5\%$ to $22.3\%$ LUTs depending on word size $w$.
  - Latency: Minimal clock cycle overhead due to pipelined word processing.

---

## 14. Experimental Statistics and Denominators
- **Fault Detection Efficiency (Table 6, p. 13):**
  - Varies from $50.7\%$ (for single-bit faults in small word sizes) to $100\%$ for multi-bit and higher word sizes.

---

## 15. Reported Failure Modes and Limitations
- Lower detection efficiency ($50.7\%$) when single-bit faults strike lower-order bits in narrow word configurations.
- Does not correct faults.
- High hardware resource requirements if scaling to many parallel PEs.

---

## 16. Security Claims and Exclusions
- Defends Montgomery reduction against computational faults and memory addressing manipulation.
- Does not defend against side-channel power/EM analysis.

---

## 17. Direct Comparison with Our Research
| Feature | Paul et al. (2025 REMO) | Our Work (Paper Track 1) |
|:---|:---|:---|
| **Domain** | Hardware FPGA RTL | Pure Software C99 (AArch64/x86_64) |
| **Arithmetic Check** | Modular offset Montgomery recomputation | Algebraic dual-butterfly sum invariants |
| **Recovery** | None (Fault flag) | Localized 1-butterfly register rollback |
| **Persistent Faults** | Memory address decoder parity | Twiddle table corruption characterization & FO failsafe |
| **INTT Butterfly** | Unformulated | Explicit GS invariant formulation |

---

## 18. What the Paper Does NOT Establish
- Does not evaluate software performance or software fault injection.
- Does not provide localized error recovery or rollback.
- Does not formulate algebraic invariants for Gentleman-Sande butterflies.
- Does not demonstrate end-to-end cryptographic containment in ML-KEM.

---

## 19. Unresolved Questions
- Could modular offset encoding ($+K\cdot q$) be adapted into software Montgomery reduction routines without branch or register spill penalties?

---

## 20. Traceable Citation Quotes
- *On REMO principle (p. 5, col. 2):* "In encoded form it calculates $(\alpha + k.q).\beta.R^{-1} \bmod q$. Both these result must be the same as $k.q.\beta.R^{-1} \bmod q$ term will be canceled out as $k$ and $R^{-1}$ are integers."
- *On fault action (Algorithm 2, lines 23–27, p. 6):* "if $\gamma_i \neq \gamma_i^f$ then $f_i \leftarrow 1$ else $f_i \leftarrow 0$ end if"
