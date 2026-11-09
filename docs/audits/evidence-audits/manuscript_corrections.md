# Manuscript Corrections and Refinement Guide

**Target File:** [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md)  
**Author:** Cryptographic Implementation Auditor & Paper Reviewer  
**Date:** October 2026  
**Status:** Verification of Applied Textual Refinements  

---

## 1. Summary of Manuscript Corrections Applied

The table below outlines the precise textual refinements applied to [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) to ensure complete alignment with source reality, prior-art literature, and experimental datasets:

| Section | Topic / Location | Previous Draft Text / Risk | Applied Correction & Technical Grounding | Status in `paper/manuscript.md` |
|:---|:---|:---|:---|:---:|
| **Abstract** | Scope & Contribution | Stated "first to propose NTT algebraic invariant checking." Overreached by ignoring Paul et al. (ACM TECS 2026). | Refined to: *"We design, implement, and empirically validate an end-to-end software-level fault-resilience architecture for ML-KEM-768... unifying dual forward and inverse transform monitoring with localized single-butterfly rollback."* | **Corrected** |
| **Section 1.1** | Prior Art Positioning | Implied prior art lacked any butterfly invariant checking. | Explicitly cites Paul et al. [P03] (ACM TECS 2026) for hardware Cooley-Tukey invariants, identifying their limitations: FPGA exclusivity, detection-only aborts, and lack of inverse GS monitoring. | **Corrected** |
| **Section 2.1** | Decapsulation Call Graph | Stated decapsulation runs Inverse NTT on $\mathbf{u}$ and Forward NTT on $\mathbf{s}$. | Corrected to FIPS 203 source reality: decapsulation runs **Forward NTT** on received ciphertext vector $\mathbf{u}$ (`indcpa.c:609`), while secret key $\hat{\mathbf{s}}$ is pre-transformed in NTT form and **never transformed**. | **Corrected** |
| **Section 3.1** | Multiplier Error Cancellation | Stated naive sum check $r_0 + r_1 = 2u$ is sufficient. | Added formal analysis proving that naive sum checking cancels multiplier errors $e_t$ completely; proved that decoupled difference checking ($r_0 - r_1 \equiv 2(v \cdot \zeta)$) is necessary to detect multiplier faults. | **Corrected** |
| **Section 3.2** | Inverse GS Invariant Form | Presented classical formulation $r_0 + \zeta r_1 \equiv 2u \pmod q$, which requires division in software. | Documented the decoupled software formulation: $r_0 \equiv u_{\text{saved}} + v_{\text{saved}} \pmod q$ and $r_1 \equiv (v_{\text{saved}} - u_{\text{saved}})\cdot \zeta \pmod q$, avoiding costly modular inversions. | **Corrected** |
| **Section 3.3** | Twiddle Blindness | Omitted local detection boundary for twiddle factors. | Added **Theorem 1 (Twiddle Factor Blindness)**, proving $0.0\%$ local detection probability and establishing outer FO re-encryption as a mandatory failsafe. | **Corrected** |
| **Section 4.1** | Operation Counting | Unverified butterfly count. | Verified line-by-line in `indcpa.c`: exactly 11 transforms (6 Forward CT + 5 Inverse GS) $\times 896$ butterflies = **9,856 total butterflies**. | **Corrected** |
| **Section 5.2** | Fault Model Qualification | Described Target $F5B$ ($t \leftarrow 0$) as physical hardware stuck-at fault. | Refined to: *"software force-value zeroing... an abstract software debug hook forcing intermediate outputs to zero,"* avoiding unsupported physical silicon claims. | **Corrected** |
| **Section 6.1** | SDC & Confidence Intervals | Claimed "zero SDC proved." | Added rigorous 95% Wilson score interval with continuity correction: $0.00\%$ observed rate, CI: $[0.00\%, 1.26\%]$. | **Corrected** |
| **Section 7** | Side-Channel & Constant-Time | Claimed recovery execution is certified constant-time. | Explicitly stated that active fault recovery introduces branching into the rollback path, qualifying constant-time claims to fault-free execution and recommending the design for non-adversarial reliability contexts. | **Corrected** |

---

## 2. Specific Verifications for Peer-Review Readiness

1. **Denominators and Trial Counts:**
   - Table 1: Exact $N = 11$ transforms, $9{,}856$ butterflies.
   - Table 2: Exact $N = 100$ trials for $F12$, $100$ for $F4$, $100$ for $F5A$, $100$ for $F5B$, $300$ active for $H2$, $100$ for KAT.
   - Table 3: Exact $N = 600$ trials ($100$ per target $T1$–$T6$) for $H1$.
   - Table 4: Exact $N = 2{,}000$ decapsulations with $5{,}000$ warmups.
2. **Oracle Dependencies:**
   - Valid keys verified against clean-room baseline ($K_{\text{valid}}$).
   - Rejection keys verified against standalone Keccak-f[1600] / SHAKE-256 oracle ($K_{\text{rej}}$ per FIPS 203 Section 7.3).
3. **Software DMR Comparison:**
   - Explicitly clarified that DMR overhead ($+135.3\%$ to $+149.0\%$) applies to single-threaded sequential software duplication, not hardware lockstep or multi-core parallel architectures.

---

## 3. Conclusion

All identified discrepancies between the implementation reality, literature, and manuscript draft have been reconciled. The resulting paper in [`paper/manuscript.md`](file:///Users/dhairyajain/Desktop/pqc%20research/paper/manuscript.md) is technically robust, mathematically rigorous, and ready for submission to target venues.
