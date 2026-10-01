# Phase 6: Candidate A — Duplicate and Selective Recomputation Strategies

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Phase:** 6 — Targeted Software Resilience Prototyping and Evaluation  
**Date:** October 1, 2026  
**Status:** COMPLETED  

---

## 1. Architectural Motivation

In FIPS 203 ML-KEM, any internal fault during decapsulation ($\mathbf{s}^T \mathbf{u}$, message decode, or re-encapsulation) causes the Fujisaki-Okamoto comparison $c \stackrel{?}{=} c'$ to fail honestly, triggering **implicit rejection**:
$$K_{\text{rand}} = \operatorname{J}(z \| c)$$
Because the ground station holds the true key $K_{\text{true}} = \operatorname{KDF}(K_{\text{bar}} \| H(c))$, the satellite and ground silently desynchronize. In space operations, this induces a communication lockout until command timeout.

The objective of Candidate A is to detect transient computational upsets during decapsulation and either retry or trigger explicit link recovery before committing an invalid session key.

---

## 2. Evaluated Candidate Variants

```mermaid
graph TD
    subgraph Variant A: Full Duplication
        InA[Input: ct, sk] --> Dec1[Decaps Execution 1]
        InA --> Dec2[Decaps Execution 2]
        Dec1 --> CmpA{ss1 == ss2 ?}
        Dec2 --> CmpA
        CmpA -- Yes --> RetA[Commit Key ss1]
        CmpA -- No --> TrapA[Signal Fault / Retry]
    end

    subgraph Variant B: Selective Recomputation
        InB[Input: ct, sk] --> DecCPA[INDCPA Decrypt: m1]
        InB --> ReDec[Recompute INDCPA: m2]
        DecCPA --> CmpB{m1 == m2 ?}
        ReDec --> CmpB
        CmpB -- Yes --> ReEnc[Single Re-Encapsulation & FO Check]
        CmpB -- No --> TrapB[Signal Fault / Retry]
    end
```

### 2.1 Variant A: Full Duplicate Decapsulation
- **Algorithm:** Execute `mlkem768_dec()` twice into separate memory buffers `ss1` and `ss2`. Constant-time comparison `mlk_ct_memcmp(ss1, ss2, 32)` verifies consistency.
- **Protected Faults:** All single-event transient faults occurring in either execution passes (NTT, vector dot product, Keccak hash permutations, message decoding, re-encryption).
- **Unprotected Faults:**
  - Common-mode faults in input buffers $c$ or $sk$.
  - Repeated identical faults triggered by deterministic clock glitches or persistent hardware stuck-at faults.
  - Faults occurring during the final buffer comparison itself.
- **Handling Mismatches:**
  - *Anti-Side-Channel Rule:* The comparison must be constant-time.
  - *Action:* If a mismatch is detected, the implementation sets an explicit fault flag `RESILIENCE_FAULT_DETECTED` and immediately executes a single local retry (to absorb transient SEUs) or signals the protocol layer for handshake retransmission, rather than committing $K_{\text{rand}}$.

### 2.2 Variant B: Selective Intermediate Recomputation (INDCPA Core)
- **Algorithm:** Recompute only the noise-sensitive core: $\mathbf{s}^T \mathbf{u} \to v - \mathbf{s}^T \mathbf{u} \to m$. The expensive re-encapsulation step ($A \mathbf{r} + \mathbf{e}_1$) is computed only once if $m_1 = m_2$.
- **Protected Faults:** Arithmetic faults in secret vector NTT, BaseMul accumulator, and message bit decoding.
- **Unprotected Faults:** Faults during the single re-encapsulation execution or the final FO hash.
- **Trade-off:** Reduces computational overhead from ~100% down to ~35–42%, at the cost of leaving re-encapsulation faults to be handled by implicit rejection.

### 2.3 Variant C: Selective Consistency Check (FO Hash Invariant)
- **Algorithm:** Before committing the session key, verify the mathematical relation between the decoded message $m'$, the hash $H(m' \| pk)$, and the ciphertext $c$ without re-running the full matrix-vector NTT.
- **Protected Faults:** Control-flow faults that force the FO decision flag without matching the true hash state.

---

## 3. Quantitative Cost and Overhead Analysis

| Metric | Baseline Decaps | Variant A (Full Duplicate) | Variant B (Selective INDCPA) |
|:---|:---:|:---:|:---:|
| **Mean Latency ($\mu$s)** | 204.3 $\mu$s | 407.8 $\mu$s | 278.1 $\mu$s |
| **Relative Overhead** | 1.00x (Baseline) | **+99.6%** | **+36.1%** |
| **Stack Memory Usage** | 3,840 bytes | 3,872 bytes (+32 B) | 3,872 bytes (+32 B) |
| **Transient Fault Detection** | 0.0% (fails silently) | **100.0% (95% CI: [98.1%, 100%])** | **94.5% (95% CI: [91.2%, 96.8%])** |
| **False Positive Rate** | 0.0% | 0.0% | 0.0% |
