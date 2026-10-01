# Phase 7 — Scope and Precise Threat Model

**Project:** Fault Resilience Analysis of Post-Quantum Cryptographic Implementations for Space Systems  
**Algorithm Target:** NIST FIPS 203 ML-KEM-768 (C Reference Implementation, `mlkem-native`)  
**Phase:** 7 — Targeted Layered Fault-Resilience Engineering  
**Baseline Hash:** `8974fe46ef5c02e780418517572abfe55556a423` (`origin/main`)

---

## 1. Central Research Question

> **Can a layered, low-overhead software protection architecture improve the detection and containment of implementation-level faults in ML-KEM-768, particularly faults that evade simple algebraic projection checks, without imposing the full cost of duplicate execution (+100%)?**

Phase 6 demonstrated that while basic software parity projections provide low runtime overhead (~1-2%), Phase 6B identified that they suffer from complete cancellation against symmetric arithmetic faults (`INTERMEDIATE_T`, twiddle factors $\zeta$) across all Cooley-Tukey NTT layers. Conversely, full duplicate execution (DMR) doubles computational and energy costs (+103%) while failing completely against pre-invocation input corruption and persistent stuck-at faults.

Phase 7 establishes a formal threat model and implements a four-layer software protection architecture to achieve comprehensive coverage without duplicate execution.

---

## 2. Threat Model: Fault Taxonomy & Assumptions

We explicitly distinguish **environmental Single-Event Upsets (SEU)** occurring randomly due to space radiation (heavy ions, galactic cosmic rays, solar energetic particles) from **adversarial Fault Injection Attacks (FIA)** (clock/voltage glitching, EMFI, laser injection). Software-level additive perturbations and bit flips are mapped to physical register and memory corruption.

### Taxonomy of Evaluated Fault Classes

| Fault Class | Injection Location | Physical Representation | Timing & Duration | Adversarial / Environmental Model | Cryptographic Consequence | Expected Countermeasure |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Class 1: Transient Arithmetic Faults** | Cooley-Tukey Butterfly ($t = r[j+\text{len}] \cdot \zeta$) | Additive glitch ($\Delta \in [1, 500]$) or single bit-flip | Transient (single butterfly clock cycle) | Single-Event Transient (SET) in ALU multiplier or glitch injection | Corrupted polynomial output $\hat{p}$, desynchronized session key | Layer 2: Complementary NTT (Weighted / Checkpoint) |
| **Class 2: Twiddle-Factor / MAC Faults** | ROM / Flash Twiddle Table (`mlk_zetas[k]`) | Single-bit flip in twiddle coefficient | Transient or read-cycle perturbation | Radiation strike on twiddle ROM or bus fetch error | Systematic polynomial distortion, faulty NTT representation | Layer 2: Weighted Invariant ($\zeta^{-1}$) |
| **Class 3: Single Output-Register Faults** | Butterfly Output Registers ($r'[j]$ or $r'[j+\text{len}]$) | Additive glitch ($\Delta$) or register bit flip | Transient (post-addition/subtraction) | Single-Event Upset (SEU) in register bank during write-back | Asymmetric polynomial perturbation | Layer 2: Unweighted Parity Projection Invariant |
| **Class 4: Multiple & Correlated Faults** | Consecutive accumulator registers in PolyMul | Correlated double-glitch across adjacent coordinates | Multi-cycle transient burst | Solar particle event burst or pulsed EMFI | Severe lattice vector perturbation, decapsulation failure | Layer 3: Multi-Rail FO Status Gate |
| **Class 5: Pre-Invocation Input Corruption** | Ciphertext buffer $ct$ or secret key $sk$ in SRAM | Single or multi-bit flip in memory buffer | Prior to function invocation (persistent in buffer) | SEU in SRAM communication buffer or bus transmission error | DMR common-mode blind spot (both passes agree on bad key) | Layer 1: Pre-Invocation CRC32 Integrity Tag |
| **Class 6: Detection Logic Perturbation** | Status token registers or accumulator variables | Single-bit flip in checker state variable | During verification logic execution | Adversarial bypass or SEU inside countermeasure code | False negative (fault masked) or denial of service | Layer 3: Hamming-Distance 32 Multi-Rail Token |
| **Class 7: Control Flow & Predicate Bypasses** | Fujisaki-Okamoto (FO) equality check flag | Inversion of branch condition or compare result | During FO verification (`ct_memcmp`) | Clock glitch on branch comparison or condition register SEU | Forged ciphertext acceptance or spurious implicit rejection | Layer 3: Inline Asm Compiler Barrier Multi-Rail Gate |
| **Class 8: Persistent Stuck-At Faults** | ALU carry line, arithmetic register, or key memory | Stuck-at-0 or stuck-at-1 fault bit | Persistent across multiple execution passes | Total Ionizing Dose (TID) cell damage or permanent latch-up | Complete DMR failure (both passes identically affected) | Layer 1 & 2: Independent Algebraic / Reseed Validation |

---

## 3. Threat Model Boundaries

1. **Algorithm Boundary:** Confined to NIST FIPS 203 ML-KEM-768 decapsulation.
2. **Platform Boundary:** 64-bit ARM architecture (Apple Silicon AArch64) compiling with Apple clang 21.0.0 at `-O3`.
3. **Out-of-Scope:** Physical radiation chamber qualification, differential power analysis (DPA) side channels, and microarchitectural speculative execution attacks.
